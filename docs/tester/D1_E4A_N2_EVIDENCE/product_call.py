"""Original instrumentation client: deadline never terminates it or clears original owners."""
from common import *
import subprocess,threading
def instrument(argv,name,deadline_seconds):
    job=ep.Job(argv,0,ep.EMPTY_SHA,ep.Limits(timeout=deadline_seconds,cleanup=2,stdout_cap=131072,stderr_cap=131072,retained_prefix=131072));ep._reserve(job);job.source=io.BytesIO();job.source_sha=ep.EMPTY_SHA
    try:
        job.spawn_attempted=True
        job.process=subprocess.Popen(argv,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,bufsize=0,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
        job.stdin=job.process.stdin;job.stdin_allocated=True
    except Exception as ex:
        job.creation_unknown=True;job.startup_error=ex;job.fail('ORIGINAL_PRODUCT_CLIENT_CREATION_UNKNOWN');job.source.close();job.source_closed=True;job.writer_returned=True
        new(name+'.json',job.record());hold();raise
    def writer():
        try:job.stdin.flush();job.flushed=True
        except Exception:job.fail('PRODUCT_STDIN_FLUSH_UNKNOWN')
        finally:
            job.stdin_close_attempted=True
            try:job.stdin.close();job.stdin_closed=True
            except Exception as ex:job.stdin_close_error=ex;job.fail('STDIN_CLOSE_UNKNOWN')
            try:job.source.close();job.source_closed=True
            except Exception:job.fail('SOURCE_CLOSE_UNKNOWN')
            job.writer_returned=True
    def waiter():
        try:
            job.exit=job.process.wait();job.exit_observed=True
            if job.exit!=0:job.fail('PROCESS_NONZERO_EXIT')
        except Exception:job.fail('ORIGINAL_PROCESS_WAIT_UNKNOWN')
    entries=[(job.out.run,(job.process.stdout,job)),(job.err.run,(job.process.stderr,job)),(writer,()),(waiter,())]
    for fn,args in entries:
        t=threading.Thread(target=fn,args=args,daemon=True);job.threads.append(t);t.start()
    until=job.start+deadline_seconds
    while not job.ownership_returned() and not job.error and time.monotonic()<until:time.sleep(.02)
    if not job.ownership_returned() and not job.error:job.fail('PRODUCT_DEADLINE_ORIGINAL_CLIENT_RETAINED_NO_RETRY')
    cleanup=time.monotonic()+2
    for t in job.threads:t.join(max(0,cleanup-time.monotonic()))
    r=job.record();ep._release_if_returned(job);new(name+'.json',r)
    for stream in ('stdout','stderr'):
        s=r[stream];(E/(name+'-'+stream+'.txt')).write_bytes(bytes.fromhex(s['prefixHex']))
    print(json.dumps({'instrumentation':name,'ownership':r['ownership'],'exit':r['originalExitCode'],'firstError':r['firstError']},indent=2),flush=True)
    if ep.retained_owners():hold()
    return r,bytes.fromhex(r['stdout']['prefixHex']).decode('utf-8','strict')
