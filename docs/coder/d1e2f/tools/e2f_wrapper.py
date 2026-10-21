"""F01 decision replacement: precise evidence gates, no execution capability."""
from completion_evaluation import evaluate_completion
from resource_evaluation import evaluate_resources
from evidence_io import BATCH, SEAL_SHA, RESULT_SHA, PRECLOSE_SHA, digest


def evaluate_bound_bundle(bundle):
    """A supported evidence finding never changes the original run result."""
    completion = evaluate_completion(bundle['manifest'], bundle['preclose'], bundle['driver'],
                                     bundle['launcher'], bundle['global_events'])
    resources = evaluate_resources(bundle)
    bindings = bundle.get('sourceIntegrity', {})
    source_bound = (bindings.get('status') == 'VERIFIED' and bindings.get('immutableFiles') == 90 and
                    bindings.get('sealSha256') == SEAL_SHA and digest(bundle['sealBytes']) == SEAL_SHA)
    originals = bundle.get('originalInputs', {})
    source_bound = (source_bound and originals.get('resultManifestSha256') == RESULT_SHA and
                    originals.get('precloseSha256') == PRECLOSE_SHA)
    accepted = source_bound and completion.get('accepted') is True and resources.get('accepted') is True
    original = {'batchId': BATCH, 'driverStatus': bundle['driver'].get('status'),
                'launcherStatus': bundle['launcher'].get('status'),
                'firstFailure': bundle['driver'].get('firstFailure'),
                'originalGExitCode': bundle['launcher'].get('originalChildExitCode'),
                'originalToolExitCode': bundle['originalCallReceipt'].get('exit_code'),
                'reservationConsumed': bundle['launcher'].get('reservationConsumed'),
                'assertions': bundle['driver'].get('driverWitness', {}).get('assertions')}
    historical_failure = (original['driverStatus'] == original['launcherStatus'] == 'FAIL' and
                          original['originalGExitCode'] == 2 and original['originalToolExitCode'] == 1 and
                          original['firstFailure'] == 'INCOMPLETE_FULL_ROW_COUNT' and
                          original['reservationConsumed'] is True and original['assertions'] == 160)
    accepted = accepted and historical_failure
    reasons = []
    if not source_bound: reasons.append('ORIGINAL_SOURCE_OR_INPUT_BINDING_NOT_VERIFIED')
    if not historical_failure: reasons.append('ORIGINAL_FAIL_EXIT_OR_CONSUMPTION_CHANGED')
    if completion.get('accepted') is not True: reasons.append('COMPLETION_EVIDENCE_REJECTED')
    if resources.get('accepted') is not True: reasons.append('RESOURCE_IDENTITY_OUTPUT_OR_EXIT_EVIDENCE_REJECTED')
    return {'schema': 1, 'scope': 'EVIDENCE_REEVALUATION',
            'decision': 'SUPPORTED_ORIGINAL_TOOL_FACTS' if accepted else 'INSUFFICIENT_OR_INVALID_EVIDENCE',
            'accepted': bool(accepted), 'reasons': reasons, 'originalResult': original,
            'originalInputs': originals, 'sourceIntegrity': bindings,
            'completion': completion, 'resources': resources, 'readerUsage': bundle.get('readerUsage'),
            'F01': {'originalDefect': 'PF_PLUS_61_CHECKPOINTS_COMPARED_TO_61',
                    'replacement': 'EXACT_PF_SCENARIO_ORDER_COMPLETION_GC_RETURN_AND_INDEPENDENT_RESOURCE_OUTPUT_GATES',
                    'countOnlyAcceptanceForbidden': True},
            'activity': {'newActualAttempts': 0, 'newActualPasses': 0, 'newG': 0, 'helpersStarted': 0,
                         'newOSMetricSamples': 0, 'newMediaExecution': 0, 'compileInvocations': 0,
                         'originalEvidenceWrites': 0, 'executionCapabilityGranted': False},
            'interpretation': 'Independent read-only reevaluation of sealed E2E evidence; original FAIL and exits remain unchanged. This is not an original-batch PASS, a new actual result, D1/P0 acceptance or real-media permission.',
            'D1': 'NOT_PASSED', 'M0': 'NOT_STARTED', 'realMedia': 'DISABLED'}
