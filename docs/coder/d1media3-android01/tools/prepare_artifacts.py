from pathlib import Path
import json,hashlib,zipfile,shutil,re,subprocess,xml.etree.ElementTree as ET,collections,ast,struct,difflib
B=Path(__file__).resolve().parents[1];R=B.parents[2];O=R/'docs/coder/d1media3-container02';E=B/'evidence';assert not (E/'media3-android01-freeze.json').exists()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
receipt=json.loads((E/'build-main-004/receipt.json').read_text(encoding='utf-8-sig'));assert receipt['exitCode']==0 and receipt['offline'] and receipt['strictVerification'] and receipt['verifyMetadata'] and receipt['strictLockMode'] and not receipt['writeNewCandidateExactLocks']
for x in json.loads((E/'local-002/source-pins.json').read_text()):assert sha(B/x['path'])==x['sha256']
pins={}
for c in ET.parse(B/'gradle/verification-metadata.xml').getroot().iter():
 if c.tag.split('}')[-1]=='component':
  for a in c:pins[(c.get('group'),c.get('name'),c.get('version'),a.get('name'))]={h.get('value') for h in a if h.tag.split('}')[-1]=='sha256'}
assert (B/'gradle/verification-metadata.xml').read_bytes()==(O/'gradle/verification-metadata.xml').read_bytes() and (B/'settings-gradle.lockfile').read_bytes()==(O/'settings-gradle.lockfile').read_bytes()
def locks(p):
 return {l.split('=')[0]:set(l.split('=')[1].split(',')) for l in p.read_text().splitlines() if l and not l.startswith(('#','empty='))}
old=locks(O/'app/gradle.lockfile');new=locks(B/'app/gradle.lockfile');assert new.keys()==old.keys() and len(new)==17
for c in old:assert {s for s in new[c] if 'AndroidTest' not in s}==old[c]
events=[json.loads(l) for l in (E/'build-main-004/consumption.jsonl').read_text().splitlines()];records={};D=E/'actual-consumption';D.mkdir()
for op in events:
 if op.get('name')!='Dependency verification':continue
 m=re.fullmatch(r'Verifying (.+) \(([^:]+):([^:]+):(.+)\)',op['progressName']);assert m,op
 artifact,g,a,v=m.groups();p=B/'offline-maven'/g.replace('.','/')/a/v/artifact;h=sha(p);assert h in pins[(g,a,v,artifact)];kind='pom' if artifact.endswith('.pom') else 'module' if artifact.endswith('.module') else 'binary';row={'coordinate':':'.join([g,a,v]),'artifact':artifact,'path':p.relative_to(B).as_posix(),'bytes':p.stat().st_size,'sha256':h,'kind':kind,'verificationEventId':op['id']}
 if kind!='binary':
  dest=D/'metadata'/p.relative_to(B/'offline-maven');dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dest);row['reviewCopy']=dest.relative_to(B).as_posix()
 records[(g,a,v,artifact)]=row
rows=sorted(records.values(),key=lambda x:(x['coordinate'],x['artifact']));oldRows=json.loads((O/'evidence/actual-consumption/artifacts.json').read_text());assert {(x['coordinate'],x['artifact'],x['sha256']) for x in rows}=={(x['coordinate'],x['artifact'],x['sha256']) for x in oldRows}
dump(D/'artifacts.json',rows);dump(D/'summary.json',{'actualArtifacts':len(rows),'counts':dict(collections.Counter(x['kind'] for x in rows)),'strict':True,'verifyMetadata':True,'strictLocks':True,'buildAttempt':'004','sameActualExternalArtifactIdentitiesAsContainer02':True})
closures=[x for x in events if x.get('event')=='actual-configuration-closure'];cp=[x for x in events if x.get('event')=='actual-javac-classpath'];assert {x['configuration'] for x in closures}=={'debugCompileClasspath','debugRuntimeClasspath','debugAndroidTestCompileClasspath','debugAndroidTestRuntimeClasspath'}
summary={}
for c in closures:
 coords=sorted({x['componentId'] for x in c['components'] if x['external']});expected=sorted(k for k,v in new.items() if c['configuration'] in v);assert coords==expected;summary[c['configuration']]={'externalCoordinates':coords,'externalCount':len(coords),'projectComponents':[x for x in c['components'] if not x['external']]}
