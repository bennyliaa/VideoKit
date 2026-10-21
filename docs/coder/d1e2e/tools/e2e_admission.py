"""E2E-only authorization. Pure guards/state machine; no IO on import."""
import hashlib
import json
import re

BATCH = 'D1-E2E-201dffc63b60405da3046f21fa7ff26d'
ROOT_NAME = 'e2e-201dffc63b60405da3046f21fa7ff26d'
PREFIX = 'docs/coder/d1e2e/'
STATE = 'PREPARED_NOT_RUN_PENDING_TESTER'
C_FREEZE = 'bccacb2e98b1f4a4d3017fc8efb9bd0f047e58d91e7c910303fff40eb3896179'
C_SOURCE = '035263006cbaa99837656bb2b66045a3f5c6181ab8af8c8fe3f5bcf5ba3e5934'
LIMITS = dict(metadataBytes=4194304, fixtureBytes=2097152, wrapperMetadataBytes=196608,
              productionMetadataPeakBytes=3178496, parentWaitSeconds=200,
              driverSeconds=180, minimumAvailablePhysicalBytes=2147483648)


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


def fingerprint(value):
    # The real backend streams 64KiB blocks; in-memory checks can pass bytes.
    return dict(bytes=len(value), sha256=digest(value)) if isinstance(value, bytes) else value


def file_fingerprint(backend, relative):
    return backend.fingerprint(relative) if hasattr(backend, 'fingerprint') else fingerprint(backend.read(relative))


def validate_batch(batch):
    exact = dict(schema=1, batchId=BATCH, machineName='LZF', uniqueRootName=ROOT_NAME,
                 state=STATE, profile='SYNTHETIC', observerMode='ACTUAL_OS_OBSERVER',
                 realExecutionAllowed=False, mockAllowed=False, maximumG=1,
                 maximumFullAttempts=1, executionDirectory='execution', fixtureParent='selfcheck',
                 packageRoot='D:/CodexProjects/VideoKit/docs/coder/d1e2e',
                 sealFile='evidence/e2e-freeze.json')
    require(type(batch) is dict, 'BATCH_SCHEMA')
    for key, value in exact.items():
        require(type(batch.get(key)) is type(value) and batch[key] == value, 'BATCH_FIELD:' + key)
    require(batch.get('limits') == LIMITS, 'BATCH_LIMITS_CHANGED')
    bindings = batch.get('productionBindings', {})
    require(bindings.get('E2CfreezeSha256') == C_FREEZE and bindings.get('E2CsourceZipSha256') == C_SOURCE,
            'E2C_BINDING_CHANGED')
    require(all(hex_sha(bindings.get(key)) for key in ('E2DfreezeSha256', 'E2DsourceZipSha256')), 'E2D_BINDING_MISSING')
    runtime = batch.get('runtimeIdentity', {})
    require(runtime.get('pythonVersion') == '3.12.14' and runtime.get('pointerBits') == 64 and
            runtime.get('pythonExecutable') == 'C:/Users/benny/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' and
            runtime.get('pythonDllSha256') == '2b6fffde96cf24a57fca642aaefd5788816ab5ef8624ea63b722cbceb94d49b1', 'RUNTIME_BINDING_CHANGED')
    return batch


