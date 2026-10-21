"""Read-only E2C lifecycle/package reconciliation; no diagnostic or native calls."""
import argparse,ast,hashlib,json
from pathlib import Path
from profile_audit import verify_configuration,verify_upstreams,is_fixture
BASE=Path(__file__).resolve().parents[1]
STAGES=('ZERO_CELLS','ONE_LIVE','ONE_DRAINED','EIGHT_LIVE','EIGHT_DRAINED','TOOL_HISTORY_RELEASED')
METRICS=('threads','handles','workingSetBytes','privateBytes')
RUNTIME_ADMISSION='BLOCKED_G_HANDLES_369_GT_256_AND_DELTA_209_GT_64_FROM_E2B_NO_NEW_ACTUAL_ADMISSION'
def read(path):return json.loads(path.read_text(encoding='utf-8-sig'))
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def relative(path):return path.relative_to(BASE).as_posix()
def owned(value,parent):
    path=Path(value)
    if not path.is_absolute():path=BASE/path
    assert path.resolve().is_relative_to(parent.resolve()),'EVIDENCE_PATH_OUTSIDE_DECLARED_SCOPE'
    return path

def verify_hub(hub):
    assert hub['lifecycle']=='CLOSED' and hub['closed'] is True and hub['remainingCredits']==[] and hub['ownershipPending'] is False
    assert hub['startupError'] is hub['cleanupError'] is None and hub['startupInProgress'] is False and hub['blocked'] is None
    assert all(hub[key]==0 for key in ('cells','queued','active','workersAlive')) and set(hub['workers'])=={'notify','deadline'}
    for worker in hub['workers'].values():
        assert all(worker[key] is True for key in ('creditReserved','creditReleased','reserveReturned','threadCreated','startEntered','startReturned','entered','exited','joinEntered','joinReturned','joined'))
        assert worker['alive'] is worker['unknown'] is False and worker['releaseProof']=='THREAD_JOIN_PROVEN'
        assert all(worker[key] is None for key in ('startError','reserveError','joinError','runtimeError','observationError'))

def verify_reader(facts,cycle):
    assert facts['scope']=='READ_ONLY_WIN32_PROCESS_METADATA' and facts['cycles']==cycle and facts['identityQueries']==1 and facts['borrowedIdentityQueries']==0
    assert facts['openedHandles']==facts['closedHandles'] and facts['maximumOwnedHandlesObserved']==1
    assert facts['observerCreditHeld'] is facts['closeUnknown'] is False and facts['mediaCalls']==facts['rpcCalls']==facts['newWorkers']==0
    assert facts['peaksAreSampled'] is True

