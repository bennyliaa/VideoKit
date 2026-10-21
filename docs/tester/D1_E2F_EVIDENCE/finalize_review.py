"""Finalize tester review with readonly hashes and links. No candidate execution."""
from pathlib import Path
from datetime import datetime
import hashlib,json,re
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent;BASE=ROOT/'docs/coder/d1e2f'
REPORT=ROOT/'docs/tester/D1_E2F_REEVALUATION_REVIEW_REPORT_V1.0.md'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_bytes())
def save(n,v):(OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
assert sha(BASE/'evidence/freeze-summary.json')=='1a73391a12f9473f661a5e62204218d5a875031f064bb12af262529c4e866dee'
for r in read(BASE/'evidence/freeze-summary.json')['files']:
    p=ROOT/r['path'];assert p.stat().st_size==r['bytes'] and sha(p)==r['sha256']
assert read(OUT/'readonly-recomputed.json')==read(BASE/'reevaluation/evidence-reevaluation.json')
for target in re.findall(r'\]\((D:/[^)]+)\)',REPORT.read_text(encoding='utf-8')):
    match=re.match(r'(.+?)(?::(\d+))?$',target);p=Path(match[1]);assert p.exists(),target
    if match[2]:assert 0<int(match[2])<=len(p.read_text(encoding='utf-8').splitlines())
old=ROOT/'docs/coder/d1e2e'
assert sha(old/'evidence/e2e-freeze.json')=='aa59420cff4153395af2ab9b97eb47d8f560e91763b730f47c0fda3c0578b66a'
assert sha(old/'execution/result-manifest.json')=='baa6a1ed87764a5d16b1d282717824110d0082bc188606edf4affb33377750ea'
assert sha(ROOT/'docs/tester/D1_E2E_ACTUAL_REGRESSION_REPORT_V1.0.md')=='bb1042940d9c6376bf019c73d95c7001a6887feddc998fe834cffd968c65a2d3'
save('readonly-verification-receipt.json',dict(verify=dict(exitCode=0,integrity='PASS',expectedFreeze='1a73391a12f9473f661a5e62204218d5a875031f064bb12af262529c4e866dee',sourceFiles=79,immutableFiles=98,sourceReadBytesCombined=260535062,sourceReadFilesCombined=277,metadataBytes=143649),reevaluate=dict(exitCode=0,readOnly=True,scope='EVIDENCE_REEVALUATION',decision='SUPPORTED_ORIGINAL_TOOL_FACTS',equalsRecordedResult=True),negativeChecksRerun=False,newActualAttempts=0,newOSMetricSamples=0))
save('review-summary.json',dict(at=datetime.now().astimezone().isoformat(),task='D1-E2F independent offline decision and original evidence reevaluation review',report=str(REPORT.relative_to(ROOT)),reportSha256=sha(REPORT),conclusion='OFFLINE_F01_DECISION_CLOSED; NO_NEW_BLOCKING_FINDINGS; RECOMMEND_LIMITED_RELIANCE_ON_ORIGINAL_TOOL_FACTS_SUBJECT_TO_COORDINATOR_DECISION',findings=[],F01ClosedWithin='New offline decision only; old actual driver unchanged; future integration NOT_RUN',candidateIntegrity='PASS',candidateUnchanged=True,sourceFiles=79,immutableFiles=98,recordedOfflineAssertions=452,recordedNegativeCases=175,negativeChecksRerun=False,readOnlyRecomputations=1,readOnlyVerifyInvocations=1,recomputedEqualsRecorded=True,originalBatchStatus='FAIL',originalGExitCode=2,originalToolExitCode=1,originalAssertions=160,originalReservationConsumed=True,originalFullBatchPasses=0,newActualAttempts=0,newActualPasses=0,newG=0,helpersStarted=0,newOSMetricSamples=0,compileInvocations=0,originalEvidenceWrites=0,inFlight=[],newExecutionAuthorized=False,perQueryDurationRecorded=False,perCycleDurationPidRecorded=False,separateIOJoinBooleanRecorded=False,continuousKernelPeakProven=False,D1Passed=False,M0Started=False,C14Resumed=False,notification='PENDING_SEND'))
print('PASS: unchanged E2F/E2E seal and report; recomputation identical; valid links; report SHA256 '+sha(REPORT))
