"""Pure E2B diagnostic receipt validation and a one-use synthetic reservation.

This module performs no IO and starts no worker/process. A reservation is only
for the explicitly approved, one-time actual-observer synthetic regression;
the caller must persist it with CREATE_NEW before launching anything. It is
never a real-media execution capability.
"""
from __future__ import annotations

import copy
import hashlib
import json
import math
import threading
from gcore import Refused

STAGES=('MINIMAL_START','LOAD_COMPLETE','INIT_COMPLETE','HELLO_SERIALIZED')
METHODS=('ADD_TYPE','LOAD_FROM')
METRICS=('threads','handles','workingSetBytes','privateBytes')
ABSOLUTE_R_LIMITS=dict(threads=64,handles=512,workingSetBytes=536870912,privateBytes=536870912)
RUNTIME_R_DELTAS=dict(threads=32,handles=128,workingSetBytes=268435456,privateBytes=268435456)
DIAGNOSTIC_SCOPE='E2C_FIXED_R_STARTUP_DIAGNOSTIC'


def _finite(value):
    return type(value) is int or (type(value) is float and math.isfinite(value))


def _identity(value):
    return (isinstance(value,dict) and type(value.get('pid')) is int and value['pid']>0 and
            type(value.get('creationTime100ns')) is int and value['creationTime100ns']>0 and
            isinstance(value.get('owner'),str) and 0<len(value['owner'])<=128)


def _same_identity(value,expected):
    return _identity(value) and all(value[key]==expected[key] for key in ('pid','creationTime100ns','owner'))


def _encoded(value):
    # Reject non-JSON objects, cycles and non-finite values even in extra fields.
    return json.dumps(value,separators=(',',':'),ensure_ascii=True,allow_nan=False).encode('ascii')


