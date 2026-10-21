"""E3 coordinator-granted tester entry. Inspect consumes no reservation."""
import argparse
from pathlib import Path
import sys
sys.dont_write_bytecode = True

TOOLS = Path(__file__).absolute().parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))
from e3_admission import (AdmissionError, OnceAdmission, BATCH, encoded, decode,
                           inspect_receipt, require)

# Deliberate strong ownership on PENDING: no implicit Popen collection/close.
RETAINED_ORIGINALS = []


def completion_receipt(admission, backend, waiting, expected_freeze, child=None):
    result = dict(scope='E3_ORIGINAL_LAUNCHER_RESULT', batchId=BATCH,
                  expectedFreeze=expected_freeze, status='PENDING',
                  finalResultManifestRequired=True,
                  reservationConsumed=admission.reservation is not None,
                  originalChild=child, originalChildExitObserved=waiting.get('exitObserved') is True,
                  originalChildExitCode=waiting.get('exitCode'), stoppedWaitingOnly=waiting.get('stoppedWaitingOnly', False),
                  noInFlight=None, remaining='ORIGINAL_OWNERS_NOT_PROVEN', realExecutionAllowed=False, real61Run=False)
    if waiting.get('exitObserved'):
        if backend.exists('execution/driver-result.json'):
            driver = decode(backend.read('execution/driver-result.json'))
            claim = driver.get('claim', {})
            require(not claim or claim.get('child') == child, 'DRIVER_RETURN_CHILD_CHANGED')
            if claim:
                require(claim.get('expectedFreeze') == expected_freeze and claim.get('batchId') == BATCH and
                        claim.get('launcher') == admission.reservation.get('launcher'), 'DRIVER_RETURN_CLAIM_CHANGED')
            completed = (driver.get('completion', {}).get('accepted') is True and
                         driver.get('resources', {}).get('accepted') is True and driver.get('real61Run') is True)
            result.update(driverStatus=driver.get('status'), driverResult=driver,
                          status='PASS' if waiting.get('exitCode') == 0 and driver.get('status') == 'PASS' and completed else 'FAIL',
                          noInFlight=driver.get('noInFlight') is True and waiting.get('parentProcessHandleCloseProven') is True)
            result.pop('driverResult', None)
            result['driverResultFile'] = 'execution/driver-result.json'
            result['driverResultSummary'] = {key: driver.get(key) for key in ('scope', 'status', 'firstFailure', 'error', 'actualFullAttempt', 'noInFlight')}
            result['productionSummary'] = {key: driver.get('driverWitness', {}).get(key)
                                           for key in ('status', 'rows', 'assertions', 'privateCells', 'remainingResources', 'error')}
            result['completion'] = driver.get('completion')
            result['resources'] = driver.get('resources')
            result['realExecutionAllowed'] = bool(claim and claim.get('realExecutionAllowed') is True)
            if driver.get('status') == 'PENDING':
                result['status'] = 'PENDING'
            if not result['noInFlight']:
                result['status'] = 'PENDING'
            result['remaining'] = {} if result['noInFlight'] else 'CHILD_REPORTED_OR_UNKNOWN_OWNERS_RETAINED'
            result['real61Run'] = result['status'] == 'PASS'
        else:
            result.update(status='PENDING', noInFlight=None, remaining='NO_ORIGINAL_DRIVER_RECEIPT')
    result['wrapperFacts'] = backend.facts()
    return result


