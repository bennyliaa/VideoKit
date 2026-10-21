"""E2C production cell lifetime checks with no OS/resource diagnostic.

The probe binds Engine methods without constructing Engine, Native or Channel.
Real PendingCell, SourceAuthority, Ledger, Future callbacks and the two existing
Hub workers are used. All completions are self-owned logical values. Events
only order controlled test code; no collection or resource decrease is inferred.
"""
from __future__ import annotations

import copy
import dataclasses
import threading
import time
from types import SimpleNamespace

from authority import SourceAuthority
from gcore import Ledger, Refused, Stop, compact, need
from gengine import Engine
from notifications import CompletionHub


class Probe:
    private_cell=Engine.private_cell
    compact_cells=Engine.compact_cells
    def __init__(self,label):
        self.lock=threading.RLock();self.ledger=Ledger();self.source=SourceAuthority(self.lock)
        self.cells={};self.cell_history=();self.cell_total=0;self.cell_peak=0
        self.row='probe';self.budget=SimpleNamespace(rows={'probe':{'buffers':8}})
        self.completions=CompletionHub(self.ledger,max_cells=8,callback_timeout=3).start()
        self.state=dict(task='S-LIFECYCLE-'+label,versions={},ops={},objects={},commands={})
        self.binding=self.source.reserve(self.state,'v1','consumer')
        self.state['objects']['H']=dict(self.binding,disposition='OWNED_OPEN_RETRYABLE')
        self.sequence=0
    def make(self,name=None,callback=None):
        self.sequence+=1;operation=name or 'cell-'+str(self.sequence)
        self.source.admit(self.state,self.binding,operation,self.state['objects']['H'])
        self.state['commands'][operation]={'status':'ADMITTED'}
        cell=self.private_cell(self.state,operation,self.binding,'read',buffer=True,handle_key='H')
        if callback is not None:cell.response.add_done_callback(callback)
        return cell
    def quiescent(self,cell):
        hub=self.completions
        with hub.condition:return hub.condition.wait_for(lambda:hub.cell_quiescent(cell),timeout=2)


class ExternalValue:
    """An external result identity which must not be copied into an audit."""
    def __init__(self,label):self.label=label;self.external_payload=object()


