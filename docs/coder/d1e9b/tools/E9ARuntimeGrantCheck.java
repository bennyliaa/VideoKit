package com.videokit.spike.e4;
import java.nio.file.*;
/** SDK-stub runtime authority rejection must invalidate a previously real shared-object synthetic grant. */
public final class E9ARuntimeGrantCheck {
    public static void main(String[] args)throws Exception{
        E9ProductionSelfCheck.output=Paths.get(args[0]);E9ProductionSelfCheck.reference=Paths.get(args[1]);E9ProductionSelfCheck.selected="E9A_RUNTIME_INVALIDATION";Files.createDirectories(E9ProductionSelfCheck.output);
        try{
            E9ProductionSelfCheck.Fixture f=new E9ProductionSelfCheck.Fixture("runtime-grant");E9Catalog c=f.complete();E9TestFiles io=new E9TestFiles(f.device);E9ProductionSelfCheck.IO.add(io);E9CurrentObservation observation=new E9CurrentObservation(f.device,E9Catalog.fromTrustedRelease(c.record.bytes(),c.record.hash(),"SYNTHETIC_LOCAL"),io);
            if(!observation.observe().startsWith("FRESH_E9"))throw new AssertionError("NO_INITIAL_SHARED_GRANT");E5AAdmission.requireCurrent();
            String result=E9Runtime.observe(null);if(!result.contains("E9_PREPARE_PRODUCT_DISABLED"))throw new AssertionError(result);
            boolean rejected=false;try{E5AAdmission.requireCurrent();}catch(java.io.IOException expected){rejected=true;}if(!rejected)throw new AssertionError("RUNTIME_FAILURE_REUSED_PRIOR_GRANT");
            System.out.println("PASS actual_new_APK_runtime=success_shared_grant_then_runtime_rejection_then_requireCurrent_denied SDK_STUB_ONLY=true deviceCalls=0");
        }finally{for(E9TestFiles io:E9ProductionSelfCheck.IO)io.closeNativeFacsimilesAfterAssertions();}
    }
}
