from pathlib import Path
import os,subprocess,time,datetime,json,hashlib,stat,re
R=Path('D:/CodexProjects/VideoKit');E=Path(__file__).resolve().parent;P=R/'docs/tester/D1_FIXTURE_SIX01_QUALIFIER03_PREPARATION';B=R/'docs/coder/d1fixture-six01-evidence'
INPUT=R/'docs/coder/d1fixture-six01/new-output/avc6-candidate.mp4';EXPECTED='19e815a413ae8275fe61e917ff9ac3c67d74a4f845df548a6ce2c382c0778a9c';SCOPE='D1QUAL03-CANDIDATE-001'
assert not (E/'control-001').exists(),'ONCE_SCOPE_PHYSICAL_GUARD_NO_REPLAY'
D=E/'control-001';D.mkdir(exist_ok=False);TEMP=D/'temp';TEMP.mkdir();reads=[]
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf8')
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(p,phase):
 h=hashlib.sha256();n=0
 with p.open('rb') as f:
  for b in iter(lambda:f.read(65536),b''):h.update(b);n+=len(b)
 if p==INPUT:reads.append(dict(phase=phase,kind='EXTERNAL_ORIGINAL_MEDIA_IDENTITY_HASH',bytes=n,chargedToHelperLedger=False))
 return h.hexdigest()
owner=dict(scope=SCOPE,registeredUtc=now(),registeredBeforePreflightAndPopen=True,state='REGISTERED',processInvocations=0,originalProcessReturned=False,stdoutHandleClosed=False,stderrHandleClosed=False,controllerTimeoutUnknownSticky=False,outputLimitUnknownSticky=False,killInterruptSecondCloseRetryRefundActions=0,oldSessionQueriesOrInterventions=0)
save(D/'owner.json',owner)
def verify(phase):
 assert sha(B/'fixture-six01-freeze.json',phase)=='ffd195f62f0fa0f6266ff2683053dd578b35cac8999acc0b747e0ec1c62c86c4';s=load(B/'fixture-six01-freeze.json');assert len(s['files'])==38
 for x in s['files']:p=R/x['path'];assert p.stat().st_size==x['bytes'] and sha(p,phase)==x['sha256']
 assert sha(P/'review-evidence-manifest.json',phase)=='cf2d8855e991387b887907e69aeacfb64135256aa5d1fae7b0d041709b48353a';v=load(P/'review-evidence-manifest.json');assert len(v['evidenceFiles'])==52 and sha(R/v['report'],phase)=='dbb128a02077e232042f59e1bce8cbe32061e9e2cf0132035798c904d8ab46a3'
 for x in v['evidenceFiles']:p=R/x['path'];assert p.stat().st_size==x['bytes'] and sha(p,phase)==x['sha256']
 contract=load(P/'future-execution-contract03.json');assert len(contract['exactHelperClassSet'])==6 and len(contract['exactSupportClassSet'])==2 and not contract['oldFullToolJarRuntimeAllowed']
 for directory,key in [('helper-classes','exactHelperClassSet'),('support','exactSupportClassSet')]:
  assert {p.resolve() for p in (P/directory).rglob('*') if p.is_file()}=={Path(x['path']).resolve() for x in contract[key]}
 for x in contract['exactHelperClassSet']+contract['exactSupportClassSet']+contract['sourceIdentities']+contract['javaIdentity']+[contract['uniqueJcodecJar']]:
  p=Path(x['path']);assert p.stat().st_size==x['bytes'] and sha(p,phase)==x['sha256']
 assert contract['uniqueJcodecJar']['sha256']=='1a7e8601be4ebb5665219f2ccfa6e75476323e7408a6b18824ecf2a37873de86'
 a=INPUT.stat();assert a.st_size==8849 and a.st_file_attributes&stat.FILE_ATTRIBUTE_READONLY and not a.st_file_attributes&stat.FILE_ATTRIBUTE_REPARSE_POINT
 for p in [INPUT]+list(INPUT.parents):assert not p.is_symlink() and not p.lstat().st_file_attributes&stat.FILE_ATTRIBUTE_REPARSE_POINT
 assert next(x for x in s['files'] if R/x['path']==INPUT)['sha256']==EXPECTED
 return dict(phase=phase,checkedUtc=now(),generationFrozenRows=38,checkerPreparationEvidenceRows=52,helperExactClasses=6,supportExactClasses=2,inputBytes=8849,inputSha256=EXPECTED,readonly=True,noReparse=True,fork=contract['uniqueJcodecJar'],helperClassPins=contract['exactHelperClassSet'],supportClassPins=contract['exactSupportClassSet'],javaIdentity=contract['javaIdentity'])
