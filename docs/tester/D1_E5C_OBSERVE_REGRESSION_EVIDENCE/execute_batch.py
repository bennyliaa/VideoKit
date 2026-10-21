"""Authorized observation and conditionally gated four methods; never retries/kills."""
from common import *
import ast
ABORT=R/'docs/tester/D1_E5C_N2_ABORT_EVIDENCE'
SETTLEMENT='5b4b769c530714c1ee42721ab7c64cc87b9c6d8377a9bc8c47d1645c8eb4e962'
BATCH='D1-E4A-E5B-NORMAL-TABLET-20261017'
METHODS=['normalMp4SixRealFrames','normalAviSixRealFrames','capabilityDenialDoesNotOpenSource','cancelRejectsWrongEpochOversizeAndLateFrame']
tree=ast.parse((ABORT/'execute_abort.py').read_text(encoding='utf-8-sig'))
node=next(n.value for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='POST' for t in n.targets))
POST=ast.literal_eval(node.func.value).replace('TASK',TASK)
def metadata(name,args,cap=256*1024):
    assert len(list(E.glob('meta-*-intent.json')))<32
    save('meta-'+name+'-intent.json',dict(at=time.time(),deadlineSeconds=15))
    s=call(name,args,cap);assert load(name+'-receipt.json')['elapsedSeconds']<=15
    return s
def private(name,extra=''):return metadata(name,['shell','run-as com.videokit.app sh -c '+shlex.quote(POST+extra)])
def block_parse(s):return {p:bytes.fromhex(h) for p,h in re.findall(r'HEX_BEGIN\|([^\n]+)\n(.*?)HEX_END',s,re.S)}
def settled_exact(s):
    current=block_parse(s);previous=block_parse((ABORT/'03-post-abort-private-stdout.txt').read_text().replace('\r\n','\n'))
    assert current==previous,'SETTLED_METADATA_CONTINUITY_CHANGED'
    assert 'ABSENT|files/e4a_output_budget/operation.pending\n' in s
def ledger_check(s,allow_pending=False):
    ledger=block_parse(s)['files/e4a_output_budget/ledger.bin'].decode();lines=ledger.splitlines();h=sha((lines[0]+'\n').encode());records={}
    for line in lines[1:]:
        payload,recordhash=line.rsplit(' ',1);assert sha((h+' '+payload).encode())==recordhash;h=recordhash;p=payload.split()
        if p[0]=='R':assert p[1] not in records;records[p[1]]=dict(batch=p[2],bytes=None,state=None)
        else:
            assert p[0]=='S' and p[1] in records and records[p[1]]['bytes'] is None
            records[p[1]].update(bytes=int(p[3]),state=p[2],sha=p[4]);assert 0<=int(p[3])<=2097152
    pending='ABSENT|files/e4a_output_budget/operation.pending\n' not in s
    reserved=sum(2097152 for v in records.values() if v['bytes'] is None);consumed=sum(v['bytes'] or 0 for v in records.values())
    assert consumed+reserved<=4194304
    if not allow_pending:assert not pending and reserved==0
    return dict(records=records,consumed=consumed,reserved=reserved,pending=pending,ledgerSha=sha(ledger.encode()))
