from pathlib import Path
import json,re,hashlib,difflib
R=Path('D:/CodexProjects/VideoKit');B=R/'docs/coder/d1input-sink04';O=R/'docs/coder/d1input-sink03';E=B/'evidence';assert not (E/'input-sink04-freeze.json').exists()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
rows=[]
for mode,directory in [('source','suites-003'),('production','suites-004')]:
 D=E/directory
 for stem,marker,count in [('results','hostResultCases=88',88),('transitions','transitionCases=33',33),('query-original','originalQueryCases=2',2),('independent-authority','independentAuthorityScenarios=3',3),('independent-cancel','independent_cancel_cases=6',6)]:
  raw=(D/(stem+'.stdout')).read_text();r=json.loads((D/(stem+'.json')).read_text());assert marker in raw and r['exitCode']==0 and r['originalProcessReturned'] and not (D/(stem+'.stderr')).read_bytes();rows.append({'mode':mode,'suite':stem,'cases':count,'log':(D/(stem+'.stdout')).relative_to(B).as_posix(),'sha256':sha(D/(stem+'.stdout')),'independentResult':'PENDING'})
 if mode=='production':assert 'ORIGIN=file:/D:/CodexProjects/VideoKit/docs/coder/d1input-sink04/artifacts/input-sink04-classes.jar' in (D/'results.stdout').read_text()
raw=(E/'suites-004/results.stdout').read_text();cases=[l[12:] for l in raw.splitlines() if l.startswith('PASS result ')];assert len(cases)==88
observations=[]
for line in raw.splitlines():
 if not line.startswith('OBSERVE '):continue
 facts={k:v for k,v in re.findall(r'(\w+)=([^\s]+)',line)}
 for k,v in list(facts.items()):
  if v in ['true','false']:facts[k]=v=='true'
  elif v=='null':facts[k]=None
  elif v.isdigit():facts[k]=int(v)
 observations.append({'facts':facts,'rawLine':line})
assert len(observations)==180
for x in observations:
 f=x['facts']
 if f['point']=='EXACT_ORIGINAL_RETURNED_AND_TERMINAL_PROVEN':assert f['ownerReturned'] and f['retained']==0
 if f['point']=='ORIGINAL_TAIL':assert f['alive'] and not f['ownerReturned'] and f['retained']==1
