from pathlib import Path
import json,hashlib,re,datetime
R=Path('D:/CodexProjects/VideoKit');B=R/'docs/coder/d1input-sink03';E=B/'evidence';assert not (E/'input-sink03-freeze.json').exists()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
jar=B/'artifacts/input-sink03-classes.jar';runs=[]
for directory,mode in [('suites-004','source'),('suites-005','production')]:
 D=E/directory;receipts=sorted(D.glob('*.json'));assert len(receipts)==16
 for p in receipts:
  r=json.loads(p.read_text());assert r['exitCode']==0 and r['originalProcessReturned'] and r['mode']==mode and r['sourcePins']=='evidence/local-005/source-pins.json';assert not p.with_suffix('.stderr').read_bytes()
  if mode=='production':assert r['productionJarFirst'] and r['jarSha256']==sha(jar) and r['argv'][3].split(';')[0]==str(jar)
  runs.append({'path':p.relative_to(B).as_posix(),'sha256':sha(p),'mode':mode,'exitCode':0,'originalProcessReturned':True})
 for stem,marker in [('core','groups=20'),('original17','originalReturnScenarios=17'),('tester12','testerIndependentScenarios=12'),('input','inputExceptionCases=5'),('matrix','phaseExceptionCases=63')]:assert marker in (D/(stem+'.stdout')).read_text()
 assert len([l for l in (D/'matrix.stdout').read_text().splitlines() if l.startswith('PASS matrix ')])==63
 assert 'sameOriginalThreadsJoined=true sourceKeepers=0 outputKeepers=0' in (D/'matrix.stdout').read_text()
assert 'ORIGIN=file:/D:/CodexProjects/VideoKit/docs/coder/d1input-sink03/artifacts/input-sink03-classes.jar' in (E/'suites-005/matrix.stdout').read_text()
phases=['WRITE','FLUSH','CLOSE','REOPEN','VALIDATE','READY','COMMIT','ABORT','QUERY'];modes=['ACK','EXEC','CANCEL','LATE_ACK','LATE_EXEC','LATE_CANCEL','THROW_CANCEL'];observations=[]
for line in (E/'suites-005/matrix.stdout').read_text().splitlines():
 if not line.startswith('OBSERVE '):continue
 facts={k:v for k,v in re.findall(r'(\w+)=([^\s]+)',line)}
 for k,v in list(facts.items()):
  if v in ['true','false']:facts[k]=v=='true'
  elif v=='null':facts[k]=None
  elif v.isdigit():facts[k]=int(v)
 observations.append({'facts':facts,'rawLine':line})
assert len(observations)==126
matrix=[]
for phase in phases:
 for mode in modes:
  pair=[x for x in observations if x['facts']['phase']==phase and x['facts']['mode']==mode];assert len(pair)==2 and pair[-1]['facts']['ownerReturned'] and pair[-1]['facts']['retained']==0
  assert (pair[-1]['facts']['error'] is None)==(mode=='ACK')
  matrix.append({'phase':phase,'resultMode':mode,'coderResult':'PASS_LIMITED_OFFLINE','sourceRun':'evidence/suites-004/matrix.stdout','productionRun':'evidence/suites-005/matrix.stdout','entryCount':1,'sameActualOriginalThreadJoined':True,'ownerReturnedAfterAccurateTerminalProof':True,'byteUnknownApplies':phase=='WRITE','businessCommitOutcomeApplies':phase=='COMMIT','asynchronousTailApplies':mode!='THROW_CANCEL','observations':pair})
dump(B/'phase-exception-matrix.json',{'candidate':'D1-20261021-INPUT-SINK03','phases':phases,'modes':modes,'cases':matrix,'caseCount':63,'notAllDistinctFromOtherSuites':True,'realPlatform':'NOT_RUN','newIndependentReview':'PENDING'})
dump(E/'original-phase-observations.json',{'productionJarSha256':sha(jar),'logSha256':sha(E/'suites-005/matrix.stdout'),'originalAuthorityQueryScope':'exact original COMMIT/task/token and original host query; no accessor RPC/retry','observations':observations,'original17Log':'suites-005/original17.stdout','final':'same originals joined; sources0 outputs0','platform':'NOT_RUN'})
old=json.loads((B/'reference/independent-case-results.json').read_text());rows=[]
for x in old['cases']:
 i=x['id'];rows.append({'id':i,'title':x['title'],'historicalInputSink02IndependentRow':x,'newCoder':'NOT_RUN_PLATFORM' if i=='S05' else 'PASS_LIMITED_OFFLINE_PENDING_INDEPENDENT_REVIEW','newEvidence':['evidence/suites-005/core.stdout']+(['evidence/suites-005/matrix.stdout','evidence/suites-005/original17.stdout'] if i in ['S01','S03','S04','S06'] else []),'newIndependent':'PENDING'})
