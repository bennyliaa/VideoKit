"""A01: real G Native metadata calls through the active Q09-ALIAS grant Flow.

Only explicitly supplied, newly created selfcheck files are used. The small
Engine double omits helpers, worker startup and observer sampling; Flow, Ops,
Store, Namespaces and G Native open/query/close are the production code.
"""
from __future__ import annotations
import copy
from pathlib import Path
import threading
from gcore import BASE, Budget, Ledger, Native, Refused, Stop, Store, need
from gengine import Engine, Flow, Ops
from namespaces import Namespaces, lexical_absolute


_PENDING_PROBES=[]  # Preserve ownership if an unexpected actual close is UNKNOWN.


class _KernelTrace:
    """Delegates to the original Win32 functions; fault modes are test-only.

    The close-unknown mode hides an observed successful close from Native. Its
    actual return is retained for later test cleanup, never used by grant.
    """
    def __init__(self,kernel,mode):
        self.kernel=kernel;self.mode=mode;self.current='';self.opens=[]
        self.query_calls=0;self.actual_queries=0;self.injected_query_failures=0
        self.closes=[];self.byte_delegates=0
    def CreateFileW(self,path,access,share,security,creation,flags,template):
        self.opens.append(dict(key=self.current,path=str(path),access=access,share=share,creation=creation,flags=flags))
        return self.kernel.CreateFileW(path,access,share,security,creation,flags,template)
    def GetFileInformationByHandle(self,handle,info):
        self.query_calls+=1
        if self.current.endswith('-alias') and self.mode=='query-failure':
            self.injected_query_failures+=1;return 0
        self.actual_queries+=1;return self.kernel.GetFileInformationByHandle(handle,info)
    def CloseHandle(self,handle):
        returned=self.kernel.CloseHandle(handle)
        hidden=self.current.endswith('-alias') and self.mode=='close-unknown' and bool(returned)
        self.closes.append(dict(key=self.current,actualReturned=bool(returned),reportedReturned=False if hidden else bool(returned),injectedUnknown=hidden))
        return 0 if hidden else returned
    def ReadFile(self,*args):
        self.byte_delegates+=1;raise AssertionError('A01_UNEXPECTED_BYTE_READ')
    def WriteFile(self,*args):
        self.byte_delegates+=1;raise AssertionError('A01_UNEXPECTED_BYTE_WRITE')


class _ObservedNative(Native):
    def __init__(self,ledger,mode):
        super().__init__(ledger);self.trace=_KernelTrace(self.k,mode);self.k=self.trace;self.mode=mode
    def open(self,rid,path,row):
        self.trace.current=rid
        try:proof=super().open(rid,path,row)
        finally:self.trace.current=''
        if rid.endswith('-alias') and self.mode=='identity-mismatch' and proof.get('identityStatus')=='OPENED_HANDLE_PROVEN':
            fields=proof['identity'].split(':');fields[0]=str((int(fields[0])+1)%4294967296)
            proof=dict(proof,identity=':'.join(fields))
        return proof
    def close(self,rid):
        self.trace.current=rid
        try:return super().close(rid)
        finally:self.trace.current=''


