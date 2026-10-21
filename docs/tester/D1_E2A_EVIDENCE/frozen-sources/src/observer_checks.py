"""E2A approved observer policy/baseline and wiring checks, without OS sampling.

Readers, kernel returns and writers here are self-owned controlled objects. Real
production MetricObserver/Win32MetricReader methods and Store are invoked, but no
Win32 reader constructor, native API, helper, media or test fixture is used.
"""
from __future__ import annotations

import copy, io, json, threading
from concurrent.futures import Future
from types import SimpleNamespace
from unittest.mock import patch
from gcore import BASE, Ledger, Refused, Stop, Store, compact, need
from runtime_metrics import (MetricObserver, Win32MetricReader, fresh_memory_check,
                             tool_policy_approval, MIN_AVAILABLE_PHYSICAL_BYTES)


IDENTITIES={
    'G':dict(pid=101,creationTime100ns=10001,owner='G-original'),
    'J':dict(pid=102,creationTime100ns=10002,owner='J-original'),
    'R':dict(pid=103,creationTime100ns=10003,owner='R-original')}
VALUES={
    'G':dict(threads=2,handles=24,workingSetBytes=16777216,privateBytes=12582912),
    'J':dict(threads=12,handles=64,workingSetBytes=134217728,privateBytes=100663296),
    'R':dict(threads=8,handles=48,workingSetBytes=67108864,privateBytes=50331648)}


class DictReader:
    # Intentionally not synthetic: tests enter the actual approved-tool policy
    # branch with dict data; this does not make those dictionaries OS evidence.
    synthetic=False
    def __init__(self):self.values=copy.deepcopy(VALUES);self.cycles=0;self.roles=[];self.edit=None
    def read_cycle(self,identities):
        self.cycles+=1;self.roles.append(tuple(identities));result={}
        for role,identity in identities.items():
            value=dict(self.values[role],pid=identity['pid'],creationTime100ns=identity['creationTime100ns'])
            if self.edit:self.edit(role,value)
            result[role]=value
        return result
    def facts(self):return dict(scope='DICT_READER_ONLY',cycles=self.cycles,nativeCalls=0)


