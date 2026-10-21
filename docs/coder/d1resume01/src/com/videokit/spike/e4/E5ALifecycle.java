package com.videokit.spike.e4;

import java.util.concurrent.*;
import java.util.function.*;

/** Production Session/instrumentation terminal barrier. One original clock, queue and actual-owner finish. */
public final class E5ALifecycle<T> {
    public static final long PRODUCT_NS=TimeUnit.SECONDS.toNanos(60),CANCEL_NS=TimeUnit.SECONDS.toNanos(30);
    public interface Ticket {void cancel();}
    public interface Scheduler {Ticket after(long nanos,Runnable callback);}
    private final Executor owner;private final Scheduler scheduler;private final LongSupplier clock;
    private final BooleanSupplier resources;private final Supplier<T> report;private final Consumer<String> cancellation;
    private final CompletableFuture<T> future=new CompletableFuture<>();
    private long productAt,cancelAt;private boolean started,initialReturned,queued,ownerReturned,terminal;private int continuations,finishes;
    private Thread originalOwner;private String phase="NEW",terminalReason="";private Ticket productTicket,cancelTicket;
    public E5ALifecycle(Executor owner,Scheduler scheduler,LongSupplier clock,BooleanSupplier resources,Supplier<T> report,Consumer<String> cancellation){this.owner=owner;this.scheduler=scheduler;this.clock=clock;this.resources=resources;this.report=report;this.cancellation=cancellation;}
    public CompletableFuture<T> future(){return future.thenApply(value->value);}
    public synchronized long cancelAt(){return cancelAt;}
    public synchronized long cancelDeadline(){return cancelAt==0?0:cancelAt+CANCEL_NS;}
    public synchronized String phase(){return phase;}
    public synchronized String terminalReason(){return terminalReason;}
    public synchronized int continuations(){return continuations;}
    public synchronized int finishes(){return finishes;}
    public synchronized boolean ownerReturnProven(){return ownerReturned;}
    public void start(){
        synchronized(this){if(started)throw new IllegalStateException("E5A_SINGLE_LIFECYCLE_START");started=true;productAt=clock.getAsLong();phase="RUNNING";}
        Ticket task=scheduler.after(PRODUCT_NS,()->cancel("E4_TOTAL_DEADLINE_PENDING"));synchronized(this){productTicket=task;if(terminal)task.cancel();}
    }
    public void cancel(String reason){
        long left;
        synchronized(this){if(terminal || cancelAt!=0)return;cancelAt=Math.max(1,clock.getAsLong());phase="CANCEL_REQUESTED";left=Math.max(0,cancelAt+CANCEL_NS-clock.getAsLong());}
        // Install the absolute terminal watchdog before any cancellation request can touch platform code.
        Ticket task=scheduler.after(left,this::absoluteDeadline);synchronized(this){cancelTicket=task;if(terminal)task.cancel();}
        cancellation.accept(reason);
    }
    public void initialReturned(boolean success,Runnable continuation,Runnable afterOriginalOwner){
        boolean enqueue;
        synchronized(this){if(initialReturned)throw new IllegalStateException("E5A_INITIAL_OWNER_RETURN_ONCE");initialReturned=true;originalOwner=Thread.currentThread();if(!terminal)phase="INITIAL_RETURNED";enqueue=!success && cancelAt!=0 && clock.getAsLong()<cancelAt+CANCEL_NS && !terminal;}
        if(enqueue){
            synchronized(this){queued=true;phase="CONTINUATION_QUEUED";}
            try{owner.execute(()->{boolean within;synchronized(this){if(Thread.currentThread()!=originalOwner){phase="ORIGINAL_OWNER_THREAD_CHANGED";return;}continuations++;if(!terminal)phase="CONTINUATION_RUNNING";within=cancelAt!=0 && clock.getAsLong()<cancelAt+CANCEL_NS;}try{if(within)continuation.run();}finally{finishOwner(afterOriginalOwner);}});return;}
            catch(RejectedExecutionException rejected){synchronized(this){phase="CONTINUATION_QUEUE_REJECTED";}}
        }
        finishOwner(afterOriginalOwner);
    }
    private void finishOwner(Runnable afterOriginalOwner){
        synchronized(this){if(ownerReturned)throw new IllegalStateException("E5A_ORIGINAL_OWNER_FINISH_ONCE");finishes++;}
        try{afterOriginalOwner.run();}
        finally{synchronized(this){ownerReturned=true;if(!terminal)phase="ORIGINAL_OWNER_RETURNED";}resourcesChanged();}
    }
    public void resourcesChanged(){
        boolean done;synchronized(this){done=ownerReturned && !terminal;}
        if(done && resources.getAsBoolean()){
            boolean productLate;synchronized(this){productLate=cancelAt==0 && clock.getAsLong()-productAt>=PRODUCT_NS;}
            if(productLate)cancel("E4_TOTAL_DEADLINE_PENDING");
            boolean late;synchronized(this){late=cancelAt!=0 && clock.getAsLong()>=cancelAt+CANCEL_NS;}
            complete(late?"ORIGINAL_CANCEL_DEADLINE_PENDING":"ACTUAL_OWNERS_RETURNED");
        }
    }
    private void absoluteDeadline(){
        long left;synchronized(this){if(terminal || cancelAt==0)return;left=cancelAt+CANCEL_NS-clock.getAsLong();}
        if(left>0){Ticket t=scheduler.after(left,this::absoluteDeadline);synchronized(this){cancelTicket=t;if(terminal)t.cancel();}return;}
        resourcesChanged();complete("ORIGINAL_CANCEL_DEADLINE_PENDING");
    }
    private void complete(String reason){
        synchronized(this){if(terminal)return;terminal=true;terminalReason=reason;phase=reason;if(productTicket!=null)productTicket.cancel();if(cancelTicket!=null)cancelTicket.cancel();}
        // No counter or owner is changed here. Deadline completion reports the actual still-pending objects.
        try{future.complete(report.get());}catch(Throwable failure){future.completeExceptionally(failure);}
    }
    /** Common exit gate for positive/negative/cancel/await exception/try-with-resources/@After. */
    public T terminalBeforeExit(){
        cancel("E4_CANCELLED");boolean interrupted=false;
        try{for(;;){try{return future.get();}catch(InterruptedException e){interrupted=true;}catch(ExecutionException impossible){throw new IllegalStateException("E5A_TERMINAL_REPORT_FAILED",impossible);}}}
        finally{if(interrupted)Thread.currentThread().interrupt();}
    }
}