assert len(rows)==19
dump(B/'independent-regression-map.json',{'candidate':'D1-20261021-INPUT-SINK03','oldIndependentOverall':'FAIL_B03_B04_UNCHANGED','cases':rows,'allPlatformPass':False,'newIndependentReview':'PENDING'})
cases23=[{'case':'tester12_'+str(i+1),'run':'tester12','sourceUnmodified':True} for i in range(12)]+[{'case':'readback_registry','run':'readback','sourceUnmodified':True}]+[{'case':'cancel_'+p,'run':'cancel-'+p,'newSafeAssertions':True} for p in ['WRITE','FLUSH','CLOSE','REOPEN','VALIDATE','COMMIT']]+[{'case':'late_cancel','run':'latecancel','newSafeAssertions':True}]+[{'case':'history_'+p,'run':'history-'+p,'newSafeAssertions':True} for p in ['ABORT','QUERY','ABORT_ERROR']]
assert len(cases23)==23
for p in ['IndependentFixCheck.java','ReadbackReturnCheck.java']:assert (B/'reference'/p).read_bytes()==(B/'checks/com/videokit/d1input'/p).read_bytes()
for x in cases23:x.update(coder='PASS_LIMITED_OFFLINE',sourceDirectory='evidence/suites-004',productionDirectory='evidence/suites-005',independent='PENDING')
dump(B/'tester23-regression-map.json',{'cases':cases23,'count':23,'oldFailingInputs':10,'oldFailingCodeAndLogs':'reference: historical reproduction, not new PASS','sourceAndJarPathsDoNotIncreaseCaseCount':True})
for name in ['D1_INPUT_SINK03_FIX_CODER_REQUIREMENTS_V1.0.md','D1_INPUT_SINK03_FIX_TESTER_REQUIREMENTS_V1.0.md']:assert (B/'reference'/name).read_bytes()==(R/'docs/milestones'/name).read_bytes()
assert sha(B/'reference/D1_INPUT_SINK02_FIX_REVIEW_REPORT_V1.0.md')=='c176949cf1c68978bf600ee62997e53360234835f09679ad816fd785db3db71f'
fixture=E/'suites-005/generated-4b.tmp';assert fixture.stat().st_size==4
dump(E/'generated-fixture-identities.json',{'path':fixture.relative_to(B).as_posix(),'bytes':4,'sha256':sha(fixture),'seed':0x20261020,'maxTestBlockBytes':65537,'newFaultBlocksAtMostBytes':32,'giantFileAllocated':False,'actualContainer':False})
items=[('B03_P2','PASS','finite direct/late cancellation consumption, redaction, WRITE UNKNOWN; tester pending'),('B04_P2','PASS','entered cleanup history/deadline race; unadmitted pending not failure; tester pending'),('B01_B02','PASS','old limited independent findings retained; new20/17/23 regression'),('A01_A02','PASS','same Provider/epoch; physical10 ACK3 caller3 UNKNOWN'),('PHASE_EXCEPTION_63','PASS','nine phases/seven modes; original threads/unknown proof/terminal cleanup'),('INPUT_EXCEPTION_5','PASS','unchanged input production; error/cancel/original return'),('STRICT_BUILD_002','PASS','real Android/Media3 ABI; build001 superseded for necessary deadline fix'),('DEPENDENCIES','PASS','15 coordinates/locks/metadata/deps unchanged; limited prior license intake'),('FROZEN_2349','PASS','all old frozen files unchanged'),('NEW_INDEPENDENT_REVIEW','BLOCKED','await new complete tester review'),('PLATFORM_AND_REAL_PUBLICATION','NOT_RUN','actual FD/fsync/codec/muxer/container/business COMMIT not executed'),('M0','NOT_RUN','not started; temporary API not final'),('FULL_D1','BLOCKED','inherited P0/UNKNOWN/dangerous chain/licenses remain')]
dump(B/'completion-matrix.json',{'candidate':'D1-20261021-INPUT-SINK03','D1':'NOT_PASSED','M0':'NOT_STARTED','coderLimitedFix':'PASS','newIndependentResult':'PENDING','rows':[{'id':i,'status':s,'scope':t} for i,s,t in items]})
dump(E/'batch-validation.json',{'candidate':'D1-20261021-INPUT-SINK03','createdUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'coder':'PASS_LIMITED_OFFLINE','independent':'PENDING','finalSourceLocal':'005','finalSourceSuite':'004','finalProductionSuite':'005','strictBuild':'002','supersededBuild':'001: repaired deadline/lateACK race; original log/hash retained','coreGroups':20,'originalReturnCases':17,'testerRegressionCases':23,'phaseExceptionCases':63,'inputExceptionCases':5,'countsOverlapNotSummed':True,'runs':runs,'productionJarSha256':sha(jar),'deviceSdkFieldOperations':0,'oldHandleQueries':0,'occupancyQueries':0,'nativeOrExternalHostBuilds':0,'newBinaryDownloads':0,'realMediaFormatValidation':'NOT_RUN','hostBusinessPublication':'NOT_RUN','D1':'NOT_PASSED','M0':'NOT_STARTED','noExecutionAuthorityCreated':True})
print('FINAL source + production JAR 20/17/23/63/5 PASS; independent PENDING')

