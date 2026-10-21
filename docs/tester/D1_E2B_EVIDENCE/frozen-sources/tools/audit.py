"""Read-only E2B reconciliation; never queries native state or starts a helper."""
import argparse,ast,hashlib,json,sys
from pathlib import Path
BASE=Path(__file__).resolve().parents[1];sys.path.insert(0,str(BASE/'src'))
from recovery import recover
from diagnostic_gate import validate_diagnostic,STAGES,METHODS
from profile_audit import verify_configuration,verify_upstreams,is_fixture

def read(path):return json.loads(path.read_text(encoding='utf-8-sig'))
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def relative(path):return path.relative_to(BASE).as_posix()
def local_evidence(value):
    path=Path(value)
    if not path.is_absolute():path=BASE/path
    assert path.resolve().is_relative_to((BASE/'evidence').resolve()),'EVIDENCE_OUTSIDE_CURRENT_PACKAGE'
    return path

def verify_diagnostic():
    summary_path=BASE/'evidence/diagnostic-summary.json';summary=read(summary_path)
    assert summary['schema']==1 and summary['scope']=='E2B_FIXED_DIAGNOSTIC_SUMMARY'
    path=local_evidence(summary['evidence']);report=read(path);validation=validate_diagnostic(report)
    assert summary['validation']==validation,'DIAGNOSTIC_SUMMARY_DISAGREES_WITH_RECOMPUTATION'
    reports=[p for p in (BASE/'evidence').glob('diagnostic-*.json') if p.name not in ('diagnostic-summary.json','diagnostic-reservation.json')]
    assert reports==[path],'ONLY_ONE_FIXED_DIAGNOSTIC_REPORT_ALLOWED'
    plan_path=BASE/'evidence/diagnostic-reservation.json';plan=read(plan_path)
    assert plan['scope']=='E2B_FIXED_DIAGNOSTIC_RESERVATION' and plan['createdBeforeFirstProcess'] is True and plan['realMediaAllowed'] is False
    assert plan['methods']==list(METHODS) and plan['stageOrder']==list(STAGES) and plan['maximumProcesses']==2 and plan['maximumMetricSamples']==8
    assert path.name=='diagnostic-'+plan['runId']+'.json'
    assert report['schema']==1 and report['scope']=='E2B_FIXED_R_STARTUP_DIAGNOSTIC' and report['evidenceKind']=='ACTUAL_OS_OBSERVER'
    assert report['configuration']['assemblySha256']==sha(BASE/'artifacts/E2B.dll')
    assert report['configuration']['methods']==list(METHODS) and report['configuration']['stageOrder']==list(STAGES)
    assert report['realExecutionAllowed'] is validation['realExecutionAllowed'] is False
    assert report['workerJoined'] is True and not report['remainingResources'],'DIAGNOSTIC_OWNERSHIP_PENDING'
    reader=report['nativeReader'];assert reader['openedHandles']==reader['closedHandles']
    assert reader['observerCreditHeld'] is reader['closeUnknown'] is False
    assert reader['maximumOwnedHandlesObserved']<=1 and reader['mediaCalls']==reader['rpcCalls']==reader['newWorkers']==0
    instances=report['instances'];assert 0<len(instances)<=2
    stages=[];identities=[]
    for index,instance in enumerate(instances):
        assert instance['method']==METHODS[index] and instance['outstandingUnknown'] is False
        proof=instance['exitProof'];assert proof['exited'] is True and type(proof['code']) is int
        assert instance['transport']['threadsJoined'] is True
        identity=instance.get('identity')
        if identity is not None:
            assert proof['pid']==identity['pid'] and proof['instance']==identity['owner'] and proof['creationTime100ns']==identity['creationTime100ns']
            assert int(plan['runId'])<=(identity['creationTime100ns']-116444736000000000)*100,'RESERVATION_MUST_PRECEDE_ORIGINAL_PROCESS'
            identities.append(identity)
        assert len(instance['stages'])<=4
        for position,record in enumerate(instance['stages']):
            assert record['stage']==STAGES[position] and identity is not None and record['identity']==identity
            metrics=record['metrics'];assert set(metrics)=={'threads','handles','workingSetBytes','privateBytes'} and all(type(value) is int and value>=0 for value in metrics.values())
            facts=record['observerFacts'];assert facts['openedHandles']==facts['closedHandles'] and not facts['observerCreditHeld'] and not facts['closeUnknown']
            assert record['sameCreationValidatedByReader'] is True
            stages.append(dict(method=instance['method'],stage=record['stage'],identity=identity,metrics=metrics))
    assert len({(value['pid'],value['creationTime100ns']) for value in identities})==len(identities) and len({value['owner'] for value in identities})==len(identities)
    costs=report['costs'];assert costs['processInstances']==len(instances)<=2 and costs['metricSamples']==len(stages)<=8
    assert costs['identityQueries']==len(identities) and costs['testMediaBytes']==0 and costs['original452Charged'] is False
    assert costs['diagnosticNativeWorkers']==1 and costs['transportReadersPerInstance']==2
    diagnostic_bytes=sum(p.stat().st_size for p in (BASE/'evidence').glob('diagnostic*.json'))
    assert summary['diagnosticArtifactBytesIncludingSummary']==diagnostic_bytes
    assert summary['stageCounts']=={value['method']:len(value['stages']) for value in instances}
    assert summary['originalInstancesExited'] is True
    assert costs['logBytes']==plan_path.stat().st_size+path.stat().st_size
    assert diagnostic_bytes<=524288 and costs['fixtureBytes']<=2097152 and costs['batchEvidenceBytes']<=4194304
    if validation['eligibleForOneActualSyntheticRegression']:
        assert len(stages)==8 and len(instances)==2 and not report['unknowns'] and costs['controlRequests']==4 and costs['stageAcks']==8
        assert all(value['exitProof']['code']==0 for value in instances)
    return dict(evidence=relative(path),summaryEvidence=relative(summary_path),reservationEvidence=relative(plan_path),validation=validation,
                eligible=validation['eligibleForOneActualSyntheticRegression'],processInstances=len(instances),observedStages=len(stages),stageMetrics=stages,
                firstExceedance=validation['firstExceedance'],diagnosticDeltasFromMinimal=validation['diagnosticDeltasFromMinimal'],
                diagnosticLogBytesIncludingSummary=diagnostic_bytes,observerClosed=True,noInFlight=True,actualOSMetrics=True)