try:save(E/'preflight.json',verify('PRE_DISPATCH'))
except BaseException as e:owner.update(state='BLOCKED_PREFLIGHT_ZERO_INVOCATIONS',errorClass=type(e).__name__);save(D/'owner.json',owner);save(E/'external-read-ledger.json',reads);raise
contract=load(P/'future-execution-contract03.json');argv=list(contract['argvTemplate']);bindings={'--expected-sha256=<NEW_EXACT_AUTHORIZED_HASH>':'--expected-sha256='+EXPECTED,'--expected-bytes=<NEW_EXACT_AUTHORIZED_SIZE>':'--expected-bytes=8849','--scope=<NEW_EXACT_AUTHORIZED_SCOPE>':'--scope='+SCOPE};assert all(argv.count(k)==1 for k in bindings);argv=[bindings.get(x,x) for x in argv];assert sum(a!=b for a,b in zip(argv,contract['argvTemplate']))==3 and not any('<' in x for x in argv)
assert argv[1:5]==['-Xmx256m','-XX:-UsePerfData','-Xlog:class+load=info:file=loaded-classes.log:uptime,level,tags','-cp'] and argv[6]=='com.videokit.fixturetool.Six01ContainerQualifier03' and 'videokit-fixture-tool02.jar' not in argv[5]
req=R/'docs/milestones/D1_FIXTURE_SIX01_CONTAINER_QUALIFY03_TESTER_REQUIREMENTS_V1.0.md';(E/'authorized-requirements-snapshot.md').write_bytes(req.read_bytes())
save(E/'exact-bound-scope.json',dict(scope=SCOPE,argv=argv,originalTemplate=contract['argvTemplate'],onlyThreeBoundArguments=True,immutableInput=dict(path=str(INPUT),bytes=8849,sha256=EXPECTED),requirementsSha256=sha(req,'CONTROL')))
env=os.environ.copy();keys=['JAVA_TOOL_OPTIONS','JDK_JAVA_OPTIONS','_JAVA_OPTIONS','JDK_JAVAC_OPTIONS','CLASSPATH']
for k in keys:env.pop(k,None)
env['TEMP']=str(TEMP);env['TMP']=str(TEMP);env['JAVA_HOME']='D:/Android/Android Studio/jbr'
owner.update(state='ORIGINAL_POPEN_ALLOCATION_ENTERED',processInvocations=1,argv=argv,cwd=str(D),environmentInjectionKeysCleared={k:k not in env for k in keys},temp=str(TEMP),observeSeconds=60,combinedStdoutStderrUtf8Cap=1048576)
save(D/'owner.json',owner);out=(D/'stdout.raw').open('xb');err=(D/'stderr.raw').open('xb');proc=None;start=time.monotonic()
try:
 owner['startUtc']=now();proc=subprocess.Popen(argv,cwd=D,env=env,stdout=out,stderr=err,stdin=subprocess.DEVNULL,shell=False);owner.update(pid=proc.pid,state='SAME_ORIGINAL_STARTED');save(D/'owner.json',owner)
 while True:
  try:code=proc.wait(timeout=.25);break
  except subprocess.TimeoutExpired:
   n=(D/'stdout.raw').stat().st_size+(D/'stderr.raw').stat().st_size
   if n>1048576:owner['outputLimitUnknownSticky']=True
   if time.monotonic()-start>=60 or owner['outputLimitUnknownSticky']:
    owner.update(controllerTimeoutUnknownSticky=True,state='UNKNOWN_SAME_ORIGINAL_RETAINED_NO_SUCCESSOR');save(D/'owner.json',owner);print('UNKNOWN original retained without kill/retry',flush=True);code=proc.wait();break
 owner.update(originalProcessReturned=True,exitCode=code,endUtc=now(),elapsedSeconds=time.monotonic()-start,state='ORIGINAL_NATURAL_RETURN')
finally:
 if proc is None or owner['originalProcessReturned']:out.close();err.close();owner.update(stdoutHandleClosed=True,stderrHandleClosed=True)
 save(D/'owner.json',owner)
raw=(D/'stdout.raw').read_bytes();stderr=(D/'stderr.raw').read_bytes();total=len(raw)+len(stderr);receipts=[];nonreceipt=[];utf8=True
if total>1048576:owner['outputLimitUnknownSticky']=True;save(D/'owner.json',owner)
else:
 try:
  text=raw.decode('utf8',errors='strict');stderr.decode('utf8',errors='strict')
  for line in text.splitlines():
   try:r=json.loads(line)
   except (ValueError,TypeError):nonreceipt.append(line);continue
   if isinstance(r,dict) and r.get('helper')=='SIX01_QUALIFIER03_PREPARED_NO_EXECUTION_AUTHORITY':receipts.append(r)
   else:nonreceipt.append(line)
 except UnicodeError:utf8=False
