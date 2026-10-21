package com.videokit.spike.e4;

import com.videokit.spike.c14.*;
import java.util.*;

/** Actual newly compiled Android public host methods, with SDK stubs only. No Android execution claim. */
public final class E9PublicAndroidEntryCheck {
    interface Call {void run()throws Exception;}
    static int calls;
    static void blocked(String name,Call call)throws Exception{
        try{call.run();throw new AssertionError("ENTRY_ACCEPTED:"+name);}catch(Exception e){
            String message=e.getMessage();if(message==null||!(message.equals("E9_PREPARE_PRODUCT_DISABLED")||message.equals("E9_LEGACY_RECOVERY_ENTRY_DISABLED")))throw new AssertionError("PHASE_DID_NOT_PRECEDE_PLATFORM:"+name,e);
            calls++;System.out.println("PASS actual_public_entry="+name+" rejection="+message+" platformStubNotReached=true");
        }
    }
    public static void main(String[] args)throws Exception{
        blocked("E4Session.constructor",()->new E4Session(null,null,0,"","",""));
        blocked("CpuTaskClient.constructor",()->new CpuTaskClient(null,null));
        blocked("E4CpuAdapter.constructor",()->new E4CpuAdapter(null,null,0));
        blocked("E4CpuAdapter.validate",()->E4CpuAdapter.validate(null,null,new long[0],List.of(),"",0,()->""));
        blocked("E5N2RecoveryAndroid.constructor",()->new E5N2RecoveryAndroid(null));
        String observation=E9Runtime.observe(null);if(!observation.contains("E9_PREPARE_PRODUCT_DISABLED"))throw new AssertionError(observation);calls++;System.out.println("PASS actual_public_entry=E9Runtime.observe result="+observation);
        if(E4Session.retainedSessions()!=0||E4Session.reservedEncoderSlots()!=0)throw new AssertionError("HOST_RESOURCE_REGISTERED");
        System.out.println("PASS publicEntries="+calls+" deviceCalls=0 AndroidRuntime=NOT_RUN");
    }
}
