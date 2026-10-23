"""Pure admission roundtrip and final pre-dynamic freeze; no constructors."""
from pathlib import Path
from datetime import datetime,timezone,timedelta
import sys,json,os,uuid,time,copy,hashlib,subprocess,ast
H=Path(__file__).resolve().parent;C=H.parent/'d1android02-readonly-facts-preauth01'
sys.path[:0]=[str(H),str(C/'tools')]
from driver_guard import source_key,resolve_key,relative_key,pin_map,tuple_key,Registry,PY,PS,sha,env_hash
from fact_preauth import load_pins,encode,validate
def save(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n',encoding='utf-8',newline='\n')
def reject(fn,expected):
 try:fn()
 except ValueError as e:
  assert str(e)==expected,(str(e),expected);return str(e)
 raise AssertionError('EXPECTED_PURE_REJECT')
manifest=json.loads((C/'reference/full-manifest.json').read_bytes());bad=[]
for row in manifest['files']:
 if sha((C/row['path']).read_bytes())!=row['sha256']:bad.append(row['path'])
assert not bad and len(manifest['files'])==56
batch=uuid.uuid4().hex;W=H/'work'/('batch-'+batch[:12]);qc=W/'qualification';qc.mkdir(parents=True,exist_ok=False)
OWN=C/'selfchecks/work'/('selfcheck02-'+batch[:12])
env=dict(SystemRoot='C:\\Windows',WINDIR='C:\\Windows',TEMP=str(qc),TMP=str(qc))
pins=load_pins(lambda p:Path(p).read_bytes());source=json.loads((C/'reference/runner-source-seal.json').read_bytes())['sources'];inputs={}
for name in ('pure','new-original','legacy-original','explicit-cli'):
 p=json.loads((C/'release/capture-policy.json').read_bytes());home=OWN/name/'home';root=home/'outputs';pid=str(uuid.uuid4());run='D1MA02-FACTS_'+uuid.uuid4().hex[:8].upper();now=datetime.now(timezone.utc)
 scope=sha('|'.join((pid,source['tools/capture_android02.ps1'],p['productSealSha256'],p['planSha256'],run)).encode());p.update(mode='OFFLINE_FIXTURE',scope=scope,planId=pid,runId=run,evidenceRoot=str(root))
 t=dict(schema='GLOBAL_IDLE_FACT_PREAUTH_V1',mode='OFFLINE_FIXTURE',sourceThreadId='01a107c3-2bf9-7fa0-94a0-234258ca6774',sourceTurnId=str(uuid.uuid4()),notBeforeUtc=(now-timedelta(seconds=1)).isoformat(),expiresUtc=(now+timedelta(seconds=80)).isoformat(),scope=scope,planId=pid,runId=run,nonce=str(uuid.uuid4()),home=str(home),evidenceRoot=str(root),policySha256=sha(encode(p)),**{k:pins[k] for k in ('sourceSealSha256','gateSourcesSha256','collectorSha256','binderSha256','entrySha256','runtimeIdentitySha256','factPlanSha256')},sdk=pins['sdk'],device=dict(serial='HA1Q6WXR',model='TB138FC',api=31,user=0),queries=pins['queries'],limits=dict(wholeSeconds=90,gateSeconds=30,qualificationSeconds=15,outerSeconds=30,proofSeconds=10,sdkChildren=1,stdoutBytes=139264,stderrBytes=8192,combinedBytes=147456,concurrency=1,retry=0))
 assert validate(encode(t),sha(encode(t)),p,pins)==t
 inputs[name]=dict(policy=p,template=t,pins=pins)
save(H/'reference/prepared-inputs.json',inputs)
folder=W/'explicit-inputs';folder.mkdir();(folder/'template.json').write_bytes(encode(inputs['explicit-cli']['template']));(folder/'policy.json').write_bytes(encode(inputs['explicit-cli']['policy']))
original=json.loads((C/'reference/profile.json').read_bytes());rows=[];oldroundtrip=[]
for rel,h in original['scriptPins'].items():
 p=C/rel;key=source_key(p);assert sha(p.read_bytes())==h and resolve_key(key)==p
 rows.append(dict(key=key,sha256=h));oldroundtrip.append(dict(originalKey=rel,canonicalKey=key,sha256=h,roundtrip=True))
for p in list(H.glob('*.py'))+list((H/'driver').rglob('*')):
 if p.is_file():rows.append(dict(key=source_key(p),sha256=sha(p.read_bytes())))
mapped=pin_map(rows)
for key,h in mapped.items():assert source_key(resolve_key(key))==key and sha(resolve_key(key).read_bytes())==h
opts=dict(stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
calls=[]
def add(label,a,k):
 i=5 if a[0]==PY else 4;calls.append(dict(label=label,argv=a,kwargs=k,sourceKey=source_key(a[i]),id=tuple_key(a,k)))
for mode in ('ok','fail'):add('qualification-python-'+mode,[PY,'-I','-X','utf8','-B',str(H/'driver/reuse/owned_child.py'),mode],dict(opts,executable=PY,cwd=str(qc),env=env,shell=False,close_fds=True))
add('qualification-PS0',[PS,'-NoProfile','-NonInteractive','-File',str(H/'driver/reuse/owned_child.ps1')],dict(opts,executable=PS,cwd=str(qc),env=env,shell=False,close_fds=True))
add('semantic',[PS,'-NoProfile','-NonInteractive','-File',str(C/'selfchecks/review_semantics.ps1'),'-InputFile',str(W/'semantics-input.json'),'-OutputFile',str(W/'semantics-results.json')],dict(opts,executable=PS,cwd=None,env=None,shell=False,close_fds=True))
add('preStart13',[PS,'-NoProfile','-NonInteractive','-File',str(C/'selfchecks/prestart_lifetimes.ps1'),'-OutputFile',str(W/'prestart.json')],dict(opts,executable=PS,cwd=None,env=None,shell=False,close_fds=True))
for name in ('new-original','legacy-original','explicit-cli'):
 add(name+'-route',[PY,'-I','-X','utf8','-B',str(C/'selfchecks/route_fixture.py'),str(OWN/name/'home/outputs/gate-context.json')],dict(opts))
 add(name+'-facts',[PY,'-I','-X','utf8','-B',str(C/'selfchecks/fact_fixture.py'),'COMPLETE'],dict(opts,shell=False))
add('explicit-cli',[PY,'-I','-X','utf8','-B',str(C/'tools/facts_entry.py'),'--template',str(folder/'template.json'),'--approved-template-sha256',sha(encode(inputs['explicit-cli']['template'])),'--policy',str(folder/'policy.json')],dict(opts,executable=PY,cwd=None,env=None,shell=False,close_fds=True))
assert len(calls)==12
unique={}
for row in calls:
 if row['id'] not in unique:unique[row['id']]=dict(row,plannedMultiplicity=1)
 else:unique[row['id']]['plannedMultiplicity']+=1
profile=dict(schema='PREAUTH01_SELFCHECK02_PROFILE_V1',hostCwd=str(Path.cwd()),qualificationCwd=str(qc),qualificationEnv=env,inheritedEnvSha256=env_hash(dict(os.environ)),driverRoot=str(H),candidateRoot=str(C),candidateOwnedOutput=str(OWN),pinRows=rows,scriptPins=mapped,tuples=list(unique.values()),allPlannedCalls=calls,inputPins={str(p):sha(p.read_bytes()) for p in (H/'reference/prepared-inputs.json',folder/'template.json',folder/'policy.json')},audit='MEMORY_OBSERVATION_ONLY',sourceSealSha256=sha((C/'reference/runner-source-seal.json').read_bytes()))
reg=Registry(profile,time.monotonic());tuplepass=[]
for row in calls:
 answer=reg.check(row['argv'],row['kwargs']);assert answer['sourceKey']==row['sourceKey'];tuplepass.append(dict(label=row['label'],sourceKey=row['sourceKey'],tupleId=answer['tupleId'],accepted=True))
negative=[]
for key in ('driver/../x','driver/./x','driver//x','/driver/x','D:/x','driver\\x','outside/x'):
 negative.append(dict(key=key,reason=reject(lambda key=key:relative_key(key),'PIN_NAMESPACE' if key=='outside/x' else 'PIN_NONCANONICAL_RELATIVE_POSIX')))
base=rows[0]
for more in (base,dict(base,key=base['key'].upper().replace('CANDIDATE/','candidate/'))):negative.append(dict(case='duplicate-or-case-collision',reason=reject(lambda more=more:pin_map([base,more]),'PIN_DUPLICATE_OR_COLLISION')))
negative.append(dict(case='absolute-outside-root',reason=reject(lambda:source_key(Path('D:/outside/a.py')),'PIN_OUTSIDE_ROOT')))
badprofile=copy.deepcopy(profile)
for row in badprofile['pinRows']:
 if row['key']==calls[0]['sourceKey']:row['sha256']='0'*64
rb=Registry(badprofile,time.monotonic())
negative.append(dict(case='wrong-content-pin-static',reason=reject(lambda:rb.check(calls[0]['argv'],calls[0]['kwargs']),'PROFILE_SOURCE')))
for row in calls:
 a=row['argv'].copy();a.append('EXTRA');negative.append(dict(case='extra:'+row['label'],reason=reject(lambda a=a,row=row:reg.check(a,row['kwargs']),'PROFILE_EXACT_TUPLE')))
 a=row['argv'].copy();a[0]='D:/Android/SDK/platform-tools/adb.exe';negative.append(dict(case='wrong-program:'+row['label'],reason=reject(lambda a=a,row=row:reg.check(a,row['kwargs']),'PROFILE_PROGRAM_ARGV')))
 k=copy.deepcopy(row['kwargs']);k['cwd']='D:/outside';negative.append(dict(case='wrong-cwd:'+row['label'],reason=reject(lambda k=k,row=row:reg.check(row['argv'],k),'PROFILE_EXACT_TUPLE')))
 k=copy.deepcopy(row['kwargs']);k['env']={'SystemRoot':'C:\\Windows'};negative.append(dict(case='wrong-env:'+row['label'],reason=reject(lambda k=k,row=row:reg.check(row['argv'],k),'PROFILE_EXACT_TUPLE')))
# Exact Windows applicationName/commandLine model; never a Popen constructor.
for row in (calls[0],next(x for x in calls if x['label']=='new-original-route')):
 model=reg.check(row['argv'],row['kwargs']);reg.local.expected=model;reg.observe('subprocess.Popen',(model['applicationName'],model['commandLine'],model['cwd'],row['kwargs'].get('env')));assert reg.events[-1]['matches'];reg.local.expected=None
reg.events.clear()
for p in H.rglob('*.py'):compile(p.read_text(),str(p),'exec')
assert not reg.calls and not reg.events and not reg.stop
save(H/'reference/profile.json',profile)
save(H/'reference/batch-plan.json',dict(schema='PREAUTH01_SELFCHECK02_PLAN_V1',batch=batch,candidateRoot=str(C),driverRoot=str(H),driverOutput=str(W),candidateOwnedOutput=str(OWN),sourceSealSha256=sha((C/'reference/runner-source-seal.json').read_bytes()),gateSourcesSha256=sha((C/'reference/gate-sources.json').read_bytes()),wholeSeconds=360,stopNewSeconds=320,readBytes=1073741824,savedBytes=16777216,auxiliaryProcesses=96,concurrency=1,retry=0,estimateSeconds=90,plannedGraphProcessBound=12,ioReservation=dict(originalGateSourceCaps=805306368,pythonAndPSImportControlUpper=67108864,driverAndSourcesUpper=33554432,total=905969664)))
save(H/'evidence/pure-preflight.json',dict(original31=len(oldroundtrip),oldKeyRoundtrips=oldroundtrip,allPins=len(rows),pinRowsBad=0,allPlannedCalls=len(calls),uniqueCallTuples=len(unique),positiveTuples=tuplepass,negative=negative,actualPopen=0,actualCapture=0,actualGate=0,actualClaim=0,actualOnce=0,original56Bad=bad,profileSha256=sha((H/'reference/profile.json').read_bytes())))
print(json.dumps(dict(original31=len(oldroundtrip),allPins=len(rows),allTuples=len(calls),purePassed=True,profile=sha((H/'reference/profile.json').read_bytes()))))
