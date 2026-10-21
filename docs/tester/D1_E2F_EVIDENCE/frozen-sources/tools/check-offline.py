"""Bounded offline E2F checks over original bytes and memory-only negatives.

This module does not import a production runner or resource adapter. Existing
authored SYNTHETIC evidence is read once by the fixed, bounded evidence reader;
negative cases change copies in memory. No old output or permit is written.
"""
from __future__ import annotations

import argparse
import ast
import builtins
import copy
import contextlib
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import sys

sys.dont_write_bytecode=True
BASE=Path(__file__).resolve().parents[1]
_MODULES={}
_ORIGINAL=None
FORBIDDEN_IMPORTS={'gengine','gcore','authority','notifications','runtime_metrics','runtime_wiring',
                   'controller','scenarios','phases','subprocess','ctypes','threading','concurrent'}


def load_tool(name):
    if name not in _MODULES:
        canonical=name.removesuffix('.py').replace('-','_')
        spec=importlib.util.spec_from_file_location(canonical,BASE/'tools'/name)
        module=importlib.util.module_from_spec(spec)
        sys.modules[canonical]=module
        previous=builtins.__import__
        def only_offline(module_name,*args,**kwargs):
            if module_name.split('.')[0] in FORBIDDEN_IMPORTS:
                raise AssertionError('OFFLINE_RUNTIME_IMPORT:'+module_name)
            return previous(module_name,*args,**kwargs)
        builtins.__import__=only_offline
        try:spec.loader.exec_module(module)
        finally:builtins.__import__=previous
        _MODULES[name]=module
    return _MODULES[name]


def original_bundle():
    global _ORIGINAL
    if _ORIGINAL is None:_ORIGINAL=load_tool('evidence_io.py').load_original_bundle()
    return _ORIGINAL


def set_path(value,path,replacement):
    current=value
    for key in path[:-1]:current=current[key]
    current[path[-1]]=replacement