def verify_alias(group):
    assert group['scope']=='E2B_A01_REAL_G_NATIVE_ALIAS_GRANT_SELF_OWNED_CHECKS' and group['status']=='PASS'
    assert group['assertions']==len(group['checks'])>0 and group['mediaBytesRead']==group['newHelpers']==0
    assert group['helpersStarted'] is group['mediaRead'] is group['realPFRun'] is group['real61Run'] is False
    expected={'normal':'INPUT_ALIAS','query-failure':'BLOCKED_VERSION_NOT_PROVEN','identity-mismatch':'SOURCE_VERSION_IDENTITY_CHANGED','close-unknown':'GUARD_CLOSE_UNKNOWN_NO_RETRY'}
    assert len(group['cases'])==4 and {row['case'] for row in group['cases']}==set(expected)
    for row in group['cases']:
        mode=row['case'];assert row['scope']=='ACTUAL_G_NATIVE_SELF_OWNED_Q09_ALIAS_FLOW' and row['reason']==expected[mode]
        assert row['controls']==1 and row['rpc']==row['mediaBytesRead']==row['fileByteDelegates']==row['remainingResources']==0
        assert len(row['opens'])==2 and row['opens'][0]['path']==row['opens'][1]['path']
        source=Path(row['opens'][0]['path']);assert source.is_relative_to(BASE/'selfcheck') and source.name=='C.bin' and source.parent.name=='inputs'
        assert all((value['access'],value['share'],value['creation'],value['flags'])==(0x80000000,1,3,0x80) for value in row['opens'])
        assert row['queryAttempts']==2 and row['actualQueryCalls']==(1 if mode=='query-failure' else 2) and row['injectedQueryFailures']==(1 if mode=='query-failure' else 0)
        record=row['stoppedObject'];assert record['object'] and record['ticket'] and record['owner']=='G' and record['attempts']==1
        assert row['metadataRequested']==row['metadataWritten'] and row['metadataTransactions']<=2
        assert len(row['closes'])==2 and all(value['actualReturned'] is True for value in row['closes'])
        if mode=='close-unknown':
            assert record['disposition']=='UNKNOWN' and record['nativeCloses']==0
            assert 'unknown-retains-original-ownership-and-credit' in group['checks'] and 'unknown-stops-active-flow' in group['checks']
            assert sum(value['injectedUnknown'] is True for value in row['closes'])==1
            assert len(row['controlledCleanup'])==1 and row['controlledCleanup'][0]['proof']=='TEST_RETAINED_ACTUAL_CLOSE_RETURN' and row['controlledCleanup'][0]['newCloseCalls']==0
        else:
            assert record['disposition']=='CLOSED_PROVEN' and record['nativeCloses']==1 and row['controlledCleanup']==[]
            assert all(value['reportedReturned'] is True and value['injectedUnknown'] is False for value in row['closes'])
    assert group['metadataRequested']==group['metadataWritten']==sum(row['metadataWritten'] for row in group['cases'])
    assert group['metadataTransactions']==sum(row['metadataTransactions'] for row in group['cases'])
    return dict(assertions=group['assertions'],activeFlow='Q09-ALIAS',cases=4,controlsPerCase=1,rpc=0,fileByteDelegates=0,
                exactInputC=True,separateInputsAndOutputs=True,unknownRetainedBeforeControlledRetirement=True,noInFlight=True)

