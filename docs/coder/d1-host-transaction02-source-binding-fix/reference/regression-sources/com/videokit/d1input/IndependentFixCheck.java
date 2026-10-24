package com.videokit.d1input;
import androidx.media3.datasource.*;
import com.videokit.spike.c14.*;
import com.videokit.spike.e4.E13SourceGroup;
import java.io.*;import java.nio.*;import java.util.*;import java.util.concurrent.*;
import static com.videokit.d1input.InputSinkCheck.*;

/** Tester-owned cases. Controlled ports only; no fake Media3 or product-state mutations. */
public final class IndependentFixCheck {
 static final List<Original<?>> jobs=new ArrayList<>();static int count;
 static class Original<T>{
  final CompletableFuture<T> ack=new CompletableFuture<>();final CountDownLatch work,tail=new CountDownLatch(1);final Thread thread;
  Original(String phase,boolean delay,Callable<T> body){work=new CountDownLatch(delay?1:0);thread=new Thread(()->{try{work.await();try{ack.complete(body.call());}catch(Throwable e){ack.completeExceptionally(e);}tail.await();}catch(InterruptedException e){ack.completeExceptionally(e);Thread.currentThread().interrupt();}},"tester-actual-"+phase);jobs.add(this);thread.start();}
  boolean returned(){return !thread.isAlive();}void ackNow()throws Exception{work.countDown();await(()->ack.isDone());}
  void joinSame()throws Exception{work.countDown();tail.countDown();thread.join(2500);need(!thread.isAlive(),"join exact original "+thread.getId());}
 }
 static class Host extends MemSink {
  final String tailPhase;Original<?> actual;int queries,reopens,reads;boolean delay,failAfterWrite;
  Host(String p){tailPhase=p;}
  <T>CompletionStage<T> stage(String phase,Callable<T> action){if(!tailPhase.equals(phase)){try{return CompletableFuture.completedFuture(action.call());}catch(Exception e){return failed(e);}}Original<T> j=new Original<>(phase,delay,()->{T value=action.call();if(failAfterWrite&&phase.equals("WRITE"))throw new IOException("private late failure");return value;});actual=j;return j.ack;}
  public CompletionStage<Integer> writeAt(long p,byte[] b,int o,int n){return stage("WRITE",()->super.writeAt(p,b,o,n).toCompletableFuture().get());}
  public CompletionStage<Void> flush(){return stage("FLUSH",()->super.flush().toCompletableFuture().get());}
  public CompletionStage<Void> closeWriter(){return stage("CLOSE",()->super.closeWriter().toCompletableFuture().get());}
  public CompletionStage<AsyncReadBridge.Provider> reopenReadOnly(){return stage("REOPEN",()->{reopens++;return super.reopenReadOnly().toCompletableFuture().get();});}
  public CompletionStage<String> markReady(String id){return stage("READY",()->super.markReady(id).toCompletableFuture().get());}
  public CompletionStage<Void> abort(String id){return stage("ABORT",()->super.abort(id).toCompletableFuture().get());}
  public CompletionStage<SinkCoordinator.Status> query(String id){return stage("QUERY",()->{queries++;return super.query(id).toCompletableFuture().get();});}
  public boolean originalOperationsReturned(){return actual==null||actual.returned();}public boolean writerOriginalsReturned(){return closed;}
  void joinSame()throws Exception{if(actual!=null)actual.joinSame();}
 }
 static class Validation implements HostOutput.Validator {
  Original<HostOutput.Validation> original;int calls;boolean delay,throwProof;
  public CompletionStage<HostOutput.Validation> validate(String id,long n,String sha){calls++;original=new Original<>("VALIDATE",delay,()->new HostOutput.Validation(id,n,sha,"HOST_ISOLATED_FORMAT_V1",true));return original.ack;}
  public boolean originalOperationsReturned(){if(throwProof)throw new IllegalStateException("private-proof");return original==null||original.returned();}
 }
 static class Commit implements HostOutput.Commit {
  Original<Void> original;int calls;boolean delay;
  public CompletionStage<Void> commit(String id,String token){calls++;original=new Original<>("COMMIT",delay,()->null);return original.ack;}
  public boolean originalOperationsReturned(){return original==null||original.returned();}
 }
 static void note(String key,TemporaryOutput s,Original<?> j){System.out.println(key+" sameThread="+(j==null?0:j.thread.getId())+" alive="+(j!=null&&j.thread.isAlive())+" keeper="+TemporaryOutput.retained()+" "+s.state());}
 static void written(TemporaryOutput s)throws Exception{s.channel().write(ByteBuffer.wrap(new byte[]{1,2,3,4}));s.channel().close();}
 static void finishAndValidate(TemporaryOutput s,MemSink h)throws Exception{written(s);s.finishWriter();s.verifyAndValidate(h.controlledValidator(true,"HOST_ISOLATED_FORMAT_V1"));}
 static void cleanup(TemporaryOutput s)throws Exception{for(Original<?> j:jobs)j.joinSame();s.observeOriginal();if(!s.returned()){if(s.readyAcknowledged())s.finishOriginalCallbacks();else need(s.abort(),"normal controlled abort");}need(s.returned(),"owner returned");}
 static void passed(String name){count++;System.out.println("PASS "+name);}
 static void inputAndPartial()throws Exception{
  Source source=new Source(20L);HostInputFactory f=factory(source);try{factory(source);throw new AssertionError("cross-factory alias");}catch(IOException e){need(e.getMessage().equals("SOURCE_RESOURCE_EXHAUSTED"),"same provider refused");}HostDataSource d=f.createDataSource();d.open(spec(f,0,4));d.close();need(f.awaitOriginalReturns(5000),"old epoch originals");d.open(spec(f,7,3));byte[] b=new byte[3];need(d.read(b,0,3)==3&&b[0]==value(7),"new offset7 generation");close(d,f);passed("original1_A01_cross_factory_epoch");
  MemSink h=new MemSink(){public CompletionStage<Integer> writeAt(long p,byte[] b,int o,int n){if(writes==0){partial=3;return super.writeAt(p,b,o,n);}partialFault=true;return super.writeAt(p,b,o,n);}};TemporaryOutput s=output(h);ByteBuffer c=ByteBuffer.wrap(new byte[32]);try{rejected(()->s.channel().write(c),"OUTPUT_NO_SPACE");need(h.physical==10&&s.acknowledgedBytesLowerBound()==3&&c.position()==3&&s.writeAmountUnknown(),"actual10 ACK3 caller3");long reserved=s.unknownWriteReservation();for(int i=0;i<3;i++)s.observeOriginal();need(s.unknownWriteReservation()==reserved,"UNKNOWN not duplicated by observation");rejected(()->s.channel().write(c),"OUTPUT_NOT_WRITABLE");}finally{cleanup(s);}passed("original2_A02_actual10_ACK3_UNKNOWN_once");
 }
 static void admission(String phase)throws Exception{
  Host h=new Host(phase);TemporaryOutput s=output(h);try{written(s);rejected(s::finishWriter,"OUTPUT_ORIGINAL_PENDING");if(phase.equals("WRITE"))need(h.flushes==0&&h.closes==0&&s.state().contains("flushPhase=NOT_ADMITTED"),"B01 no consumed admission");if(phase.equals("FLUSH"))need(h.flushes==1&&h.closes==0&&s.state().contains("closePhase=NOT_ADMITTED"),"close not admitted");rejected(s::finishWriter,"OUTPUT_ORIGINAL_PENDING");note("ADMISSION_"+phase,s,h.actual);h.joinSame();s.finishWriter();need(h.flushes==1&&h.closes==1&&s.firstFailure()==null,"after same original join flush1close1");}finally{cleanup(s);}passed("B01_"+phase);
 }
 static void validateTail()throws Exception{
  Host h=new Host("NONE");TemporaryOutput s=output(h);Validation v=new Validation();try{written(s);s.finishWriter();s.verifyAndValidate(v);need(h.originalOperationsReturned()&&s.writerReturned()&&!v.originalOperationsReturned(),"independent validator authority");rejected(s::markReady,"OUTPUT_ORIGINAL_PENDING");rejected(s::finishOriginalCallbacks,"OUTPUT_ORIGINAL_PENDING");need(h.readies==0&&!s.returned()&&TemporaryOutput.retained()==1,"B02 keeper stays");v.throwProof=true;rejected(s::markReady,"OUTPUT_ORIGINAL_PENDING");v.throwProof=false;note("VALIDATOR_TAIL",s,v.original);v.original.joinSame();s.markReady();s.finishOriginalCallbacks();need(v.calls==1&&h.readies==1&&s.returned(),"validator exact return");}finally{v.throwProof=false;cleanup(s);}passed("original4_B02_validator_separate_authority_and_unknown_proof");
 }
 static void commitTail()throws Exception{
  Host h=new Host("NONE");TemporaryOutput s=output(h);Commit c=new Commit();try{finishAndValidate(s,h);s.markReady();s.commitByExplicitHost(c);need(s.committed()&&!s.returned()&&TemporaryOutput.retained()==1,"ACK remains owner retained");rejected(s::finishOriginalCallbacks,"OUTPUT_ORIGINAL_PENDING");note("COMMIT_TAIL",s,c.original);c.original.joinSame();s.finishOriginalCallbacks();need(s.committed()&&s.returned()&&c.calls==1,"same commit exactly once");}finally{cleanup(s);}passed("original5_B02_commit_ACK_distinct_from_return");
 }
 static void reopenAndReady(String phase)throws Exception{
  Host h=new Host(phase);TemporaryOutput s=output(h);try{
   written(s);s.finishWriter();HostOutput.Validator v=h.controlledValidator(true,"HOST_ISOLATED_FORMAT_V1");
   if(phase.equals("REOPEN")){rejected(()->s.verifyAndValidate(v),"OUTPUT_ORIGINAL_PENDING");rejected(()->s.verifyAndValidate(v),"OUTPUT_ORIGINAL_PENDING");need(h.reopens==1,"no reopen replay");h.joinSame();s.verifyAndValidate(v);s.markReady();}
   else{s.verifyAndValidate(v);s.markReady();need(s.readyAcknowledged(),"READY ACK retained");rejected(()->s.commitByExplicitHost(h.controlledCommit()),"OUTPUT_ORIGINAL_PENDING");}
   if(phase.equals("READY")){rejected(s::finishOriginalCallbacks,"OUTPUT_ORIGINAL_PENDING");note("READY_TAIL",s,h.actual);h.joinSame();s.markReady();need(h.readies==1,"no READY replay");}
   s.finishOriginalCallbacks();need(s.returned(),"reopen READY tails joined");
  }finally{cleanup(s);}passed("B02_"+phase+"_same_cached_result");
 }
 static void abortQuery(String phase)throws Exception{
  Host h=new Host(phase);TemporaryOutput s=output(h);try{written(s);need(!s.abort()&&!s.returned(),"cleanup tail held");need(h.aborts==1&&(phase.equals("ABORT")?h.queries==0:h.queries==1),"no query before abort original return");need(!s.abort(),"no early owner release");note("CLEANUP_"+phase,s,h.actual);h.joinSame();need(s.abort()&&h.aborts==1&&h.queries==1&&s.returned(),"cached same RPC no repeat");}finally{cleanup(s);}passed("B02_"+phase+"_cached_RPC");
 }
 static void writeTimeoutFailure()throws Exception{
  Host h=new Host("WRITE");h.delay=true;h.failAfterWrite=true;TemporaryOutput s=new TemporaryOutput(h,false,WORKER,80);byte[] bytes={1,2,3,4};ByteBuffer c=ByteBuffer.wrap(bytes);try{rejected(()->s.channel().write(c),"OUTPUT_TIMEOUT_PENDING");long reserved=s.unknownWriteReservation();need(reserved==4&&c.position()==0&&!s.abort(),"retain original private block");bytes[0]=99;h.actual.ackNow();for(int i=0;i<3;i++)s.observeOriginal();need(s.unknownWriteReservation()==reserved&&s.writeAmountUnknown()&&s.firstFailure().equals("OUTPUT_TIMEOUT_PENDING"),"same failure observed without duplicate UNKNOWN");need(h.bytes.toByteArray()[0]==1,"original private block not caller alias");need(!s.abort(),"original write tail held despite failed ACK");h.joinSame();need(s.abort()&&s.unknownWriteReservation()==4,"abort no refund");}finally{cleanup(s);}passed("WRITE_timeout_late_failure_private_block_UNKNOWN_once");
 }
 public static void main(String[] args)throws Exception{
  System.out.println("ORIGIN="+TemporaryOutput.class.getProtectionDomain().getCodeSource().getLocation());
  try{inputAndPartial();admission("WRITE");validateTail();commitTail();admission("FLUSH");admission("CLOSE");reopenAndReady("REOPEN");reopenAndReady("READY");abortQuery("ABORT");abortQuery("QUERY");writeTimeoutFailure();need(HostInputFactory.admittedSources()==0&&TemporaryOutput.retained()==0&&E13SourceGroup.canFinish(),"all owners returned");System.out.println("DONE testerIndependentScenarios="+count+" sameOriginalThreadsJoined=true retainedSources=0 retainedOutputs=0 AndroidRuntime=NOT_RUN");}finally{for(Original<?> j:jobs)j.joinSame();}
 }
}