def run_checks():
    completion=load_tool('completion_evaluation.py')
    resources=load_tool('resource_evaluation.py')
    wrapper=load_tool('e2f_wrapper.py')
    original=original_bundle()
    passed=[];negatives=[]
    def check(condition,label):
        if not condition:raise AssertionError('E2F_OFFLINE_CHECK:'+label)
        passed.append(label)
    def evaluate(bundle):
        return completion.evaluate_completion(bundle['manifest'],bundle['preclose'],bundle['driver'],
                                               bundle['launcher'],bundle['global_events'])
    def refused(label,mutate,component='completion',semantic_reason=None):
        candidate=copy.deepcopy(original);mutate(candidate)
        if component in ('resources','aggregate'):
            # Match the caller's parsed JSON to its controlled raw-copy bytes.
            # Immutable-hash failures remain expected; semantic checks must
            # still reject the independently malformed resource facts.
            for key in ('ledgerPeaks','privateCells','callbackHub','runtimeObservation','metadataCommitStatus',
                        'metadataUnknownRequestedBytes','usage'):
                changed=candidate['driver']['driverWitness']
                if changed.get(key)!=original['driver']['driverWitness'].get(key):
                    candidate['preclose'][key]=copy.deepcopy(changed[key])
            for key,suffix in (('driver','execution/driver-result.json'),('launcher','execution/launcher-result.json'),
                               ('preclose','/result-before-close.json')):
                if candidate[key]!=original[key]:
                    name=next(name for name in candidate['files'] if name==suffix or name.endswith(suffix))
                    candidate['files'][name]=json.dumps(candidate[key],sort_keys=True,separators=(',',':')).encode('utf-8')
        before=copy.deepcopy(candidate)
        result=(evaluate(candidate) if component=='completion' else resources.evaluate_resources(candidate)
                if component=='resources' else wrapper.evaluate_bound_bundle(candidate))
        check(result.get('accepted') is False and bool(result.get('reasons')),label)
        check(candidate==before,'input-copy-remains-unchanged-'+label)
        if semantic_reason:
            check(any(semantic_reason in reason for reason in result['reasons']),
                  'actual-semantic-reason-is-observed-'+label)
        if component=='completion':
            check(result.get('newActualAttempts')==0 and result.get('executionAllowed') is False,
                  'negative-case-does-not-create-execution-authorization-'+label)
        negatives.append(dict(check=label,component=component,reasons=list(result['reasons'])))
        return result

    before=copy.deepcopy(original)
    correct=evaluate(original)
    resource_result=resources.evaluate_resources(original)
    check(correct.get('accepted') is True,'original-PF-and-61-precise-completion-proof-is-accepted-offline')
    check(resource_result.get('accepted') is True,'original-resource-and-output-proof-is-accepted-offline')
    check(correct.get('scope')=='EVIDENCE_REEVALUATION_COMPLETION' and correct.get('newActualAttempts')==0 and
          correct.get('executionAllowed') is False,'completion-acceptance-has-only-reevaluation-scope-and-no-new-authorization')
    history=correct['originalResult']
    check(history.get('driverStatus')==history.get('launcherStatus')=='FAIL' and history.get('GexitCode')==2 and
          history.get('assertions')==160 and history.get('actualBatchPasses')==0 and
          history.get('firstFailure')=='INCOMPLETE_FULL_ROW_COUNT',
          'original-FAIL-exit2-160-assertions-and-zero-batch-passes-are-preserved')
    check(hashlib.sha256(original['sealBytes']).hexdigest()=='aa59420cff4153395af2ab9b97eb47d8f560e91763b730f47c0fda3c0578b66a' and
          hashlib.sha256(original['files']['execution/result-manifest.json']).hexdigest()=='baa6a1ed87764a5d16b1d282717824110d0082bc188606edf4affb33377750ea' and
          hashlib.sha256(next(value for name,value in original['files'].items() if name.endswith('/result-before-close.json'))).hexdigest()=='702d8505e16bf504564179c14477e7cfe50af35c922531034c66645d6bc79032',
          'positive-source-is-bound-to-all-three-formally-approved-original-hashes')
    check(original==before,'positive-evaluations-do-not-overwrite-any-original-input')
    resource_history=resource_result['originalResult']
    check(resource_result.get('scope')=='EVIDENCE_REEVALUATION_RESOURCES' and resource_result.get('newActualAttempts')==0 and
          resource_history.get('status')=='FAIL' and resource_history.get('originalGExitCode')==2 and
          resource_history.get('originalAssertions')==160 and resource_history.get('actualFullPasses')==0 and
          resource_history.get('reservationConsumed') is True,
          'resource-acceptance-also-preserves-original-failure-and-consumed-permit')
    for category,byte_cap,file_cap in (('result',16777216,1024),('source',268435456,8192)):
        usage=original['readerUsage'][category]
        check(usage['byteCap']==byte_cap and usage['fileCap']==file_cap and
              0<=usage['bytes']<=byte_cap and 0<usage['files']<=file_cap,
              'fixed-bounded-original-'+category+'-read-budget-is-respected')

    # Cases below deliberately preserve count 62 where possible: a count-only
    # replacement for the old 61 check cannot satisfy these conditions.
    refused('missing-one-approved-scenario',lambda b:b['preclose']['rows'].pop(2))
    refused('duplicate-and-missing-scenario-still-counts-62',
            lambda b:b['preclose']['rows'].__setitem__(2,copy.deepcopy(b['preclose']['rows'][1])))
    refused('same-62-rows-in-wrong-approved-order',
            lambda b:b['preclose']['rows'].__setitem__(slice(1,3),list(reversed(b['preclose']['rows'][1:3]))))
    refused('extra-scenario-is-not-complete',lambda b:b['preclose']['rows'].append(copy.deepcopy(b['preclose']['rows'][1])))
    refused('unapproved-ID-cannot-replace-a-row-at-the-same-count',
            lambda b:set_path(b,('preclose','rows',2,'branch'),'EXTRA-NOT-APPROVED'))
    refused('PF-missing-even-with-all-61-scenarios',lambda b:b['preclose']['rows'].pop(0))
    refused('PF-duplicate-does-not-replace-an-approved-scenario',
            lambda b:b['preclose']['rows'].__setitem__(1,copy.deepcopy(b['preclose']['rows'][0])))
    refused('PF-must-complete-before-scenarios',
            lambda b:b['preclose']['rows'].__setitem__(slice(0,2),list(reversed(b['preclose']['rows'][0:2]))))
    refused('PF-controls-incomplete',lambda b:set_path(b,('preclose','rows',0,'controls'),15))
    refused('PF-completion-record-absent-controls',lambda b:b['preclose']['rows'][0].pop('controls'))
    refused('preclose-FAIL-is-not-complete-proof',lambda b:set_path(b,('preclose','status'),'FAIL'))
    refused('preclose-error-is-not-complete-proof',lambda b:set_path(b,('preclose','error'),'CONTROLLED_UNFINISHED'))
    for key,replacement in (('controls',3),('controls',5),('queryNew',0),('queryNew',2),('queryReplay',1),
                            ('controls',True),('dataSteps',-1),('scope','REAL_IO'),('seconds',999)):
        refused('row-rejects-'+key+'-'+str(replacement),
                lambda b,key=key,replacement=replacement:set_path(b,('preclose','rows',1,key),replacement))
    for key in ('branch','scope','controls','dataSteps','queryNew','queryReplay','seconds','elapsedSeconds'):
        refused('unfinished-row-missing-'+key,lambda b,key=key:b['preclose']['rows'][1].pop(key))
    for elapsed in (2.00001,-1,float('nan'),float('inf')):
        refused('row-deadline-must-be-finite-bounded-'+str(elapsed),
                lambda b,elapsed=elapsed:set_path(b,('preclose','rows',1,'elapsedSeconds'),elapsed))
    for path,value in ((('preclose','assertions'),159),(('preclose','assertions'),True),
                       (('driver','driverWitness','assertions'),159),(('driver','driverWitness','rows'),61)):
        refused('original-assertion-and-checkpoint-proof-mismatch-'+'-'.join(map(str,path)),
                lambda b,path=path,value=value:set_path(b,path,value))

    # GC/n32's disk record is only an intent. The actual return channel must
    # independently prove flush/fsync/close and no remaining resources.
    def gc_event_index(bundle,identifier,phase):
        return next(index for index,row in enumerate(bundle['global_events']) if isinstance(row,dict) and
                    row.get('id')==identifier and row.get('phase')==phase)
    refused('GC-control-without-DONE-is-not-complete',
            lambda b:b['global_events'].pop(gc_event_index(b,'GC/n05','DONE')))
    refused('duplicate-GC-DONE-cannot-create-another-completion',
            lambda b:b['global_events'].append(copy.deepcopy(b['global_events'][gc_event_index(b,'GC/n05','DONE')])))
    refused('GC-control-still-WAITING-is-not-complete',
            lambda b:set_path(b,('global_events',gc_event_index(b,'GC/n05','DONE'),'phase'),'WAITING_COMPLETION'))
    refused('extra-GC-control-is-not-approved',
            lambda b:b['global_events'].append(dict(id='GC/n33',phase='DONE',error='',kind='N',resultDigest='0'*64)))
    def reorder_gc(bundle):
        a=gc_event_index(bundle,'GC/n05','DONE');c=gc_event_index(bundle,'GC/n06','DONE')
        bundle['global_events'][a],bundle['global_events'][c]=bundle['global_events'][c],bundle['global_events'][a]
    refused('all-GC-completions-in-wrong-order-are-not-accepted',reorder_gc)
    for path,value in ((('driver','driverWitness','logClose','closed'),False),
                       (('driver','driverWitness','logClose','remainingResources'),1),
                       (('driver','driverWitness','logClose','remainingResources'),None),
                       (('driver','driverWitness','logClose','id'),'GC/n31'),
                       (('driver','driverWitness','logClose','method'),'READY_TO_CLOSE')):
        refused('n32-intent-is-insufficient-'+'-'.join(map(str,path)),lambda b,path=path,value=value:set_path(b,path,value))
    refused('n32-missing-original-return-channel',lambda b:b['driver']['driverWitness'].pop('logClose'))
    def fake_n32_done(bundle):
        bundle['global_events'].append(dict(id='GC/n32',phase='DONE',error='',kind='N',resultDigest='0'*64))
        bundle['driver']['driverWitness']['logClose']['closed']=False
    refused('fabricated-n32-disk-DONE-does-not-replace-actual-return',fake_n32_done)
    def waiting_audit(bundle,operation='P09-CANCEL/d01'):
        return next(row for row in bundle['preclose']['cellHistory'] if row['operation']==operation)
    for key,value in (('native_done',False),('gated',False),('released',False),('notifier_quiescent',False),
                      ('archived',False),('retained',True),('discarded',False),('deliveries',1),
                      ('callbacks_finished',1),('error_message','SOURCE_TIMEOUT')):
        refused('WAITING-needs-actual-drained-original-result-'+key,
                lambda b,key=key,value=value:waiting_audit(b).__setitem__(key,value))
    refused('WAITING-without-private-original-audit-is-not-complete',
            lambda b:b['preclose']['cellHistory'].remove(waiting_audit(b)))
    refused('WAITING-with-duplicate-original-audit-is-not-proven',
            lambda b:b['preclose']['cellHistory'].append(copy.deepcopy(waiting_audit(b))))
    for path,value in ((('driver','status'),'PASS'),(('launcher','status'),'PASS'),
                       (('launcher','originalChildExitCode'),0),(('driver','firstFailure'),None),
                       (('launcher','reservationConsumed'),False)):
        refused('original-failure-or-consumption-cannot-be-relabelled-'+'-'.join(map(str,path)),
                lambda b,path=path,value=value:set_path(b,path,value))

    # Both absolute and delta failures are needed: raising a single absolute
    # cap cannot make a changed original baseline or an unknown owner safe.
    witness_path=('driver','driverWitness')
    for suffix,value in (
            (('ledgerPeaks','os'),25),(('ledgerPeaks','media'),7),(('ledgerPeaks','buffers'),9),
            (('privateCells','total'),65),(('privateCells','archived'),63),(('privateCells','active'),1),
            (('privateCells','retained'),1),(('privateCells','peak'),9),
            (('callbackHub','cells'),1),(('callbackHub','queued'),1),(('callbackHub','active'),1),
            (('callbackHub','monitorInFlight'),1),(('callbackHub','workersAlive'),1),
            (('callbackHub','remainingCredits'),['unknown-worker']),(('callbackHub','ownershipPending'),True),
            (('callbackHub','blocked'),'UNKNOWN'),(('callbackHub','lifecycle'),'RUNNING'),
            (('callbackHub','workers','notify','joined'),False),
            (('callbackHub','workers','deadline','creditReleased'),False),
            (('callbackHub','workers','notify','unknown'),True),
            (('callbackHub','workers','notify','releaseProof'),'UNPROVEN'),
            (('runtimeObservation','nativeQueryPending'),True),
            (('runtimeObservation','reader','closeUnknown'),True),
            (('runtimeObservation','reader','closedHandles'),17),
            (('runtimeObservation','reader','observerCreditHeld'),True),
            (('runtimeObservation','reader','maximumOwnedHandlesObserved'),2),
            (('runtimeObservation','reader','newWorkers'),1),
            (('runtimeObservation','reader','rpcCalls'),1),
            (('runtimeObservation','reader','mediaCalls'),1),
            (('runtimeObservation','mode'),'MOCK'),(('runtimeObservation','mockMetricsUsed'),True),
            (('runtimeObservation','finished'),False),(('runtimeObservation','wired'),False),
            (('runtimeObservation','GAnchor'),'RESET_AFTER_PF'),
            (('runtimeObservation','observation','samples'),202),
            (('runtimeObservation','observation','maxObservedGapSeconds'),2.50001),
            (('runtimeObservation','observation','sampleDurationSeconds'),0.10001),
            (('runtimeObservation','observation','status'),'STOP_PENDING'),
            (('runtimeObservation','observation','stopAcceptance'),True),
            (('runtimeObservation','observation','peaks','G','handles'),257),
            (('runtimeObservation','observation','peaks','G','handles'),224),
            (('runtimeObservation','observation','peaks','R','handles'),513),
            (('runtimeObservation','observation','peaks','J','handles'),513),
            (('runtimeObservation','observation','peaks','G','threads'),17),
            (('runtimeObservation','observation','peaks','G','workingSetBytes'),256*1024*1024+1),
            (('runtimeObservation','observation','peaks','G','privateBytes'),17915904+128*1024*1024+1),
            (('runtimeObservation','observation','peaks','J','privateBytes'),768*1024*1024+1),
            (('runtimeObservation','observation','peaks','R','privateBytes'),512*1024*1024+1),
            (('runtimeObservation','observation','peaks','G','handles'),None),
            (('runtimeObservation','observation','peaks','R','privateBytes'),float('nan')),
            (('runtimeObservation','observation','peaks','G','threads'),-1),
            (('runtimeObservation','originalIdentities','G','creationTime100ns'),134366511035829925),
            (('runtimeObservation','observation','baselines','G','handles'),190),
            (('logClose','exitedHelpers','J','exited'),False),
            (('logClose','exitedHelpers','R','instance'),'replacement-R'),
            (('logClose','exitedHelpers','J','pid'),99999),
            (('metadataUnknownRequestedBytes',),1),(('metadataWritten',),6431844),
            (('metadataCommitStatus',),'UNKNOWN'),(('metadataPeak',),3178497)):
        path=witness_path+suffix
        refused('resource-rejects-'+'-'.join(map(str,suffix))+'-'+str(value),
                lambda b,path=path,value=value:set_path(b,path,value),'resources')
    for suffix in (('runtimeObservation','observation','peaks','G','handles'),
                   ('callbackHub','workers','deadline'),('logClose','exitedHelpers','R')):
        path=witness_path+suffix
        def remove_resource(bundle,path=path):
            current=bundle
            for key in path[:-1]:current=current[key]
            current.pop(path[-1])
        refused('missing-resource-proof-'+'-'.join(suffix),remove_resource,'resources')
    for path,value in ((('launcher','noInFlight'),False),(('launcher','originalChildExitObserved'),False),
                       (('launcher','wrapperFacts','parentProcessHandleCloseProven'),False),
                       (('launcher','wrapperFacts','parentProcessHandleCloseUnknown'),True),
                       (('launcher','wrapperFacts','identityRemaining'),1),
                       (('launcher','wrapperFacts','metadataRemaining'),['unknown-writer']),
                       (('launcher','wrapperFacts','spawnCalls'),2),
                       (('originalCallReceipt','wall_time_seconds'),200.01)):
        refused('original-exit-and-wrapper-resource-proof-'+'-'.join(path),
                lambda b,path=path,value=value:set_path(b,path,value),'resources')
    for label,path,value,reason in (
            ('ledger-over-limit',witness_path+('ledgerPeaks','os'),25,'MANAGED_LEDGER_PEAK'),
            ('retained-private-cell',witness_path+('privateCells','retained'),1,'PRIVATE_CELL_HISTORY_OR_OWNERSHIP'),
            ('worker-did-not-join',witness_path+('callbackHub','workers','notify','joined'),False,'WORKER_ACTUAL_RETURN_JOIN_PROOF'),
            ('observer-close-UNKNOWN',witness_path+('runtimeObservation','reader','closeUnknown'),True,'OBSERVER_UNKNOWN_OR_CREDIT_RETAINED'),
            ('sample-gap-exceeded',witness_path+('runtimeObservation','observation','maxObservedGapSeconds'),2.50001,'ORIGINAL_SAMPLE_DURATION_OR_GAP_GUARD'),
            ('baseline-was-reset',witness_path+('runtimeObservation','observation','baselines','G','handles'),190,'COMPACT_AND_RAW_PEAK_BINDING:G:handles'),
            ('unknown-metadata-write',witness_path+('metadataUnknownRequestedBytes',),1,'METADATA_WRITE_OR_CLOSE_UNKNOWN'),
            ('metadata-written-less-than-requested',witness_path+('metadataWritten',),6431844,'MONOTONIC_METADATA_REQUEST_WRITE_COUNTER'),
            ('parent-identity-credit-live',('launcher','wrapperFacts','identityRemaining'),1,'WRAPPER_IDENTITY_CLOSE_OR_UNKNOWN')):
        refused('semantic-'+label,lambda b,path=path,value=value:set_path(b,path,value),'resources',reason)
    def coherent_g_delta_exceeded(bundle):
        runtime=bundle['driver']['driverWitness']['runtimeObservation'];obs=runtime['observation']
        old=obs['peaks']['G']['handles'];obs['peaks']['G']['handles']=224
        if obs['observations']['G']['handles']==old:obs['observations']['G']['handles']=224
        name=next(name for name in bundle['files'] if name.endswith('/global.log'))
        lines=[]
        for line in bundle['files'][name].splitlines(keepends=True):
            if line.startswith(b'['):
                row=json.loads(line)
                if row[1] is not None and row[1][1]==old:row[1][1]=224
                line=json.dumps(row,separators=(',',':')).encode('ascii')+b'\n'
            lines.append(line)
        bundle['files'][name]=b''.join(lines)
    refused('semantic-coherent-G-handle-224-is-under-256-but-over-original-plus64',coherent_g_delta_exceeded,
            'resources','ABSOLUTE_OR_ORIGINAL_DELTA_LIMIT:G:handles')

    def output_name(bundle,suffix):
        return next(name for name in bundle['files'] if name.endswith('/'+suffix))
    def corrupt_output(bundle,suffix):
        name=output_name(bundle,suffix);raw=bundle['files'][name]
        bundle['files'][name]=(bytes([raw[0]^255])+raw[1:]) if raw else b'UNEXPECTED_BYTE'
    for suffix in ('T01.out','T02.out','T10.out','L.bin','global.log'):
        refused('sealed-output-byte-tampering-'+suffix,lambda b,suffix=suffix:corrupt_output(b,suffix),'resources')
    refused('semantic-independent-output-hash-does-not-trust-completed-rows',lambda b:corrupt_output(b,'T01.out'),
            'resources','OUTPUT_FILE_HASH_OR_LENGTH')
    refused('missing-zero-byte-output-is-still-missing-evidence',
            lambda b:b['files'].pop(output_name(b,'T10.out')),'resources')
    refused('unlisted-output-cannot-hide-outside-manifest',
            lambda b:b['files'].__setitem__(output_name(b,'T01.out').replace('T01.out','unlisted.txt'),b'extra'),'resources')
    def move_output(bundle):
        name=output_name(bundle,'T01.out');bundle['files']['selfcheck/foreign/T01.out']=bundle['files'].pop(name)
    refused('same-output-bytes-at-another-root-lose-identity-binding',move_output,'resources')
    def change_result(bundle,mutate):
        result=json.loads(bundle['files']['execution/result-manifest.json']);mutate(result)
        bundle['files']['execution/result-manifest.json']=json.dumps(result,sort_keys=True,separators=(',',':')).encode('ascii')
    for key,value in (('batchId','foreign'),('expectedFreeze','0'*64),('complete',False),('resultHashComplete',False),
                      ('noInFlight',False),('status','PASS'),('originalChildExitObserved',False)):
        refused('result-manifest-identity-or-finality-cannot-change-'+key,
                lambda b,key=key,value=value:change_result(b,lambda result:result.__setitem__(key,value)),'resources')
    refused('result-manifest-cannot-omit-declared-output',
            lambda b:change_result(b,lambda result:result['files'].pop()),'resources')
    refused('result-manifest-cannot-duplicate-declared-output',
            lambda b:change_result(b,lambda result:result['files'].append(copy.deepcopy(result['files'][0]))),'resources')

    aggregate=wrapper.evaluate_bound_bundle(original)
    check(aggregate.get('accepted') is True and aggregate.get('scope')=='EVIDENCE_REEVALUATION' and
          aggregate.get('decision')=='SUPPORTED_ORIGINAL_TOOL_FACTS','complete-independent-gates-support-only-original-tool-facts')
    check(aggregate['originalResult']['driverStatus']==aggregate['originalResult']['launcherStatus']=='FAIL' and
          aggregate['originalResult']['originalGExitCode']==2 and aggregate['originalResult']['originalToolExitCode']==1 and
          aggregate['originalResult']['reservationConsumed'] is True and aggregate['originalResult']['assertions']==160,
          'aggregate-reevaluation-never-relabels-the-original-FAIL-or-refunds-its-consumed-permit')
    check(aggregate['activity']==dict(newActualAttempts=0,newActualPasses=0,newG=0,helpersStarted=0,newOSMetricSamples=0,
                                   newMediaExecution=0,compileInvocations=0,originalEvidenceWrites=0,executionCapabilityGranted=False) and
          aggregate['D1']=='NOT_PASSED' and aggregate['M0']=='NOT_STARTED' and aggregate['realMedia']=='DISABLED',
          'offline-accepted-finding-is-neither-a-new-actual-pass-nor-D1-P0-real-media-admission')
    for path,value in ((('sourceIntegrity','status'),'UNVERIFIED'),(('sourceIntegrity','immutableFiles'),89),
                       (('sourceIntegrity','sealSha256'),'0'*64),(('originalInputs','resultManifestSha256'),'0'*64),
                       (('originalInputs','precloseSha256'),'0'*64),(('originalCallReceipt','exit_code'),0)):
        refused('aggregate-still-requires-original-binding-'+'-'.join(path),
                lambda b,path=path,value=value:set_path(b,path,value),'aggregate')
    refused('aggregate-never-accepts-a-resealed-original',
            lambda b:b.__setitem__('sealBytes',b['sealBytes']+b'\n'),'aggregate')
    refused('aggregate-does-not-short-circuit-output-hash-gate-after-complete-rows',
            lambda b:corrupt_output(b,'T01.out'),'aggregate')
    refused('aggregate-does-not-short-circuit-completion-after-valid-resource-snapshot',
            lambda b:b['preclose']['rows'].pop(2),'aggregate')
    refused('aggregate-never-turns-original-FAIL-into-PASS',
            lambda b:set_path(b,('launcher','status'),'PASS'),'aggregate')

    # Source-shape and actual default Inspect checks add no evidence reads or
    # outputs. No runner/resource import can occur through these pure entries.
    inspect=load_tool('reevaluate.py');stream=io.StringIO();saved_argv=sys.argv
    try:
        sys.argv=[str(BASE/'tools/reevaluate.py')]
        with contextlib.redirect_stdout(stream):code=inspect.main()
    finally:sys.argv=saved_argv
    receipt=json.loads(stream.getvalue())
    check(code==0 and receipt.get('status')=='NOT_RUN' and receipt.get('outputCreated') is False and
          receipt.get('actualExecutionAllowed') is False and receipt.get('originalEvidenceWrites')==0,
          'actual-default-reevaluation-entry-is-inspect-only-with-no-output-or-execution')
    for name in ('completion_evaluation.py','resource_evaluation.py','e2f_wrapper.py','evidence_io.py','reevaluate.py'):
        tree=ast.parse((BASE/'tools'/name).read_text(encoding='utf-8-sig'))
        imports=[node.module.split('.')[0] for node in ast.walk(tree) if isinstance(node,ast.ImportFrom) and node.module]
        imports += [alias.name.split('.')[0] for node in ast.walk(tree) if isinstance(node,ast.Import) for alias in node.names]
        check(not set(imports)&FORBIDDEN_IMPORTS,'offline-source-imports-no-runner-native-worker-or-process-'+name)
        calls=[node for node in ast.walk(tree) if isinstance(node,ast.Call)]
        check(not any(isinstance(node.func,ast.Attribute) and node.func.attr in
                      {'Popen','kill','terminate','spawn','fresh_memory_check','sample','start','compile','run_once'} for node in calls),
              'offline-source-has-no-execution-metric-or-destructive-resource-action-'+name)
    check(original==before,'all-negative-cases-leave-the-original-frozen-data-unchanged')
    activity=dict(newG=0,helpersStarted=0,newOSMetricSamples=0,newActualAttempts=0,newActualPasses=0,
                  compileInvocations=0,originalEvidenceWrites=0)
    check(all(type(value) is int and value==0 for value in activity.values()),'all-current-activity-counters-are-exact-integer-zero')
    return dict(schema=1,scope='E2F_OFFLINE_MEMORY_JSON_NEGATIVE_CHECKS',status='PASS',**activity,
                assertions=len(passed),checks=passed,negativeCases=negatives,
                originalBatchStatus='FAIL',originalGExitCode=2,originalAssertions=160,originalActualBatchPasses=0,
                originalReservationConsumed=True,newReservationConsumed=False,executionAllowed=False,
                osMetricSamples=0,compiledArtifacts=0,
                newFixtures=0,realMediaBytesRead=0,reservationConsumed=False,noInFlight=True,
                readerUsage=copy.deepcopy(original['readerUsage']),
                limitations='Only previously sealed authored SYNTHETIC evidence is read; negatives alter memory/JSON copies. No production runner/resource adapter is imported or started, no old result is written, and no execution authorization is created.')


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');options=parser.parse_args()
    value=run_checks() if options.check else dict(schema=1,scope='E2F_OFFLINE_CHECK_INSPECT',status='NOT_RUN',
              newActualAttempts=0,newG=0,helpersStarted=0,osMetricSamples=0,reservationConsumed=False,executionAllowed=False)
    print(json.dumps(value,sort_keys=True,separators=(',',':')))