def verify_hub(hub,success=False):
    assert hub['remainingCredits']==[] and hub['ownershipPending'] is False and not hub['startupInProgress']
    assert all(hub[key]==0 for key in ('cells','queued','active','workersAlive'))
    for worker in hub['workers'].values():
        assert worker['alive'] is False and worker['unknown'] is False
        if worker['creditReserved']:assert worker['creditReleased'] is True
        if worker['entered']:assert worker['exited'] is True and worker['joined'] is True and worker['releaseProof']=='THREAD_JOIN_PROVEN'
    if success:
        assert hub['lifecycle']=='CLOSED' and hub['blocked'] is None and hub['startupError'] is hub['cleanupError'] is None and set(hub['workers'])=={'notify','deadline'}
        for worker in hub['workers'].values():
            assert all(worker[key] is True for key in ('creditReserved','creditReleased','reserveReturned','threadCreated','startEntered','startReturned','entered','exited','joinEntered','joinReturned','joined'))
            assert all(worker[key] is None for key in ('startError','reserveError','joinError','runtimeError','observationError'))

def verify_runtime(witness,success):
    value=witness['runtimeObservation'];assert value['mode']=='ACTUAL_OS_OBSERVER' and value['mockMetricsUsed'] is False
    assert value['nativeQueryPending'] is False and value['policyState']=='APPROVED_TOOL_STRATEGY' and value['GAnchor']=='BEFORE_PF_N01_NEVER_RESET'
    assert value['realExecutionAuthorized'] is False and value['newThreads']==value['newRPC']==value['newJournalTransactions']==0
    reader=value['reader'];assert reader['openedHandles']==reader['closedHandles'] and not reader['observerCreditHeld'] and not reader['closeUnknown']
    assert reader['maximumOwnedHandlesObserved']<=1 and reader['mediaCalls']==reader['rpcCalls']==reader['newWorkers']==0
    observation=value['observation'];assert observation['scope']=='APPROVED_TOOL_RUNTIME_OBSERVATION' and observation['runtimePolicyApproved'] is True
    assert observation['realExecutionApproved'] is False and observation['peaksAreSampled'] is True and observation['gBaselineAnchor']=='ORIGINAL_PROCESS_BEFORE_PF_NOT_RESET'
    assert 0<=observation['samples']<=201
    if observation['status']=='STOP_PENDING':assert observation['stopAcceptance'] is True and observation['reasons']
    for role,baseline in observation['baselines'].items():
        identity=value['originalIdentities'][role];assert all(baseline[key]==identity[key] for key in ('pid','creationTime100ns','owner'))
    if success:
        assert all(value[key] is True for key in ('wired','started','finished'))
        assert observation['status']=='OBSERVED' and observation['stopAcceptance'] is False and not observation['reasons'] and observation['observationFinished'] is True
        assert 1<=observation['samples']<=201 and observation['maxObservedGapSeconds']<=2.5 and observation['sampleDurationSeconds']<=.1
        assert set(observation['baselines'])==set(observation['peaks'])==set(value['originalIdentities'])=={'G','J','R'}
        limits=read(BASE/'profiles/runtime-policy.json')['limits']
        for role,baseline in observation['baselines'].items():
            for metric,delta in dict(threads='deltaThreads',handles='deltaHandles',workingSetBytes='deltaWorkingSetBytes',privateBytes='deltaPrivateBytes').items():
                peak=observation['peaks'][role][metric];assert 0<=baseline[metric]<=peak<=limits[role][metric] and peak-baseline[metric]<=limits[role][delta]
        assert set(observation['activeRoles'])=={'G'} and reader['cycles']==observation['samples'] and reader['identityQueries']==3 and reader['borrowedIdentityQueries']==2
    log=value['log'];assert 0<=log['metricRows']<=observation['samples']<=201 and 0<=log['metricBytes']<=26752 and 0<=log['eventBytes']<=104320
    global_size=(BASE/'selfcheck'/witness['root']/'global.log').stat().st_size
    assert log['metricBytes']+log['eventBytes']<=global_size<=131072 and global_size-log['metricBytes']<=104320
    if success:assert log['metricRows']==observation['samples']
    return dict(mode='ACTUAL_OS_OBSERVER',mockMetricsUsed=False,status=observation['status'],stopAcceptance=observation['stopAcceptance'],reasons=observation['reasons'],sampleCycles=observation['samples'],
                GOriginalBaselinePreserved=True,baselines=observation['baselines'],sampledPeaks=observation['peaks'],peaksAreSampled=True,
                readerClosed=True,openedHandles=reader['openedHandles'],closedHandles=reader['closedHandles'],maximumObserverHandles=reader['maximumOwnedHandlesObserved'],
                freshMemory=value['freshMemory'],finalGlobalLogBytes=global_size,finalEventBytes=global_size-log['metricBytes'],metricBytes=log['metricBytes'])

