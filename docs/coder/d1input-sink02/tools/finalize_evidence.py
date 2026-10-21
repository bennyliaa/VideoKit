from pathlib import Path
import json,hashlib,re,datetime
R=Path('D:/CodexProjects/VideoKit');B=R/'docs/coder/d1input-sink02';E=B/'evidence';assert not (E/'input-sink02-freeze.json').exists()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
jar=B/'artifacts/input-sink02-classes.jar'
for directory in ['return-003','production-core-001']:
 p=E/directory;receipt=json.loads((p/'run.json').read_text());assert receipt['exitCode']==0 and receipt['originalProcessReturned'] and receipt['productionJarFirst'] and receipt['jarSha256']==sha(jar) and receipt['argv'][3].split(';')[0]==str(jar);assert not (p/'run.stderr').read_bytes()
raw=(E/'return-003/run.stdout').read_text();assert 'ORIGIN TemporaryOutput=file:/D:/CodexProjects/VideoKit/docs/coder/d1input-sink02/artifacts/input-sink02-classes.jar' in raw
cases=[l[5:] for l in raw.splitlines() if l.startswith('PASS ')];assert len(cases)==17 and 'originalThreadsJoined=true retainedSources=0 retainedOutputs=0' in raw
observations=[]
for line in raw.splitlines():
 if not line.startswith('OBSERVE '):continue
 label=line.split()[1];facts={k:v for k,v in re.findall(r'(\w+)=([^\s]+)',line)}
 for k,v in list(facts.items()):
  if v in ['true','false']:facts[k]=v=='true'
  elif v=='null':facts[k]=None
  elif v.isdigit():facts[k]=int(v)
 observations.append({'label':label,'facts':facts,'rawLine':line})
dump(E/'original-phase-observations.json',{'source':'return-003/run.stdout','sourceSha256':sha(E/'return-003/run.stdout'),'sameActualHostOriginalThreadNotReplacement':True,'productionJarSha256':sha(jar),'scenarios':cases,'observations':observations,'finalOriginalThreadsJoined':True,'retainedSources':0,'retainedOutputs':0,'realMedia':'NOT_RUN'})
baseline=json.loads((B/'reference/independent-case-results.json').read_text());rows=[]
core=(E/'production-core-001/run.stdout').read_text();assert 'groups=20' in core
for x in baseline['cases']:
 i=x['id'];rows.append({'id':i,'title':x['title'],'oldInputSink01PhaseB':x['phaseB'],'oldBaselineAssertionHistorical':x['assertion'],'newCoder':'NOT_RUN_PLATFORM' if i=='S05' else 'PASS_LIMITED_OFFLINE_PENDING_INDEPENDENT_REVIEW','newEvidence':'evidence/production-core-001/run.stdout'+(' + evidence/return-003/run.stdout' if i in ['I10','I11','S01','S03','S04','S06'] else ''),'scope':('Real Android FD/codec/muxer/fsync/container remains NOT_RUN; capability checks do not substitute' if i=='S05' else 'Real Media3 API + bounded host ports; no actual media validation/host publication claim'),'newIndependentResult':'PENDING'})
assert len(rows)==19
dump(B/'independent-regression-map.json',{'candidate':'D1-20261021-INPUT-SINK02','oldCandidate':'D1-20261021-INPUT-SINK01','oldIndependentOverall':'FAIL_B01_B02_UNCHANGED','cases':rows,'coderSemanticGroups':20,'coderOriginalReturnScenarios':17,'newOverall':'PENDING_INDEPENDENT_REVIEW','allPlatformPass':False})
matrix=[('B01_P2','PASS','coder: unadmitted flush/close flags stay false; actual write/flush/close tail joined then exactly once; tester pending'),('B02_P1','PASS','coder: distinct scoped original proof, no early owner return/READY/COMMIT; real ACK preserved; tester pending'),('A01','PASS','shared Provider/cross factory/new epoch/opaque input; input production unchanged'),('A02','PASS','physical10 ACK3 callerPos3 UNKNOWN sticky; no retry/refund'),('ORIGINAL_20_GROUPS','PASS','local003 and production-core001'),('ORIGINAL_RETURN_17','PASS','source return002 and production JAR first return003; actual same host thread joins'),('ACTUAL_FRAMEWORK_BUILD','PASS','build-main001 offline strict metadata/locks; real Android/Media3 compile'),('DEPENDENCY_IDENTITY_LICENSE','PASS','15 unchanged coordinates; inherit Phase B limited offline acceptance only'),('FROZEN_2033','PASS','all previous 2033 frozen files unchanged'),('NEW_INDEPENDENT_REVIEW','BLOCKED','waiting for tester review of this full frozen candidate'),('PLATFORM_FD_CODEC_MUXER_MEDIA','NOT_RUN','actual Android FD/fsync/codec/muxer/container not executed'),('DEVICE_AND_REAL_HOST_PUBLICATION','NOT_RUN','zero SDK/ADB/5037/device/old handle/occupancy queries; controlled COMMIT only'),('M0','NOT_RUN','not started; temporary interface not final public API'),('FULL_D1','BLOCKED','inherited UNKNOWN/P0/dangerous chain/licenses and actual effects remain open')]
dump(B/'completion-matrix.json',{'candidate':'D1-20261021-INPUT-SINK02','D1':'NOT_PASSED','M0':'NOT_STARTED','coderLimitedFix':'PASS','newIndependentResult':'PENDING','rows':[{'id':i,'status':s,'scope':t} for i,s,t in matrix]})
fixture=E/'production-core-001/generated-4b.tmp';assert fixture.stat().st_size==4
dump(E/'generated-fixture-identities.json',{'fixture':fixture.relative_to(B).as_posix(),'bytes':4,'sha256':sha(fixture),'seed':0x20261020,'pattern':'((position*1664525+0x20261020) >>>9)&255','sparseLogicalOffset':3*1024*1024*1024+7,'maxTestBlockBytes':65537,'actualContainer':False,'giantFileAllocated':False})
requirements=[B/'reference/D1_INPUT_SINK02_FIX_CODER_REQUIREMENTS_V1.0.md',B/'reference/D1_INPUT_SINK02_FIX_TESTER_REQUIREMENTS_V1.0.md']
for p in requirements:assert p.read_bytes()==(R/'docs/milestones'/p.name).read_bytes()
dump(E/'batch-validation.json',{'candidate':'D1-20261021-INPUT-SINK02','createdUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'coder':'PASS_LIMITED_OFFLINE','independent':'PENDING','finalSourceLocal':'003','finalSourceReturn':'002','finalProductionReturn':'003','productionCore':'001','strictBuild':'001','coreGroups':20,'originalReturnCases':17,'testerOriginalFiveBaselineReproduced':True,'oldFiveLogSha256':sha(E/'old-five-scenarios/reproduce.stdout'),'productionJarSha256':sha(jar),'requirements':[{'path':p.relative_to(B).as_posix(),'sha256':sha(p)} for p in requirements],'newBinaryDownloads':0,'deviceSdkFieldOperations':0,'oldHandleQueries':0,'occupancyQueries':0,'nativeOrExternalHostBuilds':0,'realMediaFormatValidation':'NOT_RUN','hostBusinessPublication':'NOT_RUN','D1':'NOT_PASSED','M0':'NOT_STARTED','noExecutionAuthorityCreated':True})
print('FINAL EVIDENCE: 20 core + 17 same-original boundaries; 19-row map; independent pending')
