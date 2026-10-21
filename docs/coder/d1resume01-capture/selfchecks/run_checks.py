"""Finite local fixtures. On an unexpected pending owner this same test process retains it; never kills."""
from pathlib import Path
import subprocess,json,hashlib,shutil,time,uuid,sys
B=Path(__file__).resolve().parents[1];R=B.parents[2];PY='C:/Users/benny/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe';PS=Path('C:/Users/benny/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/powershell/pwsh.exe');ENTRY=B/'tools/capture_metadata.ps1';FIX=B/'selfchecks/capture_fixture.py';ATTEMPT=sys.argv[1] if len(sys.argv)>1 else 'fixture-001';assert ATTEMPT in ['fixture-001','fixture-002','fixture-003','fixture-004'];WORK=B/'selfchecks/work'/ATTEMPT;E=B/'evidence'/ATTEMPT
assert not E.exists();E.mkdir(parents=True);WORK.mkdir(parents=True,exist_ok=True)
commands=[];results=[];assertions=0;owned={}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')
write(E/'inputs.json',[dict(path=p.relative_to(R).as_posix(),sha256=sha(p),bytes=p.stat().st_size) for p in [ENTRY,FIX,Path(__file__).resolve()]])
def check(ok,why):
 global assertions
 assertions+=1
 if not ok:raise AssertionError(why)
def setup(name,modes=('success',),cap=512,qual=5,fault='NONE'):
 root=WORK/name;out=root/'outputs';out.mkdir(parents=True);(root/'tools').mkdir();shutil.copyfile(ENTRY,root/'tools/capture_metadata.ps1');scope=hashlib.sha256(name.encode()).hexdigest()
 slots=[]
 for i,mode in enumerate(modes):
  argv=[PY,'-X','utf8','-B',FIX.as_posix(),mode]
  if mode=='late':argv.append(str(out/'child-return.gate'))
  slots.append(dict(id='LOCAL_'+str(i),phase='M1',argv=argv,maxTextBytes=cap,qualificationSeconds=qual))
 policy=dict(schema='RESUME01_CAPTURE_POLICY_V1',mode='OFFLINE_FIXTURE',planId=str(uuid.uuid4()),scope=scope,evidenceRoot=str(out),slots=slots,entrySha256=sha(ENTRY),toolSha256=sha(Path(PY)),fixtureScriptSha256=sha(FIX),fixtureFault=fault,fixtureGatePath=str(out/'file-close.gate'),executionPins=[])
 pp=root/'release/capture-policy.json';write(pp,policy);requests=[]
 for slot in slots:
  request=dict(schema='RESUME01_CAPTURE_REQUEST_V1',id=slot['id'],policySha256=sha(pp),scope=scope,evidenceRoot=str(out),argv=slot['argv'],maxTextBytes=cap,qualificationSeconds=qual);p=root/(slot['id']+'.json');write(p,request);requests.append(p)
 return dict(name=name,root=root,out=out,scope=scope,slots=slots,requests=requests,entry=root/'tools/capture_metadata.ps1')
def start(case,index=0,proof=None,request=None,label=None):
 name=label or case['name']+'-'+str(index);request=request or case['requests'][index];argv=[str(PS),'-NoLogo','-NoProfile','-NonInteractive','-File',str(case['entry']),'-RequestPath',str(request)]
 if proof:argv+=['-PredecessorProofSha',proof]
 so=(E/(name+'.stdout.txt')).open('xb');se=(E/(name+'.stderr.txt')).open('xb');p=subprocess.Popen(argv,stdout=so,stderr=se);owned[name]=(p,so,se,case['out']);commands.append(dict(name=name,argv=argv,pid=p.pid));write(E/'commands.json',commands);return name
def finish(name,timeout=15):
 p,so,se,_=owned[name]
 try:code=p.wait(timeout=timeout)
 except subprocess.TimeoutExpired:
  write(E/(name+'.pending.json'),dict(pid=p.pid,originalTestControllerPending=True,killed=False));print('PENDING original test controller retained '+name,flush=True)
  while p.poll() is None:time.sleep(.25)
  code=p.returncode
 so.close();se.close();del owned[name];out=(E/(name+'.stdout.txt')).read_bytes();err=(E/(name+'.stderr.txt')).read_bytes();write(E/(name+'.exit.json'),dict(pid=p.pid,exitCode=code,naturalReturn=True,stdoutBytes=len(out),stderrBytes=len(err)));return code,out,err
