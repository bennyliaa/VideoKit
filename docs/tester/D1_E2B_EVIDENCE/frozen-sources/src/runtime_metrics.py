"""Synchronous tool process metrics; importing performs no OS IO.

The E2A coordinator-approved observation strategy is separate from permission to
run a real-media batch. Native calls cannot be interrupted: elapsed deadlines
stop acceptance after return, never prove an unreturned query ended.
"""
from __future__ import annotations
import copy
import ctypes
from ctypes import wintypes
import math
import os
import threading
import time
from gcore import Stop, Refused, uid, compact, sha

_METRICS=('threads','handles','workingSetBytes','privateBytes')
_DELTAS=dict(threads='deltaThreads',handles='deltaHandles',workingSetBytes='deltaWorkingSetBytes',privateBytes='deltaPrivateBytes')
TOOL_POLICY_MODE='COORDINATOR_APPROVED_E2B_TOOL_POLICY'
TOOL_POLICY_REQUIREMENT='D1_E2B_CODER_REQUIREMENTS_V1.0'
MIN_AVAILABLE_PHYSICAL_BYTES=2147483648
_APPROVED_LIMITS={
    'G':dict(threads=16,handles=256,workingSetBytes=268435456,privateBytes=268435456,deltaThreads=12,deltaHandles=64,deltaWorkingSetBytes=134217728,deltaPrivateBytes=134217728),
    'J':dict(threads=64,handles=512,workingSetBytes=805306368,privateBytes=805306368,deltaThreads=32,deltaHandles=128,deltaWorkingSetBytes=268435456,deltaPrivateBytes=268435456),
    'R':dict(threads=64,handles=512,workingSetBytes=536870912,privateBytes=536870912,deltaThreads=32,deltaHandles=128,deltaWorkingSetBytes=268435456,deltaPrivateBytes=268435456)}


def _finite(value):
    return type(value) is int or (type(value) is float and math.isfinite(value))


def tool_policy_approval(policy):
    """Bind the already-granted E2A tool strategy; this is not a run capability."""
    return dict(mode=TOOL_POLICY_MODE,requirement=TOOL_POLICY_REQUIREMENT,
                policySha256=sha(compact(policy)),realExecutionAuthorized=False)


def _tool_policy_valid(policy,approval):
    if not isinstance(policy,dict):return False
    if type(approval) is not dict or approval.get('mode')!=TOOL_POLICY_MODE or approval.get('requirement')!=TOOL_POLICY_REQUIREMENT or approval.get('policySha256')!=sha(compact(policy)) or approval.get('realExecutionAuthorized') is not False:return False
    expected=dict(schema=1,state='APPROVED_TOOL_STRATEGY',executionAuthorized=False,
                  intervalSeconds=1,maxSamples=201,maxGapSeconds=2.5,sampleDeadlineSeconds=.1,
                  maxThreadEntries=16384,maxRecordBytes=128,maxLogBytes=26752,
                  minimumAvailablePhysicalBytes=MIN_AVAILABLE_PHYSICAL_BYTES)
    return (all(policy.get(key)==value and type(policy.get(key)) is not bool for key,value in expected.items() if key!='executionAuthorized') and
            policy.get('executionAuthorized') is False and
            policy.get('limits')==_APPROVED_LIMITS and
            policy.get('managedLimits')==dict(osResources=24,mediaHandles=6,buffers64KiB=8))


