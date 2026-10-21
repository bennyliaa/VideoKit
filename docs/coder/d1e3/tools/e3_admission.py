"""Prepared E3 authority; no IO, process, or media access on import.

The public commitment is not a grant. Only the separately retained secret,
released by the coordinator after review, can consume this one prepared batch.
No Boolean approval document, historical run, or synthetic name grants REAL_IO.
"""
import hashlib
import hmac
import json
from pathlib import PureWindowsPath
import re

BATCH = 'D1-E3-11a896d3c2c34483ba2dff60fa63f5c8'
ROOT_NAME = 'e3-11a896d3c2c34483ba2dff60fa63f5c8'
PACKAGE = 'D:/CodexProjects/VideoKit/docs/coder/d1e3'
OUTPUT_ROOT = PACKAGE + '/runs/' + ROOT_NAME
PREFIX = 'docs/coder/d1e3/'
STATE = 'PREPARED_PENDING_COORDINATOR_HANDOFF'
GRANT_COMMITMENT = 'deed54fa31a1f6ac08d33cde238f2f7409d8d4d37d700b78b603b28bfe3ab792'
INPUT_PATHS = {
    'L': 'D:/CodexProjects/VideoKit/test_media/03_large_files/large_video_over_2GiB.mkv',
    'C': 'D:/CodexProjects/VideoKit/test_media/04_corrupted_files/corrupted_video.mp4',
    'Z': 'D:/CodexProjects/VideoKit/test_media/04_corrupted_files/empty_video.mkv'}
LENGTHS = {'L': 3212959911, 'C': 4096, 'Z': 0}
LIMITS = dict(metadataBytes=4194304, fixtureBytes=2097152, wrapperMetadataBytes=196608,
              productionMetadataPeakBytes=3178496, parentWaitSeconds=200,
              driverSeconds=180, minimumAvailablePhysicalBytes=2147483648)
_ISSUER = object()


class AdmissionError(Exception):
    def __init__(self, code):
        self.code = code
        super().__init__(code)


def require(condition, code):
    if not condition:
        raise AdmissionError(code)


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True).encode('ascii')


def digest(data):
    return hashlib.sha256(data).hexdigest()


def decode(data):
    return json.loads(data.decode('utf-8-sig'))


def hex_sha(value):
    return isinstance(value, str) and re.fullmatch('[0-9a-f]{64}', value) is not None


def verify_grant(token, expected_commitment):
    """Pure secret proof; production always supplies its source-pinned constant."""
    require(hex_sha(expected_commitment) and isinstance(token, str) and
            re.fullmatch('[0-9a-f]{64}', token) is not None, 'COORDINATOR_SECRET_REQUIRED')
    require(hmac.compare_digest(digest(bytes.fromhex(token)), expected_commitment), 'COORDINATOR_SECRET_MISMATCH')
    return True


def _path_key(path):
    require(isinstance(path, str) and PureWindowsPath(path).is_absolute() and '..' not in PureWindowsPath(path).parts,
            'ABSOLUTE_AUTHORITY_PATH_REQUIRED')
    return PureWindowsPath(path).as_posix().casefold()


def build_profile(inputs_document):
    """Declared R2 values only: does not stat, hash, open, or prove a version."""
    inputs = inputs_document.get('inputs', {})
    require(set(inputs) == {'L', 'C', 'Z'}, 'REAL_INPUT_ALIAS_SET')
    for alias in ('L', 'C', 'Z'):
        item = inputs[alias]
        require(_path_key(item.get('path')) == _path_key(INPUT_PATHS[alias]), 'REAL_INPUT_PATH_NOT_AUTHORIZED:' + alias)
        require(type(item.get('historical', {}).get('bytes')) is int and
                item['historical']['bytes'] == LENGTHS[alias], 'REAL_INPUT_LENGTH_GEOMETRY:' + alias)
    return dict(schema=1, kind='REAL_IO', lengths=dict(LENGTHS), boundary=2147483648,
                inputs={alias: PureWindowsPath(inputs[alias]['path']).as_posix() for alias in ('L', 'C', 'Z')})