assert [summary[k]['externalCount'] for k in ['debugCompileClasspath','debugRuntimeClasspath','debugAndroidTestCompileClasspath','debugAndroidTestRuntimeClasspath']]==[12,17,12,0]
assert {x['task'] for x in cp}=={':app:compileDebugJavaWithJavac',':app:compileDebugAndroidTestJavaWithJavac'};dump(D/'configuration-closures.json',closures);dump(D/'configuration-closure-summary.json',summary);dump(D/'actual-javac-classpaths.json',cp)
dump(E/'dependency-license-difference.json',{'newRuntimeCoordinates':[],'newVersionsPinsBinaryDownloads':0,'appConfigurationLocksPreserved':True,'settingsLockAndVerificationMetadataByteIdentical':True,'newLockScopes':'Only exact inherited12 compile coordinates added to AndroidTestCompile; AndroidTestRuntime has no external dependency','separateActualClosures':{k:v['externalCount'] for k,v in summary.items()},'runtimeTargetSuppliesTestedCode':True,'testRunner':'android.app.Instrumentation, Android framework; no new AndroidX test dependency','inheritedAdmissionReportSha256':'e857e11a919475562587ff300223472076e8c190388f838e61a8417fecd46649','encoderProposal':'Source-only reference outside every app/test sourceSet,classPath and mirror; no encoder binary/compile/load/generation'})
artifact=B/'artifacts';mainJar=artifact/'media3-android01-classes.jar';testJar=artifact/'media3-android01-instrumentation-classes.jar';app=artifact/'media3-android01-app-debug.apk';test=artifact/'media3-android01-test-debug.apk'
shutil.copyfile(B/'app/build/outputs/apk/debug/app-debug.apk',app);shutil.copyfile(B/'app/build/outputs/apk/androidTest/debug/app-debug-androidTest.apk',test)
for dest,folder in [(mainJar,B/'app/build/intermediates/javac/debug/compileDebugJavaWithJavac/classes'),(testJar,B/'app/build/intermediates/javac/debugAndroidTest/compileDebugAndroidTestJavaWithJavac/classes')]:
 with zipfile.ZipFile(dest,'x',zipfile.ZIP_DEFLATED) as z:
  for p in sorted(folder.rglob('*.class')):assert p.relative_to(folder).as_posix().startswith('com/videokit/');z.write(p,p.relative_to(folder).as_posix())
 with zipfile.ZipFile(dest) as z:
  for p in folder.rglob('*.class'):assert z.read(p.relative_to(folder).as_posix())==p.read_bytes()
