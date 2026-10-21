"""E2 C01/C02 production completion/callback boundary checks.

No Engine constructor, Native, Channel, helper, fixture, or media is used. Real
production authority, PendingCell, CompletionHub, Future callbacks and Ledger
buffer leases are exercised. Native-handle ownership remains outside this logical
sub-suite and is not inferred from release callbacks here.
"""
from __future__ import annotations

import copy
import threading
from types import SimpleNamespace

from authority import PendingCell, SourceAuthority, complete_source_response
from gcore import Ledger, Refused, Stop, compact, need, sha
from notifications import CompletionHub


def run_checks(root, manifest):
    passed = []
    observations = []
    cells = []

    def check(value, name):
        need(value, 'COMPLETION_CHECK:' + name)
        passed.append(name)

    def refuses(action, reason, name):
        try:
            action()
        except Refused as error:
            check(str(error) == reason, name)
            return
        raise AssertionError('Missing refusal: ' + name + '/' + reason)

    def stops(action, reason, name):
        try:
            action()
        except Stop as error:
            check(str(error) == reason, name)
            return
        raise AssertionError('Missing stop: ' + name + '/' + reason)

    counter = [0]

    def make(hub, kind='read', timeout=None, binding_change=None):
        counter[0] += 1
        opid = 'completion-check-' + str(counter[0])
        authority = SourceAuthority()
        state = dict(task='S-' + opid, versions={}, ops={}, objects={},
                     commands={}, recovered=False, sourceDone=False)
        binding = authority.reserve(state, 'v1', 'a')
        authority.reserve(state, 'v1', 'b')
        handle = dict(binding, key='H-' + opid, disposition='OWNED_OPEN_RETRYABLE')
        state['objects'][handle['key']] = handle
        operation = authority.admit(state, binding, opid, handle if kind == 'read' else None)
        ledger = Ledger()
        lease = ledger.buffer({'buffers': 1}) if kind == 'read' else None
        if lease:
            lease.__enter__()
        owner = dict(privateResult=None, releases=0, drains=0)

        def release():
            need(owner['releases'] == 0, 'COMPLETION_DOUBLE_RELEASE')
            if lease:
                lease.__exit__(None, None, None)
            owner['privateResult'] = None
            owner['releases'] += 1

        def drained():
            authority.drain(state, opid)
            owner['drains'] += 1

        supplied = copy.deepcopy(binding)
        if binding_change:
            supplied.update(binding_change)
        try:
            cell = PendingCell(opid, supplied, release, on_drain=drained,
                               timeout=timeout, hub=hub, authority=authority,
                               state=state, kind=kind,
                               handle_key=handle['key'] if kind == 'read' else None)
        except BaseException:
            if lease:
                lease.__exit__(None, None, None)
            raise
        cells.append(cell)
        return SimpleNamespace(authority=authority, state=state, binding=binding,
                               handle=handle, operation=operation, id=opid,
                               ledger=ledger, owner=owner, cell=cell, kind=kind)

    def value_for(case):
        return ({'object': case.handle['key'], 'length': 32} if case.kind == 'open'
                else {'n': 7, 'sha': sha(b'private'), 'bytes': 'cHJpdmF0ZQ=='})

    def complete(case, hold):
        value = value_for(case)
        case.owner['privateResult'] = value
        return complete_source_response(case.authority, case.state, case.id,
                                        case.cell, value, hold=hold)

    def assert_released(case, label, delivered):
        check(case.cell.released and not case.cell.retained and
              case.owner['releases'] == 1 and case.owner['drains'] == 1 and
              case.operation['done'] and case.operation['nativeReturned'] and
              case.owner['privateResult'] is None and case.ledger.buffers == 0,
              label + '-actual-cell-and-buffer-drained-once')
        check(case.cell.deliveries == int(delivered) and
              case.cell.discarded == (not delivered),
              label + '-consumer-delivery-count')
        if case.kind == 'open' and not delivered:
            check(case.state['objects'][case.handle['key']]['disposition'] == 'OWNED_OPEN_RETRYABLE',
                  label + '-cell-drain-keeps-open-handle-ownership-for-cleanup')

    def cleanup_case(case):
        # Used only after a failed assertion so the central runner can still
        # return diagnostics without leaving our controlled callback work live.
        if case.cell.released:
            return
        if not case.cell.native_done:
            case.authority.mark_native(case.state, case.id)
            case.cell.complete(value_for(case))
        case.cell.cancel('CANCELLED')
        if not case.cell.gated:
            case.cell.gate(timeout=1)

    hub = CompletionHub(max_cells=8, callback_timeout=.4).start()
    try:
        # C01: both definite orders use one seal, without an accompanying cancel.
        # The read rule under this tool contract is identical: any result not
        # already delivered when seal/fence wins is discarded, then drained.
        for kind in ('open', 'read'):
            for held in (False, True):
                for first in ('delivery', 'seal'):
                    case = make(hub, kind)
                    label = kind + '-' + ('held' if held else 'ordinary') + '-' + first + '-first'
                    other_before = copy.deepcopy(case.state['versions']['v1']['consumers']['b'])
                    try:
                        if held:
                            complete(case, True)
                            check(not case.cell.response.done() and case.cell.retained and
                                  case.owner['releases'] == 0,
                                  label + '-held-native-value-private')
                        if first == 'seal':
                            case.authority.seal(case.state, 'v1')
                            check(not case.state['versions']['v1']['consumers']['a']['cancelled'],
                                  label + '-single-seal-not-masked-by-cancel')
                        if held:
                            case.cell.gate(timeout=1)
                        elif first == 'seal':
                            refuses(lambda: complete(case, False), 'SESSION_RELEASED',
                                    label + '-ordinary-return-refused')
                        else:
                            actual = complete(case, False)
                            check(actual == value_for(case), label + '-ordinary-result-is-real-value')
                        if first == 'delivery':
                            result = case.cell.response.result(timeout=1)
                            case.authority.seal(case.state, 'v1')
                            check(result == value_for(case) and
                                  case.cell.response.result(timeout=1) == result,
                                  label + '-successful-future-not-reversed-by-later-seal')
                        else:
                            refuses(lambda: case.cell.response.result(timeout=1), 'SESSION_RELEASED',
                                    label + '-future-refuses-late-result')
                        assert_released(case, label, delivered=first == 'delivery')
                        check(case.state['versions']['v1']['consumers']['b'] == other_before,
                              label + '-other-consumer-unchanged')
                        observations.append(dict(kind=kind, held=held, first=first,
                                                 deliveries=case.cell.deliveries,
                                                 discarded=case.cell.discarded))
                    finally:
                        cleanup_case(case)

        for kind in ('open', 'read'):
            for held in (False, True):
                case = make(hub, kind)
                label = kind + '-' + str(held) + '-global-fence-first'
                try:
                    if held:
                        complete(case, True)
                    case.authority.fence(case.state)
                    if held:
                        case.cell.gate(timeout=1)
                    else:
                        refuses(lambda: complete(case, False), 'SESSION_RELEASED',
                                label + '-ordinary-return-refused')
                    refuses(lambda: case.cell.response.result(timeout=1), 'SESSION_RELEASED',
                            label + '-future-refuses-late-result')
                    assert_released(case, label, delivered=False)
                finally:
                    cleanup_case(case)

        for kind in ('open', 'read'):
            case = make(hub, kind, binding_change={'generation': 'wrong-generation'})
            try:
                refuses(lambda: complete(case, False), 'SOURCE_BINDING_MISMATCH',
                        kind + '-completion-rechecks-exact-binding')
                refuses(lambda: case.cell.response.result(timeout=1), 'SOURCE_BINDING_MISMATCH',
                        kind + '-binding-mismatch-is-real-future-error')
                assert_released(case, kind + '-wrong-binding', delivered=False)
            finally:
                cleanup_case(case)

        # C02: each real callback asks a different prestarted thread to acquire
        # BOTH exact application locks. If either is held by the publisher, the
        # callback records a failure within its finite barrier wait; timeouts are
        # never counted as an acceptable outcome.
        for path in ('ordinary-complete', 'held-gate', 'end', 'cancel', 'deadline', 'gc'):
            case = make(hub, 'read', timeout=.2 if path == 'deadline' else None)
            start_probe = threading.Event()
            acquired = threading.Event()
            entered = threading.Event()
            callback_returned = threading.Event()
            facts = {}

            def probe_worker():
                if not start_probe.wait(2):
                    facts['probeStartTimeout'] = True
                    return
                with case.authority.lock:
                    case.authority.binding(case.state, 'v1', 'b')
                    with case.cell.lock:
                        facts['otherThreadAcquiredBoth'] = True
                acquired.set()

            worker = threading.Thread(target=probe_worker, name='E2-callback-lock-probe-' + path)
            worker.start()

            def callback(future):
                try:
                    entered.set()
                    facts['publishedFutureDone'] = future.done()
                    start_probe.set()
                    facts['acquiredBeforeCallbackReturn'] = acquired.wait(.25)
                finally:
                    callback_returned.set()

            case.cell.response.add_done_callback(callback)
            try:
                if path == 'ordinary-complete':
                    complete(case, False)
                else:
                    complete(case, True)
                    if path == 'held-gate':
                        case.cell.gate(timeout=1)
                    elif path == 'end':
                        case.authority.end(case.state, 'v1', 'a')
                    elif path == 'cancel':
                        case.authority.cancel(case.state, 'v1', 'a')
                    elif path == 'gc':
                        from phases import Cleanup
                        cleanup = SimpleNamespace(e=SimpleNamespace(cells={case.id: case.cell}))
                        Cleanup.release_gate(cleanup, 'read')
                    # deadline is produced by Hub's real bounded deadline worker.
                check(entered.wait(1) and callback_returned.wait(1),
                      path + '-real-done-callback-ran-and-returned')
                hub.drain(timeout=1)
                worker.join(1)
                check(not worker.is_alive() and not facts.get('probeStartTimeout') and
                      facts.get('publishedFutureDone') and
                      facts.get('otherThreadAcquiredBoth') and
                      facts.get('acquiredBeforeCallbackReturn'),
                      path + '-future-callback-outside-source-and-cell-locks')
                if path in ('end', 'cancel', 'deadline'):
                    reason = 'SOURCE_TIMEOUT' if path == 'deadline' else 'CANCELLED'
                    refuses(lambda: case.cell.response.result(timeout=1), reason,
                            path + '-real-response-error')
                    check(case.cell.retained and case.ledger.buffers == 1 and
                          case.owner['releases'] == 0,
                          path + '-callback-finish-alone-does-not-release-ungated-native-cell')
                    case.cell.gate(timeout=1)
                assert_released(case, path, delivered=path in ('ordinary-complete', 'held-gate'))
            finally:
                start_probe.set()
                worker.join(1)
                cleanup_case(case)
                need(not worker.is_alive(), 'CALLBACK_PROBE_THREAD_PENDING')

        case = make(hub, 'read')
        order = []
        try:
            for index in range(4):
                case.cell.response.add_done_callback(lambda future, index=index: order.append(index))
            refuses(lambda: case.cell.response.add_done_callback(lambda future: order.append(99)),
                    'CALLBACK_LIMIT', 'callback-registration-bounded-to-four')
            for name, action in [('cancel', case.cell.response.cancel),
                                 ('set-result', lambda: case.cell.response.set_result('forged')),
                                 ('set-exception', lambda: case.cell.response.set_exception(RuntimeError('forged')))]:
                refuses(action, 'COMPLETION_OWNED_BY_HUB', 'consumer-cannot-bypass-hub-' + name)
            check(not case.cell.response.done(), 'forbidden-public-completion-does-not-publish')
            complete(case, False)
            check(order == [0, 1, 2, 3], 'registered-real-callback-order-preserved')
            refuses(lambda: case.cell.response.add_done_callback(lambda future: order.append(100)),
                    'CALLBACK_REGISTRATION_CLOSED', 'late-callback-cannot-run-inline-after-decision')
            check(order == [0, 1, 2, 3], 'late-callback-refusal-invokes-no-user-code')
        finally:
            cleanup_case(case)
        hub.drain(timeout=1)
    finally:
        for cell in cells:
            # Normal cases already released; a failed check is surfaced even if
            # cleanup succeeds, and the central caller receives that exception.
            if cell.hub is hub and not cell.released:
                cell.cancel('CANCELLED')
                if not cell.native_done:
                    cell.authority.mark_native(cell.state, cell.operation)
                    cell.complete({'cleanup': True})
                if not cell.gated:
                    cell.gate(timeout=1)
        hub.close(timeout=1)
    check(hub.pending()['workersAlive'] == 0, 'normal-hub-fixed-workers-joined')

    # C02 slow-callback boundary: a real Future is published, but the callback
    # still owns its references. A timed-out drain/gate must STOP acceptance and
    # retain the real Ledger lease until our controlled callback actually exits.
    slow_hub = CompletionHub(max_cells=2, callback_timeout=.02).start()
    slow = make(slow_hub, 'read')
    callback_entered = threading.Event()
    release_callback = threading.Event()
    callback_exited = threading.Event()
    callback_facts = {}

    def slow_callback(future):
        try:
            callback_facts['published'] = future.done()
            callback_entered.set()
            callback_facts['releasedByTest'] = release_callback.wait(2)
        finally:
            callback_exited.set()

    slow.cell.response.add_done_callback(slow_callback)
    try:
        complete(slow, True)
        slow.cell.cancel('CANCELLED')
        check(callback_entered.wait(1), 'slow-real-callback-entered')
        refuses(lambda: slow.cell.response.result(timeout=1), 'CANCELLED',
                'slow-callback-does-not-hide-published-future-error')
        stops(lambda: slow_hub.drain(timeout=.1), 'CALLBACK_DRAIN_PENDING',
              'slow-callback-bounded-drain-stops-not-false-pass')
        stops(slow_hub.ensure_accepting, 'CALLBACK_DRAIN_PENDING',
              'callback-overdeadline-stops-new-admission')
        check(callback_facts.get('published') and slow.cell.retained and
              not slow.cell.released and slow.owner['releases'] == 0 and
              slow.ledger.buffers == 1 and not callback_exited.is_set(),
              'published-future-still-retains-callback-private-cell-and-ledger-buffer')
        stops(lambda: slow.cell.gate(timeout=.02), 'CALLBACK_DRAIN_PENDING',
              'slow-callback-bounded-gate-retains-pending')
        check(slow.cell.retained and slow.ledger.buffers == 1,
              'gate-timeout-cannot-fabricate-private-release')
        stops(lambda: slow_hub.close(timeout=.02), 'CALLBACK_DRAIN_PENDING',
              'slow-callback-close-cannot-report-all-workers-joined')
    finally:
        release_callback.set()
        need(callback_exited.wait(1), 'CONTROLLED_CALLBACK_DID_NOT_EXIT')
        slow_hub.drain(timeout=1)
        if not slow.cell.gated:
            slow.cell.gate(timeout=1)
        slow_hub.close(timeout=1)
    check(callback_facts.get('releasedByTest') and slow.cell.released and
          slow.cell.discarded and slow.cell.deliveries == 0 and
          slow.owner['releases'] == 1 and slow.ledger.buffers == 0 and
          slow_hub.pending()['workersAlive'] == 0,
          'controlled-callback-exit-allows-real-release-and-worker-join')

    # Hold the sole notifier on callback A. B makes a SUCCESS decision but its
    # Future is not yet published; a later single seal cannot reverse that
    # immutable decision. C fills the remaining bounded queue credit, so the
    # fourth live cell is refused while active/queued notification work is real.
    cap_hub = CompletionHub(max_cells=3, callback_timeout=.8).start()
    cap_cases = []
    callback_a_entered = threading.Event()
    callback_a_release = threading.Event()
    callback_a_exited = threading.Event()
    gate_b_done = threading.Event()
    lag_facts = {}
    gate_b_thread = None

    def callback_a(future):
        try:
            callback_a_entered.set()
            lag_facts['callbackAReleasedByTest'] = callback_a_release.wait(2)
        finally:
            callback_a_exited.set()

    try:
        case_a = make(cap_hub, 'read')
        cap_cases.append(case_a)
        case_a.cell.response.add_done_callback(callback_a)
        complete(case_a, True)
        case_a.cell.cancel('CANCELLED')
        check(callback_a_entered.wait(1), 'lag-notifier-busy-in-real-callback-A')
        case_b = make(cap_hub, 'open')
        cap_cases.append(case_b)
        complete(case_b, True)

        def gate_b():
            try:
                case_b.cell.gate(timeout=1)
                lag_facts['gateBReturned'] = True
            except BaseException as error:
                lag_facts['gateBError'] = type(error).__name__ + ':' + str(error)
            finally:
                gate_b_done.set()

        gate_b_thread = threading.Thread(target=gate_b, name='E2-decided-unpublished-gate-B')
        gate_b_thread.start()
        check(case_b.cell.decided.wait(.5), 'B-success-decision-observed-by-real-decision-event')
        with case_b.cell.lock:
            decided_value = copy.deepcopy(case_b.cell.outcome['value'])
            decision_error = case_b.cell.outcome['error']
        check(decision_error is None and decided_value == value_for(case_b) and
              not case_b.cell.response.done() and not gate_b_done.is_set() and
              case_b.cell.retained and case_b.owner['releases'] == 0,
              'B-success-linearized-while-future-unpublished-and-resource-retained')
        case_b.authority.seal(case_b.state, 'v1')
        with case_b.cell.lock:
            unchanged = (case_b.cell.outcome['error'] is None and
                         case_b.cell.outcome['value'] == decided_value)
        check(unchanged and not case_b.cell.response.done(),
              'later-single-seal-cannot-reverse-decided-unpublished-success')
        with cap_hub.condition:
            queued_b = cap_hub.condition.wait_for(
                lambda: case_b.cell in cap_hub.queue, timeout=.5)
        check(queued_b, 'B-notice-actually-queued-behind-controlled-callback-A')
        case_c = make(cap_hub, 'read')
        cap_cases.append(case_c)
        complete(case_c, True)
        case_c.cell.cancel('CANCELLED')
        before = copy.deepcopy(cap_hub.pending())
        check(before['cells'] == 3 and before['queued'] == 2 and before['active'] == 1,
              'fixed-notifier-has-one-active-two-real-queued-notifications')
        refuses(lambda: make(cap_hub, 'open'), 'PRIVATE_RESULT_CELL_LIMIT',
                'notification-hub-cell-and-queue-cap-refuses-fourth-live-cell')
        after = cap_hub.pending()
        check(after['cells'] == before['cells'] and after['queued'] == before['queued'] and
              after['active'] == before['active'],
              'capacity-refusal-does-not-grow-live-cell-or-notification-queue')
        callback_a_release.set()
        check(callback_a_exited.wait(1) and gate_b_done.wait(1),
              'notifier-lag-clears-after-controlled-callback-exit')
        gate_b_thread.join(1)
        check(not gate_b_thread.is_alive() and lag_facts.get('gateBReturned') and
              'gateBError' not in lag_facts and lag_facts.get('callbackAReleasedByTest') and
              case_b.cell.response.result(timeout=1) == decided_value,
              'B-decided-success-publishes-after-seal-and-notifier-lag')
        assert_released(case_b, 'lagged-success-B', delivered=True)
    finally:
        callback_a_release.set()
        if gate_b_thread is not None:
            gate_b_thread.join(1)
            need(not gate_b_thread.is_alive(), 'DECIDED_GATE_THREAD_PENDING')
        for case in cap_cases:
            cleanup_case(case)
        cap_hub.drain(timeout=1)
        cap_hub.close(timeout=1)
    check(cap_hub.pending()['workersAlive'] == 0, 'capacity-hub-fixed-workers-joined')

    # Capacity credit belongs to the notifier through its actual return, not
    # merely through private-buffer release. Pause the real released(active)
    # handoff AFTER the original method has run while B is genuinely queued.
    handoff_hub = CompletionHub(max_cells=2, callback_timeout=2).start()
    handoff_cases = []
    handoff_callback_entered = threading.Event()
    handoff_callback_release = threading.Event()
    handoff_released_entered = threading.Event()
    handoff_return_release = threading.Event()
    handoff_gate_done = threading.Event()
    handoff_gate_wait_entered = threading.Event()
    handoff_facts = {}
    handoff_gate_thread = None
    original_released = handoff_hub.released
    original_wait_cell = handoff_hub.wait_cell

    def handoff_callback(future):
        handoff_callback_entered.set()
        handoff_facts['callbackReleasedByTest'] = handoff_callback_release.wait(2)

    def paused_released(cell):
        original_released(cell)
        if cell is handoff_cases[0].cell:
            handoff_released_entered.set()
            handoff_facts['releasedReturnedByTest'] = handoff_return_release.wait(2)

    def observed_wait_cell(cell, timeout=.2):
        if cell is handoff_cases[0].cell:
            handoff_gate_wait_entered.set()
        return original_wait_cell(cell, timeout)

    handoff_hub.released = paused_released
    handoff_hub.wait_cell = observed_wait_cell
    try:
        handoff_a = make(handoff_hub, 'read')
        handoff_cases.append(handoff_a)
        handoff_a.cell.response.add_done_callback(handoff_callback)
        complete(handoff_a, True)

        def handoff_gate():
            try:
                handoff_a.cell.gate(timeout=2)
                handoff_facts['gateReturned'] = True
            except BaseException as error:
                handoff_facts['gateError'] = type(error).__name__ + ':' + str(error)
            finally:
                handoff_gate_done.set()

        handoff_gate_thread = threading.Thread(target=handoff_gate,
                                                name='E2-active-credit-gate-A')
        handoff_gate_thread.start()
        check(handoff_callback_entered.wait(1), 'active-credit-A-real-callback-entered')
        check(handoff_gate_wait_entered.wait(1),
              'active-credit-A-gate-waits-before-notifier-resource-release')
        handoff_b = make(handoff_hub, 'open')
        handoff_cases.append(handoff_b)
        complete(handoff_b, True)
        handoff_b.cell.cancel('CANCELLED')
        with handoff_hub.condition:
            b_queued = handoff_hub.condition.wait_for(
                lambda: handoff_b.cell in handoff_hub.queue, timeout=.5)
        check(b_queued, 'active-credit-B-notice-really-queued')
        handoff_callback_release.set()
        check(handoff_released_entered.wait(1),
              'real-active-credit-return-paused-after-original-released')
        handoff_snapshot = handoff_hub.pending()
        check(handoff_a.cell.released and handoff_a.ledger.buffers == 0 and
              handoff_a.owner['releases'] == 1 and not handoff_gate_done.is_set() and
              handoff_snapshot['cells'] == 2 and handoff_snapshot['active'] == 1 and
              handoff_snapshot['queued'] == 1,
              'released-private-buffer-keeps-active-notification-capacity-credit')
        refuses(lambda: make(handoff_hub, 'open'), 'PRIVATE_RESULT_CELL_LIMIT',
                'new-cell-refused-during-real-active-credit-handoff-window')
        current = handoff_hub.pending()
        check(current['cells'] == 2 and current['queued'] == 1 and current['active'] == 1,
              'handoff-refusal-cannot-expand-capacity-or-notification-queue')
        handoff_return_release.set()
        check(handoff_gate_done.wait(1), 'active-credit-gate-returns-after-notifier-handoff')
        handoff_gate_thread.join(1)
        handoff_hub.drain(timeout=1)
        check(not handoff_gate_thread.is_alive() and handoff_facts.get('gateReturned') and
              'gateError' not in handoff_facts and
              handoff_facts.get('callbackReleasedByTest') and
              handoff_facts.get('releasedReturnedByTest'),
              'active-credit-controlled-thread-and-publication-really-returned')
        cleanup_case(handoff_b)
        handoff_hub.drain(timeout=1)
        handoff_c = make(handoff_hub, 'read')
        handoff_cases.append(handoff_c)
        result = complete(handoff_c, False)
        check(result == value_for(handoff_c),
              'new-cell-admitted-and-published-after-real-credit-return')
        assert_released(handoff_c, 'post-handoff-new-cell', delivered=True)
    finally:
        handoff_callback_release.set()
        handoff_return_release.set()
        handoff_hub.released = original_released
        handoff_hub.wait_cell = original_wait_cell
        if handoff_gate_thread is not None:
            handoff_gate_thread.join(1)
            need(not handoff_gate_thread.is_alive(), 'ACTIVE_CREDIT_GATE_THREAD_PENDING')
        for case in handoff_cases:
            cleanup_case(case)
        handoff_hub.drain(timeout=1)
        handoff_hub.close(timeout=1)
    check(handoff_hub.pending()['workersAlive'] == 0,
          'active-credit-handoff-hub-workers-actually-joined')

    # Controlled submission refusal proves a decided cancellation is still
    # genuinely unpublished/PENDING. No submitted bit or private release can be
    # inferred from the decision. The original submit is used ONLY to drain this
    # test's already-cancelled cell in finally; the recorded failure and blocked
    # admission state remain intact and are never reset into a success.
    submit_hub = CompletionHub(max_cells=2, callback_timeout=.4).start()
    submit_case = make(submit_hub, 'read')
    complete(submit_case, True)
    original_submit = submit_hub.submit
    submit_failures = {'calls': 0}
    submit_failure_observation = {}

    def refused_submit(cell):
        submit_failures['calls'] += 1
        raise RuntimeError('SYNTHETIC_SUBMIT_REJECTION')

    submit_hub.submit = refused_submit
    try:
        try:
            submit_case.cell.cancel('CANCELLED')
        except RuntimeError as error:
            check(str(error) == 'SYNTHETIC_SUBMIT_REJECTION',
                  'controlled-submit-exception-reaches-original-caller')
        else:
            raise AssertionError('Notification submit exception was swallowed')
        snapshot = submit_hub.pending()
        check(submit_failures['calls'] == 1 and
              submit_case.cell.notification_submit_error == 'RuntimeError' and
              not submit_case.cell.notification_submitted and
              not submit_case.cell.notification_posting and
              not submit_case.cell.response.done() and
              submit_case.cell.retained and not submit_case.cell.released and
              submit_case.owner['releases'] == 0 and submit_case.ledger.buffers == 1 and
              not submit_case.operation['done'] and
              snapshot['cells'] == 1 and snapshot['active'] == 0 and snapshot['queued'] == 0,
              'submit-exception-keeps-real-unpublished-cell-and-buffer-without-fake-submitted')
        stops(submit_hub.ensure_accepting, 'CALLBACK_DRAIN_PENDING',
              'submit-exception-stops-new-admission')
        stops(lambda: submit_case.cell.gate(timeout=.02), 'CALLBACK_DRAIN_PENDING',
              'unsubmitted-cancellation-gate-remains-pending')
        stops(lambda: submit_hub.close(timeout=.02), 'CALLBACK_DRAIN_PENDING',
              'empty-notification-queue-cannot-hide-unsubmitted-live-cell')
        check(submit_failures['calls'] == 1 and submit_case.cell.retained and
              submit_case.ledger.buffers == 1 and not submit_case.cell.response.done(),
              'failed-submit-is-not-retried-or-treated-as-complete')
        submit_failure_observation = dict(
            phase='BEFORE_CONTROLLED_CLEANUP', responsePublished=False,
            notificationSubmitted=submit_case.cell.notification_submitted,
            notificationSubmitError=submit_case.cell.notification_submit_error,
            retained=submit_case.cell.retained, ledgerBuffers=submit_case.ledger.buffers,
            hubBlocked=snapshot['blocked'], cleanupPolicy='Original submit only drains the already-cancelled test cell; no error/blocked flag is reset.')
    finally:
        submit_hub.submit = original_submit
        if not submit_case.cell.gated:
            try:
                submit_case.cell.gate(timeout=.02)
            except Stop:
                pass
        if not submit_case.cell.notification_done:
            original_submit(submit_case.cell)
        submit_hub.drain(timeout=1)
        submit_hub.close(timeout=1)
    refuses(lambda: submit_case.cell.response.result(timeout=1), 'CANCELLED',
            'controlled-submit-cleanup-does-not-turn-cancellation-into-success')
    check(submit_case.cell.notification_submit_error == 'RuntimeError' and
          not submit_case.cell.notification_submitted and
          submit_hub.pending()['blocked'] is not None and
          submit_case.cell.discarded and submit_case.cell.deliveries == 0 and
          submit_case.cell.released and submit_case.owner['releases'] == 1 and
          submit_case.ledger.buffers == 0 and submit_hub.pending()['workersAlive'] == 0,
          'submit-failure-retained-as-failure-after-controlled-resource-drain-and-join')

    report = dict(scope='E2_PRODUCTION_LOGICAL_COMPLETION_AND_CALLBACK_CHECKS_ONLY',
                  status='PASS', assertions=len(passed), checks=passed,
                  deliveryOrderObservations=observations, fixtureBytes=0,
                  notificationSubmitFailure=submit_failure_observation,
                  metadataBytesCreated=0, newHelpers=0, nativeCalls=0,
                  unresolvedControlledThreads=0,
                  limitations='Real production Future callbacks, authority, bounded Hub workers and Ledger leases. No Native/Channel/Engine construction or media; no OS handle/durability claim and no forced interruption of arbitrary Python callbacks.')
    need(len(compact(report)) <= 131072, 'COMPLETION_REPORT_BOUND')
    return report
