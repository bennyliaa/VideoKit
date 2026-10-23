"""Inactive future owned-driver adapter. No Popen, hook or OS API on import.

This is candidate-free and cannot consume any prior LIVE/offline authority.
Only a later coordinator-approved exact source package/order may call launch.
"""
from pathlib import Path
import sys,os,time,threading,subprocess,json,ntpath,hashlib
from capture_policy import validate_plan,audit_decision,encoded,digest,decode,same,disposition,FACT_KEYS,Denied
from native_identity import from_original_handle
CUSTODY=[]
SOURCE_CUSTODY=[]
_ACTIVATION_TOKEN=object()
SOURCE_FILES={'capture_policy.py','profiles.py','evidence_io.py','stop_channel.py','future_capture.py','native_identity.py','owned_child.py','owned_child.ps1','runtime-pins.json','runtime-and-reuse-provenance.json','budget-proposal.json','INACTIVE_AUTHORITY_TEMPLATE.json','pure_review.py'}
def new_facts():
    f={k:False for k in FACT_KEYS};f['phase']='PREFLIGHT';return f
class AuditRejected(Denied):pass
class Activation:
    def __init__(self,token,authority,plans):
        if token is not _ACTIVATION_TOKEN:raise Denied('SOURCE_VERIFIED_FACTORY_REQUIRED')
        self.authority=authority;self.plans=plans;self.owner=(os.getpid(),threading.get_ident());self.start=time.monotonic();self.launches=0;self.hook_installed=False;self.used_profiles=set();self.guard=None
    def require(self):
        from datetime import datetime,timezone
        now=datetime.now(timezone.utc);expires=datetime.fromisoformat(self.authority['expiresUtc'])
        if self.owner!=(os.getpid(),threading.get_ident()) or time.monotonic()-self.start>=120 or (expires-now).total_seconds()<30:raise Denied('SAME_OWNER_SCOPE_EXPIRED_OR_INSUFFICIENT_BODY_WINDOW')
def activate_future(authority_path,external_authority_sha,package_manifest_path,external_package_sha,bindings_path,external_bindings_sha):
    """File-only admission first. Never called by this static preparation."""
    reads=[]
    def read(p,cap=16777216):
        p=Path(p)
        for q in [p,*p.parents]:
            if q.exists() and q.stat().st_file_attributes&1024:raise Denied('NO_REPARSE')
        record={'path':str(p),'closeEntered':False,'closeReturned':False};SOURCE_CUSTODY.append(record);f=None
        try:
            f=p.open('rb');record['file']=f;v=f.read(cap+1)
        finally:
            if f is not None:
                record['closeEntered']=True;f.close();record['closeReturned']=True
            if f is None or record['closeReturned']:SOURCE_CUSTODY.remove(record)
        if len(v)>cap:raise Denied('SOURCE_FILE_BOUND')
        reads.append(len(v))
        if len(reads)>4096 or sum(reads)>1073741824:raise Denied('SOURCE_TOTAL_BOUND')
        return v
    ab=read(authority_path,8192);a=decode(ab);mb=read(package_manifest_path);bb=read(bindings_path,32768)
    if digest(mb)!=external_package_sha or digest(bb)!=external_bindings_sha:raise Denied('EXTERNAL_SOURCE_AND_BINDINGS_HASH')
    verify_future_authority(a,ab,external_authority_sha,external_package_sha,external_bindings_sha)
    base=Path(__file__).resolve().parent;m=decode(mb)
    if type(m) is not dict or set(m)!={'schema','files'} or m['schema']!='DRIVER_CAPTURE_FIX01_SOURCE_MANIFEST_V1' or type(m['files']) is not list or len(m['files'])!=len(SOURCE_FILES) or {x.get('path') for x in m['files']}!=SOURCE_FILES:raise Denied('PACKAGE_MANIFEST')
    for row in m['files']:
        if type(row) is not dict or set(row)!={'path','bytes','sha256'} or type(row['bytes']) is not int:raise Denied('SOURCE_ROW_SCHEMA')
        p=(base/row['path']).resolve()
        if not p.is_relative_to(base) or len(read(p))!=row['bytes'] or digest(read(p))!=row['sha256']:raise Denied('SOURCE_PIN')
    from profiles import proposals
    plans=proposals(a['workRoot'])
    if not same(decode(bb),plans):raise Denied('ACTUAL_SERIALIZED_BINDINGS')
    root=Path(a['workRoot'])
    for q in [root,*root.parents]:
        if q.exists() and q.stat().st_file_attributes&1024:raise Denied('WORK_ROOT_REPARSE')
    if root.exists():raise Denied('FRESH_VALIDATION_ROOT')
    # Interpreter and PS/runtime provenance is pinned by the original immutable
    # runtime identity record, not a mutable PATH search or basename check.
    pins=base/'runtime-pins.json';runtime=decode(read(pins))
    if list(sys.version_info[:3])!=runtime['version'] or Path(sys.executable).resolve()!=Path(runtime['executable']).resolve():raise Denied('BUNDLED_INTERPRETER_REQUIRED')
    for row in runtime['files']:
        v=read(row['path'])
        if len(v)!=row['bytes'] or digest(v)!=row['sha256']:raise Denied('EXACT_RUNTIME_PIN')
    provenance=decode(read(base/'runtime-and-reuse-provenance.json'));stdlib=provenance['exactRuntimeSubprocess']
    if digest(read(stdlib['path']))!=stdlib['sha256']:raise Denied('EXACT_WINDOWS_STDLIB_AUDIT_ORDER')
    verify_future_authority(a,ab,external_authority_sha,external_package_sha,external_bindings_sha)
    Path(a['workRoot']).mkdir(parents=True,exist_ok=False)
    return Activation(_ACTIVATION_TOKEN,a,plans)
