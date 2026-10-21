package com.videokit.spike.c09;
import android.app.Service;
import android.content.Intent;
import android.os.*;
import java.io.IOException;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicBoolean;

/** One CPU task per ordinary isolated process, same debug APK; no FD/path or platform codec. */
public final class CpuIsolatedService extends Service {
    private final ExecutorService decode=Executors.newSingleThreadExecutor();
    private final CountDownLatch resume=new CountDownLatch(1);
    private final AtomicBoolean cancelled=new AtomicBoolean(),started=new AtomicBoolean(),frameSent=new AtomicBoolean();
    private volatile int ownerUid=-1,ownerPid=-1,mode;private volatile String task;private volatile long epoch;
    private volatile IBinder broker;private volatile boolean frameAccepted;
    private synchronized void owner() {
        int uid=Binder.getCallingUid(),pid=Binder.getCallingPid();
        if(ownerUid<0){ownerUid=uid;ownerPid=pid;}
        if(ownerUid!=uid || ownerPid!=pid)throw new SecurityException("CPU_OWNER");
    }
    private void authenticate(Parcel p){
        owner();if(!started.get() || !task.equals(p.readString()) || epoch!=p.readLong())throw new SecurityException("CPU_TASK_EPOCH");CpuProtocol.end(p);
    }
    private final Binder binder=new Binder(){
        @Override protected boolean onTransact(int code,Parcel p,Parcel reply,int flags)throws RemoteException {
            if(p.dataSize()>1024)throw new SecurityException("CPU_REQUEST_BUDGET");p.enforceInterface(CpuProtocol.WORKER);
            if(code==CpuProtocol.HELLO){owner();CpuProtocol.end(p);reply.writeInt(CpuFrameRules.ACK);reply.writeInt(android.os.Process.myPid());reply.writeInt(android.os.Process.myUid());return true;}
            if(code==CpuProtocol.START){
                owner();if(!started.compareAndSet(false,true))throw new SecurityException("CPU_ALREADY_STARTED");
                task=p.readString();epoch=p.readLong();String token=p.readString();long length=p.readLong(),target=p.readLong();int kind=p.readInt();mode=p.readInt();broker=p.readStrongBinder();CpuProtocol.end(p);
                if(task==null || !task.matches("[a-f0-9]{32}") || epoch<=0 || token==null || !token.matches("[a-f0-9]{32}")
                        || length<1 || length>CpuFrameRules.MAX_SOURCE || target<0 || target>CpuFrameRules.MAX_PTS_US-2000000
                        || kind<1 || kind>2 || mode<0 || mode>7 || broker==null)throw new SecurityException("CPU_START_PROTOCOL");
                try{broker.linkToDeath(()->killOwnProcess(),0);}catch(RemoteException dead){killOwnProcess();throw dead;}
                decode.execute(()->run(token,length,target,kind));reply.writeInt(CpuFrameRules.ACK);return true;
            }
            if(code==CpuProtocol.STOP && !started.get()){
                owner();String requestedTask=p.readString();long requestedEpoch=p.readLong();CpuProtocol.end(p);
                if(requestedTask==null || !requestedTask.matches("[a-f0-9]{32}") || requestedEpoch<=0)throw new SecurityException("CPU_STOP_IDENTITY");
                killOwnProcess();return true;
            }
            authenticate(p);
            if(code==CpuProtocol.STOP){killOwnProcess();return true;}
            if(code==CpuProtocol.RESUME){if(!frameAccepted || mode!=CpuProtocol.WAIT_FRAME)throw new SecurityException("CPU_NOT_WAITING");resume.countDown();reply.writeInt(CpuFrameRules.ACK);return true;}
            if(code==CpuProtocol.SELF_SEGV){if(!frameAccepted || mode!=CpuProtocol.WAIT_FRAME)throw new SecurityException("CPU_NOT_WAITING");try{event(CpuProtocol.SIGSEGV_ARMED);}catch(Exception e){throw new RemoteException("CPU_ARM_ACK_FAILED");}NativeFault.segvOwnProcess();throw new RemoteException("CPU_SEGV_RETURNED");}
            return false;
        }
    };
    private void killOwnProcess(){cancelled.set(true);resume.countDown();android.os.Process.killProcess(android.os.Process.myPid());}
    private Parcel request(){Parcel p=Parcel.obtain();p.writeInterfaceToken(CpuProtocol.BROKER);p.writeString(task);p.writeLong(epoch);return p;}
    private void event(int event)throws Exception {
        Parcel p=request(),a=Parcel.obtain();try{p.writeInt(event);if(!broker.transact(CpuProtocol.EVENT,p,a,0))throw new IOException("CPU_EVENT");a.readException();}finally{p.recycle();a.recycle();}
    }
    private void run(String token,long length,long target,int kind){
        try {
            if(mode>=CpuProtocol.FORGE_FRAME && mode<=CpuProtocol.FORGE_IDENTITY){new Callbacks(token).onFrame(new byte[CpuFrameRules.BYTES],target,target,256,144,mode==CpuProtocol.FORGE_FRAME?Integer.MAX_VALUE:1024,1,1,1000000,0,1,1);throw new IOException("CPU_FORGE_ACCEPTED");}
            if(mode==CpuProtocol.QUOTA_PROBE){if(NativeCpu.quotaProbe()!=0)throw new IOException("CPU_QUOTA_PROBE_FAILED");event(CpuProtocol.QUOTA_PROVED);}
            int code=NativeCpu.decode(new Callbacks(token),length,target,kind);
            if(code!=0 || !frameAccepted)throw new IOException("CPU_NATIVE_REJECTED");
            if(mode==CpuProtocol.SEGV_FRAME){event(CpuProtocol.SIGSEGV_ARMED);NativeFault.segvOwnProcess();throw new IOException("CPU_SEGV_RETURNED");}
            if(mode==CpuProtocol.HANG_FRAME){event(CpuProtocol.HANG_ARMED);new CountDownLatch(1).await();}
            if(mode==CpuProtocol.WAIT_FRAME)resume.await();
            if(!cancelled.get())event(CpuProtocol.DONE);
        }catch(Throwable error){StageLog.event("CPU_WORKER_REJECTED","code=CPU_DECODE_FAILED");try{event(CpuProtocol.ERROR);}catch(Exception ignored){}}
    }
    public final class Callbacks {
        private final String token;
        Callbacks(String token){this.token=token;}
        public boolean isCancelled(){return cancelled.get();}
        public void onBudget(long baseline,long limit,String version)throws Exception {
            Parcel p=request(),a=Parcel.obtain();try{p.writeLong(baseline);p.writeLong(limit);p.writeString(version);if(!broker.transact(CpuProtocol.BUDGET,p,a,0))throw new IOException("CPU_BUDGET_ACK");a.readException();}finally{p.recycle();a.recycle();}
        }
        public void onStage(int stage)throws Exception {Parcel p=request(),a=Parcel.obtain();try{p.writeInt(stage);if(!broker.transact(CpuProtocol.STAGE,p,a,0))throw new IOException("CPU_STAGE_ACK");a.readException();}finally{p.recycle();a.recycle();}}
        public byte[] readAt(long at,int count)throws Exception {
            if(cancelled.get() || at<0 || count<1 || count>CpuFrameRules.MAX_READ)throw new IOException("CPU_READ_BUDGET");
            Parcel p=request(),a=Parcel.obtain();try{
                p.writeString(token);p.writeLong(at);p.writeInt(count);
                if(!broker.transact(CpuProtocol.READ_AT,p,a,0))throw new IOException("CPU_READ");a.readException();
                int n=a.readInt();if(n<0 || n>count || a.dataAvail()>count+16)throw new IOException("CPU_READ_PROTOCOL");
                byte[] bytes=new byte[n];a.readByteArray(bytes);CpuProtocol.end(a);return bytes;
            }finally{p.recycle();a.recycle();}
        }
        public void onFrame(byte[] bytes,long pts,long raw,int width,int height,int stride,long peakKiB,int timeBaseNum,int timeBaseDen,int bestEffort,long quotaPeak,long quotaCurrent)throws Exception {
            if(!frameSent.compareAndSet(false,true))throw new IOException("CPU_FRAME_IN_FLIGHT");
            Parcel p=Parcel.obtain(),a=Parcel.obtain();try{
                p.writeInterfaceToken(CpuProtocol.BROKER);p.writeString(task);p.writeLong(mode==CpuProtocol.FORGE_EPOCH?(epoch^1):epoch);
                p.writeInt(CpuFrameRules.MAGIC);p.writeInt(CpuFrameRules.VERSION);p.writeInt(android.os.Process.myPid());p.writeInt(mode==CpuProtocol.FORGE_IDENTITY?-1:android.os.Process.myUid());
                p.writeInt(width);p.writeInt(height);p.writeInt(stride);p.writeInt(0);p.writeInt(bytes.length);p.writeLong(pts);p.writeInt(1);
                p.writeLong(raw);p.writeInt(timeBaseNum);p.writeInt(timeBaseDen);p.writeInt(bestEffort);p.writeLong(peakKiB);p.writeLong(quotaPeak);p.writeLong(quotaCurrent);p.writeByteArray(bytes);
                if(!broker.transact(CpuProtocol.FRAME,p,a,0))throw new IOException("CPU_FRAME");a.readException();frameAccepted=true;event(CpuProtocol.FRAME_ACCEPTED);
            }finally{p.recycle();a.recycle();}
        }
    }
    @Override public IBinder onBind(Intent intent){return binder;}
    @Override public void onDestroy(){cancelled.set(true);resume.countDown();decode.shutdownNow();super.onDestroy();}
}
