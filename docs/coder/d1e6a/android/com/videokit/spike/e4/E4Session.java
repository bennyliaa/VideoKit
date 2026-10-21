package com.videokit.spike.e4;

import android.app.ActivityManager;
import android.app.ApplicationExitInfo;
import android.content.*;
import android.os.*;
import android.system.Os;
import android.system.OsConstants;
import com.videokit.spike.c14.*;
import java.io.*;
import java.nio.file.*;
import java.security.SecureRandom;
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.*;

/** Host control/broker only. Frames never cross Flutter/Dart; host never parses compressed media. */
public final class E4Session implements AutoCloseable {
    private static final Semaphore ENCODER_OUTPUT=new Semaphore(1);
    private static final Set<E4Session> OWNERS=ConcurrentHashMap.newKeySet();
    private static final AtomicLong GENERATION=new AtomicLong();
    private static final ThreadPoolExecutor CONTROL=new ThreadPoolExecutor(1,1,0,TimeUnit.MILLISECONDS,new ArrayBlockingQueue<>(2),r->{Thread t=new Thread(r,"e4-control");t.setDaemon(true);return t;},new ThreadPoolExecutor.AbortPolicy());
    private final ThreadPoolExecutor owner=new ThreadPoolExecutor(1,1,0,TimeUnit.MILLISECONDS,new ArrayBlockingQueue<>(2),r->{Thread t=new Thread(r,"e4-host-owner");t.setDaemon(true);return t;},new ThreadPoolExecutor.AbortPolicy());
    public final String task=UUID.randomUUID().toString().replace("-","");
    public final long epoch=Math.max(1,new SecureRandom().nextLong()&Long.MAX_VALUE);
    private final Context context;private final AsyncReadBridge.Provider provider;private final int kind;private final String fault,batch,budgetIdentity;
    private final AtomicBoolean started=new AtomicBoolean(),cancelled=new AtomicBoolean(),dead=new AtomicBoolean();
    private final AtomicReference<String> first=new AtomicReference<>();
    private final AtomicReference<IBinder> original=new AtomicReference<>();
    private final E6ADiagnosticState nativeDiagnostics=new E6ADiagnosticState();
    private final E5Trace trace=new E5Trace();private volatile String cleanupError="",callbackRejectReason="";private volatile int callbackFlags,callbackCallerPid,callbackCallerUid;
    private final E4ReturnGate control=new E4ReturnGate();private volatile boolean controlUnknown;
    private final CompletableFuture<IBinder> connected=new CompletableFuture<>();
    private static final ScheduledThreadPoolExecutor TIMER=new ScheduledThreadPoolExecutor(2,r->{Thread t=new Thread(r,"e5a-terminal-clock");t.setDaemon(true);return t;});
    static {TIMER.setRemoveOnCancelPolicy(true);}
    private final E5ALifecycle<Report> lifecycle;private final CompletableFuture<Report> result;
    private final E4Broker broker=new E4Broker();private volatile E4Protocol.Identity identity;
    private volatile E4CpuAdapter source;private volatile Sink sink;
    private E4Broker.ResourceLease sourceLease,sinkLease;
    private final Object events=new Object();private volatile Bundle last=new Bundle(),terminal;
    private volatile boolean serviceStarted,startedSignal,bound,bindReturned,bindingUnknown,slot,ownerFinished,ready,ownerClosed;
    private volatile int servicePid=-1,callbacks,callbackInFlight,callbackRejected,inputs,outputs,received,consumed;
    private volatile long bindAt;private volatile String token="";private volatile Bundle exitEvidence=new Bundle();
    private final List<IBinder> rejectedConnections=new CopyOnWriteArrayList<>();
    private final long[] timeline=new long[6];private final List<byte[]> thumbs=new ArrayList<>();
    private final ServiceConnection connection=new ServiceConnection(){
        public void onServiceConnected(ComponentName name,IBinder endpoint){
            if(original.compareAndSet(null,endpoint))connected.complete(endpoint);
            else if(original.get()!=endpoint){if(rejectedConnections.size()<2)rejectedConnections.add(endpoint);first.compareAndSet(null,"E4_EXTRA_CONNECTION_UNKNOWN");}
        }
        public void onServiceDisconnected(ComponentName name){/* Only original linkToDeath proves original endpoint death. */}
        public void onBindingDied(ComponentName name){first.compareAndSet(null,"E4_BINDING_DIED");synchronized(events){events.notifyAll();}}
        public void onNullBinding(ComponentName name){connected.completeExceptionally(new IOException("E4_NULL_BINDING"));}
    };
    private final Binder callback=new Binder(){
        @Override protected boolean onTransact(int code,Parcel data,Parcel reply,int flags)throws RemoteException{
            if(code==INTERFACE_TRANSACTION){if(reply!=null)reply.writeString(E4CodecWire.CALLBACK);return true;}
            int uid=Binder.getCallingUid(),pid=Binder.getCallingPid();callbackFlags=flags;callbackCallerPid=pid;callbackCallerUid=uid;
            synchronized(events){callbackInFlight++;}
            try{
                if(code!=1 || !E5CallbackGate.synchronous(flags) || reply==null || data.dataSize()>16384)throw new SecurityException("E4_CALLBACK_PROTOCOL");
                data.enforceInterface(E4CodecWire.CALLBACK);Bundle event=data.readBundle(E4CodecWire.class.getClassLoader());
                E4Protocol.Identity expected=identity;
                if(event==null || data.dataAvail()!=0 || expected==null || dead.get() || uid!=expected.serviceUid || pid!=servicePid || !expected.matches(E4CodecWire.identity(event)))throw new SecurityException("E4_CALLBACK_ORIGINAL_IDENTITY");
                synchronized(events){
                    if(++callbacks>128)throw new SecurityException("E4_CALLBACK_BUDGET");
                    last=new Bundle(event);inputs=Math.max(inputs,event.getInt("inputs"));outputs=Math.max(outputs,event.getInt("outputs"));
                    String status=event.getString("status","");
                    if(status.equals("STARTED"))startedSignal=true;
                    if(status.equals("FRAME_CONSUMED") && event.getInt("inFlight",-1)==0 && event.getInt("nativeCalls",-1)==0)consumed=Math.max(consumed,event.getInt("inputs"));
                    if(Set.of("CAPABILITY_BLOCKED","FAILED","PENDING","CANCELLED","ENCODED_AWAITING_ISOLATED_VALIDATION").contains(status))terminal=new Bundle(event);
                    events.notifyAll();
                }
                reply.writeNoException();reply.writeInt(0x45344342);reply.writeInt(android.os.Process.myUid());reply.writeString(expected.serviceInstance);
            }catch(Exception rejected){callbackRejectReason=safe(rejected);trace.failure(callbackRejectReason);first.compareAndSet(null,"E5_CALLBACK_REJECTED");synchronized(events){callbackRejected++;events.notifyAll();}if(reply!=null)reply.writeException(new SecurityException("E4_CALLBACK_REJECTED"));}
            finally{synchronized(events){callbackInFlight--;events.notifyAll();}}
            return true;
        }
    };
    public E4Session(Context context,AsyncReadBridge.Provider source,int kind,String debugFault,String batch,String budgetIdentity){
        this.context=context.getApplicationContext();provider=Objects.requireNonNull(source);this.kind=kind;fault=debugFault==null?"":debugFault;this.batch=Objects.requireNonNull(batch);this.budgetIdentity=Objects.requireNonNull(budgetIdentity);if(!batch.matches("D1-E4A-[A-Za-z0-9-]{8,80}") || !budgetIdentity.matches("[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}"))throw new IllegalArgumentException("E4A_FORMAL_BUDGET_IDENTITY_REQUIRED");
        lifecycle=new E5ALifecycle<>(owner,(delay,task)->{ScheduledFuture<?> f=TIMER.schedule(task,delay,TimeUnit.NANOSECONDS);return ()->f.cancel(false);},System::nanoTime,this::released,this::report,this::onCancellation);result=lifecycle.future();
    }
    public CompletableFuture<Report> start(){
        if(!started.compareAndSet(false,true))throw new IllegalStateException("E4_SESSION_SINGLE_START");
        OWNERS.add(this);lifecycle.start();try{owner.execute(this::run);}catch(RuntimeException error){first.compareAndSet(null,"E4_HOST_QUEUE_REJECTED");lifecycle.cancel(first.get());lifecycle.initialReturned(false,()->{},this::finalOwnerReturn);}return result.thenApply(value->value);
    }
    private Bundle call(int code,Bundle data)throws Exception{IBinder endpoint=original.get();if(endpoint==null)throw new IOException("E4_NOT_READY");trace.event("CONTROL_ENTER","code="+code);try{return E4CodecWire.call(endpoint,code,data);}finally{trace.event("CONTROL_RETURN","code="+code);}}
    private Bundle request(){return E4CodecWire.identity(identity);}
    private void check()throws IOException{
        if(dead.get())throw new IOException("WORKER_DIED");if(cancelled.get())throw new IOException("E4_CANCELLED");
        if(first.get()!=null)throw new IOException(first.get());
    }
    private void waitFor(java.util.function.BooleanSupplier condition,long milliseconds)throws Exception{
        long stop=System.nanoTime()+TimeUnit.MILLISECONDS.toNanos(milliseconds);
        synchronized(events){while(!condition.getAsBoolean()){
            check();Bundle end=terminal;if(end!=null && !"ENCODED_AWAITING_ISOLATED_VALIDATION".equals(end.getString("status")))throw new IOException(end.getString("error",end.getString("status","E4_REMOTE_FAILED")));
            long left=stop-System.nanoTime();if(left<=0)throw new IOException("E4_REMOTE_PENDING");TimeUnit.NANOSECONDS.timedWait(events,Math.min(left,50000000));
        }}
    }
    private void observeDeath(IBinder endpoint,E4Protocol.Identity pinned){
        if(original.get()!=endpoint || identity==null || !identity.matches(pinned))return;
        dead.set(true);first.compareAndSet(null,"WORKER_DIED");try{broker.workerDied(pinned.serviceInstance);}catch(IOException ignored){}
        E4CpuAdapter cpu=source;if(cpu!=null)cpu.cancel();synchronized(events){events.notifyAll();}
    }
    private void bind()throws Exception{
        bindAt=System.currentTimeMillis();boolean entered=false;
        try{entered=true;bound=context.bindService(new Intent(context,E4CodecService.class),connection,Context.BIND_AUTO_CREATE);bindReturned=true;}
        catch(RuntimeException failure){bindingUnknown=entered;throw failure;}
        if(!bound)throw new IOException("E4_PROCESS_NOT_READY");IBinder endpoint=connected.get(5000,TimeUnit.MILLISECONDS);
        Bundle hello=E4CodecWire.call(endpoint,E4CodecWire.HELLO,new Bundle());
        long readyDeadline=System.nanoTime()+TimeUnit.SECONDS.toNanos(5);
        for(int polls=1;!hello.getBoolean("ownerReady") && "NOT_READY".equals(hello.getString("status")) && polls<51 && System.nanoTime()<readyDeadline;polls++){
            check();Thread.sleep(100);hello=E4CodecWire.call(endpoint,E4CodecWire.HELLO,new Bundle());
        }
        if(!hello.getBoolean("ownerReady") || !"OWNER_READY".equals(hello.getString("status")))throw new IOException("E4_PROCESS_NOT_READY");
        servicePid=hello.getInt("pid");int uid=hello.getInt("uid");
        if(servicePid<=0 || servicePid==android.os.Process.myPid() || uid!=android.os.Process.myUid())throw new IOException("E4_CODEC_CRASH_BOUNDARY_IDENTITY");
        identity=new E4Protocol.Identity(task,epoch,GENERATION.incrementAndGet(),hello.getString("serviceInstance"),android.os.Process.myUid(),uid);
        E4Protocol.Identity pinned=identity;endpoint.linkToDeath(()->observeDeath(endpoint,pinned),0);
        broker.createHost(identity,true);
    }
    private void run(){
        long runStart=System.nanoTime();
        try{
            if(E5N2Recovery.retainedOperations()!=0 || E5AFinalObservation.retained()!=0)throw new IOException("E5_N2_RECOVERY_OWNER_OR_DURABILITY_PENDING");
            if(!ENCODER_OUTPUT.tryAcquire())throw new IOException("E4_ENCODER_OUTPUT_BUSY_OR_QUARANTINED");slot=true;
            check();bind();check();
            source=new E4CpuAdapter(context,provider,kind);sourceLease=broker.registerResource(identity,E4Broker.ResourceKind.SOURCE,source,source::close);
            sink=new Sink();sinkLease=broker.registerResource(identity,E4Broker.ResourceKind.SINK,sink,sink::closeTransferHandles);sink.open(context,batch,budgetIdentity,identity);
            if(!fault.isEmpty()){Bundle debug=request();debug.putString("fault",fault);Bundle armed=call(E4CodecWire.DEBUG,debug);if(!"DEBUG_PLAN_ARMED".equals(armed.getString("status")))throw new IOException("E4_DEBUG_PLAN_REJECTED");}
            Bundle begin=request();begin.putBinder("callback",callback);begin.putParcelable("sink",sink.output);begin.putParcelable("lease",sink.lease);begin.putString("leaseEpoch",sink.leaseEpoch);
            sink.transferAttempted=true;Bundle admission=call(E4CodecWire.BEGIN,begin);
            sink.descriptorAdopted=admission.getBoolean("descriptorAdopted");
            sink.rejectedTransferClosed=admission.getBoolean("rejectedGrantCloseProven");
            sinkLease.close();
            if(!"ADMITTED".equals(admission.getString("status")))throw new IOException(admission.getString("error","E4_NOT_ADMITTED"));
            awaitStarted(15000);broker.serviceReady(identity.serviceUid,identity,true);
            long firstPts=-1;
            for(int sequence=1;sequence<=6;sequence++){
                check();if(System.nanoTime()-runStart>TimeUnit.SECONDS.toNanos(60))throw new IOException("E4_TOTAL_DEADLINE_PENDING");
                nativeDiagnostics.sourceEnter();E4CpuAdapter.Sample sample=source.next(sequence);nativeDiagnostics.sourceSuccess(sample.sourceTask,sample.nativeDiagnostic);received++;
                if(firstPts<0)firstPts=sample.ptsUs;long pts=sample.ptsUs-firstPts;
                E4Protocol.Frame frame=new E4Protocol.Frame(identity,sequence,pts,sample.rgba);timeline[sequence-1]=pts;thumbs.add(sample.thumb);
                Bundle data=request();data.putInt("sequence",sequence);data.putLong("ptsUs",pts);data.putInt("width",256);data.putInt("height",144);data.putInt("stride",1024);data.putInt("rotation",0);data.putByteArray("rgba",frame.pixels());
                Bundle ack=call(E4CodecWire.FRAME,data);if(!"FRAME_ACCEPTED".equals(ack.getString("status")) || ack.getInt("sequence")!=sequence)throw new IOException("E4_FRAME_NOT_ADMITTED");
                broker.forwardedFrame(identity.hostUid,identity,frame);final int wanted=sequence;waitFor(()->consumed>=wanted,10000);
            }
            sourceLease.close();broker.endFrames(identity.hostUid,identity);call(E4CodecWire.FINISH,request());
            waitFor(()->terminal!=null && "ENCODED_AWAITING_ISOLATED_VALIDATION".equals(terminal.getString("status")),15000);
            Bundle closed=awaitRemoteClosure(21);
            if(!closed.getBoolean("fsynced") || !closed.getBoolean("framesReleased") || !closed.getBoolean("leaseReleased") || closed.getInt("nativeCalls")!=0 || closed.getBoolean("imageHeld") || closed.getBoolean("creating"))throw new IOException("E4_REMOTE_CLOSE_UNPROVEN");
            if(!sink.task.workerLeaseClear())throw new IOException("E4_ORIGINAL_WORKER_LEASE_BUSY");
            broker.remoteOutputClosed(identity.serviceUid,identity,closed.getInt("outputs"),closed.getInt("liveResources"),closed.getInt("unknownResources"),closed.getBoolean("sinkReleased"),closed.getBoolean("encoderReleased"),closed.getLong("bytes"));
            E4Protocol.timeline(timeline);String before=sink.digest();long bytes=Files.size(sink.task.authorizedOutput());
            nativeDiagnostics.validatorEnter();E4CpuAdapter.Verification verification=E4CpuAdapter.validate(context,HostFixtures.file(sink.task.authorizedOutput()),timeline,thumbs,before,bytes,sink::digest);
            nativeDiagnostics.validatorSuccess(verification.task,verification.nativeDiagnostic);
            if(verification.pid<=0 || verification.uid==identity.hostUid || !verification.fullEof || !verification.sourceClosed || !verification.originalDeath || !verification.slotReleased || !before.equals(verification.sha))throw new IOException("E4_ISOLATED_VALIDATION_UNPROVEN");
            check();broker.authorizeValidator(identity.hostUid,identity,verification.uid);broker.validatedOutput(verification.uid,identity,verification.frames,timeline,true);
            if(System.nanoTime()-runStart>TimeUnit.SECONDS.toNanos(60))throw new IOException("E4_TOTAL_DEADLINE_PENDING");
            token=sink.task.ready(sink.leaseEpoch,true);sink.closeOwner();ownerClosed=true;ready=true;
        }catch(Throwable error){
            nativeDiagnostics.failure(error);trace.event("E6A_DIAGNOSTIC_FAILURE",safe(error));
            first.compareAndSet(null,safe(error));trace.failure(first.get());}
        finally{
            if(!ready){
                markCancelled();if(source!=null)source.cancel();
                if(identity!=null)try{broker.cancel(identity.hostUid,identity);}catch(Exception ignored){}
                advanceCleanup(101);
            }
            thumbs.clear();
            lifecycle.initialReturned(ready,this::continueOriginalCleanup,this::finalOwnerReturn);
        }
    }
    private void finalOwnerReturn(){
        if(dead.get())collectExit();
        if(bound && bindReturned)try{context.unbindService(connection);bound=false;}catch(RuntimeException unknown){bindingUnknown=true;}
        ownerFinished=true;control.ownerReturned();finishOwnership();tryRelease();trace.event("FINAL_ORIGINAL_OWNER_RETURN",cleanupError);
    }
    private void markCancelled(){lifecycle.cancel(first.get()==null?"E4_CANCELLED":first.get());}
    private void awaitStarted(long milliseconds)throws Exception{
        long deadline=System.nanoTime()+TimeUnit.MILLISECONDS.toNanos(milliseconds);
        for(int polls=0;polls<301 && System.nanoTime()<deadline;polls++){
            check();Bundle q=call(E4CodecWire.QUERY,request());last=q;
            if(!identity.matches(E4CodecWire.identity(q)) || q.getInt("pid")!=servicePid || q.getInt("uid")!=identity.serviceUid)throw new IOException("E5_REMOTE_SNAPSHOT_IDENTITY");
            trace.event("START_QUERY",q.getString("stage",q.getString("phase","UNKNOWN")));
            if(startedSignal && callbackInFlight==0 && q.getBoolean("startProven") && q.getBoolean("startAckReturned") && q.getBoolean("ownerOpenReturned") && !q.getBoolean("callbackAckFailed") && q.getInt("callbackInFlight",-1)==0){serviceStarted=true;return;}
            if(q.getBoolean("callbackAckFailed"))throw new IOException("E5_CALLBACK_ACK_FAILED");
            if(q.getBoolean("ownerOpenReturned") && !q.getString("firstError","").isEmpty())throw new IOException(q.getString("firstError"));
            if(terminal!=null && !"ENCODED_AWAITING_ISOLATED_VALIDATION".equals(terminal.getString("status")))throw new IOException(terminal.getString("firstError",terminal.getString("error","E5_REMOTE_START_FAILED")));
            Thread.sleep(50);
        }
        throw new IOException("E4_REMOTE_PENDING");
    }
    private void advanceCleanup(int queries){
        if(original.get()!=null && identity!=null && !dead.get())try{last=call(E4CodecWire.CANCEL,request());last=awaitRemoteClosure(queries);}catch(Exception failure){cleanupError=safe(failure);trace.event("CLEANUP_PENDING",cleanupError);}
        if(sourceLease!=null && sourceLease.state()==E4Broker.CloseState.OPEN)try{sourceLease.close();}catch(Exception pending){cleanupError=safe(pending);}
        if(sinkLease!=null && sinkLease.state()==E4Broker.CloseState.OPEN)try{sinkLease.close();}catch(Exception pending){cleanupError=safe(pending);}
        if(sink!=null && sink.task!=null && !sink.opening && (dead.get() || !sink.transferAttempted || sink.rejectedTransferClosed || remoteClosed(last)))try{
            if(sink.task.workerLeaseClear()){sink.task.abortRetaining();sink.closeOwner();ownerClosed=true;trace.event("ABORT_OWNER_RETURNED","");}
        }catch(Exception unknown){cleanupError=safe(unknown);trace.event("ABORT_PENDING",cleanupError);}
    }
    private void continueOriginalCleanup(){
        trace.event("ORIGINAL_CLEANUP_CONTINUATION","");
        try{if(!ready && !ownerClosed && !controlUnknown)advanceCleanup(601);}
        finally{trace.event("CLEANUP_CONTINUATION_RETURN",cleanupError);}
    }
    private Bundle awaitRemoteClosure(int maximumQueries)throws Exception{
        Bundle proof=null;
        for(int count=0;count<maximumQueries;count++){
            if(dead.get())throw new IOException("WORKER_DIED");
            if(lifecycle.cancelDeadline()!=0 && System.nanoTime()>=lifecycle.cancelDeadline())throw new IOException("E5_ORIGINAL_CANCEL_DEADLINE_PENDING");
            proof=call(E4CodecWire.QUERY,request());last=proof;
            if(remoteClosed(proof))return proof;
            if(proof.getBoolean("callbackUnknown"))throw new IOException("E4_CALLBACK_RETURN_UNKNOWN");
            Thread.sleep(50);
        }
        throw new IOException("E4_REMOTE_CLOSE_PENDING");
    }
    private static boolean remoteClosed(Bundle value){return value!=null && value.getBoolean("encoderReleased") && value.getBoolean("sinkReleased") && value.getBoolean("leaseReleased") && value.getBoolean("framesReleased") && !value.getBoolean("callbackUnknown",true) && value.getInt("callbackInFlight",-1)==0 && value.getInt("nativeCalls",-1)==0 && value.getInt("liveResources",-1)==0 && value.getInt("unknownResources",-1)==0;}
    private void collectExit(){
        Bundle proof=new Bundle();proof.putString("appCause","WORKER_DIED");proof.putString("signalVerdict","UNKNOWN");proof.putInt("systemReason",-1);proof.putInt("systemStatus",-1);
        try{List<ApplicationExitInfo> records=context.getSystemService(ActivityManager.class).getHistoricalProcessExitReasons(context.getPackageName(),servicePid,8);ApplicationExitInfo match=null;int count=0;
            for(ApplicationExitInfo item:records)if(item.getPid()==servicePid && item.getRealUid()==identity.serviceUid && item.getTimestamp()>=bindAt){match=item;count++;}
            if(count==1){proof.putInt("systemReason",match.getReason());proof.putInt("systemStatus",match.getStatus());proof.putLong("systemTimestamp",match.getTimestamp());proof.putString("signalVerdict",match.getStatus()==0?"UNKNOWN_FAIL_SYSTEM_ZERO":"RAW_SYSTEM_FIELDS_ONLY_NOT_SIGNAL_PROOF");}
        }catch(RuntimeException denied){proof.putString("query","UNAVAILABLE");}exitEvidence=proof;
    }
    private boolean baseReleased(){
        if(!ownerFinished || dead.get() || bound || bindingUnknown || callbackInFlight!=0 || !control.drained() || controlUnknown || !rejectedConnections.isEmpty() || sink!=null && (sink.opening || sink.transferAttempted && !sink.descriptorAdopted && !sink.rejectedTransferClosed))return false;
        if(identity==null)return !slot || source==null && sink==null;
        try{E4Broker.Snapshot s=broker.snapshot(identity);return s.resourcesReleased() && s.state!=E4Broker.State.UNKNOWN && (sink==null || ownerClosed && sink.allReturned()) && (source==null || source.sourceClosed());}catch(IOException unknown){return false;}
    }
    private boolean released(){return baseReleased() && (sink==null || sink.budget!=null && sink.budget.finished());}
    /** Called only by original owner-finally or actual CONTROL-finally, never query and never early. */
    private void finishOwnership(){
        if(!baseReleased() || !control.claimFinish())return;
        try{if(sink!=null)sink.finishBudget(ready?"READY":"ABORTED");}
        catch(Exception unknown){first.compareAndSet(null,"E4A_BUDGET_FINALIZATION_UNKNOWN");}
        tryRelease();
    }
    private synchronized void tryRelease(){if(released()){OWNERS.remove(this);if(slot){slot=false;ENCODER_OUTPUT.release();}owner.shutdown();}}
    private static String safe(Throwable error){return E6FailureCodes.safe(error);}
    public void cancel(){if(started.get())lifecycle.cancel("E4_CANCELLED");}
    private void onCancellation(String reason){
        if(!cancelled.compareAndSet(false,true))return;first.compareAndSet(null,reason);trace.event("FIRST_CANCEL",reason);synchronized(events){events.notifyAll();}
        E4Protocol.Identity id=identity;
        if(id!=null){
            try{control.admit();}catch(IOException alreadyFinished){return;}
            try{CONTROL.execute(()->control.runAdmitted(()->{try{E4CpuAdapter cpu=source;if(cpu!=null)cpu.cancel();if(original.get()!=null && !dead.get())call(E4CodecWire.CANCEL,E4CodecWire.identity(id));}catch(Exception unknown){controlUnknown=true;first.compareAndSet(null,"E4_CANCEL_RETURN_UNKNOWN");}},()->{finishOwnership();tryRelease();lifecycle.resourcesChanged();}));}
            catch(RejectedExecutionException full){control.returned();first.compareAndSet(null,"E4_CONTROL_PENDING");finishOwnership();tryRelease();lifecycle.resourcesChanged();}
        }
    }
    public Report finishForInstrumentation(){
        if(!started.get())return report();if(Looper.myLooper()==Looper.getMainLooper())throw new IllegalStateException("E5A_TERMINAL_WAIT_MAIN_THREAD");return lifecycle.terminalBeforeExit();
    }
    public Report await(long milliseconds)throws Exception{
        if(Looper.myLooper()==Looper.getMainLooper())throw new IOException("E4_AWAIT_MAIN_THREAD");
        try{return result.get(milliseconds,TimeUnit.MILLISECONDS);}catch(TimeoutException pending){return finishForInstrumentation();}
    }
    public Report query(){tryRelease();return report();}
    public Bundle debugOwnService(String operation,String armToken)throws Exception{
        if(Looper.myLooper()==Looper.getMainLooper())throw new IOException("E4_DEBUG_MAIN_THREAD");
        if(!BuildConfig.DEBUG || identity==null)throw new IOException("E4_DEBUG_NOT_READY");
        Bundle request=request();request.putString("fault",operation);if(armToken!=null)request.putString("armToken",armToken);return call(E4CodecWire.DEBUG,request);
    }
    /** Debug metadata-only reconnect. A quarantined old encoder permit is never reused. */
    public Bundle probeReplacementRejectsOldIdentity()throws Exception{
        if(!BuildConfig.DEBUG || Looper.myLooper()==Looper.getMainLooper() || !dead.get() || !ownerFinished || bound)throw new IOException("E4_RECONNECT_REQUIRES_ORIGINAL_DEATH");
        CompletableFuture<IBinder> replacement=new CompletableFuture<>();
        ServiceConnection next=new ServiceConnection(){
            public void onServiceConnected(ComponentName name,IBinder endpoint){replacement.complete(endpoint);}
            public void onServiceDisconnected(ComponentName name){}
        };
        boolean accepted=false;
        try{
            accepted=context.bindService(new Intent(context,E4CodecService.class),next,Context.BIND_AUTO_CREATE);
            if(!accepted)throw new IOException("E4_REPLACEMENT_NOT_READY");IBinder endpoint=replacement.get(5000,TimeUnit.MILLISECONDS);
            Bundle hello=E4CodecWire.call(endpoint,E4CodecWire.HELLO,new Bundle());
            long deadline=System.nanoTime()+TimeUnit.SECONDS.toNanos(5);
            for(int count=1;!hello.getBoolean("ownerReady") && count<51 && System.nanoTime()<deadline;count++){Thread.sleep(100);hello=E4CodecWire.call(endpoint,E4CodecWire.HELLO,new Bundle());}
            if(!hello.getBoolean("ownerReady") || identity.serviceInstance.equals(hello.getString("serviceInstance")) || hello.getInt("uid")!=identity.serviceUid)throw new IOException("E4_REPLACEMENT_IDENTITY");
            E4Protocol.Identity newer=new E4Protocol.Identity(task,epoch,GENERATION.incrementAndGet(),hello.getString("serviceInstance"),identity.hostUid,identity.serviceUid);
            broker.createHost(newer,true);
            Bundle rejected=E4CodecWire.call(endpoint,E4CodecWire.QUERY,E4CodecWire.identity(identity));
            if(!"REJECTED".equals(rejected.getString("status")))throw new IOException("E4_OLD_REMOTE_RESULT_ACCEPTED");
            boolean localRejected=false;try{broker.serviceReady(identity.serviceUid,identity,true);}catch(IOException expected){localRejected="E4_OLD_GENERATION".equals(expected.getMessage());}
            if(!localRejected)throw new IOException("E4_OLD_LOCAL_RESULT_ACCEPTED");
            Bundle proof=new Bundle();proof.putBoolean("oldRemoteIdentityRejected",true);proof.putBoolean("oldLocalGenerationRejected",true);proof.putBoolean("newEncoderStarted",false);proof.putBoolean("oldPermitRetained",slot);proof.putString("newInstance",newer.serviceInstance);return proof;
        }finally{if(accepted)try{context.unbindService(next);}catch(RuntimeException unknown){bindingUnknown=true;throw new IOException("E4_REPLACEMENT_BINDING_CLOSE_UNKNOWN",unknown);}}
    }
    public static int reservedEncoderSlots(){return 1-ENCODER_OUTPUT.availablePermits();}
    public static int retainedSessions(){return OWNERS.size();}
    public static final class Report {
        public final String task,status,error,token,outputTaskId,outputSha256;public final long outputLength;public final int received,inputs,outputs,callbackRejected,controlInFlight;
        public final boolean resourcesReleased,workerDied;public final Bundle remote,systemExit,diagnostics;
        private Report(E4Session s){outputTaskId=s.sink==null || s.sink.task==null?"UNKNOWN":s.sink.task.taskId;outputSha256=s.sink==null?"UNKNOWN":s.sink.outcomeSha;outputLength=s.sink==null?-1:s.sink.outcomeLength;task=s.task;error=s.first.get();resourcesReleased=s.released();workerDied=s.dead.get();
            boolean qualified=s.lifecycle.ownerReturnProven() && !s.lifecycle.terminalReason().equals("ORIGINAL_CANCEL_DEADLINE_PENDING");status=qualified && s.ready && resourcesReleased && error==null && !s.cancelled.get()?"READY":qualified && resourcesReleased?"ABORTED":"PENDING";token=status.equals("READY")?s.token:"";
            received=s.received;inputs=s.inputs;outputs=s.outputs;callbackRejected=s.callbackRejected;controlInFlight=s.control.inFlight();remote=new Bundle(s.last);systemExit=new Bundle(s.exitEvidence);diagnostics=new Bundle();diagnostics.putString("validatorNativeDiagnostic",s.nativeDiagnostics.validator());diagnostics.putString("sourceNativeDiagnostic",s.nativeDiagnostics.source());diagnostics.putString("terminalPhase",s.lifecycle.phase());diagnostics.putString("terminalReason",s.lifecycle.terminalReason());diagnostics.putLong("firstCancelAtNs",s.lifecycle.cancelAt());diagnostics.putLong("cancelDeadlineNs",s.lifecycle.cancelDeadline());diagnostics.putInt("cleanupContinuations",s.lifecycle.continuations());diagnostics.putInt("ownerFinishEntries",s.lifecycle.finishes());diagnostics.putBoolean("originalOwnerReturned",s.lifecycle.ownerReturnProven());diagnostics.putString("hostStage",s.trace.phase());diagnostics.putString("hostStageTail",s.trace.tail());diagnostics.putString("cleanupError",s.cleanupError);diagnostics.putString("callbackRejectReason",s.callbackRejectReason);diagnostics.putInt("callbackFlags",s.callbackFlags);diagnostics.putInt("callbackCallerPid",s.callbackCallerPid);diagnostics.putInt("callbackCallerUid",s.callbackCallerUid);diagnostics.putInt("hostPid",android.os.Process.myPid());diagnostics.putInt("hostUid",android.os.Process.myUid());diagnostics.putInt("codecPid",s.servicePid);diagnostics.putBoolean("startedSignal",s.startedSignal);diagnostics.putBoolean("startProven",s.serviceStarted);
        }
    }
    private Report report(){return new Report(this);}
    public void close(){if(!started.get())return;if(Looper.myLooper()==Looper.getMainLooper()){cancel();return;}finishForInstrumentation();}

