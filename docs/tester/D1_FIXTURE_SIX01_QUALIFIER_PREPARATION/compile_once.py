from pathlib import Path
import json,hashlib,subprocess,os,time,datetime,zipfile,ast,struct
R=Path('D:/CodexProjects/VideoKit'); E=Path(__file__).resolve().parent; B=R/'docs/coder/d1fixture-tool02'; J=Path('D:/Android/Android Studio/jbr')
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for block in iter(lambda:f.read(65536),b''):h.update(block)
 return h.hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf8')
def identity(p):return dict(path=str(p),bytes=p.stat().st_size,sha256=sha(p))
assert not (E/'compile').exists(), 'ONE_COMPILE_GUARD_NO_REPLAY'
seal=B/'evidence/fixture-tool02-freeze.json'; assert sha(seal)=='5dbf3359e0aa9b06a9024cf0ace91bd1e532ddbfdc37ba11d81f0716c01dc51d'
d=load(seal)
for row in d['files']:
 p=R/row['path']; assert p.stat().st_size==row['bytes'] and sha(p)==row['sha256']
assert len(d['files'])==2774
with zipfile.ZipFile(R/d['archive']['path']) as z:
 rows={x['path']:x for x in d['files'] if x['path']!=d['archive']['path']}
 assert len(z.namelist())==len(set(z.namelist()))==2773 and set(z.namelist())==set(rows)
 for n,x in rows.items():assert hashlib.sha256(z.read(n)).hexdigest()==x['sha256']
old=R/'docs/tester/D1_FIXTURE_TOOL02_FIX_REVIEW_EVIDENCE/review-evidence-manifest.json'
assert sha(old)=='4cf38051ed21b927da639418ef9ef58629219fbe042645f46b0ccf946c900109'
prior=load(old);assert sha(R/prior['report'])=='4093db865bf0ed1419245c94a3102578835ce57ecd750da6010645a314176fb4'
for row in prior['evidenceFiles']:
 p=R/row['path'];assert p.stat().st_size==row['bytes'] and sha(p)==row['sha256']
compiler=load(B/'evidence/compiler-identity.json')
for row in compiler['files']:
 p=Path(row['path']);assert p.stat().st_size==row['bytes'] and sha(p)==row['sha256']
jar=B/'artifacts/videokit-fixture-tool02.jar';assert jar.stat().st_size==1954730 and sha(jar)=='c4ed36f31cab8381bc47c0aea4c3f3d8a9c2afab09991a04a83102877f1bfecd'
W=E/'compile';W.mkdir(exist_ok=False); C=E/'classes';C.mkdir(exist_ok=False);EMPTY=E/'empty-source-and-processors';EMPTY.mkdir(exist_ok=False);T=W/'temp';T.mkdir()
env=os.environ.copy();cleared=['JAVA_TOOL_OPTIONS','JDK_JAVA_OPTIONS','_JAVA_OPTIONS','JDK_JAVAC_OPTIONS','CLASSPATH']
for k in cleared:env.pop(k,None)
env['TEMP']=str(T);env['TMP']=str(T)
argv=[str(J/'bin/javac.exe'),'-J-Xmx512m','-J-XX:-UsePerfData','--release','11','-encoding','UTF-8','-proc:none','-implicit:none','-sourcepath',str(EMPTY),'-processorpath',str(EMPTY),'-classpath',str(jar),'-d',str(C),str(E/'Six01ContainerQualifier.java')]
owner=dict(argv=argv,cwd=str(W),registeredBeforePopen=True,startUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),source=identity(E/'Six01ContainerQualifier.java'),jar=identity(jar),compilerFiles=compiler['files'],clearedEnvironmentKeys=cleared,temporaryDirectory=str(T),compileCalls=1,helperOrMediaRuntimeCalls=0,originalProcessReturned=False,outputHandlesClosed=False,timedOutSticky=False,terminationInterruptRetryActions=0,observationSeconds=60,outputLimitBytes=16777216,oldSessionQueries=0)
save(W/'owner.json',owner);out=(W/'stdout').open('xb');err=(W/'stderr').open('xb');proc=None;start=time.monotonic()
try:
 proc=subprocess.Popen(argv,cwd=W,env=env,stdout=out,stderr=err,stdin=subprocess.DEVNULL,shell=False);owner['pid']=proc.pid;save(W/'owner.json',owner)
 try:code=proc.wait(timeout=60)
 except subprocess.TimeoutExpired:
  owner['timedOutSticky']=True;save(W/'owner.json',owner);print('UNKNOWN original compiler retained; no retry or successor',flush=True);code=proc.wait()
 owner.update(exitCode=code,originalProcessReturned=True,endUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),elapsedSeconds=time.monotonic()-start)
finally:
 if proc is None or owner['originalProcessReturned']:out.close();err.close();owner['outputHandlesClosed']=True
 save(W/'owner.json',owner)
if owner.get('exitCode')!=0 or owner['timedOutSticky']:
 save(E/'compilation-summary.json',dict(result='FIRST_COMPILE_FAILED_OR_UNKNOWN_NO_RETRY',owner=owner));print('FIRST_COMPILE_FAILED_OR_UNKNOWN preserved complete stdout/stderr',flush=True);raise SystemExit(1)
tree=ast.parse((R/'docs/tester/D1_FIXTURE_TOOL01_BUILD_REVIEW_EVIDENCE/independent_static_audit.py').read_text());fs=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='classInfo'];exec(compile(ast.Module(body=fs,type_ignores=[]),'static_class_identity_only','exec'))
classes=[]
for p in sorted(C.rglob('*.class')):
 info=classInfo(p.read_bytes());assert info['major']==55 and info['sourceFile']=='Six01ContainerQualifier.java' and info['className'].startswith('com/videokit/fixturetool/Six01ContainerQualifier')
 classes.append(dict(**identity(p),classInfo=info))
assert len(classes)==3
output=sum(p.stat().st_size for p in E.rglob('*') if p.is_file());assert output<=16777216
save(E/'compilation-summary.json',dict(result='COMPILED_ONLY_RUNTIME_NOT_RUN',originalCompilerOwner=owner,classFiles=classes,preparedDirectoryBytesBeforeSummary=output,checkedToolSealRecords=2774,checkedZipMembers=2773,checkedPriorEvidenceFiles=len(prior['evidenceFiles']),tool02SealSha256=sha(seal),priorIndependentManifestSha256=sha(old),futureInputIdentity=None,futureInputIdentityState='UNBOUND_AWAIT_SEPARATE_EXACT_AUTHORIZATION',mediaReads=0,helperJvmCalls=0,encoderDecoderDemuxMainCalls=0,priorFrozenFilesUnchanged=True))
print('COMPILED_ONLY_RUNTIME_NOT_RUN classFiles',len(classes),'outputBytes',output,flush=True)
