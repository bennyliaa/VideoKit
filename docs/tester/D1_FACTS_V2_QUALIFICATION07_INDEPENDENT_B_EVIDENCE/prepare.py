"""Own new scopes, frozen graph and zero-resource preflight, then one order."""
from pathlib import Path
from datetime import datetime,timezone,timedelta
import sys,os,json,hashlib,uuid,ast,copy,time
R=Path(__file__).resolve().parent;B=R.parents[1]/'coder/d1android02-facts-v2-qualification07/rev2';sys.path[:0]=[str(R),str(R/'driver'),str(B/'tools'),str(B/'selfchecks')]
from host_context import normalize
from fact_preauth import load_pins,LIMITS,validate,complete_source_plan,FACT_RUNTIME_FILES06
from facts_contract import enc,sha
from raw_inputs import legal_raw
import fact_collector as fc
def put(p,b):
 p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('xb') as f:f.write(b)
def save(p,d):put(p,enc(d))
assert not (R/'order.json').exists()
batch=uuid.uuid4().hex;W=R/'fixtures'/batch[:8];W.mkdir(parents=True);root=W/'f';root.mkdir();home=root/'home'
pins=load_pins(lambda p:Path(p).read_bytes());raw=legal_raw(fc,139264,128).replace(b'com.fixture.p',b'org.testkit.p');assert len(raw)==139264 and len(fc.facts(raw)['systemPackages'])==128;put(root/'fixture-facts.raw',raw)
p=json.loads((B/'release/capture-policy.json').read_bytes());pid=str(uuid.uuid4());run='D1MA02-INDB07_FACT_'+batch[:4].upper();scope=sha('|'.join((pid,p['entrySha256'],p['productSealSha256'],p['planSha256'],run)).encode());p.update(mode='OFFLINE_FIXTURE',scope=scope,planId=pid,runId=run,evidenceRoot=str(home/'outputs'))
sources=json.loads((B/'reference/runner-source-seal.json').read_bytes())['sources'];g=json.loads((B/'reference/gate-sources.json').read_bytes())['files'];roleplan=json.loads((B/'reference/exact-seven-role-plan.json').read_bytes());assert len(sources)==30 and len(g)==22
for n,h in sources.items():assert sha((B/n).read_bytes())==h
for x in g:assert sha((B/x['path']).read_bytes())==x['sha256']
import fact_preauth as fp
schema=ast.literal_eval(next(n.value for n in ast.parse((B/'tools/fact_preauth.py').read_text()).body if isinstance(n,ast.Assign) and any(isinstance(a,ast.Name) and a.id=='FACT_PREAUTH_SCHEMA07_RAW' for a in n.targets)))
assert schema.encode()==(B/'reference/fact-preauth-schema.json').read_bytes()
assert fp.KEYS==set(json.loads(schema)['required'])
runtime=json.loads((B/'reference/current-runtime-identity.json').read_bytes());assert FACT_RUNTIME_FILES06==runtime['files']
for x in runtime['files']:assert Path(x['path']).stat().st_size==x['bytes'] and sha(Path(x['path']).read_bytes())==x['sha256']
paths={B/'reference/runner-source-seal.json',B/'reference/gate-sources.json',B/'tools/runtime_binding.py',B/'reference/current-runtime-identity.json',B/'selfchecks/route_fixture.py',B/'selfchecks/fact_fixture.py',B/'reference/route-backend-contract.json',B/'tools/win32_route.py',B/'tools/fact_preauth.py',B/'tools/fact_collector.py',B/'tools/facts_entry.py',B/'reference/fact-plan.json',root/'fixture-facts.raw'}
paths.update(B/x['path'] for x in g);paths.update(Path(x['path']) for x in runtime['files']);sizes={str(x):x.stat().st_size for x in paths};sourcePlan=complete_source_plan(p,g,runtime['files'],sizes,root/'fixture-facts.raw',len(raw));assert sourcePlan['sourceReads']==64;save(R/'fact-source-plan.json',sourcePlan)
targets={}
for label in ['positive','wrong-firmware','receipt-replace']:
 folder=W/label;targethome=folder/'home';pid=str(uuid.uuid4());run='D1MA02-INDB07_'+label.upper().replace('-','_');s=sha('|'.join((pid,sources['tools/capture_android02.ps1'],roleplan['product']['sealSha256'],sources['reference/exact-seven-role-plan.json'],run)).encode());targets[label]=dict(folder=str(folder),home=str(targethome),target=dict(scope=s,planId=pid,runId=run,sourceSealSha256=pins['sourceSealSha256'],planSha256=sources['reference/exact-seven-role-plan.json'],mode='OFFLINE_FIXTURE',evidenceRoot=str(folder/'authority/outputs')),request=str(folder/'request.json'),reply=str(folder/'reply'))
 assert len(str(targethome))<210
 assert all(len(str(targethome/'outputs'/(r+'-owner-admission.json')))<260 for r in ('identity','global_idle'))
