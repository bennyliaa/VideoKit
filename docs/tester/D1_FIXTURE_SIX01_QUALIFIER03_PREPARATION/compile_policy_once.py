from pathlib import Path
import json,hashlib,zipfile,subprocess,os,time,datetime,ast,struct,shutil,re
R=Path('D:/CodexProjects/VideoKit');E=Path(__file__).resolve().parent;B=R/'docs/coder/d1jcodec-observation01';OLD=R/'docs/coder/d1fixture-tool02';J=Path('D:/Android/Android Studio/jbr/bin')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf8')
assert not (E/'compile-001').exists(),'ONE_COMPILE_PHYSICAL_GUARD_NO_REPLAY'
prior=R/'docs/tester/D1_JCODEC_OBSERVATION01_REVIEW_EVIDENCE/review-evidence-manifest.json';assert sha(prior)=='5b5cc931033076c80c85c92e9b0dfac70b6ff709b14aec5590c87cc308d763fe';v=load(prior);assert sha(R/v['report'])=='6b71997ce6ad6136cdea7f7908e102bc460e6933b7c288e78657c6fb5cbbf59b'
for x in v['evidenceFiles']:p=R/x['path'];assert p.stat().st_size==x['bytes'] and sha(p)==x['sha256']
assert sha(B/'evidence/observation01-freeze.json')=='8a62ef8e4fcea016870daccfe92097903cde667e4d624892309e6984d44e0725'
for x in load(B/'evidence/observation01-freeze.json')['files']:p=R/x['path'];assert p.stat().st_size==x['bytes'] and sha(p)==x['sha256']
for x in load(B/'evidence/compiler-identity.json'):p=Path(x['path']);assert p.stat().st_size==x['bytes'] and sha(p)==x['sha256']
fork=B/'artifacts/jcodec-0.2.5-videokit-observation01.jar';assert fork.stat().st_size==1930955 and sha(fork)=='1a7e8601be4ebb5665219f2ccfa6e75476323e7408a6b18824ecf2a37873de86'
support=load(E/'support-and-source-provenance.json')['supportExactClassSet'];assert len(support)==2 and {p.resolve() for p in (E/'support').rglob('*') if p.is_file()}=={Path(x['path']).resolve() for x in support}
assert sha(OLD/'evidence/fixture-tool02-freeze.json')=='5dbf3359e0aa9b06a9024cf0ace91bd1e532ddbfdc37ba11d81f0716c01dc51d'
oldrows={x['path']:x for x in load(OLD/'evidence/fixture-tool02-freeze.json')['files']};origins={x['jarEntry']:x for x in load(OLD/'evidence/class-origin02.json')}
for x in support:
 p=Path(x['path']);src=Path(x['sourcePath']);row=origins[x['jarEntry']];assert sha(p)==x['sha256']==row['sha256'] and sha(src)==x['sourceSha256']==row['sourceSha256']==oldrows[src.relative_to(R).as_posix()]['sha256']
