"""Inherited R diagnostic; its execution allowance is not part of E2C."""
import argparse,base64,copy,ctypes,hashlib,hmac,json,os,queue,secrets,subprocess,sys,threading,time
from concurrent.futures import ThreadPoolExecutor,TimeoutError as FutureTimeout
from pathlib import Path
BASE=Path(__file__).resolve().parents[1];sys.path.insert(0,str(BASE/'src'))
from gcore import Ledger,PWSH,compact,pack,unpack,need,sha,Stop
from runtime_metrics import Win32MetricReader
from diagnostic_gate import validate_diagnostic

STAGES=('MINIMAL_START','LOAD_COMPLETE','INIT_COMPLETE','HELLO_SERIALIZED')
METHODS=(('ADD_TYPE','AddType'),('LOAD_FROM','LoadFrom'))


def create_json(path,value):
    data=(json.dumps(value,indent=2,allow_nan=False)+'\n').encode('utf-8')
    with path.open('xb',buffering=0) as file:
        need(file.write(data)==len(data),'DIAGNOSTIC_METADATA_SHORT_WRITE');file.flush();os.fsync(file.fileno())
    return len(data)


class DiagnosticChild:
    """Two original bounded pipe readers. No replacement process or sampling loop."""
    def __init__(self,method,loader,root,owner,ledger):
        self.method=method;self.owner=owner;self.ledger=ledger;self.root=root;self.name='diagnostic/'+method
        self.queue=queue.Queue(maxsize=8);self.stdout_bytes=0;self.stderr_bytes=0;self.stdin_bytes=0;self.stderr=bytearray()
        self.key=os.urandom(32);self.sent=[];self.errors=[];self.threads=[];self.exit_proof=None
        self.transport_slots=[];self.process=None;self.process_handle_deferred=False;self.unknown_process_handle=None
        for suffix in ('in-parent','in-child','out-parent','out-child','err-parent','err-child','process'):
            key=self.name+'/'+suffix;ledger.acquire(key,self.name if suffix.endswith('child') else 'G','process' if suffix=='process' else 'pipe');self.transport_slots.append(key)
        env=os.environ.copy();env['E2C_KEY']=base64.b64encode(self.key).decode()
        env.pop('E2C_INPUT_BINDINGS',None);env['E2C_NAMESPACE_MODE']='SYNTHETIC'
        self.started=time.monotonic()
        self.process=subprocess.Popen([str(PWSH),'-NoProfile','-NonInteractive','-File',str(BASE/'tools/diagnostic-r.ps1'),'-FixtureRoot',str(root),'-Loader',loader,'-Owner',owner],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,env=env,creationflags=subprocess.CREATE_NO_WINDOW,bufsize=0)
        self.pid=self.process.pid
        def output():
            try:
                while True:
                    line=self.process.stdout.readline(8194)
                    if not line:break
                    self.stdout_bytes+=len(line);need(len(line)<=8193 and self.stdout_bytes<=32768,'DIAGNOSTIC_STDOUT_LIMIT')
                    self.queue.put(line.decode('utf-8').rstrip('\r\n'),timeout=1)
            except BaseException as error:self.errors.append('stdout:'+type(error).__name__)
        def error_output():
            try:
                while True:
                    chunk=self.process.stderr.read(256)
                    if not chunk:break
                    self.stderr_bytes+=len(chunk)
                    if len(self.stderr)<8192:self.stderr.extend(chunk[:8192-len(self.stderr)])
                    if self.stderr_bytes>8192 and 'DIAGNOSTIC_STDERR_LIMIT' not in self.errors:self.errors.append('DIAGNOSTIC_STDERR_LIMIT')
            except BaseException as error:self.errors.append('stderr:'+type(error).__name__)
        for suffix,target in (('stdout-reader',output),('stderr-reader',error_output)):
            key=self.name+'/'+suffix;ledger.acquire(key,'G','worker')
            thread=threading.Thread(target=target,name='E2C-'+method+'-'+suffix,daemon=False);self.threads.append((key,thread));thread.start()
    def line(self,left):
        need(left>0,'DIAGNOSTIC_STAGE_DEADLINE')
        end=time.monotonic()+left
        while time.monotonic()<end:
            if self.errors:raise Stop('DIAGNOSTIC_TRANSPORT_STOP:'+self.errors[0])
            try:return self.queue.get(timeout=min(.05,max(.001,end-time.monotonic())))
            except queue.Empty:continue
        raise Stop('DIAGNOSTIC_STAGE_OR_PIPE_PENDING')
    def send(self,line,kind):
        data=(line+'\n').encode();need(len(data)<=8193,'DIAGNOSTIC_SEND_LIMIT')
        n=self.process.stdin.write(data);need(n==len(data),'DIAGNOSTIC_PIPE_SHORT_WRITE');self.process.stdin.flush()
        self.stdin_bytes+=len(data);self.sent.append(kind)
    def rpc(self,verb):
        id='DIAG-'+self.method+'/'+verb
        body=pack([id,verb,'DIAG-'+self.method,'DIAG',1,'','N'])
        self.send(body+'\t'+hmac.new(self.key,body.encode(),hashlib.sha256).hexdigest(),verb)
        return id
    def response(self,id,left):
        fields=unpack(self.line(left));need(len(fields)==3 and fields[0]==id and fields[1]=='OK','DIAGNOSTIC_RESPONSE_BINDING')
        return json.loads(fields[2])
    def cleanup(self,identity,end,normal=False,borrow_pending=False):
        if self.process is None:return None
        if not normal and self.process.poll() is None:
            try:self.send('STOP','STOP')
            except BaseException as error:self.errors.append('stop:'+type(error).__name__)
            try:self.process.stdin.close()
            except BaseException as error:self.errors.append('stdin-stop:'+type(error).__name__)
        try:code=self.process.wait(timeout=max(.001,min(5,end-time.monotonic())))
        except subprocess.TimeoutExpired:return dict(exited=False,pid=self.pid,instance=self.owner,code=None)
        proof=dict(exited=True,pid=self.pid,instance=self.owner,code=code,creationTime100ns=identity.get('creationTime100ns') if identity else None)
        for suffix in ('in-child','out-child','err-child'):self.ledger.release(self.name+'/'+suffix,'OWNER_EXIT_PROVEN')
        for key,thread in self.threads:
            thread.join(max(0,min(.5,end-time.monotonic())))
            if not thread.is_alive():self.ledger.release(key,'THREAD_JOIN_PROVEN')
            else:self.errors.append('reader-join-pending:'+key)
        for suffix,stream in (('in',self.process.stdin),('out',self.process.stdout),('err',self.process.stderr)):
            try:stream.close();self.ledger.release(self.name+'/'+suffix+'-parent','NATIVE_CLOSE_RETURNED')
            except BaseException as error:self.errors.append('pipe-close:'+type(error).__name__)
        self.exit_proof=proof
        if borrow_pending:self.process_handle_deferred=True
        else:self.close_process_handle()
        return proof
    def close_process_handle(self):
        if self.unknown_process_handle is not None:return
        need(self.exit_proof and self.exit_proof['exited'],'DIAGNOSTIC_PROCESS_STILL_LIVE')
        handle=int(self.process._handle)
        k=ctypes.WinDLL('kernel32',use_last_error=True);k.CloseHandle.argtypes=[ctypes.c_void_p];k.CloseHandle.restype=ctypes.c_int
        if k.CloseHandle(handle):self.process._handle.Detach();self.ledger.release(self.name+'/process','NATIVE_CLOSE_RETURNED');self.process_handle_deferred=False
        else:
            # Keep raw private ownership and credit, while preventing the
            # subprocess.Handle finalizer from issuing an unapproved retry.
            self.unknown_process_handle=handle;self.process._handle.Detach();self.errors.append('process-handle-close-unknown')


