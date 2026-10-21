package com.videokit.spike.e4;

import com.videokit.spike.c14.*;
import java.io.IOException;
import java.util.*;
import java.util.concurrent.*;

/** One real source generation. Strong keeper is registered before runtime/bridge/open allocation.
 * Uses the production AsyncReadBridge tickets/LeaseRegistry, never a mirrored release counter.
 * Permission here is the trusted host's opaque source capability, not an RCE sandbox.
 */
public final class E13SourceGroup {
    private static final Set<E13SourceGroup> OWNERS=ConcurrentHashMap.newKeySet();
    public static final class Identity {
        public final int uid,pid;public final String task,instance;public final long epoch;
        public Identity(int uid,int pid,String task,long epoch,String instance){this.uid=uid;this.pid=pid;this.task=Objects.requireNonNull(task);this.epoch=epoch;this.instance=Objects.requireNonNull(instance);}
    }
    public final Identity identity;
    private AsyncReadBridge.Runtime runtime;
    private LeaseRegistry registry;
    private long generation;
    private final List<Consumer> consumers=new ArrayList<>();
    private final List<Thread> originalCallers=new ArrayList<>();
    private boolean sealed,returned;
    public E13SourceGroup(Identity identity)throws IOException {
        this.identity=Objects.requireNonNull(identity);E13FinishOwner.admit(()->OWNERS.add(this));
        runtime=new AsyncReadBridge.Runtime();registry=new LeaseRegistry();generation=registry.create();E13ReturnEvents.returned();
    }
    private void require(Identity actual)throws IOException {
        E13FinishOwner.requireAdmission();
        SourceAdmission.require(identity.uid,identity.pid,identity.task,identity.epoch,actual.uid,actual.pid,actual.task,actual.epoch,"SOURCE_IDENTITY_REJECTED");
        if(!identity.instance.equals(actual.instance))throw new IOException("SOURCE_INSTANCE_REJECTED");
        if(sealed || returned || !registry.active(generation))throw new IOException("SESSION_RELEASED");
    }
    public synchronized Consumer consumer(Identity actual,AsyncReadBridge.Provider provider)throws IOException {
        require(actual);if(consumers.size()>=2)throw new IOException("SOURCE_CONSUMER_BUDGET");
        Consumer c=new Consumer(new AsyncReadBridge(runtime,provider,registry,generation,5000));consumers.add(c);return c;
    }
    public final class Consumer implements AutoCloseable {
        private final AsyncReadBridge bridge;private boolean closeRequested;
        private Consumer(AsyncReadBridge b){bridge=b;}
        private void admit(Identity actual)throws IOException {synchronized(E13SourceGroup.this){require(actual);if(closeRequested)throw new IOException("SESSION_RELEASED");}}
        public long open(Identity actual)throws IOException {admit(actual);return bridge.open(0,-1);}
        public int read(Identity actual,byte[] out)throws IOException {admit(actual);return bridge.read(out,0,out.length);}
        public AsyncReadBridge.CloseState closeState(){return bridge.closeState();}
        public CompletableFuture<Void> retryFailedClose(){return bridge.retryFailedClose();}
        public void close(){synchronized(E13SourceGroup.this){if(closeRequested)return;closeRequested=true;bridge.close();if(consumers.stream().allMatch(c->c.closeRequested)){sealed=true;registry.retire(generation);}}}
    }
    /** Keep the actual caller too: Future completion alone is not thread/operation return. */
    public synchronized <T>Future<T> submit(Callable<T> call)throws IOException {
        E13FinishOwner.requireAdmission();
        if(returned || originalCallers.size()>=2)throw new IOException("SOURCE_CALLER_BUDGET");
        FutureTask<T> task=new FutureTask<>(call);Thread thread=new Thread(task,"videokit-e13-source-caller");
        originalCallers.add(thread);thread.start();return task;
    }
    public synchronized LeaseRegistry.Snapshot snapshot(){return registry.query(generation);}
    public synchronized void closeAll(){for(Consumer c:consumers)c.close();if(consumers.isEmpty()){sealed=true;registry.retire(generation);}}
    public synchronized boolean tryReturn()throws InterruptedException {
        if(returned)return true;
        if(registry==null || runtime==null || !sealed || !registry.query(generation).released())return false;
        for(Thread t:originalCallers)if(t.isAlive())return false;
        if(!runtime.finishReturned(registry,generation))return false;
        returned=true;OWNERS.remove(this);E13ReturnEvents.returned();return true;
    }
    public boolean awaitReturn(long millis)throws InterruptedException {
        long end=System.nanoTime()+TimeUnit.MILLISECONDS.toNanos(millis);
        do{if(tryReturn())return true;Thread.sleep(5);}while(System.nanoTime()<end);return false;
    }
    public static int retained(){return OWNERS.size();}
    /** One original finalizer waits on existing registry/threads, never polls or cancels them. */
    public static void awaitOriginalReturns()throws InterruptedException{
        for(E13SourceGroup g:OWNERS){if(g.registry==null||g.runtime==null||g.generation==0)return;g.registry.awaitOriginalRelease(g.generation);for(Thread t:List.copyOf(g.originalCallers))t.join();g.runtime.awaitOriginalTermination(g.registry,g.generation);g.tryReturn();}
    }
    public static String pendingSummary(){
        StringBuilder out=new StringBuilder();for(E13SourceGroup g:OWNERS){LeaseRegistry.Snapshot s=g.snapshot();out.append(" task=").append(g.identity.task).append(" epoch=").append(g.identity.epoch).append(" instance=").append(g.identity.instance).append(" generation=").append(s.generation).append(" consumers=").append(s.consumers).append(" operations=").append(s.operations).append(" failedCloses=").append(s.failedCloses);}
        return out.toString();
    }
    public static boolean canFinish(){
        for(E13SourceGroup g:OWNERS)try{g.tryReturn();}catch(InterruptedException e){Thread.currentThread().interrupt();return false;}
        return OWNERS.isEmpty();
    }
}
