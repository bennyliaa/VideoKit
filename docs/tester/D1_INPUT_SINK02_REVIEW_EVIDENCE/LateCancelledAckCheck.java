package com.videokit.d1input;
import java.nio.*;import java.util.concurrent.*;
import static com.videokit.d1input.InputSinkCheck.*;
public class LateCancelledAckCheck {
 public static void main(String[] args)throws Exception{
  IndependentFixCheck.Original<?>[] job={null};
  MemSink h=new MemSink(){public CompletionStage<Integer> writeAt(long at,byte[] b,int o,int n){IndependentFixCheck.Original<Integer> j=new IndependentFixCheck.Original<>("WRITE_LATE_CANCELLED",true,()->{super.writeAt(at,b,o,n);throw new CancellationException("private-late-original-cancellation");});job[0]=j;return j.ack;}};
  TemporaryOutput s=new TemporaryOutput(h,false,WORKER,80);byte[] bytes={1,2,3,4};ByteBuffer c=ByteBuffer.wrap(bytes);
  try{
   rejected(()->s.channel().write(c),"OUTPUT_TIMEOUT_PENDING");bytes[0]=99;job[0].ackNow();String observe="",abort="";
   try{s.observeOriginal();}catch(Throwable t){observe=t.getClass().getSimpleName()+":"+t.getMessage();}
   need(!job[0].returned(),"same original tail retained");job[0].joinSame();try{s.abort();}catch(Throwable t){abort=t.getClass().getSimpleName()+":"+t.getMessage();}
   need(observe.startsWith("CancellationException:")&&abort.startsWith("CancellationException:")&&s.unknownWriteReservation()==4&&s.firstFailure().equals("OUTPUT_TIMEOUT_PENDING")&&TemporaryOutput.retained()==1,"same late terminal result unconsumed after original join");
   need(h.physical==4&&h.bytes.toByteArray()[0]==1&&c.position()==0,"private block and caller kept");
   System.out.println("ORIGIN="+TemporaryOutput.class.getProtectionDomain().getCodeSource().getLocation());
   System.out.println("REPRO LATE_CANCELLED_ACK afterSameOriginalJoin observe="+observe+" abort="+abort+" actual4 ACKlower0 UNKNOWNreservation4 firstTimeoutPreserved=true retained="+TemporaryOutput.retained()+" actualThreadAlive="+job[0].thread.isAlive()+" state="+s.state());
  }finally{for(IndependentFixCheck.Original<?> j:IndependentFixCheck.jobs)j.joinSame();}
 }
}
