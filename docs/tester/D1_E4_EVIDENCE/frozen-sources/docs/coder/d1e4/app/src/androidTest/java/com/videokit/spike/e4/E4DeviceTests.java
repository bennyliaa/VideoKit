package com.videokit.spike.e4;

import android.content.ComponentName;
import android.content.Context;
import android.content.Intent;
import android.content.ServiceConnection;
import android.os.Bundle;
import android.os.Handler;
import android.os.IBinder;
import android.os.Looper;
import android.os.Parcel;
import androidx.test.ext.junit.runners.AndroidJUnit4;
import androidx.test.platform.app.InstrumentationRegistry;
import com.videokit.spike.c14.AsyncReadBridge;
import com.videokit.spike.c14.CpuTaskClient;
import com.videokit.spike.c14.E4CpuAdapter;
import com.videokit.spike.c14.HostFixtures;
import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.junit.rules.TestName;
import org.junit.runner.RunWith;
import java.io.IOException;
import java.io.InputStream;
import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;
import java.nio.file.Files;
import java.nio.file.LinkOption;
import java.nio.file.Path;
import java.security.MessageDigest;
import java.util.Locale;
import java.util.UUID;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.CompletionStage;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicLong;
import static org.junit.Assert.*;

/**
 * Compiled future device plan only. No method is executed by the local build.
 * Select exactly one method per instrumentation invocation using e4Case and a reviewed e4Batch.
 * NormalReceipt is the SHA of an independently reviewed same-device normal report, verified by
 * the tester outside this APK; accepting its syntax here is not evidence that normal work passed.
 * Quarantine methods run LAST in an independently archived invocation. They never force cleanup,
 * reset an unknown lease, clear app data, fabricate a signal, or turn PENDING into resource release.
 */
@RunWith(AndroidJUnit4.class)
public final class E4DeviceTests {
    @Retention(RetentionPolicy.RUNTIME) public @interface NeedsNormalPrecondition {}
    @Retention(RetentionPolicy.RUNTIME) public @interface QuarantineLastSingleCase {}
    @Rule public final TestName selected=new TestName();
    private int evidence;
    private Context context(){return InstrumentationRegistry.getInstrumentation().getTargetContext();}
    private Bundle args(){return InstrumentationRegistry.getArguments();}
    @Before public void selectedFormalCaseOnly(){
        assertEquals("Select one exact reviewed method, never the entire fault class",selected.getMethodName(),args().getString("e4Case"));
        assertTrue("Coordinator-reviewed device batch required",args().getString("e4Batch","").matches("D1-E4-[A-Za-z0-9-]{8,80}"));
        assertNotEquals("Instrumentation must not block UI",Looper.getMainLooper(),Looper.myLooper());
    }
    private void normalPrerequisite(){assertTrue("External normal report identity required",args().getString("e4NormalReceiptSha256","").matches("[a-f0-9]{64}"));}
    private void quarantine(){normalPrerequisite();assertEquals("Archive this single case before any process reset","LAST_SINGLE_CASE",args().getString("e4Quarantine"));}
    private void evidence(String stage,String value){
        assertTrue("Bounded device metadata",++evidence<=64);assertTrue(value.length()<=4096);
        Bundle status=new Bundle();status.putString("stream","E4 "+stage+" "+value+"\n");InstrumentationRegistry.getInstrumentation().sendStatus(0,status);
    }
    private void record(E4Session.Report r){evidence("REPORT","task="+r.task+" status="+r.status+" error="+r.error+" received="+r.received+" inputs="+r.inputs+" outputs="+r.outputs+" released="+r.resourcesReleased+" workerDied="+r.workerDied+" rawReason="+r.systemExit.getInt("systemReason",-1)+" rawStatus="+r.systemExit.getInt("systemStatus",-1)+" signalVerdict="+r.systemExit.getString("signalVerdict","NOT_COLLECTED"));}
    private void responsiveMain()throws Exception {CountDownLatch pulse=new CountDownLatch(1);assertTrue(new Handler(Looper.getMainLooper()).post(pulse::countDown));assertTrue("Host UI/main Handler stayed responsive",pulse.await(1500,TimeUnit.MILLISECONDS));}
    private void released(E4Session.Report r){assertTrue("Actual source, sink, codec and callback owners returned",r.resourcesReleased);assertFalse(r.workerDied);assertEquals(0,r.callbackRejected);assertEquals(0,E4Session.reservedEncoderSlots());assertEquals(0,E4Session.retainedSessions());}
    private void noReady(E4Session.Report r){assertNotEquals("READY",r.status);assertEquals("",r.token);}

