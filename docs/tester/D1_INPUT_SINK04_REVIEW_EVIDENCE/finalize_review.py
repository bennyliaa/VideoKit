from pathlib import Path
import json,hashlib,re,datetime,ast,struct,zipfile
R=Path('D:/CodexProjects/VideoKit');E=Path(__file__).resolve().parent;B=R/'docs/coder/d1input-sink04';P=R/'docs/tester/D1_INPUT_SINK04_FIX_REVIEW_REPORT_V1.0.md'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
for name,total in [('D1_INPUT_SINK01_REVIEW_EVIDENCE',114),('D1_INPUT_SINK02_REVIEW_EVIDENCE',207),('D1_INPUT_SINK03_REVIEW_EVIDENCE',258)]:
 old=load(R/'docs/tester'/name/'review-evidence-manifest.json');assert len(old['evidenceFiles'])==total
 for row in old['evidenceFiles']:assert sha(R/row['path'])==row['sha256']
 assert sha(R/old['report'])==old['reportSha256']
for row in load(B/'evidence/input-sink04-freeze.json')['files']:assert sha(R/row['path'])==row['sha256']
runner=load(E/'independent-001/summary.json');assert len(runner['runs'])==42 and all(r['exitCode']==0 for r in runner['runs']) and runner['frozenCandidate'] and runner['allOriginalProcessesReturned']
for mode in ['source','production']:
 for name,text in [('results','hostResultCases=88'),('transitions','transitionCases=33'),('matrix','phaseExceptionCases=63'),('original17','originalReturnScenarios=17'),('tester12','testerIndependentScenarios=12')]:assert text in (E/f'independent-001/{name}-{mode}.stdout').read_text()
 assert 'independentResultCases=8' in (E/f'host-samples-{mode}.stdout').read_text()
for name,key in [('late-ready-contradictory_aborted-source-1','LATE_READY_CONTRADICTS_CONFIRMED_ABORTED'),('late-ready-contradictory_aborted-production','LATE_READY_CONTRADICTS_CONFIRMED_ABORTED'),('late-ready-normal_query_ready-source-1','PENDING_ORIGINAL_READY_ACK_RAW_EXCEPTION'),('late-ready-normal_query_ready-production','PENDING_ORIGINAL_READY_ACK_RAW_EXCEPTION')]:assert load(E/(name+'.json'))['exitCode']==0 and key in (E/(name+'.stdout')).read_text()
gate=load(E/'independent-output-gates.json');assert gate['result']=='PASS' and len(gate['rows'])==14
assert sha(E/'independent-001/source/generated-4b.tmp')=='e6e8cb429864b8e8d7fe95e53360dbd00756316813fb1e4a03a778d4632dbde6' and sha(E/'independent-001/production-core/generated-4b.tmp')=='e6e8cb429864b8e8d7fe95e53360dbd00756316813fb1e4a03a778d4632dbde6'
assert load(B/'evidence/build-main-001/receipt.json')['exitCode']==0 and 'BUILD SUCCESSFUL' in (B/'evidence/build-main-001/gradle.log').read_text()
for x in re.findall(r'\]\((D:/[^)]+)\)',P.read_text(encoding='utf8')):assert Path(re.sub(r':\d+$','',x)).exists(),x
tree=ast.parse((R/'docs/tester/D1_INPUT_SINK01_REVIEW_EVIDENCE/audit_frozen.py').read_text());defs=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='dexclasses'];exec(compile(ast.Module(body=defs,type_ignores=[]),'reused_dex_parser','exec'))
checks={p.stem for p in (B/'checks/com/videokit/d1input').glob('*.java')}
with zipfile.ZipFile(B/'artifacts/input-sink04-compile-probe-debug.apk') as z:classes=[c for n in z.namelist() if n.endswith('.dex') for c in dexclasses(z.read(n))];assert not any('/'+n+';' in c or '/'+n+'$' in c for c in classes for n in checks)
with zipfile.ZipFile(B/'artifacts/input-sink04-classes.jar') as z:assert not any('/'+n+'.class' in c or '/'+n+'$' in c for c in z.namelist() for n in checks)
(E/'all-check-classes-exclusion.json').write_text(json.dumps(dict(checkedNames=sorted(checks),apkAndJarExcluded=True),indent=2),encoding='utf8')
cases=load(R/'docs/tester/D1_INPUT_SINK01_PHASE_A_EVIDENCE/reusable-regression-cases.json')['cases']
for c in cases:c['newCandidateIndependentResult']='NOT_RUN_PLATFORM' if c['id']=='S05' else 'PARTIAL_FAIL_B07' if c['id']=='S03' else 'PARTIAL_FAIL_B06_B07' if c['id']=='S06' else 'PASS_LIMITED_OFFLINE'
(E/'independent-case-results.json').write_text(json.dumps(dict(candidate='D1-20261021-INPUT-SINK04',cases=cases,originalB05='PASS_LIMITED_OFFLINE_FOR_ORIGINAL_FINDING',originalC01='PASS',newFindings=[dict(id='B06',priority='P2',scope='Late READY contradicts confirmed ABORTED'),dict(id='B07',priority='P2',scope='Pending original READY response raises unchecked coordinator exception')],overall='FAIL',platformAndBusinessPublication='NOT_RUN'),ensure_ascii=False,indent=2),encoding='utf8')
records=[dict(path=p.relative_to(R).as_posix(),bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(E.rglob('*')) if p.is_file() and p.name!='review-evidence-manifest.json']
out=dict(frozenAtUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),report=P.relative_to(R).as_posix(),reportBytes=P.stat().st_size,reportSha256=sha(P),overall='FAIL',evidenceFiles=records,candidateStillUnchanged=True,oldTester114207258Unchanged=True,actualThreadsAndJdkProcessesReturned=True,finalValidChecksSourceOutputKeepers=0,initialTesterAssertionFailure='Preserved exit1; incorrect test cleanup token left memory-only keeper in that failed JVM; explicitly not treated as a return proof; corrected final dual-path checks actually joined and returned original owner',SDKDeviceAdb5037GradleCalls=0,nextBatchStarted=False)
(E/'review-evidence-manifest.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps({k:v for k,v in out.items() if k!='evidenceFiles'},ensure_ascii=False,indent=2));print('evidenceFiles',len(records))