candidateRoot=B.parent;rows=json.loads((candidateRoot/'full-manifest.json').read_bytes())['files'];profile=[dict(path=x['path'][5:],sha256=x['sha256']) for x in rows if x['path'].startswith('rev2/')];save(R/'profile.json',profile)
tester=[dict(path=f.relative_to(R).as_posix(),sha256=sha(f.read_bytes())) for f in [*R.glob('*.py'),*R.glob('*.ps1'),*(R/'driver').glob('*')] if f.is_file()];save(R/'tester-profile.json',tester)
env=normalize(dict(SystemRoot=str(Path('C:/Windows')),WINDIR=str(Path('C:/Windows')),TEMP=str(R),TMP=str(R)))
# Template freshness starts after all file-only package and runtime checks.
now=datetime.now(timezone.utc);t=dict(schema='GLOBAL_IDLE_FACT_PREAUTH_V1',mode='OFFLINE_FIXTURE',sourceThreadId='01a107c3-2bf9-7fa0-94a0-234258ca6774',sourceTurnId=str(uuid.uuid4()),notBeforeUtc=(now-timedelta(seconds=1)).isoformat(),expiresUtc=(now+timedelta(seconds=88)).isoformat(),scope=scope,planId=p['planId'],runId=p['runId'],nonce=str(uuid.uuid4()),home=str(home),evidenceRoot=p['evidenceRoot'],policySha256=sha(enc(p)),**{k:pins[k] for k in ('sourceSealSha256','gateSourcesSha256','collectorSha256','binderSha256','entrySha256','runtimeIdentitySha256','factPlanSha256')},sdk=pins['sdk'],device=dict(serial='HA1Q6WXR',model='TB138FC',api=31,user=0),queries=pins['queries'],limits=dict(LIMITS));assert validate(enc(t),sha(enc(t)),p,pins)==t;save(root/'template.json',t);save(root/'policy.json',p)
plan=dict(revision='INDEPENDENT_B_REV2',batch=batch,work=str(W),facts=dict(root=str(root),home=str(home),rawSha256=sha(raw),templateSha256=sha(enc(t))),targets=targets,cwd=str(R),expectedEnvironment=env,inputPins={str(f):sha(f.read_bytes()) for f in W.rglob('*') if f.is_file()},wholeSeconds=360,stopNewSeconds=320,readCap=1073741824,artifactCap=16777216,processCap=96,concurrency=1,productRetry=0,hostPopen=16,factsInner=2,dotNetInner=4,outerWorker=1,totalProcessGraph=23,conditionalFailureMaxGraph=25,sourceReservations=dict(factsGate=33554432,targetGates=67108864,runnerSources=100663296,driverAndModels=268435456,preparation=67108864,total=536870912))
save(R/'plan.json',plan);save(R/'budget.json',{k:plan[k] for k in ('wholeSeconds','stopNewSeconds','readCap','artifactCap','processCap','concurrency','productRetry','hostPopen','factsInner','dotNetInner','outerWorker','totalProcessGraph','conditionalFailureMaxGraph','sourceReservations')})
save(R/'full-graph.json',dict(host=['qual-ok','qual-fail','qual-PS','facts','review-positive','review-wrong-firmware','review-receipt-replace','gate-positive','capture-positive-identity','capture-positive-global_idle','gate-wrong-firmware','capture-wrong-firmware-identity','gate-receipt-replace','capture-receipt-replace-identity','budget','v1'],conditionalExtra=['capture-receipt-replace-global_idle','nested-dotnet-if-unexpected-accept'],nestedFacts=['route_fixture','fact_fixture'],dotNet=['positive.identity','positive.global_idle','wrong-firmware.identity','receipt-replace.identity'],worker=1,noRetry=True))
# Same exact aux factory supplies preflight, actual caller and frozen tuple.
from call_plan import facts_argv,review_argv,aux_argv
from independent_driver import freeze_helper_tuple
assert aux_argv(plan,'budget')==list(freeze_helper_tuple(R,W).argv)
from guard import Guard
guard=Guard();kw=dict(executable=None,cwd=None,env=None,shell=False,close_fds=True,stdin=-3,stdout=-1,stderr=-1);checks=[]
oldCwd=Path.cwd();oldEnv=dict(os.environ)
try:
 os.chdir(R);os.environ.clear();os.environ.update(env)
 for label,a in [('facts',facts_argv(plan))]+[('review-'+k,review_argv(plan,k)) for k in targets]+[(k,aux_argv(plan,k)) for k in ('budget','v1')]:assert guard.check(a,kw)==label;checks.append(dict(case='exact-'+label,accepted=True))
 for label,mut in [('wrong-source',lambda a,k:a.__setitem__(4,str(B/'selfchecks/budget_models.ps1'))),('wrong-program',lambda a,k:a.__setitem__(0,'wrong.exe')),('wrong-executable',lambda a,k:k.__setitem__('executable','wrong.exe')),('wrong-cwd',lambda a,k:k.__setitem__('cwd',str(B))),('wrong-env',lambda a,k:k.__setitem__('env',{})),('extra-arg',lambda a,k:a.append('EXTRA'))]:
  a=aux_argv(plan,'budget');k=dict(kw);mut(a,k)
  try:guard.check(a,k);why='ACCEPT'
  except ValueError as e:why=str(e)
  assert why!='ACCEPT';checks.append(dict(case=label,reason=why,Capture=0,Popen=0))