    @Test public void normalMp4SixRealFrames()throws Exception {positive("basic.mp4",CpuTaskClient.MP4_H264);}
    @Test public void normalAviSixRealFrames()throws Exception {positive("subtitle.avi",CpuTaskClient.AVI_MPEG4);}
    private void positive(String name,int kind)throws Exception {
        try(Fixture f=fixture(name);E4Session s=new E4Session(context(),HostFixtures.file(f.path),kind)){
            s.start();E4Session.Report r=s.await(90000);record(r);assertEquals("READY",r.status);assertNull(r.error);assertFalse(r.token.isEmpty());
            assertEquals(6,r.received);assertEquals(6,r.inputs);assertEquals(6,r.outputs);released(r);responsiveMain();
        }
    }
    @Test public void capabilityDenialDoesNotOpenSource()throws Exception {
        try(Fixture f=fixture("basic.mp4")){
            CountingProvider source=new CountingProvider(HostFixtures.file(f.path));
            try(E4Session s=new E4Session(context(),source,CpuTaskClient.MP4_H264,"capability-deny")){
                s.start();E4Session.Report r=s.await(30000);record(r);noReady(r);assertEquals(0,r.received);assertEquals(0,r.inputs);assertEquals(0,r.outputs);
                assertEquals("Production source broker did not open",0,source.opens.get());assertEquals(0,source.bytes.get());assertEquals(0,source.reads.get());released(r);
            }
        }
    }
    /** Actual Binder metadata refusals; no BEGIN and no codec enumeration/creation occurs. */
    @Test public void binderRefusesBeforeBeginAndOversizeParcel()throws Exception {
        try(RawEndpoint endpoint=new RawEndpoint()){
            E4Protocol.Identity id=endpoint.identity(UUID.randomUUID().toString().replace("-",""),1,1);
            Bundle before=E4CodecWire.identity(id);before.putInt("sequence",1);
            assertEquals("REJECTED",E4CodecWire.call(endpoint.binder,E4CodecWire.FRAME,before).getString("status"));
            Bundle wrong=E4CodecWire.identity(id);wrong.putLong("epoch",0);
            assertEquals("REJECTED",E4CodecWire.call(endpoint.binder,E4CodecWire.QUERY,wrong).getString("status"));
            Bundle old=E4CodecWire.identity(id);old.putString("serviceInstance",UUID.randomUUID().toString());
            assertEquals("REJECTED",E4CodecWire.call(endpoint.binder,E4CodecWire.QUERY,old).getString("status"));
            Parcel data=Parcel.obtain(),reply=Parcel.obtain();
            try{data.writeInterfaceToken(E4CodecWire.DESCRIPTOR);Bundle huge=new Bundle();huge.putByteArray("not-a-frame",new byte[E4CodecWire.MAX_PARCEL]);data.writeBundle(huge);
                assertTrue(data.dataSize()>E4CodecWire.MAX_PARCEL);assertTrue(endpoint.binder.transact(E4CodecWire.FRAME,data,reply,0));
                try{reply.readException();fail("Actual Binder admitted oversized parcel");}catch(SecurityException expected){assertEquals("E4_PARCEL_BUDGET",expected.getMessage());}
            }finally{data.recycle();reply.recycle();}
            assertEquals(0,E4Session.reservedEncoderSlots());evidence("BINDER_NEGATIVES","no_BEGIN=true actual_remote_refusals=4 codec_started=false");
        }
    }
    @Test @NeedsNormalPrecondition public void cancelRejectsWrongEpochOversizeAndLateFrame()throws Exception {
        normalPrerequisite();
        try(Fixture f=fixture("basic.mp4")){
            GateProvider source=new GateProvider(HostFixtures.file(f.path));
            try(E4Session s=new E4Session(context(),source,CpuTaskClient.MP4_H264);RawEndpoint endpoint=new RawEndpoint()){
                s.start();try{
                    E4Session.Report active=awaitActive(s);assertTrue(source.entered.await(10000,TimeUnit.MILLISECONDS));
                    E4Protocol.Identity id=E4CodecWire.identity(active.remote);
                    Bundle wrong=frame(id,147456);wrong.putLong("epoch",id.epoch==Long.MAX_VALUE?id.epoch-1:id.epoch+1);
                    assertEquals("REJECTED",E4CodecWire.call(endpoint.binder,E4CodecWire.FRAME,wrong).getString("status"));
                    Bundle oversized=frame(id,147457);Bundle rejected=E4CodecWire.call(endpoint.binder,E4CodecWire.FRAME,oversized);
                    assertEquals("REJECTED",rejected.getString("status"));assertEquals("E4_FRAME_LAYOUT",rejected.getString("error"));
                    s.cancel();assertEquals("CANCEL_PENDING",E4CodecWire.call(endpoint.binder,E4CodecWire.CANCEL,E4CodecWire.identity(id)).getString("status"));
                    Bundle late=E4CodecWire.call(endpoint.binder,E4CodecWire.FRAME,frame(id,147456));assertEquals("REJECTED",late.getString("status"));assertEquals("E4_FRAME_TASK_NOT_ACTIVE",late.getString("error"));
                }finally{source.release();s.cancel();}
                E4Session.Report result=s.await(30000);record(result);noReady(result);assertEquals(0,result.inputs);released(result);responsiveMain();
            }
        }
    }
    @Test @NeedsNormalPrecondition @QuarantineLastSingleCase public void closeUnprovenRetainsPermitAndNeverReady()throws Exception {
        quarantine();
        try(Fixture f=fixture("basic.mp4");E4Session s=new E4Session(context(),HostFixtures.file(f.path),CpuTaskClient.MP4_H264,"close-unproven")){
            s.start();E4Session.Report r=s.await(90000);record(r);noReady(r);assertEquals("PENDING",r.status);assertFalse(r.resourcesReleased);assertEquals(1,E4Session.reservedEncoderSlots());
            assertTrue("Original unknown owner retained",E4Session.retainedSessions()>=1);assertTrue(r.remote.getInt("unknownResources")>0 || r.remote.getInt("liveResources")>0);
            rejectedSecondEncoder(f.path);responsiveMain();
            evidence("QUARANTINE","No cleanup/reset/reuse claimed; execute this method last and archive PENDING.");
        }
    }
    @Test @NeedsNormalPrecondition @QuarantineLastSingleCase public void selfKillOtherCpuContinuesAndOldGenerationRejected()throws Exception {deathCase("self-kill");}
    @Test @NeedsNormalPrecondition @QuarantineLastSingleCase public void nativeSegvOtherCpuContinuesAndOldGenerationRejected()throws Exception {deathCase("native-segv");}
    private void deathCase(String operation)throws Exception {
        quarantine();
        ExecutorService secondOwner=Executors.newSingleThreadExecutor(r->new Thread(r,"e4-independent-real-cpu-owner"));
        try(Fixture f=fixture("basic.mp4")){
            GateProvider independentInput=new GateProvider(HostFixtures.file(f.path));E4CpuAdapter independent=new E4CpuAdapter(context(),independentInput,CpuTaskClient.MP4_H264);
            Future<E4CpuAdapter.Sample> other=null;
            try(E4Session s=new E4Session(context(),HostFixtures.file(f.path),CpuTaskClient.MP4_H264)){
                try{
                    s.start();E4Session.Report active=awaitActive(s);responsiveMain();
                    other=secondOwner.submit(()->{try{return independent.next(1);}finally{independent.close();}});
                    assertTrue("Another real isolated task has an actual read in flight",independentInput.entered.await(5000,TimeUnit.MILLISECONDS));assertFalse(other.isDone());
                    Bundle armed=s.debugOwnService(operation+"-arm",null);assertEquals("DEBUG_DEATH_ARMED",armed.getString("status"));
                    String arm=armed.getString("armToken");assertNotNull(arm);assertEquals("DEBUG_DEATH_COMMITTED",s.debugOwnService(operation+"-commit",arm).getString("status"));
                    long deathDeadline=System.nanoTime()+TimeUnit.MILLISECONDS.toNanos(2500);boolean observed=false;
                    for(int polls=0;polls<51 && System.nanoTime()<deathDeadline;polls++){if(s.query().workerDied){observed=true;break;}Thread.sleep(50);}
                    assertTrue("Original Binder death must arrive within the unchanged 5s read budget",observed);
                    assertFalse("Independent source remained pending across codec death",other.isDone());independentInput.release();
                    E4CpuAdapter.Sample actual=other.get(20000,TimeUnit.MILLISECONDS);assertEquals(147456,actual.rgba.length);assertTrue(actual.pid>0);assertNotEquals(active.remote.getInt("pid"),actual.pid);assertNotEquals(android.os.Process.myUid(),actual.uid);assertTrue(actual.uid%100000>=90000);assertTrue(independent.sourceClosed());
                    E4Session.Report dead=s.await(40000);record(dead);noReady(dead);assertTrue(dead.workerDied);assertEquals("WORKER_DIED",dead.error);assertFalse(dead.resourcesReleased);assertEquals("PENDING",dead.status);
                    assertEquals("Original controlled service reached the Debug fault entrance","DEBUG_DEATH_ENTERED",dead.remote.getString("status"));
                    assertEquals("WORKER_DIED",dead.systemExit.getString("appCause"));assertTrue(dead.systemExit.containsKey("systemReason"));assertTrue(dead.systemExit.containsKey("systemStatus"));
                    // Preserve raw original system values; zero/unavailable remains UNKNOWN/FAIL, never a claimed signal.
                    if(dead.systemExit.getInt("systemStatus",-1)==0)assertEquals("UNKNOWN_FAIL_SYSTEM_ZERO",dead.systemExit.getString("signalVerdict"));
                    evidence("SIGNAL_GATE","This test checks App death/UNKNOWN retention, not historical native-signal acceptance; raw system zero remains FAIL/UNKNOWN.");
                    responsiveMain();
                    evidence("OTHER_REAL_CPU","pid="+actual.pid+" uid="+actual.uid+" task="+actual.sourceTask+" rgba_sha="+E4Protocol.sha(actual.rgba)+" read_bytes="+independentInput.bytes.get()+" closed="+independent.sourceClosed());
                    Bundle replacement=s.probeReplacementRejectsOldIdentity();assertTrue(replacement.getBoolean("oldRemoteIdentityRejected"));assertTrue(replacement.getBoolean("oldLocalGenerationRejected"));assertFalse(replacement.getBoolean("newEncoderStarted"));assertTrue(replacement.getBoolean("oldPermitRetained"));
                    rejectedSecondEncoder(f.path);assertEquals(1,E4Session.reservedEncoderSlots());responsiveMain();
                }finally{independentInput.release();if(other!=null && !other.isDone())independent.cancel();}
            }
        }finally{secondOwner.shutdown();/* No shutdownNow/kill or invented release proof. */}
    }
    private void rejectedSecondEncoder(Path path)throws Exception {
        try(E4Session second=new E4Session(context(),HostFixtures.file(path),CpuTaskClient.MP4_H264)){
            second.start();E4Session.Report r=second.await(5000);record(r);noReady(r);assertEquals("E4_ENCODER_OUTPUT_BUSY_OR_QUARANTINED",r.error);assertEquals(0,r.received);assertEquals(0,r.inputs);
        }
    }
    private E4Session.Report awaitActive(E4Session session)throws Exception {
        long deadline=System.nanoTime()+TimeUnit.SECONDS.toNanos(20);
        for(int n=0;n<201 && System.nanoTime()<deadline;n++){
            E4Session.Report r=session.query();
            if("ACTIVE".equals(r.remote.getString("resourceState")) && r.remote.getBoolean("selected") && !r.remote.getBoolean("encoderReleased"))return r;
            if(!"PENDING".equals(r.status))fail("Normal precondition failed before actual codec active: "+r.status+" "+r.error);
            Thread.sleep(100);
        }
        throw new IOException("E4_DEVICE_ACTIVE_PRECONDITION_NOT_REACHED");
    }
    private static Bundle frame(E4Protocol.Identity id,int bytes){Bundle b=E4CodecWire.identity(id);b.putInt("sequence",1);b.putLong("ptsUs",0);b.putInt("width",256);b.putInt("height",144);b.putInt("stride",1024);b.putInt("rotation",0);b.putByteArray("rgba",new byte[bytes]);return b;}

