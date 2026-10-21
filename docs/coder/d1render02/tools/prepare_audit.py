from pathlib import Path
import hashlib,json,copy
B=Path(__file__).resolve().parents[1];S=B.parent/'d1render01';E=B/'evidence'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
inputs=[]
for p in sorted(B.rglob('*')):
 if p.is_file() and (p.relative_to(B).parts[0] in ['src','android','upstream','gradle','native-libs','notice-assets','fixture-assets','offline-maven'] or p.relative_to(B).as_posix() in ['app/build.gradle.kts','app/gradle.lockfile','settings.gradle.kts','build.gradle.kts','gradle.properties','local.properties'] or p.is_relative_to(B/'app/src')):
  inputs.append({'path':p.relative_to(B).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)})
dump(E/'build-inputs-final.json',inputs)
dump(E/'offline-repository.json',{'files':[x for x in inputs if x['path'].startswith('offline-maven/')],'newEvidence':'evidence/new-metadata-pin.json','newBinaryDownloads':0})
old=json.loads((S/'evidence/render01-freeze.json').read_text(encoding='utf-8'))
assert all(sha(B.parents[2]/x['path'])==x['sha256'] for x in old['files'])
dump(E/'render01-preservation.json',{'allFrozenFilesUnchanged':len(old['files']),'render01SealSha256':sha(S/'evidence/render01-freeze.json'),'render01ArchiveSha256':old['archive']['sha256']})
same=[]
for folder in ['native-libs','fixture-assets','reused-native-source']:
 for p in sorted((B/folder).rglob('*')):
  if p.is_file():assert p.read_bytes()==(S/p.relative_to(B)).read_bytes();same.append({'path':p.relative_to(B).as_posix(),'sha256':sha(p),'unchanged':True})
assert (B/'app/gradle.lockfile').read_bytes()==(S/'app/gradle.lockfile').read_bytes()
dump(E/'reused-binary-lock-identity.json',{'files':same,'runtimeLockUnchanged':True,'runtimeComponents':35,'nativeRebuilds':0,'fixtureRebuilds':0})
text=(S/'tools/audit_artifacts.py').read_text(encoding='utf-8');start=text.index('art=B/');end=text.index('# Official,')
script='''from pathlib import Path
import hashlib,json,shutil,zipfile,struct,subprocess,xml.etree.ElementTree as ET
R=Path('D:/CodexProjects/VideoKit');B=R/'docs/coder/d1render02';E=B/'evidence/apk-audit';E.mkdir(exist_ok=False)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def out(n,v):(E/n).write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
'''+text[start:end].replace("'pausedSeekAndSurfaceRecreation']","'pausedSeekAndSurfaceRecreation','manualIdleListenThreeSeconds']")+'''
jar=B/'offline-maven/com/android/tools/build/apksig/9.3.3/apksig-9.3.3.jar'
repo=json.loads((B/'evidence/offline-repository.json').read_text(encoding='utf-8'))
pin=next(x for x in repo['files'] if x['path']==jar.relative_to(B).as_posix());assert sha(jar)==pin['sha256']
classes=E/'verifier-classes';classes.mkdir();J=Path('D:/Android/Android Studio/jbr/bin');receipts=[]
for name,argv in [('compile',[str(J/'javac.exe'),'--release','11','-encoding','UTF-8','-cp',str(jar),'-d',str(classes),str(B/'tools/VerifyApk.java')]),('verify',[str(J/'java.exe'),'-cp',str(classes)+';'+str(jar),'VerifyApk',*map(str,apks)])]:
 r=subprocess.run(argv,stdout=subprocess.PIPE,stderr=subprocess.PIPE);(E/(name+'.stdout')).write_bytes(r.stdout);(E/(name+'.stderr')).write_bytes(r.stderr);receipts.append({'name':name,'exitCode':r.returncode,'argv':argv,'originalProcessReturned':True});print(r.stdout.decode('utf-8',errors='replace'));assert r.returncode==0
out('signer-verification.json',{'apksigJar':pin,'commands':receipts,'usesSDKCommand':False,'privateKeysRead':False})
inputs=json.loads((B/'evidence/build-inputs-final.json').read_text(encoding='utf-8'));assert all(sha(B/x['path'])==x['sha256'] for x in inputs)
out('artifact-audit.json',{'result':'PASS_STATIC_BUILD_ARTIFACT_ONLY','artifacts':audits,'manifests':manifests,'inputsUnchanged':len(inputs),'deviceExecution':'NOT_RUN','static16KiBIsNotDevicePageTest':True})
print(json.dumps({'result':'PASS_STATIC_BUILD_ARTIFACT_ONLY','artifacts':[{k:v for k,v in x.items() if k!='natives'} for x in audits]},indent=2))
'''
(B/'tools/audit_artifacts.py').write_text(script,encoding='utf-8')
sbom=copy.deepcopy(json.loads((S/'render01-sbom.cdx.json').read_text(encoding='utf-8')))
sbom['metadata']['component']['version']='D1-20261020-RENDER02'
sbom['metadata']['component']['properties']=[{'name':'scope','value':'Internal Debug feasibility; D1 NOT_PASSED; Android NOT_RUN'},{'name':'metadataVerification','value':'true; strict; new Guava parent provenance PENDING_INDEPENDENT_REVIEW'},{'name':'binaryIdentity','value':'35 runtime lock and 7 native files identical to RENDER01'}]
dump(B/'render02-sbom.cdx.json',sbom)
