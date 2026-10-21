"""T05 self-owned writer injections. No child, native bridge, media, or disk fault.

The Flow checks exercise the real admission ordering with a minimal Engine double;
the downstream counter is a logical unit probe, never a platform/native PASS.
"""
from __future__ import annotations
import copy, threading
from pathlib import Path
from gcore import Budget, Ledger, Stop, Store, compact, need
from gengine import Flow


class _InjectedWriter:
    def __init__(self,raw,path,factory):self.raw=raw;self.path=path;self.factory=factory
    def __getattr__(self,name):return getattr(self.raw,name)
    def write(self,data):
        f=self.factory;f.write_calls+=1
        if f.predicate(self.path):
            f.matched+=1
            if f.matched==f.at:
                f.fault_calls+=1
                if f.returned=='RAISE_SELF_OWNED':raise OSError('SELF_OWNED_WRITER_INJECTION')
                value=f.returned
                # Simulate only a returned count on this wrapper's own file. This
                # does not fill a disk, alter permissions, or fault any other writer.
                if type(value) is int and 0<=value<=len(data):self.raw.write(data[:value])
                return value
        return self.raw.write(data)


class _WriterFactory:
    def __init__(self,predicate,returned,at=1,fail_construct=False):
        self.predicate=predicate;self.returned=returned;self.at=at;self.fail_construct=fail_construct
        self.matched=0;self.fault_calls=0;self.write_calls=0;self.opened=[]
    def __call__(self,raw,path,mode):
        self.opened.append(raw)
        if self.fail_construct:raise ValueError('SELF_OWNED_WRAPPER_CONSTRUCTION')
        return _InjectedWriter(raw,path,self)


class _AdmissionProbe:
    """Real Flow + Store; action invocation is the sole logical downstream probe."""
    def __init__(self,root,manifest,factory):
        self.root=root;self.manifest=manifest;self.lock=threading.RLock();self.ledger=Ledger();self.store=Store(root,self.ledger,factory)
        self.budget=Budget(manifest);self.row=next(row['id'] for row in manifest['branches'] if row['nonquery']>=2)
        self.budget.begin(self.row);self.states={'PF':self.new_state('PF')};self.channels={};self.admissions={};self.data_counts={};self.cells={};self.stopping=False;self.calls=0
        self.flow=Flow(self,self.row)
    def new_state(self,task):
        return dict(schema=3,batch=self.root.name,task=task,domain='PF' if task=='PF' else 'source',seq=0,usage={},commands={},objects={},versions={},ops={},q={},recovered=False,sourceDone=True)
    def save(self,task):self.store.save(task,copy.deepcopy(self.states[task]))
    def event(self,event,query=False):self.store.event(self.row,event,query)
    def downstream(self):self.calls+=1;return {'logicalEffect':'INVOKED'}
    def invoke(self,index):return self.flow.transaction('metadata/n'+str(index),'N',dict(n=1),self.downstream,'probe')


