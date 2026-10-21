"""Read-only final evidence reconciliation; never launches a media/helper process."""
import argparse, ast, hashlib, json, sys
from pathlib import Path
BASE=Path(__file__).resolve().parents[1];sys.path.insert(0,str(BASE/'src'))
from recovery import recover
from profile_audit import verify_configuration,verify_upstreams,is_fixture

def verify_runtime(witness):
    runtime=json.loads((BASE/'profiles/runtime-policy.json').read_text(encoding='utf-8'))
    value=witness['runtimeObservation'];assert all(value[key] is True for key in ('wired','started','finished'))
    assert value['nativeQueryPending'] is False and value['policyState']=='APPROVED_TOOL_STRATEGY' and value['GAnchor']=='BEFORE_PF_N01_NEVER_RESET'
    assert value['mode']=='SYNTHETIC_OBSERVER_MOCK' and value['mockMetricsUsed'] is True
    assert value['newThreads']==value['newRPC']==value['newJournalTransactions']==0 and value['realExecutionAuthorized'] is False
    observation=value['observation'];assert observation['status']=='OBSERVED' and not observation['stopAcceptance'] and not observation['reasons']
    assert observation['scope']=='SYNTHETIC_POLICY_CHECK' and observation['runtimePolicyApproved'] is False
    assert observation['realExecutionApproved'] is False and observation['peaksAreSampled'] is True and observation['observationFinished'] is True
    assert observation['gBaselineAnchor']=='ORIGINAL_PROCESS_BEFORE_PF_NOT_RESET'
    assert 1<=observation['samples']<=201 and observation['maxObservedGapSeconds']<=2.5 and observation['sampleDurationSeconds']<=.1
    assert set(observation['baselines'])==set(observation['peaks'])==set(value['originalIdentities'])=={'G','J','R'}
    deltas=dict(threads='deltaThreads',handles='deltaHandles',workingSetBytes='deltaWorkingSetBytes',privateBytes='deltaPrivateBytes')
    for role,identity in value['originalIdentities'].items():
        baseline=observation['baselines'][role]
        assert all(baseline[key]==identity[key] for key in ('pid','creationTime100ns','owner'))
        for metric,delta in deltas.items():
            peak=observation['peaks'][role][metric]
            assert type(peak) in (int,float) and 0<=baseline[metric]<=peak<=runtime['limits'][role][metric]
            assert peak-baseline[metric]<=runtime['limits'][role][delta]
    for role in ('J','R'):
        proof=observation['retired'][role];identity=value['originalIdentities'][role]
        assert proof['exited'] is True and proof['code']==0 and proof['pid']==identity['pid'] and proof['instance']==identity['owner']
    assert set(observation['activeRoles'])=={'G'}
    reader=value['reader'];assert reader['openedHandles']==reader['closedHandles'] and reader['openedHandles']>0
    assert reader['maximumOwnedHandlesObserved']==1 and not reader['observerCreditHeld'] and not reader['closeUnknown']
    assert reader['mediaCalls']==reader['rpcCalls']==reader['newWorkers']==0 and reader['peaksAreSampled'] is True
    # Real process identities are captured, but this selected driver regression
    # deliberately supplies mock metric dictionaries after the actual OS gate
    # stopped. It is never evidence that the OS thresholds were met.
    assert reader['cycles']==0 and reader['identityQueries']==3 and reader['borrowedIdentityQueries']==2
    log=value['log'];assert 0<log['metricRows']<=201 and log['metricRows']==observation['samples']
    assert 0<log['metricBytes']<=26752 and 0<log['eventBytes']<=104320 and log['metricBytes']+log['eventBytes']<=131072
    global_size=(BASE/'selfcheck'/witness['root']/'global.log').stat().st_size
    assert log['metricBytes']+log['eventBytes']<=global_size<=131072 and global_size-log['metricBytes']<=104320
    return dict(mode='SYNTHETIC_OBSERVER_MOCK',actualRuntimeAdmissionPassed=False,mockMetricsUsed=True,GOriginalBaselinePreserved=True,
                originalRoles=sorted(value['originalIdentities']),sampleCycles=observation['samples'],readerClosed=True,maximumObserverHandles=1,
                metricRows=log['metricRows'],metricBytes=log['metricBytes'],eventBytes=log['eventBytes'],finalGlobalLogBytes=global_size,peaksAreSampled=True)