legacyParser=R/'docs/tester/D1_INPUT_SINK01_REVIEW_EVIDENCE/audit_frozen.py';text=legacyParser.read_text();tree=ast.parse(text);defs=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['pool','axml','dexclasses']];assert len(defs)==3;exec(compile(ast.Module(body=defs,type_ignores=[]),'reused_exact_artifact_parser','exec'))
dump(E/'artifact-parser-origin.json',{'source':legacyParser.relative_to(R).as_posix(),'sha256':sha(legacyParser),'functions':['pool','axml','dexclasses'],'purpose':'Reuse original pure Python manifest/DEX parser only; no SDK command'})
audits=[];cert='5e841a04968f3f790f6996ca5e286d8c2734338542486909f9a136717dde808f';checks={p.stem for p in (B/'checks').rglob('*.java')}
for file,package,isTest in [(app,'com.videokit.d1media3.android01',False),(test,'com.videokit.d1media3.android01.test',True)]:
 with zipfile.ZipFile(file) as z:
  tags=axml(z.read('AndroidManifest.xml'));classes=[c for n in z.namelist() if n.endswith('.dex') for c in dexclasses(z.read(n))];attrs=tags[0]['attributes'];assert attrs['package']==package and attrs['versionCode']==1 and attrs['versionName']=='D1-MEDIA3-ANDROID01-READY' and 'sharedUserId' not in attrs
  assert not any(t['tag'] in ['uses-permission','uses-permission-sdk-23','activity','activity-alias','service','provider','receiver'] for t in tags);assert not any(n.startswith('lib/') for n in z.namelist())
  assert not any(c.startswith('Lorg/jcodec/') for c in classes);assert not any(c in ['Landroid/net/Uri;','Landroid/system/ErrnoException;','Landroid/system/OsConstants;'] for c in classes);assert not any('/'+n+';' in c or '/'+n+'$' in c for c in classes for n in checks)
  with zipfile.ZipFile(next((O/'artifacts').glob('*.apk'))) as oldZip: oldAndroid={c for n in oldZip.namelist() if n.endswith('.dex') for c in dexclasses(oldZip.read(n)) if c.startswith('Landroid/')}
  assert {c for c in classes if c.startswith('Landroid/')}==oldAndroid
  application=next(t['attributes'] for t in tags if t['tag']=='application');assert application['allowBackup']==False and application['usesCleartextTraffic']==False
  instruments=[t['attributes'] for t in tags if t['tag']=='instrumentation']
  if isTest:
   assert len(instruments)==1 and instruments[0]['name']=='com.videokit.d1media3.android01.test.Media3Instrumentation' and instruments[0]['targetPackage']=='com.videokit.d1media3.android01' and instruments[0]['targetProcesses']=='com.videokit.d1media3.android01:media3';assert not any(c.startswith('Landroidx/media3/') for c in classes)
   assert len(z.read('assets/sample.mp4'))==349102 and hashlib.sha256(z.read('assets/sample.mp4')).hexdigest()=='720957c94b3665ff97bcc2f59ad5407c5ca54f566b59865723be9eecc0a6a1f9';assert b'DERIVATIVE' in z.read('assets/SOURCE_AND_LICENSE.txt')
  else:assert not instruments and application['process']==':media3' and 'assets/sample.mp4' not in z.namelist();assert 'Lcom/videokit/d1input/HostMp4Inspection;' in classes
  audits.append({'path':file.relative_to(B).as_posix(),'bytes':file.stat().st_size,'sha256':sha(file),'package':package,'manifest':tags,'dexClassCount':len(classes),'inheritedBuildGeneratedAndroidDefinitions':len(oldAndroid),'androidDefinitionSetExactlyEqualsFrozenContainer02':True,'nativeLibraries':0,'permissions':[],'instrumentation':instruments,'samplePrivateAsset':isTest,'sameUidIsRceIsolation':False,'AndroidExecution':'NOT_RUN'})
V=E/'signature-audit';V.mkdir();C=V/'classes';C.mkdir();J=Path('D:/Android/Android Studio/jbr/bin');sig=B/'offline-maven/com/android/tools/build/apksig/9.3.3/apksig-9.3.3.jar';assert sha(sig) in pins[('com.android.tools.build','apksig','9.3.3',sig.name)]
for name,argv in [('compile',[str(J/'javac.exe'),'--release','11','-encoding','UTF-8','-cp',str(sig),'-d',str(C),str(B/'tools/VerifyApk.java')])]+[(kind,[str(J/'java.exe'),'-cp',str(C)+';'+str(sig),'VerifyApk',str(p)]) for kind,p in [('app',app),('test',test)]]:
 p=subprocess.run(argv,stdout=subprocess.PIPE,stderr=subprocess.PIPE);(V/(name+'.stdout')).write_bytes(p.stdout);(V/(name+'.stderr')).write_bytes(p.stderr);dump(V/(name+'.json'),{'argv':argv,'exitCode':p.returncode,'originalProcessReturned':True,'SDKCommand':False});assert p.returncode==0
 if name!='compile':assert cert in p.stdout.decode()
for f in (B/'instrumentation').rglob('*.java'):
 source=f.read_text();assert all(t not in source for t in ['MediaCodec.','AudioTrack(','new Surface','startActivity(','killProcess(','System.exit(','Runtime.getRuntime().exec'])