def validate_diagnostic(report):
    """Validate fixed observations; assertions in a JSON receipt are not OS proof.

    Both original instances must have complete identity, timing, closure and
    exit evidence. Add-Type overlimits remain visible but cannot substitute for
    the LoadFrom HELLO. Diagnostic changes from MINIMAL_START are descriptive;
    an actual regression establishes its own R baseline at its original HELLO.
    """
    blockers=[];exceedances=[];deltas={};candidate_hello=None;valid_samples=0
    def block(reason):
        if reason not in blockers:blockers.append(reason)
    def span(value,label,limit):
        if not isinstance(value,dict):block(label+':TIME_SCHEMA');return None
        start,end,duration=(value.get(key) for key in ('startedAt','endedAt','durationSeconds'))
        if not all(_finite(item) for item in (start,end,duration)) or start<0 or end<start or duration<0:
            block(label+':TIME_INVALID');return None
        if abs((end-start)-duration)>1e-6:block(label+':DURATION_MISMATCH')
        if duration>limit:block(label+':TIME_LIMIT_EXCEEDED')
        return start,end,duration
    encoded=None
    try:encoded=_encoded(report)
    except (TypeError,ValueError,OverflowError):block('DIAGNOSTIC_JSON_INVALID')
    if encoded is not None and len(encoded)>524288:block('DIAGNOSTIC_REPORT_SIZE_EXCEEDED')
    if not isinstance(report,dict):report={};block('DIAGNOSTIC_SCHEMA')
    if type(report.get('schema')) is not int or report.get('schema')!=1:block('DIAGNOSTIC_SCHEMA')
    if report.get('scope')!=DIAGNOSTIC_SCOPE:block('DIAGNOSTIC_SCOPE')
    if report.get('evidenceKind')!='ACTUAL_OS_OBSERVER':block('ACTUAL_OS_OBSERVER_EVIDENCE_REQUIRED')
    if report.get('realExecutionAllowed',False) is not False:block('REAL_EXECUTION_NOT_AUTHORIZED')
    configuration=report.get('configuration')
    if not isinstance(configuration,dict):configuration={};block('DIAGNOSTIC_CONFIGURATION')
    if configuration.get('pwshVersion')!='7.6.5' or configuration.get('dotnetVersion')!='10.0.11':block('FIXED_RUNTIME_REQUIRED')
    digest=configuration.get('assemblySha256')
    if not isinstance(digest,str) or len(digest)!=64 or any(char not in '0123456789abcdef' for char in digest):block('FIXED_ASSEMBLY_DIGEST_REQUIRED')
    if configuration.get('stageOrder')!=list(STAGES) or configuration.get('methods')!=list(METHODS):block('FIXED_DIAGNOSTIC_PLAN_REQUIRED')
    total=span(report,'DIAGNOSTIC',90)
    if report.get('unknowns')!=[]:block('DIAGNOSTIC_UNKNOWN_OWNERSHIP_OR_RESULT')
    if report.get('workerJoined') is not True:block('DIAGNOSTIC_NATIVE_WORKER_JOIN_NOT_PROVEN')
    if type(report.get('remainingResources')) is not dict or report.get('remainingResources')!={}:block('DIAGNOSTIC_RESOURCES_PENDING')
    if type(report.get('ledgerPeak')) is not int or not 1<=report['ledgerPeak']<=24:block('DIAGNOSTIC_RESOURCE_PEAK_INVALID')
    native_reader=report.get('nativeReader')
    if not isinstance(native_reader,dict):native_reader={};block('DIAGNOSTIC_NATIVE_READER_PROOF_REQUIRED')
    for key,expected in dict(cycles=8,identityQueries=2,borrowedIdentityQueries=2,mediaCalls=0,rpcCalls=0,newWorkers=0,maximumOwnedHandlesObserved=1).items():
        if type(native_reader.get(key)) is not int or native_reader.get(key)!=expected:block('DIAGNOSTIC_NATIVE_READER:'+key)
    if (type(native_reader.get('openedHandles')) is not int or type(native_reader.get('closedHandles')) is not int or
        native_reader.get('openedHandles',0)<=0 or native_reader.get('openedHandles')!=native_reader.get('closedHandles') or
        native_reader.get('observerCreditHeld') is not False or native_reader.get('closeUnknown') is not False):block('DIAGNOSTIC_NATIVE_READER_OWNERSHIP_PENDING')
    costs=report.get('costs')
    if not isinstance(costs,dict):costs={};block('DIAGNOSTIC_COSTS')
    for key,expected in dict(processInstances=2,metricSamples=8,identityQueries=2,controlRequests=4,stageAcks=8,testMediaBytes=0).items():
        if type(costs.get(key)) is not int or costs.get(key)!=expected:block('DIAGNOSTIC_COST:'+key)
    for key,limit in dict(logBytes=524288,fixtureBytes=2097152,batchEvidenceBytes=4194304).items():
        if type(costs.get(key)) is not int or not 0<=costs.get(key)<=limit:block('DIAGNOSTIC_COST:'+key)
    if type(costs.get('logBytes')) is int and type(costs.get('batchEvidenceBytes')) is int and costs['logBytes']>costs['batchEvidenceBytes']:block('DIAGNOSTIC_LOG_OUTSIDE_BATCH_EVIDENCE')
    if type(costs.get('observerMaxOwnedHandles')) is not int or costs.get('observerMaxOwnedHandles')!=1:block('OBSERVER_SINGLE_HANDLE_REQUIRED')
    if costs.get('original452Charged') is not False:block('DIAGNOSTIC_COST_MUST_BE_SEPARATE_FROM_452')
    instances=report.get('instances')
    if not isinstance(instances,list):instances=[];block('TWO_FIXED_ORIGINAL_INSTANCES_REQUIRED')
    if len(instances)!=2:block('TWO_FIXED_ORIGINAL_INSTANCES_REQUIRED')
    previous_end=None;originals=[];request_ids=[];global_opened=global_closed=0;last_stage_facts=None
    for position,instance in enumerate(instances):
        label='INSTANCE:'+str(position)
        if not isinstance(instance,dict):block(label+':SCHEMA');continue
        method=instance.get('method');expected_method=METHODS[position] if position<len(METHODS) else None
        if method!=expected_method:block(label+':METHOD_ORDER')
        label='INSTANCE:'+str(method)
        identity=instance.get('identity');identity_valid=_identity(identity)
        if not identity_valid:block(label+':ORIGINAL_IDENTITY_INVALID')
        else:
            if any(identity['owner']==old['owner'] or (identity['pid'],identity['creationTime100ns'])==(old['pid'],old['creationTime100ns']) for old in originals):block(label+':ORIGINAL_INSTANCE_REUSED')
            originals.append(identity)
        timing=span(instance,label,30)
        if timing and total and (timing[0]<total[0] or timing[1]>total[1]):block(label+':OUTSIDE_TOTAL_TIME')
        if timing and previous_end is not None and timing[0]<previous_end:block(label+':INSTANCES_OVERLAP')
        if timing:previous_end=timing[1]
        if instance.get('outstandingUnknown') is not False:block(label+':UNKNOWN_OWNERSHIP_OR_RESULT')
        transport=instance.get('transport')
        if not isinstance(transport,dict):transport={};block(label+':TRANSPORT_PROOF_REQUIRED')
        if transport.get('threadsJoined') is not True:block(label+':TRANSPORT_READER_JOIN_NOT_PROVEN')
        if transport.get('errors')!=[]:block(label+':TRANSPORT_ERROR_OR_PENDING')
        if transport.get('events')!=['ACK','ACK','ACK','HELLO','ACK','EXIT']:block(label+':TRANSPORT_CONTROL_COST_OR_ORDER')
        records=instance.get('stages')
        if not isinstance(records,list):records=[];block(label+':FIXED_FOUR_STAGES_REQUIRED')
        if len(records)!=4:block(label+':FIXED_FOUR_STAGES_REQUIRED')
        previous_stage_end=None;minimal=None;method_deltas={}
        for index,record in enumerate(records):
            if not isinstance(record,dict):block(label+':STAGE_SCHEMA');continue
            stage=record.get('stage');stage_label=label+':'+str(stage)
            if index>=len(STAGES) or stage!=STAGES[index]:block(stage_label+':STAGE_ORDER_OR_DUPLICATE')
            stage_timing=span(record,stage_label,5)
            if stage_timing and timing and (stage_timing[0]<timing[0] or stage_timing[1]>timing[1]):block(stage_label+':OUTSIDE_INSTANCE_TIME')
            if stage_timing and previous_stage_end is not None and stage_timing[0]<previous_stage_end:block(stage_label+':STAGES_OVERLAP')
            if stage_timing:previous_stage_end=stage_timing[1]
            duration=record.get('sampleDurationSeconds')
            if not _finite(duration) or duration<0 or duration>.1 or (stage_timing and duration>stage_timing[2]):block(stage_label+':SAMPLE_DEADLINE_OR_DURATION')
            if not identity_valid or not _same_identity(record.get('identity'),identity):block(stage_label+':ORIGINAL_IDENTITY_CHANGED')
            if record.get('sameCreationValidatedByReader') is not True:block(stage_label+':ORIGINAL_PROCESS_BINDING_NOT_PROVEN')
            values=record.get('metrics');metrics_valid=isinstance(values,dict) and all(type(values.get(key)) is int and values[key]>=0 for key in METRICS)
            if not metrics_valid:block(stage_label+':RAW_METRICS_INVALID')
            else:
                valid_samples+=1
                if index==0 and stage=='MINIMAL_START':minimal=values
                if minimal is not None:method_deltas[stage]={key:values[key]-minimal[key] for key in METRICS}
                for key in METRICS:
                    if values[key]>ABSOLUTE_R_LIMITS[key]:exceedances.append(dict(method=method,stage=stage,metric=key,value=values[key],limit=ABSOLUTE_R_LIMITS[key]))
                if position==1 and index==3 and method=='LOAD_FROM' and stage=='HELLO_SERIALIZED':candidate_hello=copy.deepcopy(values)
            facts=record.get('observerFacts')
            if not isinstance(facts,dict):facts={};block(stage_label+':OBSERVER_PROOF_REQUIRED')
            opened,closed=facts.get('openedHandles'),facts.get('closedHandles')
            if (type(opened) is not int or type(closed) is not int or opened!=closed or opened<=global_opened or closed<=global_closed):block(stage_label+':OBSERVER_CLOSE_NOT_PROVEN')
            else:global_opened,global_closed=opened,closed
            if type(facts.get('cycles')) is not int or facts.get('cycles')!=position*4+index+1:block(stage_label+':OBSERVER_SAMPLE_SEQUENCE')
            if (facts.get('observerCreditHeld') is not False or facts.get('closeUnknown') is not False or
                type(facts.get('maximumOwnedHandlesObserved')) is not int or facts.get('maximumOwnedHandlesObserved')!=1):block(stage_label+':OBSERVER_OWNERSHIP_PENDING')
            last_stage_facts=facts
        deltas[str(method)]=method_deltas
        hello=instance.get('hello')
        if not isinstance(hello,dict):hello={};block(label+':ORIGINAL_HELLO_REQUIRED')
        if (not identity_valid or type(hello.get('pid')) is not int or hello.get('pid')!=identity['pid'] or
            hello.get('instance')!=identity['owner'] or hello.get('serialized') is not True or hello.get('runtime')!='.NET 10.0.11'):
            block(label+':ORIGINAL_HELLO_BINDING')
        request_id=hello.get('requestId')
        if not isinstance(request_id,str) or not 0<len(request_id)<=128 or request_id in request_ids:block(label+':HELLO_REQUEST_ID')
        else:request_ids.append(request_id)
        proof=instance.get('exitProof')
        if (not isinstance(proof,dict) or not identity_valid or proof.get('exited') is not True or
            type(proof.get('code')) is not int or proof.get('code')!=0 or type(proof.get('pid')) is not int or
            proof.get('pid')!=identity['pid'] or type(proof.get('creationTime100ns')) is not int or
            proof.get('creationTime100ns')!=identity['creationTime100ns'] or proof.get('instance')!=identity['owner']):
            block(label+':ORIGINAL_EXIT_NOT_PROVEN')
    if valid_samples!=8:block('EIGHT_RAW_STAGE_OBSERVATIONS_REQUIRED')
    if last_stage_facts is None or any(last_stage_facts.get(key)!=native_reader.get(key) for key in ('cycles','openedHandles','closedHandles')):block('DIAGNOSTIC_FINAL_READER_MISMATCH')
    candidate_ok=candidate_hello is not None and all(candidate_hello[key]<=ABSOLUTE_R_LIMITS[key] for key in METRICS)
    if not candidate_ok:block('LOAD_FROM_FIXED_HELLO_ABSOLUTE_LIMITS_NOT_MET')
    first=exceedances[0] if exceedances else None
    if 'firstExceedance' in report and report['firstExceedance']!=first:block('FIRST_EXCEEDANCE_MUST_NOT_BE_REPLACED')
    return dict(schema=1,scope='E2C_DIAGNOSTIC_ADMISSION_ONLY',valid=not blockers,
                eligibleForOneActualSyntheticRegression=not blockers,realExecutionAllowed=False,
                blockers=blockers,firstExceedance=copy.deepcopy(first),absoluteExceedances=exceedances,
                candidateHello=copy.deepcopy(candidate_hello),candidateHelloWithinApprovedAbsoluteLimits=candidate_ok,
                diagnosticDeltasFromMinimal=deltas,diagnosticMinimalIsRuntimeBaseline=False,
                actualRegressionRBaseline='ITS_OWN_ORIGINAL_HELLO',actualRegressionRDeltaLimits=copy.deepcopy(RUNTIME_R_DELTAS),
                diagnosticSha256=hashlib.sha256(encoded).hexdigest() if encoded is not None else None)


