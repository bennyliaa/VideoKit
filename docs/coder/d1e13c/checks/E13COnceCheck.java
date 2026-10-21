package com.videokit.spike.e4;
import java.io.*;
import java.nio.file.*;
import java.util.*;
import java.util.concurrent.*;
/** Executes actual helper and actual supervisor; filesystem/close scheduling only are controlled. */
public final class E13COnceCheck {
 static void require(boolean b,String m){if(!b)throw new AssertionError(m);}
 public static void main(String[] a)throws Exception{
  String mode=a[0];Path root=Paths.get(a[1]);Files.createDirectories(root);
  E9PcSupervisor supervisor=new E9PcSupervisor("E13C-LOCAL-"+mode);
  byte[] intent=new E9Record(E9Record.map("kind",mode.equals("WRONG_INTENT")?"activationDispatchIntent":"e13ActivationDispatchIntent","testOnly","true"),4096).bytes();
  String name=mode.equals("E11_OK")||mode.equals("E13_OLD_NAME")?"activation-deployment.once":mode.equals("ARBITRARY")?"arbitrary.once":"e13a-activation-deployment.once";
  Path oncePath=root.resolve(name);boolean[] dispatched={false};List<String> stages=new ArrayList<>();
  CountDownLatch entered=new CountDownLatch(1),release=new CountDownLatch(1);E11DeploymentOnce[] held=new E11DeploymentOnce[1];
  E11DeploymentOnce.Cut cut=s->{stages.add(s);if(s.equals("CLOSE_BEFORE"))require(Arrays.equals(Files.readAllBytes(oncePath),intent),"exact readback before original close");if(mode.equals("FORCE_FAIL")&&s.equals("FORCE"))throw new IOException("CONTROLLED_FORCE_FAILURE");if(mode.equals("CLOSE_IN_FLIGHT")&&s.equals("CLOSE_BEFORE")){entered.countDown();release.await();}};
  held[0]=mode.equals("E11_OK")||mode.equals("E11_NEW_NAME")?new E11DeploymentOnce(oncePath,supervisor,cut):E11DeploymentOnce.e13Activation(oncePath,supervisor,cut);
  if(mode.equals("CLOSE_IN_FLIGHT")){
   Throwable[] fail={null};Thread worker=new Thread(()->{try{held[0].record(intent);dispatched[0]=true;}catch(Throwable t){fail[0]=t;}});worker.start();require(entered.await(5,TimeUnit.SECONDS),"entered original close");
   require(!held[0].returned()&&held[0].state().equals("CLOSING")&&!dispatched[0],"no sdk while closing");
   require(supervisor.status().get("allOriginalsReturned").equals("false"),"original authority retained");
   E9Record ack=supervisor.closeIngressAndSupervise();require(ack.get("kind").equals("pcIsolationAck"),"actual original custodian pending ack");
   require(!supervisor.terminated(),"custodian has not returned");release.countDown();worker.join(5000);require(!worker.isAlive()&&fail[0]==null&&held[0].returned(),"same original close naturally returned");
   for(int i=0;i<100&&!supervisor.terminated();i++)Thread.sleep(20);require(supervisor.terminated(),"actual supervisor naturally returned");
   System.out.println("PASS CLOSE_IN_FLIGHT original=CLOSING retained=true sdkBeforeReturn=0 custody=pcIsolationAck sameOriginalNaturalReturn=true");return;
  }
  boolean ok=mode.equals("E11_OK")||mode.equals("E13_OK");
  try{E9HostRegistry.boundary(supervisor,()->{held[0].record(intent);dispatched[0]=true;});require(ok,"expected refusal");}
  catch(IOException e){require(!ok,"unexpected refusal "+e);require(!dispatched[0],"no dependent dispatch");System.out.println("REFUSED "+e.getMessage());}
  if(ok){require(held[0].returned()&&Arrays.equals(Files.readAllBytes(oncePath),intent),"exact persistent intent and close");require(stages.equals(List.of("WRITE","FORCE","CLOSE_BEFORE","CLOSE_AFTER")),"actual ordered helper stages");}
  if(!ok&&!mode.equals("FORCE_FAIL"))require(!Files.exists(oncePath),"role rejected before allocation");
  System.out.println("PASS "+mode+" sdkDispatch="+dispatched[0]+" holder="+held[0].state());
 }
}