finally:os.environ.clear();os.environ.update(oldEnv);os.chdir(oldCwd)
assert not guard.calls
save(R/'preflight.json',dict(checks=checks,source30=True,gate22=True,schemaFullExact=True,runtime14Exact=True,completeSourceReads=64,completeSourceBytes=sourcePlan['sourceBytes'],factoryTupleEqual=True,productResources=0))
paths=[f for f in R.rglob('*') if f.is_file()]+[candidateRoot/x['path'] for x in rows]+[candidateRoot/'full-manifest.json']+[Path(x['path']) for x in runtime['files']];frozen=[]
for f in sorted(set(paths)):
 b=f.read_bytes();frozen.append(dict(path=str(f),bytes=len(b),sha256=sha(b)))
now=datetime.now(timezone.utc);order=dict(schema='QUALIFICATION07_INDEPENDENT_B_ORDER_V1',batch=batch,nonce=str(uuid.uuid4()),candidate=str(B),sources=frozen,notBeforeUtc=now.isoformat(),expiresUtc=(now+timedelta(seconds=900)).isoformat(),allowedStarts=1,sourceThread='01a107c3-2bf9-7fa0-94a0-234258ca6774');save(R/'order.json',order)
print(json.dumps(dict(orderSha256=sha((R/'order.json').read_bytes()),frozenFiles=len(frozen),totalGraph=23,maxGraph=25,sourcePlanBytes=sourcePlan['sourceBytes'],fixtureExpires=t['expiresUtc'])))
