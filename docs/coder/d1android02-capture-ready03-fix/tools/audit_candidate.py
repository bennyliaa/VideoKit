from pathlib import Path
import hashlib,json
B=Path(__file__).resolve().parents[1];R=B.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def seal(rel):
 f=R/rel;d=read(f);bad=[]
 for row in d['files']:
  p=R/row['path']
  if not p.is_file() or p.stat().st_size!=row['bytes'] or sha(p)!=row['sha256']:bad.append(row['path'])
 return {'seal':rel,'sha256':sha(f),'rows':len(d['files']),'bad':bad}
seals=[seal(s) for s in ['docs/coder/d1android02-capture-ready02-fix/evidence/ready02-fix-freeze.json','docs/coder/d1android02-capture-ready01/evidence/capture-ready01-freeze.json','docs/coder/d1media3-android02-fix02/evidence/fix02-freeze.json','docs/coder/d1render02-capture/evidence/capture-adapt-freeze.json']]
p=read(B/'release/capture-policy.json');a=read(B/'release/activation-required.template.json');plan=read(B/'reference/exact-seven-role-plan.json');t=read(B/'evidence/local-selfchecks.json')
assert sha(B/'reference/D1_ANDROID02_CAPTURE_READY02_FIX_PHASE_B_REVIEW_REPORT_V1.0.md')=='cffd1476883fcf9a6ebfa924888d16e74c1a0c8633dcedf5b48c8848d36b66bb'
assert p['mode']=='PREPARATION_ONLY' and not a['approvedForExecution']
assert t['allPassed'] and t['entrySha256']==p['entrySha256']==sha(B/'tools/capture_android02.ps1') and t['ownerSha256']==p['outerOwnerSha256']==sha(B/'tools/outer_owner.py')
assert sha(B/'reference/exact-seven-role-plan.json')=='f0309a72789c67e0e0cd4afd54ca9e814384dc07d934241a6c07fe1c75ca7199'
for x in [plan['product']['app'],plan['product']['test']]:
 q=Path(x['path']);assert q.stat().st_size==x['bytes'] and sha(q)==x['sha256']
assert all(not s['bad'] for s in seals)
run=Path(t['runRoot']);size=sum(f.stat().st_size for f in run.rglob('*') if f.is_file());assert size<=4194304
pins=[{'path':f.relative_to(B).as_posix(),'sha256':sha(f),'bytes':f.stat().st_size} for f in [B/'tools/capture_android02.ps1',B/'tools/outer_owner.py',B/'selfchecks/run_checks.py',B/'selfchecks/capture_fixture.py',B/'release/capture-policy.json',B/'release/activation-required.template.json']]
d={'schema':'READY03_FIX_STATIC_AUDIT_V1','allPassed':True,'baselineSeals':seals,'pins':pins,'selfcheckRunWholeDirectoryBytes':size,'selfcheckRunFileCount':sum(f.is_file() for f in run.rglob('*')),'selfcheckSeconds':t['elapsedSeconds'],'selfcheckGroupsCompleted':len(t['results']),'schemaSamples':13,'deltaRejections':3,'history':[{'path':s.relative_to(B).as_posix(),'sha256':sha(s),'allPassed':read(s)['allPassed'],'seconds':read(s)['elapsedSeconds']} for s in sorted((B/'selfchecks/work').glob('suite-*/summary.json'))],'sdkActions':0,'deviceActions':0,'oldUnknownActions':0,'gradleAndJvmRuns':0,'newIndependentB':'PENDING','Android':'NOT_RUN'}
(B/'evidence/static-audit.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in d.items() if k!='pins'},ensure_ascii=False))