def run(case,index=0,proof=None,request=None,label=None):return finish(start(case,index,proof,request,label))
def facts(out):return json.loads(out.decode('utf-8'))
def proof(case,index,console):
 p=case['out']/(case['slots'][index]['id']+'-completion-proof.json');receipt=case['out']/(case['slots'][index]['id']+'-receipt.json')
 write(p,dict(schema='RESUME01_CAPTURE_COMPLETION_PROOF_V1',id=case['slots'][index]['id'],scope=case['scope'],controllerPid=console['controllerPid'],controllerExited=True,toolStreamsReturned=True,originalResourcesReturnedAtConsole=console['allOriginalResourcesReturnedAtConsole'],captureQualifiedAtConsole=console['captureQualified'],approvedForNext=True,captureReceiptSha256=sha(receipt)));return sha(p)
def assess(case,result,qualified,raw=None):
 code,out,err=result;check(code==(0 if qualified else 2),case['name']+' return '+err.decode('utf-8',errors='replace'));c=facts(out);check(c['captureQualified']==qualified,case['name']+' qualification');check(c['allOriginalResourcesReturnedAtConsole'] is True,case['name']+' returned')
 if raw is not None:check(c['rawBytesKnown']==raw,case['name']+' exact actual raw')
 records=[case['out']/(c['id']+'-entered.json'),case['out']/(c['id']+'-receipt.json')]
 if (case['out']/'capture-halted.json').exists():records.append(case['out']/'capture-halted.json')
 check(sum(p.stat().st_size for p in records)==c['recordWriteBytesKnown'],case['name']+' actual metadata bytes')
 check(all(r['closed'] for r in c.get('metadata',[])),case['name']+' original metadata file closes')
 for r in c['readers']:
  check(r['savedBytes']==(case['out']/(c['id']+'-'+r['role']+'.bin')).stat().st_size,case['name']+' saved distinct from read');check(r['pipeCloseReturned'] and r['fileCloseReturned'],case['name']+' original closes')
 results.append(dict(case=case['name'],status='PASS_LOCAL_FIXTURE',console=c));print(case['name'],'PASS',flush=True);write(E/'progress.json',results);return c

