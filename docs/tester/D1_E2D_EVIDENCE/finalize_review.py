"""Seal tester report; readonly final candidate recheck. No candidate execution."""
from pathlib import Path
import hashlib,json,re
from datetime import datetime
ROOT=Path(__file__).resolve().parents[3]; OUT=Path(__file__).resolve().parent
BASE=ROOT/'docs/coder/d1e2d'; REPORT=ROOT/'docs/tester/D1_E2D_G_OS_REVIEW_REPORT_V1.0.md'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_bytes())
def save(n,v):(OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for r in read(BASE/'evidence/freeze-summary.json')['files']+read(BASE/'evidence/source-manifest.json')['files']:
    p=ROOT/r['path'];assert p.stat().st_size==r['bytes'] and sha(p)==r['sha256']
assert sha(BASE/'evidence/freeze-summary.json')=='f0a3e8fc9ae7e6e8c3def52d0002d23af77212ad35cb016a612e34e45f42de1b'
assert sha(BASE/'artifacts/E2D-source.zip')=='6c6eef8c0d9541aefe1eb807a312d1fce7ba968038c127e565af9becd7ccf9d8'
for target in re.findall(r'\]\((D:/[^)]+)\)',REPORT.read_text(encoding='utf-8')):
    match=re.match(r'(.+?)(?::(\d+))?$',target); p=Path(match[1]); assert p.exists(),target
    if match[2]:assert 0<int(match[2])<=len(p.read_text(encoding='utf-8').splitlines())
binding=read(BASE/'evidence/production-binding.json')
g=read(BASE/'evidence/g-comparison-1792174935530529100.json')
diagnostic=sum(p.stat().st_size for p in (BASE/'evidence').glob('g-comparison*.json'))+(BASE/'evidence/production-binding.json').stat().st_size
assert diagnostic==109229
assert read(BASE/'evidence/freeze-summary.json')['logsAndEvidenceBytesIncludingSeal']==268089
save('verify-receipt.json',dict(command='python -B -X utf8 docs/coder/d1e2d/tools/verify.py',exitCode=0,result='PASS',sourceFiles=63,frozenFiles=32,selfcheckFiles=0,comparisonStatus=g['status'],actualFullStatus='NOT_RUN',actualFullAssertions=0,targetedAssertions=0,compileInvocations=0,productionChanges=0,scope='Inspected readonly verifier only; original execution returned PASS'))
save('review-summary.json',dict(at=datetime.now().astimezone().isoformat(),task='D1-E2D independent postfix G OS comparison review',report=str(REPORT.relative_to(ROOT)),reportSha256=sha(REPORT),conclusion='RECORDED_SIX_POINT_REFERENCE_IMPROVEMENT_SUPPORTED; NO_NEW_BLOCKING_FINDINGS; RECOMMEND_SEPARATELY_DISPATCHED_ONCE_NEW_ACTUAL_61_SELF_OWNED_FILE_REGRESSION',findings=[],candidateIntegrity='PASS',candidateUnchanged=True,diagnosticGInstances=1,recordedOSPoints=6,smallProbeTotal=9,smallProbePeak=8,ownFunctionalTests=0,newSampling=False,selfcheckRerun=False,PFStarted=False,mediaIO=False,mediaStat=False,build=False,adb=False,newHelperProcesses=0,newWorkerThreads=0,inFlight=[],diagnosticBytes=diagnostic,logsAndEvidenceBytesIncludingSeal=268089,oldG369FailPreserved=True,oldR519FailPreserved=True,exactCBackend='UNKNOWN',handleTypeCausality='UNKNOWN',actualFullAuthorized=False,realExperimentAuthorized=False,thresholdsChanged=False,D1Passed=False,M0Started=False,C14Resumed=False,notification='PENDING_SEND'))
print('PASS: frozen bytes unchanged; report links valid; report SHA256 '+sha(REPORT))
