"""Formally dispatched E6B normal batch. Append-only evidence, no retries/kills/reset."""
from pathlib import Path
import importlib.util,ast,json,re,shlex,sys,time,struct
R=Path(__file__).resolve().parents[3];E=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('recording',R/'docs/tester/D1_E5C_OBSERVE_REGRESSION_EVIDENCE/common.py')
c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c);c.E=E
sha,save,load,call=c.sha,c.save,c.load,c.call
TASK=c.TASK;BUDGET=c.BUDGET;OLD=R/'docs/tester/D1_E5C_OBSERVE_REGRESSION_EVIDENCE'
SETTLEMENT='5b4b769c530714c1ee42721ab7c64cc87b9c6d8377a9bc8c47d1645c8eb4e962'
plan=json.loads((R/'docs/coder/d1e6b/tools/device_plan.json').read_bytes())
METHODS=[s['method'] for s in plan['steps']]
tree=ast.parse((R/'docs/tester/D1_E5C_N2_ABORT_EVIDENCE/execute_abort.py').read_text(encoding='utf-8-sig'))
node=next(n.value for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='POST' for t in n.targets))
POST=ast.literal_eval(node.func.value).replace('TASK',TASK)
def metadata(name,args,cap=256*1024):
    assert len(list(E.glob('metadata-*-intent.json')))<32
    save('metadata-'+name+'-intent.json',dict(at=time.time(),deadlineSeconds=15))
    s=call(name,args,cap);assert load(name+'-receipt.json')['elapsedSeconds']<=15,'METADATA_DEADLINE';return s
def output_extra(ids):
    for i in ids:assert re.fullmatch(r'[a-f0-9]{8}(?:-[a-f0-9]{4}){3}-[a-f0-9]{12}',i)
    paths=' '.join('files/e4a_outputs/'+i+'.'+s for i in ids for s in ['identity','journal','lease','owner','mp4'])
    return '''
for p in PATHS; do
 if [ ! -e "$p" ] && [ ! -L "$p" ]; then printf 'ABSENT|%s\n' "$p"; continue; fi
 test -f "$p"; test ! -L "$p"; printf 'OUTPUT_STAT|%s|' "$p"; stat -c '%d,%i,%s,%u,%f,%Y' "$p"
 case "$p" in *.mp4) ;; *) n=$(stat -c %s "$p"); test "$n" -le 4096; printf 'HEX_BEGIN|%s\n' "$p"; od -An -v -tx1 "$p"; printf 'HEX_END\n';; esac
done
'''.replace('PATHS',paths) if paths else ''
def private(name,ids=[]):return metadata(name,['shell','run-as com.videokit.app sh -c '+shlex.quote(POST+output_extra(ids))])
def blocks(s):return {p:bytes.fromhex(h) for p,h in re.findall(r'HEX_BEGIN\|([^\n]+)\n(.*?)HEX_END',s,re.S)}
def ledger(s,allow_pending=False):
    b=blocks(s)['files/e4a_output_budget/ledger.bin'];lines=b.decode().splitlines();h=sha((lines[0]+'\n').encode());records={}
    assert lines[0]=='E4A1 '+BUDGET+' 4194304 2097152 128'
    for line in lines[1:]:
        payload,want=line.rsplit(' ',1);assert sha((h+' '+payload).encode())==want;h=want;p=payload.split()
        if p[0]=='R':assert p[1] not in records;records[p[1]]=dict(batch=p[2],bytes=None,state=None)
        else:
            assert p[0]=='S' and p[1] in records and records[p[1]]['bytes'] is None
            records[p[1]].update(state=p[2],bytes=int(p[3]),sha256=p[4]);assert 0<=int(p[3])<=2097152
    consumed=sum(v['bytes'] or 0 for v in records.values());reserved=sum(2097152 for v in records.values() if v['bytes'] is None)
    pending='ABSENT|files/e4a_output_budget/operation.pending\n' not in s
    assert consumed+reserved<=4194304
    if not allow_pending:assert not pending and reserved==0
    return dict(records=records,consumed=consumed,reserved=reserved,pending=pending,sha256=sha(b))
def continuity(s,previous,exactledger=False):
    a=blocks(s);b=blocks(previous)
    for path,value in b.items():
        if path=='files/e4a_output_budget/ledger.bin':
            assert a[path]==value if exactledger else a[path].startswith(value)
        elif path in a:assert a[path]==value,path
    for fixture,stat in [('basic.mp4','64522,20198,349102,10221,8180,1792207996'),('subtitle.avi','64522,20199,736454656,10221,8180,1792208513')]:
        assert 'DATA_STAT|files/e4_fixtures/'+fixture+'|'+stat in s
    assert 'DATA_STAT|files/e4a_outputs/'+TASK+'.mp4|64522,20386,0,10221,8180,1792208948' in s
    assert 'ABSENT|files/e4a_output_budget/operation.pending\n' in s
