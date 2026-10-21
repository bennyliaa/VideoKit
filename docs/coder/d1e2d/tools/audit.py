"""Reconcile E2D's existing comparison records only; never import its probe/src."""
import argparse,hashlib,json,math
from pathlib import Path
from profile_audit import verify_configuration,verify_upstreams,is_fixture,E2C_FREEZE_SHA,E2C_SOURCE_SHA

BASE=Path(__file__).resolve().parents[1]
STAGES=('ZERO_CELLS','ONE_LIVE','ONE_DRAINED_COMPACTED','EIGHT_LIVE','EIGHT_DRAINED_COMPACTED','PROBE_AUDIT_COPY_RELEASED')
METRICS=('threads','handles','workingSetBytes','privateBytes')
HEALTHY='OBSERVED_POSTFIX_SIX_POINTS_WITHIN_LIMITS'
RUNTIME_ADMISSION='NO_ACTUAL_ADMISSION_E2D_SMALL_PROBE_ONLY_E2B_G369_DELTA209_FAIL_PRESERVED'

def read(path):return json.loads(path.read_text(encoding='utf-8-sig'))
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def relative(path):return path.relative_to(BASE).as_posix()
def number(value):return type(value) in (int,float) and math.isfinite(value) and value>=0
def count(value,maximum):return type(value) is int and 0<=value<=maximum

def verify_reader(facts,cycles,*,complete):
    assert facts['scope']=='READ_ONLY_WIN32_PROCESS_METADATA' and facts['cycles']==cycles and facts['borrowedIdentityQueries']==0
    assert count(facts['identityQueries'],1) and count(facts['openedHandles'],13) and facts['openedHandles']==facts['closedHandles']
    assert facts['maximumOwnedHandlesObserved'] in (0,1) and facts['observerCreditHeld'] is facts['closeUnknown'] is False
    assert facts['mediaCalls']==facts['rpcCalls']==facts['newWorkers']==0 and facts['peaksAreSampled'] is True
    if complete:
        assert facts['identityQueries']==1 and facts['openedHandles']==1+2*cycles and facts['maximumOwnedHandlesObserved']==1
    else:assert 2*cycles+facts['identityQueries']<=facts['openedHandles']<=min(13,2*cycles+facts['identityQueries']+2)

def verify_closed_hub(hub,*,complete):
    assert hub['lifecycle']=='CLOSED' and hub['closed'] is True and hub['remainingCredits']==[] and hub['ownershipPending'] is False
    assert hub['startupInProgress'] is False and all(hub[key]==0 for key in ('cells','queued','active','monitorInFlight','workersAlive'))
    assert set(hub['workers'])=={'notify','deadline'}
    for worker in hub['workers'].values():
        assert worker['alive'] is worker['unknown'] is False
        if worker['creditReserved']:
            assert worker['creditReleased'] is True
            if worker['releaseProof']=='THREAD_JOIN_PROVEN':
                assert all(worker[key] is True for key in ('entered','exited','joinEntered','joinReturned','joined'))
            else:
                assert worker['releaseProof']=='THREAD_NOT_STARTED_PROVEN' and worker['neverStartedProven'] is True
        if complete:
            assert all(worker[key] is True for key in ('creditReserved','creditReleased','reserveReturned','threadCreated','startEntered','startReturned','entered','exited','joinEntered','joinReturned','joined'))
            assert worker['releaseProof']=='THREAD_JOIN_PROVEN' and all(worker[key] is None for key in ('startError','reserveError','joinError','runtimeError','observationError'))
    if complete:assert hub['startupError'] is hub['cleanupError'] is hub['blocked'] is None

def verify_audits(production,expected_total,expected_active,expected_peak):
    assert production['total']==expected_total and production['active']==expected_active and production['peak']==expected_peak
    assert production['retained']==expected_active and production['archived']==expected_total-expected_active
    history=production['history'];assert len(history)==production['archived']<=64
    assert production['total']==production['active']+production['archived']<=64 and production['active']<=8
    assert {row['operation'] for row in history}=={'E2D-CELL-'+str(index) for index in range(1,len(history)+1)}
    for row in history:
        assert row['operation'].startswith('E2D-CELL-') and row['kind']=='read' and row['handle_key'] is None
        assert row['native_done'] is row['gated'] is row['released'] is row['notification_done'] is row['notifier_quiescent'] is row['archived'] is True
        assert row['retained'] is row['discarded'] is False and row['deliveries']==1 and row['callbacks_registered']==row['callbacks_finished']==1
        assert row['callback_errors']==[] and row['error_type'] is row['error_message'] is None
        assert set(row['binding'])=={'task','version','consumer','generation'} and all(type(value) is str for value in row['binding'].values())
    assert len({row['operation'] for row in history})==len(history)

