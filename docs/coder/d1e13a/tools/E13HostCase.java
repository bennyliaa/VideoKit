package com.videokit.spike.e4;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.*;
/** Uses the original PC process/pipe/custodian and OriginalAuthority finish gate.
 * Android finish token alone is insufficient: its original instrument process must naturally return,
 * JUnit must pass the exact method, and all original pipes must be physically returned.
 */
public final class E13HostCase implements E9PcSupervisor.OriginalAuthority {
    private volatile boolean androidReturned;
    public boolean originalResourcesReturned(){return androidReturned;}
    public static void requireOwnerReturn(String raw,String scope,String method)throws IOException {
        String token="E13_PLATFORM_FINISH_ADMITTED scope="+scope+" case="+method+" ownersReturned=true";
        if(raw.indexOf(token)<0 || raw.indexOf(token)!=raw.lastIndexOf(token) || !(raw.contains("INSTRUMENTATION_CODE: -1")||raw.contains("INSTRUMENTATION_CODE: 0")))throw new IOException("E13_ORIGINAL_OWNER_RETURN_UNPROVEN");
    }
    public static void requireResult(String raw,String scope,String method)throws IOException {
        requireOwnerReturn(raw,scope,method);
        String token="E13_PLATFORM_FINISH_ADMITTED scope="+scope+" case="+method+" ownersReturned=true";
        if(raw.indexOf(token)<0 || raw.indexOf(token)!=raw.lastIndexOf(token) || !raw.contains("E13_RETURN_CHECK case="+method+" sourceRetained=0 canFinish=true") || !raw.contains("FRESH_E9_OBSERVATION_ADMITTED") || !raw.contains("OK (1 test)") || !raw.contains("INSTRUMENTATION_CODE: -1") || raw.contains("FAILURES!!!") || raw.contains("BLOCKED_SELECTION") || raw.contains("INSTRUMENTATION_STATUS_CODE: -2"))throw new IOException("E13_ANDROID_ORIGINAL_FINISH_UNPROVEN");
    }
    public static void main(String[] a)throws Exception {
        if(a.length==0){System.out.println("INSPECT_ONLY E13 exact-case plan; no dispatch");return;}
        if(a.length!=3)throw new IOException("E13_CASE_SCOPE_SHA_METHOD_REQUIRED");
        E9Record s=E13HostActivationSession.scope(E13HostActivationSession.pinned(Paths.get(a[0]),a[1],8192));String method=a[2];if(!E13Selection.METHODS.contains(method))throw new IOException("E13_EXACT_CASE");
        E13HostCase owner=new E13HostCase();E9PcSupervisor pc=new E9PcSupervisor("E13-CASE-"+a[1]+"-"+method);pc.retainAuthority(owner,null,owner);
        try{
            List<String> command=List.of("D:/Android/SDK/platform-tools/adb.exe","-s","HA1Q6WXR","shell","am","instrument","-w","-r","-e","class","com.videokit.spike.e4.E13DeviceTests#"+method,"-e","e13Case",method,"-e","e13Batch",E13Selection.BATCH,"-e","e13ScopeSha256",a[1],"com.videokit.app.test/com.videokit.spike.e4.E13Instrumentation");
            String raw=(String)pc.runDecoded("E13_EXACT_SOURCE_CASE",command,65536,E9PcSupervisor.GENERAL_NS,false,b->{String value=new String(b,StandardCharsets.UTF_8);requireOwnerReturn(value,a[1],method);owner.androidReturned=true;requireResult(value,a[1],method);return value;});
            System.out.print(raw);
        }finally{System.err.println("E13_PC_END "+new String(pc.closeIngressAndSupervise().bytes(),StandardCharsets.US_ASCII));}
    }
    private E13HostCase(){}
}
