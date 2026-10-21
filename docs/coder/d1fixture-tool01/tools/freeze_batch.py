from pathlib import Path
import json,hashlib,zipfile,datetime
B=Path(__file__).resolve().parents[1];R=B.parents[2];E=B/'evidence';seal=E/'fixture-tool01-freeze.json';assert not seal.exists()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
build=json.loads((E/'build-result.json').read_text());assert build['status']=='COMPILED_AND_PACKAGED_ONLY_NOT_RUN' and build['compilerInvocations']==build['jarInvocations']==1
for x in json.loads((E/'source-input-pins.json').read_text()):assert sha(B/x['path'])==x['sha256']
for x in json.loads((E/'build-001/prebuild-all-candidate-input-pins.json').read_text()):assert sha(B/x['path'])==x['sha256']
for x in json.loads((E/'prior-frozen-preservation.json').read_text()):
 p=R/x['sealPath'];assert sha(p)==x['sha256'];v=json.loads(p.read_text());assert all(sha(R/y['path'])==y['sha256'] for y in v['files'])
for x in json.loads((E/'prior-independent-preservation.json').read_text()):
 p=R/x['path'];assert sha(p)==x['sha256'];v=json.loads(p.read_text());assert sha(R/v['report'])==v['reportSha256'] and all(sha(R/y['path'])==y['sha256'] for y in v['evidenceFiles'])
assert len(json.loads((E/'completion-matrix.json').read_text())['cases'])==28
jar=B/'artifacts/videokit-fixture-tool01.jar';audit=json.loads((E/'jar-audit.json').read_text());assert sha(jar)==audit['sha256'] and audit['classCount']==982
for x in json.loads((E/'jar-class-origin.json').read_text()):assert sha(B/x['actualCompilerOutputPath'])==x['sha256'] and sha(B/x['sourcePath'])==x['sourceSha256']
assert not any((B/'build-output/temp').iterdir())
assert all(x['originalProcessReturned'] and x['exitCode']==0 and x['outputHandlesClosed'] and not x['timedOutSticky'] for x in build['tools'])
assert not (R/'docs/coder/d1fixture-six01').exists(),'FUTURE_OUTPUT_ROOT_ALREADY_PRESENT_REQUIRES_REVIEW'
main=R/'docs/coder/D1_FIXTURE_TOOL01_BUILD_DELIVERY_V1.0.md';archive=R/'docs/coder/D1-20261021-FIXTURE-TOOL01-BUILD-source.zip';assert not archive.exists()
files=sorted([p for p in B.rglob('*') if p.is_file()]+[main]);assert seal not in files
assert not any(p.suffix.lower() in ['.mp4','.mkv','.wav','.mp3','.exe','.dll','.so','.keystore','.jks'] for p in files)
assert sum(p.stat().st_size for p in files)<67108864
rows=[{'path':p.relative_to(R).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in files]
with zipfile.ZipFile(archive,'x',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in files:z.write(p,p.relative_to(R).as_posix())
with zipfile.ZipFile(archive) as z:
 assert z.testzip() is None and len(z.namelist())==len(set(z.namelist()))==len(rows)
 for x in rows:assert hashlib.sha256(z.read(x['path'])).hexdigest()==x['sha256']
arch={'path':archive.relative_to(R).as_posix(),'bytes':archive.stat().st_size,'sha256':sha(archive)}
value={'schemaVersion':1,'candidate':'D1-20261021-FIXTURE-TOOL01-BUILD','createdUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'FROZEN_TOOL_BUILD_ONLY_PENDING_INDEPENDENT_PHASE_B_NO_GENERATION_AUTHORIZATION','toolJarSha256':sha(jar),'sourceArchiveSha256':'9945efa92e16b3fbe8eb8bf37f00be53fa0adb52d09ac978a0744ca2ef3697db','upstreamJavaFiles':708,'bundledJaadJavaFiles':73,'driverJavaFiles':3,'actualJavaInputBytes':build['sourceInputBytes'],'inputLimit':16777216,'compilerInvocations':1,'jarInvocations':1,'actualOriginalToolReturns':2,'buildOutputBytesAtNaturalReturn':build['actualBuildOutputBytesAtNaturalReturn'],'allCandidateFilesPlusArchiveBytes':sum(x['bytes'] for x in rows)+arch['bytes'],'outputLimit':67108864,'actualCompilerClasses':982,'newClassInitializationOrMainRun':0,'newEncoderRunsOrMediaFiles':0,'newWrapperRuntimeIoTests':0,'newDeviceOrAttachOrOldSessionPoll':0,'generationAuthorized':False,'oldOriginalSessions':'48945/17257 UNKNOWN unchanged; no current liveness assertion','oldFrozenFilesUnchanged':6972,'D1':'NOT_PASSED','M0':'NOT_STARTED','sourceArchiveModified':False,'commercialOrPatentOrReleaseClearance':False,'archiveMembers':len(rows),'archive':arch,'files':rows+[arch],'excluded':'No JDK/SDK/cache/native/key/media copied; original javac classes deliberately included for byte provenance; empty temp/classpath directories are not files'}
assert value['allCandidateFilesPlusArchiveBytes']<67108864
seal.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
assert all(sha(R/x['path'])==x['sha256'] for x in value['files'])
print(json.dumps({'sealPath':seal.relative_to(R).as_posix(),'sealSha256':sha(seal),'frozenFiles':len(value['files']),'archive':arch,'mainReportSha256':sha(main),'allCandidatePlusArchiveBytes':value['allCandidateFilesPlusArchiveBytes']},ensure_ascii=False,indent=2))
