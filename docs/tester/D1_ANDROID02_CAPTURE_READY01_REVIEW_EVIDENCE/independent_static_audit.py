from pathlib import Path
import datetime,difflib,hashlib,json,zipfile
R=Path('D:/CodexProjects/VideoKit');B=R/'docs/coder/d1android02-capture-ready01';E=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def pin(p):return {'path':p.relative_to(R).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)}
def save(n,v):(E/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
s=B/'evidence/capture-ready01-freeze.json';assert sha(s)=='3ff8b42d7bd5c31f578bcfdec8bba7286dd32ba90289fcc6556dc338368fa51d';d=read(s);assert len(d['files'])==756;expected={x['path']:x for x in d['files']};assert len(expected)==756
for x in expected.values():
 p=R/x['path'];assert p.resolve().is_relative_to(R) and p.stat().st_size==x['bytes'] and sha(p)==x['sha256']
zpath=R/'docs/coder/D1_ANDROID02_CAPTURE_READY01-source.zip';assert sha(zpath)=='fff52949e2af361321cc80820d4fce38d67ab8cf6559a42301959abbd369663e'
with zipfile.ZipFile(zpath) as z:
 assert len(z.namelist())==len(set(z.namelist()))==757 and set(z.namelist())==set(expected)|{s.relative_to(R).as_posix()}
 for n in z.namelist():
  b=z.read(n);p=R/n;assert len(b)==p.stat().st_size and hashlib.sha256(b).hexdigest()==sha(p)
plan=read(B/'reference/exact-seven-role-plan.json');policy=read(B/'release/capture-policy.json');activation=read(B/'release/activation-required.template.json');assert policy['mode']=='PREPARATION_ONLY' and activation['approvedForExecution'] is False
roles=plan['steps'];assert [x['id'] for x in roles]==['identity','global_idle','app_absence','test_absence','install_app','install_test','scope_all'];assert [x['qualificationSeconds'] for x in roles]==[15,15,15,15,45,45,90]
assert sum(x['maxTextBytes'] for x in roles[:4])==1048576 and sum(x['maxTextBytes'] for x in roles[4:6])==131072 and roles[6]['maxTextBytes']==1048576
for x in roles:
 assert x['argv'][:3]==['D:/Android/SDK/platform-tools/adb.exe','-s','HA1Q6WXR'] and x['maxBinaryBytes']==0 and len(json.dumps(x['argv'],ensure_ascii=False,separators=(',',':')).encode())<=4096
assert roles[1]['argv'][-1].count('dumpsys')==2 and 'activity processes' in roles[1]['argv'][-1] and 'activity activities' in roles[1]['argv'][-1]
for idx,key in [(4,'app'),(5,'test')]:
 x=plan['product'][key];p=Path(x['path']);assert p.stat().st_size==x['bytes'] and sha(p)==x['sha256'];assert roles[idx]['argv'][3:6]==['install','-t','--no-streaming'] and roles[idx]['argv'][-1]==x['path']
assert roles[6]['argv'][-1]=='com.videokit.d1media3.android02.test/com.videokit.d1media3.android02.test.Media3Instrumentation' and roles[6]['argv'].count('scopeAll')==1 and '@RUN_ID@' in roles[6]['argv']
assert sha(Path(plan['product']['sealPath']))==plan['product']['sealSha256']=='39acf77353697204d0ee94d573708b11d926d4efcfd5b530696a21f52efbe0ad'
summary=read(B/'evidence/local-selfcheck-latest.json');assert summary['allPassed'] and len(summary['results'])==7 and summary['elapsedSeconds']<30 and summary['mockPayloadBytes']==6144 and summary['totalOuterTextBytes']==44156
history=[]
for p in sorted((B/'selfchecks/work').glob('suite-*/summary.json')):
 x=read(p);history.append({'path':str(p),'sha256':sha(p),'allPassed':x['allPassed'],'elapsedSeconds':x['elapsedSeconds'],'groups':len(x['results']),'failedGroups':[r['name'] for r in x['results'] if not r['pass']]})
assert len(history)==4 and sum(x['allPassed'] for x in history)==1
old=R/'docs/coder/d1render02-capture/tools/capture_render02.ps1';new=B/'tools/capture_android02.ps1';patch=''.join(difflib.unified_diff(old.read_text().splitlines(True),new.read_text().splitlines(True),fromfile=str(old),tofile=str(new)));(E/'independent-full-entry-diff.patch').write_text(patch,encoding='utf-8')
sem=(B/'tools/semantic-gates.ps1.txt').read_text();assert sem in new.read_text()
save('independent-material-source-plan-audit.json',{'status':'PASS_MATERIALS_AND_STATIC_PLAN_ONLY','seal':pin(s),'files':756,'zip':pin(zpath),'uniqueZipMembers':757,'entry':pin(new),'producer':pin(B/'selfchecks/capture_fixture.py'),'plan':pin(B/'reference/exact-seven-role-plan.json'),'defaultPolicy':pin(B/'release/capture-policy.json'),'roles':roles,'selfcheckHistory':history,'finalCoderSelfcheck':summary,'busyFinalSuiteCoverage':'PURE_LOCAL_SEMANTIC_ONLY; earlier busy full capture belongs failed incomplete historical suites, not current full end-to-end PASS','sourceDiff':pin(E/'independent-full-entry-diff.patch'),'sdkFilesHashedByThisAudit':False,'sdkDeviceJvmGradleMediaCalls':0,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat()});print('PASS independent756/ZIP757, exact7 plan and4 original selfcheck histories; no runtime verdict')
