"""Original new-worker Popen only. One waiter + two readers, never PID lookup."""
import subprocess,threading,time
from self_io import save,known,UNKNOWN
from parent_identity import from_original_handle
CUSTODY=[]
class Observer:
    def __init__(self,argv,executable,cwd,env,root,stop,window=180):
        self.window=window;self.argv=argv;self.root=root;self.stop=stop;self.p=None;self.held=[];self.buffers=[bytearray(),bytearray()];self.counts=[0,0];self.errors=[];self.returned=False;self.close_entered=False;self.expired=False;self.identity=None;self.start=time.monotonic();self.wait={'returned':False,'error':None};CUSTODY.append(self)
        save(root/'runtime/worker-launch-intent.json',{'argv':argv,'executable':executable,'cwd':cwd,'env':env,'scopeStartMonotonic':self.start,'originalObjectOnly':True})
        try:
            self.p=subprocess.Popen(argv,executable=executable,cwd=cwd,env=env,shell=False,close_fds=True,stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.PIPE);self.held.append(self.p)
            self.readers=[threading.Thread(target=self.drain,args=(i,s)) for i,s in enumerate((self.p.stdout,self.p.stderr))];self.held.extend(self.readers)
            for t in self.readers:t.start()
            self.waiter=threading.Thread(target=self.wait_original);self.held.append(self.waiter);self.waiter.start()
            self.identity=from_original_handle(self.p._handle,argv);save(root/'runtime/worker-original-handle.json',self.identity)
        except BaseException as e:self.errors.append(type(e).__name__);self.held.extend([e,e.__traceback__]);stop('OUTER_CREATION_OR_IDENTITY_NOT_QUALIFIED')
    def drain(self,i,s):
        try:
            while True:
                b=s.read(4096)
                if not b:break
                self.counts[i]+=len(b)
                if sum(self.counts)<=262144:self.buffers[i].extend(b)
                else:self.stop('OUTER_PIPE_BOUND')
        except BaseException as e:self.errors.append(type(e).__name__);self.held.extend([e,e.__traceback__]);self.stop('OUTER_READER_UNKNOWN')
    def wait_original(self):
        try:self.wait['exitCode']=self.p.wait();self.wait['returned']=True
        except BaseException as e:self.wait['error']=type(e).__name__;self.held.extend([e,e.__traceback__])
    def collect(self):
        while self.p is None or not self.wait['returned'] or any(t.is_alive() for t in getattr(self,'readers',[])) or getattr(self,'waiter',None) is None or self.waiter.is_alive():
            if time.monotonic()-self.start>=self.window and not self.expired:
                self.expired=True;self.stop('OUTER_FIXED_WINDOW_EXPIRED_STOP_NEW_ADMISSION');save(self.root/'runtime/outer-expired.json',{'originalsRetained':True,'noKillRetryOrSecondClose':True})
            for t in getattr(self,'readers',[]):t.join(.02)
            if getattr(self,'waiter',None) is not None:self.waiter.join(.02)
            else:time.sleep(.02)
        self.waiter.join()
        for t in self.readers:t.join()
        if self.close_entered:raise RuntimeError('ORIGINAL_OUTER_CLOSE_ONCE')
        self.close_entered=True
        try:self.p.stdout.close();self.p.stderr.close();self.p._handle.Close()
        except BaseException as e:
            self.held.extend([e,e.__traceback__]);self.stop('OUTER_ORIGINAL_CLOSE_UNKNOWN')
            while True:time.sleep(.1)
        self.returned=True
        for i,name in enumerate(('stdout','stderr')):
            data=bytes(self.buffers[i])
            for off in range(0,len(data),8192):save(self.root/'runtime'/('outer-'+name+'-'+str(off)+'.json'),{'offset':off,'hex':data[off:off+8192].hex()})
        result={'exitCode':self.wait['exitCode'],'seconds':time.monotonic()-self.start,'identity':self.identity,'originalWaitReturnedOnce':True,'readersJoined':True,'streamsAndOriginalHandleCloseReturned':True,'rawCounts':self.counts,'savedCounts':[len(b) for b in self.buffers],'errors':self.errors,'expired':self.expired,'allOriginalEvidenceFilesClosedAtObservation':known()}
        save(self.root/'runtime/outer-original-return.json',result);CUSTODY.remove(self)
        return result
