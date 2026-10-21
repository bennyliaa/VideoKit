package com.videokit.spike.c09;

import java.io.IOException;
import java.util.concurrent.*;

/** READY_UNKNOWN is reconciled using the same task identity, never by reopening output. */
public final class SinkCoordinator {
    public enum State { NEW, WRITING, VALIDATING, READY_PENDING, READY_UNKNOWN, READY, ABORT_PENDING, ABORTED }
    public enum HostState { WRITING, READY, ABORTED, UNKNOWN }
    public static final class Status {public final HostState state;public final String token;public Status(HostState state,String token){this.state=state;this.token=token;}}
    public interface Host {
        CompletionStage<String> markReady(String taskId);
        CompletionStage<Status> query(String taskId);
        CompletionStage<Void> abort(String taskId);
    }
    private final String taskId;private final Host host;private final long timeoutMs;
    private final ThreadPoolExecutor callbacks=new ThreadPoolExecutor(1,1,0,TimeUnit.MILLISECONDS,new ArrayBlockingQueue<>(4),r->{Thread t=new Thread(r,"videokit-d1-sink");t.setDaemon(true);return t;},new ThreadPoolExecutor.AbortPolicy());
    private State state=State.NEW;private boolean cancel;private CompletableFuture<String> readyOperation;private String token;
    private final java.util.concurrent.atomic.AtomicInteger outstanding=new java.util.concurrent.atomic.AtomicInteger();
    public SinkCoordinator(String taskId,Host host,long timeoutMs){this.taskId=taskId;this.host=host;this.timeoutMs=timeoutMs;}
    public synchronized State state(){return state;}
    public synchronized void start()throws IOException{if(state!=State.NEW)throw new IOException("TASK_ALREADY_USED");state=State.WRITING;}
    /** Cancel returns current status. A ready request in flight cannot be rolled back blindly. */
    public synchronized State cancel(){if(state!=State.READY && state!=State.ABORTED)cancel=true;return state;}
    public synchronized void validating()throws IOException{if(state!=State.WRITING)throw new IOException("INVALID_OUTPUT_STATE");state=State.VALIDATING;}
    private <T>CompletableFuture<T> invoke(Callable<CompletionStage<T>> operation){
        CompletableFuture<T> f=new CompletableFuture<>();if(outstanding.incrementAndGet()>8){outstanding.decrementAndGet();f.completeExceptionally(new IOException("OUTPUT_CALLBACK_RESOURCE_EXHAUSTED"));return f;}
        f.whenComplete((v,e)->outstanding.decrementAndGet());try{callbacks.execute(()->{try{operation.call().whenComplete((v,e)->{if(e==null)f.complete(v);else f.completeExceptionally(e);});}catch(Throwable e){f.completeExceptionally(e);}});}catch(RejectedExecutionException e){f.completeExceptionally(new IOException("OUTPUT_CALLBACK_RESOURCE_EXHAUSTED"));}return f;
    }
    private <T>T await(CompletableFuture<T> f)throws IOException{
        try{return f.get(timeoutMs,TimeUnit.MILLISECONDS);}catch(TimeoutException e){throw new IOException("OUTPUT_STATE_UNKNOWN");}
        catch(InterruptedException e){Thread.currentThread().interrupt();throw new IOException("CANCELLED");}
        catch(ExecutionException e){throw new IOException("OUTPUT_CALLBACK_FAILED");}
    }
    public String finalizeReady(boolean structurallyValid)throws IOException{
        boolean abort;
        synchronized(this){if(state!=State.VALIDATING)throw new IOException("INVALID_OUTPUT_STATE");abort=cancel || !structurallyValid;
            if(!abort){state=State.READY_PENDING;readyOperation=invoke(()->host.markReady(taskId));}}
        if(abort){abortBeforeReady();throw new IOException(cancel?"CANCELLED":"OUTPUT_VALIDATION_FAILED");}
        try{String value=await(readyOperation);synchronized(this){token=value;state=State.READY;}return value;}
        catch(IOException e){synchronized(this){if(state==State.ABORTED)throw new IOException("CANCELLED");if(state!=State.READY)state=State.READY_UNKNOWN;}throw new IOException("OUTPUT_READY_UNKNOWN",e);}
    }
    public State reconcile()throws IOException{
        synchronized(this){if(state!=State.READY_UNKNOWN && state!=State.ABORT_PENDING)return state;}
        Status reported=await(invoke(()->host.query(taskId)));
        synchronized(this){
            if(reported.state==HostState.READY && reported.token!=null){token=reported.token;state=State.READY;return state;}
            if(reported.state==HostState.ABORTED){state=State.ABORTED;return state;}
            // WRITING alone is not proof that an old ready RPC can no longer commit.
            // Only retry ready with the same ID; host must atomically arbitrate abort vs ready.
            if(reported.state==HostState.UNKNOWN || reported.state==HostState.READY)return state;
        }
        boolean abort; synchronized(this){abort=cancel;}
        if(abort){abortBeforeReady();return state();}
        try{String value=await(invoke(()->host.markReady(taskId)));synchronized(this){token=value;state=State.READY;}}
        catch(IOException e){throw new IOException("OUTPUT_READY_UNKNOWN",e);}return state();
    }
    public void abortBeforeReady()throws IOException{
        synchronized(this){if(state==State.READY)return;state=State.ABORT_PENDING;}
        try{await(invoke(()->host.abort(taskId)));}
        catch(IOException e){throw new IOException("OUTPUT_ABORT_UNKNOWN",e);}
        // Host abort may lose to a previously accepted ready; query determines the sole terminal.
        Status result=await(invoke(()->host.query(taskId)));
        synchronized(this){if(result.state==HostState.ABORTED)state=State.ABORTED;else if(result.state==HostState.READY && result.token!=null){state=State.READY;token=result.token;}else throw new IOException("OUTPUT_ABORT_UNKNOWN");}
    }
    public synchronized String token(){return token;}
    public void closeExecutor(){callbacks.shutdown();}
}
