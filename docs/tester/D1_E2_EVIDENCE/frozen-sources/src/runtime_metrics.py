"""Prepared, synchronous process-metadata observer; importing performs no OS IO.

The proposed real policy is deliberately not an execution capability. Only marked
synthetic readers may exercise MetricObserver in this batch. Win32MetricReader
is a separate explicit read-only adapter for later approved wiring or a separately
authorized self-process configuration check. Native calls are not interruptible;
elapsed deadlines stop acceptance after return, never prove a blocked call ended.
"""
from __future__ import annotations
import copy
import ctypes
from ctypes import wintypes
import math
import os
import threading
import time
from gcore import Stop, Refused, uid

_METRICS=('threads','handles','workingSetBytes','privateBytes')
_DELTAS=dict(threads='deltaThreads',handles='deltaHandles',workingSetBytes='deltaWorkingSetBytes',privateBytes='deltaPrivateBytes')


def _finite(value):
    return type(value) is int or (type(value) is float and math.isfinite(value))


class MetricObserver:
    """Bounded baseline/peak state, not an accumulating history or a sampler thread.

    samples is a cycle count; observations is the last fully validated role map.
    No real approval is recognized here. A future authorizer/runner must provide
    the separate reviewed execution capability before wiring this component.
    """
    def __init__(self,identities,reader,policy,approval=None):
        self.identities=copy.deepcopy(identities);self.reader=reader;self.policy=copy.deepcopy(policy);self.approval=copy.deepcopy(approval)
        self.samples=0;self.baselines={};self.peaks={};self.observations={};self.last_sample_time=None;self.last_call_time=None
        self.stopped=False;self.reasons=[];self.max_observed_gap=0;self.last_duration=None
        self.synthetic=type(self.approval) is dict and self.approval.get('mode')=='SYNTHETIC_POLICY_TEST_ONLY' and getattr(reader,'synthetic',False) is True
    def _result(self,status,sampled=False,reasons=None):
        return dict(status=status,scope='SYNTHETIC_POLICY_CHECK' if self.synthetic else 'RUNTIME_POLICY_NOT_ADMITTED',
                    stopAcceptance=status!='OBSERVED',reasons=list(self.reasons if reasons is None else reasons),samples=self.samples,
                    sampled=sampled,observations=copy.deepcopy(self.observations),baselines=copy.deepcopy(self.baselines),
                    peaks=copy.deepcopy(self.peaks),peaksAreSampled=True,maxObservedGapSeconds=self.max_observed_gap,
                    sampleDurationSeconds=self.last_duration,realExecutionApproved=False)
    def _stop(self,*reasons,sampled=False):
        self.stopped=True;self.reasons.extend(reason for reason in reasons if reason not in self.reasons)
        return self._result('STOP_PENDING',sampled)
    def _configuration_errors(self):
        errors=[];p=self.policy
        if not isinstance(p,dict):return ['RUNTIME_POLICY_SCHEMA']
        for name in ('intervalSeconds','maxGapSeconds','sampleDeadlineSeconds'):
            if not _finite(p.get(name)) or p[name]<=0:errors.append('RUNTIME_POLICY_INVALID:'+name)
        if type(p.get('maxSamples')) is not int or not 1<=p['maxSamples']<=201:errors.append('RUNTIME_POLICY_INVALID:maxSamples')
        if not isinstance(self.identities,dict) or not self.identities or not set(self.identities)<=set(('G','J','R')):return errors+['ORIGINAL_IDENTITIES_SCHEMA']
        for role,identity in self.identities.items():
            if not isinstance(identity,dict) or type(identity.get('pid')) is not int or identity['pid']<=0 or type(identity.get('creationTime100ns')) is not int or identity['creationTime100ns']<=0 or not isinstance(identity.get('owner'),str) or not identity['owner']:
                errors.append('ORIGINAL_IDENTITY_INVALID:'+role)
            all_limits=p.get('limits',{})
            limits=all_limits.get(role,{}) if isinstance(all_limits,dict) else {}
            if not isinstance(limits,dict):limits={}
            for name in (*_METRICS,*_DELTAS.values()):
                if not _finite(limits.get(name)) or limits[name]<0:errors.append('RUNTIME_POLICY_INVALID:'+role+':'+name)
        return errors
    def sample(self,now_seconds):
        if self.stopped:return self._result('STOP_PENDING')
        if not self.synthetic:return self._result('NOT_ADMITTED',reasons=['RUNTIME_POLICY_NOT_APPROVED'])
        errors=self._configuration_errors()
        if errors:return self._stop(*errors)
        if not _finite(now_seconds) or now_seconds<0:return self._stop('SAMPLE_TIME_INVALID')
        if self.last_call_time is not None and now_seconds<self.last_call_time:return self._stop('SAMPLE_CLOCK_ROLLBACK')
        self.last_call_time=now_seconds
        if self.last_sample_time is not None:
            gap=now_seconds-self.last_sample_time
            if gap>self.policy['maxGapSeconds']:return self._stop('SAMPLE_GAP_EXCEEDED')
            if gap<self.policy['intervalSeconds']:return self._result('OBSERVED')
        if self.samples>=self.policy['maxSamples']:return self._stop('SAMPLE_LIMIT_EXCEEDED')
        started=time.monotonic()
        try:
            if callable(getattr(self.reader,'read_cycle',None)):values=self.reader.read_cycle(copy.deepcopy(self.identities))
            else:values={role:self.reader(copy.deepcopy(identity)) for role,identity in self.identities.items()}
        except BaseException as error:
            self.last_duration=time.monotonic()-started
            reason=str(error)[:160] if isinstance(error,(Stop,Refused)) else type(error).__name__
            return self._stop('METRIC_READER_FAILED:'+reason)
        self.last_duration=time.monotonic()-started
        if not isinstance(values,dict) or set(values)!=set(self.identities):return self._stop('METRIC_CYCLE_SCHEMA')
        errors=[];validated={}
        for role,identity in self.identities.items():
            value=values.get(role)
            if not isinstance(value,dict):errors.append('METRIC_ROLE_SCHEMA:'+role);continue
            for name in ('pid','creationTime100ns'):
                if type(value.get(name)) is not int or value[name]!=identity[name]:errors.append('PROCESS_IDENTITY_CHANGED:'+role+':'+name)
            if 'owner' in value and value['owner']!=identity['owner']:errors.append('PROCESS_IDENTITY_CHANGED:'+role+':owner')
            metrics={}
            for name in _METRICS:
                if name not in value:errors.append('METRIC_MISSING:'+role+':'+name)
                elif not _finite(value[name]) or value[name]<0:errors.append('METRIC_INVALID:'+role+':'+name)
                else:metrics[name]=value[name]
            validated[role]=dict(pid=identity['pid'],creationTime100ns=identity['creationTime100ns'],owner=identity['owner'],**metrics)
        if errors:return self._stop(*errors)
        # Keep the threshold-crossing observation and its sampled peak. Neither
        # a lower later sample nor a stop call erases the original baseline.
        self.samples+=1;self.observations=validated
        if self.last_sample_time is not None:self.max_observed_gap=max(self.max_observed_gap,now_seconds-self.last_sample_time)
        self.last_sample_time=now_seconds
        for role,value in validated.items():
            if role not in self.baselines:self.baselines[role]=copy.deepcopy(value)
            peak=self.peaks.setdefault(role,{name:value[name] for name in _METRICS})
            for name in _METRICS:
                peak[name]=max(peak[name],value[name]);limit=self.policy['limits'][role]
                if value[name]>limit[name]:errors.append('METRIC_THRESHOLD_EXCEEDED:'+role+':'+name)
                if value[name]-self.baselines[role][name]>limit[_DELTAS[name]]:errors.append('METRIC_DELTA_EXCEEDED:'+role+':'+name)
        if self.last_duration>self.policy['sampleDeadlineSeconds']:errors.append('SAMPLE_DEADLINE_EXCEEDED_AFTER_RETURN')
        return self._stop(*errors,sampled=True) if errors else self._result('OBSERVED',sampled=True)


