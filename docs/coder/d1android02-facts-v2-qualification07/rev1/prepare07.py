"""Pure frozen plan; actual one batch follows in the same host environment."""
from pathlib import Path
from datetime import datetime,timezone,timedelta
import sys,json,uuid,hashlib,os,time
H=Path(__file__).resolve().parent;sys.path[:0]=[str(H/'tools'),str(H/'selfchecks')]
from fact_preauth import load_pins,LIMITS,validate
from raw_inputs import legal_raw
import fact_collector as fc
from facts_contract import enc,sha
def save(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(enc(d))
def digest(p):return sha(Path(p).read_bytes())
C=Path('D:/CodexProjects/VideoKit/docs/coder');DOCS=C.parent;BATCH=json.loads((H.parent/'batch-declaration07.json').read_bytes());REV=next(x for x in BATCH['revisions'] if x['root']==str(H));SEED=uuid.UUID(REV['seed']);BATCH_START=json.loads((H.parent/'execution-start.json').read_bytes())['monotonic'] if (H.parent/'execution-start.json').exists() else time.monotonic()
checks=[]
for root,mf,key,count in [(C/'d1android02-facts-v2-qualification04','reference/full-manifest.json','files',284),(DOCS/'tester/D1_FACTS_V2_QUALIFICATION04_INDEPENDENT_B_EVIDENCE','delivery-manifest.json','files',260),(DOCS/'tester/D1_FACTS_V2_QUALIFICATION05_PHASE_A_EVIDENCE','delivery-manifest.json','entries',28)]:
 m=json.loads((root/mf).read_bytes());rows=m.get(key) if type(m.get(key)) is list else m['entries'];assert len(rows)==count
 for e in rows:
  p=Path(e['path']);p=p if p.is_absolute() else root/p;assert p.stat().st_size==e['bytes'] and digest(p)==e['sha256'],str(p)
 checks.append(dict(root=str(root),manifest=mf,sha256=digest(root/mf),count=count,bad=0))
save(H/'reference/upstream-before.json',checks)
W=H/'selfchecks/work'/('q07-'+uuid.uuid5(SEED,'work').hex[:8]);W.mkdir(parents=True,exist_ok=True);assert not (W/'f/home').exists(),'NO_PREPARE_AFTER_EXECUTION';pins=load_pins(lambda p:Path(p).read_bytes());inputs={}
root=W/'f';root.mkdir(exist_ok=True);home=root/'home';raw=legal_raw(fc,139264,128);(root/'fixture-facts.raw').write_bytes(raw);p=json.loads((H/'release/capture-policy.json').read_bytes());pid=str(uuid.uuid5(SEED,'facts'));run='D1MA02-Q07_FACTS';scope=sha('|'.join((pid,p['entrySha256'],p['productSealSha256'],p['planSha256'],run)).encode());p.update(mode='OFFLINE_FIXTURE',scope=scope,planId=pid,runId=run,evidenceRoot=str(home/'outputs'));now=datetime.now(timezone.utc)
t=dict(schema='GLOBAL_IDLE_FACT_PREAUTH_V1',mode='OFFLINE_FIXTURE',sourceThreadId='01a107c3-2bf9-7fa0-94a0-234258ca6774',sourceTurnId=str(uuid.uuid4()),notBeforeUtc=(now-timedelta(seconds=1)).isoformat(),expiresUtc=(now+timedelta(seconds=79)).isoformat(),scope=scope,planId=pid,runId=run,nonce=str(uuid.uuid5(SEED,pins['sourceSealSha256']+':nonce')),home=str(home),evidenceRoot=p['evidenceRoot'],policySha256=sha(enc(p)),**{k:pins[k] for k in ('sourceSealSha256','gateSourcesSha256','collectorSha256','binderSha256','entrySha256','runtimeIdentitySha256','factPlanSha256')},sdk=pins['sdk'],device=dict(serial='HA1Q6WXR',model='TB138FC',api=31,user=0),queries=pins['queries'],limits=dict(LIMITS));assert validate(enc(t),sha(enc(t)),p,pins)==t;save(root/'template.json',t);save(root/'policy.json',p)
targets={};src=json.loads((H/'reference/runner-source-seal.json').read_bytes())['sources'];roleplan=json.loads((H/'reference/exact-seven-role-plan.json').read_bytes())
for label in ('positive','wrong-firmware','receipt-replace'):
 f=W/label;targethome=f/'home';pid=str(uuid.uuid5(SEED,label));run='D1MA02-Q07_'+label.upper().replace('-','_');scope=sha('|'.join((pid,src['tools/capture_android02.ps1'],roleplan['product']['sealSha256'],src['reference/exact-seven-role-plan.json'],run)).encode());targets[label]=dict(folder=str(f),home=str(targethome),target=dict(scope=scope,planId=pid,runId=run,sourceSealSha256=pins['sourceSealSha256'],planSha256=src['reference/exact-seven-role-plan.json'],mode='OFFLINE_FIXTURE',evidenceRoot=str(f/'authority/outputs')),request=str(f/'request.json'),reply=str(f/'reply'))
from fact_preauth import complete_source_plan,FACT_RUNTIME_FILES06
gf=json.loads((H/'reference/gate-sources.json').read_bytes())['files']
paths={H/'reference/runner-source-seal.json',H/'reference/gate-sources.json',H/'tools/runtime_binding.py',H/'reference/current-runtime-identity.json',H/'selfchecks/route_fixture.py',H/'selfchecks/fact_fixture.py',H/'reference/route-backend-contract.json',H/'tools/win32_route.py',H/'tools/fact_preauth.py',H/'tools/fact_collector.py',H/'tools/facts_entry.py',H/'reference/fact-plan.json',root/'fixture-facts.raw'}
paths.update(H/e['path'] for e in gf);paths.update(Path(e['path']) for e in FACT_RUNTIME_FILES06)
source_plan=complete_source_plan(p,gf,FACT_RUNTIME_FILES06,{str(x):x.stat().st_size for x in paths},root/'fixture-facts.raw',len(raw));save(H/'reference/fact-source-plan07.json',source_plan)
profile=[]
for f in H.rglob('*'):
 if f.is_file() and f.suffix in ('.py','.ps1','.json','.txt') and not any(k in f.parts for k in ('work','evidence')) and f.name not in ('profile07.json','plan07.json','full-manifest.json'):
  profile.append(dict(path=f.relative_to(H).as_posix(),sha256=digest(f)))
plan=dict(schema='QUALIFICATION07_BATCH_PLAN_V1',revision=REV['id'],batchStart=BATCH_START,batchDeclarationSha256=digest(H.parent/'batch-declaration07.json'),work=str(W),facts=dict(root=str(root),home=str(home),rawSha256=sha(raw),templateSha256=sha(enc(t))),targets=targets,wholeSeconds=360,stopNew=320,readCap=1073741824,savedCap=16777216,processCap=96,concurrency=1,retry=0,SDK=0,hostPopen=16,nestedFactsPopen=2,captureDotNet=4,outerWorker=1,totalProcessGraph=23,conditionalFailureMaxProcessGraph=25,sourceReservation=dict(factsGate=33554432,targetGates=67108864,runnerSources=100663296,driverAndModels=268435456,total=469762048),plannedPrefix=2,expectedPositiveRoles=['identity','global_idle'],expectedNegative='FACT_IDENTITY_FIRMWARE_DISAGREEMENT',derivedArgv='Exact original new home only; original request/predecessor/admission hashes computed once from closed new outputs before Popen; no generic dispatcher',expectedEnvironment=dict(os.environ),cwd=str(Path.cwd()),inputPins={str(f):digest(f) for f in W.rglob('*') if f.is_file()})
assert plan['sourceReservation']['total']<plan['readCap'];save(H/'reference/plan07.json',plan);save(H/'reference/profile07.json',profile)
for f in H.rglob('*.py'):
 if 'work' not in f.parts:compile(f.read_text(),str(f),'exec')
print(json.dumps(dict(plan=digest(H/'reference/plan07.json'),pins=len(profile),productProcesses=0)))