class MetricObserver:
    """Bounded baseline/peak state, not an accumulating history or a sampler thread.

    samples is a cycle count; observations is the last fully validated role map.
    G starts alone before PF. J/R may be registered once after original HELLO;
    the next scheduled cycle establishes their baselines without resetting G.
    """
    def __init__(self,identities,reader,policy,approval=None):
        self.identities=copy.deepcopy(identities);self.reader=reader;self.policy=copy.deepcopy(policy);self.approval=copy.deepcopy(approval)
        self.samples=0;self.baselines={};self.peaks={};self.observations={};self.last_sample_time=None;self.last_call_time=None
        self.stopped=False;self.reasons=[];self.max_observed_gap=0;self.last_duration=None
        self.synthetic=type(self.approval) is dict and self.approval.get('mode')=='SYNTHETIC_POLICY_TEST_ONLY' and getattr(reader,'synthetic',False) is True
        self.tool_approved=_tool_policy_valid(self.policy,self.approval)
        self._sample_lock=threading.Lock();self._state_lock=threading.RLock()
        self.registration_order=list(self.identities) if isinstance(self.identities,dict) else []
        self.original_identities=copy.deepcopy(self.identities);self.retired={};self.finished=False
    def _result(self,status,sampled=False,reasons=None):
        return dict(status=status,scope='SYNTHETIC_POLICY_CHECK' if self.synthetic else 'APPROVED_TOOL_RUNTIME_OBSERVATION' if self.tool_approved else 'RUNTIME_POLICY_NOT_ADMITTED',
                    stopAcceptance=status!='OBSERVED',reasons=list(self.reasons if reasons is None else reasons),samples=self.samples,
                    sampled=sampled,observations=copy.deepcopy(self.observations),baselines=copy.deepcopy(self.baselines),
                    peaks=copy.deepcopy(self.peaks),peaksAreSampled=True,maxObservedGapSeconds=self.max_observed_gap,
                    sampleDurationSeconds=self.last_duration,realExecutionApproved=False,
                    runtimePolicyApproved=self.tool_approved,baselineRoles=list(self.baselines),
                    registeredRoles=list(self.original_identities) if isinstance(self.original_identities,dict) else [],
                    activeRoles=list(self.identities) if isinstance(self.identities,dict) else [],
                    retired=copy.deepcopy(self.retired),observationFinished=self.finished,
                    gBaselineAnchor='ORIGINAL_PROCESS_BEFORE_PF_NOT_RESET')
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
        if self.tool_approved and 'G' not in self.identities:errors.append('ORIGINAL_G_BASELINE_REQUIRED')
        pids=[identity['pid'] for identity in self.identities.values() if isinstance(identity,dict) and type(identity.get('pid')) is int]
        if len(set(pids))!=len(pids):errors.append('PROCESS_IDENTITY_ROLE_ALIAS')
        for role,identity in self.identities.items():
            if not isinstance(identity,dict) or type(identity.get('pid')) is not int or identity['pid']<=0 or type(identity.get('creationTime100ns')) is not int or identity['creationTime100ns']<=0 or not isinstance(identity.get('owner'),str) or not identity['owner']:
                errors.append('ORIGINAL_IDENTITY_INVALID:'+role)
            all_limits=p.get('limits',{})
            limits=all_limits.get(role,{}) if isinstance(all_limits,dict) else {}
            if not isinstance(limits,dict):limits={}
            for name in (*_METRICS,*_DELTAS.values()):
                if not _finite(limits.get(name)) or limits[name]<0:errors.append('RUNTIME_POLICY_INVALID:'+role+':'+name)
        return errors
    def register_identities(self,identities):
        """Register original helper identities, not a replacement/rebase operation."""
        if not self._sample_lock.acquire(blocking=False):raise Stop('OBSERVER_CYCLE_PENDING')
        try:
            with self._state_lock:
                if self.stopped:raise Stop('RUNTIME_OBSERVER_STOPPED')
                if self.finished:raise Stop('RUNTIME_OBSERVER_FINISHED')
                if not(self.synthetic or self.tool_approved):raise Stop('RUNTIME_POLICY_NOT_APPROVED')
                if not isinstance(identities,dict) or not identities or not set(identities)<=set(('J','R')):raise Refused('HELPER_IDENTITY_REGISTRATION_SCHEMA')
                if self.tool_approved and 'G' not in self.baselines:raise Refused('G_BASELINE_REQUIRED_BEFORE_HELPERS')
                for role,identity in identities.items():
                    if role in self.original_identities:raise Refused('PROCESS_IDENTITY_ALREADY_REGISTERED:'+role)
                    if not isinstance(identity,dict) or type(identity.get('pid')) is not int or identity['pid']<=0 or type(identity.get('creationTime100ns')) is not int or identity['creationTime100ns']<=0 or not isinstance(identity.get('owner'),str) or not identity['owner']:raise Refused('ORIGINAL_IDENTITY_INVALID:'+role)
                    if any(identity['pid']==old['pid'] for old in self.original_identities.values()):raise Refused('PROCESS_IDENTITY_ROLE_ALIAS:'+role)
                if len({identity['pid'] for identity in identities.values()})!=len(identities):raise Refused('PROCESS_IDENTITY_ROLE_ALIAS')
                self.identities.update(copy.deepcopy(identities));self.original_identities.update(copy.deepcopy(identities));self.registration_order.extend(identities)
                return dict(registered=list(identities),baselinePending=[role for role in identities if role not in self.baselines],gBaselineReset=False)
        finally:self._sample_lock.release()
    def register_identity(self,role,identity):return self.register_identities({role:identity})
    def retire_identity(self,role,exit_proof):
        if not self._sample_lock.acquire(blocking=False):raise Stop('OBSERVER_CYCLE_PENDING')
        try:
            with self._state_lock:
                if role=='G':raise Refused('G_OBSERVATION_REQUIRED_UNTIL_FINISH')
                if role not in self.original_identities:raise Refused('ORIGINAL_IDENTITY_NOT_REGISTERED:'+str(role))
                if role in self.retired:raise Refused('PROCESS_IDENTITY_ALREADY_RETIRED:'+role)
                identity=self.original_identities[role]
                if not isinstance(exit_proof,dict) or exit_proof.get('exited') is not True or type(exit_proof.get('pid')) is not int or exit_proof['pid']!=identity['pid'] or exit_proof.get('instance',exit_proof.get('owner'))!=identity['owner'] or ('creationTime100ns' in exit_proof and exit_proof['creationTime100ns']!=identity['creationTime100ns']):raise Refused('ORIGINAL_EXIT_PROOF_MISMATCH:'+role)
                self.retired[role]=copy.deepcopy(exit_proof);self.identities.pop(role,None)
                return dict(retired=role,baselinePreserved=role in self.baselines,peaksPreserved=role in self.peaks)
        finally:self._sample_lock.release()
    def finish(self):
        if not self._sample_lock.acquire(blocking=False):raise Stop('OBSERVER_CYCLE_PENDING')
        try:
            with self._state_lock:self.finished=True
            return self._result('STOP_PENDING' if self.stopped else 'OBSERVED')
        finally:self._sample_lock.release()
    def ensure_ready(self,roles=None):
        with self._state_lock:
            if self.stopped:raise Stop('RUNTIME_OBSERVER_STOPPED')
            if self.finished:raise Stop('RUNTIME_OBSERVER_FINISHED')
            if not(self.synthetic or self.tool_approved):raise Stop('RUNTIME_POLICY_NOT_APPROVED')
            selected=set(self.identities if roles is None else roles)
            if not selected<=set(self.identities) or not selected<=set(self.baselines):raise Stop('RUNTIME_BASELINE_PENDING')
            return True
    def next_due_seconds(self):
        return None if self.last_sample_time is None else self.last_sample_time+self.policy['intervalSeconds']
    def sample(self,now_seconds):
        if not self._sample_lock.acquire(blocking=False):return self._stop('OBSERVER_CYCLE_PENDING')
        try:return self._sample_owned(now_seconds)
        finally:self._sample_lock.release()
    def _sample_owned(self,now_seconds):
        if self.stopped:return self._result('STOP_PENDING')
        if self.finished:return self._result('NOT_ADMITTED',reasons=['RUNTIME_OBSERVER_FINISHED'])
        if not(self.synthetic or self.tool_approved):return self._result('NOT_ADMITTED',reasons=['RUNTIME_POLICY_NOT_APPROVED'])
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
        if self.stopped:return self._result('STOP_PENDING')
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


