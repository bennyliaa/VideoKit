"""Final readonly checks and tester report seal, no runtime imports or new execution."""
from pathlib import Path
from datetime import datetime
import hashlib,json,re
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent;BASE=ROOT/'docs/coder/d1e2e'
REPORT=ROOT/'docs/tester/D1_E2E_ACTUAL_REGRESSION_REPORT_V1.0.md'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_bytes())
def save(n,v):(OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
assert sha(BASE/'evidence/e2e-freeze.json')=='aa59420cff4153395af2ab9b97eb47d8f560e91763b730f47c0fda3c0578b66a'
for r in read(BASE/'evidence/e2e-freeze.json')['immutableFiles']:
    p=ROOT/r['path'];assert p.stat().st_size==r['bytes'] and sha(p)==r['sha256']
for target in re.findall(r'\]\((D:/[^)]+)\)',REPORT.read_text(encoding='utf-8')):
    match=re.match(r'(.+?)(?::(\d+))?$',target);p=Path(match[1]);assert p.exists(),target
    if match[2]:assert 0<int(match[2])<=len(p.read_text(encoding='utf-8').splitlines())
result=read(OUT/'independent-results-audit.json')
assert sha(BASE/'execution/result-manifest.json')==result['resultManifestSha256']
save('readonly-verify-receipts.json',dict(command='python -X utf8 -B docs/coder/d1e2e/tools/verify.py --expected-freeze aa59420cff4153395af2ab9b97eb47d8f560e91763b730f47c0fda3c0578b66a',before=dict(exitCode=0,integrity='PASS',execution='NO_EXECUTION_OUTPUTS_PRESENT'),after=dict(exitCode=0,integrity='PASS',execution='EXISTING_RESULT_MANIFEST_RECONCILED',reportedStatus='FAIL',outputFiles=146,finalAggregateUsageVerified=True),meaning='Readonly verifier PASS is not execution PASS; neither invocation consumes or runs the actual batch'))
save('review-summary.json',dict(at=datetime.now().astimezone().isoformat(),task='D1-E2E one actual authored-file 61-scenario regression',report=str(REPORT.relative_to(ROOT)),reportSha256=sha(REPORT),conclusion='FAIL_PRESERVED_E2E_F01_WRAPPER_COUNTS_PF_PLUS_61_AS_INCOMPLETE',findings=[dict(id='E2E-F01',priority='P1',file='docs/coder/d1e2e/tools/e2e_driver.py',line=155,reason='Normal PF+61 is 62 checkpoints; wrapper requires61',remedy='Separate and validate PF, exact ordered61 scenario set, and original GCn32 completion; offline finite correction only unless separately dispatched')],candidateIntegrity='PASS',candidateUnchanged=True,actualAttempts=1,permissionConsumed=True,refund=False,secondAttemptAuthorized=False,completedScenarios=61,checkpointRowsIncludingPF=62,originalAssertions=160,fullBatchPasses=0,originalPrecloseStatus='PASS',originalDriverStatus='FAIL',originalGExitCode=2,originalCommandExitCode=1,independentOutputValidation='PASS',resultManifestSha256=result['resultManifestSha256'],sourceFiles=73,immutableFiles=90,newCompile=0,newDiagnosticRuns=0,mockUsed=False,realMediaIO=False,realMediaStat=False,adb=False,thresholdsChanged=False,GCForced=False,inFlight=[],D1Passed=False,M0Started=False,C14Resumed=False,notification='PENDING_SEND'))
print('PASS: immutable seal unchanged, report links valid; report SHA256 '+sha(REPORT))
