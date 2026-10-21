"""One formally dispatched managed diagnostic. Immutable call/control intent ledger; no retries or process kills."""
from pathlib import Path
import subprocess,threading,time,json,hashlib,re,sys
R=Path(__file__).resolve().parents[3];E=Path(__file__).resolve().parent
ADB='D:/Android/SDK/platform-tools/adb.exe';SERIAL='HA1Q6WXR';HANDLE='9f19bfb5-60e0-4bcc-9666-852409cfe3b4'
PLAN=json.loads((R/'docs/coder/d1e7a/tools/device_plan.json').read_bytes());COMPONENT=PLAN['component']
def sha(b):return hashlib.sha256(b).hexdigest()
def save(n,v):
    with (E/n).open('x',encoding='utf-8') as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')
def load(n):return json.loads((E/n).read_bytes())
def call(name,args,budget=15,cap=128*1024):
    save(name+'-intent.json',dict(at=time.time(),serial=SERIAL,args=args,budgetSeconds=budget))
    argv=[ADB,'-s',SERIAL,*args];began=time.monotonic();p=subprocess.Popen(argv,stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    count=0;parts=[];overflow=False
    def drain():
        nonlocal count,overflow
        while True:
            b=p.stdout.read(4096)
            if not b:break
            count+=len(b)
            if count<=cap:parts.append(b)
            else:overflow=True
        p.stdout.close()
    reader=threading.Thread(target=drain);reader.start()
    try:rc=p.wait(timeout=budget)
    except subprocess.TimeoutExpired:
        save(name+'-client-pending.json',dict(status='CLIENT_STILL_RUNNING_BUDGET_EXCEEDED_DO_NOT_KILL_OR_RETRY',pid=p.pid,handle=HANDLE,deadlineSeconds=budget))
        print(json.dumps(dict(call=name,status='CLIENT_STILL_RUNNING_BUDGET_EXCEEDED_NO_RETRY',pid=p.pid)),flush=True)
        rc=p.wait() # Preserve the original client and reader; never kill on a host clock.
    reader.join();elapsed=time.monotonic()-began;b=b''.join(parts)
    with (E/(name+'-stdout.txt')).open('xb') as f:f.write(b)
    save(name+'-receipt.json',dict(argv=argv,exitCode=rc,receivedBytes=count,savedBytes=len(b),sha256=sha(b),overflow=overflow,elapsedSeconds=elapsed,clientReturned=True))
    print(json.dumps(dict(call=name,exitCode=rc,bytes=count,elapsedSeconds=elapsed)),flush=True)
    assert sum(p.stat().st_size for p in E.glob('*-stdout.txt'))<=1048576,'TOTAL_LOG_BUDGET'
    assert rc==0 and not overflow and elapsed<=budget,name+' FAILED_OR_UNKNOWN_NO_RETRY'
    return b.decode('utf-8',errors='replace').replace('\r\n','\n')
def packages(name,version,appsha,testsha,permission=False,reuse=False):
    script='set -eu; getprop ro.product.model; getprop ro.build.version.sdk; getprop ro.product.cpu.abilist; am get-current-user; dumpsys package com.videokit.app; dumpsys package com.videokit.app.test; dumpsys activity instrumentation; ps -A -o PID,UID,NAME'
    if permission:script+="; printf 'DUMP_PERMISSION|'; pm check-permission android.permission.DUMP com.android.shell 0"
    s=(E/(name+'-stdout.txt')).read_text().replace('\r\n','\n') if reuse else call(name,['shell',script]);assert s.startswith('TB138FC\n31\narm64-v8a,armeabi-v7a,armeabi\n0\n')
    parts=s.split('Packages:')[1:];assert len(parts)==2
    for part,uid,v in zip(parts,[10221,10222],[version,0]):
        assert 'userId='+str(uid) in part and re.search(r'versionCode='+str(v)+r'\b',part)
        assert re.search(r'User 0:.*installed=true.*hidden=false.*suspended=false.*enabled=0\b',part)
    assert 'ActiveInstrumentation{' not in s and 'ActiveInstrumentation ' not in s
    assert not re.findall(r'^\s*\d+\s+\S+\s+com\.videokit\.[^\s]+\s*$',s,re.M),'PREEXISTING_APP_OR_WORKER_OWNER'
    if permission:assert 'DUMP_PERMISSION|granted\n' in s,'DUMP_NOT_CONFIRMED'
    paths=re.findall(r'codePath=(/data/app/[^\s]+)',s);assert len(paths)==2
    for role,path,want in zip(['app','test'],paths,[appsha,testsha]):
        assert re.fullmatch(r'/data/app/[A-Za-z0-9_~+=./-]+',path)
        assert call(name+'-'+role+'-hash',['shell','sha256sum',path+'/base.apk']).split()[0]==want
    return dict(version=version,appSha256=appsha,testSha256=testsha,uid=10221,testUid=10222,DUMP='CONFIRMED' if permission else 'REUSED_PRECHECK')
def clock():
    s=call('launch-device-clock',['shell','date +%s']).strip();assert s.isdigit();return s
def parse_snapshot(s):
    matches=re.findall(r'E7A handle='+HANDLE+r' sequence=\d+[^\r\n"]+',s)
    assert matches,'NO_ROUTED_HANDLE_SNAPSHOT'
    line=matches[-1].replace('\\n','').strip();f=dict(re.findall(r'([A-Za-z_]+)=([^\s]+)',line));assert f['handle']==HANDLE
    return line,f
mode=sys.argv[1];save(mode+'-stage-intent.json',dict(stage=mode,at=time.time(),once=True))
try:
    assert sha((R/'docs/coder/d1e7a/evidence/e7a-freeze.json').read_bytes())=='1264dd365255b8d22fe1586a7b892240a4745dc01e54d6f26c88ec149784cf76'
    for a in PLAN['apks']:
        b=(R/a['path']).read_bytes();assert len(b)==a['bytes'] and sha(b)==a['sha256']
    if mode=='preflight':
        assert call('00-device-state',['get-state']).strip()=='device'
        identity=packages('01-before-deployment',8,'1930ff1cde30ab48adb184128c1313ac6a0ab6957ce425dfe4974c970a91a987','ea3c95bc774204651bc8defc5084890694a192e8273e543ea37e040f6a9a9d69',True)
        save('preflight-result.json',dict(status='PASS',identity=identity,noPreviousInFlight=True,noBudgetOrOwnerContentRead=True))
    elif mode=='preflight-readonly-correction':
        failed=(E/'01-before-deployment-stdout.txt').read_text();assert 'DUMP_PERMISSION|Unknown command: check-permission' in failed
        assert load('01-before-deployment-receipt.json')['exitCode']==255
        permission=call('01-shell-dump-permission-fallback',['shell','dumpsys package com.android.shell'])
        assert re.search(r'android\.permission\.DUMP:\s+granted=true\b',permission),'DUMP_NOT_CONFIRMED'
        identity=packages('01-before-deployment',8,'1930ff1cde30ab48adb184128c1313ac6a0ab6957ce425dfe4974c970a91a987','ea3c95bc774204651bc8defc5084890694a192e8273e543ea37e040f6a9a9d69',False,True)
        identity['DUMP']='CONFIRMED_EXISTING_GRANTED_PERMISSION'
        save('preflight-result.json',dict(status='PASS_AFTER_READONLY_COMPATIBILITY_CORRECTION',identity=identity,noPreviousInFlight=True,noBudgetOrOwnerContentRead=True,successfulMetadataReused=True))
    elif mode=='deploy':
        assert load('preflight-result.json')['status'] in ['PASS','PASS_AFTER_READONLY_COMPATIBILITY_CORRECTION']
        for role,a in zip(['app','test'],PLAN['apks']):
            s=call('02-install-'+role,['install','-r',a['path']],30,16*1024);assert re.search(r'^Success\s*$',s,re.M),'INSTALL_NOT_PROVEN'
        identity=packages('03-installed',10,PLAN['apks'][0]['sha256'],PLAN['apks'][1]['sha256'])
        assert COMPONENT in (E/'03-installed-stdout.txt').read_text(),'CUSTOM_COMPONENT_NOT_INSTALLED'
        save('deployment-result.json',dict(status='PASS',identity=identity))
    elif mode=='deployment-readonly-correction':
        assert load('deploy-failure.json')['detail']=='CUSTOM_COMPONENT_NOT_INSTALLED'
        for role,a in zip(['app','test'],PLAN['apks']):
            assert re.search(r'^Success\s*$',(E/('02-install-'+role+'-stdout.txt')).read_text(),re.M)
            assert (E/('03-installed-'+role+'-hash-stdout.txt')).read_text().split()[0]==a['sha256']
        installed=(E/'03-installed-stdout.txt').read_text();assert 'versionCode=10 ' in installed and 'versionName=D1-E7A' in installed
        component=call('03-installed-component-list',['shell','pm','list','instrumentation','com.videokit.app'])
        assert 'instrumentation:'+COMPONENT+' (target=com.videokit.app)' in component,'CUSTOM_COMPONENT_NOT_REGISTERED'
        save('deployment-result.json',dict(status='PASS',identity=dict(version=10,appSha256=PLAN['apks'][0]['sha256'],testSha256=PLAN['apks'][1]['sha256'],uid=10221,testUid=10222),component=COMPONENT,allSuccessfulInstallAndIdentityChecksReused=True))
    elif mode=='launch':
        assert load('deployment-result.json')['status']=='PASS'
        args=['shell','am','instrument','--user','0']
        for k,v in PLAN['arguments'].items():args+=['-e',k,v]
        args.append(COMPONENT)
        assert '-w' not in args and '-m' not in args and '-f' not in args and 'class' not in args
        device_clock=clock()
        save('managed-task-handle.json',dict(handle=HANDLE,serial=SERIAL,user=0,appUid=10221,testUid=10222,component=COMPONENT,apks=PLAN['apks'],args=args,deviceStartClock=device_clock,hostAt=time.time(),controlMax=6,controlUsed=0,status='RESERVED_BEFORE_START'))
        s=call('04-launch-nonwaiting',args)
        assert 'INSTRUMENTATION_FAILED' not in s and 'Exception' not in s
        save('launch-result.json',dict(status='CLIENT_RETURNED_JOB_NOT_ASSUMED_DONE',handle=HANDLE,hostAt=time.time(),clock=device_clock))
    elif mode in ['status','stop','ack']:
        assert load('launch-result.json')['handle']==HANDLE
        used=len(list(E.glob('control-*-intent.json')));assert used<6,'CONTROL_TOTAL_BUDGET'
        command={'status':'STATUS','stop':'STOP_DEPENDENCIES','ack':'ACK_FINISH'}[mode]
        args=['shell','am','broadcast','--user','0','--receiver-foreground','-a',PLAN['control']['action'],'-p','com.videokit.app','--es','handle',HANDLE,'--es','command',command]
        archive=None
        if mode=='ack':
            admission=load('finish-admission.json');archive=E/admission['snapshotFile'];assert admission['admitted'] and sha(archive.read_bytes())==admission['snapshotFileSha256']
            f=load(admission['snapshotFile'])['fields'];assert f['originalOperationsReturned']=='true' and f['safeToFinish']=='true' and f['holder'] in ['EMPTY','CLOSED'] and f['finishClaimed']=='false'
            args+=['--ei','archivedSequence',f['sequence']]
            assert not any(json.loads(p.read_bytes())['command']=='ACK_FINISH' for p in E.glob('control-*-intent.json')),'ACK_ONCE'
        name='control-'+str(used+1).zfill(2)
        save(name+'-intent.json',dict(handle=HANDLE,sequenceNumber=used+1,command=command,args=args,at=time.time(),maxRequests=6,remainingAfter=5-used,archive=str(archive) if archive else None))
        s=call(name+'-response',args,5,64*1024)
        assert re.search(r'Broadcast completed: result=1\b',s),'CONTROL_RESPONSE_NOT_HANDLED'
        line,f=parse_snapshot(s)
        save(name+'-snapshot.json',dict(handle=HANDLE,command=command,rawSnapshot=line,fields=f,rawResponseSha256=load(name+'-response-receipt.json')['sha256'],used=used+1,remaining=5-used))
        print(json.dumps(dict(handle=HANDLE,control=command,used=used+1,remaining=5-used,fields=f)),flush=True)
    elif mode=='final-evidence':
        launch=load('launch-result.json')
        s=call('05-final-lifecycle',['shell','dumpsys activity instrumentation; ps -A -o PID,UID,NAME'],15,64*1024)
        logs=call('06-managed-logcat',['logcat','-d','-b','main','-b','system','-b','crash','-v','threadtime,epoch,uid','-T',launch['clock']+'.000','E7A_READ_ONLY:I','ActivityManager:I','AndroidRuntime:E','*:S'],15,512*1024)
        save('final-client-result.json',dict(status='RETURNED_REQUIRES_INDEPENDENT_REVIEW',controlUsed=len(list(E.glob('control-*-intent.json'))),controlRemaining=6-len(list(E.glob('control-*-intent.json')))))
    else:raise ValueError('UNKNOWN_STAGE')
except BaseException as error:
    save(mode+'-failure.json',dict(status='STOP_NO_RETRY_NO_KILL_RETAIN_ORIGINAL_HANDLE',handle=HANDLE,type=type(error).__name__,detail=str(error),controlUsed=len(list(E.glob('control-*-intent.json')))));raise