def verify_actual_gate_stop():
    path=BASE/'evidence/selfcheck-1792168123102649100.json'
    report=json.loads(path.read_text(encoding='utf-8'));w=report['witness']
    assert report['exitCode']!=0 and w['status']=='FAIL'
    value=w['runtimeObservation'];observation=value['observation']
    assert value.get('mockMetricsUsed',False) is False and value.get('mode')!='SYNTHETIC_OBSERVER_MOCK'
    assert value['policyState']=='APPROVED_TOOL_STRATEGY' and value['GAnchor']=='BEFORE_PF_N01_NEVER_RESET'
    assert observation['scope']=='APPROVED_TOOL_RUNTIME_OBSERVATION' and observation['runtimePolicyApproved'] is True
    assert observation['status']=='STOP_PENDING' and observation['stopAcceptance'] is True
    assert 'METRIC_THRESHOLD_EXCEEDED:R:handles' in observation['reasons']
    assert observation['samples']==3 and observation['baselines']['R']['handles']==observation['peaks']['R']['handles']==519
    runtime=json.loads((BASE/'profiles/runtime-policy.json').read_text(encoding='utf-8'));assert runtime['limits']['R']['handles']==512
    assert w['usage']['ib']==w['usage']['ic']==0
    assert w['logClose']['closed'] is True and w['logClose']['remainingResources']==0
    assert set(w['logClose']['exitedHelpers'])=={'J','R'}
    assert all(proof['exited'] is True and proof['code']==0 for proof in w['logClose']['exitedHelpers'].values())
    hub=w['callbackHub'];assert hub['lifecycle']=='CLOSED' and hub['remainingCredits']==[] and hub['ownershipPending'] is False
    assert all(hub[key]==0 for key in ('cells','queued','active','workersAlive'))
    assert hub['startupError'] is None and hub['cleanupError'] is None
    reader=value['reader'];assert reader['openedHandles']==reader['closedHandles'] and reader['cycles']==3
    assert reader['maximumOwnedHandlesObserved']==1 and not reader['observerCreditHeld'] and not reader['closeUnknown'] and value['nativeQueryPending'] is False
    summary=BASE/'selfcheck'/w['root']/w['precloseSummary'];assert hashlib.sha256(summary.read_bytes()).hexdigest()==w['precloseSummarySha']
    return dict(status='EXPECTED_STOP_VERIFIED',evidence=path.relative_to(BASE).as_posix(),originalRunStatus='FAIL',
                runtimeAdmission='BLOCKED_R_HANDLES_519_GT_512',measuredRHandles=519,approvedRHandleLimit=512,inputBytes=0,inputCalls=0,
                originalHelpersExitZero=True,remainingResources=0,countsTowardDriverAssertions=False)

