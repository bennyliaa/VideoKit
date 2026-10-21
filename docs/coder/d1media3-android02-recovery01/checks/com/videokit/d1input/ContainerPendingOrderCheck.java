package com.videokit.d1input;
import com.videokit.spike.c14.*;
import java.io.*;import java.nio.*;import java.util.concurrent.*;import java.util.concurrent.atomic.*;
import static com.videokit.d1input.InputSinkCheck.*;

/** Finite real-thread/real-CompletionStage ordering. Host ports are controlled;
 * Media3 and production fields are not substituted or altered. Four-byte input
 * is deliberately NON-MEDIA. Successful continuation means admission reaches
 * the real missing-platform/failure boundary, NEVER container success. */
public final class ContainerPendingOrderCheck {
 enum Order { ACK_FIRST, THREAD_FIRST, OBSERVER_TAIL, TIMEOUT, CANCEL_RESPONSE }
 enum Entry { HOST_STRUCTURE, LEGACY_VALIDATION }
 static int cases;
 static void done(String name){cases++;need(HostInputFactory.admittedSources()==0&&TemporaryOutput.retained()==0,"original keepers0 after "+name);System.out.println("PASS inspection_order "+name);}
 static class ScheduledHost extends MemSink {
  final Order order;final CountDownLatch work,tail=new CountDownLatch(1),observerGate=new CountDownLatch(1),observerEntered=new CountDownLatch(1);
  volatile Thread actual;volatile CompletableFuture<AsyncReadBridge.Provider> response;volatile CompletableFuture<?> actualObserver;
  int reopenRPC,providerOpens,providerCloses;final AsyncReadBridge.Provider sameProvider;
  ScheduledHost(Order order){this.order=order;work=new CountDownLatch(order==Order.TIMEOUT?1:0);sameProvider=c->{providerOpens++;byte[] b=bytes.toByteArray();return CompletableFuture.completedFuture(new AsyncReadBridge.Handle(){
   public Long length(){return (long)b.length;}
   public CompletionStage<Integer> readAt(long at,byte[] target,int off,int len,AsyncReadBridge.Cancellation token){if(at>=b.length)return CompletableFuture.completedFuture(-1);int n=(int)Math.min(len,b.length-at);System.arraycopy(b,(int)at,target,off,n);return CompletableFuture.completedFuture(n);}
   public CompletionStage<Void> closeAsync(){providerCloses++;return CompletableFuture.completedFuture(null);}
  });};}
  public CompletionStage<AsyncReadBridge.Provider> reopenReadOnly(){
   reopenRPC++;response=new CompletableFuture<>();
   if(order==Order.OBSERVER_TAIL)actualObserver=response.whenComplete((p,error)->{observerEntered.countDown();try{observerGate.await();}catch(InterruptedException e){Thread.currentThread().interrupt();throw new CompletionException(e);}});
   actual=new Thread(()->{try{work.await();if(order==Order.THREAD_FIRST)return;if(order==Order.CANCEL_RESPONSE)response.cancel(false);else response.complete(sameProvider);if(order!=Order.OBSERVER_TAIL)tail.await();}catch(InterruptedException e){Thread.currentThread().interrupt();response.completeExceptionally(e);}},"container02-original-reopen-"+order);actual.start();return response;
  }
  public boolean originalOperationsReturned(){return (actual==null||!actual.isAlive())&&(actualObserver==null||actualObserver.isDone());}
  public boolean writerOriginalsReturned(){return closed;}
  void returnSame()throws Exception{work.countDown();observerGate.countDown();tail.countDown();if(response!=null&&!response.isDone())response.complete(sameProvider);if(actual!=null){actual.join(2500);need(!actual.isAlive(),"same original worker joined");}need(actualObserver==null||actualObserver.isDone(),"same original observer returned");}
 }
 static final class RejectingValidator implements HostOutput.Validator {
  int calls;public CompletionStage<HostOutput.Validation> validate(String id,long n,String hash){calls++;return CompletableFuture.completedFuture(new HostOutput.Validation(id,n,hash,HostMp4Inspection.KIND,false));}
  public boolean originalOperationsReturned(){return true;}
 }
 static TemporaryOutput written(ScheduledHost h,long timeout)throws Exception{TemporaryOutput s=new TemporaryOutput(h,false,WORKER,timeout);s.channel().write(ByteBuffer.wrap(new byte[]{1,3,5,7}));s.channel().close();s.finishWriter();return s;}
 static void enter(TemporaryOutput s,Entry entry,RejectingValidator validator)throws Exception{if(entry==Entry.HOST_STRUCTURE)s.inspectHostMp4Structure(HostMp4Inspection.Container.FRAGMENTED_MP4);else s.verifyAndValidate(validator);}
 static void noPublication(TemporaryOutput s,ScheduledHost h){need(!s.validationAcknowledged()&&!s.readyAcknowledged()&&!s.committed()&&h.readies==0&&h.commits==0,"no isolated receipt/READY/COMMIT from pending or host inspection");}
 static void cleanup(TemporaryOutput s,ScheduledHost h)throws Exception{h.returnSame();s.observeOriginal();if(!s.returned())need(s.abort(),"same original abort cleanup");need(s.returned(),"all exact originals returned");noPublication(s,h);}

