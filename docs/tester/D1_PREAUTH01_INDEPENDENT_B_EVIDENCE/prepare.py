"""File-only full preflight; final synthetic 80s inputs frozen just before run."""
from pathlib import Path
from datetime import datetime,timezone,timedelta
import ast,builtins,collections,copy,hashlib,json,os,subprocess,symtable,sys,time,uuid,zipfile
R=Path(__file__).resolve().parent;T=R.parent;B=T.parent/'coder/d1android02-readonly-facts-preauth01';D=B.parent/'d1android02-readonly-facts-preauth01-selfcheck02';sys.path[:0]=[str(R),str(B/'tools'),str(B/'selfchecks')]
from driver_guard import Registry,PY,PS,source_key,pin_map,tuple_key,env_hash
import fact_preauth as fp
from write_guard import allowed
def sha(b):return hashlib.sha256(b).hexdigest()
def save(p,d):put(p,(json.dumps(d,ensure_ascii=True,indent=2)+'\n').encode())
def put(p,b):
 allowed(p);p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('xb') as f:f.write(b);f.flush()
def packet(base,rel,h,n,archive,zh,zn):
 raw=(base/rel).read_bytes();assert sha(raw)==h;m=json.loads(raw);assert len(m['files'])==n
 for x in m['files']:
  b=(base/x['path']).read_bytes();assert len(b)==x['bytes'] and sha(b)==x['sha256'],x['path']
 assert sha(archive.read_bytes())==zh
 with zipfile.ZipFile(archive) as z:
  assert len(z.namelist())==zn and len(set(z.namelist()))==zn
  for x in [*m['files'],dict(path=rel,bytes=len(raw),sha256=h)]:
   b=z.read(x['path']);assert len(b)==x['bytes'] and sha(b)==x['sha256']
 return dict(files=n,bytes=sum(x['bytes'] for x in m['files']),manifestSha256=h,zipSha256=zh,zipMembers=zn,bad=0)