class _FILETIME(ctypes.Structure):
    _fields_=[('dwLowDateTime',wintypes.DWORD),('dwHighDateTime',wintypes.DWORD)]


class _THREADENTRY32(ctypes.Structure):
    _fields_=[('dwSize',wintypes.DWORD),('cntUsage',wintypes.DWORD),('th32ThreadID',wintypes.DWORD),
              ('th32OwnerProcessID',wintypes.DWORD),('tpBasePri',wintypes.LONG),('tpDeltaPri',wintypes.LONG),('dwFlags',wintypes.DWORD)]


class _PROCESS_MEMORY_COUNTERS_EX(ctypes.Structure):
    _fields_=[('cb',wintypes.DWORD),('PageFaultCount',wintypes.DWORD),
              *[(name,ctypes.c_size_t) for name in ('PeakWorkingSetSize','WorkingSetSize','QuotaPeakPagedPoolUsage','QuotaPagedPoolUsage',
                'QuotaPeakNonPagedPoolUsage','QuotaNonPagedPoolUsage','PagefileUsage','PeakPagefileUsage','PrivateUsage')]]


class Win32MetricReader:
    """One reserved observer slot and at most one OS handle at any instant.

    read_cycle takes one thread snapshot, closes it, then opens/closes each target
    process sequentially. Only target thread counts are retained. Unknown close
    permanently fences this reader and retains its ledger slot; no unsafe retry.
    The original owner strings are caller HELLO evidence, not queried OS fields.
    """
    synthetic=False
    def __init__(self,ledger,max_thread_entries=16384):
        if os.name!='nt':raise Refused('WIN32_METRICS_UNAVAILABLE')
        if type(max_thread_entries) is not int or not 1<=max_thread_entries<=16384:raise Refused('THREAD_ENUM_LIMIT_INVALID')
        if ledger is None:raise Refused('OBSERVER_LEDGER_REQUIRED')
        self.ledger=ledger;self.maximum=max_thread_entries;self.slot='runtime-observer/'+uid();self.reserved=False;self.close_unknown=False;self.active_handle=None
        self.cycles=0;self.opened=0;self.closed=0;self.peak_owned_handles=0;self.last_thread_entries=0;self._cycle_lock=threading.Lock()
        self.k=ctypes.WinDLL('kernel32',use_last_error=True)
        self.k.CreateToolhelp32Snapshot.argtypes=[wintypes.DWORD,wintypes.DWORD];self.k.CreateToolhelp32Snapshot.restype=wintypes.HANDLE
        self.k.Thread32First.argtypes=[wintypes.HANDLE,ctypes.POINTER(_THREADENTRY32)];self.k.Thread32First.restype=wintypes.BOOL
        self.k.Thread32Next.argtypes=[wintypes.HANDLE,ctypes.POINTER(_THREADENTRY32)];self.k.Thread32Next.restype=wintypes.BOOL
        self.k.OpenProcess.argtypes=[wintypes.DWORD,wintypes.BOOL,wintypes.DWORD];self.k.OpenProcess.restype=wintypes.HANDLE
        self.k.WaitForSingleObject.argtypes=[wintypes.HANDLE,wintypes.DWORD];self.k.WaitForSingleObject.restype=wintypes.DWORD
        self.k.GetProcessTimes.argtypes=[wintypes.HANDLE,*([ctypes.POINTER(_FILETIME)]*4)];self.k.GetProcessTimes.restype=wintypes.BOOL
        self.k.GetProcessHandleCount.argtypes=[wintypes.HANDLE,ctypes.POINTER(wintypes.DWORD)];self.k.GetProcessHandleCount.restype=wintypes.BOOL
        self.k.K32GetProcessMemoryInfo.argtypes=[wintypes.HANDLE,ctypes.POINTER(_PROCESS_MEMORY_COUNTERS_EX),wintypes.DWORD];self.k.K32GetProcessMemoryInfo.restype=wintypes.BOOL
        self.k.CloseHandle.argtypes=[wintypes.HANDLE];self.k.CloseHandle.restype=wintypes.BOOL
    def facts(self):
        return dict(scope='READ_ONLY_WIN32_PROCESS_METADATA',cycles=self.cycles,openedHandles=self.opened,closedHandles=self.closed,
                    maximumOwnedHandlesObserved=self.peak_owned_handles,observerCreditHeld=self.reserved,closeUnknown=self.close_unknown,
                    lastThreadEntries=self.last_thread_entries,mediaCalls=0,rpcCalls=0,newWorkers=0,peaksAreSampled=True)
    def _own(self,handle):
        self.active_handle=handle;self.opened+=1;self.peak_owned_handles=max(self.peak_owned_handles,1);return handle
    def _close(self):
        handle=self.active_handle
        if handle is None:return
        try:ok=self.k.CloseHandle(handle)
        except BaseException:
            self.close_unknown=True;raise Stop('OBSERVER_CLOSE_UNKNOWN')
        if not ok:self.close_unknown=True;raise Stop('OBSERVER_CLOSE_UNKNOWN')
        self.active_handle=None;self.closed+=1
    def _threads(self,identities):
        counts={identity['pid']:0 for identity in identities.values()};entry=_THREADENTRY32();entry.dwSize=ctypes.sizeof(entry)
        handle=self.k.CreateToolhelp32Snapshot(0x4,0)
        if handle in (None,ctypes.c_void_p(-1).value):raise Stop('THREAD_SNAPSHOT_UNAVAILABLE')
        self._own(handle);number=0
        try:
            ctypes.set_last_error(0);present=self.k.Thread32First(handle,ctypes.byref(entry))
            while present:
                number+=1
                if entry.th32OwnerProcessID in counts:counts[entry.th32OwnerProcessID]+=1
                if number>=self.maximum:raise Stop('THREAD_ENUM_LIMIT')
                ctypes.set_last_error(0);present=self.k.Thread32Next(handle,ctypes.byref(entry))
            if ctypes.get_last_error()!=18:raise Stop('THREAD_ENUM_UNKNOWN')
            return counts
        finally:self.last_thread_entries=number;self._close()
    def _process(self,identity,threads):
        handle=self.k.OpenProcess(0x101000,False,identity['pid'])
        if not handle:raise Stop('TARGET_PROCESS_QUERY_UNAVAILABLE')
        self._own(handle)
        try:
            created=_FILETIME();exited=_FILETIME();kernel=_FILETIME();user=_FILETIME();handles=wintypes.DWORD()
            memory=_PROCESS_MEMORY_COUNTERS_EX();memory.cb=ctypes.sizeof(memory)
            if not self.k.GetProcessTimes(handle,ctypes.byref(created),ctypes.byref(exited),ctypes.byref(kernel),ctypes.byref(user)):raise Stop('PROCESS_TIME_UNAVAILABLE')
            creation=(int(created.dwHighDateTime)<<32)|int(created.dwLowDateTime)
            if creation!=identity['creationTime100ns']:raise Stop('ORIGINAL_PROCESS_IDENTITY_CHANGED')
            # Exit FILETIME is undefined for a running process. A zero-time
            # process-object wait provides the explicit non-terminated sample.
            if self.k.WaitForSingleObject(handle,0)!=258:raise Stop('TARGET_PROCESS_EXITED_OR_UNKNOWN')
            if not self.k.GetProcessHandleCount(handle,ctypes.byref(handles)):raise Stop('PROCESS_HANDLE_COUNT_UNAVAILABLE')
            if not self.k.K32GetProcessMemoryInfo(handle,ctypes.byref(memory),ctypes.sizeof(memory)):raise Stop('PROCESS_MEMORY_UNAVAILABLE')
            return dict(pid=identity['pid'],creationTime100ns=creation,threads=threads,handles=int(handles.value),
                        workingSetBytes=int(memory.WorkingSetSize),privateBytes=int(memory.PrivateUsage))
        finally:self._close()
    def read_cycle(self,identities):
        if not self._cycle_lock.acquire(blocking=False):raise Stop('OBSERVER_OWNERSHIP_PENDING')
        try:return self._read_cycle_owned(identities)
        finally:self._cycle_lock.release()
    def _read_cycle_owned(self,identities):
        if self.close_unknown or self.reserved:raise Stop('OBSERVER_OWNERSHIP_PENDING')
        if not isinstance(identities,dict) or not identities or len(identities)>3:raise Refused('OBSERVED_IDENTITIES_SCHEMA')
        for role,identity in identities.items():
            if role not in ('G','J','R') or not isinstance(identity,dict) or type(identity.get('pid')) is not int or identity['pid']<=0 or type(identity.get('creationTime100ns')) is not int or identity['creationTime100ns']<=0:raise Refused('OBSERVED_IDENTITY_INVALID')
        try:self.ledger.acquire(self.slot,'G','observer')
        except BaseException as error:
            # Native code has not run, including with a trusted post-commit
            # reservation fault. Return only this unique unallocated slot.
            with self.ledger.lock:
                if self.slot in self.ledger.live:self.ledger.release(self.slot,'OPEN_NOT_ALLOCATED')
            raise Stop('OBSERVER_CREDIT_UNAVAILABLE') from error
        self.reserved=True;opened_before=self.opened
        try:
            counts=self._threads(identities)
            values={role:self._process(identity,counts[identity['pid']]) for role,identity in identities.items()}
            self.cycles+=1;return values
        finally:
            # Every successful query handle is closed by its own finally. A
            # close UNKNOWN leaves both the private handle value and the credit.
            if not self.close_unknown and self.active_handle is None:
                self.ledger.release(self.slot,'NATIVE_CLOSE_RETURNED' if self.opened>opened_before else 'OPEN_NOT_ALLOCATED');self.reserved=False
    def __call__(self,identity):return self.read_cycle({'G':identity})['G']
