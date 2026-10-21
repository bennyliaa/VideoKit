package com.videokit.spike.e4;
import java.nio.file.*;
import java.io.IOException;
/** Finite LOCAL synthetic once-record test, never an installer. */
public final class OnceCheck {
    public static void main(String[] a)throws Exception{
        String mode=a[0];Path path=Paths.get(a[1]),result=Paths.get(a[2]);E9PcSupervisor s=new E9PcSupervisor("E11_R1_SYNTHETIC_ONCE_"+mode);E11DeploymentOnce once=new E11DeploymentOnce(path,s,stage->{if(mode.equals("FORCE_FAIL")&&stage.equals("FORCE"))throw new IOException("SYNTHETIC_FORCE_FAILURE");if(mode.equals("CLOSE_UNKNOWN")&&stage.equals("CLOSE_AFTER"))throw new IOException("SYNTHETIC_NATIVE_CLOSE_NO_JAVA_ACK");});int dispatched=0;String outcome="RESERVED";
        E9Record record=new E9Record(E9Record.map("kind","syntheticDispatchIntent","config",E9Record.sha("synthetic_config".getBytes()),"release",E9Record.sha("synthetic_release".getBytes()),"state","OUTCOME_NOT_ASSUMED"),4096);
        try{once.record(record.bytes());dispatched++;}catch(Exception expected){outcome="BLOCKED";}
        boolean unknown=mode.equals("CLOSE_UNKNOWN");if(unknown&&(!once.state().equals("UNKNOWN")||once.returned()||dispatched!=0))throw new AssertionError("UNKNOWN_FALSE_CLOSE");
        if(mode.equals("FORCE_FAIL")&&(dispatched!=0||!once.returned()))throw new AssertionError("KNOWN_FAIL_NO_DISPATCH");
        E9Record ack=s.closeIngressAndSupervise();if(!ack.get("kind").equals(unknown?"pcIsolationAck":"pcClosed"))throw new AssertionError("OWNER_EXIT_BOUNDARY");
        Files.writeString(result,"{\"outcome\":\""+outcome+"\",\"simulatedDispatches\":"+dispatched+",\"state\":\""+once.state()+"\",\"originalReturned\":"+once.returned()+",\"productionExitAllowed\":"+!unknown+"}\n",StandardOpenOption.CREATE_NEW);
    }
}
