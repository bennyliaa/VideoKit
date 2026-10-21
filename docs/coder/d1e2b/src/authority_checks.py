"""E2 regression checks of the production authority/cell code.

These checks use no Native, Channel, helper process, filesystem writer, or media.
The delegate counters below count eligibility after the real authority accepts an
operation. They are explicitly logical counters, not Windows/JVM I/O evidence.
The separately invoked all-61 integration exercises the same production classes
with the real J/R bindings.
"""
from __future__ import annotations

import copy
import threading
from concurrent.futures import TimeoutError as FutureTimeout

from authority import (
    PendingCell,
    SourceAuthority,
    SourceBridge,
    capture_ready_request,
    complete_source_response,
    validate_ready_request,
)
from gcore import Refused, compact, need, sha


def run_checks(root, manifest):
    """Use one bounded production completion hub and observe its actual shutdown."""
    from notifications import CompletionHub
    hub = CompletionHub()
    hub.start()
    try:
        report = _run_checks(root, manifest, hub)
    finally:
        # A pending callback or notification is an error, never a successful
        # regression result. close() must observe the fixed workers actually exit.
        hub.close()
    report['completionHubClosed'] = True
    return report


def _run_checks(root, manifest, hub):
    """Return bounded evidence; the central runner persists the returned value."""
    passed = []
    observations = []
    created_cells = []

    def check(condition, name):
        need(condition, 'AUTHORITY_CHECK:' + name)
        passed.append(name)

    def rejects(action, reason, name):
        try:
            action()
        except Refused as error:
            check(str(error) == reason, name)
            return
        raise AssertionError('Missing refusal: ' + name + '/' + reason)

    def source():
        state = dict(task='S-authority-check', versions={}, ops={}, objects={},
                     recovered=False, sourceDone=False)
        authority = SourceAuthority()
        a = authority.reserve(state, 'v1', 'a')
        b = authority.reserve(state, 'v1', 'b')
        handle = dict(a, key='H-A', disposition='OWNED_OPEN_RETRYABLE')
        return authority, state, a, b, handle

    # End(A) is tested in the exact nonterminal state that the old checks missed:
    # B remains reserved and unsealed, so the source as a whole is still active.
    authority, state, a, b, handle_a = source()
    b_before = copy.deepcopy(state['versions']['v1']['consumers']['b'])
    authority.end(state, 'v1', 'a')
    check(not state['versions']['v1']['sealed'], 'ended-A-version-still-unsealed')
    calls = {'logicalDelegateEligibility': 0}

    def accepted(binding, operation, handle=None):
        op = authority.admit(state, binding, operation, handle)
        calls['logicalDelegateEligibility'] += 1
        return op

    before = copy.deepcopy(state['ops'])
    rejects(lambda: accepted(a, 'open'), 'SESSION_RELEASED',
            'end-A-blocks-new-open-with-B-active')
    rejects(lambda: accepted(a, 'read', handle_a), 'SESSION_RELEASED',
            'end-A-blocks-new-read-with-B-active')
    check(calls['logicalDelegateEligibility'] == 0 and state['ops'] == before,
          'ended-A-refusals-create-no-operation-or-delegate-eligibility')
    check(state['versions']['v1']['consumers']['b'] == b_before,
          'end-A-refusals-preserve-B-exactly')
    op_b = accepted(b, 'open')
    authority.mark_native(state, 'open')
    authority.drain(state, 'open')
    check(calls['logicalDelegateEligibility'] == 1,
          'other-active-consumer-still-admitted')

    authority, state, a, b, handle_a = source()
    before = copy.deepcopy(state)
    rejects(lambda: authority.admit(state, b, 'read', handle_a),
            'SOURCE_BINDING_MISMATCH', 'B-cannot-read-A-handle')
    check(state == before, 'cross-consumer-handle-refusal-is-side-effect-free')
    for field, value in [('task', 'other-task'), ('version', 'other-version'),
                         ('generation', str(a['generation']) + '-old')]:
        bad = dict(a)
        bad[field] = value
        rejects(lambda bad=bad: authority.admit(state, bad, 'read', handle_a),
                'SOURCE_BINDING_MISMATCH', 'binding-refuses-wrong-' + field)
    for field, value in [('task', 'other-task'), ('version', 'other-version'),
                         ('consumer', 'b'), ('generation', a['generation'] + '-old')]:
        bad_handle = dict(handle_a)
        bad_handle[field] = value
        rejects(lambda bad_handle=bad_handle: authority.admit(state, a, 'read', bad_handle),
                'SOURCE_BINDING_MISMATCH', 'handle-refuses-wrong-' + field)
    for disposition in ('CLOSED_PROVEN', 'UNKNOWN', 'IN_FLIGHT'):
        closed_handle = dict(handle_a, disposition=disposition)
        before_ops = copy.deepcopy(state['ops'])
        rejects(lambda closed_handle=closed_handle: authority.admit(state, a, 'read', closed_handle),
                'OBJECT_NOT_OPEN', 'read-refuses-handle-disposition-' + disposition)
        check(state['ops'] == before_ops,
              'not-open-handle-adds-no-operation-' + disposition)

    # Both orders of a contested atomic point are exercised using real threads.
    # A thread starts while the authority lock is held; the chosen first action
    # completes under that same lock before the contender can observe the state.
    # No sleep, scheduler probability, or test boolean decides the outcome.
    for lifecycle in ('end', 'cancel'):
        for operation in ('open', 'read'):
            for first in ('lifecycle', 'admission'):
                authority, state, a, b, handle_a = source()
                before_b = copy.deepcopy(state['versions']['v1']['consumers']['b'])
                waiting = threading.Event()
                outcome = {}
                lock = authority.lock

                def admit_work():
                    waiting.set()
                    try:
                        outcome['operation'] = authority.admit(
                            state, a, operation, handle_a if operation == 'read' else None)
                        outcome['logicalDelegateEligibility'] = 1
                    except Refused as error:
                        outcome['error'] = str(error)
                        outcome['logicalDelegateEligibility'] = 0

                def lifecycle_work():
                    waiting.set()
                    getattr(authority, lifecycle)(state, 'v1', 'a')
                    outcome['lifecycleReturned'] = True

                with lock:
                    work = admit_work if first == 'lifecycle' else lifecycle_work
                    worker = threading.Thread(target=work,
                                              name='E2B-authority-' + lifecycle + '-' + operation)
                    worker.start()
                    need(waiting.wait(.5), 'AUTHORITY_TEST_THREAD_START')
                    if first == 'lifecycle':
                        getattr(authority, lifecycle)(state, 'v1', 'a')
                    else:
                        outcome['operation'] = authority.admit(
                            state, a, operation, handle_a if operation == 'read' else None)
                        outcome['logicalDelegateEligibility'] = 1
                worker.join(.5)
                check(not worker.is_alive(), lifecycle + '-' + operation + '-' + first + '-thread-drained')
                if first == 'lifecycle':
                    check(outcome.get('error') == 'SESSION_RELEASED' and
                          outcome['logicalDelegateEligibility'] == 0,
                          lifecycle + '-wins-' + operation + '-native-ineligible')
                else:
                    op = outcome['operation']
                    check(outcome.get('lifecycleReturned') and not op['done'],
                          operation + '-admitted-before-' + lifecycle + '-remains-in-flight')
                    authority.mark_native(state, operation)
                    authority.drain(state, operation)
                    check(op['done'] and outcome['logicalDelegateEligibility'] == 1,
                          operation + '-before-' + lifecycle + '-only-drains-original-admission')
                rejects(lambda: authority.admit(state, a, operation,
                                                handle_a if operation == 'read' else None),
                        'SESSION_RELEASED', lifecycle + '-' + operation + '-' + first + '-no-new-admission')
                check(state['versions']['v1']['consumers']['b'] == before_b,
                      lifecycle + '-' + operation + '-' + first + '-B-unchanged')
                observations.append(dict(lifecycle=lifecycle, operation=operation,
                                         first=first, logicalDelegateEligibility=outcome['logicalDelegateEligibility']))

    # This calls the production zero-length bridge, including its real authority
    # gate. A callback is supplied so any accidental provider invocation is fatal.
    authority, state, a, b, handle_a = source()
    zero_calls = {'delegate': 0}

    def forbidden_zero_delegate(*args, **kwargs):
        zero_calls['delegate'] += 1
        raise AssertionError('Zero bridge called delegate')

    zero = SourceBridge(authority).read_zero(state, a, handle_a, forbidden_zero_delegate)
    check(zero == {'n': 0, 'bytes': '', 'nativeReads': 0} and zero_calls['delegate'] == 0,
          'production-zero-bridge-returns-empty-with-zero-delegate')
    authority.end(state, 'v1', 'a')
    rejects(lambda: SourceBridge(authority).read_zero(state, a, handle_a,
                                                    forbidden_zero_delegate),
            'SESSION_RELEASED', 'zero-bridge-also-obeys-ended-reservation')
    check(zero_calls['delegate'] == 0, 'zero-bridge-refusal-also-has-zero-delegate')

    def cell_case(name, timeout=None):
        slot = {'privateBuffer': bytearray(b'E2B-private-result'), 'releases': 0, 'drains': 0}

        def release(*args, **kwargs):
            need(slot['privateBuffer'] is not None, 'PRIVATE_BUFFER_DOUBLE_RELEASE')
            slot['privateBuffer'] = None
            slot['releases'] += 1

        def drained(*args, **kwargs):
            slot['drains'] += 1

        binding = dict(task='S-cell', version='v1', consumer='a', generation='g1')
        cell = PendingCell(name, binding, release, on_drain=drained, timeout=timeout, hub=hub)
        created_cells.append(cell)
        return cell, slot

    cell, slot = cell_case('held-read-success')
    private = {'n': 7, 'sha': sha(b'private'), 'bytes': 'cHJpdmF0ZQ=='}
    cell.complete(private)
    check(cell.native_done and cell.retained and not cell.response.done(),
          'native-returned-read-remains-private-before-gate')
    try:
        cell.response.result(timeout=.01)
    except FutureTimeout:
        check(True, 'actual-response-future-still-waits-before-gate')
    else:
        raise AssertionError('Held read delivered before gate')
    check(slot['privateBuffer'] is not None and slot['releases'] == 0,
          'private-result-buffer-not-released-or-reused-while-held')
    cell.gate()
    check(cell.response.result(timeout=.2) == private and cell.deliveries == 1,
          'gate-delivers-actual-result-exactly-once')
    check(cell.released and slot['releases'] == 1 and slot['drains'] == 1,
          'successful-gate-drains-private-slot-once')
    rejects(cell.gate, 'GATE_DUPLICATE', 'duplicate-gate-refused')
    check(slot['releases'] == 1 and cell.deliveries == 1,
          'replayed-gate-cannot-redeliver-or-double-release')

    for when in ('before-native', 'after-native'):
        cell, slot = cell_case('cancel-' + when)
        late_handle = {'object': 'private-late-H', 'length': 32}
        if when == 'after-native':
            cell.complete(late_handle)
        cell.cancel()
        rejects(lambda: cell.response.result(timeout=.2), 'CANCELLED',
                'cancel-' + when + '-completes-real-response')
        check(cell.retained and slot['privateBuffer'] is not None and slot['releases'] == 0,
              'cancel-' + when + '-retains-private-resource-before-gate')
        if when == 'before-native':
            cell.gate()
            check(not cell.released and slot['releases'] == 0,
                  'cancel-gate-before-native-does-not-falsely-release')
            cell.complete(late_handle)
            hub.drain(timeout=.2)
        else:
            cell.gate()
        rejects(lambda: cell.response.result(timeout=.2), 'CANCELLED',
                'late-H-' + when + '-never-delivered')
        check(cell.discarded and cell.deliveries == 0 and cell.released and
              slot['releases'] == 1 and slot['drains'] == 1,
              'cancel-' + when + '-late-result-only-discards-and-drains-once')

    cell, slot = cell_case('deadline-read', timeout=.025)
    cell.complete({'n': 7, 'sha': sha(b'private')})
    rejects(lambda: cell.response.result(timeout=.5), 'SOURCE_TIMEOUT',
            'real-deadline-completes-actual-response-with-SOURCE_TIMEOUT')
    check(cell.native_done and cell.retained and not cell.released and
          slot['privateBuffer'] is not None and slot['releases'] == 0,
          'response-timeout-retains-returned-native-result-and-buffer')
    cell.gate()
    check(cell.discarded and cell.deliveries == 0 and cell.released and
          slot['releases'] == 1 and slot['drains'] == 1,
          'deadline-late-gate-only-discards-and-drains')

    # Ordinary calls use the same production completion function as Engine. The
    # prior tests exercise explicitly held cells; these cover the ordinary
    # auto-gate path after a native operation was already accepted. In particular
    # end/cancel must not be revalidated as a new admission and must not allow the
    # late native value to become a successful consumer response.
    def ordinary(operation, lifecycle=None, invalid=False):
        authority, state, a, b, handle_a = source()
        operation_id = 'ordinary-' + operation
        live_op = authority.admit(state, a, operation_id,
                                  handle_a if operation == 'read' else None)
        slot = {'buffer': bytearray(b'ordinary-private'), 'releases': 0, 'drains': 0}

        def release():
            need(slot['buffer'] is not None, 'ORDINARY_PRIVATE_BUFFER_DOUBLE_RELEASE')
            slot['buffer'] = None
            slot['releases'] += 1

        def on_drain():
            authority.drain(state, operation_id)
            slot['drains'] += 1

        cell = PendingCell(operation_id, a, release, on_drain=on_drain,
                           hub=hub, authority=authority, state=state)
        created_cells.append(cell)
        other_before = copy.deepcopy(state['versions']['v1']['consumers']['b'])
        if lifecycle:
            getattr(authority, lifecycle)(state, 'v1', 'a')
        if invalid:
            cell.cancel('INVALID_PROVIDER_RESULT')
        check(not live_op['done'] and not live_op['nativeReturned'] and
              cell.retained and slot['releases'] == 0,
              operation_id + '-' + str(lifecycle) + '-' + str(invalid) + '-accepted-not-released-before-native')
        value = {'object': 'private-ordinary-H', 'length': 32} if operation == 'open' else {'n': 7, 'sha': sha(b'private')}
        complete = lambda: complete_source_response(authority, state, operation_id,
                                                     cell, value, hold=False)
        label = operation_id + '-' + str(lifecycle) + '-' + str(invalid)
        if lifecycle or invalid:
            reason = 'INVALID_PROVIDER_RESULT' if invalid else 'CANCELLED'
            rejects(complete, reason, label + '-ordinary-return-is-concrete-error')
            rejects(lambda: cell.response.result(timeout=.2), reason,
                    label + '-response-remains-error-after-native-return')
            check(cell.discarded and cell.deliveries == 0,
                  label + '-ordinary-late-value-never-delivered')
        else:
            actual = complete()
            check(actual == value and cell.response.result(timeout=.2) == value and
                  cell.deliveries == 1 and not cell.discarded,
                  label + '-ordinary-success-returns-actual-value')
        check(live_op['nativeReturned'] and live_op['done'] and cell.released and
              not cell.retained and slot['buffer'] is None and
              slot['releases'] == 1 and slot['drains'] == 1,
              label + '-original-admission-drains-and-releases-exactly-once')
        check(state['versions']['v1']['consumers']['b'] == other_before,
              label + '-other-consumer-unchanged')

    for operation in ('open', 'read'):
        ordinary(operation)
        for lifecycle in ('end', 'cancel'):
            ordinary(operation, lifecycle=lifecycle)
    ordinary('read', invalid=True)

    # Exercise Engine's actual private-cell allocator and the real Ledger lease.
    # This is an unbound production method call on just its required state; no
    # Engine constructor, Native object, transport, fixture, or helper is made.
    from types import SimpleNamespace
    from gcore import Ledger
    from gengine import Engine

    authority, state, a, b, handle_a = source()
    state['commands'] = {
        name: {'status': 'ADMITTED'}
        for name in ('lease-first', 'lease-refused', 'lease-after-drain')
    }
    probe = SimpleNamespace(lock=authority.lock, source=authority, cells={}, completions=hub,
                            cell_peak=0, ledger=Ledger(),
                            budget=SimpleNamespace(rows={'probe': {'buffers': 1}}),
                            row='probe')
    first_op = authority.admit(state, a, 'lease-first', handle_a)
    first_cell = Engine.private_cell(probe, state, 'lease-first', a, 'read', buffer=True)
    authority.mark_native(state, 'lease-first')
    first_cell.complete({'n': 7, 'sha': sha(b'private')})
    first_cell.cancel()
    rejects(lambda: first_cell.response.result(timeout=.2), 'CANCELLED',
            'real-ledger-cell-cancel-completes-response')
    check(probe.ledger.buffers == 1 and first_cell.retained and
          not first_cell.released and not first_op['done'],
          'real-ledger-buffer-retained-after-response-cancel')
    before_cells = dict(probe.cells)
    before_state = copy.deepcopy(state)
    rejects(lambda: Engine.private_cell(probe, state, 'lease-refused', a,
                                       'read', buffer=True),
            'BUFFER_LIMIT', 'real-private-cell-cannot-reuse-cancelled-live-buffer')
    check(probe.cells == before_cells and state == before_state and
          probe.ledger.buffers == 1 and probe.ledger.buffer_peak == 1,
          'real-buffer-refusal-mutates-no-state-and-reuses-no-private-slot')
    # A trusted logical owner-exit fact may return J's reference but cannot
    # declare G's still-retained private result complete. No process is created.
    from phases import Cleanup
    resource=dict(handle_a,actor='J',role='H',owner='logical-J')
    state['objects']['logical-H']=resource;probe.ledger.acquire('logical-H','logical-J','media')
    probe.states={state['task']:state};probe.channels={'J':SimpleNamespace(owner='logical-J')}
    notice=SimpleNamespace(e=probe,proofs={'J':{'exited':True,'instance':'logical-J'}},
                           invoke=lambda label,action,target:action())
    observed=Cleanup.owner_notice(notice,'J','source')
    check(observed['references']==1 and resource['disposition']=='RELEASED_BY_OWNER_EXIT' and 'logical-H' not in probe.ledger.live,
          'logical-owner-fact-returns-only-its-specific-reference')
    check(not first_op['done'] and first_cell.retained and probe.ledger.buffers==1,
          'owner-reference-proof-cannot-release-G-private-cell-or-finish-its-operation')
    first_cell.gate()
    check(probe.ledger.buffers == 0 and first_cell.released and
          first_cell.discarded and first_cell.deliveries == 0 and first_op['done'] and
          state['commands']['lease-first']['status'] == 'DONE' and
          state['commands']['lease-first']['result'] == {'completion': 'DISCARDED'},
          'real-private-gate-releases-ledger-only-after-native-drain')
    next_op = authority.admit(state, a, 'lease-after-drain', handle_a)
    next_cell = Engine.private_cell(probe, state, 'lease-after-drain', a,
                                    'read', buffer=True)
    check(probe.ledger.buffers == 1 and next_cell is not first_cell and
          len(probe.cells) == 2 and not next_op['done'],
          'distinct-real-private-cell-acquires-lease-after-prior-drain')
    next_value = {'n': 3, 'sha': sha(b'new')}
    actual = complete_source_response(authority, state, 'lease-after-drain',
                                      next_cell, next_value, hold=False)
    check(actual == next_value and probe.ledger.buffers == 0 and
          probe.ledger.buffer_peak == 1 and next_cell.released and
          next_cell.deliveries == 1 and not next_cell.discarded and next_op['done'] and
          state['commands']['lease-after-drain']['result'] == {'completion': 'DELIVERED'},
          'new-real-private-cell-delivers-and-releases-once')
    rejects(first_cell.gate, 'GATE_DUPLICATE', 'real-private-cell-double-gate-refused')
    check(probe.ledger.buffers == 0 and all(cell.released for cell in probe.cells.values()),
          'real-private-lease-suite-leaves-no-live-buffer')

    # The request is captured through the exact production request constructor;
    # each refusal inspects current authority identity, never an `old` boolean.
    def sink_state():
        return dict(ownerInstance='owner-1', epoch=1, task='T-authority-check',
                    grant='grant-1', B='handle-B', attempt='attempt-1', revision='revision-1',
                    receipt=dict(epoch=1, task='T-authority-check', grant='grant-1',
                                 revision='revision-1', lease='lease-1', sha=sha(b'validated')),
                    state='READY_ELIGIBLE', sourceDone=True, abortOnly=False)

    current = sink_state()
    request = capture_ready_request(current)
    saved_request = copy.deepcopy(request)
    request_digest = sha(compact(request))
    validate_ready_request(current, request)
    check(request == saved_request and sha(compact(request)) == request_digest,
          'valid-original-owner-request-without-takeover-is-accepted-unchanged')
    current['ownerInstance'] = 'owner-2'
    current['epoch'] = 2
    current['abortOnly'] = True
    rejects(lambda: validate_ready_request(current, request), 'STALE_OWNER',
            'original-e1-request-rejected-by-current-e2-owner')
    check(request == saved_request and sha(compact(request)) == request_digest,
          'original-e1-request-submitted-byte-equivalent-after-takeover')
    current = sink_state()
    request = capture_ready_request(current)
    bad_epoch = copy.deepcopy(request)
    bad_epoch['epoch'] = 2
    rejects(lambda: validate_ready_request(current, bad_epoch), 'STALE_OWNER',
            'wrong-epoch-rejected-with-owner-reason-without-takeover')
    bad_receipt = copy.deepcopy(request)
    bad_receipt['receipt']['sha'] = sha(b'unvalidated')
    rejects(lambda: validate_ready_request(current, bad_receipt), 'RECEIPT_MISMATCH',
            'wrong-receipt-rejected-with-distinct-receipt-reason')
    for field in ('export', 'handle', 'attempt', 'revision'):
        bad = copy.deepcopy(request)
        bad[field] = str(bad[field]) + '-wrong'
        rejects(lambda bad=bad: validate_ready_request(current, bad),
                'READY_BINDING_MISMATCH', 'wrong-ready-' + field + '-binding-refused')
    current['sourceDone'] = False
    rejects(lambda: validate_ready_request(current, request), 'NOT_READY_ELIGIBLE',
            'valid-owner-still-requires-source-release')

    hub.drain(timeout=.2)
    check(all(cell.released for cell in created_cells),
          'single-completion-hub-direct-cell-regressions-all-released')
    report = dict(scope='PRODUCTION_LOGICAL_AUTHORITY_AND_PENDING_CELL_ONLY',
                  status='PASS', assertions=len(passed), checks=passed,
                  atomicOrderObservations=observations, fixtureBytes=0,
                  metadataBytesCreated=0, newHelpers=0, nativeCalls=0,
                  limitations='Logical authority/cell checks. Real J/R observations belong to the separate all-61 synthetic integration; no media or Windows/JVM native claim is made here.')
    need(len(compact(report)) <= 131072, 'AUTHORITY_CHECK_REPORT_BOUND')
    return report
