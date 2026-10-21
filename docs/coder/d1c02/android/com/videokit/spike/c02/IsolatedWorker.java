package com.videokit.spike.c02;

import android.app.Service;
import android.content.Intent;
import android.os.*;
import android.os.Process;
import java.util.concurrent.CountDownLatch;

/** Test injection is Debug-only and signals only this isolated task's own PID. */
public final class IsolatedWorker extends Service {
    private final CountDownLatch stop=new CountDownLatch(1);
    private final Binder binder=new Binder(){
        @Override protected boolean onTransact(int code,Parcel data,Parcel reply,int flags)throws RemoteException{
            data.enforceInterface(WorkerProtocol.WORKER);
            if(code==WorkerProtocol.HELLO){reply.writeNoException();reply.writeInt(Process.myPid());reply.writeInt(Process.myUid());return true;}
            if(code==WorkerProtocol.STOP){stop.countDown();new Handler(Looper.getMainLooper()).post(()->{stopSelf();Process.killProcess(Process.myPid());});return true;}
            if(code!=WorkerProtocol.RUN)return false;
            String task=data.readString();IBinder broker=data.readStrongBinder();int mode=data.readInt();long offset=data.readLong();
            if(mode==WorkerProtocol.EXIT){Process.killProcess(Process.myPid());return true;}
            if(mode==WorkerProtocol.SIGSEGV){Process.sendSignal(Process.myPid(),11);return true;}
            if(mode==WorkerProtocol.HANG){try{stop.await();}catch(InterruptedException e){Thread.currentThread().interrupt();}reply.writeNoException();reply.writeInt(0);return true;}
            byte[] pressure=null;if(mode==WorkerProtocol.PRESSURE){pressure=new byte[WorkerProtocol.MAX_PRESSURE];for(int i=0;i<pressure.length;i+=4096)pressure[i]=1;}
            Parcel request=Parcel.obtain(),answer=Parcel.obtain();
            try{request.writeInterfaceToken(WorkerProtocol.BROKER);request.writeString(task);request.writeLong(offset);request.writeInt(64);
                if(!broker.transact(WorkerProtocol.READ,request,answer,0))throw new RemoteException("BROKER_REJECTED");answer.readException();int n=answer.readInt();byte[] bytes=answer.createByteArray();
                if(bytes==null || bytes.length>WorkerProtocol.MAX_BUFFER || n>bytes.length)throw new RemoteException("BROKER_BOUNDS");
                reply.writeNoException();reply.writeInt(n);reply.writeLong(Debug.getPss());reply.writeInt(pressure==null?0:pressure.length);return true;
            }finally{request.recycle();answer.recycle();}
        }
    };
    @Override public IBinder onBind(Intent intent){return binder;}
    @Override public void onDestroy(){stop.countDown();super.onDestroy();}
}