def verify_binding_evidence(report,binding):
    path=BASE/'evidence/production-binding.json';saved=read(path)
    assert report['productionBindingEvidence']==relative(path) and saved['schema']==1 and saved['scope']=='E2D_EXACT_E2C_PRODUCTION_BINDING'
    assert saved['upstreamFreezeSha256']==E2C_FREEZE_SHA and saved['upstreamSourceZipSha256']==E2C_SOURCE_SHA
    assert saved['productionCodeChanged'] is False and saved['newCompilations']==saved['newTargetedRuns']==0
    expected=[{key:row[key] for key in ('path','bytes','sha256')} for row in binding['productionAndConfigurationFiles']]
    artifacts=[{key:row[key] for key in ('path','bytes','sha256')} for row in binding['compiledArtifacts']]
    assert sorted(saved['files'],key=lambda row:row['path'])==expected and sorted(saved['compiledArtifacts'],key=lambda row:row['path'])==artifacts
    return dict(evidence=relative(path),sha256=sha(path),productionAndConfigurationFiles=len(expected),compiledArtifacts=len(artifacts))

def verify_comparison(binding):
    plan_path=BASE/'evidence/g-comparison-reservation.json';plan=read(plan_path);run_id=plan['runId']
    assert plan['schema']==1 and plan['scope']=='E2D_SINGLE_G_RESERVATION' and type(run_id) is str and run_id.isdigit()
    assert plan['maximumG']==1 and plan['maximumMetricSamples']==6 and plan['deadlineSeconds']==60 and plan['stages']==list(STAGES)
    assert plan['createdBeforeHubAndCells'] is True and plan['realExecutionAllowed'] is plan['actualFullAllowed'] is plan['forceGCAllowed'] is False
    assert plan['upstreamFreezeSha256']==E2C_FREEZE_SHA and type(plan['pid']) is int and plan['pid']>0
    primary=[path for path in (BASE/'evidence').glob('g-comparison-*.json') if path.stem.removeprefix('g-comparison-').isdigit()]
    assert len(primary)==1 and primary[0].name=='g-comparison-'+run_id+'.json','ONE_ORIGINAL_POSTFIX_G_ONLY'
    path=primary[0];report=read(path);complete=report['status']==HEALTHY
    assert report['schema']==1 and report['scope']=='E2D_SINGLE_POSTFIX_G_COMPARISON' and report['runId']==run_id
    assert report['status'] in (HEALTHY,'FAIL','PENDING') and report['stageOrder']==list(STAGES)
    assert report['noInFlight'] is True and report['status']!='PENDING','PENDING_OWNERSHIP_CANNOT_BE_CALLED_FROZEN'
    assert report['realExecutionAllowed'] is report['actualFullRun'] is report['productionCodeChanged'] is report['forceGC'] is report['gcDisabled'] is report['baselineReset'] is False
    assert report['helpersStarted']==report['mediaBytesRead']==0 and report['diagnosticGInstances']==1
    assert report['exactCompiledSynchronizationBackend']==report['handleTypeCausality']=='UNKNOWN'
    assert report['fullEngineRuntimeAdmission']=='NOT_PROVEN_OLD_G369_AND_R519_FAILURES_PRESERVED' and report['externalObjectReclamationRequired'] is False
    assert not report['remainingResources'] and report['remainingBuffers']==0 and count(report['bufferPeak'],8) and count(report['ledgerPeak'],3)
    assert number(report['elapsedSeconds']) and type(report['errors']) is type(report['cleanupErrors']) is list
    if complete:assert report['errors']==report['cleanupErrors']==[] and report['elapsedSeconds']<=60
    else:assert report['errors'] or report['cleanupErrors'] or report['elapsedSeconds']>60
    bound=verify_binding_evidence(report,binding)
    probe_path=BASE/'tools/compare-g.py'
    assert report['probeSourceSha256']==sha(probe_path),'ORIGINAL_PROBE_SOURCE_HASH_MISMATCH'
    assert report['productionMethodBindings']=={name:'gengine.Engine.'+name for name in ('private_cell','compact_cells','cell_facts')}
    records=report['stages'];assert type(records) is list and 0<=len(records)<=6
    if complete:assert len(records)==6
    runtime=report.get('runtime',{});identity=report.get('identity')
    if identity is not None:
        assert identity['pid']==plan['pid'] and type(identity['creationTime100ns']) is int and identity['creationTime100ns']>0 and identity['owner']=='E2D-G-'+run_id
        assert runtime['implementation']=='CPython' and runtime['versionInfo'][:3]==[3,12,14] and runtime['pointerBits']==64 and runtime['compiler']
        assert runtime['runtimeDllSha256']=='2b6fffde96cf24a57fca642aaefd5788816ab5ef8624ea63b722cbceb94d49b1'
        assert runtime['gcEnabled'] is True and runtime['gcThresholds']==[700,10,10] and runtime['forceGCInvocations']==0
    else:assert not records and not complete
    expected_active=(0,1,0,8,0,0);totals=(0,1,1,9,9,9);peaks=(0,1,1,8,8,8);copies=(0,0,1,1,9,0);finished=(0,0,1,1,9,9)
    expected_stage_files={'g-comparison-stage-'+str(index)+'.json' for index in range(len(records))}
    assert {item.name for item in (BASE/'evidence').glob('g-comparison-stage-*.json')}==expected_stage_files
    entered=list((BASE/'evidence').glob('g-comparison-entered-*.json'))
    # A failed native call may leave its one entered marker without a returned
    # sample. It must never become a fabricated zero or a retry.
    assert len(records)<=len(entered)<=min(6,len(records)+int(not complete))
    assert {item.name for item in entered}=={'g-comparison-entered-'+str(index)+'.json' for index in range(len(entered))}
    for index in range(len(entered)):
        assert read(BASE/'evidence'/('g-comparison-entered-'+str(index)+'.json'))==dict(runId=run_id,stage=STAGES[index],identity=identity,state='ORIGINAL_QUERY_ENTERED')
    policy=read(BASE/'profiles/runtime-policy.json')['limits']['G'];delta_keys=dict(threads='deltaThreads',handles='deltaHandles',workingSetBytes='deltaWorkingSetBytes',privateBytes='deltaPrivateBytes')
    baseline=records[0]['metrics'] if records else None;first=None;observations=[];previous_elapsed=0
    for index,row in enumerate(records):
        assert row==read(BASE/'evidence'/('g-comparison-stage-'+str(index)+'.json')) and row['stage']==STAGES[index] and row['identity']==identity
        assert number(row['elapsedSeconds']) and previous_elapsed<=row['elapsedSeconds']<=report['elapsedSeconds'];previous_elapsed=row['elapsedSeconds']
        assert number(row['sampleDurationSeconds']) and row['sampleDeadlineSeconds']==.1 and row['sampleDeadlineMet']==(row['sampleDurationSeconds']<=.1)
        metrics=row['metrics'];assert set(metrics)==set(METRICS) and all(type(value) is int and value>=0 for value in metrics.values())
        delta={key:metrics[key]-baseline[key] for key in METRICS};assert row['deltaFromOriginalZero']==delta
        reasons=[key+':ABSOLUTE' for key in METRICS if metrics[key]>policy[key]]+[key+':DELTA' for key in METRICS if delta[key]>policy[delta_keys[key]]]
        assert row['limitExceedances']==reasons
        if reasons and first is None:first=dict(stage=row['stage'],reasons=reasons,metrics=metrics,deltaFromOriginalZero=delta)
        if reasons or not row['sampleDeadlineMet']:assert not complete and index==len(records)-1,'NO_EXTRA_SAMPLE_AFTER_STOP'
        verify_reader(row['observerFacts'],index+1,complete=True)
        hub=row['hub'];assert hub['lifecycle']=='RUNNING' and hub['workersAlive']==2 and hub['cells']==expected_active[index] and hub['peakCells']<=8 and hub['monitorInFlight']==0
        refs=row['referencesBeforeOSQuery'];verify_audits(refs['production'],totals[index],expected_active[index],peaks[index])
        assert refs['probeAuditCopyCount']==copies[index] and refs['authorityRegistered']==expected_active[index]
        assert refs['externalFutures']==(0 if index==0 else 1) and refs['externalFirstFutureDone']==(None if index==0 else index>=2)
        assert refs['externalFirstFutureCellDetached']==(None if index==0 else index>=2)
        assert refs['externalFirstOriginalResultStable']==(True if index>=2 else None)
        assert expected_active[index]<=refs['weakCellsAlive']<=totals[index] and refs['externalFutures']<=refs['weakFuturesAlive']<=totals[index]
        assert count(refs['weakClosuresAlive'],2*totals[index])
        for key in ('futureCellBackrefs','releaseClosuresRetained','drainClosuresRetained'):assert count(refs[key],refs['weakCellsAlive'])
        assert row['callbacksReturned']==row['consumedOriginalFutures']==finished[index]
        observations.append(dict(stage=row['stage'],metrics=metrics,deltaFromOriginalZero=delta,references=refs,sampleDeadlineMet=row['sampleDeadlineMet']))
    costs=report['costs'];assert costs['original452Charged'] is False and costs['metricSamples']==len(records) and costs['HubWorkers']==2
    assert costs['fixtureBytes']==costs['newRPC']==costs['newDriverControls']==0 and count(costs['identityQueries'],1)
    for key in ('privateCellCreations','sourceAdmissions','nativeLogicCompletions','gates','futureConsumptions','callbacksReturned'):assert count(costs[key],9)
    assert count(costs['normalCompactionCalls'],2) and count(costs['cleanupCompactionCalls'],1)
    for key in ('cleanupNativeLogicCompletions','cleanupGates','cleanupFutureConsumptions'):assert count(costs[key],9)
    proofs=report['consumptionProofs'];assert len(proofs)<=costs['privateCellCreations'] and len({row['operation'] for row in proofs})==len(proofs)
    for row in proofs:
        assert row['operation'].startswith('E2D-CELL-') and all(row[key] is True for key in ('callerConsumedOriginalFuture','sourceDone','nativeReturned','gateOpened','callbackReturned','perCellHubQuiescent'))
    if report.get('closure') is not None:verify_closed_hub(report['closure'],complete=complete)
    else:assert not records and not complete and costs['privateCellCreations']==0
    if report['nativeReader'] is not None:verify_reader(report['nativeReader'],len(records),complete=complete)
    else:assert not records and not complete and costs['identityQueries']==0
    if complete:
        assert all(costs[key]==9 for key in ('privateCellCreations','sourceAdmissions','nativeLogicCompletions','gates','futureConsumptions','callbacksReturned'))
        assert costs['identityQueries']==1 and costs['normalCompactionCalls']==2 and costs['cleanupCompactionCalls']==0 and len(proofs)==9
        assert {row['operation'] for row in proofs}=={'E2D-CELL-'+str(index) for index in range(1,10)}
        assert all(costs[key]==0 for key in ('cleanupNativeLogicCompletions','cleanupGates','cleanupFutureConsumptions'))
        assert report['nativeReader']==records[-1]['observerFacts'] and report['externalFutureHeldThroughClosure'] is report['externalFirstOriginalResultStableAfterClosure'] is True
        verify_audits(report['finalProductionFacts'],9,0,8)
        assert report['finalProductionFacts']['history']==records[-1]['referencesBeforeOSQuery']['production']['history'] and first is None
        for row in records:
            for role,worker in row['hub']['workers'].items():
                assert worker['threadId']==report['closure']['workers'][role]['threadId'] and worker['ident']==report['closure']['workers'][role]['ident']
    outer_path=BASE/'evidence/g-comparison-outer-exit.json';outer=read(outer_path)
    assert outer['schema']==1 and outer['scope']=='E2D_ORIGINAL_G_CALLER_EXIT_OBSERVATION' and outer['evidence']==relative(path) and outer['sha256']==sha(path)
    assert outer['runId']==run_id and outer['identity']==identity and outer['observedCommandExitCode']==(0 if complete else 2) and outer['originalInvocationComplete'] is True
    assert outer['rerun'] is outer['realExecutionAllowed'] is False and outer['newDiagnosticG']==0
    prefix_bytes=sum(item.stat().st_size for item in (BASE/'evidence').glob('g-comparison*.json'))
    snapshot=prefix_bytes-outer_path.stat().st_size
    assert report['diagnosticArtifactBytesAtReport']==snapshot,'ORIGINAL_REPORT_SNAPSHOT_MUST_NOT_BE_REWRITTEN'
    diagnostic_bytes=prefix_bytes+(BASE/'evidence/production-binding.json').stat().st_size
    assert diagnostic_bytes<=524288
    old=read(BASE/'upstream-e2c/freeze-summary.json')['lifecycle']
    return dict(evidence=relative(path),outerExitEvidence=relative(outer_path),reservationEvidence=relative(plan_path),status=report['status'],completeSixPointObservation=complete,
                identity=identity,runtime=runtime,metricSamples=len(records),diagnosticGInstances=1,observations=observations,firstApprovedLimitExceedance=first,
                reader=report['nativeReader'],closure=report.get('closure'),costs=costs,consumptionProofs=proofs,finalProductionFacts=report.get('finalProductionFacts'),
                errors=report['errors'],cleanupErrors=report['cleanupErrors'],elapsedSeconds=report['elapsedSeconds'],decisionAndCleanupWithin60Seconds=report['elapsedSeconds']<=60,
                productionBindingEvidence=bound,probeSourceSha256=report['probeSourceSha256'],productionMethodBindings=report['productionMethodBindings'],originalReportSnapshotBytes=snapshot,comparisonPrefixBytesIncludingOuterExit=prefix_bytes,
                productionBindingBytes=(BASE/'evidence/production-binding.json').stat().st_size,diagnosticLogBytesIncludingOuterExit=diagnostic_bytes,
                diagnosticByteScope='ALL_G_COMPARISON_JSON_INCLUDING_ORIGINAL_OUTER_EXIT_PLUS_PRODUCTION_BINDING_JSON',originalBaselineRetained=True,
                externalFutureRetained=report.get('externalFutureHeldThroughClosure',False),externalOriginalResultStableAfterClosure=report.get('externalFirstOriginalResultStableAfterClosure',False),
                postFixOSComparisonRun=True,noInFlight=True,eligibleForActualRegression=False,fullEngineRuntimeAdmission='NOT_PROVEN',handleTypeCausality='UNKNOWN',
                historicalE2CObservation=dict(identity=old['identity'],observations=old['observations'],differentOriginalProcess=True,mayNotSubstituteBaselineOrInferHandleTypeCausality=True))