dump(B/'return-value-matrix.json',{'candidate':'D1-20261021-INPUT-SINK04','hostResultCases':cases,'hostResultCaseCount':88,'transitionCaseCount':33,'originalQueryCaseCount':2,'observations':observations,'runs':rows,'countOverlapNotSummed':True,'newIndependent':'PENDING','allOriginalThreadsJoined':True,'finalSourceKeepers':0,'finalOutputKeepers':0,'actualPlatform':'NOT_RUN'})
boundary=[('GRANT','existing opaqueTask regex/capabilities; immutable task snapshot','null/format/length/getter throw/capability null','before owner admission; stable error'),('WRITE','Integer count in 1..originalCount; admission enforces offset/extent/budget bounds','null/0/negative/count+1/Integer.MAX/Long/type/null-stage/late-invalid','no ACK lower/position update; UNKNOWN original request once; no resubmit/refund'),('FLUSH_CLOSE','successful Void completion must be null; physical writer proof remains separate','non-null number/string/null-stage/late-invalid','ACK_FAILED or INVOCATION_UNKNOWN; no double operation; cleanup only via accurate originals'),('REOPEN','Provider/Handle non-null, declared length valid or null unknown, actual EOF extent, sequential digest','wrong type/null provider/null handle/negative/huge/mismatched length/wrong digest/bad read count','no validation or READY; original read registry/workers retained until actually returned'),('VALIDATE','same captured task, exact extent and computed hash, existing kind, structurallyValid','null/wrong type/wrong task/hash/kind/negative or overflowing bytes/false/null-stage/late','consume invalid receipt once; no READY/revalidation'),('READY','String token nonempty, some non-whitespace char, no ISO control; preserve any existing valid token','null/type/empty/blank/control/null-stage/late','no fabricated READY; protocol unknown held until accurate same original arbitration'),('COMMIT','Void null ACK; same original Commit/task/token; three-state readonly outcome','non-null/type/null-stage/late; null/throw/UNKNOWN authority','ACK and actual confirmed business fact separate; default UNKNOWN holds until exact original fact'),('ABORT_QUERY','ABORT Void null; Status and state non-null; READY requires valid token, all other states require null token','null/type/null state/empty READY/inconsistent state-token/null-stage/late; known terminal contradiction','before updating business facts, stable protocol firstFailure; same cached RPC only; bad result does not prove rollback'),('TERMINAL_AUTHORITY','same exact original task accessor; status rules and compatible transitions identical','null/throw/invalid status-token/known READY token substitution/READY vs ABORTED contradiction/backward WRITING','read only after same original tasks returned; invalid fact cannot erase prior ACK/terminal or release; accurate compatible proof can resolve')]
dump(B/'host-return-boundary-map.json',{'boundaries':[{'phase':a,'existingContractValidation':b,'coveredInvalidOrUnknownValues':c,'requiredBehavior':d} for a,b,c,d in boundary],'notDefinedInCurrentContract':['Status has no returned task/output/authorization ID: bind captured task parameter and same original port; do not invent a response nonce','Provider/Handle has no returned file/FD/source identity: existing capability plus full extent/bytes/sequential hash does not prove same physical FD','CommitOutcome enum has no returned task/token fields: exact arguments + same retained object; host truthfulness/persistence not independently verified','Opaque token has no crypto/encoding/expiry schema; no invented JWT/ASCII schema or arbitrary length threshold','Random-output mode has no independently supplied expected final hash; existing scope remains capability/extent/readback + controlled validation, not actual media or physical identity proof'],'nonApplicable':['Only WRITE has byte ACK/caller position/UNKNOWN reservation','Void null is valid success; null Status/Provider/Validation/token is not','WRITING/UNKNOWN with null token are valid nonterminal responses; cannot establish terminal release','Synchronous null-stage supplies no future; retain invocation UNKNOWN without inventing a late stage'],'newFrameworksOrProtocolFields':0,'actualPlatformAndBusinessPublication':'NOT_RUN'})
gate=json.loads((E/'tool-output-gate/summary.json').read_text());assert gate['positiveActualJdkCompileAnd20Groups'] and len(gate['negativeCases'])==7 and gate['toolSha256']==sha(B/'tools/local_check.py') and gate['positivePinsMatchFinalLocal005']
old=(O/'tools/local_check.py');new=B/'tools/local_check.py';(E/'local-check-source-diff.patch').write_text(''.join(difflib.unified_diff(old.read_text().splitlines(True),new.read_text().splitlines(True),fromfile=old.relative_to(R).as_posix(),tofile=new.relative_to(R).as_posix())),encoding='utf-8');dump(E/'tool-differences.json',{'oldToolSha256':sha(old),'newToolSha256':sha(new),'derivedFromCandidateDirectory':True,'positiveActualCompileAnd20Groups':True,'wrongPathsRejectedWithoutCreatingTarget':7,'preFreezeSelfCheckNotIndependentReview':True})
assert all(json.loads((E/'input03-reproduction'/(name+'.json')).read_text())['exitCode']==0 for name in ['null-source','null-production','empty_ready-source','empty_ready-production'])
assert json.loads((E/'input03-reproduction/c01-original-entry.json').read_text())['exitCode']==1
batch=json.loads((E/'batch-validation.json').read_text());batch.update(hostReturnCaseCount=88,transitionCaseCount=33,originalQueryCases=2,reviewOutputPositiveActual=True,reviewOutputRejectedPaths=7,oldFrozenFilesUnchanged=2978);dump(E/'batch-validation.json',batch)
runner=json.loads((E/'review-runner-gate/summary.json').read_text());assert runner['positiveOriginalReturnedRuns']==42 and runner['negativePaths']==7 and runner['runnerSha256']==sha(B/'tools/review_all.py')
mapping=json.loads((B/'independent-regression-map.json').read_text())
for row in mapping['cases']:
 if row['id'] in ['S01','S03','S04','S06']:row['newEvidence']+=['evidence/suites-004/results.stdout','evidence/suites-004/transitions.stdout','evidence/suites-004/query-original.stdout']
 if row['id']=='F01':row['newEvidence']+=['evidence/tool-output-gate/summary.json','evidence/review-runner-gate/summary.json']
dump(B/'independent-regression-map.json',mapping)
completion=json.loads((B/'completion-matrix.json').read_text())
completion['rows']=[dict(x,id='B01_B04') if x['id']=='B01_B02' else x for x in completion['rows']];dump(B/'completion-matrix.json',completion)
print('Return fields/transition matrix and actual C01 gate bound; raw original B05/C01 failures retained')
