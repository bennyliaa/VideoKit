from pathlib import Path
import hashlib,json,zipfile,struct,datetime,re
R=Path('D:/CodexProjects/VideoKit');E=Path(__file__).resolve().parent;B=R/'docs/coder/d1fixture-tool01'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(n,x):(E/n).write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf8')
seal=B/'evidence/fixture-tool01-freeze.json';assert sha(seal)=='f12b646ce6afd66091f59f509c6d46fc62e343e16671d749225242fa9d6a2670';assert sha(R/'docs/coder/D1_FIXTURE_TOOL01_BUILD_DELIVERY_V1.0.md')=='85553ab27c1a6bfe9880f1f1123a983c5352a9cd952553f9314702ccee702251'
d=load(seal)
for r in d['files']:p=R/r['path'];assert p.stat().st_size==r['bytes'] and sha(p)==r['sha256']
assert len(d['files'])==1753
with zipfile.ZipFile(R/d['archive']['path']) as z:
 expected={r['path']:r for r in d['files'] if r['path']!=d['archive']['path']};assert len(z.namelist())==len(set(z.namelist()))==1752 and set(z.namelist())==set(expected)
 for n,row in expected.items():assert hashlib.sha256(z.read(n)).hexdigest()==row['sha256']
sourcePins=load(B/'evidence/source-input-pins.json');assert len(sourcePins)==711 and sum(x['bytes'] for x in sourcePins)==4465907
for r in sourcePins:p=B/r['path'];assert p.stat().st_size==r['bytes'] and sha(p)==r['sha256']
with zipfile.ZipFile(B/'reference/jcodec-0.2.5-sources.jar') as z:
 assert hashlib.sha256((B/'reference/jcodec-0.2.5-sources.jar').read_bytes()).hexdigest()=='9945efa92e16b3fbe8eb8bf37f00be53fa0adb52d09ac978a0744ca2ef3697db'
 js={n for n in z.namelist() if n.endswith('.java')};assert len(js)==708
 for n in js:assert (B/'source'/n).read_bytes()==z.read(n)
compiler=load(B/'evidence/compiler-identity.json')
for r in compiler['files']:p=Path(r['path']);assert p.stat().st_size==r['bytes'] and sha(p)==r['sha256']
recipe=load(B/'evidence/build-recipe.json');result=load(B/'evidence/build-result.json');assert result['compilerInvocations']==result['jarInvocations']==1 and result['runtimeCalls']==result['newMediaFiles']==0
assert [x['tool'] for x in result['tools']]==['javac','jar'] and len(recipe['commands'])==2
for i,kind in enumerate(['javac','jar']):
 o=load(B/f'evidence/build-001/{kind}-owner.json');assert o==result['tools'][i] and o['argv']==recipe['commands'][i] and o['originalProcessReturned'] and o['outputHandlesClosed'] and o['exitCode']==0 and not o['timedOutSticky'] and o['terminationActions']==0
 if kind=='javac':
  assert '-proc:none' in o['argv'] and '-implicit:none' in o['argv'] and '--release' in o['argv'] and '-J-Xmx512m' in o['argv']
  for flag in ['-classpath','-sourcepath','-processorpath']:
   p=Path(o['argv'][o['argv'].index(flag)+1]);assert p.is_dir() and not any(p.iterdir())
 else:assert '--date=2026-10-21T00:00:00Z' in o['argv'] and o['argv'][o['argv'].index('--main-class')+1]=='com.videokit.fixturetool.SixFrameDriver'
args=B/recipe['sourceArgFile'];assert sha(args)==recipe['sourceArgFileSha256'];argpaths=[Path(s.strip('"')) for s in args.read_text().splitlines() if s];assert set(argpaths)=={B/r['path'] for r in sourcePins} and len(argpaths)==711
for r in load(B/'evidence/build-001/prebuild-all-candidate-input-pins.json'):assert sha(B/r['path'])==r['sha256']
actualOutput=0
for r in result['actualBuildOutputFiles']:p=B/r['path'];assert p.stat().st_size==r['bytes'] and sha(p)==r['sha256'];actualOutput+=r['bytes']
assert actualOutput==result['actualBuildOutputBytesAtNaturalReturn']==5947592
allFrozenBytes=sum(r['bytes'] for r in d['files']);assert allFrozenBytes<67108864
def classInfo(b):
 assert b[:4]==b'\xca\xfe\xba\xbe';minor,major,n=struct.unpack_from('>HHH',b,4);cp=[None]*n;p=10;i=1
 while i<n:
  tag=b[p];p+=1
  if tag==1:l=struct.unpack_from('>H',b,p)[0];p+=2;cp[i]=b[p:p+l].decode('utf8','replace');p+=l
  elif tag in [7,8,16,19,20]:cp[i]=struct.unpack_from('>H',b,p)[0];p+=2
  elif tag in [3,4,9,10,11,12,17,18]:p+=4
  elif tag in [5,6]:p+=8;i+=1
  elif tag==15:p+=3
  else:raise AssertionError(tag)
  i+=1
 access,this,sup=struct.unpack_from('>HHH',b,p);p+=6;cls=cp[cp[this]];interfaces=struct.unpack_from('>H',b,p)[0];p+=2+2*interfaces;codes={}
 for memberKind in ['field','method']:
  cnt=struct.unpack_from('>H',b,p)[0];p+=2
  for k in range(cnt):
   flags,name,desc,num=struct.unpack_from('>HHHH',b,p);p+=8
   for j in range(num):
    a,l=struct.unpack_from('>HI',b,p);p+=6
    if memberKind=='method' and cp[a]=='Code':codes[cp[name]+cp[desc]]=hashlib.sha256(b[p:p+l]).hexdigest()
    p+=l
 num=struct.unpack_from('>H',b,p)[0];p+=2;source=None
 for j in range(num):
  a,l=struct.unpack_from('>HI',b,p);p+=6
  if cp[a]=='SourceFile':source=cp[struct.unpack_from('>H',b,p)[0]]
  p+=l
 return dict(className=cls,sourceFile=source,major=major,methodCodeSha256=codes)