class SingleActualRegressionGate:
    """Consume one reservation before launch; failure never refunds it.

    A caller-supplied prior record of any kind blocks reuse. Cross-process
    exclusion is the caller's mandatory CREATE_NEW persistence, not this lock.
    """
    def __init__(self,report,prior_record=None):
        self._validation=validate_diagnostic(copy.deepcopy(report));self._prior_present=prior_record is not None
        self._consumed=self._prior_present;self._record=copy.deepcopy(prior_record);self._lock=threading.Lock()
    @property
    def validation(self):return copy.deepcopy(self._validation)
    def reserve(self,run_id):
        with self._lock:
            if self._consumed:raise Refused('ACTUAL_SYNTHETIC_REGRESSION_ALREADY_RESERVED')
            if not self._validation['eligibleForOneActualSyntheticRegression']:raise Refused('ACTUAL_SYNTHETIC_REGRESSION_NOT_ELIGIBLE')
            if not isinstance(run_id,str) or not 0<len(run_id)<=128:raise Refused('ACTUAL_SYNTHETIC_REGRESSION_RUN_ID')
            self._consumed=True
            self._record=dict(schema=1,scope='E2C_SINGLE_ACTUAL_SYNTHETIC_REGRESSION_RESERVATION',consumed=True,
                              runId=run_id,diagnosticSha256=self._validation['diagnosticSha256'],maximumActualRuns=1,
                              realExecutionAllowed=False,persistCreateNewBeforeLaunch=True)
            return copy.deepcopy(self._record)
    def snapshot(self):
        with self._lock:return dict(consumed=self._consumed,priorRecordPresent=self._prior_present,record=copy.deepcopy(self._record),realExecutionAllowed=False)
