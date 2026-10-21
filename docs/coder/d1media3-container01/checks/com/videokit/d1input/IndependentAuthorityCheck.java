package com.videokit.d1input;
import java.io.*;import java.util.*;import java.util.concurrent.*;import com.videokit.spike.c14.*;
import static com.videokit.d1input.InputSinkCheck.*;
public class IndependentAuthorityCheck {
 static class Publication implements HostOutput.Commit {
  final boolean apply;String task,token;boolean durable;int rpc,reads;HostOutput.CommitOutcome fact=HostOutput.CommitOutcome.UNKNOWN;IndependentFixCheck.Original<Void> query;
  Publication(boolean a){apply=a;}
  public CompletionStage<Void> commit(String id,String t){rpc++;task=id;token=t;durable=apply;return failed(new CancellationException("private-publish-ACK"));}
  public boolean originalOperationsReturned(){return query==null||query.returned();}
  public HostOutput.CommitOutcome originalOutcome(String id,String t){need(Objects.equals(task,id)&&Objects.equals(token,t),"exact original task/token");reads++;return fact;}
  void originalQuery(){query=new IndependentFixCheck.Original<>("COMMIT_SAME_HOST_QUERY",false,()->{fact=durable?HostOutput.CommitOutcome.CONFIRMED_COMMITTED:HostOutput.CommitOutcome.CONFIRMED_NOT_APPLIED;return null;});}
 }
 static void publication(boolean applied)throws Exception{
  MemSink h=new MemSink();TemporaryOutput s=output(h);Publication p=new Publication(applied);
  try{
   IndependentFixCheck.finishAndValidate(s,h);s.markReady();rejected(()->s.commitByExplicitHost(p),"OUTPUT_COMMIT_UNKNOWN");
   for(int i=0;i<3;i++)s.observeOriginal();need(!s.committed()&&!s.returned()&&TemporaryOutput.retained()==1&&p.rpc==1,"UNKNOWN must retain, no commit retry");rejected(s::finishOriginalCallbacks,"OUTPUT_ORIGINAL_PENDING");
   p.originalQuery();p.query.ackNow();int accesses=p.reads;s.observeOriginal();need(p.reads==accesses&&!s.returned(),"no authority acceptance across exact original query tail");p.query.joinSame();s.observeOriginal();
   need(s.committed()==applied&&s.state().contains("commitAcknowledged=false")&&s.firstFailure().equals("OUTPUT_COMMIT_UNKNOWN"),"business fact distinct from ACK and earlier error");s.finishOriginalCallbacks();
   need(s.returned()&&s.readyAcknowledged()&&!s.state().contains("abortedAck=true")&&p.rpc==1,"NOT_APPLIED never SDK rollback/ABORTED");
   System.out.println("PASS original_commit_authority applied="+applied+" exactTaskToken=true originalRPC1 querySameThreadJoined=true "+s.state());
  }finally{if(p.query!=null)p.query.joinSame();}
 }
 static void terminal()throws Exception{
  class Host extends MemSink {
   IndependentFixCheck.Original<SinkCoordinator.Status> query;SinkCoordinator.Status retained;boolean allowFact;int queryRPC,proofReads;
   public CompletionStage<SinkCoordinator.Status> query(String id){queryRPC++;query=new IndependentFixCheck.Original<>("EXACT_ORIGINAL_QUERY",false,()->{retained=super.query(id).toCompletableFuture().get();throw new IOException("private-query-ACK");});return query.ack;}
   public boolean originalOperationsReturned(){return query==null||query.returned();}public boolean writerOriginalsReturned(){return closed;}
   public SinkCoordinator.Status originalTerminalStatus(String id){need(id.equals(task),"exact original terminal task");proofReads++;return allowFact?retained:new SinkCoordinator.Status(SinkCoordinator.HostState.UNKNOWN,null);}
  }
  Host h=new Host();TemporaryOutput s=output(h);try{
   IndependentFixCheck.written(s);need(!s.abort()&&!s.returned(),"query original tail retained");h.query.ackNow();int reads=h.proofReads;need(!s.abort()&&h.proofReads==reads,"no acceptance during original query tail");h.query.joinSame();
   need(!s.abort()&&!s.returned()&&h.queryRPC==1&&h.aborts==1,"default UNKNOWN no retry/refund");h.allowFact=true;need(s.abort()&&s.returned()&&s.firstFailure().equals("OUTPUT_ABORT_UNKNOWN"),"accurate original ABORTED plus sticky failure");
   need(h.queryRPC==1&&h.aborts==1,"authority read not new RPC");System.out.println("PASS original_terminal_authority defaultUNKNOWN_held=true sameOriginalQueryJoined=true exactTask=true ABORT1QUERY1 "+s.state());
  }finally{if(h.query!=null)h.query.joinSame();}
 }
 public static void main(String[] args)throws Exception{System.out.println("ORIGIN="+TemporaryOutput.class.getProtectionDomain().getCodeSource().getLocation());publication(false);publication(true);terminal();need(TemporaryOutput.retained()==0&&HostInputFactory.admittedSources()==0,"all original owners actually returned");System.out.println("DONE independentAuthorityScenarios=3 owners0 originalThreadsJoined=true");}
}
