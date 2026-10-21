package com.videokit.d1input;
import androidx.media3.datasource.*;
import com.videokit.spike.c14.*;
import com.videokit.spike.e4.E13SourceGroup;
import java.io.*;
import java.nio.*;
import java.util.concurrent.*;
import static com.videokit.d1input.InputSinkCheck.*;

/** Tester-only bounded host fault injection; real frozen production classes and Media3 jars. */
public class IndependentBoundaryCheck {
 static class TailSink extends MemSink {
  volatile Thread tail;
  CountDownLatch release=new CountDownLatch(1), entered=new CountDownLatch(1);
  boolean writeWithTail;
  public CompletionStage<Integer> writeAt(long at,byte[] data,int o,int n){
   if(!writeWithTail)return super.writeAt(at,data,o,n);
   writes++;CompletableFuture<Integer> ack=new CompletableFuture<>();
   tail=new Thread(()->{bytes.write(data,o,n);physical+=n;ack.complete(n);try{release.await();}catch(InterruptedException e){Thread.currentThread().interrupt();}},"tester-original-write-tail");tail.start();return ack;
  }
  void startTail() throws Exception {
   tail=new Thread(()->{entered.countDown();try{release.await();}catch(InterruptedException e){Thread.currentThread().interrupt();}},"tester-original-host-tail");
   tail.start();need(entered.await(2,TimeUnit.SECONDS),"tail started");
  }
  public boolean originalOperationsReturned(){return tail==null||!tail.isAlive();}
  public boolean writerOriginalsReturned(){return closed;}
  void returnTail()throws Exception {release.countDown();if(tail!=null){tail.join(2000);need(!tail.isAlive(),"same original tail joined");}}
 }
 static void inputIndependent()throws Exception {
  Source s=new Source(20L);HostInputFactory f=factory(s);
  try{factory(s);throw new AssertionError("same provider bypass");}catch(IOException e){need(e.getMessage().equals("SOURCE_RESOURCE_EXHAUSTED"),"same provider gate");}
  HostDataSource a=f.createDataSource();a.open(spec(f,0,4));a.close();need(f.awaitOriginalReturns(5000),"old epoch original returned");a.open(spec(f,7,3));byte[] b=new byte[3];need(a.read(b,0,3)==3&&b[0]==value(7),"new epoch uses new offset");close(a,f);
  Source t=new Source(2L);HostInputFactory g=factory(t);HostDataSource d=g.createDataSource();int opens=t.opens.get();
  DataSpec alien=new DataSpec.Builder().setUri("https://private.invalid/credential").build();rejected(()->d.open(alien),"OPAQUE_READ_ONLY_SOURCE_REQUIRED");need(t.opens.get()==opens,"alien URI no host open");close(d,g);
  System.out.println("PASS independent_same_provider_cross_factory_and_new_epoch_and_capability");
 }
 static void rejectedFlushAdmission()throws Exception {
  TailSink h=new TailSink();h.writeWithTail=true;TemporaryOutput s=output(h);s.channel().write(ByteBuffer.wrap(new byte[]{1,2,3,4}));s.channel().close();
  try{
   rejected(s::finishWriter,"OUTPUT_ORIGINAL_PENDING");need(h.flushes==0&&h.closes==0,"not invoked while original tail active");
   h.returnTail();String retry="NO_ERROR";try{s.finishWriter();}catch(IOException e){retry=e.getMessage();}
   need(h.flushes==0&&h.closes==1&&retry.equals("OUTPUT_ORIGINAL_PENDING"),"reproduce consumed flush attempt before admission");
   System.out.println("REPRO B01 flushAdmissionRejected_then_originalTailReturned flushCalls="+h.flushes+" closeCalls="+h.closes+" retry="+retry+" state="+s.state());
  }finally{h.returnTail();need(s.abort(),"B01 cleanup abort same owner");}
 }
 static void validationTail()throws Exception {
  TailSink h=new TailSink();TemporaryOutput s=output(h);s.channel().write(ByteBuffer.wrap(new byte[]{1,2,3,4}));finish(s);
  try{
   s.verifyAndValidate((id,n,sha)->{try{h.startTail();}catch(Exception e){throw new RuntimeException(e);}return CompletableFuture.completedFuture(new HostOutput.Validation(id,n,sha,"HOST_ISOLATED_FORMAT_V1",true));});
   need(!h.originalOperationsReturned()&&s.writerReturned(),"writer returned distinct from validation original tail");
   s.markReady();s.finishOriginalCallbacks();need(h.readies==1&&s.returned()&&!h.originalOperationsReturned(),"reproduce READY/owner release before validation tail");
   System.out.println("REPRO B02 validatorFutureCompleted_originalTailAlive READY="+h.readies+" ownerReturned="+s.returned()+" hostOriginalReturned="+h.originalOperationsReturned()+" retained="+TemporaryOutput.retained());
  }finally{h.returnTail();if(!s.returned())need(s.abort(),"B02 cleanup");}
 }
 static void commitTail()throws Exception {
  TailSink h=new TailSink();TemporaryOutput s=output(h);s.channel().write(ByteBuffer.wrap(new byte[]{1,2,3,4}));finish(s);s.verifyAndValidate(h.controlledValidator(true,"HOST_ISOLATED_FORMAT_V1"));s.markReady();
  try{
   s.commitByExplicitHost((id,token)->{try{h.startTail();}catch(Exception e){throw new RuntimeException(e);}h.commits++;return CompletableFuture.completedFuture(null);});
   s.finishOriginalCallbacks();need(s.committed()&&s.returned()&&!h.originalOperationsReturned(),"reproduce owner release before explicit commit original tail");
   System.out.println("REPRO B02 explicitCommitFutureCompleted_originalTailAlive committed="+s.committed()+" ownerReturned="+s.returned()+" hostOriginalReturned="+h.originalOperationsReturned());
  }finally{h.returnTail();if(!s.returned())s.finishOriginalCallbacks();}
 }
 static void acknowledgedThenPartialFailure()throws Exception {
  MemSink h=new MemSink(){public CompletionStage<Integer> writeAt(long at,byte[] data,int o,int n){if(writes==0){partial=3;return super.writeAt(at,data,o,n);}partialFault=true;return super.writeAt(at,data,o,n);}};
  TemporaryOutput s=output(h);ByteBuffer caller=ByteBuffer.wrap(new byte[32]);
  rejected(()->s.channel().write(caller),"OUTPUT_NO_SPACE");
  need(s.acknowledgedBytesLowerBound()==3&&caller.position()==3&&h.physical==10&&s.writeAmountUnknown(),"known ACK prefix distinct from actual failed prefix");
  int calls=h.writes;rejected(()->s.channel().write(caller),"OUTPUT_NOT_WRITABLE");need(h.writes==calls&&s.abort()&&s.writeAmountUnknown(),"sticky no resubmission/refund");
  System.out.println("PASS independent_A02_firstACK3_then_failedActual7 totalPhysical10 acknowledgedLowerBound3 callerPosition3 UNKNOWN_preserved=true");
 }
 public static void main(String[] args)throws Exception {
  inputIndependent();acknowledgedThenPartialFailure();rejectedFlushAdmission();validationTail();commitTail();
  need(HostInputFactory.admittedSources()==0&&TemporaryOutput.retained()==0&&E13SourceGroup.canFinish(),"all controlled original owners cleaned");
  System.out.println("DONE independent scenarios=5 reproducedDefects=2 originalThreadsJoined=true retainedSources=0 retainedOutputs=0 realAndroidMedia=NOT_RUN");
 }
}