def verify_lifecycle():
    plan_path=BASE/'evidence/g-lifecycle-reservation.json';plan=read(plan_path);run_id=plan['runId']
    assert plan['schema']==1 and plan['scope']=='E2C_SINGLE_G_LIFECYCLE_RESERVATION'
    assert plan['maximumDiagnosticG']==1 and plan['maximumSamples']==6 and plan['deadlineSeconds']==60 and plan['stages']==list(STAGES)
    assert plan['createdBeforeHubAndCells'] is True and plan['realExecutionAllowed'] is plan['helpersAllowed'] is plan['actualFullAllowed'] is plan['forceGCAllowed'] is False
    primary=[path for path in (BASE/'evidence').glob('g-lifecycle-*.json') if path.stem.removeprefix('g-lifecycle-').isdigit()]
    assert len(primary)==1 and primary[0].name=='g-lifecycle-'+run_id+'.json','ONE_ORIGINAL_G_DIAGNOSTIC_ONLY'
    path=primary[0];report=read(path);identity=report['identity']
    assert report['schema']==1 and report['scope']=='E2C_SINGLE_G_LIFECYCLE_DIAGNOSTIC' and report['runId']==run_id and report['status']=='OBSERVED_FIXED_SIX_POINTS'
    assert identity['pid']==plan['pid'] and type(identity['creationTime100ns']) is int and identity['creationTime100ns']>0 and identity['owner']=='E2C-G-'+run_id
    assert report['actualOSMetrics'] is True and report['realExecutionAllowed'] is report['actualFullRun'] is report['forceGC'] is report['baselineReset'] is False
    assert report['helpersStarted']==report['mediaBytesRead']==0 and report['unknowns']==report['cleanupErrors']==[]
    assert report['diagnosticGInstances']==1 and report['metricSamples']==6 and report['stageOrder']==list(STAGES) and len(report['stages'])==6
    assert report['noInFlight'] is True and not report['remainingResources'] and report['remainingBuffers']==0 and report['bufferPeak']<=8 and report['ledgerPeak']<=24
    assert 0<=report['elapsedSeconds']<=60 and report['totalCellsCreated']==9
    verify_hub(report['closure']);verify_reader(report['nativeReader'],6)
    assert report['nativeReader']==report['stages'][-1]['observerFacts']
    expected_operations={'G-CELL-'+str(index) for index in range(1,10)}
    for key in ('resourceReleases','sourceDrains','callbacksReturned'):assert len(report[key])==9 and set(report[key])==expected_operations
    assert report['externalFutureAfterToolHistoryRelease']=='RESULT_STABLE_EXTERNAL_OWNERSHIP_RETAINED'
    assert report['allFinalReferencesReclaimed']=='NOT_CLAIMED_NO_FORCED_GC_EXTERNAL_VALUES_RESPECTED'
    assert report['realRuntimeAdmission']=='BLOCKED_G_HANDLES_369_GT_256_AND_DELTA_209_GT_64_E2B_HISTORY_PRESERVED'
    limits=read(BASE/'profiles/runtime-policy.json')['limits']['G'];deltas=dict(threads='deltaThreads',handles='deltaHandles',workingSetBytes='deltaWorkingSetBytes',privateBytes='deltaPrivateBytes')
    baseline=report['stages'][0]['metrics'];active=(0,1,0,8,0,0);history=(0,1,1,9,9,0);completed=(0,0,1,1,9,9)
    snapshots=[];first=None;previous_elapsed=0;previous_opened=0
    expected_stage_files={'g-lifecycle-stage-'+str(index)+'.json' for index in range(6)}
    expected_entered={'g-lifecycle-entered-'+str(index)+'.json' for index in range(6)}
    assert {p.name for p in (BASE/'evidence').glob('g-lifecycle-stage-*.json')}==expected_stage_files
    assert {p.name for p in (BASE/'evidence').glob('g-lifecycle-entered-*.json')}==expected_entered
    for index,record in enumerate(report['stages']):
        assert record['stage']==STAGES[index] and record['identity']==identity and record['originalCreationValidated'] is True
        assert read(BASE/'evidence'/('g-lifecycle-stage-'+str(index)+'.json'))==record
        entered=read(BASE/'evidence'/('g-lifecycle-entered-'+str(index)+'.json'))
        assert entered==dict(runId=run_id,stage=STAGES[index],pid=identity['pid'],state='ORIGINAL_QUERY_ENTERED')
        assert previous_elapsed<=record['elapsedSeconds']<=report['elapsedSeconds'] and 0<=record['sampleDurationSeconds']<=.1
        assert record['sampleDeadlineSeconds']==.1 and record['sampleDeadlineMet'] is True;previous_elapsed=record['elapsedSeconds']
        values=record['metrics'];assert set(values)==set(METRICS) and all(type(value) is int and value>=0 for value in values.values())
        delta={key:values[key]-baseline[key] for key in METRICS};assert record['deltaFromOriginalZero']==delta
        excess=[key+':ABSOLUTE' for key in METRICS if values[key]>limits[key]]+[key+':DELTA' for key in METRICS if delta[key]>limits[deltas[key]]]
        assert record['approvedLimitExceedances']==excess
        if first is None and excess:first=dict(stage=record['stage'],reasons=excess,metrics=values,deltaFromOriginalZero=delta)
        facts=record['observerFacts'];verify_reader(facts,index+1);assert facts['openedHandles']>previous_opened;previous_opened=facts['openedHandles']
        hub=record['hub'];assert hub['lifecycle']=='RUNNING' and hub['workersAlive']==2 and hub['cells']==active[index] and hub['peakCells']<=8
        for role,worker in hub['workers'].items():
            assert worker['threadId']==report['closure']['workers'][role]['threadId'] and worker['ident']==report['closure']['workers'][role]['ident']
        refs=record['references'];assert refs['toolHistoryCells']==history[index] and refs['authorityRegistered']==active[index]
        assert refs['externalFutures']==(0 if index==0 else 1) and refs['externalFirstFutureDone']==(None if index==0 else index>=2)
        assert history[index]<=refs['weakCellsAlive']<=9 and refs['externalFutures']<=refs['weakFuturesAlive']<=9
        assert all(0<=refs[key]<=refs['weakCellsAlive'] for key in ('releasedAlive','nativeDoneAlive','futureCellBackrefs','releaseClosureRetained','drainClosureRetained'))
        assert 0<=refs['weakClosuresAlive']<=18 and refs['ioFutureScope'].startswith('NOT_INSTANTIATED_NO_ENGINE_NO_NATIVE_IO;')
        assert record['releaseCount']==record['drainCount']==record['callbackCount']==completed[index]
        snapshots.append(dict(stage=record['stage'],metrics=values,deltaFromOriginalZero=delta,references=refs))
    runtime=report['runtime'];backend=report['synchronizationBackend']
    assert runtime['implementation']=='CPython' and runtime['pointerBits']==64 and runtime['forceGCInvocations']==0 and runtime['version'] and runtime['compiler'] and runtime['executable']
    assert backend['exactCBackend']==backend['handleTypeCausality']=='UNKNOWN' and backend['limitation']
    assert backend['lockModule']==backend['rlockModule']=='_thread' and backend['threadModuleOrigin']=='built-in'
    source_before=[];expected_source={'src/'+name for name in ('authority.py','notifications.py','gengine.py','phases.py')}
    assert len(report['sourceEvidence'])==4 and {row['path'] for row in report['sourceEvidence']}==expected_source
    for row in report['sourceEvidence']:
        preserved=owned(row['preservedPath'],BASE/'artifacts/diagnostic-source-before');assert preserved.name==Path(row['path']).name and sha(preserved)==row['sha256']
        current=owned(row['path'],BASE/'src');source_before.append(dict(path=row['path'],preservedPath=row['preservedPath'],beforeSha256=row['sha256'],currentSha256=sha(current)))
    outer_path=BASE/'evidence/g-lifecycle-outer-exit.json';outer=read(outer_path)
    assert outer['schema']==1 and outer['scope']=='E2C_ORIGINAL_G_CALLER_EXIT_OBSERVATION' and outer['evidence']==relative(path) and outer['sha256']==sha(path)
    assert outer['runId']==run_id and outer['identity']==identity and outer['observedCommandExitCode']==0 and outer['originalInvocationComplete'] is True
    assert outer['rerun'] is outer['realExecutionAllowed'] is False and outer['newDiagnosticG']==0
    all_bytes=sum(p.stat().st_size for p in (BASE/'evidence').glob('g-lifecycle*.json'))
    assert report['diagnosticArtifactBytes']==all_bytes-outer_path.stat().st_size and all_bytes<=524288
    return dict(evidence=relative(path),outerExitEvidence=relative(outer_path),reservationEvidence=relative(plan_path),status=report['status'],identity=identity,
                metricSamples=6,diagnosticGInstances=1,observations=snapshots,firstApprovedLimitExceedance=first,sourceBefore=source_before,
                runtime=runtime,synchronizationBackend=backend,reader=report['nativeReader'],closure=report['closure'],
                diagnosticLogBytesIncludingOuterExit=all_bytes,originalBaselineRetained=True,externalFutureRetained=True,noInFlight=True,
                eligibleForActualRegression=False,postFixOSComparisonRun=False,handleTypeCausality='UNKNOWN')