def run_checks(root,manifest):
    policy=json.loads((BASE/'profiles/runtime-policy.json').read_text(encoding='utf-8-sig'))
    passed=[];observations=[]
    def check(ok,name):need(ok,'OBSERVER_CHECK:'+name);passed.append(name)
    def refuses(action,reason,name):
        try:action()
        except Refused as error:check(str(error)==reason,name);return
        raise AssertionError('Missing refusal:'+name)
    def stops(action,reason,name):
        try:action()
        except Stop as error:check(str(error)==reason,name);return
        raise AssertionError('Missing stop:'+name)
    def observer(roles=('G',),candidate=None,approval=True):
        p=copy.deepcopy(candidate or policy);reader=DictReader()
        record=tool_policy_approval(p) if approval is True else approval
        return MetricObserver({role:copy.deepcopy(IDENTITIES[role]) for role in roles},reader,p,record),reader
    def latched(obs,reader,result,name):
        check(result['status']=='STOP_PENDING' and result['stopAcceptance'] and result['reasons'],name+'-stops')
        before=reader.cycles;again=obs.sample(999)
        check(again['status']=='STOP_PENDING' and reader.cycles==before,name+'-no-retry-read')
        observations.append(dict(check=name,reasons=result['reasons'],dictCycles=before))

    check(policy['state']=='APPROVED_TOOL_STRATEGY' and policy['executionAuthorized'] is False and
          policy['limits']['G']['threads']==16 and policy['limits']['G']['deltaThreads']==12,
          'coordinator-tool-policy-has-approved-G16-plus12-without-run-authority')
    obs,reader=observer();initial=obs.sample(0)
    check(initial['status']=='OBSERVED' and initial['runtimePolicyApproved'] and
          initial['realExecutionApproved'] is False and reader.roles==[('G',)],
          'approved-tool-path-establishes-G-only-pre-PF-baseline')
    original_g=copy.deepcopy(obs.baselines['G'])
    obs.ensure_ready(('G',))
    registration=obs.register_identities({role:IDENTITIES[role] for role in ('J','R')})
    stops(obs.ensure_ready,'RUNTIME_BASELINE_PENDING','HELLO-identities-do-not-forge-baselines')
    early=obs.sample(.5)
    check(not early['sampled'] and reader.cycles==1 and obs.baselines['G']==original_g and
          registration['gBaselineReset'] is False and obs.next_due_seconds()==1,
          'helper-registration-does-not-force-cycle-or-reset-G')
    reader.values['G']['threads']=12 # planned +10, deliberately above old +8
    at_hello=obs.sample(1);obs.ensure_ready()
    check(at_hello['status']=='OBSERVED' and set(obs.baselines)=={'G','J','R'} and
          obs.baselines['G']==original_g and reader.roles[-1]==('G','J','R'),
          'planned-G-plus10-accepted-against-pre-PF-anchor-and-JR-HELLO-baselines')
    reader.values['G']['threads']=14
    check(obs.sample(2)['status']=='OBSERVED' and obs.baselines['G']==original_g,
          'G-plus12-boundary-accepted-without-rebase')
    reader.values['G']['threads']=15 # below absolute16, above original delta12
    result=obs.sample(3)
    check('METRIC_DELTA_EXCEEDED:G:threads' in result['reasons'] and obs.baselines['G']==original_g,
          'G-plus13-stops-by-original-delta-despite-absolute-being-within16')
    latched(obs,reader,result,'G-fixed-anchor-delta')

    obs,reader=observer();obs.sample(0)
    for role in ('J','R'):obs.register_identity(role,IDENTITIES[role])
    obs.sample(1);before_g=copy.deepcopy(obs.baselines['G']);before_j=copy.deepcopy(obs.baselines['J'])
    refuses(lambda:obs.register_identity('G',IDENTITIES['G']),'HELPER_IDENTITY_REGISTRATION_SCHEMA','G-cannot-be-registered-again')
    replacement=dict(IDENTITIES['J'],owner='replacement-owner',creationTime100ns=99999)
    refuses(lambda:obs.register_identity('J',replacement),'PROCESS_IDENTITY_ALREADY_REGISTERED:J','helper-owner-cannot-replace-original-instance')
    for proof in (dict(pid=999,instance='J-original',exited=True),
                  dict(pid=102,instance='wrong-owner',exited=True),
                  dict(pid=102,instance='J-original',exited=False)):
        refuses(lambda proof=proof:obs.retire_identity('J',proof),'ORIGINAL_EXIT_PROOF_MISMATCH:J','unproven-helper-exit-does-not-remove-original-'+str(proof))
    proof=dict(pid=102,instance='J-original',creationTime100ns=10002,exited=True)
    obs.retire_identity('J',proof)
    check(obs.baselines['G']==before_g and obs.baselines['J']==before_j and 'J' in obs.peaks and
          obs.original_identities['J']==IDENTITIES['J'],
          'proven-retirement-keeps-historical-baselines-peaks-and-owner')
    next_sample=obs.sample(2)
    check(next_sample['status']=='OBSERVED' and reader.roles[-1]==('G','R') and 'J' in next_sample['retired'],
          'proven-exited-helper-is-not-queried-or-falsely-treated-as-live')
    refuses(lambda:obs.register_identity('J',replacement),'PROCESS_IDENTITY_ALREADY_REGISTERED:J','retired-helper-cannot-be-reused-or-rebased')
    refuses(lambda:obs.retire_identity('G',dict(pid=101,instance='G-original',exited=True)),'G_OBSERVATION_REQUIRED_UNTIL_FINISH','G-remains-observed-until-final-finish')
    finished=obs.finish();before=reader.cycles
    check(finished['observationFinished'] and obs.sample(3)['status']=='NOT_ADMITTED' and reader.cycles==before and
          obs.baselines['G']==before_g,'finish-stops-observation-without-claiming-G-exit-or-rebase')

    for approval in (None,False,{'approved':True}):
        denied,reader=observer(approval=approval);result=denied.sample(0)
        check(result['status']=='NOT_ADMITTED' and reader.cycles==0,'policy-approval-not-minted-by-'+str(approval))
    for field,value in (('maxSamples',202),('intervalSeconds',.5),('minimumAvailablePhysicalBytes',0),('executionAuthorized',True)):
        candidate=copy.deepcopy(policy);candidate[field]=value
        denied,reader=observer(candidate=candidate)
        check(denied.sample(0)['status']=='NOT_ADMITTED' and reader.cycles==0,
              'even-rebound-policy-record-cannot-change-approved-'+field)
    candidate=copy.deepcopy(policy);candidate['limits']['G']['deltaThreads']=13
    denied,reader=observer(candidate=candidate)
    check(denied.sample(0)['status']=='NOT_ADMITTED' and reader.cycles==0,'policy-record-cannot-increase-G-delta')

    for field in ('threads','handles','workingSetBytes','privateBytes'):
        obs,reader=observer()
        reader.edit=lambda role,value,field=field:value.pop(field)
        latched(obs,reader,obs.sample(0),'missing-'+field)
    for label,value in (('none',None),('nan',float('nan')),('negative',-1),('bool',True)):
        obs,reader=observer();reader.values['G']['handles']=value
        latched(obs,reader,obs.sample(0),'invalid-handles-'+label)
    for field in ('pid','creationTime100ns'):
        obs,reader=observer()
        reader.edit=lambda role,value,field=field:value.update({field:value[field]+1})
        latched(obs,reader,obs.sample(0),'original-identity-change-'+field)
    obs,reader=observer(('G','J'));obs.identities['J']['pid']=obs.identities['G']['pid']
    result=obs.sample(0)
    check(result['status']=='STOP_PENDING' and reader.cycles==0 and 'PROCESS_IDENTITY_ROLE_ALIAS' in result['reasons'],
          'same-PID-cannot-be-used-as-two-original-role-anchors')
    obs,reader=observer();reader.values['G']['handles']=257
    latched(obs,reader,obs.sample(0),'absolute-handles')
    obs,reader=observer();obs.sample(0)
    before=reader.cycles;result=obs.sample(3)
    check(reader.cycles==before,'sampling-gap-stops-before-OS-query')
    latched(obs,reader,result,'gap-exceeded')
    obs,reader=observer()
    okay=True
    for tick in range(201):okay=okay and obs.sample(tick)['status']=='OBSERVED'
    check(okay and reader.cycles==201,'201-bounded-cycles-accepted-without-background-thread')
    latched(obs,reader,obs.sample(201),'sample-credit-exhaustion')
    obs,reader=observer()
    with patch('runtime_metrics.time.monotonic',side_effect=[100.,100.2]):result=obs.sample(0)
    check('SAMPLE_DEADLINE_EXCEEDED_AFTER_RETURN' in result['reasons'],'return-deadline-is-checked-after-call-without-force-interrupt')
    latched(obs,reader,result,'sampling-return-deadline')

    for available,observed,now,expected in ((2147483648,10,10,'MEMORY_READY'),
                                           (2147483647,10,10,'STOP_PENDING'),
                                           (2147483648,10,10.2,'STOP_PENDING'),
                                           (2147483648,11,10,'STOP_PENDING')):
        with patch('runtime_metrics.time.monotonic',return_value=100):
            result=fresh_memory_check(lambda:dict(availablePhysicalBytes=available,observedAtMonotonic=observed),now_seconds=now)
        check(result['status']==expected and result['minimumAvailablePhysicalBytes']==MIN_AVAILABLE_PHYSICAL_BYTES and
              result['realExecutionApproved'] is False,'fresh-memory-floor-age-and-time-'+str((available,observed,now)))

    native_results=_native_interface_checks(check,stops)
    wiring_results=_wiring_checks(root,policy,check,stops,refuses)
    report=dict(scope='E2A_APPROVED_OBSERVER_POLICY_AND_MOCK_INTERFACES_ONLY',status='PASS',assertions=len(passed),checks=passed,
                observations=observations,nativeInterfaceMocks=native_results,wiring=wiring_results,
                actualOSQueries=0,mediaBytesRead=0,newHelpers=0,fixtureBytes=0,metadataBytesCreated=0,
                limitations='Controlled dict/kernel/writer returns only; no Win32 constructor or actual OS handles. Mock UNKNOWN credit remains labelled, not falsely proven released. Real original-process/FFM/IO evidence belongs to separate centrally run self-owned checks; no real execution capability is minted.')
    need(len(compact(report))<=131072,'OBSERVER_REPORT_BOUND')
    return report


