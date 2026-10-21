"""Batch-parameterized completion evidence; no IO or authorization capability.

The in-G gate proves checkpoints/GC/trace, never original G exit. The original
launcher must additionally prove child exit, closure, and output hash inventory.
No historical batch hash, original assertion total, or count-only acceptance.
"""
import hashlib
import json
import math
import re

APPROVED_SCENARIOS = (
    'P01-N1', 'P01-N2', 'P01-N3', 'P01-N4', 'P02-EOF', 'P02-ZERO',
    'P01-S1', 'P01-S2', 'P01-S3', 'P01-S4', 'P03-RAW', 'P03-MEDIA',
    'P04-SEQ', 'P04-CPU', 'P05-SHORT7', 'P06-ZERO', 'P07-EARLY',
    'P08-LATEOPEN', 'P09-CANCEL', 'P09-TIMEOUT', 'P10-A', 'P10-B',
    'P11-FUTURE', 'P11-SEALED', 'P12-OLDOPEN', 'P12-NOTICE', 'P12-CHANGED',
    'P13-SEQ', 'P13-SEEK', 'Q09-OPEN2', 'Q09-CLAIM', 'Q09-SECOND',
    'Q09-REPLAY', 'Q09-PLAN', 'Q09-SOURCE', 'Q09-PRESET', 'Q01-SEQ',
    'Q05-STREAM', 'Q06-LOST', 'Q08-READY', 'Q07-READYFIRST', 'Q04-DUP',
    'Q02-RANDOM', 'Q08-VALIDATOR', 'Q04-CLOSEACK', 'Q08-WRITER',
    'Q05-SPACEFAIL', 'Q08-UNKNOWN', 'Q08-DRAIN', 'Q07-TAKEFIRST',
    'Q09-W1', 'Q09-W2', 'Q09-W3', 'Q09-W4', 'Q09-W5', 'Q09-W0',
    'Q03-RANDOM', 'Q03-VERIFY', 'Q09-ALIAS', 'P10-D', 'P10-C')

# These are the data calls in the unchanged, approved Scenarios implementation.
# Source rows otherwise have exactly inputCalls D slots. Zero length has its
# explicit bridge slot, and output seeks/writes/validation are separate D slots.
DATA_OVERRIDES = {'P02-ZERO': 1, 'Q01-SEQ': 4, 'Q04-DUP': 1,
                  'Q02-RANDOM': 7, 'Q08-VALIDATOR': 1, 'Q04-CLOSEACK': 1,
                  'Q05-SPACEFAIL': 2, 'Q07-TAKEFIRST': 2}
EXPECTED_ERRORS = {
    'P06-ZERO/d01': 'INVALID_PROVIDER_RESULT', 'P07-EARLY/d01': 'EARLY_EOF',
    'P10-B/n08': 'STALE_REVISION', 'P11-SEALED/n09': 'SESSION_RELEASED',
    'P12-OLDOPEN/n19': 'SESSION_RELEASED', 'Q09-SECOND/n01': 'CLAIM_CONFLICT',
    'Q09-SECOND/n02': 'CLAIM_CONFLICT', 'Q09-PLAN/n01': 'INTENT_CONFLICT',
    'Q09-SOURCE/n01': 'INTENT_CONFLICT', 'Q09-PRESET/n01': 'INTENT_CONFLICT',
    'Q05-SPACEFAIL/d02': 'OUTPUT_SPACE_INSUFFICIENT',
    'Q07-TAKEFIRST/n13': 'STALE_OWNER', 'Q03-RANDOM/n01': 'RANDOM_REQUIRED',
    'Q03-VERIFY/n01': 'VALIDATION_REQUIRED', 'Q09-ALIAS/n01': 'INPUT_ALIAS',
    'P10-D/n11': 'EXHAUSTED', 'P10-C/n02': 'CLOSE_NOT_RETRYABLE',
    'P10-C/n04': 'CLOSE_NOT_RETRYABLE'}