def verify_alias(group):
    assert group['scope']=='E2C_A01_REAL_G_NATIVE_ALIAS_GRANT_SELF_OWNED_CHECKS' and group['status']=='PASS' and group['assertions']==len(group['checks'])>0
    expected={'normal':'INPUT_ALIAS','query-failure':'BLOCKED_VERSION_NOT_PROVEN','identity-mismatch':'SOURCE_VERSION_IDENTITY_CHANGED','close-unknown':'GUARD_CLOSE_UNKNOWN_NO_RETRY'}
    assert len(group['cases'])==4 and {row['case'] for row in group['cases']}==set(expected)
    assert group['helpersStarted'] is group['mediaRead'] is group['realPFRun'] is group['real61Run'] is False and group['mediaBytesRead']==group['newHelpers']==0
    for row in group['cases']:
        mode=row['case'];assert row['reason']==expected[mode] and row['controls']==1 and row['rpc']==row['mediaBytesRead']==row['fileByteDelegates']==row['remainingResources']==0
        assert len(row['opens'])==2 and row['opens'][0]['path']==row['opens'][1]['path']
        source=Path(row['opens'][0]['path']);assert source.is_relative_to(BASE/'selfcheck') and source.name=='C.bin' and source.parent.name=='inputs'
        assert all((value['access'],value['share'],value['creation'],value['flags'])==(0x80000000,1,3,0x80) for value in row['opens'])
        assert row['queryAttempts']==2 and row['actualQueryCalls']==(1 if mode=='query-failure' else 2)
        assert row['metadataRequested']==row['metadataWritten'] and row['metadataTransactions']<=2 and len(row['closes'])==2 and all(value['actualReturned'] for value in row['closes'])
        record=row['stoppedObject'];assert record['object'] and record['ticket'] and record['owner']=='G' and record['attempts']==1
        if mode=='close-unknown':
            assert record['disposition']=='UNKNOWN' and record['nativeCloses']==0 and 'unknown-retains-original-ownership-and-credit' in group['checks']
            assert len(row['controlledCleanup'])==1 and row['controlledCleanup'][0]['proof']=='TEST_RETAINED_ACTUAL_CLOSE_RETURN' and row['controlledCleanup'][0]['newCloseCalls']==0
        else:assert record['disposition']=='CLOSED_PROVEN' and record['nativeCloses']==1 and row['controlledCleanup']==[]
    return dict(assertions=group['assertions'],activeFlow='Q09-ALIAS',cases=4,rpc=0,fileByteDelegates=0,unknownRetainedBeforeControlledRetirement=True)