def verify_full_witness(result,manifest):
    w=result['witness'];assert w['status'] in ('PASS','FAIL');success=w['status']=='PASS'
    assert (result['exitCode']==0) if success else (result['exitCode']!=0)
    assert w['mediaRead'] is w['realPFRun'] is w['real61Run'] is False
    if w['scope']=='E2B_FAILURE_RETURN_CHANNEL':
        assert not success and w['remainingResources']==0 and not w['resources'] and not w['nativePending']
        assert w['logOwnershipPending'] is False and (not w['logOpened'] or w['logCloseProven'] is True)
        verify_hub(w['hub'])
        for helper in w['helpers'].values():
            if helper['started'] is False:assert helper['status']=='NOT_ATTEMPTED'
            else:
                assert helper['started'] is True and helper['exitObserved'] is True
                proof=helper['exitProof'];assert proof['exited'] is True and proof['pid']==helper['pid'] and proof['instance']==helper['instance']
        return dict(status='FAIL',reportedAssertions=w.get('assertions'),passedAssertions=0,root=None,noInFlight=True,
                    failureReturnChannel=True,error=w['error'],startupError=w['startupError'],cleanupErrors=w['cleanupErrors'],runtimeObservation=None)
    assert w['scope']=='E2B_SYNTHETIC_INTEGRATION_ONLY'
    assert w['logClose']['closed'] is True and w['logClose']['remainingResources']==0 and set(w['logClose']['exitedHelpers'])=={'J','R'}
    assert all(proof['exited'] is True and type(proof['code']) is int for proof in w['logClose']['exitedHelpers'].values())
    verify_hub(w['callbackHub'],success)
    assert w['privateCells']['retained']==0 and w['privateCells']['peak']<=8 and w['ledgerPeaks']['os']<=24
    assert Path(w['root']).name==w['root'] and Path(w['precloseSummary']).name==w['precloseSummary']
    runtime=verify_runtime(w,success);root=BASE/'selfcheck'/w['root'];summary=root/w['precloseSummary'];assert sha(summary)==w['precloseSummarySha'];pre=read(summary)
    expected=['PF']+manifest['executionOrder'];assert w['rows']==len(pre['rows']) and [row['branch'] for row in pre['rows']]==expected[:w['rows']]
    assert all(0<=row['elapsedSeconds']<=row['seconds'] for row in pre['rows']) and type(w['assertions']) is int and w['assertions']>=0
    cold=recover(root,manifest);assert cold['writeCapability'] is False and cold['nativeCalls']==0
    if cold['usageExact']:assert cold['usage']==w['usage']
    if success:
        assert pre['error'] is None and [row['branch'] for row in pre['rows']]==['PF']+manifest['executionOrder'] and all(0<=row['elapsedSeconds']<=row['seconds'] for row in pre['rows'])
        assert all(proof['code']==0 for proof in w['logClose']['exitedHelpers'].values())
        assert all(w['usage'][key]==value for key,value in dict(n=351,qn=83,qr=18,ib=1573492,ic=59,v=128,records=32,targets=10,credit=655360).items())
        assert w['metadataRequested']==w['metadataWritten'] and w['metadataUnknownRequestedBytes']==0 and w['metadataCommitStatus']=='HEALTHY'
        assert len(cold['states'])==32 and cold['usage']==w['usage']
        assert cold['usageExact'] and cold['completeness']['status']=='COMPLETE' and len(cold['completeness']['admitted'])==32 and not cold['completeness']['missingAdmitted']
        assert len(cold['unresolved'])==1 and cold['unresolved'][0]['command']=='GC/n32'
        assert cold['states']['S17']['objects']['S17-v1-C']['originalCloseDisposition']=='UNKNOWN' and cold['states']['S17']['objects']['S17-v1-C']['nativeCloses']==1
        assert cold['states']['S17']['objects']['S17-v1-D']['attempts']==3 and cold['states']['S17']['objects']['S17-v1-D']['nativeCloses']==0
        assert all(state['fenced'] and not state['confirmed'] for state in cold['states'].values())
    else:assert pre['error'] is not None
    return dict(status=w['status'],reportedAssertions=w['assertions'],passedAssertions=w['assertions'] if success else 0,completedRows=w['rows'],root=w['root'],noInFlight=True,
                metadataCommitStatus=w['metadataCommitStatus'],metadataRequested=w['metadataRequested'],metadataWritten=w['metadataWritten'],metadataPeak=w['metadataPeak'],
                metadataUnknownRequestedBytes=w['metadataUnknownRequestedBytes'],runtimeObservation=runtime,usage=w['usage'],
                closure=dict(logClosed=True,remainingResources=0,originalHelpers=w['logClose']['exitedHelpers'],callbackHubLifecycle=w['callbackHub']['lifecycle'],
                             remainingWorkerCredits=w['callbackHub']['remainingCredits'],privateCells=w['privateCells']),
                recoveredRecords=len(cold['states']),recoveryUsageExact=cold['usageExact'],recoveryUsage=cold['usage'],
                recoveryCompleteness=cold['completeness'],recoveryUnresolved=cold['unresolved'],recoveryCoversAdmittedRecordsOnly=not success,originalBusinessUnknownsPreserved=True)

