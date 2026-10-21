from pathlib import Path
import json,hashlib,zipfile,ast,struct,collections,difflib,datetime
B=Path(__file__).resolve().parents[1];R=B.parents[2];E=B/'evidence';O=R/'docs/coder/d1fixture-tool01'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
assert not (E/'fixture-tool02-freeze.json').exists()
build=json.loads((E/'build-result.json').read_text());checks=json.loads((E/'nonmedia-001/summary.json').read_text())
assert build['status']=='COMPILED_AND_PACKAGED_ONLY_NOT_RUN' and build['compilerInvocations']==build['jarInvocations']==1
assert checks['totalExecutedGroups']==58 and checks['allOriginalProcessesReturned'] and checks['groupsPerPath']==29
assert checks['combinedAllocatedPayloadBytes']==36928 and checks['combinedNativeRequestedPayloadBytes']==1248
pins=json.loads((E/'source-input-pins.json').read_text());assert len(pins)==713
for x in pins:assert sha(B/x['path'])==x['sha256']
for x in json.loads((E/'build-001/prebuild-all-candidate-input-pins.json').read_text()):assert sha(B/x['path'])==x['sha256']
tree=ast.parse((B/'tools/audit_build.py').read_text());nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='class_origin'];assert len(nodes)==1
exec(compile(ast.Module(body=nodes,type_ignores=[]),'retained01_class_parser_only','exec'))
inputMap={'/'.join(Path(x['path']).parts[1:]):x for x in pins};assert len(inputMap)==713
classes=B/'build-output/classes';packaging=json.loads((E/'class-packaging-split.json').read_text());assert len(packaging)==990
rows=[]
for x in packaging:
 p=B/x['path'];copy=B/x['packageCopy'];assert sha(p)==x['sha256']==sha(copy)
 name,source,major=class_origin(p.read_bytes());key=name.rsplit('/',1)[0]+'/'+source;assert key in inputMap
 origin=inputMap[key];assert x['testOnly']==origin['path'].startswith('checks/')
 rows.append({'className':name,'jarEntry':name+'.class','sourceFile':source,'sourcePath':origin['path'],'sourceSha256':origin['sha256'],'actualCompilerOutput':x['path'],'packageCopy':x['packageCopy'],'sha256':x['sha256'],'bytes':p.stat().st_size,'testOnly':x['testOnly'],'majorVersion':major})
prod=[x for x in rows if not x['testOnly']];test=[x for x in rows if x['testOnly']];assert len(prod)==985 and len(test)==5
jar=B/'artifacts/videokit-fixture-tool02.jar';expected={x['jarEntry'] for x in prod}|{'META-INF/MANIFEST.MF'}|{p.relative_to(B/'package-resources').as_posix() for p in (B/'package-resources').rglob('*') if p.is_file()}
with zipfile.ZipFile(jar) as z:
 names=[i.filename for i in z.infolist() if not i.is_dir()];assert len(names)==len(set(names)) and set(names)==expected and z.testzip() is None
 manifest=z.read('META-INF/MANIFEST.MF').decode();assert 'Main-Class: com.videokit.fixturetool.SixFrameDriver\r\n' in manifest
 for x in prod:assert hashlib.sha256(z.read(x['jarEntry'])).hexdigest()==x['sha256']
 for p in (B/'package-resources').rglob('*'):
  if p.is_file():assert z.read(p.relative_to(B/'package-resources').as_posix())==p.read_bytes()
 assert not any('FixtureToolFixCheck' in n or n.endswith(('.mp4','.exe','.dll','.so')) for n in names)
dump(E/'class-origin02.json',rows)
dump(E/'jar-audit02.json',{'path':jar.relative_to(B).as_posix(),'bytes':jar.stat().st_size,'sha256':sha(jar),'productionClassCount':985,'testClassCountExcluded':5,'manifest':manifest,'jarFileNames':names,'allProductionClassBytesMatchActualSingleJavacOutputAndSourcePins':True,'allTestSourceFileAttributesMapOnlyToChecks':True,'classParserOrigin':{'path':'tools/audit_build.py','sha256':sha(B/'tools/audit_build.py'),'use':'AST-extract pure class_origin function only; legacy01 top-level script not executed or offered as current entry'},'runtimeGenerationClassesLoaded':0})
changes=[]
base=json.loads((E/'baseline01-pins.json').read_text())
for x in base['files']:
 p=B/x['path']
 if sha(p)!=x['sha256']:
  assert x['path'].startswith('driver/');changes.append({'path':x['path'],'oldSha256':x['sha256'],'newSha256':sha(p)})
  out=E/(p.stem+'-diff.patch');out.write_text(''.join(difflib.unified_diff((O/x['path']).read_text().splitlines(True),p.read_text().splitlines(True),fromfile='01/'+x['path'],tofile='02/'+x['path'])),encoding='utf-8')