 static void normal(Order order,Entry first,Entry continuation)throws Exception {
  ScheduledHost h=new ScheduledHost(order);TemporaryOutput s=written(h,5000);RejectingValidator validator=new RejectingValidator();HostInputFactory identityOwner=null;Thread caller=null;
  try{
   if(order==Order.THREAD_FIRST){
    // Only one external source capability; a free second slot remains. Failure
    // therefore proves exact Provider identity reuse, rather than total quota.
    identityOwner=new HostInputFactory(1,2,"same_provider_identity_probe",h.sameProvider,WORKER);
    AtomicReference<Throwable> error=new AtomicReference<>();caller=new Thread(()->{try{enter(s,first,validator);}catch(Throwable t){error.set(t);}},"container02-original-inspection-caller");caller.start();await(()->h.response!=null&&h.actual!=null);h.actual.join(2500);
    need(!h.actual.isAlive()&&!h.response.isDone()&&caller.isAlive(),"original worker returned before exact original ACK");
    h.response.complete(h.sameProvider);caller.join(2500);need(!caller.isAlive()&&error.get() instanceof IOException&&"SOURCE_RESOURCE_EXHAUSTED".equals(error.get().getMessage()),"same Provider blocked before parser after ACK; no timeout");
   }else{
    rejected(()->enter(s,first,validator),"OUTPUT_ORIGINAL_PENDING");need(h.response.isDone()&&!h.originalOperationsReturned(),"ACK answered while original remains physically pending");
    if(order==Order.OBSERVER_TAIL){need(h.observerEntered.await(1000,TimeUnit.MILLISECONDS)&&!h.actualObserver.isDone(),"actual whenComplete observer still executing after response isDone");}
    for(Entry waiting:Entry.values()){rejected(()->enter(s,waiting,validator),"OUTPUT_ORIGINAL_PENDING");need(s.firstFailure()==null&&h.reopenRPC==1&&h.providerOpens==0&&HostInputFactory.admittedSources()==0,"stable admission wait neither consumes check nor issues another RPC/source open");}
    rejected(s::finishOriginalCallbacks,"OUTPUT_ORIGINAL_PENDING");h.returnSame();need(s.observeOriginal()&&h.originalOperationsReturned(),"observe and join same originals without cancel/abort");
    identityOwner=new HostInputFactory(1,2,"same_provider_identity_probe",h.sameProvider,WORKER);
    rejected(()->enter(s,continuation,validator),"SOURCE_RESOURCE_EXHAUSTED");
   }
   need(s.firstFailure()==null&&h.reopenRPC==1&&h.providerOpens==0&&HostInputFactory.admittedSources()==1&&validator.calls==0,"same original grant reused, pre-parser quota rejection not a consumed inspection");
   identityOwner.close();need(identityOwner.awaitOriginalReturns(2500),"exact identity probe capability returned");identityOwner=null;
   String expected=continuation==Entry.HOST_STRUCTURE?"OUTPUT_HOST_STRUCTURE_FAILED":"OUTPUT_VALIDATION_FAILED";
   rejected(()->enter(s,continuation,validator),expected);
   need(expected.equals(s.firstFailure())&&h.reopenRPC==1&&HostInputFactory.admittedSources()==0,"first actual inspection/failure boundary entered only once, same RPC");
   if(continuation==Entry.LEGACY_VALIDATION)need(h.providerOpens==1&&h.providerCloses==1&&validator.calls==1,"same original Provider actual4B EOF/hash and explicitly rejecting controlled validator");
   else need(h.providerOpens==0&&validator.calls==0,"actual parser construction platform failure, not parsed media");
   rejected(()->enter(s,Entry.HOST_STRUCTURE,validator),"OUTPUT_NOT_VALIDATABLE");rejected(()->enter(s,Entry.LEGACY_VALIDATION,validator),"OUTPUT_NOT_VALIDATABLE");need(expected.equals(s.firstFailure())&&h.reopenRPC==1,"real failure never cleared/retried");noPublication(s,h);
   System.out.println("OBSERVE order="+order+" first="+first+" continuation="+continuation+" cancelOrAbortBeforeContinue=false sameProviderIdentityProved=true reopenRPC=1 actualInspectionFailure="+expected+" containerSuccess=NOT_RUN");
  }finally{if(identityOwner!=null){identityOwner.close();need(identityOwner.awaitOriginalReturns(2500),"probe owner cleanup");}h.returnSame();if(caller!=null){caller.join(2500);need(!caller.isAlive(),"original synchronous caller joined");}cleanup(s,h);}
  done(order+"_"+first+"_TO_"+continuation);
 }
 static void stickyTimeout(Entry entry)throws Exception {
  ScheduledHost h=new ScheduledHost(Order.TIMEOUT);TemporaryOutput s=written(h,80);RejectingValidator v=new RejectingValidator();try{
   rejected(()->enter(s,entry,v),"OUTPUT_TIMEOUT_PENDING");need("OUTPUT_TIMEOUT_PENDING".equals(s.firstFailure())&&h.reopenRPC==1&&!h.response.isDone(),"genuine waited deadline retained");
   h.work.countDown();await(()->h.response.isDone());need(s.observeOriginal()&&!h.originalOperationsReturned()&&!s.returned(),"late exact ACK not physical return");
   rejected(()->enter(s,entry,v),"OUTPUT_NOT_VALIDATABLE");h.returnSame();rejected(()->enter(s,entry,v),"OUTPUT_NOT_VALIDATABLE");need("OUTPUT_TIMEOUT_PENDING".equals(s.firstFailure())&&h.reopenRPC==1&&h.providerOpens==0,"no timeout clearing, reissue or parser attempt");
  }finally{cleanup(s,h);}done("GENUINE_TIMEOUT_"+entry);
 }
 static void cancellation(boolean abort)throws Exception {
  ScheduledHost h=new ScheduledHost(Order.ACK_FIRST);TemporaryOutput s=written(h,5000);RejectingValidator v=new RejectingValidator();try{
   rejected(()->enter(s,Entry.HOST_STRUCTURE,v),"OUTPUT_ORIGINAL_PENDING");if(abort)need(!s.abort(),"abort cannot release before original tail");else s.cancel();
   need(!s.returned()&&h.reopenRPC==1,"cancel/abort intent retains exact originals");h.returnSame();s.observeOriginal();rejected(()->enter(s,Entry.HOST_STRUCTURE,v),"OUTPUT_NOT_VALIDATABLE");rejected(()->enter(s,Entry.LEGACY_VALIDATION,v),"OUTPUT_NOT_VALIDATABLE");need(h.reopenRPC==1&&h.providerOpens==0,"intent never cleared to permit inspection");
  }finally{cleanup(s,h);}done(abort?"ABORT_WHILE_ORIGINAL_TAIL":"CANCEL_WHILE_ORIGINAL_TAIL");
 }
 static void cancelledResponse()throws Exception {
  ScheduledHost h=new ScheduledHost(Order.CANCEL_RESPONSE);TemporaryOutput s=written(h,5000);RejectingValidator v=new RejectingValidator();try{
   rejected(()->enter(s,Entry.HOST_STRUCTURE,v),"OUTPUT_REOPEN_FAILED");need(!h.originalOperationsReturned()&&!s.returned(),"cancelled future not original physical return");h.returnSame();s.observeOriginal();rejected(()->enter(s,Entry.HOST_STRUCTURE,v),"OUTPUT_NOT_VALIDATABLE");need("OUTPUT_REOPEN_FAILED".equals(s.firstFailure())&&h.reopenRPC==1&&h.providerOpens==0,"failed ACK retained");
  }finally{cleanup(s,h);}done("CANCELLED_ORIGINAL_RESPONSE");
 }
 @SuppressWarnings({"rawtypes","unchecked"}) static void rejectedOriginal(String kind)throws Exception {
  ScheduledHost h=new ScheduledHost(Order.ACK_FIRST){public CompletionStage<AsyncReadBridge.Provider> reopenReadOnly(){reopenRPC++;if(kind.equals("PERMISSION"))throw new SecurityException("private grant");if(kind.equals("THROW_UNKNOWN"))throw new IllegalStateException("private maybe side effect");if(kind.equals("NULL_STAGE"))return null;return (CompletionStage)CompletableFuture.completedFuture(kind.equals("BAD_VALUE")?"private bad provider":null);}};
  TemporaryOutput s=written(h,5000);RejectingValidator v=new RejectingValidator();String expected=kind.equals("PERMISSION")?"OUTPUT_PERMISSION_DENIED":kind.equals("NULL_STAGE")?"OUTPUT_INVALID_HOST_RESULT":"OUTPUT_REOPEN_FAILED";
  try{rejected(()->enter(s,Entry.HOST_STRUCTURE,v),expected);rejected(()->enter(s,Entry.HOST_STRUCTURE,v),"OUTPUT_NOT_VALIDATABLE");need(expected.equals(s.firstFailure())&&h.reopenRPC==1&&h.providerOpens==0,"real grant/unknown/bad response failure remains sticky");}finally{cleanup(s,h);}done("ORIGINAL_"+kind);
 }
 public static void main(String[] args)throws Exception {
  System.out.println("ORIGIN="+TemporaryOutput.class.getProtectionDomain().getCodeSource().getLocation());
  for(Order order:new Order[]{Order.ACK_FIRST,Order.THREAD_FIRST,Order.OBSERVER_TAIL})for(Entry first:Entry.values())for(Entry next:Entry.values())normal(order,first,next);
  for(Entry entry:Entry.values())stickyTimeout(entry);cancellation(false);cancellation(true);cancelledResponse();
  for(String kind:new String[]{"PERMISSION","THROW_UNKNOWN","NULL_STAGE","BAD_VALUE","NULL_PROVIDER"})rejectedOriginal(kind);
  System.out.println("DONE inspectionOrderCases="+cases+" allSameOriginalCallersWorkersObserversReturned=true sourceKeepers0 outputKeepers0 actualContainerSuccess=NOT_RUN noNewPlatformPorts=true");
 }
}
