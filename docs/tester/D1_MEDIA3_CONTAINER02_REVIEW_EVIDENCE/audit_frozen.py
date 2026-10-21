from pathlib import Path
import hashlib,json,zipfile,ast,struct,re,collections,subprocess,datetime
R=Path('D:/CodexProjects/VideoKit');E=Path(__file__).resolve().parent;B=R/'docs/coder/d1media3-container02';OLD=R/'docs/coder/d1media3-container01'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def verify(rows,base=R):
 for r in rows:
  p=base/r['path'];assert p.stat().st_size==r['bytes'] and sha(p)==r['sha256'],r['path']
seal=B/'evidence/media3-container02-freeze.json';assert sha(seal)=='0bff92319ac4ec9130574db358f644c35d99f145a75fdaf2b3f7b4521f4ae06d'
assert sha(R/'docs/coder/D1_MEDIA3_CONTAINER02_FIX_DELIVERY_V1.0.md')=='cfe817dd8d966f4cebdc8710a243d47b217f1ff16139f6099de91b29029efbc6'
d=load(seal);verify(d['files']);assert len(d['files'])==676
with zipfile.ZipFile(R/d['archive']['path']) as z:
 rows={r['path']:r for r in d['files'] if r['path']!=d['archive']['path']};assert len(z.namelist())==len(set(z.namelist()))==675 and set(z.namelist())==set(rows)
 for n,r in rows.items():assert hashlib.sha256(z.read(n)).hexdigest()==r['sha256']
oldCount=0
for r in load(B/'evidence/frozen-baseline-preservation.json'):
 assert sha(R/r['sealPath'])==r['sealSha256'];old=load(R/r['sealPath']);verify(old['files']);oldCount+=len(old['files'])
assert oldCount==5556
oldEvidence=[]
for name,manifest in [('D1_MEDIA3_CONTAINER01_REVIEW_EVIDENCE','review-evidence-manifest.json'),('D1_MEDIA3_CONTAINER01_PHASE_A_EVIDENCE','phase-a-evidence-manifest.json'),('D1_INPUT_SINK05_REVIEW_EVIDENCE','review-evidence-manifest.json')]:
 old=load(E.parent/name/manifest);verify(old['evidenceFiles']);assert sha(R/old['report'])==old['reportSha256'];oldEvidence.append(dict(name=name,files=len(old['evidenceFiles']),reportSha256=old['reportSha256']))
pins=load(B/'evidence/final-source-dependency-inputs.json');verify(pins,B)
for rel in ['app/gradle.lockfile','settings-gradle.lockfile','gradle/verification-metadata.xml']:
 assert (B/rel).read_bytes()==(OLD/rel).read_bytes()
for folder in ['deps','reference/official-extractor','offline-maven','platform-fixtures','src','android','upstream']:
 for p in (OLD/folder).rglob('*'):
  if p.is_file():
   rel=p.relative_to(OLD)
   if rel.as_posix()!='src/com/videokit/d1input/TemporaryOutput.java':assert p.read_bytes()==(B/rel).read_bytes(),str(rel)
for folder in ['src','android','upstream','platform-fixtures']:
 assert {p.relative_to(OLD/folder) for p in (OLD/folder).rglob('*.java')}=={p.relative_to(B/folder) for p in (B/folder).rglob('*.java')}
assert (B/'reference/D1_MEDIA3_CONTAINER01_PHASE_B_REVIEW_REPORT_V1.0.md').read_bytes()==(E.parent/'D1_MEDIA3_CONTAINER01_PHASE_B_REVIEW_REPORT_V1.0.md').read_bytes()
assert 'LockMode.STRICT' in (B/'app/build.gradle.kts').read_text()
newRows=load(B/'evidence/actual-consumption/artifacts.json');oldRows=load(OLD/'evidence/actual-consumption/artifacts.json');identity=lambda rows:{(r['coordinate'],r['artifact']):r['sha256'] for r in rows}
assert identity(newRows)==identity(oldRows) and len(newRows)==300
events=[json.loads(x) for x in (B/'evidence/build-main-001/consumption.jsonl').read_text().splitlines() if x.strip()];ev={x['id']:x for x in events if x['name']=='Dependency verification'}
counts=collections.Counter()
for r in newRows:
 assert sha(B/r['path'])==r['sha256'];counts[r['kind']]+=1
 if 'reviewCopy' in r:assert sha(B/r['reviewCopy'])==r['sha256']
 m=re.fullmatch(r'Verifying (.+) \(([^:]+):([^:]+):(.+)\)',ev[r['verificationEventId']]['progressName']);a,g,n,v=m.groups();assert a==r['artifact'] and ':'.join([g,n,v])==r['coordinate']
