"""Separate E3 claimed orchestration; controller.run remains closed."""
import argparse
import math
import os
from pathlib import Path
import sys
sys.dont_write_bytecode = True

TOOLS = Path(__file__).absolute().parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))
from e3_admission import (AdmissionError, OnceAdmission, ROOT_NAME, RuntimePermit, decode,
                           encoded, inspect_receipt, require)
from completion_evaluation import evaluate_completion

# A launcher retaining Popen cannot retain G's Engine/Channel/native owners.
# Keep the original graph in this original G until all ownership is proven.
RETAINED_ENGINES = []


def run_claimed(admission, expected_freeze, batch_id, grant_token, execute):
    """Injectable ordering guard: execute cannot run before durable claim."""
    permit = admission.claim(expected_freeze, batch_id, grant_token)
    return execute(permit)


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
        helper_done = set(helpers) == {'J', 'R'} and all(proof.get('exited') is True and type(proof.get('code')) is int and proof['code'] == 0 and
                            type(proof.get('pid')) is int and proof['pid'] > 0 and isinstance(proof.get('instance'), str) and
                            bool(proof['instance']) for proof in helpers.values())
    else:
        helper_done = set(helpers) == {'J', 'R'}
        for value in helpers.values():
            attempt = value.get('attempt') or {}
            absent = (value.get('started') is False and value.get('status') == 'NOT_ATTEMPTED' and
                      attempt.get('attempted') is False and attempt.get('status') == 'NOT_ATTEMPTED')
            proof = value.get('exitProof') or {}
            exited = (value.get('exitObserved') is True and proof.get('exited') is True and type(proof.get('code')) is int and proof['code'] == 0 and
                      proof.get('pid') == value.get('pid') and proof.get('instance') == value.get('instance') and
                      type(proof.get('pid')) is int and proof['pid'] > 0 and bool(proof.get('instance')))
            helper_done = helper_done and (absent or exited)
    close = witness.get('logClose') if isinstance(witness.get('logClose'), dict) else {}
    remaining = witness.get('remainingResources', close.get('remainingResources'))
    log_known = close.get('closed') is True or (witness.get('logOpened') is False and witness.get('logOwnershipPending') is False)
    runtime = witness.get('runtimeObservation', {})
    native_known = (witness.get('nativePending') == [] if 'nativePending' in witness else
                    close.get('closed') is True and runtime.get('nativeQueryPending') is False)
    return (witness.get('status') in ('PASS', 'FAIL') and type(remaining) is int and remaining == 0 and log_known and native_known and
            not witness.get('logOwnershipPending', False) and
            hub.get('lifecycle') == 'CLOSED' and type(hub.get('workersAlive')) is int and hub['workersAlive'] == 0 and
            hub.get('remainingCredits') == [] and hub.get('ownershipPending') is False and
            all(type(hub.get(key)) is int and hub[key] == 0 for key in ('cells', 'queued', 'active', 'monitorInFlight')) and helper_done)


