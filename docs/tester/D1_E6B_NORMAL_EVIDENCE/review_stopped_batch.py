"""Review completed evidence, no new device/media actions; stop on AVI Before block."""
from pathlib import Path
import json,re,hashlib
E=Path(__file__).resolve().parent
def sha(b):return hashlib.sha256(b).hexdigest()
def txt(n):return (E/n).read_text(encoding='utf-8').replace('\r\n','\n')
def load(n):return json.loads((E/n).read_bytes())
def save(n,v):
    with (E/n).open('x',encoding='utf-8') as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')
def blocks(s):return {p:bytes.fromhex(h) for p,h in re.findall(r'HEX_BEGIN\|([^\n]+)\n(.*?)HEX_END',s,re.S)}
m='normalAviSixRealFrames';s=txt(m+'-instrumentation-stdout.txt');logs=txt(m+'-logcat-stdout.txt');post=txt(m+'-post-state-stdout.txt')
assert 'E4 FINAL_OBSERVATION BLOCKED WRITER_DEATH:IOException:E5A_RECOVERY_WRITER_DEATH_UNPROVEN' in s
assert 'FAILURES!!!' in s and 'Tests run: 1,  Failures: 1' in s and 'E4DeviceTests.selectedFormalCaseOnly(E4DeviceTests.java:71)' in s
assert all(x not in s for x in ['E4 FIXTURE','E4 REPORT','E4 TERMINAL_EXIT'])
assert all(x not in logs for x in ['stage=CPU_TASK_STARTED','stage=E4_SOURCE_FRAME','stage=E6_NATIVE_DIAGNOSTIC'])
a=blocks(post);b=blocks(txt('normalMp4SixRealFrames-post-state-stdout.txt'))
assert a['files/e4a_output_budget/ledger.bin']==b['files/e4a_output_budget/ledger.bin']
for p,v in a.items():assert p in b and v==b[p],p
assert 'ABSENT|files/e4a_output_budget/operation.pending\n' in post
mp4=load('normalMp4SixRealFrames-independent-review.json');budget=load(m+'-client-result.json')['ledger'];assert budget==load('normalMp4SixRealFrames-client-result.json')['ledger']
for later in ['capabilityDenialDoesNotOpenSource','cancelRejectsWrongEpochOversizeAndLateFrame']:
    assert not (E/(later+'-stage-attempt.json')).exists()
avi=dict(method=m,result='BLOCKED_BEFORE_TEST_BODY',junit='FAIL_1_OF_1',dependentMethodsAdmitted=False,phase='BEFORE_FINAL_OBSERVATION_WRITER_DEATH',finding='E6B-OBS-F01',priority='P1',error='E5A_RECOVERY_WRITER_DEATH_UNPROVEN',observerHostPid=11809,originalWriterPid=4869,originalWriterUid=10221,originalWriterRecordedAt=1792224193301,rootCause='UNKNOWN_CURRENT_EXITINFO_MATCH_COUNT_AND_REASON_NOT_EXPOSED',mediaFixtureOrProductSessionStarted=False,newCpuJobs=0,newOutputReservations=0,newConsumedBytes=0,observerActualReturn='NOT_PROVEN_FAILED_OBSERVATION_NOT_ADMITTED',ledger=budget,junitSeconds=float(re.search(r'\nTime: ([0-9.]+)',s)[1]),rawSha256=sha((E/(m+'-instrumentation-stdout.txt')).read_bytes()),logcatSha256=sha((E/(m+'-logcat-stdout.txt')).read_bytes()),postStateSha256=sha((E/(m+'-post-state-stdout.txt')).read_bytes()))
save(m+'-independent-review.json',avi)
rows=[dict(name=p.name,**json.loads(p.read_bytes())) for p in sorted(E.glob('*-receipt.json'))]
assert len(rows)==19 and all(x['clientReturned'] and x['exitCode']==0 and not x['overflow'] for x in rows)
summary=dict(result='ONE_NORMAL_PASS_ONE_BEFORE_BLOCK_TWO_DEPENDENTS_NOT_RUN',methods={'normalMp4SixRealFrames':'PASS','normalAviSixRealFrames':'BLOCKED_BEFORE_BODY_JUNIT_FAIL','capabilityDenialDoesNotOpenSource':'NOT_RUN_BLOCKED_AFTER_AVI','cancelRejectsWrongEpochOversizeAndLateFrame':'NOT_RUN_NO_TWO_NORMAL_RECEIPT'},findings=[dict(id='E6B-OBS-F01',priority='P1',issue='NEXT_HOST_ORIGINAL_RECOVERY_WRITER_DEATH_PROOF_UNAVAILABLE')],mp4=mp4,avi=avi,ledger=budget,adbCalls=len(rows),installCalls=2,instrumentationCalls=2,metadataCalls=15,batchLogBytes=sum(x['receivedBytes'] for x in rows),receipts=rows,sourceFixtureHashBytesInferred=349102*2,extraMediaOrFixtureHashBytes=0,mp4OutputDigestReadsInferred=3,mp4OutputDigestBytesInferred=53567*3,allAdbClientsReturned=True,inFlight=[],newQueryAbortStandaloneObserveG01=0,productRetries=0,gradleNativeModelRuns=0,sourceCpuReadCalls=mp4['cpuReadCalls'],sourceCpuCompressedBytes=mp4['cpuCompressedBytes'],twoNormalReceipt='NOT_CREATED_NOT_ADMITTED',D1='NOT_PASSED',M0='NOT_STARTED')
save('final-independent-review.json',summary)
save('two-normal-receipt-status.json',dict(status='NOT_CREATED_NOT_ADMITTED',reason='AVI blocked in Before; only one actual normal PASS',cancelAdmitted=False,normalReceiptSha256=None))
print(json.dumps({k:summary[k] for k in ['result','methods','ledger','adbCalls','batchLogBytes','twoNormalReceipt']}))
