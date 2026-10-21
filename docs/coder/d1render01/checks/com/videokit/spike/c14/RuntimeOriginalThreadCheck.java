package com.videokit.spike.c14;
import java.util.concurrent.*;
/** Real production executor: TERMINATED precedes Thread's uncaught-exception tail. */
public final class RuntimeOriginalThreadCheck {
    public static void run()throws Exception {
        AsyncReadBridge.Runtime runtime=new AsyncReadBridge.Runtime();LeaseRegistry registry=new LeaseRegistry();long generation=registry.create();registry.retire(generation);
        CountDownLatch entered=new CountDownLatch(1),throwNow=new CountDownLatch(1),tailEntered=new CountDownLatch(1),tailRelease=new CountDownLatch(1);
        runtime.io.execute(()->{
            Thread.currentThread().setUncaughtExceptionHandler((same,error)->{tailEntered.countDown();try{tailRelease.await();}catch(InterruptedException e){Thread.currentThread().interrupt();}});
            entered.countDown();try{throwNow.await();}catch(InterruptedException e){Thread.currentThread().interrupt();}
            throw new IllegalStateException("FINITE_ORIGINAL_WORKER_TAIL");
        });
        try{
            if(!entered.await(1,TimeUnit.SECONDS))throw new AssertionError("original worker entered");runtime.io.shutdown();throwNow.countDown();
            if(!tailEntered.await(1,TimeUnit.SECONDS))throw new AssertionError("original uncaught tail entered");
            if(!runtime.io.isTerminated())throw new AssertionError("real executor must already report TERMINATED");
            if(runtime.finishReturned(registry,generation))throw new AssertionError("TERMINATED cannot substitute for live original thread return");
        }finally{throwNow.countDown();tailRelease.countDown();runtime.awaitOriginalTermination(registry,generation);}
        if(!runtime.finishReturned(registry,generation))throw new AssertionError("same original threads joined");
        System.out.println("PASS real_executor_terminated_original_thread_still_alive_then_joined");
    }
    private RuntimeOriginalThreadCheck(){}
}
