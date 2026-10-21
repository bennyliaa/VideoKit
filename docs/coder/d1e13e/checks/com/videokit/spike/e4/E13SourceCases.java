package com.videokit.spike.e4;
import com.videokit.spike.c14.*;
import java.io.IOException;
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;

/** The same finite source scenarios run on JVM and Android against production bridge/tickets.
 * Controlled futures belong only to this non-media fixture; completing one returns its original work.
 */
public final class E13SourceCases {
    public interface Evidence {void record(String value);}
    private static void need(boolean v,String why){if(!v)throw new AssertionError(why);}
    private static <T>T get(Future<T> f)throws Exception{return f.get(5000,TimeUnit.MILLISECONDS);}
    private static void rejected(Throwing call)throws Exception {try{call.run();throw new AssertionError("expected rejection");}catch(IOException expected){}}
    private interface Throwing {void run()throws Exception;}
    private static void cancelled(Future<?> f)throws Exception {try{get(f);throw new AssertionError("expected cancellation");}catch(ExecutionException e){need(e.getCause() instanceof IOException,"original error");}}
    private static E13SourceGroup.Identity id(int uid,int pid){return new E13SourceGroup.Identity(uid,pid,UUID.randomUUID().toString(),17,UUID.randomUUID().toString());}
    private static final class Fixture implements AsyncReadBridge.Provider {
        final byte[] bytes=new byte[4096];final AtomicInteger opens=new AtomicInteger(),reads=new AtomicInteger(),readBytes=new AtomicInteger(),closes=new AtomicInteger();
        final CountDownLatch openEntered=new CountDownLatch(1),readEntered=new CountDownLatch(1),closeEntered=new CountDownLatch(1);
        final CompletableFuture<AsyncReadBridge.Handle> lateOpen=new CompletableFuture<>();
        final CompletableFuture<Integer> lateRead=new CompletableFuture<>();
        volatile boolean delayOpen,delayRead,failFirstClose;volatile byte[] delayedBuffer;volatile int delayedOffset,delayedLength;
        final List<Handle> handles=new ArrayList<>();
        final int maxOpens,maxBytes,maxCloses;
        Fixture(String method){maxOpens=method.equals("twoConsumersHoldSourceUntilLastReturn")?2:1;maxCloses=method.equals("twoConsumersHoldSourceUntilLastReturn")||method.equals("lateReadAndCloseFailureDoNotReleaseEarly")?2:1;maxBytes=method.equals("authorizedHostSourceReadAndClose")?4096:method.equals("oldGenerationNeverOpensSource")?32:method.equals("cancelLateOpenRetainsOriginalOwner")?0:48;for(int i=0;i<bytes.length;i++)bytes[i]=(byte)(i*31+7);}
        public CompletionStage<AsyncReadBridge.Handle> open(AsyncReadBridge.Cancellation c){
            need(opens.incrementAndGet()<=maxOpens,"per-case open budget");Handle h=new Handle();synchronized(handles){handles.add(h);}openEntered.countDown();
            return delayOpen?lateOpen:CompletableFuture.completedFuture(h);
        }
        final class Handle implements AsyncReadBridge.Handle {
            int attempts;boolean closed;
            public Long length(){return 4096L;}
            public synchronized CompletionStage<Integer> readAt(long at,byte[] b,int off,int n,AsyncReadBridge.Cancellation c){
                need(!closed && at>=0 && at+n<=4096,"fixture valid original read");reads.incrementAndGet();need(readBytes.addAndGet(n)<=maxBytes,"per-case payload budget");
                if(delayRead){delayedBuffer=b;delayedOffset=off;delayedLength=n;readEntered.countDown();return lateRead;}
                System.arraycopy(bytes,(int)at,b,off,n);return CompletableFuture.completedFuture(n);
            }
            public synchronized CompletionStage<Void> closeAsync(){
                need(++attempts<=3,"original ticket attempt cap");need(closes.incrementAndGet()<=maxCloses,"per-case close cap");closeEntered.countDown();
                if(failFirstClose && attempts==1){CompletableFuture<Void> f=new CompletableFuture<>();f.completeExceptionally(new IOException("FIXTURE_RETURNED_CLOSE_FAILURE"));return f;}
                closed=true;return CompletableFuture.completedFuture(null);
            }
        }
        void returnOpen(){synchronized(handles){if(!handles.isEmpty())lateOpen.complete(handles.get(0));}}
        void returnRead(){byte[] b=delayedBuffer;if(b!=null){System.arraycopy(bytes,0,b,delayedOffset,delayedLength);lateRead.complete(delayedLength);}}
        void evidence(Evidence e,String method){e.record("E13_SOURCE method="+method+" prepared_nonmedia=4096 opens="+opens+" reads="+reads+" payload_bytes="+readBytes+" close_attempts="+closes+" retained="+E13SourceGroup.retained());}
    }
    private static void allReturned(E13SourceGroup g)throws Exception {g.closeAll();need(g.awaitReturn(5000),"actual original group/runtime/callers returned");need(g.snapshot().released(),"aggregate source released");need(E13SourceGroup.canFinish(),"runner source lifetime");}
    public static void run(String method,int uid,int pid,Evidence e)throws Exception {
        Fixture f=new Fixture(method);E13SourceGroup.Identity current=id(uid,pid);E13SourceGroup g=new E13SourceGroup(current);
        long began=System.nanoTime();e.record("E13_SOURCE_ORIGINAL task="+current.task+" epoch="+current.epoch+" instance="+current.instance+" generation="+g.snapshot().generation+" beganNs="+began+" bridgeAwaitTimeoutMs=5000");
        try {
            switch(method){
            case "authorizedHostSourceReadAndClose":{
                E13SourceGroup.Consumer c=g.consumer(current,f);need(c.open(current)==4096,"real production open");byte[] bytes=new byte[4096];need(c.read(current,bytes)==4096 && Arrays.equals(bytes,f.bytes),"actual authorized payload");c.close();allReturned(g);break;
            }
            case "oldGenerationNeverOpensSource":{
                E13SourceGroup.Consumer c=g.consumer(current,f);c.open(current);byte[] good=new byte[32];need(c.read(current,good)==32 && good[0]==7,"same production gate positive read");int before=f.opens.get(),reads=f.reads.get();
                for(E13SourceGroup.Identity old:List.of(new E13SourceGroup.Identity(uid,pid,"old-task",current.epoch,current.instance),new E13SourceGroup.Identity(uid,pid,current.task,current.epoch-1,current.instance),new E13SourceGroup.Identity(uid,pid,current.task,current.epoch,"old-instance"))){
                    rejected(()->g.consumer(old,f));rejected(()->c.read(old,new byte[1]));
                }
                need(f.opens.get()==before && f.reads.get()==reads,"old identities no open/read delta");e.record("E13_CURRENT_POSITIVE opens=1 reads=1 old_task_epoch_instance_delta_opens=0 delta_reads=0");c.close();allReturned(g);break;
            }
            case "twoConsumersHoldSourceUntilLastReturn":{
                E13SourceGroup.Consumer a=g.consumer(current,f),b=g.consumer(current,f);a.open(current);b.open(current);need(a.read(current,new byte[16])==16,"first consumer real read");a.close();
                need(!g.snapshot().retired && g.snapshot().consumers==1 && !g.snapshot().released(),"first consumer cannot retire shared generation");need(b.read(current,new byte[32])==32,"second remains active after first close");b.close();allReturned(g);break;
            }
            case "cancelLateOpenRetainsOriginalOwner":{
                f.delayOpen=true;E13SourceGroup.Consumer c=g.consumer(current,f);Future<Long> open=g.submit(()->c.open(current));need(f.openEntered.await(5000,TimeUnit.MILLISECONDS),"original provider entered");long cancelAt=System.nanoTime();c.close();cancelled(open);long responseAt=System.nanoTime();
                need(g.snapshot().operations>0 && !g.snapshot().released() && !E13SourceGroup.canFinish(),"late original open retained through runner gate");e.record("E13_PENDING_ORIGINAL_OPEN retained=true source_released=false runner_can_finish=false"+E13SourceGroup.pendingSummary());f.returnOpen();allReturned(g);e.record("E13_OPEN_CANCEL_TIMES cancelAtNs="+cancelAt+" responseAtNs="+responseAt+" allOriginalsReturnedAtNs="+System.nanoTime());need(f.closes.get()==1,"late original handle actual close once");break;
            }
            case "lateReadAndCloseFailureDoNotReleaseEarly":{
                E13SourceGroup.Consumer c=g.consumer(current,f);c.open(current);need(c.read(current,new byte[16])==16,"normal read before late read");f.delayRead=true;f.failFirstClose=true;byte[] out=new byte[32];Arrays.fill(out,(byte)85);
                Future<Integer> read=g.submit(()->c.read(current,out));need(f.readEntered.await(5000,TimeUnit.MILLISECONDS),"original read entered");long cancelAt=System.nanoTime();c.close();cancelled(read);long responseAt=System.nanoTime();need(f.closeEntered.await(5000,TimeUnit.MILLISECONDS),"original close entered");
                long end=System.nanoTime()+TimeUnit.SECONDS.toNanos(5);while(c.closeState()!=AsyncReadBridge.CloseState.FAILED && System.nanoTime()<end)Thread.sleep(2);
                need(c.closeState()==AsyncReadBridge.CloseState.FAILED && g.snapshot().closeFailed,"actual returned failure ticket");need(!g.snapshot().released() && !E13SourceGroup.canFinish(),"pending original read/failure retained");
                e.record("E13_PENDING_ORIGINAL_READ close_failed=true source_released=false runner_can_finish=false"+E13SourceGroup.pendingSummary());f.returnRead();need(Arrays.equals(out,new byte[]{85,85,85,85,85,85,85,85,85,85,85,85,85,85,85,85,85,85,85,85,85,85,85,85,85,85,85,85,85,85,85,85}),"late private-buffer result not published");
                get(c.retryFailedClose());allReturned(g);e.record("E13_READ_CANCEL_TIMES cancelAtNs="+cancelAt+" responseAtNs="+responseAt+" allOriginalsReturnedAtNs="+System.nanoTime());need(f.closes.get()==2,"one initial + one failed-close retry only");break;
            }
            default:throw new IOException("E13_EXACT_SOURCE_CASE_REQUIRED");
            }
            f.evidence(e,method);
        }finally{
            // Return only our controlled fixture's original operations, even on an assertion failure.
            // This is not cancellation/forced close of an unknown real provider.
            f.returnOpen();f.returnRead();g.closeAll();
            if(!g.awaitReturn(5000))e.record("E13_SOURCE_PENDING_ORIGINAL_OWNER_RETAINED"+E13SourceGroup.pendingSummary());
        }
    }
    public static void main(String[] args)throws Exception {run(args[0],10221,1234,System.out::println);System.out.println("PASS_PRODUCTION_SOURCE_SCENARIO "+args[0]);}
    private E13SourceCases(){}
}
