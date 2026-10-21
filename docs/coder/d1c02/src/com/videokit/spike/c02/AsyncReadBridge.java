package com.videokit.spike.c02;

import java.io.IOException;
import java.util.Objects;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicBoolean;

/** D1 worker bridge, with bounded invocation threads and actual completion accounting. */
public final class AsyncReadBridge implements AutoCloseable {
    public static final int MAX_READ=65536;
    public static final class Cancellation {private final AtomicBoolean value=new AtomicBoolean();public boolean cancelled(){return value.get();}void cancel(){value.set(true);}}
    public interface Handle {
        Long length();
        CompletionStage<Integer> readAt(long position,byte[] target,int offset,int length,Cancellation cancellation);
        CompletionStage<Void> closeAsync();
    }
    public interface Provider {CompletionStage<Handle> open(Cancellation cancellation);}
    public static final class Runtime implements AutoCloseable {
        final ThreadPoolExecutor io=new ThreadPoolExecutor(2,2,0,TimeUnit.MILLISECONDS,new ArrayBlockingQueue<>(16),r->{Thread t=new Thread(r,"videokit-d1-io");t.setDaemon(true);return t;},new ThreadPoolExecutor.AbortPolicy());
        // Cleanup has its own bounded executor so blocked reads do not prevent cooperative close.
        final ThreadPoolExecutor cleanup=new ThreadPoolExecutor(2,2,0,TimeUnit.MILLISECONDS,new ArrayBlockingQueue<>(16),r->{Thread t=new Thread(r,"videokit-d1-close");t.setDaemon(true);return t;},new ThreadPoolExecutor.AbortPolicy());
        public void close(){io.shutdownNow();cleanup.shutdownNow();}
    }
    private final Runtime runtime;private final Provider provider;private final LeaseRegistry registry;
    private final long generation,timeoutMs;private final Cancellation token=new Cancellation();
    private final CompletableFuture<Handle> opened=new CompletableFuture<>();
    private final CompletableFuture<Object> cancelled=new CompletableFuture<>();
    private Handle handle;private boolean closed,reading,openStarted;private long position,remaining=-1;
    public AsyncReadBridge(Runtime runtime,Provider provider,LeaseRegistry registry,long generation,long timeoutMs)throws IOException{
        if(timeoutMs<=0)throw new IllegalArgumentException("timeout");
        this.runtime=runtime;this.provider=provider;this.registry=registry;this.generation=generation;this.timeoutMs=timeoutMs;registry.acquire(generation);
    }
    private <T> CompletableFuture<T> invoke(Callable<CompletionStage<T>> call,boolean closing){
        CompletableFuture<T> result=new CompletableFuture<>();try{registry.begin(generation,closing);}catch(IOException e){result.completeExceptionally(e);return result;}
        try{(closing?runtime.cleanup:runtime.io).execute(()->{
            try{if(!closing && (token.cancelled() || !registry.active(generation)))throw new IOException("CANCELLED");CompletionStage<T> stage=Objects.requireNonNull(call.call());stage.whenComplete((value,error)->{
                try{if(error==null)result.complete(value);else result.completeExceptionally(error);}finally{registry.end(generation);}
            });}catch(Throwable e){try{result.completeExceptionally(e);}finally{registry.end(generation);}}
        });}catch(RejectedExecutionException e){registry.end(generation);result.completeExceptionally(new IOException("SOURCE_RESOURCE_EXHAUSTED"));}
        return result;
    }
    private <T>T await(CompletableFuture<T> future)throws IOException{
        try{@SuppressWarnings("unchecked") T result=(T)CompletableFuture.anyOf(future,cancelled).get(timeoutMs,TimeUnit.MILLISECONDS);return result;}
        catch(TimeoutException e){close();throw new IOException("SOURCE_TIMEOUT");}
        catch(InterruptedException e){Thread.currentThread().interrupt();close();throw new IOException("CANCELLED");}
        catch(ExecutionException e){Throwable cause=e.getCause();while(cause instanceof CompletionException && cause.getCause()!=null)cause=cause.getCause();
            if(cause instanceof java.io.FileNotFoundException || cause instanceof java.nio.file.NoSuchFileException)throw new IOException("SOURCE_NOT_FOUND");
            if(cause instanceof java.nio.file.AccessDeniedException || cause instanceof SecurityException)throw new IOException("SOURCE_PERMISSION_DENIED");
            if(cause instanceof IOException){String code=cause.getMessage();if(java.util.Set.of("CANCELLED","SESSION_RELEASED","SOURCE_DISCONNECTED","SOURCE_TIMEOUT","SOURCE_RESOURCE_EXHAUSTED","INVALID_READ_RESULT","SUBTITLE_SIZE_EXCEEDED").contains(code==null?"":code))throw new IOException(code);throw new IOException("SOURCE_IO_FAILED");}
            throw new IOException("INTERNAL_ERROR_REDACTED");}
    }
    private void closeHandle(Handle h){
        invoke(h::closeAsync,true).whenComplete((v,e)->{if(e!=null)registry.closeFailed(generation);});
    }
    public long open(long offset,long requested)throws IOException{
        synchronized(this){
            if(closed || !registry.active(generation))throw new IOException("SESSION_RELEASED");
            if(openStarted)throw new IOException("SOURCE_ALREADY_OPEN");
            if(offset<0 || requested< -1)throw new IOException("INVALID_RANGE");
            openStarted=true;
            invoke(()->provider.open(token),false).whenComplete((h,e)->{
                synchronized(AsyncReadBridge.this){
                    if(e!=null){opened.completeExceptionally(e);return;}
                    if(h==null){opened.completeExceptionally(new IOException("INVALID_READ_RESULT"));return;}
                    if(closed || !registry.active(generation)){closeHandle(h);opened.completeExceptionally(new IOException("SESSION_RELEASED"));}
                    else{handle=h;opened.complete(h);}
                }
            });
        }
        Handle h=await(opened);Long size=await(invoke(()->CompletableFuture.completedFuture(h.length()),false));
        synchronized(this){
            if(closed || !registry.active(generation))throw new IOException("SESSION_RELEASED");
            if(size!=null && (size<0 || offset>size)){close();throw new IOException("INVALID_RANGE");}
            position=offset;remaining=size==null?requested:(requested<0?size-offset:Math.min(requested,size-offset));return remaining;
        }
    }
    public int read(byte[] target,int offset,int length)throws IOException{
        Objects.checkFromIndexSize(offset,length,target.length);final Handle current;final int count;final long at;
        synchronized(this){
            if(closed || !registry.active(generation))throw new IOException("SESSION_RELEASED");
            if(handle==null)throw new IOException("SOURCE_NOT_OPEN");
            if(length==0)return 0;if(remaining==0)return -1;if(reading)throw new IOException("READ_IN_FLIGHT");
            reading=true;current=handle;at=position;count=(int)Math.min(MAX_READ,Math.min(length,remaining<0?Long.MAX_VALUE:remaining));
        }
        byte[] privateBuffer=new byte[count];
        CompletableFuture<Integer> operation=invoke(()->current.readAt(at,privateBuffer,0,count,token),false);
        try{int n=await(operation);
        synchronized(this){
            if(closed || !registry.active(generation))throw new IOException("CANCELLED");
            if(n==0 || n< -1 || n>count)throw new IOException("INVALID_READ_RESULT");
            if(n>0){long next;try{next=Math.addExact(position,n);}catch(ArithmeticException e){throw new IOException("INVALID_RANGE");}
                System.arraycopy(privateBuffer,0,target,offset,n);position=next;if(remaining>=0)remaining-=n;}
            return n;
        }}finally{synchronized(this){reading=false;}}
    }
    public synchronized void close(){
        if(closed)return;closed=true;token.cancel();
        cancelled.completeExceptionally(new IOException("CANCELLED"));
        // Wake callers independently of a noncooperative provider; ownership remains in registry.
        opened.completeExceptionally(new IOException("CANCELLED"));
        if(handle!=null)closeHandle(handle);
        registry.releaseConsumer(generation);
    }
    public long generation(){return generation;}
}
