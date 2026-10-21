package com.videokit.d1input;
import java.io.*;import java.nio.*;import java.util.*;import java.util.concurrent.*;import com.videokit.spike.c14.*;import com.videokit.spike.e4.E13SourceGroup;import static com.videokit.d1input.InputSinkCheck.*;
/** Bad values come from the exact admitted original host action, never SDK state mutation. */
public final class HostResultCheck {
 static int cases;static final List<Job> originals=new ArrayList<>();
 @SuppressWarnings("unchecked") static <T>CompletionStage<T> raw(Object value){return (CompletionStage<T>)(CompletionStage<?>)CompletableFuture.completedFuture(value);}
 static class Job {
  final CompletableFuture<Object> ack=new CompletableFuture<>();final CountDownLatch work,tail=new CountDownLatch(1);final Thread thread;
  Job(boolean late,Callable<Object> action){work=new CountDownLatch(late?1:0);thread=new Thread(()->{try{work.await();try{ack.complete(action.call());}catch(Throwable e){ack.completeExceptionally(e);}tail.await();}catch(InterruptedException e){ack.completeExceptionally(e);Thread.currentThread().interrupt();}},"result-actual-host");originals.add(this);thread.start();}
  void ackNow()throws Exception{work.countDown();await(()->ack.isDone());}boolean returned(){return !thread.isAlive();}void joinSame()throws Exception{work.countDown();tail.countDown();thread.join(3000);need(!thread.isAlive(),"exact original result thread joined");}
 }
 static class Host extends MemSink {
  final String phase,shape,delivery;String granted;int targetCalls,queries,reopens;Job actual;boolean trusted;HostOutput.CommitOutcome commitFact=HostOutput.CommitOutcome.UNKNOWN;
  Host(String p,String s,String d){phase=p;shape=s;delivery=d;granted=task;}
  public String opaqueTask(){return granted;}
  Object value(Object correct)throws Exception{
   switch(shape){case "NULL":return null;case "WRONG_TYPE":return phase.equals("READY")?1:"private-not-the-declared-type";case "NULL_STAGE":return correct;case "VOID_VALUE":return 1;case "ZERO":return 0;case "NEGATIVE":return -1;case "TOO_LARGE":return 5;case "OVERFLOW":return Integer.MAX_VALUE;case "LONG_ACK":return 4L;case "EMPTY":return "";case "BLANK":return "   ";case "CONTROL":return "private\ncontrol";default:break;}
   if(phase.equals("QUERY"))return status(shape);
   if(phase.equals("VALIDATE")){HostOutput.Validation v=(HostOutput.Validation)correct;return new HostOutput.Validation(shape.equals("WRONG_TASK")?"wrong_task":v.task,shape.equals("NEG_BYTES")?-1:shape.equals("LONG_BYTES")?Long.MAX_VALUE:shape.equals("WRONG_BYTES")?3:v.bytes,shape.equals("WRONG_SHA")?"wrong-sha":v.sha256,shape.equals("WRONG_KIND")?"WRONG_KIND":v.kind,!shape.equals("FALSE_VALID"));}
   if(phase.equals("REOPEN"))return provider(shape);
   return correct;
  }
  @SuppressWarnings("unchecked") <T>CompletionStage<T> result(String p,Callable<T> body){
   if(!phase.equals(p)){try{return CompletableFuture.completedFuture(body.call());}catch(Exception e){return failed(e);}}
   targetCalls++;
   if(delivery.equals("IMMEDIATE")){try{Object actualValue=value(body.call());return shape.equals("NULL_STAGE")?null:raw(actualValue);}catch(Exception e){return failed(e);}}
   actual=new Job(delivery.equals("LATE"),()->value(body.call()));return (CompletionStage<T>)(CompletionStage<?>)actual.ack;
  }
  public CompletionStage<Integer> writeAt(long at,byte[] b,int o,int n){return result("WRITE",()->super.writeAt(at,b,o,n).toCompletableFuture().get());}
  public CompletionStage<Void> flush(){return result("FLUSH",()->super.flush().toCompletableFuture().get());}
  public CompletionStage<Void> closeWriter(){return result("CLOSE",()->super.closeWriter().toCompletableFuture().get());}
  public CompletionStage<AsyncReadBridge.Provider> reopenReadOnly(){return result("REOPEN",()->{reopens++;return super.reopenReadOnly().toCompletableFuture().get();});}
  public CompletionStage<String> markReady(String id){need(id.equals(task),"captured original grant task for READY");return result("READY",()->super.markReady(id).toCompletableFuture().get());}
  public CompletionStage<Void> abort(String id){need(id.equals(task),"captured original task for ABORT");return result("ABORT",()->super.abort(id).toCompletableFuture().get());}
  public CompletionStage<SinkCoordinator.Status> query(String id){need(id.equals(task),"captured original task for QUERY");return result("QUERY",()->{queries++;return super.query(id).toCompletableFuture().get();});}
  public boolean originalOperationsReturned(){return actual==null||actual.returned();}public boolean writerOriginalsReturned(){return closed;}
  public SinkCoordinator.Status originalTerminalStatus(String id){need(id.equals(task),"original readonly terminal task");return trusted?new SinkCoordinator.Status(status,status==SinkCoordinator.HostState.READY?"controlled_ready_token":null):new SinkCoordinator.Status(SinkCoordinator.HostState.UNKNOWN,null);}
  HostOutput.Validator validator(){return new HostOutput.Validator(){public CompletionStage<HostOutput.Validation> validate(String id,long n,String sha){need(id.equals(task),"original validator task");return result("VALIDATE",()->new HostOutput.Validation(id,n,sha,"HOST_ISOLATED_FORMAT_V1",true));}public boolean originalOperationsReturned(){return Host.this.originalOperationsReturned();}};}
  HostOutput.Commit commit(){return new HostOutput.Commit(){public CompletionStage<Void> commit(String id,String token){need(id.equals(task)&&"controlled_ready_token".equals(token),"original COMMIT task/token");return result("COMMIT",()->{commits++;return null;});}public boolean originalOperationsReturned(){return Host.this.originalOperationsReturned();}public HostOutput.CommitOutcome originalOutcome(String id,String token){need(id.equals(task)&&"controlled_ready_token".equals(token),"original outcome binding");return commitFact;}};}
  AsyncReadBridge.Provider provider(String which){
   if(which.equals("NULL_HANDLE"))return c->CompletableFuture.completedFuture(null);
   byte[] stored=bytes.toByteArray();return c->CompletableFuture.completedFuture(new AsyncReadBridge.Handle(){
    public Long length(){if(which.equals("UNKNOWN_LENGTH"))return null;if(which.equals("NEG_LENGTH"))return -1L;if(which.equals("LONG_LENGTH"))return Long.MAX_VALUE;if(which.equals("WRONG_LENGTH"))return 3L;return (long)stored.length;}
    public CompletionStage<Integer> readAt(long p,byte[] b,int o,int n,AsyncReadBridge.Cancellation c){if(which.equals("BAD_READ_COUNT"))return CompletableFuture.completedFuture(n+1);if(p>=stored.length)return CompletableFuture.completedFuture(-1);int count=Math.min(n,stored.length-(int)p);for(int i=0;i<count;i++)b[o+i]=which.equals("WRONG_DIGEST")?(byte)99:stored[(int)p+i];return CompletableFuture.completedFuture(count);}
    public CompletionStage<Void> closeAsync(){return CompletableFuture.completedFuture(null);}
   });
  }
 }
 static SinkCoordinator.Status status(String shape){
  switch(shape){case "STATE_NULL":return new SinkCoordinator.Status(null,null);case "READY_NULL":return new SinkCoordinator.Status(SinkCoordinator.HostState.READY,null);case "READY_EMPTY":return new SinkCoordinator.Status(SinkCoordinator.HostState.READY,"");case "READY_BLANK":return new SinkCoordinator.Status(SinkCoordinator.HostState.READY,"   ");case "READY_CONTROL":return new SinkCoordinator.Status(SinkCoordinator.HostState.READY,"bad\ncontrol");case "ABORTED_TOKEN":return new SinkCoordinator.Status(SinkCoordinator.HostState.ABORTED,"unexpected");case "WRITING_TOKEN":return new SinkCoordinator.Status(SinkCoordinator.HostState.WRITING,"unexpected");case "UNKNOWN_TOKEN":return new SinkCoordinator.Status(SinkCoordinator.HostState.UNKNOWN,"unexpected");case "WRITING":return new SinkCoordinator.Status(SinkCoordinator.HostState.WRITING,null);default:return new SinkCoordinator.Status(SinkCoordinator.HostState.UNKNOWN,null);}
 }
 interface Call {void run()throws Exception;}
 static IOException stable(Call c)throws Exception{try{c.run();return null;}catch(IOException e){need(e.getCause()==null&&!e.getMessage().contains("private"),"stable no-private error");return e;}catch(Throwable t){throw new AssertionError("raw host result escaped",t);}}
 static void note(String phase,String shape,String delivery,String point,TemporaryOutput s,Job j){System.out.println("OBSERVE phase="+phase+" shape="+shape+" delivery="+delivery+" point="+point+" originalThread="+(j==null?0:j.thread.getId())+" alive="+(j!=null&&j.thread.isAlive())+" ACKdone="+(j!=null&&j.ack.isDone())+" retained="+TemporaryOutput.retained()+" "+s.state());}
 static void written(TemporaryOutput s)throws Exception{s.channel().write(ByteBuffer.wrap(new byte[]{1,2,3,4}));s.channel().close();}
 static void one(String phase,String shape,String delivery)throws Exception{
  Host h=new Host(phase,shape,delivery);TemporaryOutput s=new TemporaryOutput(h,false,WORKER,80);ByteBuffer caller=ByteBuffer.wrap(new byte[]{1,2,3,4});
  try{
   if(!phase.equals("WRITE"))written(s);if(List.of("REOPEN","VALIDATE","READY","COMMIT").contains(phase))s.finishWriter();if(List.of("READY","COMMIT").contains(phase))s.verifyAndValidate(h.controlledValidator(true,"HOST_ISOLATED_FORMAT_V1"));if(phase.equals("COMMIT"))s.markReady();
   stable(()->{switch(phase){case "WRITE":s.channel().write(caller);break;case "FLUSH":case "CLOSE":s.finishWriter();break;case "REOPEN":s.verifyAndValidate(h.controlledValidator(true,"HOST_ISOLATED_FORMAT_V1"));break;case "VALIDATE":s.verifyAndValidate(h.validator());break;case "READY":s.markReady();break;case "COMMIT":s.commitByExplicitHost(h.commit());break;default:s.abort();}});
   if(h.actual!=null){need(!s.returned()&&TemporaryOutput.retained()==1,"bad/late ACK not original physical return");h.actual.ackNow();stable(s::observeOriginal);need(!s.returned(),"same original tail held");note(phase,shape,delivery,"ORIGINAL_TAIL",s,h.actual);h.actual.joinSame();}
   for(int n=0;n<3;n++)s.observeOriginal();String first=s.firstFailure();need(first!=null,"bad original value or missing terminal proof retained failure "+phase+"/"+shape);
   if(phase.equals("WRITE"))need(h.physical==4&&s.acknowledgedBytesLowerBound()==0&&caller.position()==0&&s.writeAmountUnknown()&&s.unknownWriteReservation()==4,"invalid write ACK is not actual0/valid count; UNKNOWN once");
   if(phase.equals("COMMIT")){need(!s.committed()&&!s.returned()&&!s.abort(),"malformed COMMIT ACK holds UNKNOWN even original returned");rejected(s::finishOriginalCallbacks,"OUTPUT_ORIGINAL_PENDING");h.commitFact=HostOutput.CommitOutcome.CONFIRMED_COMMITTED;}
   if(phase.equals("QUERY")){need(!s.readyAcknowledged()&&!s.returned()&&!s.abort(),"bad QUERY cannot fake terminal or retry");rejected(s::finishOriginalCallbacks,"OUTPUT_ORIGINAL_PENDING");need(h.queries==1&&h.aborts==1,"original QUERY/ABORT once");}
   note(phase,shape,delivery,"BAD_RESULT_OR_UNKNOWN_HELD",s,h.actual);h.trusted=true;
   for(int n=0;n<4&&!s.returned();n++){s.observeOriginal();if(s.readyAcknowledged()||s.committed())stable(s::finishOriginalCallbacks);else stable(()->s.abort());}
   need(s.returned()&&h.targetCalls==1&&first.equals(s.firstFailure()),"accurate same-original authority cleanup, no RPC retries or history clearing");if(phase.equals("QUERY"))need(h.queries==1,"no replacement query");
   note(phase,shape,delivery,"EXACT_ORIGINAL_RETURNED_AND_TERMINAL_PROVEN",s,h.actual);cases++;System.out.println("PASS result "+phase+" "+shape+" "+delivery);
  }finally{for(Job j:originals)j.joinSame();h.trusted=true;h.commitFact=HostOutput.CommitOutcome.CONFIRMED_COMMITTED;if(!s.returned()){s.observeOriginal();if(s.readyAcknowledged())stable(s::finishOriginalCallbacks);else stable(()->s.abort());}need(s.returned(),"test failure cannot abandon exact owner");}
 }
 static void authority(String shape)throws Exception{
  class H extends MemSink {int queries;boolean truthful;public CompletionStage<SinkCoordinator.Status> query(String id){queries++;return CompletableFuture.completedFuture(null);}public SinkCoordinator.Status originalTerminalStatus(String id){need(id.equals(task),"exact original authority task");if(truthful)return new SinkCoordinator.Status(SinkCoordinator.HostState.ABORTED,null);if(shape.equals("NULL"))return null;if(shape.equals("THROW"))throw new IllegalStateException("private-authority");return status(shape);}}
  H h=new H();TemporaryOutput s=output(h);try{written(s);need(!s.abort(),"bad original query held");String first=s.firstFailure();for(int n=0;n<3;n++)stable(()->s.abort());need(!s.returned()&&!s.readyAcknowledged()&&h.queries==1&&h.aborts==1,"bad/nonterminal authority never creates terminal or RPC");note("TERMINAL_AUTHORITY",shape,"READ_ONLY","UNKNOWN_HELD",s,null);h.truthful=true;need(s.abort()&&s.returned()&&first.equals(s.firstFailure()),"accurate original authority resolves, history sticky");cases++;System.out.println("PASS result TERMINAL_AUTHORITY "+shape);}finally{h.truthful=true;need(s.returned()||s.abort(),"authority cleanup");}
 }
 static void immutableTask()throws Exception{
  Host h=new Host("NONE","NONE","IMMEDIATE");TemporaryOutput s=output(h);try{h.granted="different_task";written(s);s.finishWriter();s.verifyAndValidate(h.validator());s.markReady();s.commitByExplicitHost(h.commit());s.finishOriginalCallbacks();need(s.returned()&&s.committed()&&s.firstFailure()==null,"all actions bind the single original granted task snapshot");cases++;System.out.println("PASS result ORIGINAL_TASK_SNAPSHOT");}finally{if(!s.returned())s.abort();}
 }
 public static void main(String[] args)throws Exception{
  System.out.println("ORIGIN="+TemporaryOutput.class.getProtectionDomain().getCodeSource().getLocation());
  Map<String,List<String>> table=new LinkedHashMap<>();table.put("WRITE",List.of("NULL","ZERO","NEGATIVE","TOO_LARGE","OVERFLOW","LONG_ACK","NULL_STAGE"));table.put("FLUSH",List.of("VOID_VALUE","WRONG_TYPE","NULL_STAGE"));table.put("CLOSE",List.of("VOID_VALUE","WRONG_TYPE","NULL_STAGE"));table.put("REOPEN",List.of("NULL","WRONG_TYPE","NULL_STAGE","NULL_HANDLE","NEG_LENGTH","LONG_LENGTH","WRONG_LENGTH","WRONG_DIGEST","BAD_READ_COUNT"));table.put("VALIDATE",List.of("NULL","WRONG_TYPE","NULL_STAGE","WRONG_TASK","WRONG_SHA","WRONG_KIND","NEG_BYTES","LONG_BYTES","WRONG_BYTES","FALSE_VALID"));table.put("READY",List.of("NULL","EMPTY","BLANK","CONTROL","WRONG_TYPE","NULL_STAGE"));table.put("COMMIT",List.of("VOID_VALUE","WRONG_TYPE","NULL_STAGE"));table.put("ABORT",List.of("VOID_VALUE","WRONG_TYPE","NULL_STAGE"));table.put("QUERY",List.of("NULL","WRONG_TYPE","NULL_STAGE","STATE_NULL","READY_NULL","READY_EMPTY","READY_BLANK","READY_CONTROL","ABORTED_TOKEN","WRITING_TOKEN","UNKNOWN_TOKEN","WRITING","UNKNOWN"));
  for(Map.Entry<String,List<String>> row:table.entrySet())for(String shape:row.getValue())one(row.getKey(),shape,"IMMEDIATE");
  for(String delivery:List.of("TAIL","LATE"))for(String phase:List.of("WRITE","FLUSH","CLOSE","REOPEN","VALIDATE","READY","COMMIT","ABORT","QUERY"))one(phase,phase.equals("WRITE")?"ZERO":phase.equals("FLUSH")||phase.equals("CLOSE")||phase.equals("COMMIT")||phase.equals("ABORT")?"VOID_VALUE":"NULL",delivery);
  for(String shape:List.of("NULL","THROW","STATE_NULL","READY_NULL","READY_EMPTY","READY_BLANK","READY_CONTROL","ABORTED_TOKEN","WRITING_TOKEN","UNKNOWN_TOKEN","WRITING","UNKNOWN"))authority(shape);
  immutableTask();need(TemporaryOutput.retained()==0&&HostInputFactory.admittedSources()==0&&E13SourceGroup.canFinish(),"all exact original resources returned");System.out.println("DONE hostResultCases="+cases+" originalThreadsJoined=true sourceKeepers=0 outputKeepers=0 platform=NOT_RUN");
 }
}
