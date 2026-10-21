from pathlib import Path
import json,hashlib,zipfile,shutil,re,subprocess,xml.etree.ElementTree as ET,difflib,collections,datetime
R=Path('D:/CodexProjects/VideoKit');B=R/'docs/coder/d1input-sink02';O=R/'docs/coder/d1input-sink01';E=B/'evidence'
assert not (E/'input-sink02-freeze.json').exists()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
assert json.loads((E/'build-main-001/receipt.json').read_text(encoding='utf-8-sig'))['exitCode']==0
assert 'LockMode.STRICT' in (B/'app/build.gradle.kts').read_text()
assert (B/'gradle/verification-metadata.xml').read_bytes()==(O/'gradle/verification-metadata.xml').read_bytes()
assert '<verify-metadata>true</verify-metadata>' in (B/'gradle/verification-metadata.xml').read_text()
pins={}
for c in ET.parse(B/'gradle/verification-metadata.xml').getroot().iter():
 if c.tag.split('}')[-1]=='component':
  for a in c:pins[(c.get('group'),c.get('name'),c.get('version'),a.get('name'))]={h.get('value') for h in a if h.tag.split('}')[-1]=='sha256'}
observed={};D=E/'actual-consumption';D.mkdir(exist_ok=True)
for line in (E/'build-main-001/consumption.jsonl').read_text().splitlines():
 op=json.loads(line)
 if op['name']!='Dependency verification':continue
 m=re.fullmatch(r'Verifying (.+) \(([^:]+):([^:]+):(.+)\)',op['progressName']);assert m,op
 artifact,g,a,v=m.groups();p=B/'offline-maven'/g.replace('.','/')/a/v/artifact;h=sha(p);assert h in pins[(g,a,v,artifact)]
 kind='pom' if artifact.endswith('.pom') else 'module' if artifact.endswith('.module') else 'binary'
 x={'coordinate':':'.join([g,a,v]),'artifact':artifact,'path':p.relative_to(B).as_posix(),'bytes':p.stat().st_size,'sha256':h,'kind':kind,'verificationEventId':op['id']}
 if kind!='binary':
  dest=D/'metadata'/p.relative_to(B/'offline-maven');dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dest);x['reviewCopy']=dest.relative_to(B).as_posix()
 observed[(g,a,v,artifact)]=x
records=sorted(observed.values(),key=lambda x:(x['coordinate'],x['artifact']));assert records
dump(D/'artifacts.json',records);dump(D/'summary.json',{'actualArtifacts':len(records),'counts':dict(collections.Counter(x['kind'] for x in records)),'strict':True,'verifyMetadata':True,'strictLocks':True,'buildAttempt':'001','observation':'Actual verification operations; not all cached artifacts','newVerificationPins':0})
def locked(p):return {l.split('=')[0] for l in p.read_text().splitlines() if l and not l.startswith('#') and not l.startswith('empty=')}
runtime=locked(B/'app/gradle.lockfile');assert runtime==locked(O/'app/gradle.lockfile') and len(runtime)==15
for name in ['app/gradle.lockfile','settings-gradle.lockfile','gradle/verification-metadata.xml']:
 assert (B/name).read_bytes()==(O/name).read_bytes()
for x in json.loads((E/'reused-input-sink01-pins.json').read_text()):
 assert sha(R/x['source'])==x['sha256']
 if x['path'].startswith(('deps/','gradle/','licenses/')):assert sha(B/x['path'])==x['sha256']
bom=json.loads((O/'input-sink01-sbom.cdx.json').read_text());bom['metadata']['component'].update(name='VideoKit D1 INPUT_SINK02 compile probe',version='D1-20261021-INPUT-SINK02');dump(B/'input-sink02-sbom.cdx.json',bom)
accept='dc6271e9ed151e0779740c98a63e543830f5a506ea34d641d46ba8702a09c575'
assert sha(B/'reference/D1_INPUT_SINK01_PHASE_B_REVIEW_REPORT_V1.0.md')==accept
for name in ['official-added-dependencies','apache-license-source']:
 p=O/'evidence'/name
 if p.exists():shutil.copytree(p,B/'reference'/name,dirs_exist_ok=True)
