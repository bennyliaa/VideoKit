package com.videokit.d1input;
import androidx.media3.datasource.DataSpec;import com.videokit.spike.c14.*;
import java.io.*;import java.nio.ByteBuffer;import java.util.concurrent.*;import java.util.concurrent.atomic.*;
/** Controlled non-media HOST ports, real adapter/owners/threads. Never claims a native fault injection. */
public final class BoundaryScenarios {
 private static void need(boolean ok)throws IOException{if(!ok)throw new IOException("BOUNDARY_SCENARIO_FAILED");}
 private interface Checked{void run()throws Exception;}
 private static void pending(Checked f)throws Exception{try{f.run();throw new IOException("BOUNDARY_SCENARIO_FAILED");}catch(IOException e){if(!"OUTPUT_ORIGINAL_PENDING".equals(e.getMessage()))throw e;}}
 private static void joined(Thread t)throws Exception{t.join(2000);need(!t.isAlive());}
 public static final class Result{public final int inputAck,outputAck;Result(int i,int o){inputAck=i;outputAck=o;}}
 public static Result run(String name,WorkerRule rule)throws Exception{
  rule.requireWorker();Result result;if(name.equals("cancelLateRead"))result=cancelRead(rule);else if(name.equals("writerPending"))result=writer(rule);else throw new IOException("BOUNDARY_CASE_REJECTED");
  need(HostInputFactory.admittedSources()==0&&TemporaryOutput.retained()==0);return result;
 }
 private static Result cancelRead(WorkerRule rule)throws Exception {
  CompletableFuture<Integer> read=new CompletableFuture<>();CompletableFuture<Void> close=new CompletableFuture<>();CountDownLatch entered=new CountDownLatch(1);
  AtomicReference<byte[]> privateBuffer=new AtomicReference<>();AtomicReference<Throwable> outcome=new AtomicReference<>();byte[] caller={99};
  AsyncReadBridge.Provider p=c->CompletableFuture.completedFuture(new AsyncReadBridge.Handle(){
   public Long length(){return 1L;}
   public CompletionStage<Integer> readAt(long at,byte[] b,int off,int n,AsyncReadBridge.Cancellation token){privateBuffer.set(b);entered.countDown();return read;}
   public CompletionStage<Void> closeAsync(){return close;}
  });
  HostInputFactory f=new HostInputFactory(1,1,"controlled_late_metadata",p,rule);HostDataSource ds=f.createDataSource();Thread original=null;
  try{ds.open(new DataSpec(f.uri()));original=new Thread(()->{try{ds.read(caller,0,1);}catch(Throwable e){outcome.set(e);}},"android02-controlled-original-reader");original.start();need(entered.await(2,TimeUnit.SECONDS));
   ds.close();joined(original);need(outcome.get() instanceof IOException&&!f.originalsReturned()&&caller[0]==99);
   privateBuffer.get()[0]=7;read.complete(1);need(!f.originalsReturned()&&caller[0]==99);close.complete(null);
  }finally{read.complete(1);close.complete(null);ds.close();f.close();if(original!=null)joined(original);need(f.awaitOriginalReturns(2000));}
  need(caller[0]==99);return new Result(read.getNow(0),0);
 }
 private static final class PendingWriter implements HostOutput {
  final CountDownLatch entered=new CountDownLatch(1),tail=new CountDownLatch(1);Thread original;boolean closed;int reopen,closeCalls,ready,written;SinkCoordinator.HostState terminal=SinkCoordinator.HostState.WRITING;
  public String opaqueTask(){return "android02_controlled_writer";}public Capabilities capabilities(){return new Capabilities(true,false,true,true,true);}
  public CompletionStage<Integer> writeAt(long at,byte[] b,int off,int n){written+=n;return CompletableFuture.completedFuture(n);}
  public CompletionStage<Void> flush(){return CompletableFuture.completedFuture(null);}
  public CompletionStage<Void> closeWriter(){closeCalls++;CompletableFuture<Void> ack=new CompletableFuture<>();original=new Thread(()->{closed=true;ack.complete(null);entered.countDown();try{tail.await();}catch(InterruptedException e){Thread.currentThread().interrupt();}},"android02-controlled-writer-tail");original.start();return ack;}
  public boolean originalOperationsReturned(){return original==null||!original.isAlive();}public boolean writerOriginalsReturned(){return closed&&originalOperationsReturned();}
  public CompletionStage<AsyncReadBridge.Provider> reopenReadOnly(){reopen++;return HostInputFactory.failed("FORBIDDEN_REOPEN");}
  public CompletionStage<String> markReady(String id){ready++;return HostInputFactory.failed("FORBIDDEN_READY");}
  public CompletionStage<Void> abort(String id){terminal=SinkCoordinator.HostState.ABORTED;return CompletableFuture.completedFuture(null);}
  public CompletionStage<SinkCoordinator.Status> query(String id){return CompletableFuture.completedFuture(new SinkCoordinator.Status(terminal,null));}
  public SinkCoordinator.Status originalTerminalStatus(String id){return new SinkCoordinator.Status(terminal,null);}
 }
 private static Result writer(WorkerRule rule)throws Exception {
  PendingWriter host=new PendingWriter();TemporaryOutput out=new TemporaryOutput(host,false,rule,2000);
  try{out.channel().write(ByteBuffer.wrap(new byte[]{1,2,3,4}));out.channel().close();pending(out::finishWriter);need(host.entered.await(2,TimeUnit.SECONDS));
   pending(()->out.inspectHostMp4Structure(HostMp4Inspection.Container.FRAGMENTED_MP4));need(host.reopen==0&&!out.returned()&&out.firstFailure()==null&&host.closeCalls==1);
   host.tail.countDown();joined(host.original);out.finishWriter();need(host.closeCalls==1&&out.writerReturned()&&host.reopen==0&&host.ready==0&&!out.validationAcknowledged()&&!out.readyAcknowledged()&&!out.committed());
  }finally{host.tail.countDown();if(host.original!=null)joined(host.original);out.observeOriginal();need(out.abort()&&out.returned());}
  return new Result(0,host.written);
 }
 private BoundaryScenarios(){}
}