def verify_static_evidence(lifecycle):
    build_path=BASE/'evidence/build.json';build=read(build_path)
    assert build['schema']==1 and build['scope']=='CENTRAL_LOCAL_COMPILE_OBSERVED' and build['status']=='PASS'
    assert build['invocations']==1 and build['repairCompilations']==0 and build['assemblySha256']==sha(BASE/'artifacts/E2C.dll')
    assert build['helpersStarted']==build['diagnosticGStarted']==build['mediaBytesRead']==build['downloads']==0
    for row in build['sources']:assert sha(owned(row['path'],BASE/'src'))==row['sha256']
    backend_path=BASE/'evidence/synchronization-backend.json';backend=read(backend_path)
    assert backend['schema']==1 and backend['scope']=='E2C_LOCAL_SYNCHRONIZATION_SOURCE_INSPECTION_ONLY'
    assert backend['extraMetricSamples']==backend['extraDiagnosticG']==0 and backend['compiledCBackend']==backend['handleTypeCausality']=='UNKNOWN'
    assert backend['foundThreadNtSource'] is False and backend['interpretation']
    runtime_dir=Path(lifecycle['runtime']['executable']).parent
    dll=Path(backend['runtimeDll']['path']);assert dll.parent==runtime_dir and dll.name=='python312.dll' and sha(dll)==backend['runtimeDll']['sha256']
    for row in backend['packagedHeaders']:
        path=Path(row['path']);assert path.is_relative_to(runtime_dir/'include') and path.suffix=='.h' and path.stat().st_size==row['bytes'] and sha(path)==row['sha256']
    change_path=BASE/'evidence/lifecycle-change-map.json';changes=read(change_path)
    assert changes['schema']==1 and changes['scope']=='E2C_REFERENCE_LIFECYCLE_CHANGE_MAP'
    assert changes['diagnosticEvidence']==lifecycle['evidence'] and changes['diagnosticRanBeforeFix'] is True
    assert changes['postFixOSComparisonRun'] is changes['actualFullRun'] is False
    assert len(changes['changes'])==5 and {row['path'] for row in changes['changes']}=={'src/authority.py','src/notifications.py','src/gengine.py','src/phases.py','src/controller.py'}
    before_by_path={row['path']:row for row in lifecycle['sourceBefore']}
    for row in changes['changes']:
        assert sha(owned(row['path'],BASE/'src'))==row['afterSha256'] and row['change']
        if 'beforePath' in row:
            before=before_by_path[row['path']]
            assert row['beforePath']==before['preservedPath'] and row['beforeSha256']==before['beforeSha256']
            assert row['afterSha256']==before['currentSha256'] and row['beforeSha256']!=row['afterSha256']
        else:
            assert row['path']=='src/controller.py' and row['beforeProjectPath']=='docs/coder/d1e2b/src/controller.py'
            assert sha(BASE.parents[2]/row['beforeProjectPath'])==row['beforeSha256']
    return dict(buildEvidence=relative(build_path),compileInvocations=1,repairCompilations=0,assemblySha256=build['assemblySha256'],
                synchronizationEvidence=relative(backend_path),changeMapEvidence=relative(change_path),compiledCBackend='UNKNOWN',handleTypeCausality='UNKNOWN',extraMetricSamples=0)

