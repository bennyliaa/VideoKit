"""E1E D01 deterministic startup/return-channel checks of production code.

Only self-owned real Python Thread instances are used. No Native, Channel,
Engine constructor, helper, media, or disk-fault injection is involved. A generic
start exception has deliberately weaker facts than WorkerNotStartedError.
Controlled retirement of an UNKNOWN instance is reported separately from the
original production failure/PENDING observation.
"""
from __future__ import annotations

import copy
import io
import json
import threading
from concurrent.futures import ThreadPoolExecutor
from contextlib import redirect_stdout
from pathlib import Path
from types import SimpleNamespace

from authority import PendingCell, SourceAuthority
from controller import emit_failure
from gcore import Budget, Ledger, Refused, Stop, Store, compact, need
from gengine import Engine, Flow
from notifications import CompletionHub, WorkerNotStartedError


class TrackingThread(threading.Thread):
    """Actual Thread with observations; start/join still invoke Python itself."""
    def __init__(self, label, **kwargs):
        super().__init__(**kwargs)
        self.label = label
        self.real_start_calls = 0
        self.real_join_calls = 0
        self.join_was_started = []

    def start(self):
        self.real_start_calls += 1
        return super().start()

    def join(self, timeout=None):
        self.real_join_calls += 1
        self.join_was_started.append(self.ident is not None)
        return super().join(timeout)


class HoldingExitThread(TrackingThread):
    """The supplied production wrapper exits, but this real Thread stays alive."""
    def __init__(self, label, hold_entered, release_exit, **kwargs):
        super().__init__(label, **kwargs)
        self.hold_entered = hold_entered
        self.release_exit = release_exit
        self.hold_released = False

    def run(self):
        try:
            super().run()
        finally:
            self.hold_entered.set()
            self.hold_released = self.release_exit.wait(3)


class SecondCreditFails(Ledger):
    def __init__(self):
        super().__init__()
        self.worker_attempts = 0
        self.worker_reserved = 0

    def acquire(self, rid, owner, kind, row=None):
        if kind == 'worker':
            self.worker_attempts += 1
            if self.worker_attempts == 2:
                raise Refused('SYNTHETIC_SECOND_CREDIT_FAILURE')
        result = super().acquire(rid, owner, kind, row)
        if kind == 'worker':
            self.worker_reserved += 1
        return result


class FirstCreditFails(Ledger):
    def __init__(self):
        super().__init__()
        self.worker_attempts = 0

    def acquire(self, rid, owner, kind, row=None):
        if kind == 'worker':
            self.worker_attempts += 1
            raise Refused('SYNTHETIC_FIRST_CREDIT_FAILURE')
        return super().acquire(rid, owner, kind, row)


class SecondCreditFailsAfterCommit(Ledger):
    def __init__(self):
        super().__init__()
        self.worker_attempts = 0
        self.worker_reserved = 0

    def acquire(self, rid, owner, kind, row=None):
        if kind == 'worker':
            self.worker_attempts += 1
        result = super().acquire(rid, owner, kind, row)
        if kind == 'worker':
            self.worker_reserved += 1
            if self.worker_attempts == 2:
                raise Refused('SYNTHETIC_SECOND_CREDIT_AFTER_COMMIT')
        return result


