from pathlib import Path
import json,hashlib,zipfile,ast,struct,re,difflib,datetime
R=Path('D:/CodexProjects/VideoKit');E=Path(__file__).resolve().parent;B=R/'docs/coder/d1jcodec-observation01';OLD=R/'docs/coder/d1fixture-tool02'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf8'))
def save(n,x):(E/n).write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf8')
s=B/'evidence/observation01-freeze.json';assert sha(s)=='8a62ef8e4fcea016870daccfe92097903cde667e4d624892309e6984d44e0725';v=load(s)
assert sha(R/'docs/coder/D1_JCODEC_OBSERVATION01_DELIVERY_V1.0.md')=='4cb2aa84ff19eefb2c85a68c3c81210fb70286d3eb17c32d0cdba78ef8e06856'
assert len(v['files'])==len({x['path'] for x in v['files']})==2738
for x in v['files']:p=R/x['path'];assert p.stat().st_size==x['bytes'] and sha(p)==x['sha256']
archive=R/'docs/coder/D1-20261021-JCODEC-OBSERVATION01-source.zip';assert sha(archive)==v['archive']['sha256']=='0f6042bc2b10b7e6f256d30185c48b6a3f93676406576662ad5dbffbce367df7'
with zipfile.ZipFile(archive) as z:
 assert len(z.namelist())==len(set(z.namelist()))==2738 and set(z.namelist())=={x['path'] for x in v['files']}
 for x in v['files']:assert z.getinfo(x['path']).file_size==x['bytes'] and hashlib.sha256(z.read(x['path'])).hexdigest()==x['sha256']
base={p.relative_to(OLD/'source').as_posix():p for p in (OLD/'source').rglob('*.java')};new={p.relative_to(B/'source').as_posix():p for p in (B/'source').rglob('*.java')};assert set(base)==set(new) and len(base)==708
changes=[n for n in base if base[n].read_bytes()!=new[n].read_bytes()];allowed=['org/jcodec/containers/mp4/boxes/DataRefBox.java','org/jcodec/containers/mp4/boxes/SampleDescriptionBox.java','org/jcodec/codecs/h264/mp4/AvcCBox.java'];assert set(changes)==set(allowed)
def method(text,signature):
 at=text.index(signature);start=text.index('{',at);balance=1;end=start+1
 while balance:
  if text[end]=='{':balance+=1
  if text[end]=='}':balance-=1
  end+=1
 return text[start:end]
diffs=[]
for n in allowed:
 old=base[n].read_text();newtext=new[n].read_text()
 for signature in ['void doWrite(ByteBuffer','int estimateSize(']:assert method(old,signature)==method(newtext,signature)
 # Strip only explicitly added observation storage/reset/getters; legacy parse retained.
 op=method(old,'void parse(ByteBuffer');np=method(newtext,'void parse(ByteBuffer')
 if n.endswith('AvcCBox.java'):
  np=np.replace('originalConfigurationVersion = input.get() & 0xff;','NIOUtils.skip(input, 1);')
  np=np.replace('originalSpsCountByte = input.get() & 0xff;\n        int nSPS = originalSpsCountByte & 0x1f;','int nSPS = input.get() & 0x1f;')
 else:np=np.replace('originalVersionFlagsWord = input.getInt();','input.getInt();').replace('originalDeclaredEntryCount = input.getInt() & 0xffffffffL;','input.getInt();')
 np='\n'.join(line for line in np.splitlines() if not re.match(r'\s*original\w+\s*=',line))
 assert re.sub(r'\s+','',op)==re.sub(r'\s+','',np),(n,'LEGACY_PARSE_NOT_EXACT_AFTER_REMOVING_OBSERVATION')
 diffs.append(dict(path=n,beforeSha256=sha(base[n]),afterSha256=sha(new[n]),doWriteAndEstimateExactlyPreserved=True,legacyParseExactlyPreservedAfterObservationProjection=True))
