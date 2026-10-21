from pathlib import Path
import copy,datetime,hashlib,json,subprocess,threading,time
R=Path('D:/CodexProjects/VideoKit');B=R/'docs/coder/d1android02-capture-ready01';E=Path(__file__).resolve().parent;ROOT=E/'fixtures'/'independent-001';assert not ROOT.exists();ROOT.mkdir();PY='C:/Users/benny/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe';PS='C:/Users/benny/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/powershell/pwsh.exe';ENTRY=B/'tools/capture_android02.ps1';PRODUCER=B/'selfchecks/capture_fixture.py'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,x):
 with p.open('x',encoding='utf-8',newline='\n') as f:f.write(json.dumps(x,ensure_ascii=False,indent=2)+'\n');f.flush()
def replace(p,x):
 with p.open('w',encoding='utf-8',newline='\n') as f:f.write(json.dumps(x,ensure_ascii=False,indent=2)+'\n');f.flush()
PLAN=read(B/'reference/exact-seven-role-plan.json');start=time.monotonic();total=0;payload=0;calls=0;results=[];stopped=False;traces=[]
def case(name,modes,q=2,fault='NONE',cap=None):
 global payload
 home=ROOT/name;root=home/'outputs';root.mkdir(parents=True)
 for folder in ['tools','reference','release']:(home/folder).mkdir()
 for rel in ['tools/capture_android02.ps1','reference/exact-seven-role-plan.json','reference/legacy-tool-route-contract.json']:(home/rel).write_bytes((B/rel).read_bytes())
 slots=[]
 for n,mode in enumerate(modes):
  r=PLAN['steps'][n];s={'id':r['id'],'argv':[PY,'-I','-X','utf8','-B',PRODUCER.as_posix(),mode,str(root/'fixture-gate')],'maxTextBytes':cap or min(r['maxTextBytes'],8192),'maxBinaryBytes':0,'qualificationSeconds':q}
  if mode.startswith('payload_'):
   size=4096 if mode=='payload_app' else 2048;p=root/(r['id']+'-fixture-input.bin');p.write_bytes(bytes(range(256))*(size//256));payload+=size;s['payloadPin']={'path':str(p),'bytes':size,'sha256':sha(p)}
  slots.append(s)
 policy={'schema':'ANDROID02_CAPTURE_POLICY_V1','mode':'OFFLINE_FIXTURE','entrySha256':sha(ENTRY),'planSha256':sha(B/'reference/exact-seven-role-plan.json'),'productSealSha256':PLAN['product']['sealSha256'],'scope':hashlib.sha256(('INDEPENDENT-'+name).encode()).hexdigest(),'evidenceRoot':str(root),'toolSha256':sha(PY),'fixtureScriptSha256':sha(PRODUCER),'fixtureFault':fault,'fixtureGatePath':str(root/'fixture-gate'),'slots':slots};save(home/'release/capture-policy.json',policy)
 return home,root,policy
def request(c,n):
 h,r,p=c;s=p['slots'][n];q={'schema':'ANDROID02_CAPTURE_REQUEST_V1','id':s['id'],'policySha256':sha(h/'release/capture-policy.json'),'scope':p['scope'],'evidenceRoot':str(r),'argv':s['argv'],'maxTextBytes':s['maxTextBytes'],'maxBinaryBytes':0,'qualificationSeconds':s['qualificationSeconds']};f=h/('request-'+s['id']+'.json');replace(f,q);return f
def invoke(c,n=0,proof='ABSENT',gate=False,custom=None):
 global calls,total,stopped
 if stopped or time.monotonic()-start>=27:raise RuntimeError('SUITE_STOP_NEW_ADMISSION_27_SECONDS')
 h,r,p=c;rp=request(c,n);role=p['slots'][n]['id'];argv=custom or [PS,'-NoProfile','-NonInteractive','-File',str(h/'tools/capture_android02.ps1'),'-RequestPath',str(rp),'-PredecessorProofSha',proof];calls+=1;beg=time.monotonic();ownerpath=h/('owner-'+str(calls)+'.json');owner={'argv':argv,'originalReturned':False,'killInterruptRetry':0,'sdkCalls':0};save(ownerpath,owner)
 proc=subprocess.Popen(argv,stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=False);owner['pid']=proc.pid;replace(ownerpath,owner);buf=[bytearray(),bytearray()];errors=[]
 def drain(pipe,target):
  try:
   while True:
    data=pipe.read(4096)
    if not data:break
    target.extend(data)
    if len(target)>131072:errors.append('OUTER_BYTES_OVER_BOUND')
  except BaseException as e:errors.append(type(e).__name__)
 threads=[threading.Thread(target=drain,args=(p,b)) for p,b in zip([proc.stdout,proc.stderr],buf)]
 for t in threads:t.start()
 observed=False
 try:
  if gate:
   end=time.monotonic()+1.8
   while time.monotonic()<end:
    if (r/'capture-halted.json').exists():observed=proc.poll() is None;break
    time.sleep(.005)
   (r/'fixture-gate').write_bytes(b'RELEASE_OWN_CONTROLLED_GATE_ONLY')
  try:code=proc.wait(max(.01,30-(time.monotonic()-start)))
  except subprocess.TimeoutExpired:
   stopped=True;owner['observation']='UNKNOWN_NO_NEXT_TASK_OR_KILL';replace(ownerpath,owner);code=proc.wait()
 finally:
  if gate and not (r/'fixture-gate').exists():(r/'fixture-gate').write_bytes(b'FINALLY_RELEASE_OWN_GATE')
 for t in threads:t.join()
 proc.stdout.close();proc.stderr.close();proc._handle.Close();out,err=map(bytes,buf);total+=len(out)+len(err);owner.update(originalReturned=True,exitCode=code,readersJoined=all(not t.is_alive() for t in threads),streamsClosed=proc.stdout.closed and proc.stderr.closed,originalHandleClosed=True,elapsedSeconds=time.monotonic()-beg,stdoutBytes=len(out),stderrBytes=len(err),errors=errors);replace(ownerpath,owner)
 base=role if not (r/(role+'-outer-return.json')).exists() else role+'-negative-'+str(calls)
 (r/(base+'-console.bin')).write_bytes(out);(r/(base+'-controller-stderr.bin')).write_bytes(err)
 native={'argv':argv,'controllerPid':proc.pid,'exitCode':code,'originalControllerWaitReturned':True,'sameOriginalPipeReadersJoined':owner['readersJoined'],'outerStreamsClosed':owner['streamsClosed'],'originalWindowsProcessHandleCloseReturned':True,'streamBytes':len(out)+len(err),'amountUnknown':bool(errors),'stdoutSha256':hashlib.sha256(out).hexdigest(),'stderrSha256':hashlib.sha256(err).hexdigest(),'sourceEntrySha256':sha(h/'tools/capture_android02.ps1'),'requestSha256':sha(rp),'scope':p['scope'],'id':role,'elapsedSeconds':owner['elapsedSeconds'],'producerKind':'OFFLINE_PYTHON_NOT_SDK','gatePendingOriginalControllerObserved':observed};save(r/(base+'-outer-return.json'),native)
 try:co=json.loads(out)
 except (ValueError,UnicodeError):co=None
 traces.append({'case':h.name,'role':role,'pid':proc.pid,'exitCode':code,'elapsed':owner['elapsedSeconds'],'outerTextBytes':len(out)+len(err),'gatePendingObserved':observed,'semantic':co.get('semantic') if co else None,'firstFailure':co.get('firstFailure') if co else None});assert not errors and total<=4194304 and payload<=65536
 return code,co,err,native
def proof(c,co):
 h,r,p=c;idx=next(i for i,s in enumerate(p['slots']) if s['id']==co['id']);assert co['captureQualified']
 d={'schema':'ANDROID02_CAPTURE_COMPLETION_PROOF_V1','id':co['id'],'nextId':p['slots'][idx+1]['id'],'scope':p['scope'],'controllerPid':co['controllerPid'],'controllerExited':True,'toolStreamsReturned':True,'originalResourcesReturnedAtConsole':True,'captureQualifiedAtConsole':True,'approvedForNext':True,'captureReceiptSha256':co['captureReceiptSha256'],'semanticDependency':co['id']+'_ACTUAL_RETURN_AND_SEMANTIC_PASS','dependencyAccepted':True,'batchSdkChildrenEntered':co['batchSdkChildrenEntered'],'batchTextChargedBytesKnown':co['batchTextChargedBytesKnown'],'batchBinaryArchiveBytesKnown':0,'batchAmountUnknown':False,'batchGroups':co['batchGroups'],'outerReturnSha256':sha(r/(co['id']+'-outer-return.json')),'scopeStartTick':co['scopeStartTick']};f=r/(co['id']+'-completion-proof.json');replace(f,d)
 save(h/('proof-writer-'+co['id']+'.json'),{'proof':str(f),'writerFlushAndCloseReturnedBeforeHash':True,'proofWriteBytes':f.stat().st_size,'outerReturnRecordWriteBytes':(r/(co['id']+'-outer-return.json')).stat().st_size,'captureConsoleCounter':co['batchTextChargedBytesKnown'],'actualExternalWritesNotInConsole':True})
 return sha(f)
def check(name,fn):
 try:detail=fn();results.append({'name':name,'pass':True,'detail':detail})
 except BaseException as e:results.append({'name':name,'pass':False,'detail':repr(e)});raise
positive=None
def seven():
 global positive
 positive=case('whole-seven',('identity','global_idle','app_absence','test_absence','payload_app','payload_test','instrument'));prev='ABSENT';groups=[]
 for n in range(7):
  code,co,err,_=invoke(positive,n,prev);assert code==0 and co['captureQualified'] and not err and co['batchSdkChildrenEntered']==n+1,(code,co,err)
  assert co['rawBytesKnown']==co['rawTextSavedBytesKnown'] and co['allOriginalResourcesReturnedAtConsole'];groups.append(co['batchGroups'])
  if n<6:prev=proof(positive,co)
 assert co['semantic']=='PASS_LIMITED_APP_RECEIPT_INTERNAL_FINISH_UNPROVEN' and co['batchGroups']['payload']==6144
 raw=(positive[1]/'scope_all-stdout.bin').read_bytes();assert b'INSTRUMENTATION_STATUS:' in raw and b'INSTRUMENTATION_RESULT:' in raw
 return {'groups':groups,'installFixtureStdinBytes':6144,'fullPendingFinalPreserved':True,'accountingQualification':'Tests internal console-equal chain only, not complete actual outer/proof budget closure'}
def busy():
 c=case('whole-busy',('identity','global_busy','app_absence'));code,co,_,_=invoke(c);assert code==0;prev=proof(c,co);code,co,_,_=invoke(c,1,prev);assert code==2 and co['semantic']=='ENV_WAIT_OTHER_PROJECT_OR_TEST_OCCUPIED' and not co['captureQualified'] and (c[1]/'capture-halted.json').exists();return {'freshLocalRawThroughActualCapture':True,'nextRoleNotEntered':not (c[1]/'app_absence-entered.json').exists(),'scope':c[2]['scope']}
def guards():
 cases=[]
 for name,expected in [('prepare','PREPARATION_ONLY_NO_EXECUTION_AUTHORIZATION'),('entry','ENTRY_POLICY_PIN'),('sdk','EXACT_LOCAL_PRODUCER_ONLY'),('duplicate','DUPLICATE_JSON_FIELD'),('eighth','EXACT_SEVEN_ROLES_MAX')]:
  c=case('guard-'+name,('identity',));h,r,p=c
  if name=='prepare':p['mode']='PREPARATION_ONLY'
  if name=='entry':p['entrySha256']='0'*64
  if name=='sdk':p['slots'][0]['argv'][0]=PLAN['sdkFiles'][0]['path']
  if name=='eighth':p['slots']*=8
  replace(h/'release/capture-policy.json',p);rp=request(c,0)
  if name=='duplicate':rp.write_text(rp.read_text().replace('{','{"schema":"duplicate",',1),encoding='utf-8')
  if name=='prepare':rp=h/'missing.json'
  cases.append({'name':name,'entry':str(h/'tools/capture_android02.ps1'),'request':str(rp),'proof':'ABSENT','expected':expected,'root':str(r)})
 h,r,p=positive;fp=r/'identity-completion-proof.json';original=fp.read_bytes();d=read(fp);extra=(r/'identity-outer-return.json').stat().st_size+len(original);d['batchGroups']['control']+=extra;d['batchTextChargedBytesKnown']+=extra;replace(fp,d);rp=request(positive,1)
 cases.append({'name':'actual-outer-proof-cost','entry':str(h/'tools/capture_android02.ps1'),'request':str(rp),'proof':sha(fp),'expected':'OUTER_CONSOLE_ORIGINAL_BINDING','root':str(r),'externalAddedBytes':extra})
 c=case('guard-owner',('identity',));gp=c[0]/'guards.json';save(gp,cases);script=c[0]/'guards.ps1';script.write_text('''param([string]$InputFile)
$ErrorActionPreference='Stop';$answer=@();foreach($g in (Get-Content -LiteralPath $InputFile -Raw|ConvertFrom-Json)){$errorText='';try{& $g.entry -RequestPath $g.request -PredecessorProofSha $g.proof;throw 'UNEXPECTED_ACCEPT'}catch{$errorText=$_.Exception.Message};if(-not $errorText.Contains($g.expected)){throw ('WRONG_GUARD '+$g.name+' '+$errorText)};$answer+=@{name=$g.name;observed=$errorText;expected=$g.expected}};@{guards=$answer;started=$false}|ConvertTo-Json -Depth 5 -Compress
''',encoding='utf-8')
 try:
  code,co,err,_=invoke(c,custom=[PS,'-NoProfile','-NonInteractive','-File',str(script),'-InputFile',str(gp)]);assert code==0 and not err and len(co['guards'])==6,(code,co,err);return {'guards':co['guards'],'completeActualOuterProofBytesRejected':extra}
 finally:fp.write_bytes(original)
def semantic():
 c=case('semantic-owner',('identity',));h,r,p=c;raw=r/'production-like-receipt.txt';history=[{'case':s,'caseOriginalResourcesReturned':True} for s in PLAN['product']['caseOrder']];history[-1].update(muxerKeeper={'returned':True,'eosReturned':True,'sampleWritesReturned':6},muxReopenCalls=1,muxReadyCalls=0,muxNativeSyncReturned=True,reopened={'actualExtractorClass':'androidx.media3.extractor.mp4.FragmentedMp4Extractor'})
 receipt={'scopeEntry':'scopeAll','candidate':PLAN['product']['version'],'status':'OBSERVED_ALL_SCOPE_HOST_STRUCTURE_ONLY','completedCaseCount':10,'expectedCaseCount':10,'sourceKeepers':0,'outputKeepers':0,'originalResourcesReturned':True,'workerActuallyJoined':True,'timelyOriginalBody':True,'lastControlledReturnSignalBeforeMarker':True,'snapshotOverflow':False,'runId':'D1MA02-INDEPENDENT','caseReceipts':history,'identity':{'targetPackage':'com.videokit.d1media3.android02','testPackage':'com.videokit.d1media3.android02.test','processName':'com.videokit.d1media3.android02:media3'},'meter':{'scopeInputReserved':-1,'scopeOutputRequested':-1,'scopeOutputAttempted':-1,'knownNativeFdActive':0,'assetStreamActive':0,'unknownAllocationOrClose':0},'firstFailure':'INJECTED_POLICY_COUNTEREXAMPLE_NOT_ANDROID'}
 for pkg in ['com.videokit.d1media3.android02','com.videokit.d1media3.android02.test']:receipt['identity'][pkg]={'versionName':PLAN['product']['version'],'signerSha256':PLAN['product']['signerCertificateSha256']}
 raw.write_text('INSTRUMENTATION_RESULT: receipt='+json.dumps(receipt,separators=(',',':'))+'\nINSTRUMENTATION_CODE: -1\n',encoding='utf-8');unknown=r/'unknown-global.txt';unknown.write_text('UNPROVEN_GLOBAL_FORMAT\n',encoding='utf-8');present=r/'package-present.txt';present.write_text('ANDROID02_APP_BEGIN\npackage:com.videokit.d1media3.android02\nANDROID02_APP_COMPLETE\n',encoding='utf-8')
 args=h/'semantic-inputs.json';save(args,{'plan':str(B/'reference/exact-seven-role-plan.json'),'source':str(B/'tools/semantic-gates.ps1.txt'),'receipt':str(raw),'unknown':str(unknown),'present':str(present)})
 script=h/'semantic.ps1';script.write_text('''param([string]$InputFile)
$ErrorActionPreference='Stop';$a=Get-Content -LiteralPath $InputFile -Raw|ConvertFrom-Json;$plan=Get-Content -LiteralPath $a.plan -Raw|ConvertFrom-Json;$policy=@{runId='D1MA02-INDEPENDENT'};. ([scriptblock]::Create([IO.File]::ReadAllText($a.source)));@{negativeAccountingAndFirstFailure=(RoleSemantic 'scope_all' $a.receipt $false);globalUnknown=(RoleSemantic 'global_idle' $a.unknown $true);packagePresent=(RoleSemantic 'app_absence' $a.present $true);started=$false;classification='PURE_LOCAL_FUNCTION_POLICY_NOT_ANDROID'}|ConvertTo-Json -Compress
''',encoding='utf-8')
 code,co,err,_=invoke(c,custom=[PS,'-NoProfile','-NonInteractive','-File',str(script),'-InputFile',str(args)]);assert code==0 and not err and co['globalUnknown']=='GLOBAL_FORMAT_UNPROVEN' and co['packagePresent']=='EXISTING_PACKAGE_OR_ABSENCE_UNPROVEN';assert co['negativeAccountingAndFirstFailure']=='PASS_LIMITED_APP_RECEIPT_INTERNAL_FINISH_UNPROVEN';return co
def failure(name,mode,expected,gate=False,fault='NONE',cap=None):
 c=case(name,(mode,),q=.3 if gate else 2,fault=fault,cap=cap);code,co,err,_=invoke(c,gate=gate);assert code==2 and co and not co['captureQualified'] and co['firstFailure']==expected and co['allOriginalResourcesReturnedAtConsole'],(code,co,err)
 if gate:assert traces[-1]['gatePendingObserved']
 return {'firstFailure':co['firstFailure'],'rawRead':co['rawBytesKnown'],'rawSaved':co['rawTextSavedBytesKnown'],'rawComplete':co['rawBytesKnown']==co['rawTextSavedBytesKnown'],'originalReturned':True,'gatePendingObserved':traces[-1]['gatePendingObserved']}
try:
 check('whole-seven-role-local-chain',seven);check('whole-busy-capture-stops',busy);check('six-precontext-and-full-outer-accounting-negative',guards);check('semantic-negative-count-and-first-failure-counterexample',semantic);check('overrun-honest-not-full-preservation',lambda:failure('overrun','overrun','TEXT_QUALIFIER_EXCEEDED',cap=80));check('late-original-held-no-upgrade',lambda:failure('late','late','QUALIFICATION_TIMEOUT_NO_TERMINATION',gate=True));check('raw-file-close-gate-original-held',lambda:failure('file-close','identity','QUALIFICATION_TIMEOUT_NO_TERMINATION',gate=True,fault='CLOSE_GATE'))
finally:
 elapsed=time.monotonic()-start;summary={'status':'COMPLETE_INDEPENDENT_LOCAL_SUITE' if len(results)==7 and all(x['pass'] for x in results) and elapsed<=30 else 'INCOMPLETE_OR_FAILED_INDEPENDENT_SUITE','elapsedSeconds':elapsed,'within30Seconds':elapsed<=30,'outerControllers':calls,'totalOuterTextBytes':total,'injectedFixturePayloadBytes':payload,'serial':True,'sdkDeviceJvmGradleMediaCalls':0,'killInterruptRetry':0,'results':results,'originalControllerTraces':traces,'doesNotMeanCandidatePass':True};save(E/'independent-suite-results-final.json',summary);print(json.dumps(summary,ensure_ascii=False))