def verify_lifecycle_checks(group):
    assert group['scope']=='E2C_PRODUCTION_CELL_LIFECYCLE_LOGIC_ONLY' and group['status']=='PASS' and group['assertions']==len(group['checks'])>0
    assert group['controlledThreadsJoined'] is True and group['forceGC'] is False
    assert group['actualOSQueries']==group['diagnosticGInstances']==group['actualFullRuns']==group['helpersStarted']==group['mediaBytesRead']==group['fixtureBytes']==0
    closures=group['closures'];assert closures
    for row in closures:
        assert row['hubClosed'] is True and row['workersAlive']==row['buffers']==0 and row['remainingWorkerCredits']==[]
        assert row['total']==row['activeLogicalRecords']+row['archived']<=64
    capacity=next(row for row in closures if row['case']=='64-total-capacity')
    assert capacity['total']==capacity['archived']==64 and capacity['activeLogicalRecords']==0
    unknown=next(row for row in closures if row['case']=='submit-UNKNOWN-retained')
    assert unknown['total']==unknown['activeLogicalRecords']==1 and unknown['archived']==0 and unknown['blocked'] is not None
    return dict(assertions=group['assertions'],controlledThreadsJoined=True,capacity=capacity,unknownRetained=unknown,closures=closures,actualOSQueries=0,postFixOSComparisonRun=False)