RACE_ERROR_SLOTS = ('P10-A/n06', 'P10-A/n07')
WAITING_ERRORS = {'P08-LATEOPEN/n03': 'CANCELLED',
                  'P09-CANCEL/d01': 'CANCELLED', 'P09-TIMEOUT/d01': 'SOURCE_TIMEOUT'}


def _integer(value, minimum=0):
    return type(value) is int and value >= minimum


def _number(value):
    if type(value) not in (int, float):
        return False
    try:
        return math.isfinite(value) and value >= 0
    except OverflowError:
        return False


def _sha(value):
    return isinstance(value, str) and re.fullmatch('[0-9a-f]{64}', value) is not None


class _Checks:
    def __init__(self):
        self.reasons = []

    def need(self, value, code):
        if not value and code not in self.reasons:
            self.reasons.append(code)
        return bool(value)


def _specs(manifest, check):
    branches = manifest.get('branches')
    if not check.need(type(branches) is list and len(branches) == 61 and
                      all(type(row) is dict for row in branches), 'MANIFEST_SCENARIO_SCHEMA'):
        return None
    ids = [row.get('id') for row in branches]
    if not check.need(all(type(value) is str for value in ids) and len(set(ids)) == 61 and
                      set(ids) == set(APPROVED_SCENARIOS), 'MANIFEST_APPROVED_IDS'):
        return None
    ordered = [value for value in ids if value not in ('P10-D', 'P10-C')] + ['P10-D', 'P10-C']
    check.need(ordered == list(APPROVED_SCENARIOS) and manifest.get('executionOrder') == ordered,
               'MANIFEST_APPROVED_ORDER')
    check.need([row.get('id') for row in manifest.get('phases', {}).get('PF', [])] ==
               ['PF/n%02d' % index for index in range(1, 17)], 'MANIFEST_PF_SLOTS')
    check.need([row.get('id') for row in manifest.get('phases', {}).get('GC', [])] ==
               ['GC/n%02d' % index for index in range(1, 33)], 'MANIFEST_GC_SLOTS')
    specs = {'PF': dict(nonquery=16, queriesNew=0, queriesReplay=0, seconds=20, inputCalls=2)}
    specs.update({row['id']: row for row in branches})
    valid = True
    for name, row in specs.items():
        for key in ('nonquery', 'queriesNew', 'queriesReplay', 'seconds', 'inputCalls'):
            valid = check.need(_integer(row.get(key)) and row[key] <= 180, 'MANIFEST_ROW_SCHEMA:' + name) and valid
    return specs if valid else None


