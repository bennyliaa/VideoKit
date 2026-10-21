package com.videokit.d1input;
import com.videokit.spike.c14.*;import java.util.concurrent.*;import static com.videokit.d1input.InputSinkCheck.*;
/** Original tester B06/B07 inputs; source facts/late stage identity retained, safe assertions. */
public final class OriginalResponseRegression {
 static void one(boolean normal)throws Exception{
  class Host extends MemSink {final CompletableFuture<String> response=new CompletableFuture<>();int queries;boolean truthful;public CompletionStage<String> markReady(String id){if(normal)super.markReady(id);else readies++;return response;}public CompletionStage<SinkCoordinator.Status> query(String id){queries++;return super.query(id);}public SinkCoordinator.Status originalTerminalStatus(String id){need(id.equals(task),"same exact original authority");return truthful?new SinkCoordinator.Status(status,status==SinkCoordinator.HostState.READY?"controlled_ready_token":null):new SinkCoordinator.Status(SinkCoordinator.HostState.UNKNOWN,null);}}
  Host h=new Host();TemporaryOutput s=new TemporaryOutput(h,false,WORKER,80);
  try{IndependentFixCheck.finishAndValidate(s,h);rejected(s::markReady,"OUTPUT_READY_UNKNOWN");need(h.originalOperationsReturned()&&!h.response.isDone(),"physical original method returned, retained original ACK pending");need(!s.abort(),"pending original response retains owner");rejected(s::finishOriginalCallbacks,"OUTPUT_ORIGINAL_PENDING");need(!s.returned()&&TemporaryOutput.retained()==1&&s.state().contains("pending=true")&&h.aborts==1&&h.queries==1,"complete response/callback eligibility, stable pending, no reissue");
   h.response.complete(normal?"controlled_ready_token":"contradictory_late_ready_token");await(s::originalReadyResponseReceived);
   if(normal){need(s.readyAcknowledged()&&!s.state().contains("abortedAck=true")&&s.originalReadyResponseAccepted(),"valid same original ACK agrees with QUERY");s.finishOriginalCallbacks();}
   else{need(!s.readyAcknowledged()&&s.state().contains("abortedAck=true")&&!s.originalReadyResponseAccepted()&&s.originalReadyResponseRejection().equals("CONFLICT_WITH_ABORTED"),"raw response received, contradictory READY not adopted");rejected(s::finishOriginalCallbacks,"OUTPUT_ORIGINAL_PENDING");h.truthful=true;s.finishOriginalCallbacks();}
   need(s.returned()&&s.firstFailure().equals("OUTPUT_READY_UNKNOWN")&&h.readies==1&&h.aborts==1&&h.queries==1&&TemporaryOutput.retained()==0,"same original callback/thread joined, no fake rollback/RPC/first-error reset");System.out.println("PASS original_response "+(normal?"B07_QUERY_READY_THEN_SAME_ACK":"B06_ABORTED_THEN_REJECTED_ACK")+" "+s.state());
  }finally{h.response.complete(normal?"controlled_ready_token":"contradictory_late_ready_token");h.truthful=true;if(!s.returned())s.finishOriginalCallbacks();need(s.returned(),"actual original cleanup");}
 }
 public static void main(String[] args)throws Exception{System.out.println("ORIGIN="+TemporaryOutput.class.getProtectionDomain().getCodeSource().getLocation());one(false);one(true);System.out.println("DONE originalResponseRegressions=2 sourceKeepers=0 outputKeepers=0 sameOriginalCallbacksJoined=true");}
}
