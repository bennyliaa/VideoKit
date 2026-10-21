package com.videokit.d1input;
import com.videokit.spike.c14.*;import com.videokit.spike.e4.E13SourceGroup;import java.io.*;import java.util.*;import java.util.concurrent.*;import java.util.function.*;import static com.videokit.d1input.InputSinkCheck.*;
/** Finite causal schedules. The same retained response CF is completed once; actual callback
 * tails are inside its real whenComplete observer, not a replacement proof thread/counter. */
public final class ResponseOrderCheck {
 static int cases;
 static final class Response extends CompletableFuture<String> {
  boolean gateObserver;volatile Thread callbackThread;final CountDownLatch entered=new CountDownLatch(1),leave=new CountDownLatch(1);
  public CompletableFuture<String> whenComplete(BiConsumer<? super String,? super Throwable> action){return super.whenComplete((v,e)->{callbackThread=Thread.currentThread();action.accept(v,e);entered.countDown();if(gateObserver)try{leave.await();}catch(InterruptedException x){Thread.currentThread().interrupt();throw new CompletionException(x);}});}
 }
 static class Host extends MemSink {
  final boolean applied;final Response readyResponse=new Response();final CompletableFuture<Void> abortResponse=new CompletableFuture<>();final CompletableFuture<SinkCoordinator.Status> queryResponse=new CompletableFuture<>();
  boolean holdAbort,holdQuery,allowFact,physicalTail;volatile boolean originalMethodReturned;volatile Thread delivery;final CountDownLatch deliveryTail=new CountDownLatch(1);int queries;SinkCoordinator.Status authorityOverride;
  Host(boolean applied){this.applied=applied;}
  public CompletionStage<String> markReady(String id){need(id.equals(task),"same original READY task");if(applied)super.markReady(id);else readies++;originalMethodReturned=true;return readyResponse;}
  public CompletionStage<Void> abort(String id){super.abort(id);if(!holdAbort)abortResponse.complete(null);return abortResponse;}
  SinkCoordinator.Status actualFact(){return new SinkCoordinator.Status(status,status==SinkCoordinator.HostState.READY?"controlled_ready_token":null);}
  public CompletionStage<SinkCoordinator.Status> query(String id){need(id.equals(task),"same original QUERY task");queries++;if(!holdQuery)queryResponse.complete(actualFact());return queryResponse;}
  public SinkCoordinator.Status originalTerminalStatus(String id){need(id.equals(task),"same original authority task");return allowFact?(authorityOverride==null?actualFact():authorityOverride):new SinkCoordinator.Status(SinkCoordinator.HostState.UNKNOWN,null);}
  public boolean originalOperationsReturned(){return !physicalTail||delivery==null||!delivery.isAlive();}public boolean writerOriginalsReturned(){return closed;}
  void completeReady(String kind){if(kind.equals("FAIL"))readyResponse.completeExceptionally(new IOException("private-response-failure"));else if(kind.equals("CANCEL"))readyResponse.completeExceptionally(new CancellationException("private-response-cancellation"));else readyResponse.complete(kind.equals("DIFFERENT")?"different_late_token":"controlled_ready_token");}
  void joinDelivery()throws Exception{deliveryTail.countDown();readyResponse.leave.countDown();if(delivery!=null){delivery.join(3000);need(!delivery.isAlive(),"same actual response delivery thread joined");}}
 }
 static TemporaryOutput start(Host h)throws Exception{TemporaryOutput s=new TemporaryOutput(h,false,WORKER,80);IndependentFixCheck.finishAndValidate(s,h);rejected(s::markReady,"OUTPUT_READY_UNKNOWN");need(h.originalMethodReturned&&h.readies==1,"method really returned original stage once");return s;}
 static void pending(TemporaryOutput s)throws Exception{rejected(s::finishOriginalCallbacks,"OUTPUT_ORIGINAL_PENDING");need(!s.returned()&&TemporaryOutput.retained()==1,"exact owner retained, no internal unchecked error");}
 static void observe(String key,TemporaryOutput s,Host h){System.out.println("OBSERVE order="+key+" originalReadyStage="+System.identityHashCode(h.readyResponse)+" originalAbortStage="+System.identityHashCode(h.abortResponse)+" originalQueryStage="+System.identityHashCode(h.queryResponse)+" originalMethodReturned="+h.originalMethodReturned+" originalReadyDone="+h.readyResponse.isDone()+" callbackThread="+(h.readyResponse.callbackThread==null?0:h.readyResponse.callbackThread.getId())+" callbackThreadAlive="+(h.readyResponse.callbackThread!=null&&h.readyResponse.callbackThread.isAlive())+" deliveryThread="+(h.delivery==null?0:h.delivery.getId())+" READY_RPC="+h.readies+" ABORT_RPC="+h.aborts+" QUERY_RPC="+h.queries+" actualHost="+h.status+" retained="+TemporaryOutput.retained()+" "+s.state());}
 static void awaitFinish(TemporaryOutput s)throws Exception{long end=System.nanoTime()+TimeUnit.SECONDS.toNanos(3);while(!s.returned()){try{s.finishOriginalCallbacks();}catch(IOException pending){need(pending.getMessage().equals("OUTPUT_ORIGINAL_PENDING")&&pending.getCause()==null,"only stable original pending while exact worker returns");}if(s.returned())break;need(System.nanoTime()<end,"released gate must allow same original callback/thread to return");Thread.sleep(1);}}
 static void finish(String name,TemporaryOutput s,Host h,int aborts,int queries)throws Exception{h.readyResponse.leave.countDown();h.joinDelivery();h.allowFact=true;h.authorityOverride=null;h.abortResponse.complete(null);h.queryResponse.complete(h.actualFact());awaitFinish(s);need(s.returned()&&s.firstFailure().equals("OUTPUT_READY_UNKNOWN")&&h.readies==1&&h.aborts==aborts&&h.queries==queries,"accurate same original facts, sticky first failure, no RPC replacement");need(!(s.readyAcknowledged()&&s.state().contains("abortedAck=true")),"never publish contradictory terminal pair");observe(name+"_RETURNED",s,h);cases++;System.out.println("PASS order "+name);}
 static void cleanup(TemporaryOutput s,Host h)throws Exception{h.readyResponse.leave.countDown();h.joinDelivery();h.completeReady("SUCCESS");h.abortResponse.complete(null);h.queryResponse.complete(h.actualFact());h.allowFact=true;h.authorityOverride=null;awaitFinish(s);need(s.returned(),"exception-path exact original cleanup, never JVM exit as release");}
 static void queryFirst(boolean applied,String ack)throws Exception{
  Host h=new Host(applied);TemporaryOutput s=start(h);try{need(!s.abort(),"same original READY response pending");need(s.readyAcknowledged()==applied&&s.state().contains("abortedAck="+!applied),"QUERY accurate terminal adopted");pending(s);observe("QUERY_FIRST_"+applied+"_"+ack+"_PENDING",s,h);h.completeReady(ack);await(s::originalReadyResponseReceived);
   boolean conflict=ack.equals("DIFFERENT")||!applied&&ack.equals("SUCCESS");if(conflict){need(!s.originalReadyResponseAccepted()&&s.originalReadyResponseRejection().equals(applied?"TOKEN_CHANGED":"CONFLICT_WITH_ABORTED")&&s.readyAcknowledged()==applied,"raw successful response retained but conflict rejected");pending(s);}else need(s.originalReadyResponseAccepted()==ack.equals("SUCCESS"),"response fact vs adoption distinct");
   observe("QUERY_FIRST_"+applied+"_"+ack+"_ACK",s,h);finish("QUERY_FIRST_"+applied+"_"+ack,s,h,1,1);
  }finally{cleanup(s,h);}
 }
 static void ackBeforeQuery(String reported)throws Exception{
  Host h=new Host(true);h.holdQuery=true;TemporaryOutput s=start(h);try{need(!s.abort()&&h.queries==1,"same QUERY stage still pending");h.completeReady("SUCCESS");need(s.readyAcknowledged()&&s.originalReadyResponseAccepted(),"accurate original READY ACK first");pending(s);h.queryResponse.complete(reported.equals("ACTUAL")?h.actualFact():reported.equals("WRONG_TOKEN")?new SinkCoordinator.Status(SinkCoordinator.HostState.READY,"wrong_query_token"):new SinkCoordinator.Status(SinkCoordinator.HostState.ABORTED,null));
   if(!reported.equals("ACTUAL")){need(s.readyAcknowledged()&&!s.state().contains("abortedAck=true"),"bad later QUERY cannot overwrite original accepted READY");pending(s);}observe("ACK_BEFORE_QUERY_"+reported,s,h);finish("ACK_BEFORE_QUERY_"+reported,s,h,1,1);
  }finally{cleanup(s,h);}
 }
 static void ackBeforeAbort(boolean applied,String ack)throws Exception{
  Host h=new Host(applied);h.holdAbort=true;TemporaryOutput s=start(h);try{need(!s.abort()&&h.aborts==1&&h.queries==0,"ABORT response pending, QUERY not yet entered");h.completeReady(ack);pending(s);h.abortResponse.complete(null);if(!applied)need(s.abort(),"after failure and same ABORT ACK, original QUERY proves ABORTED");observe("ACK_BEFORE_ABORT_"+applied+"_"+ack,s,h);finish("ACK_BEFORE_ABORT_"+applied+"_"+ack,s,h,1,applied?0:1);}finally{cleanup(s,h);}
 }
 static void authorityFirst(boolean applied,String ack)throws Exception{
  Host h=new Host(applied);h.holdAbort=!applied;TemporaryOutput s=start(h);try{if(!applied)need(!s.abort()&&h.queries==0,"actual ABORT entered, response still pending");h.allowFact=true;need(!s.abort()&&s.readyAcknowledged()==applied&&s.state().contains("abortedAck="+!applied),"accurate original arbitration authority first, still hold original response");h.allowFact=false;h.completeReady(ack);if(!applied)h.abortResponse.complete(null);boolean conflict=ack.equals("DIFFERENT")||!applied&&ack.equals("SUCCESS");if(conflict)pending(s);observe("AUTHORITY_FIRST_"+applied+"_"+ack,s,h);finish("AUTHORITY_FIRST_"+applied+"_"+ack,s,h,applied?0:1,0);}finally{cleanup(s,h);}
 }
 static void badAuthorityBeforeAck(boolean applied,String ack)throws Exception{
  Host h=new Host(applied);TemporaryOutput s=start(h);try{need(!s.abort(),"QUERY confirmed before original ACK");h.authorityOverride=new SinkCoordinator.Status(applied?SinkCoordinator.HostState.ABORTED:SinkCoordinator.HostState.READY,applied?null:"bad_authority_token");h.allowFact=true;need(!s.abort(),"bad readonly source cannot replace confirmed terminal");h.allowFact=false;h.completeReady(ack);pending(s);need(s.state().contains("terminalProtocolUnknown=true")&&s.readyAcknowledged()==applied,"matching ACK or failed ACK cannot erase earlier authority conflict");observe("BAD_AUTHORITY_BEFORE_ACK_"+applied+"_"+ack,s,h);finish("BAD_AUTHORITY_BEFORE_ACK_"+applied+"_"+ack,s,h,1,1);}finally{cleanup(s,h);}
 }
 static void tail(String kind,String ack)throws Exception{
  Host h=new Host(true);boolean worker=kind.equals("COORDINATOR_WORKER"),observer=kind.equals("ORIGINAL_OBSERVER");h.readyResponse.gateObserver=worker||observer;
  if(worker)h.completeReady(ack);TemporaryOutput s=start(h);
  try{
   if(!worker){need(!s.abort(),"QUERY READY first while original ACK pending");h.physicalTail=kind.equals("HOST_PHYSICAL");h.delivery=new Thread(()->{h.completeReady(ack);if(h.physicalTail)try{h.deliveryTail.await();}catch(InterruptedException e){Thread.currentThread().interrupt();}},"same-original-response-delivery");h.delivery.start();}
   else {h.allowFact=true;need(!s.abort(),"accurate authority READY while coordinator original registration tail still live");}
   need(h.readyResponse.entered.await(2,TimeUnit.SECONDS),"actual same original observer entered");if(!worker)await(s::originalReadyResponseReceived);pending(s);observe("TAIL_"+kind+"_"+ack,s,h);Thread actual=h.readyResponse.callbackThread;need(actual!=null&&actual.isAlive(),"same actual callback thread held");
   h.readyResponse.leave.countDown();h.joinDelivery();finish("TAIL_"+kind+"_"+ack,s,h,worker?0:1,worker?0:1);if(worker)need(!actual.isAlive(),"the exact original coordinator callback worker physically joined");
  }finally{cleanup(s,h);}
 }
 public static void main(String[] args)throws Exception{
  System.out.println("ORIGIN="+TemporaryOutput.class.getProtectionDomain().getCodeSource().getLocation());for(String ack:List.of("SUCCESS","FAIL","CANCEL"))queryFirst(false,ack);for(String ack:List.of("SUCCESS","DIFFERENT","FAIL","CANCEL"))queryFirst(true,ack);
  for(String q:List.of("ACTUAL","WRONG_TOKEN","ABORTED"))ackBeforeQuery(q);ackBeforeAbort(true,"SUCCESS");ackBeforeAbort(false,"FAIL");ackBeforeAbort(false,"CANCEL");
  for(String ack:List.of("SUCCESS","DIFFERENT","FAIL","CANCEL"))authorityFirst(true,ack);for(String ack:List.of("SUCCESS","FAIL","CANCEL"))authorityFirst(false,ack);
  for(String ack:List.of("SUCCESS","FAIL","CANCEL"))badAuthorityBeforeAck(true,ack);badAuthorityBeforeAck(false,"CANCEL");
  for(String k:List.of("ORIGINAL_OBSERVER","COORDINATOR_WORKER","HOST_PHYSICAL"))for(String ack:List.of("SUCCESS","CANCEL"))tail(k,ack);
  need(TemporaryOutput.retained()==0&&HostInputFactory.admittedSources()==0&&E13SourceGroup.canFinish(),"all actual original owners returned");System.out.println("DONE responseOrderCases="+cases+" allFiniteGatesReleased=true sameOriginalCallbacksAndThreadsJoined=true sourceKeepers=0 outputKeepers=0 platformAndRealPublication=NOT_RUN");
 }
}
