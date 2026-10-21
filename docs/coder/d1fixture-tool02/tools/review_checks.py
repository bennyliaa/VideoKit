from pathlib import Path
import json,subprocess,hashlib,datetime,time,os,re,sys
B=Path(__file__).resolve().parents[1];R=B.parents[2];E=B/'evidence';J=Path('D:/Android/Android Studio/jbr/bin/java.exe')
assert len(sys.argv)==3 and sys.argv[1]=='--output','NEW_ABSOLUTE_REVIEW_OUTPUT_REQUIRED'
root=R/'docs/tester/D1_FIXTURE_TOOL02_FIX_REVIEW_EVIDENCE';raw=Path(sys.argv[2]);assert raw.is_absolute(),'ABSOLUTE_ONLY';D=raw.resolve()
assert root.resolve()==root and D.is_relative_to(root) and D!=root and not D.exists(),'EXACT_NEW_REVIEW_CHILD_ONLY'
seal=E/'fixture-tool02-freeze.json';frozen=json.loads(seal.read_text());assert all(hashlib.sha256((R/x['path']).read_bytes()).hexdigest()==x['sha256'] for x in frozen['files']),'FROZEN_IDENTITY_MISMATCH'
D.mkdir(parents=True,exist_ok=False)

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
build=json.loads((E/'build-result.json').read_text());assert build['status']=='COMPILED_AND_PACKAGED_ONLY_NOT_RUN'
pins=json.loads((E/'source-input-pins.json').read_text());assert all(sha(B/x['path'])==x['sha256'] for x in pins)
jar=B/'artifacts/videokit-fixture-tool02.jar';jarHash=sha(jar);start=time.monotonic();runs=[]
env=os.environ.copy()
for k in ['JAVA_TOOL_OPTIONS','JDK_JAVA_OPTIONS','_JAVA_OPTIONS','JDK_JAVAC_OPTIONS','CLASSPATH']:env.pop(k,None)
for mode,cp in [('source',str(B/'build-output/classes')),('production',str(jar)+';'+str(B/'build-output/test-classes'))]:
 remaining=60-(time.monotonic()-start);assert remaining>0,'WHOLE_BATCH_WINDOW_CLOSED_NO_MORE_ADMISSION'
 W=D/mode;W.mkdir();T=W/'temp';T.mkdir();env['TEMP']=str(T);env['TMP']=str(T)
 argv=[str(J),'-Xmx256m','-XX:-UsePerfData','-Xlog:class+load=info:file=loaded-classes.log:uptime,level,tags','-cp',cp,'com.videokit.fixturetool.FixtureToolFixCheck']
 owner={'mode':mode,'argv':argv,'cwd':str(W),'registeredBeforePopen':True,'originalProcessReturned':False,'outputHandlesClosed':False,'observationWindowSeconds':remaining,'timedOutSticky':False,'productionJarFirst':mode=='production','productionJarSha256':jarHash,'sourcePinsSha256':sha(E/'source-input-pins.json'),'frozenSealSha256':sha(seal),'controllerSha256':sha(Path(__file__)),'generationMainOrJobRunOrEncoderAllowed':False,'terminationOrInterruptOrRetryActions':0}
 dump(W/'owner.json',owner);out=(W/'stdout').open('xb');err=(W/'stderr').open('xb');proc=None
 try:
  owner['startUtc']=datetime.datetime.now(datetime.timezone.utc).isoformat();proc=subprocess.Popen(argv,cwd=W,env=env,stdout=out,stderr=err,stdin=subprocess.DEVNULL,shell=False);owner['pid']=proc.pid;dump(W/'owner.json',owner)
  try:code=proc.wait(timeout=remaining)
  except subprocess.TimeoutExpired:
   owner['timedOutSticky']=True;owner['state']='UNKNOWN_ORIGINAL_RETAINED_NO_NEXT_PATH';dump(W/'owner.json',owner);code=proc.wait()
  owner['exitCode']=code;owner['originalProcessReturned']=True;owner['endUtc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
 finally:
  if proc is None or owner['originalProcessReturned']:out.close();err.close();owner['outputHandlesClosed']=True
  dump(W/'owner.json',owner)
 runs.append(owner);assert code==0 and not owner['timedOutSticky'],(mode,'SELFTEST_FAILED_NO_REPLAY')
 text=(W/'stdout').read_text(encoding='utf-8');passes=re.findall(r'^PASS (.+)$',text,re.M);assert len(passes)==29 and 'allStartedWorkersJoined=true' in text
 line=next(x for x in text.splitlines() if x.startswith('DONE '));values={k:int(v) for k,v in re.findall(r'(allocatedPayloadBytes|nativeRequestedPayloadBytes|nativeReturnedOrControlledPhysicalPayloadBytes|expectedRetainedMemoryUnknown)=(\d+)',line)}
 assert values['allocatedPayloadBytes']<=32768 and values['nativeRequestedPayloadBytes']<=32768
 loaded=(W/'loaded-classes.log').read_text();classes=re.findall(r'\[class,load\]\s+(\S+)',loaded)
 assert classes and not any(x.startswith(('com.videokit.fixturetool.SixFrameDriver','org.jcodec.codecs.','org.jcodec.containers.')) for x in classes)
 usedJcodec=sorted({x for x in classes if x.startswith('org.jcodec.')});assert usedJcodec==['org.jcodec.common.io.SeekableByteChannel'],usedJcodec
 origin=text.splitlines()[0];assert ('artifacts/videokit-fixture-tool02.jar' if mode=='production' else 'build-output/classes/') in origin
 assert (W/'loaded-classes.log').stat().st_size<1048576 and (W/'stdout').stat().st_size<65536
 owner['groups']=passes;owner['payload']=values;owner['loadedJcodecTypes']=usedJcodec;owner['noGenerationClassLoaded']=True;owner['actualOrigins']=origin;dump(W/'owner.json',owner)
 print(mode,'PASS29','natural original process return','payload',values,flush=True)
assert sum(x['payload']['allocatedPayloadBytes'] for x in runs)<=65536
assert sum(x['payload']['nativeRequestedPayloadBytes'] for x in runs)<=65536
summary={'status':'CODER_NONMEDIA_SOURCE_AND_PRODUCTION_CHECKS_COMPLETE_NOT_INDEPENDENT_VERDICT','runs':runs,'groupsPerPath':29,'totalExecutedGroups':58,'wholeElapsedSeconds':time.monotonic()-start,'wholeWindowSeconds':60,'perGroupObservationSecondsMax':5,'allOriginalProcessesReturned':True,'allStartedControlledWorkersJoined':True,'physicalPayloadBudgetBytes':65536,'physicalPayloadMeaning':'Memory-port byte arrays/input byte payload and cumulative native request bytes. Compiler/JAR/class-load diagnostic logs are separate build/control metadata, not synthetic media/native payload. All raw logs retained.','combinedAllocatedPayloadBytes':sum(x['payload']['allocatedPayloadBytes'] for x in runs),'combinedNativeRequestedPayloadBytes':sum(x['payload']['nativeRequestedPayloadBytes'] for x in runs),'generationMainJobEncoderMuxerOrMediaCalls':0,'oldSessionQueriesOrInterventions':0,'testPorts':['FixtureToolFixCheck.MemoryPort implements actual JDK SeekableByteChannel and production NativePort','TestOwner original worker/callback only','Gate entered/release with2s bounded wait and finally release+same original join','AtomicLong clock parameter for WorkerDeadline, not reflection/global clock replacement'],'expectedMemoryCloseUnknown':'One deliberate controlled close-throw per path, retained as memory-object UNKNOWN with no OS FD. Not false platform close evidence. All actual test worker/VM processes return normally; no permanent held gate.','priorP2Status':'Coder fixes/exercises only; independent closure PENDING'}
dump(D/'summary.json',summary);assert all(sha(B/x['path'])==x['sha256'] for x in pins)
print('BATCH_COMPLETE;no generation;old UNKNOWN unchanged',flush=True)
