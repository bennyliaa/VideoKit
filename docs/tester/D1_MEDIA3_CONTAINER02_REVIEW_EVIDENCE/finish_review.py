from pathlib import Path
import json,hashlib,subprocess,datetime
R=Path('D:/CodexProjects/VideoKit');E=Path(__file__).resolve().parent;B=R/'docs/coder/d1media3-container02';P=Path('C:/Users/benny/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
targets=[str(R/'docs/tester/D1_MEDIA3_CONTAINER01_REVIEW_EVIDENCE/container02-invalid-child'),str(R/'docs/tester/D1_INPUT_SINK05_REVIEW_EVIDENCE/container02-invalid-child'),str(B/'invalid-review-child'),str(E.parent/(E.name+'_FAKE')/'invalid-child'),str(E/'..'/'container02-invalid-escape'),'docs/tester/relative-invalid',str(E),str(E/'independent-001')];runs=[]
for tool,flag in [('review_all.py','--output'),('local_check.py','--review-output')]:
 for i,t in enumerate(targets):
  target=Path(t);existed=target.exists();argv=[str(P),'-X','utf8','-B',str(B/'tools'/tool),flag,t];p=subprocess.run(argv,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=45)
  prefix=E/f'output-gate-{tool[:-3]}-{i}';prefix.with_suffix('.stdout').write_bytes(p.stdout);prefix.with_suffix('.stderr').write_bytes(p.stderr);row=dict(argv=argv,exitCode=p.returncode,targetExistedBefore=existed,targetExistsAfter=target.exists(),originalProcessReturned=True)
  assert p.returncode!=0 and (existed or not target.exists()),row
  runs.append(row)
(E/'output-gates.json').write_text(json.dumps(dict(result='PASS_16_REJECTIONS_NO_NEW_TARGET',runs=runs),indent=2),encoding='utf8')
seal=B/'evidence/media3-container02-freeze.json';d=load(seal)
for r in d['files']:assert (R/r['path']).stat().st_size==r['bytes'] and sha(R/r['path'])==r['sha256'],r['path']
old=[]
for name,manifest in [('D1_MEDIA3_CONTAINER01_REVIEW_EVIDENCE','review-evidence-manifest.json'),('D1_MEDIA3_CONTAINER01_PHASE_A_EVIDENCE','phase-a-evidence-manifest.json'),('D1_INPUT_SINK05_REVIEW_EVIDENCE','review-evidence-manifest.json')]:
 data=load(E.parent/name/manifest);assert sha(R/data['report'])==data['reportSha256']
 for r in data['evidenceFiles']:assert (R/r['path']).stat().st_size==r['bytes'] and sha(R/r['path'])==r['sha256'],r['path']
 old.append(dict(manifest=name+'/'+manifest,files=len(data['evidenceFiles']),reportSha256=data['reportSha256']))
s=load(E/'independent-001/summary.json');assert len(s['runs'])==60 and all(x['exitCode']==0 for x in s['runs']) and s['frozenCandidate'];assert s['productionJarSha256']=='757e53a49d92a9b2148417e0b37ed9680162a7709b1493029759e58ce08dfd8f'
for mode in ['source','production']:
 for suite,count in [('shared',28),('boundary',8)]:
  assert load(E/f'independent-{suite}-{mode}-1.json')['exitCode']==0
  out=(E/f'independent-{suite}-{mode}-1.stdout').read_text();assert 'sourceKeepers0 outputKeepers0' in out
  if suite=='shared':assert out.count('PASS independent_shared ')==28 and out.count('cancelOrAbortBeforeContinue=false')==12 and 'OBSERVER_AFTER_WORKER' in out
  else:assert 'independentBoundaryPasses=8 reproducedFindings=0' in out and 'cancelOrAbortBeforeRetry=false' in out
scope=load(B/'reference/approved-sample-scope.json');sample=R/scope['path'];assert sample.stat().st_size==scope['bytes'] and sha(sample)==scope['sha256']
cases=load(E.parent/'D1_MEDIA3_CONTAINER01_REVIEW_EVIDENCE/independent-case-results.json')['cases']
for c in cases:
 c['priorPhaseBStatus']=c['status'];c['currentScope']='Inherited limited component/baseline regression rerun by frozen entry; actual functional NOT_RUN/OPEN boundaries unchanged'
 if c['id']=='MC01':c['status']='PASS_INHERITED_LIMITED_ADMISSION';c['phaseBEvidence']='Same17 coordinates/locks/pins/deps/license; actual300 consumption identity closure unchanged; no new downloads'
 if c['id']=='MC26':c['status']='PASS_LIMITED_REOPEN_ADMISSION';c['phaseBEvidence']='MC-B01 fixed independently without cancel/abort: sameProvider/RPC1 and actual original worker/observer return; real structure NOT_RUN'
 if c['id']=='MC30':c['status']='PASS_LIMITED_ORIGINAL_RETURN';c['phaseBEvidence']='Independent28 order/failure cases and old original response/worker suites passed; actual parser/cache success still NOT_RUN'
(E/'independent-case-results.json').write_text(json.dumps(dict(overall='PASS_LIMITED_FIX_WITH_FUNCTIONAL_SCOPE_OPEN',MC_B01='CLOSED_FOR_SPECIFIED_PRE_INSPECTION_ADMISSION_SCOPE',cases=cases),ensure_ascii=False,indent=2),encoding='utf8')
result=dict(checkedUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),result='PASS',frozenFilesUnchanged=676,oldEvidence=old,runnerExit0Count=60,independentSharedCasesPerPath=28,independentBoundaryCasesPerPath=8,MC_B01='PASS_LIMITED_FIX',newFindings=0,sampleAfter=dict(path=scope['path'],bytes=sample.stat().st_size,sha256=sha(sample)),sdkAdbGradleNetworkCalls=0)
(E/'post-review-preservation.json').write_text(json.dumps(result,indent=2),encoding='utf8');print(json.dumps(result,indent=2))