def _checkpoint_rows(manifest, preclose, check, profile_kind):
    specs = _specs(manifest, check)
    rows = preclose.get('rows')
    if specs is None or not check.need(type(rows) is list and len(rows) <= 128 and
                                       all(type(row) is dict for row in rows), 'CHECKPOINT_SCHEMA'):
        return specs, {}, []
    ids = [row.get('branch') for row in rows]
    check.need(len(ids) == 62, 'CHECKPOINT_COUNT')
    check.need(ids.count('PF') == 1 and bool(ids) and ids[0] == 'PF', 'PF_MISSING_OR_NOT_FIRST')
    if not check.need(all(type(value) is str for value in ids), 'CHECKPOINT_ID_SCHEMA'):
        return specs, {}, rows
    check.need(len(set(ids)) == len(ids), 'CHECKPOINT_DUPLICATE')
    check.need(set(ids) == {'PF', *APPROVED_SCENARIOS}, 'CHECKPOINT_EXACT_IDS')
    check.need(ids == ['PF', *APPROVED_SCENARIOS], 'CHECKPOINT_ORDER')
    by_id = {}
    for row in rows:
        name = row['branch']
        if name not in specs:
            continue
        by_id[name] = row
        spec = specs[name]
        wanted_scope = 'REAL_IO_TOOL_CHECKPOINT_ONLY' if profile_kind == 'REAL_IO' else 'SYNTHETIC_CHECKPOINT_ONLY'
        check.need(row.get('scope') == wanted_scope, 'CHECKPOINT_SCOPE:' + name)
        for observed, expected in (('controls', 'nonquery'), ('queryNew', 'queriesNew'),
                                   ('queryReplay', 'queriesReplay'), ('seconds', 'seconds')):
            check.need(_integer(row.get(observed)) and row[observed] == spec.get(expected),
                       'CHECKPOINT_' + observed.upper() + ':' + name)
        expected_data = DATA_OVERRIDES.get(name, spec.get('inputCalls'))
        check.need(_integer(row.get('dataSteps')) and row['dataSteps'] == expected_data,
                   'CHECKPOINT_DATA_STEPS:' + name)
        check.need(_number(row.get('elapsedSeconds')) and _integer(spec.get('seconds')) and
                   row['elapsedSeconds'] <= spec['seconds'], 'CHECKPOINT_TIME:' + name)
        if name.startswith('P01-S'):
            check.need(row.get('windowOutcome') == 'UNFILLED' and type(row.get('windowBytesObserved')) is int and
                       row['windowBytesObserved'] == 4, 'LEGAL_UNFILLED_WINDOW:' + name)
        # Original rows are appended only after Flow.finish succeeds. Explicit
        # incomplete/failure markers, if injected into a copy, cannot override it.
        check.need('completed' not in row or row['completed'] is True, 'CHECKPOINT_INCOMPLETE:' + name)
        check.need('status' not in row or row['status'] in ('DONE', 'COMPLETED'), 'CHECKPOINT_STATUS:' + name)
    check.need(preclose.get('status') == 'PASS' and preclose.get('error') is None,
               'PRECLOSE_COMPLETION_NOT_SUCCESSFUL')
    return specs, by_id, rows


def _events(global_events, check):
    if not check.need(type(global_events) is list and len(global_events) <= 4096, 'EVENT_LIST_SCHEMA'):
        return []
    events = []
    for event in global_events:
        if type(event) is dict and 'id' in event:
            if check.need(isinstance(event['id'], str) and len(event['id']) <= 64,
                          'EVENT_ID_SCHEMA'):
                events.append(event)
        elif type(event) is dict and 'runtimeMetricFormat' in event or type(event) is list:
            continue
        else:
            check.need(False, 'EVENT_SCHEMA')
    return events


def _waiting_return(operation, preclose, check):
    history = preclose.get('cellHistory')
    if not check.need(type(history) is list and len(history) <= 64, 'CELL_HISTORY_SCHEMA'):
        return
    matches = [entry for entry in history if type(entry) is dict and entry.get('operation') == operation]
    if not check.need(len(matches) == 1, 'WAITING_ORIGINAL_AUDIT:' + operation):
        return
    cell = matches[0]
    check.need(all(cell.get(key) is True for key in ('native_done', 'gated', 'released', 'notification_done',
                                                   'notifier_quiescent', 'archived')) and
               cell.get('retained') is False and cell.get('discarded') is True and
               type(cell.get('deliveries')) is int and cell['deliveries'] == 0 and
               _integer(cell.get('callbacks_registered')) and
               _integer(cell.get('callbacks_finished')) and cell.get('callbacks_finished') == cell['callbacks_registered'] and
               cell.get('callback_errors') == [] and
               cell.get('error_type') == 'Refused' and cell.get('error_message') == WAITING_ERRORS[operation],
               'WAITING_ORIGINAL_RETURN_NOT_PROVEN:' + operation)


