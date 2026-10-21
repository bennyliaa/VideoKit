package review;
import com.videokit.spike.c14.*;
import com.videokit.spike.e4.*;
import java.io.*;import java.nio.*;import java.nio.file.*;import java.util.*;import java.util.concurrent.*;import java.util.concurrent.atomic.*;
public final class BaselineCheck {
 static void need(boolean b,String m){if(!b)throw new AssertionError(m);}
 interface Action {void run()throws Exception;}
 static void rejects(Action a,String code)throws Exception {try{a.run();throw new AssertionError("expected "+code);}catch(IOException x){need(x.getMessage().equals(code),"wrong error "+x);}}
 static byte value(long p){return (byte)((p*1664525L+0x20261020L)>>>9);}
 static class Source implements AsyncReadBridge.Provider {
  final Long length;final long end;final int shortRead;final List<Long> positions=new ArrayList<>();final List<Integer> sizes=new ArrayList<>();
  Source(Long length,long end,int shortRead){this.length=length;this.end=end;this.shortRead=shortRead;}
  public CompletionStage<AsyncReadBridge.Handle> open(AsyncReadBridge.Cancellation c){return CompletableFuture.completedFuture(new AsyncReadBridge.Handle(){
   public Long length(){return length;}
   public CompletionStage<Integer> readAt(long at,byte[] b,int off,int n,AsyncReadBridge.Cancellation c){positions.add(at);sizes.add(n);if(at>=end)return CompletableFuture.completedFuture(-1);int count=(int)Math.min(Math.min(n,shortRead),end-at);for(int i=0;i<count;i++)b[off+i]=value(at+i);return CompletableFuture.completedFuture(count);}
   public CompletionStage<Void> closeAsync(){return CompletableFuture.completedFuture(null);}
  });}
 }
 static final class Ctx implements AutoCloseable {
  final AsyncReadBridge.Runtime rt=new AsyncReadBridge.Runtime();final LeaseRegistry lr=new LeaseRegistry();final long gen;final AsyncReadBridge bridge;
  Ctx(AsyncReadBridge.Provider p)throws Exception{gen=lr.create();bridge=new AsyncReadBridge(rt,p,lr,gen,2000);}
  public void close()throws Exception{bridge.close();lr.retire(gen);need(lr.awaitReleased(gen,2000),"original provider pending");rt.awaitOriginalTermination(lr,gen);need(rt.finishReturned(lr,gen),"original executor threads not joined");}
 }
 static void ranges()throws Exception {
  Source known=new Source(100L,100,3);try(Ctx x=new Ctx(known)){need(x.bridge.open(5,7)==7,"known requested range");byte[] b=new byte[16];int at=0,n;while((n=x.bridge.read(b,at,7-at))>0)at+=n;need(at==7,"short reads accumulate");for(int i=0;i<7;i++)need(b[i]==value(5+i),"exact short bytes");need(known.positions.equals(List.of(5L,8L,11L)),"long positions");need(x.bridge.read(b,0,1)==-1,"known range EOF");}
  Source unknown=new Source(null,5,3);try(Ctx x=new Ctx(unknown)){need(x.bridge.open(0,-1)==-1,"unknown length not invented");byte[] b=new byte[10];need(x.bridge.read(b,0,10)==3&&x.bridge.read(b,3,7)==2&&x.bridge.read(b,5,5)==-1,"unknown EOF exact");}
  long high=(1L<<31)+123;Source sparse=new Source(5L<<30,5L<<30,65536);try(Ctx x=new Ctx(sparse)){x.bridge.open(high,-1);byte[] b=new byte[65537];need(x.bridge.read(b,0,b.length)==65536,"single block clamp64KiB");need(sparse.positions.get(0)==high&&b[0]==value(high),"no32bit truncation");x.bridge.seekAbsolute((3L<<30)+7);need(x.bridge.read(b,0,1)==1&&sparse.positions.get(1)==(3L<<30)+7,"sparse long seek");}
  Source overflow=new Source(null,Long.MAX_VALUE,1){public CompletionStage<AsyncReadBridge.Handle> open(AsyncReadBridge.Cancellation c){return CompletableFuture.completedFuture(new AsyncReadBridge.Handle(){public Long length(){return null;}public CompletionStage<Integer> readAt(long p,byte[] b,int o,int n,AsyncReadBridge.Cancellation c){b[o]=99;return CompletableFuture.completedFuture(1);}public CompletionStage<Void> closeAsync(){return CompletableFuture.completedFuture(null);}});}};
  try(Ctx x=new Ctx(overflow)){x.bridge.open(Long.MAX_VALUE,-1);byte[] target={42};rejects(()->x.bridge.read(target,0,1),"INVALID_RANGE");need(target[0]==42,"overflow cannot copy private result to caller");}
  System.out.println("PASS short_reads_unknown_eof_sparse_gt2GiB_64KiB_and_overflow");
 }
 static void invalidReadAndErrors()throws Exception {
  for(int result:new int[]{0,-2,9}){
   AsyncReadBridge.Provider p=c->CompletableFuture.completedFuture(new AsyncReadBridge.Handle(){public Long length(){return null;}public CompletionStage<Integer> readAt(long at,byte[] b,int o,int n,AsyncReadBridge.Cancellation t){return CompletableFuture.completedFuture(result);}public CompletionStage<Void> closeAsync(){return CompletableFuture.completedFuture(null);}});
   try(Ctx x=new Ctx(p)){x.bridge.open(0,-1);rejects(()->x.bridge.read(new byte[8],0,8),"INVALID_READ_RESULT");}
  }
  AsyncReadBridge.Provider denied=c->{CompletableFuture<AsyncReadBridge.Handle> f=new CompletableFuture<>();f.completeExceptionally(new java.nio.file.AccessDeniedException("controlled-private-name"));return f;};try(Ctx x=new Ctx(denied)){rejects(()->x.bridge.open(0,-1),"SOURCE_PERMISSION_DENIED");}
  System.out.println("PASS invalid_zero_negative_oversized_result_and_redacted_permission");
 }
 static void cancelLate()throws Exception {
  CompletableFuture<Integer> read=new CompletableFuture<>();CompletableFuture<Void> close=new CompletableFuture<>();CountDownLatch entered=new CountDownLatch(1);AtomicReference<byte[]> privateBytes=new AtomicReference<>();
  AsyncReadBridge.Provider p=c->CompletableFuture.completedFuture(new AsyncReadBridge.Handle(){public Long length(){return null;}public CompletionStage<Integer> readAt(long at,byte[] b,int o,int n,AsyncReadBridge.Cancellation t){privateBytes.set(b);entered.countDown();return read;}public CompletionStage<Void> closeAsync(){return close;}});
  Ctx x=new Ctx(p);byte[] target={55};AtomicReference<Throwable> result=new AtomicReference<>();Thread caller=new Thread(()->{try{x.bridge.read(target,0,1);}catch(Throwable t){result.set(t);}});
  try{x.bridge.open(0,-1);caller.start();need(entered.await(1,TimeUnit.SECONDS),"real provider entered");rejects(()->x.bridge.read(new byte[1],0,1),"READ_IN_FLIGHT");x.bridge.close();x.lr.retire(x.gen);caller.join(1000);need(!caller.isAlive()&&result.get() instanceof IOException,"caller wakes from cancel");need(!x.lr.query(x.gen).released(),"cancel not original return");privateBytes.get()[0]=99;read.complete(1);need(target[0]==55,"late private bytes never copied");need(!x.lr.query(x.gen).released(),"late read does not close handle");close.complete(null);}finally{read.complete(1);close.complete(null);caller.join(1000);x.close();}
  System.out.println("PASS one_bridge_inflight1_cancel_late_result_and_original_close_join");
 }
 static void twoConsumers()throws Exception {
  AsyncReadBridge.Runtime rt=new AsyncReadBridge.Runtime();LeaseRegistry lr=new LeaseRegistry();long g=lr.create();CountDownLatch both=new CountDownLatch(2);List<CompletableFuture<Integer>> pending=Collections.synchronizedList(new ArrayList<>());AtomicInteger live=new AtomicInteger(),peak=new AtomicInteger(),closes=new AtomicInteger();
  AsyncReadBridge.Provider p=c->CompletableFuture.completedFuture(new AsyncReadBridge.Handle(){public Long length(){return 1L;}public CompletionStage<Integer> readAt(long at,byte[] b,int o,int n,AsyncReadBridge.Cancellation t){int v=live.incrementAndGet();peak.accumulateAndGet(v,Math::max);CompletableFuture<Integer> f=new CompletableFuture<>();f.whenComplete((a,z)->live.decrementAndGet());pending.add(f);both.countDown();return f;}public CompletionStage<Void> closeAsync(){closes.incrementAndGet();return CompletableFuture.completedFuture(null);}});
  AsyncReadBridge a=new AsyncReadBridge(rt,p,lr,g,2000),b=new AsyncReadBridge(rt,p,lr,g,2000);AtomicReference<Throwable> err=new AtomicReference<>();Thread ta=new Thread(()->{try{a.read(new byte[1],0,1);}catch(Throwable t){err.set(t);}}),tb=new Thread(()->{try{b.read(new byte[1],0,1);}catch(Throwable t){err.set(t);}});
  try{a.open(0,-1);b.open(0,-1);ta.start();tb.start();need(both.await(1,TimeUnit.SECONDS),"two real async provider stages");need(peak.get()==2,"expected baseline per-consumer rather than per-source gate");a.close();need(!lr.query(g).released(),"first close retains source");for(CompletableFuture<Integer> f:pending)f.complete(1);ta.join(1000);tb.join(1000);b.close();lr.retire(g);need(lr.awaitReleased(g,2000),"both consumers returned");rt.awaitOriginalTermination(lr,g);need(rt.finishReturned(lr,g)&&closes.get()==2,"same runtime threads and two physical handle closes");}finally{for(CompletableFuture<Integer> f:pending)f.complete(1);a.close();b.close();lr.retire(g);ta.join(1000);tb.join(1000);rt.awaitOriginalTermination(lr,g);}
  System.out.println("OBSERVED GAP_A01 baseline_same_source_pending_reads_peak=2 new_batch_requires1; dual_consumer_originals_returned=true");
 }
 static void outputFaults(Path dir)throws Exception {
  AtomicInteger physical=new AtomicInteger();OutputStream partial=new OutputStream(){boolean failed;public void write(int b){physical.incrementAndGet();}public void write(byte[] b,int o,int n)throws IOException{if(!failed){failed=true;physical.addAndGet(7);throw new IOException("CONTROLLED_PARTIAL_WRITE");}physical.addAndGet(n);}};
  BoundedOutputChannel c=new BoundedOutputChannel(partial);ByteBuffer data=ByteBuffer.wrap(new byte[32]);try{c.write(data);throw new AssertionError("partial failure missing");}catch(IOException expected){}
  need(c.bytes()==32&&physical.get()==7&&data.position()==32,"attempted versus actual prefix");need(c.isOpen(),"legacy primitive is not sticky transaction");c.close();
  AtomicInteger closeCalls=new AtomicInteger();OutputStream badClose=new OutputStream(){public void write(int v){}public void close()throws IOException{closeCalls.incrementAndGet();throw new IOException("CONTROLLED_CLOSE_FAIL");}};
  BoundedOutputChannel guarded=new BoundedOutputChannel(badClose);E4Owned<BoundedOutputChannel> owned=new E4Owned<>("controlled-original-channel",BoundedOutputChannel::close);owned.allocate(()->guarded);try{owned.close();throw new AssertionError();}catch(IOException expected){}need(!owned.returned()&&owned.state()==E4Owned.State.UNKNOWN&&owned.original()==guarded,"same failed owner retained");try{owned.close();throw new AssertionError();}catch(IOException expected){}need(closeCalls.get()==1,"no second original close");
  Path input=dir.resolve("generated-validation-input.bin");Files.write(input,new byte[]{1,2,3,4},StandardOpenOption.CREATE_NEW);AtomicInteger realClose=new AtomicInteger();E4Owned<InputStream> reopen=new E4Owned<>(input,stream->{stream.close();realClose.incrementAndGet();});reopen.allocate(()->Files.newInputStream(input));try{reopen.initialize(stream->{need(stream.read()==1,"actual file reopen");throw new IOException("CONTROLLED_VALIDATION_REJECTED_NOT_CONTAINER");});throw new AssertionError();}catch(IOException expected){}need(reopen.returned()&&realClose.get()==1&&reopen.firstFailure()!=null,"validation failed and original file closed");
  E4Owned<InputStream> missing=new E4Owned<>(dir.resolve("absent.bin"),InputStream::close);try{missing.allocate(()->Files.newInputStream(dir.resolve("absent.bin")));throw new AssertionError();}catch(NoSuchFileException expected){}need(!missing.returned()&&missing.state()==E4Owned.State.UNKNOWN,"failed reopen cannot publish return/READY");
  ByteArrayOutputStream target=new ByteArrayOutputStream();BoundedOutputChannel limit=new BoundedOutputChannel(target);try{limit.write(ByteBuffer.allocate(PipelineRules.MAX_OUTPUT+1));throw new AssertionError();}catch(IOException expected){need(target.size()==0&&limit.bytes()==0,"budget reject before write");}limit.close();
  System.out.println("OBSERVED GAP_A02 partial_actual_prefix=7 attempted_budget=32 buffer_position=32; primitive_not_transactional");
  System.out.println("PASS owned_close_failure_unknown_no_second_close_real_file_reopen_validation_failure_and_budget_reject");
 }
 static void readyLayer()throws Exception {
  E4Protocol.Identity id=new E4Protocol.Identity("0123456789abcdef0123456789abcdef",1,1,"01234567-89ab-cdef-0123-456789abcdef",10001,99001);E4Broker broker=new E4Broker();broker.createHost(id,true);broker.serviceReady(99001,id,true);
  rejects(()->broker.remoteOutputClosed(99001,id,6,0,0,true,true,32),"E4_REMOTE_OUTPUT_CLOSE_UNPROVEN");broker.authorizeValidator(10001,id,99002);rejects(()->broker.validatedOutput(99002,id,6,new long[]{0,1,2,3,4,5},true),"E4_VALIDATION_NOT_PROVEN");need(broker.snapshot(id).state!=E4Broker.State.READY,"metadata cannot fabricate validated container");
  need(Arrays.stream(E4Broker.State.values()).noneMatch(x->x.name().contains("COMMIT")),"READY is not host business COMMIT");broker.cancel(10001,id);
  System.out.println("PASS premature_ready_rejected_no_container_validation_claim_no_business_commit_state");
 }
 public static void main(String[] args)throws Exception{ranges();invalidReadAndErrors();cancelLate();twoConsumers();outputFaults(Paths.get(args[0]));readyLayer();System.out.println("PHASE_A_FROZEN_BASELINE_ONLY no_Media3_DataSource_integration_no_container_decode_no_device_claim");}
}
