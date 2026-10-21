"""Binary process IO, bounded drains, original-owner wait. No shell and no automatic retry."""
from __future__ import annotations
from dataclasses import dataclass, asdict
import hashlib
import io
import os
from pathlib import Path
import subprocess
import threading
import time

EMPTY_SHA=hashlib.sha256(b'').hexdigest()
_OWNERS=set()
_LOCK=threading.Lock()

@dataclass(frozen=True)
class Limits:
    timeout: float=120
    cleanup: float=2
    chunk: int=65536
    stdout_cap: int=1048576
    stderr_cap: int=1048576
    retained_prefix: int=65536

def write_all(stream,data,credited):
    """A write return is credited once; short positive returns continue with the original remainder."""
    view=memoryview(data)
    while view:
        n=stream.write(view)
        if type(n) is not int or n<=0 or n>len(view):raise IOError('BINARY_WRITE_NOT_PROVEN')
        credited(view[:n]);view=view[n:]

class Drain:
    def __init__(self,cap,keep):self.cap=cap;self.keep=keep;self.count=0;self.prefix=bytearray();self.digest=hashlib.sha256();self.returned=False;self.error=None
    def run(self,stream,job):
        try:
            while True:
                data=stream.read(16384)
                if not data:break
                self.count+=len(data);self.digest.update(data)
                self.prefix.extend(data[:max(0,self.keep-len(self.prefix))])
                if self.count>self.cap:job.fail('PROCESS_OUTPUT_BUDGET');break
        except Exception as error:self.error=repr(error);job.fail('PROCESS_DRAIN_UNKNOWN')
        finally:
            try:stream.close();self.returned=True
            except Exception as error:self.error=repr(error);job.fail('PROCESS_PIPE_CLOSE_UNKNOWN')
    def record(self):return dict(bytes=self.count,sha256=self.digest.hexdigest(),prefixHex=bytes(self.prefix).hex(),prefixTruncated=self.count>len(self.prefix),closeReturned=self.returned,error=self.error)

class Job:
    def __init__(self,argv,expected_bytes,expected_sha,limits):
        self.argv=list(argv);self.expected_bytes=expected_bytes;self.expected_sha=expected_sha;self.limits=limits
        self.process=None;self.spawn_attempted=False;self.creation_unknown=False;self.startup_error=None
        self.stdin=None;self.stdin_allocated=False;self.stdin_close_attempted=False;self.stdin_close_error=None
        self.source=None;self.threads=[];self.error=None;self.errors=[];self.stop=threading.Event();self.start=time.monotonic()
        self.submitted=0;self.stream_read=0;self.pre_read=0;self.digest=hashlib.sha256();self.source_sha=None
        self.flushed=False;self.stdin_closed=False;self.source_closed=False;self.writer_returned=False;self.exit=None;self.exit_observed=False;self.terminated=False
        self.out=Drain(limits.stdout_cap,limits.retained_prefix);self.err=Drain(limits.stderr_cap,limits.retained_prefix)
    def fail(self,reason):
        if self.error is None:self.error=reason
        if len(self.errors)<8 and reason not in self.errors:self.errors.append(reason)
        self.stop.set()
    def credit(self,data):self.submitted+=len(data);self.digest.update(data)
    def ownership_returned(self):
        if not self.spawn_attempted:
            return self.process is None and self.stdin is None and not self.creation_unknown and self.writer_returned and self.source_closed
        if self.process is None or self.creation_unknown:return False
        return (not self.stdin_allocated or self.stdin_closed) and self.exit_observed and self.writer_returned and self.source_closed and self.out.returned and self.err.returned and all(not t.is_alive() for t in self.threads)
    def record(self):
        returned=self.ownership_returned()
        complete=returned and not self.error and self.exit==0 and self.submitted==self.expected_bytes and self.stream_read==self.expected_bytes and self.source_sha==self.expected_sha and self.digest.hexdigest()==self.expected_sha and self.flushed and self.stdin_closed
        return dict(status='PROCESS_IO_COMPLETE_ONLY' if complete else 'NOT_ADMITTED',ownership='RETURNED' if returned else 'UNKNOWN_RETAINED',argv=self.argv,
                    expectedBytes=self.expected_bytes,expectedSha256=self.expected_sha,sourcePrehashBytes=self.pre_read,sourcePrehashSha256=self.source_sha,sourceStreamReadBytes=self.stream_read,
                    submittedBytes=self.submitted,submittedSha256=self.digest.hexdigest(),flushReturned=self.flushed,stdinCloseReturned=self.stdin_closed,sourceCloseReturned=self.source_closed,
                    originalExitCode=self.exit,originalExitObserved=self.exit_observed,terminatedOwnedChild=self.terminated,writerReturned=self.writer_returned,
                    elapsedSeconds=round(time.monotonic()-self.start,4),firstError=self.error,errors=self.errors,stdout=self.out.record(),stderr=self.err.record(),
                    remoteFileVerified=False,stdinOwnerAllocated=self.stdin_allocated,stdinCloseAttempted=self.stdin_close_attempted,
                    stdinCloseError=repr(self.stdin_close_error)[:200] if self.stdin_close_error is not None else None,creationUnknown=self.creation_unknown)