try:
 # Production preparation mode must stop before a tool hash or SDK start.
 prod=next((B/'release/requests').glob('*.json'));prodcase=dict(name='production-preparation',entry=ENTRY,requests=[prod],out=E);prodresult=run(prodcase,label='production-preparation');check(prodresult[0]!=0 and b'PREPARATION_ONLY_NO_EXECUTION_AUTHORIZATION' in prodresult[2],'production preparation refuses execution');check(not Path(json.loads(prod.read_text())['evidenceRoot']).exists(),'no execution root created')

 case=setup('success-two-requests',('success','success'));c=assess(case,run(case),True,17);pid=c['controllerPid'];check(pid==commands[-1]['pid'],'same actual controller pid')
 # No external proof => cannot start next exact slot.
 bad=run(case,1,label='success-no-proof');check(bad[0]!=0,'missing external predecessor proof blocked');check(not (case['out']/'LOCAL_1-entered.json').exists(),'missing proof no new intent')
 goodProof=proof(case,0,c);assess(case,run(case,1,goodProof),True,17)
 replay=run(case,0,label='success-repeat');check(replay[0]!=0 and b'REQUEST_ALREADY_ENTERED_NO_REPLAY' in replay[2],'same request replay rejected')

 case=setup('stderr',('stderr',));c=assess(case,run(case),False,17);check(c['firstFailure'] is not None,'stderr halts');check((case['out']/'LOCAL_0-stderr.bin').read_bytes()==b'LOCAL_STDERR\n','stderr preserved')
 case=setup('chunk-overrun',('chunks',),cap=96);c=assess(case,run(case),False,192);check(sum(r['savedBytes'] for r in c['readers'])<=96,'save bound');check(c['rawBytesKnown']>96,'overrun not clipped accounting')
 case=setup('qualification-timeout',('timeout',),qual=.6);c=assess(case,run(case),False,19);check(c['firstFailure']=='QUALIFICATION_TIMEOUT_NO_TERMINATION','timeout stays failed after late return')
 case=setup('writer-fault',fault='WRITE_FAULT_ONCE');c=assess(case,run(case),False,17);check(c['firstFailure']=='RAW_FILE_WRITE_FAILED','actual faulted writer task handling');check(sum(r['savedBytes'] for r in c['readers'])==0,'no invented saved bytes')
 case=setup('reader-fault-unknown',fault='READ_FAULT_ONCE');c=assess(case,run(case),False);check(c['rawAmountUnknown'] is True,'unknown amount retained');check(c['firstFailure']=='ORIGINAL_READ_FAULT_UNKNOWN_AMOUNT','faulted original read task branch')
 case=setup('child-exception',('exit',));assess(case,run(case),False,25)

 for name,mode,fault,gate in [('late-return','late','NONE','child-return.gate'),('file-return-unproven','success','CLOSE_GATE','file-close.gate')]:
  case=setup(name,(mode,),qual=.6,fault=fault);pending=start(case);deadline=time.monotonic()+8
  snapshot=None
  while snapshot is None and time.monotonic()<deadline:
   try:snapshot=json.loads((case['out']/'capture-halted.json').read_text())
   except (FileNotFoundError,json.JSONDecodeError,UnicodeDecodeError):time.sleep(.02)
  if snapshot is None:finish(pending);raise AssertionError(name+' no complete pending snapshot')
  check(snapshot['started'] is True,'original child started before pending');check(owned[pending][0].poll() is None,'same foreground original controller retained')
  if mode=='late':check(snapshot['rawKnownIsPrefix'] and snapshot['rawAmountUnknown'],'pending reads cannot become final exact amount')
  if name=='file-return-unproven':check(snapshot['waitReturned'] and any(not r['fileCloseReturned'] for r in snapshot['readers']),'process exit is not file return proof')
  rejected=run(case,0,label=name+'-reentry');check(rejected[0]!=0,'pending batch no reentry')
  (case['out']/gate).write_text('release same controlled original fixture\n');c=assess(case,finish(pending),False,21 if mode=='late' else 17)
  check(c['owner']==snapshot['owner'] and c['processToken']==snapshot['processToken'],'same original owner/process across late return');check([(r['readerToken'],r['streamToken']) for r in c['readers']]==[(r['readerToken'],r['streamToken']) for r in snapshot['readers']],'same pipe/reader identity')
  check((case['out']/'capture-halted.json').exists(),'late return does not remove halt')

 case=setup('invalid-input',('success',));original=json.loads(case['requests'][0].read_text())
 for label,changes in [('legacy-root',dict(evidenceRoot='D:\\CodexProjects\\VideoKit\\docs\\tester\\D1_TABLET_CLOSEOUT_CONT_EVIDENCE')),('bad-argv',dict(argv=['D:/Android/SDK/platform-tools/adb.exe','version'])),('bad-cap',dict(maxTextBytes=1048576)),('string-cap',dict(maxTextBytes='512')),('boolean-time',dict(qualificationSeconds=True)),('bad-policy',dict(policySha256='0'*64)),('bad-id',dict(id='NOT_AN_EXACT_SLOT'))]:
  d=dict(original);d.update(changes);path=case['root']/(label+'.json');write(path,d);r=run(case,request=path,label=label);check(r[0]!=0,label+' rejected');check(not (case['out']/'LOCAL_0-entered.json').exists(),label+' no original child intent')
 d=dict(original);d['maxBytes']=d.pop('maxTextBytes');path=case['root']/'legacy-schema.json';write(path,d);check(run(case,request=path,label='legacy-schema')[0]!=0,'legacy schema rejected')
 path=case['root']/'duplicate-key.json';path.write_text(case['requests'][0].read_text().replace('"schema":','"schema":"DUPLICATE","schema":',1));check(run(case,request=path,label='duplicate-key')[0]!=0,'duplicate JSON rejected')
 check(not owned,'all original test controllers naturally returned')
 write(E/'results.json',dict(status='PASS_CAPTURE_FINITE_LOCAL_FIXTURES',assertions=assertions,fixtureCases=len(results),results=results,subprocesses='Only fixed local Python fixture and PowerShell capture entry',sdkCalls=0,adb5037Connections=0,deviceCalls=0,productionSourcesChanged=0,androidBuilds=0,kills=0,ownerPending=False,overrunBytesClipped=False,oldReleaseModified=False));print('PASS_CAPTURE_FINITE_LOCAL_FIXTURES assertions='+str(assertions),flush=True)

except BaseException:
 for pendingName in list(owned):
  outputRoot=owned[pendingName][3]
  for gateName in ["child-return.gate","file-close.gate"]:(outputRoot/gateName).write_text("release exact controlled fixture after test observer failure\n")
  finish(pendingName)
 raise
