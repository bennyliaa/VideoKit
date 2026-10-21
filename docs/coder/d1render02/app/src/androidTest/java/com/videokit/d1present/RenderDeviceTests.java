package com.videokit.d1present;
import android.app.Application;
import android.content.Intent;
import android.os.Bundle;
import androidx.test.ext.junit.runners.AndroidJUnit4;
import androidx.test.platform.app.InstrumentationRegistry;
import org.junit.*;
import org.junit.runner.RunWith;
import java.util.concurrent.TimeUnit;
import static org.junit.Assert.*;

/** Compiled future whole-cluster entry points. No device invocation is part of coder build. */
@RunWith(AndroidJUnit4.class)
public final class RenderDeviceTests {
    private PresentationActivity activity;
    private Bundle args(){return InstrumentationRegistry.getArguments();}
    @Before public void scope(){
        assertEquals("One reviewed exact method only",getClass().getName()+"#"+args().getString("renderCase"),args().getString("class"));
        assertTrue("Coordinator scope is required, syntax is NOT execution permission",args().getString("renderScopeSha256","").matches("[a-f0-9]{64}"));
        assertEquals("Target exact presentation process", "com.videokit.d1present:presentation",Application.getProcessName());
        if("manualIdleListenThreeSeconds".equals(args().getString("renderCase")))assertEquals("IDLE_LISTEN_3S_V1",args().getString("renderManual"));
        else assertFalse("Automatic methods never opt into manual sound",args().containsKey("renderManual"));
    }
    private WorkSession start(boolean generated,int rotation)throws Exception {
        return start(generated,rotation,false);
    }
    private WorkSession start(boolean generated,int rotation,boolean paused)throws Exception {
        Intent intent=new Intent(InstrumentationRegistry.getInstrumentation().getTargetContext(),PresentationActivity.class).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
        activity=(PresentationActivity)InstrumentationRegistry.getInstrumentation().startActivitySync(intent);
        long deadline=System.nanoTime()+TimeUnit.SECONDS.toNanos(5);
        while(!activity.surfaceAvailable()&&System.nanoTime()<deadline)Thread.sleep(10);
        assertTrue("Real texture availability required",activity.surfaceAvailable());
        final Throwable[] error={null};InstrumentationRegistry.getInstrumentation().runOnMainSync(()->{try{activity.startProbe(generated,rotation,paused);}catch(Throwable t){error[0]=t;}});
        if(error[0]!=null)throw new AssertionError(error[0]);return activity.session();
    }
    @Test public void generatedMutedDualConsumers()throws Exception {normal(true,90);}
    @Test public void existingMp4RawMutedDualConsumers()throws Exception {normal(false,0);}
    private void normal(boolean generated,int rotation)throws Exception {
        WorkSession s=start(generated,rotation);assertFalse("Default must remain muted",s.audibleRequested());
        assertTrue("Actual owners, not elapsed window",s.await(30000));assertNull(s.state(),s.failure());assertTrue(s.sourceReleased());assertEquals(0,s.pixels.held());
        assertTrue(s.renderConsumerReturned());assertTrue(s.audioConsumerReturned());
        assertEquals("All six actual submissions required, not a zero-frame green run",6,s.drawn());assertEquals(576000,s.pcmSubmitted());
        assertTrue(s.video.peak()<=2);assertTrue(s.audio.peak()<=4);System.out.println("D1_RENDER_ORIGINALS "+s.state());
        for(String receipt:s.frameReceipts())System.out.println("D1_RENDER_FRAME "+receipt);
        for(String receipt:s.consumerReceipts())System.out.println("D1_RENDER_CONSUMER "+receipt);
        assertTrue("First actual consumer cannot release the whole source",s.consumerReceipts().get(0).contains("sourceReleased=false"));
        // Screenshot, actual sound, direction and user-visible effect require independent external evidence.
    }
    @Test public void cancelRejectsLateGeneration()throws Exception {
        WorkSession s=start(true,0,true);long ready=System.nanoTime()+TimeUnit.SECONDS.toNanos(5);
        while(s.video.inFlight()==0&&s.failure()==null&&System.nanoTime()<ready)Thread.sleep(2);
        assertNull("Cancellation needs the real loaded source, not an unrelated setup failure",s.failure());
        assertEquals(1,s.video.inFlight());assertFalse(s.sourceReleased());
        long e=s.gate.epoch(),surface=s.gate.surface();s.cancel();
        assertFalse(s.gate.accepts(e,surface));assertTrue(s.await(30000));assertTrue(s.sourceReleased());assertEquals(0,s.pixels.held());
        assertTrue("Only qualified cancellation is accepted",s.failure()==null||"SESSION_CANCELLED".equals(s.failure()));
        System.out.println("D1_RENDER_CANCEL_ORIGINALS "+s.state());
    }
    @Test public void pausedSeekAndSurfaceRecreation()throws Exception {
        WorkSession s=start(true,90,true);long oldEpoch=s.gate.epoch(),oldSurface=s.gate.surface();
        InstrumentationRegistry.getInstrumentation().runOnMainSync(activity::recreateSurface);
        long deadline=System.nanoTime()+TimeUnit.SECONDS.toNanos(5);while(!activity.surfaceAvailable()&&System.nanoTime()<deadline)Thread.sleep(10);
        assertTrue(activity.surfaceAvailable());s.seek();assertFalse(s.gate.accepts(oldEpoch,oldSurface));assertFalse("Intent cannot be an owner ACK",s.gate.renderAcknowledged());
        s.pause(false);assertTrue(s.await(30000));assertNull(s.state(),s.failure());assertTrue(s.drawn()>0&&s.drawn()<=6);assertTrue(s.sourceReleased());
        for(String receipt:s.frameReceipts()){assertTrue(receipt,receipt.contains("playEpoch="+s.gate.epoch()));assertTrue(receipt,receipt.contains("surfaceGeneration="+s.gate.surface()));System.out.println("D1_RENDER_RECREATED "+receipt);}
    }
    @Test public void manualIdleListenThreeSeconds()throws Exception {
        Intent intent=new Intent(InstrumentationRegistry.getInstrumentation().getTargetContext(),PresentationActivity.class)
            .addFlags(Intent.FLAG_ACTIVITY_NEW_TASK).putExtra("renderManualIdle",true);
        activity=(PresentationActivity)InstrumentationRegistry.getInstrumentation().startActivitySync(intent);
        long ready=System.nanoTime()+TimeUnit.SECONDS.toNanos(5);
        while(!activity.surfaceAvailable()&&System.nanoTime()<ready)Thread.sleep(10);
        assertTrue("Manual surface preparation capped at 5s",activity.surfaceAvailable());assertNull("Must remain idle",activity.session());
        InstrumentationRegistry.getInstrumentation().runOnMainSync(activity::armManualListen);
        Bundle marker=new Bundle();marker.putString("stream","RENDER02_MANUAL_IDLE_READY click Listen once within15s; no session/sound started\n");
        InstrumentationRegistry.getInstrumentation().sendStatus(0,marker);
        long idle=System.nanoTime()+ManualListenWindow.IDLE_NS;
        while(!activity.manualListenStarted()&&activity.manualListenFailure()==null&&System.nanoTime()<idle)Thread.sleep(10);
        final boolean[] started={false};InstrumentationRegistry.getInstrumentation().runOnMainSync(()->started[0]=activity.closeManualIdle());
        assertNull(activity.manualListenFailure());assertTrue("No click is not a listening result",started[0]);
        WorkSession s=activity.session();assertNotNull(s);assertTrue("Initial explicit intent before audio admission",s.audibleRequested());
        assertTrue("Window expiry never proves original return",s.await(30000));assertNull(s.state(),s.failure());
        assertEquals(576000,s.pcmSubmitted());assertTrue(s.sourceReleased());assertEquals(0,s.pixels.held());
        System.out.println("RENDER02_MANUAL_LIFECYCLE_ONLY "+s.state()+" actualListening=REQUIRES_INDEPENDENT_HUMAN_EVIDENCE");
    }
    @After public void finishOnlyAfterOriginals(){
        if(activity!=null&&activity.session()==null)InstrumentationRegistry.getInstrumentation().runOnMainSync(()->{if("manualIdleListenThreeSeconds".equals(args().getString("renderCase")))activity.closeManualIdle();activity.finish();});
        if(activity!=null&&activity.session()!=null){activity.session().cancel();if(activity.session().returned())InstrumentationRegistry.getInstrumentation().runOnMainSync(activity::finish);}
    }
}