def _prune_proven_returns_locked():
    # Observe actual original flags and thread termination only. Never closes anything or clears UNKNOWN.
    for old in tuple(_OWNERS):
        if old.ownership_returned():_OWNERS.discard(old)

def _reserve(job):
    with _LOCK:
        _prune_proven_returns_locked()
        if _OWNERS:raise RuntimeError('ORIGINAL_PROCESS_OWNER_BUSY_OR_UNKNOWN')
        _OWNERS.add(job)

def _release_if_returned(job):
    if job.ownership_returned():
        with _LOCK:_OWNERS.discard(job)

def retained_owners():
    with _LOCK:_prune_proven_returns_locked();return len(_OWNERS)

def _run(job,source):
    job.source=source
    # A demonstrable pre-launch refusal has allocated neither process nor stdin. No PATH search.
    try:
        executable=Path(job.argv[0]);executable_admitted=executable.is_absolute() and not executable.is_symlink() and executable.is_file()
    except Exception as failure:job.startup_error=failure;executable_admitted=False
    if not executable_admitted:
        job.fail('EXECUTABLE_PREFLIGHT_REJECTED_NO_ALLOCATION')
        try:source.close();job.source_closed=True
        except Exception:job.fail('SOURCE_CLOSE_UNKNOWN')
        job.writer_returned=True;_release_if_returned(job);return job.record()
    try:
        flags=getattr(subprocess,'CREATE_NO_WINDOW',0);job.spawn_attempted=True
        job.process=subprocess.Popen(job.argv,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,bufsize=0,shell=False,close_fds=True,creationflags=flags)
        job.stdin=job.process.stdin;job.stdin_allocated=job.stdin is not None
    except Exception as failure:
        # Entered opaque allocator: no returned handle is NOT proof that no allocation occurred.
        job.creation_unknown=True;job.startup_error=failure
        try:source.close();job.source_closed=True
        except Exception:job.fail('SOURCE_CLOSE_UNKNOWN')
        job.writer_returned=True;job.fail('PROCESS_CREATE_FAILED')
        return job.record()
    process=job.process
    for name,drain,stream in [('stdout',job.out,process.stdout),('stderr',job.err,process.stderr)]:
        thread=threading.Thread(target=drain.run,args=(stream,job),name='e4at-'+name,daemon=True);job.threads.append(thread);thread.start()
    def writer():
        try:
            while not job.stop.is_set():
                data=source.read(min(job.limits.chunk,job.expected_bytes-job.stream_read+1))
                if not data:break
                if not isinstance(data,bytes):raise IOError('SOURCE_NOT_BINARY')
                job.stream_read+=len(data)
                if job.stream_read>job.expected_bytes:raise IOError('SOURCE_GREW')
                write_all(job.stdin,data,job.credit)
            if job.stop.is_set():raise IOError('TRANSFER_STOPPED')
            if job.stream_read!=job.expected_bytes or job.digest.hexdigest()!=job.expected_sha:raise IOError('SOURCE_STREAM_IDENTITY_MISMATCH')
            job.stdin.flush();job.flushed=True
        except Exception:job.fail('BINARY_INPUT_NOT_COMPLETE')
        finally:
            if job.stdin_allocated:
                job.stdin_close_attempted=True
                try:job.stdin.close();job.stdin_closed=True
                except Exception as failure:job.stdin_close_error=failure;job.fail('STDIN_CLOSE_UNKNOWN')
            try:source.close();job.source_closed=True
            except Exception:job.fail('SOURCE_CLOSE_UNKNOWN')
            job.writer_returned=True
    thread=threading.Thread(target=writer,name='e4at-binary-writer',daemon=True);job.threads.append(thread);thread.start()
    deadline=job.start+job.limits.timeout
    while True:
        code=process.poll()
        if code is not None:
            job.exit=code;job.exit_observed=True
            if code!=0:job.fail('PROCESS_NONZERO_EXIT')
            if all(not t.is_alive() for t in job.threads):break
        if job.stop.is_set() or time.monotonic()>=deadline:
            if not job.stop.is_set():job.fail('PROCESS_TIMEOUT')
            break
        job.stop.wait(min(.02,max(0,deadline-time.monotonic())))
    cleanup_deadline=time.monotonic()+job.limits.cleanup
    if process.poll() is None and job.error:
        try:process.kill();job.terminated=True
        except Exception:job.fail('OWNED_CHILD_STOP_UNKNOWN')
    try:job.exit=process.wait(timeout=max(.001,cleanup_deadline-time.monotonic()));job.exit_observed=True
    except Exception:job.fail('ORIGINAL_PROCESS_WAIT_UNKNOWN')
    for thread in job.threads:thread.join(max(0,cleanup_deadline-time.monotonic()))
    if any(t.is_alive() for t in job.threads):job.fail('ORIGINAL_PIPE_OWNER_UNRETURNED')
    record=job.record();_release_if_returned(job);return record