def main():
 assert not (R/'order.json').exists()
 old=packet(B,'reference/full-manifest.json','3ce81441d75e8a47368078197fcc43a20ace8eef916f1f3dcbd6f08c3cd8059c',56,B/'readonly-facts-preauth01-blocked-frozen.zip','e563573ca4d51c428ae7c56d79f4b5b7e03bd6e106157f95286c849a91afed52',57)
 dev=packet(D,'reference/full-manifest.json','2c8c69d8ecec03d7bc339ae8bdb2349bdb942258f0c050b183197f1aa960fe61',108,D/'preauth01-selfcheck02-frozen.zip','1a0fb5e9d424e83ed6de8668607a05b28365c401b3d527d55cfaf7f959773b3c',109)
 assert sha((B/'reference/runner-source-seal.json').read_bytes())=='02ac6306cb55b08787cd63d77a2bcdc1be24e522fa5a6480f4ba287df0e708df'
 assert sha((B/'reference/gate-sources.json').read_bytes())=='bdc8cba37c2157077ad3066709c4a4ca732f525746980521cbcc623203912192'
 source=json.loads((B/'reference/runner-source-seal.json').read_bytes())['sources'];assert len(source)==20
 for rel,h in source.items():assert sha((B/rel).read_bytes())==h,rel
 runtime=json.loads((B/'reference/current-runtime-identity.json').read_bytes())
 for x in runtime['files']:
  b=Path(x['path']).read_bytes();assert len(b)==x['bytes'] and sha(b)==x['sha256']
 save(R/'before-audit.json',dict(original56=old,developer108=dev,source20Bad=0,gate12Bad=0,runtimeFiles=len(runtime['files']),runtimeBad=0,knownHistoricalOverwrite='Restored old result now matches; do not claim it never changed during developer run',actualPopen=0))
 # Check definition dependency closure without invoking their bodies/once.
 text=(R/'reused_checks.py').read_text();table=symtable.symtable(text,'reused_checks.py','exec');required=set()
 def walk(s):
  for name in s.get_identifiers():
   v=s.lookup(name)
   if v.is_referenced() and v.is_global():required.add(name)
  for child in s.get_children():walk(child)
 walk(table)
 worker=ast.parse((R/'worker.py').read_text());nsnode=next(n for n in ast.walk(worker) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='dict' and any(k.arg=='PreparedFacts' for k in n.keywords));provided={k.arg for k in nsnode.keywords}|{n.name for n in ast.parse(text).body if isinstance(n,ast.FunctionDef)}|set(dir(builtins));missing=sorted(required-provided);assert not missing,missing
 save(R/'namespace-preflight.json',dict(requiredGlobals=sorted(required),providedExplicitGlobals=sorted(k.arg for k in nsnode.keywords),missing=missing,actualPreparedFactsConstructors=0,actualGate=0,actualOnce=0))
 from contract_cases import make
 from independent_cases_original import cases as independent
 from contract03_cases import cases as extra
 original=make();ind=independent(B);new=extra();semantic=original+ind+new;assert len(original)==98 and len(ind)==175 and sum(x['expected']=='PASS' for x in ind)==17 and len(new)==73
 W=R/'work';shards=[];parts=[];part=[]
 for row in semantic:
  if part and len(fp.encode([*part,row]))>900000:parts.append(part);part=[]
  part.append(row)
 if part:parts.append(part)
 for i,part in enumerate(parts):
  inp=W/('semantics-input-'+str(i)+'.json');out=W/('semantics-results-'+str(i)+'.json');raw=fp.encode(part);assert len(raw)<=1048576;put(inp,raw);argv=[PS,'-NoProfile','-NonInteractive','-File',str(B/'selfchecks/review_semantics.ps1'),'-InputFile',str(inp),'-OutputFile',str(out)];shards.append(dict(input=str(inp),output=str(out),rows=len(part),sha256=sha(raw),argv=argv))
 save(R/'reference/semantic-shards.json',shards)
 batch=uuid.uuid4().hex;OWN=B/'selfchecks/work'/('indb-'+batch[:12]);assert not OWN.exists();qc=W/'qualification';qc.mkdir()
 pins=fp.load_pins(lambda p:Path(p).read_bytes());inputs={};now=datetime.now(timezone.utc)
 for name in ['pure','new-original','wrong-receiver','legacy-original','explicit-cli']:
  p=json.loads((B/'release/capture-policy.json').read_bytes());home=OWN/name/'home';root=home/'outputs';plan=str(uuid.uuid4());run='D1MA02-TESTB_'+uuid.uuid4().hex[:8].upper();scope=sha('|'.join([plan,source['tools/capture_android02.ps1'],p['productSealSha256'],p['planSha256'],run]).encode());p.update(mode='OFFLINE_FIXTURE',scope=scope,planId=plan,runId=run,evidenceRoot=str(root))
  t=dict(schema='GLOBAL_IDLE_FACT_PREAUTH_V1',mode='OFFLINE_FIXTURE',sourceThreadId=fp.COORDINATOR,sourceTurnId=str(uuid.uuid4()),notBeforeUtc=(now-timedelta(seconds=1)).isoformat(),expiresUtc=(now+timedelta(seconds=80)).isoformat(),scope=scope,planId=plan,runId=run,nonce=str(uuid.uuid4()),home=str(home),evidenceRoot=str(root),policySha256=sha(fp.encode(p)),**{k:pins[k] for k in ['sourceSealSha256','gateSourcesSha256','collectorSha256','binderSha256','entrySha256','runtimeIdentitySha256','factPlanSha256']},sdk=pins['sdk'],device=dict(serial='HA1Q6WXR',model='TB138FC',api=31,user=0),queries=pins['queries'],limits=dict(fp.LIMITS))
  assert fp.validate(fp.encode(t),sha(fp.encode(t)),p,pins)==t
  inputs[name]=dict(policy=p,template=t,pins=pins)
 save(R/'reference/prepared-inputs.json',inputs)
 folder=W/'explicit-inputs';put(folder/'template.json',fp.encode(inputs['explicit-cli']['template']));put(folder/'policy.json',fp.encode(inputs['explicit-cli']['policy']));put(folder/'policy-pretty.json',json.dumps(inputs['explicit-cli']['policy'],indent=2).encode())
 from independent_models import matrix
 models=matrix(fp,inputs['pure']['policy'],inputs['pure']['template'],pins);save(R/'pure-matrix-preflight.json',dict(total=models['total'],bad=models['bad'],actualGate=0,actualOnce=0));assert not models['bad'],models['bad'][:3]
 # Source pins only cover this exact product and independent driver files.
 pinrows=[]
 for p in [*R.glob('*.py'),*list((R/'driver').rglob('*.py')),*list((R/'driver').rglob('*.ps1')),*list((B/'tools').glob('*.py')),*list((B/'tools').glob('*.ps1')),*list((B/'selfchecks').glob('*.py')),*list((B/'selfchecks').glob('*.ps1'))]:
  if p.suffix=='.py':ast.parse(p.read_text(encoding='utf-8-sig'))
  pinrows.append(dict(key=source_key(p),sha256=sha(p.read_bytes())))
 mapped=pin_map(pinrows);opts=dict(stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.PIPE);calls=[]
 def add(label,a,k):
  i=5 if a[0]==PY else 4;calls.append(dict(label=label,argv=a,kwargs=k,sourceKey=source_key(a[i]),id=tuple_key(a,k)))
 env=dict(SystemRoot='C:\\Windows',WINDIR='C:\\Windows',TEMP=str(qc),TMP=str(qc))
 for mode in ['ok','fail']:add('qualify-'+mode,[PY,'-I','-X','utf8','-B',str(R/'driver/reuse/owned_child.py'),mode],dict(opts,executable=PY,cwd=str(qc),env=env,shell=False,close_fds=True))
 add('qualify-PS',[PS,'-NoProfile','-NonInteractive','-File',str(R/'driver/reuse/owned_child.ps1')],dict(opts,executable=PS,cwd=str(qc),env=env,shell=False,close_fds=True))
 def outerkwargs(a):return dict(opts,executable=a[0],cwd=None,env=None,shell=False,close_fds=True)
 for i,s in enumerate(shards):add('current-semantics-'+str(i),s['argv'],outerkwargs(s['argv']))
 a=[PS,'-NoProfile','-NonInteractive','-File',str(B/'selfchecks/prestart_lifetimes.ps1'),'-OutputFile',str(W/'prestart.json')];add('preStart13',a,outerkwargs(a))
 for name in ['new-original','wrong-receiver','legacy-original','explicit-cli']:
  add(name+'-route',[PY,'-I','-X','utf8','-B',str(B/'selfchecks/route_fixture.py'),str(OWN/name/'home/outputs/gate-context.json')],dict(opts))
  if name!='wrong-receiver':add(name+'-facts',[PY,'-I','-X','utf8','-B',str(B/'selfchecks/fact_fixture.py'),'COMPLETE'],dict(opts,shell=False))
 base=[PY,'-I','-X','utf8','-B',str(B/'tools/facts_entry.py')];full=base+['--template',str(folder/'template.json'),'--approved-template-sha256',sha(fp.encode(inputs['explicit-cli']['template'])),'--policy',str(folder/'policy.json')]
 cli=[dict(name='complete',argv=full,exitCode=0,reason=None),dict(name='same-home-replay',argv=full,exitCode=2,reason='PREAUTH_FRESH_OUTPUT_REQUIRED'),dict(name='default',argv=base,exitCode=2,reason=None),dict(name='missing-external-hash',argv=base+['--template',str(folder/'template.json'),'--policy',str(folder/'policy.json')],exitCode=2,reason=None),dict(name='extra-action',argv=full+['--run-sdk-now'],exitCode=2,reason=None),dict(name='noncanonical-policy',argv=full[:-1]+[str(folder/'policy-pretty.json')],exitCode=2,reason='FACT_ENTRY_POLICY_CANONICAL_BYTES'),dict(name='wrong-external-hash',argv=full[:9]+['0'*64]+full[10:],exitCode=2,reason='PREAUTH_EXTERNAL_HASH')]
 for row in cli:add('CLI-'+row['name'],row['argv'],outerkwargs(row['argv']))
 save(R/'reference/cli-calls.json',cli)
 unique={}
 for c in calls:
  if c['id'] not in unique:unique[c['id']]=dict(c,plannedMultiplicity=1)
  else:unique[c['id']]['plannedMultiplicity']+=1
 outerEnv=dict(SystemRoot=str(Path('C:/Windows')),WINDIR=str(Path('C:/Windows')),TEMP=str(R),TMP=str(R))
 profile=dict(schema='PREAUTH01_TESTER_CLOSED_PROFILE_V1',hostCwd=str(R),inheritedEnvSha256=env_hash(outerEnv),qualificationCwd=str(qc),qualificationEnv=env,pinRows=pinrows,scriptPins=mapped,tuples=list(unique.values()),allPlannedCalls=calls,driverRoot=str(R),candidateRoot=str(B),audit='MEMORY_OBSERVATION_ONLY',expectedRuntimeEnvironment=outerEnv)
 reg=Registry(profile,time.monotonic());positive=[];negative=[]
 for row in calls:
  d=reg.check(row['argv'],row['kwargs'],check_host=False);positive.append(dict(label=row['label'],tupleId=d['tupleId'],futureHostContext=profile['hostCwd']))
  for label,a,k,expected in [('wrong-program',['D:/Android/SDK/platform-tools/adb.exe',*row['argv'][1:]],row['kwargs'],'PROFILE_PROGRAM_ARGV'),('extra',row['argv']+['UNPLANNED'],row['kwargs'],'PROFILE_EXACT_TUPLE'),('cwd',row['argv'],dict(row['kwargs'],cwd='D:/outside'),'PROFILE_EXACT_TUPLE'),('env',row['argv'],dict(row['kwargs'],env={}),'PROFILE_EXACT_TUPLE')]:
   try:reg.check(a,k,check_host=False)
   except ValueError as e:assert str(e)==expected;negative.append(dict(tuple=row['label'],case=label,reason=str(e)))
   else:raise AssertionError('PURE_NEGATIVE_NOT_REJECTED')
  reg.local.expected=d;reg.observe('subprocess.Popen',(d['applicationName'],d['commandLine'],d['cwd'],row['kwargs'].get('env')));assert reg.events[-1]['matches'];reg.local.expected=None
 assert not reg.calls and not reg.stop
 save(R/'reference/profile.json',profile)
 save(R/'tuple-preflight.json',dict(positive=positive,negative=negative,rawWindowsAuditModels=len(calls),actualPopen=0,actualOnce=0,modelHostContextExplicit=True,runtimeConstructorsUseActualHostCheck=True))
 graph=dict(parentWorkerPopen=len(calls)-2,childCliPopen=2,powerShellDotNetChildren=[dict(parent='preStart13',program=PY,argv=['-I','-X','utf8','-B','-c','print("LOCAL_PRESTART_STATE_THREE")'],sourceKey=source_key(B/'selfchecks/prestart_lifetimes.ps1'),sourcePin=sha((B/'selfchecks/prestart_lifetimes.ps1').read_bytes()),expectedOriginalWaitReadersStreamsDispose=True)],outerWorker=1,totalActualProcessUpper=len(calls)+2,popenTuples=len(calls),note='CLI route/fact are child-local, not parent registry calls. Outer worker full argv derived from final order SHA and fixed before its constructor.')
 assert len(calls)==18+len(shards) and len(cli)==7 and graph['totalActualProcessUpper']<=64
 save(R/'process-graph.json',graph)
 save(R/'write-destinations.json',dict(driverStartup=[str(R/'once.json'),str(R/'worker-self.json'),str(R/'worker-admit.json'),str(R/'outer-self.json'),str(R/'runtime')],groups=[str(W),str(R/'group-N.json'),str(OWN/'new-original/home/outputs'),str(OWN/'wrong-receiver/home/outputs'),str(OWN/'legacy-original/home/outputs'),str(OWN/'explicit-cli/home/outputs')],finallyAndException=[str(R/'worker-final.json'),str(R/'stop.json'),str(R/'outer-final.json'),str(R/'runtime/outer-expired.json')],childPS=[str(W/'semantics-results.json'),str(W/'prestart.json'),str(W/'prestart-<guid>')],childCLI='Pinned policy restricts original Gate outputs/claim to explicit-cli/home; fixed producer stdout only',writeGuard='Parent builtins.open/io.open/os.open/os.mkdir pre-operation whitelist; fixed Popen DEVNULL only inside admitted constructor; no audit rejection',neverWrite=[str(B/'evidence'),str(B/'DELIVERY.md'),str(D)],historicalWorkerMainExecuted=False))
 save(R/'budget.json',dict(outerSeconds=360,workerSeconds=300,stopNewSeconds=240,children=64,plannedWholeGraph=graph['totalActualProcessUpper'],readBytes=2147483648,readCalls=8192,artifactBytes=33554432,artifactFiles=2048,singleArtifactBytes=1048576,singleStreamBytes=1048576,auxObserveSeconds=90,concurrency=1,retry=0,ioReservation=dict(fourOriginalGateCaps=1073741824,pythonAndPSImportControl=805306368,driverAndArchive=67108864,modelPreparations=134217728,total=2080374784,meaning='Conservative reservation; not total physical IO measurement'),estimatedSeconds=80,originalProductionLimits='UNCHANGED'))
 rows=[]
 for p in sorted(R.rglob('*')):
  if p.is_file():
   b=p.read_bytes();assert len(b)<=1048576;rows.append(dict(path=str(p),bytes=len(b),sha256=sha(b)))
 now=datetime.now(timezone.utc);o=dict(schema='PREAUTH01_INDEPENDENT_B_ORDER_V1',batch=batch,nonce=str(uuid.uuid4()),work=str(OWN),candidate=str(B),sources=rows,allowedStarts=1,notBeforeUtc=now.isoformat(),expiresUtc=(now+timedelta(seconds=900)).isoformat(),sourceSeal='02ac6306cb55b08787cd63d77a2bcdc1be24e522fa5a6480f4ba287df0e708df',sourceThread=fp.COORDINATOR)
 save(R/'order.json',o);print(json.dumps(dict(orderSha256=sha((R/'order.json').read_bytes()),work=str(OWN),templateExpiresUtc=inputs['explicit-cli']['template']['expiresUtc'],tuples=len(calls),wholeGraph=graph['totalActualProcessUpper'],namespaceMissing=missing,pureMatrix=models['total'])))
if __name__=='__main__':main()
