package com.videokit.spike.c06;

import android.content.*;
import android.os.*;
import java.io.IOException;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicBoolean;

/** Each instance owns one isolated process name, one broker lease, and bounded callbacks. */
public final class WorkerClient implements AutoCloseable {
    private static final java.util.concurrent.atomic.AtomicInteger WORKERS=new java.util.concurrent.atomic.AtomicInteger();
    private final Context context;private final String task;private final LeaseRegistry leases;private final AsyncReadBridge source;
    private final ExecutorService connectionExecutor=Executors.newSingleThreadExecutor(r->{Thread t=new Thread(r,"videokit-worker-connect");t.setDaemon(true);return t;});
    private final ThreadPoolExecutor calls=new ThreadPoolExecutor(1,1,0,TimeUnit.MILLISECONDS,new ArrayBlockingQueue<>(4),r->{Thread t=new Thread(r,"videokit-worker-call");t.setDaemon(true);return t;},new ThreadPoolExecutor.AbortPolicy());
    private final CompletableFuture<IBinder> connected=new CompletableFuture<>();private final CompletableFuture<Void> dead=new CompletableFuture<>();
    private final AtomicBoolean revoked=new AtomicBoolean();private final AtomicBoolean reservationReleased=new AtomicBoolean();private final java.util.concurrent.atomic.AtomicInteger brokerReads=new java.util.concurrent.atomic.AtomicInteger();private volatile long authorizedOffset;private volatile boolean bound;private volatile IBinder remote;private volatile int workerUid=-1;private volatile int workerPid=-1;
    private volatile String eventPhase="",taskPhase="";private volatile long bindStartedAt;
    private volatile String stage="NEW";private volatile Throwable brokerCause;private volatile int eventMode=-1;private final java.util.concurrent.atomic.AtomicInteger eventHits=new java.util.concurrent.atomic.AtomicInteger();
    private void stage(String value){stage=value;StageLog.event("WORKER_"+value,"");}
    public String stage(){return stage;}public String eventPhase(){return eventPhase;}public long bindStartedAt(){return bindStartedAt;}public int eventMode(){return eventMode;}public int eventHits(){return eventHits.get();}
    private volatile long pssKb;private volatile int pressureBytes;
    private final ServiceConnection connection=new ServiceConnection(){
        public void onServiceConnected(ComponentName name,IBinder service){
            remote=service;stage("BIND_CONNECTED");try{service.linkToDeath(()->{terminate("WORKER_DIED");releaseReservation();dead.complete(null);},0);if(revoked.get()){stopWorker();unbind();return;}Parcel req=Parcel.obtain(),resp=Parcel.obtain();try{req.writeInterfaceToken(WorkerProtocol.WORKER);service.transact(WorkerProtocol.HELLO,req,resp,0);resp.readException();workerPid=resp.readInt();workerUid=resp.readInt();if(workerUid<=0 || workerPid<=0 || workerUid==android.os.Process.myUid() || workerPid==android.os.Process.myPid())throw new IOException("WORKER_IDENTITY_INVALID");stage("HELLO_OK");connected.complete(service);}finally{req.recycle();resp.recycle();}}
            catch(Exception e){connected.completeExceptionally(new IOException("WORKER_BIND_FAILED",e));StageLog.failure("WORKER_BIND_FAILED",e);terminate("WORKER_BIND_FAILED");}
        }
        public void onServiceDisconnected(ComponentName name){terminate("WORKER_DIED");releaseReservation();dead.complete(null);}
        public void onBindingDied(ComponentName name){terminate("WORKER_DIED");}
        public void onNullBinding(ComponentName name){terminate("WORKER_BIND_FAILED");}
    };
    private final Binder broker=new Binder(){
        @Override protected boolean onTransact(int code,Parcel data,Parcel reply,int flags)throws RemoteException{
            data.enforceInterface(WorkerProtocol.BROKER);
            if(code==WorkerProtocol.EVENT){String id=data.readString();int mode=data.readInt();if(!task.equals(id) || Binder.getCallingUid()!=workerUid || Binder.getCallingPid()!=workerPid)throw new SecurityException("BROKER_EVENT_REJECTED");String phase=data.readString();if(phase==null || !phase.matches("ENTERED|EXIT_ARMED|SIGSEGV_ARMED|HANG_WAIT_BEGIN"))throw new SecurityException("BROKER_EVENT_REJECTED");if(phase.equals("ENTERED")){if(eventHits.incrementAndGet()!=1)throw new SecurityException("BROKER_DUPLICATE_EVENT");eventMode=mode;}else if(eventMode!=mode || !eventPhase.equals("ENTERED"))throw new SecurityException("BROKER_EVENT_ORDER");eventPhase=phase;stage("MODE_"+mode+"_"+phase);reply.writeNoException();return true;}
            if(code!=WorkerProtocol.READ)return false;
            String requested=data.readString();long offset=data.readLong();int n=data.readInt();
            if(revoked.get() || !task.equals(requested) || Binder.getCallingUid()!=workerUid || Binder.getCallingPid()!=workerPid || offset!=authorizedOffset || n<0 || n>WorkerProtocol.MAX_BUFFER || brokerReads.incrementAndGet()>1){reply.writeException(new SecurityException("BROKER_REJECTED"));return true;}
            try{byte[] bytes=new byte[n];int count;
                // This prototype owns one bounded contiguous source interval per worker call.
                // Opening a new bridge is unnecessary: source is prepared at the requested offset by run().
                stage("BROKER_READ_BEGIN");count=source.read(bytes,0,n);stage("BROKER_READ_DONE");if(revoked.get())throw new IOException("CANCELLED");reply.writeNoException();reply.writeInt(count);reply.writeByteArray(bytes);return true;
            }catch(IOException e){brokerCause=e;StageLog.failure("WORKER_BROKER_READ_FAILED",e);reply.writeException(new IllegalStateException(e.getMessage()));return true;}
        }
    };
    public WorkerClient(Context context,String task,AsyncReadBridge source,LeaseRegistry leases)throws IOException{
        this.context=context.getApplicationContext();this.task=task;this.source=source;this.leases=leases;
        if(WORKERS.incrementAndGet()>2){WORKERS.decrementAndGet();connectionExecutor.shutdown();calls.shutdown();source.close();leases.retire(source.generation());throw new IOException("WORKER_BUDGET_EXHAUSTED");}
    }
    public int run(int mode,long offset,long timeoutMs)throws IOException{
        if(Looper.myLooper()==Looper.getMainLooper())throw new IOException("MAIN_THREAD_IO_REJECTED");
        if(revoked.get())throw new IOException("SESSION_RELEASED");
        try{
            authorizedOffset=offset;stage("SOURCE_OPEN_BEGIN");source.open(offset,WorkerProtocol.MAX_BUFFER);stage("SOURCE_OPEN_DONE");
            bound=true;java.util.concurrent.Executor safeConnection=command->{try{connectionExecutor.execute(command);}catch(RejectedExecutionException ignored){}};
            bindStartedAt=System.currentTimeMillis();stage("BIND_BEGIN");boolean accepted=context.bindIsolatedService(new Intent(context,IsolatedWorker.class),Context.BIND_AUTO_CREATE,TaskNames.instance("task",task),safeConnection,connection);
            if(!accepted){bound=false;releaseReservation();throw new IOException("WORKER_BIND_FAILED");}IBinder service=connected.get(timeoutMs,TimeUnit.MILLISECONDS);
            stage("RPC_BEGIN");Future<Integer> request=calls.submit(()->{Parcel req=Parcel.obtain(),reply=Parcel.obtain();try{req.writeInterfaceToken(WorkerProtocol.WORKER);req.writeString(task);req.writeStrongBinder(broker);req.writeInt(mode);req.writeLong(offset);service.transact(WorkerProtocol.RUN,req,reply,0);reply.readException();int n=reply.readInt();if(mode!=WorkerProtocol.HANG){pssKb=reply.readLong();pressureBytes=reply.readInt();}return n;}finally{req.recycle();reply.recycle();}});
            try{int value=request.get(timeoutMs,TimeUnit.MILLISECONDS);stage("RPC_DONE");return value;}catch(TimeoutException e){stopWorker();terminate("WORKER_TIMEOUT");throw new IOException("WORKER_TIMEOUT",e);}
        }catch(TimeoutException e){stopWorker();terminate("WORKER_TIMEOUT");throw new IOException("WORKER_TIMEOUT",e);}
        catch(InterruptedException e){Thread.currentThread().interrupt();stopWorker();terminate("CANCELLED");throw new IOException("CANCELLED");}
        catch(ExecutionException | RuntimeException e){Throwable cause=brokerCause!=null?brokerCause:e;StageLog.failure("WORKER_FAILURE_"+stage,cause);terminate("WORKER_RPC_OR_BIND_FAILED");throw new IOException("WORKER_RPC_OR_BIND_FAILED",cause);}
        catch(IOException e){StageLog.failure("WORKER_FAILURE_"+stage,e);terminate(e.getMessage());throw e;}
    }
    public int uid(){return workerUid;}public int pid(){return workerPid;}
    public long pssKb(){return pssKb;}public int pressureBytes(){return pressureBytes;}
    public boolean awaitDeath(long millis)throws Exception{try{dead.get(millis,TimeUnit.MILLISECONDS);return true;}catch(TimeoutException e){return false;}}
    private void stopWorker(){IBinder service=remote;if(service!=null){Parcel p=Parcel.obtain();try{p.writeInterfaceToken(WorkerProtocol.WORKER);service.transact(WorkerProtocol.STOP,p,null,IBinder.FLAG_ONEWAY);}catch(Exception ignored){}finally{p.recycle();}}}
    private void terminate(String reason){
        if(revoked.compareAndSet(false,true)){source.close();leases.retire(source.generation());connected.completeExceptionally(new IOException(reason));stopWorker();unbind();if(!bound && remote==null)releaseReservation();}
    }
    private void releaseReservation(){if(reservationReleased.compareAndSet(false,true))WORKERS.decrementAndGet();}
    private void unbind(){new Handler(Looper.getMainLooper()).post(()->{if(bound){bound=false;try{context.unbindService(connection);}catch(IllegalArgumentException ignored){}}});}
    @Override public void close(){stopWorker();terminate("CANCELLED");calls.shutdown();connectionExecutor.shutdown();}
}
