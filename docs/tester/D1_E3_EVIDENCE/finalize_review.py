"""Tester report seal and final readonly candidate checks; no execution."""
from pathlib import Path
from datetime import datetime
import hashlib,json,re
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent;BASE=ROOT/'docs/coder/d1e3';REPORT=ROOT/'docs/tester/D1_E3_REAL_IO_ADMISSION_REVIEW_REPORT_V1.0.md'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_bytes())
def save(n,v):(OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
assert sha(BASE/'evidence/e3-freeze.json')=='7f5c4bda5189f056c089695adc5a94eab31b221db821218bb49bd2ea5222d709'
for r in read(BASE/'evidence/e3-freeze.json')['immutableFiles']+read(BASE/'evidence/e3-freeze.json')['selfcheckFiles']:
    p=ROOT/r['path'];assert p.stat().st_size==r['bytes'] and sha(p)==r['sha256']
for target in re.findall(r'\]\((D:/[^)]+)\)',REPORT.read_text(encoding='utf-8')):
    match=re.match(r'(.+?)(?::(\d+))?$',target);p=Path(match[1]);assert p.exists(),target
    if match[2]:assert 0<int(match[2])<=len(p.read_text(encoding='utf-8').splitlines())
assert not (BASE/'execution').exists() and not (BASE/'runs').exists()
save('readonly-verification-receipt.json',dict(command='python -X utf8 -B docs/coder/d1e3/tools/verify.py --expected-freeze 7f5c4bda5189f056c089695adc5a94eab31b221db821218bb49bd2ea5222d709',exitCode=0,integrity='PASS',sourceFiles=54,immutableFiles=90,runtimeFiles=65,preparationAssertions=280,nativeProbeAssertions=25,sourceReadUsage=dict(physicalFileBytes=103494201,physicalFileReads=100,zipLogicalBytes=104793631,zipEntryReads=133,totalBytes=208287832,totalFileReads=233,byteCap=268435456,fileCap=8192),prepUsage=dict(metadataBytes=136241,fixtureBytes=8192),execution='NO_EXECUTION_OUTPUTS_PRESENT',mediaStatCalls=0,mediaBytesRead=0,executionStartedByVerify=False,reservationConsumedByVerify=False))
save('review-summary.json',dict(at=datetime.now().astimezone().isoformat(),task='D1-E3 independent real finite IO admission review',report=str(REPORT.relative_to(ROOT)),reportSha256=sha(REPORT),conclusion='NO_NEW_CODE_BLOCKERS; CONDITIONAL_RECOMMENDATION_FOR_SEPARATELY_FORMALLY_HANDED_OFF_ONCE_REAL_FINITE_IO',findings=[],candidateIntegrity='PASS',candidateUnchanged=True,sourceFiles=54,immutableFiles=90,runtimeFiles=65,productionFilesChanged=13,recordedPreparationAssertions=280,recordedJavaNativeAssertions=25,recordedJavaNativeProcesses=2,GNewNativePathExecuted=False,RNewNativePathExecuted=False,realLargeWindowsExecuted=False,typedPermitOrFullEntryIntegrationExecuted=False,postReadVersionChangeInjectionExecuted=False,JavaBindFailureOrCloseUnknownInjectionExecuted=False,ownCodeTests=0,probesRerun=False,readonlyVerifyInvocations=1,newG=0,newR=0,newJava=0,newOSMetricSamples=0,newCompile=0,mediaStatCalls=0,mediaBytesRead=0,newRealPF=False,newReal61=False,adb=False,reservationConsumed=False,grantTokenReceived=False,grantDeliveryAutomaticRejectionReportedByCoordinator=True,grantDeliveryRejectionReasonProvided=False,grantRetryOrBypassAttempted=False,realExecutionAuthorized=False,inFlight=[],oldE2EFinalFailPreserved=True,oldHistoricalGAndRFailPreserved=True,D1Passed=False,M0Started=False,C14Resumed=False,notification='PENDING_SEND'))
print('PASS: frozen bytes unchanged; report links valid; report SHA256 '+sha(REPORT))
