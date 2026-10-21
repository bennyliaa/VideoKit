"""Independent review of the actual failed MP4 and stop conditions; existing receipts only."""
from common import *
METHOD='normalMp4SixRealFrames'
raw=(E/(METHOD+'-instrumentation-stdout.txt')).read_bytes();s=raw.decode().replace('\r\n','\n')
lograw=(E/(METHOD+'-logcat-stdout.txt')).read_bytes();logs=lograw.decode().replace('\r\n','\n')
post=(E/(METHOD+'-post-state-stdout.txt')).read_text().replace('\r\n','\n')
assert 'FAILURES!!!' in s and 'Tests run: 1,  Failures: 1' in s and 'expected:<[READY]> but was:<[ABORTED]>' in s
assert 'E4 FINAL_OBSERVATION FRESH_OBSERVATION_ADMITTED' in s
report=re.search(r'E4 REPORT task=(\S+) status=(\S+) error=(\S+) received=(\d+) inputs=(\d+) outputs=(\d+) outputTask=(\S+) outputBytes=(\d+) outputSha=([a-f0-9]{64}) controlInFlight=(\d+) released=(\S+) workerDied=(\S+)',s)
assert report
task,status,error,received,inputs,outputs,output_task,n,outputsha,control,released,dead=report.groups()
assert (status,error,received,inputs,outputs,n,control,released,dead)==('ABORTED','E4_HOST_OPERATION_FAILED','6','6','6','53651','0','true','false')
assert 'terminalReason=ACTUAL_OWNERS_RETURNED' in s and 'originalOwnerReturned=true' in s and 'cleanupContinuations=1 ownerFinishEntries=1' in s
assert 'callbackFlags=18' in s and 'startedSignal=true startProven=true cleanupError= ' in s
assert 'callbackInFlight=0 callbackEntered=8 callbackReturned=8 callbackAckFailed=false callbackUnknown=false' in s
assert 'nativeCalls=0 liveResources=0 unknownResources=0 creating=false imageHeld=false encoderReleased=true sinkReleased=true leaseReleased=true framesReleased=true' in s
source=re.findall(r'stage=E4_SOURCE_FRAME .*?sequence=(\d+) task=(\S+) epoch=(\d+) pid=(\d+) uid=(\d+) pts_us=(\d+) raw=(\d+) num=(\d+) den=(\d+) sha=([a-f0-9]{64})',logs)
assert [int(x[0]) for x in source]==[1,2,3,4,5,6] and all(int(x[4])>=90000 for x in source)
verified=re.findall(r'stage=CPU_OUTPUT_FRAME_VERIFIED .*?task=(\S+) epoch=(\d+) pid=(\d+) uid=(\d+) sequence=(\d+) pts_us=(\d+)',logs)
assert [int(x[4]) for x in verified]==[1,2,3,4,5]
assert 'code=CPU_DECODE_FAILED phase=NATIVE_STAGE_5' in logs and 'cause_chain=java.io.IOException:CPU_NATIVE_REJECTED' in logs
assert 'stage=PIPE_VISUAL_CHECK' not in logs and 'stage=PIPE_CONTENT_FRAME' not in logs
starts=re.findall(r'stage=CPU_TASK_STARTED .*?task=(\S+) epoch=(\d+) pid=(\d+) uid=(\d+) kind=(\d+) mode=(\d+)',logs)
assert len(starts)==7 and [int(x[5]) for x in starts].count(10)==6 and [int(x[5]) for x in starts].count(11)==1
ledgers={}
for line in logs.splitlines():
    if 'stage=CPU_LEDGER ' in line:
        t=re.search(r'task=(\S+)',line).group(1);ledgers[t]=line
assert len(ledgers)==7
for line in ledgers.values():
    for field in ['stop_pending=false','pending_calls=0','actual_death=true','source_released=true','slot_released=true','operations=0','consumers=0','failed_closes=0','source_close=CLOSED']:assert field in line
def blocks(text):return {p:bytes.fromhex(h) for p,h in re.findall(r'HEX_BEGIN\|([^\n]+)\n(.*?)HEX_END',text,re.S)}
data=blocks(post);before=blocks((E/'03-post-observation-stdout.txt').read_text().replace('\r\n','\n'))
for path,b in before.items():
    if path!='files/e4a_output_budget/ledger.bin':assert data[path]==b,path