def _probe(ledger,kernel=None):
    probe=object.__new__(Win32MetricReader)
    probe.ledger=ledger;probe.slot='self-owned-mock-observer';probe.maximum=16384
    probe.reserved=False;probe.close_unknown=False;probe.active_handle=None
    probe.cycles=0;probe.identity_queries=0;probe.borrowed_identity_queries=0
    probe.opened=0;probe.closed=0;probe.peak_owned_handles=0;probe.last_thread_entries=0
    probe._cycle_lock=threading.Lock();probe.k=kernel
    return probe


def _native_interface_checks(check,stops):
    ledger=Ledger()
    for index in range(24):ledger.acquire('full-'+str(index),'self-owned','pipe')
    probe=_probe(ledger);queries=[]
    probe._threads=lambda identities:queries.append('threads')
    stops(lambda:probe.read_cycle({'G':IDENTITIES['G']}),'OBSERVER_CREDIT_UNAVAILABLE','full-24-credit-ledger-prevents-any-observer-native-call')
    check(not queries and not probe.reserved and len(ledger.live)==24,'capacity-failure-cannot-expand-24-or-reserve-hidden-handle')
    duplicate_ledger=Ledger();duplicate=_probe(duplicate_ledger)
    duplicate_ledger.acquire(duplicate.slot,'G','observer');duplicate_queries=[]
    duplicate._threads=lambda identities:duplicate_queries.append('threads')
    stops(lambda:duplicate.read_cycle({'G':IDENTITIES['G']}),'OBSERVER_CREDIT_UNAVAILABLE','duplicate-reservation-stops-before-native-query')
    check(duplicate.slot in duplicate_ledger.live and not duplicate_queries and not duplicate_ledger.audit,
          'reservation-error-cannot-refund-a-credit-that-already-existed')

    class Kernel:
        def __init__(self,pid=102,close_ok=True):self.pid=pid;self.close_ok=close_ok;self.calls=[]
        def OpenProcess(self,*args):self.calls.append('OpenProcess');return 888
        def GetProcessId(self,handle):self.calls.append('GetProcessId');return self.pid
        def GetProcessTimes(self,handle,created,*args):
            self.calls.append('GetProcessTimes');created._obj.dwLowDateTime=10002;created._obj.dwHighDateTime=0;return True
        def WaitForSingleObject(self,handle,timeout):self.calls.append('WaitForSingleObject');return 258
        def CloseHandle(self,handle):self.calls.append('CloseHandle');return self.close_ok
    ledger=Ledger();kernel=Kernel();borrowed=_probe(ledger,kernel)
    identity=borrowed.capture_identity(102,'J-original',process_handle=777)
    check(identity==IDENTITIES['J'] and kernel.calls==['GetProcessId','GetProcessTimes','WaitForSingleObject'] and
          not ledger.live and borrowed.opened==0 and borrowed.closed==0 and borrowed.borrowed_identity_queries==1,
          'original-process-handle-borrowed-without-open-dup-or-close')
    ledger=Ledger();kernel=Kernel(pid=999);wrong=_probe(ledger,kernel)
    stops(lambda:wrong.capture_identity(102,'J-original',process_handle=777),'ORIGINAL_PROCESS_HANDLE_IDENTITY_CHANGED','borrowed-handle-PID-mismatch-cannot-anchor-reused-PID')
    check(kernel.calls==['GetProcessId'] and not ledger.live and wrong.opened==0 and wrong.closed==0,
          'borrowed-identity-mismatch-does-not-close-owner-handle-or-leak-credit')
    ledger=Ledger();kernel=Kernel(close_ok=False);unknown=_probe(ledger,kernel)
    ledger.acquire(unknown.slot,'G','observer');unknown.reserved=True;unknown._own(object())
    stops(unknown._close,'OBSERVER_CLOSE_UNKNOWN','controlled-close-UNKNOWN-retains-original-private-owner')
    before=list(kernel.calls)
    stops(lambda:unknown.read_cycle({'G':IDENTITIES['G']}),'OBSERVER_OWNERSHIP_PENDING','UNKNOWN-close-blocks-new-query-without-retry')
    check(unknown.active_handle is not None and unknown.reserved and unknown.slot in ledger.live and
          unknown.closed==0 and kernel.calls==before,'UNKNOWN-logical-credit-is-not-falsely-returned-or-reclosed')
    return dict(scope='CONTROLLED_KERNEL_RETURN_INTERFACES_NOT_OS',borrowedOpens=0,borrowedCloses=0,
                unknownMockCreditsRetained=1,actualHandlesAllocated=0,actualNativeCalls=0)


