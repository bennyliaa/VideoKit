"""Isolated narrow stdin-close injection through the actual production collect/transfer paths."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys
import threading
import time
import exact_process as ep

BASE=Path(__file__).resolve().parents[1]
ASSERTIONS=0
def check(ok,why):
    global ASSERTIONS
    ASSERTIONS+=1
    if not ok:raise AssertionError(why)
def denied(action):
    try:action()
    except RuntimeError as error:check(str(error)=='ORIGINAL_PROCESS_OWNER_BUSY_OR_UNKNOWN','same admission refusal');return
    raise AssertionError('unknown admitted next call')
class CloseFault(IOError):pass

def main():
    name=sys.argv[1];root=Path(sys.argv[2]).resolve()
    if not root.is_relative_to(BASE/'evidence') or root.exists():raise ValueError('new owned case root only')
    root.mkdir();(root/'.owned-fixture-root').write_text('E4AT_OWNED_FAKE_FILES_ONLY');(root/'files/e4_fixtures').mkdir(parents=True)
    argv=[sys.executable,'-X','utf8','-B','-u',str(BASE/'tools/fake_child.py'),'argv','--root',str(root),'--',name]
    original=ep.subprocess.Popen;launches=[];proxies=[];injected=CloseFault('OWNED_STDIN_CLOSE_FAILURE');entered=threading.Event();release=threading.Event()
    class Proxy:
        def __init__(self,raw,process):self.raw=raw;self.process=process;self.close_calls=0
        def write(self,data):return self.raw.write(data)
        def flush(self):return self.raw.flush()
        def close(self):
            self.close_calls+=1
            # Child independently exits without needing stdin EOF. This makes the exact exit0 counterexample observable.
            check(self.process.wait(timeout=2)==0,'original process exited0 before injected close outcome')
            if name=='throw_after':self.raw.close();raise injected
            if name=='throw_before':raise injected
            entered.set()
            if not release.wait(5):raise CloseFault('OWNED_BARRIER_NOT_RELEASED')
            self.raw.close()
    def launch(*args,**kwargs):
        if name=='no_stdin':kwargs['stdin']=subprocess.DEVNULL
        process=original(*args,**kwargs);launches.append(process)
        if name in {'throw_before','throw_after','blocked_return'}:
            proxy=Proxy(process.stdin,process);process.stdin=proxy;proxies.append(proxy)
        if name=='no_stdin':check(process.wait(timeout=2)==0,'child without stdin completed independently')
        return process
    ep.subprocess.Popen=launch
    results=[];proof={}
    if name=='success_transfer':
        data=bytes(range(256));source=root/'own-source.bin';source.write_bytes(data)
        target='files/e4_fixtures/own.part';command=[sys.executable,'-X','utf8','-B','-u',str(BASE/'tools/fake_child.py'),'receive','--root',str(root),'--target',target]
        result=ep.transfer_file(command,source,len(data),hashlib.sha256(data).hexdigest(),ep.Limits(timeout=3));results.append(result)
        check(result['status']=='PROCESS_IO_COMPLETE_ONLY' and result['ownership']=='RETURNED','real binary transfer actual close/wait returns')
        check(result['stdinOwnerAllocated'] and result['stdinCloseAttempted'] and result['stdinCloseReturned'],'actual allocated pipe close necessary and returned')
        check((root/target).read_bytes()==data,'source binary unchanged by closure fix')
        check(ep.retained_owners()==0,'success returned original owner')
    elif name=='no_process':
        result=ep.collect([str(root/'never-allocated.exe')],ep.Limits(timeout=1));results.append(result)
        check(not launches and result['originalExitCode'] is None,'pre-launch refusal never enters allocator')
        check(not result['stdinOwnerAllocated'] and not result['stdinCloseAttempted'] and not result['stdinCloseReturned'],'absent stdin is not a fake close success')
        check(result['sourceCloseReturned'] and result['ownership']=='RETURNED' and ep.retained_owners()==0,'actual existing source closed; no nonexistent process charge')
        second=ep.collect(argv,ep.Limits(timeout=3));results.append(second);check(second['status']=='PROCESS_IO_COMPLETE_ONLY','no permanent admission after proven no allocation')
    elif name=='no_stdin':
        result=ep.collect(argv,ep.Limits(timeout=3));results.append(result)
        check(launches[0].stdin is None and not result['stdinOwnerAllocated'],'process exists, stdin actually never allocated')
        check(not result['stdinCloseAttempted'] and not result['stdinCloseReturned'],'no close of nonexistent stdin')
        check(result['ownership']=='RETURNED' and result['status']=='NOT_ADMITTED','allocated drains/wait/source returned but missing requested input is not admitted')
        check(ep.retained_owners()==0,'unallocated stdin does not make permanent occupied owner')
    else:
        limits=ep.Limits(timeout=.35,cleanup=.2) if name=='blocked_return' else ep.Limits(timeout=3)
        result=ep.collect(argv,limits);results.append(result)
        check(result['ownership']=='UNKNOWN_RETAINED' and result['status']=='NOT_ADMITTED','close failure/pending cannot return owner')
        check(result['originalExitObserved'] and result['originalExitCode']==0,'exit0 cannot substitute stdin return')
        check(result['stdinOwnerAllocated'] and result['stdinCloseAttempted'] and not result['stdinCloseReturned'],'one real original pipe, no invented close proof')
        check(ep.retained_owners()==1,'original registry still holds actual job')
        jobs=tuple(ep._OWNERS);check(len(jobs)==1,'one original retained owner');job=jobs[0];proxy=proxies[0]
        check(job.process is launches[0] and job.stdin is proxy and job.process.stdin is proxy,'actual process and original stdin strongly reachable')
        check(job.source is not None and job.argv==argv and proxy.raw is not None,'actual source and original parameters/raw pipe retained')
        check(job.out.returned and job.err.returned,'other original pipe closes actually returned')
        count=len(launches);denied(lambda:ep.collect(argv,ep.Limits(timeout=1)))
        denied(lambda:ep.transfer_file(argv,root/'not-opened.bin',0,ep.EMPTY_SHA,ep.Limits(timeout=1)))
        check(len(launches)==count and proxy.close_calls==1,'no next process or second close after refusal')
        proof=dict(actualJobReachable=True,actualProcessReachable=True,actualStdinReachable=True,actualRawPipeReachable=True,originalSourceReachable=True,originalArgumentsReachable=True,closeCalls=proxy.close_calls)
        if name=='blocked_return':
            check(entered.is_set() and not job.writer_returned and any(t.is_alive() for t in job.threads),'actual close still inside barrier')
            check(job.stdin_close_error is None and not job.stdin_closed,'pending not an exception or return')
            before=job.record();release.set()
            for thread in job.threads:thread.join(1)
            check(all(not t.is_alive() for t in job.threads) and job.stdin_closed and job.source_closed,'barrier release yields actual close/source/thread returns')
            after=job.record();check(before['ownership']=='UNKNOWN_RETAINED' and after['ownership']=='RETURNED','only original observed return changes ownership')
            check(after['status']=='NOT_ADMITTED' and 'PROCESS_TIMEOUT' in after['errors'],'late cleanup never admits original timed-out transfer')
            check(ep.retained_owners()==0 and proxy.close_calls==1,'observation prunes only proven return; no retry or manual registry clear')
            def fresh_launch(*args,**kwargs):
                process=original(*args,**kwargs);launches.append(process);return process
            ep.subprocess.Popen=fresh_launch
            second=ep.collect(argv,ep.Limits(timeout=3));results.extend([after,second]);check(second['status']=='PROCESS_IO_COMPLETE_ONLY','new independent call only after original actual return')
        else:
            check(job.writer_returned and all(not t.is_alive() for t in job.threads),'writer/all threads returned yet pipe ownership still unknown')
            check(job.source_closed and job.stdin_close_error is injected,'source return and original exception retained separately')
            check(not job.stdin_closed and proxy.close_calls==1 and ep.retained_owners()==1,'exception permanently unproven, no retry/clear')
            if name=='throw_after':check(proxy.raw.closed,'even raw.closed flag plus exception is not actual close-return proof')
            # Do not close the raw pipe or clear _OWNERS. This isolated case ends UNKNOWN.
    ep.subprocess.Popen=original
    record=dict(schema=1,case=name,status='PASS',assertions=ASSERTIONS,actualChildLaunches=len(launches),retainedOwnersAtCaseExit=ep.retained_owners(),proof=proof,results=results,
                registryManuallyCleared=False,forcedGc=False,deviceRuns=0,adbCalls=0,gradleRuns=0,realMediaBytesRead=0,isolatedExitCleanupNotCredited=True)
    (root/'case-result.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({key:record[key] for key in ['case','status','assertions','actualChildLaunches','retainedOwnersAtCaseExit']},sort_keys=True))

if __name__=='__main__':main()
