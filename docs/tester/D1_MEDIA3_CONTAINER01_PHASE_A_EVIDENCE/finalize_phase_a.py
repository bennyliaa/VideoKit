from pathlib import Path
import json,hashlib,re,datetime
R=Path('D:/CodexProjects/VideoKit');E=Path(__file__).resolve().parent;B=R/'docs/coder/d1input-sink05';P=R/'docs/tester/D1_MEDIA3_CONTAINER01_PHASE_A_REPORT_V1.0.md'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
old=load(R/'docs/tester/D1_INPUT_SINK05_REVIEW_EVIDENCE/review-evidence-manifest.json');assert len(old['evidenceFiles'])==1093
for row in old['evidenceFiles']:assert sha(R/row['path'])==row['sha256']
assert sha(R/old['report'])==old['reportSha256']
for row in load(B/'evidence/input-sink05-freeze.json')['files']:assert sha(R/row['path'])==row['sha256']
for row in load(E/'source-pins.json'):assert sha(E/'source-snapshots'/Path(row['path']).name)==row['sha256']
cases=load(E/'independent-cases.json')['cases'];assert len(cases)==32 and len({c['id'] for c in cases})==32
assert load(E/'fixture-acceptance.json')['fixtureSha256'] is None and load(E/'fixture-acceptance.json')['newMediaBytesRead']==0
runtime=(E/'probe-runtime.stdout').read_text();assert runtime.count('PASS frozen_E6_guard')==5 and 'HOST_PLATFORM_LINKAGE_BLOCKED NoClassDefFoundError:android/util/SparseArray' in runtime and 'emittedBytes=0' in runtime and 'READY=0 COMMIT=NOT_RUN originalOwnerReturned=true' in runtime and 'sourceKeepers0 outputKeepers0' in runtime
assert all('static-libs' not in a for a in load(E/'probe-runtime.json')['argv'])
for i in range(14):assert load(E/f'abi-{i:02d}.json')['exitCode']==0
for x in re.findall(r'\]\((D:/[^)]+)\)',P.read_text(encoding='utf8')):assert Path(re.sub(r':\d+$','',x)).exists(),x
summary=dict(phase='A',result='BASELINE_REVIEW_COMPLETE_WITH_GAPS',newCandidateTested=False,phaseBStarted=False,staticRealABIClasses=14,baselineE6NegativeGuardChecks=5,muxerConstructor='HOST_PLATFORM_LINKAGE_BLOCKED_android_util_SparseArray',extractorRuntime='NOT_RUN_NEW_USE_ADMISSION_PENDING',qualifiedEncodedFixture='NOT_AVAILABLE',reusableIndependentCases=32,READYCalls=0,COMMIT='NOT_RUN',allActualJdkProcessesAndOriginalOwnerReturned=True,sourceAndOutputKeepers=0,deviceSdkGradleNetworkCalls=0,D1='NOT_PASSED',M0='NOT_STARTED')
(E/'phase-a-result.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf8')
records=[dict(path=p.relative_to(R).as_posix(),bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(E.rglob('*')) if p.is_file() and p.name!='phase-a-evidence-manifest.json']
out=dict(frozenAtUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),report=P.relative_to(R).as_posix(),reportBytes=P.stat().st_size,reportSha256=sha(P),result=summary['result'],evidenceFiles=records,oldBaselineAnd1093TesterEvidenceUnchanged=True,newCandidateReadOrTested=False,phaseBStarted=False,deviceSdkGradleNetworkCalls=0)
(E/'phase-a-evidence-manifest.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps({k:v for k,v in out.items() if k!='evidenceFiles'},ensure_ascii=False,indent=2));print('evidenceFiles',len(records))
