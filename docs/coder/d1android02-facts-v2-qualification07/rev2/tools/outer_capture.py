# Derived from accepted SELF Capture: receiver/wait/close algorithm retained.
import os,time,threading,subprocess,ntpath
from capture_policy import disposition,FACT_KEYS
from native_identity import from_original_handle
from capture_origin import constructed,started,threads,eof,completed,before_constructor,before_launch
CUSTODY=[]
def new_facts():
 f={k:False for k in FACT_KEYS};f['phase']='PREFLIGHT';return f
class Capture:
    def __init__(self,plan,binding,journal,control,audit):
            before_constructor(self,journal)
            self.plan=plan;self.binding=binding;self.journal=journal;self.control=control;self.audit=audit;self.owner=(os.getpid(),threading.get_ident());self.facts=new_facts();self.original=None;self.held=[];self.readers=[];self.counts=[0,0];self.buffers=[bytearray(),bytearray()];self.failure=None;self.closed_entered=False;self.start=None;self.returned=False;self.pipe_amount_unknown=False;self.waiter=None;self.wait_fact={'entered':False,'returned':False,'error':None};CUSTODY.append(self);constructed(self)
    def _drain(self,i,s):
            try:
                while True:
                    b=s.read(4096)
                    if not b:eof(self,i);break
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
            if self.returned:return disposition(self.facts)
            if self.original is None:
                self.facts['otherEvidenceReturned']=self.journal.returned() and self.control.returned();answer=disposition(self.facts)
                if not answer.startswith('RETAIN') and self in CUSTODY:CUSTODY.remove(self)
                return answer
            if self.closed_entered and not self.returned:return 'RETAIN_ORIGINAL_CLOSE_ALREADY_ENTERED'
            p=self.original
            try:
                while not self.wait_fact['returned'] or any(t.is_alive() for t in self.readers) or (self.waiter is not None and self.waiter.is_alive()):
                    if time.monotonic()-self.start>=self.observationSeconds:self.failure=self.failure or 'OBSERVATION_EXPIRED';self.control.request('OBSERVATION_EXPIRED')
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
            if self.returned and self.failure is None:completed(self)
            answer=disposition(self.facts)
            if not answer.startswith('RETAIN') and self in CUSTODY:CUSTODY.remove(self)
            return answer
    def launch(self,registry,seconds):
        before_launch(self)
        self.observationSeconds=seconds
        kw=dict(executable=self.plan['argv'][0],cwd=self.plan['cwd'],env=self.plan['env'],shell=False,close_fds=True,stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        # Validation occurs before any original Popen constructor or temporary pipe.
        registry.check(self.plan['argv'],kw)
        self.journal.write('launch-intent',self.plan)
        self.start=time.monotonic();self.facts['phase']='CONSTRUCTOR_ENTERED'
        try:
            p=registry.construct(self.plan['argv'],**kw);self.original=p;self.held.append(p);started(self,p)
            self.facts.update(phase='CREATED_ORIGINAL',popenObjectReturned=True,constructorTempsReturned=True,auditObserved=bool(registry.events and registry.events[-1]['matches']))
            self.readers=[threading.Thread(target=self._drain,args=(i,s)) for i,s in enumerate((p.stdout,p.stderr))];self.held.extend(self.readers)
            for t in self.readers:t.start()
            self.waiter=threading.Thread(target=self._wait_original);self.held.append(self.waiter);self.waiter.start();threads(self)
            self.identity=from_original_handle(p._handle,self.plan['argv'])
            self.facts['identityBound']=self.identity['pid']==p.pid and self.identity['creationFileTime']>0 and ntpath.normcase(ntpath.normpath(self.identity['image']))==ntpath.normcase(ntpath.normpath(self.plan['argv'][0]))
            if not self.facts['identityBound']:self.failure='ORIGINAL_IDENTITY_MISMATCH'
            self.journal.write('original-identity',self.identity)
        except BaseException as e:
            self.failure=type(e).__name__;self.held.extend([e,e.__traceback__]);self.control.request('ORIGINAL_LAUNCH_OR_IDENTITY_FAILURE')
        return self