class _GrantProbe:
    new_state=Engine.new_state
    add_object=Engine.add_object
    def __init__(self,root,paths,manifest,mode):
        self.root=root;self.manifest=manifest;self.lock=threading.RLock();self.ledger=Ledger()
        self.store=Store(root,self.ledger);self.native=_ObservedNative(self.ledger,mode)
        self.namespace=Namespaces(root,paths,mode='SYNTHETIC');self.channels={};self.cells={}
        self.admissions={};self.data_counts={};self.stopping=False;self.rpc_calls=0
        self.states={'PF':self.new_state('PF')};self.row='Q09-ALIAS';self.budget=Budget(manifest)
    def prepare(self):
        # Setup is separately counted metadata work, not another frozen control.
        key='PF-v1-guard';proof=self.native.open(key,self.namespace.input_path('C'),self.budget.rows[self.row])
        self.states['PF']['objects'][key]=dict(proof,key=key,actor='G',role='guard',version='v1',consumer='')
        try:self.namespace.bind_input('C',proof)
        finally:self.states['PF']['objects'][key].update(self.native.close(key))
        self.budget.begin(self.row);self.flow=Flow(self,self.row)
    def save(self,task):self.store.save(task,copy.deepcopy(self.states[task]))
    def event(self,event,query=False):self.store.event(self.row,event,query)
    def remote(self,*args,**kwargs):
        self.rpc_calls+=1;raise AssertionError('A01_UNEXPECTED_HELPER_RPC')
    def retire(self):
        retired=[]
        for key in list(self.native.owned):
            if key in self.native.close_unknown:
                # Only this explicit hidden-return fixture has independent proof
                # of actual closure. An actual OS failure remains pending.
                witnessed=any(p['key']==key and p['actualReturned'] and p['injectedUnknown'] for p in self.native.trace.closes)
                if not witnessed:
                    _PENDING_PROBES.append(self);raise Stop('A01_ACTUAL_CLOSE_UNKNOWN_OWNERSHIP_RETAINED')
                del self.native.owned[key];self.ledger.release(key,'NATIVE_CLOSE_RETURNED')
                retired.append(dict(key=key,proof='TEST_RETAINED_ACTUAL_CLOSE_RETURN',newCloseCalls=0))
            else:self.native.close(key)
        return retired


