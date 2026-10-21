"""Review immutable actual diagnostic/control/runner evidence only. No ADB or media reads."""
from pathlib import Path
import json,re,hashlib
E=Path(__file__).resolve().parent
def sha(b):return hashlib.sha256(b).hexdigest()
def load(n):return json.loads((E/n).read_bytes())
def txt(n):return (E/n).read_text(encoding='utf-8').replace('\r\n','\n')
def save(n,v):
    with (E/n).open('x',encoding='utf-8') as out:json.dump(v,out,ensure_ascii=False,indent=2);out.write('\n')
handle='9f19bfb5-60e0-4bcc-9666-852409cfe3b4';first=load('control-01-snapshot.json');f=first['fields'];ack=txt('control-02-response-stdout.txt');logs=txt('06-managed-logcat-stdout.txt');final=txt('05-final-lifecycle-stdout.txt')
for k,want in dict(handle=handle,sequence='9',phase='RETURNED',verdict='QUALIFIED_DIAGNOSTIC',holder='CLOSED',originalOperationsReturned='true',safeToFinish='true',finishClaimed='false',admission='NONE',history='AVAILABLE',returned='0',matches='0',proc='NOT_REQUESTED',code='NO_UNIQUE_MATCH_MISSING',matchedTimestamp='NOT_COLLECTED',matchedReason='NOT_COLLECTED',matchedStatus='NOT_COLLECTED').items():assert f[k]==want,(k,f[k])
for key in ['rejectPid','rejectUid','rejectProcess','rejectBeforeOwner','rejectFuture','reasonNonPositive']:assert f[key]=='0'
assert first['rawResponseSha256']==sha((E/'control-01-response-stdout.txt').read_bytes())
admission=load('finish-admission.json');assert admission['admitted'] and admission['snapshotFileSha256']==sha((E/'control-01-snapshot.json').read_bytes())
assert 'Broadcast completed: result=1' in ack and 'sequence=10' in ack and 'finishClaimed=true' in ack and 'holder=CLOSED originalOperationsReturned=true safeToFinish=true' in ack
direct=load('control-02-direct-tool-receipt.json');assert direct['toolResult']['exit_code']==0 and direct['toolResult']['wall_time_seconds']<5 and direct['actualAckRequests']==1
assert 'holder=CLOSED originalOperationsReturned=true safeToFinish=true finishClaimed=true' in logs
start=re.search(r'(\d+\.\d+)\s+1000.*Start proc (\d+):com\.videokit\.app/u0a221',logs);assert start
pid=int(start[2]);assert pid==13876
reserved=re.search(r'(\d+\.\d+)\s+10221\s+'+str(pid)+r'.*sequence=1 phase=RESERVED',logs)
returned=re.search(r'(\d+\.\d+)\s+10221\s+'+str(pid)+r'.*sequence=9 phase=RETURNED verdict=QUALIFIED_DIAGNOSTIC',logs)
claim=re.search(r'(\d+\.\d+)\s+10221\s+'+str(pid)+r'.*sequence=10.*finishClaimed=true',logs)
finished=re.search(r'(\d+\.\d+)\s+1000.*Force stopping com\.videokit\.app appid=10221 user=0: finished inst',logs)
killed=re.search(r'(\d+\.\d+)\s+1000.*Killing '+str(pid)+r':com\.videokit\.app/u0a221.*finished inst',logs)
assert all([reserved,returned,claim,finished,killed]) and float(start[1])<float(reserved[1])<=float(returned[1])<float(claim[1])<=float(finished[1])<=float(killed[1])
assert not re.search(r'^\s*'+str(pid)+r'\s+',final,re.M) and not re.search(r'^\s*\d+\s+\S+\s+com\.videokit\.[^\s]+\s*$',final,re.M)
assert float(claim[1])-float(returned[1])>10,'ASYNC_RUNNER_DID_NOT_REMAIN_UNFINISHED_BEFORE_EXTERNAL_ACK'
budget=load('control-budget-final.json');assert budget['used']==2 and budget['remaining']==4 and budget['ackRequests']==1 and budget['noBudgetReset']
assert load('ack-failure.json')['type']=='KeyError' and not (E/'ack-client-pending.json').exists()
assert 'DUMP_PERMISSION|Unknown command: check-permission' in txt('01-before-deployment-stdout.txt')
assert re.search(r'android\.permission\.DUMP:\s+granted=true\b',txt('01-shell-dump-permission-fallback-stdout.txt'))
receipts=[dict(name=p.name,**json.loads(p.read_bytes())) for p in sorted(E.glob('*-receipt.json')) if p.name!='control-02-direct-tool-receipt.json']
assert len(receipts)==15
assert len([r for r in receipts if r['exitCode']!=0])==1 and next(r for r in receipts if r['exitCode']!=0)['name']=='01-before-deployment-receipt.json'
assert all(r['clientReturned'] and not r['overflow'] for r in receipts)
for role in ['app','test']:assert txt('02-install-'+role+'-stdout.txt').strip().endswith('Success')
total=sum(p.stat().st_size for p in E.glob('*-stdout.txt'));assert total<1048576
result=dict(collection='QUALIFIED_DIAGNOSTIC_COMPLETED',deathGate='BLOCKED_CURRENT_GATE_NO_UNIQUE_MATCH_MISSING',history='AVAILABLE',historyRowsReturned=0,identityTimeMatches=0,proc='NOT_REQUESTED',deathReason='NOT_COLLECTED',rootCause='NO_MATCHING_RECORDS_RETURNED_IN_THIS_QUERY; OLD_AVI_CAUSE_AND_RETENTION_REBOOT_PID_REUSE_NOT_PROVEN',originalOwner=dict(holder='CLOSED',operationsReturned=True,safeToFinish=True,proof='ACTUAL_PRODUCTION_JOB_STATE_PLUS_FROZEN_OS_CLOSE_BINDING_NOT_INDEPENDENT_SYSCALL_TRACE'),runner=dict(component='com.videokit.app.test/com.videokit.spike.e4.E7AReadOnlyInstrumentation',handle=handle,pid=pid,uid=10221,startedAt=float(start[1]),reservedLogAt=float(reserved[1]),returnedLogAt=float(returned[1]),reservedToReturnedLogSeconds=round(float(returned[1])-float(reserved[1]),3),finishClaimLogAt=float(claim[1]),platformFinishedInstLogAt=float(finished[1]),systemKilledForFinishedInstLogAt=float(killed[1]),actualPlatformFinishObserved=True,finalProcessAbsent=True,receiverUnregister='CONTROL_FLOW_INFERENCE_BEFORE_SOLE_SUPER_FINISH_WITH_REAL_FINISHED_INST_NOT_SEPARATE_SYSCALL_TRACE'),controlBudget=budget,control1ElapsedSeconds=load('control-01-response-receipt.json')['elapsedSeconds'],control2ToolElapsedSeconds=direct['toolResult']['wall_time_seconds'],adbCalls=16,installCalls=2,launchCalls=1,controlWireCalls=2,remainingMetadataCalls=11,batchLogBytes=total,receipts=receipts,readonlyCompatibilityCorrections=2,ackWrapperFailureBeforeAdb=True,wrapperModifiedForAck=False,ackWireRetry=False,actualAckWireCalls=1,hostChecksUnsupported=['pm check-permission','dumpsys activity instrumentation'],finalLifecycleBasis='Real ActivityManager finished-inst records plus process inventory, not unsupported dumpsys subcommand',inFlight=[],pendingOriginalOwner=False,additionalMediaOrBudgetContentReadBytes=0,ownerReadMaxBytes=257,historyCallsMax=1,historyLimit=8,grant='NONE',newRecoveryWriteObserveOrProductMethods=0,longTermE6B_OBS_F01='OPEN_DESIGN_BLOCKED',oldBudgetLastObserved=dict(consumed=107218,reserved=0,newlyReadThisBatch=False),D1='NOT_PASSED',M0='NOT_STARTED',scopeLimit='FAST_COMPLETED_JOB_AND_POSITIVE_CONTROL_PATH_ONLY; NO_TIMEOUT_UNKNOWN_OR_PERMISSION_DENIAL_FAULT_INJECTION')
save('final-independent-review.json',result)
print(json.dumps({k:result[k] for k in ['collection','deathGate','historyRowsReturned','proc','adbCalls','batchLogBytes','inFlight','longTermE6B_OBS_F01']}))