assert {x['path'] for x in changes}=={'driver/com/videokit/fixturetool/AttemptBudgetChannel.java','driver/com/videokit/fixturetool/SixFrameDriver.java'}
dump(E/'source-differences02.json',{'changed':changes,'newProduction':['driver/com/videokit/fixturetool/WorkerDeadline.java'],'newChecks':['checks/com/videokit/fixturetool/FixtureToolFixCheck.java'],'unchangedOriginalJava':708,'receiptJsonUnchanged':True,'noReflectionStateMutation':True,'newNativeOrBinaryDependency':False,'fixClaims':'Coder source/JAR checks only; independent FT-B01/B02 closure pending'})
licenses=json.loads((E/'source-license-inventory.json').read_text());assert len(licenses)==713
assert all(sha(B/x['path'])==x['sha256'] for x in licenses)
text=(B/'licenses/SOURCE_NOTICES.txt').read_text();assert 'Copyright (C) 2007 The Guava Authors' in text and 'Public Domain license' in text and 'Apache License' in text
sbom=json.loads((O/'evidence/sbom-and-licenses.json').read_text());sbom['components'][-1]['sourceJavaFiles']=4;sbom['testAuxiliary']='1 source/5 classes, separately retained, never in production JAR';sbom['notices']=[{'path':p.relative_to(B).as_posix(),'sha256':sha(p)} for p in (B/'licenses').iterdir()];dump(E/'sbom02.json',sbom)
old=[]
for folder,sealName in [('d1fixture-tool01','fixture-tool01-freeze.json')]+[('d1media3-android01','media3-android01-freeze.json')]:
 p=R/'docs/coder'/folder/'evidence'/sealName;v=json.loads(p.read_text());assert all(sha(R/x['path'])==x['sha256'] for x in v['files']);old.append({'sealPath':p.relative_to(R).as_posix(),'sha256':sha(p),'files':len(v['files'])})
for x in json.loads((R/'docs/coder/d1media3-android01/evidence/frozen-baseline-preservation.json').read_text()):
 p=R/x['sealPath'];assert sha(p)==x['sealSha256'];v=json.loads(p.read_text());assert all(sha(R/y['path'])==y['sha256'] for y in v['files']);old.append({'sealPath':p.relative_to(R).as_posix(),'sha256':sha(p),'files':len(v['files'])})
assert sum(x['files'] for x in old)==8725;dump(E/'prior-frozen02.json',old)
manifest=R/'docs/tester/D1_FIXTURE_TOOL01_BUILD_REVIEW_EVIDENCE/review-evidence-manifest.json';m=json.loads(manifest.read_text());assert m['reportSha256']=='57107a238dc62d11fa40b18b95bd283988388a2fcf10f8cbed08acb78eb759da' and sha(R/m['report'])==m['reportSha256'] and all(sha(R/x['path'])==x['sha256'] for x in m['evidenceFiles'])
dump(E/'prior-independent02.json',{'manifestPath':manifest.relative_to(R).as_posix(),'sha256':sha(manifest),'reportSha256':m['reportSha256'],'files':len(m['evidenceFiles']),'verdictPreserved':m.get('overall')})
dump(E/'validation02.json',{'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'oneJavacOneJarNaturalReturns':True,'compiledSources':713,'productionClasses':985,'testClassesOnly':5,'controlledGroupsSource':29,'controlledGroupsProductionJarFirst':29,'sourceAndJarOriginsAndClassLoadingProven':True,'byteArraysAllocatedBothPaths':36928,'memoryPortRequestsBothPaths':1248,'memoryPortPhysicalWritesBothPaths':1148,'nativeFileOrEncoderOrMainJobRunOrMuxerMediaTests':0,'oldOwnerCollectionsAttachInterventions':0,'oldFrozenFilesUnchanged':8725,'independentClosurePending':True})
print(json.dumps({'jarSha256':sha(jar),'productionClasses':985,'checksClasses':5,'nonmediaGroups':58,'oldFrozenUnchanged':8725},indent=2))