def run_checks(root,manifest):
    """Create a fresh independent root and return evidence; caller saves its report.

    All metadata bytes created here, including incomplete slots, stay under 128KiB.
    No module import or invocation starts helpers or accesses a media fixture.
    """
    root=Path(root).resolve();root.mkdir(parents=True,exist_ok=False);results=[];assertions=0
    def check(ok,reason):
        nonlocal assertions
        need(ok,'T05_ASSERT:'+reason);assertions+=1
    def stopped(action):
        try:action()
        except Stop as error:return str(error)
        raise AssertionError('T05 expected a stopped metadata commit')
    def make(name,factory=None):
        directory=root/name;directory.mkdir();return Store(directory,Ledger(),factory)
    state=dict(schema=2,batch=root.name,task='T01',usage={},commands={},q={},objects={})

    store=make('full-snapshot');store.save('T01',state)
    check(store.requested==store.written==8192 and store.seq['T01']==1 and store.transactions==1,'full-slot-commits-after-exact-return')
    check(store.native['write']==1 and not store.ledger.live,'one-slot-write-and-closed-resource')
    results.append(dict(case='full-snapshot',requested=store.requested,actualWritten=store.written,transactions=store.transactions))

    # Invalid returns include bool (a Python int subclass) and a count above the
    # request. Such values never become fabricated actual-written byte facts.
    for name,value in [('zero',0),('short',7),('last-byte-missing',8191),('none',None),('negative',-1),('too-large',8193),('string','7'),('bool',True),('raised','RAISE_SELF_OWNED')]:
        factory=_WriterFactory(lambda p:p.suffix=='.slot',value);store=make('snapshot-'+name,factory)
        error=stopped(lambda:store.save('T01',state));written=value if type(value) is int and 0<=value<=8192 else 0
        check(store.requested==8192 and store.written==written,'slot-credit-vs-actual-'+name)
        check(store.transactions==0 and not store.seq and store.commit_status=='UNKNOWN','slot-not-committed-'+name)
        check(factory.fault_calls==factory.write_calls==1 and store.native['sync']==0,'no-repair-or-sync-'+name)
        check(not store.ledger.live and all(f.closed for f in factory.opened),'failed-slot-close-proven-'+name)
        before=store.requested;stopped(lambda:store.save('T01',state))
        check(store.requested==before and factory.write_calls==1,'poison-prevents-later-write-'+name)
        results.append(dict(case='snapshot-'+name,error=error,requested=store.requested,actualWritten=store.written,unknownRequestedBytes=store.unknown_requested_bytes,transactions=store.transactions,writeCalls=factory.write_calls))

    for query in (False,True):
        factory=_WriterFactory(lambda p:p.suffix==('.q' if query else '.ops'),None if query else 3);store=make('query-event' if query else 'row-event',factory)
        payload=dict(id='test/event',phase='ADMITTED');error=stopped(lambda:store.event('P01',payload,query))
        check(store.requested==len(compact(payload))+1 and store.written==(0 if query else 3),'event-actual-count-query-'+str(query))
        check(store.commit_status=='UNKNOWN' and store.native['sync']==0 and factory.write_calls==1,'event-no-false-durability-query-'+str(query))
        check(not store.ledger.live,'event-closes-self-owned-file-'+str(query))
        results.append(dict(case='query-event' if query else 'row-event',error=error,requested=store.requested,actualWritten=store.written,unknownRequestedBytes=store.unknown_requested_bytes))

    factory=_WriterFactory(lambda p:p.name=='global.log',2);store=make('global-setup',factory)
    error=stopped(lambda:store.open_log(b'HEADER\n'))
    check(store.written==2 and store.requested==7 and store.log is None,'setup-short-is-not-open-log-completion')
    check(not store.ledger.live and factory.write_calls==1,'setup-short-closes-no-repair')
    results.append(dict(case='global-setup',error=error,requested=store.requested,actualWritten=store.written,completed=False))

    factory=_WriterFactory(lambda p:p.name=='global.log',2,at=2);store=make('global-event',factory);log=store.open_log(b'HEADER\n')
    error=stopped(lambda:store.event('P01',dict(id='global/event')))
    check(store.written==9 and store.requested>9 and not store.event_bytes,'global-event-short-not-committed')
    check(factory.write_calls==2 and factory.fault_calls==1,'global-setup-and-event-each-one-write')
    # Cleanup is a real close on the one self-owned file, without attempting any
    # write or claiming that the failed global event became durable.
    store._close_file(log,'global-log');store.log=None
    check(not store.ledger.live,'failed-global-event-resource-closed')
    results.append(dict(case='global-event',error=error,requested=store.requested,actualWritten=store.written,completed=False))

    factory=_WriterFactory(lambda p:p.name=='result-before-close.json',None);store=make('final-receipt',factory)
    receipt=b'{"status":"READY_TO_CLOSE"}';error=stopped(lambda:store.write_receipt(receipt))
    check(store.requested==len(receipt) and store.written==0 and store.unknown_requested_bytes==len(receipt),'receipt-none-retains-request-credit')
    check(factory.write_calls==1 and store.native['sync']==0 and not store.ledger.live,'receipt-no-completion-or-repair')
    results.append(dict(case='final-receipt',error=error,requested=store.requested,actualWritten=store.written,completed=False))

    factory=_WriterFactory(lambda p:True,0,fail_construct=True);store=make('wrapper-open-failure',factory)
    stopped(lambda:store.save('T01',state))
    check(store.native['open']==store.native['close']==1 and not store.ledger.live,'wrapper-failure-closes-original-open-file')
    check(all(file.closed for file in factory.opened) and store.requested==0,'wrapper-failure-does-not-invent-write')
    results.append(dict(case='wrapper-construction-failure',opened=store.native['open'],closed=store.native['close'],remainingResources=len(store.ledger.live)))

    for stage,suffix in [('snapshot','.slot'),('admission-event','.ops')]:
        directory=root/('flow-'+stage);directory.mkdir();factory=_WriterFactory(lambda p,suffix=suffix:p.suffix==suffix,3)
        probe=_AdmissionProbe(directory,manifest,factory);error=stopped(lambda:probe.invoke(1))
        command=probe.states[probe.flow.task]['commands']['metadata/n1']
        check(probe.calls==0 and command['status']=='ADMITTED','real-flow-stops-before-action-'+stage)
        check(not probe.admissions['metadata/n1']['saved'],'failed-admission-never-authorizes-rpc-'+stage)
        writes=factory.write_calls;stopped(lambda:probe.invoke(2))
        check(probe.calls==0 and factory.write_calls==writes,'subsequent-action-stays-stopped-'+stage)
        results.append(dict(case='real-flow-'+stage,error=error,downstreamActionInvocations=probe.calls,nativeStarted=False,rpcStarted=False,scope='LOGICAL_ADMISSION_ORDERING_ONLY',completion=command['status'],writeCalls=factory.write_calls))

    actual_bytes=sum(path.stat().st_size for path in root.rglob('*') if path.is_file())
    check(actual_bytes<=131072,'independent-metadata-byte-bound')
    return dict(scope='T05_SELF_OWNED_WRITER_AND_REAL_FLOW_LOGICAL_CHECKS',status='PASS',assertions=assertions,cases=results,metadataBytes=actual_bytes,helpersStarted=False,nativeBridgeStarted=False,mediaRead=False,realDiskFault=False)