for p in (O/'evidence').glob('*license*'):
 if p.is_file():shutil.copyfile(p,B/'reference'/p.name)
dump(E/'dependency-license-difference.json',{'runtimeCoordinates':15,'newCoordinatesComparedToInputSink01':[],'versionChanges':[],'newBinaryDownloads':0,'newVerificationPins':0,'lockFilesByteIdentical':True,'verificationMetadataByteIdentical':True,'independentNewUseAdmission':'PASS_IDENTITY_LICENSE_FOR_THIS_OFFLINE_CANDIDATE inherited from INPUT_SINK01 Phase B','acceptanceReportSha256':accept,'newFixIndependentReview':'PENDING','newPlatformOrReleaseAdmission':False})
for x in json.loads((E/'local-003/source-pins.json').read_text()):assert sha(B/x['path'])==x['sha256']
dump(E/'local-003/classpath-end-binding.json',[{'path':p.relative_to(B).as_posix(),'sha256':sha(p)} for p in sorted((B/'deps').glob('*.jar'))])
art=B/'artifacts';art.mkdir(exist_ok=True);apk=art/'input-sink02-compile-probe-debug.apk';shutil.copyfile(B/'app/build/outputs/apk/debug/app-debug.apk',apk)
classes=B/'app/build/intermediates/javac/debug/compileDebugJavaWithJavac/classes';jar=art/'input-sink02-classes.jar';assert not jar.exists()
with zipfile.ZipFile(jar,'x',zipfile.ZIP_DEFLATED) as z:
 for p in sorted(classes.rglob('*.class')):assert p.relative_to(classes).as_posix().startswith('com/videokit/');z.write(p,p.relative_to(classes).as_posix())
with zipfile.ZipFile(jar) as z:
 assert len(z.namelist())>20
 for p in classes.rglob('*.class'):assert z.read(p.relative_to(classes).as_posix())==p.read_bytes()
with zipfile.ZipFile(apk) as z:
 dex=b''.join(z.read(n) for n in z.namelist() if n.endswith('.dex'));assert not any(n.startswith('lib/') for n in z.namelist())
 for text in [b'InputSinkCheck',b'ReturnBoundaryCheck',b'controlled_ready_token',b'fixture-ui']:assert text not in dex
 for name in ['HostDataSource','HostInputFactory','TemporaryOutput','MatureMuxerBinding','AndroidGrantedStream','PlatformOutputErrors']:assert ('Lcom/videokit/d1input/'+name+';').encode() in dex
manifest=B/'app/build/intermediates/merged_manifests/debug/processDebugManifest/AndroidManifest.xml';root=ET.parse(manifest).getroot();assert root.get('package')=='com.videokit.d1input' and not root.findall('uses-permission') and not list(root.find('application'));shutil.copyfile(manifest,E/'compile-probe-merged-manifest.xml')
V=E/'signature-audit';V.mkdir(exist_ok=False);vc=V/'classes';vc.mkdir();J=Path('D:/Android/Android Studio/jbr/bin');apksig=B/'offline-maven/com/android/tools/build/apksig/9.3.3/apksig-9.3.3.jar';assert sha(apksig) in pins[('com.android.tools.build','apksig','9.3.3',apksig.name)]
for name,argv in [('compile',[str(J/'javac.exe'),'--release','11','-encoding','UTF-8','-cp',str(apksig),'-d',str(vc),str(B/'tools/VerifyApk.java')]),('verify',[str(J/'java.exe'),'-cp',str(vc)+';'+str(apksig),'VerifyApk',str(apk)])]:
 p=subprocess.run(argv,stdout=subprocess.PIPE,stderr=subprocess.PIPE);(V/(name+'.stdout')).write_bytes(p.stdout);(V/(name+'.stderr')).write_bytes(p.stderr);dump(V/(name+'.json'),{'argv':argv,'exitCode':p.returncode,'originalProcessReturned':True,'SDKCommand':False});assert p.returncode==0
