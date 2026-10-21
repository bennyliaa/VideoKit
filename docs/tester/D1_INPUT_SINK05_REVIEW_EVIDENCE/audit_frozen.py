from pathlib import Path
import json,hashlib,zipfile,xml.etree.ElementTree as ET,re,collections,ast,struct,subprocess,datetime
R=Path('D:/CodexProjects/VideoKit');B=R/'docs/coder/d1input-sink05';E=Path(__file__).resolve().parent;OLD=R/'docs/coder/d1input-sink04'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def seal(p):
 d=load(p)
 for row in d['files']:
  f=R/row['path'];assert f.stat().st_size==row['bytes'] and sha(f)==row['sha256'],row['path']
 return d
s=B/'evidence/input-sink05-freeze.json';assert sha(s)=='ec7e5e9a8f38d2d1fe531592117f5db0a6d3481cd3ff89536d985f9dae173d96';d=seal(s)
assert sha(R/'docs/coder/D1_INPUT_SINK05_FIX_DELIVERY_V1.0.md')=='25503fe0f72310db4b22eeb23875fbdc17f782092ebd4e0bf132baf2fb3f82a7'
with zipfile.ZipFile(R/d['archive']['path']) as z:
 names=z.namelist();expected={r['path']:r for r in d['files'] if r['path']!=d['archive']['path']}
 assert set(names)==set(expected) and len(names)==len(set(names))==827
 for n in names:assert hashlib.sha256(z.read(n)).hexdigest()==expected[n]['sha256']
assert d['archive']['sha256']=='b387471995c555628baee54e0f56a3affd1782b36da2f6de1fd3425aa08fa5ab'
old=[]
for r in load(B/'evidence/frozen-baseline-preservation.json'):
 p=R/r['sealPath'];assert sha(p)==r['sealSha256'];x=seal(p);assert len(x['files'])==r['filesUnchanged'];old.append(dict(candidate=r['candidate'],files=len(x['files']),sealSha256=sha(p)))
assert sum(r['files'] for r in old)==3683
inputs=load(B/'evidence/final-source-dependency-inputs.json')
for r in inputs:
 p=B/r['path'];assert p.stat().st_size==r['bytes'] and sha(p)==r['sha256']
for p in (B/'deps').glob('*.jar'):assert p.read_bytes()==(OLD/'deps'/p.name).read_bytes()
for name in ['gradle/verification-metadata.xml','app/gradle.lockfile','settings-gradle.lockfile']:assert (B/name).read_bytes()==(OLD/name).read_bytes()
for folder in ['src','upstream']:
 for p in (B/folder).rglob('*.java'):
  rel=p.relative_to(B).as_posix()
  if rel not in ['src/com/videokit/d1input/TemporaryOutput.java','upstream/com/videokit/spike/c14/SinkCoordinator.java']:assert p.read_bytes()==(OLD/rel).read_bytes()
pins={};root=ET.parse(B/'gradle/verification-metadata.xml').getroot()
for c in root.iter():
 if c.tag.split('}')[-1]=='component':
  coord=':'.join(c.get(k) for k in ['group','name','version'])
  for a in c:
   if a.tag.split('}')[-1]=='artifact':pins[(coord,a.get('name'))]={x.get('value') for x in a if x.tag.split('}')[-1]=='sha256'}
assert any(x.tag.split('}')[-1]=='verify-metadata' and x.text=='true' for x in root.iter())
assert 'LockMode.STRICT' in (B/'app/build.gradle.kts').read_text()
rows=load(B/'evidence/actual-consumption/artifacts.json');events=[json.loads(x) for x in (B/'evidence/build-main-001/consumption.jsonl').read_text().splitlines() if x.strip()];ev={x['id']:x for x in events if x['name']=='Dependency verification'};counts=collections.Counter()
for r in rows:
 assert r['sha256'] in pins[(r['coordinate'],r['artifact'])]
 assert sha(B/r['path'])==r['sha256']
 if 'reviewCopy' in r:assert sha(B/r['reviewCopy'])==r['sha256']
 x=ev[r['verificationEventId']];m=re.fullmatch(r'Verifying (.+) \(([^:]+):([^:]+):(.+)\)',x['progressName']);artifact,g,a,v=m.groups();assert artifact==r['artifact'] and ':'.join([g,a,v])==r['coordinate'];counts[r['kind']]+=1
