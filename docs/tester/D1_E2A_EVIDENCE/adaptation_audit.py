"""Independent static/archival review. No candidate imports or native probes."""
from pathlib import Path
import ast,hashlib,json
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2];BASE=ROOT/'docs/coder/d1e2a';OLD=ROOT/'docs/coder/d1e2'
def read(p):return json.loads(p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,v):(OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
freeze=read(BASE/'evidence/freeze-summary.json');p=read(BASE/'profiles/runtime-policy.json');cases=read(BASE/'profiles/cases.json');old=read(OLD/'profiles/cases.json')
assert p['state']=='APPROVED_TOOL_STRATEGY' and not p['executionAuthorized']
assert p['limits']['G']['threads']==16 and p['limits']['G']['deltaThreads']==12
assert p['limits']['R']['handles']==512 and p['minimumAvailablePhysicalBytes']==2147483648
fields=('task','nonquery','queriesNew','queriesReplay','inputBytes','inputCalls','validationBytes','newTargets','newRecords','outputBytes','mediaHandles','buffers','seconds','operations')
for a,b in zip(cases['cases'],old['cases']):assert a['id']==b['id'] and all(a[k]==b[k] for k in fields)
actual=read(BASE/freeze['actualRuntimeGateStopEvidence']);w=actual['witness'];runtime=w['runtimeObservation'];o=runtime['observation']
assert actual['exitCode']==1 and w['status']=='FAIL' and w['usage']['ib']==w['usage']['ic']==0
assert o['scope']=='APPROVED_TOOL_RUNTIME_OBSERVATION' and o['status']=='STOP_PENDING'
assert o['reasons']==['METRIC_THRESHOLD_EXCEEDED:R:handles'] and o['baselines']['R']['handles']==o['peaks']['R']['handles']==519
assert o['samples']==3 and runtime['reader']['cycles']==3
assert runtime['reader']['openedHandles']==runtime['reader']['closedHandles']==10 and runtime['reader']['maximumOwnedHandlesObserved']==1
assert not runtime['reader']['observerCreditHeld'] and not runtime['reader']['closeUnknown'] and not runtime['nativeQueryPending']
assert w['logClose']['remainingResources']==0 and w['callbackHub']['lifecycle']=='CLOSED'
assert all(x['code']==0 and x['exited'] for x in w['logClose']['exitedHelpers'].values())
save('actual-runtime-gate-review.json',dict(scope='Original archived OS observer failure, not rerun',source=freeze['actualRuntimeGateStopEvidence'],sha256=sha(BASE/freeze['actualRuntimeGateStopEvidence']),exitCode=actual['exitCode'],status=w['status'],usage=w['usage'],runtimeObservation=runtime,logClose=w['logClose'],conclusion='R519_GT512_REMAINS_BLOCKED; no source bytes; no runtime admission claimed'))
t=read(BASE/freeze['targetedEvidence']);assert t['assertions']==844 and sum(g['assertions'] for g in t['groups'])==844
ns=next(g for g in t['groups'] if g['scope']=='SELF_CREATED_NON_MEDIA_NAMESPACE_CHECKS')
assert ns['assertions']==32 and any('ACTUAL_HARDLINK_NOT_CREATED' in s for s in ns['limitations']) and any('OS_SYMLINK_CREATION_NOT_AVAILABLE' in s for s in ns['limitations'])
bridge=read(BASE/freeze['javaBridgeEvidence']);assert bridge['assertions']==87 and bridge['completedProcesses']==bridge['plannedProcesses']==len(bridge['cases'])==10
assert bridge['pending'] is None and bridge['noInFlight'] and all(c['processExitObserved'] for c in bridge['cases'])
assert sum(c['assertions'] for c in bridge['cases'])==87
for c in bridge['cases']:
 if c['case']=='missing-preview':assert c['exitCode']!=0 and c['previewStartupRejected'];continue
 r=c['receipt'];assert r['nativeReads']==r['nativeSeeks']==0 and r['nativeCloses']==1 and r['threadsJoined']
 if c['case']=='close-race':assert r['closeWaitedForQuery']
 if c['case']=='path-separation':assert r['unrelatedPathLength']==17 and r['openReceipt'].startswith('4096|')
save('namespace-and-java-evidence-review.json',dict(scope='Existing owned-file/probe evidence only, no rerun',namespace=ns,javaBridge=bridge,hardlinkCreationPassed=False,actualSymlinkCreationPassed=False,actualRenameOrReplacementProved=False))
selected=read(BASE/freeze['integrationEvidence'])['witness'];r=selected['runtimeObservation']
assert r['mockMetricsUsed'] and r['mode']=='SYNTHETIC_OBSERVER_MOCK' and r['observation']['scope']=='SYNTHETIC_POLICY_CHECK'
assert not r['observation']['runtimePolicyApproved'] and r['reader']['cycles']==0 and r['reader']['identityQueries']==3 and r['reader']['borrowedIdentityQueries']==2
run=BASE/'selfcheck'/selected['root'];raw=(run/'global.log').read_bytes();metric_rows=[line for line in raw.splitlines(keepends=True) if line.startswith(b'[') or line.startswith(b'{"runtimeMetricFormat"')]
metric_bytes=sum(len(s) for s in metric_rows);assert metric_bytes==560 and len(raw)==93462 and len(raw)-metric_bytes==92902
assert r['log']['eventBytes']==92828 and 92902-92828==74
assert selected['metadataRequested']==selected['metadataWritten']==6401375 and selected['metadataPeak']==634207
save('mock-driver-and-log-review.json',dict(scope='Existing mixed evidence: mock counters, actual authored-file IO and process identity',runtimeObservation=r,finalLogBytes=len(raw),finalEventBytes=len(raw)-metric_bytes,metricBytes=metric_bytes,metricRecordLengths=[len(s) for s in metric_rows],precloseEventBytes=92828,finalN32EventBytes=74,metadataRequested=selected['metadataRequested'],metadataWritten=selected['metadataWritten'],metadataPeak=selected['metadataPeak'],runtimeAdmissionPassed=False))
same=[]
for rel in ['src/authority.py','src/recovery.py','src/recovery_checks.py','src/Core.cs']:
 assert (BASE/rel).read_text(encoding='utf-8')==(OLD/rel).read_text(encoding='utf-8'),rel
 same.append(dict(path=rel,sha256=sha(BASE/rel),normalizedTextUnchangedFromE2=True,rawBytesUnchanged=(BASE/rel).read_bytes()==(OLD/rel).read_bytes()))
for rel in ['src/notifications.py','src/startup_checks.py']:
 expected=(OLD/rel).read_text(encoding='utf-8').replace('E2','E2A')
 if rel=='src/startup_checks.py':expected=expected.replace('"""E2A D01','"""E2 D01',1)
 assert (BASE/rel).read_text(encoding='utf-8')==expected,rel
 same.append(dict(path=rel,sha256=sha(BASE/rel),changes='E2 -> E2A literal label only'))
save('preserved-fix-audit.json',dict(scope='Static selected byte identity/explicit prefix normalization, not regression rerun',preserved=same))
source=(BASE/'src/gengine.py').read_text(encoding='utf-8');lines=source.splitlines();loc=next(i for i,s in enumerate(lines,1) if "self.e.root/'C.bin'" in s)
assert "if alias:" in lines[loc-2] and any(r['id']=='Q09-ALIAS' for r in cases['cases'])
save('alias-path-gap-review.json',dict(scope='Static adapter counterexample; no open or candidate execution',id='E2A-A01',severity='P2',path='docs/coder/d1e2a/src/gengine.py',line=loc,text=lines[loc-1],facts=['Q09-ALIAS calls grant(alias=True)','Ops.grant opens e.root/C.bin directly','Candidate input/output namespaces separate approved C path from output root','No C.bin fixture is created under a future CREATE_NEW output namespace','Therefore this branch cannot test the configured C alias: normally GUARD_OPEN_FAILED instead of intended INPUT_ALIAS'],suggestion='Resolve exact C input through Namespaces.input_path inside the existing grant native suboperation; validate same-object proof and original ownership/cleanup without new control/RPC/byte read',observedRuntimeFailure=False))
for rel in [freeze['actualRuntimeGateStopEvidence'],freeze['javaBridgeEvidence'],'evidence/selfcheck-1792168242897341600.json','evidence/targeted-1792168285935793100.json','evidence/entry-denials.json','evidence/adapter-feasibility.json']:
 source_file=BASE/rel;(OUT/source_file.name).write_bytes(source_file.read_bytes())
save('review-scope.json',dict(candidateFreezeSha256=sha(BASE/'evidence/freeze-summary.json'),configurationBudgetPreserved=True,syntheticAssertions=1003,javaBridgeAssertions=87,realRuntimeAdmission='BLOCKED_R_HANDLES_519_GT_512',fixtureBytes=freeze['syntheticFixtureBytes'],logsAndEvidenceBytesIncludingSeal=freeze['logsAndEvidenceBytesIncludingSeal'],ownFunctionalTests=0,mediaIO=False,newSampling=False,PF=False,build=False,adb=False,inFlight=[]))
print(json.dumps(dict(archiveReview='PASS',actualRHandles=519,actualLimit=512,runtimeAdmission=False,adapterGaps=1,ownFunctionalTests=0)))
