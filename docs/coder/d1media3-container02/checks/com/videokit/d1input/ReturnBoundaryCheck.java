package com.videokit.d1input;
import androidx.media3.datasource.*;import com.videokit.spike.c14.*;import com.videokit.spike.e4.E13SourceGroup;
import java.io.*;import java.nio.*;import java.util.*;import java.util.concurrent.*;import static com.videokit.d1input.InputSinkCheck.*;

/** Tester five scenarios replayed against production classes; extra same-original phase tails.
 * Each Job executes the ACTUAL controlled host method on its original thread before ACK, then
 * holds THAT thread's tail. No replacement worker/counter is a physical-return proof. */
public final class ReturnBoundaryCheck {
 static final List<Job<?>> originals=new CopyOnWriteArrayList<>();static int scenarios;
 static final class Job<T> {
  final CompletableFuture<T> ack=new CompletableFuture<>();final CountDownLatch entered=new CountDownLatch(1),work,tail=new CountDownLatch(1);final Thread original;
  Job(String phase,boolean delayed,Callable<T> action){work=new CountDownLatch(delayed?1:0);original=new Thread(()->{entered.countDown();try{work.await();try{ack.complete(action.call());}catch(Throwable e){ack.completeExceptionally(e);}tail.await();}catch(InterruptedException e){ack.completeExceptionally(e);Thread.currentThread().interrupt();}},"actual-host-"+phase);originals.add(this);}
  void start(){original.start();try{need(entered.await(2,TimeUnit.SECONDS),"same original entered");}catch(InterruptedException e){throw new AssertionError(e);}}
  boolean returned(){return !original.isAlive();}
  void allowAck()throws Exception{work.countDown();await(()->ack.isDone());}
  void returnSame()throws Exception{work.countDown();tail.countDown();original.join(3000);need(!original.isAlive(),"same original physically joined");}
 }
 static class TailHost extends MemSink {
  final String phase;final boolean delayed;volatile Job<?> active;int reopens,queries;
  TailHost(String phase,boolean delayed){this.phase=phase;this.delayed=delayed;}
  <T>CompletionStage<T> run(String p,Callable<T> action){Job<T> j=new Job<>(p,delayed,action);active=j;j.start();return j.ack;}
  public CompletionStage<Integer> writeAt(long p,byte[] b,int o,int n){return phase.equals("WRITE")?run("WRITE",()->super.writeAt(p,b,o,n).toCompletableFuture().get()):super.writeAt(p,b,o,n);}
  public CompletionStage<Void> flush(){return phase.equals("FLUSH")?run("FLUSH",()->super.flush().toCompletableFuture().get()):super.flush();}
  public CompletionStage<Void> closeWriter(){return phase.equals("CLOSE")?run("CLOSE",()->super.closeWriter().toCompletableFuture().get()):super.closeWriter();}
  public CompletionStage<AsyncReadBridge.Provider> reopenReadOnly(){return phase.equals("REOPEN")?run("REOPEN",()->{reopens++;return super.reopenReadOnly().toCompletableFuture().get();}):normalReopen();}
  CompletionStage<AsyncReadBridge.Provider> normalReopen(){reopens++;return super.reopenReadOnly();}
  public CompletionStage<String> markReady(String id){return phase.equals("READY")?run("READY",()->super.markReady(id).toCompletableFuture().get()):super.markReady(id);}
  public CompletionStage<Void> abort(String id){return phase.equals("ABORT")?run("ABORT",()->super.abort(id).toCompletableFuture().get()):super.abort(id);}
  public CompletionStage<SinkCoordinator.Status> query(String id){if(phase.equals("QUERY"))return run("QUERY",()->{queries++;return super.query(id).toCompletableFuture().get();});queries++;return super.query(id);}
  public boolean originalOperationsReturned(){return active==null||active.returned();}public boolean writerOriginalsReturned(){return closed;}
  void returnSame()throws Exception{if(active!=null)active.returnSame();}
 }
 static class ValidatorPort implements HostOutput.Validator {
  final boolean delayed;Job<HostOutput.Validation> actual;int calls;ValidatorPort(boolean d){delayed=d;}
  public CompletionStage<HostOutput.Validation> validate(String id,long n,String sha){calls++;actual=new Job<>("VALIDATE",delayed,()->new HostOutput.Validation(id,n,sha,"HOST_ISOLATED_FORMAT_V1",true));actual.start();return actual.ack;}
  public boolean originalOperationsReturned(){return actual==null||actual.returned();}
 }
 static class CommitPort implements HostOutput.Commit {
  final MemSink host;final boolean delayed;Job<Void> actual;int calls;CommitPort(MemSink h,boolean d){host=h;delayed=d;}
  public CompletionStage<Void> commit(String id,String token){calls++;actual=new Job<>("COMMIT",delayed,()->{host.commits++;return null;});actual.start();return actual.ack;}
  public boolean originalOperationsReturned(){return actual==null||actual.returned();}
 }
 static void written(TemporaryOutput s)throws Exception{s.channel().write(ByteBuffer.wrap(new byte[]{1,2,3,4}));s.channel().close();}
 static void normalValidated(TemporaryOutput s,MemSink h)throws Exception{written(s);s.finishWriter();s.verifyAndValidate(h.controlledValidator(true,"HOST_ISOLATED_FORMAT_V1"));}
 static void note(String name,TemporaryOutput s,Job<?> original){System.out.println("OBSERVE "+name+" originalThreadId="+(original==null?0:original.original.getId())+" originalThreadAlive="+(original!=null&&original.original.isAlive())+" originalAckDone="+(original!=null&&original.ack.isDone())+" retained="+TemporaryOutput.retained()+" "+s.state());}
 static void cleanup(TemporaryOutput s)throws Exception{for(Job<?> j:originals)j.returnSame();s.observeOriginal();if(!s.returned()){if(s.readyAcknowledged()||s.committed())s.finishOriginalCallbacks();else need(s.abort(),"controlled cleanup abort");}need(s.returned(),"same original owner cleaned");}
 static void done(String name){scenarios++;System.out.println("PASS "+name);}
 static void inputIndependent()throws Exception {
  Source p=new Source(20L);HostInputFactory f=factory(p);try{factory(p);throw new AssertionError("same provider bypass");}catch(IOException e){need(e.getMessage().equals("SOURCE_RESOURCE_EXHAUSTED"),"same provider gate");}
  HostDataSource a=f.createDataSource();a.open(spec(f,0,4));a.close();need(f.awaitOriginalReturns(5000),"old originals");a.open(spec(f,7,3));byte[] out=new byte[3];need(a.read(out,0,3)==3&&out[0]==value(7),"new epoch exact offset");close(a,f);
  Source q=new Source(2L);HostInputFactory g=factory(q);HostDataSource d=g.createDataSource();DataSpec alien=new DataSpec.Builder().setUri("https://private.invalid/credential").build();rejected(()->d.open(alien),"OPAQUE_READ_ONLY_SOURCE_REQUIRED");need(q.opens.get()==0,"no alien host open");close(d,g);done("tester1_A01_cross_factory_epoch_capability");
 }
 static void partialIndependent()throws Exception {
  MemSink h=new MemSink(){public CompletionStage<Integer> writeAt(long p,byte[] b,int o,int n){if(writes==0){partial=3;return super.writeAt(p,b,o,n);}partialFault=true;return super.writeAt(p,b,o,n);}};TemporaryOutput s=output(h);ByteBuffer caller=ByteBuffer.wrap(new byte[32]);
  try{rejected(()->s.channel().write(caller),"OUTPUT_NO_SPACE");need(s.acknowledgedBytesLowerBound()==3&&caller.position()==3&&h.physical==10&&s.writeAmountUnknown(),"physical10 ACK3 position3 UNKNOWN");int calls=h.writes;rejected(()->s.channel().write(caller),"OUTPUT_NOT_WRITABLE");need(h.writes==calls&&s.abort()&&s.writeAmountUnknown(),"no rewind/retry/refund");note("A02_physical10_ACK3_position3",s,null);}finally{cleanup(s);}done("tester2_A02_actual10_ACK3_sticky");
 }
 static void preAdmission(String phase)throws Exception {
  TailHost h=new TailHost(phase,false);TemporaryOutput s=output(h);
  try{written(s);rejected(s::finishWriter,"OUTPUT_ORIGINAL_PENDING");if(phase.equals("WRITE"))need(h.flushes==0&&h.closes==0&&s.state().contains("flushPhase=NOT_ADMITTED"),"B01 did not consume flush admission");if(phase.equals("FLUSH"))need(h.flushes==1&&h.closes==0&&s.state().contains("closePhase=NOT_ADMITTED"),"close not admitted while original flush tail");if(phase.equals("CLOSE"))need(h.flushes==1&&h.closes==1,"close ACK distinct from tail");note("B01_before_"+phase+"_return",s,h.active);rejected(s::finishWriter,"OUTPUT_ORIGINAL_PENDING");h.returnSame();s.finishWriter();need(h.flushes==1&&h.closes==1&&s.firstFailure()==null,"exactly once flush then close after original return");note("B01_after_"+phase+"_return",s,h.active);}finally{cleanup(s);}done("B01_"+phase+"_not_admitted_vs_executed");
 }
 static void validatorTail(boolean hostAlsoTracks)throws Exception {
  TailHost h=new TailHost("NONE",false);TemporaryOutput s=output(h);ValidatorPort v=new ValidatorPort(false){public boolean originalOperationsReturned(){return super.originalOperationsReturned();}};
  try{written(s);s.finishWriter();s.verifyAndValidate(v);if(hostAlsoTracks)h.active=v.actual;need(s.writerReturned()&&!v.originalOperationsReturned(),"writer and validator real originals distinct");rejected(s::markReady,"OUTPUT_ORIGINAL_PENDING");rejected(s::finishOriginalCallbacks,"OUTPUT_ORIGINAL_PENDING");need(h.readies==0&&!s.returned()&&TemporaryOutput.retained()==1,"B02 no READY/no slot refund");note("B02_validator_early_ACK_hostTracks="+hostAlsoTracks,s,v.actual);v.actual.returnSame();s.markReady();s.finishOriginalCallbacks();need(h.readies==1&&v.calls==1&&s.returned(),"same validator returned then READY once");}finally{cleanup(s);}done(hostAlsoTracks?"tester4_B02_validator_tail":"B02_independent_validator_authority_host_writer_true");
 }
 static void commitTail(boolean delayed)throws Exception {
  MemSink h=new MemSink();TemporaryOutput s=new TemporaryOutput(h,false,WORKER,delayed?100:500);CommitPort c=new CommitPort(h,delayed);
  try{normalValidated(s,h);s.markReady();if(delayed)rejected(()->s.commitByExplicitHost(c),"OUTPUT_TIMEOUT_PENDING");else s.commitByExplicitHost(c);rejected(s::finishOriginalCallbacks,"OUTPUT_ORIGINAL_PENDING");need(!s.returned()&&TemporaryOutput.retained()==1&&h.originalOperationsReturned(),"independent COMMIT original authority required");note("B02_commit_before_original_return",s,c.actual);c.actual.allowAck();s.observeOriginal();need(s.committed()&&!s.returned(),"ACK preserved not original return");rejected(s::finishOriginalCallbacks,"OUTPUT_ORIGINAL_PENDING");c.actual.returnSame();s.finishOriginalCallbacks();need(s.committed()&&s.returned()&&h.commits==1&&c.calls==1,"same COMMIT original exits; never rollback ACK");note("B02_commit_after_original_return",s,c.actual);}finally{cleanup(s);}done(delayed?"B02_COMMIT_timeout_then_same_late_ACK_and_return":"tester5_B02_COMMIT_early_ACK_tail");
 }
 static void reopenTail()throws Exception {
  TailHost h=new TailHost("REOPEN",false);TemporaryOutput s=output(h);int[] validatorCalls={0};HostOutput.Validator v=new HostOutput.Validator(){public CompletionStage<HostOutput.Validation> validate(String id,long n,String sha){validatorCalls[0]++;return CompletableFuture.completedFuture(new HostOutput.Validation(id,n,sha,"HOST_ISOLATED_FORMAT_V1",true));}public boolean originalOperationsReturned(){return true;}};
  try{written(s);s.finishWriter();rejected(()->s.verifyAndValidate(v),"OUTPUT_ORIGINAL_PENDING");need(h.reopens==1&&validatorCalls[0]==0&&!s.returned(),"reopen ACK cannot cross original tail");note("REOPEN_ACK_before_same_tail_return",s,h.active);h.returnSame();s.verifyAndValidate(v);s.markReady();s.finishOriginalCallbacks();need(h.reopens==1&&validatorCalls[0]==1,"retained original reopen result, no second reopen");}finally{cleanup(s);}done("B02_REOPEN_early_ACK_no_later_stage_until_original");
 }
 static void readyTail(boolean delayed)throws Exception {
  TailHost h=new TailHost("READY",delayed);TemporaryOutput s=new TemporaryOutput(h,false,WORKER,delayed?100:500);CommitPort c=new CommitPort(h,false);
  try{normalValidated(s,h);if(delayed)rejected(s::markReady,"OUTPUT_READY_UNKNOWN");else s.markReady();rejected(s::finishOriginalCallbacks,"OUTPUT_ORIGINAL_PENDING");note("READY_before_original_return",s,h.active);if(delayed){h.active.allowAck();await(s::readyAcknowledged);}else rejected(()->s.commitByExplicitHost(c),"OUTPUT_ORIGINAL_PENDING");need(s.readyAcknowledged()&&!s.returned()&&h.readies==1,"real READY ACK retained, owner held");h.returnSame();if(!delayed){need(s.markReady()!=null&&h.readies==1,"same READY ACK, no replay");s.commitByExplicitHost(h.controlledCommit());}s.finishOriginalCallbacks();need(s.returned()&&h.readies==1,"READY original tail returned");}finally{cleanup(s);}done(delayed?"B02_READY_timeout_late_ACK_no_rollback":"B02_READY_early_ACK_blocks_COMMIT_admission");
 }
 static void pendingPhase(String phase)throws Exception {
  TailHost h=new TailHost(phase,true);TemporaryOutput s=new TemporaryOutput(h,false,WORKER,100);
  try{written(s);rejected(s::finishWriter,"OUTPUT_TIMEOUT_PENDING");int calls=phase.equals("FLUSH")?h.flushes:h.closes;rejected(s::finishWriter,"OUTPUT_NOT_VALIDATABLE");need((phase.equals("FLUSH")?h.flushes:h.closes)==calls,"no duplicate original pending invocation");need(!s.abort(),"keep pending original");h.active.allowAck();s.observeOriginal();need(!s.abort()&&!s.returned(),"ACK not original thread tail");note(phase+"_late_ACK_tail",s,h.active);h.returnSame();need(s.abort()&&h.flushes==1&&h.closes==1&&s.firstFailure().equals("OUTPUT_TIMEOUT_PENDING"),"exact original flush/close once; first failure preserved");}finally{cleanup(s);}done("B01_"+phase+"_ACK_PENDING_never_blind_retry");
 }
 static void validatorTimeout()throws Exception {
  MemSink h=new MemSink();TemporaryOutput s=new TemporaryOutput(h,false,WORKER,100);ValidatorPort v=new ValidatorPort(true);
  try{written(s);s.finishWriter();rejected(()->s.verifyAndValidate(v),"OUTPUT_TIMEOUT_PENDING");need(!s.abort(),"validator original pending");v.actual.allowAck();s.observeOriginal();need(s.validationAcknowledged()&&!s.returned()&&!s.abort()&&h.readies==0,"late validator ACK recorded, no READY while tail");note("VALIDATE_timeout_late_ACK",s,v.actual);v.actual.returnSame();need(s.abort()&&v.calls==1&&h.readies==0,"no revalidation or READY after timeout");}finally{cleanup(s);}done("B02_VALIDATE_timeout_original_receipt_retained");
 }
 static void cleanupPhaseTail(String phase)throws Exception {
  TailHost h=new TailHost(phase,false);TemporaryOutput s=output(h);
  try{written(s);need(!s.abort()&&!s.returned()&&TemporaryOutput.retained()==1,"abort/query ACK alone not full return");note(phase+"_early_ACK",s,h.active);if(phase.equals("ABORT"))need(h.aborts==1&&h.queries==0,"query not admitted while abort tail");else need(h.aborts==1&&h.queries==1,"query ACK current original");h.returnSame();need(s.abort()&&s.returned()&&h.aborts==1&&h.queries==1&&h.closes==1,"same original cached ACK, no new host cleanup invocations");}finally{cleanup(s);}done("B02_"+phase+"_same_original_once");
 }
 public static void main(String[] args)throws Exception {
  System.out.println("ORIGIN TemporaryOutput="+TemporaryOutput.class.getProtectionDomain().getCodeSource().getLocation());
  try{inputIndependent();partialIndependent();preAdmission("WRITE");validatorTail(true);commitTail(false);validatorTail(false);preAdmission("FLUSH");preAdmission("CLOSE");reopenTail();readyTail(false);pendingPhase("FLUSH");pendingPhase("CLOSE");validatorTimeout();readyTail(true);commitTail(true);cleanupPhaseTail("ABORT");cleanupPhaseTail("QUERY");need(HostInputFactory.admittedSources()==0&&TemporaryOutput.retained()==0&&E13SourceGroup.canFinish(),"no original owner lost");System.out.println("DONE originalReturnScenarios="+scenarios+" originalThreadsJoined=true retainedSources=0 retainedOutputs=0 realAndroidMedia=NOT_RUN");}
  finally{for(Job<?> j:originals)j.returnSame();}
 }
}
