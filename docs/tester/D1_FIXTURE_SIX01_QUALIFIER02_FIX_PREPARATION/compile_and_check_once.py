from pathlib import Path
import json,hashlib,subprocess,os,time,datetime,ast,struct,shutil,re
R=Path('D:/CodexProjects/VideoKit');E=Path(__file__).resolve().parent;P=R/'docs/tester/D1_FIXTURE_SIX01_QUALIFIER_PREPARATION';T=R/'docs/coder/d1fixture-tool02';J=Path('D:/Android/Android Studio/jbr/bin')
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(65536),b''):h.update(b)
 return h.hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf8')
assert not (E/'compile-001').exists(),'ONE_COMPILE_ONLY_NO_REPLAY'
baselines=[]
for path,expected in [(P/'review-evidence-manifest.json','6c570d2ac81c20f3bebf28d141c92edf85a153ccecfe7462e367ea8f011d412f'),(R/'docs/tester/D1_FIXTURE_SIX01_CONTAINER_QUALIFICATION/review-evidence-manifest.json','599837c166d723f458d170414e42f0d3b886b0a9b326a2a1ca24779eaca4d376')]:
 assert sha(path)==expected;v=load(path);assert sha(R/v['report'])==v['reportSha256']
 for x in v['evidenceFiles']:
  q=R/x['path'];assert q.stat().st_size==x['bytes'] and sha(q)==x['sha256']
 baselines.append(dict(manifest=str(path),sha256=expected,unchangedEvidenceFiles=len(v['evidenceFiles'])))
seal=T/'evidence/fixture-tool02-freeze.json';assert sha(seal)=='5dbf3359e0aa9b06a9024cf0ace91bd1e532ddbfdc37ba11d81f0716c01dc51d';v=load(seal)
for x in v['files']:q=R/x['path'];assert q.stat().st_size==x['bytes'] and sha(q)==x['sha256']
assert len(v['files'])==2774
contract=load(P/'future-execution-contract.json')
for x in contract['javaIdentity']+[contract['jarIdentity'],contract['helperSource']]+contract['classIdentities']:
 q=Path(x['path']);assert q.stat().st_size==x['bytes'] and sha(q)==x['sha256']
req=R/'docs/milestones/D1_FIXTURE_SIX01_QUALIFIER02_FIX_TESTER_REQUIREMENTS_V1.0.md';(E/'authorized-requirements-snapshot.md').write_bytes(req.read_bytes())
jar=T/'artifacts/videokit-fixture-tool02.jar';C=E/'all-compiled-classes';C.mkdir(exist_ok=False);PROD=E/'helper-classes';PROD.mkdir(exist_ok=False);TEST=E/'test-only-classes';TEST.mkdir(exist_ok=False);EMPTY=E/'empty-source-and-processors';EMPTY.mkdir(exist_ok=False)
sources=[E/x for x in ['Six01ContainerQualifier02.java','DataReferencePolicy.java','DataReferenceSemanticCheck.java']]
env=os.environ.copy();keys=['JAVA_TOOL_OPTIONS','JDK_JAVA_OPTIONS','_JAVA_OPTIONS','JDK_JAVAC_OPTIONS','CLASSPATH']
for k in keys:env.pop(k,None)
runs=[]
def run(name,argv,seconds):
 D=E/name;D.mkdir(exist_ok=False);temp=D/'temp';temp.mkdir();env['TEMP']=str(temp);env['TMP']=str(temp)
 o=dict(registeredBeforePopen=True,argv=argv,cwd=str(D),startUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),environmentCleared={k:k not in env for k in keys},temp=str(temp),observationSeconds=seconds,originalProcessReturned=False,stdoutHandleClosed=False,stderrHandleClosed=False,unknownSticky=False,killInterruptSecondCloseRetryActions=0)
 save(D/'owner.json',o);out=(D/'stdout.raw').open('xb');err=(D/'stderr.raw').open('xb');proc=None;start=time.monotonic()
 try:
  proc=subprocess.Popen(argv,cwd=D,env=env,stdout=out,stderr=err,stdin=subprocess.DEVNULL,shell=False);o['pid']=proc.pid;save(D/'owner.json',o)
  try:code=proc.wait(timeout=seconds)
  except subprocess.TimeoutExpired:
   o['unknownSticky']=True;save(D/'owner.json',o);print('UNKNOWN original '+name+' retained; no successor/retry',flush=True);code=proc.wait()
  o.update(originalProcessReturned=True,exitCode=code,endUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),elapsedSeconds=time.monotonic()-start)
 finally:
  if proc is None or o['originalProcessReturned']:out.close();err.close();o.update(stdoutHandleClosed=True,stderrHandleClosed=True)
  save(D/'owner.json',o)
 runs.append(o);print(name,'natural exit',o.get('exitCode'),flush=True)
 if o.get('exitCode')!=0 or o['unknownSticky']:
  save(E/'first-failure-no-retry.json',dict(status='FIRST_COMPILE_OR_SEMANTIC_FAILURE_OR_UNKNOWN_NO_RETRY',runs=runs));raise SystemExit(1)
 return D,o
