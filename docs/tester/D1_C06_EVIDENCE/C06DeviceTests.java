package com.videokit.spike.c06;

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
public final class C06DeviceTests {
    private void main(Runnable r)throws IOException{try{BoundedDispatch.run(command->new android.os.Handler(android.os.Looper.getMainLooper()).post(command),r,5000);}catch(IOException e){StageLog.failure("MAIN_DISPATCH_FAILED",e);StageLog.mainBlocked();throw e;}}
    private android.content.Context context(){return InstrumentationRegistry.getInstrumentation().getTargetContext();}
    private void metric(String label){PowerManager power=(PowerManager)context().getSystemService(android.content.Context.POWER_SERVICE);System.out.println("D1 "+label+" pss_kb="+Debug.getPss()+" thermal="+power.getCurrentThermalStatus()+" api="+android.os.Build.VERSION.SDK_INT+" abi="+android.os.Build.SUPPORTED_ABIS[0]);}
    @Test public void playbackMp4()throws Exception{playback(MediaEngine.MP4,false,false);}
    @Test public void playbackAviWithoutSrt()throws Exception{playback(MediaEngine.AVI,false,false);}
    @Test public void playbackAviSrt()throws Exception{playback(MediaEngine.AVI,true,true);}
    @Test public void playbackMkvAss()throws Exception{playback(MediaEngine.MKV,false,true);}
    private void playback(String uri,boolean srt,boolean textExpected)throws Exception{
        LeaseRegistry leases=new LeaseRegistry();long generation=leases.create();AsyncReadBridge.Runtime runtime=new AsyncReadBridge.Runtime();
        AtomicReference<ExoPlayer> player=new AtomicReference<>();AtomicReference<PlaybackException> failure=new AtomicReference<>();AtomicReference<Surface> surface=new AtomicReference<>();AtomicReference<SurfaceTexture> texture=new AtomicReference<>();AtomicInteger cues=new AtomicInteger();RoutingDataSource.Group sourceGroup=new RoutingDataSource.Group();
        try{
            StageLog.event("PREPARE_MAIN_POST","srt="+srt);main(()->{StageLog.event("PREPARE_MAIN_ENTER","");ExoPlayer p=MediaEngine.player(context(),runtime,leases,generation,DeviceFixtures.routes(context()),sourceGroup);player.set(p);p.setVolume(0);p.addListener(new Player.Listener(){public void onPlayerError(PlaybackException e){failure.set(e);}public void onCues(CueGroup group){if(!group.cues.isEmpty())cues.incrementAndGet();}});
                p.addListener(new Player.Listener(){public void onPlaybackStateChanged(int state){StageLog.event("PLAYER_STATE","state="+state);}public void onPlayerError(PlaybackException error){StageLog.event("PLAYER_ERROR_CODE","code="+error.errorCode);StageLog.failure("PLAYER_ERROR",error);}});
                SurfaceTexture t=new SurfaceTexture(false);t.setDefaultBufferSize(624,352);texture.set(t);Surface s=new Surface(t);surface.set(s);p.setVideoSurface(s);p.setMediaItem(MediaEngine.item(uri,srt));StageLog.event("PREPARE_CALL_BEGIN","");p.prepare();StageLog.event("PREPARE_CALL_RETURN","");});
            settle(player,failure,0,false);AtomicReference<String> audioStatus=new AtomicReference<>();main(()->audioStatus.set(AudioDiagnostics.tracks(player.get().getCurrentTracks())));assertEquals("required audio path; muted test does not establish actual sound","AUDIO_PATH_SELECTED_SOUND_NOT_VERIFIED",audioStatus.get());AtomicLong duration=new AtomicLong();main(()->duration.set(player.get().getDuration()));assertTrue("duration",duration.get()>0);
            if(textExpected){AtomicReference<TrackSelectionOverride> override=new AtomicReference<>();main(()->{for(Tracks.Group group:player.get().getCurrentTracks().getGroups())if(group.getType()==C.TRACK_TYPE_TEXT && group.isTrackSupported(0)){override.set(new TrackSelectionOverride(group.getMediaTrackGroup(),0));break;}});
                assertNotNull("supported subtitle track",override.get());main(()->player.get().setTrackSelectionParameters(player.get().getTrackSelectionParameters().buildUpon().setTrackTypeDisabled(C.TRACK_TYPE_TEXT,false).setOverrideForType(override.get()).build()));
                Thread.sleep(100);AtomicBoolean selected=new AtomicBoolean();main(()->selected.set(player.get().getCurrentTracks().isTypeSelected(C.TRACK_TYPE_TEXT)));assertTrue("subtitle selection",selected.get());
                main(()->player.get().setTrackSelectionParameters(player.get().getTrackSelectionParameters().buildUpon().setTrackTypeDisabled(C.TRACK_TYPE_TEXT,true).build()));Thread.sleep(100);main(()->selected.set(player.get().getCurrentTracks().isTypeSelected(C.TRACK_TYPE_TEXT)));assertFalse("subtitle disabled",selected.get());
                main(()->player.get().setTrackSelectionParameters(player.get().getTrackSelectionParameters().buildUpon().setTrackTypeDisabled(C.TRACK_TYPE_TEXT,false).build()));
            }
            for(double fraction:new double[]{0,.25,.5,.9,.99}){long position=(long)(duration.get()*fraction);main(()->player.get().seekTo(position));settle(player,failure,position,true);}
            main(()->{player.get().seekTo(2000);player.get().play();});Thread.sleep(3000);main(()->player.get().pause());assertNull(failure.get());System.out.println("D1 cue_events="+cues.get()+" (visual glyph/PTS accuracy requires manual probe)");metric("playback");
        }finally{sourceGroup.cancel();leases.retire(generation);IOException releaseError=null;try{StageLog.event("RELEASE_MAIN_BEGIN","");main(()->{if(player.get()!=null)player.get().release();if(surface.get()!=null)surface.get().release();if(texture.get()!=null)texture.get().release();});StageLog.event("RELEASE_MAIN_DONE","");}catch(IOException e){releaseError=e;StageLog.failure("GRAPHICS_RELEASE_UNKNOWN",e);}boolean released=leases.awaitReleased(generation,10000);StageLog.event("SOURCE_RELEASE_QUERY","released="+released+" operations="+leases.query(generation).operations+" consumers="+leases.query(generation).consumers);if(released)runtime.close();assertTrue("actual all input consumers drained",released);if(releaseError!=null)throw releaseError;}
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
        String id=UUID.randomUUID().toString();LeaseRegistry leases=new LeaseRegistry();long generation=leases.create();AsyncReadBridge.Runtime runtime=new AsyncReadBridge.Runtime();File output=new File(context().getCacheDir(),"d1_c06_"+id+".mp4");AuthorizedSink host=new AuthorizedSink(output,id);host.inject(fault);SinkCoordinator coordinator=new SinkCoordinator(id,host,5000);coordinator.start();
        AtomicReference<Transformer> transformer=new AtomicReference<>();AtomicReference<ExportException> failure=new AtomicReference<>();CountDownLatch done=new CountDownLatch(1);
        try{
            main(()->{Transformer t=MediaEngine.transformer(context(),runtime,leases,generation,DeviceFixtures.routes(context()),host,new Transformer.Listener(){public void onCompleted(Composition c,ExportResult result){done.countDown();}public void onError(Composition c,ExportResult result,ExportException e){failure.set(e);done.countDown();}});transformer.set(t);
                MediaItem item=new MediaItem.Builder().setUri(MediaEngine.MP4).setClippingConfiguration(new MediaItem.ClippingConfiguration.Builder().setStartPositionMs(500).setEndPositionMs(3500).build()).build();
                EditedMediaItem edited=new EditedMediaItem.Builder(item).setEffects(new Effects(List.of(),List.of(Presentation.createForHeight(144)))).build();t.start(edited,host.authorizedBackendPath());});
            assertTrue("real encoder deadline",done.await(90,TimeUnit.SECONDS));
            if(failure.get()!=null){
                StageLog.failure("HOST_EXPORT_ERROR_"+failure.get().errorCode,failure.get());if(!expectFailure)throw new AssertionError("NORMAL_EXPORT_FAILED code="+failure.get().errorCode,failure.get());
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
        String id=UUID.randomUUID().toString();LeaseRegistry leases=new LeaseRegistry();long generation=leases.create();AsyncReadBridge.Runtime runtime=new AsyncReadBridge.Runtime();File output=new File(context().getCacheDir(),"d1_c06_"+id+".mp4");AuthorizedSink sink=new AuthorizedSink(output,id);AtomicBoolean completed=new AtomicBoolean();
        main(()->{Transformer t=MediaEngine.transformer(context(),runtime,leases,generation,DeviceFixtures.routes(context()),sink,new Transformer.Listener(){public void onCompleted(Composition c,ExportResult result){completed.set(true);}});
            t.start(new EditedMediaItem.Builder(MediaEngine.item(MediaEngine.MP4,false)).setEffects(new Effects(List.of(),List.of(Presentation.createForHeight(144)))).build(),sink.authorizedBackendPath());t.cancel();});
        leases.retire(generation);boolean released=leases.awaitReleased(generation,10000);if(released)runtime.close();sink.abort(id).toCompletableFuture().get(5,TimeUnit.SECONDS);assertTrue(released);assertFalse("cancelled pipeline must not complete",completed.get());assertFalse(sink.ready());assertFalse(output.exists());
        System.out.println("D1 actual Transformer immediate cancellation; mid-encode cancellation still requires device observation");
    }
    @Test public void writingJournalRecovery()throws Exception{
        String id=UUID.randomUUID().toString();File output=new File(context().getCacheDir(),"d1_c06_"+id+".mp4");new AuthorizedSink(output,id);
        try(FileOutputStream partial=new FileOutputStream(output)){partial.write(new byte[]{0,1,2,3});}
        AuthorizedSink recovered=new AuthorizedSink(output,id);assertEquals(SinkCoordinator.HostState.WRITING,recovered.query(id).toCompletableFuture().get().state);
        recovered.abort(id).toCompletableFuture().get();assertFalse(output.exists());assertEquals(SinkCoordinator.HostState.ABORTED,recovered.query(id).toCompletableFuture().get().state);
        System.out.println("D1 partial-output host journal recovery; this is not an actual process-kill experiment");
    }
    @Test public void isolatedWorkerDeathAndTimeout()throws Exception{
        for(int mode:new int[]{WorkerProtocol.NORMAL,WorkerProtocol.PRESSURE,WorkerProtocol.EXIT})brokerCase(mode);
    }
    @Test public void isolatedBrokerSigsegvIndependently()throws Exception{brokerCase(WorkerProtocol.NORMAL);brokerCase(WorkerProtocol.SIGSEGV);}
    @Test public void isolatedBrokerHangIndependently()throws Exception{brokerCase(WorkerProtocol.NORMAL);brokerCase(WorkerProtocol.HANG);}
    private void brokerCase(int mode)throws Exception{
        LeaseRegistry leases=new LeaseRegistry();long generation=leases.create();AsyncReadBridge.Runtime runtime=new AsyncReadBridge.Runtime();
        AsyncReadBridge source=new AsyncReadBridge(runtime,HostFixtures.file(new File(DeviceFixtures.directory(context()),"basic.mp4").toPath()),leases,generation,5000);
        WorkerClient worker=new WorkerClient(context(),UUID.randomUUID().toString(),source,leases);Throwable problem=null;
        try{
            long began=System.nanoTime();IOException actual=null;Integer value=null;
            try{value=worker.run(mode,0,mode==WorkerProtocol.HANG?1000:10000);}catch(IOException error){actual=error;StageLog.failure("BROKER_CASE_ERROR",error);}
            assertTrue("different UID/PID",worker.uid()>0 && worker.uid()!=android.os.Process.myUid() && worker.pid()>0 && worker.pid()!=android.os.Process.myPid());
            assertEquals(mode,worker.eventMode());assertEquals(1,worker.eventHits());
            if(mode==WorkerProtocol.NORMAL || mode==WorkerProtocol.PRESSURE){if(actual!=null)throw new AssertionError("NORMAL_OR_PRESSURE_FAILED",actual);assertEquals(Integer.valueOf(64),value);}
            else{
                assertNotNull("fault must not return a normal RPC result",actual);assertNull(value);
                assertEquals(mode==WorkerProtocol.HANG?"HANG_WAIT_BEGIN":mode==WorkerProtocol.SIGSEGV?"SIGSEGV_ARMED":"EXIT_ARMED",worker.eventPhase());
                if(mode==WorkerProtocol.HANG){assertEquals("WORKER_TIMEOUT",actual.getMessage());assertTrue("bounded hang wait",TimeUnit.NANOSECONDS.toMillis(System.nanoTime()-began)<10000);}
                assertTrue("actual death before test cleanup",worker.awaitDeath(10000));
                ExitEvidence exit=ExitEvidence.collect(context(),worker.pid(),worker.uid(),worker.bindStartedAt());exit.log();
                if(mode==WorkerProtocol.SIGSEGV)assertTrue("OS PID/UID/time matched SIGSEGV, not mere mode entry or cleanup kill",exit.isSignal(11));
            }
        }catch(Throwable failure){problem=failure;}
        finally{
            worker.close();boolean died=worker.awaitDeath(10000),released=leases.awaitReleased(generation,10000);
            StageLog.event("BROKER_FINAL_STATE","mode="+mode+" pid="+worker.pid()+" uid="+worker.uid()+" phase="+worker.eventPhase()+" death="+died+" source_released="+released+" operations="+leases.query(generation).operations+" consumers="+leases.query(generation).consumers+" failed_closes="+leases.query(generation).failedCloses);
            if(released)runtime.close();else StageLog.event("BROKER_SOURCE_QUARANTINE","");
            if(!died || !released){AssertionError cleanup=new AssertionError("BROKER_FINAL_RELEASE_UNKNOWN");if(problem==null)problem=cleanup;else problem.addSuppressed(cleanup);}
        }
        if(problem!=null)throw new AssertionError("BROKER_CASE_FAILED mode="+mode,problem);
        long healthy=leases.create();try(AsyncReadBridge.Runtime checkRuntime=new AsyncReadBridge.Runtime();AsyncReadBridge other=new AsyncReadBridge(checkRuntime,HostFixtures.file(new File(DeviceFixtures.directory(context()),"basic.mp4").toPath()),leases,healthy,5000)){other.open(0,8);assertEquals(8,other.read(new byte[8],0,8));}leases.retire(healthy);assertTrue(leases.awaitReleased(healthy,5000));
    }
    @Test public void videoFrameCaptureMp4Control()throws Exception{
        Bitmap frame=frameViaCapturePipeline(MediaEngine.MP4,2000000);try{assertNotNull("same capture contract MP4 pipeline control",frame);}finally{if(frame!=null)frame.recycle();}
    }
    @Test public void offlinePlatformFaceFeasibility()throws Exception{
        Bitmap control=null,frame=null;
        try{control=AuthorizedFrameProbe.read(new File(DeviceFixtures.directory(context()),"basic.mp4"),2000000,20000);assertNotNull("same-device MP4 control",control);
            try{frame=AuthorizedFrameProbe.read(new File(DeviceFixtures.directory(context()),"subtitle.avi"),10000000,20000);}
            catch(IOException platform){StageLog.failure("AVI_PLATFORM_FRAME_LIMIT",platform);if(!"FRAME_AT_REQUESTED_TIME_UNAVAILABLE".equals(platform.getMessage()))throw platform;}
            if(frame==null)frame=frameViaCapturePipeline(MediaEngine.AVI,10000000);
            assertNotNull("AVI source requested time must decode; no null/MP4-only substitute",frame);int faces=PlatformFaceProbe.detect(frame);System.out.println("D1 platform_face_candidates="+faces+" requested_source_pts_us=10000000 actual_source_frame_pts=UNKNOWN quality=NOT_RUN");}
        finally{if(control!=null)control.recycle();if(frame!=null)frame.recycle();}metric("offline-face feasibility");
    }
    private Bitmap frameViaCapturePipeline(String uri,long requestedUs)throws Exception{
        CaptureInputKind kind=CaptureInputKind.fromRoute(uri);FrameWindow window=FrameWindow.at(requestedUs);File[] retained=context().getCacheDir().listFiles((dir,name)->name.startsWith("d1_c06_capture_") && name.endsWith(".capture"));
        if(retained==null || retained.length>=2)throw new IOException("FRAME_CLIP_CACHE_BUDGET_REVIEW_REQUIRED");
        String id=UUID.randomUUID().toString();File output=new File(context().getCacheDir(),"d1_c06_capture_"+id+".mp4");VideoFrameSink sink=new VideoFrameSink(output,id);
        LeaseRegistry leases=new LeaseRegistry();long generation=leases.create();AsyncReadBridge.Runtime runtime=new AsyncReadBridge.Runtime();RoutingDataSource.Group group=new RoutingDataSource.Group();
        AtomicReference<Transformer> active=new AtomicReference<>();AtomicReference<ExportException> failure=new AtomicReference<>();CountDownLatch done=new CountDownLatch(1);Bitmap bitmap=null;boolean delivered=false;
        try{
            StageLog.event("FRAME_CAPTURE_PLAN","source="+kind+" contract=VIDEO_CAPTURE_ONLY source_requested_us="+requestedUs+" clip_start_ms="+window.startMs+" clip_end_ms="+window.endMs+" requested_clip_us="+window.localUs+" actual_source_frame_pts=UNKNOWN watchdog_ms=10000");
            main(()->{Transformer transformer=MediaEngine.captureTransformer(context(),runtime,leases,generation,DeviceFixtures.routes(context()),sink,new Transformer.Listener(){public void onCompleted(Composition c,ExportResult r){done.countDown();}public void onError(Composition c,ExportResult r,ExportException e){failure.set(e);done.countDown();}},group,kind);active.set(transformer);
                MediaItem item=new MediaItem.Builder().setUri(uri).setClippingConfiguration(new MediaItem.ClippingConfiguration.Builder().setStartPositionMs(window.startMs).setEndPositionMs(window.endMs).build()).build();
                transformer.start(new EditedMediaItem.Builder(item).setRemoveAudio(true).setEffects(new Effects(List.of(),List.of(Presentation.createForHeight(144)))).build(),sink.path());});
            if(!done.await(90,TimeUnit.SECONDS))throw new IOException("FRAME_CAPTURE_TIMEOUT");if(failure.get()!=null){StageLog.failure("FRAME_CAPTURE_FAILED",failure.get());throw new IOException("FRAME_CAPTURE_FAILED",failure.get());}
            if(!sink.validate(3000) || !sink.validated() || sink.samples()==0 || sink.bytes()==0)throw new IOException("FRAME_CAPTURE_UNVALIDATED");
            StageLog.event("FRAME_CAPTURE_VIDEO_VALIDATED","source="+kind+" video_tracks=1 audio_tracks=0 sample_pts_and_full_decode=true product_ready=false");
            bitmap=AuthorizedFrameProbe.readClosest(output,window.localUs,20000);if(bitmap==null)throw new IOException("FRAME_CAPTURE_FRAME_UNAVAILABLE");
            StageLog.event("FRAME_CAPTURE_RESULT","source="+kind+" requested_source_us="+requestedUs+" requested_clip_us="+window.localUs+" actual_source_frame_pts=UNKNOWN quality=NOT_RUN cache_retained=true");delivered=true;return bitmap;
        }finally{
            group.cancel();leases.retire(generation);IOException cleanup=null;boolean cancelReturned=false;try{main(()->{if(active.get()!=null)active.get().cancel();});cancelReturned=true;}catch(IOException error){cleanup=error;StageLog.failure("FRAME_CAPTURE_RELEASE_UNKNOWN",error);}
            boolean outputClosed=cancelReturned && sink.closeForQuarantine();boolean released=leases.awaitReleased(generation,10000);if(released && cancelReturned)runtime.close();StageLog.event("FRAME_CAPTURE_FINAL_STATE","source="+kind+" source_released="+released+" output_retained=true transformer_cancel_returned="+cancelReturned+" output_descriptors_closed="+outputClosed);
            if(!released || !outputClosed || cleanup!=null){if(bitmap!=null)bitmap.recycle();throw new IOException("FRAME_CAPTURE_RESOURCE_QUARANTINE",cleanup);}if(!delivered && bitmap!=null)bitmap.recycle();
        }
    }
}
