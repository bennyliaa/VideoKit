"""Bounded read-only E2E evidence loader. No production/runtime imports."""
import hashlib
import json
import os
from pathlib import Path
import stat

BASE = Path(__file__).absolute().parents[1]
PROJECT = BASE.parents[2]
ORIGINAL = BASE.parent / 'd1e2e'
SEAL_SHA = 'aa59420cff4153395af2ab9b97eb47d8f560e91763b730f47c0fda3c0578b66a'
RESULT_SHA = 'baa6a1ed87764a5d16b1d282717824110d0082bc188606edf4affb33377750ea'
PRECLOSE_SHA = '702d8505e16bf504564179c14477e7cfe50af35c922531034c66645d6bc79032'
BATCH = 'D1-E2E-201dffc63b60405da3046f21fa7ff26d'
ROOT_NAME = 'e2e-201dffc63b60405da3046f21fa7ff26d'
SOURCE_FOLDERS = ('src','tools','manifest','profiles','upstream-e2d','upstream-e2c',
                  'upstream-e2b','upstream-e2a','upstream-e2','upstream-e1e')
TESTER_FILES = ('independent-results-audit.json', 'original-launch-tool-receipt.json')


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def decode(data):
    return json.loads(data.decode('utf-8-sig'))


def relative_name(name):
    require(isinstance(name, str) and '\\' not in name and ':' not in name and
            all(part not in ('', '.', '..') for part in name.split('/')), 'RELATIVE_EVIDENCE_PATH')
    return name


class BoundedReader:
    """Every disk read charged before requesting bytes; no metric/native reader."""
    def __init__(self):
        self.usage = {'source': {'bytes': 0, 'files': 0, 'byteCap': 268435456, 'fileCap': 8192},
                      'result': {'bytes': 0, 'files': 0, 'byteCap': 16777216, 'fileCap': 1024}}
        self.fingerprints = {}
        self.retained = {}

    def safe(self, path):
        path = Path(os.path.abspath(path))
        allowed = (path == ORIGINAL or path.is_relative_to(ORIGINAL) or
                   path.parent == BASE.parent and path.name in
                   {'D1_E2E_DELIVERY_V1.0.md','D1_E2E_EXECUTION_PLAN_V1.0.md','D1_E2E_EXECUTION_APPENDIX_V1.0.md'} or
                   path.parent == PROJECT/'docs/tester/D1_E2E_EVIDENCE' and path.name in TESTER_FILES)
        require(allowed, 'EVIDENCE_PATH_OUTSIDE_FIXED_SCOPE')
        for part in reversed((path, *path.parents)):
            info = os.lstat(part)
            require(not stat.S_ISLNK(info.st_mode) and not getattr(info, 'st_file_attributes', 0) & 0x400,
                    'EVIDENCE_REPARSE_DENIED')
            if part != path:
                require(stat.S_ISDIR(info.st_mode), 'EVIDENCE_ANCESTOR_NOT_DIRECTORY')
        return path

    def read(self, path, category, *, retain=True):
        require(category in self.usage, 'READ_CATEGORY')
        path = self.safe(path)
        key = (str(path), category)
        if retain and key in self.retained:
            return self.retained[key]
        if not retain and key in self.fingerprints:
            return self.fingerprints[key]
        account = self.usage[category]
        require(account['files'] < account['fileCap'], 'OFFLINE_FILE_READ_LIMIT')
        account['files'] += 1
        parts = []; count = 0; sha = hashlib.sha256()
        require(stat.S_ISREG(os.lstat(path).st_mode), 'EVIDENCE_REGULAR_FILE_REQUIRED')
        with open(path, 'rb', buffering=0) as stream:
            while True:
                remaining = account['byteCap'] - account['bytes']
                require(remaining > 0, 'OFFLINE_BYTE_READ_LIMIT')
                block = stream.read(min(65536, remaining))
                if not block:
                    break
                account['bytes'] += len(block); count += len(block); sha.update(block)
                if retain:
                    require(count <= (2097152 if category == 'source' else 16777216), 'RETAINED_EVIDENCE_SIZE_LIMIT')
                    parts.append(block)
        fact = {'bytes': count, 'sha256': sha.hexdigest()}
        self.fingerprints[key] = fact
        if retain:
            value = b''.join(parts); self.retained[key] = value
            return value
        return fact

    def walk_files(self, root, maximum=1024):
        root = self.safe(root); files = []; visited = 0
        for directory, dirs, names in os.walk(root, followlinks=False):
            visited += len(dirs) + len(names) + 1
            require(visited <= maximum * 2, 'OFFLINE_NAMESPACE_ENTRY_LIMIT')
            for name in dirs:
                self.safe(Path(directory)/name)
            for name in sorted(names):
                path = self.safe(Path(directory)/name)
                require(stat.S_ISREG(os.lstat(path).st_mode), 'EVIDENCE_NONREGULAR_FILE')
                files.append(path)
                require(len(files) <= maximum, 'OFFLINE_NAMESPACE_FILE_LIMIT')
        return files


