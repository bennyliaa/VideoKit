"""E2 configuration/admission and injected-metric checks; no real IO execution.

Reads only this package's JSON configuration through load_bundle. All process
metrics below come from explicitly synthetic dict readers, never an OS reader.
No media bytes/stat calls, helper, Engine, Native, fixture or run directory is
created by this sub-suite. Passing checks cannot authorize an execution batch.
"""
from __future__ import annotations

import copy
import json
from unittest.mock import patch

from admission import load_bundle, validate_profile, inspect_admission, request_real_run
from gcore import Refused, compact, need, sha
from profile_bindings import synthetic_profile, real_profile, boundary_for, require_synthetic
from runtime_metrics import MetricObserver


def run_checks(root, manifest):
    bundle = load_bundle()
    passed = []
    observations = []

    def check(condition, name):
        need(condition, 'E2C_CHECK:' + name)
        passed.append(name)

    def refuses(action, reason, name):
        try:
            action()
        except Refused as error:
            check(str(error) == reason, name)
            return
        raise AssertionError('Missing refusal: ' + name)

    def invalid(mutator, name, mutate_manifest=False):
        candidate = copy.deepcopy(bundle)
        candidate_manifest = copy.deepcopy(manifest)
        mutator(candidate_manifest if mutate_manifest else candidate)
        result = validate_profile(candidate, candidate_manifest)
        check(result['valid'] is False and bool(result['errors']), name)

    original_bundle = sha(compact(bundle))
    original_manifest = sha(compact(manifest))
    baseline = validate_profile(bundle, manifest)
    check(baseline['valid'] is True and not baseline['errors'],
          'frozen-real-profile-configuration-is-structurally-valid')
    from types import SimpleNamespace
    from gengine import Ops
    from gcore import Native,Ledger
    guard=dict(identity='1:2:3',length=4096,mtime100ns=123,identityStatus='OPENED_HANDLE_PROVEN',disposition='OWNED_OPEN_RETRYABLE')
    gate=SimpleNamespace(e=SimpleNamespace(object=lambda key:guard),rid=lambda *args:'guard',source_version=lambda:'v1')
    original=dict(guard,identityStatus='PROVEN',version='v1')
    check(Ops.source_identity(gate,original),'opened-J-identity-matches-live-guard')
    for field,value in [('identity','1:2:4'),('length',4097),('mtime100ns',124),('identityStatus','PATH_HASH_ONLY')]:
        refuses(lambda field=field,value=value:Ops.source_identity(gate,dict(original,**{field:value})),'BLOCKED_VERSION_NOT_PROVEN','opened-identity-mismatch-before-byte-'+field)
    guard['disposition']='CLOSED_PROVEN'
    refuses(lambda:Ops.source_identity(gate,original),'BLOCKED_VERSION_NOT_PROVEN','closed-guard-cannot-authorize-a-byte')
    guard['disposition']='OWNED_OPEN_RETRYABLE'
    class FailedQuery:
        closes=0
        def CreateFileW(self,*args):return 1234
        def GetFileInformationByHandle(self,*args):return 0
        def CloseHandle(self,*args):self.closes+=1;return 1
    native=Native.__new__(Native);native.ledger=Ledger();native.k=FailedQuery();native.owned={};native.close_unknown=set()
    proof=native.open('self-owned-mock','NO_FILE_OPENED',None)
    check(proof['identityStatus']=='BLOCKED_VERSION_NOT_PROVEN' and proof['disposition']=='OWNED_OPEN_RETRYABLE' and len(native.ledger.live)==1 and 'self-owned-mock' in native.owned,'failed-G-query-keeps-original-allocation-for-cleanup')
    native.close('self-owned-mock')
    check(native.k.closes==1 and not native.ledger.live and not native.owned,'failed-G-query-original-object-cleaned-once')
    expected_lengths = {'L': 3212959911, 'C': 4096, 'Z': 0}
    expected_sha = {
        'L': '28af909ce8d9f9e1431253715e07bbfa9024aa8963882a000ee7a15807622b26',
        'C': 'c0d66c6510904af0301dc1d923a403a1983f446e5a326299074f1b6a88a75405',
        'Z': 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
    }
    check({alias: bundle['inputs']['inputs'][alias]['historical']['bytes']
           for alias in expected_lengths} == expected_lengths,
          'real-L-C-Z-historical-lengths-are-exact')
    check({alias: bundle['inputs']['inputs'][alias]['historical']['sha256']
           for alias in expected_sha} == expected_sha,
          'historical-hash-identities-retained-without-rehash')
    windows = bundle['inputs']['largeFileWindows']
    check(windows['boundaryBytes'] == 2147483648 and
          [(window['offset'], window['requestedBytes']) for window in windows['windows']] ==
          [(2147418112, 65536), (2147450880, 65536),
           (2147483648, 65536), (3212894375, 65536)],
          'real-four-windows-cross-exact-2GiB-and-large-file-tail')
    check(len(bundle['cases']['cases']) == 61 and
          {case['id'] for case in bundle['cases']['cases']} ==
          {case['id'] for case in manifest['branches']} and
          bundle['cases']['limits'] == manifest['limits'],
          'all61-identities-and-original-budgets-preserved')
    check(bundle['cases']['plannedRequestUsage'] ==
          {'inputBytes': 1573492, 'inputCalls': 59, 'validationBytes': 128} and
          manifest['limits']['control'] == 452 and manifest['limits']['controlHard'] == 544 and
          manifest['limits']['query'] == 101 and manifest['limits']['inputBytes'] == 1573522 and
          manifest['limits']['inputCalls'] == 59,
          'planned-real-request-usage-does-not-spend-unused-allocation')

    synthetic = synthetic_profile()
    real = real_profile(bundle)
    check(synthetic['kind'] == 'SYNTHETIC' and synthetic['lengths'] ==
          {'L': 131072, 'C': 4096, 'Z': 0} and boundary_for(synthetic) == 65536,
          'synthetic-geometry-explicit-and-scaled')
    check(real['kind'] == 'REAL_IO' and real['lengths'] == expected_lengths and
          boundary_for(real) == 2147483648,
          'real-geometry-explicit-and-not-scaled')
    for profile, expected in [(synthetic, 65536), (real, 2147483648)]:
        for root_name in ('D:/outside-any-selfcheck/real',
                          'D:/misleading/selfcheck/renamed-real',
                          'D:/synthetic-but-named-real/outputs'):
            renamed = copy.deepcopy(profile)
            renamed['root'] = root_name
            renamed['name'] = 'SelfCheck' if profile['kind'] == 'REAL_IO' else 'REAL_IO'
            check(boundary_for(renamed) == expected,
                  profile['kind'] + '-boundary-never-inferred-from-' + root_name)
    refuses(lambda: require_synthetic(real), 'REAL_EXECUTION_DISABLED_E2C_ADMISSION',
            'real-profile-cannot-enter-synthetic-binding')
    bad_geometry = copy.deepcopy(synthetic)
    bad_geometry['boundary'] = 2147483648
    refuses(lambda: boundary_for(bad_geometry), 'PROFILE_BOUNDARY',
            'synthetic-label-cannot-carry-real-geometry')
    bad_geometry = copy.deepcopy(real)
    bad_geometry['boundary'] = 65536
    refuses(lambda: boundary_for(bad_geometry), 'PROFILE_BOUNDARY',
            'real-label-cannot-carry-scaled-geometry')

    invalid(lambda b: b['inputs']['inputs']['L']['historical'].update(bytes=3212959910),
            'altered-historical-large-length-invalid')
    invalid(lambda b: b['cases']['inputs']['L'].update(lengthBytes=131072),
            'scaled-large-length-cannot-enter-real-case-profile')
    invalid(lambda b: b['cases'].update(boundaryBytes=65536),
            'scaled-real-case-boundary-invalid')
    invalid(lambda b: b['inputs']['largeFileWindows']['windows'][2].update(offset=65536),
            'real-window-offset-cannot-use-synthetic-boundary')
    invalid(lambda b: b['cases']['limits'].update(controlHard=545),
            'case-profile-cannot-expand-hard-control-budget')
    invalid(lambda b: b['cases']['limits'].update(inputBytes=1573523),
            'case-profile-cannot-expand-input-allocation')
    invalid(lambda m: m['limits'].update(controlHard=545),
            'manifest-mutation-cannot-redefine-approved-hard-budget', mutate_manifest=True)
    invalid(lambda b: b['cases']['cases'][0].update(nonquery=5),
            'case-profile-cannot-add-a-control-to-reviewed-row')
    invalid(lambda b: b['cases']['cases'].__setitem__(-1, copy.deepcopy(b['cases']['cases'][0])),
            'duplicate-case-id-cannot-replace-missing-case')
    invalid(lambda b: b['cases']['plannedRequestUsage'].update(inputCalls=60),
            'planned-usage-cannot-hide-an-extra-media-read')
    invalid(lambda b: (b['inputs']['inputs']['L']['historical'].update(sha256='0' * 64),
                       b['cases']['inputs']['L'].update(historicalSha256='0' * 64)),
            'matching-but-unapproved-historical-hash-cannot-rebind-input')

    # These windows are appended while declared row/global usage stays intact.
    # The earlier skip-on-not-True behavior would omit their real IO entirely,
    # making them stronger negatives than removing the flag on a charged window
    # that would already fail an unrelated derived-total comparison.
    def append_unaccounted_window(candidate, marker, omit=False):
        row = candidate['cases']['cases'][0]
        extra = copy.deepcopy(row['realIO']['windows'][0])
        extra.update(offsetBytes=0, requestedBytes=1, expectedActualBytes=1,
                     delegateCalls=1)
        if omit:
            extra.pop('inputRequestCharged', None)
        else:
            extra['inputRequestCharged'] = marker
        row['realIO']['windows'].append(extra)

    invalid(lambda b: append_unaccounted_window(b, False),
            'uncharged-one-byte-delegate-window-cannot-hide-behind-unchanged-usage')
    invalid(lambda b: append_unaccounted_window(b, None, omit=True),
            'missing-charge-flag-cannot-hide-appended-native-IO')
    for marker in (0, 'true'):
        invalid(lambda b, marker=marker: append_unaccounted_window(b, marker),
                'non-bool-charge-flag-cannot-hide-appended-native-IO-' + repr(marker))

    baseline_inspection = inspect_admission(bundle, manifest)
    check(baseline_inspection['configurationValid'] is True and
          baseline_inspection['executionAllowed'] is False and
          bool(baseline_inspection['blockers']),
          'valid-configuration-is-distinct-from-execution-admission')
    for approval in (True, {'approved': True},
                     {'approved': True, 'batchId': 'SYNTHETIC-FAKE-GRANT',
                      'mode': 'EXECUTE_REAL_IO', 'thresholdsApproved': True}):
        inspection = inspect_admission(bundle, manifest, approval=approval)
        check(inspection['executionAllowed'] is False and bool(inspection['blockers']),
              'untrusted-approval-shape-never-opens-real-execution-' + str(approval))
    fake_policy = copy.deepcopy(bundle['runtime'])
    fake_policy.update(state='APPROVED', executionAuthorized=True)
    inspection = inspect_admission(bundle, manifest, runtime_policy=fake_policy)
    check(inspection['executionAllowed'] is False and
          'RUNTIME_THRESHOLDS_UNAPPROVED' in inspection['blockers'] and
          inspection['configurationValid'] is False,
          'editing-policy-state-cannot-create-coordinator-threshold-approval')
    stat_metadata = {alias: copy.deepcopy(item['currentStat'])
                     for alias, item in bundle['inputs']['inputs'].items()}
    for alias in stat_metadata:
        stat_metadata[alias].update(versionProven=True,
                                    sha256=expected_sha[alias], sameObject=True)
    stat_inspection = inspect_admission(bundle, manifest, stat_metadata=stat_metadata)
    check(stat_inspection['executionAllowed'] is False and
          any('VERSION' in reason.upper() for reason in stat_inspection['blockers']),
          'matching-stat-and-historical-hash-do-not-prove-current-version')
    check(all(not item['currentContentVerified'] and item['currentVersionGuarantee'] == 'UNPROVEN'
              for item in bundle['inputs']['inputs'].values()),
          'inspection-does-not-upgrade-input-version-evidence')
    for level, namespace_required in [('NAMESPACE_DURABLE', False),
                                       ('OS_DATA_SYNC_ACK', True),
                                       ('NAMESPACE_DURABLE', True)]:
        candidate = copy.deepcopy(bundle)
        output_case = next(case for case in candidate['cases']['cases'] if case['id'] == 'Q01-SEQ')
        output_case['requiredDurability'].update(level=level, namespaceRequired=namespace_required)
        inspection = inspect_admission(candidate, manifest,
                                       approval={'approved': True, 'namespaceApproved': True})
        admission = next(case for case in inspection['caseAdmissions'] if case['id'] == 'Q01-SEQ')
        check(admission['status'] == 'NOT_RUN_DURABILITY_UNPROVEN' and
              inspection['executionAllowed'] is False,
              'namespace-requirement-never-downgraded-' + level + '-' + str(namespace_required))
        if namespace_required and level == 'OS_DATA_SYNC_ACK':
            check(inspection['configurationValid'] is False and
                  any('DURABILITY_DOWNGRADE' in error for error in inspection['errors']),
                  'OS-sync-level-cannot-satisfy-declared-namespace-requirement')
    check(all(case['productVariant'].get('admission') == 'NOT_RUN_DURABILITY_UNPROVEN'
              for case in bundle['cases']['cases']
              if case['productVariant'].get('requiredDurability') == 'NAMESPACE_DURABLE'),
          'protocol-probe-configuration-keeps-product-namespace-P0-blocked')

    calls = {'media': 0, 'helper': 0}

    def forbidden_media(*args, **kwargs):
        calls['media'] += 1
        raise AssertionError('E2 configuration request attempted media access')

    def forbidden_helper(*args, **kwargs):
        calls['helper'] += 1
        raise AssertionError('E2 configuration request attempted helper launch')

    for batch_id in ('E2C-UNAUTHORIZED-CONFIGURATION-PROBE', 'SelfCheck', '../not-a-batch'):
        with patch('pathlib.Path.mkdir', side_effect=AssertionError('E2 gate tried mkdir')) as mkdir, \
             patch('pathlib.Path.open', side_effect=AssertionError('E2 gate tried file open')) as path_open, \
             patch('builtins.open', side_effect=AssertionError('E2 gate tried file open')) as file_open:
            code, report = request_real_run(batch_id, bundle, manifest,
                                            media_reader=forbidden_media,
                                            helper_launcher=forbidden_helper)
        check(code == 2 and report['executionAllowed'] is False and
              calls == {'media': 0, 'helper': 0} and mkdir.call_count == 0 and
              path_open.call_count == 0 and file_open.call_count == 0,
              'real-execution-entry-closes-before-any-file-or-helper-' + batch_id)
        observations.append(dict(batchId=batch_id, code=code,
                                 executionAllowed=report['executionAllowed']))

    # Runtime observer checks are appended below using the actual frozen policy
    # schema. No read_process/Windows reader is imported or invoked here.
    runtime_results = _runtime_checks(bundle, check)
    check(sha(compact(bundle)) == original_bundle and sha(compact(manifest)) == original_manifest,
          'all-inspections-leave-frozen-config-and-manifest-unchanged')
    report = dict(scope='E2C_CONFIG_ADMISSION_AND_INJECTED_OBSERVER_CHECKS_ONLY',
                  status='PASS', assertions=len(passed), checks=passed,
                  executionGateObservations=observations,
                  runtimeObservations=runtime_results,
                  mediaBytesRead=0, mediaStatCalls=0, newHelpers=0, nativeCalls=0,
                  fixtureBytes=0, metadataBytesCreated=0,
                  limitations='Only package configuration, pure admission/profile functions, fatal side-effect sentinels and synthetic metric dictionaries. No real execution grant, OS metric sampling, media read/stat/hash, helper or real PF is proved by these checks.')
    need(len(compact(report)) <= 131072, 'E2C_REPORT_BOUND')
    return report


