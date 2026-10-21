from pathlib import Path
import os,subprocess,time,datetime,json,hashlib,stat
R=Path('D:/CodexProjects/VideoKit');E=Path(__file__).resolve().parent;P=R/'docs/tester/D1_FIXTURE_SIX01_QUALIFIER_PREPARATION';B=R/'docs/coder/d1fixture-six01-evidence';T=R/'docs/coder/d1fixture-tool02'
INPUT=R/'docs/coder/d1fixture-six01/new-output/avc6-candidate.mp4';EXPECTED='19e815a413ae8275fe61e917ff9ac3c67d74a4f845df548a6ce2c382c0778a9c';SCOPE='D1QUAL01-CANDIDATE-001'
assert not (E/'control-001').exists(),'ONE_EXACT_INVOCATION_GUARD_NO_REPLAY'
D=E/'control-001';D.mkdir(exist_ok=False);TEMP=D/'temp';TEMP.mkdir();reads=[]
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf8')
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(p,phase):
 h=hashlib.sha256();n=0
 with p.open('rb') as f:
  for b in iter(lambda:f.read(65536),b''):n+=len(b);h.update(b)
 if p==INPUT:reads.append(dict(phase=phase,kind='EXTERNAL_EXACT_IDENTITY_HASH_READ',bytes=n,helperReadBudgetCharged=False))
 return h.hexdigest()
owner=dict(scope=SCOPE,registeredUtc=now(),registeredBeforePreflightAndPopen=True,state='REGISTERED',processInvocations=0,originalProcessReturned=False,stdoutHandleClosed=False,stderrHandleClosed=False,controllerTimeoutUnknownSticky=False,outputLimitUnknownSticky=False,killInterruptSecondCloseRetryRefundActions=0,oldSessionQueriesOrInterventions=0)
save(D/'owner.json',owner)
def verify(phase):
 assert sha(B/'fixture-six01-freeze.json',phase)=='ffd195f62f0fa0f6266ff2683053dd578b35cac8999acc0b747e0ec1c62c86c4'
 sealed=load(B/'fixture-six01-freeze.json');assert len(sealed['files'])==38
 for row in sealed['files']:
  p=R/row['path'];assert p.stat().st_size==row['bytes'] and sha(p,phase)==row['sha256']
 assert sha(P/'review-evidence-manifest.json',phase)=='6c570d2ac81c20f3bebf28d141c92edf85a153ccecfe7462e367ea8f011d412f'
 manifest=load(P/'review-evidence-manifest.json');assert sha(R/manifest['report'],phase)=='0e98643827cdb7cef7841965c34bcdc6a039afe5956006bf1f979e8cf0920e73'
 for row in manifest['evidenceFiles']:
  p=R/row['path'];assert p.stat().st_size==row['bytes'] and sha(p,phase)==row['sha256']
 contract=load(P/'future-execution-contract.json')
 assert {p.resolve() for p in (P/'classes').rglob('*') if p.is_file()}=={Path(x['path']).resolve() for x in contract['classIdentities']} and len(contract['classIdentities'])==3
 for row in [contract['helperSource'],contract['jarIdentity']]+contract['classIdentities']+contract['javaIdentity']:
  p=Path(row['path']);assert p.stat().st_size==row['bytes'] and sha(p,phase)==row['sha256']
 assert contract['helperSource']['sha256']=='a757ecc7587c9a02ce817152f092659863ff3370e6e594bef5acbe4a08ad3544'
 assert contract['jarIdentity']['sha256']=='c4ed36f31cab8381bc47c0aea4c3f3d8a9c2afab09991a04a83102877f1bfecd'
 a=INPUT.stat();assert a.st_size==8849 and (a.st_file_attributes&stat.FILE_ATTRIBUTE_READONLY) and not (a.st_file_attributes&stat.FILE_ATTRIBUTE_REPARSE_POINT) and not INPUT.is_symlink()
 for p in [INPUT]+list(INPUT.parents):
  z=p.lstat();assert not p.is_symlink() and not (z.st_file_attributes&stat.FILE_ATTRIBUTE_REPARSE_POINT)
 assert next(x for x in sealed['files'] if R/x['path']==INPUT)['sha256']==EXPECTED
 return dict(phase=phase,checkedUtc=now(),sealedGenerationRows=38,helperEvidenceFiles=len(manifest['evidenceFiles']),helperClasses=3,exactClassSet=True,readOnly=True,noReparse=True,mediaBytes=8849,mediaSha256=EXPECTED,helperSource=contract['helperSource'],jar=contract['jarIdentity'],classes=contract['classIdentities'],javaIdentity=contract['javaIdentity'])