tree=ast.parse((R/'docs/tester/D1_FIXTURE_TOOL01_BUILD_REVIEW_EVIDENCE/independent_static_audit.py').read_text());fs=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='classInfo'];exec(compile(ast.Module(body=fs,type_ignores=[]),'static_class_parser_only','exec'))
rows=load(B/'evidence/class-origin.json');assert len(rows)==980
jar=B/'artifacts/jcodec-0.2.5-videokit-observation01.jar';assert jar.stat().st_size==1930955 and sha(jar)=='1a7e8601be4ebb5665219f2ccfa6e75476323e7408a6b18824ecf2a37873de86'
origins=[];same=0;changedClasses=[]
with zipfile.ZipFile(jar) as z,zipfile.ZipFile(OLD/'artifacts/videokit-fixture-tool02.jar') as oldjar:
 names=set(z.namelist());assert sum(n.endswith('.class') for n in names)==977 and not any(n.startswith('com/videokit/') for n in names)
 manifest=z.read('META-INF/MANIFEST.MF').replace(b'\r\n ',b'');assert b'Implementation-Version: 0.2.5-videokit-observation01' in manifest and b'Main-Class:' not in manifest and b'f5f472b6bf6422832c66db4764a1a2d431be4c296c0f33d8bc3e853c2382f23c' in manifest
 for x in rows:
  p=B/x['compilerOutput'];b=p.read_bytes();ci=classInfo(b);assert sha(p)==sha(B/x['copy'])==x['sha256'] and sha(B/x['sourcePath'])==x['sourceSha256'] and ci['major']==55 and ci['sourceFile']==x['sourceFile'] and ci['className']==x['className']
  if x['testOnly']:assert x['jarEntry'] not in names
  else:
   assert z.read(x['jarEntry'])==b
   if oldjar.read(x['jarEntry'])==b:same+=1
   else:changedClasses.append(x['jarEntry'])
  origins.append(dict(className=ci['className'],sha256=x['sha256'],source=x['sourcePath'],sourceSha256=x['sourceSha256'],major=ci['major'],testOnly=x['testOnly']))
assert same==974 and set(changedClasses)=={n[:-5]+'.class' for n in allowed} and sum(x['testOnly'] for x in origins)==3
for name in ['Apache-2.0.txt','JCODEC-FreeBSD-LICENSE.txt']:assert (OLD/'licenses'/name).read_bytes()==(B/'licenses'/name).read_bytes()
def noticeEntries(p):
 text=p.read_text();matches=list(re.finditer(r'(?m)^((?:source|driver|checks)/\S+) SHA256 ([0-9a-f]{64})\s*$',text));out={}
 for j,m in enumerate(matches):out[m[1]]=(m[2],text[m.end():matches[j+1].start() if j+1<len(matches) else len(text)].strip())
 return out
oldNotices=noticeEntries(OLD/'licenses/SOURCE_NOTICES.txt');newNotices=noticeEntries(B/'licenses/SOURCE_NOTICES.txt')
for n in base:
 key='source/'+n;assert oldNotices[key][1]==newNotices[key][1] and newNotices[key][0]==sha(new[n])
for n in allowed:assert base[n].read_text().split('public class',1)[0]==new[n].read_text().split('public class',1)[0]
projectNotice=(B/'licenses/PROJECT-CODE-NOTICE.txt').read_text();assert 'observation modifications' in projectNotice and 'no product integration' in projectNotice
notice=(B/'licenses/MODIFICATION-NOTICE.txt').read_text();assert '0.2.5-videokit-observation01' in notice and 'NOT the official' in notice and 'f5f472b6bf6422832c66db4764a1a2d431be4c296c0f33d8bc3e853c2382f23c' in notice
build=load(B/'evidence/build-result.json');assert build['compilerCalls']==build['jarCalls']==1
for o in build['owners']:assert o['exitCode']==0 and o['registeredBeforePopen'] and o['originalProcessReturned'] and o['outputHandlesClosed'] and not o['unknownSticky'] and o['terminationOrRetry']==0
owner=load(B/'evidence/metadata-001/owner.json');assert owner['exitCode']==1 and owner['originalProcessReturned'] and owner['outputHandlesClosed'] and not owner['unknownSticky']
stdout=(B/'evidence/metadata-001/stdout.raw').read_bytes();err=(B/'evidence/metadata-001/stderr.raw').read_bytes();assert len(stdout)==425 and len(err)==393 and b'Box$LeafBox.hasOriginalParseObservation()' in err
assert len([json.loads(x) for x in stdout.splitlines()])==3
save('independent-material-audit.json',dict(result='PASS_STATIC_MATERIALS_ORIGINAL_CODER_HELPER_FAILURE_PRESERVED',checkedUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),frozenRows=2738,zipUniqueMembers=2738,sourceJava=708,unchangedSources=705,patches=diffs,productionClasses=977,testOnlyClasses=3,originalClassBytesUnchanged=974,changedProductionClassEntries=changedClasses,actualClassOrigins=origins,coderCompileJarNaturalReturns=2,coderMetadataJvmExitCode=1,coderMetadataParseDifferentialCases=0,coderFreshCasesOnly=2,noRuntimeStartedByThisAudit=True,newMediaReads=0,toolJarSha256=sha(jar),coderFailureNotOverwritten=True))
print('PASS independent2738/ZIP2738; source705same/3patch; class974same/3patch; coderfailure preserved')
