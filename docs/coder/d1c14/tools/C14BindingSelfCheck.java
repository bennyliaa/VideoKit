package com.videokit.spike.c14;
import java.util.concurrent.*;
public final class C14BindingSelfCheck {
    static int checks;static void yes(boolean value){if(!value)throw new AssertionError("case "+checks);checks++;}
    public static void main(String[] args)throws Exception {
        BindingRevocation unknown=new BindingRevocation();unknown.beginBind();unknown.returned(true);yes(unknown.request());yes(unknown.queue());yes(unknown.snapshot().pending);yes(!unknown.queue());unknown.finished(true,"UNBOUND_WAIT_DEATH");yes(unknown.snapshot().closed);yes(!unknown.request());yes(!unknown.queue());
        WorkerGenerations noIdentity=new WorkerGenerations();noIdentity.bindingClosed();yes(!noIdentity.allDead());yes(!noIdentity.canRelease());
        CpuLifecycle lifecycle=new CpuLifecycle();lifecycle.requestBind();lifecycle.bindReturned(true);lifecycle.sourceReleased(true);yes(!lifecycle.releaseSlot());yes(!lifecycle.snapshot().actualDeath);yes(!lifecycle.snapshot().noWorkerProven());
        BindingRevocation late=new BindingRevocation();yes(late.request());yes(!late.queue());late.beginBind();yes(!late.queue());late.returned(true);yes(late.queue());late.finished(true,"UNBOUND_WAIT_DEATH");yes(late.snapshot().closed);yes(late.snapshot().attempts==1);
        BindingRevocation pending=new BindingRevocation();pending.beginBind();pending.request();yes(!pending.queue());yes(pending.snapshot().inFlight);pending.returnedUnknown();yes(pending.queue());pending.finished(false,"UNBIND_FAILED");yes(!pending.snapshot().closed);yes(pending.snapshot().uncertain);yes(!pending.request());
        for(int attempt=2;attempt<=3;attempt++){yes(pending.queue());yes(pending.snapshot().attempts==attempt);yes(!pending.queue());pending.finished(false,"QUEUE_OR_UNBIND_FAILED");}yes(!pending.queue());yes(!pending.snapshot().closed);
        BindingRevocation rejected=new BindingRevocation();rejected.beginBind();rejected.returned(false);rejected.request();yes(!rejected.queue());yes(!rejected.snapshot().closed);
        BindingRevocation recover=new BindingRevocation();recover.beginBind();recover.returned(true);recover.request();yes(recover.queue());recover.finished(false,"UNBIND_FAILED");yes(!recover.snapshot().closed);yes(recover.queue());recover.finished(true,"UNBOUND_WAIT_DEATH");yes(recover.snapshot().closed);yes(!recover.queue());
        // An unresolved STOP executor cannot consume the separate binding-revocation executor.
        ExecutorService stop=Executors.newSingleThreadExecutor(),unbind=Executors.newSingleThreadExecutor();CountDownLatch blocked=new CountDownLatch(1),release=new CountDownLatch(1);
        try{Future<?> first=stop.submit(()->{blocked.countDown();try{release.await();}catch(InterruptedException error){Thread.currentThread().interrupt();}});yes(blocked.await(1,TimeUnit.SECONDS));BindingRevocation separate=new BindingRevocation();separate.beginBind();separate.returned(true);separate.request();yes(separate.queue());unbind.submit(()->separate.finished(true,"UNBOUND_WAIT_DEATH")).get(1,TimeUnit.SECONDS);yes(separate.snapshot().closed);yes(!first.isDone());release.countDown();first.get(1,TimeUnit.SECONDS);checks++;}
        finally{release.countDown();stop.shutdownNow();unbind.shutdownNow();}
        System.out.println("PASS "+checks+" bind/cancel/late-return/failed-unbind/unknown-retention counterexamples; Android unbind NOT_RUN");
    }
}
