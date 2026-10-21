from pathlib import Path
import json,hashlib,shutil,datetime
B=Path(__file__).resolve().parents[1];R=B.parents[2];E=B/'evidence';assert not (E/'media3-container01-freeze.json').exists()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
source=R/'docs/tester/D1_MEDIA3_CONTAINER01_REVIEW_EVIDENCE/coder-documented-entry-prefreeze-003';summary=json.loads((source/'summary.json').read_text());assert not summary['frozenCandidate'] and len(summary['runs'])==56 and all(x['exitCode']==0 for x in summary['runs']);assert summary['toolSha256']==sha(B/'tools/review_all.py') and summary['productionJarSha256']==sha(B/'artifacts/media3-container01-classes.jar')
assert json.loads((source/'source/source-pins.json').read_text())==json.loads((E/'local-007/source-pins.json').read_text())
D=E/'documented-review-prefreeze';shutil.copytree(source,D,ignore=shutil.ignore_patterns('classes'))
rows=[]
for x in summary['runs']:
 p=D/(x['name']+'.json');r=json.loads(p.read_text());assert r['exitCode']==0 and r['originalProcessReturned']
 if x['mode']=='production':assert r['productionJarFirst'] and r['jarSha256']==summary['productionJarSha256']
 rows.append({'path':p.relative_to(B).as_posix(),'mode':x['mode'],'sha256':sha(p),'name':x['name']})
for mode in ['source','production']:
 text=(D/('extractor-input-'+mode+'.stdout')).read_text();assert 'M07_cumulative8MiB_rejected_BEFORE_next_original_read' in text and 'DONE seven boundary groups' in text
 assert 'MP4_parse_decode=NOT_RUN' in (D/('approved-read-'+mode+'.stdout')).read_text()
 assert 'NOT_RUN_PLATFORM' in (D/('platform-availability-'+mode+'.stdout')).read_text()
 dump(E/('runtime-origin-'+mode+'.json'),{'adapterOriginLines':[l for l in text.splitlines() if 'ORIGIN=' in l],'productionJarFirst':mode=='production','jarSha256':summary['productionJarSha256'],'actualMedia3InputJarSha256':sha(B/'deps/media3-extractor.jar'),'AndroidPlatformRuntime':False,'actualMp4ParseMuxAndDecode':'NOT_RUN'})
for name in ['tool-output-gate-final','review-runner-gate-final']:
 gate=json.loads((E/name/'summary.json').read_text());assert (len(gate['negativeCases'])==7) if 'negativeCases' in gate else gate['negativePaths']==7
failure=R/'docs/tester/D1_MEDIA3_CONTAINER01_REVIEW_EVIDENCE/coder-documented-entry-prefreeze-001';F=E/'prototype-review-entry-failure';shutil.copytree(failure,F,ignore=shutil.ignore_patterns('classes'))
dump(E/'prototype-check-history.json',{'reviewEntry001':{'outerExitCode':1,'exitObservation':'Coder tool returned exit1; parent failed while forming its receipt because of stale dynamic artifact path input-sink01-classes.jar','retainedScript':'evidence/review_all-before-artifact-path-fix.py','rawChildOutputs':'evidence/prototype-review-entry-failure','childCompileAndCoreReturned':all(json.loads((F/'source'/n).read_text())['exitCode']==0 for n in ['compile.json','checks.json']),'notFinalOrIndependent':True},'reviewEntry002':{'status':'SUCCESS_BEFORE_CUMULATIVE_BUDGET_REFINEMENT','retained':'evidence/pre-budget-fix/documented-review-002','jar':'evidence/pre-budget-fix/media3-container01-classes-build003.jar'},'budgetRefinement':{'sourceFix':'Reject before next read when aggregate8MiB exhausted; no speculative EOF byte','regression':'M07:128x64KiB, next host read not entered','finalLocal':'007','finalBuild':'004','finalReview':'prefreeze-003'},'build001':'Gradle daemon communication failed, no task success','build002':'33 tasks executed before final source refinements','build003':'4 executed29 up-to-date, prior successful artifact retained','build004':'4 executed29 up-to-date, final strict offline artifact','historicalFailuresNotRewritten':True})
dump(E/'batch-validation.json',{'candidate':B.name,'result':'LIMITED_REAL_READING_PROGRESS_WITH_EXPLICIT_GAPS','independent':'PENDING','D1':'NOT_PASSED','M0':'NOT_STARTED','finalLocal':'007','finalBuild':'004','finalDocumentedEntry':'prefreeze-003','runs':rows,'topLevelReturnedProcesses':56,'newBoundaryGroups':7,'approvedRawSampleReadModes':2,'platformProbesAreAccurateNOT_RUNNotContainerPASS':True,'countsOverlapNotSummed':True,'newCodedFixture':False,'realMp4StructureAndMuxedPayload':'NOT_RUN','deviceSdkFieldOperations':0,'newAndroidPlatformPorts':0})
scope=json.loads((B/'reference/approved-sample-scope.json').read_text(encoding='utf-8'));assert sha(R/scope['path'])==scope['sha256']
dump(E/'sample-read-only-postcheck.json',{'originalSha256':scope['sha256'],'actualAfterAllChecksSha256':sha(R/scope['path']),'unchanged':True,'includedInSourceZip':False})
print('FINAL source/JAR-first56 original process receipts verified;7 new reading boundary groups, platform parse/mux NOT_RUN.')
