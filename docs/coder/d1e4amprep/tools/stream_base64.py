"""Bounded same-FD raw prehash + Base64 stream, using the unchanged T1 original-owner pump."""
import base64
import hashlib
import os
from pathlib import Path
import time
import exact_process as ep

RAW_CHUNK=24576 # Multiple of3. Short raw reads still use an explicit0..2-byte carry.

def encoded_length(n):return 4*((n+2)//3)

class EncodedSource:
    def __init__(self,path,n,sha,deadline,chunk=RAW_CHUNK):
        if not 1<=chunk<=RAW_CHUNK:raise ValueError('BOUNDED_RAW_CHUNK')
        self.path=Path(path);self.n=n;self.sha=sha;self.deadline=deadline;self.chunk=chunk
        self.raw=None;self.signature=None;self.close_returned=False;self.peak_buffer=0;self.reset()
    def reset(self):self.count=0;self.digest=hashlib.sha256();self.carry=b'';self.pending=b'';self.done=False
    def sig(self):
        s=os.fstat(self.raw.fileno());return (s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns)
    def open(self):
        if self.path.is_symlink() or not self.path.is_file():raise ValueError('RAW_REGULAR_SOURCE_REQUIRED')
        self.raw=self.path.open('rb',buffering=0);self.signature=self.sig()
        if self.signature[2]!=self.n:raise ValueError('RAW_SOURCE_LENGTH')
    def read(self,n):
        if not 1<=n<=65536:raise ValueError('FINITE_ENCODED_READ')
        while not self.pending and not self.done:
            if time.monotonic()>self.deadline:raise TimeoutError('RAW_ENCODING_DEADLINE')
            raw=self.raw.read(min(self.chunk,self.n-self.count)) if self.count<self.n else b''
            self.count+=len(raw);self.digest.update(raw)
            if self.count>self.n:raise ValueError('RAW_SOURCE_GREW')
            data=self.carry+raw
            if raw:
                cut=len(data)//3*3;self.pending=base64.b64encode(data[:cut]);self.carry=data[cut:]
            else:
                if self.count!=self.n or self.digest.hexdigest()!=self.sha or self.sig()!=self.signature:raise ValueError('RAW_STREAM_IDENTITY')
                self.pending=base64.b64encode(data);self.carry=b'';self.done=True
            self.peak_buffer=max(self.peak_buffer,len(raw)+len(data)+len(self.pending)+len(self.carry))
        result=self.pending[:n];self.pending=self.pending[n:];return result
    def rewind(self):self.raw.seek(0);self.reset()
    def close(self):
        if self.raw is not None:self.raw.close()
        self.close_returned=True

def transfer_base64(argv,path,n,sha,limits=ep.Limits(timeout=15,cleanup=2)):
    total=encoded_length(n);ep._validate(argv,total,'0'*64,limits)
    if n<0 or len(sha)!=64 or any(c not in '0123456789abcdef' for c in sha):raise ValueError('RAW_EXPECTATION')
    job=ep.Job(argv,total,'0'*64,limits);ep._reserve(job)
    source=EncodedSource(path,n,sha,job.start+limits.timeout);job.source=source
    pre=dict(rawBytes=0,rawSha256=None,encodedBytes=0,encodedSha256=None)
    digest=hashlib.sha256();stream_started=False
    try:
        source.open()
        while True:
            data=source.read(65536)
            if not data:break
            job.pre_read+=len(data);digest.update(data)
        pre.update(rawBytes=source.count,rawSha256=source.digest.hexdigest(),encodedBytes=job.pre_read,encodedSha256=digest.hexdigest())
        if job.pre_read!=total:raise ValueError('ENCODED_PREHASH_LENGTH')
        job.expected_sha=job.source_sha=digest.hexdigest();source.rewind()
    except Exception as error:
        pre.update(rawBytes=source.count,rawSha256=source.digest.hexdigest(),encodedBytes=job.pre_read,encodedSha256=digest.hexdigest())
        job.fail(str(error)[:120]);job.writer_returned=True
        try:source.close();job.source_closed=True
        except Exception:job.fail('SOURCE_CLOSE_UNKNOWN')
        ep._release_if_returned(job);record=job.record()
    else:stream_started=True;record=ep._run(job,source)
    record['rawSource']=dict(expectedBytes=n,expectedSha256=sha,prehash=pre,streamBytes=source.count if stream_started else 0,streamSha256=source.digest.hexdigest() if stream_started else ep.EMPTY_SHA,streamReachedDeclaredEnd=source.done if stream_started else False,actualRawCloseReturned=source.close_returned,rawChunkCap=RAW_CHUNK,peakTrackedBufferBytes=source.peak_buffer)
    record['encoding']=dict(type='BASE64_STANDARD_NO_LF',expectedBytes=total,expectedSha256=pre['encodedSha256'],actualSubmittedBytes=record['submittedBytes'],actualSubmittedSha256=record['submittedSha256'],noEncodedDiskCopy=True)
    return record