assert '5e841a04968f3f790f6996ca5e286d8c2734338542486909f9a136717dde808f' in (V/'verify.stdout').read_text()
out=[{'path':p.relative_to(R).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in [apk,jar]];dump(E/'artifact-audit.json',{'result':'PASS_COMPILE_PROBE_ONLY','artifacts':out,'package':'com.videokit.d1input','versionCode':2,'versionName':'D1-INPUT-SINK02','permissions':[],'components':[],'nativeLibraries':0,'testAndPlatformPortClassesExcluded':True,'APKRuntime':'NOT_RUN','actualMedia3AndAndroidCompile':True,'signerCertificateSha256':'5e841a04968f3f790f6996ca5e286d8c2734338542486909f9a136717dde808f'})
preserved=[]
for directory,filename in [('d1render01','render01-freeze.json'),('d1render02','render02-freeze.json'),('d1render02-capture','capture-adapt-freeze.json'),('d1input-sink01','input-sink01-freeze.json')]:
 s=R/'docs/coder'/directory/'evidence'/filename;f=json.loads(s.read_text());assert all(sha(R/x['path'])==x['sha256'] for x in f['files']);preserved.append({'candidate':directory,'sealPath':s.relative_to(R).as_posix(),'sealSha256':sha(s),'filesUnchanged':len(f['files'])})
assert sum(x['filesUnchanged'] for x in preserved)==2033;dump(E/'frozen-baseline-preservation.json',preserved)
changes=[]
reuse=json.loads((E/'reused-input-sink01-pins.json').read_text())
check='checks/com/videokit/d1input/InputSinkCheck.java';reuse.append({'source':(O/check).relative_to(R).as_posix(),'path':check,'sha256':sha(O/check)})
for x in reuse:
 p=B/x['path']
 if sha(p)!=x['sha256']:
  changes.append({'path':x['path'],'originalSha256':x['sha256'],'candidateSha256':sha(p)})
  if p.suffix=='.java':(E/(p.stem+'-source-diff.patch')).write_text(''.join(difflib.unified_diff((R/x['source']).read_text().splitlines(True),p.read_text().splitlines(True),fromfile=x['source'],tofile=x['path'])),encoding='utf-8')
assert {x['path'] for x in changes}=={'src/com/videokit/d1input/TemporaryOutput.java','src/com/videokit/d1input/HostOutput.java','android/com/videokit/d1input/AndroidGrantedStream.java','upstream/com/videokit/spike/c14/SinkCoordinator.java','checks/com/videokit/d1input/InputSinkCheck.java'}
dump(E/'source-differences.json',{'changedCopiedFiles':changes,'newBoundaryTest':'checks/com/videokit/d1input/ReturnBoundaryCheck.java','A01InputSourcesUnchanged':True,'dependenciesUnchanged':True})
inputs=[{'path':p.relative_to(B).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(B.rglob('*')) if p.is_file() and (p.relative_to(B).parts[0] in ['src','android','upstream','deps','gradle','offline-maven'] or p.relative_to(B).as_posix() in ['build.gradle.kts','settings.gradle.kts','gradle.properties','local.properties','app/build.gradle.kts','app/gradle.lockfile','settings-gradle.lockfile','app/src/main/AndroidManifest.xml'])];dump(E/'final-source-dependency-inputs.json',inputs)
print(json.dumps({'artifacts':out,'actualArtifacts':len(records),'counts':dict(collections.Counter(x['kind'] for x in records)),'oldFrozenFilesUnchanged':2033,'changedCopiedFiles':[x['path'] for x in changes]},indent=2))