def output_extra(output_task):
    assert re.fullmatch(r'[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}',output_task)
    return '''
for p in files/e4a_outputs/ID.identity files/e4a_outputs/ID.journal files/e4a_outputs/ID.lease files/e4a_outputs/ID.owner files/e4a_outputs/ID.mp4; do
 if [ ! -e "$p" ] && [ ! -L "$p" ]; then printf 'ABSENT|%s\n' "$p"; continue; fi
 test -f "$p"; test ! -L "$p"; printf 'OUTPUT_STAT|%s|' "$p"; stat -c '%d,%i,%s,%u,%f,%Y' "$p"
 case "$p" in *.mp4) ;; *) n=$(stat -c %s "$p"); test "$n" -le 4096; printf 'HEX_BEGIN|%s\n' "$p"; od -An -v -tx1 "$p"; printf 'HEX_END\n';; esac
done
'''.replace('ID',output_task)
mode=sys.argv[1];save(mode+'-stage-attempt.json',dict(stage=mode,at=time.time(),attempts=1))
try:
    plan=artifacts();assert sha((R/'docs/tester/D1_E5C_N2_ABORT_REPORT_V1.1.md').read_bytes())==SETTLEMENT
    if mode=='preflight':
        s=metadata('00-packages',['shell','set -eu; am get-current-user; dumpsys package com.videokit.app; dumpsys package com.videokit.app.test']);assert s.startswith('0\n')
        parts=s.split('Packages:')[1:];assert len(parts)==2
        for part,uid,version in zip(parts,[10221,10222],[5,0]):
            assert 'userId='+str(uid) in part and re.search(r'versionCode='+str(version)+r'\b',part)
            assert re.search(r'User 0:.*installed=true.*hidden=false.*suspended=false.*enabled=0\b',part)
        s=private('01-settled-continuity');settled_exact(s);save('preflight-result.json',dict(status='PASS',ledger=ledger_check(s),reusedDeployment=True))
    elif mode=='observe':
        assert load('preflight-result.json')['status']=='PASS'
        args=list(plan['steps'][3]['argvAfterBoundAdbSerial']);args[args.index('e5N2Action')+1]='OBSERVE_SETTLED_N2';args[-1:-1]=['-e','e5aSettlementReceiptSha256',SETTLEMENT]
        call('02-original-observation',args,4*1024*1024)
        s=private('03-post-observation');settled_exact(s);save('observation-client-result.json',dict(status='RETURNED_REQUIRES_REVIEW',ledger=ledger_check(s)))
    elif mode in METHODS:
        assert load('observation-independent-admission.json')['admitted'];index=METHODS.index(mode)
        for earlier in METHODS[:index]:assert load(earlier+'-independent-review.json')['dependentMethodsAdmitted']
        latest=load(METHODS[index-1]+'-independent-review.json')['ledger'] if index else load('observation-independent-admission.json')['ledger']
        assert not latest['pending'] and latest['reserved']==0 and latest['consumed']<=2097152
        extra=[]
        if index==3:
            gate=load('cancel-admission.json');assert gate['admitted'] and len(gate['normalReceiptSha256'])==64;extra=['-e','e4NormalReceiptSha256',gate['normalReceiptSha256']]
        clock=metadata(mode+'-clock',['shell','date +%s']).strip();assert clock.isdigit()
        args=['shell','am','instrument','-w','-r','-e','class','com.videokit.spike.e4.E4DeviceTests#'+mode,'-e','e4Case',mode,'-e','e4Batch',BATCH,'-e','e4BudgetIdentity',BUDGET,'-e','e5aObservation','REVIEWED_ORIGINAL_N2_SETTLEMENT','-e','e5aSettlementReceiptSha256',SETTLEMENT,*extra,plan['runner']]
        s=call(mode+'-instrumentation',args,4*1024*1024)
        metadata(mode+'-logcat',['logcat','-d','-b','main','-b','system','-b','crash','-v','threadtime,epoch,uid','-T',clock+'.000','VideoKitD1:I','AndroidRuntime:E','ActivityManager:I','TestRunner:I','*:S'],4*1024*1024)
        ids=re.findall(r'outputTask=([a-f0-9-]{36})',s);extra=output_extra(ids[-1]) if ids else ''
        state=private(mode+'-post-state',extra);save(mode+'-client-result.json',dict(status='RETURNED_REQUIRES_REVIEW',ledger=ledger_check(state,True)))
    else:raise ValueError('UNKNOWN_STAGE')
except BaseException as e:
    save(mode+'-failure.json',dict(status='STOP_DEPENDENCIES_NO_RETRY',type=type(e).__name__,detail=str(e)));raise
