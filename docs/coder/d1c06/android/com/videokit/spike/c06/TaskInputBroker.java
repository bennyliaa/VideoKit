package com.videokit.spike.c06;

import android.os.*;
import java.io.IOException;
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.*;

/** Host-only provider ownership, authenticated isolated UID, bounded handles/bytes/in-flight RPCs. */
public final class TaskInputBroker extends Binder {
    private final String task;private final Map<String,AsyncReadBridge.Provider> routes;
    private final AsyncReadBridge.Runtime runtime;private final LeaseRegistry leases;private final long generation;
    private final Map<Long,AsyncReadBridge> handles=new ConcurrentHashMap<>();private final List<AsyncReadBridge> owned=new ArrayList<>();
    private final AtomicLong ids=new AtomicLong();private final AtomicInteger calls=new AtomicInteger();
    private final AtomicBoolean revoked=new AtomicBoolean();private volatile int workerUid=-1,workerPid=-1;private final AtomicLong bytes=new AtomicLong();
    public TaskInputBroker(String task,Map<String,AsyncReadBridge.Provider> routes,AsyncReadBridge.Runtime runtime,LeaseRegistry leases)throws IOException {
        this.task=task;this.routes=Map.copyOf(routes);this.runtime=runtime;this.leases=leases;generation=leases.create();
    }
    public void attachWorker(int uid,int pid)throws IOException {if(uid<=0 || uid==android.os.Process.myUid() || pid<=0 || pid==android.os.Process.myPid() || workerUid!=-1)throw new IOException("BROKER_UID_REJECTED");workerUid=uid;workerPid=pid;}
    @Override protected boolean onTransact(int code,Parcel data,Parcel reply,int flags)throws RemoteException {
        data.enforceInterface(MediaProtocol.BROKER);
        if(Binder.getCallingUid()!=workerUid || Binder.getCallingPid()!=workerPid || !task.equals(data.readString())){reply.writeException(new SecurityException("BROKER_REJECTED"));return true;}
        if(calls.incrementAndGet()>4){calls.decrementAndGet();reply.writeException(new IllegalStateException("BROKER_RESOURCE_EXHAUSTED"));return true;}
        try {
            if(revoked.get())throw new IOException("SESSION_RELEASED");
            if(code==MediaProtocol.OPEN){
                String uri=data.readString();long offset=data.readLong(),requested=data.readLong();AsyncReadBridge.Provider provider=routes.get(uri);
                if(provider==null)throw new IOException("SOURCE_NOT_AUTHORIZED");
                AsyncReadBridge bridge;long id;
                synchronized(owned){if(revoked.get())throw new IOException("SESSION_RELEASED");if(handles.size()>=8 || owned.size()>=64)throw new IOException("BROKER_RESOURCE_EXHAUSTED");bridge=new AsyncReadBridge(runtime,provider,leases,generation,5000);owned.add(bridge);id=ids.incrementAndGet();handles.put(id,bridge);}
                try{long length=bridge.open(offset,requested);if(revoked.get())throw new IOException("CANCELLED");reply.writeNoException();reply.writeLong(id);reply.writeLong(length);}
                catch(IOException e){handles.remove(id);bridge.close();throw e;}
            }else if(code==MediaProtocol.READ){
                long id=data.readLong();int count=data.readInt();if(count<1 || count>MediaProtocol.MAX_READ)throw new IOException("INVALID_READ_RANGE");
                AsyncReadBridge bridge=handles.get(id);if(bridge==null)throw new IOException("SOURCE_HANDLE_REVOKED");byte[] privateBuffer=new byte[count];int n=bridge.read(privateBuffer,0,count);
                if(revoked.get())throw new IOException("CANCELLED");reply.writeNoException();reply.writeInt(n);reply.writeByteArray(n<0?new byte[0]:Arrays.copyOf(privateBuffer,n));if(n>0)bytes.addAndGet(n);
            }else if(code==MediaProtocol.CLOSE){AsyncReadBridge bridge=handles.remove(data.readLong());if(bridge!=null)bridge.close();reply.writeNoException();}
            else return false;
            return true;
        }catch(IOException e){reply.writeException(new IllegalStateException(e.getMessage()));return true;}
        finally{calls.decrementAndGet();}
    }
    public void revoke(){if(revoked.compareAndSet(false,true)){synchronized(owned){for(AsyncReadBridge b:owned)b.close();handles.clear();leases.retire(generation);}}}
    public void retryFailedCloses(long deadlineMs)throws IOException {
        revoke();List<CompletableFuture<Void>> attempts=new ArrayList<>();synchronized(owned){for(AsyncReadBridge b:owned)attempts.add(b.retryFailedClose());}
        try{CompletableFuture.allOf(attempts.toArray(new CompletableFuture<?>[0])).get(deadlineMs,TimeUnit.MILLISECONDS);}
        catch(Exception e){throw new IOException("SOURCE_CLOSE_RECOVERY_INCOMPLETE");}
    }
    public boolean awaitReleased(long deadlineMs)throws InterruptedException {return leases.awaitReleased(generation,deadlineMs);}
    public LeaseRegistry.Snapshot query(){return leases.query(generation);}
    public long bytes(){return bytes.get();}
}
