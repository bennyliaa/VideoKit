"""Fixed, read-only Win32 route observation for this candidate only.

Importing this module makes no OS calls. TCP access is explicitly enabled only
by the live entry point, after exact context validation. No CIM fallback.
"""
import ctypes as C
import hashlib, ipaddress, json, ntpath, os, sys, time
from datetime import datetime, timezone, timedelta
from pathlib import Path

BACKEND = 'WIN32_OWNER_PID_V1'
ORIGINAL_OVERRIDES = ('ADB_SERVER_SOCKET','ANDROID_ADB_SERVER_PORT','ADB_SERVER_PORT','ANDROID_ADB_SERVER_ADDRESS','ADB_VENDOR_KEYS','ANDROID_SERIAL')
ADDITIONAL_OVERRIDES = ('ADB_SERVER_ADDRESS',)
TOOL = 'D:/Android/SDK/platform-tools/adb.exe'
TOOL_BYTES = 8273560
TABLE_CAP = 8192
METADATA_CAP = 40960
PATH_CHARS = 512
D = C.c_uint32
H = C.c_void_p
B = C.c_int32
P = C.POINTER
CUSTODY = []
UINT32_MAX=(1<<32)-1
UINT64_MAX=(1<<64)-1
FORBIDDEN_IMAGE_ATTRIBUTES=16|64|1024 # directory, reserved device, reparse
FILE_FIELD_MAX={'volume':UINT32_MAX,'attrs':UINT32_MAX,'fileId':UINT64_MAX,
                'bytes':UINT64_MAX,'creation':UINT64_MAX,'lastWrite':UINT64_MAX}

class FileTime(C.Structure):
    _fields_ = [('low', D), ('high', D)]

class FileInfo(C.Structure):
    _fields_ = [('attrs', D), ('creation', FileTime), ('access', FileTime),
                ('write', FileTime), ('volume', D), ('sizeHigh', D),
                ('sizeLow', D), ('links', D), ('idHigh', D), ('idLow', D)]

class Row4(C.Structure):
    _fields_ = [(x, D) for x in ('state', 'addr', 'port', 'remote', 'remotePort', 'pid')]

class Row6(C.Structure):
    _fields_ = [('addr', C.c_ubyte * 16), ('scope', D), ('port', D),
                ('remote', C.c_ubyte * 16), ('remoteScope', D),
                ('remotePort', D), ('state', D), ('pid', D)]

class Table4(C.Structure):
    _fields_ = [('count', D), ('rows', Row4 * 1)]

class Table6(C.Structure):
    _fields_ = [('count', D), ('rows', Row6 * 1)]

def layout():
    # Candidate ABI: Windows AMD64, fixed DWORD widths, SDK default alignment.
    value = (C.sizeof(D), C.sizeof(Row4), C.sizeof(Row6),
             Table4.rows.offset, Table6.rows.offset, C.sizeof(FileInfo))
    if value != (4, 24, 56, 4, 4, 52):
        raise ValueError('UNSUPPORTED_ABI')
    return value

def exact_int(n, lo, hi):
    return type(n) is int and lo <= n <= hi

def filetime(f):
    return (int(f.high) << 32) | int(f.low)