try:
 pre=verify('PRE_DISPATCH');save(E/'preflight.json',pre)
except BaseException as e:
 owner.update(state='BLOCKED_IDENTITY_ZERO_INVOCATIONS',errorClass=type(e).__name__);save(D/'owner.json',owner);save(E/'external-read-ledger.json',reads);raise
req=R/'docs/milestones/D1_FIXTURE_SIX01_CONTAINER_QUALIFY_TESTER_REQUIREMENTS_V1.0.md';(E/'authorized-requirements-snapshot.md').write_bytes(req.read_bytes())
argv=['D:/Android/Android Studio/jbr/bin/java.exe','-Xmx256m','-XX:-UsePerfData','-cp','D:/CodexProjects/VideoKit/docs/tester/D1_FIXTURE_SIX01_QUALIFIER_PREPARATION/classes;D:/CodexProjects/VideoKit/docs/coder/d1fixture-tool02/artifacts/videokit-fixture-tool02.jar','com.videokit.fixturetool.Six01ContainerQualifier','--expected-sha256='+EXPECTED,'--expected-bytes=8849','--scope='+SCOPE]
env=os.environ.copy();keys=['JAVA_TOOL_OPTIONS','JDK_JAVA_OPTIONS','_JAVA_OPTIONS','JDK_JAVAC_OPTIONS','CLASSPATH']
for k in keys:env.pop(k,None)
env['TEMP']=str(TEMP);env['TMP']=str(TEMP);env['JAVA_HOME']='D:/Android/Android Studio/jbr'
owner.update(argv=argv,cwd=str(D),environmentInjectionKeysCleared={k:k not in env for k in keys},environmentOverrides=dict(TEMP=str(TEMP),TMP=str(TEMP),JAVA_HOME=env['JAVA_HOME']),state='ORIGINAL_POPEN_ALLOCATION_ENTERED',processInvocations=1,requirementsSha256=sha(req,'CONTROL'),receiptUtf8CombinedCap=1048576,controllerObservationSeconds=60)
save(D/'owner.json',owner);out=(D/'stdout.raw').open('xb');err=(D/'stderr.raw').open('xb');proc=None;start=time.monotonic()
try:
 owner['startUtc']=now();proc=subprocess.Popen(argv,cwd=D,env=env,stdin=subprocess.DEVNULL,stdout=out,stderr=err,shell=False);owner.update(pid=proc.pid,state='SAME_ORIGINAL_PROCESS_STARTED');save(D/'owner.json',owner)
 while True:
  try:code=proc.wait(timeout=.25);break
  except subprocess.TimeoutExpired:
   n=(D/'stdout.raw').stat().st_size+(D/'stderr.raw').stat().st_size
   if n>1048576:owner['outputLimitUnknownSticky']=True
   if time.monotonic()-start>=60 or owner['outputLimitUnknownSticky']:
    owner.update(controllerTimeoutUnknownSticky=True,state='UNKNOWN_ORIGINAL_RETAINED_NO_SUCCESSOR');save(D/'owner.json',owner);print('UNKNOWN same original retained; no kill/retry',flush=True);code=proc.wait();break
 owner.update(originalProcessReturned=True,exitCode=code,endUtc=now(),elapsedSeconds=time.monotonic()-start,state='ORIGINAL_NATURAL_RETURN')
finally:
 if proc is None or owner['originalProcessReturned']:out.close();err.close();owner.update(stdoutHandleClosed=True,stderrHandleClosed=True)
 save(D/'owner.json',owner)
