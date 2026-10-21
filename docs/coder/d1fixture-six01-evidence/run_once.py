from pathlib import Path
import json,hashlib,datetime,subprocess,os,time,shutil
E=Path(__file__).resolve().parent;R=E.parents[2];T=R/'docs/coder/d1fixture-tool02';ROOT=R/'docs/coder/d1fixture-six01';OUTPUT=ROOT/'new-output/avc6-candidate.mp4'
J=Path('D:/Android/Android Studio/jbr');SCOPE='D1GEN01-CANDIDATE-001';D=E/'control-001';D.mkdir(exist_ok=False)
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(65536),b''):h.update(b)
 return h.hexdigest()
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def dump(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
assert not (E/'fixture-six01-freeze.json').exists()
owner={'scope':SCOPE,'registeredUtc':now(),'state':'REGISTERED_BEFORE_PREFLIGHT_AND_POPEN','processInvocations':0,'originalProcessReturned':False,'stdoutHandleClosed':False,'stderrHandleClosed':False,'controllerObservationUnknownSticky':False,'receiptBudgetExceededSticky':False,'killInterruptSecondCloseRetryRefundActions':0}
dump(D/'owner.json',owner)
try:
 seal=T/'evidence/fixture-tool02-freeze.json';assert sha(seal)=='5dbf3359e0aa9b06a9024cf0ace91bd1e532ddbfdc37ba11d81f0716c01dc51d'
 f=json.loads(seal.read_text());assert len(f['files'])==2774
 assert all((R/x['path']).stat().st_size==x['bytes'] and sha(R/x['path'])==x['sha256'] for x in f['files'])
 jar=T/'artifacts/videokit-fixture-tool02.jar';assert jar.stat().st_size==1954730 and sha(jar)=='c4ed36f31cab8381bc47c0aea4c3f3d8a9c2afab09991a04a83102877f1bfecd'
 compiler=json.loads((T/'evidence/compiler-identity.json').read_text());assert all(sha(Path(x['path']))==x['sha256'] for x in compiler['files'])
 report=R/'docs/tester/D1_FIXTURE_TOOL02_FIX_REVIEW_REPORT_V1.0.md';assert sha(report)=='4093db865bf0ed1419245c94a3102578835ce57ecd750da6010645a314176fb4'
 assert not ROOT.exists(),'DRIVER_OUTPUT_ROOT_EXISTS_ZERO_EXECUTIONS'
 refs=E/'reference';refs.mkdir();shutil.copyfile(report,refs/report.name)
 req=R/'docs/milestones/D1_FIXTURE_SIX01_GENERATE_CODER_REQUIREMENTS_V1.0.md';shutil.copyfile(req,refs/req.name)
 for p in [seal,T/'evidence/compiler-identity.json',T/'evidence/sbom02.json',T/'evidence/generation-plan02.json']:
  shutil.copyfile(p,refs/p.name)
 shutil.copytree(T/'licenses',refs/'tool-licenses')
 dump(D/'preflight.json',{'checkedUtc':now(),'toolSealSha256':sha(seal),'toolFrozenFilesVerified':2774,'toolJarSha256':sha(jar),'jdkFiles':compiler['files'],'independentReportSha256':sha(report),'requirementsSha256':sha(req),'outputRootAbsent':True,'controllerDidNotCreateOutputRoot':True,'inputOriginalMediaOpened':False,'oldSessionQueriesOrInterventions':0})
except BaseException as error:
 owner['state']='BLOCKED_PREFLIGHT_ZERO_EXECUTIONS';owner['blockedErrorClass']=type(error).__name__;dump(D/'owner.json',owner);raise
argv=['D:/Android/Android Studio/jbr/bin/java.exe','-Xmx256m','-XX:-UsePerfData','-jar','D:/CodexProjects/VideoKit/docs/coder/d1fixture-tool02/artifacts/videokit-fixture-tool02.jar','--generate-six','--scope=D1GEN01-CANDIDATE-001']
env=os.environ.copy();cleared={}
for key in ['JAVA_TOOL_OPTIONS','JDK_JAVA_OPTIONS','_JAVA_OPTIONS','JDK_JAVAC_OPTIONS','CLASSPATH']:
 cleared[key]={'wasPresent':key in env,'presentAfterClear':False};env.pop(key,None)
temp=D/'temp';temp.mkdir();env['TMP']=str(temp);env['TEMP']=str(temp);env['JAVA_HOME']=str(J)
owner.update({'argv':argv,'cwd':str(D),'environmentInjectionKeysCleared':cleared,'environmentOverrides':{'TEMP':str(temp),'TMP':str(temp),'JAVA_HOME':str(J)},'stdout':'control-001/stdout.raw','stderr':'control-001/stderr.raw','receiptUtf8TotalCap':1048576,'controllerObservationSeconds':60,'bodyDeadlineMeaning':'Driver monotonic body/cleanup60s and actual original join; controller separate original-process observation, no automatic kill','processInvocations':1,'state':'POpen_ALLOCATION_ENTERED'})
dump(D/'owner.json',owner);out=(D/'stdout.raw').open('xb');err=(D/'stderr.raw').open('xb');proc=None;started=time.monotonic()
try:
 owner['startUtc']=now();proc=subprocess.Popen(argv,cwd=D,env=env,stdin=subprocess.DEVNULL,stdout=out,stderr=err,shell=False);owner['pid']=proc.pid;owner['state']='SAME_ORIGINAL_PROCESS_STARTED';dump(D/'owner.json',owner)
 while True:
  try:code=proc.wait(timeout=.25);break
  except subprocess.TimeoutExpired:
   bytesNow=(D/'stdout.raw').stat().st_size+(D/'stderr.raw').stat().st_size
   if bytesNow>1048576:owner['receiptBudgetExceededSticky']=True
   if time.monotonic()-started>=60 or owner['receiptBudgetExceededSticky']:
    owner['controllerObservationUnknownSticky']=True;owner['state']='UNKNOWN_ORIGINAL_PROCESS_RETAINED_NO_NEW_ADMISSION';owner['observedRawOutputBytes']=bytesNow;dump(D/'owner.json',owner)
    code=proc.wait() # SAME original; keep both capture handles. No timeout kill.
    break
 owner['exitCode']=code;owner['originalProcessReturned']=True;owner['endUtc']=now();owner['elapsedSeconds']=time.monotonic()-started;owner['state']='ORIGINAL_NATURAL_RETURN_WITH_STICKY_UNKNOWN' if owner['controllerObservationUnknownSticky'] else 'ORIGINAL_NATURAL_RETURN'
finally:
 if proc is None or owner['originalProcessReturned']:
  out.close();owner['stdoutHandleClosed']=True;err.close();owner['stderrHandleClosed']=True
 dump(D/'owner.json',owner)
stdout=(D/'stdout.raw').read_bytes();stderr=(D/'stderr.raw').read_bytes();total=len(stdout)+len(stderr)
if total>1048576:owner['receiptBudgetExceededSticky']=True;dump(D/'owner.json',owner)
receipts=[];nonreceipt=[]
if total<=1048576:
 for line in stdout.decode('utf-8').splitlines():
  try:r=json.loads(line)
  except (ValueError,TypeError):nonreceipt.append(line);continue
  if isinstance(r,dict) and r.get('tool')=='D1_FIXTURE_TOOL02_FIX':receipts.append(r)
  else:nonreceipt.append(line)
dump(D/'all-original-json-receipts.json',receipts);dump(D/'nonreceipt-output-lines.json',nonreceipt)
final=receipts[-1] if receipts else {};pendingUnknown=any(str(x.get('status','')).startswith('UNKNOWN') or x.get('deadlineUnknownSticky') for x in receipts)
required={'scope':final.get('scopeLabelNotAuthorization')==SCOPE,'status':final.get('status')=='GENERATED_CANDIDATE_NOT_QUALIFIED','firstError':final.get('firstError') is None,'deadline':final.get('deadlineUnknownSticky') is False,'joined':final.get('sameWorkerExternallyJoined') is True,'resourcesReturned':final.get('originalResourceOwnersReturned') is True,'finish':final.get('muxFinishReturned') is True,'readOnly':final.get('outputReadOnly') is True,'wholeEOF':final.get('wholeOutputEof') is True,'workerTimely':final.get('workerDeadline',{}).get('timelyBodyAndOriginalJoin') is True,'writerForce':final.get('writer',{}).get('forceReturned') is True,'writerClosed':final.get('writer',{}).get('sameOriginalCloseReturned') is True,'readerClosed':final.get('reader',{}).get('sameOriginalCloseReturned') is True,'inputBound':isinstance(final.get('inputAttemptedReserved'),int) and final['inputAttemptedReserved']<=8388608,'outputBound':isinstance(final.get('outputBudget',{}).get('attemptedBytes'),int) and final['outputBudget']['attemptedBytes']<=16777216,'sixSamples':len(final.get('sixRawEncoderSamples',[]))==6,'controllerReturned':owner['originalProcessReturned'] and owner.get('exitCode')==0,'noStickyUnknown':not pendingUnknown and not owner['controllerObservationUnknownSticky'] and not owner['receiptBudgetExceededSticky']}
fileInfo=None
if OUTPUT.is_file():
 size=OUTPUT.stat().st_size
 if size<=16777216:
  fileInfo={'path':OUTPUT.relative_to(R).as_posix(),'bytes':size,'sha256':sha(OUTPUT),'dosReadOnly':bool(getattr(OUTPUT.stat(),'st_file_attributes',0)&1),'externalHashReadBytes':size,'hashInputChargedToDriver8MiB':False,'hashPurpose':'Separately authorized external preservation reread; no container parser or decoder'}
  required['fileSizeAndHash']=size==final.get('outputBytes') and fileInfo['sha256']==final.get('outputSha256')
  required['readOnlyAttribute']=fileInfo['dosReadOnly']
 else:required['outputFileOverBound']=False
else:required['outputFilePresent']=False
good=all(required.values())
result={'scope':SCOPE,'status':'GENERATED_CANDIDATE_NOT_QUALIFIED' if good else 'FAILED_OR_UNKNOWN_GENERATION_NO_RETRY','requirements':required,'originalDriverStatus':final.get('status'),'originalReceiptCount':len(receipts),'nonreceiptLineCount':len(nonreceipt),'rawStdoutBytes':len(stdout),'rawStderrBytes':len(stderr),'receiptUtf8TotalCap':1048576,'pendingUnknownNeverUpgraded':pendingUnknown,'originalProcessOwner':owner,'output':fileInfo,'fileIndependentQualification':'NOT_RUN','generationInvocations':1,'retryOrToolChangeOrFallback':False,'newDeviceOrOldSessionAction':False,'D1':'NOT_PASSED','M0':'NOT_STARTED'}
dump(E/'generation-result.json',result);dump(E/'last-original-driver-receipt.json',final)
print(json.dumps({'status':result['status'],'originalDriverStatus':final.get('status'),'originalProcessReturned':owner['originalProcessReturned'],'exitCode':owner.get('exitCode'),'elapsedSeconds':owner.get('elapsedSeconds'),'rawOutputBytes':total,'failedRequirements':[k for k,v in required.items() if not v],'output':fileInfo},ensure_ascii=False,indent=2),flush=True)
