"""Explicit Windows backend for E2E. Construction/import never starts a run."""
import ctypes
import hashlib
import json
import os
from pathlib import Path
import secrets
import stat
import struct
import subprocess
import sys
import time

from e2e_admission import (AdmissionError, BATCH, ROOT_NAME, PREFIX, LIMITS,
                           require, encoded, decode, digest, validate_result_inventory, result_finalizable)

FILE_CAPS = {'reservation.json': 4096, 'launch.json': 4096, 'launch.pending': 4096, 'claim.json': 8192,
             'fresh-memory.json': 4096, 'child-memory.json': 4096,
             'driver-result.json': 32768, 'launcher-result.json': 16384,
             'result-manifest.json': 49152, 'late-exit.json': 8192,
             'late-result-manifest.json': 49152}
MAX_GATE_BYTES = 268435456
MAX_GATE_FILES = 8192
SUBPROCESS_BYTES = 88747
SUBPROCESS_SHA256 = '85d29b2bf0249f5436838298c9a60ee93508b1102e9ac43b001f8a7e7ae8f375'


class LocalBackend:
    def __init__(self, base):
        self.base = Path(os.path.abspath(base))
        self.project = self.base.parents[2]
        self.process = None
        self.gate_bytes = self.gate_files = self.result_hash_bytes = 0
        self.identity_queries = self.identity_opened = self.identity_closed = 0
        self.identity_owned = self.identity_peak = 0
        self.close_unknown = False
        self.spawn_calls = 0
        self.spawn_error = None
        self.parent_handle_closed = False
        self.parent_handle_close_unknown = False
        self.cached_exit_proof = None
        self.metadata_owned = {}
        self.metadata_close_unknown = False
        self.metadata_credit = 0
        self.metadata_peak = 0
        self.original_child = None
        self.launch_publications = 0
        self.spawn_credit = 0

    def _reserve_metadata(self):
        require(self.metadata_credit == 0 and not self.metadata_close_unknown, 'WRAPPER_METADATA_CREDIT_PENDING')
        self.metadata_credit = 1
        self.metadata_peak = max(self.metadata_peak, self.metadata_credit)

    def _open_metadata(self, path, mode):
        self._reserve_metadata()
        try:
            return open(path, mode, buffering=0)
        except BaseException:
            self.metadata_credit = 0
            raise

    def _close_metadata(self, key, file):
        try:
            file.close()
        except BaseException:
            self.metadata_close_unknown = True
            raise
        else:
            del self.metadata_owned[key]
            self.metadata_credit = 0

    def _safe(self, path, allow_missing=False):
        path = Path(os.path.abspath(path))
        require(path == self.base or path.is_relative_to(self.base) or
                path.parent == self.base.parent and path.name.startswith('D1_E2E_') and path.suffix == '.md' or
                path == self.project/'docs/milestones/D1_E2E_CODER_REQUIREMENTS_V1.0.md', 'WRAPPER_PATH_DENIED')
        for entry in reversed((path, *path.parents)):
            try:
                fact = os.lstat(entry)
            except FileNotFoundError:
                require(allow_missing, 'WRAPPER_PATH_MISSING')
                continue
            require(not stat.S_ISLNK(fact.st_mode) and not getattr(fact, 'st_file_attributes', 0) & 0x400,
                    'WRAPPER_REPARSE_DENIED')
            if entry != path:
                require(stat.S_ISDIR(fact.st_mode), 'WRAPPER_ANCESTOR_NOT_DIRECTORY')
        return path

    def _relative(self, relative, allow_missing=False):
        require(isinstance(relative, str) and not Path(relative).is_absolute() and '\\' not in relative and
                all(p not in ('', '.', '..') for p in relative.split('/')), 'WRAPPER_RELATIVE_PATH')
        return self._safe(self.base/relative, allow_missing)

    def _gate_file(self, path, retain=False):
        self.gate_files += 1
        require(self.gate_files <= MAX_GATE_FILES, 'GATE_FILE_COUNT_LIMIT')
        require(stat.S_ISREG(os.lstat(path).st_mode), 'GATE_NONREGULAR_DENIED')
        sha = hashlib.sha256(); count = 0; parts = []
        source = self._open_metadata(path, 'rb')
        key = 'gate:' + str(path); self.metadata_owned[key] = source
        try:
            while True:
                require(self.gate_bytes < MAX_GATE_BYTES, 'GATE_METADATA_READ_LIMIT')
                block = source.read(min(65536, MAX_GATE_BYTES - self.gate_bytes))
                if not block:
                    break
                count += len(block); self.gate_bytes += len(block)
                require(self.gate_bytes <= MAX_GATE_BYTES, 'GATE_METADATA_READ_LIMIT')
                if retain:
                    require(count <= 2097152, 'GATE_JSON_SIZE_LIMIT')
                    parts.append(block)
                sha.update(block)
        finally:
            self._close_metadata(key, source)
        return b''.join(parts) if retain else dict(bytes=count, sha256=sha.hexdigest())

    def assert_code_inventory(self, entries):
        expected = {entry['path'][len(PREFIX):] for entry in entries if entry['path'].startswith(PREFIX) and
                    entry['path'][len(PREFIX):].split('/')[0] in ('src', 'tools', 'profiles', 'manifest', 'artifacts')}
        observed = set()
        directories = 0
        for name in ('src', 'tools', 'profiles', 'manifest', 'artifacts'):
            for directory, dirs, files in os.walk(self._relative(name), followlinks=False):
                directories += 1
                require(directories <= 256 and len(observed) + len(files) <= 4096, 'CODE_INVENTORY_LIMIT')
                for child in dirs:
                    self._safe(Path(directory)/child)
                for child in files:
                    path = self._safe(Path(directory)/child)
                    require(stat.S_ISREG(os.lstat(path).st_mode), 'CODE_NONREGULAR_DENIED')
                    observed.add(path.relative_to(self.base).as_posix())
        require(observed == expected, 'UNSEALED_CODE_INVENTORY_CHANGED')

    def read(self, relative):
        return self._gate_file(self._relative(relative), retain=True)

    def read_project(self, relative):
        return self._gate_file(self._safe(self.project/relative), retain=True)

    def fingerprint(self, relative):
        return self._gate_file(self._relative(relative))

    def fingerprint_project(self, relative):
        return self._gate_file(self._safe(self.project/relative))

    def exists(self, relative):
        path = self._relative(relative, True)
        return path.exists()

    def mkdir_new(self, relative):
        require(relative == 'execution', 'EXECUTION_DIRECTORY_ONLY')
        self._relative(relative, True).mkdir(exist_ok=False)

    def create_new(self, relative, value):
        require(relative.startswith('execution/') and relative.count('/') == 1 and
                relative.split('/')[1] in FILE_CAPS, 'WRAPPER_METADATA_FILE_DENIED')
        data = encoded(value)
        require(len(data) <= FILE_CAPS[relative.split('/')[1]], 'WRAPPER_METADATA_FILE_CAP')
        final_path = self._relative(relative, True)
        # Publish only the already-fsynced/actually-closed launch record. Windows
        # rename is no-replace; a failed publication never gets a repair/retry.
        path = self._relative('execution/launch.pending', True) if relative == 'execution/launch.json' else final_path
        # One exact write, no append/repair, no refund if a partial write exists.
        target = self._open_metadata(path, 'xb')
        self.metadata_owned[relative] = target
        try:
            require(target.write(data) == len(data), 'WRAPPER_SHORT_WRITE_NO_REPAIR')
            target.flush(); os.fsync(target.fileno())
        finally:
            self._close_metadata(relative, target)
        if relative == 'execution/launch.json':
            self.launch_publications += 1
            require(self.launch_publications == 1, 'SECOND_LAUNCH_PUBLICATION_FORBIDDEN')
            os.rename(path, final_path)
        return digest(data)

    def machine_name(self):
        require(os.name == 'nt', 'WINDOWS_REQUIRED')
        k = ctypes.WinDLL('kernel32', use_last_error=True)
        name = ctypes.create_unicode_buffer(256); size = ctypes.c_uint(256)
        k.GetComputerNameW.argtypes = [ctypes.c_wchar_p, ctypes.POINTER(ctypes.c_uint)]
        k.GetComputerNameW.restype = ctypes.c_int
        require(k.GetComputerNameW(name, ctypes.byref(size)), 'MACHINE_IDENTITY_UNAVAILABLE')
        return name.value

    def verify_runtime(self, expected):
        require(os.name == 'nt' and '.'.join(map(str, sys.version_info[:3])) == expected['pythonVersion'] and
                struct.calcsize('P') * 8 == expected['pointerBits'] and
                os.path.normcase(os.path.abspath(sys.executable)) == os.path.normcase(expected['pythonExecutable']),
                'ORIGINAL_PYTHON_REQUIRED')
        require(str(self.base).replace('\\', '/') == 'D:/CodexProjects/VideoKit/docs/coder/d1e2e', 'PACKAGE_ROOT_CHANGED')
        dll = Path(sys.executable).parent/'python312.dll'
        # Runtime DLL is a separate explicit allowlisted metadata read.
        for part in (dll, *dll.parents):
            fact = os.lstat(part)
            require(not stat.S_ISLNK(fact.st_mode) and not getattr(fact, 'st_file_attributes', 0) & 0x400,
                    'RUNTIME_REPARSE_DENIED')
        require(self._gate_file(dll)['sha256'] == expected['pythonDllSha256'], 'PYTHON_DLL_CHANGED')
        k = ctypes.WinDLL('kernel32', use_last_error=True)
        k.GetModuleFileNameW.argtypes = [ctypes.c_void_p, ctypes.c_wchar_p, ctypes.c_uint]
        k.GetModuleFileNameW.restype = ctypes.c_uint
        loaded = ctypes.create_unicode_buffer(32768)
        count = k.GetModuleFileNameW(ctypes.c_void_p(sys.dllhandle), loaded, len(loaded))
        require(0 < count < len(loaded) and os.path.normcase(os.path.abspath(loaded.value)) ==
                os.path.normcase(str(dll)), 'LOADED_PYTHON_DLL_PATH_CHANGED')
        library = Path(sys.executable).parent/'Lib/subprocess.py'
        require(os.path.normcase(os.path.abspath(subprocess.__file__)) == os.path.normcase(str(library)),
                'SUBPROCESS_MODULE_PATH_CHANGED')
        for part in (library, *library.parents):
            fact = os.lstat(part)
            require(not stat.S_ISLNK(fact.st_mode) and not getattr(fact, 'st_file_attributes', 0) & 0x400,
                    'RUNTIME_REPARSE_DENIED')
        fact = self._gate_file(library)
        require(fact['bytes'] == SUBPROCESS_BYTES and fact['sha256'] == SUBPROCESS_SHA256,
                'SUBPROCESS_IMPLEMENTATION_CHANGED')

    def nonce(self):
        return secrets.token_hex(24)

    def now(self):
        return time.monotonic()

    def identity(self, role, process=None):
        require(role in ('self', 'parent', 'child'), 'IDENTITY_ROLE')
        pid = os.getpid() if role == 'self' else os.getppid() if role == 'parent' else process.pid
        k = ctypes.WinDLL('kernel32', use_last_error=True)
        k.GetCurrentProcess.restype = ctypes.c_void_p
        k.OpenProcess.argtypes = [ctypes.c_uint, ctypes.c_int, ctypes.c_uint]; k.OpenProcess.restype = ctypes.c_void_p
        k.CloseHandle.argtypes = [ctypes.c_void_p]; k.CloseHandle.restype = ctypes.c_int
        k.GetProcessTimes.argtypes = [ctypes.c_void_p, *([ctypes.POINTER(ctypes.c_ulonglong)] * 4)]
        k.GetProcessTimes.restype = ctypes.c_int
        k.WaitForSingleObject.argtypes = [ctypes.c_void_p, ctypes.c_uint]; k.WaitForSingleObject.restype = ctypes.c_uint
        owned = role == 'parent'
        if owned:
            require(self.identity_owned == 0 and not self.close_unknown, 'WRAPPER_IDENTITY_CREDIT_PENDING')
            # Reserve before OpenProcess; an allocation failure is known absent.
            self.identity_owned = 1
            self.identity_peak = max(self.identity_peak, self.identity_owned)
        handle = k.OpenProcess(0x101000, False, pid) if owned else int(process._handle) if role == 'child' else k.GetCurrentProcess()
        if not handle:
            if owned:
                self.identity_owned = 0
            raise AdmissionError('ORIGINAL_PROCESS_HANDLE_UNAVAILABLE')
        if owned:
            self.identity_opened += 1
        try:
            require(k.WaitForSingleObject(handle, 0) == 0x102, 'ORIGINAL_PROCESS_NOT_RUNNING')
            values = [ctypes.c_ulonglong() for _ in range(4)]
            require(k.GetProcessTimes(handle, *(ctypes.byref(value) for value in values)), 'PROCESS_CREATION_UNAVAILABLE')
            self.identity_queries += 1
            return dict(pid=pid, creationTime100ns=values[0].value)
        finally:
            if owned:
                if not k.CloseHandle(handle):
                    self.close_unknown = True
                    raise AdmissionError('WRAPPER_IDENTITY_CLOSE_UNKNOWN')
                self.identity_closed += 1; self.identity_owned -= 1

    def fresh_memory(self):
        source = str(self.base/'src')
        if source not in sys.path:
            sys.path.insert(0, source)
        from runtime_metrics import fresh_memory_check
        return fresh_memory_check()

    def await_launch(self, seconds):
        end = time.monotonic() + min(1.0, seconds)
        path = self._relative('execution/launch.json', True)
        # Wait for the parent's single exact write/fsync/close. No retry of a
        # mismatched record: only absent/incomplete JSON can await publication.
        while True:
            try:
                raw = self.read('execution/launch.json')
                return decode(raw)
            except (FileNotFoundError, json.JSONDecodeError):
                pass
            except AdmissionError as failure:
                if failure.code != 'WRAPPER_PATH_MISSING':
                    raise
            require(time.monotonic() < end, 'ORIGINAL_LAUNCH_RECORD_NOT_RETURNED')
            time.sleep(min(.01, max(0, end - time.monotonic())))

    def spawn(self, reservation, expected_freeze, batch_id):
        require(self.spawn_calls == 0, 'SECOND_G_FORBIDDEN')
        self.spawn_calls += 1
        # Independent parent credits, never borrowed from G's original 24.
        self.spawn_credit = 6
        args = [sys.executable, '-I', '-B', str(self.base/'tools/e2e_driver.py'), '--run',
                '--expected-freeze', expected_freeze, '--batch-id', batch_id]
        # No parent PIPE, collector worker, unbounded communicate(), or retry.
        self.process = subprocess.Popen.__new__(subprocess.Popen)
        try:
            subprocess.Popen.__init__(self.process, args, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                                      stderr=subprocess.DEVNULL, cwd=str(self.base), close_fds=True,
                                      creationflags=subprocess.CREATE_NO_WINDOW)
        except BaseException as failure:
            self.spawn_error = type(failure).__name__
            raise
        self.spawn_credit = 1
        return self.process

    def child_identity(self, process):
        self.original_child = self.identity('child', process)
        return self.original_child

    def wait_bounded(self, process, seconds):
        if self.cached_exit_proof is not None:
            return dict(self.cached_exit_proof)
        if self.spawn_error is not None:
            return dict(status='PENDING', exitObserved=False, exitCode=None,
                        noInFlight=None, remaining='POPEN_START_RETURN_UNKNOWN', stoppedWaitingOnly=True)
        try:
            code = process.wait(timeout=min(200, seconds))
        except subprocess.TimeoutExpired:
            return dict(status='PENDING', exitObserved=False, exitCode=None,
                        noInFlight=None, remaining='ORIGINAL_G_AND_ITS_OWNERS_NOT_PROVEN', stoppedWaitingOnly=True)
        except BaseException as failure:
            return dict(status='PENDING', exitObserved=False, exitCode=None,
                        noInFlight=None, remaining='ORIGINAL_WAIT_RETURN_UNKNOWN', waitError=type(failure).__name__)
        return self._exit_receipt(process, code)

    def _exit_receipt(self, process, code):
        if self.cached_exit_proof is not None:
            return dict(self.cached_exit_proof)
        # Only one close attempt after actual exit. A later receipt error does
        # not authorize another Close on this original Popen handle.
        try:
            if not self.parent_handle_closed and not self.parent_handle_close_unknown:
                process._handle.Close()
                self.parent_handle_closed = True
                self.spawn_credit = 0
        except BaseException:
            self.parent_handle_close_unknown = True
        self.cached_exit_proof = dict(status='EXIT_OBSERVED', exitObserved=True, exitCode=code,
                                      parentProcessHandleCloseProven=self.parent_handle_closed)
        return dict(self.cached_exit_proof)

    def retain_original(self, process):
        # The 200s notice ended the caller's bounded wait, not ownership. This
        # same launcher remains alive and retains this exact Popen until exit.
        if self.parent_handle_close_unknown or self.spawn_error is not None:
            self.hold_unknown_ownership()
        if self.cached_exit_proof is not None:
            return dict(self.cached_exit_proof, pendingReceiptPreserved=True, newG=0, newSamples=0)
        while True:
            try:
                code = process.wait(timeout=1)
                break
            except subprocess.TimeoutExpired:
                continue
            except BaseException:
                self.hold_unknown_ownership()
        return dict(self._exit_receipt(process, code), status='EXIT_OBSERVED_AFTER_PENDING',
                    pendingReceiptPreserved=True, newG=0, newSamples=0)

    def hold_unknown_ownership(self):
        # An UNKNOWN close is never retried or silently converted into release.
        # Keep this original launcher/strong owners alive for human resolution.
        while True:
            time.sleep(1)

    def facts(self):
        return dict(gateMetadataReadBytes=self.gate_bytes, gateMetadataFileReads=self.gate_files,
                    gateReadByteCap=MAX_GATE_BYTES, gateFileReadCap=MAX_GATE_FILES, hashBlockBytes=65536,
                    identityQueries=self.identity_queries, identityHandlesOpened=self.identity_opened,
                    identityHandlesClosed=self.identity_closed, identityOwnedPeak=self.identity_peak,
                    identityRemaining=self.identity_owned, identityCloseUnknown=self.close_unknown,
                    metadataRemaining=list(self.metadata_owned), metadataCloseUnknown=self.metadata_close_unknown,
                    metadataCreditRemaining=self.metadata_credit, metadataHandlePeak=self.metadata_peak,
                    launchPublicationCalls=self.launch_publications, maximumLaunchPublications=1,
                    spawnCalls=self.spawn_calls, spawnError=self.spawn_error, parentPipes=0, parentCollectorWorkers=0,
                    spawnTemporaryDevnullHandleCap=4, spawnTemporaryPrimaryThreadHandleCap=1,
                    spawnParentKernelHandlePeakCap=6, parentProcessHandleCap=1,
                    parentSpawnCreditsRemaining=self.spawn_credit,
                    parentProcessHandleCloseProven=self.parent_handle_closed,
                    parentProcessHandleCloseUnknown=self.parent_handle_close_unknown,
                    resultHashBytes=self.result_hash_bytes, resultHashByteCap=6291456)

    def _inventory(self, include_root, manifest_name):
        rows = []; totals = dict(metadataBytes=0, fixtureBytes=0)
        roots = [self.base/'execution'] + ([self.base/'selfcheck'/ROOT_NAME] if include_root else [])
        for root in roots:
            if not root.exists():
                continue
            for directory, dirs, names in os.walk(self._safe(root), followlinks=False):
                require(len(rows) + len(dirs) + len(names) <= 512, 'RESULT_FILE_COUNT_LIMIT')
                for name in dirs:
                    self._safe(Path(directory)/name)
                for name in sorted(names):
                    path = self._safe(Path(directory)/name)
                    relative = path.relative_to(self.base).as_posix()
                    if relative == 'execution/' + manifest_name:
                        continue
                    require(stat.S_ISREG(os.lstat(path).st_mode), 'RESULT_NONREGULAR_DENIED')
                    kind = 'FIXTURE' if path.name in ('L.bin', 'C.bin', 'Z.bin') or path.suffix == '.out' else 'METADATA'
                    sha = hashlib.sha256(); count = 0
                    file = self._open_metadata(path, 'rb')
                    key = 'result:' + relative; self.metadata_owned[key] = file
                    try:
                        while True:
                            require(self.result_hash_bytes < 6291456, 'RESULT_HASH_BYTE_LIMIT')
                            block = file.read(min(65536, 6291456 - self.result_hash_bytes))
                            if not block:
                                break
                            count += len(block); self.result_hash_bytes += len(block)
                            require(self.result_hash_bytes <= 6291456, 'RESULT_HASH_BYTE_LIMIT')
                            sha.update(block)
                    finally:
                        self._close_metadata(key, file)
                    totals['fixtureBytes' if kind == 'FIXTURE' else 'metadataBytes'] += count
                    rows.append(dict(path=relative, bytes=count, sha256=sha.hexdigest(), kind=kind))
                    require(len(rows) <= 512, 'RESULT_FILE_COUNT_LIMIT')
        return rows, totals

    def record_result(self, receipt, freeze, late=False):
        self.create_new('execution/late-exit.json' if late else 'execution/launcher-result.json', receipt)
        exited = receipt.get('originalChildExitObserved') is True
        manifest_name = 'late-result-manifest.json' if late else 'result-manifest.json'
        complete = result_finalizable(receipt, self.spawn_calls,
                    self.identity_owned == 0 and not self.close_unknown and not self.metadata_owned and
                    not self.metadata_close_unknown and not self.parent_handle_close_unknown and self.spawn_error is None)
        if complete:
            files, usage = self._inventory(exited, manifest_name)
        else:
            # A live/unknown child can still write. Do not hash mutable root
            # files and present them as final; preserve the original PENDING.
            files, usage = [], dict(metadataBytes=None, fixtureBytes=None)
        value = dict(schema=1, scope='E2E_EXECUTION_RESULT_MANIFEST', batchId=BATCH,
                     status=receipt['status'], complete=complete,
                     expectedFreeze=receipt['expectedFreeze'], files=files, prepUsage=freeze['prepUsage'],
                     outputUsage=usage, combinedUsage={}, caps=LIMITS,
                     noInFlight=receipt.get('noInFlight'), originalChildExitObserved=exited,
                     manifestBytes=0, wrapperFacts=self.facts(), resultHashComplete=complete)
        for _ in range(16):
            size = len(encoded(value))
            if value['manifestBytes'] == size:
                break
            value['manifestBytes'] = size
            if usage['metadataBytes'] is not None:
                value.update(validate_result_inventory(self.batch, freeze['prepUsage'], files, size))
        require(value['manifestBytes'] == len(encoded(value)), 'RESULT_MANIFEST_SIZE_FIXED_POINT')
        if value['complete']:
            require(value['combinedUsage']['metadataBytes'] <= 4194304 and
                    value['combinedUsage']['fixtureBytes'] <= 2097152, 'RESULT_AGGREGATE_CAP_EXCEEDED')
        self.create_new('execution/' + manifest_name, value)
        return value