class _MEMORYSTATUSEX(ctypes.Structure):
    _fields_=[('dwLength',wintypes.DWORD),('dwMemoryLoad',wintypes.DWORD),
              *[(name,ctypes.c_ulonglong) for name in ('ullTotalPhys','ullAvailPhys','ullTotalPageFile','ullAvailPageFile','ullTotalVirtual','ullAvailVirtual','ullAvailExtendedVirtual')]]


def read_memory_status():
    """Explicit, handle-free GlobalMemoryStatusEx call; not invoked on import."""
    if os.name!='nt':raise Refused('WIN32_MEMORY_METRICS_UNAVAILABLE')
    k=ctypes.WinDLL('kernel32',use_last_error=True)
    k.GlobalMemoryStatusEx.argtypes=[ctypes.POINTER(_MEMORYSTATUSEX)];k.GlobalMemoryStatusEx.restype=wintypes.BOOL
    memory=_MEMORYSTATUSEX();memory.dwLength=ctypes.sizeof(memory)
    if not k.GlobalMemoryStatusEx(ctypes.byref(memory)):raise Stop('MEMORY_STATUS_UNAVAILABLE')
    return dict(availablePhysicalBytes=int(memory.ullAvailPhys),totalPhysicalBytes=int(memory.ullTotalPhys),
                memoryLoadPercent=int(memory.dwMemoryLoad),observedAtMonotonic=time.monotonic(),
                source='FRESH_READ_ONLY_GLOBAL_MEMORY_STATUS_EX')


