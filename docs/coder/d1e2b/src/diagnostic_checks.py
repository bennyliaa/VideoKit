"""Controlled JSON-only diagnostic gate checks; not actual R/OS evidence."""
from __future__ import annotations

import copy
import threading
from diagnostic_gate import STAGES,METHODS,DIAGNOSTIC_SCOPE,validate_diagnostic,SingleActualRegressionGate
from gcore import Refused,compact,need


def _receipt():
    instances=[]
    for method_index,method in enumerate(METHODS):
        identity=dict(pid=501+method_index,creationTime100ns=100001+method_index,owner='original-'+method)
        records=[];begin=method_index*10.
        for stage_index,stage in enumerate(STAGES):
            # Keep the known historical Add-Type 519 observation. Candidate's
            # startup->HELLO change exceeds128 but is not a runtime delta base.
            handles=(350,519,520,519)[stage_index] if method_index==0 else (300,490,505,512)[stage_index]
            start=begin+stage_index
            cycle=method_index*4+stage_index+1
            records.append(dict(stage=stage,startedAt=start,endedAt=start+.2,durationSeconds=.2,sampleDurationSeconds=.01,
                                identity=copy.deepcopy(identity),metrics=dict(threads=16,handles=handles,workingSetBytes=67108864,privateBytes=50331648),
                                sameCreationValidatedByReader=True,
                                observerFacts=dict(cycles=cycle,openedHandles=2*cycle,closedHandles=2*cycle,maximumOwnedHandlesObserved=1,
                                                   observerCreditHeld=False,closeUnknown=False)))
        instances.append(dict(method=method,identity=identity,startedAt=begin,endedAt=begin+4,durationSeconds=4,
                              stages=records,hello=dict(instance=identity['owner'],pid=identity['pid'],runtime='.NET 10.0.11',serialized=True,requestId=method+'-HELLO'),
                              exitProof=dict(pid=identity['pid'],creationTime100ns=identity['creationTime100ns'],instance=identity['owner'],code=0,exited=True),outstandingUnknown=False,
                              transport=dict(threadsJoined=True,errors=[],events=['ACK','ACK','ACK','HELLO','ACK','EXIT'])))
    return dict(schema=1,scope=DIAGNOSTIC_SCOPE,evidenceKind='ACTUAL_OS_OBSERVER',realExecutionAllowed=False,
                configuration=dict(pwshVersion='7.6.5',dotnetVersion='10.0.11',assemblySha256='a'*64,stageOrder=list(STAGES),methods=list(METHODS)),
                startedAt=0.,endedAt=15.,durationSeconds=15.,instances=instances,unknowns=[],
                workerJoined=True,remainingResources={},ledgerPeak=11,
                nativeReader=dict(cycles=8,identityQueries=2,borrowedIdentityQueries=2,openedHandles=16,closedHandles=16,
                                  maximumOwnedHandlesObserved=1,observerCreditHeld=False,closeUnknown=False,mediaCalls=0,rpcCalls=0,newWorkers=0),
                costs=dict(processInstances=2,metricSamples=8,identityQueries=2,controlRequests=4,stageAcks=8,logBytes=10000,fixtureBytes=0,
                           batchEvidenceBytes=10000,testMediaBytes=0,observerMaxOwnedHandles=1,original452Charged=False))


