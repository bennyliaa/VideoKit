package com.videokit.spike.c03;

import android.graphics.SurfaceTexture;
import android.graphics.Bitmap;
import android.media.MediaMetadataRetriever;
import android.os.Debug;
import android.os.PowerManager;
import android.view.Surface;
import androidx.media3.common.*;
import androidx.media3.common.text.CueGroup;
import androidx.media3.effect.Presentation;
import androidx.media3.exoplayer.ExoPlayer;
import androidx.media3.transformer.*;
import androidx.test.ext.junit.runners.AndroidJUnit4;
import androidx.test.platform.app.InstrumentationRegistry;
import java.io.*;
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.*;
import org.junit.Test;
import org.junit.runner.RunWith;
import static org.junit.Assert.*;

@RunWith(AndroidJUnit4.class)
public final class C03DeviceTests {
    private void main(Runnable r){InstrumentationRegistry.getInstrumentation().runOnMainSync(r);}
    private android.content.Context context(){return InstrumentationRegistry.getInstrumentation().getTargetContext();}
    private void metric(String label){PowerManager power=(PowerManager)context().getSystemService(android.content.Context.POWER_SERVICE);System.out.println("D1 "+label+" pss_kb="+Debug.getPss()+" thermal="+power.getCurrentThermalStatus()+" api="+android.os.Build.VERSION.SDK_INT+" abi="+android.os.Build.SUPPORTED_ABIS[0]);}
    @Test public void playbackMp4()throws Exception{playback(MediaEngine.MP4,false,false);}
    @Test public void playbackAviSrt()throws Exception{playback(MediaEngine.AVI,true,true);}
    @Test public void playbackMkvAss()throws Exception{playback(MediaEngine.MKV,false,true);}
    private void playback(String uri,boolean srt,boolean textExpected)throws Exception{
        LeaseRegistry leases=new LeaseRegistry();long generation=leases.create();AsyncReadBridge.Runtime runtime=new AsyncReadBridge.Runtime();
        AtomicReference<ExoPlayer> player=new AtomicReference<>();AtomicReference<PlaybackException> failure=new AtomicReference<>();AtomicReference<Surface> surface=new AtomicReference<>();AtomicReference<SurfaceTexture> texture=new AtomicReference<>();AtomicInteger cues=new AtomicInteger();
        try{
            main(()->{ExoPlayer p=MediaEngine.player(context(),runtime,leases,generation,DeviceFixtures.routes(context()));player.set(p);p.setVolume(0);p.addListener(new Player.Listener(){public void onPlayerError(PlaybackException e){failure.set(e);}public void onCues(CueGroup group){if(!group.cues.isEmpty())cues.incrementAndGet();}});
                SurfaceTexture t=new SurfaceTexture(false);t.setDefaultBufferSize(624,352);texture.set(t);Surface s=new Surface(t);surface.set(s);p.setVideoSurface(s);p.setMediaItem(MediaEngine.item(uri,srt));p.prepare();});
            settle(player,failure,0,false);AtomicLong duration=new AtomicLong();main(()->duration.set(player.get().getDuration()));assertTrue("duration",duration.get()>0);
            if(textExpected){AtomicReference<TrackSelectionOverride> override=new AtomicReference<>();main(()->{for(Tracks.Group group:player.get().getCurrentTracks().getGroups())if(group.getType()==C.TRACK_TYPE_TEXT && group.isTrackSupported(0)){override.set(new TrackSelectionOverride(group.getMediaTrackGroup(),0));break;}});
                assertNotNull("supported subtitle track",override.get());main(()->player.get().setTrackSelectionParameters(player.get().getTrackSelectionParameters().buildUpon().setTrackTypeDisabled(C.TRACK_TYPE_TEXT,false).setOverrideForType(override.get()).build()));
                Thread.sleep(100);AtomicBoolean selected=new AtomicBoolean();main(()->selected.set(player.get().getCurrentTracks().isTypeSelected(C.TRACK_TYPE_TEXT)));assertTrue("subtitle selection",selected.get());
                main(()->player.get().setTrackSelectionParameters(player.get().getTrackSelectionParameters().buildUpon().setTrackTypeDisabled(C.TRACK_TYPE_TEXT,true).build()));Thread.sleep(100);main(()->selected.set(player.get().getCurrentTracks().isTypeSelected(C.TRACK_TYPE_TEXT)));assertFalse("subtitle disabled",selected.get());
                main(()->player.get().setTrackSelectionParameters(player.get().getTrackSelectionParameters().buildUpon().setTrackTypeDisabled(C.TRACK_TYPE_TEXT,false).build()));
            }
            for(double fraction:new double[]{0,.25,.5,.9,.99}){long position=(long)(duration.get()*fraction);main(()->player.get().seekTo(position));settle(player,failure,position,true);}
            main(()->{player.get().seekTo(2000);player.get().play();});Thread.sleep(3000);main(()->player.get().pause());assertNull(failure.get());System.out.println("D1 cue_events="+cues.get()+" (visual glyph/PTS accuracy requires manual probe)");metric("playback");
        }finally{main(()->{if(player.get()!=null)player.get().release();if(surface.get()!=null)surface.get().release();if(texture.get()!=null)texture.get().release();});leases.retire(generation);boolean released=leases.awaitReleased(generation,10000);if(released)runtime.close();assertTrue("actual all input consumers drained",released);}
    }
    private void settle(AtomicReference<ExoPlayer> player,AtomicReference<PlaybackException> error,long expected,boolean checkPosition)throws Exception{
        long stop=System.nanoTime()+TimeUnit.SECONDS.toNanos(30);while(System.nanoTime()<stop){AtomicBoolean ready=new AtomicBoolean();main(()->ready.set(player.get().getPlaybackState()==Player.STATE_READY && (!checkPosition || Math.abs(player.get().getCurrentPosition()-expected)<500)));assertNull("engine error",error.get());if(ready.get())return;Thread.sleep(50);}fail("prepare/seek deadline");
    }
    @Test public void realEncoderOutput()throws Exception{export("",false);}
    @Test public void outputValidationCounterexamples()throws Exception{
        ValidationSelfCheck.main(new String[0]);
        File source=new File(DeviceFixtures.directory(context()),"basic.mp4");
        try(FileInputStream input=new FileInputStream(source)){
            try{AndroidOutputValidator.validate(input.getFD(),3000);fail("unscaled/unclipped source must not satisfy output preset");}
            catch(IOException expected){assertEquals("OUTPUT_VALIDATION_FAILED",expected.getMessage());}
        }
    }
    @Test public void exportReadyResponseLoss()throws Exception{export("ready-response",false);}
    @Test public void exportWriteFault()throws Exception{export("write",true);}
    @Test public void exportFlushFault()throws Exception{export("flush",true);}
    @Test public void exportValidationFault()throws Exception{export("validate",true);}
    private boolean chainHas(Throwable e,String marker){for(int i=0;e!=null && i<20;i++,e=e.getCause())if(e.getMessage()!=null && e.getMessage().contains(marker))return true;return false;}
    private void export(String fault,boolean expectFailure)throws Exception{
        File inputFile=new File(DeviceFixtures.directory(context()),"basic.mp4");byte[] sourceBefore=java.security.MessageDigest.getInstance("SHA-256").digest(java.nio.file.Files.readAllBytes(inputFile.toPath()));
        String id=UUID.randomUUID().toString();LeaseRegistry leases=new LeaseRegistry();long generation=leases.create();AsyncReadBridge.Runtime runtime=new AsyncReadBridge.Runtime();File output=new File(context().getCacheDir(),"d1_c03_"+id+".mp4");AuthorizedSink host=new AuthorizedSink(output,id);host.inject(fault);SinkCoordinator coordinator=new SinkCoordinator(id,host,5000);coordinator.start();
        AtomicReference<Transformer> transformer=new AtomicReference<>();AtomicReference<ExportException> failure=new AtomicReference<>();CountDownLatch done=new CountDownLatch(1);
        try{
            main(()->{Transformer t=MediaEngine.transformer(context(),runtime,leases,generation,DeviceFixtures.routes(context()),host,new Transformer.Listener(){public void onCompleted(Composition c,ExportResult result){done.countDown();}public void onError(Composition c,ExportResult result,ExportException e){failure.set(e);done.countDown();}});transformer.set(t);
                MediaItem item=new MediaItem.Builder().setUri(MediaEngine.MP4).setClippingConfiguration(new MediaItem.ClippingConfiguration.Builder().setStartPositionMs(500).setEndPositionMs(3500).build()).build();
                EditedMediaItem edited=new EditedMediaItem.Builder(item).setEffects(new Effects(List.of(),List.of(Presentation.createForHeight(144)))).build();t.start(edited,host.authorizedBackendPath());});
            assertTrue("real encoder deadline",done.await(90,TimeUnit.SECONDS));
            if(failure.get()!=null){
                assertTrue("codec/source failure before target injection must FAIL: code="+failure.get().errorCode,expectFailure && (fault.equals("write") || fault.equals("flush")));
                assertEquals("requested injection actually hit",fault,host.injectionStage());assertEquals("exactly one injected failure",1,host.injectionHits());
                assertTrue("correct injected error chain",chainHas(failure.get(),"D1_INJECTED_OUTPUT_"+fault.toUpperCase(java.util.Locale.ROOT)));
                if(fault.equals("flush"))assertTrue("encoded bytes before finalize injection",host.bytes()>0);
                System.out.println("D1 INJECTION stage="+host.injectionStage()+" hits="+host.injectionHits()+" code="+failure.get().errorCode);coordinator.abortBeforeReady();assertFalse(host.ready());assertFalse(output.exists());return;
            }
            if(expectFailure && !fault.equals("validate"))fail("target write/flush injection did not fail engine");
            coordinator.validating();boolean valid=host.validate(3000);
            if(expectFailure){try{coordinator.finalizeReady(valid);fail("fault unexpectedly ready");}catch(IOException expected){assertEquals("OUTPUT_VALIDATION_FAILED",expected.getMessage());assertEquals("validate",host.injectionStage());assertEquals(1,host.injectionHits());assertTrue("validation reached after finalized encoded output",host.flushes()>0 && host.bytes()>0);assertFalse(host.ready());assertFalse(output.exists());System.out.println("D1 INJECTION stage=validate hits=1 code="+expected.getMessage());}}
            else{assertEquals("normal output has no fault hits",0,host.injectionHits());assertTrue("preset samples and video decoder validated",valid);if(fault.equals("ready-response")){try{coordinator.finalizeReady(valid);fail("expected response-loss injection");}catch(IOException expected){assertEquals("OUTPUT_READY_UNKNOWN",expected.getMessage());}assertEquals(SinkCoordinator.State.READY,coordinator.reconcile());}else coordinator.finalizeReady(valid);
                assertTrue("validated real H264 output",host.ready());assertTrue("FD fsync performed",host.flushes()>0);assertTrue("encoded sample bytes",host.bytes()>0);assertNotNull(coordinator.token());System.out.println("D1 REAL_ENCODER bytes="+output.length()+" task="+id+" revision=clipped-scaled-144h");}
            if(host.ready()){AuthorizedSink recovered=new AuthorizedSink(output,id);assertEquals(SinkCoordinator.HostState.READY,recovered.query(id).toCompletableFuture().get().state);assertEquals(coordinator.token(),recovered.markReady(id).toCompletableFuture().get());}
            metric("export");
        }finally{main(()->{if(transformer.get()!=null)transformer.get().cancel();});leases.retire(generation);boolean released=leases.awaitReleased(generation,10000);if(released)runtime.close();coordinator.closeExecutor();if(!host.ready())host.abort(id).toCompletableFuture().get(5,TimeUnit.SECONDS);assertTrue("export input lease drained",released);assertArrayEquals("source bytes unchanged after export/failure",sourceBefore,java.security.MessageDigest.getInstance("SHA-256").digest(java.nio.file.Files.readAllBytes(inputFile.toPath())));}
    }
    @Test public void realPipelineImmediateCancel()throws Exception{
        String id=UUID.randomUUID().toString();LeaseRegistry leases=new LeaseRegistry();long generation=leases.create();AsyncReadBridge.Runtime runtime=new AsyncReadBridge.Runtime();File output=new File(context().getCacheDir(),"d1_c03_"+id+".mp4");AuthorizedSink sink=new AuthorizedSink(output,id);AtomicBoolean completed=new AtomicBoolean();
        main(()->{Transformer t=MediaEngine.transformer(context(),runtime,leases,generation,DeviceFixtures.routes(context()),sink,new Transformer.Listener(){public void onCompleted(Composition c,ExportResult result){completed.set(true);}});
            t.start(new EditedMediaItem.Builder(MediaEngine.item(MediaEngine.MP4,false)).setEffects(new Effects(List.of(),List.of(Presentation.createForHeight(144)))).build(),sink.authorizedBackendPath());t.cancel();});
        leases.retire(generation);boolean released=leases.awaitReleased(generation,10000);if(released)runtime.close();sink.abort(id).toCompletableFuture().get(5,TimeUnit.SECONDS);assertTrue(released);assertFalse("cancelled pipeline must not complete",completed.get());assertFalse(sink.ready());assertFalse(output.exists());
        System.out.println("D1 actual Transformer immediate cancellation; mid-encode cancellation still requires device observation");
    }
    @Test public void writingJournalRecovery()throws Exception{
        String id=UUID.randomUUID().toString();File output=new File(context().getCacheDir(),"d1_c03_"+id+".mp4");new AuthorizedSink(output,id);
        try(FileOutputStream partial=new FileOutputStream(output)){partial.write(new byte[]{0,1,2,3});}
        AuthorizedSink recovered=new AuthorizedSink(output,id);assertEquals(SinkCoordinator.HostState.WRITING,recovered.query(id).toCompletableFuture().get().state);
        recovered.abort(id).toCompletableFuture().get();assertFalse(output.exists());assertEquals(SinkCoordinator.HostState.ABORTED,recovered.query(id).toCompletableFuture().get().state);
        System.out.println("D1 partial-output host journal recovery; this is not an actual process-kill experiment");
    }
    @Test public void isolatedWorkerDeathAndTimeout()throws Exception{
        LeaseRegistry leases=new LeaseRegistry();try(AsyncReadBridge.Runtime runtime=new AsyncReadBridge.Runtime()){
            for(int mode:new int[]{WorkerProtocol.NORMAL,WorkerProtocol.PRESSURE,WorkerProtocol.EXIT,WorkerProtocol.SIGSEGV,WorkerProtocol.HANG}){
                long generation=leases.create();AsyncReadBridge source=new AsyncReadBridge(runtime,HostFixtures.file(new File(DeviceFixtures.directory(context()),"basic.mp4").toPath()),leases,generation,5000);
                try(WorkerClient worker=new WorkerClient(context(),UUID.randomUUID().toString(),source,leases)){
                    try{int result=worker.run(mode,0,mode==WorkerProtocol.HANG?1000:10000);assertTrue("normal bounded broker result",mode==WorkerProtocol.NORMAL || mode==WorkerProtocol.PRESSURE);assertEquals(64,result);}
                    catch(IOException e){assertTrue("injected termination only",mode==WorkerProtocol.EXIT || mode==WorkerProtocol.SIGSEGV || mode==WorkerProtocol.HANG);}
                    assertTrue("different UID (isolated, not only process name)",worker.uid()>0 && worker.uid()!=android.os.Process.myUid());assertTrue("distinct PID",worker.pid()>0 && worker.pid()!=android.os.Process.myPid());
                    System.out.println("D1 worker_mode="+mode+" pss_kb="+worker.pssKb()+" pressure_bytes="+worker.pressureBytes());worker.close();assertTrue("observed Binder death",worker.awaitDeath(10000));
                }
                assertTrue("worker source actual drained",leases.awaitReleased(generation,10000));
                // Parent continues execution and independently opens another source after each death.
                long healthy=leases.create();try(AsyncReadBridge other=new AsyncReadBridge(runtime,HostFixtures.file(new File(DeviceFixtures.directory(context()),"basic.mp4").toPath()),leases,healthy,5000)){other.open(0,8);assertEquals(8,other.read(new byte[8],0,8));}leases.retire(healthy);assertTrue(leases.awaitReleased(healthy,5000));
            }
        }
        metric("isolated-worker parent survives");
    }
    @Test public void offlinePlatformFaceFeasibility()throws Exception{
        File video=new File(DeviceFixtures.directory(context()),"subtitle.avi");MediaMetadataRetriever retriever=new MediaMetadataRetriever();Bitmap frame=null;
        try(FileInputStream source=new FileInputStream(video)){retriever.setDataSource(source.getFD());frame=retriever.getScaledFrameAtTime(10000000,MediaMetadataRetriever.OPTION_CLOSEST_SYNC,256,144);assertNotNull("authorized frame decode",frame);int faces=PlatformFaceProbe.detect(frame);System.out.println("D1 platform_face_candidates="+faces+" quality=NOT_RUN(no labeled frame), identity_recognition=none");}
        finally{if(frame!=null)frame.recycle();retriever.release();}
        metric("offline-face feasibility");
    }
}
