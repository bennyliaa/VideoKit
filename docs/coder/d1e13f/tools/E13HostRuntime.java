package com.videokit.spike.e4;
import java.util.*;
/** Fixed production dispatch. Package-private source seam permits explicit SDK/JVM substitutes in offline checks. */
final class E13HostRuntime {
 static E9PcSupervisor supervisor(String scope)throws Exception{return new E9PcSupervisor(scope);}
 static long caseBudget(){return E9PcSupervisor.GENERAL_NS;}
 static E9HostDeployment.Commands deploymentCommands(E9PcSupervisor pc){return new E9HostDeployment.Processes(pc);}
 static List<String> caseCommand(String scope,String method){return List.of("D:/Android/SDK/platform-tools/adb.exe","-s","HA1Q6WXR","shell","am","instrument","-w","-r","-e","class","com.videokit.spike.e4.E13DeviceTests#"+method,"-e","e13Case",method,"-e","e13Batch",E13Selection.BATCH,"-e","e13ScopeSha256",scope,"com.videokit.app.test/com.videokit.spike.e4.E13Instrumentation");}
 private E13HostRuntime(){}
}
