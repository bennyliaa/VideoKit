package com.videokit.d1input;
import android.net.Uri;
import androidx.media3.datasource.*;
import com.videokit.spike.c14.*;
import com.videokit.spike.e4.*;
import java.io.*;import java.util.*;import java.util.concurrent.*;import java.util.concurrent.atomic.*;

/** Finite feasibility binding, not frozen M0 API. SourceReleased is ONLY the original E13 registry
 * plus its original workers' return. This set limits two host source capabilities; it is no ledger. */
public final class HostInputFactory implements DataSource.Factory,AutoCloseable {
 private static final Set<HostInputFactory> ADMITTED=ConcurrentHashMap.newKeySet();
 final WorkerRule worker;final Uri opaqueUri;private final String version,task=UUID.randomUUID().toString();private final int uid,pid;
 private final AsyncReadBridge.Provider original;private final AtomicBoolean hostRead=new AtomicBoolean();
 private final List<HostDataSource> adapters=new ArrayList<>(2);private final List<Range> ranges=new ArrayList<>(2);private E13SourceGroup current;private long epoch;private boolean closed;
 public HostInputFactory(int uid,int pid,String opaqueVersion,AsyncReadBridge.Provider provider,WorkerRule worker)throws IOException {
  if(opaqueVersion==null||!opaqueVersion.matches("[A-Za-z0-9_-]{1,64}"))throw new IOException("OPAQUE_VERSION_REQUIRED");
  this.uid=uid;this.pid=pid;version=opaqueVersion;original=Objects.requireNonNull(provider);this.worker=Objects.requireNonNull(worker);opaqueUri=Uri.parse("videokit-source:"+UUID.randomUUID());
  synchronized(ADMITTED){if(ADMITTED.size()>=2||ADMITTED.stream().anyMatch(f->f.original==provider))throw new IOException("SOURCE_RESOURCE_EXHAUSTED");ADMITTED.add(this);}
 }
 public synchronized HostDataSource createDataSource(){if(closed||adapters.size()>=2)throw new IllegalStateException("FINITE_SOURCE_ADAPTER_BUDGET");HostDataSource a=new HostDataSource(this);adapters.add(a);return a;}
 public Uri uri(){return opaqueUri;}
 private AsyncReadBridge.Provider guarded(){return cancellation->original.open(cancellation).thenApply(h->{if(h==null)throw new CompletionException(new IOException("INVALID_READ_RESULT"));return new AsyncReadBridge.Handle(){
  public Long length(){return h.length();}
  public CompletionStage<Integer> readAt(long p,byte[] b,int o,int n,AsyncReadBridge.Cancellation c){
   if(!hostRead.compareAndSet(false,true))return failed("SOURCE_RESOURCE_EXHAUSTED");
   try{CompletionStage<Integer> result=Objects.requireNonNull(h.readAt(p,b,o,n,c));return result.whenComplete((v,e)->hostRead.set(false));}catch(Throwable t){hostRead.set(false);CompletableFuture<Integer> f=new CompletableFuture<>();f.completeExceptionally(t);return f;}
  }
  public CompletionStage<Void> closeAsync(){return h.closeAsync();}
 };});}
 static <T>CompletableFuture<T> failed(String code){CompletableFuture<T> f=new CompletableFuture<>();f.completeExceptionally(new IOException(code));return f;}
 static final class Range {final E13SourceGroup group;final E13SourceGroup.Consumer consumer;Range(E13SourceGroup g,E13SourceGroup.Consumer c){group=g;consumer=c;}}
 Range range()throws IOException {
  E13SourceGroup prior;synchronized(this){if(closed)throw new IOException("SESSION_RELEASED");prior=current;}
  if(prior!=null&&prior.snapshot().retired){try{if(!prior.awaitReturn(5000))throw new IOException("SOURCE_ORIGINAL_PENDING");}catch(InterruptedException e){Thread.currentThread().interrupt();throw new IOException("CANCELLED");}synchronized(this){if(current==prior){current=null;ranges.clear();}}}
  synchronized(this){if(closed)throw new IOException("SESSION_RELEASED");if(current==null)current=new E13SourceGroup(new E13SourceGroup.Identity(uid,pid,task,++epoch,version));Range r=new Range(current,current.consumer(current.identity,guarded()));ranges.add(r);return r;}
 }
 public void close(){List<HostDataSource> copy;synchronized(this){closed=true;copy=List.copyOf(adapters);}for(HostDataSource a:copy)a.cancel();synchronized(this){if(current!=null)current.closeAll();}}
 public synchronized boolean originalsReturned()throws InterruptedException {boolean done=current==null||current.tryReturn();if(closed&&done){synchronized(ADMITTED){ADMITTED.remove(this);}}return done;}
 public boolean awaitOriginalReturns(long millis)throws InterruptedException,IOException {worker.requireWorker();long end=System.nanoTime()+TimeUnit.MILLISECONDS.toNanos(millis);do{if(originalsReturned())return true;Thread.sleep(2);}while(System.nanoTime()<end);return originalsReturned();}
 public synchronized LeaseRegistry.Snapshot sourceSnapshot(){return current==null?null:current.snapshot();}
 /** Read-only identity of the SAME original generation; no allocation/admission. */
 public synchronized E13SourceGroup.Identity sourceIdentity(){return current==null?null:current.identity;}
 /** Explicit owner recovery ONLY after a completed FAILED close, via the original bridge API.
  * Never called automatically on timeout/pending/unknown; no substitute handle is opened. */
 public void retryObservedFailedClose()throws IOException {worker.requireWorker();List<Range> copy;synchronized(this){copy=List.copyOf(ranges);}for(Range r:copy){if(r.consumer.closeState()==AsyncReadBridge.CloseState.FAILED){try{r.consumer.retryFailedClose().get(5000,TimeUnit.MILLISECONDS);}catch(InterruptedException e){Thread.currentThread().interrupt();throw new IOException("CANCELLED");}catch(ExecutionException|TimeoutException e){throw new IOException("SOURCE_ORIGINAL_PENDING");}}}}
 public static int admittedSources(){return ADMITTED.size();}
}
