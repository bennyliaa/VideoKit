from pathlib import Path
import hashlib,json,zipfile,xml.etree.ElementTree as ET,struct,collections,subprocess,re
R=Path('D:/CodexProjects/VideoKit');B=R/'docs/coder/d1input-sink01';E=R/'docs/tester/D1_INPUT_SINK01_REVIEW_EVIDENCE'
def sha(b):return hashlib.sha256(b).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def checkfiles(seal):
 d=load(seal);rows=d['files']
 for r in rows:
  p=R/r['path'];b=p.read_bytes();assert len(b)==r['bytes'] and sha(b)==r['sha256'],r['path']
 return len(rows)
s=B/'evidence/input-sink01-freeze.json';assert sha(s.read_bytes())=='128113fd40b958b56823cb76b230833b5cc9a42aff0f0bcfab7a5db90038a238'
count=checkfiles(s);manifest=load(s);a=R/manifest['archive']['path']
with zipfile.ZipFile(a) as z:
 names=z.namelist();assert len(names)==len(set(names))==333
 expected={r['path']:r for r in manifest['files'] if r['path']!=manifest['archive']['path']}
 assert set(names)==set(expected)
 for n in names:assert sha(z.read(n))==expected[n]['sha256'],n
old=[]
for name,fn in [('d1render01','render01-freeze.json'),('d1render02','render02-freeze.json'),('d1render02-capture','capture-adapt-freeze.json')]:
 p=R/'docs/coder'/name/'evidence'/fn;old.append(dict(candidate=name,files=checkfiles(p),sealSha256=sha(p.read_bytes())))
inputs=load(B/'evidence/final-source-dependency-inputs.json')
for r in inputs:
 b=(B/r['path']).read_bytes();assert sha(b)==r['sha256'] and len(b)==r['bytes']
xml=B/'gradle/verification-metadata.xml';root=ET.parse(xml).getroot();pins={}
for c in root.iter():
 if c.tag.split('}')[-1]=='component':
  coord=':'.join(c.get(x) for x in ['group','name','version'])
  for art in c:
   if art.tag.split('}')[-1]=='artifact':pins[(coord,art.get('name'))]={x.get('value') for x in art if x.tag.split('}')[-1]=='sha256'}
assert any(x.tag.split('}')[-1]=='verify-metadata' and x.text=='true' for x in root.iter())
assert xml.read_bytes()==(R/'docs/coder/d1render02/gradle/verification-metadata.xml').read_bytes()
rows=load(B/'evidence/actual-consumption/artifacts.json');counts=collections.Counter()
for r in rows:
 assert r['sha256'] in pins[(r['coordinate'],r['artifact'])],r
 counts[r['kind']]+=1
 if 'reviewCopy' in r:assert sha((B/r['reviewCopy']).read_bytes())==r['sha256']
assert dict(counts)==dict(binary=121,module=35,pom=140)
events=[json.loads(x) for x in (B/'evidence/build-main-005/consumption.jsonl').read_text().splitlines() if x.strip()]
eventmap={x['id']:x for x in events if x['name']=='Dependency verification'}
for r in rows:
 x=eventmap[r['verificationEventId']];m=re.fullmatch(r'Verifying (.+) \(([^:]+):([^:]+):(.+)\)',x['progressName']);assert m
 artifact,g,a,v=m.groups();assert artifact==r['artifact'] and ':'.join([g,a,v])==r['coordinate']
licenseRow=load(B/'evidence/apache-license-source.json');licenseFiles=list((B/'licenses').glob('*'))
assert any(p.is_file() and sha(p.read_bytes())==licenseRow['sha256'] for p in licenseFiles)
official=load(B/'evidence/official-added-dependencies/receipt.json');newdeps=[]
for r in official['records']:
 fn=r['finalUrl'].split('/')[-1];p=B/'evidence/official-added-dependencies'/fn;b=p.read_bytes()
 assert r['status']==200 and r['requestedUrl']==r['finalUrl'] and r['finalUrl'].startswith('https://dl.google.com/dl/android/maven2/') and sha(b)==r['sha256'] and len(b)==r['bytes']
 if p.suffix=='.pom':
  x=ET.fromstring(b);ns={'m':'http://maven.apache.org/POM/4.0.0'};licenses=[i.text for i in x.findall('m:licenses/m:license/m:name',ns)];assert any('Apache' in i for i in licenses)
 else:
  m=json.loads(b);c=m['component'];coord=':'.join(c[i] for i in ['group','module','version']);assert sha(b) in pins[(coord,fn)]
  ars={f['name']:f['sha256'] for v in m['variants'] for f in v.get('files',[]) if f['name'].endswith('.aar')}
  for an,ah in ars.items():
   assert ah in pins[(coord,an)];p0=B/'offline-maven'/Path(coord.replace(':','/'))/an
   # Maven group uses path separators, module and version have individual segments.
   g,n,v=coord.split(':');p0=B/'offline-maven'/g.replace('.','/')/n/v/an
   assert sha(p0.read_bytes())==ah
  newdeps.append(dict(coordinate=coord,moduleSha256=sha(b),aarPins=ars))
