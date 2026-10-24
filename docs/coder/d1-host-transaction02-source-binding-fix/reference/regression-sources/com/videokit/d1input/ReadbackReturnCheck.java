package com.videokit.d1input;
import com.videokit.spike.c14.*;import java.util.concurrent.*;
import static com.videokit.d1input.InputSinkCheck.*;
public class ReadbackReturnCheck {
 public static void main(String[] args)throws Exception{
  IndependentFixCheck.Original<?>[] closeJob={null};
  MemSink h=new MemSink(){int reopenCalls;
   public CompletionStage<AsyncReadBridge.Provider> reopenReadOnly(){reopenCalls++;byte[] b=bytes.toByteArray();return CompletableFuture.completedFuture(c->{AsyncReadBridge.Handle d=HostFixtures.memory(b);return CompletableFuture.completedFuture(new AsyncReadBridge.Handle(){
    public Long length(){return d.length();}
    public CompletionStage<Integer> readAt(long p,byte[] out,int o,int n,AsyncReadBridge.Cancellation cancel){return d.readAt(p,out,o,n,cancel);}
    public CompletionStage<Void> closeAsync(){IndependentFixCheck.Original<Void> j=new IndependentFixCheck.Original<>("READBACK_CLOSE",true,()->{d.closeAsync().toCompletableFuture().get();return null;});closeJob[0]=j;return j.ack;}
   });});}
  };TemporaryOutput s=output(h);
  try{
   IndependentFixCheck.written(s);s.finishWriter();rejected(()->s.verifyAndValidate(h.controlledValidator(true,"HOST_ISOLATED_FORMAT_V1")),"OUTPUT_REOPEN_FAILED");
   need(closeJob[0]!=null&&!closeJob[0].returned()&&!s.abort()&&!s.returned()&&TemporaryOutput.retained()==1&&HostInputFactory.admittedSources()==1,"same reopened registry and close retained");
   System.out.println("ORIGIN="+TemporaryOutput.class.getProtectionDomain().getCodeSource().getLocation());
   IndependentFixCheck.note("READBACK_originalCloseStillPending",s,closeJob[0]);closeJob[0].joinSame();
   long until=System.nanoTime()+TimeUnit.SECONDS.toNanos(2);while(!s.abort()&&System.nanoTime()<until)Thread.sleep(2);
   need(s.returned()&&TemporaryOutput.retained()==0&&HostInputFactory.admittedSources()==0&&s.firstFailure().equals("OUTPUT_REOPEN_FAILED")&&h.readies==0,"original read registry and workers returned, no validation/READY retry");
   System.out.println("PASS reopened_original_registry_close_and_workers_retained_until_same_original_return firstFailurePreserved=true sourceKeepers0 outputKeepers0");
  }finally{for(IndependentFixCheck.Original<?> j:IndependentFixCheck.jobs)j.joinSame();}
 }
}
