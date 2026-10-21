package com.videokit.spike.e4;
import android.content.Context;
import android.os.*;
import android.os.Process;
import androidx.test.platform.app.InstrumentationRegistry;
import org.junit.*;
import org.junit.rules.TestName;
import static org.junit.Assert.*;
public final class E13DeviceTests {
    @Rule public final TestName selected=new TestName();private long began;
    private Context context(){return InstrumentationRegistry.getInstrumentation().getTargetContext();}
    private void evidence(String s){assertTrue(s.length()<=4096);Bundle b=new Bundle();b.putString("stream",s+" scope="+InstrumentationRegistry.getArguments().getString("e13ScopeSha256")+"\n");InstrumentationRegistry.getInstrumentation().sendStatus(0,b);}
    @Before public void observed()throws Exception {
        assertNotEquals(Looper.getMainLooper(),Looper.myLooper());assertEquals(selected.getMethodName(),InstrumentationRegistry.getArguments().getString("e13Case"));
        assertEquals(16,context().getPackageManager().getPackageInfo(context().getPackageName(),0).getLongVersionCode());assertEquals(10221,Process.myUid());
        assertTrue("No prior E13 source/control holder may be replaced",E13Instrumentation.canFinish());
        String value=E9Runtime.observe(context());evidence(value);assertTrue(value.startsWith("FRESH_E9_OBSERVATION_ADMITTED"));E9Phase.requireProduct();began=System.nanoTime();
    }
    private void source()throws Exception {E13SourceCases.run(selected.getMethodName(),Process.myUid(),Process.myPid(),this::evidence);}
    @After public void retainedBeforeFinish(){long elapsed=System.nanoTime()-began;evidence("E13_RETURN_CHECK case="+selected.getMethodName()+" sourceRetained="+E13SourceGroup.retained()+" canFinish="+E13Instrumentation.canFinish()+" elapsedNs="+elapsed);assertTrue("Original source/control holders returned",E13Instrumentation.canFinish());assertTrue("30s qualifies this result only; never terminates unknown work",elapsed<=30000000000L);}
    @Test public void ordinarySenderCannotBindCodec()throws Exception {Bundle r=E13PermissionProbe.run(context(),InstrumentationRegistry.getArguments().getString("e13ScopeSha256"));evidence("E13_KERNEL_BIND_REJECTION uid="+r.getInt("fixtureUid")+" pid="+r.getInt("fixturePid")+" outcome="+r.getString("kernelOutcome")+" internalTransactAttempted=false resourcesReturned="+r.getBoolean("resourcesReturned"));}
    @Test public void authorizedHostSourceReadAndClose()throws Exception {source();}
    @Test public void oldGenerationNeverOpensSource()throws Exception {source();}
    @Test public void twoConsumersHoldSourceUntilLastReturn()throws Exception {source();}
    @Test public void cancelLateOpenRetainsOriginalOwner()throws Exception {source();}
    @Test public void lateReadAndCloseFailureDoNotReleaseEarly()throws Exception {source();}
}
