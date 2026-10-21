from pathlib import Path
import json,hashlib,zipfile,ast,struct,difflib,datetime,re
B=Path(__file__).resolve().parents[1];R=B.parents[2];E=B/'evidence';O=R/'docs/coder/d1fixture-tool02'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
assert not (E/'observation01-freeze.json').exists()
build=json.loads((E/'build-result.json').read_text());assert build['status']=='BUILT_AUDIT_FORK_ONLY' and build['compilerCalls']==build['jarCalls']==1
pins=json.loads((E/'compile-source-pins.json').read_text());assert len(pins)==709 and all(sha(B/x['path'])==x['sha256'] for x in pins)
old=json.loads((E/'original-source-pins.json').read_text());changed={x['path'] for x in old if sha(B/x['path'])!=x['sha256']};assert len(changed)==3
assert changed=={'source/org/jcodec/containers/mp4/boxes/DataRefBox.java','source/org/jcodec/containers/mp4/boxes/SampleDescriptionBox.java','source/org/jcodec/codecs/h264/mp4/AvcCBox.java'}
def method(source,name):
 match=re.search(r'public\s+(?:void|int)\s+'+name+r'\s*\([^)]*\)\s*\{',source);assert match
 begin=match.start();pos=match.end();depth=1
 while depth:
  if source[pos]=='{':depth+=1
  if source[pos]=='}':depth-=1
  pos+=1
 return source[begin:pos]
methods=[]
for p in sorted(changed):
 for name in ['doWrite','estimateSize']:
  oldText=method((O/p).read_text(),name);newText=method((B/p).read_text(),name);assert oldText==newText;methods.append({'path':p,'method':name,'sourceBodySha256':hashlib.sha256(oldText.encode()).hexdigest(),'byteIdenticalSourceBody':True})
dump(E/'unchanged-write-methods.json',methods)
parser=O/'tools/audit_build.py';tree=ast.parse(parser.read_text());node=[x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='class_origin'];assert len(node)==1;exec(compile(ast.Module(body=node,type_ignores=[]),'existing_pure_class_parser','exec'))
inputMap={'/'.join(Path(x['path']).parts[1:]):x for x in pins};rows=[]
for x in json.loads((E/'class-split.json').read_text()):
 p=B/x['originalOutput'];assert sha(p)==x['sha256']==sha(B/x['copy']);name,source,major=class_origin(p.read_bytes());key=name.rsplit('/',1)[0]+'/'+source;assert key in inputMap
 origin=inputMap[key];assert x['testOnly']==origin['path'].startswith('checks/');rows.append({'className':name,'jarEntry':name+'.class','sourcePath':origin['path'],'sourceFile':source,'sourceSha256':origin['sha256'],'sha256':x['sha256'],'bytes':p.stat().st_size,'compilerOutput':x['originalOutput'],'copy':x['copy'],'testOnly':x['testOnly'],'major':major})
prod=[x for x in rows if not x['testOnly']];tests=[x for x in rows if x['testOnly']];assert len(prod)==977 and len(tests)==3
jar=B/'artifacts/jcodec-0.2.5-videokit-observation01.jar';base=O/'artifacts/videokit-fixture-tool02.jar';assert sha(base)=='c4ed36f31cab8381bc47c0aea4c3f3d8a9c2afab09991a04a83102877f1bfecd';assert sha(jar)=='1a7e8601be4ebb5665219f2ccfa6e75476323e7408a6b18824ecf2a37873de86'
same=[];different=[]
with zipfile.ZipFile(jar) as z,zipfile.ZipFile(base) as bz:
 assert z.testzip() is None;names=[x.filename for x in z.infolist() if not x.is_dir()];expected={x['jarEntry'] for x in prod}|{'META-INF/MANIFEST.MF'}|{p.relative_to(B/'package-resources').as_posix() for p in (B/'package-resources').rglob('*') if p.is_file()};assert set(names)==expected
 raw=z.read('META-INF/MANIFEST.MF').decode();lines=[]
 for line in raw.splitlines():
  if line.startswith(' '):lines[-1]+=line[1:]
  else:lines.append(line)
 manifest=dict(line.split(': ',1) for line in lines if ': ' in line);assert manifest['Implementation-Version']=='0.2.5-videokit-observation01' and manifest['VideoKit-Patch-SHA256']==sha(B/'patches/observation01.patch') and manifest['JCodec-Original-Sources-SHA256']=='9945efa92e16b3fbe8eb8bf37f00be53fa0adb52d09ac978a0744ca2ef3697db' and 'Main-Class' not in manifest
 for x in prod:
  data=z.read(x['jarEntry']);assert hashlib.sha256(data).hexdigest()==x['sha256'];(same if data==bz.read(x['jarEntry']) else different).append(x['className'])
  if x['sourcePath'] in changed:assert b'hasOriginalParseObservation' in data and b'ORIGINAL_PARSE_NOT_OBSERVED' in data
 for p in (B/'package-resources').rglob('*'):
  if p.is_file():assert z.read(p.relative_to(B/'package-resources').as_posix())==p.read_bytes()
 assert not any('MetadataObservationCheck' in n or 'SixFrameDriver' in n or n.endswith(('.exe','.dll','.so','.mp4')) for n in names)