def utc_filetime(n):
    if not exact_int(n, 1, 2650467743999999999):
        raise ValueError('FILETIME_RANGE')
    return (datetime(1601, 1, 1, tzinfo=timezone.utc) +
            timedelta(microseconds=n // 10)).isoformat()

def path_key(p):
    if type(p) is not str or not p or '\x00' in p:
        raise ValueError('IMAGE_PATH')
    if p.startswith('\\\\?\\'):
        p = p[4:]
    if len(p)<3 or p[0] not in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz' or p[1]!=':' or p[2] not in '\\/' or ':' in p[2:]:
        raise ValueError('LOCAL_IMAGE_PATH')
    for part in p[3:].replace('/','\\').split('\\'):
        if part not in ('','.','..') and part[-1] in ' .':
            raise ValueError('IMAGE_PATH_TRAILING_DOT_OR_SPACE')
    return ntpath.normcase(ntpath.normpath(p))

def regular_image_attrs(attrs):
    return exact_int(attrs,0,UINT32_MAX) and not(attrs&FORBIDDEN_IMAGE_ATTRIBUTES) and not(attrs&128 and attrs!=128)

def validate_file_identity(f,process_creation=None,success=False):
    if type(f) is not dict or set(f)!=set(FILE_FIELD_MAX)|{'finalPath'} or type(f['finalPath']) is not str:
        raise ValueError('QUERY_FILE_SCHEMA')
    for key,maximum in FILE_FIELD_MAX.items():
        if not exact_int(f[key],0,maximum):raise ValueError('QUERY_FILE_TYPE:'+key)
    if success:
        path_bytes=len(f['finalPath'].encode('utf-16-le'))
        if not 0<path_bytes<=2*(PATH_CHARS-1) or not regular_image_attrs(f['attrs']) or f['bytes']!=TOOL_BYTES or path_key(f['finalPath'])!=path_key(TOOL) or not 0<f['creation']<=process_creation or not 0<f['lastWrite']<=process_creation:
            raise ValueError('QUERY_IMAGE_BINDING')

def pairs(rows):
    d = {}; seen = set()
    for k, v in rows:
        if k.casefold() in seen:
            raise ValueError('DUPLICATE_JSON')
        d[k] = v; seen.add(k.casefold())
    return d

def decode(raw):
    return json.loads(raw.decode('utf-8-sig'), object_pairs_hook=pairs)

def encode(d):
    return (json.dumps(d, ensure_ascii=False, separators=(',', ':')) + '\n').encode()

STATS_KEYS = set('mode logicalObservations tcpCalls tableWorkflows tableAllocatedBytes tableReturnedBytes metadataBytesKnown metadataAmountUnknown imageHashBytes imageHashAmountUnknown imageHashBytesReservedUnknown apiCalls observationOrder processCreationFiletime imageFileIdentity'.split())
API_LIMITS = {'GetExtendedTcpTable':8, 'OpenProcess':1, 'GetProcessId':2,
    'GetProcessTimes':2, 'QueryFullProcessImageNameW':2, 'WaitForSingleObject':2,
    'GetFileAttributesW':16, 'CreateFileW':1, 'GetFileInformationByHandle':2,
    'GetFinalPathNameByHandleW':2, 'ReadFile':127, 'CloseHandle':2}

def validate_stats(s, fixture=False, success=True):
    if type(s) is not dict or set(s) != STATS_KEYS:
        raise ValueError('QUERY_STATS_SCHEMA')
    mode = 'OFFLINE_TABLES' if fixture else 'LIVE_SYSTEM_API'
    if s['mode'] != mode or type(s['metadataAmountUnknown']) is not bool or type(s['imageHashAmountUnknown']) is not bool:
        raise ValueError('QUERY_STATS_MODE')
    for k, cap in {'logicalObservations':4, 'tcpCalls':8, 'tableWorkflows':4,
                   'tableAllocatedBytes':32768, 'tableReturnedBytes':32768,
                   'metadataBytesKnown':METADATA_CAP, 'imageHashBytes':TOOL_BYTES,
                   'imageHashBytesReservedUnknown':TOOL_BYTES,
                   'processCreationFiletime':2650467743999999999}.items():
        if not exact_int(s[k], 0, cap):
            raise ValueError('QUERY_STATS_INTEGER:' + k)
    if type(s['apiCalls']) is not dict or set(s['apiCalls']) - set(API_LIMITS):
        raise ValueError('QUERY_API_SCHEMA')
    for k, n in s['apiCalls'].items():
        if not exact_int(n, 1, API_LIMITS[k]):
            raise ValueError('QUERY_API_BOUND:' + k)
    if s['tcpCalls'] != s['apiCalls'].get('GetExtendedTcpTable', 0):
        raise ValueError('QUERY_TCP_ACCOUNTING')
    if s['tableReturnedBytes'] > s['tableAllocatedBytes'] or s['imageHashBytes']+s['imageHashBytesReservedUnknown']>TOOL_BYTES or (s['imageHashBytesReservedUnknown'] and not s['imageHashAmountUnknown']):
        raise ValueError('QUERY_OUTPUT_ACCOUNTING')
    if not fixture and not s['tableWorkflows'] <= s['tcpCalls'] <= 2*s['tableWorkflows']:
        raise ValueError('QUERY_TABLE_CALL_RELATION')
    if type(s['observationOrder']) is not list or s['observationOrder'] != ['L1','P1','P2','L2'][:s['logicalObservations']]:
        raise ValueError('QUERY_ORDER')
    f = s['imageFileIdentity']
    if type(f) is not dict:
        raise ValueError('QUERY_FILE_SCHEMA')
    if f:
        validate_file_identity(f)
    if success:
        if s['metadataAmountUnknown'] or s['imageHashAmountUnknown'] or s['imageHashBytesReservedUnknown'] or s['logicalObservations'] != 4 or not f or not s['processCreationFiletime'] or not s['metadataBytesKnown'] or s['imageHashBytes'] != TOOL_BYTES or s['tableWorkflows'] != 4 or s['tableReturnedBytes']<2*(4+24)+2*4:
            raise ValueError('QUERY_SUCCESS_FACTS')
        if fixture:
            if s['tcpCalls'] or s['apiCalls']:
                raise ValueError('FIXTURE_OS_API_FORBIDDEN')
        else:
            required = {k:v for k,v in API_LIMITS.items() if k != 'GetFileAttributesW'}
            # Fixed known tool length requires exactly 127 bounded hash reads.
            if any(s['apiCalls'].get(k) != v for k,v in required.items()) or not 1 <= s['apiCalls'].get('GetFileAttributesW',0) <= 16:
                raise ValueError('LIVE_RAW_CALLS')
        validate_file_identity(f,s['processCreationFiletime'],True)
        lo,hi=metadata_bounds(s,fixture)
        if not lo <= s['metadataBytesKnown'] <= hi:
            raise ValueError('QUERY_METADATA_DERIVED_BOUNDS')

def metadata_bounds(s, fixture=False):
    # Success-only original producer fees, not guessed host totals. Each
    # process-name result is nonempty UTF16 plus NUL, up to512 code units.
    a=s['apiCalls'] if not fixture else dict(GetProcessId=2,GetProcessTimes=2,
        QueryFullProcessImageNameW=2,WaitForSingleObject=2,
        GetFileInformationByHandle=2,GetFinalPathNameByHandleW=2)
    base=s['tableReturnedBytes']+4*(s['tcpCalls'] if not fixture else 2*s['tableWorkflows'])
    for name,fee in {'GetProcessId':4,'GetProcessTimes':32,'QueryFullProcessImageNameW':4,
        'WaitForSingleObject':4,'GetFileInformationByHandle':52,'GetFileAttributesW':4,'ReadFile':4}.items():
        base+=fee*a.get(name,0)
    base+=(len(s['imageFileIdentity']['finalPath'].encode('utf-16-le'))+2)*a.get('GetFinalPathNameByHandleW',0)
    n=a.get('QueryFullProcessImageNameW',0)
    minimum_name_bytes=len(path_key(TOOL).encode('utf-16-le'))+2
    return base+minimum_name_bytes*n,base+2*PATH_CHARS*n

class Ledger:
    def __init__(self, mode):
        self.data = dict(mode=mode, logicalObservations=0, tcpCalls=0,
            tableWorkflows=0, tableAllocatedBytes=0, tableReturnedBytes=0,
            metadataBytesKnown=0, metadataAmountUnknown=False, imageHashBytes=0, imageHashAmountUnknown=False,imageHashBytesReservedUnknown=0,
            apiCalls={}, observationOrder=[], processCreationFiletime=0,
            imageFileIdentity={})

    def call(self, name):
        a = self.data['apiCalls']
        if name not in API_LIMITS or a.get(name, 0) >= API_LIMITS[name]:
            raise ValueError('RAW_API_CALL_BOUND:' + name)
        a[name] = a.get(name, 0) + 1

    def charge(self, n):
        self.data['metadataBytesKnown'] += n
        if self.data['metadataBytesKnown'] > METADATA_CAP:
            raise ValueError('METADATA_BOUND')

    def observe(self, name):
        self.data['logicalObservations'] += 1
        self.data['observationOrder'].append(name)
        if self.data['logicalObservations'] > 4:
            raise ValueError('LOGICAL_QUERY_BOUND')

def parse_table(raw, family):
    layout()
    if family not in (2, 23) or type(raw) is not bytes or not 4 <= len(raw) <= TABLE_CAP:
        raise ValueError('TABLE_BUFFER')
    row_type, offset = (Row4, Table4.rows.offset) if family == 2 else (Row6, Table6.rows.offset)
    count = int.from_bytes(raw[:4], 'little'); stride = C.sizeof(row_type)
    if count > 128 or len(raw) < offset + count * stride:
        raise ValueError('TABLE_COUNT_OR_TRUNCATION')
    rows = []
    for i in range(count):
        r = row_type.from_buffer_copy(raw, offset + i * stride)
        # GetExtendedTcpTable OWNER_PID_LISTENER still cannot make malformed
        # or non-listener fixture rows into target listeners.
        if r.state != 2:
            continue
        port_raw = int(r.port).to_bytes(4, 'little')
        if port_raw[2:] != b'\x00\x00':
            raise ValueError('PORT_HIGH_BITS')
        port = int.from_bytes(port_raw[:2], 'big')
        if port != 5037:
            continue
        addr = str(ipaddress.ip_address(int(r.addr).to_bytes(4, 'little') if family == 2 else bytes(r.addr)))
        if not exact_int(int(r.pid), 1, 2147483647):
            raise ValueError('TARGET_PID')
        rows.append(dict(family=family, address=addr, port=port,
                         scope=0 if family == 2 else int(r.scope), pid=int(r.pid)))
    return rows

def listener(api, name):
    api.ledger.observe(name)
    # Both complete tables must succeed before endpoint filtering/selection.
    raw4 = api.table(2); raw6 = api.table(23)
    rows = parse_table(raw4, 2) + parse_table(raw6, 23)
    if len(rows) != 1 or rows[0]['family'] != 2 or rows[0]['address'] != '127.0.0.1':
        raise ValueError('DEFAULT_LISTENER_NOT_UNIQUE')
    return rows[0]

class OwnedHandle:
    def __init__(self, api, value, label):
        self.api, self.value, self.label = api, value, label
        self.close_entered = False; self.closed = False
        CUSTODY.append(self)

    def close(self):
        if self.close_entered:
            raise ValueError('CLOSE_ONCE')
        self.close_entered = True
        try:
            self.api.invoke('CloseHandle', self.value)
        except Exception as e:
            raise CloseUnknown('ORIGINAL_CLOSE_UNKNOWN:' + str(e)) from e
        self.closed = True; CUSTODY.remove(self)

class CloseUnknown(RuntimeError):
    pass

class Native:
    def __init__(self, ledger, *, allow_tcp=False):
        layout()
        if os.name != 'nt' or C.sizeof(H) != 8 or C.sizeof(C.c_wchar) != 2:
            raise ValueError('WINDOWS_AMD64_ONLY')
        self.ledger = ledger; self.allow_tcp = allow_tcp
        self.k = C.WinDLL('kernel32.dll', use_last_error=True, winmode=0x800)
        self.ip = C.WinDLL('iphlpapi.dll', use_last_error=True, winmode=0x800) if allow_tcp else None
        defs = {
            'OpenProcess': (H, [D, B, D]), 'CloseHandle': (B, [H]),
            'GetProcessId': (D, [H]),
            'GetProcessTimes': (B, [H, P(FileTime), P(FileTime), P(FileTime), P(FileTime)]),
            'QueryFullProcessImageNameW': (B, [H, D, C.c_wchar_p, P(D)]),
            'WaitForSingleObject': (D, [H, D]),
            'CreateFileW': (H, [C.c_wchar_p, D, D, H, D, D, H]),
            'GetFileInformationByHandle': (B, [H, P(FileInfo)]),
            'GetFinalPathNameByHandleW': (D, [H, C.c_wchar_p, D, D]),
            'GetFileAttributesW': (D, [C.c_wchar_p]),
            'ReadFile': (B, [H, H, D, P(D), H]),
        }
        for name, (restype, args) in defs.items():
            fn = getattr(self.k, name); fn.restype = restype; fn.argtypes = args
        if allow_tcp:
            self.ip.GetExtendedTcpTable.restype = D
            self.ip.GetExtendedTcpTable.argtypes = [H, P(D), B, D, D, D]

    def invoke(self, name, *args):
        fn=getattr(self.k,name) # failed lookup has not entered the FFI call
        self.ledger.call(name)
        try:
            result = fn(*args)
        except Exception as e:
            resource=name in ('OpenProcess','CreateFileW','CloseHandle')
            if resource:
                self.resource_unknown=True;self.unknown_original=(name,args,e);CUSTODY.append(self)
            try:
                self.failed_output(name,args)
            finally:
                if resource:raise CloseUnknown('ORIGINAL_NATIVE_HANDLE_RETURN_UNKNOWN:'+name) from e
            raise
        if name == 'CloseHandle' and not result:
            self.failed_output(name,args)
            raise CloseUnknown('CLOSE_RETURN_UNKNOWN:' + str(C.get_last_error()))
        if name in ('GetProcessTimes', 'QueryFullProcessImageNameW', 'GetFileInformationByHandle', 'ReadFile') and not result:
            self.failed_output(name,args)
            raise ValueError(name + ':' + str(C.get_last_error()))
        return result

    def failed_output(self,name,args):
        self.ledger.data['metadataAmountUnknown']=True
        if name=='ReadFile':
            cap=args[2] if len(args)>2 and exact_int(args[2],1,65536) else 65536
            self.ledger.data['imageHashAmountUnknown']=True
            self.ledger.data['imageHashBytesReservedUnknown']+=cap
        fee={'OpenProcess':8,'CreateFileW':8,'CloseHandle':4,'GetProcessId':4,
             'GetProcessTimes':32,'QueryFullProcessImageNameW':4+2*PATH_CHARS,
             'WaitForSingleObject':4,'GetFileInformationByHandle':C.sizeof(FileInfo),
             'GetFinalPathNameByHandleW':4+2*PATH_CHARS,'GetFileAttributesW':4,'ReadFile':4}[name]
        self.ledger.charge(fee)

    def table(self, family):
        if not self.allow_tcp or self.ledger.data['mode'] != 'LIVE_SYSTEM_API':
            raise ValueError('TCP_NOT_AUTHORIZED')
        if family not in (2, 23) or self.ledger.data['tcpCalls'] >= 8:
            raise ValueError('TCP_CALL_BOUND')
        self.ledger.data['tableWorkflows'] += 1
        size = D(0)
        def call(buf):
            self.ledger.call('GetExtendedTcpTable'); self.ledger.data['tcpCalls'] += 1
            try:
                code = self.ip.GetExtendedTcpTable(buf, C.byref(size), False, family, 3, 0)
            except Exception:
                self.ledger.data['metadataAmountUnknown'] = True
                self.ledger.charge(4 + (0 if buf is None else C.sizeof(buf)))
                raise
            self.ledger.charge(4)
            return code
        code = call(None)
        if code != 122 or not 4 <= size.value <= TABLE_CAP:
            raise ValueError('TCP_SIZE:' + str(code))
        allocated = int(size.value); buf = C.create_string_buffer(allocated)
        self.ledger.data['tableAllocatedBytes'] += allocated
        code = call(buf)
        # Failed fill size may be a required length, not copied bytes. Charge
        # the entire allocated output buffer conservatively, mark actual
        # returned amount unknown; never retry or report an empty table.
        if code or not 4 <= size.value <= allocated:
            self.ledger.charge(allocated)
            self.ledger.data['metadataAmountUnknown'] = True
            raise ValueError('TCP_FILL:' + str(code))
        n = int(size.value); self.ledger.data['tableReturnedBytes'] += n
        self.ledger.charge(n)
        return bytes(buf.raw[:n])

    def open_process(self, pid):
        value = self.invoke('OpenProcess', 0x101000, False, pid)
        if not value:
            raise ValueError('OPEN_PROCESS:' + str(C.get_last_error()))
        return OwnedHandle(self, value, 'exact-listener-process')

    def alive(self, h):
        value = self.invoke('WaitForSingleObject', h.value, 0)
        self.ledger.charge(4)
        if value != 258:
            raise ValueError('PROCESS_NOT_LIVE:' + str(value))

    def identity(self, h, phase):
        self.ledger.observe(phase)
        pid = int(self.invoke('GetProcessId', h.value)); self.ledger.charge(4)
        times = [FileTime() for _ in range(4)]
        self.invoke('GetProcessTimes', h.value, *(C.byref(v) for v in times)); self.ledger.charge(32)
        creation = filetime(times[0]); utc_filetime(creation)
        if not pid or creation > int((datetime.now(timezone.utc) - datetime(1601, 1, 1, tzinfo=timezone.utc)) // timedelta(microseconds=1)) * 10:
            raise ValueError('PROCESS_TIME_OR_PID')
        buf = C.create_unicode_buffer(PATH_CHARS); size = D(PATH_CHARS)
        self.invoke('QueryFullProcessImageNameW', h.value, 0, buf, C.byref(size))
        if not 0 < size.value < PATH_CHARS:
            self.ledger.charge(1028); self.ledger.data['metadataAmountUnknown'] = True
            raise ValueError('IMAGE_PATH_TRUNCATED')
        image = buf[:size.value]; self.ledger.charge(4 + 2 * (size.value + 1))
        path_key(image)
        return dict(pid=pid, creation=creation, image=image)

    def open_image(self, image):
        path_key(image)
        parts = [Path(image), *Path(image).parents]
        if len(parts) > 16:
            raise ValueError('IMAGE_ANCESTOR_BOUND')
        for p in parts:
            attrs = int(self.invoke('GetFileAttributesW', str(p))); self.ledger.charge(4)
            if attrs == 0xffffffff or attrs & 1024:
                raise ValueError('IMAGE_REPARSE_OR_ATTRIBUTES')
        value = self.invoke('CreateFileW', image, 0x80000000, 1, None, 3, 0x00200080, None)
        if value in (None, C.c_void_p(-1).value):
            raise ValueError('OPEN_EXISTING_IMAGE:' + str(C.get_last_error()))
        return OwnedHandle(self, value, 'exact-image-file')

    def file_identity(self, h):
        info = FileInfo(); self.invoke('GetFileInformationByHandle', h.value, C.byref(info))
        self.ledger.charge(C.sizeof(info))
        buf = C.create_unicode_buffer(PATH_CHARS)
        n = int(self.invoke('GetFinalPathNameByHandleW', h.value, buf, PATH_CHARS, 0))
        if not 0 < n < PATH_CHARS:
            self.ledger.charge(1024); self.ledger.data['metadataAmountUnknown'] = True
            raise ValueError('FILE_FINAL_PATH_TRUNCATED')
        self.ledger.charge(2 * (n + 1))
        if not regular_image_attrs(int(info.attrs)) or not info.links:
            raise ValueError('IMAGE_FILE_ATTRIBUTES')
        return dict(volume=int(info.volume), fileId=(int(info.idHigh) << 32) | int(info.idLow),
            creation=filetime(info.creation), lastWrite=filetime(info.write),
            bytes=(int(info.sizeHigh) << 32) | int(info.sizeLow), attrs=int(info.attrs),
            finalPath=buf[:n])

    def hash_image(self, h, expected_bytes):
        digest = hashlib.sha256(); total = 0
        while total < expected_bytes:
            cap = min(65536, expected_bytes - total)
            buf = C.create_string_buffer(cap); n = D(0)
            self.invoke('ReadFile', h.value, buf, cap, C.byref(n), None)
            self.ledger.charge(4)
            if not 0 < n.value <= cap:
                raise ValueError('IMAGE_HASH_SHORT_READ')
            total += int(n.value); self.ledger.data['imageHashBytes'] += int(n.value)
            digest.update(buf.raw[:n.value])
        return digest.hexdigest()

def sample(api, expected_path, expected_sha, expected_bytes):
    process = image = None
    try:
        first = listener(api, 'L1')
        process = api.open_process(first['pid'])
        p1 = api.identity(process, 'P1'); api.alive(process)
        api.ledger.data['processCreationFiletime'] = p1['creation']
        if p1['pid'] != first['pid'] or path_key(p1['image']) != path_key(expected_path):
            raise ValueError('PROCESS_IMAGE_BINDING')
        image = api.open_image(p1['image']); f1 = api.file_identity(image)
        api.ledger.data['imageFileIdentity'] = f1
        if f1['bytes'] != expected_bytes or path_key(f1['finalPath']) != path_key(expected_path) or not 0 < f1['creation'] <= p1['creation'] or not 0 < f1['lastWrite'] <= p1['creation']:
            raise ValueError('IMAGE_FILE_BINDING')
        digest = api.hash_image(image, expected_bytes)
        if digest != expected_sha:
            raise ValueError('IMAGE_HASH')
        p2 = api.identity(process, 'P2')
        second = listener(api, 'L2')
        # Original handles survive exit; this guard must be AFTER L2.
        api.alive(process)
        f2 = api.file_identity(image)
        if first != second or p1 != p2 or f1 != f2:
            raise ValueError('GENERATION_CHANGED')
        api.ledger.data['processCreationFiletime'] = p1['creation']
        api.ledger.data['imageFileIdentity'] = f1
        return dict(serverPid=p1['pid'], serverCreationUtc=utc_filetime(p1['creation']),
                    serverImage=p1['image'], serverFileSha256=digest)
    finally:
        # If close is unknown, execution stops here and the outer entry keeps
        # all remaining original objects; no second close of either object.
        if image is not None and not getattr(api,'resource_unknown',False):
            image.close()
        if process is not None and not getattr(api,'resource_unknown',False):
            process.close()

def validate_context(c):
    keys = set('kind scope planId generation toolPath toolSha256 toolBytes routeBackend'.split())
    if type(c) is not dict or set(c) != keys or any(type(c[k]) is not str for k in keys - {'toolBytes'}):
        raise ValueError('CONTEXT_SCHEMA')
    if c['kind'] != 'LIVE_LOCAL_METADATA' or c['routeBackend'] != BACKEND or c['toolPath'] != TOOL or c['toolBytes'] != TOOL_BYTES or type(c['toolBytes']) is not int:
        raise ValueError('FIXED_BACKEND_CONTEXT')
    if any(not c[k] for k in ('scope', 'planId', 'generation')) or len(c['toolSha256']) != 64 or any(x not in '0123456789abcdef' for x in c['toolSha256']):
        raise ValueError('CONTEXT_IDENTITY')
    for k in ORIGINAL_OVERRIDES+ADDITIONAL_OVERRIDES:
        if os.environ.get(k) is not None:
            raise ValueError('ROUTING_OVERRIDE:' + k)

def main():
    ledger = Ledger('LIVE_SYSTEM_API')
    try:
        if len(sys.argv) != 2:
            raise ValueError('EXACT_CONTEXT_ARGUMENT')
        with Path(sys.argv[1]).open('rb') as f:
            raw = f.read(8193)
        if len(raw) > 8192:
            raise ValueError('CONTEXT_BOUND')
        c = decode(raw); validate_context(c)
        api = Native(ledger, allow_tcp=True)
        d = sample(api, c['toolPath'], c['toolSha256'], c['toolBytes'])
        d.update(schema='ENTRY_LOCAL_ROUTE_V2', kind=c['kind'], scope=c['scope'],
            planId=c['planId'], generation=c['generation'],
            checkedAtUtc=datetime.now(timezone.utc).isoformat(), endpoint='127.0.0.1:5037',
            identityStable=True, routingOverrides={}, contextReadBytes=len(raw), queryCount=4,
            sourceSha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            routeBackend=BACKEND, queryStats=ledger.data)
        output = encode(d)
        if len(output) > 8192:
            raise ValueError('ROUTE_OUTPUT_BOUND')
        sys.stdout.buffer.write(output); sys.stdout.buffer.flush()
        return 0
    except CloseUnknown as e:
        sys.stderr.write(str(e) + '\n'); sys.stderr.flush()
        while True:
            time.sleep(.05)  # keep originals, no success/exit/retry/second close
    except Exception as e:
        output = encode(dict(schema='ENTRY_LOCAL_ROUTE_REJECT_V2', routeBackend=BACKEND,
                             error=str(e)[:256], queryStats=ledger.data))
        sys.stdout.buffer.write(output); sys.stdout.buffer.flush()
        return 2

if __name__ == '__main__':
    raise SystemExit(main())
