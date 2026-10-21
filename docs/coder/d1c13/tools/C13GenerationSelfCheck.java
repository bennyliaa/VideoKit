package com.videokit.spike.c13;
import java.util.concurrent.*;
public final class C13GenerationSelfCheck {
    static int checks;static void yes(boolean value){if(!value)throw new AssertionError("case "+checks);checks++;}
    public static void main(String[] args)throws Exception {
        WorkerGenerations first=new WorkerGenerations(),second=new WorkerGenerations();Object old=new Object(),next=new Object();
        WorkerGenerations.Worker original=first.register(old,27146,99055);yes(original.primary);yes(first.accept(original));original.validated(27146,99055);yes(original.hello());
        yes(first.register(old,27146,99055)==original);yes(first.snapshot().size()==1);
        try{first.register(old,27175,99056);throw new AssertionError();}catch(SecurityException expected){checks++;}
        try{original.validated(27175,99056);throw new AssertionError();}catch(SecurityException expected){checks++;}
        yes(first.died(original));yes(!first.accept(original));
        WorkerGenerations.Worker rebuilt=first.register(next,27175,99056);yes(!rebuilt.primary);yes(first.primary()==original);yes(!first.accept(rebuilt));yes(first.unresolved()==1);
        first.died(original);yes(!rebuilt.dead());yes(!first.allDead());first.bindingClosed();yes(!first.canRelease());
        WorkerGenerations.Worker independent=second.register(new Object(),27200,99057);yes(second.accept(independent));yes(!independent.dead());
        yes(rebuilt.queueStop());yes(!rebuilt.queueStop());rebuilt.stopFinished();yes(!first.canRelease());first.died(rebuilt);yes(first.canRelease());yes(second.accept(independent));
        WorkerGenerations afterCancel=new WorkerGenerations();afterCancel.terminate();WorkerGenerations.Worker late=afterCancel.register(new Object(),3,99060);yes(!late.primary);yes(!afterCancel.accept(late));yes(!afterCancel.canRelease());afterCancel.bindingClosed();yes(!afterCancel.canRelease());afterCancel.died(late);yes(afterCancel.canRelease());
        WorkerGenerations closed=new WorkerGenerations();closed.bindingClosed();WorkerGenerations.Worker terminal=closed.register(new Object(),4,99061);yes(!terminal.primary);yes(!closed.accept(terminal));yes(!closed.canRelease());closed.died(terminal);yes(closed.canRelease());
        WorkerGenerations unknown=new WorkerGenerations();unknown.bindingClosed();yes(!unknown.canRelease());unknown.quarantine();yes(unknown.unresolved()==1);yes(!unknown.canRelease());
        WorkerGenerations overflow=new WorkerGenerations();for(int i=0;i<WorkerGenerations.MAX_WORKERS;i++){WorkerGenerations.Worker w=overflow.register(new Object(),100+i,99100+i);yes(w.primary==(i==0));overflow.died(w);}yes(overflow.snapshot().size()==4);
        try{overflow.register(new Object(),200,99200);throw new AssertionError();}catch(IllegalStateException expected){checks++;}overflow.bindingClosed();yes(!overflow.canRelease());yes(overflow.unresolved()==1);
        // Race cancel against first registration/HELLO validation. Never re-adopt after terminal.
        for(int iteration=0;iteration<20;iteration++){
            WorkerGenerations race=new WorkerGenerations();CountDownLatch ready=new CountDownLatch(1),go=new CountDownLatch(1);Object key=new Object();
            Thread thread=new Thread(()->{ready.countDown();try{go.await();WorkerGenerations.Worker w=race.register(key,7,99070);w.validated(7,99070);}catch(InterruptedException error){throw new AssertionError(error);}});
            thread.start();yes(ready.await(1,TimeUnit.SECONDS));race.terminate();go.countDown();thread.join(1000);yes(!thread.isAlive());WorkerGenerations.Worker w=race.find(key);yes(!race.accept(w));yes(!w.primary);yes(!race.canRelease());race.died(w);race.bindingClosed();yes(race.canRelease());
        }
        System.out.println("PASS "+checks+" generation/duplicate/terminal/overflow/independent-slot counterexamples; actual Binder NOT_RUN");
    }
}
