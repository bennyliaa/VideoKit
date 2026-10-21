from pathlib import Path
import json,hashlib,re,datetime
R=Path('D:/CodexProjects/VideoKit');E=Path(__file__).resolve().parent;B=R/'docs/coder/d1input-sink02';P=R/'docs/tester/D1_INPUT_SINK02_FIX_REVIEW_REPORT_V1.0.md'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
old=load(R/'docs/tester/D1_INPUT_SINK01_REVIEW_EVIDENCE/review-evidence-manifest.json')
for row in old['evidenceFiles']:assert sha(R/row['path'])==row['sha256']
assert len(old['evidenceFiles'])==114 and sha(R/old['report'])==old['reportSha256']
for row in load(B/'evidence/input-sink02-freeze.json')['files']:assert sha(R/row['path'])==row['sha256']
for mode in ['source','production']:
 assert 'testerIndependentScenarios=12' in (E/f'tester-independent-{mode}.stdout').read_text()
 assert 'originalReturnScenarios=17' in (E/f'coder-boundaries-{mode}.stdout').read_text()
 assert 'sourceKeepers0 outputKeepers0' in (E/f'readbackreturncheck-{mode}.stdout').read_text()
 for phase in ['write','flush','close','reopen','validate','commit']:assert 'REPRO CANCELLED_ACK_UNCONSUMED' in (E/f'cancelled-{phase}-{mode}.stdout').read_text()
 for phase in ['abort','query','abort_error']:assert 'REPRO ABORT_QUERY_FAILURE_HISTORY_LOST' in (E/f'history-{phase}-{mode}.stdout').read_text()
 assert 'REPRO LATE_CANCELLED_ACK' in (E/f'latecancelledackcheck-{mode}.stdout').read_text()
assert 'groups=20' in (E/'independent-001/checks.stdout').read_text() and 'groups=20' in (E/'production-core.stdout').read_text()
for n in ['independent-001/generated-4b.tmp','production-core/generated-4b.tmp']:assert sha(E/n)=='e6e8cb429864b8e8d7fe95e53360dbd00756316813fb1e4a03a778d4632dbde6'
assert load(B/'evidence/build-main-001/receipt.json')['exitCode']==0 and 'BUILD SUCCESSFUL' in (B/'evidence/build-main-001/gradle.log').read_text()
for x in re.findall(r'\]\((D:/[^)]+)\)',P.read_text(encoding='utf8')):assert Path(re.sub(r':\d+$','',x)).exists(),x
cases=load(R/'docs/tester/D1_INPUT_SINK01_PHASE_A_EVIDENCE/reusable-regression-cases.json')['cases']
for c in cases:c['newCandidateIndependentResult']='NOT_RUN_PLATFORM' if c['id']=='S05' else 'PARTIAL_FAIL_B03_B04' if c['id'] in ['S03','S06'] else 'PARTIAL_FAIL_B03' if c['id'] in ['S01','S04'] else 'PASS_LIMITED_OFFLINE'
(E/'independent-case-results.json').write_text(json.dumps(dict(candidate='D1-20261021-INPUT-SINK02',cases=cases,matrixTotal=19,originalB01='PASS_LIMITED_OFFLINE',originalB02='PASS_LIMITED_OFFLINE_FOR_ORIGINAL_FINDING',newFindings=[dict(id='B03',priority='P2',scope='Cancellation ACK consumption/redaction'),dict(id='B04',priority='P2',scope='ABORT/QUERY first failure history')],independentDistinctScenarios=23,independentPassingScenarios=13,independentDefectReproductionScenarios=10,bothSourceAndProductionJar=True,overall='FAIL',actualAndroidAndBusinessCommit='NOT_RUN'),ensure_ascii=False,indent=2),encoding='utf8')
records=[dict(path=p.relative_to(R).as_posix(),bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(E.rglob('*')) if p.is_file() and p.name!='review-evidence-manifest.json']
out=dict(frozenAtUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),report=P.relative_to(R).as_posix(),reportBytes=P.stat().st_size,reportSha256=sha(P),overall='FAIL',candidateStillUnchanged=True,oldTesterEvidenceFilesUnchanged=114,evidenceFiles=records,allOriginalJdkProcessesReturned=True,allActualControlledThreadsJoined=True,cancelledAckLogicalKeepers='Actual retained1 failure preserved inside isolated JVM; JVM then exited; no manual product-state deletion',deviceSdkAdb5037GradleCalls=0,nextBatchStarted=False)
(E/'review-evidence-manifest.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps({k:v for k,v in out.items() if k!='evidenceFiles'},ensure_ascii=False,indent=2));print('evidenceFiles',len(records))
