from pathlib import Path
import datetime,difflib,hashlib,json,zipfile
R=Path('D:/CodexProjects/VideoKit');B=R/'docs/coder/d1android02-capture-ready02-fix';E=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def pin(p):return {'path':p.relative_to(R).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)}
def save(n,v):(E/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
s=B/'evidence/ready02-fix-freeze.json';assert sha(s)=='c5ec7bafa461bc6e99ed2790248c67edce92cf11cd4a3e33c72fed54f5b82b1e';rows=read(s)['files'];assert len(rows)==364
for x in rows:
 p=R/x['path'];assert p.resolve().is_relative_to(R) and p.stat().st_size==x['bytes'] and sha(p)==x['sha256']
zpath=R/'docs/coder/D1_ANDROID02_CAPTURE_READY02_FIX-source.zip';assert sha(zpath)=='929ae193f2cf385c911b0cb4e82e4b99aeacf6e76f819fe2107ef0303e1adb9e'
with zipfile.ZipFile(zpath) as z:
 assert len(z.namelist())==len(set(z.namelist()))==365 and set(z.namelist())=={x['path'] for x in rows}|{s.relative_to(R).as_posix()}
 for n in z.namelist():
  b=z.read(n);p=R/n;assert len(b)==p.stat().st_size and hashlib.sha256(b).hexdigest()==sha(p)
old=R/'docs/coder/d1android02-capture-ready01';plan=B/'reference/exact-seven-role-plan.json';assert sha(plan)==sha(old/'reference/exact-seven-role-plan.json')=='f0309a72789c67e0e0cd4afd54ca9e814384dc07d934241a6c07fe1c75ca7199';p=read(plan)
assert read(B/'release/capture-policy.json')['mode']=='PREPARATION_ONLY' and read(B/'release/activation-required.template.json')['approvedForExecution'] is False
assert sum(x['maxTextBytes'] for x in p['steps'][:4])==1048576 and sum(x['maxTextBytes'] for x in p['steps'][4:6])==131072 and p['steps'][6]['maxTextBytes']==1048576
for n in ['app','test']:
 x=p['product'][n];q=Path(x['path']);assert q.stat().st_size==x['bytes'] and sha(q)==x['sha256']
assert sha(Path(p['product']['sealPath']))==p['product']['sealSha256']
for rel in ['tools/capture_android02.ps1','selfchecks/capture_fixture.py']:
 (E/(Path(rel).name+'.independent.patch')).write_text(''.join(difflib.unified_diff((old/rel).read_text().splitlines(True),(B/rel).read_text().splitlines(True),fromfile='READY01/'+rel,tofile='READY02/'+rel)),encoding='utf-8')
history=[]
for q in sorted((B/'selfchecks/work').glob('suite-*/summary.json')):
 x=read(q);history.append({'path':str(q),'sha256':sha(q),'elapsedSeconds':x['elapsedSeconds'],'allPassed':x['allPassed'],'entrySha256':x['entrySha256'],'ownerSha256':x['ownerSha256'],'groups':len(x['results'])})
final=read(B/'evidence/local-selfchecks.json');assert final['allPassed'] and len(final['results'])==7 and final['elapsedSeconds']<30
assert final['entrySha256']==sha(B/'tools/capture_android02.ps1') and final['ownerSha256']==sha(B/'tools/outer_owner.py')
save('independent-static-audit.json',{'status':'PASS_FROZEN364_ZIP365_PLAN_IDENTITY_ONLY','seal':pin(s),'zip':pin(zpath),'sourcePins':[pin(B/q) for q in ['tools/capture_android02.ps1','tools/outer_owner.py','selfchecks/capture_fixture.py','release/capture-policy.json','release/activation-required.template.json','reference/original-outer-owner-contract.md']],'plan':pin(plan),'history':history,'finalSelfcheck':final,'coderIntermediateRunNotFinalSourceEvidence':True,'sdkFileHashesNotRequeried':True,'newSdkDeviceJvmGradleMediaActions':0,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat()});print('PASS independent364/ZIP365; unchanged exact7 plan; final/intermediate histories separate')