def _operation_records(specs, by_id, preclose, events, check):
    if specs is None:
        return
    index = {}; expected = set()
    for position, event in enumerate(events):
        index.setdefault(event['id'], []).append((position, event))
    race_errors = 0
    for name in ('PF', *APPROVED_SCENARIOS):
        spec = specs.get(name, {})
        if not all(_integer(spec.get(key)) for key in ('nonquery', 'inputCalls')):
            continue
        data_steps = DATA_OVERRIDES.get(name, spec['inputCalls'])
        for prefix, count, kind in (('n', spec['nonquery'], 'N'), ('d', data_steps, 'D')):
            for number in range(1, count + 1):
                operation = name + '/' + prefix + '%02d' % number
                expected.add(operation)
                records = index.get(operation, [])
                phases = [entry.get('phase') for _, entry in records]
                terminal = 'WAITING_COMPLETION' if operation in WAITING_ERRORS else 'DONE'
                wanted = [terminal] if operation == 'PF/n01' else ['ADMITTED', terminal]
                check.need(phases == wanted, 'OPERATION_COMPLETION:' + operation)
                check.need(all(entry.get('kind') == kind for _, entry in records), 'OPERATION_KIND:' + operation)
                if not records or phases[-1:] != [terminal]:
                    continue
                last = records[-1][1]
                error = last.get('error')
                if operation in RACE_ERROR_SLOTS:
                    check.need(error in ('', 'STALE_REVISION'), 'UNAPPROVED_OPERATION_ERROR:' + operation)
                    race_errors += error == 'STALE_REVISION'
                else:
                    check.need(error == EXPECTED_ERRORS.get(operation, ''), 'UNAPPROVED_OPERATION_ERROR:' + operation)
                check.need(_sha(last.get('resultDigest')), 'OPERATION_RESULT_DIGEST:' + operation)
                if terminal == 'WAITING_COMPLETION':
                    _waiting_return(operation, preclose, check)
    check.need(race_errors == 1, 'ORIGINAL_RETRY_RACE_OUTCOME')
    observed = {event['id'] for event in events if not event['id'].startswith('GC/')}
    check.need(observed == expected, 'OPERATION_EXACT_IDS')
    # Concurrent operations may return in either order, but serial rows must not
    # be interleaved or completed after the next row/GC starts.
    order = {name: position for position, name in enumerate(('PF', *APPROVED_SCENARIOS, 'GC'))}
    row_order = [order.get(event['id'].split('/')[0], -1) for event in events]
    check.need(all(left <= right for left, right in zip(row_order, row_order[1:])), 'OPERATION_ROW_ORDER')


def _gc(manifest, preclose, driver, events, check):
    records = [event for event in events if event['id'].startswith('GC/')]
    wanted = [(f'GC/n{number:02}', phase) for number in range(1, 32) for phase in ('ADMITTED', 'DONE')]
    wanted.append(('GC/n32', 'READY_TO_CLOSE'))
    check.need([(event['id'], event.get('phase')) for event in records] == wanted, 'GC_EXACT_COMPLETION_SEQUENCE')
    for event in records:
        if event.get('phase') in ('ADMITTED', 'DONE'):
            check.need(event.get('kind') == 'N', 'GC_OPERATION_KIND')
        if event.get('phase') == 'DONE':
            check.need(event.get('error') == '' and _sha(event.get('resultDigest')), 'GC_OPERATION_NOT_SUCCESSFUL')
        if event.get('id') == 'GC/n32':
            check.need(event.get('scope') == 'RETURN_CHANNEL_WITNESS', 'GC_N32_INTENT_SCOPE')
    witness = driver
    check.need(preclose.get('logClose') == 'PENDING_RETURN_CHANNEL' or
               preclose.get('logClose') == witness.get('logClose'), 'REPORT_CLOSE_BINDING')
    close = witness.get('logClose', {})
    check.need(type(close) is dict and close.get('id') == 'GC/n32' and close.get('closed') is True and
               close.get('method') == 'flush/fsync/close actually returned' and
               type(close.get('remainingResources')) is int and close['remainingResources'] == 0,
               'GC_N32_ORIGINAL_RETURN_REQUIRED')