with zipfile.ZipFile(testJar) as z:
 for name in z.namelist():assert all(t not in z.read(name) for t in [b'android/media/MediaCodec',b'android/media/MediaExtractor',b'android/media/AudioTrack',b'android/view/Surface',b'killProcess',b'setStreamVolume',b'startActivity'])
dump(E/'artifact-audit.json',{'result':'PASS_OFFLINE_APP_AND_TEST_IDENTITY_ONLY','apks':audits,'jarArtifacts':[{'path':p.relative_to(B).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in [mainJar,testJar]],'signerCertificateSha256':cert,'builtInInstrumentationNoNewTestRuntime':True,'noNewOwnDecoderPlaybackSurfaceAudioCodecGpuCalls':True,'noNewPlatformStandinsInAPKs':True,'proposalSourceNeverOnAPKClasspath':True,'noActualAndroidRun':True})
changed=[]
for x in json.loads((E/'baseline-pins.json').read_text()):
 if sha(B/x['path'])!=x['sha256']:
  changed.append({'path':x['path'],'oldSha256':x['sha256'],'newSha256':sha(B/x['path'])});p=B/x['path'];(E/(p.stem+'-source-diff.patch')).write_text(''.join(difflib.unified_diff((R/x['source']).read_text().splitlines(True),p.read_text().splitlines(True),fromfile=x['source'],tofile=x['path'])),encoding='utf-8')
assert {x['path'] for x in changed}=={'src/com/videokit/d1input/HostInputFactory.java','src/com/videokit/d1input/HostMp4Inspection.java','src/com/videokit/d1input/TemporaryOutput.java'}
dump(E/'source-differences.json',{'changedCopiedProduction':changed,'changes':'Read-only same-source identity; bounded true ranges/seek/replay/release witnesses; explicit actual-host UID/PID overload (generic old default unchanged)','MC_B01AdmissionHelpersRetained':True,'newProductionHelpers':['ExperimentContract','VerifiedFixtureCopy'],'newAndroidTestSources':['Media3Instrumentation','ExperimentJob','OwnedFiles'],'unchangedUpstreamIncludingOriginalFinishOwner':True,'newPlatformStandins':0})
oldSeals=[]
for folder,name in [('d1render01','render01-freeze.json'),('d1render02','render02-freeze.json'),('d1render02-capture','capture-adapt-freeze.json')]+[('d1input-sink'+n,'input-sink'+n+'-freeze.json') for n in ['01','02','03','04','05']]+[('d1media3-container'+n,'media3-container'+n+'-freeze.json') for n in ['01','02']]:
 p=R/'docs/coder'/folder/'evidence'/name;s=json.loads(p.read_text());assert all(sha(R/x['path'])==x['sha256'] for x in s['files']);oldSeals.append({'sealPath':p.relative_to(R).as_posix(),'sealSha256':sha(p),'filesUnchanged':len(s['files'])})
assert sum(x['filesUnchanged'] for x in oldSeals)==6232;dump(E/'frozen-baseline-preservation.json',oldSeals)
inputs=[{'path':p.relative_to(B).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(B.rglob('*')) if p.is_file() and (p.relative_to(B).parts[0] in ['src','android','upstream','instrumentation','instrumentation-assets','notice-assets','deps','gradle','offline-maven'] or p.relative_to(B).as_posix() in ['app/build.gradle.kts','app/gradle.lockfile','app/src/main/AndroidManifest.xml','app/src/androidTest/AndroidManifest.xml','settings.gradle.kts','settings-gradle.lockfile','build.gradle.kts','gradle.properties','local.properties'])];dump(E/'final-source-dependency-inputs.json',inputs)
print(json.dumps({'apks':[{k:x[k] for k in ['path','bytes','sha256','package','dexClassCount']} for x in audits],'jars':json.loads((E/'artifact-audit.json').read_text())['jarArtifacts'],'configCounts':{k:v['externalCount'] for k,v in summary.items()},'oldFrozenFilesUnchanged':6232},indent=2))