def audit():
    configuration=verify_configuration(read(BASE/'manifest/branches.json'));upstream=verify_upstreams()
    for pattern in ('targeted*.json','build*.json','entry-denials*.json','run-selfcheck*.json','mock-selfcheck*.json','diagnostic*.json','actual-regression*.json','g-lifecycle*.json'):
        assert not list((BASE/'evidence').glob(pattern)),'E2D_FORBIDS_NEW_TARGETED_BUILD_FULL_OR_OTHER_DIAGNOSTIC:'+pattern
    checks=[path for path in (BASE/'selfcheck').rglob('*') if path.is_file()];assert not checks,'E2D_PROBE_CREATES_NO_FIXTURE_OR_TARGETED_CHECK_OUTPUT'
    comparison=verify_comparison(configuration['productionBinding'])
    fixtures=sum(path.stat().st_size for path in checks if is_fixture(path));logs=sum(path.stat().st_size for path in checks if not is_fixture(path))+sum(path.stat().st_size for path in (BASE/'evidence').glob('*') if path.is_file())
    assert fixtures<=2097152 and logs<=4194304
    return dict(status='PASS',scope='E2D_READ_ONLY_COMPARISON_EVIDENCE_AUDIT',configurationVerified=True,configuration=configuration,productionBindingVerified=True,
                productionBinding=configuration['productionBinding'],comparisonVerified=True,comparison=comparison,comparisonStatus=comparison['status'],
                comparisonEvidence=comparison['evidence'],comparisonOuterExitEvidence=comparison['outerExitEvidence'],diagnosticGInstances=1,metricSamples=comparison['metricSamples'],
                targetedAssertions=0,totalAssertions=0,driverSyntheticAssertions=0,targetedRuns=0,compileInvocations=0,repairCompilations=0,actualFullRuns=0,
                actualFullStatus='NOT_RUN',actualFullAssertions=0,actualFullReportedAssertions=None,actualFullReason='E2D_AUTHORIZES_ONLY_ONE_POSTFIX_G_COMPARISON_NO_ACTUAL_FULL',
                runtimeAdmission=RUNTIME_ADMISSION,postFixOSComparisonRun=True,handleTypeCausality='UNKNOWN',noInFlightVerified=True,
                realExecutionEnabled=False,realMedia='NOT_RUN',realPF='NOT_RUN',syntheticBytes=fixtures,logAndEvidenceBytesAtAudit=logs,mockAssertionsIncluded=False,mediaRead=False,**upstream)
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--audit',action='store_true');options=parser.parse_args()
    print(json.dumps(audit() if options.audit else dict(mode='INSPECT_ONLY',diagnosticRun=False),separators=(',',':')))
