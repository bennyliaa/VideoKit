package com.videokit.spike.c13;

import android.content.*;
import android.os.*;
import androidx.test.ext.junit.runners.AndroidJUnit4;
import androidx.test.platform.app.InstrumentationRegistry;
import java.io.*;
import java.nio.file.*;
import java.security.MessageDigest;
import java.util.*;
import java.util.concurrent.*;
import org.junit.*;
import org.junit.runner.RunWith;
import static org.junit.Assert.*;

/** Prepared only. Actual Android isolated codec, FD locks and process recovery must run on devices later. */
@RunWith(AndroidJUnit4.class)
public final class C13IsolatedDeviceTests {
    private Context context(){return InstrumentationRegistry.getInstrumentation().getTargetContext();}
    private byte[] sourceHash()throws Exception{return MessageDigest.getInstance("SHA-256").digest(Files.readAllBytes(new File(DeviceFixtures.directory(context()),"basic.mp4").toPath()));}
    private void isolated(IsolatedExportController owner){assertTrue(owner.workerPid()>0 && owner.workerPid()!=android.os.Process.myPid());assertTrue(owner.workerUid()>0 && owner.workerUid()!=android.os.Process.myUid());}
    @Test public void ordinaryIsolatedCodecOutcomeDoesNotReady()throws Exception {
        String id=UUID.randomUUID().toString();Throwable problem=null;
        try(IsolatedExportController owner=new IsolatedExportController(context(),id,DeviceFixtures.routes(context()),IsolatedExportController.Backend.ISOLATED_SERVICE)){
            try{
                owner.start(MediaProtocol.CAPABILITY_PROBE);isolated(owner);IOException actual=null;
                try{owner.awaitResult(30000);fail("probe must never produce a validated output");}catch(IOException error){actual=error;StageLog.failure("ORDINARY_CODEC_PROBE_RESULT",error);}
                assertNotNull(actual);assertTrue("actual worker death",owner.awaitDeath(15000));
                boolean javaFailure=actual.getMessage().equals("ISOLATED_CODEC_JAVA_CALL_FAILED") && owner.probeState().javaFailureObserved();
                ExitEvidence exit=ExitEvidence.collect(context(),owner.workerPid(),owner.workerUid(),owner.bindStartedAt());exit.log();
                boolean explainedNative=actual.getMessage().equals("WORKER_DIED") && owner.probeState().nativeCallPending() && exit.explainedCodecNativeAbort();
                StageLog.event("ORDINARY_CODEC_OBSERVED","stage="+owner.probeState().last()+" java_call_failed="+javaFailure+" native_abort_with_cause="+explainedNative+" permission_denial_proven=false");
                assertTrue("Java cause or task-matched native SIGABRT tombstone reason required; unknown WORKER_DIED must FAIL",owner.probeState().explainedOutcome(actual.getMessage(),exit.explainedCodecNativeAbort()));
            }catch(Throwable failure){problem=failure;}
            finally{
                owner.cancel();boolean died=owner.awaitDeath(15000),released=owner.awaitSourceReleased(10000),leaseClear=false;
                if(died)try{leaseClear=owner.recoverAbort(5000)==FencedTask.State.ABORTED;}catch(IOException error){StageLog.failure("ORDINARY_CODEC_LEASE_QUARANTINE",error);}
                StageLog.event("ORDINARY_CODEC_FINAL_STATE","task="+id+" pid="+owner.workerPid()+" uid="+owner.workerUid()+" death="+died+" source_released="+released+" lease_clear="+leaseClear);
                if(!died || !released || !leaseClear || owner.token()!=null){AssertionError cleanup=new AssertionError("ORDINARY_CODEC_FINAL_STATE_UNKNOWN_QUARANTINE");if(problem==null)problem=cleanup;else problem.addSuppressed(cleanup);}
            }
        }
        if(problem!=null)throw new AssertionError("ORDINARY_CODEC_OUTCOME_UNPROVEN",problem);
    }
    @Test public void nativeLeaseSurvivesDuplicateDescriptorClose()throws Exception {
        String id=UUID.randomUUID().toString();
        try(FencedTask owner=IsolatedExportController.openTask(context(),id)){
            try{IsolatedExportController.openTask(context(),id);fail("second owner must be rejected");}catch(IOException expected){assertEquals("OUTPUT_OWNER_BUSY",expected.getMessage());}
            try{AndroidLease.exclusive(IsolatedExportController.targetDirectory(context()).resolve(id+".owner"));fail("failed competing owner must not release original native owner lock");}catch(IOException expected){assertEquals("OUTPUT_WORKER_ACTIVE",expected.getMessage());}
            String epoch=owner.issue();ParcelFileDescriptor original=ParcelFileDescriptor.open(owner.authorizedLease().toFile(),ParcelFileDescriptor.MODE_READ_ONLY);
            try(AndroidLease.WorkerLease worker=AndroidLease.WorkerLease.acquire(original,epoch)){
                ParcelFileDescriptor duplicate=ParcelFileDescriptor.dup(original.getFileDescriptor());duplicate.close();
                try{owner.abort();fail("another FD close must not release the worker flock lease");}catch(IOException expected){assertEquals("OUTPUT_WORKER_ACTIVE",expected.getMessage());}
                assertTrue(Files.exists(owner.authorizedOutput()));
            }
            assertEquals(FencedTask.State.ABORTED,owner.abort());assertFalse(Files.exists(owner.authorizedOutput()));
        }
    }
    @Test public void isolatedActualEncodeAndReadyRecovery()throws Exception {
        byte[] before=sourceHash();String id=UUID.randomUUID().toString(),token;
        try(IsolatedExportController owner=new IsolatedExportController(context(),id,DeviceFixtures.routes(context()))){
            owner.start(MediaProtocol.EXPORT);isolated(owner);IsolatedExportController.Report r=owner.awaitResult(120000);
            assertTrue("isolated real encoder + isolated reopen validation",r.valid && r.videoSamples>0 && r.bytes>0);assertTrue("broker input, not direct path/FD",owner.brokerBytes()>0);
            assertTrue("actual worker Binder death",owner.awaitDeath(15000));assertTrue("all host provider consumers/operations actually drained",owner.awaitSourceReleased(10000));
            try{owner.markReady(true);fail("lost ready response injection");}catch(IOException expected){assertEquals("OUTPUT_READY_UNKNOWN",expected.getMessage());}
            assertEquals(FencedTask.State.READY,owner.query());token=owner.token();assertNotNull(token);
        }
        try(FencedTask newOwner=IsolatedExportController.openTask(context(),id)){assertEquals(FencedTask.State.READY,newOwner.query());assertEquals(token,newOwner.token());assertEquals(FencedTask.State.READY,newOwner.abort());}
        assertArrayEquals("read-only input unchanged",before,sourceHash());
    }
    @Test public void cancelAfterActualVideoSample()throws Exception {interruptedExport(0);}
    @Test public void workerExitDuringActualEncoding()throws Exception {interruptedExport(1);}
    @Test public void workerSigsegvDuringActualEncoding()throws Exception {interruptedExport(2);}
    @Test public void secondCodecTaskSurvivesFirstNativeCrash()throws Exception {
        String firstId=UUID.randomUUID().toString(),secondId=UUID.randomUUID().toString();
        try(IsolatedExportController first=new IsolatedExportController(context(),firstId,DeviceFixtures.routes(context()));
            IsolatedExportController second=new IsolatedExportController(context(),secondId,DeviceFixtures.routes(context()))){
            first.start(MediaProtocol.GATE_AFTER_SAMPLE);assertTrue(first.awaitProcessedVideo(90000));second.start(MediaProtocol.GATE_AFTER_SAMPLE);assertTrue(second.awaitProcessedVideo(90000));
            assertNotEquals(first.workerPid(),second.workerPid());assertEquals(first.workerUid(),second.workerUid());
            first.injectTermination(true);assertTrue(first.awaitDeath(15000));assertEquals(FencedTask.State.ABORTED,first.recoverAbort(5000));assertTrue(first.awaitSourceReleased(10000));
            assertFalse("other task/process must still be alive",second.awaitDeath(100));second.resumeAfterSample();assertTrue(second.awaitResult(120000).valid);assertTrue(second.awaitDeath(15000));assertTrue(second.awaitSourceReleased(10000));assertNotNull(second.markReady(false));
        }
    }
    private void interruptedExport(int termination)throws Exception {
        byte[] before=sourceHash();String id=UUID.randomUUID().toString();
        try(IsolatedExportController owner=new IsolatedExportController(context(),id,DeviceFixtures.routes(context()))){
            owner.start(MediaProtocol.GATE_AFTER_SAMPLE);isolated(owner);assertTrue("actual H264 sample processed before interrupt",owner.awaitProcessedVideo(90000));assertTrue(owner.processedVideoSamples()>0 && owner.processedBytes()>0);
            if(termination==0)owner.cancel();else owner.injectTermination(termination==2);
            assertTrue("observed actual worker death",owner.awaitDeath(15000));assertEquals(FencedTask.State.ABORTED,owner.recoverAbort(5000));assertTrue(owner.awaitSourceReleased(10000));
            assertFalse("partial output removed only after lease clear",Files.exists(IsolatedExportController.targetDirectory(context()).resolve(id+".mp4")));assertNull(owner.token());
            try{owner.markReady(false);fail("interrupted output must never READY");}catch(IOException expected){}
        }
        assertArrayEquals(before,sourceHash());
    }
    @Test public void actualHostDeathDuringEncodingAndCrossOwnerAbort()throws Exception {
        byte[] before=sourceHash();String id=UUID.randomUUID().toString();
        try(HostClient host=new HostClient(context())){
            host.start(id,false);HostStatus status=host.awaitSample(90000);assertTrue(status.samples>0 && status.bytes>0);assertTrue(status.workerPid>0 && status.workerPid!=host.pid);assertTrue(status.workerUid>0 && status.workerUid!=host.uid);
            host.killOwnHarness();assertTrue("actual task host process death (instrumentation still alive)",host.awaitDeath(15000));
        }
        try(FencedTask newOwner=recoverOwner(id,10000)){assertEquals(FencedTask.State.ABORTED,abortWhenLeaseClear(newOwner,10000));assertFalse(Files.exists(newOwner.authorizedOutput()));assertNull(newOwner.token());}
        assertArrayEquals(before,sourceHash());
    }
    @Test public void actualHostDeathAfterReadyAndSameTaskQuery()throws Exception {
        byte[] before=sourceHash();String id=UUID.randomUUID().toString();
        try(HostClient host=new HostClient(context())){host.start(id,true);assertTrue("host accepted real validated output then died without returning token",host.awaitDeath(150000));}
        String token;try(FencedTask newOwner=recoverOwner(id,10000)){assertEquals("durable original task, no second output",FencedTask.State.READY,newOwner.query());token=newOwner.token();assertNotNull(token);assertEquals(FencedTask.State.READY,newOwner.abort());assertTrue(Files.size(newOwner.authorizedOutput())>0);}
        try(FencedTask again=IsolatedExportController.openTask(context(),id)){assertEquals(token,again.token());}
        assertArrayEquals(before,sourceHash());
    }
    private FencedTask recoverOwner(String id,long budgetMs)throws Exception {
        long stop=System.nanoTime()+TimeUnit.MILLISECONDS.toNanos(budgetMs);while(true)try{return IsolatedExportController.openTask(context(),id);}
        catch(IOException e){if(!"OUTPUT_OWNER_BUSY".equals(e.getMessage()) || System.nanoTime()>=stop)throw e;Thread.sleep(20);}
    }
    private FencedTask.State abortWhenLeaseClear(FencedTask owner,long budgetMs)throws Exception {
        long stop=System.nanoTime()+TimeUnit.MILLISECONDS.toNanos(budgetMs);while(true)try{return owner.abort();}catch(IOException e){if(!"OUTPUT_WORKER_ACTIVE".equals(e.getMessage()) || System.nanoTime()>=stop)throw e;Thread.sleep(20);}
    }
    private static final class HostStatus {final long samples,bytes;final int workerPid,workerUid;final String phase;HostStatus(Parcel p){phase=p.readString();samples=p.readLong();bytes=p.readLong();workerPid=p.readInt();workerUid=p.readInt();}}
    private static final class HostClient implements AutoCloseable {
        private final Context context;private final ExecutorService executor=Executors.newSingleThreadExecutor();private final CompletableFuture<IBinder> connected=new CompletableFuture<>();private final CompletableFuture<Void> dead=new CompletableFuture<>();
        private IBinder remote;private boolean bound;int pid,uid;
        private final ServiceConnection connection=new ServiceConnection(){public void onServiceConnected(ComponentName name,IBinder service){try{service.linkToDeath(()->dead.complete(null),0);connected.complete(service);}catch(RemoteException e){connected.completeExceptionally(e);}}
            public void onServiceDisconnected(ComponentName n){dead.complete(null);}public void onBindingDied(ComponentName n){connected.completeExceptionally(new IOException("HOST_BINDING_DIED"));}};
        HostClient(Context context)throws Exception {
            this.context=context;bound=context.bindService(new Intent(context,RecoveryHostService.class),Context.BIND_AUTO_CREATE,executor,connection);assertTrue(bound);remote=connected.get(15,TimeUnit.SECONDS);
            Parcel req=request(),reply=Parcel.obtain();try{remote.transact(RecoveryHostService.HELLO,req,reply,0);reply.readException();pid=reply.readInt();uid=reply.readInt();assertTrue(pid>0 && pid!=android.os.Process.myPid());assertEquals(android.os.Process.myUid(),uid);}finally{req.recycle();reply.recycle();}
        }
        private Parcel request(){Parcel p=Parcel.obtain();p.writeInterfaceToken(RecoveryHostService.INTERFACE);return p;}
        void start(String id,boolean readyThenDie)throws Exception {Parcel req=request(),reply=Parcel.obtain();try{req.writeString(id);req.writeInt(readyThenDie?1:0);remote.transact(RecoveryHostService.START,req,reply,0);reply.readException();}finally{req.recycle();reply.recycle();}}
        HostStatus awaitSample(long budgetMs)throws Exception {
            long stop=System.nanoTime()+TimeUnit.MILLISECONDS.toNanos(budgetMs);while(System.nanoTime()<stop){Parcel req=request(),reply=Parcel.obtain();try{remote.transact(RecoveryHostService.QUERY,req,reply,0);reply.readException();HostStatus status=new HostStatus(reply);if(status.phase.contains("FAILED"))fail(status.phase);if(status.samples>0)return status;}finally{req.recycle();reply.recycle();}Thread.sleep(50);}throw new AssertionError("actual host video processing deadline");
        }
        void killOwnHarness()throws Exception {Parcel req=request();try{remote.transact(RecoveryHostService.KILL_SELF_AFTER_SAMPLE,req,null,IBinder.FLAG_ONEWAY);}finally{req.recycle();}}
        boolean awaitDeath(long budgetMs)throws Exception {try{dead.get(budgetMs,TimeUnit.MILLISECONDS);return true;}catch(TimeoutException e){return false;}}
        public void close(){if(bound){bound=false;context.unbindService(connection);}executor.shutdown();}
    }
}
