from pathlib import Path
import json,hashlib,zipfile,datetime
B=Path(__file__).resolve().parents[1];R=B.parents[2];E=B/'evidence';seal=E/'fixture-tool02-freeze.json';assert not seal.exists()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
for file in ['source-input-pins.json','build-001/prebuild-all-candidate-input-pins.json']:
 for x in json.loads((E/file).read_text()):assert sha(B/x['path'])==x['sha256']
v=json.loads((E/'build-result.json').read_text());assert v['status']=='COMPILED_AND_PACKAGED_ONLY_NOT_RUN' and v['compilerInvocations']==v['jarInvocations']==1
assert all(x['originalProcessReturned'] and x['outputHandlesClosed'] and x['exitCode']==0 and not x['timedOutSticky'] for x in v['tools'])
c=json.loads((E/'nonmedia-001/summary.json').read_text());assert c['totalExecutedGroups']==58 and c['allOriginalProcessesReturned'] and c['combinedAllocatedPayloadBytes']==36928 and c['combinedNativeRequestedPayloadBytes']==1248
for x in c['runs']:assert x['exitCode']==0 and x['originalProcessReturned'] and x['outputHandlesClosed'] and not x['timedOutSticky'] and x['noGenerationClassLoaded']
for x in json.loads((E/'class-origin02.json').read_text()):assert sha(B/x['actualCompilerOutput'])==x['sha256']==sha(B/x['packageCopy']) and sha(B/x['sourcePath'])==x['sourceSha256']
count=0
for x in json.loads((E/'prior-frozen02.json').read_text()):
 p=R/x['sealPath'];assert sha(p)==x['sha256'];f=json.loads(p.read_text());assert all(sha(R/y['path'])==y['sha256'] for y in f['files']);count+=len(f['files'])
assert count==8725
x=json.loads((E/'prior-independent02.json').read_text());p=R/x['manifestPath'];assert sha(p)==x['sha256'];m=json.loads(p.read_text());assert sha(R/m['report'])==m['reportSha256'] and all(sha(R/y['path'])==y['sha256'] for y in m['evidenceFiles'])
assert len(json.loads((E/'completion-matrix02.json').read_text())['cases'])==28
assert not list((B/'build-output/temp').iterdir()) and not (R/'docs/coder/d1fixture-six01').exists()
main=R/'docs/coder/D1_FIXTURE_TOOL02_FIX_DELIVERY_V1.0.md';archive=R/'docs/coder/D1-20261021-FIXTURE-TOOL02-FIX-source.zip';assert not archive.exists()
files=sorted([p for p in B.rglob('*') if p.is_file()]+[main]);assert not any(p.suffix.lower() in ['.mp4','.mkv','.wav','.mp3','.exe','.dll','.so','.jks','.keystore'] for p in files)
rows=[{'path':p.relative_to(R).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in files]
with zipfile.ZipFile(archive,'x',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in files:z.write(p,p.relative_to(R).as_posix())
with zipfile.ZipFile(archive) as z:
 assert z.testzip() is None and len(z.namelist())==len(set(z.namelist()))==len(rows)
 for x in rows:assert hashlib.sha256(z.read(x['path'])).hexdigest()==x['sha256']
arch={'path':archive.relative_to(R).as_posix(),'bytes':archive.stat().st_size,'sha256':sha(archive)};total=sum(x['bytes'] for x in rows)+arch['bytes'];assert total<67108864
jar=B/'artifacts/videokit-fixture-tool02.jar';audit=json.loads((E/'jar-audit02.json').read_text());assert sha(jar)==audit['sha256']
value={'candidate':'D1-20261021-FIXTURE-TOOL02-FIX','createdUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'FROZEN_CODER_NONMEDIA_FIX_CHECKS_COMPLETE_PENDING_INDEPENDENT_P2_REVIEW','priorIndependentFailPreserved':'57107a238dc62d11fa40b18b95bd283988388a2fcf10f8cbed08acb78eb759da','independentFT_B01_B02Closure':'PENDING','toolJarSha256':sha(jar),'sourceJavaFiles':708,'driverJavaFiles':4,'checkJavaFiles':1,'actualCompilerClasses':990,'productionClassesInJar':985,'testClassesExcludedFromJar':5,'compilerCalls':1,'jarCalls':1,'nonmediaJvms':2,'controlledGroupsEach':29,'controlledGroupsTotal':58,'payloadArraysBothPaths':36928,'nativeRequestPayloadBothPaths':1248,'originalControlledWorkersJoined':True,'originalNewJvmProcessesReturned':True,'runtimeGenerationMainJobEncoderMuxerMediaCalls':0,'newDeviceOldOwnerQueriesOrInterventions':0,'oldOriginalUnknowns':'48945/17257 UNKNOWN untouched','oldFrozenFilesUnchanged':8725,'sourceInputBytes':v['sourceInputBytes'],'buildOutputBytesAtReturn':v['actualBuildOutputBytesAtNaturalReturn'],'allCandidatePlusArchiveBytes':total,'outputLimitBytes':67108864,'generationAuthorized':False,'D1':'NOT_PASSED','M0':'NOT_STARTED','archiveMembers':len(rows),'archive':arch,'files':rows+[arch]}
seal.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');assert all(sha(R/x['path'])==x['sha256'] for x in value['files'])
print(json.dumps({'sealPath':seal.relative_to(R).as_posix(),'sealSha256':sha(seal),'frozenFiles':len(value['files']),'archive':arch,'reportSha256':sha(main),'allCandidatePlusArchiveBytes':total},ensure_ascii=False,indent=2))
