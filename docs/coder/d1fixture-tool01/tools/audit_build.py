from pathlib import Path
import json,hashlib,zipfile,struct,collections,datetime,re
B=Path(__file__).resolve().parents[1];R=B.parents[2];E=B/'evidence'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
assert not (E/'fixture-tool01-freeze.json').exists()
build=json.loads((E/'build-result.json').read_text());assert build['status']=='COMPILED_AND_PACKAGED_ONLY_NOT_RUN' and build['compilerInvocations']==build['jarInvocations']==1
for owner in build['tools']:assert owner['exitCode']==0 and owner['originalProcessReturned'] and owner['outputHandlesClosed'] and not owner['timedOutSticky'] and owner['terminationActions']==0
for x in json.loads((E/'source-input-pins.json').read_text()):assert sha(B/x['path'])==x['sha256']
for x in json.loads((E/'build-001/prebuild-all-candidate-input-pins.json').read_text()):assert sha(B/x['path'])==x['sha256']
def class_origin(data):
 assert data[:4]==b'\xca\xfe\xba\xbe';minor,major,count=struct.unpack_from('>HHH',data,4);p=10;pool=[None]*count;i=1
 while i<count:
  tag=data[p];p+=1
  if tag==1:
   length=struct.unpack_from('>H',data,p)[0];p+=2;pool[i]=data[p:p+length].decode('utf-8','replace');p+=length
  elif tag in [7,8,16,19,20]:pool[i]=struct.unpack_from('>H',data,p)[0];p+=2
  elif tag in [3,4,9,10,11,12,17,18]:p+=4
  elif tag in [5,6]:p+=8;i+=1
  elif tag==15:p+=3
  else:raise AssertionError(('constant pool tag',tag))
  i+=1
 _,thisClass,_=struct.unpack_from('>HHH',data,p);p+=6;name=pool[pool[thisClass]]
 interfaces=struct.unpack_from('>H',data,p)[0];p+=2+interfaces*2
 def skip_attribute(offset):
  length=struct.unpack_from('>I',data,offset+2)[0];return offset+6+length
 for kind in ['fields','methods']:
  items=struct.unpack_from('>H',data,p)[0];p+=2
  for _ in range(items):
   attributes=struct.unpack_from('>H',data,p+6)[0];p+=8
   for _ in range(attributes):p=skip_attribute(p)
 attributes=struct.unpack_from('>H',data,p)[0];p+=2;source=None
 for _ in range(attributes):
  index,length=struct.unpack_from('>HI',data,p)
  if pool[index]=='SourceFile':assert length==2;source=pool[struct.unpack_from('>H',data,p+6)[0]]
  p=skip_attribute(p)
 assert p==len(data) and source and major==55
 return name,source,major
inputMap={}
for x in json.loads((E/'source-input-pins.json').read_text()):
 parts=Path(x['path']).parts;assert parts[0] in ['source','driver'];key='/'.join(parts[1:]);assert key not in inputMap;inputMap[key]=x
jar=B/'artifacts/videokit-fixture-tool01.jar';classes=B/'build-output/classes';rows=[]
with zipfile.ZipFile(jar) as z:
 assert z.testzip() is None
 names=[i.filename for i in z.infolist() if not i.is_dir()];assert len(names)==len(set(names))
 expected={p.relative_to(classes).as_posix() for p in classes.rglob('*.class')}|{p.relative_to(B/'package-resources').as_posix() for p in (B/'package-resources').rglob('*') if p.is_file()}|{'META-INF/MANIFEST.MF'}
 assert set(names)==expected
 manifest=z.read('META-INF/MANIFEST.MF').decode();assert 'Main-Class: com.videokit.fixturetool.SixFrameDriver\r\n' in manifest
 for n in names:
  if not n.endswith('.class'):continue
  p=classes/n;data=p.read_bytes();assert z.read(n)==data;name,source,major=class_origin(data);assert name+'.class'==n
  key=name.rsplit('/',1)[0]+'/'+source;assert key in inputMap,(n,key)
  origin=inputMap[key];rows.append({'jarEntry':n,'bytes':len(data),'sha256':sha(p),'className':name,'sourceFileAttribute':source,'sourcePath':origin['path'],'sourceSha256':origin['sha256'],'actualCompilerOutputPath':p.relative_to(B).as_posix(),'majorVersion':major})
 for n in names:
  if n!='META-INF/MANIFEST.MF' and not n.endswith('.class'):assert z.read(n)==(B/'package-resources'/n).read_bytes()
 assert not any(n.endswith(('.exe','.dll','.so','.mp4','.class.java')) for n in names)
 assert all(x['className'].startswith(('com/videokit/fixturetool/','org/jcodec/','net/sourceforge/jaad/')) for x in rows)
 dump(E/'jar-class-origin.json',rows)
 dump(E/'jar-audit.json',{'artifact':jar.relative_to(B).as_posix(),'bytes':jar.stat().st_size,'sha256':sha(jar),'mainClass':'com.videokit.fixturetool.SixFrameDriver','manifestVerbatim':manifest,'files':names,'classCount':len(rows),'classesByNamespace':dict(collections.Counter('driver' if x['className'].startswith('com/videokit/') else 'bundledJAAD' if x['className'].startswith('net/') else 'JCodec' for x in rows)),'everyClassByteEqualsOriginalJavacOutput':True,'everyClassSourceFileMatchesPinnedExplicitSource':True,'extraUnlistedClassOrResource':False,'nativeLibraries':0,'mainRunOrEncoderInitialization':False,'qualifiedFixture':False,'publicReleaseLicenseOrPatentClearance':False})
