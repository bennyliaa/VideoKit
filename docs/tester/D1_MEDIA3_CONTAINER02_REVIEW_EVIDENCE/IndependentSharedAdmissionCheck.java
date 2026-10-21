package com.videokit.d1input;
import com.videokit.spike.c14.*;
import java.io.*;import java.nio.*;import java.util.concurrent.*;import java.util.concurrent.atomic.*;
import static com.videokit.d1input.InputSinkCheck.*;

/** Independent tester cases. Controlled host boundaries only; actual product, input and Media3 retained. */
public final class IndependentSharedAdmissionCheck {
 enum Entry { STRUCTURE, VERIFY }
 enum Order { ACK_THREAD_TAIL, WORKER_BEFORE_ACK, OBSERVER_AFTER_WORKER }
 static int passed;
 static final class Reject implements HostOutput.Validator {
  int calls;public CompletionStage<HostOutput.Validation> validate(String t,long n,String hash){calls++;return CompletableFuture.completedFuture(new HostOutput.Validation(t,n,hash,HostMp4Inspection.KIND,false));}
  public boolean originalOperationsReturned(){return true;}
 }
 static class Host extends MemSink {
  final Order order;final CountDownLatch responseGate=new CountDownLatch(1),threadTail=new CountDownLatch(1),observerGate=new CountDownLatch(1),observerEntered=new CountDownLatch(1);
  volatile Thread actualWorker,actualObserverThread;volatile CompletableFuture<AsyncReadBridge.Provider> response;volatile CompletableFuture<?> observer;
  int rpc,opens,readCalls,sourceCloses;final AsyncReadBridge.Provider identity;
  Host(Order o){order=o;identity=c->{opens++;byte[] b=bytes.toByteArray();return CompletableFuture.completedFuture(new AsyncReadBridge.Handle(){
   public Long length(){return (long)b.length;}
   public CompletionStage<Integer> readAt(long at,byte[] dst,int off,int n,AsyncReadBridge.Cancellation c){readCalls++;if(at>=b.length)return CompletableFuture.completedFuture(-1);int count=Math.min(1,(int)Math.min(n,b.length-at));System.arraycopy(b,(int)at,dst,off,count);return CompletableFuture.completedFuture(count);}
   public CompletionStage<Void> closeAsync(){sourceCloses++;return CompletableFuture.completedFuture(null);}
  });};}
  public CompletionStage<AsyncReadBridge.Provider> reopenReadOnly(){rpc++;response=new CompletableFuture<>();
   if(order==Order.OBSERVER_AFTER_WORKER)observer=response.whenCompleteAsync((p,e)->{observerEntered.countDown();try{observerGate.await();}catch(InterruptedException ex){Thread.currentThread().interrupt();throw new CompletionException(ex);}},r->{actualObserverThread=new Thread(r,"tester-real-whenComplete-observer");actualObserverThread.start();});
   actualWorker=new Thread(()->{try{
    if(order==Order.WORKER_BEFORE_ACK)return;
    responseGate.await();response.complete(identity);
    if(order==Order.ACK_THREAD_TAIL)threadTail.await();
   }catch(InterruptedException ex){Thread.currentThread().interrupt();response.completeExceptionally(ex);}},"tester-original-reopen-worker");actualWorker.start();return response;
  }
  public boolean writerOriginalsReturned(){return closed;}
  public boolean originalOperationsReturned(){return (actualWorker==null||!actualWorker.isAlive())&&(observer==null||observer.isDone())&&(actualObserverThread==null||!actualObserverThread.isAlive());}
  void joinOriginals()throws Exception{responseGate.countDown();threadTail.countDown();observerGate.countDown();if(response!=null&&!response.isDone())response.complete(identity);if(actualWorker!=null){actualWorker.join(2000);need(!actualWorker.isAlive(),"same original worker joined");}if(actualObserverThread!=null){actualObserverThread.join(2000);need(!actualObserverThread.isAlive()&&observer.isDone(),"same actual whenComplete stage and thread returned");}}
 }
 static TemporaryOutput written(Host h,long timeout)throws Exception{TemporaryOutput s=new TemporaryOutput(h,false,WORKER,timeout);s.channel().write(ByteBuffer.wrap(new byte[]{2,4,6,8}));s.channel().close();s.finishWriter();return s;}
 static void call(TemporaryOutput s,Entry entry,Reject v)throws Exception{if(entry==Entry.STRUCTURE)s.inspectHostMp4Structure(HostMp4Inspection.Container.MP4);else s.verifyAndValidate(v);}
 static void unpublished(TemporaryOutput s,Host h){need(!s.validationAcknowledged()&&!s.readyAcknowledged()&&!s.committed()&&h.readies==0&&h.commits==0,"no format receipt, READY or COMMIT");}
 static void finish(TemporaryOutput s,Host h)throws Exception{h.joinOriginals();s.observeOriginal();if(!s.returned())need(s.abort(),"same original abort cleanup");need(s.returned(),"same owners actually returned");unpublished(s,h);need(HostInputFactory.admittedSources()==0&&TemporaryOutput.retained()==0,"all keepers0");}
 static void pass(String label){passed++;System.out.println("PASS independent_shared "+label);}
 static void normal(Order order,Entry initial,Entry next)throws Exception {
  Host h=new Host(order);TemporaryOutput s=written(h,2500);Reject v=new Reject();Thread caller=null;HostInputFactory blocker=null;
  try{
   if(order==Order.WORKER_BEFORE_ACK){
    blocker=new HostInputFactory(3,4,"independent_identity",h.identity,WORKER);
    AtomicReference<Throwable> error=new AtomicReference<>();caller=new Thread(()->{try{call(s,initial,v);}catch(Throwable e){error.set(e);}},"tester-original-caller-awaiting-response");caller.start();await(()->h.response!=null&&h.actualWorker!=null);h.actualWorker.join(2000);
    need(!h.actualWorker.isAlive()&&!h.response.isDone()&&caller.isAlive(),"same worker returned while ACK/caller still pending");h.response.complete(h.identity);caller.join(2000);need(!caller.isAlive()&&error.get() instanceof IOException&&"SOURCE_RESOURCE_EXHAUSTED".equals(error.get().getMessage()),"original caller reached exact Provider admission not timeout");
   }else{
    h.responseGate.countDown();rejected(()->call(s,initial,v),"OUTPUT_ORIGINAL_PENDING");
    if(order==Order.OBSERVER_AFTER_WORKER){need(h.observerEntered.await(2000,TimeUnit.MILLISECONDS),"actual observer entered");h.actualWorker.join(2000);need(!h.actualWorker.isAlive()&&h.response.isDone()&&!h.observer.isDone(),"isolate actual observer tail after worker returned");}
    for(Entry e:Entry.values()){rejected(()->call(s,e,v),"OUTPUT_ORIGINAL_PENDING");need(s.firstFailure()==null&&h.rpc==1&&h.opens==0&&!s.returned(),"wait does not poison/admit/release/reissue");}
    rejected(s::finishOriginalCallbacks,"OUTPUT_ORIGINAL_PENDING");h.joinOriginals();need(s.observeOriginal()&&s.firstFailure()==null,"same original observed without cancel/abort");
    blocker=new HostInputFactory(3,4,"independent_identity",h.identity,WORKER);
   }
   need(HostInputFactory.admittedSources()==1,"second global slot free");
   for(Entry e:Entry.values())rejected(()->call(s,e,v),"SOURCE_RESOURCE_EXHAUSTED");
   need(s.firstFailure()==null&&h.opens==0&&h.rpc==1&&v.calls==0,"same Provider identity retained and admission not consumed by denied source");
   blocker.close();need(blocker.awaitOriginalReturns(2000),"exact identity reservation returned");blocker=null;
   String realFailure=next==Entry.STRUCTURE?"OUTPUT_HOST_STRUCTURE_FAILED":"OUTPUT_VALIDATION_FAILED";
   rejected(()->call(s,next,v),realFailure);
   need(realFailure.equals(s.firstFailure())&&h.rpc==1,"actual first check runs once after originals return");
   if(next==Entry.VERIFY)need(h.opens==1&&h.sourceCloses==1&&h.readCalls==4&&v.calls==1,"exact Provider real short1x4+known-length EOF and false validator, no content qualification");else need(h.opens==0&&v.calls==0,"real Media3 construction blocked before provider open");
   for(Entry e:Entry.values())rejected(()->call(s,e,v),"OUTPUT_NOT_VALIDATABLE");
   need(realFailure.equals(s.firstFailure())&&h.rpc==1,"actual check failure sticky across shared entries");unpublished(s,h);
   System.out.println("OBSERVE order="+order+" initial="+initial+" next="+next+" cancelOrAbortBeforeContinue=false sameProviderWithFreeSecondSlot=true reopenRPC="+h.rpc+" realFailure="+realFailure+" realContainer=NOT_RUN");
  }finally{if(blocker!=null){blocker.close();need(blocker.awaitOriginalReturns(2000),"blocker return");}h.joinOriginals();if(caller!=null){caller.join(2000);need(!caller.isAlive(),"same caller returned");}finish(s,h);}
  pass(order+"_"+initial+"_TO_"+next);
 }
 static void timeout(Entry entry)throws Exception{Host h=new Host(Order.ACK_THREAD_TAIL);TemporaryOutput s=written(h,70);Reject v=new Reject();try{
  rejected(()->call(s,entry,v),"OUTPUT_TIMEOUT_PENDING");need(h.rpc==1&&"OUTPUT_TIMEOUT_PENDING".equals(s.firstFailure())&&!h.response.isDone(),"real deadline expired");h.responseGate.countDown();await(()->h.response.isDone());s.observeOriginal();need(!h.originalOperationsReturned()&&!s.returned(),"late ACK retains same worker");h.joinOriginals();s.observeOriginal();for(Entry e:Entry.values())rejected(()->call(s,e,v),"OUTPUT_NOT_VALIDATABLE");need(h.rpc==1&&h.opens==0&&"OUTPUT_TIMEOUT_PENDING".equals(s.firstFailure()),"late normal ACK cannot clear true timeout");
 }finally{finish(s,h);}pass("REAL_TIMEOUT_"+entry);}
 static void intent(boolean abort)throws Exception{Host h=new Host(Order.ACK_THREAD_TAIL);TemporaryOutput s=written(h,2500);Reject v=new Reject();try{h.responseGate.countDown();rejected(()->call(s,Entry.STRUCTURE,v),"OUTPUT_ORIGINAL_PENDING");if(abort)need(!s.abort(),"pending original blocks release");else s.cancel();need(!s.returned(),"intent no fake return");h.joinOriginals();s.observeOriginal();for(Entry e:Entry.values())rejected(()->call(s,e,v),"OUTPUT_NOT_VALIDATABLE");need(h.rpc==1&&h.opens==0,"cancel/abort never cleared");}finally{finish(s,h);}pass(abort?"ABORT_STICKY":"CANCEL_STICKY");}
 @SuppressWarnings({"unchecked","rawtypes"}) static void invalid(Entry entry,String kind)throws Exception {
  Host h=new Host(Order.ACK_THREAD_TAIL){public CompletionStage<AsyncReadBridge.Provider> reopenReadOnly(){rpc++;if(kind.equals("PERMISSION"))throw new SecurityException("private permission path");if(kind.equals("UNKNOWN"))throw new IllegalStateException("private invocation outcome unknown");if(kind.equals("NULL_STAGE"))return null;if(kind.equals("CANCELLED_STAGE")){CompletableFuture f=new CompletableFuture();f.cancel(false);return f;}return (CompletionStage)CompletableFuture.completedFuture(kind.equals("WRONG_VALUE")?"private token":null);}};
  TemporaryOutput s=written(h,2500);Reject v=new Reject();String expected=kind.equals("PERMISSION")?"OUTPUT_PERMISSION_DENIED":kind.equals("NULL_STAGE")?"OUTPUT_INVALID_HOST_RESULT":"OUTPUT_REOPEN_FAILED";
  try{rejected(()->call(s,entry,v),expected);for(Entry e:Entry.values())rejected(()->call(s,e,v),"OUTPUT_NOT_VALIDATABLE");need(expected.equals(s.firstFailure())&&h.rpc==1&&h.opens==0,"real bad result/UNKNOWN no clear/retry/parse");}finally{finish(s,h);}pass("FAILURE_"+kind+"_"+entry);
 }
 public static void main(String[] args)throws Exception{
  System.out.println("ORIGIN="+TemporaryOutput.class.getProtectionDomain().getCodeSource().getLocation());
  for(Order order:Order.values())for(Entry initial:Entry.values())for(Entry next:Entry.values())normal(order,initial,next);
  for(Entry e:Entry.values()){timeout(e);for(String kind:new String[]{"PERMISSION","UNKNOWN","NULL_STAGE","NULL_PROVIDER","WRONG_VALUE","CANCELLED_STAGE"})invalid(e,kind);}
  intent(false);intent(true);need(passed==28,"finite independent count");System.out.println("DONE independentSharedCases="+passed+" sameCallersWorkersObserversReturned=true sourceKeepers0 outputKeepers0 actualContainerSuccess=NOT_RUN");
 }
}