def run_checks(root=None,manifest=None):
    passed=[];blocked=[]
    def check(value,name):need(value,'DIAGNOSTIC_CHECK:'+name);passed.append(name)
    def invalid(change,reason,name):
        report=_receipt();change(report);result=validate_diagnostic(report)
        check(not result['eligibleForOneActualSyntheticRegression'] and result['realExecutionAllowed'] is False and any(reason in blocker for blocker in result['blockers']),name)
        blocked.append(dict(check=name,blockers=result['blockers']))
    def refuses(action,reason,name):
        try:action()
        except Refused as error:check(str(error)==reason,name);return
        raise AssertionError('Missing refusal:'+name)
    receipt=_receipt();result=validate_diagnostic(receipt)
    check(result['eligibleForOneActualSyntheticRegression'] and result['realExecutionAllowed'] is False,'complete-controlled-receipt-only-permits-one-synthetic-reservation')
    check(result['firstExceedance']==dict(method='ADD_TYPE',stage='LOAD_COMPLETE',metric='handles',value=519,limit=512),
          'historical-first519-survives-later520-and-candidate512')
    check(result['candidateHello']['handles']==512 and result['diagnosticDeltasFromMinimal']['LOAD_FROM']['HELLO_SERIALIZED']['handles']==212 and
          result['diagnosticMinimalIsRuntimeBaseline'] is False and result['actualRegressionRDeltaLimits']['handles']==128,
          'startup-difference-is-descriptive-and-cannot-replace-original-HELLO-runtime-baseline')
    invalid(lambda r:r['instances'][1]['stages'].pop(),'FIXED_FOUR_STAGES','missing-fixed-HELLO-stage-cannot-use-earlier-low-stage')
    invalid(lambda r:r['instances'][1]['stages'][3].update(stage='INIT_COMPLETE'),'STAGE_ORDER_OR_DUPLICATE','duplicate-stage-cannot-create-completeness')
    invalid(lambda r:r['instances'].reverse(),'METHOD_ORDER','AddType-cannot-substitute-for-LoadFrom-candidate')
    invalid(lambda r:r['instances'][1]['stages'][2]['identity'].update(owner='replacement'),'ORIGINAL_IDENTITY_CHANGED','owner-swap-in-middle-stage-blocks')
    invalid(lambda r:r['instances'][1]['stages'][2]['identity'].update(creationTime100ns=999),'ORIGINAL_IDENTITY_CHANGED','PID-reuse-or-creation-change-blocks')
    invalid(lambda r:r['instances'][1]['hello'].update(instance='old-owner'),'ORIGINAL_HELLO_BINDING','HELLO-must-serialize-the-same-original-owner')
    invalid(lambda r:r['instances'][1]['hello'].update(serialized=False),'ORIGINAL_HELLO_BINDING','unserialized-HELLO-is-not-the-fixed-gate')
    invalid(lambda r:r['instances'][1]['exitProof'].update(exited=False),'ORIGINAL_EXIT_NOT_PROVEN','unknown-original-exit-blocks-regression')
    invalid(lambda r:r['instances'][1]['exitProof'].update(code=1),'ORIGINAL_EXIT_NOT_PROVEN','failed-original-instance-exit-is-not-successful-diagnostic')
    for value in (None,float('nan'),float('inf'),-1,True,3.5):
        invalid(lambda r,value=value:r['instances'][1]['stages'][3]['metrics'].update(handles=value),'RAW_METRICS_INVALID','invalid-raw-handles-'+str(value))
    invalid(lambda r:r['instances'][1]['stages'][3]['metrics'].pop('privateBytes'),'RAW_METRICS_INVALID','all-four-raw-metrics-required')
    for field,value in (('threads',65),('handles',513),('workingSetBytes',536870913),('privateBytes',536870913)):
        invalid(lambda r,field=field,value=value:r['instances'][1]['stages'][3]['metrics'].update({field:value}),
                'LOAD_FROM_FIXED_HELLO_ABSOLUTE_LIMITS_NOT_MET','candidate-HELLO-overlimit-'+field)
    invalid(lambda r:r['instances'][1]['stages'][1]['observerFacts'].update(closeUnknown=True),'OBSERVER_OWNERSHIP_PENDING','unknown-close-is-not-refunded-by-later-success')
    invalid(lambda r:r['instances'][1]['stages'][1]['observerFacts'].update(closedHandles=3),'OBSERVER_CLOSE_NOT_PROVEN','opened-and-closed-counts-must-match-at-each-stage')
    invalid(lambda r:r['instances'][1]['stages'][1]['observerFacts'].update(observerCreditHeld=True),'OBSERVER_OWNERSHIP_PENDING','held-observer-credit-blocks-regression')
    invalid(lambda r:r['instances'][1]['stages'][1]['observerFacts'].update(maximumOwnedHandlesObserved=2),'OBSERVER_OWNERSHIP_PENDING','two-simultaneous-observer-handles-cannot-hide-behind-net-close')
    invalid(lambda r:r['instances'][1]['stages'][1].update(sampleDurationSeconds=.100001),'SAMPLE_DEADLINE','native-return-after100ms-is-not-a-successful-sample')
    invalid(lambda r:r['instances'][1]['stages'][1].update(durationSeconds=5.1,endedAt=16.1),'TIME_LIMIT_EXCEEDED','stage-over5s-blocks-without-forced-interruption')
    invalid(lambda r:r['instances'][1].update(durationSeconds=30.1,endedAt=40.1),'TIME_LIMIT_EXCEEDED','instance-over30s-blocks')
    invalid(lambda r:r.update(durationSeconds=90.1,endedAt=90.1),'TIME_LIMIT_EXCEEDED','total-over90s-blocks')
    invalid(lambda r:r.update(unknowns=['NATIVE_QUERY_PENDING']),'DIAGNOSTIC_UNKNOWN','inflight-native-result-is-pending-not-a-pass')
    invalid(lambda r:r.update(workerJoined=False),'DIAGNOSTIC_NATIVE_WORKER_JOIN_NOT_PROVEN','empty-unknown-list-cannot-hide-unjoined-native-worker')
    invalid(lambda r:r.update(remainingResources={'original-process':'UNKNOWN'}),'DIAGNOSTIC_RESOURCES_PENDING','empty-unknown-list-cannot-hide-original-resource-credit')
    invalid(lambda r:r.update(ledgerPeak=25),'DIAGNOSTIC_RESOURCE_PEAK_INVALID','diagnostic-cannot-expand-the-original24-resource-peak')
    invalid(lambda r:r['nativeReader'].update(cycles=7),'DIAGNOSTIC_NATIVE_READER:cycles','claimed8-cost-samples-cannot-hide-native-reader7')
    invalid(lambda r:r['nativeReader'].update(borrowedIdentityQueries=1),'DIAGNOSTIC_NATIVE_READER:borrowedIdentityQueries','both-original-process-anchors-must-use-borrowed-original-handles')
    invalid(lambda r:r['nativeReader'].update(closeUnknown=True),'DIAGNOSTIC_NATIVE_READER_OWNERSHIP_PENDING','top-level-native-UNKNOWN-blocks-even-when-stage-flags-look-safe')
    invalid(lambda r:r['nativeReader'].update(closedHandles=15),'DIAGNOSTIC_NATIVE_READER_OWNERSHIP_PENDING','unclosed-final-query-handle-cannot-hide-behind-process-exit')
    invalid(lambda r:r['nativeReader'].update(openedHandles=18,closedHandles=18),'DIAGNOSTIC_FINAL_READER_MISMATCH','unaccounted-query-after-last-stage-blocks')
    invalid(lambda r:r['instances'][1]['transport'].update(threadsJoined=False),'TRANSPORT_READER_JOIN_NOT_PROVEN','empty-unknown-list-cannot-hide-live-original-pipe-reader')
    invalid(lambda r:r['instances'][1]['transport'].update(errors=['process-handle-close-unknown']),'TRANSPORT_ERROR_OR_PENDING','transport-close-error-blocks-independently-of-top-level-unknowns')
    invalid(lambda r:r['instances'][1]['transport']['events'].append('HELLO'),'TRANSPORT_CONTROL_COST_OR_ORDER','extra-control-request-cannot-hide-in-fixed4-cost-counter')
    invalid(lambda r:r['instances'][1]['stages'][0]['observerFacts'].update(cycles=1),'OBSERVER_SAMPLE_SEQUENCE','second-instance-cannot-reset-single-reader-counters')
    invalid(lambda r:r['instances'][1]['stages'][0].update(sameCreationValidatedByReader=False),'ORIGINAL_PROCESS_BINDING_NOT_PROVEN','claimed-stable-identity-needs-original-process-binding')
    invalid(lambda r:r['costs'].update(logBytes=524289),'DIAGNOSTIC_COST:logBytes','diagnostic-log-does-not-expand512KiB')
    invalid(lambda r:r['costs'].update(batchEvidenceBytes=4194305),'DIAGNOSTIC_COST:batchEvidenceBytes','diagnostic-log-is-included-in-original4MiB')
    invalid(lambda r:r['costs'].update(fixtureBytes=2097153),'DIAGNOSTIC_COST:fixtureBytes','fixture2MiB-hard-limit')
    invalid(lambda r:r['costs'].update(processInstances=3),'DIAGNOSTIC_COST:processInstances','third-R-instance-is-not-a-diagnostic-retry')
    invalid(lambda r:r['costs'].update(metricSamples=9),'DIAGNOSTIC_COST:metricSamples','ninth-sample-is-not-a-retake-to-get-low-value')
    invalid(lambda r:r['costs'].update(controlRequests=5),'DIAGNOSTIC_COST:controlRequests','diagnostic-controls-have-independent-fixed-cost')
    invalid(lambda r:r['costs'].update(original452Charged=True),'DIAGNOSTIC_COST_MUST_BE_SEPARATE','diagnostic-costs-cannot-be-hidden-in-original452')
    invalid(lambda r:r['costs'].update(testMediaBytes=1),'DIAGNOSTIC_COST:testMediaBytes','diagnostic-does-not-read-one-test-media-byte')
    invalid(lambda r:r.update(firstExceedance=None),'FIRST_EXCEEDANCE_MUST_NOT_BE_REPLACED','declared-first-exceedance-cannot-erase-history')
    invalid(lambda r:r.update(evidenceKind='MOCK'),'ACTUAL_OS_OBSERVER_EVIDENCE_REQUIRED','mock-receipt-is-not-actual-run-admission')
    invalid(lambda r:r.update(realExecutionAllowed=True),'REAL_EXECUTION_NOT_AUTHORIZED','synthetic-diagnostic-does-not-grant-real-execution')

    gate=SingleActualRegressionGate(receipt);receipt['instances'][1]['stages'][3]['metrics']['handles']=999
    reservation=gate.reserve('one-original-actual-run')
    check(reservation['consumed'] and reservation['maximumActualRuns']==1 and reservation['persistCreateNewBeforeLaunch'] and
          reservation['realExecutionAllowed'] is False,'reservation-is-consumed-before-caller-launch-and-independent-of-mutated-input')
    reservation['consumed']=False
    check(gate.snapshot()['record']['consumed'],'caller-cannot-refund-reservation-by-mutating-returned-record')
    refuses(lambda:gate.reserve('retry-after-failed-full-run'),'ACTUAL_SYNTHETIC_REGRESSION_ALREADY_RESERVED','first-actual-FAIL-does-not-authorize-a-second-run')
    for prior in ({},False,{'consumed':False},gate.snapshot()['record']):
        refuses(lambda prior=prior:SingleActualRegressionGate(_receipt(),prior).reserve('restart'),
                'ACTUAL_SYNTHETIC_REGRESSION_ALREADY_RESERVED','any-existing-reservation-record-prevents-restart-'+str(prior))
    bad=_receipt();bad['instances'][1]['stages'][3]['metrics']['handles']=519
    refuses(lambda:SingleActualRegressionGate(bad).reserve('must-not-start'),'ACTUAL_SYNTHETIC_REGRESSION_NOT_ELIGIBLE','failed-candidate-gate-blocks-before-launch')
    gate=SingleActualRegressionGate(_receipt());barrier=threading.Barrier(3);outcomes=[]
    def reserve_competing(run_id):
        barrier.wait(1)
        try:gate.reserve(run_id);outcomes.append('RESERVED')
        except Refused as error:outcomes.append(str(error))
    threads=[threading.Thread(target=reserve_competing,args=('competing-'+str(index),),name='E2B-gate-probe-'+str(index)) for index in range(2)]
    for thread in threads:thread.start()
    barrier.wait(1)
    for thread in threads:thread.join(1)
    check(all(not thread.is_alive() for thread in threads) and sorted(outcomes)==['ACTUAL_SYNTHETIC_REGRESSION_ALREADY_RESERVED','RESERVED'],
          'two-in-process-callers-cannot-consume-the-same-one-run-reservation')
    report=dict(scope='E2B_JSON_GATE_LOGIC_ONLY_NOT_DIAGNOSTIC_OS_EVIDENCE',status='PASS',assertions=len(passed),checks=passed,
                negativeReceipts=blocked,controlledThreadsJoined=2,actualRInstances=0,actualOSQueries=0,mediaBytesRead=0,fixtureBytes=0,
                limitations='JSON claims are controlled test data. Runner must collect actual original-instance facts and atomically persist CREATE_NEW reservation before its one launch. This suite does not run the diagnostic or any regression; real entry remains closed.')
    need(len(compact(report))<=131072,'DIAGNOSTIC_CHECK_REPORT_BOUND')
    return report
