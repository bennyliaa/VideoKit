package com.videokit.spike.c14;
import android.content.*;
import android.os.*;
import java.io.IOException;
import java.security.SecureRandom;
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.*;

/** Host control and readonly broker. Exactly two task slots; unresolved death/release retains its slot. */
public final class CpuTaskClient implements AutoCloseable {
    private final E6ADiagnosticInbox diagnosticInbox=new E6ADiagnosticInbox(new E6ADiagnosticInbox.State(){
        public int pid(){return pid;}public int uid(){return uid;}public String task(){return task;}public long epoch(){return epoch;}
        public boolean revoked(){return revoked.get();}public int stage(){return nativeStage;}public int mode(){return mode;}public int frames(){return verificationFrames().size();}
    });
    E6NativeDiagnostic nativeDiagnostic(){return diagnosticInbox.snapshot();}

    private static final Semaphore SLOTS=new Semaphore(2);
    private static final Set<CpuTaskClient> OWNERS=ConcurrentHashMap.newKeySet();
    private static ThreadPoolExecutor pool(String name,int threads,int queue){return new ThreadPoolExecutor(threads,threads,0,TimeUnit.MILLISECONDS,new ArrayBlockingQueue<>(queue),r->{Thread t=new Thread(r,name);t.setDaemon(true);return t;},new ThreadPoolExecutor.AbortPolicy());}
    private static final ThreadPoolExecutor CONNECTIONS=pool("c14-cpu-connect",2,16), RPC=pool("c14-cpu-rpc",2,4), STOPS=pool("c14-cpu-stop",2,2);
    private final CpuLifecycle lifecycle=new CpuLifecycle();
    private final WorkerGenerations workers=new WorkerGenerations();
    private static final ThreadPoolExecutor RETIRE=pool("c14-cpu-retire",2,4);
    private static final ThreadPoolExecutor UNBINDS=pool("c14-cpu-unbind",2,4);
    private final BindingRevocation bindingRevocation=new BindingRevocation();
    private final AtomicIntegerArray registrationCounts=new AtomicIntegerArray(32);
    private final AtomicBoolean primaryConnectionClaimed=new AtomicBoolean();
    private final AtomicBoolean startClaimed=new AtomicBoolean();
    private final Set<DebugExtraBinding> debugBindings=ConcurrentHashMap.newKeySet();
    volatile CountDownLatch debugHelloEntered,debugHelloRelease;
    volatile CountDownLatch debugRegistrationEntered,debugRegistrationRelease,debugBindReturnEntered,debugBindReturnRelease,debugUnbindEntered,debugUnbindRelease;
    volatile boolean debugRegistrationProbes;volatile int debugRegistrationReply;
    final AtomicInteger debugUnbindFailures=new AtomicInteger();
    // Includes framework runnables already dispatched before unbind, not just callback bodies.
    private final Executor callbackExecutor=work->{lifecycle.callStarted();try{CONNECTIONS.execute(()->{try{work.run();}finally{lifecycle.callFinished();}});}catch(RuntimeException e){lifecycle.callFinished();throw e;}};
    public static final int NORMAL=CpuProtocol.NORMAL, WAIT_FRAME=CpuProtocol.WAIT_FRAME, SEGV_FRAME=CpuProtocol.SEGV_FRAME, HANG_FRAME=CpuProtocol.HANG_FRAME, FORGE_FRAME=CpuProtocol.FORGE_FRAME, FORGE_EPOCH=CpuProtocol.FORGE_EPOCH, FORGE_IDENTITY=CpuProtocol.FORGE_IDENTITY;
    public static final int AVI_MPEG4=CpuProtocol.AVI_MPEG4, MP4_H264=CpuProtocol.MP4_H264;
    public static final int QUOTA_PROBE=CpuProtocol.QUOTA_PROBE;
    public static final int STOP_STALL=CpuProtocol.STOP_STALL,STOP_ACK_LOSS=CpuProtocol.STOP_ACK_LOSS;
    public static final int PIPELINE_FRAME=CpuProtocol.PIPELINE_FRAME,VERIFY_OUTPUT=CpuProtocol.VERIFY_OUTPUT;
    private volatile boolean orientationVerified,verificationDone;private long[] verificationTimeline;
    public static final class VerifyFrame {
        public final long pts,raw;public final int num,den,best;public final String sha;private final byte[] thumb;
        private VerifyFrame(long pts,long raw,int num,int den,int best,byte[] hash,byte[] thumb){this.pts=pts;this.raw=raw;this.num=num;this.den=den;this.best=best;StringBuilder out=new StringBuilder();for(byte b:hash)out.append(String.format(java.util.Locale.ROOT,"%02x",b&255));sha=out.toString();this.thumb=thumb.clone();}
        public byte[] thumb(){return thumb.clone();}
    }
    private final java.util.List<VerifyFrame> verificationFrames=new java.util.ArrayList<>();
    void verificationTimeline(long[] timeline)throws IOException{PipelineRules.timeline(timeline);if(startClaimed.get())throw new IOException("PIPE_VERIFY_ALREADY_STARTED");verificationTimeline=timeline.clone();}
    public boolean orientationVerified(){return orientationVerified;}
    public boolean verificationDone(){return verificationDone;}
    public java.util.List<VerifyFrame> verificationFrames(){synchronized(verificationFrames){return java.util.List.copyOf(verificationFrames);}}
    void awaitVerification(long ms)throws Exception{finished.get(ms,TimeUnit.MILLISECONDS);if(!verificationDone)throw new IOException("PIPE_VERIFY_UNPROVEN");}
    public static final class Frame {
        public final long ptsUs,sourceTimestamp,peakRssKiB,quotaPeakBytes,quotaCurrentBytes;public final int timeBaseNum,timeBaseDen;public final boolean bestEffort;
        public final int width=CpuFrameRules.WIDTH,height=CpuFrameRules.HEIGHT,stride=CpuFrameRules.STRIDE;
        private final byte[] pixels;
        private Frame(long pts,long raw,int num,int den,int best,long peak,long quotaPeak,long quotaCurrent,byte[] pixels){ptsUs=pts;sourceTimestamp=raw;timeBaseNum=num;timeBaseDen=den;bestEffort=best==1;peakRssKiB=peak;quotaPeakBytes=quotaPeak;quotaCurrentBytes=quotaCurrent;this.pixels=pixels;}
        public byte[] copyPixels(){return pixels.clone();}
        public int bytes(){return pixels.length;}
    }
    private final Context context;public final String task=UUID.randomUUID().toString().replace("-","");
    public final long epoch=new SecureRandom().nextLong() & Long.MAX_VALUE;
    private final String token=UUID.randomUUID().toString().replace("-","");
    private final LeaseRegistry leases=new LeaseRegistry();private final AsyncReadBridge.Runtime runtime=new AsyncReadBridge.Runtime();
    private final long generation;private final AsyncReadBridge source;private final long length;
    private final CompletableFuture<IBinder> connected=new CompletableFuture<>();
    private final CompletableFuture<Void> death=new CompletableFuture<>();
    private final CompletableFuture<Frame> firstFrame=new CompletableFuture<>(),finished=new CompletableFuture<>();
    private final CompletableFuture<Integer> armed=new CompletableFuture<>();
    private final AtomicBoolean revoked=new AtomicBoolean(),releasedSlot=new AtomicBoolean(),stopRequested=new AtomicBoolean();
    private final AtomicBoolean sourceCall=new AtomicBoolean(),frameCall=new AtomicBoolean();private final AtomicLong readBytes=new AtomicLong();
    private final AtomicInteger reads=new AtomicInteger(),rejections=new AtomicInteger();
    private volatile IBinder remote;private volatile boolean bound,greeted,accepted;private volatile Frame frame;
    private volatile int pid=-1,uid=-1,mode,nativeStage;private volatile long target,startedAt;private volatile boolean launched,budgetAccepted,quotaProved;
    public CpuTaskClient(Context context,AsyncReadBridge.Provider provider)throws Exception {this(e9CheckedContext(context),provider,true);}
    private static Context e9CheckedContext(Context c)throws java.io.IOException{com.videokit.spike.e4.E9Phase.requireProduct();return c;}
    private CpuTaskClient(Context context,AsyncReadBridge.Provider provider,boolean phaseChecked)throws Exception {
        com.videokit.spike.e4.E9Phase.requireProduct();
        if(Looper.myLooper()==Looper.getMainLooper())throw new IOException("CPU_HOST_MAIN_THREAD");
        if(!SLOTS.tryAcquire())throw new IOException("CPU_SLOTS_EXHAUSTED_OR_QUARANTINED");
        this.context=context.getApplicationContext();long gen=0;AsyncReadBridge opened=null;long size=0;
        try {gen=leases.create();opened=new AsyncReadBridge(runtime,provider,leases,gen,5000);size=opened.open(0,-1);
            CpuFrameRules.sourceLength(size);
        }catch(Exception error){CpuDiagnostics.Failure primary=CpuDiagnostics.failure("CPU_SOURCE_OPEN_FAILED","SOURCE_OPEN",error);
            if(opened!=null)opened.close();if(gen>0)leases.retire(gen);boolean drained=gen==0;
            try{drained|=gen>0 && leases.awaitReleased(gen,5000);}catch(InterruptedException cleanup){Thread.currentThread().interrupt();primary.addSuppressed(CpuDiagnostics.failure("CPU_SOURCE_CLEANUP_INTERRUPTED","SOURCE_CLEANUP",cleanup));}
            if(drained){runtime.close();SLOTS.release();}else AbandonedSource.retain(runtime,leases,gen,opened);
            throw primary;
        }
        generation=gen;source=opened;length=size;OWNERS.add(this);
    }
    /** Constructor cleanup failures count against the same two slots until explicit recovery. */
    private static final class AbandonedSource {
        static final List<AbandonedSource> RETAINED=new CopyOnWriteArrayList<>();
        final AsyncReadBridge.Runtime runtime;final LeaseRegistry leases;final long gen;final AsyncReadBridge bridge;
        AbandonedSource(AsyncReadBridge.Runtime r,LeaseRegistry l,long g,AsyncReadBridge b){runtime=r;leases=l;gen=g;bridge=b;}
        static void retain(AsyncReadBridge.Runtime r,LeaseRegistry l,long g,AsyncReadBridge b){RETAINED.add(new AbandonedSource(r,l,g,b));}
    }
    public static int quarantinedSources(){return AbandonedSource.RETAINED.size();}
    public static List<LeaseRegistry.Snapshot> abandonedSourceLedgers(){List<LeaseRegistry.Snapshot> result=new ArrayList<>();for(AbandonedSource item:AbandonedSource.RETAINED)result.add(item.leases.query(item.gen));return List.copyOf(result);}
    public static int recoverAbandonedSources(long budgetMs)throws Exception {
        if(Looper.myLooper()==Looper.getMainLooper())throw new IllegalStateException("CPU_RECOVERY_MAIN_THREAD");
        if(budgetMs<1 || budgetMs>15000)throw new IllegalArgumentException("CPU_RECOVERY_BUDGET");
        long stop=System.nanoTime()+TimeUnit.MILLISECONDS.toNanos(budgetMs);int recovered=0;
        for(AbandonedSource item:AbandonedSource.RETAINED){
            if(item.bridge.closeState()==AsyncReadBridge.CloseState.FAILED)item.bridge.retryFailedClose();
            if(item.leases.awaitReleased(item.gen,Math.max(1,TimeUnit.NANOSECONDS.toMillis(stop-System.nanoTime()))) && AbandonedSource.RETAINED.remove(item)){item.runtime.close();SLOTS.release();recovered++;}
            if(System.nanoTime()>=stop)break;
        }return recovered;
    }
    private CpuDiagnostics.Failure diagnose(String code,String phase,Throwable error){
        CpuDiagnostics.Failure failure=CpuDiagnostics.failure(code,phase,error);lifecycle.firstFailure(failure.code,failure.phase);
        StageLog.event("CPU_DIAGNOSIS","task="+task+" epoch="+epoch+" code="+failure.code+" phase="+failure.phase+" category="+failure.category+" original_type="+failure.originalType);return failure;
    }
    private void observeDeath(WorkerGenerations.Worker worker){
        boolean primary=workers.died(worker);
        StageLog.event("CPU_GENERATION_DEATH","task="+task+" epoch="+epoch+" generation="+worker.serial+" pid="+worker.pid+" uid="+worker.uid+" primary="+primary);
        if(primary){lifecycle.death();death.complete(null);revoke();IOException died=new IOException("CPU_WORKER_DIED");finished.completeExceptionally(died);firstFrame.completeExceptionally(died);detachAfterDeath();}
    }
    private void detachAfterDeath(){requestBindingRevocation();}
    private void requestBindingRevocation(){if(bindingRevocation.request()){logBindingRevocation();queueBindingRevocation();}}
    private void queueBindingRevocation(){
        if(!bindingRevocation.queue())return;
        lifecycle.callStarted();logBindingRevocation();try{UNBINDS.execute(()->{boolean success=false;String result="UNBIND_FAILED";
            try{
                if(debugUnbindEntered!=null){debugUnbindEntered.countDown();if(!debugUnbindRelease.await(10,TimeUnit.SECONDS))throw new IOException("CPU_DEBUG_UNBIND_TIMEOUT");}
                if(debugUnbindFailures.getAndUpdate(n->Math.max(0,n-1))>0)throw new IOException("CPU_DEBUG_UNBIND_FAILED");
                // No client/workers monitor is held across Context or system-server IPC.
                context.unbindService(connection);bound=false;workers.bindingClosed();success=true;result="UNBOUND_WAIT_DEATH";
            }catch(Exception error){StageLog.failure("CPU_UNBIND_UNPROVEN",error);}
            finally{bindingRevocation.finished(success,result);lifecycle.callFinished();logBindingRevocation();}
        });}catch(RejectedExecutionException error){bindingRevocation.finished(false,"QUEUE_REJECTED");lifecycle.callFinished();logBindingRevocation();}
    }
    private void logBindingRevocation(){BindingRevocation.Snapshot s=bindingRevocation.snapshot();StageLog.event("CPU_UNBIND_LEDGER","task="+task+" epoch="+epoch+" issued="+s.issued+" requested="+s.requested+" bind_in_flight="+s.inFlight+" accepted="+s.accepted+" uncertain="+s.uncertain+" attempts="+s.attempts+" pending="+s.pending+" closed="+s.closed+" result="+s.result);}
    /** Invoked synchronously from every service onBind, before Android can publish its Binder.
     * Catches rebuilt services even when unbind suppresses their ServiceConnection callback. */
    private final Binder registrar=new Binder(){
        @Override protected boolean onTransact(int code,Parcel p,Parcel reply,int flags)throws RemoteException {
            int callerPid=Binder.getCallingPid(),callerUid=Binder.getCallingUid(),bytes=p.dataSize(),result=RegistrationProtocol.CALLBACK,serial=0,phase=RegistrationProtocol.CALLBACK;
            lifecycle.callStarted();try{
                if(!RegistrationProtocol.synchronous(flags))throw new RegistrationProtocol.Rejected(RegistrationProtocol.ONEWAY);
                if(reply==null)throw new RegistrationProtocol.Rejected(RegistrationProtocol.INPUT);
                if(code!=RegistrationProtocol.REGISTER && code!=RegistrationProtocol.FAILURE)throw new RegistrationProtocol.Rejected(RegistrationProtocol.CODE);
                if(bytes<1 || bytes>RegistrationProtocol.MAX_INPUT)throw new RegistrationProtocol.Rejected(RegistrationProtocol.INPUT);
                phase=RegistrationProtocol.DESCRIPTOR;p.enforceInterface(CpuProtocol.WORKER+".registration");
                RegistrationProtocol.identity(callerPid,callerUid,android.os.Process.myPid(),android.os.Process.myUid());
                phase=RegistrationProtocol.INPUT;String requestedTask=p.readString();long requestedEpoch=p.readLong();IBinder endpoint=p.readStrongBinder();
                int reported=code==RegistrationProtocol.FAILURE?p.readInt():0;CpuProtocol.end(p);
                if(!task.equals(requestedTask) || epoch!=requestedEpoch)throw new RegistrationProtocol.Rejected(RegistrationProtocol.SESSION);
                if(endpoint==null)throw new RegistrationProtocol.Rejected(RegistrationProtocol.ENDPOINT);
                if(code==RegistrationProtocol.FAILURE && !RegistrationProtocol.error(reported))throw new RegistrationProtocol.Rejected(RegistrationProtocol.INPUT);
                if(code==RegistrationProtocol.FAILURE){
                    workers.terminate();revoke();CpuDiagnostics.Failure failure=diagnose(RegistrationProtocol.name(reported),"REGISTER",null);
                    connected.completeExceptionally(failure);finished.completeExceptionally(failure);firstFrame.completeExceptionally(failure);requestBindingRevocation();
                }
                if(debugRegistrationEntered!=null && code==RegistrationProtocol.REGISTER){debugRegistrationEntered.countDown();if(!debugRegistrationRelease.await(10,TimeUnit.SECONDS))throw new RegistrationProtocol.Rejected(RegistrationProtocol.CALLBACK);}
                WorkerGenerations.Worker worker;boolean duplicate;
                synchronized(workers){
                    WorkerGenerations.Worker previous=workers.find(endpoint);duplicate=previous!=null;
                    if(previous!=null && (previous.pid!=callerPid || previous.uid!=callerUid))throw new RegistrationProtocol.Rejected(RegistrationProtocol.DUPLICATE_IDENTITY);
                    phase=RegistrationProtocol.OVERFLOW;worker=workers.register(endpoint,callerPid,callerUid,code==RegistrationProtocol.REGISTER);
                    if(worker.primary && remote==null){remote=endpoint;pid=worker.pid;uid=worker.uid;}
                }
                phase=RegistrationProtocol.CALLBACK;
                if(!duplicate)try{endpoint.linkToDeath(()->observeDeath(worker),0);}catch(DeadObjectException dead){observeDeath(worker);}
                serial=worker.serial;result=!workers.accept(worker)?RegistrationProtocol.RETIRED:duplicate?RegistrationProtocol.DUPLICATE:RegistrationProtocol.OK;
                StageLog.event("CPU_GENERATION_REGISTERED","task="+task+" epoch="+epoch+" generation="+serial+" pid="+worker.pid+" uid="+worker.uid+" primary="+worker.primary+" result="+RegistrationProtocol.name(result));
                if(!workers.accept(worker))stopRejected(worker);
            }catch(RegistrationProtocol.Rejected rejected){result=rejected.code;serial=0;}
            catch(Exception error){result=phase;serial=0;if(phase==RegistrationProtocol.CALLBACK)workers.quarantine();}
            finally{
                if(result>=0 && result<registrationCounts.length())registrationCounts.incrementAndGet(result);
                StageLog.event("CPU_REGISTRATION_DIAG","task="+task+" epoch="+epoch+" code="+code+" flags="+flags+" caller_pid="+callerPid+" caller_uid="+callerUid+" input_bytes="+bytes+" result="+RegistrationProtocol.name(result)+" generation="+serial);
                if(reply!=null && RegistrationProtocol.synchronous(flags)){
                    reply.setDataSize(0);reply.setDataPosition(0);reply.writeInt(debugRegistrationReply==1 && code==RegistrationProtocol.REGISTER && result<10?0:RegistrationProtocol.MAGIC);reply.writeInt(RegistrationProtocol.VERSION);reply.writeInt(result);reply.writeInt(serial);
                    if(debugRegistrationReply==2 && code==RegistrationProtocol.REGISTER && result<10)reply.writeInt(0);
                }
                lifecycle.callFinished();
            }
            return true;
        }
    };
    private void hello(WorkerGenerations.Worker worker)throws Exception {
        IBinder binder=(IBinder)worker.key;
        Parcel p=request(CpuProtocol.WORKER),a=Parcel.obtain();try{
            taskHeader(p);if(!binder.transact(CpuProtocol.HELLO,p,a,0))throw new IOException("CPU_HELLO_REJECTED");acknowledgement(a,1152);int actualPid=a.readInt(),actualUid=a.readInt();String process=a.readString();CpuProtocol.end(a);
            if(actualPid<=0 || actualPid==android.os.Process.myPid() || actualUid<=0 || actualUid==android.os.Process.myUid() || actualUid%100000<90000)throw new IOException("CPU_ISOLATION_IDENTITY");
            worker.validated(actualPid,actualUid);
            if(process==null || process.length()>512 || !process.startsWith(context.getPackageName()+":d1_cpu_worker:"+CpuIsolatedService.class.getName()+":"))throw new IOException("CPU_PROCESS_IDENTITY");
            if(worker.primary){if(primaryProcess!=null && !primaryProcess.equals(process))throw new IOException("CPU_PROCESS_IDENTITY");primaryProcess=process;greeted=true;lifecycle.identity();}
            StageLog.event("CPU_HELLO_VALIDATED","task="+task+" epoch="+epoch+" generation="+worker.serial+" pid="+worker.pid+" uid="+worker.uid+" primary="+worker.primary);
        }finally{p.recycle();a.recycle();}
    }
    private final ServiceConnection connection=new ServiceConnection(){
        @Override public void onServiceConnected(ComponentName name,IBinder binder){
            WorkerGenerations.Worker worker=workers.find(binder);
            if(worker==null){connected.completeExceptionally(diagnose("CPU_UNREGISTERED_BINDER_QUARANTINED","CONNECT",null));workers.quarantine();revoke();requestBindingRevocation();return;}
            if(!workers.accept(worker)){stopRejected(worker);connected.completeExceptionally(diagnose("CPU_TERMINAL_CONNECTION","CONNECT",null));return;}
            if(!primaryConnectionClaimed.compareAndSet(false,true)){StageLog.event("CPU_DUPLICATE_CONNECTION_REJECTED","task="+task+" generation="+worker.serial);return;}
            lifecycle.connected();lifecycle.callStarted();StageLog.event("CPU_BIND_CONNECTED","task="+task+" epoch="+epoch+" generation="+worker.serial);
            try{if(debugHelloEntered!=null){debugHelloEntered.countDown();if(!debugHelloRelease.await(3,TimeUnit.SECONDS))throw new IOException("CPU_DEBUG_HELLO_TIMEOUT");}hello(worker);if(!workers.accept(worker)){stopRejected(worker);connected.completeExceptionally(new IOException("CPU_TERMINAL_HELLO"));return;}connected.complete(binder);}
            catch(DeadObjectException error){observeDeath(worker);connected.completeExceptionally(diagnose("CPU_PEER_DIED_BEFORE_HELLO","HELLO",error));}
            catch(Exception error){connected.completeExceptionally(diagnose("CPU_HELLO_FAILED","HELLO",error));requestBindingRevocation();}
            finally{lifecycle.callFinished();if(stopRequested.get() && lifecycle.snapshot().stopAttempts==0)sendStop();}
        }
        @Override public void onServiceDisconnected(ComponentName name){/* Binder DeathRecipient is the actual-death witness. */}
        @Override public void onNullBinding(ComponentName name){connected.completeExceptionally(diagnose("CPU_NULL_BINDING","CONNECT",null));requestBindingRevocation();}
        @Override public void onBindingDied(ComponentName name){connected.completeExceptionally(diagnose("CPU_BINDING_DIED","CONNECT",null));requestBindingRevocation();}
    };
    private static Parcel request(String descriptor){Parcel p=Parcel.obtain();p.writeInterfaceToken(descriptor);return p;}
    private static void acknowledgement(Parcel p)throws IOException {
        acknowledgement(p,64);
    }
    private static void acknowledgement(Parcel p,int maximum)throws IOException {
        if(p.dataSize()<4 || p.dataSize()>maximum)throw new IOException("CPU_WORKER_ACK_PROTOCOL");
        int marker=p.readInt();if(marker==CpuControlRules.ERROR){if(p.dataSize()!=8)throw new IOException("CPU_WORKER_ACK_PROTOCOL");throw new IOException(CpuControlRules.errorCode(p.readInt()));}
        if(marker!=CpuFrameRules.ACK)throw new IOException("CPU_WORKER_ACK_PROTOCOL");
    }
    private void taskHeader(Parcel p){p.writeString(task);p.writeLong(epoch);}
    private <T>T rpc(String phase,Callable<T> work,long ms)throws Exception {
        AtomicBoolean expired=new AtomicBoolean();Future<T> f;lifecycle.callStarted();
        try{f=RPC.submit(()->{try{if(expired.get() || (stopRequested.get() && !phase.equals("RECOVERY_RELEASE")))throw new IOException("CPU_COMMAND_CANCELLED");return work.call();}finally{lifecycle.callFinished();}});}
        catch(RejectedExecutionException error){lifecycle.callFinished();throw diagnose("CPU_RPC_QUEUE_REJECTED",phase,error);}
        try{return f.get(ms,TimeUnit.MILLISECONDS);}catch(TimeoutException error){expired.set(true);throw diagnose("CPU_RPC_DEADLINE_QUARANTINED",phase,error);}
        catch(ExecutionException error){throw diagnose(phase.equals("BIND")?"CPU_BIND_CALL_FAILED":phase.equals("START")?"CPU_START_CALL_FAILED":phase.equals("ENVIRONMENT")?"CPU_ENVIRONMENT_QUERY_FAILED":"CPU_COMMAND_FAILED",phase,error);}
    }
    public void start(int kind,long targetUs,int mode)throws Exception {
        if(Looper.myLooper()==Looper.getMainLooper())throw diagnose("CPU_HOST_MAIN_THREAD","START",null);
        if(kind<1 || kind>2 || mode<0 || mode>11 || epoch==0
                || targetUs<0 || targetUs>CpuFrameRules.MAX_PTS_US-2000000)throw new IOException("CPU_START_STATE");
        if(!startClaimed.compareAndSet(false,true) || stopRequested.get())throw new IOException("CPU_START_STATE");
        if(mode==VERIFY_OUTPUT && (verificationTimeline==null || kind!=MP4_H264 || targetUs!=0 || length>PipelineRules.MAX_OUTPUT))throw new IOException("PIPE_VERIFY_REQUEST");
        this.mode=mode;target=targetUs;startedAt=System.currentTimeMillis();
        rpc("ENVIRONMENT",()->{CpuEnvironment.requireReady(context);return null;},5000);
        launched=true;StageLog.event("CPU_BIND_REQUEST","task="+task+" epoch="+epoch);
        try{rpc("BIND",()->{lifecycle.requestBind();bindingRevocation.beginBind();Intent intent=new Intent(context,CpuIsolatedService.class);Bundle registration=new Bundle();registration.putBinder("registrar",registrar);registration.putString("task",task);registration.putLong("epoch",epoch);registration.putBoolean("debug_registration_probes",debugRegistrationProbes);intent.putExtra("c14_registration",registration);
            boolean acceptedBind;
            try{acceptedBind=context.bindIsolatedService(intent,Context.BIND_AUTO_CREATE,"cpu_"+task,callbackExecutor,connection);}
            catch(RuntimeException error){bindingRevocation.returnedUnknown();queueBindingRevocation();throw error;}
            bound=acceptedBind;lifecycle.bindReturned(acceptedBind);
            if(debugBindReturnEntered!=null){debugBindReturnEntered.countDown();if(!debugBindReturnRelease.await(10,TimeUnit.SECONDS)){bindingRevocation.returned(acceptedBind);queueBindingRevocation();throw new IOException("CPU_DEBUG_BIND_RETURN_TIMEOUT");}}
            bindingRevocation.returned(acceptedBind);queueBindingRevocation();if(!acceptedBind)throw new IOException("CPU_BIND_REJECTED");
            return null;},5000);}
        catch(Exception error){requestBindingRevocation();throw diagnose("CPU_BIND_CALL_FAILED","BIND",error);}
        try{connected.get(5000,TimeUnit.MILLISECONDS);}catch(Exception error){requestBindingRevocation();throw diagnose("CPU_CONNECT_FAILED","CONNECT",error);}
        rpc("START",()->{Parcel p=request(CpuProtocol.WORKER),a=Parcel.obtain();try{
            if(!workers.accept(workers.primary()))throw new IOException("CPU_GENERATION_TERMINAL");
            taskHeader(p);p.writeString(token);p.writeLong(length);p.writeLong(targetUs);p.writeInt(kind);p.writeInt(mode);p.writeStrongBinder(broker);
            if(mode==VERIFY_OUTPUT)p.writeLongArray(verificationTimeline);
            if(!remote.transact(CpuProtocol.START,p,a,0))throw new IOException("CPU_START_REJECTED");acknowledgement(a);CpuProtocol.end(a);return null;
        }finally{p.recycle();a.recycle();}},5000);
        lifecycle.started();StageLog.event("CPU_TASK_STARTED","task="+task+" epoch="+epoch+" pid="+pid+" uid="+uid+" kind="+kind+" mode="+mode);
    }
    private final Binder broker=new Binder(){
        @Override protected boolean onTransact(int code,Parcel p,Parcel reply,int flags)throws RemoteException {
            boolean sourceAcquired=false,frameAcquired=false;
            try {
                if(p.dataSize()>CpuFrameRules.BYTES+1024 || (code!=CpuProtocol.FRAME && p.dataSize()>1024))throw new IOException("CPU_PARCEL_BUDGET");
                p.enforceInterface(CpuProtocol.BROKER);
                int callerPid=Binder.getCallingPid(),callerUid=Binder.getCallingUid();String requestedTask=p.readString();long requestedEpoch=p.readLong();
                SourceAdmission.require(uid,pid,task,epoch,callerUid,callerPid,requestedTask,requestedEpoch,"CPU_BROKER_IDENTITY");
                if(revoked.get())throw new IOException("CPU_BROKER_IDENTITY");
                if(code==CpuProtocol.NATIVE_DIAGNOSTIC){
                    E6NativeDiagnostic d=diagnosticInbox.receive(callerPid,callerUid,requestedTask,requestedEpoch,p.dataSize(),new E6ADiagnosticInbox.Payload(){
                        public E6NativeDiagnostic parse()throws Exception{return new E6NativeDiagnostic(p.readInt(),p.readInt(),p.readInt(),p.readInt(),p.readInt(),p.readInt(),p.readInt(),p.readInt(),p.readInt(),p.readInt(),p.readLong(),p.readLong(),p.readLong());}
                        public void end(){CpuProtocol.end(p);}
                    });
                    StageLog.event("E6_NATIVE_DIAGNOSTIC","task="+task+" epoch="+epoch+" pid="+pid+" uid="+uid+" "+d.safe()+" broker_read_at_requests="+reads.get()+" broker_compressed_bytes="+readBytes.get());reply.writeNoException();return true;
                }
                if(code==CpuProtocol.ORIENTATION){int rotation=p.readInt();CpuProtocol.end(p);if((mode!=PIPELINE_FRAME && mode!=VERIFY_OUTPUT) || rotation!=0 || orientationVerified || nativeStage!=1)throw new IOException("PIPE_ORIENTATION_REJECTED");orientationVerified=true;StageLog.event("CPU_ORIENTATION_VERIFIED","task="+task+" epoch="+epoch+" pid="+pid+" uid="+uid+" rotation=0");reply.writeNoException();return true;}
                if(code==CpuProtocol.VERIFY_FRAME){
                    if(mode!=VERIFY_OUTPUT || !orientationVerified || nativeStage!=5)throw new IOException("PIPE_VERIFY_PHASE");
                    int sequence=p.readInt(),width=p.readInt(),height=p.readInt(),stride=p.readInt(),length=p.readInt(),rotation=p.readInt();long pts=p.readLong(),raw=p.readLong();int num=p.readInt(),den=p.readInt(),best=p.readInt();long rss=p.readLong(),peak=p.readLong(),current=p.readLong();
                    PipelineRules.layout(width,height,stride,length,rotation);CpuFrameRules.timestamp(raw,num,den,pts,best,rss);CpuFrameRules.allocationQuota(peak,current);
                    synchronized(verificationFrames){if(sequence!=verificationFrames.size()+1 || sequence>PipelineRules.FRAMES || Math.abs(pts-verificationTimeline[sequence-1])>1000)throw new IOException("PIPE_VERIFY_PTS_OR_COUNT");byte[] hash=new byte[32],thumb=new byte[144];p.readByteArray(hash);p.readByteArray(thumb);CpuProtocol.end(p);verificationFrames.add(new VerifyFrame(pts,raw,num,den,best,hash,thumb));}
                    StageLog.event("CPU_OUTPUT_FRAME_VERIFIED","task="+task+" epoch="+epoch+" pid="+pid+" uid="+uid+" sequence="+sequence+" pts_us="+pts+" raw="+raw+" time_base="+num+"/"+den);reply.writeNoException();return true;
                }
                if(code==CpuProtocol.BUDGET){
                    long baseline=p.readLong(),limit=p.readLong();String version=p.readString();CpuProtocol.end(p);
                    if(budgetAccepted || baseline<=0 || baseline>Long.MAX_VALUE-201326592 || limit!=baseline+201326592 || !"8.0.3".equals(version))throw new IOException("CPU_BUDGET_PROTOCOL");budgetAccepted=true;
                    StageLog.event("CPU_PREALLOC_BUDGET","task="+task+" epoch="+epoch+" pid="+pid+" uid="+uid+" ffmpeg="+version+" baseline_vms="+baseline+" hard_vms_limit="+limit+" max_pixels=2073600 max_single_alloc=16777216");reply.writeNoException();return true;
                }
                if(code==CpuProtocol.STAGE){
                    int stage=p.readInt();CpuProtocol.end(p);
                    if(!budgetAccepted || !((stage==nativeStage+1 && stage<=5) || (nativeStage==1 && stage==6)))throw new IOException("CPU_NATIVE_STAGE");nativeStage=stage;
                    StageLog.event("CPU_NATIVE_STAGE","task="+task+" epoch="+epoch+" pid="+pid+" uid="+uid+" stage="+stage);reply.writeNoException();return true;
                }
                if(code==CpuProtocol.READ_AT){
                    if(!sourceCall.compareAndSet(false,true))throw new IOException("CPU_READ_IN_FLIGHT");sourceAcquired=true;
                    String input=p.readString();long at=p.readLong();int count=p.readInt();CpuProtocol.end(p);
                    if(!token.equals(input) || at<0 || at>length || count<1 || count>CpuFrameRules.MAX_READ || reads.incrementAndGet()>8192)throw new IOException("CPU_READ_BOUNDS");
                    if(readBytes.get()+count>CpuFrameRules.READ_BUDGET)throw new IOException("CPU_READ_TOTAL_BUDGET");
                    source.seekAbsolute(at);byte[] bytes=new byte[count];int n=source.read(bytes,0,count);if(revoked.get())throw new IOException("CPU_REVOKED");
                    if(n<0)n=0;readBytes.addAndGet(n);reply.writeNoException();reply.writeInt(n);reply.writeByteArray(bytes,0,n);return true;
                }
                if(code==CpuProtocol.FRAME){
                    if(mode==VERIFY_OUTPUT || (mode==PIPELINE_FRAME && !orientationVerified))throw new IOException("PIPE_RAW_FRAME_PHASE");
                    if(!frameCall.compareAndSet(false,true))throw new IOException("CPU_FRAME_IN_FLIGHT");frameAcquired=true;
                    if(frame!=null)throw new IOException("CPU_FRAME_QUEUE_FULL");
                    int magic=p.readInt(),version=p.readInt(),claimedPid=p.readInt(),claimedUid=p.readInt();
                    int width=p.readInt(),height=p.readInt(),stride=p.readInt(),offset=p.readInt(),length=p.readInt();long pts=p.readLong();int sequence=p.readInt();
                    CpuFrameRules.frame(magic,version,task,task,epoch,epoch,claimedPid,claimedUid,pid,uid,width,height,stride,offset,length,pts,target,sequence);
                    long raw=p.readLong();int num=p.readInt(),den=p.readInt(),best=p.readInt();long peak=p.readLong();
                    CpuFrameRules.timestamp(raw,num,den,pts,best,peak);
                    long quotaPeak=p.readLong(),quotaCurrent=p.readLong();CpuFrameRules.allocationQuota(quotaPeak,quotaCurrent);
                    if(!budgetAccepted || nativeStage!=5)throw new IOException("CPU_FRAME_BEFORE_DECODE");
                    // Validate metadata before allocating exactly one fixed-size host pixel array.
                    byte[] pixels=new byte[CpuFrameRules.BYTES];p.readByteArray(pixels);CpuProtocol.end(p);frame=new Frame(pts,raw,num,den,best,peak,quotaPeak,quotaCurrent,pixels);
                    reply.writeNoException();StageLog.event("CPU_FRAME","task="+task+" epoch="+epoch+" pid="+pid+" uid="+uid+" pts_us="+pts+" raw="+raw+" time_base="+num+"/"+den+" best_effort="+best+" peak_rss_kib="+peak+" allocation_peak="+quotaPeak+" allocation_current="+quotaCurrent+" format=RGBA bytes="+pixels.length);return true;
                }
                if(code==CpuProtocol.EVENT){
                    E6NativeDiagnostic nativeDiagnostic=nativeDiagnostic();int event=p.readInt();int workerFailure=event==CpuProtocol.ERROR?p.readInt():0;CpuProtocol.end(p);
                    if(event==CpuProtocol.QUOTA_PROVED){if(mode!=QUOTA_PROBE || quotaProved || budgetAccepted)throw new IOException("CPU_QUOTA_PROBE_PHASE");quotaProved=true;}
                    else if(event==CpuProtocol.FRAME_ACCEPTED){if(frame==null || accepted)throw new IOException("CPU_FRAME_PHASE");accepted=true;firstFrame.complete(frame);}
                    else if(event==CpuProtocol.DONE){if(mode==VERIFY_OUTPUT){if(verificationFrames().size()!=PipelineRules.FRAMES || !orientationVerified || finished.isDone() || nativeDiagnostic==null || nativeDiagnostic.site!=0 || nativeDiagnostic.demuxEof!=1 || nativeDiagnostic.decoderEof!=1 || nativeDiagnostic.accepted!=6)throw new IOException("PIPE_VERIFY_DONE_PHASE");verificationDone=true;finished.complete(null);StageLog.event("CPU_OUTPUT_FULL_EOF_VERIFIED","task="+task+" epoch="+epoch+" pid="+pid+" uid="+uid+" frames="+PipelineRules.FRAMES+" audio_tracks=0");}else{if(frame==null || !accepted || finished.isDone())throw new IOException("CPU_DONE_PHASE");finished.complete(frame);}}
                    else if(event==CpuProtocol.ERROR){if(workerFailure<1 || workerFailure>4)throw new IOException("CPU_WORKER_ERROR_PROTOCOL");CpuDiagnostics.Failure error=nativeDiagnostic!=null && nativeDiagnostic.site!=0?diagnose(nativeDiagnostic.code(),"NATIVE_STAGE_"+nativeStage,CpuDiagnostics.nativeFailure(nativeDiagnostic)):diagnose(workerFailure==1?"CPU_NATIVE_LOAD_FAILED":workerFailure==2?"CPU_DECODE_FAILED":workerFailure==3?"CPU_WORKER_IO_OR_PROTOCOL_FAILED":"CPU_WORKER_INTERNAL_FAILED",workerFailure==1?"NATIVE_LOAD":"NATIVE_STAGE_"+nativeStage,null);finished.completeExceptionally(error);firstFrame.completeExceptionally(error);}
                    else if(event==CpuProtocol.SIGSEGV_ARMED || event==CpuProtocol.HANG_ARMED){
                        if(frame==null || !accepted || armed.isDone() || (event==CpuProtocol.SIGSEGV_ARMED && mode!=SEGV_FRAME && mode!=WAIT_FRAME)
                                || (event==CpuProtocol.HANG_ARMED && mode!=HANG_FRAME))throw new IOException("CPU_FAULT_PHASE");armed.complete(event);
                    }else throw new IOException("CPU_EVENT_CODE");
                    StageLog.event("CPU_EVENT","task="+task+" epoch="+epoch+" pid="+pid+" uid="+uid+" event="+event);reply.writeNoException();return true;
                }
                throw new IOException("CPU_TRANSACTION_CODE");
            }catch(Exception error){rejections.incrementAndGet();boolean sourceError=error instanceof IOException && error.getMessage()!=null && error.getMessage().matches("SOURCE_[A-Z_0-9]{1,64}");IOException rejected=sourceError?diagnose("CPU_SOURCE_FAILED","SOURCE",error):diagnose("CPU_PROTOCOL_REJECTED","BROKER",null);StageLog.failure("CPU_BROKER_LOCAL_CAUSE",error);finished.completeExceptionally(rejected);firstFrame.completeExceptionally(rejected);
                reply.writeException(new IllegalStateException("CPU_PROTOCOL_REJECTED"));return true;
            }finally{if(sourceAcquired)sourceCall.set(false);if(frameAcquired)frameCall.set(false);}
        }
    };
    private void revoke(){if(revoked.compareAndSet(false,true)){source.close();leases.retire(generation);}}
    private void sendStop(){
        IBinder endpoint=remote;if(endpoint==null || !lifecycle.queueStop())return;
        WorkerGenerations.Worker stopping=workers.primary();if(stopping==null || !stopping.queueStop()){lifecycle.stopFinished("GENERATION_NOT_QUEUED",false);return;}
        try{STOPS.execute(()->{
            lifecycle.callStarted();String outcome="STOP_FAILED";boolean ack=false;
            try{
                if(!greeted)hello(workers.primary()); // May authenticate a terminal worker only to stop it, never to restart.
                Parcel p=request(CpuProtocol.WORKER),a=Parcel.obtain();try{
                    taskHeader(p);if(!endpoint.transact(CpuProtocol.STOP,p,a,0))throw new IOException("CPU_STOP_REJECTED");acknowledgement(a);
                    if(a.readInt()!=1)throw new IOException("CPU_STOP_NOT_GRANTED");CpuProtocol.end(a);ack=true;outcome="ACKED_WAIT_DEATH";
                }finally{p.recycle();a.recycle();}
            }catch(DeadObjectException error){outcome="PEER_DIED_ACK_UNKNOWN";/* DeathRecipient, not this classification, remains the death witness. */}
            catch(Exception error){CpuDiagnostics.Failure failure=CpuDiagnostics.failure("CPU_STOP_FAILED","STOP",error);outcome=failure.code;StageLog.event("CPU_STOP_DIAGNOSIS","task="+task+" code="+failure.code+" category="+failure.category+" original_type="+failure.originalType);}
            finally{lifecycle.callFinished();stopping.stopFinished(outcome,ack);lifecycle.stopFinished(outcome,ack);StageLog.event("CPU_STOP_RESULT","task="+task+" epoch="+epoch+" generation="+stopping.serial+" outcome="+outcome+" ack="+ack);}
        });}catch(RejectedExecutionException error){stopping.stopFinished("QUEUE_REJECTED",false);lifecycle.stopFinished("QUEUE_REJECTED",false);StageLog.event("CPU_STOP_QUEUE_REJECTED","task="+task);}
    }
    private void stopRejected(WorkerGenerations.Worker worker){
        if(worker.primary){sendStop();return;}
        if(!worker.queueStop())return;
        lifecycle.callStarted();try{RETIRE.execute(()->{String outcome="UNPROVEN";try{
            hello(worker);Parcel p=request(CpuProtocol.WORKER),a=Parcel.obtain();try{taskHeader(p);
                if(!((IBinder)worker.key).transact(CpuProtocol.STOP,p,a,0))throw new IOException("CPU_ORPHAN_STOP_REJECTED");acknowledgement(a);if(a.readInt()!=1)throw new IOException("CPU_STOP_NOT_GRANTED");CpuProtocol.end(a);outcome="ACKED_WAIT_DEATH";
            }finally{p.recycle();a.recycle();}
        }catch(Exception error){StageLog.failure("CPU_ORPHAN_STOP_UNPROVEN",error);}
        finally{worker.stopFinished(outcome,outcome.equals("ACKED_WAIT_DEATH"));lifecycle.callFinished();StageLog.event("CPU_ORPHAN_STOP","task="+task+" generation="+worker.serial+" pid="+worker.pid+" uid="+worker.uid+" outcome="+outcome);}});}
        catch(RejectedExecutionException error){worker.stopFinished("QUEUE_REJECTED",false);lifecycle.callFinished();StageLog.failure("CPU_ORPHAN_QUEUE_QUARANTINED",error);}
    }
    public void cancel(){workers.terminate();revoke();IOException cancelled=new IOException("CPU_CANCELLED");if(!finished.isDone())lifecycle.firstFailure("CPU_CANCELLED","CANCEL");finished.completeExceptionally(cancelled);firstFrame.completeExceptionally(cancelled);if(stopRequested.compareAndSet(false,true))sendStop();requestBindingRevocation();for(WorkerGenerations.Worker worker:workers.snapshot())if(!worker.primary)stopRejected(worker);}
    private void command(int code)throws Exception {rpc(code==CpuProtocol.RESUME?"RESUME":"SELF_SEGV",()->{Parcel p=request(CpuProtocol.WORKER),a=Parcel.obtain();try{taskHeader(p);if(!remote.transact(code,p,a,0))throw new IOException("CPU_COMMAND_REJECTED");acknowledgement(a);CpuProtocol.end(a);return null;}finally{p.recycle();a.recycle();}},3000);}
    public void resume()throws Exception {command(CpuProtocol.RESUME);}
    /** Debug counterexample only; production sendStop above is always synchronous. */
    public void probeOnewayStopDenied()throws Exception {rpc("NEGATIVE_ONEWAY_STOP",()->{Parcel p=request(CpuProtocol.WORKER);try{taskHeader(p);remote.transact(CpuProtocol.STOP,p,null,IBinder.FLAG_ONEWAY);return null;}finally{p.recycle();}},3000);}
    public int controlOnewayRejections()throws Exception {return rpc("QUERY_CONTROL",()->{Parcel p=request(CpuProtocol.WORKER),a=Parcel.obtain();try{taskHeader(p);if(!remote.transact(CpuProtocol.QUERY_CONTROL,p,a,0))throw new IOException("CPU_CONTROL_QUERY_REJECTED");acknowledgement(a);int count=a.readInt();CpuProtocol.end(a);if(count<0)throw new IOException("CPU_CONTROL_QUERY_PROTOCOL");return count;}finally{p.recycle();a.recycle();}},1000);}
    public void probeWrongStopEpochDenied()throws Exception {rpc("NEGATIVE_STOP_EPOCH",()->{Parcel p=request(CpuProtocol.WORKER),a=Parcel.obtain();try{p.writeString(task);p.writeLong(epoch^1);if(!remote.transact(CpuProtocol.STOP,p,a,0))throw new IOException("CPU_STOP_REJECTED");acknowledgement(a);throw new IOException("CPU_INVALID_STOP_ACCEPTED");}finally{p.recycle();a.recycle();}},3000);}
    public void releaseStopStall()throws Exception {rpc("RECOVERY_RELEASE",()->{Parcel p=request(CpuProtocol.WORKER),a=Parcel.obtain();try{taskHeader(p);if(!remote.transact(CpuProtocol.RELEASE_STOP_STALL,p,a,0))throw new IOException("CPU_STOP_STALL_RELEASE_REJECTED");acknowledgement(a);CpuProtocol.end(a);return null;}finally{p.recycle();a.recycle();}},3000);}
    public void selfSegv()throws Exception {try{command(CpuProtocol.SELF_SEGV);}catch(CpuDiagnostics.Failure error){if(!error.category.equals("PEER_DEAD"))throw error;}}
    public Frame awaitFrame(long ms)throws Exception {return firstFrame.get(ms,TimeUnit.MILLISECONDS);}
    public Frame awaitResult(long ms)throws Exception {return finished.get(ms,TimeUnit.MILLISECONDS);}
    public int awaitArmed(long ms)throws Exception {return armed.get(ms,TimeUnit.MILLISECONDS);}
    public boolean awaitDeath(long ms)throws InterruptedException {try{death.get(ms,TimeUnit.MILLISECONDS);return true;}catch(ExecutionException|TimeoutException error){return false;}}
    public boolean awaitSourceReleased(long ms)throws InterruptedException {return leases.awaitReleased(generation,ms);}
    public boolean stopAndAwait(long ms)throws InterruptedException {
        if(Looper.myLooper()==Looper.getMainLooper())throw new IllegalStateException("CPU_CLEANUP_MAIN_THREAD");
        if(ms<1 || ms>15000)throw new IllegalArgumentException("CPU_CLEANUP_BUDGET");
        cancel();long stop=System.nanoTime()+TimeUnit.MILLISECONDS.toNanos(ms);
        do{if(releaseIfProven())break;Thread.sleep(Math.min(20,Math.max(1,TimeUnit.NANOSECONDS.toMillis(stop-System.nanoTime()))));}while(System.nanoTime()<stop);
        logLedger();return releasedSlot.get();
    }
    private synchronized boolean releaseIfProven(){
        synchronized(workers){
        lifecycle.sourceReleased(leases.query(generation).released());
        if(releasedSlot.get())return true;
        if(!debugBindings.isEmpty())return false;
        if(lifecycle.snapshot().noWorkerProven() && !workers.snapshot().isEmpty())return false;
        if(!lifecycle.snapshot().noWorkerProven()){
            if(!workers.allDead())return false;
            if(!workers.closed() || !bindingRevocation.snapshot().closed)return false;
            if(!workers.canRelease())return false;
            if(workers.primary()==null)lifecycle.death(); // All registered workers actually died; never a timeout or unbind inference.
        }
        if(!lifecycle.snapshot().canRelease())return false;
        if(lifecycle.releaseSlot() && releasedSlot.compareAndSet(false,true)){runtime.close();OWNERS.remove(this);SLOTS.release();}return releasedSlot.get();
        }
    }
    public CpuLifecycle.Snapshot lifecycle(){lifecycle.sourceReleased(leases.query(generation).released());return lifecycle.snapshot();}
    public boolean recover(long ms,boolean retrySourceClose)throws Exception {
        if(Looper.myLooper()==Looper.getMainLooper())throw new IllegalStateException("CPU_RECOVERY_MAIN_THREAD");
        if(ms<1 || ms>15000)throw new IllegalArgumentException("CPU_RECOVERY_BUDGET");
        revoke();stopRequested.set(true);
        if(retrySourceClose && source.closeState()==AsyncReadBridge.CloseState.FAILED)source.retryFailedClose();
        if(!lifecycle.snapshot().actualDeath)sendStop();requestBindingRevocation();queueBindingRevocation();for(WorkerGenerations.Worker worker:workers.snapshot())if(!worker.primary)stopRejected(worker);return stopAndAwait(ms);
    }
    public static int recoverRetainedTasks(long budgetMs,boolean retrySourceClose)throws Exception {
        if(budgetMs<1 || budgetMs>15000)throw new IllegalArgumentException("CPU_RECOVERY_BUDGET");
        long stop=System.nanoTime()+TimeUnit.MILLISECONDS.toNanos(budgetMs);int released=0;
        for(CpuTaskClient task:OWNERS){if(task.recover(Math.max(1,TimeUnit.NANOSECONDS.toMillis(stop-System.nanoTime())),retrySourceClose))released++;if(System.nanoTime()>=stop)break;}return released;
    }
    public void logLedger(){
        CpuLifecycle.Snapshot s=lifecycle();LeaseRegistry.Snapshot source=sourceLedger();
        logBindingRevocation();
        for(WorkerGenerations.Worker worker:workers.snapshot())StageLog.event("CPU_GENERATION_LEDGER","task="+task+" epoch="+epoch+" generation="+worker.serial+" pid="+worker.pid+" uid="+worker.uid+" primary="+worker.primary+" actual_death="+worker.dead()+" hello="+worker.hello()+" stop_attempts="+worker.stopAttempts()+" stop_pending="+worker.stopPending()+" stop_ack="+worker.stopAck()+" stop_result="+worker.stopResult());
        StageLog.event("CPU_BINDING_LEDGER","task="+task+" epoch="+epoch+" binding_closed="+workers.closed()+" unresolved_workers="+unprovenWorkerCount()+" rejected_workers="+workers.rejected()+" global_unproven_workers="+globalUnprovenWorkers()+" reserved_cpu_slots="+reservedCpuSlots());
        StageLog.event("CPU_LEDGER","task="+task+" epoch="+epoch+" pid="+pid+" uid="+uid+" binding="+s.binding+" identity="+s.identity+" start_ack="+s.startAck+" stop_attempts="+s.stopAttempts+" stop_ack="+s.stopAck+" stop_pending="+s.stopPending+" stop_result="+s.stopResult+" pending_calls="+s.pendingCalls+" actual_death="+s.actualDeath+" no_worker_proven="+s.noWorkerProven()+" source_released="+s.sourceReleased+" slot_released="+s.slotReleased+" operations="+source.operations+" consumers="+source.consumers+" failed_closes="+source.failedCloses+" source_close="+this.source.closeState()+" frame_count="+(frame==null?0:1)+" native_stage="+nativeStage+" first_code="+s.firstCode+" first_phase="+s.firstPhase);
    }
    public LeaseRegistry.Snapshot sourceLedger(){return leases.query(generation);}
    public int workerPid(){return pid;}public int workerUid(){return uid;}public long bindStartedAt(){return startedAt;}
    public String workerProcess(){return primaryProcess;}
    public int unresolvedWorkers(){return workers.unresolved();}
    public BindingRevocation.Snapshot bindingRevocation(){return bindingRevocation.snapshot();}
    public int registrationCount(int result){return result>=0 && result<registrationCounts.length()?registrationCounts.get(result):0;}
    int debugRegistrarHostIdentity(){Parcel p=request(CpuProtocol.WORKER+".registration"),a=Parcel.obtain();try{taskHeader(p);p.writeStrongBinder(new Binder());registrar.transact(RegistrationProtocol.REGISTER,p,a,0);try{return RegistrationProtocol.validateReply(a.dataSize(),a.readInt(),a.readInt(),a.readInt(),a.readInt());}catch(RegistrationProtocol.Rejected rejected){return rejected.code;}}catch(RemoteException error){throw new AssertionError(error);}finally{p.recycle();a.recycle();}}
    private int unprovenWorkerCount(){int count=workers.unresolved();if(!lifecycle.snapshot().noWorkerProven() && (workers.snapshot().isEmpty() || (!workers.closed() && workers.terminal())))count++;return count;}
    public static int globalUnprovenWorkers(){int count=0;for(CpuTaskClient task:OWNERS)count+=task.unprovenWorkerCount();return count;}
    public static int reservedCpuSlots(){return 2-SLOTS.availablePermits();}
    private volatile String primaryProcess;
    void debugDuplicateConnection(){connection.onServiceConnected(new ComponentName(context,CpuIsolatedService.class),remote);}
    void debugReplayDeadPrimary(){WorkerGenerations.Worker worker=workers.primary();if(worker==null || !worker.dead())throw new IllegalStateException("CPU_NO_REAL_DEATH_TO_REPLAY");observeDeath(worker);}
    /** Real isolated Binder counterexample. No START, broker, source token or decoding allocation is sent. */
    final class DebugExtraBinding implements AutoCloseable {
        final CompletableFuture<WorkerGenerations.Worker> ready=new CompletableFuture<>();boolean acceptedBind;
        final ServiceConnection extra=new ServiceConnection(){
            public void onServiceConnected(ComponentName name,IBinder endpoint){WorkerGenerations.Worker worker=workers.find(endpoint);if(worker==null)ready.completeExceptionally(new IOException("CPU_EXTRA_UNREGISTERED"));else{stopRejected(worker);ready.complete(worker);}}
            public void onServiceDisconnected(ComponentName name){}
        };
        WorkerGenerations.Worker await(long ms)throws Exception{WorkerGenerations.Worker worker=ready.get(ms,TimeUnit.MILLISECONDS);long deadline=System.nanoTime()+TimeUnit.MILLISECONDS.toNanos(ms);while(!worker.hello()){if(worker.dead() || System.nanoTime()>=deadline)throw new IOException("CPU_EXTRA_HELLO_UNPROVEN");Thread.sleep(10);}return worker;}
        void releaseStall()throws Exception {WorkerGenerations.Worker worker=await(3000);Parcel p=request(CpuProtocol.WORKER),a=Parcel.obtain();try{taskHeader(p);if(!((IBinder)worker.key).transact(CpuProtocol.RELEASE_STOP_STALL,p,a,0))throw new IOException("CPU_EXTRA_RELEASE");acknowledgement(a);CpuProtocol.end(a);}finally{p.recycle();a.recycle();}}
        @Override public void close(){if(acceptedBind){context.unbindService(extra);acceptedBind=false;}debugBindings.remove(this);}
    }
    DebugExtraBinding debugExtraWorker(boolean stall)throws Exception {
        if(releasedSlot.get() || workers.primary()==null)throw new IOException("CPU_DEBUG_EXTRA_STATE");
        DebugExtraBinding extra=new DebugExtraBinding();debugBindings.add(extra);lifecycle.callStarted();
        try{Bundle registration=new Bundle();registration.putBinder("registrar",registrar);registration.putString("task",task);registration.putLong("epoch",epoch);registration.putBoolean("debug_stop_stall",stall);Intent intent=new Intent(context,CpuIsolatedService.class).putExtra("c14_registration",registration);
            extra.acceptedBind=context.bindIsolatedService(intent,Context.BIND_AUTO_CREATE,"extra_"+task,callbackExecutor,extra.extra);if(!extra.acceptedBind){debugBindings.remove(extra);throw new IOException("CPU_EXTRA_BIND_REJECTED");}return extra;
        }finally{lifecycle.callFinished();}
    }
    public int rejections(){return rejections.get();}public long brokerBytes(){return readBytes.get();}
    public int nativeStage(){return nativeStage;}
    public boolean budgetApplied(){return budgetAccepted;}
    public boolean quotaProbeProved(){return quotaProved;}
    @Override public void close(){cancel();logLedger();/* no unbind/await on a possible UI caller; explicit off-main stopAndAwait/recover proves release */}
}
