from pathlib import Path
import json,hashlib,subprocess,datetime,os,re
B=Path(__file__).resolve().parents[1];E=B/'evidence';R=B.parents[2];D=E/'metadata-001';D.mkdir(exist_ok=False)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
assert not (E/'observation01-freeze.json').exists()
build=json.loads((E/'build-result.json').read_text());assert build['status']=='BUILT_AUDIT_FORK_ONLY'
base=R/'docs/coder/d1fixture-tool02/artifacts/videokit-fixture-tool02.jar';fork=B/'artifacts/jcodec-0.2.5-videokit-observation01.jar'
assert sha(base)=='c4ed36f31cab8381bc47c0aea4c3f3d8a9c2afab09991a04a83102877f1bfecd' and sha(fork)=='1a7e8601be4ebb5665219f2ccfa6e75476323e7408a6b18824ecf2a37873de86'
pins=json.loads((E/'compile-source-pins.json').read_text());assert all(sha(B/x['path'])==x['sha256'] for x in pins)
argv=['D:/Android/Android Studio/jbr/bin/java.exe','-Xmx256m','-XX:-UsePerfData','-Xlog:class+load=info:file=class-load.log:uptime,level,tags','-cp',str(B/'build-output/test-classes'),'com.videokit.observation.MetadataObservationCheck']
env=os.environ.copy();cleared=[]
for k in ['JAVA_TOOL_OPTIONS','JDK_JAVA_OPTIONS','_JAVA_OPTIONS','JDK_JAVAC_OPTIONS','CLASSPATH']:
 if k in env:env.pop(k);cleared.append(k)
(D/'temp').mkdir();env['TMP']=str(D/'temp');env['TEMP']=str(D/'temp')
owner={'argv':argv,'cwd':str(D),'registeredBeforePopen':True,'heapBytes':268435456,'processInvocations':1,'outerObservationSeconds':5,'originalProcessReturned':False,'outputHandlesClosed':False,'unknownSticky':False,'killInterruptRetry':0,'clearedInjectionKeys':cleared,'baseJarSha256':sha(base),'forkJarSha256':sha(fork),'testSourcePinsSha256':sha(E/'compile-source-pins.json'),'loaderMechanism':'Two file-only URLClassLoaders with platform parent; invoke public constructors/factory/parse/getters only. No reflection field writes or setAccessible.'}
dump(D/'owner.json',owner);out=(D/'stdout.raw').open('xb');err=(D/'stderr.raw').open('xb');p=None
try:
 owner['startUtc']=datetime.datetime.now(datetime.timezone.utc).isoformat();p=subprocess.Popen(argv,cwd=D,env=env,stdin=subprocess.DEVNULL,stdout=out,stderr=err,shell=False);owner['pid']=p.pid;dump(D/'owner.json',owner)
 try:code=p.wait(timeout=5)
 except subprocess.TimeoutExpired:owner['unknownSticky']=True;owner['state']='UNKNOWN_SAME_ORIGINAL_RETAINED_NO_RETRY';dump(D/'owner.json',owner);code=p.wait()
 owner['exitCode']=code;owner['originalProcessReturned']=True;owner['endUtc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
finally:
 if p is None or owner['originalProcessReturned']:out.close();err.close();owner['outputHandlesClosed']=True
 dump(D/'owner.json',owner)
assert owner['exitCode']==0 and not owner['unknownSticky'],'METADATA_TEST_FAILED_NO_REPLAY'
raw=(D/'stdout.raw').read_bytes();stderr=(D/'stderr.raw').read_bytes();assert len(raw)+len(stderr)<1048576
rows=[json.loads(x) for x in raw.decode('utf-8').splitlines()];summary=rows[-1];cases=[x for x in rows if x.get('result')=='PASS_NONMEDIA_METADATA'];assert summary['status']=='METADATA_PARSE_CHECKS_COMPLETE_NOT_MEDIA_QUALIFICATION' and len(cases)==summary['cases'] and summary['sameOriginalWorkerJoined'] and summary['originalUrlLoadersClosed'] and summary['bodyElapsedNanos']<5000000000
assert summary['explicitBytePayload']+summary['matureHeaderScratchAllowance']<=8192
origins=rows[0];assert '/d1fixture-tool02/artifacts/videokit-fixture-tool02.jar' in origins['baseline'] and '/d1jcodec-observation01/artifacts/jcodec-0.2.5-videokit-observation01.jar' in origins['fork']
loaded=(D/'class-load.log').read_text();classes=re.findall(r'\[class,load\]\s+(\S+)',loaded)
assert not any(('MP4Demuxer' in x or 'MP4Muxer' in x or 'SixFrameDriver' in x or x.endswith('Encoder') or x.endswith('Decoder')) for x in classes)
required=['org.jcodec.containers.mp4.boxes.DataRefBox','org.jcodec.containers.mp4.boxes.SampleDescriptionBox','org.jcodec.codecs.h264.mp4.AvcCBox','org.jcodec.containers.mp4.boxes.AliasBox','org.jcodec.containers.mp4.boxes.UrlBox']
for x in required:assert classes.count(x)==2,(x,classes.count(x))
assert sha(base)==owner['baseJarSha256'] and sha(fork)==owner['forkJarSha256'] and all(sha(B/x['path'])==x['sha256'] for x in pins)
dump(E/'metadata-results.json',{'status':'CODER_METADATA_DIFFERENTIAL_COMPLETE_NOT_INDEPENDENT_REVIEW_OR_MEDIA_QUALIFICATION','owner':owner,'origins':origins,'summary':summary,'cases':cases,'allOriginalRawRows':len(rows),'rawStdoutBytes':len(raw),'rawStderrBytes':len(stderr),'loadedExpectedTypesTwice':required,'noMediaCodecDemuxMuxerDriverTypesLoaded':True,'reflectionStateMutation':False,'actualMp4Reads':0,'newEncoderOrMediaRuns':0,'oldSessionActions':0})
print(json.dumps({'status':summary['status'],'cases':len(cases),'payloadBytes':summary['explicitBytePayload'],'matureScratchAllowance':summary['matureHeaderScratchAllowance'],'bodyNanos':summary['bodyElapsedNanos'],'oldAndForkOrigins':origins,'stdoutBytes':len(raw),'stderrBytes':len(stderr),'naturalExitCode':owner['exitCode'],'actualMediaReads':0},indent=2))
