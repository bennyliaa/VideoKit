from pathlib import Path
import json,hashlib,zipfile,re,datetime
R=Path('D:/CodexProjects/VideoKit');B=R/'docs/coder/d1e13k';E=R/'docs/tester/D1_E13K_REVIEW_EVIDENCE';checks=[];seen={}
def raw(p):
 p=Path(p);p=p if p.is_absolute() else R/p;b=p.read_bytes();seen.setdefault(p.as_posix(),hashlib.sha256(b).hexdigest());return b
def obj(p):return json.loads(raw(p).decode('utf-8-sig'))
def ck(n,v):
 checks.append({'id':n,'pass':bool(v)})
 if not v:raise AssertionError(n)
def pin(r):
 b=raw(r['path']);ck('bytes:'+r['path'],len(b)==r['bytes']);ck('sha:'+r['path'],hashlib.sha256(b).hexdigest()==r['sha256'])
seal=B/'evidence/e13k-freeze.json';ck('exact seal',hashlib.sha256(raw(seal)).hexdigest()=='bb3e6511dcb62146d6ed87686ebdb5818338b0cb22ddc0fbdc65ceaa028c0916');s=obj(seal)
for r in s['immutableFiles']:pin(r)
with zipfile.ZipFile(R/s['archive']['path']) as z:
 members={r['path']:r for r in s['immutableFiles'] if r['path']!=s['archive']['path']};ck('exact ZIP membership',len(z.namelist())==len(set(z.namelist()))==len(members) and set(z.namelist())==set(members));ck('ZIP CRC',z.testzip() is None)
 for n,r in members.items():b=z.read(n);ck('ZIP member:'+n,len(b)==r['bytes'] and hashlib.sha256(b).hexdigest()==r['sha256'])
prior=[]
for g in s['priorSeals']:
 pin(g['seal']);rows=obj(g['seal']['path'])['immutableFiles'];ck('old count:'+g['seal']['path'],len(rows)==g['immutableRowsVerified']);prior.append(len(rows))
 for r in rows:pin(r)
d=obj(B/'evidence/jar-member-difference.json');pin(d['baseline']);pin(d['jar']);changed=[]
with zipfile.ZipFile(R/d['baseline']['path']) as a,zipfile.ZipFile(R/d['jar']['path']) as b:
 ck('193 identical entry sets',len(a.namelist())==len(b.namelist())==193 and set(a.namelist())==set(b.namelist()))
 for n in a.namelist():
  if a.read(n)!=b.read(n):changed.append(n)
 ck('192 unchanged only outer policy changed',changed==['com/videokit/spike/e4/E13JReadOnly.class'])
sha='a5a7fd2f15c41f2a01f8e49f11b942c34bb23c9e890e5d6f8f275d49a7bffa03'
ck('typed release exact SHA',hashlib.sha256(raw(B/'release/read-only-release.json')).hexdigest()==sha)
release=obj(B/'release/read-only-release.json');expected={'budget':'262144','kind':'e13jFixedReadOnlyRelease','requests':'2','review':'f9e5a63acf2aea2fc51c9c71ec50ceba5ed080cdded46676cd7fd9cec6374583','scope':'116c978327fc2240dbe04a9ead566165d231b88d14166776e03938a40b76aaef','serial':'HA1Q6WXR'};ck('exact six release fields',release=={'e9':1,'fields':expected});ck('functional review actual hash',hashlib.sha256(raw('docs/tester/D1_E13J_R1_FIXED_SOCKET_REVIEW_REPORT_V1.0.md')).hexdigest()==expected['review'])
before=raw('docs/coder/d1e13j-r1/tools/E13JReadOnly.java').decode();after=raw(B/'policy/E13JReadOnly.java').decode();ck('source only exact policy and describe value',after.replace(sha,'ABSENT')==before)
def norm(t):return re.sub(r'[ \t]+',' ',re.sub(r'#\d+','#CP',t.replace(sha,'ABSENT'))).strip()
ck('javap preserves instructions offsets and branches',norm(raw(B/'evidence/javap-old.stdout.txt').decode())==norm(raw(B/'evidence/javap-new.stdout.txt').decode()))
request=obj(B/'release/observer-request.json');scope=obj(B/'release/execution-scope.json');ck('new execution batch distinct original',scope['batch']==request['executionBatch']=='d7b4ca4f-36a3-49c9-9b61-cdc7ebdcb5b6' and scope['originalScope']==request['originalScope']=='aeefe32f-816d-4c0b-aca7-16f76dbd45ff');ck('original runtime bound',scope['runtimeScopeSha256']==request['scope']==expected['scope']);ck('one exact JAR pin',request['pins']==[{'path':'D:/CodexProjects/VideoKit/'+d['jar']['path'],'sha256':d['jar']['sha256']}])
final=obj(B/'evidence/final-binding-receipt.json')
for k in ['release','scope','executionCommandRequest','observerRequest','jar','observer','launch','sourcePolicy']:pin(final[k])
marker=b'# Same original local context';ck('observer ownership body exact',raw(final['observer']['path']).split(marker,1)[1]==raw('docs/coder/d1e13j-r1/tools/observe_j_only.ps1').split(marker,1)[1])
launch=raw(final['launch']['path']).decode();ck('launch checks all exact pins',all(final[k]['sha256'] in launch for k in ['release','scope','observerRequest','jar','observer']));ck('capture once and bounded summary',launch.count('$captured = & ')==1 and '[Console]::WriteLine($summary)' in launch and 'WriteLine($captured)' not in launch)
command=obj(B/'release/execution-command.json');ck('four exact launch argv',command['argv']==['C:/Users/benny/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/powershell/pwsh.exe','-NoProfile','-File','D:/CodexProjects/VideoKit/docs/coder/d1e13k/release/launch_once.ps1'])
budget=json.loads(raw(B/'evidence/final-static-002/outer-budget.stdout.txt').decode('utf-8-sig'));ck('8157 includes exact CRLF command request',sum(budget['parts'].values())==budget['totalUpperBound']==8157 and budget['parts']['executionCommandRequest']==len(raw(B/'release/execution-command.json'))==204 and budget['bound']==8192 and budget['remaining']==35)
root=R/'docs/tester/D1_E13J_R1_G_SUPPLEMENT_EVIDENCE';ck('no prior execution root conflict',not root.exists());ck('once id fixed',request['id']=='E13J-R1-SUPPLEMENT-ONCE' and Path(request['evidenceRoot'])==root)
E.mkdir(parents=True,exist_ok=True);(E/'reviewed-input-snapshot.json').write_text(json.dumps([{'path':p,'sha256':h} for p,h in sorted(seen.items())],indent=2),'utf-8')
r={'atUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'PASS_INDEPENDENT_MECHANICAL_BEFORE_EXECUTION','checks':checks,'checkCount':len(checks),'uniqueFrozenFilesRead':len(seen),'oldManifestCounts':prior,'unchangedClasses':192,'changedClasses':changed,'outerBudgetUpperBound':8157,'budgetBound':8192,'launchNotYetExecuted':True,'rootAbsentAtCheck':True,'originalSessionRead':'BLOCKED_NO_BYTE_LIMIT_GUARANTEE','noOldPIDQuery':True}
(E/'mechanical-audit.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),'utf-8');print(json.dumps({k:v for k,v in r.items() if k!='checks'}))
