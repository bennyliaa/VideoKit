package com.videokit.d1input;
import com.videokit.spike.c14.*;import java.io.*;import java.util.concurrent.*;
import static com.videokit.d1input.InputSinkCheck.*;
/** Original READY invocation returns its retained response stage; no host task/side effect is
 * claimed by that pending response. Original ABORT/QUERY then prove actual ABORTED. */
public class IndependentLateReadyCheck {
 public static void main(String[] args)throws Exception{
  boolean normal=args.length>0&&args[0].equals("NORMAL_QUERY_READY");
  class Host extends MemSink {
   final CompletableFuture<String> originalReadyResponse=new CompletableFuture<>();int queries;
   public CompletionStage<String> markReady(String id){if(normal)super.markReady(id);else readies++;return originalReadyResponse;}
   public CompletionStage<SinkCoordinator.Status> query(String id){queries++;return super.query(id);}
  }
  Host h=new Host();TemporaryOutput s=new TemporaryOutput(h,false,WORKER,80);String abortError="NONE";
  try{
   IndependentFixCheck.finishAndValidate(s,h);rejected(s::markReady,"OUTPUT_READY_UNKNOWN");
   need(h.originalOperationsReturned()&&!h.originalReadyResponse.isDone(),"original host call returned, same response stage still pending");
   try{s.abort();}catch(Throwable e){abortError=e.getClass().getSimpleName()+":"+e.getMessage();}
   if(normal)try{s.finishOriginalCallbacks();}catch(Throwable e){abortError=e.getClass().getSimpleName()+":"+e.getMessage();}
   need(h.aborts==1&&h.queries==1,"original ABORT/QUERY only once");
   if(normal)need(h.status==SinkCoordinator.HostState.READY&&s.readyAcknowledged()&&!s.state().contains("abortedAck=true")&&abortError.equals("IllegalStateException:ORIGINAL_SINK_CALLBACK_PENDING"),"normal original QUERY confirms READY but pending ACK throws raw coordinator error");
   else need(h.status==SinkCoordinator.HostState.ABORTED&&s.state().contains("abortedAck=true")&&!s.readyAcknowledged(),"actual original ABORT/QUERY fixed terminal ABORTED");
   System.out.println("BEFORE sameOriginalREADYResponsePending=true "+(normal?"finishError=":"abortError=")+abortError+" "+s.state());
   // Deliberately malformed late ACK: it contradicts the already-confirmed terminal.
   h.originalReadyResponse.complete(normal?"controlled_ready_token":"contradictory_late_ready_token");await(s::readyAcknowledged);s.finishOriginalCallbacks();
   if(normal)need(s.returned()&&!s.state().contains("abortedAck=true"),"same correct late ACK consumed and original callback returned");
   else need(s.readyAcknowledged()&&s.state().contains("abortedAck=true")&&s.returned()&&h.status==SinkCoordinator.HostState.ABORTED,"reproduce late READY overwrites terminal guard");
   System.out.println("ORIGIN="+TemporaryOutput.class.getProtectionDomain().getCodeSource().getLocation());
   System.out.println("REPRO "+(normal?"PENDING_ORIGINAL_READY_ACK_RAW_EXCEPTION":"LATE_READY_CONTRADICTS_CONFIRMED_ABORTED")+" actualHost="+h.status+" READY_RPC="+h.readies+" ABORT_RPC="+h.aborts+" QUERY_RPC="+h.queries+" "+s.state());
  }finally{h.originalReadyResponse.complete(normal?"controlled_ready_token":"cleanup_response");if(!s.returned())s.finishOriginalCallbacks();need(s.returned()&&TemporaryOutput.retained()==0,"same coordinator callbacks physically joined, no abandoned owner");}
 }
}
