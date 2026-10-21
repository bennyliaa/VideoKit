package com.videokit.fixturetool;
import java.util.Map;
import java.util.function.LongSupplier;

/** Body deadline for the one tool worker. Completion is the LAST controlled
 * statement after cleanup, not OS thread exit. Same-thread join is separate. */
final class WorkerDeadline {
    private final LongSupplier clock;
    private final long duration;
    private Thread original;
    private long start,completed,observed,completionElapsed,lastElapsed;
    private boolean begun,bodyComplete,unknown,invalidClock,joined;
    WorkerDeadline(LongSupplier clock,long durationNanos){
        if(clock==null||durationNanos<=0||durationNanos>Long.MAX_VALUE/4)throw new IllegalArgumentException("DEADLINE_RANGE");
        this.clock=clock;duration=durationNanos;
    }
    synchronized void begin(Thread worker){
        if(begun||worker==null||worker.getState()!=Thread.State.NEW)throw new IllegalStateException("EXACT_NEW_WORKER_REQUIRED");
        original=worker;start=clock.getAsLong();begun=true;
    }
    private long elapsed(long now){long delta=now-start;if(delta<0||delta<lastElapsed){invalidClock=true;unknown=true;}else lastElapsed=delta;return delta;}
    synchronized void bodyCompletedByOriginal(){
        if(!begun||Thread.currentThread()!=original||bodyComplete)throw new IllegalStateException("SAME_ORIGINAL_COMPLETION_REQUIRED");
        completed=clock.getAsLong();completionElapsed=elapsed(completed);bodyComplete=true;
        if(completionElapsed<0||completionElapsed>=duration)unknown=true;
    }
    synchronized boolean observeUnknown(){
        if(!begun)throw new IllegalStateException("WORKER_NOT_BEGUN");observed=elapsed(clock.getAsLong());
        if(!bodyComplete&&observed>=duration)unknown=true;return unknown;
    }
    synchronized void forceUnknown(){unknown=true;}
    void awaitBodyWindow()throws InterruptedException {
        if(Thread.currentThread()==original)throw new IllegalStateException("EXTERNAL_WAITER_REQUIRED");
        for(;;){long left;synchronized(this){if(observeUnknown()||bodyComplete)return;if(original.getState()==Thread.State.TERMINATED){unknown=true;return;}left=duration-observed;}
            // Timed join return is not itself a deadline decision.
            original.join(left/1000000L,(int)(left%1000000L));}
    }
    void joinSameOriginal()throws InterruptedException {
        Thread worker;synchronized(this){if(!begun||Thread.currentThread()==original)throw new IllegalStateException("EXTERNAL_ORIGINAL_JOIN_REQUIRED");worker=original;}
        worker.join();synchronized(this){joined=true;observeUnknown();}
    }
    synchronized boolean timelyAndJoined(){return bodyComplete&&joined&&!unknown;}
    synchronized Map<String,Object> receipt(){return ReceiptJson.map("deadlineNanos",duration,"startNanoTime",start,"completionPointRecordedBySameWorker",bodyComplete,
        "bodyCompletedNanoTime",bodyComplete?completed:null,"completionElapsedNanos",bodyComplete?completionElapsed:null,"observerElapsedNanos",observed,
        "deadlineUnknownSticky",unknown,"invalidMonotonicRange",invalidClock,"sameOriginalExternallyJoined",joined,"timelyBodyAndOriginalJoin",timelyAndJoined(),
        "equalDeadlineIsLate",true,"completionPointContract","LAST_DRIVER_CONTROLLED_STATEMENT_AFTER_CLEANUP_NOT_OS_THREAD_EXIT");}
}
