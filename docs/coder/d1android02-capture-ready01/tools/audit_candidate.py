"""Static whole-source preservation, byte budgets, and evidence inventory only."""
from pathlib import Path
import hashlib,json
B=Path(__file__).resolve().parents[1];R=B.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def audit_seal(rel):
 p=R/rel;d=read(p);bad=[]
 for row in d['files']:
  q=R/row['path']
  if not q.is_file() or q.stat().st_size!=row['bytes'] or sha(q)!=row['sha256']:bad.append(row['path'])
 return {'seal':rel,'sha256':sha(p),'rows':len(d['files']),'bad':bad}
plan=read(B/'reference/exact-seven-role-plan.json');entry=(B/'tools/capture_android02.ps1').read_text();old=(B/'reference/capture_render02-original.ps1').read_text()
seals=[audit_seal('docs/coder/d1media3-android02-fix02/evidence/fix02-freeze.json'),audit_seal('docs/coder/d1render02-capture/evidence/capture-adapt-freeze.json')]
pins=[]
for p in [plan['product']['app'],plan['product']['test']]+plan['sdkFiles']:
 q=Path(p['path']);pins.append({'path':str(q),'bytes':q.stat().st_size,'sha256':sha(q),'match':q.stat().st_size==p['bytes'] and sha(q)==p['sha256'],'action':'STATIC_FILE_READ_ONLY_NO_EXECUTION'})
rolecaps={g:sum(s['maxTextBytes'] for s in plan['steps'] if s['group']==g) for g in ['preflight','install','instrument']}
markers={
 'AC01':'PREPARATION_ONLY_NO_EXECUTION_AUTHORIZATION','AC02':'EXACT_LOCAL_PRODUCER_ONLY','AC03':'DUPLICATE_JSON_FIELD','AC04':'EXACT_NEW_ACTIVATION_BINDING','AC05':'EXACT_SEVEN_REQUEST_ONLY','AC06':'EXISTING_FRESH_ROUTE_CLAIM_UNPROVEN','AC07':'GLOBAL_FOREGROUND_UNPROVEN','AC08':'OpenPinnedSource','AC09':'$global:Android02CaptureCustody[$c.owner]=$c','AC10':'$c.rawBytes+=$n','AC11':'$bodyReturned=','AC12':'EXACT_OUTER_ORIGINAL_RETURN_REQUIRED','AC13':'PREDECESSOR_RAW_SEMANTIC_NOT_PASS','AC14':'NO_SCOPE_CONSUMPTION_RESET','AC15':'7629605','AC16':'WHOLE_SEVEN_ROLE_BUDGET_BEFORE_CHILD','AC17':'NOT_MEASURED_NOT_FREE_NOT_ARCHIVE','AC18':'$request.qualificationSeconds -gt 90','AC19':'QUALIFICATION_TIMEOUT_NO_TERMINATION','AC20':'$r.file.WriteAsync','AC21':'EXACT_LOCAL_PRODUCER_ONLY','AC22':'EXACT_BOUNDED_FIXTURE_PAYLOAD','AC23':'FIX02_PRODUCT_SEAL_PIN','AC24':'FRESH_SCOPE_REQUIRED','AC25':'PREPARATION_ONLY_NO_EXECUTION_AUTHORIZATION'}
matrix=[{'oracle':k,'sourceMarker':v,'present':v in entry,'classification':'STATIC_MAPPING_NOT_INDEPENDENT_B_NOT_DEVICE_PROOF'} for k,v in markers.items()]
roles=[{'oracle':'CR%02d'%(i+1),'role':s['id'],'argv':s['argv'],'maxTextBytes':s['maxTextBytes'],'qualificationSeconds':s['qualificationSeconds'],'classification':'FIXED_PLAN_STATIC_AND_LOCAL_FAKE_CHAIN_ONLY_NOT_DEVICE'} for i,s in enumerate(plan['steps'])]
hist=[]
for p in sorted((B/'selfchecks/work').glob('suite-*/summary.json')):hist.append({'path':p.relative_to(B).as_posix(),'sha256':sha(p),'elapsedSeconds':read(p)['elapsedSeconds'],'allPassed':read(p)['allPassed'],'results':len(read(p)['results'])})
summary=read(B/'evidence/local-selfcheck-latest.json')
out={'schema':'ANDROID02_READY01_STATIC_AUDIT_V1','priorFrozenSeals':seals,'pins':pins,'sourceEntrySha256':sha(B/'tools/capture_android02.ps1'),'planSha256':sha(B/'reference/exact-seven-role-plan.json'),'producerSha256':sha(B/'selfchecks/capture_fixture.py'),'policySha256':sha(B/'release/capture-policy.json'),'roleCapSums':rolecaps,'oracleMatrix':matrix,'roles':roles,'selfcheckAttemptHistory':hist,'latestSelfchecksPassed':summary['allPassed'],'sdkChildren':0,'deviceQueries':0,'serverQueries':0,'oldUnknownQueries':0,'gradleRuns':0,'actualAndroid':'NOT_RUN','independentNewToolB':'NOT_RUN_PENDING_REVIEW','allStaticChecksPassed':all(not s['bad'] for s in seals) and all(p['match'] for p in pins) and all(r['present'] for r in matrix) and rolecaps=={'preflight':1048576,'install':131072,'instrument':1048576}}
save(B/'evidence/static-audit.json',out)
print(json.dumps({k:v for k,v in out.items() if k not in ['oracleMatrix','pins','roles']},ensure_ascii=False))
assert out['allStaticChecksPassed'] and summary['allPassed']
