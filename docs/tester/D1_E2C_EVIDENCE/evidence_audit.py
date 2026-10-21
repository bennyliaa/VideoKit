"""Independent existing JSON/hash/source review; no candidate imports or probes."""
from pathlib import Path
import ast,hashlib,json
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2];BASE=ROOT/'docs/coder/d1e2c';OLD=ROOT/'docs/coder/d1e2b'
def read(p):return json.loads(p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,v):(OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
f=read(BASE/'evidence/freeze-summary.json');d=read(BASE/f['diagnosticEvidence']);plan=read(BASE/'evidence/g-lifecycle-reservation.json');outer=read(BASE/'evidence/g-lifecycle-outer-exit.json')
stages=['ZERO_CELLS','ONE_LIVE','ONE_DRAINED','EIGHT_LIVE','EIGHT_DRAINED','TOOL_HISTORY_RELEASED']
assert plan['maximumDiagnosticG']==1 and plan['maximumSamples']==6 and plan['stages']==stages and plan['createdBeforeHubAndCells']
assert d['identity']['pid']==plan['pid']==26368 and d['metricSamples']==6 and d['totalCellsCreated']==9
assert [s['stage'] for s in d['stages']]==stages and [s['metrics']['handles'] for s in d['stages']]==[160,164,164,196,196,196]
assert not d['forceGC'] and not d['baselineReset'] and d['runtime']['forceGCInvocations']==0 and d['runtime']['gcEnabled']
assert d['noInFlight'] and not d['remainingResources'] and d['remainingBuffers']==0 and d['bufferPeak']==8 and d['ledgerPeak']==3
assert d['nativeReader']['cycles']==6 and d['nativeReader']['openedHandles']==d['nativeReader']['closedHandles']==13 and not d['nativeReader']['observerCreditHeld']
assert d['closure']['lifecycle']=='CLOSED' and d['closure']['remainingCredits']==[] and not d['closure']['ownershipPending']
for worker in d['closure']['workers'].values():assert worker['joined'] and worker['exited'] and not worker['alive'] and worker['releaseProof']=='THREAD_JOIN_PROVEN'
for i,s in enumerate(d['stages']):
 assert s==read(BASE/f'evidence/g-lifecycle-stage-{i}.json') and s['identity']==d['identity'] and s['originalCreationValidated']
 assert read(BASE/f'evidence/g-lifecycle-entered-{i}.json')==dict(runId=d['runId'],stage=s['stage'],pid=26368,state='ORIGINAL_QUERY_ENTERED')
 assert s['observerFacts']['cycles']==i+1 and s['observerFacts']['openedHandles']==s['observerFacts']['closedHandles']
 assert s['releaseCount']==s['drainCount']==s['callbackCount']==[0,0,1,1,9,9][i]
last=d['stages'][-1]['references'];assert last['toolHistoryCells']==0 and last['externalFutures']==1 and last['weakCellsAlive']==last['weakFuturesAlive']==9 and last['weakClosuresAlive']==18
assert outer['sha256']==sha(BASE/f['diagnosticEvidence']) and outer['identity']==d['identity'] and outer['observedCommandExitCode']==0 and outer['originalInvocationComplete']
assert not outer['rerun'] and outer['newDiagnosticG']==0
for row in d['sourceEvidence']:assert sha(BASE/row['preservedPath'])==row['sha256']
backend=read(BASE/'evidence/synchronization-backend.json');assert backend['compiledCBackend']==backend['handleTypeCausality']=='UNKNOWN' and backend['extraMetricSamples']==0
assert sha(Path(backend['runtimeDll']['path']))==backend['runtimeDll']['sha256']
for row in backend['packagedHeaders']:assert sha(Path(row['path']))==row['sha256']
save('six-point-before-fix-review.json',dict(scope='Existing before-fix one-G OS observation only; not rerun',report=d,originalOuterExit=outer,backendStatic=backend,postFixOSObserved=False,doesNotProve='Exact C backend, kernel handle type, per-cell handle attribution or post-fix runtime admission'))
t=read(BASE/f['targetedEvidence']);assert t['assertions']==sum(g['assertions'] for g in t['groups'])==1125 and len(t['groups'])==12
g=next(g for g in t['groups'] if g['module']=='lifecycle_checks');assert g['assertions']==len(g['checks'])==170 and g['controlledThreadsJoined']
assert g['actualOSQueries']==g['actualFullRuns']==g['diagnosticGInstances']==0
for c in g['closures']:
 assert c['total']==c['activeLogicalRecords']+c['archived']<=64 and c['hubClosed'] and c['workersAlive']==c['buffers']==0 and not c['remainingWorkerCredits']
cap=next(c for c in g['closures'] if c['case']=='64-total-capacity');assert cap['total']==cap['archived']==64
unknown=next(c for c in g['closures'] if c['case']=='submit-UNKNOWN-retained');assert unknown['activeLogicalRecords']==1 and unknown['archived']==0 and unknown['blocked']=='NOTIFICATION_SUBMIT_UNKNOWN'
callback=next(c for c in g['closures'] if c['case']=='callback-error');assert callback['archived']==1 and callback['blocked']=='CALLBACK_FAILED'
save('lifecycle-logical-evidence-review.json',dict(scope='Existing producer170 logical assertions, not tester rerun; no OS decrease claim',group=g,originalUnknownPreserved=True,knownCallbackErrorPreserved=True))
changes=read(BASE/'evidence/lifecycle-change-map.json');assert changes['diagnosticRanBeforeFix'] and not changes['postFixOSComparisonRun'] and not changes['actualFullRun']
for c in changes['changes']:
 assert sha(BASE/c['path'])==c['afterSha256']
 if 'beforePath' in c:assert sha(BASE/c['beforePath'])==c['beforeSha256']
 else:assert sha(ROOT/c['beforeProjectPath'])==c['beforeSha256']
assert (BASE/'profiles/runtime-policy.json').read_bytes()==(OLD/'profiles/runtime-policy.json').read_bytes()
fields=('task','nonquery','queriesNew','queriesReplay','inputBytes','inputCalls','validationBytes','newTargets','newRecords','outputBytes','mediaHandles','buffers','seconds','operations')
current=read(BASE/'profiles/cases.json');previous=read(OLD/'profiles/cases.json');assert len(current['cases'])==len(previous['cases'])==61 and current['limits']==previous['limits']
for a,b in zip(current['cases'],previous['cases']):assert a['id']==b['id'] and all(a[k]==b[k] for k in fields)
assert not list((BASE/'evidence').glob('run-selfcheck-*.json')) and not list((BASE/'evidence').glob('mock-selfcheck-*.json'))
denials=read(BASE/'evidence/entry-denials.json');assert denials['newHelpers']==denials['newDiagnosticG']==denials['newOSMetricSamples']==0 and not denials['forbiddenConstructorsEntered']
save('change-and-scope-review.json',dict(scope='Static hash/config and existing entry evidence',changes=changes,runtimePolicyByteUnchanged=True,all61OperationsAndAllocationsUnchanged=True,denials=denials,actualFull='NOT_RUN',postFixOS='NOT_RUN',oldG369BlockerPreserved=True))
for rel in ['src/authority.py','src/notifications.py','src/gengine.py','src/phases.py']:
 tree=ast.parse((BASE/rel).read_text(encoding='utf-8'));assert tree
save('review-scope.json',dict(freezeSha256=sha(BASE/'evidence/freeze-summary.json'),sourceZipSha256=sha(BASE/'artifacts/E2C-source.zip'),targetedAssertions=1125,lifecycleAssertions=170,diagnosticG=1,OSPoints=6,postFixOSRun=False,actualFullRun=False,fixtureBytes=f['syntheticFixtureBytes'],logsAndEvidenceBytesIncludingSeal=f['logsAndEvidenceBytesIncludingSeal'],ownFunctionalTests=0,newSampling=False,mediaIO=False,build=False,adb=False,inFlight=[]))
for name in ['g-lifecycle-reservation.json','g-lifecycle-outer-exit.json','synchronization-backend.json','lifecycle-change-map.json','entry-denials.json']:
 p=BASE/'evidence'/name;(OUT/name).write_bytes(p.read_bytes())
for i in range(6):
 for prefix in ['g-lifecycle-stage-','g-lifecycle-entered-']:
  p=BASE/'evidence'/f'{prefix}{i}.json';(OUT/p.name).write_bytes(p.read_bytes())
print(json.dumps(dict(integrity='PASS',beforeFixOSPoints=6,logicalChecks=1125,lifecycle170=True,postFixOS=False,actualFull=False)))