def _assertions(preclose, witness, check):
    trace = preclose.get('assertionEvidence')
    if not check.need(type(trace) is list and 0 < len(trace) <= 1024, 'ASSERTION_TRACE_SCHEMA'):
        return 0
    allowed = {'INIT', 'PF', 'GC', *APPROVED_SCENARIOS}
    check.need(all(type(item) is dict and set(item) == {'seq', 'row', 'label'} and
                   type(item.get('seq')) is int and item['seq'] == index and
                   type(item.get('row')) is str and item['row'] in allowed and
                   type(item.get('label')) is str and 0 < len(item['label']) <= 160
                   for index, item in enumerate(trace, 1)), 'ASSERTION_TRACE_SEQUENCE')
    sha = hashlib.sha256(json.dumps(trace, sort_keys=True, separators=(',', ':'), ensure_ascii=True).encode('ascii')).hexdigest()
    check.need(all(type(value) is int and value == len(trace) for value in
                   (preclose.get('assertions'), witness.get('assertions'), witness.get('assertionEvidenceCount'))) and
               witness.get('assertionEvidenceSha256') == sha, 'ASSERTION_TRACE_RETURN_BINDING')
    return len(trace)


def _usage(manifest, preclose, witness, rows, check):
    usage = preclose.get('usage', {})
    caps = manifest.get('limits', {})
    branches = manifest.get('branches', [])
    limits = dict(n=caps.get('nonquery'), qn=sum(row.get('queriesNew', 0) for row in branches),
                  qr=sum(row.get('queriesReplay', 0) for row in branches), ib=caps.get('inputBytes'),
                  ic=caps.get('inputCalls'), v=caps.get('validationBytes'), targets=caps.get('targets'),
                  records=caps.get('records'), credit=caps.get('outputBytes'))
    check.need(type(usage) is dict and usage == witness.get('usage') and set(usage) == set(limits) and
               all(_integer(usage.get(key)) and _integer(cap) and usage[key] <= cap for key, cap in limits.items()),
               'USAGE_RETURN_BINDING_AND_CAPS')
    check.need(usage.get('n') == sum(row.get('controls', 0) for row in rows) + 32 and
               usage.get('qn') == sum(row.get('queryNew', 0) for row in rows) and
               usage.get('qr') == sum(row.get('queryReplay', 0) for row in rows), 'ROW_AND_GC_USAGE_TOTALS')
    check.need(limits['n'] + limits['qn'] + limits['qr'] == caps.get('control') and
               usage.get('ic') == limits['ic'] and usage.get('targets') == limits['targets'] and
               usage.get('records') == limits['records'], 'APPROVED_ALLOCATION_COMPLETED')


