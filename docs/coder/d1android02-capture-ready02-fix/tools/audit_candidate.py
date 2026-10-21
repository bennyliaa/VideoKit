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
seals=[seal('docs/coder/d1android02-capture-ready01/evidence/capture-ready01-freeze.json'),seal('docs/coder/d1media3-android02-fix02/evidence/fix02-freeze.json'),seal('docs/coder/d1render02-capture/evidence/capture-adapt-freeze.json')]
p=read(B/'release/capture-policy.json');plan=read(B/'reference/exact-seven-role-plan.json');t=read(B/'evidence/local-selfchecks.json')
pins=[{'path':str(B/r),'sha256':sha(B/r),'bytes':(B/r).stat().st_size} for r in ['tools/capture_android02.ps1','tools/outer_owner.py','tools/strict-receipt.ps1.txt','selfchecks/capture_fixture.py','selfchecks/run_checks.py','reference/exact-seven-role-plan.json','release/capture-policy.json','release/activation-required.template.json','reference/original-outer-owner-contract.md','reference/D1_ANDROID02_CAPTURE_READY01_PHASE_B_REVIEW_REPORT_V1.0.md']]
assert sha(B/'reference/D1_ANDROID02_CAPTURE_READY01_PHASE_B_REVIEW_REPORT_V1.0.md')=='606205d01c6db42c357ca72f403c6b676ed78b0f7a229f5a210e2c9be8efcfaa'
assert p['mode']=='PREPARATION_ONLY' and p['entrySha256']==sha(B/'tools/capture_android02.ps1') and p['outerOwnerSha256']==sha(B/'tools/outer_owner.py')
assert t['allPassed'] and t['entrySha256']==p['entrySha256'] and t['ownerSha256']==p['outerOwnerSha256']
for x in [plan['product']['app'],plan['product']['test']]+plan['sdkFiles']:
 q=Path(x['path']);assert q.stat().st_size==x['bytes'] and sha(q)==x['sha256']
assert all(not s['bad'] for s in seals)
history=[{'path':f.relative_to(B).as_posix(),'sha256':sha(f),'allPassed':read(f)['allPassed'],'seconds':read(f)['elapsedSeconds'],'entrySha256':read(f)['entrySha256'],'ownerSha256':read(f)['ownerSha256']} for f in sorted((B/'selfchecks/work').glob('suite-*/summary.json'))]
d={'schema':'READY02_FIX_STATIC_AUDIT_V1','allPassed':True,'baselineSeals':seals,'pins':pins,'history':history,'productAndSdkFilePinsMatch':True,'sdkActions':0,'deviceActions':0,'oldUnknownActions':0,'gradleAndJvmRuns':0,'scopeRoleCount':len(plan['steps']),'localSuiteSeconds':t['elapsedSeconds'],'independentNewB':'PENDING','Android':'NOT_RUN'}
(B/'evidence/static-audit.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in d.items() if k!='pins'},ensure_ascii=False))
