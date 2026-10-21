package com.videokit.spike.c03;

import android.content.*;
import android.os.*;
import android.system.*;
import java.io.*;
import java.nio.file.Path;
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.*;

/** Host-only task authority. FDs are explicitly granted; source bytes arrive solely through the broker. */
public final class IsolatedExportController implements AutoCloseable {
    public enum Backend { ISOLATED_SERVICE, SIGNED_CODEC_COMPANION }
    public static final class Report {
        public final long videoSamples,bytes;public final boolean valid;
        Report(long samples,long bytes,boolean valid){videoSamples=samples;this.bytes=bytes;this.valid=valid;}
    }
    private static final Map<String,IsolatedExportController> OWNERS=new HashMap<>();
    private final Context context;private final String id;private final FencedTask task;private volatile String epoch;private final Backend backend;
    private final int slot;private volatile boolean claimRejected;
    private final AsyncReadBridge.Runtime runtime=new AsyncReadBridge.Runtime();private final LeaseRegistry registry=new LeaseRegistry();
    private final TaskInputBroker broker;
    private final ExecutorService connections=Executors.newSingleThreadExecutor(r->{Thread t=new Thread(r,"c03-media-connection");t.setDaemon(true);return t;});
    private final ThreadPoolExecutor commands=new ThreadPoolExecutor(1,1,0,TimeUnit.MILLISECONDS,new ArrayBlockingQueue<>(2),r->{Thread t=new Thread(r,"c03-media-command");t.setDaemon(true);return t;},new ThreadPoolExecutor.AbortPolicy());
    private final CompletableFuture<IBinder> boundResult=new CompletableFuture<>();private final CompletableFuture<Void> death=new CompletableFuture<>();
    private final CompletableFuture<Report> result=new CompletableFuture<>();private final CountDownLatch sample=new CountDownLatch(1);
    private final AtomicBoolean cancelled=new AtomicBoolean(),started=new AtomicBoolean(),closed=new AtomicBoolean();
    private final AtomicInteger grantPhase=new AtomicInteger(); // 0=not sent, 1=sent/unknown, 2=cancelled before any grant.
    private volatile IBinder remote;private volatile boolean bound;private volatile int workerUid=-1,workerPid=-1;private volatile long processedVideoSamples,processedBytes;
    private final Binder callback=new Binder(){
        @Override protected boolean onTransact(int code,Parcel data,Parcel reply,int flags)throws RemoteException {
            data.enforceInterface(MediaProtocol.CALLBACK);String taskId=data.readString(),version=data.readString(),status=data.readString();
            long samples=data.readLong(),bytes=data.readLong();boolean valid=data.readInt()!=0;int pid=data.readInt(),uid=data.readInt();
            if(Binder.getCallingUid()!=workerUid || Binder.getCallingPid()!=workerPid || uid!=workerUid || pid!=workerPid || !id.equals(taskId) || !Objects.equals(epoch,version))throw new SecurityException("WORKER_CALLBACK_REJECTED");
            if(code==MediaProtocol.SAMPLE){if(samples<1 || bytes<1)throw new IllegalStateException("INVALID_PROCESSING_PROOF");processedVideoSamples=samples;processedBytes=bytes;sample.countDown();}
            else if(code==MediaProtocol.DONE){broker.revoke();if(cancelled.get())result.completeExceptionally(new IOException("CANCELLED"));else result.complete(new Report(samples,bytes,valid && samples>0 && bytes>0));}
            else if(code==MediaProtocol.ERROR){broker.revoke();result.completeExceptionally(new IOException(status!=null && status.matches("[A-Z_0-9]{3,64}")?status:"WORKER_ERROR_REDACTED"));}
            else return false;reply.writeNoException();return true;
        }
    };
    private final ServiceConnection connection=new ServiceConnection(){
        public void onServiceConnected(ComponentName name,IBinder service){
            remote=service;
            try {
                service.linkToDeath(()->died(),0);if(closed.get()){send(MediaProtocol.CANCEL);unbind();return;}
                Parcel req=Parcel.obtain(),reply=Parcel.obtain();try{req.writeInterfaceToken(MediaProtocol.WORKER);service.transact(MediaProtocol.HELLO,req,reply,0);reply.readException();workerPid=reply.readInt();workerUid=reply.readInt();
                    if(workerPid<=0 || workerUid<=0 || workerPid==android.os.Process.myPid() || workerUid==android.os.Process.myUid())throw new IOException("WORKER_NOT_ISOLATED");broker.attachWorker(workerUid,workerPid);boundResult.complete(service);
                }finally{req.recycle();reply.recycle();}
            }catch(Exception e){boundResult.completeExceptionally(new IOException("WORKER_BIND_FAILED"));broker.revoke();send(MediaProtocol.CANCEL);}
        }
        public void onServiceDisconnected(ComponentName name){died();}
        public void onBindingDied(ComponentName name){boundResult.completeExceptionally(new IOException("WORKER_BINDING_DIED"));broker.revoke();unbind();}
        public void onNullBinding(ComponentName name){boundResult.completeExceptionally(new IOException("WORKER_BIND_FAILED"));broker.revoke();unbind();}
    };
    public static void syncDirectory(Path directory)throws IOException {
        if(!java.nio.file.Files.isDirectory(directory))throw new IOException("OUTPUT_DIRECTORY_INVALID");
        FileDescriptor fd=null;try{fd=Os.open(directory.toString(),OsConstants.O_RDONLY,0);Os.fsync(fd);}
        catch(ErrnoException e){throw new IOException("OUTPUT_DIRECTORY_SYNC_FAILED");}finally{if(fd!=null)try{Os.close(fd);}catch(ErrnoException ignored){}}
    }
    public IsolatedExportController(Context context,String taskId,Map<String,AsyncReadBridge.Provider> routes)throws IOException {
        this(context,taskId,routes,Backend.SIGNED_CODEC_COMPANION);
    }
    public IsolatedExportController(Context context,String taskId,Map<String,AsyncReadBridge.Provider> routes,Backend backend)throws IOException {
        this.context=context.getApplicationContext();id=taskId;this.backend=backend;
        synchronized(OWNERS){OWNERS.values().removeIf(owner->{if(owner.releasable()){owner.runtime.close();return true;}return false;});if(OWNERS.size()>=2)throw new IOException("WORKER_OR_QUARANTINE_BUDGET_EXHAUSTED");
            if(OWNERS.containsKey(id))throw new IOException("OUTPUT_OWNER_BUSY");
            slot=OWNERS.values().stream().anyMatch(owner->owner.slot==0)?1:0;
            task=openTask(context,id);
            try{broker=new TaskInputBroker(id,routes,runtime,registry);}catch(IOException e){task.close();throw e;}OWNERS.put(id,this);
        }
    }
    public static Path targetDirectory(Context context){return new File(context.getCacheDir(),"d1_c03_worker_targets").toPath();}
    public static FencedTask openTask(Context context,String taskId)throws IOException{return new FencedTask(targetDirectory(context),taskId,IsolatedExportController::syncDirectory,AndroidLease::exclusive);}
    public void start(int mode)throws IOException {
        if(Looper.myLooper()==Looper.getMainLooper())throw new IOException("MAIN_THREAD_IO_REJECTED");if(!started.compareAndSet(false,true))throw new IOException("TASK_ALREADY_STARTED");
        try {
            java.util.concurrent.Executor safe=command->{try{connections.execute(command);}catch(RejectedExecutionException ignored){}};
            boolean accepted;
            if(backend==Backend.ISOLATED_SERVICE){bound=true;accepted=context.bindIsolatedService(new Intent(context,IsolatedMediaService.class),Context.BIND_AUTO_CREATE,"media_"+id,safe,connection);}
            else {
                // Separate ordinary app UID, signature permission + exact host UID check; no same-UID downgrade.
                if(context.getPackageManager().checkSignatures("com.videokit.app","com.videokit.worker.spike")!=android.content.pm.PackageManager.SIGNATURE_MATCH)throw new IOException("WORKER_SIGNATURE_REJECTED");
                bound=true;accepted=context.bindService(new Intent().setComponent(new ComponentName("com.videokit.worker.spike",slot==0?IsolatedMediaService.class.getName():CodecWorkerSlot1.class.getName())),Context.BIND_AUTO_CREATE,safe,connection);
            }
            if(!accepted){bound=false;death.complete(null);throw new IOException("WORKER_BIND_FAILED");}
            IBinder worker=boundResult.get(15,TimeUnit.SECONDS);epoch=task.issue();
            Future<?> transfer=commands.submit(()->{
                try(ParcelFileDescriptor output=ParcelFileDescriptor.open(task.authorizedOutput().toFile(),ParcelFileDescriptor.MODE_READ_WRITE);ParcelFileDescriptor lease=ParcelFileDescriptor.open(task.authorizedLease().toFile(),ParcelFileDescriptor.MODE_READ_ONLY)){
                    Parcel req=Parcel.obtain(),reply=Parcel.obtain();try{req.writeInterfaceToken(MediaProtocol.WORKER);req.writeString(id);req.writeString(epoch);req.writeStrongBinder(broker);req.writeStrongBinder(callback);req.writeInt(mode);output.writeToParcel(req,0);lease.writeToParcel(req,0);if(!grantPhase.compareAndSet(0,1))throw new IOException("CANCELLED");worker.transact(MediaProtocol.START,req,reply,0);reply.readException();if(reply.readInt()!=1){claimRejected=true;throw new IOException("WORKER_SLOT_BUSY");}}finally{req.recycle();reply.recycle();}
                }catch(Exception e){throw new CompletionException(new IOException("OUTPUT_GRANT_FAILED"));}
            });transfer.get(15,TimeUnit.SECONDS);
        }catch(Exception e){cancel();throw new IOException(e instanceof TimeoutException?"WORKER_START_TIMEOUT":"WORKER_START_FAILED");}
    }
    public Report awaitResult(long deadlineMs)throws IOException {
        try{return result.get(deadlineMs,TimeUnit.MILLISECONDS);}catch(TimeoutException e){cancel();throw new IOException("EXPORT_TIMEOUT");}
        catch(InterruptedException e){Thread.currentThread().interrupt();cancel();throw new IOException("CANCELLED");}
        catch(ExecutionException e){Throwable c=e.getCause();throw c instanceof IOException?(IOException)c:new IOException("EXPORT_FAILED");}
    }
    public boolean awaitProcessedVideo(long deadlineMs)throws InterruptedException{return sample.await(deadlineMs,TimeUnit.MILLISECONDS);}
    public String markReady(boolean loseResponse)throws IOException {
        if(cancelled.get())throw new IOException("CANCELLED");Report report=awaitResult(1);
        try{if(!awaitDeath(15000))throw new IOException("OUTPUT_READY_UNKNOWN");}catch(InterruptedException e){Thread.currentThread().interrupt();throw new IOException("CANCELLED");}
        String token=task.ready(epoch,report.valid);
        if(loseResponse)throw new IOException("OUTPUT_READY_UNKNOWN");return token;
    }
    public FencedTask.State query()throws IOException{return task.query();}public String token()throws IOException{return task.token();}
    public void cancel(){
        cancelled.set(true);grantPhase.compareAndSet(0,2);broker.revoke();result.completeExceptionally(new IOException("CANCELLED"));
        try{task.abort();}catch(IOException ignored){}send(MediaProtocol.CANCEL);
    }
    /** Only this task's isolated process receives the injection, after real processing proof in tests. */
    public void injectTermination(boolean nativeSignal){send(nativeSignal?MediaProtocol.SIGSEGV:MediaProtocol.EXIT);}
    public void resumeAfterSample(){send(MediaProtocol.RESUME);}
    private void send(int code){IBinder service=remote;if(service!=null && !claimRejected){Parcel req=Parcel.obtain();try{req.writeInterfaceToken(MediaProtocol.WORKER);req.writeString(id);req.writeString(epoch);service.transact(code,req,null,IBinder.FLAG_ONEWAY);}catch(Exception ignored){}finally{req.recycle();}}}
    private void died(){broker.revoke();death.complete(null);boundResult.completeExceptionally(new IOException("WORKER_DIED"));result.completeExceptionally(new IOException("WORKER_DIED"));unbind();}
    private void unbind(){new Handler(Looper.getMainLooper()).post(()->{if(bound){bound=false;try{context.unbindService(connection);}catch(IllegalArgumentException ignored){}}});}
    public boolean awaitDeath(long deadlineMs)throws InterruptedException {try{death.get(deadlineMs,TimeUnit.MILLISECONDS);return true;}catch(ExecutionException | TimeoutException e){return false;}}
    public FencedTask.State recoverAbort(long deadlineMs)throws IOException,InterruptedException {
        long stop=System.nanoTime()+TimeUnit.MILLISECONDS.toNanos(deadlineMs);
        while(true)try{return task.abort();}catch(IOException e){if(!"OUTPUT_WORKER_ACTIVE".equals(e.getMessage()) || System.nanoTime()>=stop)throw e;Thread.sleep(20);}
    }
    public boolean awaitSourceReleased(long deadlineMs)throws InterruptedException {return broker.awaitReleased(deadlineMs);}
    public void retrySourceClose(long deadlineMs)throws IOException{broker.retryFailedCloses(deadlineMs);}
    public static List<String> quarantinedTasks(){synchronized(OWNERS){return new ArrayList<>(OWNERS.keySet());}}
    public static boolean recoverQuarantinedSource(String taskId,long deadlineMs)throws IOException,InterruptedException{
        IsolatedExportController owner;synchronized(OWNERS){owner=OWNERS.get(taskId);}if(owner==null)return true;
        owner.retrySourceClose(deadlineMs);boolean released=owner.awaitSourceReleased(deadlineMs);
        synchronized(OWNERS){if(owner.releasable()){owner.runtime.close();OWNERS.remove(taskId,owner);}}return released;
    }
    public LeaseRegistry.Snapshot sourceQuery(){return broker.query();}
    public int workerPid(){return workerPid;}public int workerUid(){return workerUid;}public long brokerBytes(){return broker.bytes();}
    public long processedVideoSamples(){return processedVideoSamples;}public long processedBytes(){return processedBytes;}
    private boolean releasable(){return closed.get() && (death.isDone() || claimRejected || grantPhase.get()==2) && broker.query().released() && commands.getActiveCount()==0 && commands.getQueue().isEmpty();}
    @Override public void close(){
        if(!closed.compareAndSet(false,true))return;cancel();unbind();commands.shutdown();connections.shutdown();
        if(broker.query().released())runtime.close();try{task.close();}catch(IOException ignored){}
        synchronized(OWNERS){if(releasable())OWNERS.remove(id,this);}
        // Undrained owners remain in OWNERS (maximum 2) for explicit recovery/query; no endless new pools.
    }
}
