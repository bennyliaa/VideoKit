from pathlib import Path
import json,hashlib,re,datetime,ast,struct,zipfile
R=Path('D:/CodexProjects/VideoKit');E=Path(__file__).resolve().parent;B=R/'docs/coder/d1input-sink03';P=R/'docs/tester/D1_INPUT_SINK03_FIX_REVIEW_REPORT_V1.0.md'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
for name,total in [('D1_INPUT_SINK01_REVIEW_EVIDENCE',114),('D1_INPUT_SINK02_REVIEW_EVIDENCE',207)]:
 old=load(R/'docs/tester'/name/'review-evidence-manifest.json');assert len(old['evidenceFiles'])==total
 for row in old['evidenceFiles']:assert sha(R/row['path'])==row['sha256']
 assert sha(R/old['report'])==old['reportSha256']
for row in load(B/'evidence/input-sink03-freeze.json')['files']:assert sha(R/row['path'])==row['sha256']
for name in ['IndependentFixCheck.java','ReadbackReturnCheck.java']:assert (B/'checks/com/videokit/d1input'/name).read_bytes()==(R/'docs/tester/D1_INPUT_SINK02_REVIEW_EVIDENCE'/name).read_bytes()
for mode in ['source','production']:
 for f,marker in [('core','groups=20'),('original17','originalReturnScenarios=17'),('tester12','testerIndependentScenarios=12'),('readback','sourceKeepers0 outputKeepers0'),('input5','inputExceptionCases=5'),('matrix63','phaseExceptionCases=63'),('independent-authority','independentAuthorityScenarios=3'),('independent-cancel','independent_cancel_cases=6')]:assert marker in (E/f'{f}-{mode}.stdout').read_text(),f
 for phase in ['write','flush','close','reopen','validate','commit']:assert f'PASS tester_cancel_{phase.upper()}' in (E/f'cancel-{phase}-{mode}.stdout').read_text()
 for phase in ['abort','query','abort_error']:assert 'PASS tester_history' in (E/f'history-{phase}-{mode}.stdout').read_text()
 for case in ['null','empty_ready']:assert 'REPRO QUERY_RESULT_NOT_VALIDATED' in (E/f'invalid-query-{case}-{mode}.stdout').read_text()
 assert sha(E/f'core-{mode}/generated-4b.tmp')=='e6e8cb429864b8e8d7fe95e53360dbd00756316813fb1e4a03a778d4632dbde6'
for x in re.findall(r'\]\((D:/[^)]+)\)',P.read_text(encoding='utf8')):assert Path(re.sub(r':\d+$','',x)).exists(),x
assert load(B/'evidence/build-main-002/receipt.json')['exitCode']==0 and 'BUILD SUCCESSFUL' in (B/'evidence/build-main-002/gradle.log').read_text()
assert load(B/'evidence/build-main-001/superseded.json')['status']=='SUPERSEDED_NOT_FINAL_DELIVERY'
# Explicitly exclude all nine frozen check entry classes from both delivered binaries.
tree=ast.parse((R/'docs/tester/D1_INPUT_SINK01_REVIEW_EVIDENCE/audit_frozen.py').read_text());defs=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='dexclasses'];exec(compile(ast.Module(body=defs,type_ignores=[]),'reused_dex_parser','exec'))
checkNames={p.stem for p in (B/'checks/com/videokit/d1input').glob('*.java')}
with zipfile.ZipFile(B/'artifacts/input-sink03-compile-probe-debug.apk') as z:classes=[c for n in z.namelist() if n.endswith('.dex') for c in dexclasses(z.read(n))];assert not any('/'+n+';' in c or '/'+n+'$' in c for c in classes for n in checkNames)
with zipfile.ZipFile(B/'artifacts/input-sink03-classes.jar') as z:assert not any('/'+n+'.class' in c or '/'+n+'$' in c for c in z.namelist() for n in checkNames)
(E/'all-check-classes-exclusion.json').write_text(json.dumps(dict(checkedNames=sorted(checkNames),apkAndJarExcluded=True),indent=2),encoding='utf8')
cases=load(R/'docs/tester/D1_INPUT_SINK01_PHASE_A_EVIDENCE/reusable-regression-cases.json')['cases']
for c in cases:c['newCandidateIndependentResult']='NOT_RUN_PLATFORM' if c['id']=='S05' else 'PARTIAL_FAIL_B05' if c['id'] in ['S03','S06'] else 'PASS_LIMITED_OFFLINE'
(E/'independent-case-results.json').write_text(json.dumps(dict(candidate='D1-20261021-INPUT-SINK03',matrix=cases,oldB01B02='PASS_LIMITED_OFFLINE_FOR_ORIGINAL_FINDINGS',oldB03B04='PASS_LIMITED_OFFLINE_FOR_ORIGINAL_FINDINGS',newFindings=[dict(id='B05',priority='P2',scope='Invalid QUERY terminal result'),dict(id='C01',priority='P3',scope='Documented external review root mismatch')],sourceAndProductionJarBoth=True,overall='FAIL',platformAndRealBusinessCommit='NOT_RUN',deadlineExactInstructionInterleaving='Static causal audit plus dynamic late ACK; not deterministically injected'),ensure_ascii=False,indent=2),encoding='utf8')
records=[dict(path=p.relative_to(R).as_posix(),bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(E.rglob('*')) if p.is_file() and p.name!='review-evidence-manifest.json']
out=dict(frozenAtUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),report=P.relative_to(R).as_posix(),reportBytes=P.stat().st_size,reportSha256=sha(P),overall='FAIL',evidenceFiles=records,allActualHostThreadsJoined=True,allJdkProcessesReturned=True,finalSourceKeepers=0,finalOutputKeepers=0,oldTester114And207Unchanged=True,candidateStillUnchanged=True,SDKDeviceAdb5037GradleCalls=0,nextBatchStarted=False)
(E/'review-evidence-manifest.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps({k:v for k,v in out.items() if k!='evidenceFiles'},ensure_ascii=False,indent=2));print('evidenceFiles',len(records))