stdout=(D/'stdout.raw').read_bytes();stderr=(D/'stderr.raw').read_bytes();total=len(stdout)+len(stderr)
if total>1048576:owner['outputLimitUnknownSticky']=True;save(D/'owner.json',owner)
receipts=[];nonreceipt=[];utf8=True
if total<=1048576:
 try:
  text=stdout.decode('utf8',errors='strict');stderr.decode('utf8',errors='strict')
  for line in text.splitlines():
   try:r=json.loads(line)
   except (ValueError,TypeError):nonreceipt.append(line);continue
   if isinstance(r,dict) and r.get('helper')=='SIX01_QUALIFIER_PREPARATION_COMPILED_NOT_YET_AUTHORIZED_TO_READ':receipts.append(r)
   else:nonreceipt.append(line)
 except UnicodeError:utf8=False
save(E/'all-original-receipts.json',receipts);save(E/'nonreceipt-output-lines.json',nonreceipt)
post=None;postError=None
try:post=verify('POST_ORIGINAL_RETURN');save(E/'post-return-preservation.json',post)
except BaseException as e:postError=type(e).__name__;save(E/'post-return-preservation.json',dict(result='IDENTITY_MISMATCH_OR_UNPROVEN',errorClass=postError))
save(E/'external-read-ledger.json',dict(reads=reads,totalOriginalMediaBytes=sum(x['bytes'] for x in reads),helperBudgetCharged=False,measurement='Logical application bytes not physical disk IO; control/JDK/JAR/archive hashes separate'))
final=receipts[-1] if receipts else {};obs=final.get('actualContainerObservation');inp=final.get('originalInputOwner',{});deadline=final.get('workerDeadline',{})
conditions=dict(originalProcess=owner['originalProcessReturned'] and owner.get('exitCode')==0,captureHandlesReturned=owner['stdoutHandleClosed'] and owner['stderrHandleClosed'],noControllerUnknown=not owner['controllerTimeoutUnknownSticky'] and not owner['outputLimitUnknownSticky'],completeUtf8Output=utf8 and total<=1048576 and not nonreceipt and len(stderr)==0,originalFinalStatus=final.get('status')=='HOST_CONTAINER_QUALIFICATION',scopeAndIdentity=final.get('scopeLabelNotAuthority')==SCOPE and final.get('expectedBytes')==8849 and final.get('expectedSha256')==EXPECTED and final.get('wholeHash')==EXPECTED and final.get('wholeHashEof') is True,originalInputReturned=inp.get('state')=='CLOSE_RETURNED' and inp.get('sameOriginalCloseReturned') is True and not inp.get('uncertainSticky',True),originalReaderAndWorker=final.get('sameOriginalCheckerThreadJoined') is True and final.get('originalInputAndLibraryReaderReturn') is True,timelyBodyAndJoin=deadline.get('timelyBodyAndOriginalJoin') is True and not deadline.get('deadlineUnknownSticky',True),noFirstError=final.get('firstError') is None,noEarlierUnknown=all(not x.get('status','').startswith('UNKNOWN') for x in receipts),actualContainerObserved=isinstance(obs,dict),postIdentityPreserved=post is not None and postError is None)
good=all(conditions.values());status='PASS_HOST_CONTAINER_QUALIFICATION_ONLY' if good else 'FAILED_OR_BLOCKED_OR_UNKNOWN_NO_RETRY'
save(E/'execution-result.json',dict(scope=SCOPE,status=status,conditions=conditions,originalProcessOwner=owner,rawStdoutBytes=len(stdout),rawStderrBytes=len(stderr),allOriginalReceiptCount=len(receipts),nonreceiptLines=len(nonreceipt),finalOriginalReceipt=final,actualContainerObservation=obs,media3='NOT_RUN',decode='NOT_RUN',Android='NOT_RUN',hostIsolatedFormat='NOT_RUN',READY=False,COMMIT=False,oldSessionsTouched=False,subsequentTestAdmitted=False))
print(json.dumps(dict(status=status,exitCode=owner.get('exitCode'),elapsedSeconds=owner.get('elapsedSeconds'),receiptCount=len(receipts),stdoutBytes=len(stdout),stderrBytes=len(stderr),firstError=final.get('firstError'),originalHelperStatus=final.get('status'),failedConditions=[k for k,v in conditions.items() if not v]),ensure_ascii=False),flush=True)
