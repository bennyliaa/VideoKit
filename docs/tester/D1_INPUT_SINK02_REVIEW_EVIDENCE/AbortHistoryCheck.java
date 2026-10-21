package com.videokit.d1input;
import java.io.*;import java.util.concurrent.*;
import static com.videokit.d1input.InputSinkCheck.*;
public class AbortHistoryCheck {
 public static void main(String[] args)throws Exception{
  String phase=args[0];IndependentFixCheck.Host h=new IndependentFixCheck.Host(phase.equals("ABORT_ERROR")?"NONE":phase){
   public CompletionStage<Void> abort(String id){if(!phase.equals("ABORT_ERROR"))return super.abort(id);super.abort(id);return failed(new IOException("private-abort-failed-after-side-effect"));}
  };h.delay=!phase.equals("ABORT_ERROR");TemporaryOutput s=new TemporaryOutput(h,false,WORKER,80);
  try{
   IndependentFixCheck.written(s);boolean initial=s.abort();String first=s.firstFailure();
   System.out.println("INITIAL phase="+phase+" abortResult="+initial+" error="+first+" state="+s.state());
   if(h.actual!=null){h.actual.ackNow();need(!s.abort()&&!s.returned(),"early ACK still original tail");h.joinSame();}
   for(int i=0;i<3&&!s.returned();i++)s.abort();
   need(s.returned()&&h.aborts==1&&h.queries==1&&s.firstFailure()==null,"reproduce lost first failure after terminal reconciliation");
   System.out.println("ORIGIN="+TemporaryOutput.class.getProtectionDomain().getCodeSource().getLocation());
   System.out.println("REPRO ABORT_QUERY_FAILURE_HISTORY_LOST phase="+phase+" error="+s.firstFailure()+" ownerReturned="+s.returned()+" abortRPC="+h.aborts+" queryRPC="+h.queries+" originalThreadsJoined=true");
  }finally{for(IndependentFixCheck.Original<?> j:IndependentFixCheck.jobs)j.joinSame();}
 }
}