compileDir,compiler=run('compile-001',[str(J/'javac.exe'),'-J-Xmx512m','-J-XX:-UsePerfData','--release','11','-encoding','UTF-8','-proc:none','-implicit:none','-sourcepath',str(EMPTY),'-processorpath',str(EMPTY),'-classpath',str(jar),'-d',str(C)]+[str(p) for p in sources],60)
tree=ast.parse((R/'docs/tester/D1_FIXTURE_TOOL01_BUILD_REVIEW_EVIDENCE/independent_static_audit.py').read_text());fs=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='classInfo'];exec(compile(ast.Module(body=fs,type_ignores=[]),'static_class_identity_only','exec'))
classes=[]
for p in sorted(C.rglob('*.class')):
 b=p.read_bytes();ci=classInfo(b);assert ci['major']==55 and ci['sourceFile'] in [x.name for x in sources]
 test=ci['sourceFile']=='DataReferenceSemanticCheck.java';dest=(TEST if test else PROD)/p.relative_to(C);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dest);assert sha(dest)==sha(p)
 classes.append(dict(path=str(dest),bytes=dest.stat().st_size,sha256=sha(dest),originalCompilerOutput=str(p),sourceFile=ci['sourceFile'],classInfo=ci,testOnly=test))
assert len(classes)==5 and sum(x['testOnly'] for x in classes)==1
save(E/'compile-class-identities.json',dict(compiler=compiler,classes=classes,productionClasses=4,testOnlyClasses=1,sources=[dict(path=str(p),bytes=p.stat().st_size,sha256=sha(p)) for p in sources],jar=contract['jarIdentity'],javaIdentity=contract['javaIdentity'],matureLibraryRebuilt=False,mediaReads=0,baselines=baselines))
assert sum(p.stat().st_size for p in E.rglob('*') if p.is_file())<=16777216
D,semantic=run('semantics-001',[str(J/'java.exe'),'-Xmx256m','-XX:-UsePerfData','-Xlog:class+load=info:file=loaded-classes.log:uptime,level,tags','-cp',str(TEST)+';'+str(PROD)+';'+str(jar),'com.videokit.fixturetool.DataReferenceSemanticCheck'],5)
raw=(D/'stdout.raw').read_bytes();err=(D/'stderr.raw').read_bytes();assert len(raw)+len(err)<=1048576 and err==b'';lines=[json.loads(x) for x in raw.decode('utf8',errors='strict').splitlines()]
assert len(lines)==27 and len({x['case'] for x in lines[:-1]})==26
summary=lines[-1];assert summary['summary']=='QUALIFIER02_NONMEDIA_SEMANTICS' and summary['checks']==26 and summary['allocatedExplicitPayloadBytes']==132 and summary['actualOriginalWorkerJoined'] and summary['bodyReturned'] and not summary['unknownSticky'] and summary['elapsedNanos']<5000000000 and summary['mediaReads']==summary['helperRuntimeCalls']==0
loaded=(D/'loaded-classes.log').read_text();names=re.findall(r'\[class,load\]\s+(\S+)',loaded)
assert not any(n.startswith(('com.videokit.fixturetool.Six01ContainerQualifier','com.videokit.fixturetool.SixFrameDriver','org.jcodec.containers.mp4.demuxer.','org.jcodec.containers.mp4.muxer.','org.jcodec.codecs.h264.H264Encoder','org.jcodec.codecs.h264.H264Decoder')) for n in names)
assert 'org.jcodec.containers.mp4.boxes.AliasBox' in names and 'org.jcodec.containers.mp4.boxes.UrlBox' in names and 'com.videokit.fixturetool.DataReferencePolicy' in names
assert sum(x['result']=='PASS_ACCEPT_CHILD_SEMANTICS_ONLY' for x in lines[:-1])==4 and sum(x['result']=='PASS_REJECT' for x in lines[:-1])==20 and sum(x['result']=='PASS_MANDATORY_WHOLE_QUALIFICATION_BLOCKED' for x in lines[:-1])==2
for x in contract['javaIdentity']+[contract['jarIdentity'],contract['helperSource']]+contract['classIdentities']:
 p=Path(x['path']);assert p.stat().st_size==x['bytes'] and sha(p)==x['sha256']
save(E/'semantic-results.json',dict(result='PASS_LIMITED_CHILD_SEMANTICS_WHOLE_DREF_METADATA_BLOCKED',cases=lines[:-1],summary=summary,compiler=compiler,semanticProcess=semantic,rawStdoutBytes=len(raw),rawStderrBytes=len(err),classLoadAudit=dict(qualifierMainEncoderDecoderDemuxMuxerLoaded=False,loadedJcodecClasses=sorted({x for x in names if x.startswith('org.jcodec.')})),explicitPayloadAllocated=132,additionalMatureFourccArraysBoundedByStaticSource=64,conservativePayloadTotalMax=4096,actualContainerQualification='NOT_RUN_AND_MANDATORY_METADATA_BLOCKED',mediaReads=0,oldSessionsTouched=False,compileCalls=1,semanticJvms=1,actualQualificationHelperJvms=0))
print('PASS limited semantic26:4acceptChild20reject2wholeBlocked; explicitPayload132; no helper/media runtime; overallContainerBLOCKED',flush=True)
