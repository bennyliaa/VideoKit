from pathlib import Path
import json,hashlib,os,subprocess,time,datetime,re,ast,struct
R=Path('D:/CodexProjects/VideoKit');E=Path(__file__).resolve().parent;B=R/'docs/coder/d1jcodec-observation01';OLD=R/'docs/coder/d1fixture-tool02';J=Path('D:/Android/Android Studio/jbr/bin')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf8')
assert not (E/'own-compile-001').exists(),'ONE_COMPILE_GUARD_NO_REPLAY'
assert load(E/'independent-material-audit.json')['result']=='PASS_STATIC_MATERIALS_ORIGINAL_CODER_HELPER_FAILURE_PRESERVED'
assert sha(B/'evidence/observation01-freeze.json')=='8a62ef8e4fcea016870daccfe92097903cde667e4d624892309e6984d44e0725'
for row in load(B/'evidence/observation01-freeze.json')['files']:
 p=R/row['path'];assert p.stat().st_size==row['bytes'] and sha(p)==row['sha256']
for row in load(B/'evidence/compiler-identity.json'):
 p=Path(row['path']);assert p.stat().st_size==row['bytes'] and sha(p)==row['sha256']
base=OLD/'artifacts/videokit-fixture-tool02.jar';fork=B/'artifacts/jcodec-0.2.5-videokit-observation01.jar';assert sha(base)=='c4ed36f31cab8381bc47c0aea4c3f3d8a9c2afab09991a04a83102877f1bfecd' and sha(fork)=='1a7e8601be4ebb5665219f2ccfa6e75476323e7408a6b18824ecf2a37873de86'
source=E/'IndependentObservationCheck.java';assert sha(source)==load(E/'own-helper-source-provenance.json')['newSha256']
classes=E/'own-helper-classes';classes.mkdir(exist_ok=False);empty=E/'empty-source-classpath-processors';empty.mkdir(exist_ok=False)
env=os.environ.copy();keys=['JAVA_TOOL_OPTIONS','JDK_JAVA_OPTIONS','_JAVA_OPTIONS','JDK_JAVAC_OPTIONS','CLASSPATH']
for k in keys:env.pop(k,None)
runs=[]
def run(name,argv,seconds):
 D=E/name;D.mkdir(exist_ok=False);temp=D/'temp';temp.mkdir();env['TEMP']=str(temp);env['TMP']=str(temp)
 o=dict(registeredBeforePopen=True,argv=argv,cwd=str(D),startUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),environmentCleared={k:k not in env for k in keys},temp=str(temp),observeSeconds=seconds,originalProcessReturned=False,stdoutHandleClosed=False,stderrHandleClosed=False,unknownSticky=False,killInterruptRetrySecondCloseActions=0)
 save(D/'owner.json',o);out=(D/'stdout.raw').open('xb');err=(D/'stderr.raw').open('xb');proc=None;start=time.monotonic()
 try:
  proc=subprocess.Popen(argv,cwd=D,env=env,stdout=out,stderr=err,stdin=subprocess.DEVNULL,shell=False);o['pid']=proc.pid;save(D/'owner.json',o)
  try:code=proc.wait(timeout=seconds)
  except subprocess.TimeoutExpired:o['unknownSticky']=True;save(D/'owner.json',o);print('UNKNOWN same original retained, no successor/kill/retry',flush=True);code=proc.wait()
  o.update(originalProcessReturned=True,exitCode=code,endUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),elapsedSeconds=time.monotonic()-start)
 finally:
  if proc is None or o['originalProcessReturned']:out.close();err.close();o.update(stdoutHandleClosed=True,stderrHandleClosed=True)
  save(D/'owner.json',o)
 runs.append(o);print(name,'natural exit',o.get('exitCode'),flush=True)
 if o.get('exitCode')!=0 or o['unknownSticky']:
  save(E/'own-first-failure-no-retry.json',dict(result='FIRST_HELPER_COMPILE_OR_METADATA_FAILURE_NO_RETRY',runs=runs,rawStdout=str(D/'stdout.raw'),rawStderr=str(D/'stderr.raw')));raise SystemExit(1)
 return D,o
D,compiler=run('own-compile-001',[str(J/'javac.exe'),'-J-Xmx512m','-J-XX:-UsePerfData','--release','11','-encoding','UTF-8','-proc:none','-implicit:none','-classpath',str(empty),'-sourcepath',str(empty),'-processorpath',str(empty),'-d',str(classes),str(source)],60)
tree=ast.parse((R/'docs/tester/D1_FIXTURE_TOOL01_BUILD_REVIEW_EVIDENCE/independent_static_audit.py').read_text());fs=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='classInfo'];exec(compile(ast.Module(body=fs,type_ignores=[]),'static_class_parser','exec'))
compiled=[]
for p in sorted(classes.rglob('*.class')):
 ci=classInfo(p.read_bytes());assert ci['major']==55 and ci['sourceFile']=='IndependentObservationCheck.java' and ci['className'].startswith('com/videokit/testerobs/IndependentObservationCheck');compiled.append(dict(path=str(p),bytes=p.stat().st_size,sha256=sha(p),classInfo=ci))