ledger=data['files/e4a_output_budget/ledger.bin'].decode();old=before['files/e4a_output_budget/ledger.bin'].decode();assert ledger.startswith(old)
assert ledger.count('\nR ')==2 and ledger.count('\nS ')==2
h=sha((ledger.splitlines()[0]+'\n').encode())
for line in ledger.splitlines()[1:]:p,v=line.rsplit(' ',1);assert sha((h+' '+p).encode())==v;h=v
budget=load(METHOD+'-client-result.json')['ledger'];assert budget['consumed']==53651 and budget['reserved']==0 and not budget['pending']
assert budget['records'][output_task]['sha']==outputsha and budget['records'][output_task]['state']=='ABORTED'
assert 'ABSENT|files/e4a_output_budget/operation.pending\n' in post
assert re.search(r'OUTPUT_STAT\|files/e4a_outputs/'+re.escape(output_task)+r'\.mp4\|64522,20174,53651,10221,8180,',post)
j=data['files/e4a_outputs/'+output_task+'.journal'];assert struct.unpack_from('>i',j,42)[0]==2
assert 'DATA_STAT|files/e4a_outputs/'+TASK+'.mp4|64522,20386,0,10221,8180,1792208948' in post
assert 'DATA_STAT|files/e4_fixtures/basic.mp4|64522,20198,349102,10221,8180,1792207996' in post
assert 'DATA_STAT|files/e4_fixtures/subtitle.avi|64522,20199,736454656,10221,8180,1792208513' in post
for later in ['normalAviSixRealFrames','capabilityDenialDoesNotOpenSource','cancelRejectsWrongEpochOversizeAndLateFrame']:
    assert not (E/(later+'-stage-attempt.json')).exists()
review=dict(method=METHOD,result='FAIL',dependentMethodsAdmitted=False,finding='E5C-REG-F01',priority='P1',failureStage='ISOLATED_ENCODED_OUTPUT_VALIDATION_NATIVE_STAGE_5',rootCause='UNKNOWN_NATIVE_REJECTION_DETAIL_NOT_EXPOSED',task=task,outputTask=output_task,received=6,inputs=6,outputs=6,status=status,error=error,resourcesReleased=True,terminalReason='ACTUAL_OWNERS_RETURNED',originalOwnerReturned=True,controlInFlight=0,remoteNativeLiveUnknownAllZero=True,allSevenCpuJobsReturned=True,sourceFrames=source,outputVerifiedFrames=verified,actualCpuJobs=starts,cpuReadRequestsAndBytes='NOT_COLLECTED_NOT_ZERO',outputBytes=53651,outputSha256=outputsha,outputInode=20174,ledger=budget,fixturePreAndCloseHashBytesInferredFromFrozenPath=698204,extraFixtureHashBytes=0,outputHashBytesInferredTwoPasses=107302,outputHashInference='pre-verifier digest and original-owner settlement digest; verifier post-digest not reached',junitSeconds=float(re.search(r'\nTime: ([0-9.]+)',s).group(1)),rawSha256=sha(raw),logcatSha256=sha(lograw),postStateSha256=sha((E/(METHOD+'-post-state-stdout.txt')).read_bytes()),oldN2MetadataExceptAppendOnlyLedgerUnchanged=True)
save(METHOD+'-independent-review.json',review)
rows=[json.loads(p.read_bytes()) for p in sorted(E.glob('*-receipt.json'))];assert len(rows)==8
assert all(r['clientReturned'] and r['exitCode']==0 and not r['overflow'] for r in rows)
total=sum(r['savedBytes'] for r in rows);assert total<32*1024*1024
summary=dict(result='OBSERVE_PASS_REGRESSION_0_PASS_1_FAIL_3_BLOCKED',observation=load('observation-independent-admission.json'),methods={METHOD:'FAIL','normalAviSixRealFrames':'BLOCKED_AFTER_MP4_FAIL','capabilityDenialDoesNotOpenSource':'BLOCKED_AFTER_MP4_FAIL','cancelRejectsWrongEpochOversizeAndLateFrame':'BLOCKED_NORMAL_RECEIPTS_NOT_ADMITTED'},findings=[dict(id='E5C-REG-F01',priority='P1',issue='SIX_ENCODED_SAMPLES_BUT_ISOLATED_OUTPUT_VALIDATOR_NATIVE_REJECTED_NO_READY')],ledger=budget,adbCalls=8,metadataCalls=6,instrumentationCalls=2,observationCalls=1,productCalls=1,batchLogBytes=total,allCurrentClientsReturned=True,inFlight=[],newProductOwnersReturned=True,sourceMediaFixtureHashBytesInferred=698204,declaredAllFourFixtureHashCeiling=1475003924,extraFixtureHashBytes=0,cpuJobs=7,cpuReadBytes='NOT_COLLECTED',newAbortOrReset=0,install=0,gradleOrModelRuns=0,oldN2FailureUnchanged=True,D1='NOT_PASSED',M0='NOT_STARTED')
save('final-independent-review.json',summary);print(json.dumps({k:summary[k] for k in ['result','methods','findings','adbCalls','batchLogBytes','newProductOwnersReturned','cpuJobs']}))
