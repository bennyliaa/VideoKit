from pathlib import Path
import json,hashlib,datetime
R=Path('D:/CodexProjects/VideoKit');E=Path(__file__).resolve().parent;B=R/'docs/coder/d1fixture-tool02'
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
own=load(E/'own-helper-summary.json');doc=load(E/'checks-001/summary.json');assert own['groupsPerPath']==17 and doc['groupsPerPath']==29
assert own['allStartedWorkersActuallyJoined'] and doc['allOriginalProcessesReturned'] and own['combinedDocumentedAndOwnAllocatedPayloadBytes']==40320 and own['combinedDocumentedAndOwnNativeRequestBytes']==1366
for name in ['own-source','own-production','helper-compile']:
 x=load(E/name/'owner.json');assert x['exitCode']==0 and x['originalProcessReturned'] and x['outputHandlesClosed'] and not x['timedOutSticky']
for x in doc['runs']:assert x['exitCode']==0 and x['originalProcessReturned'] and x['outputHandlesClosed'] and not x['timedOutSticky']
for x in load(B/'evidence/fixture-tool02-freeze.json')['files']:p=R/x['path'];assert p.stat().st_size==x['bytes'] and sha(p)==x['sha256']
recipe=load(B/'evidence/build-recipe.json');build=load(B/'evidence/build-result.json');assert len(recipe['commands'])==2 and [x['argv'] for x in build['tools']]==recipe['commands']
for argv in recipe['commands']:assert '-J-Xmx512m' in argv
a=recipe['commands'][0];assert '-proc:none' in a and '-implicit:none' in a
for flag in ['-classpath','-sourcepath','-processorpath']:p=Path(a[a.index(flag)+1]);assert p.is_dir() and not any(p.iterdir())
sourceArg=Path(next(x[1:] for x in a if x.startswith('@')));assert len(sourceArg.read_text().splitlines())==713
cases=load(R/'docs/tester/D1_FIXTURE_TOOL01_BUILD_PHASE_A_EVIDENCE/independent-driver-oracles.json')['cases']
runtimeIds={'FT09','FT10','FT11','FT12','FT13','FT14','FT15','FT16','FT22','FT23'}
staticIds={'FT01','FT02','FT03','FT04','FT05','FT06','FT25','FT26','FT27','FT28'}
for c in cases:
 c['stageAStatus']=c['status'];c['newToolVerdict']='LIMITED_CURRENT_SCOPE';c['generationAuthorized']=False
 c['status']='PASS_NONMEDIA_LIMITED' if c['id'] in runtimeIds else 'PASS_STATIC_MATERIAL_ONLY' if c['id'] in staticIds else 'STATIC_REVIEWED_REAL_GENERATION_OR_FILE_PATH_NOT_RUN'
 c['runtimeScope']='Memory NativePort/WorkerDeadline/original callback/real worker join only; no Job/Main/encoder/muxer/OS FileChannel'
 c['realMediaPlatform']='NOT_RUN'
out=dict(overall='PASS_LIMITED_NONMEDIA_FIX_WITH_GENERATION_NOT_RUN',FT_B01='CLOSED_FOR_SPECIFIED_NONMEDIA_CALL_AND_ADOPTION_SNAPSHOT_SCOPE',FT_B02='CLOSED_FOR_SPECIFIED_MONOTONIC_BODY_COMPLETION_PLUS_REAL_JOIN_SCOPE',newFindings=0,cases=cases,originalHistoricalFailNotRewritten=True)
(E/'independent-ft01-ft28-results.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
result=dict(checkedUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),result='PASS_CURRENT_FINITE_SCOPE_AND_PRESERVATION',candidateRecordsUnchanged=2774,documentedGroupsPerPath=29,independentGroupsPerPath=17,independentOriginalWorkersJoinedPerPath=16,combinedAllocatedPayloadBytes=40320,combinedNativeRequestBytes=1366,combinedControlledReturnedOrPhysicalPayloadBytes=1148+90,reviewerHelperCompiles=1,reviewerControlledJvmProcessesReturned=4,rawGenerationOrOSFileChannelOperations=0,expectedRetainedMemoryCloseUnknown='One per JVM, four total across documented+independent. Memory objects only, retained until each JVM exits; not OS descriptor close proof.',oldSessionsQueriedOrDisposed=False,newFindings=0)
(E/'post-review-preservation.json').write_text(json.dumps(result,indent=2),encoding='utf8');print(json.dumps(result,indent=2))
