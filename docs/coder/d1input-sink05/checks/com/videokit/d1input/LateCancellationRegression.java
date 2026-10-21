package com.videokit.d1input;
import java.nio.*;import java.util.concurrent.*;import static com.videokit.d1input.InputSinkCheck.*;
public final class LateCancellationRegression {
 public static void main(String[] args)throws Exception{
  IndependentFixCheck.Original<?>[] job={null};MemSink h=new MemSink(){
   public CompletionStage<Integer> writeAt(long at,byte[] b,int o,int n){IndependentFixCheck.Original<Integer> j=new IndependentFixCheck.Original<>("WRITE_LATE_CANCELLED",true,()->{super.writeAt(at,b,o,n);throw new CancellationException("private-late-original-cancellation");});job[0]=j;return j.ack;}
   public boolean originalOperationsReturned(){return job[0]==null||job[0].returned();}
  };TemporaryOutput s=new TemporaryOutput(h,false,WORKER,80);byte[] bytes={1,2,3,4};ByteBuffer c=ByteBuffer.wrap(bytes);
  try{rejected(()->s.channel().write(c),"OUTPUT_TIMEOUT_PENDING");bytes[0]=99;job[0].ackNow();for(int n=0;n<5;n++)s.observeOriginal();need(!s.abort()&&!s.returned(),"cancelled ACK not exact original tail return");need(s.state().contains("pending=false")&&s.unknownWriteReservation()==4&&s.firstFailure().equals("OUTPUT_TIMEOUT_PENDING"),"late terminal consumed once, first timeout and UNKNOWN4 sticky");need(h.physical==4&&h.bytes.toByteArray()[0]==1&&c.position()==0,"private original block and caller position");job[0].joinSame();need(s.abort()&&s.returned()&&TemporaryOutput.retained()==0,"exact same original returns before cleanup");
   System.out.println("ORIGIN="+TemporaryOutput.class.getProtectionDomain().getCodeSource().getLocation());System.out.println("PASS tester_late_cancel actual4 ACKlower0 UNKNOWN4 timeoutSticky=true originalThreadJoined=true "+s.state());
  }finally{for(IndependentFixCheck.Original<?> j:IndependentFixCheck.jobs)j.joinSame();need(s.returned()||s.abort(),"failure cleanup original owner");}
 }
}
