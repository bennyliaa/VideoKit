package com.videokit.spike.e4;

import android.os.Bundle;
import android.content.Context;
import androidx.test.platform.app.InstrumentationRegistry;
import org.junit.Test;
import static org.junit.Assert.*;

/** Separately dispatched recovery admission only. Never selected by the product four-case batch. */
public final class E5RecoveryDeviceTests {
    @Test public void originalN2QueryOrAbort()throws Exception {
        Bundle args=InstrumentationRegistry.getArguments();String action=args.getString("e5N2Action","QUERY");
        assertTrue("Explicit recovery selection",action.equals("QUERY") || action.equals("ABORT_ORIGINAL_N2") || action.equals("OBSERVE_SETTLED_N2"));
        assertEquals(E5N2Recovery.TASK,args.getString("e5N2Task"));assertEquals(E5N2Recovery.BUDGET,args.getString("e5N2Budget"));
        assertEquals("D1-E5A-N2-RECOVERY-20261017",args.getString("e5RecoveryBatch"));
        Context c=InstrumentationRegistry.getInstrumentation().getTargetContext();
        E5N2RecoveryAndroid platform=new E5N2RecoveryAndroid(c);
        if(action.equals("OBSERVE_SETTLED_N2")){
            assertTrue(args.getString("e5aSettlementReceiptSha256","").matches("[a-f0-9]{64}"));String observed=new E5AFinalObservation(c.getFilesDir().toPath(),platform).observe();Bundle evidence=new Bundle();evidence.putString("stream","E5A_FINAL_OBSERVATION "+observed+" "+platform.evidence()+"\n");InstrumentationRegistry.getInstrumentation().sendStatus(0,evidence);assertTrue(observed,observed.startsWith("FRESH_OBSERVATION_ADMITTED"));return;
        }
        E5N2Recovery.Result r=new E5N2Recovery(c.getFilesDir().toPath(),platform).execute(action.equals("ABORT_ORIGINAL_N2"));
        Bundle status=new Bundle();status.putString("stream","E5_N2_RECOVERY "+r+"\nE5_N2_SYSTEM_EVIDENCE "+platform.evidence()+"\n");InstrumentationRegistry.getInstrumentation().sendStatus(0,status);
        assertEquals(action.equals("QUERY")?"QUERY_ELIGIBLE":"ABORTED_SETTLED",r.status);assertFalse(r.oldCloseAck);assertEquals(0,E5N2Recovery.retainedOperations());
    }
}