def _validate(argv,n,sha,limits):
    if not isinstance(argv,(tuple,list)) or not argv or any(not isinstance(x,str) or '\0' in x for x in argv):raise ValueError('PARAMETER_ARRAY_REQUIRED')
    if not 0<=n<=1073741824 or len(sha)!=64 or any(c not in '0123456789abcdef' for c in sha):raise ValueError('SOURCE_EXPECTATION_REQUIRED')
    if not (0<limits.timeout<=600 and 0<limits.cleanup<=5 and 1<=limits.chunk<=65536 and 0<=limits.retained_prefix<=65536 and 1<=limits.stdout_cap<=1048576 and 1<=limits.stderr_cap<=1048576):raise ValueError('FINITE_PROCESS_LIMITS_REQUIRED')

def transfer_file(argv,path,expected_bytes,expected_sha,limits=Limits()):
    """Prehash and transfer the SAME original read-only source FD. Never verify success from submit count."""
    _validate(argv,expected_bytes,expected_sha,limits);job=Job(argv,expected_bytes,expected_sha,limits);_reserve(job)
    try:
        path=Path(path)
        if path.is_symlink() or not path.is_file():raise IOError('SOURCE_REGULAR_ROLE')
        job.source=path.open('rb',buffering=0);before=os.fstat(job.source.fileno())
        if before.st_size!=expected_bytes:raise IOError('SOURCE_LENGTH_MISMATCH')
        digest=hashlib.sha256()
        while True:
            data=job.source.read(min(limits.chunk,expected_bytes-job.pre_read+1))
            if not data:break
            job.pre_read+=len(data)
            if job.pre_read>expected_bytes:raise IOError('SOURCE_PREHASH_BOUND')
            digest.update(data)
        job.source_sha=digest.hexdigest()
        if job.pre_read!=expected_bytes or job.source_sha!=expected_sha:raise IOError('SOURCE_PREHASH_MISMATCH')
        after=os.fstat(job.source.fileno())
        if (before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns)!=(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns):raise IOError('SOURCE_CHANGED')
        job.source.seek(0)
    except Exception as failure:
        job.fail(str(failure) if str(failure).isupper() else 'SOURCE_PREFLIGHT_FAILED')
        if job.source is not None:
            try:job.source.close();job.source_closed=True
            except Exception:job.fail('SOURCE_CLOSE_UNKNOWN')
        else:job.source_closed=True
        job.writer_returned=True
        if job.source_closed:
            with _LOCK:_OWNERS.discard(job)
        return job.record()
    return _run(job,job.source)

def collect(argv,limits=Limits(timeout=30)):
    _validate(argv,0,EMPTY_SHA,limits);job=Job(argv,0,EMPTY_SHA,limits);_reserve(job);job.source_sha=EMPTY_SHA
    return _run(job,io.BytesIO())

def stdout_bytes(result):
    stream=result['stdout']
    if result['status']!='PROCESS_IO_COMPLETE_ONLY' or stream['prefixTruncated']:raise IOError('COMMAND_RESULT_NOT_COMPLETE')
    return bytes.fromhex(stream['prefixHex'])

def installation_success(exit_code,stdout,stderr=b''):
    """Parse a finished original install response; never installs or triggers a second attempt."""
    try:lines=[line.strip() for line in stdout.decode('utf-8','strict').splitlines() if line.strip()];errors=stderr.decode('utf-8','strict').strip()
    except UnicodeError:return False
    return exit_code==0 and not errors and bool(lines) and lines[-1]=='Success' and all(line in {'Performing Streamed Install','Performing Push Install'} for line in lines[:-1])
