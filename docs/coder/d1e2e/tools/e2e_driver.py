"""Separate E2E orchestration; the immutable controller.run stays closed."""
import argparse
from pathlib import Path
import sys
sys.dont_write_bytecode = True

TOOLS = Path(__file__).absolute().parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))
from e2e_admission import (AdmissionError, OnceAdmission, ROOT_NAME, decode,
                           encoded, inspect_receipt, require)

# A launcher retaining Popen cannot retain G's Engine/Channel/native owners.
# Keep the original graph in this original G until all ownership is proven.
RETAINED_ENGINES = []


def run_claimed(admission, expected_freeze, batch_id, execute):
    """Injectable ordering guard: execute cannot run before durable claim."""
    claim = admission.claim(expected_freeze, batch_id)
    return execute(claim)


def quiescence(witness):
    hub = witness.get('callbackHub', witness.get('hub', {}))
    workers = hub.get('workers', {})
    if set(workers) != {'notify', 'deadline'}:
        return False
    for worker in workers.values():
        if worker.get('unknown') is not False or worker.get('alive') is not False or worker.get('startInProgress') is not False:
            return False
        joined = (worker.get('joined') is True and worker.get('entered') is True and worker.get('exited') is True and
                  worker.get('joinReturned') is True and worker.get('creditReleased') is True and
                  worker.get('releaseProof') == 'THREAD_JOIN_PROVEN')
        never = (worker.get('creditReleased') is True and worker.get('releaseProof') == 'THREAD_NOT_STARTED_PROVEN')
        not_allocated = all(worker.get(key) is False for key in
                            ('creditReserved', 'reserveEntered', 'threadCreated', 'startEntered', 'entered'))
        if not (joined or never or not_allocated):
            return False
    helpers = witness.get('helpers')
    if helpers is None:
        helpers = witness.get('logClose', {}).get('exitedHelpers', {}) if isinstance(witness.get('logClose'), dict) else {}
        helper_done = set(helpers) == {'J', 'R'} and all(proof.get('exited') is True and proof.get('code') == 0 and
                            type(proof.get('pid')) is int and proof['pid'] > 0 and isinstance(proof.get('instance'), str) and
                            bool(proof['instance']) for proof in helpers.values())
    else:
        helper_done = set(helpers) == {'J', 'R'}
        for value in helpers.values():
            attempt = value.get('attempt') or {}
            absent = (value.get('started') is False and value.get('status') == 'NOT_ATTEMPTED' and
                      attempt.get('attempted') is False and attempt.get('status') == 'NOT_ATTEMPTED')
            proof = value.get('exitProof') or {}
            exited = (value.get('exitObserved') is True and proof.get('exited') is True and proof.get('code') == 0 and
                      proof.get('pid') == value.get('pid') and proof.get('instance') == value.get('instance') and
                      type(proof.get('pid')) is int and proof['pid'] > 0 and bool(proof.get('instance')))
            helper_done = helper_done and (absent or exited)
    close = witness.get('logClose') if isinstance(witness.get('logClose'), dict) else {}
    remaining = witness.get('remainingResources', close.get('remainingResources'))
    log_known = close.get('closed') is True or (witness.get('logOpened') is False and witness.get('logOwnershipPending') is False)
    runtime = witness.get('runtimeObservation', {})
    native_known = witness.get('nativePending') == [] or close.get('closed') is True and runtime.get('nativeQueryPending') is False
    return (witness.get('status') in ('PASS', 'FAIL') and remaining == 0 and log_known and native_known and
            not witness.get('logOwnershipPending', False) and
            hub.get('lifecycle') == 'CLOSED' and hub.get('workersAlive') == 0 and
            hub.get('remainingCredits') == [] and hub.get('ownershipPending') is False and
            all(hub.get(key) == 0 for key in ('cells', 'queued', 'active', 'monitorInFlight')) and helper_done)