assert dict(counts)==dict(binary=121,module=35,pom=140)
coords={x.split('=')[0] for x in (B/'app/gradle.lockfile').read_text().splitlines() if x and not x.startswith(('#','empty='))};assert len(coords)==15
tree=ast.parse((R/'docs/tester/D1_INPUT_SINK01_REVIEW_EVIDENCE/audit_frozen.py').read_text());defs=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['pool','axml','dexclasses']];exec(compile(ast.Module(body=defs,type_ignores=[]),'reused_binary_parser','exec'))
apk=B/'artifacts/input-sink05-compile-probe-debug.apk';jar=B/'artifacts/input-sink05-classes.jar'
assert sha(apk)=='0b5fc8d530c8159c9283d670472255b883d97ad3885e2bae8fd427d25c1148b7' and sha(jar)=='6fbf307a4f0a06f45606ad9a162fcad95330924c2f220b5f68cec1e851916b0b'
with zipfile.ZipFile(apk) as z:
 tags=axml(z.read('AndroidManifest.xml'));classes=[c for n in z.namelist() if n.endswith('.dex') for c in dexclasses(z.read(n))]
 assert not any(t['tag'] in ['uses-permission','activity','service','provider','receiver'] for t in tags)
 assert tags[0]['attributes']['versionCode']==5 and tags[0]['attributes']['package']=='com.videokit.d1input'
 assert not any(n.startswith('lib/') and n.endswith('.so') for n in z.namelist())
 assert not any(any(x in c for x in ['InputSinkCheck','ReturnBoundaryCheck','IndependentFixCheck','ExceptionMatrixCheck','CancellationRegression','InputExceptionCheck']) for c in classes)
 assert not any(c in ['Landroid/net/Uri;','Landroid/system/ErrnoException;','Landroid/system/OsConstants;'] for c in classes)
 for c in ['HostDataSource','HostInputFactory','TemporaryOutput','AndroidGrantedStream','MatureMuxerBinding']:assert 'Lcom/videokit/d1input/'+c+';' in classes
with zipfile.ZipFile(jar) as z:assert not any('InputSinkCheck' in n or 'ReturnBoundaryCheck' in n or n.startswith('android/') for n in z.namelist());jarEntries=len(z.namelist())
out=dict(result='PASS_FROZEN_IDENTITY_STATIC_ARTIFACT_DEPENDENCY_AUDIT',candidateFiles=len(d['files']),zipMembers=len(names),oldFrozen=old,oldFrozenFiles=3683,inputPins=len(inputs),runtimeCoordinates=len(coords),actualConsumption=dict(counts),eventRows=len(events),apkManifest=tags,apkClassCount=len(classes),jarEntries=jarEntries,newDependencies=0,originalInputAdaptersUnchanged=True,SDKOrDeviceOrGradleCommands=0)
(E/'frozen-audit.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
# Independent JDK verifier, existing pinned official library; no SDK command or cache mutation.
src=E/'VerifySignature.java';src.write_bytes((R/'docs/tester/D1_INPUT_SINK01_REVIEW_EVIDENCE/VerifySignature.java').read_bytes());C=E/'signature-classes';C.mkdir(exist_ok=False);J=Path('D:/Android/Android Studio/jbr/bin');sig=B/'offline-maven/com/android/tools/build/apksig/9.3.3/apksig-9.3.3.jar'
for i,args in enumerate([[str(J/'javac.exe'),'--release','11','-cp',str(sig),'-d',str(C),str(src)],[str(J/'java.exe'),'-cp',str(C)+';'+str(sig),'VerifySignature',str(apk)]]):
 p=subprocess.run(args,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=45);(E/f'signature-{i}.stdout').write_bytes(p.stdout);(E/f'signature-{i}.stderr').write_bytes(p.stderr);(E/f'signature-{i}.json').write_text(json.dumps(dict(argv=args,exitCode=p.returncode,originalProcessReturned=True,SDKCommand=False),indent=2),encoding='utf8');assert p.returncode==0,p.stderr.decode('utf8','replace')
print(json.dumps({k:v for k,v in out.items() if k!='apkManifest'},ensure_ascii=False,indent=2));print((E/'signature-1.stdout').read_text())
