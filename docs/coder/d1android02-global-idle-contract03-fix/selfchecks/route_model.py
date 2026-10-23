"""Synthetic kernel outputs only. Never imported by the live checker."""
import ctypes as C
from win32_route import D, Row4, Row6, Ledger, TOOL, TOOL_BYTES, OwnedHandle

CREATION = 134116992000000000  # 2026-01-01, exactly represented 100ns ticks

def table(rows, family=2):
    result = len(rows).to_bytes(4, 'little')
    for values in rows:
        r = Row4() if family == 2 else Row6()
        r.state = values.get('state', 2); r.pid = values.get('pid', 12345)
        r.port = int.from_bytes(values.get('port', 5037).to_bytes(2, 'big') + b'\0\0', 'little')
        import ipaddress
        addr = ipaddress.ip_address(values.get('address', '127.0.0.1' if family == 2 else '::1')).packed
        if family == 2:
            r.addr = int.from_bytes(addr, 'little')
        else:
            r.addr[:] = addr; r.scope = values.get('scope', 0)
        result += bytes(r)
    return result

class Model:
    def __init__(self, sha, path=TOOL, size=TOOL_BYTES):
        self.ledger = Ledger('OFFLINE_TABLES'); self.sha = sha
        self.path, self.size = path, size
        self.tables = [table([{}]), table([],23), table([{}]), table([],23)]
        self.index = 0; self.closed = []; self.opened = []; self.waits = 0
        self.identities = [dict(pid=12345, creation=CREATION, image=path)] * 2
        self.files = [dict(volume=1, fileId=2, creation=CREATION-1000,
            lastWrite=CREATION-1000, bytes=size, attrs=128, finalPath=path)] * 2
        self.identity_index = self.file_index = 0
        self.raise_at = None; self.close_fail = False; self.trace = []

    def step(self, name):
        self.trace.append(name)
        if self.raise_at == name:
            raise ValueError('MODEL_ERROR:' + name)

    def table(self, family):
        self.step('table' + str(self.index)); raw = self.tables[self.index]; self.index += 1
        if isinstance(raw, Exception):
            raise raw
        self.ledger.data['tableWorkflows'] += 1
        self.ledger.data['tableAllocatedBytes'] += len(raw)
        self.ledger.data['tableReturnedBytes'] += len(raw)
        self.ledger.charge(len(raw) + 8)
        return raw

    def invoke(self, name, value):
        self.step('close-' + str(value))
        self.closed.append(value)
        if self.close_fail:
            from win32_route import CloseUnknown
            raise CloseUnknown('MODEL_ONLY_CLOSE_UNKNOWN')
        return True

    def open_process(self, pid):
        self.step('open-process'); self.opened.append(pid)
        return OwnedHandle(self, 1, 'MODEL-process')

    def alive(self, h):
        assert h.value == 1
        self.step('wait' + str(self.waits)); self.waits += 1; self.ledger.charge(4)

    def identity(self, h, phase):
        assert h.value == 1
        self.step(phase); self.ledger.observe(phase)
        d = self.identities[self.identity_index]; self.identity_index += 1
        self.ledger.charge(40 + 2 * (len(d['image']) + 1))
        return d

    def open_image(self, image):
        self.step('open-image'); assert image == self.path
        return OwnedHandle(self, 2, 'MODEL-file')

    def file_identity(self, h):
        assert h.value == 2
        self.step('file' + str(self.file_index)); d = self.files[self.file_index]; self.file_index += 1
        self.ledger.charge(52 + 2 * (len(d['finalPath']) + 1)); return d

    def hash_image(self, h, expected_bytes):
        assert h.value == 2 and expected_bytes == self.size
        self.step('hash'); self.ledger.data['imageHashBytes'] += expected_bytes
        return self.sha