def audit():
    manifest=read(BASE/'manifest/branches.json');configuration=verify_configuration(manifest);upstream=verify_upstreams()
    for pattern in ('run-selfcheck-*.json','mock-selfcheck-*.json','pending-*.json','diagnostic-*.json','actual-regression-*.json'):
        assert not list((BASE/'evidence').glob(pattern)),'E2C_FORBIDS_FULL_OR_OLD_R_EXECUTION:'+pattern
    targets=[(p,read(p)) for p in (BASE/'evidence').glob('targeted-*.json')]
    passing=[(p,value) for p,value in targets if value['status']=='PASS'];assert passing,'TARGETED_PASS_EVIDENCE_MISSING'
    path,target=max(passing,key=lambda item:item[0].name);groups={row['module']:row for row in target['groups']}
    expected={'e2c_checks','alias_checks','diagnostic_checks','namespace_checks','observer_checks','startup_checks','completion_checks','authority_checks','recovery_checks','metadata_checks','unitcheck','lifecycle_checks'}
    assert len(target['groups'])==len(groups)==12 and set(groups)==expected and all(row['status']=='PASS' and type(row['assertions']) is int and row['assertions']>0 for row in groups.values())
    assert target['assertions']==sum(row['assertions'] for row in groups.values()) and target['helpersStarted'] is target['mediaRead'] is target['realExecution'] is False
    alias=verify_alias(groups['alias_checks']);lifecycle=verify_lifecycle();static=verify_static_evidence(lifecycle);logical_lifecycle=verify_lifecycle_checks(groups['lifecycle_checks'])
    for item in [*(BASE/'src').glob('*.py'),*(BASE/'tools').glob('*.py')]:ast.parse(item.read_text(encoding='utf-8'),filename=str(item))
    files=[p for p in (BASE/'selfcheck').rglob('*') if p.is_file()];fixtures=sum(p.stat().st_size for p in files if is_fixture(p))
    logs=sum(p.stat().st_size for p in files if not is_fixture(p))+sum(p.stat().st_size for p in (BASE/'evidence').glob('*') if p.is_file())
    assert fixtures<=2097152 and logs<=4194304
    denials=read(BASE/'evidence/entry-denials.json');assert denials['schema']==1 and denials['status']=='PASS' and denials['scope']=='E2C_ENTRY_DENIALS' and len(denials['cases'])==7
    for row in denials['cases']:
        response=row['response'];assert row['exitCode']==2 and response['helpersStarted']==0
        assert response.get('realExecutionAllowed',response.get('executionAllowed')) is False
        assert response.get('noInFlight') is True or (response.get('executionAllowed') is False and response.get('outputRootCreated') is False and response['mediaBytesRead']==0)
    assert denials['actualAPIDenials']==dict(reserve_actual='E2C_ACTUAL_FULL_NOT_AUTHORIZED_NEW_BATCH_REQUIRED',claim_actual='E2C_ACTUAL_FULL_NOT_AUTHORIZED_NEW_BATCH_REQUIRED')
    assert denials['singleGReservationCheck']=='EXCLUSIVE_EXISTING_RESERVATION_REFUSED_NO_DIAGNOSTIC_RUN' and denials['singleGReservationUnchanged'] is True
    assert denials['singleGReservationSha256']==sha(BASE/'evidence/g-lifecycle-reservation.json') and denials['forbiddenConstructorsEntered']==[]
    assert denials['newHelpers']==denials['newDiagnosticG']==denials['newOSMetricSamples']==denials['mediaBytesRead']==0 and denials['realRootCreated'] is False
    assert denials['noInFlight'] is True and denials['realExecutionAllowed'] is False
    return dict(status='PASS',scope='E2C_READ_ONLY_EVIDENCE_AUDIT',configurationVerified=True,configuration=configuration,
                targetedEvidence=relative(path),targetedGroups=list(groups),targetedAssertions=target['assertions'],totalAssertions=target['assertions'],driverSyntheticAssertions=target['assertions'],
                aliasFixVerified=True,alias=alias,lifecycleFixVerified=True,lifecycleChecksAssertions=groups['lifecycle_checks']['assertions'],lifecycleChecks=logical_lifecycle,
                diagnosticVerified=True,lifecycle=lifecycle,diagnosticEvidence=lifecycle['evidence'],diagnosticOuterExitEvidence=lifecycle['outerExitEvidence'],diagnosticGInstances=1,metricSamples=6,
                staticEvidence=static,entryDenialsEvidence='evidence/entry-denials.json',
                actualFullStatus='NOT_RUN',actualFullAssertions=0,actualFullReportedAssertions=None,actualFullReason='E2C_FULL_NOT_AUTHORIZED_E2B_ALLOWANCE_CONSUMED',
                runtimeAdmission=RUNTIME_ADMISSION,postFixOSComparisonRun=False,handleTypeCausality='UNKNOWN',noInFlightVerified=True,
                realExecutionEnabled=False,realMedia='NOT_RUN',realPF='NOT_RUN',syntheticBytes=fixtures,logAndEvidenceBytesAtAudit=logs,mockAssertionsIncluded=False,mediaRead=False,**upstream)
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--audit',action='store_true');options=parser.parse_args()
    print(json.dumps(audit() if options.audit else dict(mode='INSPECT_ONLY'),separators=(',',':')))