def run():
    print(json.dumps(dict(scope='E2C_INHERITED_R_DIAGNOSTIC_BLOCKED',status='NOT_RUN_E2C_R_DIAGNOSTIC_NOT_AUTHORIZED',
                          reason='The fixed E2B two-R diagnostic is historical evidence only; E2C permits one G lifecycle diagnostic.',
                          processInstances=0,metricSamples=0,helpersStarted=0,mediaBytesRead=0,fixtureBytesCreated=0,noInFlight=True,realExecutionAllowed=False)))
    return 2
    # Historical implementation retained below; no reservation, fixture, native
    # reader, pool or process is reached by this E2C --run entry.
    need(not (BASE/'evidence/freeze-summary.json').exists(),'FROZEN_PACKAGE_READ_ONLY')
    reservation=BASE/'evidence/diagnostic-reservation.json'
    stamp=str(time.time_ns());started=time.monotonic();end=started+90;utc_started=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())
    plan=dict(scope='E2C_FIXED_DIAGNOSTIC_RESERVATION',runId=stamp,methods=[name for name,_ in METHODS],stageOrder=list(STAGES),maximumProcesses=2,maximumMetricSamples=8,createdBeforeFirstProcess=True,realMediaAllowed=False)
    create_json(reservation,plan)
    root=BASE/'selfcheck'/('r-diagnostic-'+stamp);root.mkdir(parents=True,exist_ok=False)
    for part in [root,*root.parents]:need(not part.is_symlink() and not part.is_junction(),'DIAGNOSTIC_REPARSE_ROOT_DENIED')
    ledger=Ledger();worker_credit='diagnostic/native-worker';ledger.acquire(worker_credit,'G','worker')
    pool=ThreadPoolExecutor(max_workers=1,thread_name_prefix='E2C-diagnostic-native');futures=[];instances=[];children=[];unknowns=[]
    reader=Win32MetricReader(ledger)
    dll=BASE/'artifacts/E2C.dll';assembly_sha=sha(dll.read_bytes())
    total_samples=0;identity_queries=0;stage_acks=0;rpc_requests=0;processes=0
    def invoke(fn,timeout):
        future=pool.submit(fn);futures.append(future)
        try:return future.result(timeout=max(.001,timeout))
        except FutureTimeout:raise Stop('DIAGNOSTIC_NATIVE_PENDING_NO_RETRY')
    for method,loader in METHODS:
        child=None;identity=None;instance=dict(method=method,stages=[],outstandingUnknown=False);instances.append(instance)
        t0=time.monotonic();instance.update(startedAt=t0);instance_end=min(end,t0+30)
        try:
            need(time.monotonic()<end,'DIAGNOSTIC_TOTAL_DEADLINE')
            owned=root/method;owned.mkdir(exist_ok=False);owner=secrets.token_hex(16)
            child=DiagnosticChild.__new__(DiagnosticChild);children.append(child);processes+=1
            child.__init__(method,loader,owned,owner,ledger)
            stage_start=child.started
            for index,stage in enumerate(STAGES):
                stage_end=min(stage_start+5,instance_end,end)
                line=child.line(stage_end-time.monotonic())
                need(line=='E2C_DIAGNOSTIC_STAGE|'+stage+'|'+str(child.pid)+'|'+owner,'DIAGNOSTIC_STAGE_ORDER_OR_IDENTITY')
                if identity is None:
                    identity=invoke(lambda:reader.capture_identity(child.pid,owner,process_handle=int(child.process._handle)),min(.1,stage_end-time.monotonic()));identity_queries+=1;instance['identity']=identity
                before=copy.deepcopy(reader.facts());sample_start=time.monotonic()
                values=invoke(lambda:reader.read_cycle({'R':identity}),min(.1,stage_end-time.monotonic()));sample_end=time.monotonic();total_samples+=1
                need(time.monotonic()<=stage_end,'DIAGNOSTIC_STAGE_DEADLINE')
                after=copy.deepcopy(reader.facts());value=values['R']
                record=dict(stage=stage,startedAt=stage_start,endedAt=sample_end,durationSeconds=sample_end-stage_start,sampleDurationSeconds=sample_end-sample_start,identity=copy.deepcopy(identity),
                            metrics={key:value[key] for key in ('threads','handles','workingSetBytes','privateBytes')},observerFacts=after,observerBefore=before,
                            ledgerResourcesAfterSample=len(ledger.live),sameCreationValidatedByReader=True)
                instance['stages'].append(record)
                child.send('ACK:'+stage,'ACK');stage_acks+=1;stage_start=time.monotonic()
                if stage=='INIT_COMPLETE':hello_id=child.rpc('HELLO');rpc_requests+=1
            hello=child.response(hello_id,min(5,instance_end-time.monotonic(),end-time.monotonic()))
            need(hello['instance']==owner and hello['pid']==child.pid,'DIAGNOSTIC_HELLO_ORIGINAL_IDENTITY')
            instance['hello']=dict(hello,serialized=True,requestId=hello_id)
            exit_id=child.rpc('EXIT');rpc_requests+=1
            exit_reply=child.response(exit_id,min(5,instance_end-time.monotonic(),end-time.monotonic()))
            need(exit_reply['instance']==owner,'DIAGNOSTIC_EXIT_INSTANCE')
            instance['exitProof']=child.cleanup(identity,instance_end,normal=True)
            need(instance['exitProof'].get('exited') is True and instance['exitProof'].get('code')==0,'DIAGNOSTIC_ORIGINAL_EXIT_NOT_PROVEN')
        except BaseException as error:
            instance['error']=type(error).__name__+':'+str(error)[:256];unknowns.append(method+':'+instance['error'])
            if child is not None:instance['exitProof']=child.cleanup(identity,min(instance_end,end),borrow_pending=any(not future.done() for future in futures))
            if any(not future.done() for future in futures):instance['outstandingUnknown']=True
        finally:
            instance['endedAt']=time.monotonic();instance['durationSeconds']=instance['endedAt']-t0
            if child is not None:
                instance['transport']=dict(stdinBytes=child.stdin_bytes,stdoutBytes=child.stdout_bytes,stderrBytes=child.stderr_bytes,stderr=child.stderr.decode('utf-8',errors='replace'),events=child.sent,threadsJoined=all(not thread.is_alive() for _,thread in child.threads),errors=child.errors)
                if child.errors:instance['outstandingUnknown']=True;unknowns.extend(method+':'+item for item in child.errors)
        if instance['outstandingUnknown'] or not (instance.get('exitProof') or {}).get('exited'):break
    all_returned=all(future.done() for future in futures)
    pool.shutdown(wait=all_returned,cancel_futures=False)
    if all_returned:
        for child in children:
            if getattr(child,'process_handle_deferred',False) and child.exit_proof and child.exit_proof['exited']:child.close_process_handle()
    workers=list(pool._threads);worker_joined=all_returned and all(not thread.is_alive() for thread in workers)
    if worker_joined:ledger.release(worker_credit,'THREAD_JOIN_PROVEN' if workers else 'THREAD_NOT_STARTED_PROVEN')
    else:unknowns.append('DIAGNOSTIC_NATIVE_WORKER_PENDING')
    report=dict(schema=1,scope='E2C_FIXED_R_STARTUP_DIAGNOSTIC',evidenceKind='ACTUAL_OS_OBSERVER',utcStarted=utc_started,
                configuration=dict(pwshVersion='7.6.5',dotnetVersion='10.0.11',assemblySha256=assembly_sha,stageOrder=list(STAGES),methods=[name for name,_ in METHODS]),
                startedAt=started,endedAt=time.monotonic(),instances=instances,unknowns=unknowns,
                costs=dict(processInstances=processes,metricSamples=total_samples,identityQueries=identity_queries,controlRequests=rpc_requests,stageAcks=stage_acks,logBytes=0,fixtureBytes=0,batchEvidenceBytes=0,testMediaBytes=0,
                           observerMaxOwnedHandles=reader.facts()['maximumOwnedHandlesObserved'],original452Charged=False,diagnosticNativeWorkers=1,transportReadersPerInstance=2),
                nativeReader=reader.facts(),workerJoined=worker_joined,remainingResources=copy.deepcopy(ledger.live),ledgerPeak=ledger.peak,realExecutionAllowed=False)
    report['durationSeconds']=report['endedAt']-started
    # Size accounting includes its own final JSON, reservation and every prior
    # batch evidence file; repeated fixed-point encoding does not write repairs.
    path=BASE/'evidence'/('diagnostic-'+stamp+'.json')
    prior_evidence=sum(p.stat().st_size for p in (BASE/'evidence').glob('*') if p.is_file())
    for _ in range(20):
        encoded=(json.dumps(report,indent=2,allow_nan=False)+'\n').encode('utf-8')
        log_bytes=reservation.stat().st_size+len(encoded);batch_bytes=prior_evidence+len(encoded)
        if report['costs']['logBytes']==log_bytes and report['costs']['batchEvidenceBytes']==batch_bytes:break
        report['costs'].update(logBytes=log_bytes,batchEvidenceBytes=batch_bytes)
    else:raise RuntimeError('DIAGNOSTIC_SIZE_ACCOUNTING_NOT_STABLE')
    need(log_bytes<=524288 and batch_bytes<=4194304,'DIAGNOSTIC_LOG_BUDGET_STOP')
    create_json(path,report)
    validation=validate_diagnostic(report)
    print(json.dumps(dict(evidence=str(path),validation=validation,processInstances=processes,samples=total_samples,remainingResources=len(ledger.live),workerJoined=worker_joined),separators=(',',':')))
    return 0 if not unknowns and not ledger.live else 2


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--run',action='store_true');args=parser.parse_args()
    raise SystemExit(run() if args.run else print('INSPECT_ONLY: E2C R diagnostic is blocked; E2B observations are historical only.'))
