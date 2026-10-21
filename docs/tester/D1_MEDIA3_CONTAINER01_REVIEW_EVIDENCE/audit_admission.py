from pathlib import Path
import json,hashlib,zipfile,xml.etree.ElementTree as ET,re,collections,ast,struct,subprocess
R=Path('D:/CodexProjects/VideoKit');B=R/'docs/coder/d1media3-container01';OLD=R/'docs/coder/d1input-sink05';E=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def verifySeal(p):
 d=load(p)
 for row in d['files']:f=R/row['path'];assert f.stat().st_size==row['bytes'] and sha(f)==row['sha256'],row['path']
 return d
s=B/'evidence/media3-container01-freeze.json';assert sha(s)=='6d08e618dd1b98852830468a69b5048f65b55f4bc0a9117360c7bd414423c4ed';d=verifySeal(s);assert len(d['files'])==1045
assert sha(R/'docs/coder/D1_MEDIA3_CONTAINER01_DELIVERY_V1.0.md')=='18137c21ad6806b13d1a8d0a8b818b5be1b0db20ba7b07067900cda6018dfca7'
with zipfile.ZipFile(R/d['archive']['path']) as z:
 expected={r['path']:r for r in d['files'] if r['path']!=d['archive']['path']};names=z.namelist();assert len(names)==len(set(names))==1044 and set(names)==set(expected)
 for n in names:assert hashlib.sha256(z.read(n)).hexdigest()==expected[n]['sha256']
oldfiles=0
for row in load(B/'evidence/frozen-baseline-preservation.json'):
 assert sha(R/row['sealPath'])==row['sealSha256'];oldfiles+=len(verifySeal(R/row['sealPath'])['files'])
assert oldfiles==4511
inputs=load(B/'evidence/final-source-dependency-inputs.json')
for r in inputs:assert sha(B/r['path'])==r['sha256']
def pinmap(p):
 root=ET.parse(p).getroot();pins={}
 for c in root.iter():
  if c.tag.split('}')[-1]=='component':
   coord=':'.join(c.get(k) for k in ['group','name','version'])
   for a in c:
    if a.tag.split('}')[-1]=='artifact':pins[(coord,a.get('name'))]={x.get('value') for x in a if x.tag.split('}')[-1]=='sha256'}
 assert any(x.tag.split('}')[-1]=='verify-metadata' and x.text=='true' for x in root.iter());return pins
pins=pinmap(B/'gradle/verification-metadata.xml');oldpins=pinmap(OLD/'gradle/verification-metadata.xml')
assert all(pins[k]==v for k,v in oldpins.items());added=set(pins)-set(oldpins);assert added=={('androidx.media3:media3-extractor:1.9.3','media3-extractor-1.9.3.pom'),('androidx.media3:media3-decoder:1.9.3','media3-decoder-1.9.3.pom')}
admissions=[];F=B/'reference/official-extractor';ns={'m':'http://maven.apache.org/POM/4.0.0'}
for r in load(B/'evidence/extractor-source-admission.json')['records']:
 g,n,v=r['coordinate'].split(':');folder=B/'offline-maven'/g.replace('.','/')/n/v;pom=F/(n+'-'+v+'.pom');meta=F/(n+'-'+v+'.module');aar=folder/(n+'-'+v+'.aar');jar=B/'deps'/(n+'.jar')
 for p,key in [(pom,'pomSha256'),(meta,'moduleSha256'),(aar,'aarSha256'),(jar,'classesJarSha256')]:assert sha(p)==r[key]
 assert sha(pom) in pins[(r['coordinate'],pom.name)] and sha(meta) in oldpins[(r['coordinate'],meta.name)] and sha(aar) in oldpins[(r['coordinate'],aar.name)]
 assert meta.read_bytes()==(folder/meta.name).read_bytes();module=load(meta)
 assert module['component']['group']==g and module['component']['module']==n and module['component']['version']==v
 for variant in module['variants']:
  for item in variant.get('files',[]):
   if item['name']==aar.name:assert item['sha256']==sha(aar) and item['size']==aar.stat().st_size
 x=ET.parse(pom).getroot();assert [x.find('m:'+tag,ns).text for tag in ['groupId','artifactId','version']]==[g,n,v];assert any('Apache' in a.text for a in x.findall('m:licenses/m:license/m:name',ns))
 assert sha(F/'LICENSE')==r['licenseSha256']=='cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30'
 assert r['officialBase']=='https://dl.google.com/dl/android/maven2/'+g.replace('.','/')+'/'+n+'/'+v+'/'
 with zipfile.ZipFile(aar) as z:assert hashlib.sha256(z.read('classes.jar')).hexdigest()==sha(jar)
 admissions.append(dict(coordinate=r['coordinate'],result='PASS_IDENTITY_LICENSE_FOR_THIS_LIMITED_OFFLINE_USE',sourceRecordAndPreservedPomModuleLicenseVerified=True,oldBinaryModulePinsUnchanged=True,newPomPin=sha(pom),platformAdmission=False))
