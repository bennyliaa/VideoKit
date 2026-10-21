package com.videokit.d1input;
import java.io.*;import java.util.concurrent.*;import static com.videokit.d1input.InputSinkCheck.*;
public final class AbortHistoryRegression {
 public static void main(String[] args)throws Exception{
  String phase=args[0];IndependentFixCheck.Host h=new IndependentFixCheck.Host(phase.equals("ABORT_ERROR")?"NONE":phase){public CompletionStage<Void> abort(String id){if(!phase.equals("ABORT_ERROR"))return super.abort(id);super.abort(id);return failed(new IOException("private-abort-failed-after-side-effect"));}};
  h.delay=!phase.equals("ABORT_ERROR");TemporaryOutput s=new TemporaryOutput(h,false,WORKER,80);
  try{IndependentFixCheck.written(s);boolean initial=s.abort();String first=s.firstFailure();need(first!=null&&!first.contains("private"),"already entered cleanup failure/timeout immediately sticky");
   if(h.actual!=null){h.actual.ackNow();need(!s.abort()&&!s.returned(),"same original tail retained");h.joinSame();}
   for(int n=0;n<4&&!s.returned();n++)s.abort();need(s.returned()&&h.aborts==1&&h.queries==1&&first.equals(s.firstFailure()),"real ABORTED and original return coexist with sticky error, no repeated RPC");
   System.out.println("ORIGIN="+TemporaryOutput.class.getProtectionDomain().getCodeSource().getLocation());System.out.println("PASS tester_history "+phase+" initial="+initial+" first="+first+" ABORT1 QUERY1 sameOriginalJoined=true "+s.state());
  }finally{for(IndependentFixCheck.Original<?> j:IndependentFixCheck.jobs)j.joinSame();need(s.returned()||s.abort(),"cleanup keeps originals");}
 }
}