def verify_bridge():
    reports=[(p,json.loads(p.read_text(encoding='utf-8'))) for p in (BASE/'evidence').glob('java-bridge-*.json')]
    passing=[(p,r) for p,r in reports if r.get('status')=='PASS'];assert passing,'JAVA_BRIDGE_EVIDENCE_MISSING'
    path,report=max(passing,key=lambda item:item[0].name)
    assert report['scope']=='E2A_SELF_OWNED_JAVA_BRIDGE_METADATA_CHECKS' and report['noInFlight'] is True and report['pending'] is None
    expected={'success','path-separation','query-failure','field-missing','field-type','symbol-missing','close-race','missing-native-access','missing-java-io-open','missing-preview'}
    assert report['plannedProcesses']==report['completedProcesses']==len(report['cases'])==len(expected)
    assert {case['case'] for case in report['cases']}==expected
    assert report['mediaBytesRead']==0 and report['formalPFRun'] is False and report['formal61Run'] is False
    total=0
    for case in report['cases']:
        assert case['status']=='PASS' and case['processExitObserved'] is True and case['pid']>0 and case['endedNs']>=case['startedNs']
        if case['previewStartupRejected']:
            assert case['case']=='missing-preview' and case['exitCode']!=0 and case['receipt'] is None and case['assertions']==1
        else:
            receipt=case['receipt'];assert case['exitCode']==0 and receipt['status']=='PASS' and receipt['pid']==case['pid']
            assert receipt['nativeCloses']==1 and receipt['nativeReads']==receipt['nativeSeeks']==0 and receipt['threadsJoined'] is True
            fields=receipt['openReceipt'].split('|');assert len(fields)==11
            if case['case'] in ('success','path-separation','close-race'):assert fields[-1]=='PROVEN' and fields[0]=='4096'
            else:assert fields[-1]=='BLOCKED_VERSION_NOT_PROVEN' and fields[:3]==['-1','-1','']
            assert case['assertions']==receipt['assertions'] and receipt['assertions']>0
        total+=case['assertions']
    assert report['assertions']==total and total>0
    return path,report