def run_checks(root=None,manifest=None):
    passed=[];closures=[];threads=[]
    def check(value,name):need(value,'LIFECYCLE_CHECK:'+name);passed.append(name)
    def refuses(action,reason,name):
        try:action()
        except Refused as error:check(str(error)==reason,name);return
        raise AssertionError('Missing refusal:'+name)
    def stops(action,reason,name):
        try:action()
        except Stop as error:check(str(error)==reason,name);return
        raise AssertionError('Missing stop:'+name)
    def immutable(audit,label):
        original=audit.as_dict();view=audit.as_dict();view['binding'].clear();view['callback_errors'].append('FORGED');view['operation']='FORGED'
        check(audit.as_dict()==original,label+'-audit-views-are-independent-copies')
        try:setattr(audit,'operation','FORGED')
        except dataclasses.FrozenInstanceError:check(True,label+'-audit-record-is-frozen')
        else:raise AssertionError('Mutable archive:'+label)
        def scalar_tuple(value):
            return value is None or type(value) in (str,int,float,bool) or (type(value) is tuple and all(scalar_tuple(item) for item in value))
        check(all(scalar_tuple(getattr(audit,field.name)) for field in dataclasses.fields(audit)),
              label+'-archive-holds-no-Future-value-exception-state-lock-or-callable')
        return original
    def detached(cell,label):
        check(cell.archived and cell.response.cell is None and cell.release is None and cell.on_drain is None and
              cell.state is None and cell.authority is None and cell.hub is None and cell.outcome is None,
              label+'-only-unneeded-tool-backreferences-are-detached')
        called=[]
        refuses(lambda:cell.response.add_done_callback(lambda future:called.append(future)),
                'CALLBACK_REGISTRATION_CLOSED',label+'-late-callback-keeps-original-refusal')
        check(not called,label+'-late-registration-does-not-run-user-code')
        refuses(cell.response.cancel,'COMPLETION_OWNED_BY_HUB',label+'-external-cancel-still-owned')
        refuses(lambda:cell.complete('DUPLICATE'),'DUPLICATE_NATIVE_COMPLETION',label+'-duplicate-native-return-is-still-refused')
        refuses(cell.gate,'GATE_DUPLICATE',label+'-duplicate-gate-is-still-refused')
    def finish(probe,label):
        # Failure cleanup completes only accepted logical test operations. It
        # never synthesizes a Native/Channel return or clears UNKNOWN flags.
        hub=probe.completions
        try:
            for cell in list(probe.cells.values()):
                if not cell.native_done:cell.complete('CONTROLLED_LOGICAL_CLEANUP')
                if not cell.gated:cell.gate(timeout=2)
            hub.drain(timeout=2);hub.close(timeout=2)
        except BaseException:
            hub.stop_when_drained();hub._cleanup_workers(time.monotonic()+2)
            raise
        facts=hub.pending()
        check(facts['closed'] and not facts['ownershipPending'] and not facts['remainingCredits'] and
              facts['workersAlive']==0 and not probe.ledger.live and probe.ledger.buffers==0,label+'-actual-Hub-workers-and-leases-are-closed')
        closures.append(dict(case=label,total=probe.cell_total,activeLogicalRecords=len(probe.cells),archived=len(probe.cell_history),
                             hubClosed=facts['closed'],workersAlive=facts['workersAlive'],buffers=probe.ledger.buffers,
                             remainingWorkerCredits=facts['remainingCredits'],blocked=facts['blocked']))

    # One allocator processes its full finite lifetime, rather than replacing
    # the owner or resetting counters after each eight-result wave.
    probe=Probe('64');first_cell=None;first_future=None;first_value=None;callbacks=[]
    try:
        for wave in range(8):
            batch=[probe.make(callback=lambda future:callbacks.append(future.result())) for _ in range(8)]
            check(len(probe.cells)==8 and probe.ledger.buffers==8 and probe.cell_total==(wave+1)*8,
                  'wave-'+str(wave)+'-eight-live-cells-share-original-owner-and-limit')
            if wave<7:
                before=(probe.cell_total,probe.cell_history,probe.ledger.buffers,len(probe.cells),probe.completions.total)
                refuses(lambda:probe.private_cell(probe.state,'ninth-'+str(wave),probe.binding,'read',buffer=True,handle_key='H'),
                        'PRIVATE_RESULT_CELL_LIMIT','wave-'+str(wave)+'-ninth-active-cell-refused')
                check(before==(probe.cell_total,probe.cell_history,probe.ledger.buffers,len(probe.cells),probe.completions.total),
                      'wave-'+str(wave)+'-refusal-does-not-lease-or-admit-another-cell')
            for index,cell in enumerate(batch):
                value=ExternalValue(str(wave)+'-'+str(index));future=cell.response
                if first_cell is None:first_cell,first_future,first_value=cell,future,value
                cell.complete(value);cell.gate(timeout=2)
                check(future.result(timeout=1) is value,'wave-'+str(wave)+'-value-'+str(index)+'-keeps-external-identity')
            probe.completions.drain(timeout=2)
            check(probe.compact_cells()==8 and not probe.cells and len(probe.cell_history)==(wave+1)*8 and probe.ledger.buffers==0,
                  'wave-'+str(wave)+'-only-actual-drain-allows-eight-immutable-archives')
            if wave==0:
                archived=probe.cell_history[0];before=(probe.cell_total,probe.cell_history,probe.ledger.buffers)
                refuses(lambda:probe.private_cell(probe.state,archived.operation,probe.binding,'read',buffer=True,handle_key='H'),
                        'SOURCE_OPERATION_REUSED','archived-operation-id-cannot-overwrite-its-audit-or-start-again')
                check(before==(probe.cell_total,probe.cell_history,probe.ledger.buffers),
                      'archived-id-refusal-keeps-original-history-and-admission-count')
        check(probe.cell_total==64 and probe.cell_peak==8 and probe.completions.total==64 and len(callbacks)==64,
              '64-total-and-original-peak-survive-all-compactions')
        before=(probe.cell_total,probe.cell_history,probe.ledger.buffers,probe.completions.total)
        refuses(lambda:probe.private_cell(probe.state,'sixty-fifth',probe.binding,'read',buffer=True,handle_key='H'),
                'PRIVATE_RESULT_CELL_HISTORY_LIMIT','sixty-fifth-cell-is-refused-after-active-table-is-empty')
        check(before==(probe.cell_total,probe.cell_history,probe.ledger.buffers,probe.completions.total) and not probe.cells,
              'history-limit-does-not-reset-total-reuse-audit-or-consume-lease')
        record=immutable(probe.cell_history[0],'64-history')
        check(first_future.result(timeout=1) is first_value and record['deliveries']==1 and record['notifier_quiescent'] is True,
              'external-Future-and-value-survive-tool-history-compaction')
        detached(first_cell,'64-history')
        saved=copy.deepcopy(first_cell.audit.as_dict());first_cell.cancel('LATE_CANCEL')
        check(first_future.result(timeout=1) is first_value and first_cell.audit.as_dict()==saved and
              first_cell.archive() is first_cell.audit and probe.compact_cells()==0,
              'late-cancel-cannot-reverse-value-rewrite-audit-or-archive-twice')
    finally:finish(probe,'64-total-capacity')

    # Resource release and cell.drained can occur before the notifier actually
    # returns. Hold precisely that window after the real publication method.
    probe=Probe('notifier');cell=probe.make();value=ExternalValue('notifier');entered=threading.Event();leave=threading.Event()
    original_publish=cell._publish_outside_locks;publish_facts={}
    def publishing():
        original_publish();entered.set();publish_facts['releasedByTest']=leave.wait(3)
    cell._publish_outside_locks=publishing
    try:
        cell.complete(value);cell.gate(timeout=2);check(entered.wait(2),'real-publisher-return-barrier-entered')
        check(cell.released and cell.drained.is_set() and cell.response.done() and not probe.completions.cell_quiescent(cell),
              'released-result-is-still-owned-by-active-notifier-stack')
        check(probe.compact_cells()==0 and len(probe.cells)==1 and not probe.cell_history and cell.response.cell is cell,
              'active-notifier-cannot-be-archived-or-detached-early')
    finally:
        leave.set();probe.completions.drain(timeout=2);cell._publish_outside_locks=original_publish
        need(probe.quiescent(cell),'NOTIFIER_QUIESCENCE_PENDING')
        foreign=[]
        worker=threading.Thread(target=lambda:foreign.append(probe.compact_cells()),name='E2C-controlled-foreign-compact')
        threads.append(worker);worker.start();worker.join(2)
        check(not worker.is_alive() and foreign==[0] and len(probe.cells)==1 and not probe.cell_history,
              'foreign-thread-cannot-compact-even-a-physically-quiescent-cell')
        check(publish_facts.get('releasedByTest') and probe.compact_cells()==1,'notifier-return-allows-one-archive')
        check(cell.response.result(timeout=1) is value,'notifier-barrier-does-not-change-external-result')
        finish(probe,'notifier-return')

    # The deadline monitor can own a local reference independently of queued or
    # active notification. No per-cell production Event is added for this test.
    probe=Probe('monitor');cell=probe.make();value=ExternalValue('monitor');entered=threading.Event();leave=threading.Event()
    original_cancel=cell.cancel;monitor_facts={}
    def cancelling(reason='CANCELLED'):
        entered.set();monitor_facts['releasedByTest']=leave.wait(3);return original_cancel(reason)
    cell.cancel=cancelling
    try:
        with probe.completions.condition:
            probe.completions.deadlines[id(cell)]=0;probe.completions.condition.notify_all()
        check(entered.wait(2),'real-deadline-monitor-inflight-barrier-entered')
        cell.complete(value);cell.gate(timeout=2);probe.completions.drain(timeout=2)
        check(cell.drained.is_set() and cell.released and probe.completions.pending()['monitorInFlight']>=1 and
              not probe.completions.cell_quiescent(cell),'monitor-local-reference-survives-native-gate-and-notifier-drain')
        check(probe.compact_cells()==0 and cell.response.cell is cell and not probe.cell_history,
              'monitor-inflight-prevents-archive-despite-empty-notification-queue')
    finally:
        leave.set();need(probe.quiescent(cell),'MONITOR_QUIESCENCE_PENDING');cell.cancel=original_cancel
        check(monitor_facts.get('releasedByTest') and probe.compact_cells()==1,'actual-monitor-return-allows-one-archive')
        check(cell.response.result(timeout=1) is value,'late-monitor-cancel-cannot-reverse-already-decided-success')
        finish(probe,'monitor-return')

    # Cancellation publishes a real error before native completion. It does not
    # release either the private buffer or the operation until the late return.
    probe=Probe('late-native');cell=probe.make();future=cell.response
    try:
        cell.cancel('CANCELLED');error=future.exception(timeout=2);probe.completions.drain(timeout=2)
        try:future.result(timeout=1)
        except Refused as actual:check(actual is error,'published-error-is-the-original-exception-object')
        traceback=error.__traceback__
        check(future.done() and not cell.native_done and probe.ledger.buffers==1 and probe.compact_cells()==0,
              'completed-cancel-Future-does-not-retire-unreturned-native-owner')
        cell.gate(timeout=2)
        check(cell.gated and probe.ledger.buffers==1 and probe.compact_cells()==0,'gate-alone-cannot-retire-unreturned-native-owner')
        cell.complete(ExternalValue('late-discarded'))
        check(probe.quiescent(cell) and probe.compact_cells()==1 and probe.ledger.buffers==0,
              'only-actual-late-completion-drains-cancelled-result-once')
        check(future.exception(timeout=1) is error and error.__traceback__ is traceback and cell.audit.as_dict()['discarded'] and
              cell.audit.as_dict()['deliveries']==0,'archive-preserves-external-error-and-existing-traceback-without-delivery')
        immutable(cell.audit,'cancelled');detached(cell,'cancelled')
        held=probe.make();held_future=held.response;held_value=ExternalValue('gate-held');held.complete(held_value)
        check(not held_future.done() and held.native_done and not held.gated and probe.compact_cells()==0 and probe.ledger.buffers==1,
              'native-return-with-private-value-does-not-archive-before-gate')
        held.gate(timeout=2);probe.completions.drain(timeout=2)
        check(probe.compact_cells()==1 and held_future.result(timeout=1) is held_value,'gate-opens-the-original-value-without-replacement-cell')
    finally:finish(probe,'native-and-gate-order')

    # Hold a real callback after Future publication; another bounded test thread
    # opens the gate so the creator can inspect the ownership window.
    probe=Probe('callback');cell=probe.make();future=cell.response;value=ExternalValue('callback')
    entered=threading.Event();leave=threading.Event();callback_facts={};gate_errors=[]
    def callback(published):
        callback_facts['sameFuture']=published is future;callback_facts['sameValue']=published.result() is value
        entered.set();callback_facts['releasedByTest']=leave.wait(3)
    def gating():
        try:cell.gate(timeout=2)
        except BaseException as error:gate_errors.append(type(error).__name__+':'+str(error))
    future.add_done_callback(callback);cell.complete(value)
    worker=threading.Thread(target=gating,name='E2C-controlled-gate');threads.append(worker);worker.start()
    try:
        check(entered.wait(2),'real-callback-has-published-Future-and-entered-barrier')
        check(future.done() and not cell.notification_done and probe.ledger.buffers==1 and probe.compact_cells()==0,
              'Future-done-does-not-archive-a-running-callback-or-release-its-buffer')
    finally:
        leave.set();worker.join(3);probe.completions.drain(timeout=2)
        check(not worker.is_alive() and not gate_errors and callback_facts==dict(sameFuture=True,sameValue=True,releasedByTest=True),
              'callback-and-original-gate-return-before-archive')
        check(probe.compact_cells()==1 and future.result(timeout=1) is value,'callback-drain-retains-external-value-after-archive')
        finish(probe,'callback-drain')

    # A callback which has actually returned with a known exception differs
    # from an unreturned/UNKNOWN publication. Its error is immutable audit data;
    # it cannot be used to clear the Hub's admission stop.
    probe=Probe('callback-error');cell=probe.make();future=cell.response;value=ExternalValue('callback-error')
    def raising_callback(published):raise RuntimeError('CONTROLLED_CALLBACK_RETURNED_ERROR')
    future.add_done_callback(raising_callback)
    try:
        cell.complete(value);cell.gate(timeout=2);probe.completions.drain(timeout=2)
        check(cell.callbacks_finished==cell.callbacks_registered==1 and cell.callback_errors==['RuntimeError'] and
              probe.ledger.buffers==0 and probe.compact_cells()==1,
              'known-returned-callback-error-can-be-archived-after-real-drain')
        check(cell.audit.as_dict()['callback_errors']==['RuntimeError'] and future.result(timeout=1) is value,
              'callback-error-audit-keeps-error-fact-and-original-success-value')
        stops(probe.completions.ensure_accepting,'CALLBACK_DRAIN_PENDING','archive-does-not-unblock-known-callback-failure')
        immutable(cell.audit,'callback-error')
    finally:finish(probe,'callback-error')

    # A successful decision queued behind another real callback is immutable
    # even when the source is cancelled before the notifier can publish it.
    probe=Probe('decision');a=probe.make();b=probe.make();a_future=a.response;b_future=b.response;value=ExternalValue('decision')
    entered=threading.Event();leave=threading.Event();gate_errors=[]
    def callback_a(future):entered.set();need(leave.wait(3),'CONTROLLED_CALLBACK_RELEASE_PENDING')
    a_future.add_done_callback(callback_a);a.cancel();a.gate();a.complete('discard-A')
    def gate_b():
        try:b.gate(timeout=2)
        except BaseException as error:gate_errors.append(type(error).__name__+':'+str(error))
    worker=threading.Thread(target=gate_b,name='E2C-controlled-decision-gate');threads.append(worker)
    try:
        check(entered.wait(2),'decision-lag-notifier-blocked-on-original-callback')
        b.complete(value);worker.start();check(b.decided.wait(2),'original-B-success-decision-is-observable-before-publication')
        probe.source.cancel(probe.state,'v1','consumer')
        check(not b_future.done() and b.outcome['error'] is None and b.outcome['value'] is value and probe.compact_cells()==0,
              'lifecycle-cancel-after-decision-does-not-reverse-queued-success-or-archive-active-notice')
    finally:
        leave.set()
        if worker.ident is not None:worker.join(3)
        probe.completions.drain(timeout=2)
        check(not worker.is_alive() and not gate_errors,'decision-lag-gate-and-callback-actually-return')
        check(probe.compact_cells()==2 and b_future.result(timeout=1) is value and str(a_future.exception(timeout=1))=='CANCELLED',
              'both-original-decisions-survive-late-lifecycle-and-archive-once')
        immutable(b.audit,'queued-success');finish(probe,'decision-and-cancel-race')

    # A failed submit has no publication proof. Even a later controlled drain
    # used solely to join the test workers must not erase that original UNKNOWN.
    probe=Probe('submit-unknown');cell=probe.make();future=cell.response;original_submit=probe.completions.submit;submit_calls=[]
    def failed_submit(accepted):submit_calls.append(accepted.operation);raise RuntimeError('CONTROLLED_SUBMIT_UNKNOWN')
    probe.completions.submit=failed_submit
    try:
        cell.complete(ExternalValue('unknown'))
        try:cell.cancel('CANCELLED')
        except RuntimeError as error:check(str(error)=='CONTROLLED_SUBMIT_UNKNOWN','submit-UNKNOWN-is-a-real-production-exception-path')
        else:raise AssertionError('Submit exception was swallowed')
        check(cell.notification_submit_error=='RuntimeError' and not cell.notification_submitted and not future.done() and
              probe.ledger.buffers==1 and probe.compact_cells()==0 and len(probe.cells)==1 and not probe.cell_history,
              'unpublished-UNKNOWN-keeps-original-live-cell-private-value-and-buffer-credit')
        stops(probe.completions.ensure_accepting,'CALLBACK_DRAIN_PENDING','submit-UNKNOWN-stably-stops-new-cell-admission')
        stops(lambda:cell.gate(timeout=.01),'CALLBACK_DRAIN_PENDING','unknown-notice-cannot-be-made-drained-by-opening-gate')
        check(len(submit_calls)==1 and probe.compact_cells()==0 and future.cell is cell,
              'compaction-neither-retries-UNKNOWN-submit-nor-detaches-external-Future')
    finally:
        probe.completions.submit=original_submit
        if not cell.gated:
            try:cell.gate(timeout=.01)
            except Stop:pass
        if not cell.notification_done:original_submit(cell)
        probe.completions.drain(timeout=2)
        check(cell.released and probe.ledger.buffers==0 and cell.notification_submit_error=='RuntimeError' and
              probe.compact_cells()==0 and len(probe.cells)==1 and not probe.cell_history and not cell.archived and
              str(future.exception(timeout=1))=='CANCELLED',
              'controlled-cleanup-proves-physical-drain-without-falsely-archiving-or-clearing-original-UNKNOWN')
        finish(probe,'submit-UNKNOWN-retained')

    check(all(not thread.is_alive() for thread in threads),'all-controlled-test-threads-actually-joined')
    report=dict(scope='E2C_PRODUCTION_CELL_LIFECYCLE_LOGIC_ONLY',status='PASS',assertions=len(passed),checks=passed,closures=closures,
                controlledThreads=len(threads),controlledThreadsJoined=True,actualOSQueries=0,diagnosticGInstances=0,actualFullRuns=0,
                helpersStarted=0,mediaBytesRead=0,fixtureBytes=0,forceGC=False,
                limitations='No Engine/Native/Channel construction or OS metrics. Future/value/exception identities are external ownership, not a reclamation claim. Submit UNKNOWN remains one logical unarchived record after separately labelled controlled physical drain; no failure flag is reset. Actual worker join and Ledger buffer return are observed, not inferred from Future.done.')
    need(len(compact(report))<=131072,'LIFECYCLE_REPORT_BOUND')
    return report
