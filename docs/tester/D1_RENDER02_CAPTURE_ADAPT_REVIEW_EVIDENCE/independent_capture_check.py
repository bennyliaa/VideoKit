from pathlib import Path
import subprocess,threading,json,hashlib,time,shutil,sys
W=Path('D:/CodexProjects/VideoKit');B=W/'docs/coder/d1render02-capture';E=Path(__file__).resolve().parent
PS='C:/Users/benny/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/powershell/pwsh.exe'
PY='C:/Users/benny/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
FIX=B/'selfchecks/capture_fixture.py';ENTRY=B/'tools/capture_render02.ps1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,v):
 with p.open('x',encoding='utf-8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def setup(name,mode='success',fault='NONE',cap=65536,binary=0,q=10,with_input=False,chain=False):
 d=E/'fixtures'/name;r=d/'outputs';r.mkdir(parents=True);(d/'tools').mkdir();(d/'release').mkdir();shutil.copyfile(ENTRY,d/'tools/capture_render02.ps1')
 argv=[PY,'-X','utf8','-B',FIX.as_posix(),mode,str(r/'fixture-gate')]
 slot={'id':'fixture_a','argv':argv,'maxTextBytes':cap,'maxBinaryBytes':binary,'qualificationSeconds':q}
 p={'schema':'RENDER02_CAPTURE_POLICY_V1','mode':'OFFLINE_FIXTURE','entrySha256':sha(ENTRY),'scope':'a'*64,'evidenceRoot':str(r),'slots':[slot],'fixtureFault':fault,'fixtureGatePath':str(r/'fixture-gate'),'fixtureScriptSha256':sha(FIX),'toolSha256':sha(Path(PY))}
 if chain:p['slots'].append(dict(slot,id='fixture_b'))
 if with_input:
  data=(bytes(range(255,-1,-1))*1364)[:349102];(r/'fixture-input.bin').write_bytes(data);p['inputPin']={'path':str(r/'fixture-input.bin'),'bytes':349102,'sha256':hashlib.sha256(data).hexdigest()}
 dump(d/'release/capture-policy.json',p)
 req={'schema':'RENDER02_CAPTURE_REQUEST_V1','id':'fixture_a','policySha256':sha(d/'release/capture-policy.json'),'scope':p['scope'],'evidenceRoot':str(r),'argv':argv,'maxTextBytes':cap,'maxBinaryBytes':binary,'qualificationSeconds':q};dump(d/'request.json',req)
 return d,r
def launch(d,name,request=None,proof=None):
 argv=[PS,'-NoLogo','-NoProfile','-NonInteractive','-File',str(d/'tools/capture_render02.ps1'),'-RequestPath',str(request or d/'request.json')]
 if proof:argv+=['-PredecessorProofSha',proof]
 proc=subprocess.Popen(argv,stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
 counts={};parts={};errors=[];threads=[]
 def reader(role,stream):
  count=0;chunks=[]
  try:
   while True:
    b=stream.read(4096)
    if not b:break
    count+=len(b)
    if count<=65536:chunks.append(b)
  except BaseException as ex:errors.append(role+':'+type(ex).__name__)
  finally:
   stream.close();counts[role]=count;parts[role]=b''.join(chunks)
 for role,stream in [('stdout',proc.stdout),('stderr',proc.stderr)]:
  t=threading.Thread(target=reader,args=(role,stream));t.start();threads.append(t)
 # This observer keeps the SAME Popen and original readers until natural exit. No timeout/kill.
 proc.wait()
 for t in threads:t.join()
 proc._handle.Close()
 record={'controllerPid':proc.pid,'exitCode':proc.returncode,'originalWaitReturned':True,'originalReadersJoined':True,'originalPipeCloseReturned':True,'originalWindowsProcessHandleCloseReturned':True,'streamReadBytes':counts,'streamSavedBytes':{k:len(v) for k,v in parts.items()},'readErrors':errors,'argv':argv,'sdkCalls':0}
 for role,data in parts.items():(E/(name+'-'+role+'.bin')).write_bytes(data)
 dump(E/(name+'-outer-return.json'),record)
 assert not errors and all(counts[k]==len(parts[k]) for k in counts)
 return record,json.loads(parts['stdout'].decode('utf-8-sig')) if parts['stdout'] else None
def check_return(c):
 assert c['allOriginalResourcesReturnedAtConsole'] and c['processDisposed']
 assert all(x['pipeCloseReturned'] and x['fileCloseReturned'] and x['readTaskReturned'] for x in c['readers'])
 assert c['input']['sourceCloseReturned'] and c['input']['stdinCloseReturned']
 assert all(x['closed'] and x['writeReturned'] for x in c['metadata'])
def suite():
 results=[]
 for name,kw,expected in [('normal',{},None),('binary',{'mode':'binary','binary':4194304},None),('stdin',{'mode':'stdin','with_input':True},None),('overrun',{'mode':'overrun','cap':80},'TEXT_QUALIFIER_EXCEEDED'),('binary_stderr',{'mode':'binary_stderr','binary':4194304},'STDERR_REQUIRES_STOP'),('write_fault',{'fault':'WRITE_FAULT_ONCE'},'RAW_FILE_WRITE_FAILED'),('read_fault',{'fault':'READ_FAULT_ONCE'},'ORIGINAL_READ_FAULT_UNKNOWN_AMOUNT'),('stdin_write_fault',{'mode':'stdin','with_input':True,'fault':'STDIN_WRITE_FAULT_ONCE'},'ORIGINAL_STDIN_WRITE_FAULT_UNKNOWN_AMOUNT')]:
  d,r=setup(name,**kw);outer,c=launch(d,name);check_return(c);assert c['firstFailure']==expected and outer['exitCode']==(0 if expected is None else 2)
  if name=='stdin':
   f=c['input'];assert f['pinReadBytes']==f['transportSourceReadBytes']==f['stdinWriteReturnedBytes']==349102 and f['stdinWriteCalls']==86
   assert read(r/'fixture_a-stdout.bin')['sha256']==sha(r/'fixture-input.bin')
  if name=='binary':assert (r/'fixture_a-stdout.bin').read_bytes()==b'\x89PNG\r\n\x1a\n'+bytes(range(256))*32+b'\xff' and c['binaryBytesKnown']==8201 and c['textBytesKnown']==0
  if name=='overrun':assert c['textBytesKnown']==192
  if name in ['write_fault','read_fault','stdin_write_fault']:assert c['batchAmountUnknown']
  results.append({'name':name,'exitCode':outer['exitCode'],'firstFailure':c['firstFailure'],'rawText':c['textBytesKnown'],'rawBinary':c['binaryBytesKnown'],'batchUnknown':c['batchAmountUnknown']})
 d,r=setup('prep');shutil.copyfile(B/'release/capture-policy.json',d/'release/capture-policy.json');outer,c=launch(d,'prep',r/'missing-request.json');assert outer['exitCode']==1 and c is None and b'PREPARATION_ONLY_NO_EXECUTION_AUTHORIZATION' in (E/'prep-stderr.bin').read_bytes();assert not (r/'.capture.lock').exists()
 results.append({'name':'prep_before_request','exitCode':1,'noContext':True})
 d,r=setup('sdk_reject');p=read(d/'release/capture-policy.json');p['slots'][0]['argv'][0]='D:/Android/SDK/platform-tools/adb.exe';(d/'release/capture-policy.json').write_text(json.dumps(p),encoding='utf-8');req=read(d/'request.json');req['argv']=p['slots'][0]['argv'];req['policySha256']=sha(d/'release/capture-policy.json');(d/'request.json').write_text(json.dumps(req),encoding='utf-8');outer,c=launch(d,'sdk_reject');assert outer['exitCode']==1 and b'EXACT_LOCAL_FIXTURE_ONLY' in (E/'sdk_reject-stderr.bin').read_bytes() and not (r/'.capture.lock').exists()
 results.append({'name':'fixture_sdk_rejected_before_child','exitCode':1,'noContext':True})
 d,r=setup('chain',chain=True);outer,c=launch(d,'chain-first');check_return(c);assert outer['exitCode']==0
 dump(E/'chain-first-console.json',c)
 dump(E/'independent-suite-results.json',{'status':'PASS_REPRESENTATIVE_OFFLINE_ONLY','cases':results,'outerControllersReturned':11,'sdkCalls':0,'proofForSecondNotYetCreated':True,'firstToolMustReturnBeforeProof':True})
 print(json.dumps({'status':'PASS_REPRESENTATIVE_OFFLINE_ONLY','cases':results,'chainFirstReturned':True}))
if __name__=='__main__':
 if sys.argv[1]=='suite':suite()
 elif sys.argv[1]=='gate':
  d,r=setup('stdin-close-gate',mode='stdin',fault='STDIN_CLOSE_GATE',q=.5,with_input=True);dump(E/'gate-location.json',{'path':str(r/'fixture-gate'),'root':str(r)});outer,c=launch(d,'stdin-close-gate');check_return(c);assert outer['exitCode']==2 and c['firstFailure']=='QUALIFICATION_TIMEOUT_NO_TERMINATION' and c['input']['closeGateObserved'];print('PASS SAME_ORIGINAL_STDIN_GATE_LATE_RETURN_NOT_REQUALIFIED')