def audit():
    manifest=json.loads((BASE/'manifest/branches.json').read_text(encoding='utf-8'))
    configuration=verify_configuration(manifest)
    candidates=[(p,json.loads(p.read_text(encoding='utf-8'))) for p in (BASE/'evidence').glob('selfcheck-*.json')]
    passing=[(p,x) for p,x in candidates if x['exitCode']==0 and x.get('witness',{}).get('status')=='PASS'];assert passing
    path,result=max(passing,key=lambda item:item[1]['started']);w=result['witness'];root=BASE/'selfcheck'/w['root']
    summary=root/w['precloseSummary'];assert hashlib.sha256(summary.read_bytes()).hexdigest()==w['precloseSummarySha'];pre=json.loads(summary.read_bytes());assert pre['error'] is None
    expected=['PF']+manifest['executionOrder'];assert [x['branch'] for x in pre['rows']]==expected
    assert all(0<=x['elapsedSeconds']<=x['seconds'] for x in pre['rows'])
    assert w['usage']['n']==351 and w['usage']['qn']==83 and w['usage']['qr']==18 and w['usage']['records']==32 and w['usage']['targets']==10
    assert w['logClose']['closed'] and w['logClose']['remainingResources']==0
    assert all(p['exited'] and p['code']==0 for p in w['logClose']['exitedHelpers'].values())
    cold=recover(root,manifest);assert len(cold['states'])==32 and cold['usage']==w['usage']
    assert cold['writeCapability'] is False and cold['nativeCalls']==0
    assert cold['usageExact'] and cold['completeness']['status']=='COMPLETE' and len(cold['completeness']['admitted'])==32 and not cold['completeness']['missingAdmitted']
    assert w['metadataRequested']==w['metadataWritten'] and w['metadataUnknownRequestedBytes']==0 and w['metadataCommitStatus']=='HEALTHY'
    assert w['privateCells']['retained']==0 and w['privateCells']['peak']<=8
    assert all(w['callbackHub'][key]==0 for key in ('cells','queued','active','workersAlive')) and w['callbackHub']['blocked'] is None
    hub=w['callbackHub'];assert hub['lifecycle']=='CLOSED' and hub['remainingCredits']==[] and hub['ownershipPending'] is False
    assert hub['startupError'] is None and hub['cleanupError'] is None and hub['startupInProgress'] is False and set(hub['workers'])=={'notify','deadline'}
    for worker in hub['workers'].values():
        assert all(worker[key] is True for key in ('creditReserved','creditReleased','reserveReturned','threadCreated','startEntered','startReturned','entered','exited','joinEntered','joinReturned','joined'))
        assert worker['alive'] is False and worker['unknown'] is False and worker['releaseProof']=='THREAD_JOIN_PROVEN'
        assert all(worker[key] is None for key in ('startError','reserveError','joinError','runtimeError','observationError'))
    assert w['ledgerPeaks']['os']<=24
    assert len(cold['unresolved'])==1 and cold['unresolved'][0]['command']=='GC/n32'
    assert cold['states']['S17']['objects']['S17-v1-C']['originalCloseDisposition']=='UNKNOWN'
    assert cold['states']['S17']['objects']['S17-v1-D']['attempts']==3
    assert cold['states']['S17']['objects']['S17-v1-D']['nativeCloses']==0
    assert cold['states']['S17']['objects']['S17-v1-C']['nativeCloses']==1
    assert all(s['fenced'] and not s['confirmed'] for s in cold['states'].values())
    for p in [*(BASE/'src').glob('*.py'),*(BASE/'tools').glob('*.py')]:ast.parse(p.read_text(encoding='utf-8'),filename=str(p))
    files=[p for p in (BASE/'selfcheck').rglob('*') if p.is_file()];fixtures=[p for p in files if is_fixture(p)]
    synthetic=sum(p.stat().st_size for p in fixtures);logs=sum(p.stat().st_size for p in files if p not in fixtures)+sum(p.stat().st_size for p in (BASE/'evidence').glob('*') if p.is_file())
    assert synthetic<=2097152 and logs<=4194304
    upstream=verify_upstreams()
    targets=[(p,json.loads(p.read_text(encoding='utf-8'))) for p in (BASE/'evidence').glob('targeted-*.json')]
    target_path,target=max(((p,r) for p,r in targets if r['status']=='PASS'),key=lambda item:item[0].name)
    groups={group['module']:group for group in target['groups']}
    assert set(groups)=={'e2a_checks','namespace_checks','observer_checks','startup_checks','completion_checks','authority_checks','recovery_checks','metadata_checks','unitcheck'}
    assert all(group['status']=='PASS' for group in groups.values()) and groups['startup_checks']['assertions']>0 and groups['e2a_checks']['assertions']>0
    total=w['assertions']+target['assertions']
    runtime=verify_runtime(w);actual_gate=verify_actual_gate_stop();bridge_path,bridge=verify_bridge()
    denials=json.loads((BASE/'evidence/entry-denials.json').read_text(encoding='utf-8-sig'))
    assert denials['status']=='PASS' and len(denials['cases'])==2
    assert all(row['exitCode']==2 and row['response']['executionAllowed'] is False and row['response']['mediaBytesRead']==0 and row['response']['helpersStarted']==0 and row['response']['outputRootCreated'] is False for row in denials['cases'])
    return {'status':'PASS','scope':'READ_ONLY_EVIDENCE_AUDIT','integrationEvidence':path.relative_to(BASE).as_posix(),'targetedEvidence':target_path.relative_to(BASE).as_posix(),'javaBridgeEvidence':bridge_path.relative_to(BASE).as_posix(),
            'root':root.name,'syntheticAssertions':w['assertions'],'targetedAssertions':target['assertions'],'totalAssertions':total,'javaBridgeAssertions':bridge['assertions'],'javaBridgeProcesses':bridge['completedProcesses'],
            'scenarios':61,'phaseControls':48,'controls':452,'recoveredRecords':32,'recoveredBudgetMatches':True,'inventoryComplete':True,'uncertainLogCloseRequiresExternalWitness':True,'originalCloseFactsPreserved':True,
            'allRowsWithinDeadline':True,'syntheticBytes':synthetic,'logAndEvidenceBytesAtAudit':logs,**upstream,'callbackHubDrainedAndJoined':True,'startupLifecycleVerified':True,'startupFixVerified':True,
            'configurationVerified':configuration['configurationVerified'],'configuration':configuration,'runtimeObservationVerified':True,'runtimeObservation':runtime,
            'actualRuntimeGateStopVerified':True,'actualRuntimeGateStop':actual_gate,'runtimeAdmission':'BLOCKED_R_HANDLES_519_GT_512',
            'javaBridgeVerified':True,'targetedGroups':list(groups),'mediaRead':False}
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--audit',action='store_true');args=parser.parse_args()
    print(json.dumps(audit() if args.audit else {'mode':'INSPECT_ONLY'},separators=(',',':')))