def _runtime_checks(bundle, check):
    policy = copy.deepcopy(bundle['runtime'])
    identities = {
        'G': {'pid': 101, 'creationTime100ns': 10001, 'owner': 'G-original-synthetic'},
        'J': {'pid': 102, 'creationTime100ns': 10002, 'owner': 'J-original-synthetic'},
        'R': {'pid': 103, 'creationTime100ns': 10003, 'owner': 'R-original-synthetic'},
    }
    values = {
        'G': {'threads': 4, 'handles': 32, 'workingSetBytes': 33554432, 'privateBytes': 25165824},
        'J': {'threads': 12, 'handles': 64, 'workingSetBytes': 134217728, 'privateBytes': 100663296},
        'R': {'threads': 8, 'handles': 48, 'workingSetBytes': 67108864, 'privateBytes': 50331648},
    }
    results = []

    def fixture(mutator=None, approval=None, synthetic=True, candidate_policy=None):
        counts = {'calls': 0}
        role_by_pid = {identity['pid']: role for role, identity in identities.items()}

        def reader(identity):
            counts['calls'] += 1
            role = role_by_pid[identity['pid']]
            result = dict(values[role], pid=identity['pid'],
                          creationTime100ns=identity['creationTime100ns'])
            if mutator:
                mutator(role, result, counts)
            return result

        if synthetic:
            reader.synthetic = True
        observer = MetricObserver(copy.deepcopy(identities), reader,
                                  copy.deepcopy(candidate_policy or policy), approval=approval)
        return observer, counts

    def test_fixture(mutator=None, candidate_policy=None):
        return fixture(mutator, approval={'mode': 'SYNTHETIC_POLICY_TEST_ONLY'},
                       candidate_policy=candidate_policy)

    def stopped(observer, counts, result, label, later=1000):
        check(result['status'] == 'STOP_PENDING' and result['stopAcceptance'] is True and
              bool(result['reasons']) and result['peaksAreSampled'] is True,
              label + '-stops-admission-with-concrete-reason')
        before = counts['calls']
        again = observer.sample(later)
        check(again['status'] == 'STOP_PENDING' and again['stopAcceptance'] is True and
              counts['calls'] == before,
              label + '-stop-is-latched-without-further-reader-call')
        results.append(dict(check=label, status=result['status'], reasons=result['reasons'],
                            syntheticReaderCalls=before))

    for approval in (None, True, {'approved': True},
                     {'state': 'APPROVED', 'executionAuthorized': True}):
        observer, counts = fixture(approval=approval)
        result = observer.sample(0)
        check(result['status'] == 'NOT_ADMITTED' and result['stopAcceptance'] is True and
              counts['calls'] == 0 and bool(result['reasons']),
              'PROPOSED-thresholds-not-approved-by-' + str(approval))
    observer, counts = fixture(approval={'mode': 'SYNTHETIC_POLICY_TEST_ONLY'}, synthetic=False)
    result = observer.sample(0)
    check(result['status'] == 'NOT_ADMITTED' and counts['calls'] == 0,
          'test-approval-cannot-enable-an-unmarked-OS-like-reader')

    observer, counts = test_fixture()
    baseline = observer.sample(0)
    check(baseline['status'] == 'OBSERVED' and not baseline['stopAcceptance'] and
          baseline['scope'] == 'SYNTHETIC_POLICY_CHECK' and counts['calls'] == 3 and
          baseline['peaksAreSampled'] is True,
          'test-only-approval-measures-three-synthetic-original-instances')
    early = observer.sample(policy['intervalSeconds'] / 2)
    check(early['status'] == 'OBSERVED' and early.get('sampled') is False and counts['calls'] == 3,
          'too-early-observer-tick-does-not-increase-native-or-reader-budget')
    normal = observer.sample(policy['intervalSeconds'])
    check(normal['status'] == 'OBSERVED' and not normal['stopAcceptance'] and counts['calls'] == 6,
          'next-scheduled-synthetic-cycle-preserves-original-instance-baseline')

    metric_names = ('threads', 'handles', 'workingSetBytes', 'privateBytes')
    for metric in metric_names:
        for invalid_value in ('missing', None):
            def bad_metric(role, result, counts, metric=metric, invalid_value=invalid_value):
                if role == 'J':
                    if invalid_value == 'missing':
                        result.pop(metric)
                    else:
                        result[metric] = invalid_value

            observer, counts = test_fixture(bad_metric)
            stopped(observer, counts, observer.sample(0),
                    'required-J-' + metric + '-' + str(invalid_value))
    for label, invalid_value in [('nan', float('nan')), ('infinite', float('inf')), ('negative', -1)]:
        def invalid_number(role, result, counts, invalid_value=invalid_value):
            if role == 'G':
                result['workingSetBytes'] = invalid_value

        observer, counts = test_fixture(invalid_number)
        stopped(observer, counts, observer.sample(0), 'invalid-metric-' + label)

    for field in ('pid', 'creationTime100ns', 'owner'):
        def wrong_identity(role, result, counts, field=field):
            if role == 'J':
                result[field] = ('different-owner' if field == 'owner' else result[field] + 1)

        observer, counts = test_fixture(wrong_identity)
        stopped(observer, counts, observer.sample(0), 'original-instance-mismatch-' + field)

    def over_absolute(role, result, counts):
        if role == 'G':
            result['handles'] = policy['limits']['G']['handles'] + 1

    observer, counts = test_fixture(over_absolute)
    stopped(observer, counts, observer.sample(0), 'absolute-handle-threshold')
    phase = {'afterBaseline': False}

    def over_delta(role, result, counts):
        if role == 'G' and phase['afterBaseline']:
            result['handles'] += policy['limits']['G']['deltaHandles'] + 1

    observer, counts = test_fixture(over_delta)
    baseline = observer.sample(0)
    check(baseline['status'] == 'OBSERVED', 'delta-threshold-starts-from-real-synthetic-baseline')
    phase['afterBaseline'] = True
    stopped(observer, counts, observer.sample(1), 'baseline-delta-handle-threshold')

    observer, counts = test_fixture()
    observer.sample(0)
    before = counts['calls']
    gap_result = observer.sample(policy['maxGapSeconds'] + 1)
    check(counts['calls'] == before, 'overlong-sampling-gap-stops-before-another-read')
    stopped(observer, counts, gap_result, 'sampling-gap-exceeded')

    observer, counts = test_fixture()
    all_observed = True
    for index in range(policy['maxSamples']):
        result = observer.sample(index * policy['intervalSeconds'])
        all_observed = all_observed and result['status'] == 'OBSERVED' and not result['stopAcceptance']
    check(all_observed and counts['calls'] == 3 * policy['maxSamples'],
          'observer-accepts-only-finite-proposed-number-of-synthetic-cycles')
    before = counts['calls']
    exhausted = observer.sample(policy['maxSamples'] * policy['intervalSeconds'])
    check(counts['calls'] == before, 'observer-sample-credit-exhaustion-does-not-read-again')
    stopped(observer, counts, exhausted, 'sample-count-exhausted')

    check(policy['managedLimits'] == {'osResources': 24, 'mediaHandles': 6, 'buffers64KiB': 8} and
          policy['state'] == 'APPROVED_TOOL_STRATEGY' and policy['executionAuthorized'] is False and
          policy['maxRecordBytes'] == 128 and policy['maxLogBytes'] == 26752,
          'runtime-proposals-do-not-replace-managed-hard-limits-or-log-credit')
    return results
