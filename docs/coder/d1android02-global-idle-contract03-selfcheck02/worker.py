"""One frozen SELFCHECK02 batch. Product17 remains read-only throughout."""
from pathlib import Path
import sys,os,time,json,copy,hashlib,subprocess,threading,uuid
H=Path(__file__).resolve().parent
sys.path[:0]=[str(H),str(H/'reuse'),str(H/'helpers')]
from guard import Registry,B,PY,PS,digest,env_digest
from owned_capture import Capture,CUSTODY as AUX_CUSTODY
from evidence_io import Journal
START=time.monotonic();plan=json.loads((H/'reference/plan.json').read_bytes());profile=json.loads((H/'reference/profile.json').read_bytes());W=H/'work';results=[];caps=[];stop=False;ns=None
registry=Registry(profile)
class Control:
 def __init__(self):self.stop=False;self.reasons=[]
 def request(self,r):self.stop=True;self.reasons.append(r)
 def poll(self):return self.stop
 def returned(self):return True # no external STOP IO was created by this adapter
control=Control()
def save(p,d):p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
def load(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def known_child(argv,qual=False,expected=0):
 seq=len(caps);root=W/('capture-'+str(seq));root.mkdir()
 cwd=profile['qualificationCwd'] if qual else None;env=profile['qualificationEnv'] if qual else None
 p=dict(argv=list(argv),executable=argv[0],cwd=cwd,env=env,profile='python_fail' if expected else 'python_ok' if argv[0]==PY else 'powershell_ok')
 # This check precedes Capture/Popen and any stream/temporary child allocation.
 registry.check(p['argv'],dict(executable=argv[0],cwd=cwd,env=env,shell=False,close_fds=True,stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.PIPE))
 journal=Journal(root);c=Capture(p,copy.deepcopy(p),journal,control,registry);caps.append(c)
 c.launch(registry,5 if qual else 80);answer=c.collect()
 fact=dict(sequence=seq,disposition=answer,exitCode=getattr(c,'exit_code',None),semantic=getattr(c,'semantic_status',None),facts=c.facts,failure=c.failure,counts=c.counts,returned=c.returned,identity=getattr(c,'identity',None),journal=journal.facts(),elapsed=time.monotonic()-c.start)
 save(root/'holder-observation.json',fact)
 if answer.startswith('RETAIN') or not c.returned:
  control.request('ORIGINAL_RETURN_UNKNOWN');save(H/'evidence/PENDING_UNKNOWN.json',fact)
  while True:time.sleep(.1) # retain originals; no kill/retry/second close
 return c.exit_code,bytes(c.buffers[0]),bytes(c.buffers[1])
def child(argv):return known_child(argv)
def pure_qualification():
 argv=[PY,'-I','-X','utf8','-B',str(H/'reuse/owned_child.py'),'ok'];kw=dict(executable=PY,cwd=profile['qualificationCwd'],env=profile['qualificationEnv'],shell=False,close_fds=True,stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
 good=registry.check(argv,kw);neg=[]
 for key,val in [('program','D:/Android/SDK/platform-tools/adb.exe'),('extra','EXTRA'),('cwd','D:/outside'),('env',{'SystemRoot':'C:\\Windows'})]:
  a=argv.copy();k=copy.deepcopy(kw)
  if key=='program':a[0]=val
  elif key=='extra':a.append(val)
  else:k[key]=val
  try:registry.check(a,k);raise AssertionError('PURE_PROFILE_NEGATIVE_ACCEPTED')
  except ValueError as e:neg.append(dict(kind=key,reason=str(e)))
 # Pure observations exercise None/applicationName and serialized Windows argv;
 # no original Popen/temporary handle is used to test these negatives.
 sample=dict(good);sample['applicationName']=None;registry.local.expected=sample
 before=len(registry.events);registry.observe('subprocess.Popen',(None,sample['commandLine'],sample['cwd'],dict(kw['env'])));assert registry.events[-1]['matches']
 registry.observe('subprocess.Popen',(PY,sample['commandLine'],sample['cwd'],dict(kw['env'])));assert not registry.events[-1]['matches']
 model=registry.events[before:];del registry.events[before:];registry.stop=False;registry.local.expected=None
 return dict(positive=True,negative=neg,pureAuditModels=model,wrongProgramsActuallyStarted=0)
def qualify():
 pure=pure_qualification();out=[]
 for name,argv,expected in [('python_ok',[PY,'-I','-X','utf8','-B',str(H/'reuse/owned_child.py'),'ok'],0),('python_fail',[PY,'-I','-X','utf8','-B',str(H/'reuse/owned_child.py'),'fail'],7),('powershell_ok',[PS,'-NoProfile','-NonInteractive','-File',str(H/'reuse/owned_child.ps1')],0)]:
  code,b,e=known_child(argv,True,expected);c=caps[-1];assert code==expected and not e and c.returned and time.monotonic()-c.start<5 and c.failure is None and not registry.stop,(name,code,e)
  out.append(dict(name=name,exitCode=code,semantic=c.semantic_status,allOriginalsReturned=True,seconds=time.monotonic()-c.start))
 assert not AUX_CUSTODY and not control.stop
 return dict(pure=pure,actualThree=out,nonzeroClassifiedKnownReturned=True)
def group(name,fn,qualification=False):
 global stop
 if stop or registry.stop or control.stop or time.monotonic()-START>=320:
  results.append(dict(name=name,status='NOT_RUN_STOP_NEW_ADMISSION'));return
 before=time.monotonic()
 try:
  detail=fn();results.append(dict(name=name,status='PASS',seconds=time.monotonic()-before,detail=detail))
 except BaseException as e:
  results.append(dict(name=name,status='FAIL',seconds=time.monotonic()-before,error=repr(e)))
  if qualification:stop=True
 save(H/'evidence'/('group-'+str(len(results))+'.json'),results[-1])
def setup():
 global ns
 sys.path.insert(0,str(B/'tools'))
 ns={'__file__':str(H/'helpers/affected_definitions.py')};exec((H/'helpers/affected_definitions.py').read_text(),ns);ns['child']=child
 # The original cli function looks child up in its own namespace at call time.
 import groups as g
 g.B=B;g.H=H;g.W=W;g.PS=PS;g.child=child;g.ns=ns;g.save=save;g.load=load;g.rejection=ns['rejection'];g.plan=dict(plan,fixtureRoot=plan['testerRoot'])
 return g
def original_prestart():
 code,out,err=child([PS,'-NoProfile','-NonInteractive','-File',str(H/'helpers/prestart_lifetimes.ps1'),'-OutputFile',str(W/'prestart.json')]);assert code==0 and not err,(code,err);d=load(W/'prestart.json');assert d['allPassed'];return d
def original_collector():
 cn={'__file__':str(H/'helpers/collector_definitions.py'),'SHARED_NS':ns};exec((H/'helpers/collector_definitions.py').read_text(),cn);cn['child']=child
 return dict(pure=cn['collector_pure'](),owned=cn['owned_collector']())
def audit_originals():
 from production_runner import RUNNER_CUSTODY
 from entry_gates import CUSTODY
 from fact_collector import CUSTODY as FC
 if RUNNER_CUSTODY or CUSTODY or FC or AUX_CUSTODY:
  save(H/'evidence/PENDING_UNKNOWN.json',dict(runner=len(RUNNER_CUSTODY),gate=len(CUSTODY),fact=len(FC),aux=len(AUX_CUSTODY)))
  control.request('NEW_CUSTODY_UNKNOWN');return False
 return True
def material_snapshot():
 src=load(B/'reference/freeze-manifest.json');bad=[]
 for r in src['files']:
  if digest((B/r['path']).read_bytes())!=r['sha256']:bad.append(r['path'])
 assert not bad,bad
 return dict(rows=len(src['files']),bad=bad,sourceSeal=digest((B/'reference/runner-source-seal.json').read_bytes()))
before=material_snapshot();sys.addaudithook(registry.observe);subprocess.Popen=registry.construct
try:
 group('finite-three-call-driver-qualification',qualify,True)
 if not stop:
  g=setup()
  for name,fn in [('pure-five-defect-parameters',g.parameters),('direct-preStart13',original_prestart),('original98-independent175-new73-semantics',g.semantics),('proposal-static-pins',g.proposal),('original-collector-and-facts-wire',original_collector),('default-deny',ns['default_deny']),('prior-source-authority-budget',ns['authority']),('original-seven-END-once',ns['full_cli']),('eleven-finite-original-faults',ns['finite_failures']),('PS-post-last-Start',lambda:ns['ps_post_guards']() if ns['positive'] else dict(status='NOT_RUN_MISSING_POSITIVE_DEPENDENCY')),('materialization-change',ns['changed_materialization']),('new-tester-root-original-seven',g.real_tester_root),('exact-small-append-source-pin',g.append_exact)]:
   group(name,fn)
   if not audit_originals():stop=True
finally:
 subprocess.Popen=ORIGINAL=__import__('guard').ORIGINAL_POPEN
 after=material_snapshot();d=dict(schema='CONTRACT03_SELFCHECK02_RESULT_V1',batch=plan['batch'],seconds=time.monotonic()-START,results=results,allPassed=bool(results) and all(r['status']=='PASS' for r in results),before=before,after=after,calls=registry.calls,audit=registry.events,ownAuxOriginalsReturned=all(c.returned for c in caps),auxCaptures=len(caps),auxCustody=len(AUX_CUSTODY),stopNew=stop or registry.stop or control.stop,actualSDK=0,actualNativeRoute=0,oldQueries=0,externalHandoff='NOT_RUN_NOT_IMPLEMENTED',D1='NOT_PASSED')
 save(H/'evidence/result.json',d);print(json.dumps(dict(groups=len(results),allPassed=d['allPassed'],seconds=d['seconds'],auxReturned=d['ownAuxOriginalsReturned'],stopNew=d['stopNew'])))
if not d['allPassed']:raise SystemExit(2)