def validate_freeze(freeze, expected_sha, actual_sha, read_file, machine):
    require(hex_sha(expected_sha) and expected_sha == actual_sha, 'EXPECTED_FREEZE_MISMATCH')
    require(type(freeze) is dict and freeze.get('schema') == 1 and freeze.get('state') == STATE, 'FREEZE_SCHEMA')
    require(machine == 'LZF', 'MACHINE_NOT_AUTHORIZED')
    entries = freeze.get('immutableFiles')
    require(type(entries) is list and 48 <= len(entries) <= 4096, 'IMMUTABLE_INVENTORY')
    seen = set()
    for entry in entries:
        path = entry.get('path', '')
        require(isinstance(path, str) and path.startswith('docs/') and '\\' not in path and
                all(part not in ('', '.', '..') for part in path.split('/')) and path not in seen,
                'IMMUTABLE_PATH')
        require(not path.startswith(PREFIX + 'execution/') and not path.startswith(PREFIX + 'selfcheck/') and
                path != PREFIX + 'evidence/e2e-freeze.json', 'OUTPUT_IN_IMMUTABLE_INVENTORY')
        seen.add(path)
        fact = fingerprint(read_file(path))
        require(type(entry.get('bytes')) is int and fact['bytes'] == entry['bytes'] and fact['sha256'] == entry.get('sha256'),
                'IMMUTABLE_FILE_CHANGED:' + path)
    needed = {PREFIX + 'manifest/e2e-batch.json', PREFIX + 'upstream-e2c/freeze-summary.json',
              PREFIX + 'upstream-e2c/source-manifest.json',
              PREFIX + 'upstream-e2c/E2C-source.zip', PREFIX + 'upstream-e2d/freeze-summary.json',
              PREFIX + 'upstream-e2d/E2D-source.zip', PREFIX + 'tools/r-helper.ps1'}
    needed.update(PREFIX + 'tools/' + name for name in ('e2e_admission.py', 'e2e_runtime.py', 'e2e_driver.py', 'launch-once.py'))
    require(needed <= seen, 'REQUIRED_IMMUTABLE_MISSING')
    usage = freeze.get('prepUsage', {})
    require(type(usage.get('metadataBytes')) is int and 0 <= usage['metadataBytes'] <= 819200 and
            type(usage.get('fixtureBytes')) is int and usage['fixtureBytes'] == 0, 'PREP_AGGREGATE_CREDIT')
    return freeze


def bind_claim(reservation, launch, parent, child):
    require(reservation.get('batchId') == BATCH and reservation.get('rootName') == ROOT_NAME, 'RESERVATION_BATCH')
    require(launch.get('reservationSha256') == digest(encoded(reservation)), 'LAUNCH_RESERVATION_BINDING')
    require(parent == reservation.get('launcher') == launch.get('launcher'), 'ORIGINAL_LAUNCHER_REQUIRED')
    require(child == launch.get('child') and child.get('pid') != parent.get('pid') and
            all(type(identity.get(key)) is int and identity[key] > 0 for identity in (parent, child)
                for key in ('pid', 'creationTime100ns')), 'ORIGINAL_CHILD_REQUIRED')
    require(launch.get('expectedFreeze') == reservation.get('expectedFreeze') and
            launch.get('batchId') == BATCH, 'CLAIM_FREEZE_BINDING')
    return dict(schema=1, scope='E2E_SINGLE_ACTUAL_SELF_OWNED_CLAIM', batchId=BATCH,
                expectedFreeze=reservation['expectedFreeze'], rootName=ROOT_NAME,
                launcher=parent, child=child, reservationSha256=digest(encoded(reservation)),
                launchSha256=digest(encoded(launch)), profile='SYNTHETIC',
                observerMode='ACTUAL_OS_OBSERVER', mockMetricsUsed=False, realExecutionAllowed=False)


def inspect_receipt():
    return dict(scope='E2E_PREPARATION_INSPECT', status='NOT_RUN', batchId=BATCH,
                executionAllowed=False, reservationConsumed=False, outputRootCreated=False,
                actualFullRun=False, helpersStarted=0, mediaBytesRead=0)


