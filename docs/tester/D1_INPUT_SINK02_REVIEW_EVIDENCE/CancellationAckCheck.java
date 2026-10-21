package com.videokit.d1input;
import java.nio.*;import java.util.concurrent.*;import java.io.*;
import com.videokit.spike.c14.*;
import static com.videokit.d1input.InputSinkCheck.*;
/** Independent terminal-failure check, isolated JVM per phase, no files or worker tasks. */
public class CancellationAckCheck {
 static <T>CompletionStage<T> cancelledAck(){CompletableFuture<T> f=new CompletableFuture<>();f.completeExceptionally(new CancellationException("private-host-cancellation-detail"));return f;}
 public static void main(String[] args)throws Exception{
  String phase=args[0];MemSink h=new MemSink(){
   public CompletionStage<Integer> writeAt(long p,byte[] b,int o,int n){if(phase.equals("WRITE")){writes++;return cancelledAck();}return super.writeAt(p,b,o,n);}
   public CompletionStage<Void> flush(){if(phase.equals("FLUSH")){flushes++;return cancelledAck();}return super.flush();}
   public CompletionStage<Void> closeWriter(){if(phase.equals("CLOSE")){closes++;closed=true;return cancelledAck();}return super.closeWriter();}
   public CompletionStage<AsyncReadBridge.Provider> reopenReadOnly(){return phase.equals("REOPEN")?cancelledAck():super.reopenReadOnly();}
  };TemporaryOutput s=output(h);String thrown="NONE",observed="NONE",aborted="NONE";ByteBuffer caller=ByteBuffer.wrap(new byte[]{1,2,3,4});
  try{
   s.channel().write(caller);s.channel().close();s.finishWriter();
   HostOutput.Validator v=phase.equals("VALIDATE")?new HostOutput.Validator(){public CompletionStage<HostOutput.Validation> validate(String id,long n,String sha){return cancelledAck();}public boolean originalOperationsReturned(){return true;}}:h.controlledValidator(true,"HOST_ISOLATED_FORMAT_V1");
   s.verifyAndValidate(v);s.markReady();
   if(phase.equals("COMMIT"))s.commitByExplicitHost(new HostOutput.Commit(){public CompletionStage<Void> commit(String id,String token){return cancelledAck();}public boolean originalOperationsReturned(){return true;}});
  }catch(Throwable t){thrown=t.getClass().getSimpleName()+":"+t.getMessage();}
  try{s.observeOriginal();}catch(Throwable t){observed=t.getClass().getSimpleName()+":"+t.getMessage();}
  try{aborted=String.valueOf(s.abort());}catch(Throwable t){aborted=t.getClass().getSimpleName()+":"+t.getMessage();}
  System.out.println("ORIGIN="+TemporaryOutput.class.getProtectionDomain().getCodeSource().getLocation());
  System.out.println("RESULT phase="+phase+" originalHostReturned="+h.originalOperationsReturned()+" thrown="+thrown+" observe="+observed+" abort="+aborted+" callerPos="+caller.position()+" actualWriteCalls="+h.writes+" keeper="+TemporaryOutput.retained()+" state="+s.state());
  need(thrown.startsWith("CancellationException:")&&observed.startsWith("CancellationException:")&&aborted.startsWith("CancellationException:")&&TemporaryOutput.retained()==1,"reproduce unconsumed terminal cancelled original ACK");
  if(phase.equals("WRITE"))need(!s.writeAmountUnknown()&&s.firstFailure()==null,"missing sticky failure and UNKNOWN");
  System.out.println("REPRO CANCELLED_ACK_UNCONSUMED noActiveHostThreads=true JVMexitReclaimsMemoryOnly=true device=NOT_RUN");
 }
}