req=R/'docs/milestones/D1_FIXTURE_SIX01_QUALIFIER03_PREPARATION_TESTER_REQUIREMENTS_V1.0.md';(E/'authorized-requirements-snapshot.md').write_bytes(req.read_bytes())
sources=[E/n for n in ['Six01ContainerQualifier03.java','DataReferencePolicy03.java','MetadataPolicy03.java','OriginFence03.java','Qualifier03PolicyCheck.java','Qualifier03PolicyLauncher.java']]
sourcepins=[dict(path=str(p),bytes=p.stat().st_size,sha256=sha(p)) for p in sources]
C=E/'all-compiled-classes';C.mkdir(exist_ok=False);H=E/'helper-classes';H.mkdir(exist_ok=False);TEST=E/'test-only-classes';TEST.mkdir(exist_ok=False);LAUNCH=E/'launcher-classes';LAUNCH.mkdir(exist_ok=False);EMPTY=E/'empty-source-processors';EMPTY.mkdir(exist_ok=False)
env=os.environ.copy();keys=['JAVA_TOOL_OPTIONS','JDK_JAVA_OPTIONS','_JAVA_OPTIONS','JDK_JAVAC_OPTIONS','CLASSPATH']
for k in keys:env.pop(k,None)
runs=[]
def run(name,argv,seconds):
 D=E/name;D.mkdir(exist_ok=False);temp=D/'temp';temp.mkdir();env['TEMP']=str(temp);env['TMP']=str(temp)
 o=dict(registeredBeforePopen=True,argv=argv,cwd=str(D),startUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),environmentInjectionKeysCleared={k:k not in env for k in keys},temp=str(temp),observeSeconds=seconds,originalProcessReturned=False,stdoutHandleClosed=False,stderrHandleClosed=False,unknownSticky=False,killInterruptSecondCloseRetryActions=0)
 save(D/'owner.json',o);out=(D/'stdout.raw').open('xb');err=(D/'stderr.raw').open('xb');proc=None;start=time.monotonic()
 try:
  proc=subprocess.Popen(argv,cwd=D,env=env,stdout=out,stderr=err,stdin=subprocess.DEVNULL,shell=False);o['pid']=proc.pid;save(D/'owner.json',o)
  try:code=proc.wait(timeout=seconds)
  except subprocess.TimeoutExpired:o['unknownSticky']=True;save(D/'owner.json',o);print('UNKNOWN original retained; no kill/retry/successor',flush=True);code=proc.wait()
  o.update(originalProcessReturned=True,exitCode=code,endUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),elapsedSeconds=time.monotonic()-start)
 finally:
  if proc is None or o['originalProcessReturned']:out.close();err.close();o.update(stdoutHandleClosed=True,stderrHandleClosed=True)
  save(D/'owner.json',o)
 runs.append(o);print(name,'natural exit',o.get('exitCode'),flush=True)
 if o.get('exitCode')!=0 or o['unknownSticky']:
  save(E/'first-failure-no-retry.json',dict(status='FIRST_COMPILE_OR_POLICY_FAILURE_OR_UNKNOWN_STOPPED',runs=runs));raise SystemExit(1)
 return D,o
D,compiler=run('compile-001',[str(J/'javac.exe'),'-J-Xmx512m','-J-XX:-UsePerfData','--release','11','-encoding','UTF-8','-proc:none','-implicit:none','-classpath',str(E/'support')+';'+str(fork),'-sourcepath',str(EMPTY),'-processorpath',str(EMPTY),'-d',str(C)]+[str(p) for p in sources],60)
tree=ast.parse((R/'docs/tester/D1_FIXTURE_TOOL01_BUILD_REVIEW_EVIDENCE/independent_static_audit.py').read_text());fs=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='classInfo'];exec(compile(ast.Module(body=fs,type_ignores=[]),'static_class_identity_only','exec'))
classes=[]
for p in sorted(C.rglob('*.class')):
 ci=classInfo(p.read_bytes());assert ci['major']==55 and ci['sourceFile'] in [q.name for q in sources]
 category='launcher' if ci['sourceFile']=='Qualifier03PolicyLauncher.java' else 'test' if ci['sourceFile']=='Qualifier03PolicyCheck.java' else 'helper';dest={'launcher':LAUNCH,'test':TEST,'helper':H}[category]/p.relative_to(C);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dest);assert sha(dest)==sha(p)
 classes.append(dict(path=str(dest),bytes=dest.stat().st_size,sha256=sha(dest),actualCompilerOutput=str(p),classInfo=ci,category=category))