assert dict(counts)==dict(binary=123,module=37,pom=140)
tree=ast.parse((R/'docs/tester/D1_INPUT_SINK01_REVIEW_EVIDENCE/audit_frozen.py').read_text());defs=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['pool','axml','dexclasses']];exec(compile(ast.Module(body=defs,type_ignores=[]),'reused_artifact_parser','exec'))
apk=B/'artifacts/media3-container02-compile-probe-debug.apk';jar=B/'artifacts/media3-container02-classes.jar';assert apk.stat().st_size==7094375 and sha(apk)=='51d163ae79e4b3f92ca9417267806290b3924f66aba3f5871442a0c1d081c871';assert jar.stat().st_size==108666 and sha(jar)=='757e53a49d92a9b2148417e0b37ed9680162a7709b1493029759e58ce08dfd8f'
with zipfile.ZipFile(apk) as z:
 tags=axml(z.read('AndroidManifest.xml'));classes=[c for n in z.namelist() if n.endswith('.dex') for c in dexclasses(z.read(n))];assert tags[0]['attributes']['versionCode']==7 and tags[0]['attributes']['package']=='com.videokit.d1input';assert not any(t['tag'] in ['uses-permission','activity','service','provider','receiver'] for t in tags);assert not any(n.startswith('lib/') and n.endswith('.so') for n in z.namelist())
 checks={p.stem for p in (B/'checks/com/videokit/d1input').glob('*.java')};assert not any('/'+n+';' in c or '/'+n+'$' in c for c in classes for n in checks);assert not any(c in ['Landroid/net/Uri;','Landroid/system/ErrnoException;','Landroid/system/OsConstants;'] for c in classes)
with zipfile.ZipFile(jar) as z:assert not any('/'+n+'.class' in c or '/'+n+'$' in c for c in z.namelist() for n in checks);jarEntries=len(z.namelist())
scope=load(B/'reference/approved-sample-scope.json');sample=R/scope['path'];assert sample.stat().st_size==scope['bytes'] and sha(sample)==scope['sha256']
J=Path('D:/Android/Android Studio/jbr/bin');src=E/'VerifySignature.java';src.write_bytes((E.parent/'D1_MEDIA3_CONTAINER01_REVIEW_EVIDENCE/VerifySignature.java').read_bytes());C=E/'signature-classes';C.mkdir(exist_ok=False);sig=B/'offline-maven/com/android/tools/build/apksig/9.3.3/apksig-9.3.3.jar'
for i,argv in enumerate([[str(J/'javac.exe'),'--release','11','-cp',str(sig),'-d',str(C),str(src)],[str(J/'java.exe'),'-cp',str(C)+';'+str(sig),'VerifySignature',str(apk)]]):
 p=subprocess.run(argv,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=40);(E/f'signature-{i}.stdout').write_bytes(p.stdout);(E/f'signature-{i}.stderr').write_bytes(p.stderr);(E/f'signature-{i}.json').write_text(json.dumps(dict(argv=argv,exitCode=p.returncode,originalProcessReturned=True),indent=2),encoding='utf8');assert p.returncode==0
out=dict(result='PASS_FROZEN_IDENTITY_AND_INHERITED_LIMITED_ADMISSION',checkedUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),frozenFiles=676,zipMembers=675,oldFrozenFiles=oldCount,oldEvidence=oldEvidence,inputPins=len(pins),actualConsumption=dict(counts),events=len(events),dependenciesLocksPinsLicenseByteIdentical=True,newProductionFiles=0,onlyProductionChange='TemporaryOutput.java',apkManifest=tags,apkClasses=len(classes),jarEntries=jarEntries,sampleBefore=dict(path=scope['path'],bytes=sample.stat().st_size,sha256=sha(sample)),sdkAdbGradleNetworkCalls=0)
(E/'admission-and-artifact-audit.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps({k:v for k,v in out.items() if k not in ['apkManifest']},indent=2))