def _wiring_checks(root,policy,check,stops,refuses):
    from runtime_wiring import RuntimeSampler
    from pathlib import Path
    ledger=Ledger();store=Store(Path(root)/'memory-only-wiring',ledger);store.log=io.BytesIO()
    calls=[]
    engine=SimpleNamespace(ledger=ledger,store=store,lock=threading.RLock(),pending={},stopping=False,
                           remaining=lambda:10)
    def invoke(fn,timeout=None,observe=True):
        calls.append(dict(timeout=timeout,observe=observe));return fn()
    engine.io_call=invoke
    sampler=RuntimeSampler(engine);reader=DictReader()
    sampler.reader=reader;sampler.observer=MetricObserver({'G':IDENTITIES['G']},reader,policy,tool_policy_approval(policy))
    sampler.started=True;sampler.origin=100
    with patch('runtime_wiring.time.monotonic',return_value=100):sampler.step()
    check(reader.cycles==1 and len(sampler.pending_lines)==1 and not store.metric_header,
          'pre-PF-G-sample-is-buffered-until-original-log-is-open')
    sampler.attach()
    check(store.metric_header and store.metric_rows==1 and store.metric_bytes<=1024+128 and
          store.requested==store.written and all(call['observe'] is False and call['timeout']<=.1 for call in calls),
          'wiring-uses-existing-IO-entry-with-recursion-disabled-and-exact-write')
    before=len(calls)
    with engine.lock:sampler.step()
    check(len(calls)==before,'holding-source-lock-never-synchronously-waits-on-observer-worker')
    worker_done=threading.Event()
    def worker():
        try:sampler.step()
        finally:worker_done.set()
    thread=threading.Thread(target=worker,name='E2A-controlled-native-worker-probe');thread.start()
    need(worker_done.wait(1),'CONTROLLED_OBSERVER_WORKER_PENDING');thread.join(1)
    check(not thread.is_alive() and len(calls)==before,'native-worker-cannot-submit-and-wait-on-its-own-pool')
    store.metric_rows=201;before_written=store.written
    refuses(lambda:store.metric_record(b'[0,null,null,null]\n'),'BLOCKED_OBSERVER_LOG_CREDIT','201-record-credit-prevents-extra-metric-write')
    check(store.written==before_written,'exhausted-metric-capacity-does-not-write')
    store.metric_rows=1;store.global_event_bytes=104320
    refuses(lambda:store.event('P01-N1',{'x':1}),'BLOCKED_OBSERVER_LOG_CREDIT','event-credit-cannot-consume-approved-metric-reservation')

    class ShortWriter(io.BytesIO):
        def write(self,data):return super().write(data[:max(0,len(data)-1)])
    bad_store=Store(Path(root)/'memory-only-short',Ledger());bad_store.log=ShortWriter()
    bad_engine=SimpleNamespace(ledger=bad_store.ledger,store=bad_store,lock=threading.RLock(),pending={},stopping=False,remaining=lambda:10)
    bad_calls=[]
    def bad_invoke(fn,timeout=None,observe=True):bad_calls.append(1);return fn()
    bad_engine.io_call=bad_invoke;bad_sampler=RuntimeSampler(bad_engine);bad_reader=DictReader()
    bad_sampler.reader=bad_reader;bad_sampler.observer=MetricObserver({'G':IDENTITIES['G']},bad_reader,policy,tool_policy_approval(policy))
    bad_sampler.started=True;bad_sampler.origin=100
    stops(bad_sampler.attach,'METADATA_SHORT_OR_INVALID_WRITE_NO_REPAIR','observer-header-short-write-poisons-existing-Store')
    check(bad_store.commit_status=='UNKNOWN' and not bad_store.metric_header and bad_store.metric_bytes==0 and
          bad_store.written<bad_store.requested,'short-header-not-falsely-committed-or-repaired')
    before=bad_reader.cycles
    with patch('runtime_wiring.time.monotonic',return_value=100):
        stops(bad_sampler.step,'METADATA_COMMIT_UNKNOWN_NO_NEW_EFFECT','poisoned-metric-log-stops-before-another-process-query')
    check(bad_reader.cycles==before and bad_store.native['write']==1,
          'shortwrite-stops-next-observer-read-and-write')
    pending_future=Future();pending_invocations=[]
    pending_engine=SimpleNamespace(ledger=Ledger(),store=store,lock=threading.RLock(),pending={'probe':pending_future},
                                   stopping=False,remaining=lambda:10,row=None)
    def timed_out(fn,timeout=None,observe=True):
        pending_invocations.append(dict(timeout=timeout,observe=observe));raise Stop('NATIVE_PENDING_DEADLINE')
    pending_engine.io_call=timed_out;pending_sampler=RuntimeSampler(pending_engine)
    query_calls=[]
    stops(lambda:pending_sampler._invoke(lambda:query_calls.append('query')),'NATIVE_PENDING_DEADLINE',
          'existing-IO-pool-timeout-is-an-explicit-pending-result')
    check(pending_sampler.pending_query and pending_engine.stopping and not pending_future.done() and not query_calls and
          pending_invocations==[dict(timeout=.1,observe=False)],
          'waiting-deadline-does-not-fabricate-native-return-or-release-future')
    pending_future.set_result('CONTROLLED_FUTURE_RETURN_NOT_NATIVE')
    check(pending_future.done() and pending_engine.stopping and pending_sampler.pending_query,
          'later-controlled-return-does-not-erase-original-pending-witness-or-reopen-acceptance')
    return dict(scope='REAL_STORE_WITH_SELF_OWNED_MEMORY_WRITERS_AND_DICT_READER',
                normalMetricRows=1,controlledWorkerJoined=not thread.is_alive(),actualOSQueries=0,
                diskBytesWritten=0,shortWriteStatus=bad_store.commit_status,pendingWitnessRetained=True)