for p in (OLD/'deps').glob('*.jar'):assert p.read_bytes()==(B/'deps'/p.name).read_bytes()
assert (B/'settings-gradle.lockfile').read_bytes()==(OLD/'settings-gradle.lockfile').read_bytes() and 'LockMode.STRICT' in (B/'app/build.gradle.kts').read_text()
def coords(p):return {x.split('=')[0] for x in p.read_text().splitlines() if x and not x.startswith(('#','empty='))}
assert len(coords(B/'app/gradle.lockfile'))==17 and coords(B/'app/gradle.lockfile')-coords(OLD/'app/gradle.lockfile')=={r['coordinate'] for r in admissions}
rows=load(B/'evidence/actual-consumption/artifacts.json');events=[json.loads(x) for x in (B/'evidence/build-main-004/consumption.jsonl').read_text().splitlines() if x.strip()];ev={x['id']:x for x in events if x['name']=='Dependency verification'};counts=collections.Counter()
for r in rows:
 assert r['sha256'] in pins[(r['coordinate'],r['artifact'])] and sha(B/r['path'])==r['sha256']
 if 'reviewCopy' in r:assert sha(B/r['reviewCopy'])==r['sha256']
 m=re.fullmatch(r'Verifying (.+) \(([^:]+):([^:]+):(.+)\)',ev[r['verificationEventId']]['progressName']);artifact,g,a,v=m.groups();assert artifact==r['artifact'] and ':'.join([g,a,v])==r['coordinate'];counts[r['kind']]+=1
assert dict(counts)==dict(binary=123,module=37,pom=140)
oldRows={(r['coordinate'],r['artifact']):r['sha256'] for r in load(OLD/'evidence/actual-consumption/artifacts.json')};newRows={(r['coordinate'],r['artifact']):r['sha256'] for r in rows};assert all(newRows[k]==v for k,v in oldRows.items());newActual=set(newRows)-set(oldRows);assert len(newActual)==4 and all(k[0] in {a['coordinate'] for a in admissions} and k[1].endswith(('.aar','.module')) for k in newActual)
for folder in ['src','android','upstream','platform-fixtures']:
 for p in (OLD/folder).rglob('*.java'):
  rel=p.relative_to(OLD);assert rel.as_posix()=='src/com/videokit/d1input/TemporaryOutput.java' or p.read_bytes()==(B/rel).read_bytes()
tree=ast.parse((R/'docs/tester/D1_INPUT_SINK01_REVIEW_EVIDENCE/audit_frozen.py').read_text());defs=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['pool','axml','dexclasses']];exec(compile(ast.Module(body=defs,type_ignores=[]),'reused_artifact_parser','exec'))
apk=B/'artifacts/media3-container01-compile-probe-debug.apk';jar=B/'artifacts/media3-container01-classes.jar';assert sha(apk)=='0979fc8fc8428f5ee8ada6fb4859450aa8a39f5acd67bba0d7872310bb7ea3aa' and sha(jar)=='57f07b9f841487a5e76750ed0380656f72862e60caeef78a4ae9cb40d42e527e'
with zipfile.ZipFile(apk) as z:
 tags=axml(z.read('AndroidManifest.xml'));classes=[c for n in z.namelist() if n.endswith('.dex') for c in dexclasses(z.read(n))];assert tags[0]['attributes']['versionCode']==6 and tags[0]['attributes']['package']=='com.videokit.d1input';assert not any(t['tag'] in ['uses-permission','activity','service','provider','receiver'] for t in tags);assert not any(n.startswith('lib/') and n.endswith('.so') for n in z.namelist())
 checks={p.stem for p in (B/'checks/com/videokit/d1input').glob('*.java')};assert not any('/'+n+';' in c or '/'+n+'$' in c for c in classes for n in checks);assert not any(c in ['Landroid/net/Uri;','Landroid/system/ErrnoException;','Landroid/system/OsConstants;'] for c in classes)
with zipfile.ZipFile(jar) as z:assert not any('/'+n+'.class' in c or '/'+n+'$' in c for c in z.namelist() for n in checks);jarEntries=len(z.namelist())
sample=load(B/'reference/approved-sample-scope.json');sp=R/sample['path'];assert sp.stat().st_size==sample['bytes'] and sha(sp)==sample['sha256'] and sample['readOnly'] and sample['writeAdmission']=='DENIED_FIXTURE_MISMATCH'
out=dict(result='PASS_FROZEN_IDENTITY_AND_LIMITED_NEW_USE_ADMISSION',frozenFiles=1045,archiveMembers=1044,oldFrozenFiles=4511,inputPins=len(inputs),runtimeCoordinates=17,admissions=admissions,newPins=[list(k) for k in sorted(added)],actualConsumption=dict(counts),newActualConsumption=[list(k) for k in sorted(newActual)],events=len(events),apkManifest=tags,apkClassCount=len(classes),jarEntries=jarEntries,referenceSampleBefore=dict(path=sample['path'],bytes=sp.stat().st_size,sha256=sha(sp)),networkSdkGradleCalls=0)
(E/'admission-and-artifact-audit.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
J=Path('D:/Android/Android Studio/jbr/bin');src=E/'VerifySignature.java';src.write_bytes((R/'docs/tester/D1_INPUT_SINK01_REVIEW_EVIDENCE/VerifySignature.java').read_bytes());C=E/'signature-classes';C.mkdir(exist_ok=False);sig=B/'offline-maven/com/android/tools/build/apksig/9.3.3/apksig-9.3.3.jar'
for i,args in enumerate([[str(J/'javac.exe'),'--release','11','-cp',str(sig),'-d',str(C),str(src)],[str(J/'java.exe'),'-cp',str(C)+';'+str(sig),'VerifySignature',str(apk)]]):
 p=subprocess.run(args,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=40);(E/f'signature-{i}.stdout').write_bytes(p.stdout);(E/f'signature-{i}.stderr').write_bytes(p.stderr);(E/f'signature-{i}.json').write_text(json.dumps(dict(argv=args,exitCode=p.returncode,originalProcessReturned=True),indent=2),encoding='utf8');assert p.returncode==0
print(json.dumps({k:v for k,v in out.items() if k not in ['apkManifest','admissions']},ensure_ascii=False,indent=2));print('NEW EXTRACTOR/DECODER LIMITED SOURCE IDENTITY LICENSE ADMISSION PASSED BEFORE REVIEW RUNTIME')
