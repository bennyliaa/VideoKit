package com.videokit.d1input;
import java.util.concurrent.*;import com.videokit.spike.c14.*;
import static com.videokit.d1input.InputSinkCheck.*;
public class QueryResultCheck {
 public static void main(String[] args)throws Exception{
  boolean empty=args[0].equals("EMPTY_READY");
  class Host extends MemSink {int queries;boolean authority;
   public CompletionStage<SinkCoordinator.Status> query(String id){queries++;return CompletableFuture.completedFuture(empty?new SinkCoordinator.Status(SinkCoordinator.HostState.READY,""):null);}
   public SinkCoordinator.Status originalTerminalStatus(String id){need(id.equals(task),"exact task");return authority?new SinkCoordinator.Status(status,null):new SinkCoordinator.Status(SinkCoordinator.HostState.UNKNOWN,null);}
  }
  Host h=new Host();TemporaryOutput s=output(h);String thrown="NONE";
  try{
   IndependentFixCheck.written(s);try{s.abort();}catch(Throwable t){thrown=t.getClass().getSimpleName()+":"+t.getMessage();}
   if(empty){need(s.readyAcknowledged()&&"".equals(s.readyAcknowledgementToken())&&s.firstFailure()==null,"empty READY incorrectly accepted");s.finishOriginalCallbacks();need(s.returned(),"invalid READY allows owner returned");}
   else need(thrown.startsWith("NullPointerException:")&&s.firstFailure()==null&&!s.returned(),"null query result raw exception without stable failure");
   System.out.println("ORIGIN="+TemporaryOutput.class.getProtectionDomain().getCodeSource().getLocation());System.out.println("REPRO QUERY_RESULT_NOT_VALIDATED mode="+args[0]+" thrown="+thrown+" queryRPC="+h.queries+" actualHostTerminal="+h.status+" "+s.state());
  }finally{h.authority=true;if(!s.returned())need(s.abort(),"cleanup using truthful original ABORTED authority");need(TemporaryOutput.retained()==0,"no abandoned keeper");}
 }
}