def fresh_memory_check(reader=None,now_seconds=None):
    """The approved 2GiB floor cannot be lowered by a caller or cached snapshot."""
    started=time.monotonic();reasons=[];value=None
    try:value=(reader or read_memory_status)()
    except BaseException as error:reasons.append('MEMORY_READER_FAILED:'+type(error).__name__)
    duration=time.monotonic()-started;now=time.monotonic() if now_seconds is None else now_seconds
    if not isinstance(value,dict):reasons.append('MEMORY_OBSERVATION_SCHEMA')
    else:
        available=value.get('availablePhysicalBytes');observed=value.get('observedAtMonotonic')
        if type(available) is not int or available<0:reasons.append('AVAILABLE_PHYSICAL_MEMORY_INVALID')
        elif available<MIN_AVAILABLE_PHYSICAL_BYTES:reasons.append('INSUFFICIENT_AVAILABLE_PHYSICAL_MEMORY')
        if not _finite(now) or not _finite(observed) or observed<0 or now<observed:reasons.append('MEMORY_OBSERVATION_TIME_INVALID')
        elif now-observed>.1:reasons.append('MEMORY_OBSERVATION_STALE')
    if duration>.1:reasons.append('MEMORY_DEADLINE_EXCEEDED_AFTER_RETURN')
    return dict(status='STOP_PENDING' if reasons else 'MEMORY_READY',stopAcceptance=bool(reasons),reasons=reasons,
                minimumAvailablePhysicalBytes=MIN_AVAILABLE_PHYSICAL_BYTES,observation=copy.deepcopy(value),
                sampleDurationSeconds=duration,realExecutionApproved=False)


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
        self.cycles=0;self.identity_queries=0;self.borrowed_identity_queries=0;self.opened=0;self.closed=0;self.peak_owned_handles=0;self.last_thread_entries=0;self._cycle_lock=threading.Lock()
        self.k=ctypes.WinDLL('kernel32',use_last_error=True)
        self.k.CreateToolhelp32Snapshot.argtypes=[wintypes.DWORD,wintypes.DWORD];self.k.CreateToolhelp32Snapshot.restype=wintypes.HANDLE
        self.k.Thread32First.argtypes=[wintypes.HANDLE,ctypes.POINTER(_THREADENTRY32)];self.k.Thread32First.restype=wintypes.BOOL
        self.k.Thread32Next.argtypes=[wintypes.HANDLE,ctypes.POINTER(_THREADENTRY32)];self.k.Thread32Next.restype=wintypes.BOOL
        self.k.OpenProcess.argtypes=[wintypes.DWORD,wintypes.BOOL,wintypes.DWORD];self.k.OpenProcess.restype=wintypes.HANDLE
        self.k.WaitForSingleObject.argtypes=[wintypes.HANDLE,wintypes.DWORD];self.k.WaitForSingleObject.restype=wintypes.DWORD
        self.k.GetProcessTimes.argtypes=[wintypes.HANDLE,*([ctypes.POINTER(_FILETIME)]*4)];self.k.GetProcessTimes.restype=wintypes.BOOL
        self.k.GetProcessId.argtypes=[wintypes.HANDLE];self.k.GetProcessId.restype=wintypes.DWORD
        self.k.GetProcessHandleCount.argtypes=[wintypes.HANDLE,ctypes.POINTER(wintypes.DWORD)];self.k.GetProcessHandleCount.restype=wintypes.BOOL
        self.k.K32GetProcessMemoryInfo.argtypes=[wintypes.HANDLE,ctypes.POINTER(_PROCESS_MEMORY_COUNTERS_EX),wintypes.DWORD];self.k.K32GetProcessMemoryInfo.restype=wintypes.BOOL
        self.k.CloseHandle.argtypes=[wintypes.HANDLE];self.k.CloseHandle.restype=wintypes.BOOL
    def facts(self):
        return dict(scope='READ_ONLY_WIN32_PROCESS_METADATA',cycles=self.cycles,identityQueries=self.identity_queries,borrowedIdentityQueries=self.borrowed_identity_queries,openedHandles=self.opened,closedHandles=self.closed,
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
    def capture_identity(self,pid,owner,process_handle=None):
        """Anchor one original process, with the same single temporary credit.

        The opaque owner is original G/HELLO evidence supplied by the caller;
        creation time and non-termination are read from the opened OS process.
        No thread snapshot, media read, pipe, helper or new worker is created.
        """
        if type(pid) is not int or pid<=0 or not isinstance(owner,str) or not owner:raise Refused('OBSERVED_IDENTITY_INVALID')
        borrowed=process_handle is not None
        if borrowed:
            try:
                if isinstance(process_handle,bool):raise ValueError('bool')
                borrowed_handle=int(process_handle)
                if borrowed_handle==0:raise ValueError('zero')
            except (TypeError,ValueError,OverflowError) as error:raise Refused('ORIGINAL_PROCESS_HANDLE_INVALID') from error
        if not self._cycle_lock.acquire(blocking=False):raise Stop('OBSERVER_OWNERSHIP_PENDING')
        try:
            if self.close_unknown or self.reserved:raise Stop('OBSERVER_OWNERSHIP_PENDING')
            with self.ledger.lock:reservation_prior=self.slot in self.ledger.live
            try:self.ledger.acquire(self.slot,'G','observer')
            except BaseException as error:
                with self.ledger.lock:
                    entry=self.ledger.live.get(self.slot)
                    if not reservation_prior and entry is not None and entry.get('owner')=='G' and entry.get('kind')=='observer':self.ledger.release(self.slot,'OPEN_NOT_ALLOCATED')
                raise Stop('OBSERVER_CREDIT_UNAVAILABLE') from error
            self.reserved=True;opened_before=self.opened
            try:
                handle=borrowed_handle if borrowed else self.k.OpenProcess(0x101000,False,pid)
                if not handle:raise Stop('TARGET_PROCESS_QUERY_UNAVAILABLE')
                if not borrowed:self._own(handle)
                try:
                    if borrowed and self.k.GetProcessId(handle)!=pid:raise Stop('ORIGINAL_PROCESS_HANDLE_IDENTITY_CHANGED')
                    created=_FILETIME();exited=_FILETIME();kernel=_FILETIME();user=_FILETIME()
                    if not self.k.GetProcessTimes(handle,ctypes.byref(created),ctypes.byref(exited),ctypes.byref(kernel),ctypes.byref(user)):raise Stop('PROCESS_TIME_UNAVAILABLE')
                    creation=(int(created.dwHighDateTime)<<32)|int(created.dwLowDateTime)
                    if creation<=0 or self.k.WaitForSingleObject(handle,0)!=258:raise Stop('TARGET_PROCESS_EXITED_OR_UNKNOWN')
                    self.identity_queries+=1
                    if borrowed:self.borrowed_identity_queries+=1
                    return dict(pid=pid,creationTime100ns=creation,owner=owner)
                finally:
                    if not borrowed:self._close()
            finally:
                if not self.close_unknown and self.active_handle is None:
                    self.ledger.release(self.slot,'NATIVE_CLOSE_RETURNED' if self.opened>opened_before else 'OPEN_NOT_ALLOCATED');self.reserved=False
        finally:self._cycle_lock.release()
    def read_cycle(self,identities):
        if not self._cycle_lock.acquire(blocking=False):raise Stop('OBSERVER_OWNERSHIP_PENDING')
        try:return self._read_cycle_owned(identities)
        finally:self._cycle_lock.release()
    def _read_cycle_owned(self,identities):
        if self.close_unknown or self.reserved:raise Stop('OBSERVER_OWNERSHIP_PENDING')
        if not isinstance(identities,dict) or not identities or len(identities)>3:raise Refused('OBSERVED_IDENTITIES_SCHEMA')
        for role,identity in identities.items():
            if role not in ('G','J','R') or not isinstance(identity,dict) or type(identity.get('pid')) is not int or identity['pid']<=0 or type(identity.get('creationTime100ns')) is not int or identity['creationTime100ns']<=0:raise Refused('OBSERVED_IDENTITY_INVALID')
        with self.ledger.lock:reservation_prior=self.slot in self.ledger.live
        try:self.ledger.acquire(self.slot,'G','observer')
        except BaseException as error:
            # Native code has not run, including with a trusted post-commit
            # reservation fault. Return only this unique unallocated slot.
            with self.ledger.lock:
                entry=self.ledger.live.get(self.slot)
                if not reservation_prior and entry is not None and entry.get('owner')=='G' and entry.get('kind')=='observer':self.ledger.release(self.slot,'OPEN_NOT_ALLOCATED')
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
