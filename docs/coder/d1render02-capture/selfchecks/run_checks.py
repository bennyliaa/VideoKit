from pathlib import Path
import sys,json,hashlib,shutil,subprocess,threading,time,uuid
B=Path(__file__).resolve().parents[1];assert not (B/'evidence/capture-adapt-freeze.json').exists()
ATTEMPT=sys.argv[1];E=B/'evidence'/('selfcheck-'+ATTEMPT);E.mkdir(exist_ok=False)
W=B/'selfchecks/work'/ATTEMPT;W.mkdir(parents=True,exist_ok=False)
PS=Path('C:/Users/benny/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/powershell/pwsh.exe')
PY=Path(sys.executable).as_posix();FIX=B/'selfchecks/capture_fixture.py';ENTRY=B/'tools/capture_render02.ps1'
owners=[];results=[]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
def setup(name,mode='success',fault='NONE',cap=65536,binary=0,q=10,input=False):
 d=W/name;root=d/'outputs';root.mkdir(parents=True);(d/'tools').mkdir();(d/'release').mkdir();shutil.copyfile(ENTRY,d/'tools/capture_render02.ps1')
 argv=[PY,'-X','utf8','-B',FIX.as_posix(),mode,str(root/'fixture-gate')]
 slot={'id':'fixture_a','argv':argv,'maxTextBytes':cap,'maxBinaryBytes':binary,'qualificationSeconds':q}
 policy={'schema':'RENDER02_CAPTURE_POLICY_V1','mode':'OFFLINE_FIXTURE','entrySha256':sha(ENTRY),'scope':'f'*64,'evidenceRoot':str(root),'slots':[slot],'fixtureFault':fault,'fixtureGatePath':str(root/'fixture-gate'),'fixtureScriptSha256':sha(FIX),'toolSha256':sha(Path(PY))}
 if input:
  data=(bytes(range(256))*1364)[:349102];assert len(data)==349102;(root/'fixture-input.bin').write_bytes(data);policy['inputPin']={'path':str(root/'fixture-input.bin'),'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}
 dump(d/'release/capture-policy.json',policy)
 req={'schema':'RENDER02_CAPTURE_REQUEST_V1','id':'fixture_a','policySha256':sha(d/'release/capture-policy.json'),'scope':policy['scope'],'evidenceRoot':str(root),'argv':argv,'maxTextBytes':cap,'maxBinaryBytes':binary,'qualificationSeconds':q};dump(d/'request.json',req)
 return d,root
def launch(d,request=None,proof=None):
 argv=[str(PS),'-NoProfile','-NonInteractive','-File',str(d/'tools/capture_render02.ps1'),'-RequestPath',str(request or d/'request.json')]
 if proof:argv+=['-PredecessorProofSha',proof]
 p=subprocess.Popen(argv,stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
 c={'process':p,'root':d/'outputs','argv':argv,'buffers':{},'counts':{},'unknown':False,'threads':[],'start':time.time()};owners.append(c)
 def read(role,stream):
  total=0;parts=[]
  try:
   while True:
    b=stream.read(4096)
    if not b:break
    total+=len(b)
    if total<=65536:parts.append(b)
    else:c['unknown']=True
  except BaseException:c['unknown']=True;raise
  finally:stream.close();c['buffers'][role]=b''.join(parts);c['counts'][role]=total
 for role,stream in [('stdout',p.stdout),('stderr',p.stderr)]:
  t=threading.Thread(target=read,args=(role,stream));t.start();c['threads'].append(t)
 return c
def finish(c,name):
 p=c['process'];deadline=time.monotonic()+15
 while p.poll() is None and time.monotonic()<deadline:time.sleep(.02)
 if p.poll() is None:
  # Release ONLY controlled fixture gates. Keep same controller and original pipes; never kill.
  (c['root']/'fixture-gate').write_text('BOUNDED_FIXTURE_RELEASE',encoding='utf-8')
  while p.poll() is None:time.sleep(.05)
 p.wait()
 for t in c['threads']:t.join()
 if hasattr(p,'_handle'):p._handle.Close()
 c['processHandleClosed']=True
 d=E/name;d.mkdir();
 for role,b in c['buffers'].items():(d/(role+'.bin')).write_bytes(b)
 receipt={'argv':c['argv'],'controllerPid':p.pid,'exitCode':p.returncode,'originalControllerWaitReturned':True,'sameOriginalPipeReadersJoined':True,'outerStreamsClosed':True,'originalWindowsProcessHandleCloseReturned':True,'streamBytes':c['counts'],'amountUnknown':c['unknown'],'startEpoch':c['start'],'endEpoch':time.time()};dump(d/'outer-return.json',receipt)
 if c['buffers']['stdout']:
  try:receipt['console']=json.loads(c['buffers']['stdout'].decode('utf-8-sig'))
  except Exception:pass
 return receipt
def check(name,**kwargs):
 d,root=setup(name,**kwargs);c=launch(d);r=finish(c,name);return d,root,r
def need(v,message):
 if not v:raise AssertionError(message)
def record(name,r):results.append({'case':name,'status':'PASS','outerExit':r['exitCode'],'firstFailure':r.get('console',{}).get('firstFailure')})
try:
 dump(E/'tested-source-pins.json',[{'path':p.relative_to(B).as_posix(),'sha256':sha(p)} for p in [ENTRY,FIX,Path(__file__)]])
 for name,kw in [('normal',{}),('binary',{'mode':'binary','binary':4194304}),('stdin_exact',{'mode':'stdin','input':True})]:
  d,root,r=check(name,**kw);need(r['exitCode']==0 and r['console']['captureQualified'],str(r));need(r['console']['allOriginalResourcesReturnedAtConsole'],'originals')
  if name=='binary':need((root/'fixture_a-stdout.bin').read_bytes()==b'\x89PNG\r\n\x1a\n'+bytes(range(256))*32+b'\xff','byte-exact binary');need(r['console']['textBytesKnown']==0 and r['console']['binaryBytesKnown']==8201,'binary separated')
  if name=='stdin_exact':
   f=r['console']['input'];need(f['stdinWriteReturnedBytes']==349102 and f['transportSourceReadBytes']==349102 and f['pinReadBytes']==349102 and f['sourceCloseReturned'] and f['stdinCloseReturned'],'same stdin/source tasks returned');child=json.loads((root/'fixture_a-stdout.bin').read_bytes());need(child['sha256']==f['expectedSha256'],'exact stdin source hash')
  record(name,r)
 for name,kw,expected in [('binary_stderr',{'mode':'binary_stderr','binary':4194304},'STDERR_REQUIRES_STOP'),('text_overrun',{'mode':'overrun','cap':80},'TEXT_QUALIFIER_EXCEEDED'),('binary_overrun',{'mode':'binary','binary':80},'BINARY_QUALIFIER_EXCEEDED'),('write_fault',{'fault':'WRITE_FAULT_ONCE'},'RAW_FILE_WRITE_FAILED'),('read_fault',{'fault':'READ_FAULT_ONCE'},'ORIGINAL_READ_FAULT_UNKNOWN_AMOUNT'),('stdin_write_fault',{'mode':'stdin','input':True,'fault':'STDIN_WRITE_FAULT_ONCE'},'ORIGINAL_STDIN_WRITE_FAULT_UNKNOWN_AMOUNT')]:
  d,root,r=check(name,**kw);need(r['exitCode']==2 and r['console']['firstFailure']==expected,str(r));need((root/'capture-halted.json').is_file(),'persistent halt')
  if name in ['read_fault','write_fault','stdin_write_fault']:need(r['console']['batchAmountUnknown'],'retain exact unknown class')
  record(name,r)
 for name,kw in [('late_original',{'mode':'late','q':.25}),('stdin_close_gate',{'mode':'stdin','input':True,'fault':'STDIN_CLOSE_GATE','q':.25}),('file_close_gate',{'fault':'CLOSE_GATE','q':.25})]:
  d,root=setup(name,**kw);c=launch(d);end=time.monotonic()+5
  while not (root/'capture-halted.json').exists() and time.monotonic()<end and c['process'].poll() is None:time.sleep(.01)
  need(c['process'].poll() is None and (root/'capture-halted.json').exists(),'same original controller must remain alive past qualifier')
  # A second invocation must not advance while the first owns the original lock/halt.
  second=launch(d);rejected=finish(second,name+'-successor-rejected');need(rejected['exitCode']!=0 and not (root/'fixture_b-entered.json').exists(),'successor refused')
  (root/'fixture-gate').write_text('CONTROLLED_RELEASE',encoding='utf-8');r=finish(c,name);need(r['exitCode']==2 and r['console']['firstFailure']=='QUALIFICATION_TIMEOUT_NO_TERMINATION',str(r));record(name,r)
 # PREPARATION_ONLY rejects before it even reads the missing request, creates no capture context.
 d,root=setup('preparation_reject');shutil.copyfile(B/'release/capture-policy.json',d/'release/capture-policy.json');r=finish(launch(d,root/'no-request.json'),'preparation_reject');need(r['exitCode']!=0 and b'PREPARATION_ONLY_NO_EXECUTION_AUTHORIZATION' in r['buffers']['stderr'] if 'buffers' in r else r['exitCode']!=0,'prep rejected');need(not (root/'.capture.lock').exists(),'no context/child in preparation');record('preparation_reject',r)
 # New exact production activation fields must be complete BEFORE looking at the SDK binary.
 d,root=setup('production_no_authorization');(d/'reference').mkdir();shutil.copyfile(B/'reference/exact-operation-and-accounting-plan.json',d/'reference/exact-operation-and-accounting-plan.json');pol=json.loads((B/'release/capture-policy.json').read_text());pol.update(mode='PRODUCTION',scope='e'*64,planId=str(uuid.uuid4()));pol['evidenceRoot']='D:\\CodexProjects\\VideoKit\\docs\\tester\\D1_RENDER02_CAPTURE_EXECUTION\\'+pol['planId']+'\\outputs';dump(d/'release/capture-policy.json',pol)
 plan=json.loads((B/'reference/exact-operation-and-accounting-plan.json').read_text());s=plan['steps'][0];req=json.loads((d/'request.json').read_text());req.update(id=s['id'],scope=pol['scope'],evidenceRoot=pol['evidenceRoot'],argv=s['argv'],qualificationSeconds=15,policySha256=sha(d/'release/capture-policy.json'));dump(d/'request.json',req);r=finish(launch(d),'production_no_authorization');need(r['exitCode']!=0 and b'NEW_AUTHORIZATION_AND_REVIEW_REQUIRED' in (E/'production_no_authorization/stderr.bin').read_bytes(),'new auth rejected before SDK');need(not (root/'.capture.lock').exists(),'no production context');record('production_no_authorization',r)
 d,root=setup('fixture_sdk_refused');pol=json.loads((d/'release/capture-policy.json').read_text());pol['slots'][0]['argv'][0]='D:/Android/SDK/platform-tools/adb.exe';dump(d/'release/capture-policy.json',pol);req=json.loads((d/'request.json').read_text());req['argv']=pol['slots'][0]['argv'];req['policySha256']=sha(d/'release/capture-policy.json');dump(d/'request.json',req);r=finish(launch(d),'fixture_sdk_refused');need(r['exitCode']!=0 and b'EXACT_LOCAL_FIXTURE_ONLY' in (E/'fixture_sdk_refused/stderr.bin').read_bytes(),'fixture cannot execute SDK');record('fixture_sdk_refused',r)
 d,root=setup('source_pin_failure',mode='stdin',input=True);f=root/'fixture-input.bin';data=bytearray(f.read_bytes());data[0]^=1;f.write_bytes(data);r=finish(launch(d),'source_pin_failure');need(r['exitCode']==2 and not r['console']['started'] and r['console']['firstFailure']=='SOURCE_HASH_MISMATCH' and r['console']['input']['sourceCloseReturned'],'source pin failure before child, same file returned');record('source_pin_failure',r)
 # Same reviewed predecessor mechanism: receipt cannot prove its own close/outer return.
 d,root=setup('two_request_chain');pol=json.loads((d/'release/capture-policy.json').read_text());second=dict(pol['slots'][0]);second['id']='fixture_b';pol['slots'].append(second);dump(d/'release/capture-policy.json',pol);req=json.loads((d/'request.json').read_text());req['policySha256']=sha(d/'release/capture-policy.json');dump(d/'request.json',req);r=finish(launch(d),'two_request_chain-first');need(r['exitCode']==0,'first returned');co=r['console']
 proof={'schema':'RENDER02_CAPTURE_COMPLETION_PROOF_V1','id':'fixture_a','nextId':'fixture_b','scope':pol['scope'],'controllerPid':co['controllerPid'],'controllerExited':True,'toolStreamsReturned':True,'originalResourcesReturnedAtConsole':co['allOriginalResourcesReturnedAtConsole'],'captureQualifiedAtConsole':co['captureQualified'],'approvedForNext':True,'captureReceiptSha256':co['captureReceiptSha256'],'semanticDependency':'OFFLINE_FIRST_RETURNED','dependencyAccepted':True,'batchSdkChildrenEntered':co['batchSdkChildrenEntered'],'batchTextChargedBytesKnown':co['batchTextChargedBytesKnown'],'batchBinaryArchiveBytesKnown':co['batchBinaryArchiveBytesKnown'],'batchAmountUnknown':co['batchAmountUnknown']};dump(root/'fixture_a-completion-proof.json',proof)
 req['id']='fixture_b';dump(d/'request-b.json',req);second_owner=launch(d,d/'request-b.json',sha(root/'fixture_a-completion-proof.json'));r2=finish(second_owner,'two_request_chain-second');need(r2['exitCode']==0 and r2['console']['batchSdkChildrenEntered']==2 and r2['console']['batchTextChargedBytesKnown']>co['batchTextChargedBytesKnown'],'same predecessor and cumulative accounting');record('two_request_chain',r2)
 dump(E/'summary.json',{'result':'PASS_OFFLINE_FIXTURES_ONLY','cases':results,'sdkChildren':0,'deviceOperations':0,'productChanges':0,'ownersNaturallyReturned':len(owners),'screenshotEffect':'NOT_RUN','noKillOrTimeoutTermination':True})
 print(json.dumps({'result':'PASS_OFFLINE_FIXTURES_ONLY','cases':len(results),'outerOwnersReturned':len(owners),'SDK':0},ensure_ascii=False))
finally:
 for c in owners:
  if c['process'].poll() is None:
   (c['root']/'fixture-gate').write_text('FINALLY_RELEASE_CONTROLLED_FIXTURE',encoding='utf-8')
   while c['process'].poll() is None:time.sleep(.05)
   c['process'].wait()
   for t in c['threads']:t.join()
  if not c.get('processHandleClosed'):
   if hasattr(c['process'],'_handle'):c['process']._handle.Close()
   c['processHandleClosed']=True
 dump(E/'original-owner-audit.json',[{'pid':c['process'].pid,'returned':c['process'].poll() is not None,'pipeReadersJoined':all(not t.is_alive() for t in c['threads']),'processHandleCloseReturned':c['processHandleClosed'],'unknown':c['unknown'],'capturedBytes':c['counts']} for c in owners])