def execute_production(backend, claim):
    """Only the original small orchestration is adapted; no production patch."""
    memory = backend.fresh_memory()
    backend.create_new('execution/child-memory.json', memory)
    if (memory.get('status') != 'MEMORY_READY' or memory.get('stopAcceptance') is not False or
            memory.get('minimumAvailablePhysicalBytes') != 2147483648 or
            type(memory.get('observation', {}).get('availablePhysicalBytes')) is not int or
            memory['observation']['availablePhysicalBytes'] < 2147483648):
        return 2, dict(scope='E2E_CHILD_FRESH_MEMORY_REJECTED', status='FAIL', claim=claim,
                       error='CHILD_FRESH_MEMORY_REJECTED_NO_ENGINE', noInFlight=True,
                       actualFullAttempt=False, helpersStarted=0, mockMetricsUsed=False,
                       realExecutionAllowed=False, wrapperFacts=backend.facts())
    source = str(backend.base/'src')
    if source not in sys.path:
        sys.path.insert(0, source)
    from controller import fixtures, stop_failure
    from gengine import Engine
    from scenarios import Scenarios
    from phases import preflight, Cleanup
    manifest = decode(backend.read('manifest/branches.json'))
    require(len(manifest['branches']) == 61 and manifest['limits']['seconds'] == 180, 'ORIGINAL_FULL_MANIFEST')
    root = backend._relative('selfcheck/' + ROOT_NAME, True)
    require(not root.exists(), 'FIXTURE_ROOT_CREATE_NEW_REQUIRED')
    fixtures(root)  # Original mkdir(exist_ok=False), original authored bytes only.
    engine = Engine.__new__(Engine)
    RETAINED_ENGINES.append(engine)
    first_error = None
    witness = None
    code = 2
    stop_called = False
    def stop_once(error):
        nonlocal stop_called
        if stop_called:
            return 2, dict(status='PENDING', error=error, stopFailureAlreadyAttempted=True,
                           remainingResources=None, nativePending='ORIGINAL_OWNERS_NOT_PROVEN')
        stop_called = True
        try:
            return stop_failure(engine, error, timeout=1)
        except BaseException as stop_error:
            return 2, dict(status='PENDING', error=error,
                           stopFailureError=type(stop_error).__name__ + ':' + str(stop_error)[:160],
                           remainingResources=None, nativePending='ORIGINAL_OWNERS_NOT_PROVEN')
    try:
        Engine.__init__(engine, root, manifest, synthetic_observer_mock=False)
        engine.actual_regression_claim = claim
        driver = Scenarios(engine)
        try:
            preflight(engine)
            ordered = [row for row in manifest['branches'] if row['id'] not in ('P10-D', 'P10-C')]
            ordered += [row for row in manifest['branches'] if row['id'] in ('P10-D', 'P10-C')]
            for row in ordered:
                engine.begin(row['id']); driver.run(row['id']); engine.flow.finish()
        except BaseException as failure:
            first_error = type(failure).__name__ + ':' + str(failure)[:512]
        startup = engine.completions.pending()
        unsafe = (startup['lifecycle'] != 'RUNNING' or any(name not in engine.channels for name in ('J', 'R')) or
                  any(not future.done() for future in engine.pending.values()) or
                  any(worker['unknown'] for worker in startup['workers'].values()))
        if first_error is not None and unsafe:
            code, witness = stop_once(first_error)
        else:
            try:
                cleanup = Cleanup(engine); cleanup.run()
                report = dict(status='PASS' if first_error is None else 'FAIL', error=first_error,
                              rows=engine.results, assertions=engine.assertions)
                witness = cleanup.finish(report)
                code = 0 if first_error is None else 1
            except BaseException as failure:
                cleanup_error = type(failure).__name__ + ':' + str(failure)[:512]
                first_error = first_error or cleanup_error
                code, witness = stop_once(first_error)
    except BaseException as failure:
        first_error = first_error or type(failure).__name__ + ':' + str(failure)[:512]
        if hasattr(engine, 'completions'):
            code, witness = stop_once(first_error)
        else:
            # Engine's IO executor has no submitted jobs before completions is
            # assigned. Preserve a conservative partial-init failure receipt.
            if hasattr(engine, 'io'):
                engine.io.shutdown(wait=False, cancel_futures=True)
            ledger = getattr(engine, 'ledger', None)
            witness = dict(status='PENDING', error=first_error, constructorIncomplete=True,
                           remainingResources=len(ledger.live) if ledger is not None else None,
                           nativePending='CONSTRUCTOR_NOT_FULLY_OBSERVED', helpersStarted=0,
                           logOpened=False, logCloseProven=False)
    require(witness is not None, 'ORIGINAL_DRIVER_WITNESS_REQUIRED')
    if witness['status'] == 'PASS' and witness.get('rows') != 61:
        code = 2
        first_error = 'INCOMPLETE_FULL_ROW_COUNT'
        witness = dict(witness, status='FAIL')
    drained = quiescence(witness)
    if drained:
        RETAINED_ENGINES.remove(engine)
    return code, dict(scope='E2E_ACTUAL_SELF_OWNED_DRIVER', status=witness['status'] if drained else 'PENDING',
                      firstFailure=first_error, claim=claim, productionScopePreserved=True,
                      driverWitness=witness, noInFlight=drained,
                      actualFullAttempt=True, mockMetricsUsed=False, realExecutionAllowed=False,
                      wrapperFacts=backend.facts())


def main():
    parser = argparse.ArgumentParser()
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument('--run', action='store_true')
    modes.add_argument('--inspect', action='store_true')
    parser.add_argument('--expected-freeze')
    parser.add_argument('--batch-id')
    options = parser.parse_args()
    if not options.run:
        print(encoded(inspect_receipt()).decode('ascii')); return 0
    from e2e_runtime import LocalBackend
    backend = LocalBackend(TOOLS.parent)
    receipt = None
    execute_entered = False
    def execute(claim):
        nonlocal execute_entered
        execute_entered = True
        return execute_production(backend, claim)
    try:
        batch = decode(backend.read('manifest/e2e-batch.json')); backend.batch = batch
        admission = OnceAdmission(batch, backend)
        code, receipt = run_claimed(admission, options.expected_freeze, options.batch_id, execute)
    except BaseException as failure:
        code = 2
        receipt = dict(scope='E2E_DRIVER_ADMISSION_REJECTED', status='PENDING' if execute_entered else 'FAIL',
                       error=type(failure).__name__ + ':' + str(failure)[:512],
                       noInFlight=not execute_entered and backend.identity_owned == 0 and not backend.close_unknown and not backend.metadata_owned,
                       actualFullAttempt=execute_entered, helpersStarted=None if execute_entered else 0, realExecutionAllowed=False,
                       wrapperFacts=backend.facts())
    # Driver never writes a root/claim on a failed authorization path. The
    # existing parent-owned execution namespace is its sole return channel.
    if backend.exists('execution'):
        backend.create_new('execution/driver-result.json', receipt)
    if receipt.get('status') == 'PENDING' or RETAINED_ENGINES or backend.metadata_close_unknown or backend.close_unknown:
        backend.hold_unknown_ownership()
    return code


if __name__ == '__main__':
    sys.exit(main())