assert len(different)==3 and len(same)==974
dump(E/'class-origin.json',rows);dump(E/'jar-audit.json',{'path':jar.relative_to(B).as_posix(),'bytes':jar.stat().st_size,'sha256':sha(jar),'manifest':manifest,'jarFileNames':names,'productionClasses':977,'helperClassesExcluded':3,'sameOriginalLibraryClassBytes':974,'changedClassBytes':different,'originalArtifactNeverOverwritten':True,'classParserOrigin':{'path':str(parser),'sha256':sha(parser)},'notOfficialUnmodifiedArtifact':True})
owner=json.loads((E/'metadata-001/owner.json').read_text());assert owner['processInvocations']==1 and owner['originalProcessReturned'] and owner['outputHandlesClosed'] and owner['exitCode']==1 and not owner['unknownSticky']
raw=(E/'metadata-001/stdout.raw').read_bytes();err=(E/'metadata-001/stderr.raw').read_bytes();out=[json.loads(x) for x in raw.decode().splitlines()];passed=[x for x in out if x.get('result')=='PASS_NONMEDIA_METADATA'];assert len(passed)==2 and len(out)==3
assert b'NoSuchMethodException: org.jcodec.containers.mp4.boxes.Box$LeafBox.hasOriginalParseObservation()' in err
logs=(E/'metadata-001/class-load.log').read_text();classes=re.findall(r'\[class,load\]\s+(\S+)',logs);assert not any(('MP4Demuxer' in c or 'MP4Muxer' in c or 'SixFrameDriver' in c or c.startswith('org.jcodec.') and (c.endswith('Encoder') or c.endswith('Decoder'))) for c in classes)
dump(E/'metadata-failure-result.json',{'status':'VALIDATION_BLOCKED_HELPER_FACTORY_CONTEXT_FAILURE','originalJvmExitCode':1,'originalJvmNaturalReturn':True,'captureHandlesClosed':True,'timeoutUnknown':False,'originalControllerAlsoExit1':'Existing exec chunk95c153, after already-returned child assertion; no replay','rawStdoutBytes':len(raw),'rawStderrBytes':len(err),'allOriginalStdoutJsonRows':out,'completedCases':2,'completedCaseNames':[x['case'] for x in passed],'completedParseDifferentialCases':0,'intendedMetadataVectorsExecuted':False,'blocker':'Helper Api.box(avcC) uses BoxFactory.getDefault/DefaultBoxes, which has no avcC mapping; factory returns LeafBox, so first new-AvcC-observation getter lookup fails. Original and fork factories are unchanged.','unproven':'All actual header/count/avcC getters on completed parse, consumption/exception/legacy append/reparse/write comparisons NOT_RUN. Do not infer fork pass or actual parse bug from this helper failure.','threadAndLoaders':'Source reaches actual worker.join before final assertion; try-with-resources attempts both original URLClassLoader closes. No successful final summary emitted, so do not invent its endNanos/loader-close success receipt. Original JVM naturally exited; no new retained running process was observed by this controller.','noReflectiveStateMutation':True,'noForbiddenGenerationOrMediaTypesLoaded':True,'actualMp4Reads':0,'newGeneration':0,'recompileOrRetry':0,'oldSessionActions':0})
helper=B/'checks/com/videokit/observation/MetadataObservationCheck.java';s=helper.read_text();needle='Object box(String fourcc)throws Exception{return call(factory,"newBox",new Class<?>[]{header},header.getConstructor(String.class).newInstance(fourcc));}'
assert needle in s
replacement='Object box(String fourcc)throws Exception{Object h=header.getConstructor(String.class).newInstance(fourcc);if(fourcc.equals("avcC"))return Class.forName("org.jcodec.codecs.h264.mp4.AvcCBox",true,loader).getConstructor(header).newInstance(h);return call(factory,"newBox",new Class<?>[]{header},h);}'
(E/'PROPOSED_HELPER_ENTRY_FIX_NOT_APPLIED.patch').write_text(''.join(difflib.unified_diff(s.splitlines(True),s.replace(needle,replacement).splitlines(True),fromfile='current-compiled-helper',tofile='PROPOSAL_ONLY_NEW_REVIEWED_HELPER_REQUIRED')),encoding='utf-8')
dump(E/'helper-fix-proposal.json',{'status':'PROPOSAL_ONLY_NOT_APPLIED_OR_COMPILED_OR_RUN','scope':'Only helper public mature-object construction, no production source/factory/map change','proposal':'Use public AvcCBox(Header) constructor in BOTH original/fork isolated loaders for avcC unit metadata. Keep actual default factory for dref/stsd. Alternatively correctly scoped mature VideoBoxes factory only after review.','why':'avcC belongs to VideoBoxes mapping, reached in real sample-entry factory context; default root factory LeafBox is original behavior, not new fork defect.','requiredBeforeUse':'Coordinator new precise helper compile/JVM scope or independent review; current one compile/one jar/one JVM consumed. No generation/media read/new producer rebuild/retry in this batch.'})
dump(E/'static-validation.json',{'dateUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'sourceFiles':708,'modified':3,'unchanged':705,'compileInputsWithHelper':709,'classFiles':980,'productionClassFiles':977,'testClassFiles':3,'allNewClassOriginsAndSourcePinsMatched':True,'compilerAndJarNaturalExit0':True,'metadataJvmNaturalExit1':True,'onlyFreshDrefStsdObservationGuardsCompleted':2,'parseDifferentialUnvalidated':True,'mandatoryOA_DYNAMIC_SCOPE':'BLOCKED_NOT_GREEN','sourceBytes':build['sourceInputBytes'],'buildOutputBytes':build['buildOutputBytesAtReturn'],'mediaReadsGenerationDeviceOrOldOwnerActions':0})
print(json.dumps({'jarSha256':sha(jar),'patchSha256':sha(B/'patches/observation01.patch'),'prodClasses':977,'testClasses':3,'modifiedSource':3,'unchangedClassesByteForByte':974,'metadataStatus':'BLOCKED_HELPER_FACTORY_CONTEXT','actualCompletedCases':2,'actualParseDifferentialCases':0},indent=2))