def validate_result_inventory(batch, prep_usage, entries, manifest_bytes=0):
    """Pure final byte ledger; immutable files are never execution output."""
    validate_batch(batch)
    require(type(manifest_bytes) is int and manifest_bytes >= 0, 'RESULT_MANIFEST_BYTES')
    require(type(prep_usage) is dict and all(type(prep_usage.get(key)) is int and prep_usage[key] >= 0
                                          for key in ('metadataBytes', 'fixtureBytes')),
            'RESULT_PREP_USAGE')
    require(type(entries) is list and len(entries) <= 512, 'RESULT_ENTRY_COUNT')
    totals = dict(metadataBytes=manifest_bytes, fixtureBytes=0)
    wrapper = manifest_bytes
    seen = set()
    for entry in entries:
        path = entry['path']; size = entry['bytes']
        require(type(size) is int and size >= 0 and path not in seen and '\\' not in path and
                all(p not in ('', '.', '..') for p in path.split('/')),
                'RESULT_INVENTORY_ENTRY')
        seen.add(path)
        require(path.startswith('execution/') or path.startswith('selfcheck/' + ROOT_NAME + '/'),
                'RESULT_OUTPUT_SCOPE')
        fixture = path.split('/')[-1] in ('L.bin', 'C.bin', 'Z.bin') or path.endswith('.out')
        require(entry.get('kind') == ('FIXTURE' if fixture else 'METADATA'), 'RESULT_CLASSIFICATION')
        totals['fixtureBytes' if fixture else 'metadataBytes'] += size
        if path.startswith('execution/'):
            wrapper += size
    combined = {key: prep_usage[key] + totals[key] for key in totals}
    require(combined['metadataBytes'] <= 4194304 and combined['fixtureBytes'] <= 2097152 and
            totals['fixtureBytes'] <= 790528 and wrapper <= 196608, 'RESULT_AGGREGATE_CAP_EXCEEDED')
    return dict(outputUsage=totals, combinedUsage=combined, wrapperMetadataBytes=wrapper)


def result_finalizable(receipt, spawn_calls, local_clear=True):
    require(type(spawn_calls) is int and 0 <= spawn_calls <= 1, 'RESULT_SPAWN_COUNT')
    return (local_clear is True and receipt.get('status') in ('PASS', 'FAIL') and
            receipt.get('noInFlight') is True and
            (spawn_calls == 0 or receipt.get('originalChildExitObserved') is True))


