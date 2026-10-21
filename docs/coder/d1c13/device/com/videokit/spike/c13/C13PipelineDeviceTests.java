package com.videokit.spike.c13;
import android.content.Context;
import android.os.Bundle;
import androidx.test.ext.junit.runners.AndroidJUnit4;
import androidx.test.platform.app.InstrumentationRegistry;
import org.junit.*;
import org.junit.runner.RunWith;
import java.io.*;
import java.nio.file.*;
import java.security.*;
import java.util.*;
import java.util.concurrent.*;
import static org.junit.Assert.*;

@RunWith(AndroidJUnit4.class)
public final class C13PipelineDeviceTests {
    private Context context(){return InstrumentationRegistry.getInstrumentation().getTargetContext();}
    private Path directory(){return new File(context().getCacheDir(),"d1_c13_pipeline_outputs").toPath();}
    private Path source(String name){return new File(DeviceFixtures.directory(context()),name).toPath();}
    private byte[] hash(Path path)throws Exception{MessageDigest digest=MessageDigest.getInstance("SHA-256");try(InputStream input=Files.newInputStream(path)){byte[] b=new byte[65536];int n;while((n=input.read(b))!=-1)digest.update(b,0,n);}return digest.digest();}
    @Before public void environment(){CpuEnvironment.Snapshot state=CpuEnvironment.inspect(context());Bundle status=new Bundle();status.putString("stream",(state.ready()?"C13_ENVIRONMENT_READY ":"C13_ENVIRONMENT_BLOCKED ")+state.details()+"\n");InstrumentationRegistry.getInstrumentation().sendStatus(0,status);Assume.assumeTrue("ENVIRONMENT_BLOCKED",state.ready());}
    private void capability(RealFramePipeline.Report report){if(report.status.equals("CAPABILITY_BLOCKED")){Bundle status=new Bundle();status.putString("stream","C13_PIPELINE_CAPABILITY_BLOCKED "+report.error+"\n");InstrumentationRegistry.getInstrumentation().sendStatus(0,status);Assume.assumeTrue("CAPABILITY_BLOCKED: public encoder input",false);}}
    private void released(RealFramePipeline.Report report){assertTrue("actual pipeline resource release",report.resourcesReleased);assertTrue(report.sourceReleased);assertTrue(report.codecReleased);assertTrue(report.writerReleased);assertTrue(report.framesReleased);assertEquals(0,report.consumers);assertEquals(0,RealFramePipeline.reservedEncoderOutputSlots());assertTrue(RealFramePipeline.quarantinedIds().isEmpty());}
    private RealFramePipeline.Report run(String file,int kind,String fault)throws Exception{
        byte[] before=hash(source(file));Throwable primary=null;try(RealFramePipeline pipeline=new RealFramePipeline(context(),HostFixtures.file(source(file)),kind,directory(),fault)){RealFramePipeline.Report report=pipeline.await(90000);capability(report);released(report);return report;}catch(Exception|Error failure){primary=failure;throw failure;}finally{try{assertArrayEquals(before,hash(source(file)));}catch(Exception|Error cleanup){if(primary!=null)primary.addSuppressed(cleanup);else throw cleanup;}}
    }
    private RealFramePipeline.Report positive(String file,int kind,String fault)throws Exception{RealFramePipeline.Report report=run(file,kind,fault);assertEquals("READY",report.status);assertNull(report.error);assertNotNull(report.token);assertEquals(PipelineRules.FRAMES,report.received);assertEquals(PipelineRules.FRAMES,report.inputs);assertEquals(PipelineRules.FRAMES,report.outputs);assertEquals(PipelineRules.FRAMES,report.verified);assertTrue(report.bytes>0 && report.bytes<=PipelineRules.MAX_OUTPUT);return report;}
    private void negative(String fault,String expected)throws Exception{RealFramePipeline.Report report=run("basic.mp4",CpuTaskClient.MP4_H264,fault);assertEquals("ABORTED",report.status);assertEquals(expected,report.error);assertNull(report.token);}
    @Test public void pipelineMp4RealFramesVideoOnly()throws Exception{positive("basic.mp4",CpuTaskClient.MP4_H264,"");}
    @Test public void pipelineAviRealFramesVideoOnly()throws Exception{positive("subtitle.avi",CpuTaskClient.AVI_MPEG4,"");}
    @Test public void pipelineRejectsCrossEpochBeforeCopy()throws Exception{negative("frame-epoch","PIPE_FRAME_IDENTITY");}
    @Test public void pipelineRejectsLateFrame()throws Exception{negative("late-frame","PIPE_FRAME_ORDER");}
    @Test public void pipelineQueueSaturationAborts()throws Exception{negative("consumer-slow","PIPE_FRAME_QUEUE_FULL");}
    @Test public void pipelineConsumerLostAborts()throws Exception{negative("consumer-lost","PIPE_CONSUMER_LOST");}
    @Test public void pipelineEncoderInputRejectedNoReady()throws Exception{negative("encoder-reject","PIPE_ENCODER_INPUT_REJECTED");}
    @Test public void pipelineEncoderErrorNoReady()throws Exception{negative("encoder-error","PIPE_ENCODER_INJECTED_ERROR");}
    @Test public void pipelineSinkWriteFailureAborts()throws Exception{
        byte[] before=hash(source("basic.mp4"));try(RealFramePipeline p=new RealFramePipeline(context(),HostFixtures.file(source("basic.mp4")),CpuTaskClient.MP4_H264,directory(),"write")){RealFramePipeline.Report r=p.await(90000);capability(r);released(r);assertEquals("ABORTED",r.status);assertNull(r.token);assertTrue(p.sinkFaultHits()>0);assertTrue(r.error.equals("PIPE_ENCODER_OR_VALIDATION_FAILED") || r.error.equals("PIPE_OUTPUT_FINALIZE_FAILED"));}finally{assertArrayEquals(before,hash(source("basic.mp4")));}
    }
    @Test public void pipelineSinkFlushFailureAborts()throws Exception{negative("flush","PIPE_OUTPUT_FINALIZE_FAILED");}
    @Test public void pipelineCorruptOutputRejectedByIsolatedDecoder()throws Exception{
        RealFramePipeline.Report r=run("basic.mp4",CpuTaskClient.MP4_H264,"validate");assertEquals("ABORTED",r.status);assertNull(r.token);assertTrue(r.error.startsWith("CPU_") || r.error.startsWith("PIPE_OUTPUT_") || r.error.startsWith("PIPE_VERIFY_"));assertEquals(PipelineRules.FRAMES,r.inputs);
    }
    @Test public void pipelineReadyResponseLossSameToken()throws Exception{RealFramePipeline.Report report=positive("basic.mp4",CpuTaskClient.MP4_H264,"ready-response");PipelineOutputSink recovered=new PipelineOutputSink(directory(),report.id,"");try{assertEquals(report.token,recovered.query(report.id).toCompletableFuture().get().token);recovered.abort(report.id).toCompletableFuture().get();assertEquals(SinkCoordinator.HostState.READY,recovered.query(report.id).toCompletableFuture().get().state);assertEquals(report.token,recovered.query(report.id).toCompletableFuture().get().token);}finally{assertTrue(recovered.closeOwner());}}
    @Test public void pipelineDecodeFailureAborts()throws Exception{
        AsyncReadBridge.Provider bad=c->CompletableFuture.completedFuture(HostFixtures.memory(new byte[]{0,1,2,3}));try(RealFramePipeline p=new RealFramePipeline(context(),bad,CpuTaskClient.MP4_H264,directory(),"")){RealFramePipeline.Report r=p.await(90000);capability(r);released(r);assertEquals("ABORTED",r.status);assertEquals(0,r.inputs);assertNull(r.token);assertTrue(r.error.startsWith("CPU_") || r.error.startsWith("PIPE_SOURCE"));}
    }
    @Test public void pipelineCancelInFlightRetainsFrameLease()throws Exception{
        byte[] before=hash(source("basic.mp4"));try(RealFramePipeline p=new RealFramePipeline(context(),HostFixtures.file(source("basic.mp4")),CpuTaskClient.MP4_H264,directory(),"",new CountDownLatch(1))){
            try{if(!p.consumerEntered.await(15,TimeUnit.SECONDS)){RealFramePipeline.Report early=p.await(1000);capability(early);fail("consumer not reached");}InstrumentationRegistry.getInstrumentation().runOnMainSync(p::cancel);RealFramePipeline.Report held=p.query();assertEquals("PENDING",held.status);assertEquals(1,held.consumers);assertFalse(held.framesReleased);assertFalse(held.resourcesReleased);assertEquals(1,RealFramePipeline.reservedEncoderOutputSlots());}
            finally{p.consumerRelease.countDown();}RealFramePipeline.Report r=p.await(20000);released(r);assertEquals("ABORTED",r.status);assertNull(r.token);
        }finally{assertArrayEquals(before,hash(source("basic.mp4")));}
    }
    @Test public void pipelineIndependentCpuSurvivesFailure()throws Exception{
        try(CpuTaskClient second=new CpuTaskClient(context(),HostFixtures.file(source("basic.mp4")))){try{second.start(CpuTaskClient.MP4_H264,2000000,CpuTaskClient.WAIT_FRAME);assertEquals(147456,second.awaitFrame(30000).bytes());RealFramePipeline.Report r=run("basic.mp4",CpuTaskClient.MP4_H264,"consumer-lost");assertEquals("ABORTED",r.status);assertFalse(second.awaitDeath(100));second.resume();assertEquals(147456,second.awaitResult(10000).bytes());}finally{assertTrue(second.stopAndAwait(5000));}}
    }
    @Test public void pipelineRejectsSecondEncoderBeforeCreation()throws Exception{
        try(RealFramePipeline p=new RealFramePipeline(context(),HostFixtures.file(source("basic.mp4")),CpuTaskClient.MP4_H264,directory(),"",new CountDownLatch(1))){try{
            if(!p.consumerEntered.await(15,TimeUnit.SECONDS)){RealFramePipeline.Report early=p.await(1000);capability(early);fail("consumer not reached");}
            try{new RealFramePipeline(context(),HostFixtures.file(source("basic.mp4")),CpuTaskClient.MP4_H264,directory(),"");fail("second encoder admitted");}catch(IOException expected){assertEquals("PIPE_ENCODER_OUTPUT_BUDGET_BUSY",expected.getMessage());}
        }finally{p.cancel();p.consumerRelease.countDown();}released(p.await(20000));}
    }
    @Test public void pipelineOwnerRecoveryFencesIncompleteWriting()throws Exception{
        String id=UUID.randomUUID().toString();PipelineOutputSink first=new PipelineOutputSink(directory(),id,"");first.open();
        try{try{new PipelineOutputSink(directory(),id,"");fail("live owner replaced");}catch(IOException expected){assertEquals("OUTPUT_OWNER_BUSY",expected.getMessage());}assertTrue(first.closeHandles());}
        finally{assertTrue(first.closeOwner());}
        PipelineOutputSink recovered=new PipelineOutputSink(directory(),id,"");try{assertEquals(SinkCoordinator.HostState.WRITING,recovered.query(id).toCompletableFuture().get().state);recovered.abort(id).toCompletableFuture().get();assertEquals(SinkCoordinator.HostState.ABORTED,recovered.query(id).toCompletableFuture().get().state);assertNull(recovered.query(id).toCompletableFuture().get().token);}finally{assertTrue(recovered.closeOwner());}
    }
}
