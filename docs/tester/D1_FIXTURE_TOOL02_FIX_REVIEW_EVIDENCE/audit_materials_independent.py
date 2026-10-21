from pathlib import Path
import hashlib,json,zipfile,ast,struct,datetime
R=Path('D:/CodexProjects/VideoKit');E=Path(__file__).resolve().parent;B=R/'docs/coder/d1fixture-tool02';OLD=R/'docs/coder/d1fixture-tool01'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
seal=B/'evidence/fixture-tool02-freeze.json';assert sha(seal)=='5dbf3359e0aa9b06a9024cf0ace91bd1e532ddbfdc37ba11d81f0716c01dc51d';assert sha(R/'docs/coder/D1_FIXTURE_TOOL02_FIX_DELIVERY_V1.0.md')=='ff875c5c0b7c6e589fd6704927b4e413b04236ae466dd51348b66f1026b3cf68';d=load(seal)
for x in d['files']:p=R/x['path'];assert p.stat().st_size==x['bytes'] and sha(p)==x['sha256']
assert len(d['files'])==2774
with zipfile.ZipFile(R/d['archive']['path']) as z:
 rows={x['path']:x for x in d['files'] if x['path']!=d['archive']['path']};assert len(z.namelist())==len(set(z.namelist()))==2773 and set(z.namelist())==set(rows)
 for n,x in rows.items():assert hashlib.sha256(z.read(n)).hexdigest()==x['sha256']
pins=load(B/'evidence/source-input-pins.json');assert len(pins)==713 and sum(x['bytes'] for x in pins)==4492852
for x in pins:p=B/x['path'];assert p.stat().st_size==x['bytes'] and sha(p)==x['sha256']
upstream=list((B/'source').rglob('*.java'));assert len(upstream)==708
for p in upstream:assert p.read_bytes()==(OLD/p.relative_to(B)).read_bytes()
assert (B/'driver/com/videokit/fixturetool/ReceiptJson.java').read_bytes()==(OLD/'driver/com/videokit/fixturetool/ReceiptJson.java').read_bytes()
for x in load(B/'evidence/compiler-identity.json')['files']:p=Path(x['path']);assert p.stat().st_size==x['bytes'] and sha(p)==x['sha256']
build=load(B/'evidence/build-result.json');assert build['compilerInvocations']==build['jarInvocations']==1 and build['runtimeCalls']==0
for o in build['tools']:assert o['exitCode']==0 and o['originalProcessReturned'] and o['outputHandlesClosed'] and not o['timedOutSticky'] and o['terminationActions']==0
total=0
for x in build['actualBuildOutputFiles']:p=B/x['path'];assert p.stat().st_size==x['bytes'] and sha(p)==x['sha256'];total+=x['bytes']
assert total==9578896
tree=ast.parse((R/'docs/tester/D1_FIXTURE_TOOL01_BUILD_REVIEW_EVIDENCE/independent_static_audit.py').read_text());f=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='classInfo'];exec(compile(ast.Module(body=f,type_ignores=[]),'read_only_class_parser','exec'))
origins=load(B/'evidence/class-origin02.json');assert len(origins)==990
jar=B/'artifacts/videokit-fixture-tool02.jar';assert sha(jar)=='c4ed36f31cab8381bc47c0aea4c3f3d8a9c2afab09991a04a83102877f1bfecd' and jar.stat().st_size==1954730
actual=[];prod=tests=0
with zipfile.ZipFile(jar) as z:
 names={n for n in z.namelist() if not n.endswith('/')};assert sum(n.endswith('.class') for n in names)==985
 resources={p.relative_to(B/'package-resources').as_posix():p for p in (B/'package-resources').rglob('*') if p.is_file()};assert names=={x['jarEntry'] for x in origins if not x['testOnly']}|set(resources)|{'META-INF/MANIFEST.MF'}
 for n,p in resources.items():assert z.read(n)==p.read_bytes()
 assert 'Main-Class: com.videokit.fixturetool.SixFrameDriver' in z.read('META-INF/MANIFEST.MF').decode()
 for x in origins:
  p=B/x['actualCompilerOutput'];copy=B/x['packageCopy'];b=p.read_bytes();assert sha(p)==sha(copy)==x['sha256'] and sha(B/x['sourcePath'])==x['sourceSha256'];c=classInfo(b);assert c['major']==55 and c['className']==x['className'] and c['sourceFile']==x['sourceFile']
  if x['testOnly']:tests+=1;assert x['jarEntry'] not in names
  else:prod+=1;assert z.read(x['jarEntry'])==b
  actual.append(dict(className=c['className'],source=x['sourcePath'],sourceSha256=x['sourceSha256'],classSha256=x['sha256'],testOnly=x['testOnly']))
assert prod==985 and tests==5
notices=(B/'licenses/SOURCE_NOTICES.txt').read_text();assert '2007 The Guava Authors' in notices and 'Public Domain license' in notices and 'FreeBSD' in notices
old=0
for row in load(B/'evidence/prior-frozen02.json'):
 assert sha(R/row['sealPath'])==row['sha256'];v=load(R/row['sealPath'])
 for x in v['files']:assert sha(R/x['path'])==x['sha256'];old+=1
assert old==8725
row=load(B/'evidence/prior-independent02.json');assert sha(R/row['manifestPath'])==row['sha256'];v=load(R/row['manifestPath']);assert sha(R/v['report'])==v['reportSha256']
for x in v['evidenceFiles']:assert sha(R/x['path'])==x['sha256']
footprint=sum(x['bytes'] for x in d['files']);assert footprint<67108864
out=dict(result='PASS_STATIC_ADMISSION_AND_PRODUCTION_TEST_SPLIT_BEFORE_OWN_HELPER',checkedUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),frozenRecords=2774,zipMembers=2773,sourceFiles=713,sourceBytes=4492852,unchangedUpstreamJava=708,productionClasses=prod,testClasses=tests,toolJarSha256=sha(jar),buildNaturalReturns=2,buildOutputBytes=total,frozenCandidateIncludingZipBytes=footprint,oldFrozenFiles=old,originalIndependentFailPreserved=True,noNewDependencyOrRuntimeEncoderAdmission=True,classOrigins=actual)
(E/'independent-material-audit.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8');print('PASS independent materials,985 production/5 excluded tests,8725 older freeze; own helper admitted ONLY for nonmedia scope')