for r in load(B/'evidence/real-media3-classpath.json'):
 g,n,v=r['coordinate'].split(':');p=B/'offline-maven'/g.replace('.','/')/n/v/(n+'-'+v+'.aar')
 if p.exists():
  assert sha(p.read_bytes())==r['aarSha256']
  with zipfile.ZipFile(p) as z:assert sha(z.read('classes.jar'))==r['classesJarSha256']
 assert any(sha(p.read_bytes())==r['classesJarSha256'] for p in (B/'deps').glob('*.jar')),r['coordinate']
for r in load(B/'evidence/jvm-transitive-classpath.json'):assert sha((B/r['path']).read_bytes())==r['sha256']
apk=B/'artifacts/input-sink01-compile-probe-debug.apk'
def pool(b,at):
 _,h,n=struct.unpack_from('<HHI',b,at);num,styles,flags,base,_=struct.unpack_from('<IIIII',b,at+8);out=[]
 def sz(pos,utf8):
  if utf8:
   v=b[pos];return ((v&127)*256+b[pos+1],pos+2) if v&128 else (v,pos+1)
  v=struct.unpack_from('<H',b,pos)[0];return (((v&32767)<<16)|struct.unpack_from('<H',b,pos+2)[0],pos+4) if v&32768 else (v,pos+2)
 for i in range(num):
  p=at+base+struct.unpack_from('<I',b,at+h+i*4)[0]
  if flags&256:_,p=sz(p,True);n,p=sz(p,True);out.append(b[p:p+n].decode('utf8'))
  else:n,p=sz(p,False);out.append(b[p:p+n*2].decode('utf-16le'))
 return out
def axml(b):
 pos=8;ss=[];tags=[]
 while pos<len(b):
  typ,h,n=struct.unpack_from('<HHI',b,pos);assert n>=h>0
  if typ==1:ss=pool(b,pos)
  if typ==0x102:
   ext=pos+16;_,name,start,size,cnt,_,_,_=struct.unpack_from('<IIHHHHHH',b,ext);attrs={}
   for j in range(cnt):
    a=ext+start+j*size;_,an,raw,_,_,vt,val=struct.unpack_from('<IIIHBBI',b,a)
    attrs[ss[an]]=ss[raw] if raw!=0xffffffff else ss[val] if vt==3 else val
   tags.append(dict(tag=ss[name],attributes=attrs))
  pos+=n
 return tags
def dexclasses(b):
 stringsN,stringsAt=struct.unpack_from('<II',b,56);typesN,typesAt=struct.unpack_from('<II',b,64);clsN,clsAt=struct.unpack_from('<II',b,96);ss=[]
 for i in range(stringsN):
  p=struct.unpack_from('<I',b,stringsAt+i*4)[0]
  while b[p]&128:p+=1
  p+=1;end=b.index(0,p);ss.append(b[p:end].decode('utf8','replace'))
 types=[ss[struct.unpack_from('<I',b,typesAt+i*4)[0]] for i in range(typesN)]
 return [types[struct.unpack_from('<I',b,clsAt+i*32)[0]] for i in range(clsN)]
with zipfile.ZipFile(apk) as z:
 tags=axml(z.read('AndroidManifest.xml'));classes=[c for n in z.namelist() if n.endswith('.dex') for c in dexclasses(z.read(n))]
 assert not any(t['tag'] in ['uses-permission','activity','service','provider','receiver'] for t in tags)
 assert not any(n.startswith('lib/') and n.endswith('.so') for n in z.namelist())
 assert not any(any(v in c for v in ['InputSinkCheck','IndependentBoundaryCheck']) for c in classes)
 assert not any(c in ['Landroid/net/Uri;','Landroid/system/ErrnoException;','Landroid/system/OsConstants;'] for c in classes),'JVM platform standins must not be packaged'
 for c in ['HostDataSource','HostInputFactory','TemporaryOutput','AndroidInput','AndroidGrantedStream','MatureMuxerBinding']:assert 'Lcom/videokit/d1input/'+c+';' in classes
 assert 'Landroidx/media3/datasource/DataSource;' in classes
with zipfile.ZipFile(B/'artifacts/input-sink01-classes.jar') as z:
 jarClasses=z.namelist();assert not any(n.startswith('android/') or 'InputSinkCheck' in n for n in jarClasses)
out=dict(result='PASS_FROZEN_IDENTITY_DEPENDENCY_AND_ARTIFACT_STATIC_AUDIT',newFrozenFiles=count,zipMembers=len(names),oldFrozen=old,finalInputPins=len(inputs),consumption=dict(counts),consumptionRows=len(rows),eventRows=len(events),newDependencies=newdeps,apkManifest=tags,apkClassCount=len(classes),jarEntries=len(jarClasses),realAndroidRuntime='NOT_RUN',networkOrDeviceOrGradleCommands=0)
(E/'frozen-audit.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps({k:v for k,v in out.items() if k not in ['apkManifest','newDependencies']},ensure_ascii=False,indent=2))
