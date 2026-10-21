package com.videokit.d1input;
import com.videokit.spike.c14.*;import com.videokit.spike.e4.E13SourceGroup;
import java.io.*;import java.nio.*;import java.util.*;import java.util.concurrent.*;import static com.videokit.d1input.InputSinkCheck.*;

/** Actual original host action, its original ACK and THAT thread's tail are controlled separately.
 * No SDK future is cancelled; exception modes complete the original ACK exceptionally. */
public final class ExceptionMatrixCheck {
 static final List<Actual<?>> jobs=new ArrayList<>();static int cases;
 static final class Actual<T>{
  final CompletableFuture<T> ack=new CompletableFuture<>();final CountDownLatch work,tail=new CountDownLatch(1);final Thread thread;
  Actual(String phase,String mode,Callable<T> action){work=new CountDownLatch(mode.startsWith("LATE")?1:0);thread=new Thread(()->{try{work.await();try{T result=action.call();if(mode.endsWith("CANCEL"))throw new CancellationException("private-host-cancellation-detail");if(mode.endsWith("EXEC"))throw new IOException("private-host-io-detail");ack.complete(result);}catch(Throwable e){ack.completeExceptionally(e);}tail.await();}catch(InterruptedException e){ack.completeExceptionally(e);Thread.currentThread().interrupt();}},"matrix-actual-"+phase);jobs.add(this);thread.start();}
  void ackNow()throws Exception{work.countDown();await(()->ack.isDone());}boolean returned(){return !thread.isAlive();}
  void joinSame()throws Exception{work.countDown();tail.countDown();thread.join(3000);need(!thread.isAlive(),"same original thread joined");}
 }
 static final class Host extends MemSink {
  final String phase,mode;Actual<?> actual;int entries,queries,reopens;boolean proofThrows,published;final CommitPort commit=new CommitPort();
  Host(String p,String m){phase=p;mode=m;}
  <T>CompletionStage<T> stage(String p,Callable<T> body){
   if(!phase.equals(p)){try{return CompletableFuture.completedFuture(body.call());}catch(Exception e){return failed(e);}}
   entries++;
   if(mode.equals("THROW_CANCEL")){try{body.call();}catch(Exception e){throw new AssertionError(e);}throw new CancellationException("private-inline-original-cancellation");}
   Actual<T> j=new Actual<>(p,mode,body);actual=j;return j.ack;
  }
  public CompletionStage<Integer> writeAt(long p,byte[] b,int o,int n){return stage("WRITE",()->super.writeAt(p,b,o,n).toCompletableFuture().get());}
  public CompletionStage<Void> flush(){return stage("FLUSH",()->super.flush().toCompletableFuture().get());}
  public CompletionStage<Void> closeWriter(){return stage("CLOSE",()->super.closeWriter().toCompletableFuture().get());}
  public CompletionStage<AsyncReadBridge.Provider> reopenReadOnly(){return stage("REOPEN",()->{reopens++;return super.reopenReadOnly().toCompletableFuture().get();});}
  public CompletionStage<String> markReady(String id){return stage("READY",()->super.markReady(id).toCompletableFuture().get());}
  public CompletionStage<Void> abort(String id){return stage("ABORT",()->super.abort(id).toCompletableFuture().get());}
  public CompletionStage<SinkCoordinator.Status> query(String id){return stage("QUERY",()->{queries++;return super.query(id).toCompletableFuture().get();});}
  public boolean originalOperationsReturned(){if(proofThrows)throw new IllegalStateException("private-original-proof");return actual==null||actual.returned();}
  public boolean writerOriginalsReturned(){return closed;}
  public SinkCoordinator.Status originalTerminalStatus(String id){need(id.equals(opaqueTask()),"same task authority");return published?new SinkCoordinator.Status(status,status==SinkCoordinator.HostState.READY?"controlled_ready_token":null):new SinkCoordinator.Status(SinkCoordinator.HostState.UNKNOWN,null);}
  final class ValidatorPort implements HostOutput.Validator {
   Actual<HostOutput.Validation> original;
   public CompletionStage<HostOutput.Validation> validate(String id,long n,String sha){entries++;if(mode.equals("THROW_CANCEL"))throw new CancellationException("private-validator-inline");original=new Actual<>("VALIDATE",mode,()->new HostOutput.Validation(id,n,sha,"HOST_ISOLATED_FORMAT_V1",true));return original.ack;}
   public boolean originalOperationsReturned(){if(proofThrows)throw new IllegalStateException("private-validator-proof");return original==null||original.returned();}
  }
  final class CommitPort implements HostOutput.Commit {
   Actual<Void> original,query;HostOutput.CommitOutcome resolution=HostOutput.CommitOutcome.UNKNOWN;String id,token;
   public CompletionStage<Void> commit(String task,String ready){entries++;id=task;token=ready;if(mode.equals("THROW_CANCEL")){commits++;throw new CancellationException("private-commit-inline");}original=new Actual<>("COMMIT",mode,()->{commits++;return null;});return original.ack;}
   public boolean originalOperationsReturned(){if(proofThrows)throw new IllegalStateException("private-commit-proof");return (original==null||original.returned())&&(query==null||query.returned());}
   public HostOutput.CommitOutcome originalOutcome(String task,String ready){need(Objects.equals(task,id)&&Objects.equals(ready,token),"exact original commit task/token");return resolution;}
   void querySameOriginal(){need(query==null,"one actual host authority query");query=new Actual<>("COMMIT_ORIGINAL_QUERY","ACK",()->{resolution=commits==1?HostOutput.CommitOutcome.CONFIRMED_COMMITTED:HostOutput.CommitOutcome.CONFIRMED_NOT_APPLIED;return null;});}
  }
 }
 static Throwable invoke(Callable<?> action)throws Exception{try{action.call();return null;}catch(IOException e){need(e.getCause()==null&&!e.getMessage().contains("private"),"stable IOException without private cause");return e;}catch(Throwable raw){throw new AssertionError("unmapped boundary exception",raw);}}
 static void note(String phase,String mode,String point,TemporaryOutput s,Actual<?> j){System.out.println("OBSERVE phase="+phase+" mode="+mode+" point="+point+" thread="+(j==null?Thread.currentThread().getId():j.thread.getId())+" alive="+(j!=null&&j.thread.isAlive())+" ACKdone="+(j!=null&&j.ack.isDone())+" retained="+TemporaryOutput.retained()+" "+s.state());}
 static void written(TemporaryOutput s)throws Exception{s.channel().write(ByteBuffer.wrap(new byte[]{1,2,3,4}));s.channel().close();}
 static void one(String phase,String mode)throws Exception{
  Host h=new Host(phase,mode);Host.ValidatorPort v=h.new ValidatorPort();TemporaryOutput s=new TemporaryOutput(h,false,WORKER,80);byte[] bytes={1,2,3,4};ByteBuffer caller=ByteBuffer.wrap(bytes);Actual<?> original=null;
  try{
   if(!phase.equals("WRITE"))written(s);
   if(List.of("REOPEN","VALIDATE","READY","COMMIT").contains(phase))s.finishWriter();
   if(List.of("READY","COMMIT").contains(phase))s.verifyAndValidate(h.controlledValidator(true,"HOST_ISOLATED_FORMAT_V1"));
   if(phase.equals("COMMIT"))s.markReady();
   Throwable thrown=invoke(()->{switch(phase){case "WRITE":return s.channel().write(caller);case "FLUSH":case "CLOSE":s.finishWriter();return null;case "REOPEN":case "VALIDATE":return s.verifyAndValidate(phase.equals("VALIDATE")?v:h.controlledValidator(true,"HOST_ISOLATED_FORMAT_V1"));case "READY":return s.markReady();case "COMMIT":s.commitByExplicitHost(h.commit);return null;default:return s.abort();}});
   original=phase.equals("VALIDATE")?v.original:phase.equals("COMMIT")?h.commit.original:h.actual;
   if(!mode.equals("ACK"))need(s.firstFailure()!=null,"entered exception/timeout first failure retained "+phase+"/"+mode);
   if(mode.startsWith("LATE"))need(original!=null&&!original.ack.isDone(),"same original ACK still pending at timeout");
   if(phase.equals("WRITE")){bytes[0]=99;if(!mode.equals("ACK"))need(s.writeAmountUnknown()&&s.unknownWriteReservation()==4&&caller.position()==0,"entered WRITE without valid ACK is UNKNOWN once");}
   if(original!=null){need(!s.returned()&&TemporaryOutput.retained()==1,"ACK/failure not original physical return");h.proofThrows=true;need(!s.abort()&&!s.returned()&&h.entries==1,"unknown original authority actively blocks cleanup without another RPC");rejected(s::finishOriginalCallbacks,"OUTPUT_ORIGINAL_PENDING");h.proofThrows=false;original.ackNow();}
   String first=s.firstFailure();for(int n=0;n<4;n++)s.observeOriginal();need(Objects.equals(first,s.firstFailure()),"late result never replaces earlier first failure");
   if(phase.equals("WRITE")){need(h.physical==4&&h.bytes.toByteArray()[0]==1,"actual private block before caller mutation");if(!mode.equals("ACK"))need(s.unknownWriteReservation()==4,"one UNKNOWN reservation across observations");}
   note(phase,mode,"ACK_OR_FAILURE_ORIGINAL_TAIL",s,original);
   if(original!=null){need(!s.returned(),"tail still holds owner");original.joinSame();}
   if(phase.equals("COMMIT")&&!mode.equals("ACK")&&!mode.equals("LATE_ACK")){
    s.observeOriginal();need(!s.committed()&&!s.returned()&&!s.abort(),"returned cancelled/failed COMMIT has UNKNOWN business outcome");rejected(s::finishOriginalCallbacks,"OUTPUT_ORIGINAL_PENDING");
    h.commit.querySameOriginal();h.commit.query.ackNow();s.observeOriginal();need(!s.returned()&&!s.committed(),"host query result cannot cross its SAME original tail");h.commit.query.joinSame();s.observeOriginal();need(s.committed(),"exact original host authority confirms actual side effect, not cancellation inference");
   }
   if(phase.equals("QUERY")&&!mode.equals("ACK")&&!mode.equals("LATE_ACK")){need(!s.abort()&&!s.returned(),"failed QUERY no terminal proof retains owner");h.published=true;}
   // No new target invocation. Cleanup may confirm the real host terminal or retain READY.
   for(int n=0;n<4&&!s.returned();n++){s.observeOriginal();if(s.readyAcknowledged()||s.committed())invoke(()->{s.finishOriginalCallbacks();return null;});else s.abort();}
   need(s.returned()&&TemporaryOutput.retained()==0,"same original resources returned after proven terminal "+phase+"/"+mode);
   need(h.entries==1&&Objects.equals(first,s.firstFailure()),"exact once original entry + sticky history");
   if(mode.equals("ACK"))need(first==null,"normal ACK or unadmitted pending never creates a failure");
   note(phase,mode,"SAME_ORIGINAL_JOINED_TERMINAL_PROVEN",s,original);cases++;System.out.println("PASS matrix "+phase+" "+mode);
  }finally{h.proofThrows=false;for(Actual<?> j:jobs)j.joinSame();if(!s.returned()){h.published=true;if(phase.equals("COMMIT")){if(h.commit.query==null)h.commit.querySameOriginal();h.commit.query.joinSame();}s.observeOriginal();if(s.readyAcknowledged())s.finishOriginalCallbacks();else s.abort();}need(s.returned(),"failure-path test cleanup never drops original owner");}
 }
 public static void main(String[] args)throws Exception{
  System.out.println("ORIGIN="+TemporaryOutput.class.getProtectionDomain().getCodeSource().getLocation());
  for(String phase:List.of("WRITE","FLUSH","CLOSE","REOPEN","VALIDATE","READY","COMMIT","ABORT","QUERY"))for(String mode:List.of("ACK","EXEC","CANCEL","LATE_ACK","LATE_EXEC","LATE_CANCEL","THROW_CANCEL"))one(phase,mode);
  need(HostInputFactory.admittedSources()==0&&TemporaryOutput.retained()==0&&E13SourceGroup.canFinish(),"all exact original keepers returned");System.out.println("DONE phaseExceptionCases="+cases+" sameOriginalThreadsJoined=true sourceKeepers=0 outputKeepers=0 AndroidRuntime=NOT_RUN");
 }
}