def test(root,manifest):
    """Create <=4KiB fixtures and <=128KiB metadata; never start a helper.

    Failure injection is confined to metadata return values on these original
    test handles. It is not evidence of a real OS query/close failure.
    """
    root=lexical_absolute(root);need(root.is_relative_to((BASE/'selfcheck').absolute()),'A01_SELF_CREATED_ROOT_ONLY')
    root.mkdir(parents=True,exist_ok=False);source=root/'inputs';outputs=root/'outputs';source.mkdir();outputs.mkdir()
    paths={name:source/(name+'.bin') for name in ('L','C','Z')};fixture_bytes=0
    for name,data in (('L',b'L'),('C',b'E2B A01 self-owned C, not media\n'),('Z',b'')):
        with open(paths[name],'xb',buffering=0) as file:need(file.write(data)==len(data),'A01_FIXTURE_EXACT_WRITE')
        fixture_bytes+=len(data)
    before={name:(path.stat().st_size,path.stat().st_mtime_ns) for name,path in paths.items()}
    checks=[];cases=[];metadata_requested=0;metadata_written=0;metadata_transactions=0
    def check(ok,label):need(ok,'A01_ASSERT:'+label);checks.append(label)
    for mode,expected in (('normal','INPUT_ALIAS'),('query-failure','BLOCKED_VERSION_NOT_PROVEN'),('identity-mismatch','SOURCE_VERSION_IDENTITY_CHANGED'),('close-unknown','GUARD_CLOSE_UNKNOWN_NO_RETRY')):
        output=outputs/mode;output.mkdir();probe=None
        try:
            probe=_GrantProbe(output,paths,manifest,mode)
            probe.prepare()
            try:Ops(probe).grant(alias=True)
            except (Refused,Stop) as error:reason=str(error)
            else:raise AssertionError('A01_EXPECTED_GRANT_REFUSAL:'+mode)
            record=probe.states[probe.flow.task]['objects'][probe.flow.task+'-alias'];trace=probe.native.trace
            check(reason==expected,'exact-grant-rejection-'+mode)
            check(len(trace.opens)==2 and all(p['path']==str(paths['C']) for p in trace.opens),'original-and-alias-open-exact-input-C-'+mode)
            check(all((p['access'],p['share'],p['creation'],p['flags'])==(0x80000000,1,3,0x80) for p in trace.opens),'approved-readonly-open-existing-share-read-'+mode)
            check(bool(record['object']) and bool(record['ticket']) and record['owner']=='G' and record['attempts']==1,'allocated-original-object-ticket-retained-'+mode)
            check(probe.flow.ni==1 and probe.budget.globalused['n']==1 and probe.rpc_calls==0 and probe.admissions['Q09-ALIAS/n01']['calls']==0,'one-original-control-zero-rpc-'+mode)
            check(trace.byte_delegates==0 and all(probe.budget.globalused[k]==0 for k in ('ib','ic','v','targets','credit')) and not (output/'C.bin').exists() and not list(output.glob('*.out')),'no-byte-delegate-copy-or-output-target-'+mode)
            check(probe.store.transactions<=2 and probe.store.requested==probe.store.written and probe.store.commit_status=='HEALTHY','original-two-phase-metadata-bound-'+mode)
            if mode=='close-unknown':
                check(record['disposition']=='UNKNOWN' and record['nativeCloses']==0 and record['key'] in probe.native.owned and record['key'] in probe.native.close_unknown and record['key'] in probe.ledger.live,'unknown-retains-original-ownership-and-credit')
                check(probe.states[probe.flow.task]['commands']['Q09-ALIAS/n01']['status']=='UNKNOWN' and probe.stopping,'unknown-stops-active-flow')
            else:
                check(record['disposition']=='CLOSED_PROVEN' and record['nativeCloses']==1 and not probe.native.owned and not probe.ledger.live,'one-actual-close-after-refusal-'+mode)
                check(probe.states[probe.flow.task]['commands']['Q09-ALIAS/n01']['error']==expected,'active-flow-persists-refusal-'+mode)
            check(trace.query_calls==2 and trace.actual_queries==(1 if mode=='query-failure' else 2),'bounded-original-handle-query-'+mode)
            stopped_record=copy.deepcopy(record);retired=probe.retire()
            check(len(trace.closes)==2 and all(p['actualReturned'] for p in trace.closes) and not probe.native.owned and not probe.ledger.live,'all-original-test-handles-actually-closed-once-'+mode)
            metadata_requested+=probe.store.requested;metadata_written+=probe.store.written;metadata_transactions+=probe.store.transactions
            cases.append(dict(case=mode,scope='ACTUAL_G_NATIVE_SELF_OWNED_Q09_ALIAS_FLOW',reason=reason,controls=probe.flow.ni,rpc=probe.rpc_calls,mediaBytesRead=0,fileByteDelegates=0,
                              opens=trace.opens,queryAttempts=trace.query_calls,actualQueryCalls=trace.actual_queries,injectedQueryFailures=trace.injected_query_failures,closes=trace.closes,
                              stoppedObject=stopped_record,controlledCleanup=retired,metadataRequested=probe.store.requested,metadataWritten=probe.store.written,metadataTransactions=probe.store.transactions,remainingResources=len(probe.ledger.live)))
        finally:
            if probe is not None:probe.retire()
    after={name:(path.stat().st_size,path.stat().st_mtime_ns) for name,path in paths.items()}
    check(before==after,'fixture-input-length-and-mtime-unchanged')
    metadata_bytes=sum(path.stat().st_size for path in outputs.rglob('*') if path.is_file())
    check(fixture_bytes<=4096 and metadata_bytes<=131072,'independent-fixture-and-metadata-byte-bounds')
    return dict(scope='E2B_A01_REAL_G_NATIVE_ALIAS_GRANT_SELF_OWNED_CHECKS',status='PASS',assertions=len(checks),checks=checks,cases=cases,
                fixtureBytes=fixture_bytes,metadataBytes=metadata_bytes,metadataRequested=metadata_requested,metadataWritten=metadata_written,metadataTransactions=metadata_transactions,
                helpersStarted=False,newHelpers=0,mediaRead=False,mediaBytesRead=0,realPFRun=False,real61Run=False,
                limitations=['Minimal Engine double omits helper/worker/observer startup; production Flow.grant, Store, Namespaces and G Native calls remain active.',
                             'Original C proof setup is separately counted open/query/close, not an added frozen control.',
                             'Query failure, identity mismatch and hidden successful close return are explicit self-owned injections, not actual OS fault evidence.',
                             'Close UNKNOWN is asserted with ownership/credit retained before test-only retirement from independently retained actual close return; no second close occurs.',
                             'No hardlink, reparse replacement, hostile race, media current-version or real execution admission is proved.'])


def run_checks(root,manifest):return test(root,manifest)