def packages(name,version,appsha,testsha):
    s=metadata(name,['shell','set -eu; getprop ro.product.model; getprop ro.build.version.sdk; getprop ro.product.cpu.abilist; am get-current-user; dumpsys package com.videokit.app; dumpsys package com.videokit.app.test; df -k /data; dumpsys activity instrumentation; ps -A -o PID,UID,NAME'])
    assert s.startswith('TB138FC\n31\narm64-v8a,armeabi-v7a,armeabi\n0\n')
    parts=s.split('Packages:')[1:];assert len(parts)==2
    for part,uid,v in zip(parts,[10221,10222],[version,0]):
        assert 'userId='+str(uid) in part and re.search(r'versionCode='+str(v)+r'\b',part)
        assert re.search(r'User 0:.*installed=true.*hidden=false.*suspended=false.*enabled=0\b',part)
    paths=re.findall(r'codePath=(/data/app/[^\s]+)',s);assert len(paths)==2
    for role,path,h in zip(['app','test'],paths,[appsha,testsha]):
        assert re.fullmatch(r'/data/app/[A-Za-z0-9_~+=./-]+',path)
        assert metadata(name+'-'+role+'-hash',['shell','sha256sum',path+'/base.apk']).split()[0]==h
    assert 'ActiveInstrumentation{' not in s and 'ActiveInstrumentation ' not in s
    # Block if an app/isolated worker owner is still present, rather than forcibly stopping it.
    owners=re.findall(r'^\s*\d+\s+\S+\s+(com\.videokit\.[^\s]+)\s*$',s,re.M);assert not owners,owners
    return dict(version=version,appSha256=appsha,testSha256=testsha,uid=10221,testUid=10222)
mode=sys.argv[1];save(mode+'-stage-attempt.json',dict(at=time.time(),stage=mode,attempts=1))
try:
    assert sha((R/'docs/coder/d1e6b/evidence/e6b-freeze.json').read_bytes())=='21ef22f4e92535a0d4e50703d87ff46849c4228f5a20dd6f9721c31c87dddc33'
    assert sha((R/'docs/tester/D1_E5C_N2_ABORT_REPORT_V1.1.md').read_bytes())==SETTLEMENT
    for a in plan['apks']:
        b=(R/a['path']).read_bytes();assert len(b)==a['bytes'] and sha(b)==a['sha256']
    if mode=='preflight':
        assert metadata('00-device-state',['get-state']).strip()=='device'
        identity=packages('01-original-packages',5,'5b7992f1ec01f8782b59dd1508c6a47e3af4f2602ba428e1b65892724f73f464','5101c8efa43fd4ab5944479c8bafa8934ab9c4a1a1318fd9c6eae4c5d3f0e36c')
        s=private('02-before-install',['0ee15550-8952-4639-91ac-83ab9d14d36c']);previous=(OLD/'normalMp4SixRealFrames-post-state-stdout.txt').read_text().replace('\r\n','\n')
        continuity(s,previous,True);budget=ledger(s);assert budget['consumed']==53651
        save('preflight-result.json',dict(status='PASS',identity=identity,ledger=budget))
    elif mode=='deploy':
        assert load('preflight-result.json')['status']=='PASS'
        for role,args in zip(['app','test'],plan['deployment']['argv']):
            assert args[:2]==['-s','HA1Q6WXR'];s=call('03-install-'+role,args[2:],16*1024);assert re.search(r'^Success\s*$',s,re.M),'INSTALL_NOT_PROVEN'
        identity=packages('04-installed-packages',8,plan['apks'][0]['sha256'],plan['apks'][1]['sha256'])
        s=private('05-after-install',['0ee15550-8952-4639-91ac-83ab9d14d36c']);continuity(s,(E/'02-before-install-stdout.txt').read_text(),True)
        save('deployment-result.json',dict(status='PASS',identity=identity,ledger=ledger(s),preservedData=True))
    elif mode in METHODS:
        assert load('deployment-result.json')['status']=='PASS';i=METHODS.index(mode)
        for earlier in METHODS[:i]:assert load(earlier+'-independent-review.json')['dependentMethodsAdmitted']
        budget=load(METHODS[i-1]+'-independent-review.json')['ledger'] if i else load('deployment-result.json')['ledger']
        assert not budget['pending'] and not budget['reserved'] and budget['consumed']<=2097152
        args=list(plan['steps'][i]['reviewOnlyArgv']);assert args[:2]==['-s','HA1Q6WXR']
        if i==3:
            gate=load('cancel-admission.json');receipt=R/gate['normalReceiptReport'];assert gate['admitted'] and sha(receipt.read_bytes())==gate['normalReceiptSha256']
            args[args.index('e4NormalReceiptSha256')+1]=gate['normalReceiptSha256']
        clock=metadata(mode+'-clock',['shell','date +%s']).strip();assert clock.isdigit()
        s=call(mode+'-instrumentation',args[2:],4*1024*1024)
        metadata(mode+'-logcat',['logcat','-d','-b','main','-b','system','-b','crash','-v','threadtime,epoch,uid','-T',clock+'.000','VideoKitD1:I','AndroidRuntime:E','ActivityManager:I','TestRunner:I','*:S'],4*1024*1024)
        ids=list(dict.fromkeys(re.findall(r'outputTask=([a-f0-9-]{36})',s)))
        state=private(mode+'-post-state',['0ee15550-8952-4639-91ac-83ab9d14d36c',*ids]);continuity(state,(E/'05-after-install-stdout.txt').read_text())
        assert sum(load(mode+'-'+n+'-receipt.json')['receivedBytes'] for n in ['instrumentation','logcat','post-state','clock'])<=4*1024*1024,'METHOD_LOG_LIMIT'
        save(mode+'-client-result.json',dict(status='RETURNED_REQUIRES_INDEPENDENT_REVIEW',ledger=ledger(state,True)))
    else:raise ValueError('UNKNOWN_STAGE')
except BaseException as error:
    save(mode+'-failure.json',dict(status='STOP_DEPENDENCIES_NO_RETRY',type=type(error).__name__,detail=str(error)));raise