jar=B/'artifacts/videokit-fixture-tool01.jar';assert jar.stat().st_size==1948772 and sha(jar)=='af24b4aa66bed72957803f2ff44a8a45cd7c143d72441e3f640cb55490af9959'
origins=[];driverCode={}
with zipfile.ZipFile(jar) as z:
 names=[n for n in z.namelist() if not n.endswith('/')];classes=[n for n in names if n.endswith('.class')];assert len(classes)==982
 actual={p.relative_to(B/'build-output/classes').as_posix():p for p in (B/'build-output/classes').rglob('*.class')};assert set(classes)==set(actual)
 allowedResources={p.relative_to(B/'package-resources').as_posix():p for p in (B/'package-resources').rglob('*') if p.is_file()};assert set(names)==set(classes)|set(allowedResources)|{'META-INF/MANIFEST.MF'}
 assert 'Main-Class: com.videokit.fixturetool.SixFrameDriver' in z.read('META-INF/MANIFEST.MF').decode()
 for n,p in allowedResources.items():assert z.read(n)==p.read_bytes()
 for n in classes:
  b=z.read(n);assert b==actual[n].read_bytes();c=classInfo(b);assert c['major']==55 and c['className']+'.class'==n
  suffix=c['className'].rsplit('/',1)[0]+'/'+c['sourceFile'];matches=[r for r in sourcePins if r['path'].endswith('/'+suffix)];assert len(matches)==1,(n,suffix)
  origins.append(dict(className=c['className'],source=matches[0]['path'],sourceSha256=matches[0]['sha256'],classSha256=hashlib.sha256(b).hexdigest(),major=55,sourceFile=c['sourceFile']))
  if n.startswith('com/videokit/fixturetool/'):driverCode[n]=c
 assert not any(n.lower().endswith(('.dll','.so','.exe')) for n in names)
save('independent-class-origin.json',dict(result='PASS_STATIC_CLASS_SOURCE_AND_ACTUAL_JAVAC_BYTES',classes=origins,driverMethodCode=driverCode,runtimeInitialization=False))
licenses=load(B/'evidence/source-license-inventory.json');assert len(licenses)==711
notices=(B/'licenses/SOURCE_NOTICES.txt').read_text();assert '2007 The Guava Authors' in notices and 'Public Domain license' in notices and 'FreeBSD' in notices and (B/'licenses/Apache-2.0.txt').stat().st_size>10000
oldCount=0
for r in load(B/'evidence/prior-frozen-preservation.json'):
 assert sha(R/r['sealPath'])==r['sha256']
 for row in load(R/r['sealPath'])['files']:assert sha(R/row['path'])==row['sha256'];oldCount+=1
assert oldCount==6972
oldEvidence=[]
for r in load(B/'evidence/prior-independent-preservation.json'):
 p=R/r['path'];assert sha(p)==r['sha256'];v=load(p);assert sha(R/v['report'])==v['reportSha256']
 for row in v['evidenceFiles']:assert sha(R/row['path'])==row['sha256']
 oldEvidence.append(dict(path=r['path'],files=len(v['evidenceFiles'])))
save('independent-material-audit.json',dict(result='PASS_IDENTITY_BUILD_AND_SOURCE_BYTES_ONLY_RUNTIME_NOT_RUN',checkedUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),frozenRecords=1753,zipMembers=1752,sources=711,unchangedUpstreamSources=708,sourceInputBytes=4465907,classes=982,jarBytes=1948772,jarSha256=sha(jar),buildActualOutputBytes=actualOutput,frozenCandidateBytesIncludingArchive=allFrozenBytes,buildOutputLimit=67108864,naturalBuildToolReturns=2,newReviewerJvmCompilerMainCalls=0,licenseResourcesMatched=True,oldFrozenFiles=6972,oldEvidence=oldEvidence,sourceDerivedFindings='SEPARATE_FINDINGS_FILE_NO_DYNAMIC_REPRODUCTION',runtimeWrapperOrEncoder='NOT_RUN',oldOwnerQueriesOrInterventions=0))
print('PASS independent1753/ZIP1752,711 sources982classes, exact build2 original returns; Python only; runtime NOT_RUN')
