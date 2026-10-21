package com.videokit.spike.c05;

import android.app.Service;
import android.content.Intent;
import android.os.*;
import java.util.concurrent.*;

/** Debug helper host in a DISTINCT same-app process; killing it never kills the instrumentation process. */
public final class RecoveryHostService extends Service {
    public static final String INTERFACE="videokit.d1.c05.recovery.host";
    public static final int HELLO=1,START=2,QUERY=3,KILL_SELF_AFTER_SAMPLE=4;
    private volatile IsolatedExportController controller;private volatile String phase="NEW";
    private final ExecutorService completion=Executors.newSingleThreadExecutor(r->{Thread t=new Thread(r,"c05-host-completion");t.setDaemon(true);return t;});
    private final Binder binder=new Binder(){
        @Override protected boolean onTransact(int code,Parcel data,Parcel reply,int flags)throws RemoteException {
            data.enforceInterface(INTERFACE);if(Binder.getCallingUid()!=getApplicationInfo().uid)throw new SecurityException("HOST_CALLER_REJECTED");
            if(code==HELLO){reply.writeNoException();reply.writeInt(android.os.Process.myPid());reply.writeInt(android.os.Process.myUid());return true;}
            if(code==START){
                String id=data.readString();boolean readyThenDie=data.readInt()!=0;
                synchronized(RecoveryHostService.this){if(controller!=null)throw new IllegalStateException("HOST_ALREADY_USED");try{controller=new IsolatedExportController(RecoveryHostService.this,id,DeviceFixtures.routes(RecoveryHostService.this));controller.start(readyThenDie?MediaProtocol.EXPORT:MediaProtocol.GATE_AFTER_SAMPLE);phase="ENCODING";}
                    catch(Exception e){phase="START_FAILED";throw new IllegalStateException("HOST_START_FAILED");}}
                if(readyThenDie)completion.execute(()->{
                    try{IsolatedExportController.Report report=controller.awaitResult(120000);if(!report.valid)throw new IllegalStateException("INVALID_OUTPUT");controller.markReady(false);phase="READY_PERSISTED_RESPONSE_NOT_SENT";android.os.Process.killProcess(android.os.Process.myPid());}
                    catch(Exception e){phase="EXPORT_OR_READY_FAILED";}
                });reply.writeNoException();return true;
            }
            if(code==QUERY){reply.writeNoException();reply.writeString(phase);reply.writeLong(controller==null?0:controller.processedVideoSamples());reply.writeLong(controller==null?0:controller.processedBytes());reply.writeInt(controller==null?-1:controller.workerPid());reply.writeInt(controller==null?-1:controller.workerUid());return true;}
            if(code==KILL_SELF_AFTER_SAMPLE){if(controller==null || controller.processedVideoSamples()<1)throw new IllegalStateException("NO_REAL_VIDEO_PROGRESS");android.os.Process.killProcess(android.os.Process.myPid());return true;}
            return false;
        }
    };
    @Override public IBinder onBind(Intent intent){return binder;}
    @Override public void onDestroy(){if(controller!=null)controller.close();completion.shutdown();super.onDestroy();}
}
