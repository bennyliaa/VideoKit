from pathlib import Path
import json,hashlib,re,difflib
R=Path('D:/CodexProjects/VideoKit');B=R/'docs/coder/d1input-sink05';E=B/'evidence';assert not (E/'input-sink05-freeze.json').exists()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
proofs=[]
for directory,mode in [('suites-004','source'),('suites-005','production')]:
 D=E/directory
 for stem,marker,n in [('orders','responseOrderCases=30',30),('coordinator-orders','coordinatorOrderCases=7',7),('original-responses','originalResponseRegressions=2',2),('independent-host','independentResultCases=8',8),('results','hostResultCases=88',88),('transitions','transitionCases=33',33)]:
  p=D/(stem+'.stdout');receipt=json.loads((D/(stem+'.json')).read_text());assert marker in p.read_text() and receipt['exitCode']==0 and receipt['originalProcessReturned'] and not (D/(stem+'.stderr')).read_bytes();proofs.append({'mode':mode,'suite':stem,'count':n,'path':p.relative_to(B).as_posix(),'sha256':sha(p)})
raw=(E/'suites-005/orders.stdout').read_text();names=[l[11:] for l in raw.splitlines() if l.startswith('PASS order ')];assert len(names)==30
observations=[]
for line in raw.splitlines():
 if not line.startswith('OBSERVE '):continue
 facts={k:v for k,v in re.findall(r'(\w+)=([^\s]+)',line)}
 for k,v in list(facts.items()):
  if v in ['true','false']:facts[k]=v=='true'
  elif v=='null':facts[k]=None
  elif v.isdigit():facts[k]=int(v)
 observations.append({'facts':facts,'rawLine':line})
assert len(observations)==67
for x in observations:
 f=x['facts'];assert not(f['readyAck'] and f['abortedAck'])
 if f['ownerReturned']:assert f['retained']==0 and f['scopedObserversReturned'] and f['coordinatorResponsesCompleted']
 else:assert f['retained']==1
 if f['order'].endswith('_RETURNED'):assert f['ownerReturned']