assert len(classes)==9 and sum(x['category']=='helper' for x in classes)==6 and sum(x['category']=='test' for x in classes)==2 and sum(x['category']=='launcher' for x in classes)==1
save(E/'compile-and-class-identities.json',dict(compiler=compiler,sources=sourcepins,classes=classes,support=support,uniqueJcodecJar=dict(path=str(fork),bytes=fork.stat().st_size,sha256=sha(fork)),javaIdentity=load(B/'evidence/compiler-identity.json'),runtimeOldFullJarAllowed=False,libraryRebuilt=False))
assert sum(p.stat().st_size for p in E.rglob('*') if p.is_file())<16777216
D,process=run('policy-001',[str(J/'java.exe'),'-Xmx256m','-XX:-UsePerfData','-Xlog:class+load=info:file=loaded-classes.log:uptime,level,tags','-cp',str(LAUNCH),'com.videokit.qualifier03launcher.Qualifier03PolicyLauncher'],5)
raw=(D/'stdout.raw').read_bytes();err=(D/'stderr.raw').read_bytes();assert len(raw)+len(err)<=1048576 and err==b'';lines=[json.loads(x) for x in raw.decode('utf8',errors='strict').splitlines()];summary=lines[-1];caseRows=[x for x in lines if 'case' in x]
assert len(caseRows)==len({x['case'] for x in caseRows})==34 and sum(x['result']=='PASS_POLICY_ACCEPT' for x in caseRows)==4 and sum(x['result']=='PASS_POLICY_REJECT' for x in caseRows)==30
assert summary['status']=='QUALIFIER03_POLICY_ORIGINALS_RETURNED_NOT_MEDIA' and summary['policyCases']==34 and summary['holderRegisteredBeforeLoaderAllocation'] and summary['loaderAllocationReturned'] and summary['originalLoaderCloseEntered'] and summary['sameOriginalLoaderCloseReturned'] and summary['originalWorkerBodyReturned'] and summary['sameOriginalWorkerJoined'] and not summary['unknownSticky'] and summary['elapsedNanos']<5000000000
assert summary['failureClass'] is None and summary['explicitMetadataPayloadBytes']+summary['matureScratchAllowance']<=8192 and summary['actualQualifierInvocations']==summary['mediaReads']==0
origin=next(x['actualClassOrigins'] for x in lines if 'actualClassOrigins' in x);assert origin['forkVersion']=='0.2.5-videokit-observation01' and not origin['fullJcodecJarFallback'] and len(origin['classes'])==15
loaded=(D/'loaded-classes.log').read_text();names=re.findall(r'\[class,load\]\s+(\S+)',loaded)
assert not any(n.startswith(('com.videokit.fixturetool.Six01ContainerQualifier','com.videokit.fixturetool.SixFrameDriver','org.jcodec.containers.mp4.demuxer.','org.jcodec.containers.mp4.muxer.')) for n in names)
for line in loaded.splitlines():
 n=re.search(r'\[class,load\]\s+(\S+)',line)
 if n and n[1].startswith(('org.jcodec.','net.sourceforge.jaad.')):
  assert 'jcodec-0.2.5-videokit-observation01.jar' in line and not re.search(r'(?:Encoder|Decoder)(?:\$|$)',n[1]),line
assert 'videokit-fixture-tool02.jar' not in loaded
for x in sourcepins+support:
 p=Path(x['path']);assert p.stat().st_size==x['bytes'] and sha(p)==x['sha256']
assert sha(fork)=='1a7e8601be4ebb5665219f2ccfa6e75476323e7408a6b18824ecf2a37873de86'
save(E/'policy-results.json',dict(result='PASS_PREPARATION_LIMITED34_POLICY_MEDIA_NOT_RUN',cases=caseRows,actualCodeSourceProof=origin,summary=summary,compiler=compiler,policyProcess=process,rawStdoutBytes=len(raw),rawStderrBytes=len(err),uniqueForkJcodecOrigin=True,oldFullJarNotLoaded=True,classLoadNames=names,explicitMetadataPayloadBytes=summary['explicitMetadataPayloadBytes'],matureScratchAllowance=2048,metadataBudget=8192,qualifierRuntimeCalls=0,mediaReads=0,oldSessionsTouched=False))
print('PASS checker03 preparation34 policy cases, fork-only Jcodec/support2; no actual media or qualifier run',flush=True)
