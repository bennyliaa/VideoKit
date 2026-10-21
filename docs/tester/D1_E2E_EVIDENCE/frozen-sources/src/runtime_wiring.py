"""Observation uses the original Engine IO pool; no sampler worker or RPC."""
import json, os, threading, time
from gcore import BASE, Stop, need, compact, sha
from runtime_metrics import MetricObserver,Win32MetricReader,tool_policy_approval,fresh_memory_check


class RuntimeSampler:
    def __init__(self,engine,synthetic_mock=False):
        self.e=engine;self.thread=threading.get_ident();self.started=False;self.finished=False;self.busy=False
        self.exits_in_progress=False;self.reader=None;self.observer=None;self.pending_lines=[];self.header_written=False
        self.policy=json.loads((BASE/'profiles/runtime-policy.json').read_text(encoding='utf-8'))
        self.last=None;self.origin=None;self.fresh_memory=None;self.pending_query=False
        self.synthetic_mock=synthetic_mock
    def _invoke(self,fn):
        if self.pending_query:raise Stop('OBSERVER_QUERY_PENDING_RETAIN_ORIGINAL')
        try:return self.e.io_call(fn,timeout=min(.1,self.e.remaining()),observe=False)
        except BaseException:
            self.e.stopping=True;self.pending_query=any(not f.done() for f in self.e.pending.values());raise
    def start(self):
        need(not self.started,'OBSERVER_ALREADY_STARTED')
        self.origin=time.monotonic();self.reader=Win32MetricReader(self.e.ledger,self.policy['maxThreadEntries'])
        identity=self._invoke(lambda:self.reader.capture_identity(os.getpid(),'G'))
        self.fresh_memory=self._invoke(fresh_memory_check)
        # A low-memory result blocks future real admission. These are authored
        # synthetic fixtures, not permission to lower the real 2GiB floor.
        metric_reader=self.reader
        approval=tool_policy_approval(self.policy)
        if self.synthetic_mock:
            # Explicit driver regression only. Original identities still come
            # from OS handles; these values are never physical measurements.
            class MockMetrics:
                synthetic=True
                def read_cycle(self,identities):
                    return {role:dict(identity,threads=5,handles=100,workingSetBytes=33554432,privateBytes=33554432) for role,identity in identities.items()}
            metric_reader=MockMetrics();approval={'mode':'SYNTHETIC_POLICY_TEST_ONLY'}
        self.observer=MetricObserver({'G':identity},metric_reader,self.policy,approval)
        self.started=True;self.step()
        self.observer.ensure_ready(('G',))
    def attach(self):
        need(self.started and self.e.store.log is not None,'OBSERVER_LOG_NOT_READY')
        def write():
            header=compact(dict(runtimeMetricFormat=['milliseconds','G','J','R'],units=['threads','handles','workingSetKiB','privateKiB'],policySha256=sha(compact(self.policy)),scope='SAMPLED_ORIGINAL_TOOL_INSTANCES'))+b'\n'
            self.e.store.metric_record(header,header=True);self.header_written=True
            for line in self.pending_lines:self.e.store.metric_record(line)
            self.pending_lines=[]
        self._invoke(write)
    def eligible(self):
        return (self.started and not self.finished and not self.busy and not self.exits_in_progress and
                threading.get_ident()==self.thread and not self.e.lock._is_owned())
    def step(self):
        if self.pending_query:
            if getattr(self.e,'row',None)=='GC':return
            raise Stop('OBSERVER_QUERY_PENDING_RETAIN_ORIGINAL')
        if not self.eligible():return
        if self.observer.stopped:
            if getattr(self.e,'row',None)=='GC':return
            raise Stop('RUNTIME_OBSERVER_STOPPED')
        now=time.monotonic()
        if self.last is not None and now<self.observer.next_due_seconds():return
        self.busy=True
        try:
            self.e.store.ensure_writable()
            def sample():
                result=self.observer.sample(time.monotonic())
                if result['sampled'] and result['status']=='OBSERVED':
                    row=[round((time.monotonic()-self.origin)*1000)]
                    for role in ('G','J','R'):
                        value=result['observations'].get(role) if role in self.observer.identities else None
                        row.append(None if value is None else [value['threads'],value['handles'],(value['workingSetBytes']+1023)//1024,(value['privateBytes']+1023)//1024])
                    line=compact(row)+b'\n';need(len(line)<=128,'BLOCKED_OBSERVER_LOG_CREDIT')
                    if self.header_written:self.e.store.metric_record(line)
                    else:
                        need(len(self.pending_lines)<201,'BLOCKED_OBSERVER_LOG_CREDIT');self.pending_lines.append(line)
                return result
            self.last=self._invoke(sample)
            if self.last['status']!='OBSERVED':self.e.stopping=True;raise Stop('RUNTIME_STOP:'+','.join(self.last['reasons']))
        except BaseException:
            self.e.stopping=True;raise
        finally:self.busy=False
    def register(self,role,channel):
        identity=self._invoke(lambda:self.reader.capture_identity(channel.pid,channel.owner,process_handle=int(channel.process._handle)))
        self.observer.register_identities({role:identity})
        while role not in self.observer.baselines:
            need(self.e.remaining()>.001,'RUNTIME_BASELINE_DEADLINE')
            self.step()
            if role not in self.observer.baselines:time.sleep(min(.02,max(.001,self.observer.next_due_seconds()-time.monotonic())))
        self.observer.ensure_ready((role,))
        return identity
    def retired(self,role,proof):self.observer.retire_identity(role,proof)
    def finish(self):
        if not self.started:return
        if self.pending_query:return
        self.step();self.last=self.observer.finish();self.finished=True
    def facts(self):
        return dict(wired=True,started=self.started,finished=self.finished,nativeQueryPending=self.pending_query,
                    mode='SYNTHETIC_OBSERVER_MOCK' if self.synthetic_mock else 'ACTUAL_OS_OBSERVER',mockMetricsUsed=self.synthetic_mock,
                    policyState=self.policy['state'],GAnchor='BEFORE_PF_N01_NEVER_RESET',
                    originalIdentities=self.observer.original_identities if self.observer else {},
                    observation=self.last,reader=self.reader.facts() if self.reader else None,
                    freshMemory=self.fresh_memory,memoryFloorAppliesTo='FUTURE_REAL_ADMISSION',
                    log=dict(eventBytes=self.e.store.global_event_bytes,metricBytes=self.e.store.metric_bytes,metricRows=self.e.store.metric_rows),
                    newThreads=0,newRPC=0,newJournalTransactions=0,realExecutionAuthorized=False)