assert len([x for x in observations if x['facts']['order'].endswith('_RETURNED')])==30
dump(B/'response-order-matrix.json',{'candidate':'D1-20261021-INPUT-SINK05','caseCount':30,'cases':names,'coordinatorCases':7,'originalDefectRegressions':2,'proofs':proofs,'observations':observations,'notAMathematicalAllProtocolProof':True,'countsOverlapNotSummed':True,'finalSameOriginalGatesCallbacksThreadsJoined':True,'sourceKeepers':0,'outputKeepers':0,'newIndependentReview':'PENDING','platformAndRealPublication':'NOT_RUN'})
returnRaw=(E/'suites-005/results.stdout').read_text();returnCases=[line[12:] for line in returnRaw.splitlines() if line.startswith('PASS result ')];assert len(returnCases)==88
dump(B/'return-value-matrix.json',{'candidate':'D1-20261021-INPUT-SINK05','hostResultCases':returnCases,'transitionCaseCount':33,'originalQueryCaseCount':2,'sourceRun':'evidence/suites-004/results.stdout','productionRun':'evidence/suites-005/results.stdout','productionSha256':sha(E/'suites-005/results.stdout'),'boundOriginalSources':'checks/com/videokit/d1input/HostResultCheck.java and TransitionCheck.java unchanged from INPUT_SINK04','overlapNotSummed':True,'newIndependentReview':'PENDING'})
dump(E/'response-fact-adoption-model.json',{'originalReadyTransportFact':['readyResponseReceived','readyResponseSucceeded','originalReadyResponseToken (private retained, never logged)'],'adoptionFact':['readyResponseAccepted','readyResponseRejection','readyAck','abortedAck','readyToken (accepted only)'],'rejectedReasonExamples':['CONFLICT_WITH_ABORTED','CONFLICT_WITH_READY','TOKEN_CHANGED','TERMINAL_REGRESSION','INVALID_RESULT','ORIGINAL_ACK_FAILED'],'oneAtomicGate':'TemporaryOutput.acceptTerminal for first/late ACK, awaited READY, QUERY, readonly authority, derived coordinator terminal; coordinator accepts its own terminal results via shared acceptTerminal','conflictUnknownClearedOnlyBy':'accurate compatible original QUERY or readonly original arbitration, never matching ACK/derived cached result alone','physicalEligibility':['same direct original future consumed','same scoped original response view answered','actual scoped whenComplete return stage complete','original host/validator/commit/readback tasks returned','same coordinator result and actual observer stages returned','original coordinator executor terminated and every actual original worker joined'],'zeroOutstandingCounterNotPositiveProof':True,'originalReferenceBound':'eight existing coordinator calls, prune only actual observer returned; same original worker references still retained for join','noNewExecutorLedgerProtocolFields':True,'unknownAuthorityMissingFields':'same inherited opaque port/task/token contract; no new IDs/nonce/crypto/physicalFD proof'})
coord=(E/'suites-005/coordinator-orders.stdout').read_text();assert 'callbacks=0 responsesComplete=false' in coord and 'zeroCounter_actualOriginalObserverAndThreadJoined' in coord
before=E/'suites-001/ResponseOrderCheck-before-wait-fix.java';pins=json.loads((E/'local-002/source-pins.json').read_text());pinned=next(x['sha256'] for x in pins if x['path'].endswith('/ResponseOrderCheck.java'));assert sha(before)==pinned
dump(E/'prototype-check-history.json',{'initialRun':'suites-001/orders.json','exitCode':json.loads((E/'suites-001/orders.json').read_text())['exitCode'],'originalProcessReturned':True,'initialCheckSourceSha256':sha(before),'reason':'test assumed immediate worker return after releasing same original gate; correct stable pending reached cleanup before worker scheduled','productSourceChangedForThisFix':False,'correction':'bounded retries of metadata-only finish while same original worker/response returns, then actual same-thread join; no new RPC, replacement task or SDK state mutation','initialExitNotReturnProof':True,'finalEffectiveSource':'suites-004/orders.stdout','finalEffectiveProduction':'suites-005/orders.stdout','allFinalActualOriginalsJoined':True})
old=R/'docs/coder/d1input-sink04/tools/local_check.py';new=B/'tools/local_check.py';dump(E/'tool-root-regression.json',{'entryToolByteIdenticalToAcceptedInput04':old.read_bytes()==new.read_bytes(),'entryToolSha256':sha(new),'candidateDerivedRoot':'D:/CodexProjects/VideoKit/docs/tester/D1_INPUT_SINK05_REVIEW_EVIDENCE','actualCompilePositiveAnd7Negative':'tool-output-gate/summary.json','fullRunnerPositiveAnd7Negative':'review-runner-gate/summary.json','newRootNotOldEvidence':True})
gate=json.loads((E/'tool-output-gate/summary.json').read_text());runner=json.loads((E/'review-runner-gate/summary.json').read_text());assert gate['positiveActualJdkCompileAnd20Groups'] and len(gate['negativeCases'])==7 and runner['positiveOriginalReturnedRuns']==50 and runner['negativePaths']==7 and runner['runnerSha256']==sha(B/'tools/review_all.py')
mapping=json.loads((B/'independent-regression-map.json').read_text())
for x in mapping['cases']:
 if x['id'] in ['S03','S06']:x['newEvidence']+=['evidence/suites-005/original-responses.stdout','evidence/suites-005/orders.stdout','evidence/suites-005/coordinator-orders.stdout']
 if x['id']=='F01':x['newEvidence']+=['evidence/tool-output-gate/summary.json','evidence/review-runner-gate/summary.json']
dump(B/'independent-regression-map.json',mapping)
for name in ['contradictory_aborted-source','contradictory_aborted-production','normal_query_ready-source','normal_query_ready-production']:assert json.loads((E/'input04-reproduction'/(name+'.json')).read_text())['exitCode']==0
batch=json.loads((E/'batch-validation.json').read_text());batch.update(oldFrozenFilesUnchanged=3683,responseOrderCases=30,coordinatorOrderCases=7,originalResponseRegressions=2,reviewOutputActualPositive=True,reviewOutputNegativePathsPerEntry=7,documentedRunnerTopLevelRuns=50,prototypeTestTimingFailurePreserved=True);dump(E/'batch-validation.json',batch)
print('Finite causal order facts/stages/callbacks/thread joins bound; prototype timing failure retained honestly')