def verify_actual_full(diagnostic,manifest):
    runs=sorted((BASE/'evidence').glob('run-selfcheck-*.json'));assert len(runs)<=1,'ACTUAL_REGRESSION_MUST_NOT_BE_RETRIED'
    assert not list((BASE/'evidence').glob('pending-*.json')),'OUTER_CALLER_STILL_PENDING'
    reservation_path=BASE/'evidence/actual-regression-reservation.json';claim_path=BASE/'evidence/actual-regression-claim.json'
    not_run_path=BASE/'evidence/actual-regression-not-run.json'
    if not runs:
        report=read(not_run_path)
        assert report['scope']=='E2B_CONDITIONAL_ACTUAL_REGRESSION' and report['status']=='NOT_RUN' and isinstance(report['reason'],str) and report['reason']
        assert report['helpersStarted']==0 and report['noInFlight'] is True and report['realExecutionAllowed'] is False
        assert not reservation_path.exists() and not claim_path.exists(),'RESERVED_ACTUAL_RUN_HAS_NO_FINAL_OUTCOME'
        return dict(status='NOT_RUN',evidence=relative(not_run_path),reason=report['reason'],reportedAssertions=None,passedAssertions=0,
                    noInFlight=True,runtimeObservation=None,root=None)
    assert diagnostic['eligible'],'ACTUAL_RUN_WITHOUT_ELIGIBLE_DIAGNOSTIC'
    assert not not_run_path.exists(),'CONFLICTING_ACTUAL_OUTCOMES'
    path=runs[0];result=read(path);assert result['scope']=='OUTER_CALLER_RETURN_CHANNEL'
    assert result['noInFlight'] is True and result['mockMetricsUsed'] is False and result['ended']>=result['started']
    reservation=read(reservation_path);claim=read(claim_path);digest=diagnostic['validation']['diagnosticSha256']
    assert reservation['schema']==1 and reservation['scope']=='E2B_SINGLE_ACTUAL_SYNTHETIC_REGRESSION_RESERVATION'
    assert reservation['consumed'] is True and reservation['maximumActualRuns']==1 and reservation['persistCreateNewBeforeLaunch'] is True
    assert reservation['realExecutionAllowed'] is False and reservation['runId']==str(result['started'])
    assert reservation['diagnosticSha256']==digest and reservation['diagnosticEvidence']==diagnostic['evidence']
    assert reservation['diagnosticFileSha256']==sha(BASE/diagnostic['evidence'])
    assert reservation['dllSha256']==sha(BASE/'artifacts/E2B.dll') and reservation['policySha256']==sha(BASE/'profiles/runtime-policy.json')
    assert reservation['loader']=='ABSOLUTE_ASSEMBLY_LOAD_FROM' and reservation['profile']=='SYNTHETIC_SELF_OWNED_ONLY'
    assert claim['schema']==1 and claim['scope']=='E2B_SINGLE_ACTUAL_SYNTHETIC_CLAIM' and claim['runId']==reservation['runId']
    assert claim['diagnosticSha256']==digest and claim['launcherPid']==reservation['launcherPid'] and type(claim['controllerPid']) is int and claim['controllerPid']>0
    assert claim['profile']=='SYNTHETIC' and claim['mockMetricsUsed'] is claim['realExecutionAllowed'] is False
    assert result['witness']['actualRegressionAdmission']==claim,'ORIGINAL_CONTROLLER_CLAIM_MISSING_OR_CHANGED'
    full=verify_full_witness(result,manifest)
    runtime=result['witness'].get('runtimeObservation')
    if runtime is not None:
        identity=runtime['originalIdentities']['G'];assert identity['pid']==claim['controllerPid']
        assert reservation_path.stat().st_mtime_ns<=(identity['creationTime100ns']-116444736000000000)*100,'RESERVATION_AFTER_CONTROLLER_CREATION'
    full.update(evidence=relative(path),reservationEvidence=relative(reservation_path),claimEvidence=relative(claim_path),claim=claim)
    return full

