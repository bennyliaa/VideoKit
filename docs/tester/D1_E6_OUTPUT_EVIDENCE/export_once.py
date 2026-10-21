"""One exact read-only binary export with finite buffers and original process ownership."""
from pathlib import Path
import hashlib,json,subprocess,time,threading,shlex,os
E=Path(__file__).resolve().parent;R=E.parents[2]
ADB='D:/Android/SDK/platform-tools/adb.exe';SERIAL='HA1Q6WXR'
PATH='files/e4a_outputs/0ee15550-8952-4639-91ac-83ab9d14d36c.mp4'
EXPECTED='20ad48067b3293aa9e6b8f3eacc7543e29edcda8ab19c15cbe438d55c995b6dd'
STAMP='64522,20174,53651,10221,8180,1792225287'
OWNERS=[]
def save(name,v):
    with (E/name).open('x',encoding='utf-8') as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')
def run(name,args,cap,outpath=None):
    save(name+'-attempt.json',dict(args=args,serial=SERIAL,seconds=15,stdoutCap=cap,began=time.time()))
    start=time.monotonic();owner=dict(process=None,threads=[],stdout=bytearray(),stderr=bytearray(),actualStdout=0,actualStderr=0,overflow=False,errors=[],closed=[False,False],hostFile=None,hostFileClosed=outpath is None);OWNERS.append(owner)
    if outpath:owner['hostFile']=outpath.open('xb')
    p=subprocess.Popen([ADB,'-s',SERIAL,*args],stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.PIPE);owner['process']=p
    def drain(pipe,index):
        key='stdout' if index==0 else 'stderr';actual='actualStdout' if index==0 else 'actualStderr';bound=cap if index==0 else 65536
        try:
            while True:
                b=pipe.read(4096)
                if not b:break
                owner[actual]+=len(b);remaining=max(0,bound-len(owner[key]));owner[key].extend(b[:remaining])
                if len(b)>remaining:owner['overflow']=True
                if index==0 and outpath:owner['hostFile'].write(b[:remaining])
        except BaseException as e:owner['errors'].append(str(e))
        finally:
            try:pipe.close();owner['closed'][index]=True
            except BaseException as e:owner['errors'].append(str(e))
    for i,pipe in enumerate([p.stdout,p.stderr]):
        t=threading.Thread(target=drain,args=(pipe,i),daemon=True);owner['threads'].append(t);t.start()
    timedout=False
    try:rc=p.wait(timeout=15)
    except subprocess.TimeoutExpired:
        timedout=True;save(name+'-deadline.json',dict(status='PENDING_ORIGINAL_CLIENT_RETAINED_NO_KILL'));print('PENDING original export client retained, no cancel or fallback',flush=True);rc=p.wait()
    for t in owner['threads']:t.join()
    if outpath:
        try:owner['hostFile'].flush();os.fsync(owner['hostFile'].fileno())
        finally:owner['hostFile'].close();owner['hostFileClosed']=True
    b=bytes(owner['stdout']);err=bytes(owner['stderr']);elapsed=time.monotonic()-start
    with (E/(name+'-stderr.txt')).open('xb') as f:f.write(err)
    if not outpath:
        with (E/(name+'-stdout.txt')).open('xb') as f:f.write(b)
    returned=all(owner['closed']) and owner['hostFileClosed'] and not any(t.is_alive() for t in owner['threads'])
    row=dict(args=args,exitCode=rc,elapsedSeconds=elapsed,stdoutBytes=owner['actualStdout'],savedBytes=len(b),stdoutSha256=hashlib.sha256(b).hexdigest(),stderrBytes=owner['actualStderr'],overflow=owner['overflow'],errors=owner['errors'],timedOut=timedout,clientReturned=returned,pipesClosed=owner['closed'],hostFileClosed=owner['hostFileClosed'])
    save(name+'-receipt.json',row)
    if returned:OWNERS.remove(owner)
    assert returned and rc==0 and not timedout and elapsed<=15 and not owner['overflow'] and not owner['errors'],name
    assert not err,name+' unexpected stderr'
    print(json.dumps(dict(call=name,exitCode=rc,bytes=len(b),elapsedSeconds=elapsed)),flush=True)
    return b
SCRIPT="set -eu; printf 'UID|'; id -u; test -f "+PATH+"; test ! -L "+PATH+"; printf 'STAT|'; stat -c '%d,%i,%s,%u,%f,%Y' "+PATH
save('batch-attempt.json',dict(exportAttempts=1,output=PATH,host='failed-output-53651.mp4',expectedBytes=53651,expectedSha256=EXPECTED,metadataMaxCalls=3,sourceMediaAllowed=False))
try:
    assert shlex.split('run-as com.videokit.app sh -c '+shlex.quote(SCRIPT))==['run-as','com.videokit.app','sh','-c',SCRIPT]
    pre=run('00-pre-stat',['shell','run-as com.videokit.app sh -c '+shlex.quote(SCRIPT)],4096)
    assert pre.decode().replace('\r\n','\n')=='UID|10221\nSTAT|'+STAMP+'\n'
    raw=run('01-binary-export',['exec-out','run-as','com.videokit.app','cat',PATH],53652,E/'failed-output-53651.mp4')
    began=time.monotonic();host=(E/'failed-output-53651.mp4').read_bytes();digest=hashlib.sha256(host).hexdigest();hash_seconds=time.monotonic()-began
    assert hash_seconds<=2 and len(raw)==len(host)==53651 and raw==host and digest==EXPECTED
    save('host-binary-identity.json',dict(bytes=len(host),sha256=digest,hostHashSeconds=hash_seconds,identity='EXACT_PRODUCTION_SHA_MATCH',readOnlyCoderUseAllowedAfterFinalStat=True))
    post=run('02-post-stat',['shell','run-as com.videokit.app sh -c '+shlex.quote(SCRIPT)],4096);assert post==pre
    save('export-independent-review.json',dict(result='PASS_EXACT_SINGLE_READONLY_EXPORT',device=SERIAL,uid=10221,remotePath=PATH,remoteStamp=STAMP,hostPath=str(E/'failed-output-53651.mp4'),bytes=53651,sha256=digest,prePostStatUnchanged=True,metadataCalls=2,exportCalls=1,adbCalls=3,stdoutCap=53652,hostHashSeconds=hash_seconds,allCurrentClientsAndPipesReturned=not OWNERS,inFlight=[],sourceMediaBytes=0,failedOutputContentReadBytes=53651,sourceRecoding=False,productOrObservationOrAbortCalls=0,installOrGradleCalls=0,ledgerWrites=0,originalFailure='UNCHANGED',D1='NOT_PASSED',M0='NOT_STARTED'))
except BaseException as e:
    save('failure.json',dict(status='STOP_NO_FALLBACK_OR_PARTIAL_REFETCH',type=type(e).__name__,detail=str(e),retainedOwners=len(OWNERS)));raise