def validate_batch(batch):
    exact = dict(schema=1, batchId=BATCH, machineName='LZF', uniqueRootName=ROOT_NAME,
                 state=STATE, profile='REAL_IO', observerMode='ACTUAL_OS_OBSERVER',
                 executionAuthorized=False, mockAllowed=False, externalGrantRequired=True,
                 maximumG=1, maximumFullAttempts=1, executionDirectory='execution', outputParent='runs',
                 packageRoot=PACKAGE, sealFile='evidence/e3-freeze.json',
                 coordinatorGrantCommitment=GRANT_COMMITMENT)
    require(type(batch) is dict, 'BATCH_SCHEMA')
    for key, value in exact.items():
        require(type(batch.get(key)) is type(value) and batch[key] == value, 'BATCH_FIELD:' + key)
    require(batch.get('limits') == LIMITS, 'BATCH_LIMITS_CHANGED')
    runtime = batch.get('runtimeIdentity', {})
    require(runtime.get('pythonVersion') == '3.12.14' and runtime.get('pointerBits') == 64 and
            runtime.get('pythonExecutable') == 'C:/Users/benny/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' and
            runtime.get('pythonDllSha256') == '2b6fffde96cf24a57fca642aaefd5788816ab5ef8624ea63b722cbceb94d49b1',
            'RUNTIME_BINDING_CHANGED')
    return batch


class RuntimePermit:
    """Process-local capability issued after the original child's durable claim."""
    __slots__ = ('_wire', '_profile_sha', '_issuer', '_secret', '_proof')

    def __init__(self, receipt, profile, issuer=None, grant_token=None):
        require(issuer is _ISSUER, 'DURABLE_ORIGINAL_CLAIM_REQUIRED')
        verify_grant(grant_token, GRANT_COMMITMENT)
        self._wire = encoded(receipt)
        self._profile_sha = digest(encoded(profile))
        self._issuer = issuer
        self._secret = bytes.fromhex(grant_token)
        self._proof = hmac.new(self._secret, self._wire + self._profile_sha.encode('ascii'), hashlib.sha256).digest()

    @property
    def receipt(self):
        return decode(self._wire)

    def binds(self, root, profile):
        receipt = self.receipt
        valid_secret = hmac.compare_digest(digest(self._secret), GRANT_COMMITMENT)
        proof = hmac.new(self._secret, self._wire + self._profile_sha.encode('ascii'), hashlib.sha256).digest()
        return (valid_secret and hmac.compare_digest(proof, self._proof) and
                self._issuer is _ISSUER and _path_key(str(root)) == _path_key(OUTPUT_ROOT) and
                receipt.get('outputRoot') == OUTPUT_ROOT and receipt.get('batchId') == BATCH and
                receipt.get('profileSha256') == self._profile_sha == digest(encoded(profile)) and
                receipt.get('grantCommitment') == GRANT_COMMITMENT and receipt.get('profile') == 'REAL_IO')


def fingerprint(value):
    return dict(bytes=len(value), sha256=digest(value)) if isinstance(value, bytes) else value


def validate_freeze(freeze, expected_sha, actual_sha, read_file, machine):
    require(hex_sha(expected_sha) and hmac.compare_digest(expected_sha, actual_sha), 'EXPECTED_FREEZE_MISMATCH')
    require(type(freeze) is dict and freeze.get('schema') == 1 and freeze.get('state') == STATE, 'FREEZE_SCHEMA')
    require(machine == 'LZF', 'MACHINE_NOT_AUTHORIZED')
    immutable = freeze.get('immutableFiles'); runtime = freeze.get('runtimeFiles')
    require(type(immutable) is list and type(runtime) is list and 40 <= len(runtime) <= 4096,
            'RUNTIME_INVENTORY')
    all_rows = {}
    for row in immutable:
        path = row.get('path', '')
        document = path in {'docs/coder/D1_E3_' + name + '_V1.0.md' for name in
                            ('DELIVERY', 'REAL_IO_EXECUTION_PLAN', 'EXECUTION_APPENDIX')}
        require(isinstance(path, str) and (path.startswith(PREFIX) or document) and '\\' not in path and
                all(part not in ('', '.', '..') for part in path.split('/')) and path not in all_rows,
                'IMMUTABLE_PATH')
        require(not path.startswith((PREFIX + 'execution/', PREFIX + 'runs/', PREFIX + 'selfcheck/')),
                'OUTPUT_IN_IMMUTABLE_INVENTORY')
        all_rows[path] = row
    seen = set()
    for row in runtime:
        path = row.get('path', '')
        require(path.startswith(PREFIX) and path in all_rows and row == all_rows[path] and path not in seen, 'RUNTIME_NOT_FROZEN')
        relative = path[len(PREFIX):]
        require(relative.split('/')[0] in ('src', 'tools', 'profiles', 'manifest') or
                relative == 'artifacts/E3.dll' or relative.startswith('artifacts/java-e3/') and relative.endswith('.class'), 'RUNTIME_PATH')
        seen.add(path)
        fact = fingerprint(read_file(path))
        require(type(row.get('bytes')) is int and fact['bytes'] == row['bytes'] and fact['sha256'] == row.get('sha256'),
                'RUNTIME_FILE_CHANGED:' + path)
    needed = {PREFIX + path for path in ('manifest/e3-batch.json', 'manifest/branches.json',
              'profiles/inputs.json', 'profiles/cases.json', 'profiles/runtime-policy.json', 'profiles/machine.json',
              'tools/e3_admission.py', 'tools/e3_runtime.py', 'tools/e3_driver.py', 'tools/launch-once.py',
              'tools/completion_evaluation.py', 'tools/r-helper.ps1', 'artifacts/E3.dll')}
    require(needed <= seen, 'REQUIRED_RUNTIME_FILE_MISSING')
    usage = freeze.get('prepUsage', {})
    require(type(usage.get('metadataBytes')) is int and 0 <= usage['metadataBytes'] <= 819200 and
            type(usage.get('fixtureBytes')) is int and 0 <= usage['fixtureBytes'] <= 1441792,
            'PREP_AGGREGATE_CREDIT')
    return freeze