def run_once(admission, backend, expected_freeze, batch_id, grant_token=None):
    process = None; child = None; waited = False; spawn_entered = False; waiting = None; spawn_started = None
    prior_reservation = admission.reservation
    try:
        reservation = admission.reserve(expected_freeze, batch_id, grant_token)
        backend.stage_grant(grant_token)
        spawn_entered = True
        spawn_started = backend.now()
        process = backend.spawn(reservation, expected_freeze, batch_id)
        RETAINED_ORIGINALS.append((backend, process))
        child = backend.child_identity(process)
        admission.bind_launch(reservation, child)
        waited = True
        waiting = backend.wait_bounded(process, max(0, 200 - (backend.now() - spawn_started)))
        receipt = completion_receipt(admission, backend, waiting, expected_freeze, child)
    except BaseException as failure:
        if spawn_entered and process is None and getattr(backend, 'process', None) is not None:
            process = backend.process
            RETAINED_ORIGINALS.append((backend, process))
        if process is not None and not waited:
            waited = True
            waiting = backend.wait_bounded(process, max(0, 200 - (backend.now() - spawn_started)))
        receipt = dict(scope='E3_LAUNCH_REJECTED', batchId=BATCH, expectedFreeze=expected_freeze,
                       status='PENDING' if spawn_entered else 'FAIL',
                       error=type(failure).__name__ + ':' + str(failure)[:512],
                       reservationConsumed=admission.reservation is not None,
                       originalChild=child, originalChildExitObserved=bool(waiting and waiting.get('exitObserved')),
                       originalChildExitCode=waiting.get('exitCode') if waiting else None,
                       noInFlight=True if process is None and backend.facts().get('spawnCalls', 0) == 0 and backend.facts().get('identityRemaining') == 0 and not backend.facts().get('identityCloseUnknown') and not backend.facts().get('metadataRemaining') else None,
                       remaining='ORIGINAL_OWNERS_NOT_PROVEN' if spawn_entered else {},
                       realExecutionAllowed=False, wrapperFacts=backend.facts())
    if admission.reservation is not None and admission.reservation is not prior_reservation:
        backend.record_result(receipt, admission.freeze)
    if process is not None and receipt.get('originalChildExitObserved') and backend.facts().get('parentProcessHandleCloseProven') is True:
        RETAINED_ORIGINALS.remove((backend, process))
    return receipt


def main():
    parser = argparse.ArgumentParser()
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument('--run', action='store_true')
    modes.add_argument('--inspect', action='store_true')
    parser.add_argument('--expected-freeze')
    parser.add_argument('--batch-id')
    parser.add_argument('--grant-token')
    options = parser.parse_args()
    if not options.run:
        print(encoded(inspect_receipt()).decode('ascii')); return 0
    from e3_runtime import LocalBackend
    backend = LocalBackend(TOOLS.parent)
    admission = None
    try:
        batch = decode(backend.read('manifest/e3-batch.json')); backend.batch = batch
        admission = OnceAdmission(batch, backend)
        receipt = run_once(admission, backend, options.expected_freeze, options.batch_id, options.grant_token)
    except BaseException as failure:
        receipt = dict(scope='E3_ENTRY_REJECTED', status='FAIL', batchId=BATCH,
                       error=type(failure).__name__ + ':' + str(failure)[:512],
                       expectedFreeze=options.expected_freeze,
                       reservationConsumed=bool(admission and admission.reservation), noInFlight=None,
                       originalChild=getattr(backend, 'original_child', None), realExecutionAllowed=False)
        if RETAINED_ORIGINALS:
            receipt['status'] = 'PENDING'
    require(len(encoded(receipt)) <= 32768, 'LAUNCHER_RECEIPT_LIMIT')
    print(encoded(receipt).decode('ascii'), flush=True)
    # A PENDING notice never abandons the original owner or silently closes its
    # process handle. No collector thread, kill, replacement, or fresh sample.
    for owner, process in list(RETAINED_ORIGINALS):
        waiting = owner.retain_original(process)
        late = completion_receipt(admission, owner, waiting, options.expected_freeze,
                                  receipt.get('originalChild'))
        late['initialPendingPreserved'] = True
        owner.record_result(late, admission.freeze, late=True)
        if owner.parent_handle_close_unknown or owner.metadata_close_unknown:
            owner.hold_unknown_ownership()
        RETAINED_ORIGINALS.remove((owner, process))
    if backend.metadata_close_unknown or backend.close_unknown:
        backend.hold_unknown_ownership()
    if backend.spawn_calls > 0 and not backend.parent_handle_closed:
        backend.hold_unknown_ownership()
    return 0 if receipt['status'] == 'PASS' else 2


if __name__ == '__main__':
    sys.exit(main())