def resource_gate(witness, policy, claim, production_seconds=None):
    """Pure original-fact gate. Samples are read, never resampled or rebased."""
    reasons = []
    def need(condition, code):
        if not condition and code not in reasons:
            reasons.append(code)
    def number(value):
        return type(value) in (int, float) and math.isfinite(value) and value >= 0
    try:
        need(quiescence(witness), 'ORIGINAL_OWNERS_NOT_QUIESCENT')
        need(number(production_seconds) and production_seconds <= 180, 'ORIGINAL_180_SECOND_COMPLETION_BOUND')
        hub = witness.get('callbackHub', {})
        need(hub.get('blocked') is None and hub.get('startupError') is None and
             type(hub.get('notices')) is int and hub['notices'] >= 0,
             'ORIGINAL_CALLBACK_FAILURE_OR_UNKNOWN')
        runtime = witness.get('runtimeObservation', {}); observation = runtime.get('observation', {})
        reader = runtime.get('reader', {}); fresh = runtime.get('freshMemory', {})
        need(runtime.get('wired') is True and runtime.get('started') is True and runtime.get('finished') is True and
             runtime.get('nativeQueryPending') is False and runtime.get('mode') == 'ACTUAL_OS_OBSERVER' and
             runtime.get('mockMetricsUsed') is False, 'ORIGINAL_RUNTIME_OBSERVER_REQUIRED')
        need(observation.get('status') == 'OBSERVED' and observation.get('stopAcceptance') is False and
             observation.get('reasons') == [] and observation.get('observationFinished') is True and
             observation.get('runtimePolicyApproved') is True and
             observation.get('gBaselineAnchor') == 'ORIGINAL_PROCESS_BEFORE_PF_NOT_RESET', 'RUNTIME_STOP_OR_UNKNOWN')
        need(type(observation.get('samples')) is int and 1 <= observation['samples'] <= policy['maxSamples'] and
             number(observation.get('maxObservedGapSeconds')) and observation['maxObservedGapSeconds'] <= policy['maxGapSeconds'] and
             number(observation.get('sampleDurationSeconds')) and observation['sampleDurationSeconds'] <= policy['sampleDeadlineSeconds'],
             'ORIGINAL_SAMPLE_BOUNDS')
        need(fresh.get('status') == 'MEMORY_READY' and fresh.get('stopAcceptance') is False and
             type(fresh.get('observation', {}).get('availablePhysicalBytes')) is int and
             fresh['observation']['availablePhysicalBytes'] >= policy['minimumAvailablePhysicalBytes'], 'ORIGINAL_FRESH_MEMORY')
        identities = runtime.get('originalIdentities', {}); baselines = observation.get('baselines', {}); peaks = observation.get('peaks', {})
        need(set(identities) == set(baselines) == set(peaks) == {'G', 'J', 'R'}, 'ORIGINAL_BASELINES_REQUIRED')
        need(all(type(identity.get(key)) is int and identity[key] > 0 for identity in identities.values()
                 for key in ('pid', 'creationTime100ns')) and
             all(type(identity.get('owner')) is str and bool(identity['owner']) for identity in identities.values()),
             'ORIGINAL_ROLE_CREATION_IDENTITIES')
        need(all(identities.get('G', {}).get(key) == claim.get('child', {}).get(key)
                 for key in ('pid', 'creationTime100ns')), 'ORIGINAL_G_IDENTITY_REQUIRED')
        need(len({value['pid'] for value in identities.values()}) == 3, 'ORIGINAL_ROLE_ALIAS')
        delta = dict(threads='deltaThreads', handles='deltaHandles', workingSetBytes='deltaWorkingSetBytes', privateBytes='deltaPrivateBytes')
        exited = witness.get('logClose', {}).get('exitedHelpers', {})
        for role in ('G', 'J', 'R'):
            identity = identities.get(role, {}); baseline = baselines.get(role, {}); peak = peaks.get(role, {})
            need(all(baseline.get(key) == identity.get(key) for key in ('pid', 'creationTime100ns', 'owner')),
                 'BASELINE_IDENTITY:' + role)
            for key, difference in delta.items():
                need(number(baseline.get(key)) and number(peak.get(key)) and
                     baseline[key] <= peak[key] <= policy['limits'][role][key] and
                     peak[key] - baseline[key] <= policy['limits'][role][difference], 'SAMPLED_LIMIT:' + role + ':' + key)
            if role != 'G':
                proof = exited.get(role, {}); retired = observation.get('retired', {}).get(role, {})
                need(proof == retired and proof.get('pid') == identity.get('pid') and
                     proof.get('instance') == identity.get('owner') and proof.get('exited') is True and proof.get('code') == 0,
                     'ORIGINAL_HELPER_EXIT:' + role)
        need(type(reader.get('openedHandles')) is int and type(reader.get('closedHandles')) is int and
             0 <= reader['openedHandles'] == reader['closedHandles'] and reader.get('closeUnknown') is False and
             reader.get('observerCreditHeld') is False and type(reader.get('maximumOwnedHandlesObserved')) is int and
             0 <= reader['maximumOwnedHandlesObserved'] <= 1,
             'ORIGINAL_OBSERVER_HANDLE_RETURN')
        need(witness.get('metadataCommitStatus') == 'HEALTHY' and type(witness.get('metadataUnknownRequestedBytes')) is int and
             witness['metadataUnknownRequestedBytes'] == 0 and
             type(witness.get('metadataPeak')) is int and 0 <= witness['metadataPeak'] <= 3178496,
             'ORIGINAL_METADATA_BOUND')
        ledger = witness.get('ledgerPeaks', {})
        need(all(type(ledger.get(key)) is int and 0 <= ledger[key] <= cap
                 for key, cap in (('os', 24), ('media', 6), ('buffers', 8))), 'ORIGINAL_LEDGER_BOUNDS')
        cells = witness.get('privateCells', {})
        need(type(cells.get('total')) is int and 0 <= cells['total'] <= 64 and
             type(cells.get('peak')) is int and 0 <= cells['peak'] <= 8 and
             all(type(cells.get(key)) is int for key in ('active', 'retained', 'archived')) and
             cells['active'] == cells['retained'] == 0 and cells['archived'] == cells['total'],
             'ORIGINAL_PRIVATE_CELLS_RETURN')
        need(hub.get('notices') == cells.get('total'), 'ORIGINAL_NOTIFICATION_AUDIT_COUNT')
        identity_queries = witness.get('identityQueries', {})
        need(all(type(identity_queries.get(key)) is int and identity_queries[key] == 0 for key in ('extraRPCs', 'extraSourceBytes')) and
             identity_queries.get('perActorCap') == 512 and
             all(type(identity_queries.get(role)) is int and 0 < identity_queries[role] <= 512 for role in ('G', 'J', 'R')),
             'ORIGINAL_OPENED_IDENTITY_QUERY_BOUNDS')
    except (KeyError, TypeError, ValueError, AttributeError, OverflowError):
        need(False, 'RESOURCE_EVIDENCE_SCHEMA')
    return dict(scope='E3_ORIGINAL_RESOURCE_GATE', accepted=not reasons, reasons=reasons,
                productionElapsedSeconds=production_seconds, sampledPeaksOnly=True, additionalSamples=0, executionAllowed=False)