def bind_claim(reservation, launch, parent, child):
    require(reservation.get('batchId') == BATCH and reservation.get('rootName') == ROOT_NAME,
            'RESERVATION_BATCH')
    require(launch.get('reservationSha256') == digest(encoded(reservation)), 'LAUNCH_RESERVATION_BINDING')
    require(parent == reservation.get('launcher') == launch.get('launcher'), 'ORIGINAL_LAUNCHER_REQUIRED')
    require(child == launch.get('child') and child.get('pid') != parent.get('pid') and
            all(type(identity.get(key)) is int and identity[key] > 0 for identity in (parent, child)
                for key in ('pid', 'creationTime100ns')), 'ORIGINAL_CHILD_REQUIRED')
    require(launch.get('expectedFreeze') == reservation.get('expectedFreeze') and launch.get('batchId') == BATCH,
            'CLAIM_FREEZE_BINDING')
    return dict(schema=1, scope='E3_COORDINATOR_GRANTED_ORIGINAL_CLAIM', batchId=BATCH,
                expectedFreeze=reservation['expectedFreeze'], rootName=ROOT_NAME, outputRoot=OUTPUT_ROOT,
                launcher=parent, child=child, reservationSha256=digest(encoded(reservation)),
                launchSha256=digest(encoded(launch)), profile='REAL_IO', profileSha256=reservation['profileSha256'],
                grantCommitment=GRANT_COMMITMENT, coordinatorSecretVerified=True,
                profileGeometry=dict(boundary=2147483648, lengths=dict(LENGTHS)),
                observerMode='ACTUAL_OS_OBSERVER', mockMetricsUsed=False, realExecutionAllowed=True)


def inspect_receipt():
    return dict(scope='E3_PREPARATION_INSPECT', status='NOT_RUN', batchId=BATCH,
                executionAllowed=False, coordinatorGrantReleased=False, reservationConsumed=False,
                outputRootCreated=False, actualFullRun=False, helpersStarted=0, mediaBytesRead=0)


def validate_result_inventory(batch, prep_usage, entries, manifest_bytes=0):
    validate_batch(batch)
    require(type(manifest_bytes) is int and manifest_bytes >= 0 and type(entries) is list and len(entries) <= 512,
            'RESULT_INVENTORY_SCHEMA')
    require(type(prep_usage) is dict and all(type(prep_usage.get(key)) is int and prep_usage[key] >= 0
                                          for key in ('metadataBytes', 'fixtureBytes')), 'RESULT_PREP_USAGE')
    totals = dict(metadataBytes=manifest_bytes, fixtureBytes=0); wrapper = manifest_bytes; seen = set()
    for row in entries:
        require(type(row) is dict and type(row.get('path')) is str, 'RESULT_INVENTORY_ENTRY')
        path = row['path']; size = row['bytes']
        require(type(size) is int and size >= 0 and path not in seen and '\\' not in path and
                all(part not in ('', '.', '..') for part in path.split('/')), 'RESULT_INVENTORY_ENTRY')
        seen.add(path)
        require(path.startswith('execution/') or path.startswith('runs/' + ROOT_NAME + '/'), 'RESULT_OUTPUT_SCOPE')
        fixture = path.startswith('runs/') and path.endswith('.out')
        require(row.get('kind') == ('FIXTURE' if fixture else 'METADATA'), 'RESULT_CLASSIFICATION')
        totals['fixtureBytes' if fixture else 'metadataBytes'] += size
        wrapper += size if path.startswith('execution/') else 0
    combined = {key: prep_usage[key] + totals[key] for key in totals}
    require(combined['metadataBytes'] <= 4194304 and combined['fixtureBytes'] <= 2097152 and
            totals['fixtureBytes'] <= 655360 and wrapper <= 196608 and
            totals['metadataBytes'] - wrapper <= 3178496, 'RESULT_AGGREGATE_CAP_EXCEEDED')
    return dict(outputUsage=totals, combinedUsage=combined, wrapperMetadataBytes=wrapper)


