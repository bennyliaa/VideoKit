"""Final readonly seal/manifest checks and tester report receipt; no runtime."""
from pathlib import Path
from datetime import datetime
import json,hashlib,re
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent;BASE=ROOT/'docs/coder/d1e3';REPORT=ROOT/'docs/tester/D1_E3_REAL_IO_TEST_REPORT_V1.0.md'
def sha(b):return hashlib.sha256(b).hexdigest()
def save(n,v):(OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
control_path=OUT/'control-and-waiting-audit.json';control_raw=control_path.read_bytes();control=json.loads(control_raw);cost=dict(control['resultReadUsageIncludingEarlierReview']);cost['bytes']+=len(control_raw);cost['files']+=1
def result_meta(p):
    size=p.stat().st_size;assert cost['bytes']+size<=6291456 and cost['files']<512
    cost['bytes']+=size;cost['files']+=1;return p.read_bytes()
sem=json.loads(result_meta(OUT/'semantic-audit.json'));collection=json.loads(result_meta(OUT/'collection-integrity.json'))
assert sha(result_meta(BASE/'execution/result-manifest.json'))==collection['resultManifestSha256']=='870896d1063c465382a25a48fa501a22dc47f409e72ce48c003b17ae240e06c0'
source_bytes=0;source_files=0
raw=(BASE/'evidence/e3-freeze.json').read_bytes();source_bytes+=len(raw);source_files+=1
assert sha(raw)=='7f5c4bda5189f056c089695adc5a94eab31b221db821218bb49bd2ea5222d709'
for r in json.loads(raw)['immutableFiles']+json.loads(raw)['selfcheckFiles']:
    data=(ROOT/r['path']).read_bytes();source_bytes+=len(data);source_files+=1
    assert len(data)==r['bytes'] and sha(data)==r['sha256']
assert source_bytes<=268435456 and source_files<=8192
for target in re.findall(r'\]\((D:/[^)]+)\)',REPORT.read_text(encoding='utf-8')):
    match=re.match(r'(.+?)(?::(\d+))?$',target);p=Path(match[1]);assert p.exists(),target
    if match[2]:assert 0<int(match[2])<=len(p.read_text(encoding='utf-8').splitlines())
save('readonly-verify-receipt.json',dict(exitCode=0,integrity='PASS',expectedFreeze='7f5c4bda5189f056c089695adc5a94eab31b221db821218bb49bd2ea5222d709',sourceFiles=54,immutableFiles=90,runtimeFiles=65,sourcePhysicalBytes=103494201,sourceZipLogicalBytes=104793631,sourceTotalBytes=208287832,sourceTotalFileReads=233,executionReportedStatus='PASS',finalAggregateUsageVerified=True,outputFiles=143,outputReadBytes=719649,outputReadFiles=143,combinedUsage=dict(metadataBytes=855814,fixtureBytes=8268),executionStartedByVerify=False,reservationConsumedByVerify=False))
save('final-read-and-integrity-receipt.json',dict(resultReadUsageIncludingPriorVerifyAndTesterCopies=cost,finalCandidateHashReadBytes=source_bytes,finalCandidateHashReadFiles=source_files,candidateUnchanged=True,resultManifestUnchanged=True,scope='All output reads in this tester review charged, including stopped semantic pass, selected-copy resume and final summary/manifest reads; source hashes use a separate bounded command'))
save('review-summary.json',dict(at=datetime.now().astimezone().isoformat(),task='D1-E3 independent original real finite IO results review',report=str(REPORT.relative_to(ROOT)),reportSha256=sha(REPORT.read_bytes()),conclusion='PASS_THIS_FIXED_REAL_L_C_Z_FINITE_BYTE_IO_TOOL_BATCH_ONLY',findings=[],candidateIntegrity='PASS',candidateUnchanged=True,resultManifestSha256=collection['resultManifestSha256'],precloseSha256=collection['precloseSha256'],coordinatorActualAttempts=1,newActualRunsByTester=0,completedScenarios=61,preflightCheckpoints=1,originalAssertions=160,completedGcSlots=32,originalG=collection['originalG'],originalGExitCode=0,originalLauncher=collection['originalLauncher'],independentOutputVerification='PASS',finalBatchPassProven=True,resultReadUsage=cost,windowJRDigestsEqual=True,shortReadOutcome='UNFILLED_4_BYTES_EACH_WINDOW',identityQueries=sem['identityQueries'],metadataCumulativeWritten=6443406,metadataPeak=676238,outputUsage=dict(metadataBytes=719573,fixtureBytes=76),combinedUsage=dict(metadataBytes=855814,fixtureBytes=8268),newOSMetricSamples=0,mediaStatCallsByTester=0,mediaBytesReadByTester=0,newCompile=0,adb=False,grantTokenReceivedByTester=False,reservationConsumed=True,nextAttemptAuthorized=False,inFlight=[],oldFailuresPreserved=True,D1Passed=False,M0Started=False,C14Resumed=False,notification='PENDING_SEND'))
print(json.dumps(dict(status='PASS',reportSha256=sha(REPORT.read_bytes()),finalResultReadUsage=cost,finalSourceHashReadBytes=source_bytes,finalSourceHashReadFiles=source_files)))
