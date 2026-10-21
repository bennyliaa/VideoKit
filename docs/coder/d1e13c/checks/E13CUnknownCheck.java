package com.videokit.spike.e4;
import java.io.*;
import java.nio.file.*;
/** Actual helper with test-only supervisor retention substitute; no persistent JVM/SDK/real scope. */
public final class E13CUnknownCheck {
 public static void main(String[] a)throws Exception{
  E9PcSupervisor s=new E9PcSupervisor("LOCAL_UNKNOWN_SUBSTITUTE");Path dir=Paths.get(a[0]);Files.createDirectories(dir);
  int[] closes={0},dispatch={0};E11DeploymentOnce once=E11DeploymentOnce.e13Activation(dir.resolve("e13a-activation-deployment.once"),s,stage->{if(stage.equals("CLOSE_AFTER")){closes[0]++;throw new IOException("CONTROLLED_CLOSE_RETURN_UNKNOWN");}});
  byte[] intent=new E9Record(E9Record.map("kind","e13ActivationDispatchIntent","testOnly","true"),4096).bytes();
  try{once.record(intent);dispatch[0]++;throw new AssertionError("accepted unknown");}catch(IOException expected){if(!expected.getMessage().equals("CONTROLLED_CLOSE_RETURN_UNKNOWN"))throw expected;}
  if(!once.state().equals("UNKNOWN")||once.returned()||s.authority!=once||s.resources.originalResourcesReturned()||closes[0]!=1||dispatch[0]!=0)throw new AssertionError("original UNKNOWN ownership lost");
  try{once.record(intent);throw new AssertionError("reentry accepted");}catch(IOException e){if(!e.getMessage().equals("E11_ONCE_OBJECT_REENTRY"))throw e;}
  if(closes[0]!=1||once.returned())throw new AssertionError("second close fabricated");
  System.out.println("PASS CLOSE_UNKNOWN actualHelper=true authoritySubstitute=true retainedSameOriginal=true holder=UNKNOWN originalReturn=false dispatch=0 closeAttempts=1 noSecondClose=true");
 }
}
