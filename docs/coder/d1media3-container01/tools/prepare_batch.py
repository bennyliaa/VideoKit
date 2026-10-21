from pathlib import Path
import json,hashlib,zipfile,shutil,re,subprocess,xml.etree.ElementTree as ET,collections,difflib
B=Path(__file__).resolve().parents[1];R=B.parents[2];O=R/'docs/coder/d1input-sink05';E=B/'evidence'
assert not (E/'media3-container01-freeze.json').exists()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
receipt=json.loads((E/'build-main-004/receipt.json').read_text(encoding='utf-8-sig'));assert receipt['exitCode']==0 and receipt['offline'] and receipt['strictVerification'] and receipt['verifyMetadata'] and receipt['strictLockMode']
for row in json.loads((E/'local-007/source-pins.json').read_text()):assert sha(B/row['path'])==row['sha256']
pins={}
for c in ET.parse(B/'gradle/verification-metadata.xml').getroot().iter():
 if c.tag.split('}')[-1]=='component':
  for a in c:pins[(c.get('group'),c.get('name'),c.get('version'),a.get('name'))]={h.get('value') for h in a if h.tag.split('}')[-1]=='sha256'}
D=E/'actual-consumption';D.mkdir(exist_ok=True);observed={}
for line in (E/'build-main-004/consumption.jsonl').read_text().splitlines():
 op=json.loads(line)
 if op['name']!='Dependency verification':continue
 m=re.fullmatch(r'Verifying (.+) \(([^:]+):([^:]+):(.+)\)',op['progressName']);assert m,op
 artifact,g,a,v=m.groups();p=B/'offline-maven'/g.replace('.','/')/a/v/artifact;h=sha(p);assert h in pins[(g,a,v,artifact)]
 kind='pom' if artifact.endswith('.pom') else 'module' if artifact.endswith('.module') else 'binary'
 row={'coordinate':':'.join([g,a,v]),'artifact':artifact,'path':p.relative_to(B).as_posix(),'bytes':p.stat().st_size,'sha256':h,'kind':kind,'verificationEventId':op['id']}
 if kind!='binary':
  dest=D/'metadata'/p.relative_to(B/'offline-maven');dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dest);row['reviewCopy']=dest.relative_to(B).as_posix()
 observed[(g,a,v,artifact)]=row
records=sorted(observed.values(),key=lambda x:(x['coordinate'],x['artifact']));assert records
dump(D/'artifacts.json',records);dump(D/'summary.json',{'actualArtifacts':len(records),'counts':dict(collections.Counter(x['kind'] for x in records)),'strict':True,'verifyMetadata':True,'strictLocks':True,'buildAttempt':'004','observation':'Actual verification events; not all cached artifacts'})
def lock(path):return {l.split('=')[0] for l in path.read_text().splitlines() if l and not l.startswith('#') and not l.startswith('empty=')}
new=lock(B/'app/gradle.lockfile')-lock(O/'app/gradle.lockfile');assert new=={'androidx.media3:media3-extractor:1.9.3','androidx.media3:media3-decoder:1.9.3'}
assert (B/'settings-gradle.lockfile').read_bytes()==(O/'settings-gradle.lockfile').read_bytes()
def pinmap(path):
 rows={}
 for c in ET.parse(path).getroot().iter():
  if c.tag.split('}')[-1]=='component':
   for a in c:rows[(c.get('group'),c.get('name'),c.get('version'),a.get('name'))]=sorted(h.get('value') for h in a if h.tag.split('}')[-1]=='sha256')
 return rows
oldpins=pinmap(O/'gradle/verification-metadata.xml');assert all(pins[k]==set(v) for k,v in oldpins.items());added=set(pins)-set(oldpins);assert added=={('androidx.media3','media3-extractor','1.9.3','media3-extractor-1.9.3.pom'),('androidx.media3','media3-decoder','1.9.3','media3-decoder-1.9.3.pom')}
dump(E/'dependency-license-difference.json',{'runtimeCoordinates':len(lock(B/'app/gradle.lockfile')),'newUseCoordinates':sorted(new),'versionChanges':[],'newBinaryDownloads':0,'newVerificationBinaryOrModulePins':0,'newOfficialPomPins':[list(x) for x in sorted(added)],'allOldPinsUnchanged':True,'settingsLockByteIdentical':True,'appLockChanges':'Two same-version coordinates; container now also compile, decoder runtime only','newUseSourceAdmission':'reference/official-extractor and evidence/extractor-source-admission.json; independent admission PENDING','oldUseAdmissionReport':'docs/tester/D1_INPUT_SINK01_PHASE_B_REVIEW_REPORT_V1.0.md','oldUseAdmissionSha256':'dc6271e9ed151e0779740c98a63e543830f5a506ea34d641d46ba8702a09c575','platformRuntimeAdmission':False})
admission=json.loads((E/'extractor-source-admission.json').read_text());
for x in admission['records']:x['strictBinaryAndModulePinsPreexisting']=x.pop('strictPinsPreexisting',True);x['officialPomPinNewInThisBatch']=True
dump(E/'extractor-source-admission.json',admission)
jar=B/'artifacts/media3-container01-classes.jar';apk=B/'artifacts/media3-container01-compile-probe-debug.apk';assert jar.exists();shutil.copyfile(B/'app/build/outputs/apk/debug/app-debug.apk',apk)
classes=B/'app/build/intermediates/javac/debug/compileDebugJavaWithJavac/classes'
with zipfile.ZipFile(jar,'w',zipfile.ZIP_DEFLATED) as z:
 for p in sorted(classes.rglob('*.class')):
  assert p.relative_to(classes).as_posix().startswith('com/videokit/');z.write(p,p.relative_to(classes).as_posix())
