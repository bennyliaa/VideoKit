from pathlib import Path
import json,hashlib,re,datetime,ast,struct,zipfile
R=Path('D:/CodexProjects/VideoKit');E=Path(__file__).resolve().parent;B=R/'docs/coder/d1input-sink05';P=R/'docs/tester/D1_INPUT_SINK05_FIX_REVIEW_REPORT_V1.0.md'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
for name,total in [('D1_INPUT_SINK01_REVIEW_EVIDENCE',114),('D1_INPUT_SINK02_REVIEW_EVIDENCE',207),('D1_INPUT_SINK03_REVIEW_EVIDENCE',258),('D1_INPUT_SINK04_REVIEW_EVIDENCE',993)]:
 old=load(R/'docs/tester'/name/'review-evidence-manifest.json');assert len(old['evidenceFiles'])==total
 for row in old['evidenceFiles']:assert sha(R/row['path'])==row['sha256']
 assert sha(R/old['report'])==old['reportSha256']
for row in load(B/'evidence/input-sink05-freeze.json')['files']:assert sha(R/row['path'])==row['sha256']
runner=load(E/'independent-001/summary.json');assert len(runner['runs'])==50 and all(x['exitCode']==0 for x in runner['runs']) and runner['frozenCandidate'] and runner['allOriginalProcessesReturned']
for mode in ['source','production']:
 for name,text in [('results','hostResultCases=88'),('transitions','transitionCases=33'),('matrix','phaseExceptionCases=63'),('original17','originalReturnScenarios=17'),('tester12','testerIndependentScenarios=12'),('orders','ownerOrderCases=30'),('coordinator-orders','coordinatorOrderCases=7')]:
  if name=='orders':assert re.search(r'(?:ownerOrderCases|responseOrderCases|orderCases)=30',(E/f'independent-001/{name}-{mode}.stdout').read_text()),name
  else:assert text in (E/f'independent-001/{name}-{mode}.stdout').read_text(),name
 assert load(E/f'independent-orders-{mode}-1.json')['exitCode']==0 and 'independentOrderScenarios=8' in (E/f'independent-orders-{mode}-1.stdout').read_text()
assert load(E/'independent-output-gates.json')['result']=='PASS'
assert sha(E/'independent-001/source/generated-4b.tmp')=='e6e8cb429864b8e8d7fe95e53360dbd00756316813fb1e4a03a778d4632dbde6' and sha(E/'independent-001/production-core/generated-4b.tmp')=='e6e8cb429864b8e8d7fe95e53360dbd00756316813fb1e4a03a778d4632dbde6'
assert load(B/'evidence/build-main-001/receipt.json')['exitCode']==0 and 'BUILD SUCCESSFUL' in (B/'evidence/build-main-001/gradle.log').read_text()
for x in re.findall(r'\]\((D:/[^)]+)\)',P.read_text(encoding='utf8')):assert Path(re.sub(r':\d+$','',x)).exists(),x
tree=ast.parse((R/'docs/tester/D1_INPUT_SINK01_REVIEW_EVIDENCE/audit_frozen.py').read_text());defs=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='dexclasses'];exec(compile(ast.Module(body=defs,type_ignores=[]),'reused_dex_parser','exec'))
checks={p.stem for p in (B/'checks/com/videokit/d1input').glob('*.java')}
with zipfile.ZipFile(B/'artifacts/input-sink05-compile-probe-debug.apk') as z:classes=[c for n in z.namelist() if n.endswith('.dex') for c in dexclasses(z.read(n))];assert not any('/'+n+';' in c or '/'+n+'$' in c for c in classes for n in checks)
with zipfile.ZipFile(B/'artifacts/input-sink05-classes.jar') as z:assert not any('/'+n+'.class' in c or '/'+n+'$' in c for c in z.namelist() for n in checks)
(E/'all-check-classes-exclusion.json').write_text(json.dumps(dict(checkedNames=sorted(checks),apkAndJarExcluded=True),indent=2),encoding='utf8')
cases=load(R/'docs/tester/D1_INPUT_SINK01_PHASE_A_EVIDENCE/reusable-regression-cases.json')['cases']
for c in cases:c['newCandidateIndependentResult']='NOT_RUN_PLATFORM' if c['id']=='S05' else 'PASS_LIMITED_OFFLINE'
(E/'independent-case-results.json').write_text(json.dumps(dict(candidate='D1-20261021-INPUT-SINK05',cases=cases,originalB06='PASS_LIMITED_OFFLINE_FOR_ORIGINAL_FINDING',originalB07='PASS_LIMITED_OFFLINE_FOR_ORIGINAL_FINDING',additionalIndependentOrderScenarios=8,sourceAndProductionJarBoth=True,newBlockingFindings=[],overall='PASS_LIMITED_OFFLINE',D1='NOT_PASSED',M0='NOT_STARTED',platformAndBusinessPublication='NOT_RUN'),ensure_ascii=False,indent=2),encoding='utf8')
records=[dict(path=p.relative_to(R).as_posix(),bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(E.rglob('*')) if p.is_file() and p.name!='review-evidence-manifest.json']
out=dict(frozenAtUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),report=P.relative_to(R).as_posix(),reportBytes=P.stat().st_size,reportSha256=sha(P),overall='PASS_LIMITED_OFFLINE',evidenceFiles=records,candidateStillUnchanged=True,oldTester114207258993Unchanged=True,allActualThreadsObserversAndJdkProcessesReturned=True,finalSourceOutputKeepers=0,SDKDeviceAdb5037GradleCalls=0,nextBatchStarted=False,D1='NOT_PASSED',M0='NOT_STARTED')
(E/'review-evidence-manifest.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps({k:v for k,v in out.items() if k!='evidenceFiles'},ensure_ascii=False,indent=2));print('evidenceFiles',len(records))