class OnceAdmission:
    def __init__(self, batch, backend):
        self.batch = validate_batch(batch)
        self.backend = backend
        self.reservation = None
        self.freeze = None

    def prepare(self, expected_freeze, batch_id):
        require(batch_id == BATCH, 'BATCH_ID_MISMATCH')
        raw = self.backend.read('evidence/e2e-freeze.json')
        reader = getattr(self.backend, 'fingerprint_project', self.backend.read_project)
        freeze = validate_freeze(decode(raw), expected_freeze, digest(raw), reader,
                                 self.backend.machine_name())
        require(freeze.get('batchManifestSha256') == digest(self.backend.read('manifest/e2e-batch.json')),
                'BATCH_MANIFEST_CHANGED')
        require(freeze.get('productionBindings') == self.batch['productionBindings'], 'FREEZE_PRODUCTION_BINDINGS')
        if hasattr(self.backend, 'assert_code_inventory'):
            self.backend.assert_code_inventory(freeze['immutableFiles'])
        for key, relative in (('E2CfreezeSha256', 'upstream-e2c/freeze-summary.json'),
                              ('E2CsourceZipSha256', 'upstream-e2c/E2C-source.zip'),
                              ('E2DfreezeSha256', 'upstream-e2d/freeze-summary.json'),
                              ('E2DsourceZipSha256', 'upstream-e2d/E2D-source.zip')):
            require(file_fingerprint(self.backend, relative)['sha256'] == self.batch['productionBindings'][key], 'UPSTREAM_CHANGED:' + key)
        old = decode(self.backend.read('upstream-e2c/freeze-summary.json'))
        source_row = next((entry for entry in old['files']
                           if entry['path'] == 'docs/coder/d1e2c/evidence/source-manifest.json'), None)
        require(source_row is not None, 'ORIGINAL_SOURCE_MANIFEST_MISSING')
        source_raw = self.backend.read('upstream-e2c/source-manifest.json')
        require(len(source_raw) == source_row['bytes'] and digest(source_raw) == source_row['sha256'],
                'ORIGINAL_SOURCE_MANIFEST_CHANGED')
        source = decode(source_raw)
        selected = {}
        for entry in source['files'] + old['files']:
            path = entry['path']
            if not path.startswith('docs/coder/d1e2c/'):
                continue
            relative = path[len('docs/coder/d1e2c/'):]
            if (relative.startswith(('src/', 'profiles/')) or relative == 'manifest/branches.json' or
                    relative == 'tools/r-helper.ps1' or relative == 'artifacts/E2C.dll' or
                    relative.startswith('artifacts/java/') and relative.endswith('.class')):
                selected[relative] = entry
        require(sum(p.startswith('src/') for p in selected) == 32 and
                sum(p.startswith('profiles/') for p in selected) == 4 and
                sum(p.startswith('artifacts/') for p in selected) == 10 and len(selected) == 48,
                'ORIGINAL_PRODUCTION_INVENTORY')
        for relative, entry in selected.items():
            fact = file_fingerprint(self.backend, relative)
            require(fact['bytes'] == entry['bytes'] and fact['sha256'] == entry['sha256'], 'PRODUCTION_CHANGED:' + relative)
        require(not self.backend.exists('evidence/freeze-summary.json'), 'LEGACY_ACTIVE_SEAL_BLOCKS_ORIGINAL_HELPER')
        self.freeze = freeze
        return freeze

    def reserve(self, expected_freeze, batch_id):
        self.prepare(expected_freeze, batch_id)
        self.backend.verify_runtime(self.batch['runtimeIdentity'])
        require(not self.backend.exists('execution') and not self.backend.exists('selfcheck'), 'ONCE_OUTPUT_ALREADY_EXISTS')
        self.backend.mkdir_new('execution')
        reservation = dict(schema=1, scope='E2E_ONE_SHOT_RESERVATION', batchId=BATCH, rootName=ROOT_NAME,
                           expectedFreeze=expected_freeze, launcher=self.backend.identity('self'),
                           nonce=self.backend.nonce(), productionBindings=self.batch['productionBindings'],
                           consumed=True, refundAllowed=False, maximumG=1, createdBeforeG=True)
        self.reservation = reservation
        self.backend.create_new('execution/reservation.json', reservation)
        memory = self.backend.fresh_memory()
        self.backend.create_new('execution/fresh-memory.json', memory)
        require(memory.get('status') == 'MEMORY_READY' and memory.get('stopAcceptance') is False and
                memory.get('minimumAvailablePhysicalBytes') == 2147483648 and
                type(memory.get('observation', {}).get('availablePhysicalBytes')) is int and
                memory['observation']['availablePhysicalBytes'] >= 2147483648, 'FRESH_MEMORY_REJECTED_RESERVATION_CONSUMED')
        return reservation

    def bind_launch(self, reservation, child):
        launch = dict(schema=1, batchId=BATCH, expectedFreeze=reservation['expectedFreeze'],
                      reservationSha256=digest(encoded(reservation)), launcher=reservation['launcher'], child=child)
        bind_claim(reservation, launch, reservation['launcher'], child)
        self.backend.create_new('execution/launch.json', launch)
        return launch

    def claim(self, expected_freeze, batch_id):
        self.prepare(expected_freeze, batch_id)
        self.backend.verify_runtime(self.batch['runtimeIdentity'])
        reservation = decode(self.backend.read('execution/reservation.json'))
        require(reservation.get('expectedFreeze') == expected_freeze and
                reservation.get('productionBindings') == self.batch['productionBindings'] and
                reservation.get('consumed') is True and reservation.get('refundAllowed') is False,
                'RESERVATION_CHANGED')
        launch = self.backend.await_launch(1.0)
        claim = bind_claim(reservation, launch, self.backend.identity('parent'), self.backend.identity('self'))
        self.backend.create_new('execution/claim.json', claim)
        return claim