licenses=json.loads((E/'source-license-inventory.json').read_text());assert len(licenses)==711
assert len([x for x in licenses if x['path'].startswith('source/net/sourceforge/jaad/')])==73
assert 'Copyright (C) 2007 The Guava Authors' in (B/'licenses/SOURCE_NOTICES.txt').read_text()
assert 'Licensed under the Apache License' in (B/'licenses/SOURCE_NOTICES.txt').read_text()
assert 'Public Domain license' in (B/'licenses/SOURCE_NOTICES.txt').read_text()
sbom={'format':'Project review inventory, not a clearance certificate','components':[{'name':'JCodec','version':'0.2.5','kind':'Exact official source artifact','sourceArchiveSha256':'9945efa92e16b3fbe8eb8bf37f00be53fa0adb52d09ac978a0744ca2ef3697db','sourceJavaFiles':635,'license':'See verbatim file headers, FreeBSD/POM and official repository text; per-file exceptions separately retained','source':'https://repo.maven.apache.org/maven2/org/jcodec/jcodec/0.2.5/jcodec-0.2.5-sources.jar'},{'name':'JAAD bundled inside exact JCodec source','sourceJavaFiles':73,'license':'Source declares Public Domain; JCodec changes FreeBSD','scope':'Compiled main tree; no AAC decoding invoked'},{'name':'Guava-derived Preconditions','path':'source/org/jcodec/common/Preconditions.java','license':'Apache-2.0','copyright':'2007 The Guava Authors','newExternalGuavaDependency':False},{'name':'VideoKit fixture driver','sourceJavaFiles':3,'license':'Project-authored internal review; public release terms not inferred'}],'buildOnlyJdk':'Existing JetBrains21.0.10 exact compiler-identity.json; not downloaded/redistributed','externalRuntimeArtifactsOutsideBuiltJar':[],'newMavenGradleOrBinaryDependencies':[],'notices':[{'path':p.relative_to(B).as_posix(),'sha256':sha(p)} for p in (B/'licenses').iterdir()],'unusedCompiledCode':'Full708-source archive includes other codecs/decoders/CLI classes. Their presence is not permission to invoke them, no general encoder/decoder execution approved.'}
dump(E/'sbom-and-licenses.json',sbom)
frozen=[]
android=R/'docs/coder/d1media3-android01/evidence/media3-android01-freeze.json';assert sha(android)=='fca6adcdf9783b91c9af396de3b836efad72c4d59ef820eb1924d8658f0b928a';a=json.loads(android.read_text());assert all(sha(R/x['path'])==x['sha256'] for x in a['files']);frozen.append({'sealPath':android.relative_to(R).as_posix(),'sha256':sha(android),'files':len(a['files'])})
for row in json.loads((R/'docs/coder/d1media3-android01/evidence/frozen-baseline-preservation.json').read_text()):
 p=R/row['sealPath'];assert sha(p)==row['sealSha256'];v=json.loads(p.read_text());assert all(sha(R/x['path'])==x['sha256'] for x in v['files']);frozen.append({'sealPath':p.relative_to(R).as_posix(),'sha256':sha(p),'files':len(v['files'])})
assert sum(x['files'] for x in frozen)==6972;dump(E/'prior-frozen-preservation.json',frozen)
prior=[]
for p in [R/'docs/tester/D1_FIXTURE_TOOL01_BUILD_PHASE_A_EVIDENCE/phase-a-evidence-manifest.json',R/'docs/tester/D1_MEDIA3_ANDROID01_READY_PHASE_B_EVIDENCE/review-evidence-manifest.json']:
 if not p.exists():
  # Existing Android phase B directory is named REVIEW_EVIDENCE; no guessing of content.
  assert 'ANDROID01' in str(p);p=R/'docs/tester/D1_MEDIA3_ANDROID01_READY_REVIEW_EVIDENCE/review-evidence-manifest.json'
 m=json.loads(p.read_text());assert sha(R/m['report'])==m['reportSha256'] and all(sha(R/x['path'])==x['sha256'] for x in m['evidenceFiles']);prior.append({'path':p.relative_to(R).as_posix(),'sha256':sha(p),'reportSha256':m['reportSha256'],'files':len(m['evidenceFiles'])})
dump(E/'prior-independent-preservation.json',prior)
dump(E/'static-validation.json',{'checkedUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'BYTE_AND_SOURCE_AUDIT_ONLY_NOT_RUNTIME_PASS','classes':len(rows),'explicitSources':711,'upstreamSources':708,'driverSources':3,'sourceBytes':build['sourceInputBytes'],'buildOutputBytesAtReturn':build['actualBuildOutputBytesAtNaturalReturn'],'compilerProcesses':1,'jarProcesses':1,'naturalReturns':2,'runtimeJavaOrMainOrEncoderCalls':0,'newMediaFilesInCandidate':len(list(B.rglob('*.mp4'))),'noOldOwnerPollingOrAttach':True,'priorFrozen6972Unchanged':True,'jcodecSourceModified':False,'movieDateUsesCurrentTime':'Original MP4Muxer.movieHeader new Date().getTime preserved; no repeated whole-media hash determinism claim','perAuTransformedAvccHash':'NOT_OBSERVED_BY_THIS_BUILD; future actual container qualification separate; rawAnnexB and actual mux-track CSD capture implemented'})
print(json.dumps({'jarSha256':sha(jar),'classes':len(rows),'sourceFiles':711,'priorFrozenFilesUnchanged':6972,'currentRuntimeOperations':0},indent=2))
