from pathlib import Path
import hashlib,json,re,subprocess,zipfile
B=Path(__file__).resolve().parents[1];R=B.parents[2];OLD=R/'docs/coder/d1e11';SDK=Path('D:/Android/SDK/build-tools/36.0.0');JAVA=Path('D:/Android/Android Studio/jbr/bin/java.exe')
E=B/'evidence/apk-delivery';E.mkdir(parents=True,exist_ok=True);A=B/'artifacts/D1-20261018-E13/delivery';A.mkdir(parents=True,exist_ok=True)
def sha(b):return hashlib.sha256(b).hexdigest()
def rel(p):return p.relative_to(R).as_posix()
def pin(p):b=p.read_bytes();return {'path':rel(p),'bytes':len(b),'sha256':sha(b)}
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def run(name,args):
 p=E/(name+'.txt')
 if p.exists():return p.read_text(encoding='utf-8-sig')
 with p.open('xb') as f:r=subprocess.run([str(a) for a in args],stdout=f,stderr=subprocess.STDOUT)
 assert r.returncode==0,name
 return p.read_text(encoding='utf-8-sig')
inputs=json.loads((B/'evidence/final-build-inputs.json').read_text(encoding='utf-8'))['files']
for r in inputs:assert pin(R/r['path'])==r,r['path']
mainSigner='5e841a04968f3f790f6996ca5e286d8c2734338542486909f9a136717dde808f';apks=[];native=[]
for kind,path,pkg in [('app','app/build/outputs/apk/debug/app-debug.apk','com.videokit.app'),('test','app/build/outputs/apk/androidTest/debug/app-debug-androidTest.apk','com.videokit.app.test'),('fixture','fixture/build/outputs/apk/debug/fixture-debug.apk','com.videokit.e13.sender')]:
 source=B/path;target=A/source.name
 if target.exists():assert target.read_bytes()==source.read_bytes()
 else:target.write_bytes(source.read_bytes())
 signature=run(kind+'-signing',[JAVA,'-jar',SDK/'lib/apksigner.jar','verify','--verbose','--print-certs',target]);found=re.findall(r'Signer #1 certificate SHA-256 digest: ([0-9a-f]{64})',signature);assert len(found)==1
 signer=found[0];assert (signer==mainSigner) if kind!='fixture' else (signer!=mainSigner)
 badging=run(kind+'-badging',[SDK/'aapt2.exe','dump','badging',target]);assert f"package: name='{pkg}'" in badging
 if kind=='app':assert "versionCode='16'" in badging and "versionName='D1-E13-ACTIVATION'" in badging
 xml=run(kind+'-manifest',[SDK/'aapt2.exe','dump','xmltree','--file','AndroidManifest.xml',target])
 run(kind+'-zipalign16',[SDK/'zipalign.exe','-c','-P','16','-v','4',target])
 if kind=='app':
  assert 'ACTIVATION' in xml and 'videokit.e9.gateAbi' in xml and 'android.permission.INTERNET' not in xml
  assert 'com.videokit.e13.sender' in xml
  serviceBlocks=re.split(r'(?m)^\s*E: service\b',xml)[1:];assert len(serviceBlocks)==2
  for name in ['com.videokit.spike.e4.E4CodecService','com.videokit.spike.c14.CpuIsolatedService']:
   blocks=[v.split('\n      E:',1)[0] for v in serviceBlocks if name in v];assert len(blocks)==1
   assert re.search(r'android:exported[^\n]*(?:=false\b|0x0\b)',blocks[0])
 if kind=='test':assert 'com.videokit.spike.e4.E13Instrumentation' in xml and 'E9MigrationInstrumentation' not in xml
 if kind=='fixture':assert 'com.videokit.e13.sender.SenderService' in xml and re.search(r'android:exported[^\n]*(?:=true\b|0xffffffff)',xml) and 'android.permission.' not in xml
 with zipfile.ZipFile(target) as z:
  entries=[n for n in z.namelist() if n.startswith('lib/') and n.endswith('.so')]
  if kind=='app':
   assert len(entries)==7
   for n in entries:
    p=B/'upstream-c14/native-libs'/Path(n).relative_to('lib');assert z.read(n)==p.read_bytes()==(OLD/p.relative_to(B)).read_bytes();native.append({'entry':n,**pin(p)})
   dex=b''.join(z.read(n) for n in z.namelist() if n.endswith('.dex'))
   for marker in [b'E13SourceGroup',b'E13PermissionProbe',b'SourceAdmission',b'ACTIVATION',b'E9CurrentObservation']:assert marker in dex,marker
  else:assert not entries
  if kind=='fixture':assert not any(n.startswith('kotlin/') for n in z.namelist())
  if kind=='test':
   dex=b''.join(z.read(n) for n in z.namelist() if n.endswith('.dex'))
   for marker in [b'E13Instrumentation',b'E13SourceCases',b'E13_PLATFORM_FINISH_ADMITTED']:assert marker in dex,marker
 apks.append({'kind':kind,**pin(target),'package':pkg,'signer':signer})
lock=B/'app/gradle.lockfile';assert lock.read_bytes()==(OLD/'app/gradle.lockfile').read_bytes()
coords=[l for l in lock.read_text().splitlines() if l and not l.startswith('#') and not l.startswith('empty=')];assert len(coords)==35
fixtureLock=B/'fixture/gradle.lockfile';assert fixtureLock.is_file()
fixtureCoords=[l for l in fixtureLock.read_text().splitlines() if l and not l.startswith('#') and not l.startswith('empty=')];assert fixtureCoords==[]
sbom=json.loads((OLD/'evidence/sbom.json').read_text(encoding='utf-8'));sbom['metadata']['component']['name']='VideoKit E13 source lifecycle Debug';sbom['metadata']['component']['version']='D1-20261018-E13';write(E/'sbom.json',sbom)
write(E/'sbom-difference.json',{'baseline':'E11 accepted','coordinates':35,'coordinateDelta':[],'lock':pin(lock),'nativeLibraries':native,'nativeDelta':[],'nativeRebuild':False,'downloads':0,'media3':'1.9.3','ffmpeg':'8.0.3','licenseClearance':'UNCHANGED_NOT_GRANTED','fixtureThirdPartyRuntimeCoordinates':0,'fixtureLockGeneratedByBuild':pin(fixtureLock),'fixtureSigningKeyIncluded':False})
write(E/'apk-audit.json',{'status':'PASS_LOCAL_APK_IDENTITY_AUDIT','apks':apks,'nativeLibraries':7,'mavenCoordinates':35,'appTestSameSigner':True,'fixtureDifferentSigner':True,'finalBuildInputsVerified':True,'deviceCalls':0,'AndroidExecution':'NOT_RUN','alignmentScope':'ZIP static alignment only; no actual 16KiB device runtime claim'})
print(json.dumps({'status':'PASS_LOCAL_APK_IDENTITY_AUDIT','apks':apks,'native':7,'coordinates':35}))