class ScopedAudit:
    def __init__(self,journal):
        self.journal=journal;self.owner=(os.getpid(),threading.get_ident());self.plan=None;self.binding=None;self.used=False;self.last=None;self.events=0
    def arm(self,plan,binding):
        if self.plan is not None:raise Denied('ONE_ORIGINAL_CONSTRUCTOR_AT_A_TIME')
        self.plan=plan;self.binding=binding;self.used=False;self.last=None
    def disarm(self):self.plan=self.binding=None
    def __call__(self,event,args):
        if event!='subprocess.Popen':return
        self.events+=1
        if self.events>16:raise AuditRejected('AUDIT_EVENT_BUDGET')
        row=audit_decision(event,args,self.plan,self.binding,active=self.plan is not None,same_owner=self.owner==(os.getpid(),threading.get_ident()),event_unused=not self.used)
        self.used=True;self.last=row
        # The actual event payload is archived before permitting CreateProcess.
        # Unsupported/oversized values explicitly say rawPayloadComplete=false.
        self.journal.write('audit-event',row)
        if not row['allowed']:raise AuditRejected(row['reason'])
def verify_future_authority(a,raw,external_hash,package_hash,bindings_hash):
    from datetime import datetime,timezone
    import uuid
    keys=set('schema stage mode approvedForExecution sourceThreadId sourceTurnId packageSha256 bindingsSha256 notBeforeUtc expiresUtc workRoot batch controlNonce'.split())
    if type(a) is not dict or set(a)!=keys or digest(raw)!=external_hash:raise Denied('FUTURE_AUTHORITY_SCHEMA_OR_HASH')
    if a['schema']!='OWNED_DRIVER_VALIDATION_AUTH_V1' or a['stage']!='OWNED_DRIVER_ONLY' or a['mode']!='NO_CANDIDATE_NO_TCP' or a['approvedForExecution'] is not True:raise Denied('NO_DYNAMIC_AUTHORITY')
    if a['sourceThreadId']!='01a107c3-2bf9-7fa0-94a0-234258ca6774' or str(uuid.UUID(a['sourceTurnId']))!=a['sourceTurnId'] or a['sourceTurnId']=='01a16706-8919-7311-b071-ac157eb7ce65':raise Denied('FUTURE_DISPATCH_REQUIRED')
    if a['packageSha256']!=package_hash or a['bindingsSha256']!=bindings_hash:raise Denied('EXACT_FROZEN_BINDING')
    begin=datetime.fromisoformat(a['notBeforeUtc']);end=datetime.fromisoformat(a['expiresUtc']);now=datetime.now(timezone.utc)
    if begin.tzinfo is None or end.tzinfo is None or not begin<=now<end or not 180<=(end-now).total_seconds() or not 0<(end-begin).total_seconds()<=900:raise Denied('NARROW_FUTURE_UTC_WINDOW')
    root=Path(a['workRoot']).resolve();allowed=Path('D:/CodexProjects/VideoKit/docs/tester/D1_DRIVER_CAPTURE_FIX01_VALIDATION')
    if str(root)!=a['workRoot'] or root.parent!=allowed or str(uuid.UUID(a['batch']))!=a['batch'] or root.name!=a['batch']:raise Denied('FUTURE_FRESH_ROOT')
    if type(a['controlNonce']) is not str or str(uuid.UUID(a['controlNonce']))!=a['controlNonce']:raise Denied('CONTROL_NONCE')
    return True