def execute_production(backend, permit, profile):
    """Only the original small orchestration is adapted; no production patch."""
    require(type(permit) is RuntimePermit, 'DURABLE_ORIGINAL_CLAIM_REQUIRED')
    claim = permit.receipt
    memory = backend.fresh_memory()
    backend.create_new('execution/child-memory.json', memory)
    if (memory.get('status') != 'MEMORY_READY' or memory.get('stopAcceptance') is not False or
            memory.get('minimumAvailablePhysicalBytes') != 2147483648 or
            type(memory.get('observation', {}).get('availablePhysicalBytes')) is not int or
            memory['observation']['availablePhysicalBytes'] < 2147483648):
        return 2, dict(scope='E3_CHILD_FRESH_MEMORY_REJECTED', status='FAIL', claim=claim,
                       error='CHILD_FRESH_MEMORY_REJECTED_NO_ENGINE', noInFlight=True,
                       actualFullAttempt=False, helpersStarted=0, mockMetricsUsed=False,
                       realExecutionAllowed=False, wrapperFacts=backend.facts())
    source = str(backend.base/'src')
    if source not in sys.path:
        sys.path.insert(0, source)
    from controller import stop_failure
    from gengine import Engine
    from scenarios import Scenarios
    from phases import preflight, Cleanup
    manifest = decode(backend.read('manifest/branches.json'))
    require(len(manifest['branches']) == 61 and manifest['limits']['seconds'] == 180, 'ORIGINAL_FULL_MANIFEST')
    root = backend.create_output_root(permit, profile)
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
        Engine.__init__(engine, root, manifest, profile=profile, execution_claim=permit, synthetic_observer_mock=False)
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
    drained = quiescence(witness)
    completion = dict(accepted=False, reasons=['ORIGINAL_COMPLETION_NOT_AVAILABLE'])
    production_seconds = max(0, backend.now() - engine.budget.started) if hasattr(engine, 'budget') else None
    resources = resource_gate(witness, decode(backend.read('profiles/runtime-policy.json')), claim, production_seconds)
    if drained and witness.get('status') == 'PASS':
        try:
            raw = backend.read_owned_evidence('runs/' + ROOT_NAME + '/result-before-close.json')
            events = backend.read_owned_evidence('runs/' + ROOT_NAME + '/global.log').splitlines()
            require(events and events[0] == b'E3 LIMITED REAL IO TOOL INTEGRATION', 'ORIGINAL_EVENT_LOG_SCOPE')
            global_events = [decode(line) for line in events[1:] if line]
            completion = evaluate_completion(manifest, decode(raw), witness, claim, global_events)
        except BaseException as failure:
            completion = dict(accepted=False, reasons=['COMPLETION_READ_OR_SCHEMA:' + type(failure).__name__])
    accepted = first_error is None and completion['accepted'] is True and resources['accepted'] is True and drained
    if not accepted and first_error is None:
        first_error = 'COMPLETION_OR_RESOURCE_GATE_REJECTED'
    code = 0 if accepted else 2
    if drained:
        RETAINED_ENGINES.remove(engine)
    return code, dict(scope='E3_CLAIMED_REAL_IO_DRIVER', status=('PASS' if accepted else 'FAIL') if drained else 'PENDING',
                      firstFailure=first_error, claim=claim, productionScopePreserved=True,
                      driverWitness=witness, noInFlight=drained,
                      completion=completion, resources=resources, real61Run=accepted,
                      actualFullAttempt=True, mockMetricsUsed=False, realExecutionAllowed=True,
                      wrapperFacts=backend.facts())


def main():
    parser = argparse.ArgumentParser()
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument('--run', action='store_true')
    modes.add_argument('--inspect', action='store_true')
    parser.add_argument('--expected-freeze')
    parser.add_argument('--batch-id')
    options = parser.parse_args()
    # Removed before importing Engine/Channel: helpers cannot inherit the grant.
    grant_token = os.environ.pop('E3_GRANT_TOKEN', None)
    if not options.run:
        print(encoded(inspect_receipt()).decode('ascii')); return 0
    from e3_runtime import LocalBackend
    backend = LocalBackend(TOOLS.parent)
    receipt = None
    execute_entered = False
    def execute(permit):
        nonlocal execute_entered
        execute_entered = True
        return execute_production(backend, permit, admission.profile)
    try:
        batch = decode(backend.read('manifest/e3-batch.json')); backend.batch = batch
        admission = OnceAdmission(batch, backend)
        code, receipt = run_claimed(admission, options.expected_freeze, options.batch_id, grant_token, execute)
    except BaseException as failure:
        code = 2
        receipt = dict(scope='E3_DRIVER_ADMISSION_REJECTED', status='PENDING' if execute_entered else 'FAIL',
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
