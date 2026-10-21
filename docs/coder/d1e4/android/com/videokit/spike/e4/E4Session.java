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
    private final Context context;private final AsyncReadBridge.Provider provider;private final int kind;private final String fault;
    private final AtomicBoolean started=new AtomicBoolean(),cancelled=new AtomicBoolean(),dead=new AtomicBoolean();
    private final AtomicReference<String> first=new AtomicReference<>();
    private final AtomicReference<IBinder> original=new AtomicReference<>();
    private final AtomicInteger controlInFlight=new AtomicInteger();
    private final CompletableFuture<IBinder> connected=new CompletableFuture<>();
    private final CompletableFuture<Report> result=new CompletableFuture<>();
    private final E4Broker broker=new E4Broker();private volatile E4Protocol.Identity identity;
    private volatile E4CpuAdapter source;private volatile Sink sink;
    private E4Broker.ResourceLease sourceLease,sinkLease;
    private final Object events=new Object();private volatile Bundle last=new Bundle(),terminal;
    private volatile boolean serviceStarted,bound,bindReturned,bindingUnknown,slot,ownerFinished,ready,ownerClosed;
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
            int uid=Binder.getCallingUid(),pid=Binder.getCallingPid();
            synchronized(events){callbackInFlight++;}
            try{
                if(code!=1 || flags!=0 || reply==null || data.dataSize()>16384)throw new SecurityException("E4_CALLBACK_PROTOCOL");
                data.enforceInterface(E4CodecWire.CALLBACK);Bundle event=data.readBundle(E4CodecWire.class.getClassLoader());
                E4Protocol.Identity expected=identity;
                if(event==null || data.dataAvail()!=0 || expected==null || dead.get() || uid!=expected.serviceUid || pid!=servicePid || !expected.matches(E4CodecWire.identity(event)))throw new SecurityException("E4_CALLBACK_ORIGINAL_IDENTITY");
                synchronized(events){
                    if(++callbacks>128)throw new SecurityException("E4_CALLBACK_BUDGET");
                    last=new Bundle(event);inputs=Math.max(inputs,event.getInt("inputs"));outputs=Math.max(outputs,event.getInt("outputs"));
                    String status=event.getString("status","");
                    if(status.equals("STARTED"))serviceStarted=true;
                    if(status.equals("FRAME_CONSUMED") && event.getInt("inFlight",-1)==0 && event.getInt("nativeCalls",-1)==0)consumed=Math.max(consumed,event.getInt("inputs"));
                    if(Set.of("CAPABILITY_BLOCKED","FAILED","PENDING","CANCELLED","ENCODED_AWAITING_ISOLATED_VALIDATION").contains(status))terminal=new Bundle(event);
                    events.notifyAll();
                }
                reply.writeNoException();reply.writeInt(0x45344342);reply.writeInt(android.os.Process.myUid());reply.writeString(expected.serviceInstance);
            }catch(Exception rejected){synchronized(events){callbackRejected++;events.notifyAll();}if(reply!=null)reply.writeException(new SecurityException("E4_CALLBACK_REJECTED"));}
            finally{synchronized(events){callbackInFlight--;events.notifyAll();}}
            return true;
        }
    };
    public E4Session(Context context,AsyncReadBridge.Provider source,int kind){this(context,source,kind,"");}
    public E4Session(Context context,AsyncReadBridge.Provider source,int kind,String debugFault){
        this.context=context.getApplicationContext();provider=Objects.requireNonNull(source);this.kind=kind;fault=debugFault==null?"":debugFault;
    }
    public CompletableFuture<Report> start(){
        if(!started.compareAndSet(false,true))throw new IllegalStateException("E4_SESSION_SINGLE_START");
        OWNERS.add(this);try{owner.execute(this::run);}catch(RuntimeException error){first.compareAndSet(null,"E4_HOST_QUEUE_REJECTED");ownerFinished=true;result.complete(report());}return result;
    }
    private Bundle call(int code,Bundle data)throws Exception{IBinder endpoint=original.get();if(endpoint==null)throw new IOException("E4_NOT_READY");return E4CodecWire.call(endpoint,code,data);}
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
            if(!ENCODER_OUTPUT.tryAcquire())throw new IOException("E4_ENCODER_OUTPUT_BUSY_OR_QUARANTINED");slot=true;
            check();bind();check();
            source=new E4CpuAdapter(context,provider,kind);sourceLease=broker.registerResource(identity,E4Broker.ResourceKind.SOURCE,source,source::close);
            sink=new Sink();sinkLease=broker.registerResource(identity,E4Broker.ResourceKind.SINK,sink,sink::closeTransferHandles);sink.open(context);
            if(!fault.isEmpty()){Bundle debug=request();debug.putString("fault",fault);Bundle armed=call(E4CodecWire.DEBUG,debug);if(!"DEBUG_PLAN_ARMED".equals(armed.getString("status")))throw new IOException("E4_DEBUG_PLAN_REJECTED");}
            Bundle begin=request();begin.putBinder("callback",callback);begin.putParcelable("sink",sink.output);begin.putParcelable("lease",sink.lease);begin.putString("leaseEpoch",sink.leaseEpoch);
            sink.transferAttempted=true;Bundle admission=call(E4CodecWire.BEGIN,begin);
            sink.descriptorAdopted=admission.getBoolean("descriptorAdopted");
            sink.rejectedTransferClosed=admission.getBoolean("rejectedGrantCloseProven");
            sinkLease.close();
            if(!"ADMITTED".equals(admission.getString("status")))throw new IOException(admission.getString("error","E4_NOT_ADMITTED"));
            waitFor(()->serviceStarted,15000);broker.serviceReady(identity.serviceUid,identity,true);
            long firstPts=-1;
            for(int sequence=1;sequence<=6;sequence++){
                check();if(System.nanoTime()-runStart>TimeUnit.SECONDS.toNanos(60))throw new IOException("E4_TOTAL_DEADLINE_PENDING");
                E4CpuAdapter.Sample sample=source.next(sequence);received++;
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
            E4CpuAdapter.Verification verification=E4CpuAdapter.validate(context,HostFixtures.file(sink.task.authorizedOutput()),timeline,thumbs,before,bytes,sink::digest);
            if(verification.pid<=0 || verification.uid==identity.hostUid || !verification.fullEof || !verification.sourceClosed || !verification.originalDeath || !verification.slotReleased || !before.equals(verification.sha))throw new IOException("E4_ISOLATED_VALIDATION_UNPROVEN");
            check();broker.authorizeValidator(identity.hostUid,identity,verification.uid);broker.validatedOutput(verification.uid,identity,verification.frames,timeline,true);
            if(System.nanoTime()-runStart>TimeUnit.SECONDS.toNanos(60))throw new IOException("E4_TOTAL_DEADLINE_PENDING");
            token=sink.task.ready(sink.leaseEpoch,true);sink.closeOwner();ownerClosed=true;ready=true;
        }catch(Throwable error){first.compareAndSet(null,safe(error));}
        finally{
            if(!ready){
                cancelled.set(true);if(source!=null)source.cancel();
                if(identity!=null)try{broker.cancel(identity.hostUid,identity);}catch(Exception ignored){}
                if(original.get()!=null && identity!=null && !dead.get())try{last=call(E4CodecWire.CANCEL,request());last=awaitRemoteClosure(101);}catch(Exception failure){first.compareAndSet(null,"E4_CANCEL_RETURN_UNKNOWN");}
                if(sourceLease!=null && sourceLease.state()==E4Broker.CloseState.OPEN)try{sourceLease.close();}catch(Exception pending){}
                if(sinkLease!=null && sinkLease.state()==E4Broker.CloseState.OPEN)try{sinkLease.close();}catch(Exception pending){}
                if(sink!=null && sink.task!=null && !sink.opening && (dead.get() || !sink.transferAttempted || sink.rejectedTransferClosed || remoteClosed(last) || remoteClosed(terminal)))try{
                    if(sink.task.workerLeaseClear()){sink.task.abort();sink.closeOwner();ownerClosed=true;}
                }catch(Exception unknown){first.compareAndSet(null,"E4_SINK_ABORT_OR_OWNER_PENDING");}
            }
            if(dead.get())collectExit();
            if(bound && bindReturned)try{context.unbindService(connection);bound=false;}catch(RuntimeException unknown){bindingUnknown=true;}
            ownerFinished=true;thumbs.clear();
            tryRelease();
            result.complete(report());
        }
    }
    private Bundle awaitRemoteClosure(int maximumQueries)throws Exception{
        Bundle proof=null;
        for(int count=0;count<maximumQueries;count++){
            if(dead.get())throw new IOException("WORKER_DIED");
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
    private boolean released(){
        if(!ownerFinished || dead.get() || bound || bindingUnknown || callbackInFlight!=0 || controlInFlight.get()!=0 || !rejectedConnections.isEmpty() || sink!=null && (sink.opening || sink.transferAttempted && !sink.descriptorAdopted && !sink.rejectedTransferClosed))return false;
        if(identity==null)return !slot || source==null && sink==null;
        try{E4Broker.Snapshot s=broker.snapshot(identity);return s.resourcesReleased() && s.state!=E4Broker.State.UNKNOWN && (sink==null || ownerClosed) && (source==null || source.sourceClosed());}catch(IOException unknown){return false;}
    }
    private synchronized void tryRelease(){if(released()){OWNERS.remove(this);if(slot){slot=false;ENCODER_OUTPUT.release();}owner.shutdown();}}
    private static String safe(Throwable error){String code=error.getMessage();return code!=null && code.matches("[A-Z][A-Z0-9_]{0,95}")?code:"E4_HOST_OPERATION_FAILED";}
    public void cancel(){
        if(ready || ownerFinished)return;
        if(!cancelled.compareAndSet(false,true))return;
        first.compareAndSet(null,"E4_CANCELLED");E4CpuAdapter cpu=source;if(cpu!=null)cpu.cancel();synchronized(events){events.notifyAll();}
        E4Protocol.Identity id=identity;if(id!=null && original.get()!=null && !dead.get()){
            controlInFlight.incrementAndGet();try{CONTROL.execute(()->{try{call(E4CodecWire.CANCEL,E4CodecWire.identity(id));}catch(Exception unknown){first.compareAndSet(null,"E4_CANCEL_RETURN_UNKNOWN");}finally{controlInFlight.decrementAndGet();}});}catch(RejectedExecutionException full){controlInFlight.decrementAndGet();first.compareAndSet(null,"E4_CONTROL_PENDING");}
        }
    }
    public Report await(long milliseconds)throws Exception{
        if(Looper.myLooper()==Looper.getMainLooper())throw new IOException("E4_AWAIT_MAIN_THREAD");
        try{return result.get(milliseconds,TimeUnit.MILLISECONDS);}catch(TimeoutException pending){throw new IOException("E4_PENDING_ORIGINAL_OWNERS_RETAINED");}
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
        public final String task,status,error,token;public final int received,inputs,outputs,callbackRejected;
        public final boolean resourcesReleased,workerDied;public final Bundle remote,systemExit;
        private Report(E4Session s){task=s.task;error=s.first.get();resourcesReleased=s.released();workerDied=s.dead.get();
            status=s.ready && resourcesReleased?"READY":resourcesReleased?"ABORTED":"PENDING";token=status.equals("READY")?s.token:"";
            received=s.received;inputs=s.inputs;outputs=s.outputs;callbackRejected=s.callbackRejected;remote=new Bundle(s.terminal==null?s.last:s.terminal);systemExit=new Bundle(s.exitEvidence);
        }
    }
    private Report report(){return new Report(this);}
    public void close(){if(!ownerFinished)cancel();}

    private static final class Sink {
        FencedTask task;String leaseEpoch;ParcelFileDescriptor output,lease;
        FileDescriptor directorySync;boolean directoryOpening,directoryCloseUnknown;
        boolean outputClosed,leaseClosed,ownerClosed,descriptorAdopted,opening,transferAttempted,rejectedTransferClosed;
        void open(Context context)throws Exception{
            opening=true;
            Path directory=context.getFilesDir().toPath().resolve("e4_outputs");Files.createDirectories(directory);
            int tasks=0;long bytes=0;
            try(java.util.stream.Stream<Path> entries=Files.list(directory)){
                for(Path entry:(Iterable<Path>)entries::iterator){if(Files.isSymbolicLink(entry))throw new IOException("E4_OUTPUT_REPARSE");if(++tasks>128)throw new IOException("E4_OUTPUT_RECORD_BUDGET");if(Files.isRegularFile(entry))bytes=Math.addExact(bytes,Files.size(entry));}
            }
            if(bytes>4194304L-E4Protocol.MAX_OUTPUT_BYTES)throw new IOException("E4_OUTPUT_AGGREGATE_BUDGET");
            task=new FencedTask(directory,UUID.randomUUID().toString(),this::syncDirectory,AndroidLease::exclusive);
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
        String digest()throws Exception{
            long size=Files.size(task.authorizedOutput());if(size<1 || size>E4Protocol.MAX_OUTPUT_BYTES)throw new IOException("E4_OUTPUT_SIZE");
            java.security.MessageDigest digest=java.security.MessageDigest.getInstance("SHA-256");long read=0;
            try(InputStream stream=Files.newInputStream(task.authorizedOutput())){byte[] buffer=new byte[65536];int n;while((n=stream.read(buffer))!=-1){read+=n;if(read>E4Protocol.MAX_OUTPUT_BYTES)throw new IOException("E4_OUTPUT_HASH_CAP");digest.update(buffer,0,n);}}
            StringBuilder value=new StringBuilder();for(byte b:digest.digest())value.append(String.format(Locale.ROOT,"%02x",b&255));return value.toString();
        }
    }
}
