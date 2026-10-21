package com.videokit.spike.c08;

import java.io.*;
import java.nio.file.*;
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.*;

public final class C08SelfCheck {
    private static int passed;
    private static void check(boolean ok,String name){if(!ok)throw new AssertionError(name);passed++;System.out.println("PASS "+name);}
    private static void error(String code,Callable<?> call)throws Exception{try{call.call();throw new AssertionError("expected "+code);}catch(IOException e){check(code.equals(e.getMessage()),code);}}
    private static AsyncReadBridge bridge(AsyncReadBridge.Runtime r,LeaseRegistry leases,long gen,AsyncReadBridge.Provider provider,long timeout)throws IOException{return new AsyncReadBridge(r,provider,leases,gen,timeout);}
    static class Host implements SinkCoordinator.Host {
        SinkCoordinator.HostState state=SinkCoordinator.HostState.WRITING;int readyCalls,abortCalls;boolean loseReady,loseAbort,queryUnknown;
        public synchronized CompletionStage<String> markReady(String id){readyCalls++;if(state==SinkCoordinator.HostState.ABORTED)return HostFixtures.failed(new IOException("ABORTED"));state=SinkCoordinator.HostState.READY;return loseReady?HostFixtures.failed(new IOException("response lost")):CompletableFuture.completedFuture("opaque-"+id);}
        public synchronized CompletionStage<SinkCoordinator.Status> query(String id){return CompletableFuture.completedFuture(new SinkCoordinator.Status(queryUnknown?SinkCoordinator.HostState.UNKNOWN:state,state==SinkCoordinator.HostState.READY?"opaque-"+id:null));}
        public synchronized CompletionStage<Void> abort(String id){abortCalls++;if(state!=SinkCoordinator.HostState.READY)state=SinkCoordinator.HostState.ABORTED;return loseAbort?HostFixtures.failed(new IOException("response lost")):CompletableFuture.completedFuture(null);}
    }
    static final class DelayedHost extends Host {
        final CompletableFuture<String> pending=new CompletableFuture<>();final CountDownLatch readyEntered=new CountDownLatch(1);
        public synchronized CompletionStage<String> markReady(String id){readyCalls++;readyEntered.countDown();return pending;}
        synchronized void commit(String id){if(state==SinkCoordinator.HostState.ABORTED)pending.completeExceptionally(new IOException("ABORTED"));else{state=SinkCoordinator.HostState.READY;pending.complete("opaque-"+id);}}
    }
    public static void main(String[] args)throws Exception {
        Path root=Path.of(args[0]);LeaseRegistry leases=new LeaseRegistry();ExecutorService caller=Executors.newSingleThreadExecutor();
        try(AsyncReadBridge.Runtime runtime=new AsyncReadBridge.Runtime()){
            long g=leases.create();AtomicReference<String> thread=new AtomicReference<>();
            AsyncReadBridge a=bridge(runtime,leases,g,t->{thread.set(Thread.currentThread().getName());return CompletableFuture.completedFuture(HostFixtures.memory(new byte[]{1,2,3,4,5}));},1000);
            check(a.open(1,3)==3,"known length range");byte[] data=new byte[10];check(a.read(data,2,2)==2 && data[2]==2 && data[3]==3,"async buffer target offset");
            check(a.read(data,0,4)==1 && a.read(data,0,1)==-1,"bounded EOF");check(thread.get().startsWith("videokit-d1-io"),"provider invocation on independent IO executor");a.close();a.close();leases.retire(g);check(leases.awaitReleased(g,1000),"idempotent close and actual resource drain");error("SESSION_RELEASED",()->a.read(data,0,1));
            g=leases.create();final long multi=g;AsyncReadBridge first=bridge(runtime,leases,g,HostFixtures.file(root.resolve("test_media/imgs_and_videos/videos/sample.mp4")),1000);
            AsyncReadBridge second=bridge(runtime,leases,g,HostFixtures.file(root.resolve("test_media/imgs_and_videos/videos/sample.mp4")),1000);first.open(0,1);second.open(0,1);leases.retire(g);first.close();
            check(!leases.query(g).released() && leases.query(g).consumers==1,"multi-consumer query prevents early SourceReleased");second.close();check(leases.awaitReleased(g,1000),"all consumers close before released");error("SESSION_RELEASED",()->bridge(runtime,leases,multi,HostFixtures.file(root.resolve("unused")),1000));
            g=leases.create();final long late=g;CompletableFuture<AsyncReadBridge.Handle> delayedOpen=new CompletableFuture<>();CountDownLatch entered=new CountDownLatch(1);AtomicBoolean handleClosed=new AtomicBoolean();
            AsyncReadBridge openRace=bridge(runtime,leases,g,c->{entered.countDown();return delayedOpen;},1000);
            Future<?> race=caller.submit(()->{try{openRace.open(0,-1);throw new AssertionError();}catch(IOException e){if(!e.getMessage().equals("CANCELLED"))throw new RuntimeException(e);}});
            check(entered.await(1,TimeUnit.SECONDS),"open provider entered");openRace.close();leases.retire(g);race.get(1,TimeUnit.SECONDS);check(!leases.query(g).released(),"late open retained in resource ledger");
            delayedOpen.complete(new AsyncReadBridge.Handle(){public Long length(){return 1L;}public CompletionStage<Integer>readAt(long p,byte[] b,int o,int n,AsyncReadBridge.Cancellation c){return CompletableFuture.completedFuture(-1);}public CompletionStage<Void>closeAsync(){handleClosed.set(true);return CompletableFuture.completedFuture(null);}});
            check(leases.awaitReleased(late,1000) && handleClosed.get(),"late open completion closed, not adopted by retired generation");
            g=leases.create();final long stuck=g;CompletableFuture<Integer> ignoredCancel=new CompletableFuture<>();AtomicReference<byte[]> owned=new AtomicReference<>();CountDownLatch readEntered=new CountDownLatch(1);
            AsyncReadBridge noncooperative=bridge(runtime,leases,g,c->CompletableFuture.completedFuture(new AsyncReadBridge.Handle(){public Long length(){return null;}public CompletionStage<Integer>readAt(long p,byte[] b,int o,int n,AsyncReadBridge.Cancellation t){owned.set(b);readEntered.countDown();return ignoredCancel;}public CompletionStage<Void>closeAsync(){return CompletableFuture.completedFuture(null);}}),80);
            noncooperative.open(0,-1);byte[] untouched={9};long start=System.nanoTime();error("SOURCE_TIMEOUT",()->noncooperative.read(untouched,0,1));leases.retire(g);
            check(readEntered.getCount()==0 && !leases.query(g).released(),"noncooperative read not falsely released at deadline");check(untouched[0]==9,"timeout cannot mutate caller memory");
            owned.get()[0]=88;ignoredCancel.complete(1);check(leases.awaitReleased(stuck,1000) && untouched[0]==9,"late read drains privately without caller mutation");System.out.println("METRIC desktop_timeout_return_ms="+(System.nanoTime()-start)/1e6);
            g=leases.create();CompletableFuture<Integer> pending=new CompletableFuture<>();CountDownLatch reading=new CountDownLatch(1);
            AsyncReadBridge cancelled=bridge(runtime,leases,g,c->CompletableFuture.completedFuture(new AsyncReadBridge.Handle(){public Long length(){return null;}public CompletionStage<Integer>readAt(long p,byte[] b,int o,int n,AsyncReadBridge.Cancellation t){reading.countDown();return pending;}public CompletionStage<Void>closeAsync(){pending.completeExceptionally(new IOException("CANCELLED"));return CompletableFuture.completedFuture(null);}}),3000);
            cancelled.open(0,-1);Future<?> running=caller.submit(()->{try{cancelled.read(new byte[1],0,1);throw new AssertionError();}catch(IOException e){if(!e.getMessage().equals("CANCELLED"))throw new RuntimeException(e);}});
            check(reading.await(1,TimeUnit.SECONDS),"async read started");cancelled.close();leases.retire(g);running.get(1,TimeUnit.SECONDS);check(leases.awaitReleased(g,1000),"close wakes caller and drains cooperative provider");
            g=leases.create();AsyncReadBridge huge=bridge(runtime,leases,g,HostFixtures.file(root.resolve("test_media/03_large_files/large_video_over_2GiB.mkv")),1000);
            long at=(1L<<31)+4321;huge.open(at,64);byte[] actual=new byte[64],expected=new byte[64];check(huge.read(actual,0,64)==64,"async actual 2GiB+ read");try(RandomAccessFile f=new RandomAccessFile(root.resolve("test_media/03_large_files/large_video_over_2GiB.mkv").toFile(),"r")){f.seek(at);f.readFully(expected);}check(Arrays.equals(actual,expected),"actual large-file bytes match reference");huge.close();leases.retire(g);check(leases.awaitReleased(g,1000),"large-file handle drained");
            g=leases.create();Path srt;try(var paths=Files.list(root.resolve("test_media/02_videos"))){srt=paths.filter(p->p.toString().endsWith(".srt")).findFirst().orElseThrow();}
            AsyncReadBridge subtitle=bridge(runtime,leases,g,HostFixtures.srt(srt),1000);long len=subtitle.open(0,-1);ByteArrayOutputStream out=new ByteArrayOutputStream();byte[] chunk=new byte[8192];int n;while((n=subtitle.read(chunk,0,chunk.length))!=-1)out.write(chunk,0,n);
            String text=new String(out.toByteArray(),java.nio.charset.StandardCharsets.UTF_8);check(out.size()==len && text.contains("-->"),"real GB-family SRT exposed as bounded UTF8 read source");subtitle.close();leases.retire(g);check(leases.awaitReleased(g,1000),"subtitle lease drained");
            g=leases.create();AsyncReadBridge unknown=bridge(runtime,leases,g,c->CompletableFuture.completedFuture(new AsyncReadBridge.Handle(){public Long length(){return null;}int calls;public CompletionStage<Integer>readAt(long p,byte[] b,int o,int n,AsyncReadBridge.Cancellation t){if(calls++>1)return CompletableFuture.completedFuture(-1);b[o]=7;return CompletableFuture.completedFuture(1);}public CompletionStage<Void>closeAsync(){return CompletableFuture.completedFuture(null);}}),1000);
            check(unknown.open(0,-1)==-1 && unknown.read(data,0,9)==1 && unknown.read(data,0,9)==1 && unknown.read(data,0,9)==-1,"unknown length short reads EOF");unknown.close();leases.retire(g);check(leases.awaitReleased(g,1000),"unknown source drained");
            g=leases.create();AsyncReadBridge redacted=bridge(runtime,leases,g,c->HostFixtures.failed(new IOException("secret-password-and-path")),1000);error("SOURCE_IO_FAILED",()->redacted.open(0,-1));redacted.close();leases.retire(g);check(leases.awaitReleased(g,1000),"failed open releases consumer");
            g=leases.create();AsyncReadBridge failingClose=bridge(runtime,leases,g,c->CompletableFuture.completedFuture(new AsyncReadBridge.Handle(){public Long length(){return 0L;}public CompletionStage<Integer>readAt(long p,byte[] b,int o,int n,AsyncReadBridge.Cancellation t){return CompletableFuture.completedFuture(-1);}public CompletionStage<Void>closeAsync(){return HostFixtures.failed(new IOException("transport refused close"));}}),1000);
            failingClose.open(0,-1);failingClose.close();leases.retire(g);check(!leases.awaitReleased(g,100) && leases.query(g).closeFailed,"failed close is retained as unreleased, not hidden");
            // A failed lease remains visible; other generations remain usable.
            long goodGeneration=leases.create();AsyncReadBridge good=bridge(runtime,leases,goodGeneration,c->CompletableFuture.completedFuture(HostFixtures.memory(new byte[]{3})),1000);good.open(0,-1);check(good.read(data,0,1)==1,"other generation survives close failure");good.close();leases.retire(goodGeneration);check(leases.awaitReleased(goodGeneration,1000),"healthy generation releases independently");
            long blockingGeneration=leases.create();CountDownLatch invocationEntered=new CountDownLatch(1),invokeStop=new CountDownLatch(1);
            AsyncReadBridge synchronousBlock=bridge(runtime,leases,blockingGeneration,c->CompletableFuture.completedFuture(new AsyncReadBridge.Handle(){public Long length(){return null;}public CompletionStage<Integer>readAt(long p,byte[] b,int o,int n,AsyncReadBridge.Cancellation t){invocationEntered.countDown();try{invokeStop.await();}catch(InterruptedException e){Thread.currentThread().interrupt();}return HostFixtures.failed(new IOException("CANCELLED"));}public CompletionStage<Void>closeAsync(){invokeStop.countDown();return CompletableFuture.completedFuture(null);}}),3000);
            synchronousBlock.open(0,-1);Future<?> blocked=caller.submit(()->{try{synchronousBlock.read(data,0,1);throw new AssertionError();}catch(IOException e){if(!e.getMessage().equals("CANCELLED"))throw new RuntimeException(e);}});
            check(invocationEntered.await(1,TimeUnit.SECONDS),"provider invocation can block without UI dependency");synchronousBlock.close();leases.retire(blockingGeneration);blocked.get(1,TimeUnit.SECONDS);check(leases.awaitReleased(blockingGeneration,1000),"independent cleanup lane interrupts blocked IO invocation");
            for(int i=0;i<130;i++){long retired=leases.create();leases.retire(retired);}check(leases.query(goodGeneration).released(),"bounded generation history retains released-query meaning");
        }finally{caller.shutdownNow();}
        Host host=new Host();host.loseReady=true;SinkCoordinator sink=new SinkCoordinator("task-A",host,100);sink.start();sink.validating();error("OUTPUT_READY_UNKNOWN",()->sink.finalizeReady(true));sink.cancel();
        check(sink.reconcile()==SinkCoordinator.State.READY && "opaque-task-A".equals(sink.token()),"unknown ready query recovers original output token");check(host.readyCalls==1 && host.abortCalls==0,"no second target or blind abort after ready response loss");sink.closeExecutor();
        host=new Host();SinkCoordinator cancel=new SinkCoordinator("task-B",host,100);cancel.start();cancel.cancel();cancel.validating();error("CANCELLED",()->cancel.finalizeReady(true));check(cancel.state()==SinkCoordinator.State.ABORTED && host.readyCalls==0,"cancel before ready wins and aborts");cancel.closeExecutor();
        host=new Host();host.loseAbort=true;SinkCoordinator aborted=new SinkCoordinator("task-C",host,100);aborted.start();error("OUTPUT_ABORT_UNKNOWN",()->{aborted.abortBeforeReady();return null;});check(aborted.reconcile()==SinkCoordinator.State.ABORTED,"lost abort response query reconciles cleanup");aborted.closeExecutor();
        host=new Host();host.loseReady=true;host.queryUnknown=true;SinkCoordinator unresolved=new SinkCoordinator("task-D",host,100);unresolved.start();unresolved.validating();error("OUTPUT_READY_UNKNOWN",()->unresolved.finalizeReady(true));check(unresolved.reconcile()==SinkCoordinator.State.READY_UNKNOWN,"unknown host state remains unknown");unresolved.closeExecutor();
        host=new Host();SinkCoordinator invalid=new SinkCoordinator("task-E",host,100);invalid.start();invalid.validating();error("OUTPUT_VALIDATION_FAILED",()->invalid.finalizeReady(false));check(invalid.state()==SinkCoordinator.State.ABORTED && host.readyCalls==0,"invalid output never ready");invalid.closeExecutor();
        DelayedHost lateReady=new DelayedHost();SinkCoordinator arbitration=new SinkCoordinator("task-F",lateReady,80);arbitration.start();arbitration.validating();error("OUTPUT_READY_UNKNOWN",()->arbitration.finalizeReady(true));arbitration.cancel();
        check(arbitration.reconcile()==SinkCoordinator.State.ABORTED,"host atomic abort wins over uncommitted late ready");lateReady.commit("task-F");check(lateReady.state==SinkCoordinator.HostState.ABORTED && arbitration.reconcile()==SinkCoordinator.State.ABORTED,"late ready cannot resurrect aborted task");arbitration.closeExecutor();
        System.out.println("RESULT assertions="+passed+" failures=0; Android/codec/native-crash/model effects NOT_RUN");
    }
}
