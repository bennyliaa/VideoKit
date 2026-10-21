package com.videokit.spike.c11;
import java.io.IOException;
import java.util.concurrent.*;
public final class C11LifecycleSelfCheck {
    static int checks;
    static void yes(boolean value){if(!value)throw new AssertionError("case "+checks);checks++;}
    interface Work{void run()throws Exception;}
    static void security(Work work)throws Exception {try{work.run();throw new AssertionError("unauthorized accepted");}catch(SecurityException expected){checks++;}}
    public static void main(String[] args)throws Exception {
        CpuControlRules.synchronous(0);checks++;security(()->CpuControlRules.synchronous(1));
        CpuControlRules.owner(10221,20000,10221,20000);checks++;
        security(()->CpuControlRules.owner(10221,20000,10221,0));security(()->CpuControlRules.owner(10221,20000,10221,20001));security(()->CpuControlRules.owner(10221,20000,10222,20000));security(()->CpuControlRules.owner(-1,-1,10221,20000));
        CpuControlRules.session("task",7,"task",7);checks++;security(()->CpuControlRules.session("task",7,"other",7));security(()->CpuControlRules.session("task",7,"task",8));security(()->CpuControlRules.session(null,7,"task",7));
        yes(CpuControlRules.errorCode(1).equals("CPU_CONTROL_AUTH_REJECTED"));yes(CpuControlRules.errorCode(999).equals("CPU_CONTROL_ERROR_PROTOCOL"));
        yes(CpuLifecycle.environmentReady(0,true,0,true,true,true,false));yes(CpuLifecycle.environmentReady(1,true,1,true,true,true,false));
        for(int disabled:new int[]{2,3,4})yes(!CpuLifecycle.environmentReady(disabled,true,0,true,true,true,false));
        yes(!CpuLifecycle.environmentReady(0,false,0,true,true,true,false));yes(!CpuLifecycle.environmentReady(0,true,2,true,true,true,false));yes(!CpuLifecycle.environmentReady(0,true,0,false,true,true,false));yes(!CpuLifecycle.environmentReady(0,true,0,true,false,true,false));yes(!CpuLifecycle.environmentReady(0,true,0,true,true,false,false));yes(!CpuLifecycle.environmentReady(0,true,0,true,true,true,true));
        CpuLifecycle never=new CpuLifecycle();never.sourceReleased(true);yes(never.snapshot().noWorkerProven());yes(!never.snapshot().actualDeath);yes(never.releaseSlot());yes(!never.releaseSlot());
        CpuLifecycle rejected=new CpuLifecycle();rejected.requestBind();rejected.bindReturned(false);rejected.sourceReleased(true);yes(rejected.releaseSlot());yes(!rejected.snapshot().actualDeath);
        CpuLifecycle unknown=new CpuLifecycle();unknown.requestBind();unknown.sourceReleased(true);yes(!unknown.releaseSlot());unknown.bindReturned(true);yes(!unknown.releaseSlot());
        CpuLifecycle task=new CpuLifecycle();task.requestBind();task.connected();task.bindReturned(true);yes(task.snapshot().binding==CpuLifecycle.Binding.CONNECTED);task.identity();task.started();task.sourceReleased(true);
        yes(task.queueStop());yes(!task.queueStop());task.callStarted();yes(!task.releaseSlot());task.stopFinished("ACKED_WAIT_DEATH",true);yes(!task.releaseSlot());task.death();yes(!task.releaseSlot());task.callFinished();yes(task.releaseSlot());yes(task.snapshot().actualDeath);yes(task.snapshot().stopAck);
        CpuLifecycle lost=new CpuLifecycle();lost.requestBind();lost.bindReturned(true);lost.sourceReleased(true);yes(lost.queueStop());lost.stopFinished("ACK_UNKNOWN",false);yes(!lost.releaseSlot());lost.death();yes(lost.releaseSlot());yes(!lost.snapshot().stopAck);
        CpuLifecycle pending=new CpuLifecycle();pending.requestBind();pending.connected();pending.death();pending.sourceReleased(false);yes(!pending.releaseSlot());pending.sourceReleased(true);yes(pending.releaseSlot());
        CpuLifecycle retry=new CpuLifecycle();retry.requestBind();retry.connected();for(int i=0;i<3;i++){yes(retry.queueStop());yes(!retry.queueStop());retry.stopFinished("QUEUE_OR_REPLY_FAILED",false);}yes(!retry.queueStop());yes(retry.snapshot().stopAttempts==3);yes(!retry.releaseSlot());
        retry.firstFailure("CPU_HELLO_REJECTED","HELLO");retry.firstFailure("CPU_CANCELLED","CANCEL");yes(retry.snapshot().firstCode.equals("CPU_HELLO_REJECTED"));yes(retry.snapshot().firstPhase.equals("HELLO"));
        IOException original=new IOException("CPU_HELLO_REJECTED");AssertionError cleanup=new AssertionError("CPU_CLEANUP_UNPROVEN");
        try{CpuDiagnostics.preserving(()->{throw original;},()->{throw cleanup;});throw new AssertionError("primary lost");}catch(Throwable result){yes(result==original);yes(result.getSuppressed()[0]==cleanup);}
        try{CpuDiagnostics.preserving(()->{},()->{throw cleanup;});throw new AssertionError("cleanup lost");}catch(Throwable result){yes(result==cleanup);}
        CpuDiagnostics.Failure hello=CpuDiagnostics.failure("CPU_HELLO_FAILED","HELLO",new ExecutionException(new IOException("CPU_CONTROL_AUTH_REJECTED")));
        yes(hello.code.equals("CPU_CONTROL_AUTH_REJECTED"));yes(hello.phase.equals("HELLO"));yes(hello.category.equals("IO"));
        CpuDiagnostics.Failure privateCause=CpuDiagnostics.failure("CPU_BIND_CALL_FAILED","BIND",new SecurityException("/private/credential-secret"));yes(privateCause.code.equals("CPU_BIND_CALL_FAILED"));yes(privateCause.category.equals("SECURITY"));yes(privateCause.getCause()==null);yes(!privateCause.toString().contains("credential"));
        yes(CpuDiagnostics.failure("CPU_CONNECT_TIMEOUT","CONNECT",new TimeoutException()).category.equals("TIMEOUT"));
        yes(CpuDiagnostics.workerCategory(new UnsatisfiedLinkError())==1);yes(CpuDiagnostics.workerCategory(new ExceptionInInitializerError())==1);yes(CpuDiagnostics.workerCategory(new IOException("CPU_NATIVE_REJECTED"))==2);yes(CpuDiagnostics.workerCategory(new IOException("CPU_EVENT"))==3);yes(CpuDiagnostics.workerCategory(new AssertionError())==4);
        // Two bounded executors: a physically pending STOP cannot occupy the normal command executor.
        ExecutorService stop=Executors.newFixedThreadPool(1),rpc=Executors.newFixedThreadPool(1);CountDownLatch entered=new CountDownLatch(1),release=new CountDownLatch(1);
        try{Future<?> first=stop.submit(()->{entered.countDown();try{release.await();}catch(InterruptedException error){Thread.currentThread().interrupt();}});yes(entered.await(1,TimeUnit.SECONDS));yes(rpc.submit(()->42).get(1,TimeUnit.SECONDS)==42);yes(!first.isDone());release.countDown();first.get(1,TimeUnit.SECONDS);checks++;}finally{release.countDown();stop.shutdownNow();rpc.shutdownNow();}
        System.out.println("PASS "+checks+" lifecycle/auth/primary-cleanup/environment/executor counterexamples; Android NOT_RUN");
    }
}
