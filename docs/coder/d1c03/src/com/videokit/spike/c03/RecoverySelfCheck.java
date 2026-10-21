package com.videokit.spike.c03;

import java.io.*;
import java.nio.channels.*;
import java.nio.file.*;
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.*;

/** JVM-only protocol tests, including two processes created and terminated by this test. */
public final class RecoverySelfCheck {
    private static int passed;
    private static void check(boolean value,String label){if(!value)throw new AssertionError(label);passed++;System.out.println("PASS "+label);}
    private interface Checked {void run()throws Exception;}
    private static void error(String code,Checked action)throws Exception{try{action.run();throw new AssertionError("expected "+code);}catch(IOException e){check(code.equals(e.getMessage()),code);}}
    private static AsyncReadBridge.Handle failOnce(AtomicInteger calls){return new AsyncReadBridge.Handle(){
        public Long length(){return 1L;}public CompletionStage<Integer>readAt(long p,byte[] b,int o,int n,AsyncReadBridge.Cancellation c){return CompletableFuture.completedFuture(-1);}
        public CompletionStage<Void>closeAsync(){return calls.incrementAndGet()==1?HostFixtures.failed(new IOException("CLOSE_FAILED")):CompletableFuture.completedFuture(null);}
    };}
    private static Process child(String mode,Path directory,String task,String epoch)throws IOException {
        String java=Path.of(System.getProperty("java.home"),"bin","java.exe").toString();if(!Files.exists(Path.of(java)))java=Path.of(System.getProperty("java.home"),"bin","java").toString();
        return new ProcessBuilder(java,"-cp",System.getProperty("java.class.path"),RecoverySelfCheck.class.getName(),mode,directory.toString(),task,epoch).redirectErrorStream(true).start();
    }
    private static String line(Process process)throws Exception {
        ExecutorService reader=Executors.newSingleThreadExecutor(r->{Thread t=new Thread(r);t.setDaemon(true);return t;});
        try{return reader.submit(()->new BufferedReader(new InputStreamReader(process.getInputStream())).readLine()).get(10,TimeUnit.SECONDS);}finally{reader.shutdownNow();}
    }
    private static FencedTask recoverOwner(Path directory,String task)throws Exception {
        long deadline=System.nanoTime()+TimeUnit.SECONDS.toNanos(3);
        while(true)try{return new FencedTask(directory,task,d->{});}catch(IOException e){if(!"OUTPUT_OWNER_BUSY".equals(e.getMessage()) || System.nanoTime()>=deadline)throw e;Thread.sleep(20);}
    }
    private static FencedTask.State recoverAbort(FencedTask task)throws Exception {
        long deadline=System.nanoTime()+TimeUnit.SECONDS.toNanos(3);
        while(true)try{return task.abort();}catch(IOException e){if(!"OUTPUT_WORKER_ACTIVE".equals(e.getMessage()) || System.nanoTime()>=deadline)throw e;Thread.sleep(20);}
    }
    public static void main(String[] args)throws Exception {
        if(args[0].equals("child-host")){
            try(FencedTask task=new FencedTask(Path.of(args[1]),args[2],d->{})){String epoch=task.issue();System.out.println(epoch);System.out.flush();new CountDownLatch(1).await();}return;
        }
        if(args[0].equals("child-worker")){
            Path directory=Path.of(args[1]);String task=args[2];
            try(FileInputStream lease=new FileInputStream(directory.resolve(task+".lease").toFile());FencedTask.WorkerLease hold=FencedTask.WorkerLease.acquire(lease.getChannel(),args[3]);RandomAccessFile output=new RandomAccessFile(directory.resolve(task+".mp4").toFile(),"rw")){
                output.write(new byte[]{1,2,3,4});output.getFD().sync();System.out.println("WORKER_HOLDS_REAL_OUTPUT_AND_LEASE");System.out.flush();new CountDownLatch(1).await();
            }return;
        }
        Path directory=Path.of(args[0]);Files.createDirectories(directory);LeaseRegistry leases=new LeaseRegistry();
        try(AsyncReadBridge.Runtime runtime=new AsyncReadBridge.Runtime()) {
            long generation=leases.create();AtomicInteger firstCalls=new AtomicInteger(),secondCalls=new AtomicInteger();
            AsyncReadBridge first=new AsyncReadBridge(runtime,c->CompletableFuture.completedFuture(failOnce(firstCalls)),leases,generation,1000);
            AsyncReadBridge second=new AsyncReadBridge(runtime,c->CompletableFuture.completedFuture(failOnce(secondCalls)),leases,generation,1000);
            first.open(0,-1);second.open(0,-1);first.close();second.close();leases.retire(generation);
            long stop=System.nanoTime()+TimeUnit.SECONDS.toNanos(2);while(leases.query(generation).failedCloses<2 && System.nanoTime()<stop)Thread.sleep(5);
            check(leases.query(generation).failedCloses==2,"two failed handles retained independently");
            first.retryFailedClose().get(1,TimeUnit.SECONDS);check(!leases.awaitReleased(generation,50) && leases.query(generation).failedCloses==1,"one recovered close cannot erase another failure");
            second.retryFailedClose().get(1,TimeUnit.SECONDS);check(leases.awaitReleased(generation,1000),"explicit successful retries allow actual SourceReleased");
            long exhausted=leases.create();AtomicInteger attempts=new AtomicInteger();AsyncReadBridge permanent=new AsyncReadBridge(runtime,c->CompletableFuture.completedFuture(new AsyncReadBridge.Handle(){
                public Long length(){return 0L;}public CompletionStage<Integer>readAt(long p,byte[] b,int o,int n,AsyncReadBridge.Cancellation c){return CompletableFuture.completedFuture(-1);}
                public CompletionStage<Void>closeAsync(){attempts.incrementAndGet();return HostFixtures.failed(new IOException("FAIL"));}
            }),leases,exhausted,1000);
            permanent.open(0,-1);permanent.close();leases.retire(exhausted);while(permanent.closeState()==AsyncReadBridge.CloseState.PENDING)Thread.sleep(5);
            for(int i=0;i<3;i++)try{permanent.retryFailedClose().get(1,TimeUnit.SECONDS);}catch(ExecutionException expected){}
            check(attempts.get()==3 && permanent.closeState()==AsyncReadBridge.CloseState.EXHAUSTED && !leases.query(exhausted).released(),"retry budget is initial plus two, exhaustion remains unreleased");
            // Saturate BOTH IO invocation threads and their bounded queue; cancelled queued calls are drained later.
            long saturated=leases.create();CountDownLatch entered=new CountDownLatch(2),unblock=new CountDownLatch(1);List<AsyncReadBridge> bridges=new ArrayList<>();ExecutorService callers=Executors.newFixedThreadPool(21);
            List<Future<String>> results=new ArrayList<>();
            try {
                for(int i=0;i<21;i++){AsyncReadBridge b=new AsyncReadBridge(runtime,c->{entered.countDown();try{unblock.await();}catch(InterruptedException e){Thread.currentThread().interrupt();}return CompletableFuture.completedFuture(HostFixtures.memory(new byte[1]));},leases,saturated,5000);bridges.add(b);results.add(callers.submit(()->{try{b.open(0,-1);return "OPENED";}catch(IOException e){return e.getMessage();}}));}
                check(entered.await(1,TimeUnit.SECONDS),"noncooperative invocations occupy both bounded IO threads");
                long deadline=System.nanoTime()+TimeUnit.SECONDS.toNanos(2);while(runtime.io.getQueue().size()<16 && System.nanoTime()<deadline)Thread.sleep(5);
                check(runtime.io.getPoolSize()==2 && runtime.io.getQueue().size()==16,"IO executor never expands when queue fills");
                for(AsyncReadBridge b:bridges)b.close();leases.retire(saturated);check(!leases.awaitReleased(saturated,20),"timeout/cancel cannot release still-blocked invocations");
                unblock.countDown();check(leases.awaitReleased(saturated,3000),"late invocations and cancelled queued work actually drain");
                int rejected=0;for(Future<String> r:results)if(r.get(1,TimeUnit.SECONDS).equals("SOURCE_RESOURCE_EXHAUSTED"))rejected++;
                check(rejected>0,"full queue returns stable bounded rejection");
            }finally{unblock.countDown();callers.shutdownNow();}
        }
        String id=UUID.randomUUID().toString(),token;
        final String firstId=id;
        try(FencedTask task=new FencedTask(directory,id,d->{})) {
            String epoch=task.issue();error("OUTPUT_OWNER_BUSY",()->new FencedTask(directory,firstId,d->{}));
            try(FileInputStream lease=new FileInputStream(task.authorizedLease().toFile());FencedTask.WorkerLease hold=FencedTask.WorkerLease.acquire(lease.getChannel(),epoch);FileOutputStream output=new FileOutputStream(task.authorizedOutput().toFile())){
                output.write(new byte[]{1,2,3});output.flush();error("OUTPUT_WORKER_ACTIVE",task::abort);check(task.query()==FencedTask.State.ABORT_PENDING && Files.exists(task.authorizedOutput()),"worker lease prevents deletion/ready while writer is live");
            }
            check(task.abort()==FencedTask.State.ABORTED && !Files.exists(task.authorizedOutput()),"worker close permits fenced abort and target removal");
            try(FileInputStream late=new FileInputStream(task.authorizedLease().toFile())){error("OUTPUT_FENCED",()->FencedTask.WorkerLease.acquire(late.getChannel(),epoch));}
        }
        id=UUID.randomUUID().toString();
        try(FencedTask task=new FencedTask(directory,id,d->{})){String epoch=task.issue();Files.write(task.authorizedOutput(),new byte[]{1,2,3});error("OUTPUT_NOT_READY",()->task.ready(epoch,false));token=task.ready(epoch,true);check(task.abort()==FencedTask.State.READY,"accepted ready cannot be rolled back by cancel");}
        try(FencedTask recovered=new FencedTask(directory,id,d->{})){check(recovered.query()==FencedTask.State.READY && recovered.token().equals(token),"cross-owner durable READY recovers same token");}
        // Actual two test-created JVMs: forcibly terminate only Process instances owned by this harness.
        String killedId=UUID.randomUUID().toString();Process host=null,worker=null;
        try {
            host=child("child-host",directory,killedId,"unused");String epoch=line(host);check(epoch!=null && epoch.matches("[0-9a-f-]{36}"),"actual child host persisted grant");
            worker=child("child-worker",directory,killedId,epoch);check("WORKER_HOLDS_REAL_OUTPUT_AND_LEASE".equals(line(worker)),"actual child worker owns output FD and lease lock");
            host.destroyForcibly();check(host.waitFor(5,TimeUnit.SECONDS),"only test-created host process terminated");
            try(FencedTask newOwner=recoverOwner(directory,killedId)){
                error("OUTPUT_WORKER_ACTIVE",newOwner::abort);check(Files.exists(newOwner.authorizedOutput()),"new owner does not delete orphan worker's open output");
                worker.destroyForcibly();check(worker.waitFor(5,TimeUnit.SECONDS),"only test-created worker terminated, OS releases its FD/lock");
                check(recoverAbort(newOwner)==FencedTask.State.ABORTED && !Files.exists(newOwner.authorizedOutput()),"cross-owner recovery after actual process deaths aborts incomplete output");
            }
        }finally{if(host!=null && host.isAlive())host.destroyForcibly();if(worker!=null && worker.isAlive())worker.destroyForcibly();}
        System.out.println("RESULT recovery_assertions="+passed+" failures=0; Windows/JVM process and lock proof only; Android/Binder/codec/device durability NOT_RUN; directory fsync mocked on Windows");
    }
}