def result_finalizable(receipt, spawn_calls, local_clear=True):
    require(type(spawn_calls) is int and 0 <= spawn_calls <= 1, 'RESULT_SPAWN_COUNT')
    return (local_clear is True and receipt.get('status') in ('PASS', 'FAIL') and receipt.get('noInFlight') is True and
            (spawn_calls == 0 or receipt.get('originalChildExitObserved') is True))


class OnceAdmission:
    def __init__(self, batch, backend):
        self.batch = validate_batch(batch); self.backend = backend
        self.freeze = None; self.reservation = None; self.profile = None

    def prepare(self, expected_freeze, batch_id):
        require(batch_id == BATCH, 'BATCH_ID_MISMATCH')
        raw = self.backend.read('evidence/e3-freeze.json')
        reader = getattr(self.backend, 'fingerprint_project', self.backend.read_project)
        freeze = validate_freeze(decode(raw), expected_freeze, digest(raw), reader, self.backend.machine_name())
        require(freeze.get('batchManifestSha256') == digest(self.backend.read('manifest/e3-batch.json')),
                'BATCH_MANIFEST_CHANGED')
        self.backend.assert_code_inventory(freeze['runtimeFiles'])
        self.profile = build_profile(decode(self.backend.read('profiles/inputs.json')))
        self.freeze = freeze
        return freeze

    def reserve(self, expected_freeze, batch_id, grant_token):
        self.prepare(expected_freeze, batch_id)
        verify_grant(grant_token, GRANT_COMMITMENT)
        self.backend.verify_runtime(self.batch['runtimeIdentity'])
        require(not self.backend.exists('execution') and not self.backend.exists('runs/' + ROOT_NAME),
                'ONCE_OUTPUT_ALREADY_EXISTS')
        self.backend.mkdir_new('execution')
        reservation = dict(schema=1, scope='E3_ONE_SHOT_RESERVATION', batchId=BATCH, rootName=ROOT_NAME,
                           outputRoot=OUTPUT_ROOT, expectedFreeze=expected_freeze, launcher=self.backend.identity('self'),
                           profileSha256=digest(encoded(self.profile)), nonce=self.backend.nonce(),
                           grantCommitment=GRANT_COMMITMENT, coordinatorSecretVerified=True,
                           consumed=True, refundAllowed=False, maximumG=1, createdBeforeG=True)
        self.reservation = reservation
        self.backend.create_new('execution/reservation.json', reservation)
        memory = self.backend.fresh_memory(); self.backend.create_new('execution/fresh-memory.json', memory)
        require(memory.get('status') == 'MEMORY_READY' and memory.get('stopAcceptance') is False and
                memory.get('minimumAvailablePhysicalBytes') == 2147483648 and
                type(memory.get('observation', {}).get('availablePhysicalBytes')) is int and
                memory['observation']['availablePhysicalBytes'] >= 2147483648,
                'FRESH_MEMORY_REJECTED_RESERVATION_CONSUMED')
        return reservation

    def bind_launch(self, reservation, child):
        launch = dict(schema=1, batchId=BATCH, expectedFreeze=reservation['expectedFreeze'],
                      reservationSha256=digest(encoded(reservation)), launcher=reservation['launcher'], child=child)
        bind_claim(reservation, launch, reservation['launcher'], child)
        self.backend.create_new('execution/launch.json', launch)
        return launch

    def claim(self, expected_freeze, batch_id, grant_token):
        self.prepare(expected_freeze, batch_id)
        verify_grant(grant_token, GRANT_COMMITMENT)
        self.backend.verify_runtime(self.batch['runtimeIdentity'])
        reservation = decode(self.backend.read('execution/reservation.json'))
        require(reservation.get('expectedFreeze') == expected_freeze and reservation.get('consumed') is True and
                reservation.get('refundAllowed') is False and reservation.get('grantCommitment') == GRANT_COMMITMENT and
                reservation.get('profileSha256') == digest(encoded(self.profile)), 'RESERVATION_CHANGED')
        launch = self.backend.await_launch(1.0)
        receipt = bind_claim(reservation, launch, self.backend.identity('parent'), self.backend.identity('self'))
        self.backend.create_new('execution/claim.json', receipt)
        return RuntimePermit(receipt, self.profile, _ISSUER, grant_token=grant_token)