    private static final class Sink {
        E4FencedTask task;E4OutputBudget budget;String leaseEpoch;ParcelFileDescriptor output,lease;
        final List<E4Owned<InputStream>> hashOwners=new CopyOnWriteArrayList<>();
        E4Owned<DirectoryStream<Path>> directoryEntries;E4Owned<FileOutputStream> identityRecord;volatile long outcomeLength=-1;volatile String outcomeSha="UNKNOWN";
        FileDescriptor directorySync;boolean directoryOpening,directoryCloseUnknown;
        boolean outputClosed,leaseClosed,ownerClosed,descriptorAdopted,opening,transferAttempted,rejectedTransferClosed;
        void open(Context context,String batch,String budgetIdentity,E4Protocol.Identity originalIdentity)throws Exception{
            opening=true;
            Path directory=context.getFilesDir().toPath().resolve("e4a_outputs");Files.createDirectories(directory);
            int records=0;long metadata=0,liveOutput=0;
            directoryEntries=new E4Owned<>(directory,DirectoryStream::close);directoryEntries.allocate(()->Files.newDirectoryStream(directory));
            try{
                for(Path entry:directoryEntries.original()){if(!Files.isRegularFile(entry,LinkOption.NOFOLLOW_LINKS))throw new IOException("E4A_OUTPUT_ROLE");if(++records>122)throw new IOException("E4_OUTPUT_RECORD_BUDGET");long n=Files.size(entry);if(entry.toString().endsWith(".mp4"))liveOutput=Math.addExact(liveOutput,n);else metadata=Math.addExact(metadata,n);}
            }
            finally{directoryEntries.close();}
            if(liveOutput>4194304 || metadata>130048)throw new IOException("E4A_OUTPUT_STOCK_OR_METADATA_BOUND");
            String hex=originalIdentity.task;String outputTask=hex.substring(0,8)+"-"+hex.substring(8,12)+"-"+hex.substring(12,16)+"-"+hex.substring(16,20)+"-"+hex.substring(20);
            budget=new E4OutputBudget(context.getFilesDir().toPath().resolve("e4a_output_budget"),budgetIdentity,outputTask,batch,this::syncDirectory);
            budget.reserve(); // durable whole-output reservation BEFORE allocating task guards or output FDs
            task=new E4FencedTask(directory,outputTask,this::syncDirectory,new E5BGuard.Policy<>(android.os.Process.myUid(),new E5BAndroidGuardIO()));
            task.initialize(); // Sink.task and task.owner holder are externally reachable before any open/acquire
            Path identityPath=directory.resolve(outputTask+".identity");if(Files.exists(identityPath))throw new IOException("E4A_OUTPUT_IDENTITY_EXISTS");
            identityRecord=new E4Owned<>(identityPath,FileOutputStream::close);identityRecord.allocate(()->new FileOutputStream(identityPath.toFile()));
            identityRecord.initialize(raw->{DataOutputStream out=new DataOutputStream(raw);out.writeUTF("E4A_ORIGINAL_IDENTITY_V1");out.writeUTF(batch);out.writeUTF(budgetIdentity);out.writeUTF(originalIdentity.task);out.writeLong(originalIdentity.epoch);out.writeLong(originalIdentity.generation);out.writeUTF(originalIdentity.serviceInstance);out.writeInt(originalIdentity.hostUid);out.writeInt(originalIdentity.serviceUid);out.writeUTF(outputTask);out.flush();raw.getFD().sync();});identityRecord.close();syncDirectory(directory);
            leaseEpoch=task.issue();output=ParcelFileDescriptor.open(task.authorizedOutput().toFile(),ParcelFileDescriptor.MODE_WRITE_ONLY);lease=ParcelFileDescriptor.open(task.authorizedLease().toFile(),ParcelFileDescriptor.MODE_READ_ONLY);
            opening=false;
        }
        void syncDirectory(Path directory)throws IOException{
            if(directorySync!=null || directoryOpening || directoryCloseUnknown)throw new IOException("E4_DIRECTORY_SYNC_OWNER_PENDING");
            directoryOpening=true;
            try{
                directorySync=Os.open(directory.toString(),OsConstants.O_RDONLY,0);directoryOpening=false;
                if(!OsConstants.S_ISDIR(Os.fstat(directorySync).st_mode))throw new IOException("E4_OUTPUT_DIRECTORY_ROLE");
                Os.fsync(directorySync);
            }catch(android.system.ErrnoException failure){throw new IOException("E4_OUTPUT_DIRECTORY_SYNC",failure);}
            finally{if(directorySync!=null)try{Os.close(directorySync);directorySync=null;}catch(android.system.ErrnoException unknown){directoryCloseUnknown=true;throw new IOException("E4_DIRECTORY_CLOSE_UNKNOWN",unknown);}}
        }
        void closeTransferHandles()throws Exception{if(output!=null && !outputClosed){output.close();outputClosed=true;}if(lease!=null && !leaseClosed){lease.close();leaseClosed=true;}if(opening || directorySync!=null || directoryOpening || directoryCloseUnknown)throw new IOException("E4_SINK_PARTIAL_OPEN_UNKNOWN");}
        void closeOwner()throws Exception{if(!ownerClosed){task.close();ownerClosed=true;}}
        boolean allReturned(){if(directoryEntries==null || !directoryEntries.returned() || task==null || !task.allReturned() || identityRecord==null || !identityRecord.returned() || opening || directorySync!=null || directoryOpening || directoryCloseUnknown)return false;for(E4Owned<?> h:hashOwners)if(!h.returned())return false;return true;}
        void finishBudget(String state)throws Exception{String hash=digest();long length=Files.size(task.authorizedOutput());outcomeLength=length;outcomeSha=hash;budget.finish(length,hash,state);}
        String digest()throws Exception{
            long size=Files.size(task.authorizedOutput());if(size<0 || size>E4Protocol.MAX_OUTPUT_BYTES)throw new IOException("E4_OUTPUT_SIZE");
            if(hashOwners.size()>=3)throw new IOException("E4A_OUTPUT_HASH_COUNT");
            E4Owned<InputStream> holder=new E4Owned<>(task.authorizedOutput(),InputStream::close);hashOwners.add(holder);holder.allocate(()->Files.newInputStream(task.authorizedOutput()));
            java.security.MessageDigest digest=java.security.MessageDigest.getInstance("SHA-256");long read=0;
            try{byte[] buffer=new byte[65536];int n;while((n=holder.original().read(buffer))!=-1){read+=n;if(read>E4Protocol.MAX_OUTPUT_BYTES)throw new IOException("E4_OUTPUT_HASH_CAP");digest.update(buffer,0,n);}}
            finally{holder.close();}
            if(read!=size || Files.size(task.authorizedOutput())!=size)throw new IOException("E4A_OUTPUT_CHANGED_WHILE_HASHING");
            StringBuilder value=new StringBuilder();for(byte b:digest.digest())value.append(String.format(Locale.ROOT,"%02x",b&255));return value.toString();
        }
    }
}
