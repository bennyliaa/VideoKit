package com.videokit.spike.c11;
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
    private final CountDownLatch stopStall=new CountDownLatch(1);
    private final AtomicBoolean cancelled=new AtomicBoolean(),started=new AtomicBoolean(),frameSent=new AtomicBoolean(),stopGranted=new AtomicBoolean();
    private volatile int ownerUid=-1,ownerPid=-1,mode;private volatile String task;private volatile long epoch;
    private volatile IBinder broker;private volatile boolean frameAccepted;private volatile int workerFailure;
    private final java.util.concurrent.atomic.AtomicInteger rejectedOneway=new java.util.concurrent.atomic.AtomicInteger();
    private synchronized void owner() {
        int uid=Binder.getCallingUid(),pid=Binder.getCallingPid();
        try{CpuControlRules.owner(ownerUid,ownerPid,uid,pid);}catch(SecurityException error){StageLog.event("CPU_OWNER_REJECTED","expected_uid="+ownerUid+" expected_pid="+ownerPid+" actual_uid="+uid+" actual_pid="+pid);throw error;}
    }
    private synchronized void hello(String requestedTask,long requestedEpoch){
        int uid=Binder.getCallingUid(),pid=Binder.getCallingPid();
        if(pid<=0 || uid<=0 || requestedTask==null || !requestedTask.matches("[a-f0-9]{32}") || requestedEpoch<=0)throw new SecurityException("CPU_HELLO_IDENTITY");
        if(ownerUid<0){ownerUid=uid;ownerPid=pid;task=requestedTask;epoch=requestedEpoch;}
        owner();CpuControlRules.session(task,epoch,requestedTask,requestedEpoch);
    }
    private void authenticate(Parcel p){
        owner();CpuControlRules.session(task,epoch,p.readString(),p.readLong());CpuProtocol.end(p);
    }
    private final Binder binder=new Binder(){
        @Override protected boolean onTransact(int code,Parcel p,Parcel reply,int flags)throws RemoteException {
            try{return dispatch(code,p,reply,flags);}catch(Exception error){
                StageLog.failure("CPU_CONTROL_REJECTED",error);
                if(reply!=null){reply.setDataSize(0);reply.setDataPosition(0);reply.writeInt(CpuControlRules.ERROR);reply.writeInt(CpuControlRules.errorNumber(error.getMessage()));}return true;
            }
        }
        private boolean dispatch(int code,Parcel p,Parcel reply,int flags)throws RemoteException {
            if(p.dataSize()>1024)throw new SecurityException("CPU_REQUEST_BUDGET");p.enforceInterface(CpuProtocol.WORKER);
            if((flags&IBinder.FLAG_ONEWAY)!=0){rejectedOneway.incrementAndGet();StageLog.event("CPU_CONTROL_ONEWAY_REJECTED","caller_uid="+Binder.getCallingUid()+" caller_pid="+Binder.getCallingPid()+" flags="+flags);}
            CpuControlRules.synchronous(flags);
            if(code==CpuProtocol.HELLO){String requestedTask=p.readString();long requestedEpoch=p.readLong();CpuProtocol.end(p);hello(requestedTask,requestedEpoch);reply.writeInt(CpuFrameRules.ACK);reply.writeInt(android.os.Process.myPid());reply.writeInt(android.os.Process.myUid());reply.writeString(android.app.Application.getProcessName());return true;}
            if(code==CpuProtocol.START){
                owner();if(stopGranted.get() || cancelled.get())throw new SecurityException("CPU_STOP_ALREADY_GRANTED");if(!started.compareAndSet(false,true))throw new SecurityException("CPU_ALREADY_STARTED");
                CpuControlRules.session(task,epoch,p.readString(),p.readLong());String token=p.readString();long length=p.readLong(),target=p.readLong();int kind=p.readInt();mode=p.readInt();broker=p.readStrongBinder();CpuProtocol.end(p);
                if(task==null || !task.matches("[a-f0-9]{32}") || epoch<=0 || token==null || !token.matches("[a-f0-9]{32}")
                        || length<1 || length>CpuFrameRules.MAX_SOURCE || target<0 || target>CpuFrameRules.MAX_PTS_US-2000000
                        || kind<1 || kind>2 || mode<0 || mode>9 || broker==null)throw new SecurityException("CPU_START_PROTOCOL");
                try{broker.linkToDeath(()->killOwnProcess(),0);}catch(RemoteException dead){killOwnProcess();throw dead;}
                decode.execute(()->run(token,length,target,kind));reply.writeInt(CpuFrameRules.ACK);return true;
            }
            authenticate(p);
            if(code==CpuProtocol.QUERY_CONTROL){reply.writeInt(CpuFrameRules.ACK);reply.writeInt(rejectedOneway.get());return true;}
            if(code==CpuProtocol.RELEASE_STOP_STALL){if(mode!=CpuProtocol.STOP_STALL)throw new SecurityException("CPU_NOT_STOP_STALLED");stopStall.countDown();reply.writeInt(CpuFrameRules.ACK);return true;}
            if(code==CpuProtocol.STOP){
                if(mode==CpuProtocol.STOP_STALL)try{stopStall.await();}catch(InterruptedException error){Thread.currentThread().interrupt();throw new RemoteException("CPU_STOP_STALL_INTERRUPTED");}
                if(mode!=CpuProtocol.STOP_ACK_LOSS){reply.writeInt(CpuFrameRules.ACK);reply.writeInt(1);}
                if(stopGranted.compareAndSet(false,true)){cancelled.set(true);resume.countDown();StageLog.event("CPU_STOP_GRANTED","task="+task+" epoch="+epoch+" caller_uid="+Binder.getCallingUid()+" caller_pid="+Binder.getCallingPid());new Handler(Looper.getMainLooper()).postDelayed(()->killOwnProcess(),25);}
                return true;
            }
            if(code==CpuProtocol.RESUME){if(!frameAccepted || mode!=CpuProtocol.WAIT_FRAME)throw new SecurityException("CPU_NOT_WAITING");resume.countDown();reply.writeInt(CpuFrameRules.ACK);return true;}
            if(code==CpuProtocol.SELF_SEGV){if(!frameAccepted || mode!=CpuProtocol.WAIT_FRAME)throw new SecurityException("CPU_NOT_WAITING");try{event(CpuProtocol.SIGSEGV_ARMED);}catch(Exception e){throw new RemoteException("CPU_ARM_ACK_FAILED");}NativeFault.segvOwnProcess();throw new RemoteException("CPU_SEGV_RETURNED");}
            return false;
        }
    };
    private void killOwnProcess(){cancelled.set(true);resume.countDown();android.os.Process.killProcess(android.os.Process.myPid());}
    private Parcel request(){Parcel p=Parcel.obtain();p.writeInterfaceToken(CpuProtocol.BROKER);p.writeString(task);p.writeLong(epoch);return p;}
    private void event(int event)throws Exception {
        Parcel p=request(),a=Parcel.obtain();try{p.writeInt(event);if(event==CpuProtocol.ERROR)p.writeInt(workerFailure);if(!broker.transact(CpuProtocol.EVENT,p,a,0))throw new IOException("CPU_EVENT");a.readException();}finally{p.recycle();a.recycle();}
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
        }catch(Throwable error){workerFailure=CpuDiagnostics.workerCategory(error);StageLog.failure("CPU_WORKER_REJECTED_CATEGORY_"+workerFailure,error);try{event(CpuProtocol.ERROR);}catch(Exception ignored){}}
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
    @Override public IBinder onBind(Intent intent){
        Bundle registration=intent.getBundleExtra("c11_registration");
        if(registration==null){killOwnProcess();return null;}
        if(registration.getBoolean("debug_stop_stall",false))mode=CpuProtocol.STOP_STALL;
        IBinder registrar=registration.getBinder("registrar");Parcel p=Parcel.obtain(),a=Parcel.obtain();
        try{if(registrar==null)throw new SecurityException("CPU_REGISTRAR_MISSING");
            p.writeInterfaceToken(CpuProtocol.WORKER+".registration");p.writeString(registration.getString("task"));p.writeLong(registration.getLong("epoch"));p.writeStrongBinder(binder);
            if(!registrar.transact(1,p,a,0) || a.readInt()!=CpuFrameRules.ACK || a.dataAvail()!=0)throw new SecurityException("CPU_REGISTRATION_REJECTED");
            registrar.linkToDeath(()->killOwnProcess(),0);return binder;
        }catch(Exception error){StageLog.failure("CPU_REGISTRATION_FAILED",error);killOwnProcess();return null;}
        finally{p.recycle();a.recycle();}
    }
    @Override public void onDestroy(){cancelled.set(true);resume.countDown();decode.shutdownNow();super.onDestroy();killOwnProcess();}
}