def load_original_bundle():
    reader = BoundedReader()
    seal_bytes = reader.read(ORIGINAL/'evidence/e2e-freeze.json', 'source')
    require(digest(seal_bytes) == SEAL_SHA, 'ORIGINAL_SEAL_CHANGED')
    seal = decode(seal_bytes)
    require(seal.get('batchId') == BATCH and seal.get('state') == 'PREPARED_NOT_RUN_PENDING_TESTER', 'ORIGINAL_SEAL_IDENTITY')
    immutable = seal.get('immutableFiles')
    require(type(immutable) is list and len(immutable) == 90, 'ORIGINAL_IMMUTABLE_SET')
    names = set()
    # Retain only the two configuration JSONs needed by pure evaluators.
    manifest_bytes = reader.read(ORIGINAL/'manifest/branches.json', 'source')
    policy_bytes = reader.read(ORIGINAL/'profiles/runtime-policy.json', 'source')
    for entry in immutable:
        name = relative_name(entry['path'])
        require(name not in names, 'DUPLICATE_ORIGINAL_IMMUTABLE_PATH'); names.add(name)
        fact = reader.read(PROJECT/name, 'source', retain=False)
        require(fact == {'bytes': entry['bytes'], 'sha256': entry['sha256']}, 'ORIGINAL_IMMUTABLE_CHANGED:'+name)
    expected_sources = {name for name in names if any(name.startswith('docs/coder/d1e2e/'+folder+'/') for folder in SOURCE_FOLDERS)}
    actual_sources = {path.relative_to(PROJECT).as_posix() for folder in SOURCE_FOLDERS
                      for path in reader.walk_files(ORIGINAL/folder, maximum=8192)}
    require(actual_sources == expected_sources, 'ORIGINAL_SOURCE_FILE_SET_CHANGED')
    raw_manifest = reader.read(ORIGINAL/'execution/result-manifest.json', 'result')
    require(digest(raw_manifest) == RESULT_SHA, 'ORIGINAL_RESULT_MANIFEST_CHANGED')
    result = decode(raw_manifest)
    require(result.get('batchId') == BATCH and result.get('expectedFreeze') == SEAL_SHA, 'ORIGINAL_RESULT_IDENTITY')
    entries = result.get('files')
    require(type(entries) is list and len(entries) == 145, 'ORIGINAL_OUTPUT_COUNT')
    files = {'execution/result-manifest.json': raw_manifest}
    for entry in entries:
        name = relative_name(entry['path'])
        require(name not in files and (name.startswith('execution/') or name.startswith('selfcheck/'+ROOT_NAME+'/')),
                'ORIGINAL_OUTPUT_SCOPE_OR_DUPLICATE')
        raw = reader.read(ORIGINAL/name, 'result')
        require(len(raw) == entry['bytes'] and digest(raw) == entry['sha256'], 'ORIGINAL_OUTPUT_HASH_CHANGED:'+name)
        files[name] = raw
    actual_outputs = {path.relative_to(ORIGINAL).as_posix() for root in
                      (ORIGINAL/'execution', ORIGINAL/'selfcheck'/ROOT_NAME)
                      for path in reader.walk_files(root)}
    require(set(files) == actual_outputs and len(files) == 146, 'ORIGINAL_OUTPUT_FILE_SET_CHANGED')
    preclose_raw = files['selfcheck/'+ROOT_NAME+'/result-before-close.json']
    require(digest(preclose_raw) == PRECLOSE_SHA, 'ORIGINAL_PRECLOSE_CHANGED')
    global_lines = files['selfcheck/'+ROOT_NAME+'/global.log'].splitlines()
    require(global_lines and global_lines[0] == b'E2A SYNTHETIC TOOL INTEGRATION', 'ORIGINAL_GLOBAL_HEADER')
    global_events = []
    for line in global_lines[1:]:
        value = decode(line)
        if isinstance(value, dict):
            global_events.append(value)
    tester = PROJECT/'docs/tester/D1_E2E_EVIDENCE'
    audit_bytes = reader.read(tester/TESTER_FILES[0], 'result')
    call_bytes = reader.read(tester/TESTER_FILES[1], 'result')
    bundle = {'files': files, 'sealBytes': seal_bytes, 'manifest': decode(manifest_bytes),
              'policy': decode(policy_bytes), 'testerAudit': decode(audit_bytes),
              'originalCallReceipt': decode(call_bytes), 'preclose': decode(preclose_raw),
              'driver': decode(files['execution/driver-result.json']),
              'launcher': decode(files['execution/launcher-result.json']),
              'global_events': global_events, 'readerUsage': reader.usage,
              'sourceIntegrity': {'status': 'VERIFIED', 'immutableFiles': 90, 'sealSha256': SEAL_SHA},
              'originalInputs': {'resultManifestSha256': RESULT_SHA, 'precloseSha256': PRECLOSE_SHA,
                                 'testerAuditSha256': digest(audit_bytes), 'originalCallReceiptSha256': digest(call_bytes)}}
    return bundle