def install_scoped_audit(activation,journal):
    if type(activation) is not Activation:raise Denied('ACTIVE_SOURCE_BINDING_REQUIRED')
    activation.require()
    if activation.hook_installed:raise Denied('AUDIT_INSTALL_ONCE')
    guard=ScopedAudit(journal);sys.addaudithook(guard);activation.hook_installed=True;activation.guard=guard;return guard
class Capture:
    def __init__(self,plan,binding,journal,control,audit):
        self.plan=plan;self.binding=binding;self.journal=journal;self.control=control;self.audit=audit;self.owner=(os.getpid(),threading.get_ident());self.facts=new_facts();self.original=None;self.held=[];self.readers=[];self.counts=[0,0];self.buffers=[bytearray(),bytearray()];self.failure=None;self.closed_entered=False;self.start=None;self.returned=False;self.pipe_amount_unknown=False;self.waiter=None;self.wait_fact={'entered':False,'returned':False,'error':None};CUSTODY.append(self)
    def launch(self,validated_activation):
        # Activation is supplied by the future caller only after full source/
        # order checks. There is intentionally no active CLI entry in this pack.
        try:
            if type(validated_activation) is not Activation:raise Denied('INACTIVE_UNTIL_LATER_DISPATCH')
            validated_activation.require()
            if validated_activation.launches>=3 or not same(self.binding,validated_activation.plans[validated_activation.launches]) or self.binding.get('profile') in validated_activation.used_profiles or not validated_activation.hook_installed or self.audit is not validated_activation.guard:raise Denied('FIXED_THREE_PROFILES_ONLY_IN_ORDER')
            if Path(self.journal.root).resolve()!=Path(validated_activation.authority['workRoot']).resolve() or self.control.path.parent.resolve()!=Path(self.journal.root).resolve():raise Denied('EXACT_OWN_EVIDENCE_SCOPE')
            if self.control.poll():raise Denied('STOP_BEFORE_ANY_CONSTRUCTOR')
            validate_plan(self.plan,self.binding)
            self.journal.write('launch-intent',self.plan);self.audit.arm(self.plan,self.binding)
        except BaseException as e:
            self.held.extend([e,e.__traceback__]);self.facts.update(preflightRejected=True,otherEvidenceReturned=self.journal.returned() and self.control.returned());self.failure=type(e).__name__;return self
        validated_activation.launches+=1;validated_activation.used_profiles.add(self.plan['profile']);self.start=time.monotonic()
        self.facts['phase']='CONSTRUCTOR_ENTERED'
        try:
            # Explicit executable is the essential correction. It is also
            # checked in the actual serialized Windows audit event.
            p=subprocess.Popen(list(self.plan['argv']),executable=self.plan['executable'],cwd=self.plan['cwd'],env=dict(self.plan['env']),shell=False,close_fds=True,stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            self.original=p;self.held.append(p);self.facts.update(phase='CREATED_ORIGINAL',popenObjectReturned=True,constructorTempsReturned=True,auditObserved=self.audit.last is not None)
            self.readers=[threading.Thread(target=self._drain,args=(i,s)) for i,s in enumerate((p.stdout,p.stderr))];self.held.extend(self.readers)
            for t in self.readers:t.start()
            self.waiter=threading.Thread(target=self._wait_original);self.held.append(self.waiter);self.waiter.start()
            self.journal.write('original-object-created',{'pid':p.pid,'identityBinding':'PENDING','argv':self.plan['argv'],'source':'ORIGINAL_POPEN_OBJECT_NOT_PID_LOOKUP'})
            self.identity=from_original_handle(p._handle,self.plan['argv']);self.facts['identityBound']=self.identity['pid']==p.pid and type(self.identity['creationFileTime']) is int and self.identity['creationFileTime']>0 and ntpath.normcase(ntpath.normpath(self.identity['image']))==ntpath.normcase(ntpath.normpath(self.plan['executable']))
            if not self.facts['identityBound']:raise Denied('ORIGINAL_IMAGE_OR_CREATION_BINDING')
            self.journal.write('original-handle-identity',self.identity)
        except BaseException as e:
            self.held.extend([e,e.__traceback__]);self.failure=type(e).__name__
            try:self.control.request('CONSTRUCTOR_OR_IDENTITY_FAILURE')
            except BaseException as ce:self.held.extend([ce,ce.__traceback__])
            if self.original is None and self.audit.last and not self.audit.last['allowed']:
                self.facts.update(phase='AUDIT_REJECTED_PRE_CREATEPROCESS',auditObserved=True,auditRejectedBeforeCreate=True)
            # No unconditional endless hold here. The shared failure exit first
            # collects all actually returned original objects, then classifies.
        finally:self.audit.disarm()
        return self
    def _drain(self,i,s):
        try:
            while True:
                b=s.read(4096)
                if not b:break
                self.counts[i]+=len(b)
                if sum(self.counts)<=262144:self.buffers[i].extend(b)
                else:self.failure='PIPE_BOUND';self.control.request('PIPE_BOUND')
        except BaseException as e:
            self.failure='PIPE_RETURN_UNKNOWN';self.pipe_amount_unknown=True;self.held.extend([e,e.__traceback__])
            try:self.control.request(self.failure)
            except BaseException as ce:self.held.extend([ce,ce.__traceback__])
    def _wait_original(self):
        self.wait_fact['entered']=True
        try:self.wait_fact['exitCode']=self.original.wait();self.wait_fact['returned']=True
        except BaseException as e:self.wait_fact['error']=type(e).__name__;self.held.extend([e,e.__traceback__])
    def collect(self):
        if self.owner!=(os.getpid(),threading.get_ident()):return 'RETAIN_WRONG_ORIGINAL_HOLDER'
        if self.original is None:
            self.facts['otherEvidenceReturned']=self.journal.returned() and self.control.returned();answer=disposition(self.facts)
            if not answer.startswith('RETAIN') and self in CUSTODY:CUSTODY.remove(self)
            return answer
        if self.closed_entered and not self.returned:return 'RETAIN_ORIGINAL_CLOSE_ALREADY_ENTERED'
        p=self.original
        try:
            while not self.wait_fact['returned'] or any(t.is_alive() for t in self.readers) or (self.waiter is not None and self.waiter.is_alive()):
                if time.monotonic()-self.start>=30:self.failure=self.failure or 'OBSERVATION_EXPIRED';self.control.request('OBSERVATION_EXPIRED')
                self.control.poll()
                for t in self.readers:t.join(.02)
                if self.waiter is not None:self.waiter.join(.02)
                else:time.sleep(.02)
            self.waiter.join();code=self.wait_fact['exitCode'];self.exit_code=code;self.facts['originalWaitReturned']=True
            for t in self.readers:t.join()
            self.facts['readersJoined']=True
            if self.closed_entered:raise RuntimeError('ORIGINAL_CLOSE_ONCE')
            self.closed_entered=True;p.stdout.close();p.stderr.close();self.facts['streamsClosed']=True;p._handle.Close();self.facts['handleCloseReturned']=True
            self.returned=True
            self.journal.write('original-return',{'exitCode':code,'pipeCountsLowerBound':self.counts,'pipeAmountUnknown':self.pipe_amount_unknown,'pipeReservationIfUnknown':262144 if self.pipe_amount_unknown else None,'capturedCounts':[len(x) for x in self.buffers],'truncated':sum(self.counts)!=sum(map(len,self.buffers)),'originalWaitReturned':True,'readersJoined':True,'streamsClosed':True,'originalHandleCloseReturned':True})
            self.exit_code=code
            self.semantic_status='FAIL' if code!=0 or self.failure or self.pipe_amount_unknown or sum(self.counts)!=sum(map(len,self.buffers)) else 'PASS'
            for i,b in enumerate(self.buffers):
                # 8192 raw bytes per JSON record, hex encoding remains bounded.
                for offset in range(0,len(b),8192):self.journal.write('pipe-'+str(i),{'offset':offset,'hex':bytes(b[offset:offset+8192]).hex()})
        except BaseException as e:
            self.failure=self.failure or type(e).__name__;self.held.extend([e,e.__traceback__])
            try:self.control.request('ORIGINAL_RETURN_OR_ARCHIVE_FAILURE')
            except BaseException as ce:self.held.extend([ce,ce.__traceback__])
        self.facts['otherEvidenceReturned']=self.journal.returned() and self.control.returned()
        answer=disposition(self.facts)
        if not answer.startswith('RETAIN') and self in CUSTODY:CUSTODY.remove(self)
        return answer
def failure_exit(error,captures,control,journal):
    """Same original owner: known returned FAIL exits normally; UNKNOWN serves STOP."""
    control_error=None
    try:control.request('STOP_NEW_ADMISSION')
    except BaseException as ce:control_error=ce
    rows=[]
    originals=list(captures)
    for c in CUSTODY:
        if c not in originals:originals.append(c)
    for c in originals:
        answer=c.collect() if not c.returned else disposition(c.facts)
        rows.append({'disposition':answer,'facts':dict(c.facts),'failure':c.failure})
    unknown=bool(SOURCE_CUSTODY) or bool(CUSTODY) or any(r['disposition'].startswith('RETAIN') for r in rows) or not journal.returned() or not control.returned()
    try:journal.write('failure-exit',{'status':'PENDING_UNKNOWN' if unknown else 'FAIL_RETURNED','errorType':type(error).__name__,'captures':rows,'noRetryOrExternalClose':True})
    except BaseException:unknown=unknown or not journal.returned()
    if unknown:
        # Original refs remain in this holder. Polling itself is bounded; STOP
        # never means terminate, release foreign handles or acknowledge return.
        while True:control.poll();time.sleep(.1)
    return {'status':'FAIL_RETURNED','captures':rows}
class CaptureGuard:
    def __init__(self,captures,control,journal):self.captures=captures;self.control=control;self.journal=journal
    def __enter__(self):return self
    def __exit__(self,kind,error,tb):
        if kind is not None:failure_exit(error,self.captures,self.control,self.journal)
        elif CUSTODY or SOURCE_CUSTODY or not self.control.returned() or not self.journal.returned():failure_exit(RuntimeError('ORIGINALS_PENDING_AT_NORMAL_EXIT'),self.captures,self.control,self.journal)
        return False
