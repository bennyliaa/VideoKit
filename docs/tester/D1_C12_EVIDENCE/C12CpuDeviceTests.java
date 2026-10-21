package com.videokit.spike.c12;
import android.content.Context;
import androidx.test.ext.junit.runners.AndroidJUnit4;
import androidx.test.platform.app.InstrumentationRegistry;
import org.junit.*;
import org.junit.runner.RunWith;
import java.io.*;
import java.nio.file.Files;
import java.security.MessageDigest;
import java.util.concurrent.*;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import static org.junit.Assert.*;

/** One-APK CPU group. Prepared/compiled locally only; no companion or platform compressed parser. */
@RunWith(AndroidJUnit4.class)
public final class C12CpuDeviceTests {
    private final ThreadLocal<Throwable> primaryFailure=new ThreadLocal<>();
    private void recordPrimary(Throwable error){if(primaryFailure.get()==null)primaryFailure.set(error);StageLog.failure("CPU_CASE_PRIMARY",error);}
    @Before public void environment(){
        primaryFailure.remove();CpuEnvironment.Snapshot state=CpuEnvironment.inspect(context());android.os.Bundle status=new android.os.Bundle();
        status.putString("stream",(state.ready()?"C12_ENVIRONMENT_READY ":"C12_ENVIRONMENT_BLOCKED ")+state.details()+"\n");InstrumentationRegistry.getInstrumentation().sendStatus(0,status);
        Assume.assumeTrue("ENVIRONMENT_BLOCKED: installed App/component/service state",state.ready());
    }
    @Test public void cpuEnvironmentPreflight(){assertTrue(CpuEnvironment.inspect(context()).ready());}
    private Context context(){return InstrumentationRegistry.getInstrumentation().getTargetContext();}
    private File file(String name){return new File(DeviceFixtures.directory(context()),name);}
    private AsyncReadBridge.Provider provider(String name){return HostFixtures.file(file(name).toPath());}
    private byte[] hash(String name)throws Exception {
        MessageDigest digest=MessageDigest.getInstance("SHA-256");try(InputStream in=Files.newInputStream(file(name).toPath())){byte[] bytes=new byte[65536];int n;while((n=in.read(bytes))!=-1)digest.update(bytes,0,n);}return digest.digest();
    }
    private void identity(CpuTaskClient task){assertTrue(task.workerPid()>0 && task.workerPid()!=android.os.Process.myPid());assertTrue(task.workerUid()>0 && task.workerUid()!=android.os.Process.myUid());}
    private void released(CpuTaskClient task)throws Exception {
        try{
            assertTrue("CPU_CLEANUP_UNPROVEN: primary retained independently",task.stopAndAwait(5000));
            CpuLifecycle.Snapshot state=task.lifecycle();assertTrue(state.noWorkerProven() || state.actualDeath);assertTrue(state.slotReleased);assertEquals(0,state.pendingCalls);assertFalse(state.stopPending);
            LeaseRegistry.Snapshot ledger=task.sourceLedger();assertTrue(ledger.released());assertEquals(0,ledger.operations);assertEquals(0,ledger.consumers);assertEquals(0,ledger.failedCloses);
        }catch(Exception|Error cleanup){StageLog.failure("CPU_CASE_CLEANUP_FAILED",cleanup);Throwable primary=primaryFailure.get();if(primary!=null && primary!=cleanup){primary.addSuppressed(cleanup);return;}throw cleanup;}
    }
    private void cleanupPreserving(CpuDiagnostics.Action action)throws Exception {
        try{action.run();}catch(Throwable cleanup){Throwable primary=primaryFailure.get();if(primary!=null && primary!=cleanup){primary.addSuppressed(cleanup);StageLog.failure("CPU_CASE_SUPPRESSED_CLEANUP",cleanup);return;}if(cleanup instanceof Exception)throw (Exception)cleanup;if(cleanup instanceof Error)throw (Error)cleanup;throw new AssertionError(cleanup);}
    }
    private void releaseBoth(CpuTaskClient first,CpuTaskClient second)throws Exception {cleanupPreserving(()->CpuDiagnostics.preserving(()->released(first),()->released(second)));}
    private void frame(CpuTaskClient.Frame frame,long target){assertEquals(147456,frame.bytes());assertEquals(1024,frame.stride);assertTrue(frame.ptsUs>=target && frame.ptsUs<=target+2000000);byte[] rgba=frame.copyPixels();boolean nonzero=false;for(byte b:rgba)if(b!=0){nonzero=true;break;}assertTrue("decoded pixel payload is not an empty control message",nonzero);}
    private void normal(String name,int kind,long target)throws Exception {
        byte[] before=hash(name);int host=android.os.Process.myPid();
        try(CpuTaskClient task=new CpuTaskClient(context(),provider(name))){try{task.start(kind,target,CpuTaskClient.NORMAL);identity(task);frame(task.awaitResult(30000),target);assertTrue(task.brokerBytes()>0);assertEquals(0,task.rejections());}catch(Exception|Error primary){recordPrimary(primary);throw primary;}finally{released(task);}}
        assertEquals(host,android.os.Process.myPid());assertArrayEquals(before,hash(name));
    }
    @Test public void cpuCleanupWithoutBindProvesNoWorker()throws Exception {
        try(CpuTaskClient task=new CpuTaskClient(context(),provider("basic.mp4"))){assertTrue(task.stopAndAwait(500));CpuLifecycle.Snapshot s=task.lifecycle();assertTrue(s.noWorkerProven());assertFalse(s.actualDeath);assertTrue(s.slotReleased);assertEquals(0,s.stopAttempts);}
    }
    @Test public void cpuFirstFailureSurvivesCleanupFailure()throws Exception {
        IOException first=new IOException("CPU_HELLO_REJECTED");try{CpuDiagnostics.preserving(()->{throw first;},()->{throw new AssertionError("CPU_CLEANUP_UNPROVEN");});fail("primary lost");}catch(Throwable actual){assertSame(first,actual);assertEquals(1,actual.getSuppressed().length);}
    }
    private void holdUnbind(CpuTaskClient task){task.debugUnbindEntered=new CountDownLatch(1);task.debugUnbindRelease=new CountDownLatch(1);}
    @Test public void cpuRegistrarSynchronousMetadataAndRejects()throws Exception {
        try(CpuTaskClient task=new CpuTaskClient(context(),provider("basic.mp4"))){task.debugRegistrationProbes=true;try{
            task.start(CpuTaskClient.MP4_H264,2000000,CpuTaskClient.WAIT_FRAME);frame(task.awaitFrame(30000),2000000);identity(task);
            long deadline=System.nanoTime()+TimeUnit.SECONDS.toNanos(2);while(task.registrationCount(RegistrationProtocol.ONEWAY)<4 && System.nanoTime()<deadline)Thread.sleep(10);
            assertEquals(1,task.registrationCount(RegistrationProtocol.OK));assertTrue(task.registrationCount(RegistrationProtocol.DUPLICATE)>=5);assertEquals(4,task.registrationCount(RegistrationProtocol.ONEWAY));
            for(int error:new int[]{RegistrationProtocol.CODE,RegistrationProtocol.DESCRIPTOR,RegistrationProtocol.SESSION,RegistrationProtocol.ENDPOINT,RegistrationProtocol.INPUT})assertEquals(RegistrationProtocol.name(error),1,task.registrationCount(error));
            assertEquals(1,task.unresolvedWorkers());assertFalse(task.awaitDeath(100));task.resume();frame(task.awaitResult(10000),2000000);
        }catch(Exception|Error primary){recordPrimary(primary);throw primary;}finally{released(task);}}
    }
    @Test public void cpuRegistrarLocalHostIdentityRejected()throws Exception {
        try(CpuTaskClient task=new CpuTaskClient(context(),provider("basic.mp4"))){try{assertEquals(RegistrationProtocol.IDENTITY,task.debugRegistrarHostIdentity());assertEquals(0,task.unresolvedWorkers());assertFalse(task.lifecycle().identity);}catch(Exception|Error primary){recordPrimary(primary);throw primary;}finally{released(task);}}
    }
    @Test public void cpuRegistrationBadMagicPreservesFirstCause()throws Exception {badRegistrationReply(1,"CPU_REG_REPLY_MAGIC");}
    @Test public void cpuRegistrationTrailingReplyPreservesFirstCause()throws Exception {badRegistrationReply(2,"CPU_REG_REPLY_TRAILING");}
    private void badRegistrationReply(int mode,String expected)throws Exception {
        try(CpuTaskClient task=new CpuTaskClient(context(),provider("basic.mp4"))){task.debugRegistrationReply=mode;try{
            try{task.start(CpuTaskClient.MP4_H264,2000000,CpuTaskClient.NORMAL);fail("bad registration reply started media");}catch(CpuDiagnostics.Failure failure){assertEquals(expected,failure.code);assertEquals("REGISTER",failure.phase);}
            assertEquals(expected,task.lifecycle().firstCode);assertFalse(task.lifecycle().startAck);assertEquals(0,task.nativeStage());assertTrue("fatal registration report revokes Source before cleanup",task.awaitSourceReleased(5000));assertTrue(task.stopAndAwait(5000));assertTrue(task.bindingRevocation().closed);assertTrue(task.lifecycle().actualDeath);assertEquals(expected,task.lifecycle().firstCode);
        }catch(Exception|Error primary){recordPrimary(primary);throw primary;}finally{released(task);}}
    }
    @Test public void cpuCancelBeforeRegistrationClosesBindingAndRetainsUnknown()throws Exception {cancelRegistrationRace(false);}
    @Test public void cpuCancelBeforeBindReturnRevokesLateAcceptance()throws Exception {cancelRegistrationRace(true);}
    private void cancelRegistrationRace(boolean lateReturn)throws Exception {
        ExecutorService executor=Executors.newSingleThreadExecutor();
        try(CpuTaskClient first=new CpuTaskClient(context(),provider("basic.mp4"));CpuTaskClient second=new CpuTaskClient(context(),provider("basic.mp4"))){
            first.debugRegistrationEntered=new CountDownLatch(1);first.debugRegistrationRelease=new CountDownLatch(1);
            if(lateReturn){first.debugBindReturnEntered=new CountDownLatch(1);first.debugBindReturnRelease=new CountDownLatch(1);}
            try{
                second.start(CpuTaskClient.MP4_H264,2000000,CpuTaskClient.WAIT_FRAME);frame(second.awaitFrame(30000),2000000);
                Future<?> starting=executor.submit(()->{try{first.start(CpuTaskClient.MP4_H264,2000000,CpuTaskClient.WAIT_FRAME);throw new AssertionError("cancelled registration started media");}catch(Exception expected){StageLog.failure("CPU_EXPECTED_CANCELLED_REGISTRATION",expected);}});
                assertTrue(first.debugRegistrationEntered.await(5,TimeUnit.SECONDS));if(lateReturn)assertTrue(first.debugBindReturnEntered.await(5,TimeUnit.SECONDS));
                long before=System.nanoTime();InstrumentationRegistry.getInstrumentation().runOnMainSync(first::cancel);assertTrue(TimeUnit.NANOSECONDS.toMillis(System.nanoTime()-before)<1000);if(lateReturn)first.debugBindReturnRelease.countDown();
                long deadline=System.nanoTime()+TimeUnit.SECONDS.toNanos(3);while(!first.bindingRevocation().closed && System.nanoTime()<deadline)Thread.sleep(10);
                assertTrue("unknown bind must revoke without waiting for registration/death",first.bindingRevocation().closed);before=System.nanoTime();assertFalse(first.stopAndAwait(100));assertTrue("cleanup budget cannot wait on start monitor",TimeUnit.NANOSECONDS.toMillis(System.nanoTime()-before)<700);assertFalse(first.lifecycle().slotReleased);assertFalse(first.lifecycle().actualDeath);assertFalse(first.lifecycle().noWorkerProven());assertTrue(first.lifecycle().pendingCalls>0);
                assertEquals(2,CpuTaskClient.reservedCpuSlots());assertTrue("unbind cannot erase the unknown process reservation",CpuTaskClient.globalUnprovenWorkers()>=2);
                try{new CpuTaskClient(context(),provider("basic.mp4"));fail("unknown worker allowed a third task");}catch(IOException expected){assertEquals("CPU_SLOTS_EXHAUSTED_OR_QUARANTINED",expected.getMessage());}
                assertFalse(second.awaitDeath(100));second.resume();frame(second.awaitResult(10000),2000000);
                first.debugRegistrationRelease.countDown();starting.get(6000,TimeUnit.MILLISECONDS);assertFalse(first.lifecycle().startAck);assertTrue(first.stopAndAwait(5000));assertTrue(first.lifecycle().actualDeath);assertEquals(0,first.unresolvedWorkers());
            }catch(Exception|Error primary){recordPrimary(primary);throw primary;}finally{first.debugRegistrationRelease.countDown();if(lateReturn)first.debugBindReturnRelease.countDown();releaseBoth(first,second);}
        }finally{executor.shutdownNow();}
    }
    @Test public void cpuUnbindFailureRequiresExplicitRecovery()throws Exception {
        try(CpuTaskClient task=new CpuTaskClient(context(),provider("basic.mp4"))){try{
            task.start(CpuTaskClient.MP4_H264,2000000,CpuTaskClient.NORMAL);frame(task.awaitResult(30000),2000000);task.debugUnbindFailures.set(1);task.cancel();
            long deadline=System.nanoTime()+TimeUnit.SECONDS.toNanos(3);while((task.bindingRevocation().attempts==0 || task.bindingRevocation().pending) && System.nanoTime()<deadline)Thread.sleep(10);
            assertEquals(1,task.bindingRevocation().attempts);assertFalse(task.bindingRevocation().closed);assertFalse(task.stopAndAwait(100));task.cancel();assertEquals(1,task.bindingRevocation().attempts);assertFalse(task.lifecycle().slotReleased);
            assertTrue(task.recover(5000,false));assertEquals(2,task.bindingRevocation().attempts);assertTrue(task.bindingRevocation().closed);assertTrue(task.lifecycle().actualDeath);
        }catch(Exception|Error primary){recordPrimary(primary);throw primary;}finally{try{if(!task.bindingRevocation().closed)cleanupPreserving(()->{assertTrue(task.recover(5000,false));});}finally{released(task);}}}
    }
    @Test public void cpuStopAckLossStillRequiresActualDeath()throws Exception {
        try(CpuTaskClient task=new CpuTaskClient(context(),provider("basic.mp4"))){holdUnbind(task);try{
            task.start(CpuTaskClient.MP4_H264,2000000,CpuTaskClient.STOP_ACK_LOSS);frame(task.awaitResult(30000),2000000);task.cancel();assertTrue(task.awaitDeath(5000));long stop=System.nanoTime()+TimeUnit.SECONDS.toNanos(3);while(task.lifecycle().stopPending && System.nanoTime()<stop)Thread.sleep(10);assertEquals("CPU_WORKER_ACK_PROTOCOL",task.lifecycle().stopResult);task.debugUnbindRelease.countDown();assertTrue(task.stopAndAwait(5000));CpuLifecycle.Snapshot s=task.lifecycle();assertFalse(s.stopAck);assertTrue(s.actualDeath);assertTrue(s.slotReleased);
        }catch(Exception|Error primary){recordPrimary(primary);throw primary;}finally{task.debugUnbindRelease.countDown();released(task);}}
    }
    @Test public void cpuStalledStopDoesNotConsumeSecondRpcSlot()throws Exception {
        try(CpuTaskClient first=new CpuTaskClient(context(),provider("basic.mp4"));CpuTaskClient second=new CpuTaskClient(context(),provider("basic.mp4"))){holdUnbind(first);try{
            first.start(CpuTaskClient.MP4_H264,2000000,CpuTaskClient.STOP_STALL);frame(first.awaitResult(30000),2000000);
            try{assertFalse(first.stopAndAwait(150));assertTrue(first.lifecycle().stopPending);assertEquals(1,first.lifecycle().stopAttempts);assertFalse(first.recover(100,false));assertEquals(1,first.lifecycle().stopAttempts);second.start(CpuTaskClient.MP4_H264,2000000,CpuTaskClient.NORMAL);frame(second.awaitResult(30000),2000000);}
            catch(Exception|Error primary){recordPrimary(primary);throw primary;}finally{try{cleanupPreserving(first::releaseStopStall);}finally{first.debugUnbindRelease.countDown();}}
        }catch(Exception|Error primary){recordPrimary(primary);throw primary;}finally{first.debugUnbindRelease.countDown();releaseBoth(first,second);}}
    }
    @Test public void cpuCancelFromMainThreadDoesNotBlockSecondTask()throws Exception {
        try(CpuTaskClient first=new CpuTaskClient(context(),provider("basic.mp4"));CpuTaskClient second=new CpuTaskClient(context(),provider("basic.mp4"))){try{
            first.start(CpuTaskClient.MP4_H264,2000000,CpuTaskClient.WAIT_FRAME);second.start(CpuTaskClient.MP4_H264,2000000,CpuTaskClient.WAIT_FRAME);frame(first.awaitFrame(30000),2000000);frame(second.awaitFrame(30000),2000000);
            long before=System.nanoTime();InstrumentationRegistry.getInstrumentation().runOnMainSync(first::cancel);assertTrue(TimeUnit.NANOSECONDS.toMillis(System.nanoTime()-before)<1000);assertTrue(first.stopAndAwait(5000));second.resume();frame(second.awaitResult(10000),2000000);
        }catch(Exception|Error primary){recordPrimary(primary);throw primary;}finally{releaseBoth(first,second);}}
    }
    @Test public void cpuWrongStopEpochRejectedAndTaskContinues()throws Exception {
        try(CpuTaskClient task=new CpuTaskClient(context(),provider("basic.mp4"))){try{task.start(CpuTaskClient.MP4_H264,2000000,CpuTaskClient.WAIT_FRAME);frame(task.awaitFrame(30000),2000000);try{task.probeWrongStopEpochDenied();fail("wrong epoch accepted");}catch(CpuDiagnostics.Failure expected){assertEquals("CPU_TASK_EPOCH_REJECTED",expected.code);}assertFalse(task.awaitDeath(100));task.resume();frame(task.awaitResult(10000),2000000);}catch(Exception|Error primary){recordPrimary(primary);throw primary;}finally{released(task);}}
    }
    @Test public void cpuOnewayStopRejectedAndTaskContinues()throws Exception {
        try(CpuTaskClient task=new CpuTaskClient(context(),provider("basic.mp4"))){try{task.start(CpuTaskClient.MP4_H264,2000000,CpuTaskClient.WAIT_FRAME);frame(task.awaitFrame(30000),2000000);task.probeOnewayStopDenied();int count=0;for(int i=0;i<3 && count==0;i++){Thread.sleep(50);count=task.controlOnewayRejections();}assertTrue(count>0);assertFalse(task.awaitDeath(100));task.resume();frame(task.awaitResult(10000),2000000);}catch(Exception|Error primary){recordPrimary(primary);throw primary;}finally{released(task);}}
    }
    @Test public void cpuMp4H264ActualPtsFrame()throws Exception {normal("basic.mp4",CpuTaskClient.MP4_H264,2000000);}
    @Test public void cpuAviMpeg4ActualPtsFrame()throws Exception {normal("subtitle.avi",CpuTaskClient.AVI_MPEG4,10000000);}
    @Test public void cpuActualAggregateAllocationQuotaAndDecode()throws Exception {
        try(CpuTaskClient task=new CpuTaskClient(context(),provider("basic.mp4"))){try{task.start(CpuTaskClient.MP4_H264,2000000,CpuTaskClient.QUOTA_PROBE);CpuTaskClient.Frame output=task.awaitResult(30000);frame(output,2000000);assertTrue(task.quotaProbeProved());assertEquals(67108864,output.quotaPeakBytes);assertTrue(output.quotaCurrentBytes>=147456);}catch(Exception|Error primary){recordPrimary(primary);throw primary;}finally{released(task);}}
    }
    @Test public void cpuSeekUsesNewEpochAndDecodedTimestamp()throws Exception {
        long priorEpoch;CpuTaskClient.Frame earlier;
        try(CpuTaskClient first=new CpuTaskClient(context(),provider("basic.mp4"))){try{first.start(CpuTaskClient.MP4_H264,2000000,CpuTaskClient.NORMAL);earlier=first.awaitResult(30000);priorEpoch=first.epoch;}finally{released(first);}}
        try(CpuTaskClient next=new CpuTaskClient(context(),provider("basic.mp4"))){try{next.start(CpuTaskClient.MP4_H264,4000000,CpuTaskClient.NORMAL);CpuTaskClient.Frame later=next.awaitResult(30000);frame(later,4000000);assertNotEquals(priorEpoch,next.epoch);assertTrue(later.ptsUs>earlier.ptsUs);
            byte[] firstCopy=later.copyPixels();byte original=firstCopy[0];firstCopy[0]^=1;assertEquals("host frame is immutable to its consumer copy",original,later.copyPixels()[0]);
        }finally{released(next);}}
    }
    private static byte[] chunk(String id,byte[] payload)throws Exception {ByteArrayOutputStream out=new ByteArrayOutputStream();out.write(id.getBytes("US-ASCII"));out.write(ByteBuffer.allocate(4).order(ByteOrder.LITTLE_ENDIAN).putInt(payload.length).array());out.write(payload);if((payload.length&1)!=0)out.write(0);return out.toByteArray();}
    private static byte[] join(byte[]... parts)throws Exception {ByteArrayOutputStream out=new ByteArrayOutputStream();for(byte[] p:parts)out.write(p);return out.toByteArray();}
    private static byte[] avi(int width,int height)throws Exception {
        ByteBuffer avih=ByteBuffer.allocate(56).order(ByteOrder.LITTLE_ENDIAN);avih.putInt(40000).putInt(0).putInt(0).putInt(0).putInt(1).putInt(0).putInt(1).putInt(0).putInt(width).putInt(height);
        ByteBuffer strh=ByteBuffer.allocate(56).order(ByteOrder.LITTLE_ENDIAN);strh.put("vidsXVID".getBytes("US-ASCII")).putInt(0).putShort((short)0).putShort((short)0).putInt(0).putInt(1).putInt(25).putInt(0).putInt(1).putInt(0).putInt(-1).putInt(0);
        ByteBuffer strf=ByteBuffer.allocate(40).order(ByteOrder.LITTLE_ENDIAN);strf.putInt(40).putInt(width).putInt(height).putShort((short)1).putShort((short)24).put("XVID".getBytes("US-ASCII"));
        byte[] strl=chunk("LIST",join("strl".getBytes("US-ASCII"),chunk("strh",strh.array()),chunk("strf",strf.array())));
        byte[] hdrl=chunk("LIST",join("hdrl".getBytes("US-ASCII"),chunk("avih",avih.array()),strl));
        return chunk("RIFF",join("AVI ".getBytes("US-ASCII"),hdrl,chunk("LIST",join("movi".getBytes("US-ASCII"),chunk("00dc",new byte[]{0})))));
    }
    @Test public void cpuOversizedDeclarationRejectedBeforeDecoderOpen()throws Exception {
        byte[] huge=avi(32767,32767);
        try(CpuTaskClient task=new CpuTaskClient(context(),c->CompletableFuture.completedFuture(HostFixtures.memory(huge)))){
            try{task.start(CpuTaskClient.AVI_MPEG4,0,CpuTaskClient.NORMAL);try{task.awaitResult(30000);fail("oversized decoder allocation");}catch(ExecutionException expected){assertEquals("native dimension reject stage before codec alloc/open",6,task.nativeStage());}}
            finally{released(task);}
        }
    }
    @Test public void cpuValidAviHeaderBadPacketRejects()throws Exception {
        byte[] badPacket=avi(320,240);
        try(CpuTaskClient task=new CpuTaskClient(context(),c->CompletableFuture.completedFuture(HostFixtures.memory(badPacket)))){
            try{task.start(CpuTaskClient.AVI_MPEG4,0,CpuTaskClient.NORMAL);try{task.awaitResult(30000);fail("bad compressed packet must not make a frame");}catch(ExecutionException expected){assertTrue("actual codec opened before bad packet",task.nativeStage()>=3 && task.nativeStage()<5);}}
            finally{released(task);}
        }
    }
    @Test public void cpuCancelActiveReadRetainsPendingSourceLedger()throws Exception {
        CountDownLatch readEntered=new CountDownLatch(1);CompletableFuture<Integer> actualRead=new CompletableFuture<>();
        AsyncReadBridge.Provider blocked=c->CompletableFuture.completedFuture(new AsyncReadBridge.Handle(){
            public Long length(){return 100L;}
            public CompletionStage<Integer> readAt(long at,byte[] bytes,int offset,int length,AsyncReadBridge.Cancellation cancel){readEntered.countDown();return actualRead;}
            public CompletionStage<Void> closeAsync(){return CompletableFuture.completedFuture(null);}
        });
        try(CpuTaskClient task=new CpuTaskClient(context(),blocked)){
            try{task.start(CpuTaskClient.MP4_H264,0,CpuTaskClient.NORMAL);assertTrue(readEntered.await(5000,TimeUnit.MILLISECONDS));task.cancel();assertTrue(task.awaitDeath(5000));assertFalse(task.awaitSourceReleased(100));assertTrue(task.sourceLedger().operations>0);
                actualRead.complete(-1);assertTrue(task.awaitSourceReleased(5000));
            }finally{actualRead.complete(-1);released(task);}
        }
    }
    @Test public void cpuTruncatedInputRejectsAndReleases()throws Exception {
        byte[] corrupt=new byte[]{0,0,0,24,'f','t','y','p','i','s','o','m'};
        try(CpuTaskClient task=new CpuTaskClient(context(),c->CompletableFuture.completedFuture(HostFixtures.memory(corrupt)))){
            try{task.start(CpuTaskClient.MP4_H264,0,CpuTaskClient.NORMAL);try{task.awaitResult(30000);fail("truncated must not produce a frame");}catch(ExecutionException expected){assertNotNull(expected.getCause());assertTrue(task.budgetApplied());assertTrue("actual native AVIO read",task.brokerBytes()>0);}}
            finally{released(task);}
        }
    }
    @Test public void cpuWrongDeclaredFormatRejects()throws Exception {
        try(CpuTaskClient task=new CpuTaskClient(context(),provider("basic.mp4"))){try{task.start(CpuTaskClient.AVI_MPEG4,0,CpuTaskClient.NORMAL);try{task.awaitResult(30000);fail("wrong demux/codec contract");}catch(ExecutionException expected){assertNotNull(expected.getCause());assertTrue(task.budgetApplied());assertTrue(task.brokerBytes()>0);}}catch(Exception|Error primary){recordPrimary(primary);throw primary;}finally{released(task);}}
    }
    @Test public void cpuForgedFrameRejectedBeforeHostAllocation()throws Exception {
        try(CpuTaskClient task=new CpuTaskClient(context(),provider("basic.mp4"))){try{task.start(CpuTaskClient.MP4_H264,2000000,CpuTaskClient.FORGE_FRAME);try{task.awaitResult(10000);fail("forged stride must fail");}catch(ExecutionException expected){assertEquals("CPU_PROTOCOL_REJECTED",expected.getCause().getMessage());}assertTrue(task.rejections()>0);}catch(Exception|Error primary){recordPrimary(primary);throw primary;}finally{released(task);}}
    }
    @Test public void cpuForgedEpochAndClaimedIdentityRejected()throws Exception {
        for(int mode:new int[]{CpuTaskClient.FORGE_EPOCH,CpuTaskClient.FORGE_IDENTITY}){
            try(CpuTaskClient task=new CpuTaskClient(context(),provider("basic.mp4"))){try{task.start(CpuTaskClient.MP4_H264,2000000,mode);try{task.awaitResult(10000);fail("forged primitive identity");}catch(ExecutionException expected){assertEquals("CPU_PROTOCOL_REJECTED",expected.getCause().getMessage());}assertTrue(task.rejections()>0);assertEquals(0,task.nativeStage());}catch(Exception|Error primary){recordPrimary(primary);throw primary;}finally{released(task);}}
        }
    }
    @Test public void cpuCompiledH263DoesNotExpandAcceptedInputCodec()throws Exception {
        byte[] h263=avi(320,240);
        for(int i=0;i<=h263.length-4;i++)if(h263[i]=='X' && h263[i+1]=='V' && h263[i+2]=='I' && h263[i+3]=='D'){h263[i]='H';h263[i+1]='2';h263[i+2]='6';h263[i+3]='3';}
        try(CpuTaskClient task=new CpuTaskClient(context(),c->CompletableFuture.completedFuture(HostFixtures.memory(h263)))){
            try{task.start(CpuTaskClient.AVI_MPEG4,0,CpuTaskClient.NORMAL);try{task.awaitResult(30000);fail("H263 registration is not external codec admission");}catch(ExecutionException expected){assertEquals(6,task.nativeStage());}}
            finally{released(task);}
        }
    }
    @Test public void cpuUnknownAndEmptyLengthRejectWithActualClose()throws Exception {
        for(Long length:new Long[]{null,0L}){
            java.util.concurrent.atomic.AtomicBoolean closed=new java.util.concurrent.atomic.AtomicBoolean();int before=CpuTaskClient.quarantinedSources();
            AsyncReadBridge.Provider source=c->CompletableFuture.completedFuture(new AsyncReadBridge.Handle(){
                public Long length(){return length;}public CompletionStage<Integer> readAt(long at,byte[] bytes,int off,int n,AsyncReadBridge.Cancellation token){throw new AssertionError("must reject before reading");}
                public CompletionStage<Void> closeAsync(){closed.set(true);return CompletableFuture.completedFuture(null);}
            });
            try(CpuTaskClient unused=new CpuTaskClient(context(),source)){fail("known positive length required");}catch(IOException expected){assertEquals("CPU_SOURCE_LENGTH_REQUIRED",expected.getMessage());}
            assertTrue(closed.get());assertEquals(before,CpuTaskClient.quarantinedSources());
        }
    }
    @Test public void cpuCancelAfterActualFrame()throws Exception {
        byte[] before=hash("basic.mp4");try(CpuTaskClient task=new CpuTaskClient(context(),provider("basic.mp4"))){try{task.start(CpuTaskClient.MP4_H264,2000000,CpuTaskClient.WAIT_FRAME);frame(task.awaitFrame(30000),2000000);task.cancel();}catch(Exception|Error primary){recordPrimary(primary);throw primary;}finally{released(task);}}assertArrayEquals(before,hash("basic.mp4"));
    }
    @Test public void cpuHungTaskBoundedStopAndDeath()throws Exception {
        try(CpuTaskClient task=new CpuTaskClient(context(),provider("basic.mp4"))){try{task.start(CpuTaskClient.MP4_H264,2000000,CpuTaskClient.HANG_FRAME);frame(task.awaitFrame(30000),2000000);assertEquals(CpuProtocol.HANG_ARMED,task.awaitArmed(5000));long before=System.nanoTime();released(task);assertTrue(TimeUnit.NANOSECONDS.toMillis(System.nanoTime()-before)<6500);}catch(Exception|Error primary){recordPrimary(primary);throw primary;}finally{released(task);}}
    }
    @Test public void cpuDuplicateConnectionKeepsOriginalIdentity()throws Exception {
        try(CpuTaskClient task=new CpuTaskClient(context(),provider("basic.mp4"))){try{
            task.start(CpuTaskClient.MP4_H264,2000000,CpuTaskClient.WAIT_FRAME);frame(task.awaitFrame(30000),2000000);int pid=task.workerPid(),uid=task.workerUid();
            task.debugDuplicateConnection();assertEquals(pid,task.workerPid());assertEquals(uid,task.workerUid());assertEquals(1,task.unresolvedWorkers());assertFalse(task.awaitDeath(100));task.resume();frame(task.awaitResult(10000),2000000);
        }catch(Exception|Error primary){recordPrimary(primary);throw primary;}finally{released(task);}}
    }
    @Test public void cpuCancelDuringHelloCannotStartOrRevive()throws Exception {
        ExecutorService executor=Executors.newSingleThreadExecutor();
        try(CpuTaskClient task=new CpuTaskClient(context(),provider("basic.mp4"))){task.debugHelloEntered=new CountDownLatch(1);task.debugHelloRelease=new CountDownLatch(1);try{
            Future<?> start=executor.submit(()->{try{task.start(CpuTaskClient.MP4_H264,2000000,CpuTaskClient.WAIT_FRAME);throw new AssertionError("cancelled HELLO revived START");}catch(Exception expected){StageLog.failure("CPU_EXPECTED_CANCEL_DURING_HELLO",expected);}});
            assertTrue(task.debugHelloEntered.await(5,TimeUnit.SECONDS));InstrumentationRegistry.getInstrumentation().runOnMainSync(task::cancel);task.debugHelloRelease.countDown();start.get(6000,TimeUnit.MILLISECONDS);
            assertFalse(task.lifecycle().startAck);assertTrue(task.awaitDeath(5000));assertTrue(task.awaitSourceReleased(5000));
        }catch(Exception|Error primary){recordPrimary(primary);throw primary;}finally{task.debugHelloRelease.countDown();released(task);}}
        finally{executor.shutdownNow();}
    }
    @Test public void cpuRejectedExtraWorkerRetainsSlotAndSecondTask()throws Exception {extraWorkerCounterexample(false);}
    @Test public void cpuLateWorkerCannotBorrowOriginalDeath()throws Exception {extraWorkerCounterexample(true);}
    private void extraWorkerCounterexample(boolean afterDeath)throws Exception {
        CpuTaskClient.DebugExtraBinding extra=null;
        try(CpuTaskClient first=new CpuTaskClient(context(),provider("basic.mp4"));CpuTaskClient second=new CpuTaskClient(context(),provider("basic.mp4"))){try{
            first.start(CpuTaskClient.MP4_H264,2000000,CpuTaskClient.WAIT_FRAME);second.start(CpuTaskClient.MP4_H264,2000000,CpuTaskClient.WAIT_FRAME);frame(first.awaitFrame(30000),2000000);frame(second.awaitFrame(30000),2000000);int pid=first.workerPid(),uid=first.workerUid();
            if(afterDeath){first.cancel();assertTrue(first.awaitDeath(5000));}
            extra=first.debugExtraWorker(true);WorkerGenerations.Worker rejected=extra.await(5000);assertFalse(rejected.primary);assertNotEquals(pid,rejected.pid);assertEquals(pid,first.workerPid());assertEquals(uid,first.workerUid());
            first.cancel();assertTrue(first.awaitDeath(5000));first.debugReplayDeadPrimary();assertFalse("old death cannot release live rejected worker",first.stopAndAwait(200));assertFalse(rejected.dead());assertFalse(first.lifecycle().slotReleased);
            try{new CpuTaskClient(context(),provider("basic.mp4"));fail("third CPU slot admitted while extra worker unproven");}catch(IOException expected){assertEquals("CPU_SLOTS_EXHAUSTED_OR_QUARANTINED",expected.getMessage());}
            assertFalse(second.awaitDeath(100));second.resume();frame(second.awaitResult(10000),2000000);
            extra.releaseStall();extra.close();extra=null;assertTrue(first.stopAndAwait(5000));assertEquals(0,first.unresolvedWorkers());assertEquals(pid,first.workerPid());
        }catch(Exception|Error primary){recordPrimary(primary);throw primary;}finally{
            CpuTaskClient.DebugExtraBinding remaining=extra;try{if(remaining!=null)cleanupPreserving(()->{try{remaining.releaseStall();}finally{remaining.close();}});}finally{releaseBoth(first,second);}
        }}
    }
    @Test public void cpuExitCollectionRejectsMainThread()throws Exception {
        ExitEvidence[] result=new ExitEvidence[1];InstrumentationRegistry.getInstrumentation().runOnMainSync(()->{try{result[0]=ExitEvidence.collect(context(),1,99001,1);}catch(InterruptedException error){throw new AssertionError(error);}});
        assertNotNull(result[0]);assertFalse(result[0].matched);assertEquals("EXIT_EVIDENCE_MAIN_THREAD_REJECTED",result[0].traceStatus);
    }
    @Test public void cpuSelfSigsegvSignalMustBeProven()throws Exception {
        int host=android.os.Process.myPid();byte[] before=hash("basic.mp4");
        try(CpuTaskClient task=new CpuTaskClient(context(),provider("basic.mp4"))){
            try{task.start(CpuTaskClient.MP4_H264,2000000,CpuTaskClient.SEGV_FRAME);frame(task.awaitFrame(30000),2000000);assertEquals(CpuProtocol.SIGSEGV_ARMED,task.awaitArmed(5000));
                assertTrue("self fault death must precede any cleanup stop",task.awaitDeath(5000));assertTrue(task.awaitSourceReleased(5000));
                ExitEvidence exit=ExitEvidence.collect(context(),task.workerPid(),task.workerUid(),task.bindStartedAt(),task.workerProcess());exit.log();
                assertTrue("signal0 stays UNKNOWN/FAIL; matching external tombstone is recorded separately",exit.isSignal(11));
            }catch(Exception|Error primary){recordPrimary(primary);throw primary;}finally{released(task);}
        }finally{cleanupPreserving(()->{assertEquals(host,android.os.Process.myPid());assertArrayEquals(before,hash("basic.mp4"));});}
    }
    @Test public void cpuSecondSlotAndHostSurviveFirstSelfCrash()throws Exception {
        int host=android.os.Process.myPid();
        try(CpuTaskClient first=new CpuTaskClient(context(),provider("basic.mp4"));CpuTaskClient second=new CpuTaskClient(context(),provider("basic.mp4"))){
            try{first.start(CpuTaskClient.MP4_H264,2000000,CpuTaskClient.WAIT_FRAME);second.start(CpuTaskClient.MP4_H264,2000000,CpuTaskClient.WAIT_FRAME);
                frame(first.awaitFrame(30000),2000000);frame(second.awaitFrame(30000),2000000);assertNotEquals(first.workerPid(),second.workerPid());assertNotEquals(first.workerUid(),second.workerUid());
                first.selfSegv();assertEquals(CpuProtocol.SIGSEGV_ARMED,first.awaitArmed(5000));assertTrue(first.awaitDeath(5000));assertTrue(first.awaitSourceReleased(5000));
                assertFalse("second actual Binder still alive",second.awaitDeath(100));second.resume();frame(second.awaitResult(10000),2000000);assertEquals(host,android.os.Process.myPid());
                StageLog.event("CPU_INDEPENDENT_CRASH_REQUIRES_RAW_MATCH","task="+first.task+" epoch="+first.epoch+" pid="+first.workerPid()+" uid="+first.workerUid());
                ExitEvidence exit=ExitEvidence.collect(context(),first.workerPid(),first.workerUid(),first.bindStartedAt(),first.workerProcess());exit.log();assertTrue("target signal must remain independently proven, not cleanup",exit.isSignal(11));
            }catch(Exception|Error primary){recordPrimary(primary);throw primary;}finally{releaseBoth(first,second);}
        }
    }
}