def run_checks(root, manifest):
    root = Path(root)
    passed = []
    observations = []
    return_channels = []

    def check(condition, name):
        need(condition, 'STARTUP_CHECK:' + name)
        passed.append(name)

    def refuses(action, reason, name):
        try:
            action()
        except Refused as error:
            check(str(error) == reason, name)
            return
        raise AssertionError('Missing refusal: ' + name + '/' + reason)

    def stops(action, name):
        try:
            action()
        except Stop as error:
            check(str(error) == 'CALLBACK_DRAIN_PENDING', name)
            return
        raise AssertionError('Missing stop: ' + name)

    def fixture(ledger=None, mode='healthy'):
        ledger = ledger if ledger is not None else Ledger()
        threads = []
        start_labels = []
        second_start_entered = threading.Event()
        release_second_start = threading.Event()
        held_exit_entered = threading.Event()
        release_held_exit = threading.Event()

        def factory(*, label, target, name, daemon):
            if mode == 'join-timeout' and not threads:
                thread = HoldingExitThread(label, held_exit_entered, release_held_exit,
                                           target=target, name=name, daemon=daemon)
            else:
                thread = TrackingThread(label, target=target, name=name, daemon=daemon)
            threads.append(thread)
            return thread

        def starter(thread, label):
            start_labels.append(label)
            index = len(start_labels)
            if mode == 'first-clear' and index == 1:
                raise WorkerNotStartedError('SYNTHETIC_FIRST_NOT_STARTED')
            if mode == 'second-clear' and index == 2:
                raise WorkerNotStartedError('SYNTHETIC_SECOND_NOT_STARTED')
            if mode == 'generic-before-start' and index == 1:
                # No explicit non-start promise is given to production code.
                raise RuntimeError('SYNTHETIC_START_STATUS_UNKNOWN')
            if mode == 'starting-barrier' and index == 2:
                second_start_entered.set()
                need(release_second_start.wait(2), 'CONTROLLED_SECOND_START_NOT_RELEASED')
            thread.start()
            if mode in ('after-real-start', 'join-timeout') and index == 1:
                need(hub.workers[label]['entered_event'].wait(.5),
                     'CONTROLLED_REAL_WORKER_ENTRY_NOT_OBSERVED')
                raise RuntimeError('SYNTHETIC_ERROR_AFTER_REAL_START' if mode == 'after-real-start'
                                   else 'SYNTHETIC_ERROR_WITH_EXIT_PENDING')

        hub = CompletionHub(ledger=ledger, thread_factory=factory, starter=starter,
                            startup_timeout=1 if mode == 'starting-barrier' else .2)
        return SimpleNamespace(hub=hub, ledger=ledger, threads=threads,
                               start_labels=start_labels, mode=mode,
                               second_start_entered=second_start_entered,
                               release_second_start=release_second_start,
                               held_exit_entered=held_exit_entered,
                               release_held_exit=release_held_exit)

    def attempt(case, expected_type, expected_text):
        try:
            case.hub.start()
        except expected_type as error:
            check(str(error) == expected_text, case.mode + '-original-start-error-propagated')
            return error
        raise AssertionError('Hub unexpectedly started: ' + case.mode)

    def stable_refusal(case):
        before = copy.deepcopy(case.hub.pending())
        for index in range(3):
            stops(case.hub.ensure_accepting,
                  case.mode + '-ensure-accepting-stably-refused-' + str(index))
        releases = []
        stops(lambda: PendingCell('forbidden-cell', {'task': 'none'},
                                  lambda: releases.append('released'), hub=case.hub),
              case.mode + '-failed-start-refuses-real-cell-registration')
        after = case.hub.pending()
        check(not releases and after['cells'] == before['cells'] == 0 and
              after['queued'] == 0 and after['active'] == 0,
              case.mode + '-refused-cell-allocates-no-notice-or-private-release')
        start_count = len(case.start_labels)
        thread_count = len(case.threads)
        refuses(case.hub.start, 'COMPLETION_HUB_RESTART_DENIED',
                case.mode + '-failed-start-cannot-retry-or-restart')
        check(len(case.start_labels) == start_count and len(case.threads) == thread_count,
              case.mode + '-restart-refusal-creates-no-new-thread')

    def production_gates(case):
        """Actual Flow/Engine entry methods, with an unreachable effect sentinel."""
        label = case.mode
        budget = Budget(manifest)
        row = 'P01-N1'
        budget.begin(row)
        pool = ThreadPoolExecutor(max_workers=1, thread_name_prefix='E1E-unused-gate-io')
        probe = SimpleNamespace(root=root / ('gates-' + label), manifest=manifest,
                                ledger=case.ledger, completions=case.hub,
                                budget=budget, store=Store(root / ('gates-' + label), case.ledger),
                                states={}, admissions={}, data_counts={}, channels={},
                                pending={}, cells={}, cell_peak=0, io=pool,
                                lock=threading.RLock(), row=row, stopping=False)
        probe.source = SourceAuthority(probe.lock)
        probe.new_state = lambda task: Engine.new_state(probe, task)
        state = probe.new_state('S01')
        probe.states['S01'] = state
        flow = Flow(probe, row)
        probe.flow = flow
        effects = {'action': 0, 'io': 0}

        def forbidden_action():
            effects['action'] += 1
            raise AssertionError('Failed startup reached transaction effect')

        def forbidden_io(fn, timeout=None):
            effects['io'] += 1
            raise AssertionError('Failed startup reached IO/RPC scheduling')

        probe.io_call = forbidden_io
        probe.save = lambda task: Engine.save(probe, task)
        probe.event = lambda event, query=False: Engine.event(probe, event, query)
        probe.view = lambda: Engine.view(probe)
        before_usage = copy.deepcopy(budget.globalused)
        before_state = copy.deepcopy(state)
        try:
            stops(lambda: flow.transaction('P01-N1/probe', 'N', {'n': 1},
                                           forbidden_action, 'res', args=['v1', 'a']),
                  label + '-failed-start-blocks-production-transaction')
            check(budget.globalused == before_usage and state == before_state and
                  not probe.admissions and effects == {'action': 0, 'io': 0},
                  label + '-transaction-gate-precedes-credit-state-and-effect')
            stops(flow.query, label + '-failed-start-blocks-production-query')
            check(flow.qn == 0 and flow.qr == 0 and budget.globalused == before_usage and
                  state == before_state and effects['io'] == 0,
                  label + '-query-gate-precedes-cache-credit-and-log')
            flow.current_id = 'P01-N1/rpc-probe'
            probe.admissions[flow.current_id] = {'label': 'h+', 'saved': True, 'calls': 0}
            stops(lambda: Engine.remote(probe, 'J', 'OPEN', ['unreachable-H', 'unread.bin']),
                  label + '-failed-start-blocks-production-RPC')
            check(probe.admissions[flow.current_id]['calls'] == 0 and effects['io'] == 0 and
                  probe.store.native['write'] == 0 and probe.store.native['open'] == 0,
                  label + '-RPC-gate-reaches-no-helper-or-metadata-native-call')
        finally:
            pool.shutdown(wait=True, cancel_futures=True)

    def failure_receipt(case, original_error, expected_status):
        pool = ThreadPoolExecutor(max_workers=1, thread_name_prefix='E1E-unused-failure-io')
        probe = SimpleNamespace(completions=case.hub, ledger=case.ledger, channels={},
                                helper_attempts={name: {'attempted': False, 'status': 'NOT_ATTEMPTED'}
                                                 for name in ('J', 'R')},
                                pending={}, io=pool,
                                store=Store(root / ('receipt-' + case.mode), case.ledger),
                                global_log=None, global_close=None,
                                root=root / ('receipt-' + case.mode))
        channel = io.StringIO()
        try:
            with redirect_stdout(channel):
                code = emit_failure(probe, original_error, timeout=.05)
            lines = channel.getvalue().splitlines()
            check(code == 2 and len(lines) == 1,
                  case.mode + '-production-return-channel-emits-one-line-and-nonzero')
            witness = json.loads(lines[0])
            check(witness['scope'] == 'E1E_FAILURE_RETURN_CHANNEL' and
                  witness['status'] == expected_status and witness['status'] != 'PASS' and
                  witness['pid'] > 0 and witness['startupError'] and
                  witness['hub']['startupError'] == witness['startupError'],
                  case.mode + '-return-channel-keeps-original-failure-lifecycle')
            check(all(witness['helpers'][name]['started'] is False and
                      witness['helpers'][name]['pid'] is None and
                      witness['helpers'][name]['instance'] is None and
                      witness['helpers'][name]['exitObserved'] is False
                      for name in ('J', 'R')),
                  case.mode + '-pre-helper-return-reports-absence-without-fake-exit')
            check(witness['logOpened'] is False and witness['logCloseProven'] is False and
                  witness['logOwnershipPending'] is False and
                  witness['mediaRead'] is False and witness['realPFRun'] is False,
                  case.mode + '-unopened-log-is-not-falsely-proven-closed')
            check(witness['remainingWorkerCredits'] == witness['hub']['remainingCredits'] and
                  witness['remainingResources'] == len(case.ledger.live),
                  case.mode + '-return-channel-includes-real-remaining-worker-credit')
            return_channels.append(copy.deepcopy(witness))
            return witness
        finally:
            pool.shutdown(wait=True, cancel_futures=True)

    def assert_no_fake_join(case):
        for thread in case.threads:
            check(all(thread.join_was_started),
                  case.mode + '-' + thread.label + '-never-joins-unstarted-thread')
        check(all(not thread.is_alive() for thread in case.threads if thread.ident is not None),
              case.mode + '-every-actually-started-controlled-thread-exited')

    first_credit = fixture(FirstCreditFails(), mode='first-credit')
    try:
        error = attempt(first_credit, Refused, 'SYNTHETIC_FIRST_CREDIT_FAILURE')
        snapshot = first_credit.hub.pending()
        check(first_credit.ledger.worker_attempts == 1 and not first_credit.threads and
              not first_credit.start_labels and not first_credit.ledger.live and
              not first_credit.ledger.audit and not snapshot['remainingCredits'] and
              not snapshot['ownershipPending'],
              'first-credit-failure-creates-no-thread-credit-refund-or-join')
        stable_refusal(first_credit)
        failure_receipt(first_credit, error, 'FAIL')
        observations.append(dict(case=first_credit.mode, originalFailure=copy.deepcopy(snapshot)))
    finally:
        first_credit.hub.close(timeout=.2)
        assert_no_fake_join(first_credit)

    # First start explicitly did not invoke Thread.start: no join is permitted.
    first = fixture(mode='first-clear')
    try:
        error = attempt(first, WorkerNotStartedError, 'SYNTHETIC_FIRST_NOT_STARTED')
        snapshot = first.hub.pending()
        check(snapshot['lifecycle'] != 'RUNNING' and snapshot['startupError'] and
              not snapshot['ownershipPending'] and not snapshot['remainingCredits'] and
              not first.ledger.live and len(first.threads) == 1 and
              first.threads[0].real_start_calls == 0 and first.threads[0].real_join_calls == 0,
              'first-clear-failure-returns-only-proven-unstarted-credit')
        check(any(worker['neverStartedProven'] and not worker['joined']
                  for worker in snapshot['workers'].values()) and
              all(proof != 'THREAD_JOIN_PROVEN' for _, proof in first.ledger.audit),
              'first-clear-failure-does-not-invent-thread-join-proof')
        stable_refusal(first)
        production_gates(first)
        failure_receipt(first, error, 'FAIL')
        before_audit = copy.deepcopy(first.ledger.audit)
        first.hub.close(timeout=.2)
        first.hub.close(timeout=.2)
        check(first.ledger.audit == before_audit and first.threads[0].real_join_calls == 0,
              'first-clear-repeated-close-no-double-release-or-unstarted-join')
        observations.append(dict(case=first.mode, originalFailure=copy.deepcopy(snapshot)))
    finally:
        first.hub.close(timeout=.2)
        assert_no_fake_join(first)

    # The first worker is really started. A second explicit non-start failure
    # requires stopping/joining that exact first instance and no join of second.
    second = fixture(mode='second-clear')
    try:
        error = attempt(second, WorkerNotStartedError, 'SYNTHETIC_SECOND_NOT_STARTED')
        snapshot = second.hub.pending()
        check(len(second.threads) == 2 and second.threads[0].real_start_calls == 1 and
              second.threads[0].real_join_calls >= 1 and second.threads[0].ident is not None and
              not second.threads[0].is_alive() and second.threads[1].real_start_calls == 0 and
              second.threads[1].real_join_calls == 0 and
              not snapshot['ownershipPending'] and not snapshot['remainingCredits'] and
              not second.ledger.live,
              'second-clear-failure-joins-first-real-instance-only')
        check(any(worker['entered'] and worker['exited'] and worker['joined'] and
                  not worker['neverStartedProven'] for worker in snapshot['workers'].values()) and
              any(worker['neverStartedProven'] and not worker['joined']
                  for worker in snapshot['workers'].values()),
              'second-clear-failure-distinguishes-actual-exit-from-never-started')
        stable_refusal(second)
        production_gates(second)
        failure_receipt(second, error, 'FAIL')
        joins = [thread.real_join_calls for thread in second.threads]
        audit = copy.deepcopy(second.ledger.audit)
        second.hub.close(timeout=.2)
        second.hub.close(timeout=.2)
        check([thread.real_join_calls for thread in second.threads] == joins and
              second.ledger.audit == audit,
              'second-clear-repeated-close-does-not-join-or-refund-twice')
        observations.append(dict(case=second.mode, originalFailure=copy.deepcopy(snapshot)))
    finally:
        second.hub.close(timeout=.2)
        assert_no_fake_join(second)

    # A failed second credit is not an existing worker or a credit to refund.
    credit = fixture(SecondCreditFails(), mode='second-credit')
    try:
        error = attempt(credit, Refused, 'SYNTHETIC_SECOND_CREDIT_FAILURE')
        snapshot = credit.hub.pending()
        check(credit.ledger.worker_attempts == 2 and credit.ledger.worker_reserved == 1 and
              len(credit.threads) == 1 and credit.threads[0].real_start_calls == 1 and
              credit.threads[0].real_join_calls >= 1 and not credit.threads[0].is_alive() and
              not credit.ledger.live and not snapshot['remainingCredits'] and
              not snapshot['ownershipPending'],
              'second-credit-failure-does-not-presume-second-thread-or-reservation')
        check(len(credit.ledger.audit) == 1 and credit.ledger.audit[0][1] == 'THREAD_JOIN_PROVEN',
              'second-credit-failure-releases-only-first-real-exited-worker')
        stable_refusal(credit)
        production_gates(credit)
        failure_receipt(credit, error, 'FAIL')
        observations.append(dict(case=credit.mode, originalFailure=copy.deepcopy(snapshot)))
    finally:
        credit.hub.close(timeout=.2)
        assert_no_fake_join(credit)

    # A trusted allocator can raise immediately after its real atomic commit.
    # That second reservation exists and must be retired as not started; it
    # cannot disappear merely because acquire did not return normally.
    committed = fixture(SecondCreditFailsAfterCommit(), mode='second-credit-after-commit')
    try:
        error = attempt(committed, Refused, 'SYNTHETIC_SECOND_CREDIT_AFTER_COMMIT')
        snapshot = committed.hub.pending()
        check(committed.ledger.worker_attempts == 2 and committed.ledger.worker_reserved == 2 and
              len(committed.threads) == 1 and not committed.threads[0].is_alive() and
              not committed.ledger.live and not snapshot['remainingCredits'] and
              not snapshot['ownershipPending'] and len(committed.ledger.audit) == 2,
              'post-commit-reserve-error-observes-and-retires-real-second-credit')
        second_facts = snapshot['workers']['deadline']
        check(second_facts['creditReserved'] and second_facts['creditReleased'] and
              second_facts['reserveError'] and not second_facts['reserveReturned'] and
              not second_facts['threadCreated'] and not second_facts['startEntered'] and
              second_facts['neverStartedProven'] and not second_facts['joined'],
              'post-commit-second-credit-is-not-invented-thread-or-join')
        stable_refusal(committed)
        failure_receipt(committed, error, 'FAIL')
        observations.append(dict(case=committed.mode, originalFailure=copy.deepcopy(snapshot)))
    finally:
        committed.hub.close(timeout=.2)
        assert_no_fake_join(committed)

    # A starter may call the real start and then raise. It is not a never-started
    # fact; entry+exit+actual join are required for release.
    after_start = fixture(mode='after-real-start')
    try:
        error = attempt(after_start, RuntimeError, 'SYNTHETIC_ERROR_AFTER_REAL_START')
        snapshot = after_start.hub.pending()
        facts = [worker for worker in snapshot['workers'].values() if worker['startEntered']]
        check(len(after_start.threads) == 1 and after_start.threads[0].real_start_calls == 1 and
              after_start.threads[0].real_join_calls >= 1 and
              not after_start.threads[0].is_alive() and len(facts) == 1 and
              facts[0]['entered'] and facts[0]['exited'] and facts[0]['joined'] and
              not facts[0]['startReturned'] and not facts[0]['neverStartedProven'] and
              not snapshot['ownershipPending'] and not snapshot['remainingCredits'],
              'error-after-real-start-requires-real-entry-exit-and-join')
        check(after_start.ledger.audit and
              all(proof == 'THREAD_JOIN_PROVEN' for _, proof in after_start.ledger.audit),
              'after-real-start-error-is-not-refunded-as-unstarted')
        stable_refusal(after_start)
        production_gates(after_start)
        failure_receipt(after_start, error, 'FAIL')
        observations.append(dict(case=after_start.mode, originalFailure=copy.deepcopy(snapshot)))
    finally:
        after_start.hub.close(timeout=.2)
        assert_no_fake_join(after_start)

    # Generic error BEFORE actual start deliberately gives production no proof
    # that start never happened. Neither alive=False nor ident=None is a refund.
    unknown = fixture(mode='generic-before-start')
    original_unknown = None
    unknown_receipt = None
    try:
        error = attempt(unknown, RuntimeError, 'SYNTHETIC_START_STATUS_UNKNOWN')
        original_unknown = copy.deepcopy(unknown.hub.pending())
        facts = [worker for worker in original_unknown['workers'].values()
                 if worker['creditReserved'] and not worker['creditReleased']]
        check(original_unknown['ownershipPending'] and len(original_unknown['remainingCredits']) == 1 and
              len(unknown.ledger.live) == 1 and len(unknown.threads) == 1 and
              unknown.threads[0].ident is None and not unknown.threads[0].is_alive() and
              unknown.threads[0].real_start_calls == 0 and unknown.threads[0].real_join_calls == 0 and
              len(facts) == 1 and facts[0]['unknown'] and not facts[0]['neverStartedProven'],
              'generic-start-error-retains-credit-despite-not-alive-and-no-ident')
        stable_refusal(unknown)
        production_gates(unknown)
        stops(lambda: unknown.hub.close(timeout=.02),
              'unknown-start-close-remains-pending-without-unstarted-join')
        check(unknown.threads[0].real_join_calls == 0 and not unknown.ledger.audit,
              'unknown-start-never-joins-or-refunds-unproven-instance')
        unknown_receipt = failure_receipt(unknown, error, 'PENDING')
        check(unknown_receipt['remainingWorkerCredits'] and
              unknown_receipt['hub']['ownershipPending'] and
              unknown_receipt['remainingResources'] == 1,
              'original-return-channel-does-not-falsely-zero-unknown-worker-credit')
        observations.append(dict(case=unknown.mode,
                                 originalFailure=copy.deepcopy(original_unknown),
                                 originalReturn=copy.deepcopy(unknown_receipt),
                                 controlledCleanup='Only after recording PENDING: test starts the original already-stopping wrapper and actually joins it. This is retirement, not a production retry or proof that the original failure had zero ownership.'))
    finally:
        # Test-owned retirement obtains NEW real facts only after the original
        # UNKNOWN/PENDING witness above. Never clear startupError or retry Hub.
        unknown.hub.stop_when_drained()
        for thread in unknown.threads:
            if thread.ident is None:
                thread.start()
            thread.join(timeout=1)
            need(not thread.is_alive(), 'CONTROLLED_UNKNOWN_THREAD_RETIREMENT_PENDING')
        unknown.hub.close(timeout=.2)
    retired = unknown.hub.pending()
    check(original_unknown is not None and original_unknown['ownershipPending'] and
          unknown_receipt is not None and unknown_receipt['status'] == 'PENDING' and
          retired['startupError'] == original_unknown['startupError'] and
          not retired['ownershipPending'] and not retired['remainingCredits'] and
          not unknown.ledger.live,
          'controlled-retirement-preserves-original-unknown-failure-evidence')
    assert_no_fake_join(unknown)

    # Wrapper exit is weaker than actual Thread exit. A test-owned Thread pauses
    # AFTER the supplied wrapper has returned, making join timeout/real ownership
    # deterministic without a permanent hang or system thread exhaustion.
    joining = fixture(mode='join-timeout')
    joining_snapshot = None
    joining_receipt = None
    try:
        error = attempt(joining, RuntimeError, 'SYNTHETIC_ERROR_WITH_EXIT_PENDING')
        check(joining.held_exit_entered.wait(1),
              'join-timeout-real-thread-paused-after-production-wrapper-exit')
        joining_snapshot = copy.deepcopy(joining.hub.pending())
        facts = joining_snapshot['workers']['notify']
        check(facts['entered'] and facts['exited'] and facts['alive'] is True and
              facts['joinEntered'] and facts['joinReturned'] and not facts['joined'] and
              facts['unknown'] and not facts['creditReleased'] and
              joining.threads[0].is_alive() and joining_snapshot['ownershipPending'] and
              len(joining_snapshot['remainingCredits']) == 1 and len(joining.ledger.live) == 1,
              'wrapper-exit-and-returned-join-do-not-prove-real-thread-release')
        check(not joining.ledger.audit and joining.threads[0].real_join_calls >= 1,
              'join-timeout-retains-real-owner-without-THREAD_JOIN_PROVEN')
        stable_refusal(joining)
        production_gates(joining)
        joining_receipt = failure_receipt(joining, error, 'PENDING')
        check(joining_receipt['hub']['workers']['notify']['threadId'] == facts['threadId'] and
              joining_receipt['hub']['workers']['notify']['entryIdent'] == facts['entryIdent'] and
              joining_receipt['remainingWorkerCredits'] and
              joining_receipt['hub']['workersAlive'] == 1,
              'join-timeout-return-channel-keeps-original-live-worker-identity')
        observations.append(dict(
            case=joining.mode, originalFailure=copy.deepcopy(joining_snapshot),
            originalReturn=copy.deepcopy(joining_receipt),
            controlledCleanup='Only after original PENDING receipt: release the test Event, actually join the original Thread and let Hub observe new exit facts. Original wrapper-exit/join-timeout is never relabelled as proven release.'))
    finally:
        joining.release_held_exit.set()
        for thread in joining.threads:
            if thread.ident is not None:
                thread.join(timeout=1)
                need(not thread.is_alive(), 'CONTROLLED_HELD_EXIT_THREAD_PENDING')
        joining.hub.close(timeout=.2)
    retired_joining = joining.hub.pending()
    check(joining_snapshot is not None and joining_snapshot['ownershipPending'] and
          joining_receipt is not None and joining_receipt['status'] == 'PENDING' and
          retired_joining['startupError'] == joining_snapshot['startupError'] and
          not retired_joining['ownershipPending'] and not joining.ledger.live and
          joining.threads[0].hold_released,
          'real-exit-after-controlled-release-does-not-rewrite-original-PENDING-receipt')
    assert_no_fake_join(joining)

    # Both actual workers are required before RUNNING. The second starter is
    # held at a finite barrier while the first real worker already exists.
    starting = fixture(mode='starting-barrier')
    startup_owner_done = threading.Event()
    startup_owner_facts = {}

    def startup_owner():
        try:
            starting.hub.start()
            startup_owner_facts['returned'] = True
        except BaseException as error:
            startup_owner_facts['error'] = type(error).__name__ + ':' + str(error)
        finally:
            startup_owner_done.set()

    startup_owner_thread = threading.Thread(target=startup_owner,
                                             name='E1E-controlled-startup-owner')
    startup_owner_thread.start()
    try:
        check(starting.second_start_entered.wait(1), 'second-start-finite-barrier-entered')
        snapshot = starting.hub.pending()
        check(snapshot['lifecycle'] == 'STARTING' and snapshot['startupInProgress'] and
              snapshot['workers']['notify']['entered'] and
              not snapshot['workers']['deadline']['entered'] and
              len(starting.threads) == 2 and starting.threads[0].is_alive() and
              starting.threads[1].real_start_calls == 0,
              'one-real-worker-does-not-advertise-RUNNING-or-complete-startup')
        stops(starting.hub.ensure_accepting, 'STARTING-hub-cannot-accept-cell')
        production_gates(starting)
        starting.release_second_start.set()
        check(startup_owner_done.wait(1), 'both-real-starts-let-original-start-return')
        startup_owner_thread.join(1)
        check(not startup_owner_thread.is_alive() and startup_owner_facts.get('returned') and
              'error' not in startup_owner_facts and starting.hub.pending()['lifecycle'] == 'RUNNING',
              'RUNNING-only-after-second-worker-real-entry')
        starting.hub.ensure_accepting()
    finally:
        starting.release_second_start.set()
        startup_owner_thread.join(1)
        need(not startup_owner_thread.is_alive(), 'STARTUP_OWNER_THREAD_PENDING')
        starting.hub.close(timeout=1)
        assert_no_fake_join(starting)

    # A normal lifecycle is a separate baseline for idempotent close and exact
    # joins; no failure branch can borrow these successful startup facts.
    healthy = fixture(mode='healthy')
    try:
        healthy.hub.start()
        snapshot = healthy.hub.pending()
        healthy.hub.ensure_accepting()
        check(snapshot['lifecycle'] == 'RUNNING' and len(healthy.threads) == 2 and
              all(thread.real_start_calls == 1 and thread.is_alive() for thread in healthy.threads),
              'normal-hub-admits-only-after-two-actual-workers-start')
        healthy.hub.close(timeout=1)
        joins = [thread.real_join_calls for thread in healthy.threads]
        audit = copy.deepcopy(healthy.ledger.audit)
        healthy.hub.close(timeout=.2)
        healthy.hub.close(timeout=.2)
        check(all(count >= 1 for count in joins) and
              [thread.real_join_calls for thread in healthy.threads] == joins and
              healthy.ledger.audit == audit and not healthy.ledger.live and
              healthy.hub.pending()['workersAlive'] == 0,
              'normal-repeated-close-joins-and-releases-each-real-instance-once')
        stops(healthy.hub.ensure_accepting, 'closed-normal-hub-stably-refuses-new-admission')
    finally:
        healthy.hub.close(timeout=1)
        assert_no_fake_join(healthy)

    # Missing Channel is not itself proof that helper construction never began.
    # This return-channel-only negative has no actual helper/thread launch.
    for premise in ('attempted-without-channel', 'missing-attempt-inventory'):
        helper_ledger = Ledger()
        helper_hub = CompletionHub(ledger=helper_ledger)
        pool = ThreadPoolExecutor(max_workers=1, thread_name_prefix='E1E-unused-helper-premise-io')
        probe = SimpleNamespace(completions=helper_hub, ledger=helper_ledger,
                                channels={}, pending={}, io=pool,
                                store=Store(root / premise, helper_ledger),
                                global_log=None, global_close=None, root=root / premise)
        if premise == 'attempted-without-channel':
            probe.helper_attempts = {
                'J': {'attempted': True, 'status': 'CONSTRUCTION_UNKNOWN'},
                'R': {'attempted': False, 'status': 'NOT_ATTEMPTED'},
            }
        channel = io.StringIO()
        try:
            with redirect_stdout(channel):
                code = emit_failure(probe, 'CONTROLLED_HELPER_CONSTRUCTION_PREMISE', timeout=.05)
            lines = channel.getvalue().splitlines()
            witness = json.loads(lines[0])
            check(code == 2 and len(lines) == 1 and witness['status'] == 'PENDING' and
                  witness['helpers']['J']['started'] is None and
                  witness['helpers']['J']['exitObserved'] is False,
                  premise + '-return-does-not-invent-unattempted-helper-or-zero-ownership')
            if premise == 'missing-attempt-inventory':
                check(witness['helpers']['R']['started'] is None,
                      'absent-attempt-inventory-does-not-prove-either-helper-unstarted')
            else:
                check(witness['helpers']['R']['started'] is False,
                      'explicit-unattempted-R-remains-distinct-from-unknown-J')
            check(not helper_ledger.live and helper_hub.pending()['workersAlive'] == 0 and
                  not witness['logOpened'] and not witness['logCloseProven'],
                  premise + '-unknown-premise-test-starts-no-helper-worker-or-log')
            return_channels.append(copy.deepcopy(witness))
        finally:
            helper_hub.close(timeout=.2)
            pool.shutdown(wait=True, cancel_futures=True)

    report = dict(scope='E1E_PRODUCTION_LOGICAL_STARTUP_FAILURE_CHECKS_ONLY',
                  status='PASS', assertions=len(passed), checks=passed,
                  startupObservations=observations, originalReturnChannels=return_channels,
                  fixtureBytes=0, metadataBytesCreated=0, newHelpers=0, nativeCalls=0,
                  unresolvedControlledThreads=0,
                  limitations='Actual self-owned Thread start/join, production Hub/Flow/query/RPC gates and original failure stdout are checked. UNKNOWN evidence is captured before separately labelled controlled retirement. No Engine constructor, Native/Channel/helper/media or OS thread-exhaustion claim.')
    need(len(compact(report)) <= 131072, 'STARTUP_REPORT_BOUND')
    return report
