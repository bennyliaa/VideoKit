from pathlib import Path
import json,subprocess,hashlib,datetime,time,os,re
R=Path('D:/CodexProjects/VideoKit');E=Path(__file__).resolve().parent;B=R/'docs/coder/d1fixture-tool02';J=Path('D:/Android/Android Studio/jbr/bin');C=E/'independent-helper-classes';C.mkdir(exist_ok=False);EMPTY=E/'empty-source-and-processors';EMPTY.mkdir(exist_ok=False)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf8')
assert json.loads((E/'independent-material-audit.json').read_text())['result']=='PASS_STATIC_ADMISSION_AND_PRODUCTION_TEST_SPLIT_BEFORE_OWN_HELPER'
start=time.monotonic();env=os.environ.copy()
for k in ['JAVA_TOOL_OPTIONS','JDK_JAVA_OPTIONS','_JAVA_OPTIONS','JDK_JAVAC_OPTIONS','CLASSPATH']:env.pop(k,None)
runs=[]
def run(name,argv):
 W=E/name;W.mkdir(exist_ok=False);T=W/'temp';T.mkdir();env['TEMP']=str(T);env['TMP']=str(T)
 remaining=60-(time.monotonic()-start);assert remaining>0
 owner=dict(argv=argv,cwd=str(W),registeredBeforePopen=True,startUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),sourceHash=sha(E/'IndependentFix02Check.java'),productionJarSha256=sha(B/'artifacts/videokit-fixture-tool02.jar'),timedOutSticky=False,originalProcessReturned=False,outputHandlesClosed=False,terminationInterruptRetryActions=0)
 save(W/'owner.json',owner);out=(W/'stdout').open('xb');err=(W/'stderr').open('xb');proc=None
 try:
  proc=subprocess.Popen(argv,cwd=W,env=env,stdout=out,stderr=err,stdin=subprocess.DEVNULL,shell=False);owner['pid']=proc.pid;save(W/'owner.json',owner)
  try:code=proc.wait(timeout=remaining)
  except subprocess.TimeoutExpired:owner['timedOutSticky']=True;save(W/'owner.json',owner);code=proc.wait()
  owner.update(exitCode=code,originalProcessReturned=True,endUtc=datetime.datetime.now(datetime.timezone.utc).isoformat())
 finally:
  if proc is None or owner['originalProcessReturned']:out.close();err.close();owner['outputHandlesClosed']=True
  save(W/'owner.json',owner)
 runs.append(owner);print(name,'exit',owner.get('exitCode'),flush=True);assert owner.get('exitCode')==0 and not owner['timedOutSticky'],(name,(W/'stderr').read_text(errors='replace'))
 return W,owner
run('helper-compile',[str(J/'javac.exe'),'-J-Xmx256m','-J-XX:-UsePerfData','--release','11','-encoding','UTF-8','-proc:none','-implicit:none','-sourcepath',str(EMPTY),'-processorpath',str(EMPTY),'-classpath',str(B/'build-output/production-classes'),'-d',str(C),str(E/'IndependentFix02Check.java')])
source=str(C)+';'+str(B/'build-output/classes');prod=str(B/'artifacts/videokit-fixture-tool02.jar')+';'+str(C)
payload=[]
for mode,cp in [('source',source),('production',prod)]:
 W,owner=run('own-'+mode,[str(J/'java.exe'),'-Xmx256m','-XX:-UsePerfData','-Xlog:class+load=info:file=loaded-classes.log:uptime,level,tags','-cp',cp,'com.videokit.fixturetool.IndependentFix02Check'])
 text=(W/'stdout').read_text();assert text.count('PASS independent02 ')==17
 line=next(x for x in text.splitlines() if x.startswith('DONE '));numbers={k:int(v) for k,v in re.findall(r'(allocatedPayloadBytes|nativeRequestedPayloadBytes|controlledReturnedOrPhysicalBytes|startedOriginalWorkers|joinedOriginalWorkers|retainedMemoryUnknown)=(\d+)',line)}
 assert numbers['startedOriginalWorkers']==numbers['joinedOriginalWorkers']==16 and numbers['allocatedPayloadBytes']<=4096 and numbers['nativeRequestedPayloadBytes']<=8192
 loaded=(W/'loaded-classes.log').read_text();classes=re.findall(r'\[class,load\]\s+(\S+)',loaded);assert not any(x.startswith(('com.videokit.fixturetool.SixFrameDriver','org.jcodec.codecs.','org.jcodec.containers.')) for x in classes)
 assert sorted({x for x in classes if x.startswith('org.jcodec.')})==['org.jcodec.common.io.SeekableByteChannel']
 origin=text.splitlines()[0];assert ('artifacts/videokit-fixture-tool02.jar' if mode=='production' else 'build-output/classes/') in origin
 owner.update(groups=17,payload=numbers,origin=origin,onlyJcodecInterfaceLoaded=True);save(W/'owner.json',owner);payload.append(numbers)
earlier=json.loads((E/'checks-001/summary.json').read_text());allocation=earlier['combinedAllocatedPayloadBytes']+sum(x['allocatedPayloadBytes'] for x in payload);requests=earlier['combinedNativeRequestedPayloadBytes']+sum(x['nativeRequestedPayloadBytes'] for x in payload);assert allocation<=65536 and requests<=65536
save(E/'own-helper-summary.json',dict(result='PASS_INDEPENDENT17_SOURCE_AND_PRODUCTION_NONMEDIA_ONLY',runs=runs,groupsPerPath=17,allStartedWorkersActuallyJoined=True,combinedOwnPayload=payload,combinedDocumentedAndOwnAllocatedPayloadBytes=allocation,combinedDocumentedAndOwnNativeRequestBytes=requests,wholeOwnCompileAndRunSeconds=time.monotonic()-start,expectedMemoryOnlyCloseUnknownPerPath=1,newFindings=0,MainJobEncoderMuxerMediaOrFileChannelCalls=0,oldSessionQueriesOrInterventions=0))
print('OWN_FIXED_NONMEDIA_BATCH_COMPLETE groups17each allOriginalWorkersJoined combinedAllocated',allocation,'combinedRequested',requests,flush=True)