def evaluate_completion(manifest, preclose, witness, claim, global_events):
    """Evaluate immutable-decoded evidence without mutating any input.

    Full byte/seal/output integrity and original resource identity are separate
    mandatory gates. This result must never be used alone as a batch verdict.
    """
    check = _Checks(); specs = None; rows = []; by_id = {}; events = []
    assertion_count = 0
    if check.need(all(type(value) is dict for value in (manifest, preclose, witness, claim)), 'COMPLETION_INPUT_SCHEMA'):
        try:
            kind = claim.get('profile')
            check.need(kind in ('REAL_IO', 'SYNTHETIC'), 'CLAIM_PROFILE_REQUIRED')
            specs, by_id, rows = _checkpoint_rows(manifest, preclose, check, kind)
            events = _events(global_events, check)
            _operation_records(specs, by_id, preclose, events, check)
            _gc(manifest, preclose, witness, events, check)
            assertion_count = _assertions(preclose, witness, check)
            _usage(manifest, preclose, witness, rows, check)
            check.need(witness.get('status') == preclose.get('status') == 'PASS' and preclose.get('error') is None,
                       'ORIGINAL_TOOL_COMPLETION_REQUIRED')
            check.need(type(witness.get('rows')) is int and witness['rows'] == len(rows) and
                       len(rows) == len(APPROVED_SCENARIOS) + 1, 'RETURN_CHECKPOINT_COUNT_BINDING')
            preclose_sha = hashlib.sha256(json.dumps(preclose, separators=(',', ':'), ensure_ascii=True).encode()).hexdigest()
            check.need(witness.get('precloseSummary') == 'result-before-close.json' and
                       witness.get('precloseSummarySha') == preclose_sha and witness.get('root') == claim.get('rootName'),
                       'PRECLOSE_ORIGINAL_BYTES_RETURN_BINDING')
            check.need(claim == preclose.get('actualRegressionAdmission') == witness.get('actualRegressionAdmission') and
                       type(claim.get('batchId')) is str and bool(claim['batchId']) and
                       type(claim.get('rootName')) is str and bool(claim['rootName']) and
                       _sha(claim.get('expectedFreeze')) and _sha(claim.get('profileSha256')) and
                       claim.get('observerMode') == 'ACTUAL_OS_OBSERVER' and claim.get('mockMetricsUsed') is False,
                       'COMPLETION_CLAIM_BINDING')
            parent, child = claim.get('launcher', {}), claim.get('child', {})
            check.need(all(_integer(identity.get(key), 1) for identity in (parent, child)
                           for key in ('pid', 'creationTime100ns')) and parent['pid'] != child['pid'],
                       'ORIGINAL_PARENT_CHILD_REQUIRED')
            geometry = claim.get('profileGeometry', {})
            lengths = geometry.get('lengths', {})
            boundary = geometry.get('boundary')
            approved_geometry = manifest.get('profile', {}).get('real' if kind == 'REAL_IO' else 'synthetic', {})
            check.need(_integer(boundary, 65536) and set(lengths) == {'L', 'C', 'Z'} and
                       all(_integer(lengths.get(alias)) for alias in ('L', 'C', 'Z')) and
                       lengths['L'] >= boundary + 65536 and lengths['C'] == 4096 and lengths['Z'] == 0 and
                       boundary == approved_geometry.get('boundary') and
                       all(lengths[alias] == approved_geometry.get(alias) for alias in ('L', 'C', 'Z')),
                       'PROFILE_GEOMETRY_REQUIRED')
        except (KeyError, TypeError, ValueError, OverflowError, AttributeError):
            check.need(False, 'COMPLETION_EVIDENCE_SCHEMA')
    elapsed = [row.get('elapsedSeconds') for row in rows if type(row) is dict and _number(row.get('elapsedSeconds'))]
    gc_done = {event['id'] for event in events if event.get('phase') == 'DONE' and event.get('error') == '' and
               event.get('kind') == 'N' and event['id'] in {f'GC/n{number:02}' for number in range(1, 32)}}
    final_close = witness.get('logClose', {}) if type(witness) is dict else {}
    n32_returned = (type(final_close) is dict and final_close.get('closed') is True and final_close.get('id') == 'GC/n32' and
                    final_close.get('method') == 'flush/fsync/close actually returned' and
                    type(final_close.get('remainingResources')) is int and final_close['remainingResources'] == 0)
    return dict(scope='BATCH_COMPLETION_EVALUATION', accepted=not check.reasons,
                reasons=check.reasons, executionAllowed=False,
                facts=dict(preflightCheckpoints=sum(row.get('branch') == 'PF' for row in rows),
                           scenarioCheckpoints=sum(row.get('branch') in APPROVED_SCENARIOS for row in rows),
                           reportedCheckpoints=len(rows), approvedScenarioIds=list(APPROVED_SCENARIOS),
                           requiredGcNonquerySlots=32, gcNonquerySlots=len(gc_done) + int(n32_returned),
                           gcN32OriginalReturnProven=n32_returned, gcN32RequiresOriginalReturn=True,
                           checkpointElapsedSecondsSum=sum(elapsed), observedAssertions=assertion_count,
                           queryTimingEvidence='ORIGINAL_FLOW_FINISH_0_1_SECOND_QUERY_GUARD_AND_ROW_DEADLINE',
                           perQueryDurationRecorded=False, fullRuntimeDurationProvenByThisModule=False,
                           independentResourceAndOutputHashGatesRequired=True))
