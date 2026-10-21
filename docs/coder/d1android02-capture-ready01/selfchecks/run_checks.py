"""Finite, serial OFFLINE_FIXTURE checks. Never invokes SDK, device, or server tools.
The original native Popen and its original pipe readers are retained until return.
No terminate/kill/retry path exists. All paths stay under this candidate.
"""
from pathlib import Path
import copy, hashlib, json, subprocess, threading, time, uuid

B=Path(__file__).resolve().parents[1]
PY='C:/Users/benny/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
PS='C:/Users/benny/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/powershell/pwsh.exe'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,x):
 p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('w',encoding='utf-8',newline='\n') as f:f.write(json.dumps(x,ensure_ascii=False,indent=2)+'\n');f.flush()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
PLAN=read(B/'reference/exact-seven-role-plan.json')
ENTRY=B/'tools/capture_android02.ps1'
PRODUCER=B/'selfchecks/capture_fixture.py'
RUN=B/'selfchecks/work'/('suite-'+uuid.uuid4().hex[:12]);RUN.mkdir(parents=True)
START=time.monotonic();results=[];text_total=0;payload_total=0;outer_count=0;producer_count=0

def case(name,modes=('identity',),fault='NONE',q=2):
 global payload_total
 home=RUN/name;root=home/'outputs';root.mkdir(parents=True)
 for d in ('tools','reference','release'):(home/d).mkdir()
 for rel in ('tools/capture_android02.ps1','reference/exact-seven-role-plan.json','reference/legacy-tool-route-contract.json'):(home/rel).write_bytes((B/rel).read_bytes())
 slots=[]
 for i,mode in enumerate(modes):
  role=PLAN['steps'][i];s={'id':role['id'],'argv':[PY,'-I','-X','utf8','-B',PRODUCER.as_posix(),mode,str(root/'fixture-gate')],'maxTextBytes':min(role['maxTextBytes'],8192),'maxBinaryBytes':0,'qualificationSeconds':q}
  if mode in ('payload_app','payload_test'):
   n=4096 if mode=='payload_app' else 2048;p=root/(s['id']+'-fixture-input.bin');p.write_bytes(bytes(range(256))*(n//256));payload_total+=n
   s['payloadPin']={'path':str(p),'bytes':n,'sha256':sha(p)}
  slots.append(s)
 policy={'schema':'ANDROID02_CAPTURE_POLICY_V1','mode':'OFFLINE_FIXTURE','entrySha256':sha(ENTRY),'planSha256':sha(B/'reference/exact-seven-role-plan.json'),'productSealSha256':PLAN['product']['sealSha256'],'scope':hashlib.sha256(name.encode()).hexdigest(),'evidenceRoot':str(root),'toolSha256':sha(PY),'fixtureScriptSha256':sha(PRODUCER),'fixtureFault':fault,'fixtureGatePath':str(root/'fixture-gate'),'slots':slots}
 save(home/'release/capture-policy.json',policy)
 return home,root,policy

def invoke(c,index=0,proofsha='ABSENT',mutate=None,policy_mutate=None,release_gate=False,raw_request=None,outerargv=None):
 global text_total,outer_count,producer_count
 home,root,policy=c
 if time.monotonic()-START>26:raise AssertionError('SUITE_ADMISSION_STOP_26_SECONDS_NO_MORE_CHILDREN')
 if policy_mutate:policy_mutate(policy);save(home/'release/capture-policy.json',policy)
 slot=policy['slots'][index];req={'schema':'ANDROID02_CAPTURE_REQUEST_V1','id':slot['id'],'policySha256':sha(home/'release/capture-policy.json'),'scope':policy['scope'],'evidenceRoot':str(root),'argv':slot['argv'],'maxTextBytes':slot['maxTextBytes'],'maxBinaryBytes':0,'qualificationSeconds':slot['qualificationSeconds']}
 if mutate:mutate(req)
 request=home/('request-'+slot['id']+'-'+str(outer_count)+'.json');save(request,req)
 if raw_request:request.write_text(raw_request(request.read_text()),encoding='utf-8')
 argv=[PS,'-NoProfile','-NonInteractive','-File',str(home/'tools/capture_android02.ps1'),'-RequestPath',str(request),'-PredecessorProofSha',proofsha]
 if outerargv:argv=outerargv
 begin=time.monotonic();p=subprocess.Popen(argv,stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.PIPE);outer_count+=1
 chunks=[bytearray(),bytearray()];errors=[]
 def drain(stream,target):
  try:
   while True:
    b=stream.read(4096)
    if not b:break
    target.extend(b)
    if len(target)>65536:errors.append('OUTER_STREAM_BOUND_EXCEEDED')
  except BaseException as e:errors.append(repr(e))
 threads=[threading.Thread(target=drain,args=(s,t)) for s,t in zip((p.stdout,p.stderr),chunks)]
 for t in threads:t.start()
 gate_pending=False
 if release_gate:
  until=time.monotonic()+2
  while time.monotonic()<until:
   if (root/'capture-halted.json').exists():gate_pending=p.poll() is None;break
   time.sleep(.005)
  (root/'fixture-gate').write_bytes(b'RELEASE_ONLY_CONTROLLED_LOCAL_GATE')
 # No timeout kills: wait is on this exact original Popen, not a replacement.
 code=p.wait()
 for t in threads:t.join()
 p.stdout.close();p.stderr.close();p._handle.Close()
 out,err=map(bytes,chunks);text_total+=len(out)+len(err)
 console=None
 try:console=json.loads(out)
 except (ValueError,UnicodeError):pass
 suffix='-attempt-'+str(outer_count)
 # Success chain names are immutable and are the exact bytes this owner read.
 base=slot['id'] if not (root/(slot['id']+'-outer-return.json')).exists() else slot['id']+suffix
 (root/(base+'-console.bin')).write_bytes(out);(root/(base+'-controller-stderr.bin')).write_bytes(err)
 native={'argv':argv,'controllerPid':p.pid,'exitCode':code,'originalControllerWaitReturned':True,'sameOriginalPipeReadersJoined':all(not t.is_alive() for t in threads),'outerStreamsClosed':p.stdout.closed and p.stderr.closed,'originalWindowsProcessHandleCloseReturned':True,'streamBytes':len(out)+len(err),'amountUnknown':bool(errors),'stdoutSha256':hashlib.sha256(out).hexdigest(),'stderrSha256':hashlib.sha256(err).hexdigest(),'sourceEntrySha256':sha(home/'tools/capture_android02.ps1'),'requestSha256':sha(request),'scope':policy['scope'],'id':slot['id'],'producerKind':'OFFLINE_PYTHON_NOT_SDK','elapsedSeconds':time.monotonic()-begin,'gatePendingOriginalControllerObserved':gate_pending}
 save(root/(base+'-outer-return.json'),native)
 if console and console.get('started'):producer_count+=1
 assert not errors,errors
 assert text_total<=4194304 and payload_total<=65536
 return code,console,err,native

def check(name,fn):
 begin=time.monotonic()
 try:detail=fn();results.append({'name':name,'pass':True,'detail':detail,'seconds':time.monotonic()-begin})
 except BaseException as e:results.append({'name':name,'pass':False,'detail':repr(e),'seconds':time.monotonic()-begin});raise

def proof(c,co):
 home,root,policy=c;i=next(i for i,s in enumerate(policy['slots']) if s['id']==co['id'])
 assert co['captureQualified'] and co['allOriginalResourcesReturnedAtConsole']
 assert co['semantic'] in ('PASS','PASS_LIMITED_APP_RECEIPT_INTERNAL_FINISH_UNPROVEN')
 d={'schema':'ANDROID02_CAPTURE_COMPLETION_PROOF_V1','id':co['id'],'nextId':policy['slots'][i+1]['id'],'scope':policy['scope'],'controllerPid':co['controllerPid'],'controllerExited':True,'toolStreamsReturned':True,'originalResourcesReturnedAtConsole':True,'captureQualifiedAtConsole':True,'approvedForNext':True,'captureReceiptSha256':co['captureReceiptSha256'],'semanticDependency':co['id']+'_ACTUAL_RETURN_AND_SEMANTIC_PASS','dependencyAccepted':True,'batchSdkChildrenEntered':co['batchSdkChildrenEntered'],'batchTextChargedBytesKnown':co['batchTextChargedBytesKnown'],'batchBinaryArchiveBytesKnown':0,'batchAmountUnknown':False,'batchGroups':co['batchGroups'],'outerReturnSha256':sha(root/(co['id']+'-outer-return.json')),'scopeStartTick':co['scopeStartTick']}
 p=root/(co['id']+'-completion-proof.json');save(p,d)
 # save() returned after the proof writer's own flush and close.
 return sha(p)

positive=None;positive_first=None
def chain():
 global positive,positive_first
 positive=case('seven-role-positive',('identity','global_idle','app_absence','test_absence','payload_app','payload_test','instrument'));prev='ABSENT';groups=[]
 for i in range(7):
  code,co,err,native=invoke(positive,i,prev);assert code==0 and not err,(i,code,err.decode(errors='replace'),co)
  assert co['captureQualified'] and co['batchSdkChildrenEntered']==i+1
  assert sum(co['batchGroups'][k] for k in ('preflight','install','instrument','control'))==co['batchTextChargedBytesKnown']
  if groups:assert all(co['batchGroups'][k]>=groups[-1][k] for k in co['batchGroups'])
  groups.append(co['batchGroups'])
  if i==0:positive_first=copy.deepcopy(co)
  if i in (4,5):assert co['input']['verified'] and co['input']['stdinWriteReturnedBytes']==(4096 if i==4 else 2048) and co['input']['sourceCloseReturned']
  if i<6:prev=proof(positive,co)
 assert co['semantic']=='PASS_LIMITED_APP_RECEIPT_INTERNAL_FINISH_UNPROVEN'
 raw=(positive[1]/'scope_all-stdout.bin').read_bytes();assert b'INSTRUMENTATION_STATUS:' in raw and b'INSTRUMENTATION_RESULT:' in raw
 assert co['batchGroups']['payload']==6144
 return {'groups':groups,'finalSemantic':co['semantic'],'actualSdkChildren':0,'localProducers':7}

def rejection(name,mutation=None,pm=None,raw=None,expected=None):
 c=case(name);code,co,err,native=invoke(c,mutate=mutation,policy_mutate=pm,raw_request=raw)
 assert code!=0 and co is None and not (c[1]/'identity-entered.json').exists(),(code,co,err)
 if expected:assert expected.encode() in err,err.decode(errors='replace')
 return {'rejectedBeforeContext':True,'sdkChildren':0,'stderrSha256':native['stderrSha256']}

def failed_capture(name,mode,expected,q=2,cap=None,gate=False,fault='NONE'):
 c=case(name,(mode,),fault=fault,q=q)
 if cap:c[2]['slots'][0]['maxTextBytes']=cap;save(c[0]/'release/capture-policy.json',c[2])
 code,co,err,native=invoke(c,release_gate=gate)
 assert code==2 and co and not co['captureQualified'] and (c[1]/'capture-halted.json').exists(),(code,co,err)
 assert expected in co['firstFailure'],co
 assert co['allOriginalResourcesReturnedAtConsole'] and co['waitReturned'] and co['processDisposed']
 if gate:assert native['gatePendingOriginalControllerObserved']
 return {'failure':co['firstFailure'],'originalReturned':True,'gateObservedPending':native['gatePendingOriginalControllerObserved'],'rawBytes':co['rawBytesKnown'],'savedBytes':co['rawTextSavedBytesKnown']}

def busy():
 c=case('global-busy',('identity','global_busy','app_absence'));code,co,_,_=invoke(c);assert code==0;prev=proof(c,co)
 code,co,_,_=invoke(c,1,prev);assert code==2 and co['semantic'].startswith('ENV_WAIT') and (c[1]/'capture-halted.json').exists()
 # Forged true labels are deliberately negative fixtures, not real completion proofs.
 fp=c[1]/'global_idle-completion-proof.json';fake=read(c[1]/'identity-completion-proof.json');fake.update(id='global_idle',nextId='app_absence',controllerPid=co['controllerPid'],captureReceiptSha256=co['captureReceiptSha256'],batchSdkChildrenEntered=2,batchTextChargedBytesKnown=co['batchTextChargedBytesKnown'],batchGroups=co['batchGroups'],outerReturnSha256=sha(c[1]/'global_idle-outer-return.json'));save(fp,fake)
 code,none,_,_=invoke(c,2,sha(fp));assert code!=0 and none is None and not (c[1]/'app_absence-entered.json').exists()
 return {'envWaitStopped':True,'forgedTrueLabelsRejected':True,'sdkChildren':0}

def tampered_predecessor():
 home,root,pol=positive;pp=root/'identity-completion-proof.json';original=pp.read_bytes();p=read(pp);p['batchGroups']['preflight']=0;save(pp,p)
 try:
  code,co,err,_=invoke(positive,1,sha(pp));assert code!=0 and co is None and b'EXACT_AGGREGATE_GROUP_SUM' in err
 finally:pp.write_bytes(original)
 return 'Counter reset rejected before reentry'

def guard_batch():
 """Pre-context throws can share one outer host: none has entered a Process.
 This is only a finite test harness; it cannot run a successful capture role.
 """
 guards=[]
 for name,expected in [('entry','ENTRY_POLICY_PIN'),('preparation','PREPARATION_ONLY_NO_EXECUTION_AUTHORIZATION'),('sdk','EXACT_LOCAL_PRODUCER_ONLY'),('duplicate','DUPLICATE_JSON_FIELD'),('eighth','EXACT_SEVEN_ROLES_MAX')]:
  c=case('batch-'+name);home,root,p=c
  if name=='entry':p['entrySha256']='0'*64
  if name=='preparation':p['mode']='PREPARATION_ONLY'
  if name=='sdk':p['slots'][0]['argv'][0]=PLAN['sdkFiles'][0]['path']
  if name=='eighth':p['slots']*=8
  save(home/'release/capture-policy.json',p);s=p['slots'][0]
  req={'schema':'ANDROID02_CAPTURE_REQUEST_V1','id':s['id'],'policySha256':sha(home/'release/capture-policy.json'),'scope':p['scope'],'evidenceRoot':str(root),'argv':s['argv'],'maxTextBytes':s['maxTextBytes'],'maxBinaryBytes':0,'qualificationSeconds':s['qualificationSeconds']};rp=home/'guard-request.json';save(rp,req)
  if name=='duplicate':rp.write_text(rp.read_text().replace('{','{"schema":"duplicate",',1),encoding='utf-8')
  if name=='preparation':rp=home/'missing-request.json'
  guards.append({'name':name,'entry':str(home/'tools/capture_android02.ps1'),'request':str(rp),'proof':'ABSENT','expected':expected,'root':str(root),'id':'identity'})
 home,root,p=positive;pp=root/'identity-completion-proof.json';prior=pp.read_bytes();forged=read(pp);forged['batchGroups']['preflight']=0;save(pp,forged)
 s=p['slots'][1];req={'schema':'ANDROID02_CAPTURE_REQUEST_V1','id':s['id'],'policySha256':sha(home/'release/capture-policy.json'),'scope':p['scope'],'evidenceRoot':str(root),'argv':s['argv'],'maxTextBytes':s['maxTextBytes'],'maxBinaryBytes':0,'qualificationSeconds':s['qualificationSeconds']};rp=home/'counter-negative.json';save(rp,req)
 guards.append({'name':'counter','entry':str(home/'tools/capture_android02.ps1'),'request':str(rp),'proof':sha(pp),'expected':'EXACT_AGGREGATE_GROUP_SUM','root':str(root),'id':'global_idle'})
 c=case('guard-batch-owner');gp=c[0]/'guards.json';save(gp,guards)
 script=c[0]/'precontext-guard-checks.ps1'
 script.write_text('''param([string]$Checks)
$ErrorActionPreference='Stop'
$results=@()
foreach($g in (Get-Content -LiteralPath $Checks -Raw | ConvertFrom-Json)){
 $caught=''
 try{& $g.entry -RequestPath $g.request -PredecessorProofSha $g.proof;throw 'UNEXPECTED_NO_REJECTION'}catch{$caught=$_.Exception.Message}
 if(-not $caught.Contains($g.expected)){throw ('GUARD_MISMATCH '+$g.name+' '+$caught)}
 $results+=@{name=$g.name;expected=$g.expected;observed=$caught;pass=$true}
}
@{guardResults=$results;started=$false;sdkChildren=0}|ConvertTo-Json -Depth 6 -Compress
''',encoding='utf-8')
 try:
  code,co,err,_=invoke(c,outerargv=[PS,'-NoProfile','-NonInteractive','-File',str(script),'-Checks',str(gp)])
  assert code==0 and not err and len(co['guardResults'])==6,(code,co,err)
  for g in guards[:5]:assert not (Path(g['root'])/'identity-entered.json').exists()
  return co['guardResults']
 finally:pp.write_bytes(prior)

def busy_semantic():
 # Already captured original local busy stream, not historical real-device data.
 sources=[p for p in (B/'selfchecks/work').glob('suite-*/global-busy/outputs/global_idle-stdout.bin') if p.stat().st_size]
 assert sources
 c=case('busy-semantic-owner');script=c[0]/'semantic-only.ps1'
 save(c[0]/'args.json',{'semanticSource':str(B/'tools/semantic-gates.ps1.txt'),'plan':str(B/'reference/exact-seven-role-plan.json'),'raw':str(sources[0])})
 script.write_text('''param([string]$Inputs)
$ErrorActionPreference='Stop';$a=Get-Content -LiteralPath $Inputs -Raw|ConvertFrom-Json
$plan=Get-Content -LiteralPath $a.plan -Raw|ConvertFrom-Json
. ([scriptblock]::Create([IO.File]::ReadAllText($a.semanticSource)))
$s=RoleSemantic 'global_idle' $a.raw $true
if($s -cne 'ENV_WAIT_OTHER_PROJECT_OR_TEST_OCCUPIED'){throw $s}
@{started=$false;semantic=$s;sdkChildren=0;kind='PURE_LOCAL_SEMANTIC_ONLY'}|ConvertTo-Json -Compress
''',encoding='utf-8')
 code,co,err,_=invoke(c,outerargv=[PS,'-NoProfile','-NonInteractive','-File',str(script),'-Inputs',str(c[0]/'args.json')]);assert code==0 and not err,(code,co,err)
 return co

try:
 check('seven-role-chain',chain)
 check('six-precontext-guards-one-owner',guard_batch)
 check('busy-semantic-original-local-raw',busy_semantic)
 check('overrun-sticky',lambda:failed_capture('overrun','overrun','TEXT_QUALIFIER_EXCEEDED',cap=80))
 check('stderr-stops',lambda:failed_capture('stderr','stderr','STDERR_REQUIRES_STOP'))
 check('timeout-keeps-original',lambda:failed_capture('late','late','QUALIFICATION_TIMEOUT_NO_TERMINATION',q=.2,gate=True))
 check('file-close-retains-owner',lambda:failed_capture('close-gate','identity','QUALIFICATION_TIMEOUT_NO_TERMINATION',q=.2,gate=True,fault='CLOSE_GATE'))
finally:
 elapsed=time.monotonic()-START
 summary={'schema':'ANDROID02_READY01_LOCAL_SELFCHECK_V1','candidateEntrySha256':sha(ENTRY),'producerSha256':sha(PRODUCER),'planSha256':sha(B/'reference/exact-seven-role-plan.json'),'runRoot':str(RUN),'elapsedSeconds':elapsed,'suiteWithin30Seconds':elapsed<=30,'totalOuterTextBytes':text_total,'mockPayloadBytes':payload_total,'outerControllers':outer_count,'localProducerStarts':producer_count,'sdkChildren':0,'deviceQueries':0,'serverQueries':0,'kills':0,'retries':0,'results':results,'allPassed':bool(results) and all(r['pass'] for r in results) and len(results)==7 and elapsed<=30}
 save(RUN/'summary.json',summary);save(B/'evidence/local-selfcheck-latest.json',summary)
 print(json.dumps(summary,ensure_ascii=False))