def runtime_admission(full):
    runtime=full.get('runtimeObservation')
    if full['status']=='FAIL' and runtime is not None:
        limits=read(BASE/'profiles/runtime-policy.json')['limits']
        for role in ('G','J','R'):
            if all(reason in runtime['reasons'] for reason in ('METRIC_THRESHOLD_EXCEEDED:'+role+':handles','METRIC_DELTA_EXCEEDED:'+role+':handles')):
                peak=runtime['sampledPeaks'][role]['handles'];delta=peak-runtime['baselines'][role]['handles'];limit=limits[role]
                assert peak>limit['handles'] and delta>limit['deltaHandles']
                return 'BLOCKED_'+role+'_HANDLES_'+str(peak)+'_GT_'+str(limit['handles'])+'_AND_DELTA_'+str(delta)+'_GT_'+str(limit['deltaHandles'])
    return 'ACTUAL_OS_SYNTHETIC_'+full['status']

def audit():
    manifest=read(BASE/'manifest/branches.json');configuration=verify_configuration(manifest);upstream=verify_upstreams()
    targets=[(p,read(p)) for p in (BASE/'evidence').glob('targeted-*.json')]
    passing=[(p,value) for p,value in targets if value['status']=='PASS'];assert passing,'TARGETED_PASS_EVIDENCE_MISSING'
    target_path,target=max(passing,key=lambda item:item[0].name)
    groups={group['module']:group for group in target['groups']}
    expected={'e2b_checks','alias_checks','diagnostic_checks','namespace_checks','observer_checks','startup_checks','completion_checks','authority_checks','recovery_checks','metadata_checks','unitcheck'}
    assert len(target['groups'])==len(groups)==11 and set(groups)==expected and all(group['status']=='PASS' for group in groups.values())
    assert all(type(group['assertions']) is int and group['assertions']>0 for group in groups.values())
    assert target['assertions']==sum(group['assertions'] for group in groups.values())
    assert target['helpersStarted'] is target['mediaRead'] is target['realExecution'] is False
    alias=verify_alias(groups['alias_checks']);diagnostic=verify_diagnostic();full=verify_actual_full(diagnostic,manifest)
    for path in [*(BASE/'src').glob('*.py'),*(BASE/'tools').glob('*.py')]:ast.parse(path.read_text(encoding='utf-8'),filename=str(path))
    files=[p for p in (BASE/'selfcheck').rglob('*') if p.is_file()];fixture_bytes=sum(p.stat().st_size for p in files if is_fixture(p))
    logs=sum(p.stat().st_size for p in files if not is_fixture(p))+sum(p.stat().st_size for p in (BASE/'evidence').glob('*') if p.is_file())
    assert fixture_bytes<=2097152 and logs<=4194304
    denials=read(BASE/'evidence/entry-denials.json');assert denials['status']=='PASS' and len(denials['cases'])==2
    assert all(row['exitCode']==2 and row['response']['executionAllowed'] is False and row['response']['mediaBytesRead']==row['response']['helpersStarted']==0 and row['response']['outputRootCreated'] is False for row in denials['cases'])
    assert denials['scope']=='E2B_REAL_AND_REPEAT_SYNTHETIC_ENTRY_DENIALS'
    assert denials['secondActualReservationRejected']=='ACTUAL_SYNTHETIC_REGRESSION_ALREADY_RESERVED'
    assert denials['originalReservationAndClaimUnchanged'] is True and denials['newHelpersFromDenials']==0 and denials['realOutputRootCreated'] is False
    # Mock runs are retained as separate evidence. They can never supply a
    # missing actual run or contribute to this batch's actual pass count.
    mocks=sorted((BASE/'evidence').glob('mock-selfcheck-*.json'))
    for path in mocks:
        receipt=read(path);assert receipt['mockMetricsUsed'] is True and receipt['noInFlight'] is True
    total=target['assertions']+full['passedAssertions']
    return dict(status='PASS',scope='E2B_READ_ONLY_EVIDENCE_AUDIT',configurationVerified=True,configuration=configuration,
                targetedEvidence=relative(target_path),targetedGroups=list(groups),targetedAssertions=target['assertions'],aliasFixVerified=True,alias=alias,
                diagnosticVerified=True,diagnostic=diagnostic,diagnosticEvidence=diagnostic['evidence'],diagnosticEligible=diagnostic['eligible'],
                actualFullEvidence=full['evidence'],actualFullStatus=full['status'],actualFullReportedAssertions=full['reportedAssertions'],actualFullAssertions=full['passedAssertions'],actualFull=full,
                totalAssertions=total,driverSyntheticAssertions=total,mockEvidence=[relative(path) for path in mocks],mockAssertionsIncluded=False,
                runtimeAdmission=runtime_admission(full),noInFlightVerified=True,realExecutionEnabled=False,realMedia='NOT_RUN',realPF='NOT_RUN',
                syntheticBytes=fixture_bytes,logAndEvidenceBytesAtAudit=logs,startupFixVerified=True,startupLifecycleVerified=True,mediaRead=False,**upstream)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--audit',action='store_true');args=parser.parse_args()
    print(json.dumps(audit() if args.audit else dict(mode='INSPECT_ONLY'),separators=(',',':')))
