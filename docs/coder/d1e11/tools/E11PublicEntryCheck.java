package com.videokit.spike.e4;
import com.videokit.spike.c14.*;
import java.nio.file.*;
import java.util.*;

/** Actual NEW Gradle app classes with SDK stubs; never Android execution. */
public final class E11PublicEntryCheck {
    interface Call {void run()throws Exception;}static int assertions;
    static void ok(boolean v){assertions++;if(!v)throw new AssertionError("SDK_PUBLIC_"+assertions);}
    static void denied(String name,Call action,String message)throws Exception{boolean no=false;try{action.run();}catch(Exception expected){if(!message.equals(expected.getMessage()))throw new AssertionError(name+" reached platform/wrong boundary",expected);no=true;}ok(no);System.out.println("PASS actual_new_gradle_public="+name+" denied="+message);}
    public static void main(String[] args)throws Exception{
        ok(E9BuildPolicy.role().equals("ACTIVATION"));ok(E9Phase.catalog().catalog().record.hash().equals("27fe90573f2d8a3a750c270e760f4e19e797fe188287ade5c58268e8c6d911b7"));
        String absent="E9_CURRENT_HOST_PROOF_REQUIRED";
        denied("E4Session",()->new E4Session(null,null,0,"","",""),absent);denied("CpuTaskClient",()->new CpuTaskClient(null,null),absent);denied("E4CpuAdapter",()->new E4CpuAdapter(null,null,0),absent);denied("E4CpuAdapter.validate",()->E4CpuAdapter.validate(null,null,new long[0],List.of(),"",0,()->""),absent);denied("legacy recovery",()->new E5N2RecoveryAndroid(null),"E9_LEGACY_RECOVERY_ENTRY_DISABLED");
        E9Actor old=E9Phase.catalog().catalog().actors[0];Map<String,String> f=new TreeMap<>();for(String k:new String[]{"registry","migration","ordinal","attempt","handle","descriptor","app","test","bootKind","environment"})f.put(k,old.record.get(k));f.put("kind","identityRequest");f.put("priorActor","ABSENT");f.put("priorEvidence","ABSENT");f.put("recoveryDisposition","NONE");E9Record request=new E9Record(f,8192);
        denied("old prepare test pair E9AndroidIdentity",()->new E9AndroidIdentity(null,request),"E9_MUTATING_ENTRY_DISABLED");
        E11ProductionCheck.out=Paths.get(args[0]);E11ProductionCheck.reference=Paths.get(args[1]);Files.createDirectories(E11ProductionCheck.out);E11ProductionCheck.Current synthetic=new E11ProductionCheck.Current("metadata-platform-substitute");ok(synthetic.observe.observe().startsWith("FRESH_E9"));E9Phase.requireProduct();ok(E11ActivationLifetime.canFinish());
        String result=E9Runtime.observe(null);ok(result.startsWith("BLOCKED E9_RELEASE_AUTHORITY:")&&result.contains("NullPointerException"));denied("runtime failed observation revoked prior grant",E9Phase::requireProduct,absent);ok(E11ActivationLifetime.canFinish());ok(E4Session.retainedSessions()==0&&E4Session.reservedEncoderSlots()==0);
        synthetic.io.closeNativeFacsimilesAfterAssertions();System.out.println("PASS SDK_PUBLIC assertions="+assertions+" actual_new_Gradle_classes=true AndroidRuntime=NOT_RUN deviceCalls=0");
    }
}
