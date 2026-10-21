package com.videokit.spike.c08;

import android.app.Service;
import android.content.Intent;
import android.os.*;
import androidx.media3.common.*;
import androidx.media3.common.util.Clock;
import androidx.media3.datasource.*;
import androidx.media3.exoplayer.source.DefaultMediaSourceFactory;
import androidx.media3.effect.Presentation;
import androidx.media3.transformer.*;
import java.io.*;
import java.util.List;
import java.util.concurrent.*;
import java.util.concurrent.atomic.*;

/** Actual Media3 path in a separate UID. Ordinary isolatedProcess is a denial probe; companion uses normal app UID. */
public class IsolatedMediaService extends Service {
    private final Handler main=new Handler(Looper.getMainLooper());private final AtomicBoolean started=new AtomicBoolean(),stopping=new AtomicBoolean();
    private volatile int hostUid=-1;private volatile FdOutputMuxer muxer;private Transformer transformer;
    private IBinder sourceBroker,callback;private volatile String task,epoch;
    private AndroidLease.WorkerLease lease;
    private final ScheduledExecutorService watchdog=Executors.newSingleThreadScheduledExecutor(r->{Thread t=new Thread(r,"d1-media-exit-watchdog");t.setDaemon(true);return t;});
    private final Binder binder=new Binder(){
        @Override protected boolean onTransact(int code,Parcel data,Parcel reply,int flags)throws RemoteException {
            data.enforceInterface(MediaProtocol.WORKER);int caller=Binder.getCallingUid();
            if(code==MediaProtocol.HELLO){
                if(getPackageName().equals("com.videokit.worker.spike"))try{if(caller!=getPackageManager().getApplicationInfo("com.videokit.app",0).uid)throw new SecurityException("WORKER_HOST_PACKAGE_REJECTED");}catch(android.content.pm.PackageManager.NameNotFoundException e){throw new SecurityException("WORKER_HOST_PACKAGE_MISSING");}
                synchronized(IsolatedMediaService.this){if(hostUid==-1)hostUid=caller;if(hostUid!=caller)throw new SecurityException("WORKER_OWNER_REJECTED");}
                reply.writeNoException();reply.writeInt(android.os.Process.myPid());reply.writeInt(android.os.Process.myUid());return true;}
            if(caller!=hostUid)throw new SecurityException("WORKER_OWNER_REJECTED");
            if(code==MediaProtocol.START){
                String id=data.readString(),version=data.readString();IBinder broker=data.readStrongBinder(),listener=data.readStrongBinder();int mode=data.readInt();
                ParcelFileDescriptor output=ParcelFileDescriptor.CREATOR.createFromParcel(data),leaseFd=ParcelFileDescriptor.CREATOR.createFromParcel(data);
                if(!started.compareAndSet(false,true)){closeFd(output);closeFd(leaseFd);reply.writeNoException();reply.writeInt(0);return true;}
                task=id;epoch=version;
                main.post(()->startExport(id,version,broker,listener,output,leaseFd,mode));reply.writeNoException();reply.writeInt(1);return true;
            }
            if(!java.util.Objects.equals(task,data.readString()) || !java.util.Objects.equals(epoch,data.readString()))throw new SecurityException("WORKER_TASK_OWNER_REJECTED");
            if(code==MediaProtocol.CANCEL){stop("CANCELLED");return true;}
            if(code==MediaProtocol.RESUME){if(muxer!=null)muxer.releaseGate();return true;}
            if(code==MediaProtocol.EXIT){android.os.Process.killProcess(android.os.Process.myPid());return true;}
            if(code==MediaProtocol.SIGSEGV){android.os.Process.sendSignal(android.os.Process.myPid(),11);return true;}
            return false;
        }
    };
    private void startExport(String id,String version,IBinder broker,IBinder listener,ParcelFileDescriptor output,ParcelFileDescriptor leaseFd,int mode){
        task=id;epoch=version;sourceBroker=broker;callback=listener;
        try {
            if(stopping.get() || task==null || !task.matches("[0-9a-f-]{36}") || epoch==null || !epoch.matches("[0-9a-f-]{36}") || (mode!=MediaProtocol.EXPORT && mode!=MediaProtocol.GATE_AFTER_SAMPLE && mode!=MediaProtocol.CAPABILITY_PROBE))throw new IOException("TASK_START_REJECTED");
            // Orphan workers self-terminate if the ONLY input authority disappears.
            sourceBroker.linkToDeath(()->stop("SOURCE_OWNER_DIED"),0);
            lease=AndroidLease.WorkerLease.acquire(leaseFd,epoch);
            if(mode==MediaProtocol.CAPABILITY_PROBE){
                if(getPackageName().equals("com.videokit.worker.spike"))throw new IOException("PROBE_BACKEND_REJECTED");
                probeEvent("PROBE_LEASE_ACQUIRED");probeEvent("PROBE_CODEC_CREATE_BEGIN");
                String status;android.media.MediaCodec codec=null;Exception createFailure=null;
                try{codec=android.media.MediaCodec.createEncoderByType("video/avc");}catch(IOException|RuntimeException e){createFailure=e;}
                if(createFailure!=null){StageLog.failure("ISOLATED_CODEC_CREATE_FAILED",createFailure);status="ISOLATED_CODEC_JAVA_CALL_FAILED";probeEvent("PROBE_JAVA_FAILURE_"+(createFailure instanceof SecurityException?"SECURITY":createFailure instanceof IOException?"IO":"RUNTIME")+"_EXCEPTION");}
                else{
                    status="ISOLATED_CODEC_CAPABILITY_AVAILABLE";probeEvent("PROBE_CODEC_CREATE_END");probeEvent("PROBE_CODEC_RELEASE_BEGIN");RuntimeException releaseFailure=null;
                    try{codec.release();}catch(RuntimeException e){releaseFailure=e;}
                    if(releaseFailure==null)probeEvent("PROBE_CODEC_RELEASE_END");else{probeEvent("PROBE_CODEC_RELEASE_FAILED");StageLog.failure("ISOLATED_CODEC_RELEASE_FAILED",releaseFailure);status="ISOLATED_CODEC_CAPABILITY_RELEASE_UNKNOWN";}
                }
                closeFd(output);stop(status);return; // Dedicated API attempt; source/codec-export errors cannot masquerade as this marker.
            }
            muxer=new FdOutputMuxer(output,mode==MediaProtocol.GATE_AFTER_SAMPLE,()->event(MediaProtocol.SAMPLE,"VIDEO_SAMPLE_WRITTEN",muxer.videoSamples(),muxer.bytes(),false));
            DataSource.Factory inputs=()->new BrokerDataSource(sourceBroker,task);
            DefaultAssetLoaderFactory assets=new DefaultAssetLoaderFactory(this,new DefaultDecoderFactory.Builder(this).build(),Clock.DEFAULT,new DefaultMediaSourceFactory(inputs),new DataSourceBitmapLoader(this));
            transformer=new Transformer.Builder(this).setAssetLoaderFactory(assets).setMuxerFactory(muxer).setVideoMimeType("video/avc").setAudioMimeType("audio/mp4a-latm").addListener(new Transformer.Listener(){
                public void onCompleted(Composition composition,ExportResult result){finishSuccess();}
                public void onError(Composition composition,ExportResult result,ExportException e){StageLog.failure("COMPANION_EXPORT_ERROR_"+e.errorCode,e);if(muxer!=null)StageLog.event("COMPANION_MUXER_AT_FAILURE","video_samples="+muxer.videoSamples()+" bytes="+muxer.bytes());stop("EXPORT_ERROR_"+e.errorCode);}
            }).build();
            MediaItem input=new MediaItem.Builder().setUri(MediaProtocol.INPUT_MP4).setClippingConfiguration(new MediaItem.ClippingConfiguration.Builder().setStartPositionMs(500).setEndPositionMs(7500).build()).build();
            EditedMediaItem edited=new EditedMediaItem.Builder(input).setEffects(new Effects(List.of(),List.of(Presentation.createForHeight(144)))).build();
            // Transformer requires a string. Custom muxer owns the FD; isolated UID cannot create/delete this root path.
            // No host path is transmitted. Cancellation path deletion is inert; host handles authorized target cleanup.
            transformer.start(edited,"/videokit-c08-fd-only-output.mp4");
        }catch(Exception e){StageLog.failure("MEDIA_EXPORT_START_FAILED",e);if(muxer==null)closeFd(output);if(lease==null)closeFd(leaseFd);stop("EXPORT_START_FAILED");}
    }
    private void finishSuccess(){
        if(!stopping.compareAndSet(false,true))return;
        watchdog.schedule(()->android.os.Process.killProcess(android.os.Process.myPid()),20,TimeUnit.SECONDS);
        try {boolean valid=muxer.validate(7000);long samples=muxer.videoSamples(),bytes=muxer.bytes();boolean flushed=muxer.fsynced();
            closeCapabilities();event(valid && flushed?MediaProtocol.DONE:MediaProtocol.ERROR,valid?"VALIDATED":"OUTPUT_INVALID",samples,bytes,valid && flushed);
        }catch(Exception e){closeCapabilities();event(MediaProtocol.ERROR,"OUTPUT_VALIDATION_FAILED",0,0,false);}
        finally{killSelfSoon();}
    }
    private void probeEvent(String code)throws IOException {
        Parcel req=Parcel.obtain(),reply=Parcel.obtain();try{req.writeInterfaceToken(MediaProtocol.CALLBACK);req.writeString(task);req.writeString(epoch);req.writeString(code);req.writeLong(0);req.writeLong(0);req.writeInt(0);req.writeInt(android.os.Process.myPid());req.writeInt(android.os.Process.myUid());if(callback==null || !callback.transact(MediaProtocol.PROBE_STAGE,req,reply,0))throw new IOException("PROBE_ACK_MISSING");reply.readException();StageLog.event(code,"pid="+android.os.Process.myPid()+" uid="+android.os.Process.myUid());}catch(RemoteException e){throw new IOException("PROBE_ACK_FAILED",e);}finally{req.recycle();reply.recycle();}
    }
    private void event(int type,String code,long samples,long bytes,boolean valid){
        IBinder listener=callback;if(listener==null)return;Parcel req=Parcel.obtain(),reply=Parcel.obtain();
        try{req.writeInterfaceToken(MediaProtocol.CALLBACK);req.writeString(task);req.writeString(epoch);req.writeString(code);req.writeLong(samples);req.writeLong(bytes);req.writeInt(valid?1:0);req.writeInt(android.os.Process.myPid());req.writeInt(android.os.Process.myUid());listener.transact(type,req,reply,0);reply.readException();}
        catch(Exception ignored){}finally{req.recycle();reply.recycle();}
    }
    private void stop(String code){
        if(!stopping.compareAndSet(false,true))return;FdOutputMuxer current=muxer;if(current!=null)current.releaseGate();
        // A blocked native cancellation on main cannot prevent bounded self termination.
        watchdog.schedule(()->android.os.Process.killProcess(android.os.Process.myPid()),2,TimeUnit.SECONDS);
        main.post(()->{try{if(transformer!=null)transformer.cancel();}finally{closeCapabilities();event(MediaProtocol.ERROR,code,0,0,false);killSelfSoon();}});
    }
    private void closeCapabilities(){
        // Closing all output/read descriptors BEFORE dropping the shared lease makes exclusive host recovery safe.
        if(muxer!=null && !muxer.closeDescriptors())return; // Keep the lease until actual process death if descriptor close is uncertain.
        try{if(lease!=null)lease.close();}catch(IOException ignored){}lease=null;
    }
    private static void closeFd(ParcelFileDescriptor fd){if(fd!=null)try{fd.close();}catch(IOException ignored){}}
    private void killSelfSoon(){watchdog.schedule(()->android.os.Process.killProcess(android.os.Process.myPid()),50,TimeUnit.MILLISECONDS);}
    @Override public IBinder onBind(Intent intent){return binder;}
    @Override public void onDestroy(){stop("SERVICE_DESTROYED");super.onDestroy();}
}