    /** Exact preprovisioned names only. Hash reads are bounded fixture verification, not parser work. */
    private Fixture fixture(String name)throws Exception {return new Fixture(name);}
    private final class Fixture implements AutoCloseable {
        final Path path;final long length;final String expected;
        Fixture(String name)throws Exception {
            if(name.equals("basic.mp4")){length=349102;expected="720957c94b3665ff97bcc2f59ad5407c5ca54f566b59865723be9eecc0a6a1f9";}
            else if(name.equals("subtitle.avi")){length=736454656;expected="3f0bf3e9fa6f24130a546fee5be98ba43274959cdc0df82a2ee74306ad4ef52f";}
            else throw new IOException("E4_FIXTURE_NOT_DECLARED");
            path=context().getFilesDir().toPath().resolve("e4_fixtures").resolve(name);verify();evidence("FIXTURE","name="+name+" length="+length+" sha="+expected);
        }
        void verify()throws Exception {
            assertTrue("Tester must preprovision this exact regular file",Files.isRegularFile(path,LinkOption.NOFOLLOW_LINKS));assertEquals(length,Files.size(path));
            MessageDigest digest=MessageDigest.getInstance("SHA-256");long read=0;
            try(InputStream input=Files.newInputStream(path)){byte[] buffer=new byte[65536];int n;while((n=input.read(buffer,0,(int)Math.min(buffer.length,length-read+1)))!=-1){read+=n;if(read>length)throw new IOException("E4_FIXTURE_GREW");digest.update(buffer,0,n);}}
            assertEquals(length,read);StringBuilder actual=new StringBuilder();for(byte b:digest.digest())actual.append(String.format(Locale.ROOT,"%02x",b&255));assertEquals(expected,actual.toString());
        }
        public void close()throws Exception {verify();}
    }
    private final class RawEndpoint implements AutoCloseable {
        final CompletableFuture<IBinder> connected=new CompletableFuture<>();final ServiceConnection connection;
        final IBinder binder;final Bundle hello;boolean bound;
        RawEndpoint()throws Exception {
            connection=new ServiceConnection(){public void onServiceConnected(ComponentName n,IBinder b){connected.complete(b);}public void onServiceDisconnected(ComponentName n){}};
            bound=context().bindService(new Intent(context(),E4CodecService.class),connection,Context.BIND_AUTO_CREATE);assertTrue(bound);binder=connected.get(5000,TimeUnit.MILLISECONDS);
            Bundle state=E4CodecWire.call(binder,E4CodecWire.HELLO,new Bundle());
            for(int n=0;!state.getBoolean("ownerReady") && n<50;n++){Thread.sleep(100);state=E4CodecWire.call(binder,E4CodecWire.HELLO,new Bundle());}
            hello=state;assertTrue("Fresh service owner ready for metadata only",hello.getBoolean("ownerReady"));
        }
        E4Protocol.Identity identity(String task,long epoch,long generation)throws Exception {return new E4Protocol.Identity(task,epoch,generation,hello.getString("serviceInstance"),android.os.Process.myUid(),hello.getInt("uid"));}
        public void close(){if(bound){context().unbindService(connection);bound=false;}}
    }
    private static class CountingProvider implements AsyncReadBridge.Provider {
        final AsyncReadBridge.Provider delegate;final AtomicInteger opens=new AtomicInteger(),closes=new AtomicInteger(),reads=new AtomicInteger();final AtomicLong bytes=new AtomicLong();
        CountingProvider(AsyncReadBridge.Provider source){delegate=source;}
        public CompletionStage<AsyncReadBridge.Handle> open(AsyncReadBridge.Cancellation token){return delegate.open(token).thenApply(handle->{opens.incrementAndGet();return new AsyncReadBridge.Handle(){
            final AtomicBoolean closed=new AtomicBoolean();public Long length(){return handle.length();}
            public CompletionStage<Integer> readAt(long at,byte[] target,int offset,int count,AsyncReadBridge.Cancellation cancellation){reads.incrementAndGet();return read(handle,at,target,offset,count,cancellation).thenApply(n->{if(n!=null && n>0)bytes.addAndGet(n);return n;});}
            public CompletionStage<Void> closeAsync(){return handle.closeAsync().thenRun(()->{if(closed.compareAndSet(false,true))closes.incrementAndGet();});}
        };});}
        CompletionStage<Integer> read(AsyncReadBridge.Handle handle,long at,byte[] target,int offset,int count,AsyncReadBridge.Cancellation token){return handle.readAt(at,target,offset,count,token);}
    }
    /** One real read stays pending until the test releases the original request; no synthetic frame. */
    private static final class GateProvider extends CountingProvider {
        final CountDownLatch entered=new CountDownLatch(1);final AtomicBoolean first=new AtomicBoolean(true);private Runnable pending;private boolean released;
        GateProvider(AsyncReadBridge.Provider source){super(source);}
        @Override CompletionStage<Integer> read(AsyncReadBridge.Handle handle,long at,byte[] target,int offset,int count,AsyncReadBridge.Cancellation token){
            if(!first.compareAndSet(true,false))return super.read(handle,at,target,offset,count,token);
            CompletableFuture<Integer> result=new CompletableFuture<>();Runnable actual=()->{try{handle.readAt(at,target,offset,count,token).whenComplete((n,error)->{if(error==null)result.complete(n);else result.completeExceptionally(error);});}catch(Throwable error){result.completeExceptionally(error);}};
            synchronized(this){if(released)actual.run();else pending=actual;}entered.countDown();return result;
        }
        void release(){Runnable original;synchronized(this){released=true;original=pending;pending=null;}if(original!=null)original.run();}
    }
}