assert len(compiled)==3;save(E/'own-compile-identities.json',dict(sourceSha256=sha(source),compiler=compiler,actualClasses=compiled,productionLibraryCompileCalls=0))
assert sum(p.stat().st_size for p in E.rglob('*') if p.is_file())<16777216
D,owner=run('own-metadata-001',[str(J/'java.exe'),'-Xmx256m','-XX:-UsePerfData','-Xlog:class+load=info:file=loaded-classes.log:uptime,level,tags','-cp',str(classes),'com.videokit.testerobs.IndependentObservationCheck'],5)
stdout=(D/'stdout.raw').read_bytes();stderr=(D/'stderr.raw').read_bytes();assert len(stdout)+len(stderr)<=1048576 and stderr==b'';lines=[json.loads(x) for x in stdout.decode('utf8',errors='strict').splitlines()]
cases=[x for x in lines if 'case' in x];origins=[x for x in lines if 'classOrigins' in x];summary=lines[-1]
assert len(cases)==len({x['case'] for x in cases})==79 and all(x['result']=='PASS_NONMEDIA_METADATA' for x in cases)
assert len(origins)==3 and {x['classOrigins'] for x in origins}=={'dref','stsd','avcC'} and all(x['baseline']!=x['fork'] for x in origins)
assert summary['status']=='INDEPENDENT_METADATA_PARSE_COMPLETE_NOT_MEDIA_QUALIFICATION' and summary['cases']==79 and summary['sameOriginalWorkerJoined'] and summary['workerBodyComplete'] and not summary['unknownSticky'] and summary['twoOriginalLoadersCloseReturned'] and summary['bodyElapsedNanos']<5000000000
assert summary['explicitBytePayload']+summary['matureHeaderScratchAllowance']<=8192 and summary['mediaReads']==summary['encoderDecoderDemuxMuxerMainRuns']==0
assert len(summary['originalLoaderOwners'])==2 and all(x['registeredBeforeLoaderAllocation'] and x['openReturned'] and x['closeEntered'] and x['sameOriginalCloseReturned'] and x['sameOriginalWorkerCloser'] for x in summary['originalLoaderOwners'])
loaded=(D/'loaded-classes.log').read_text();names=re.findall(r'\[class,load\]\s+(\S+)',loaded)
for name in names:
 assert not name.startswith(('com.videokit.fixturetool.SixFrameDriver','org.jcodec.containers.mp4.demuxer.','org.jcodec.containers.mp4.muxer.'))
 if name.startswith(('org.jcodec.','net.sourceforge.jaad.')):assert not re.search(r'(?:Encoder|Decoder)(?:\$|$)',name),name
assert 'org.jcodec.codecs.h264.mp4.AvcCBox' in names
for row in load(B/'evidence/observation01-freeze.json')['files']:
 p=R/row['path'];assert p.stat().st_size==row['bytes'] and sha(p)==row['sha256']
assert sha(source)==load(E/'own-helper-source-provenance.json')['newSha256']
for p in [base,fork]:assert sha(p)==('c4ed36f31cab8381bc47c0aea4c3f3d8a9c2afab09991a04a83102877f1bfecd' if p==base else '1a7e8601be4ebb5665219f2ccfa6e75476323e7408a6b18824ecf2a37873de86')
save(E/'independent-metadata-results.json',dict(result='PASS_LIMITED_INDEPENDENT_METADATA_ORIGINAL_OBSERVABILITY_NOT_MEDIA',cases=cases,classOrigins=origins,summary=summary,originalCompilerOwner=compiler,originalMetadataProcessOwner=owner,rawStdoutBytes=len(stdout),rawStderrBytes=len(stderr),classLoadAudit=dict(forbiddenJcodecOrJaadMediaCodecClassesLoaded=False,jdkCharsetClassesExcludedFromMediaFilter=True,jdkCharsetClassNames=sorted({n for n in names if n.startswith(('sun.nio.cs.','java.nio.charset.'))}),loadedJcodecClassNames=sorted({n for n in names if n.startswith('org.jcodec.')})),postReturnFrozen2738RowsUnchanged=True,mediaReads=0,actualMediaQualification='NOT_RUN',checkerIntegration='NOT_RUN',oldSessionsTouched=False,newProductionFindings=0))
assert sum(p.stat().st_size for p in E.rglob('*') if p.is_file())<16777216
print('PASS independent79 metadata; payload',summary['explicitBytePayload'],'+scratch',summary['matureHeaderScratchAllowance'],'original worker2loader/process returned; no media',flush=True)