save(E/'all-original-receipts.json',receipts);save(E/'nonreceipt-output-lines.json',nonreceipt)
postOkay=False
try:save(E/'post-return-preservation.json',verify('POST_ORIGINAL_RETURN'));postOkay=True
except BaseException as e:save(E/'post-return-preservation.json',dict(status='IDENTITY_UNPROVEN_OR_MISMATCH',errorClass=type(e).__name__))
save(E/'external-read-ledger.json',dict(entries=reads,originalMediaLogicalReadBytes=sum(x['bytes'] for x in reads),helperMediaLedgerCharged=False,measurement='External application logical payload not physical disk IO; archive/JAR/helper/JDK/control identities separately from original input'))
classlog=D/'loaded-classes.log';loaded=classlog.read_text(encoding='utf8',errors='strict') if classlog.is_file() else '';names=re.findall(r'\[class,load\]\s+(\S+)',loaded);originErrors=[]
for line in loaded.splitlines():
 m=re.search(r'\[class,load\]\s+(\S+)',line)
 if m and m[1].startswith(('org.jcodec.','net.sourceforge.jaad.')):
  if 'jcodec-0.2.5-videokit-observation01.jar' not in line:originErrors.append(line)
  if re.search(r'(?:Encoder|Decoder)(?:\$|$)',m[1]):originErrors.append(line)
 if m and m[1].startswith('com.videokit.fixturetool.SixFrameDriver'):originErrors.append(line)
if 'videokit-fixture-tool02.jar' in loaded:originErrors.append('OLD_FULL_TOOL_JAR_LOADED')
save(E/'actual-classload-audit.json',dict(logPresent=bool(loaded),loadedClassCount=len(names),actualJcodecClasses=sorted({x for x in names if x.startswith('org.jcodec.')}),originOrForbiddenClassErrors=originErrors,oldFullToolJarLoaded='videokit-fixture-tool02.jar' in loaded,jdkCharsetNotClassifiedAsMedia=True))
r=receipts[-1] if receipts else {};obs=r.get('actualContainerObservation');i=r.get('originalInputOwner',{});w=r.get('workerDeadline',{});metadata=r.get('actualOriginalMetadataObservation');child=r.get('actualDataReferenceChildObservation');proof=r.get('actualCodeSourceProof')
conditions=dict(originalProcessReturned=owner['originalProcessReturned'] and owner.get('exitCode')==0,originalStreamsReturned=owner['stdoutHandleClosed'] and owner['stderrHandleClosed'],noControllerUnknown=not owner['controllerTimeoutUnknownSticky'] and not owner['outputLimitUnknownSticky'],completeOriginalRawOutput=utf8 and total<=1048576 and not nonreceipt and not stderr,helperStatus=r.get('status')=='HOST_CONTAINER_QUALIFICATION',scopeAndHash=r.get('scopeLabelNotAuthority')==SCOPE and r.get('expectedSha256')==EXPECTED and r.get('expectedBytes')==8849 and r.get('wholeHash')==EXPECTED and r.get('wholeHashEof') is True,noEarlierUnknown=all(not x.get('status','').startswith('UNKNOWN') for x in receipts),firstErrorNull=r.get('firstError') is None,originalInputClose=i.get('state')=='CLOSE_RETURNED' and i.get('sameOriginalCloseReturned') is True and not i.get('uncertainSticky',True) and i.get('nativeInFlight')==0,originalFacadeAndWorker=r.get('originalInputAndLibraryReaderReturn') is True and r.get('sameOriginalCheckerThreadJoined') is True,timelyOriginalBodyJoin=w.get('timelyBodyAndOriginalJoin') is True and not w.get('deadlineUnknownSticky',True),readBudget=isinstance(i.get('mediaReadRequestedCumulative'),int) and i['mediaReadRequestedCumulative']<=1048576,actualContainer=isinstance(obs,dict),actualOriginalMetadata=isinstance(metadata,dict) and isinstance(child,dict),actualCodeSources=isinstance(proof,dict) and proof.get('forkVersion')=='0.2.5-videokit-observation01' and bool(loaded) and not originErrors,postIdentityUnchanged=postOkay)
good=all(conditions.values());status='PASS_HOST_CONTAINER_QUALIFICATION_ONLY' if good else 'FAILED_OR_BLOCKED_OR_UNKNOWN_NO_RETRY'
save(E/'execution-result.json',dict(scope=SCOPE,status=status,conditions=conditions,originalProcessOwner=owner,rawStdoutBytes=len(raw),rawStderrBytes=len(stderr),allOriginalReceiptCount=len(receipts),nonreceiptLineCount=len(nonreceipt),finalOriginalReceipt=r,actualContainerObservation=obs,actualOriginalMetadataObservation=metadata,actualDataReferenceChildObservation=child,actualCodeSourceProof=proof,actualClassloadErrors=originErrors,media3='NOT_RUN',Android='NOT_RUN',decode='NOT_RUN',hostIsolatedFormat='NOT_RUN',READY=False,COMMIT=False,playback='NOT_RUN',oldSessionsTouched=False,successorAdmitted=False))
print(json.dumps(dict(status=status,exitCode=owner.get('exitCode'),elapsedSeconds=owner.get('elapsedSeconds'),receiptCount=len(receipts),stdoutBytes=len(raw),stderrBytes=len(stderr),firstError=r.get('firstError'),originalHelperStatus=r.get('status'),failedConditions=[k for k,v in conditions.items() if not v]),ensure_ascii=False),flush=True)