with zipfile.ZipFile(jar) as z:
 for p in classes.rglob('*.class'):assert z.read(p.relative_to(classes).as_posix())==p.read_bytes()
 assert all(not n.startswith(('android/','androidx/')) for n in z.namelist())
with zipfile.ZipFile(apk) as z:
 dex=b''.join(z.read(n) for n in z.namelist() if n.endswith('.dex'));assert not any(n.startswith('lib/') for n in z.namelist())
 for text in [b'ExtractorInputCheck',b'Media3AvailabilityCheck',b'ApprovedSampleReadCheck',b'InputSinkCheck',b'fixture-ui',b'controlled_ready_token']:assert text not in dex
 for text in [b'HostMp4Inspection',b'MatureContainerRemux',b'TemporaryOutput']:assert text in dex
manifest=B/'app/build/intermediates/merged_manifests/debug/processDebugManifest/AndroidManifest.xml';root=ET.parse(manifest).getroot();assert root.get('package')=='com.videokit.d1input' and not root.findall('uses-permission') and not list(root.find('application'));shutil.copyfile(manifest,E/'compile-probe-merged-manifest.xml')
V=E/'signature-audit';V.mkdir(exist_ok=True);vc=V/'classes';vc.mkdir(exist_ok=True);J=Path('D:/Android/Android Studio/jbr/bin');apksig=B/'offline-maven/com/android/tools/build/apksig/9.3.3/apksig-9.3.3.jar';assert sha(apksig) in pins[('com.android.tools.build','apksig','9.3.3',apksig.name)]
for name,argv in [('compile',[str(J/'javac.exe'),'--release','11','-encoding','UTF-8','-cp',str(apksig),'-d',str(vc),str(B/'tools/VerifyApk.java')]),('verify',[str(J/'java.exe'),'-cp',str(vc)+';'+str(apksig),'VerifyApk',str(apk)])]:
 p=subprocess.run(argv,stdout=subprocess.PIPE,stderr=subprocess.PIPE);(V/(name+'.stdout')).write_bytes(p.stdout);(V/(name+'.stderr')).write_bytes(p.stderr);dump(V/(name+'.json'),{'argv':argv,'exitCode':p.returncode,'originalProcessReturned':True,'SDKCommand':False});assert p.returncode==0
assert '5e841a04968f3f790f6996ca5e286d8c2734338542486909f9a136717dde808f' in (V/'verify.stdout').read_text()
dump(E/'artifact-audit.json',{'result':'PASS_STRICT_COMPILE_ONLY','artifacts':[{'path':p.relative_to(R).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in [jar,apk]],'package':'com.videokit.d1input','versionCode':6,'versionName':'D1-MEDIA3-CONTAINER01','permissions':[],'components':[],'nativeLibraries':0,'testAndPlatformPortsExcluded':True,'APKRuntime':'NOT_RUN','signerCertificateSha256':'5e841a04968f3f790f6996ca5e286d8c2734338542486909f9a136717dde808f'})
preserved=[]
for folder,name in [('d1render01','render01-freeze.json'),('d1render02','render02-freeze.json'),('d1render02-capture','capture-adapt-freeze.json')]+[('d1input-sink'+n,'input-sink'+n+'-freeze.json') for n in ['01','02','03','04','05']]:
 p=R/'docs/coder'/folder/'evidence'/name;f=json.loads(p.read_text());assert all(sha(R/x['path'])==x['sha256'] for x in f['files']);preserved.append({'candidate':folder,'sealPath':p.relative_to(R).as_posix(),'sealSha256':sha(p),'filesUnchanged':len(f['files'])})
assert sum(x['filesUnchanged'] for x in preserved)==4511;dump(E/'frozen-baseline-preservation.json',preserved)
changes=[]
for row in json.loads((E/'baseline-pins.json').read_text()):
 if sha(B/row['path'])!=row['sha256']:
  changes.append({'path':row['path'],'oldSha256':row['sha256'],'newSha256':sha(B/row['path'])})
  if row['path'].endswith('.java'):(E/(Path(row['path']).stem+'-source-diff.patch')).write_text(''.join(difflib.unified_diff((R/row['source']).read_text().splitlines(True),(B/row['path']).read_text().splitlines(True),fromfile=row['source'],tofile=row['path'])),encoding='utf-8')
assert {x['path'] for x in changes}=={'src/com/videokit/d1input/TemporaryOutput.java','gradle/verification-metadata.xml'}
dump(E/'source-differences.json',{'changedCopiedInputs':changes,'newProductionJava':['HostMp4Inspection','MatureContainerRemux'],'inputAdaptersUpstreamAndMuxerBindingUnchanged':True,'newJVMPlatformPorts':0})
inputs=[{'path':p.relative_to(B).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(B.rglob('*')) if p.is_file() and (p.relative_to(B).parts[0] in ['src','android','upstream','deps','gradle','offline-maven'] or p.relative_to(B).as_posix() in ['build.gradle.kts','settings.gradle.kts','gradle.properties','local.properties','app/build.gradle.kts','app/gradle.lockfile','settings-gradle.lockfile','app/src/main/AndroidManifest.xml'])];dump(E/'final-source-dependency-inputs.json',inputs)
dump(E/'jvm-classpath.json',[{'path':p.relative_to(B).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted((B/'deps').glob('*.jar'))])
print(json.dumps({'actualArtifacts':len(records),'oldFrozenUnchanged':4511,'jarSha256':sha(jar),'apkSha256':sha(apk)},indent=2))
