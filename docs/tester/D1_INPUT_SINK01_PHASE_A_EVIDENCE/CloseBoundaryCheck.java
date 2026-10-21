package review;
import com.videokit.spike.c14.*;import java.io.*;import java.util.concurrent.*;import java.util.concurrent.atomic.*;
public final class CloseBoundaryCheck {
 public static void main(String[] args)throws Exception {
  AtomicInteger closeCalls=new AtomicInteger();
  AsyncReadBridge.Provider source=t->CompletableFuture.completedFuture(new AsyncReadBridge.Handle(){
   public Long length(){return null;}
   public CompletionStage<Integer> readAt(long p,byte[] b,int o,int n,AsyncReadBridge.Cancellation c){return CompletableFuture.completedFuture(-1);}
   public CompletionStage<Void> closeAsync(){if(closeCalls.incrementAndGet()==1){CompletableFuture<Void> f=new CompletableFuture<>();f.completeExceptionally(new IOException("CONTROLLED_KNOWN_CLOSE_FAILURE"));return f;}return CompletableFuture.completedFuture(null);}
  });
  AsyncReadBridge.Runtime rt=new AsyncReadBridge.Runtime();LeaseRegistry lr=new LeaseRegistry();long gen=lr.create();AsyncReadBridge bridge=new AsyncReadBridge(rt,source,lr,gen,1000);
  bridge.open(0,-1);BaselineCheck.rejects(()->bridge.open(0,-1),"SOURCE_ALREADY_OPEN");BaselineCheck.rejects(()->bridge.seekAbsolute(1),"CPU_SEEK_UNSUPPORTED");bridge.close();lr.retire(gen);
  long stop=System.nanoTime()+1000000000L;while(bridge.closeState()!=AsyncReadBridge.CloseState.FAILED&&System.nanoTime()<stop)Thread.sleep(1);
  BaselineCheck.need(bridge.closeState()==AsyncReadBridge.CloseState.FAILED&&lr.query(gen).closeFailed&&!lr.query(gen).released()&&closeCalls.get()==1,"failed original close retained, no automatic retry");
  BaselineCheck.rejects(()->bridge.open(0,-1),"SESSION_RELEASED");
  // The original API explicitly permits an owner retry of an observed FAILED callback, not a hung/UNKNOWN native close.
  bridge.retryFailedClose().get(1,TimeUnit.SECONDS);BaselineCheck.need(lr.awaitReleased(gen,1000),"same handle recovery must actually finish");rt.awaitOriginalTermination(lr,gen);BaselineCheck.need(rt.finishReturned(lr,gen)&&closeCalls.get()==2,"same original threads returned");
  System.out.println("PASS failed_source_close_not_released_no_auto_retry_or_reopen; explicit_API_owner_recovery_only_after_observed_callback_failure");
 }
}
