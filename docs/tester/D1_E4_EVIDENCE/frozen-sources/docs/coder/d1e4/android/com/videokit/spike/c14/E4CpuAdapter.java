package com.videokit.spike.c14;

import android.content.Context;
import android.os.Looper;
import java.io.IOException;
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;

/** E4 bridge to the unchanged isolated C14 CPU protocol. No host media parser. */
public final class E4CpuAdapter implements AutoCloseable {
    public static final class Sample {
        public final int sequence,pid,uid,num,den,best; public final String sourceTask;
        public final long sourceEpoch,ptsUs,raw; public final byte[] rgba,thumb;
        Sample(int sequence,CpuTaskClient cpu,CpuTaskClient.Frame frame,PipelinePacket packet){
            this.sequence=sequence;pid=cpu.workerPid();uid=cpu.workerUid();sourceTask=cpu.task;sourceEpoch=cpu.epoch;
            ptsUs=frame.ptsUs;raw=frame.sourceTimestamp;num=frame.timeBaseNum;den=frame.timeBaseDen;best=frame.bestEffort?1:0;
            rgba=packet.pixels();thumb=packet.thumb();
        }
    }
    public static final class Verification {
        public final int pid,uid,frames;public final String task,sha;public final long bytes;
        public final boolean fullEof,sourceClosed,originalDeath,slotReleased;
        private Verification(CpuTaskClient cpu,PipelineValidationReceipt proof){
            pid=proof.pid;uid=proof.uid;task=proof.task;sha=proof.sha;bytes=proof.bytes;
            frames=cpu.verificationFrames().size();fullEof=cpu.verificationDone();
            CpuLifecycle.Snapshot s=cpu.lifecycle();sourceClosed=s.sourceReleased;originalDeath=s.actualDeath;slotReleased=s.slotReleased;
        }
    }
    private final Context context;private final TrackedProvider provider;private final int kind;
    private volatile CpuTaskClient active;private volatile boolean closed;private int next=1;
    private final List<CpuTaskClient> retained=new CopyOnWriteArrayList<>();
    private static final List<CpuTaskClient> RETAINED_VERIFIERS=new CopyOnWriteArrayList<>();
    public E4CpuAdapter(Context context,AsyncReadBridge.Provider provider,int kind)throws IOException{
        if(kind!=CpuTaskClient.MP4_H264 && kind!=CpuTaskClient.AVI_MPEG4)throw new IOException("E4_SOURCE_KIND");
        this.context=context.getApplicationContext();this.provider=new TrackedProvider(provider);this.kind=kind;
    }
    private static void offMain()throws IOException{if(Looper.myLooper()==Looper.getMainLooper())throw new IOException("E4_CPU_MAIN_THREAD");}
    public Sample next(int sequence)throws Exception{
        offMain();if(closed || active!=null || sequence!=next || sequence>6)throw new IOException("E4_SOURCE_SEQUENCE_OR_PENDING");
        CpuTaskClient cpu=new CpuTaskClient(context,provider);active=cpu;Throwable primary=null;
        try{
            cpu.start(kind,2000000L+(sequence-1)*PipelineRules.STEP_US,CpuTaskClient.PIPELINE_FRAME);
            CpuTaskClient.Frame frame=cpu.awaitResult(10000);
            if(!cpu.orientationVerified())throw new IOException("E4_SOURCE_ORIENTATION_UNPROVEN");
            PipelineRules.Identity id=new PipelineRules.Identity(cpu.task,cpu.epoch,cpu.workerPid(),cpu.workerUid());
            PipelinePacket packet=new PipelinePacket(id,id,sequence,frame.ptsUs,frame.sourceTimestamp,
                frame.timeBaseNum,frame.timeBaseDen,frame.bestEffort?1:0,frame.width,frame.height,frame.stride,0,frame.copyPixels());
            Sample result=new Sample(sequence,cpu,frame,packet);next++;
            StageLog.event("E4_SOURCE_FRAME","sequence="+sequence+" task="+cpu.task+" epoch="+cpu.epoch+" pid="+result.pid+" uid="+result.uid+" pts_us="+frame.ptsUs+" raw="+result.raw+" num="+result.num+" den="+result.den+" sha="+packet.sha);
            return result;
        }catch(Exception|Error failure){primary=failure;throw failure;}
        finally{
            boolean clean=false;
            try{clean=cpu.stopAndAwait(5000);if(!clean)throw new IOException("E4_SOURCE_CLOSE_OR_DEATH_UNPROVEN");}
            catch(Exception|Error cleanup){if(primary!=null)primary.addSuppressed(cleanup);else throw cleanup;}
            finally{cpu.close();if(clean)active=null;else if(!retained.contains(cpu))retained.add(cpu);}
        }
    }
    public void cancel(){closed=true;CpuTaskClient cpu=active;if(cpu!=null)cpu.cancel();}
    public boolean sourceClosed(){return active==null && retained.isEmpty() && provider.released() && CpuTaskClient.quarantinedSources()==0;}
    public int handlesOpened(){return provider.opened.get();}public int handlesClosed(){return provider.closed.get();}
    public int pendingSourceCalls(){return provider.calls.get();}
    public void close()throws IOException{
        offMain();closed=true;long stop=System.nanoTime()+TimeUnit.SECONDS.toNanos(1);
        while(active==null && retained.isEmpty() && !sourceClosed() && System.nanoTime()<stop)try{Thread.sleep(5);}catch(InterruptedException error){Thread.currentThread().interrupt();throw new IOException("E4_SOURCE_PENDING_NO_REUSE",error);}
        if(!sourceClosed())throw new IOException("E4_SOURCE_PENDING_NO_REUSE");
    }
    public static Verification validate(Context context,AsyncReadBridge.Provider source,long[] timeline,List<byte[]> thumbs,String before,long bytes,Callable<String> digestAfter)throws Exception{
        offMain();PipelineRules.timeline(timeline);TrackedProvider tracked=new TrackedProvider(source);
        CpuTaskClient verifier=new CpuTaskClient(context,tracked);Throwable primary=null;
        try{verifier.verificationTimeline(timeline);verifier.start(CpuTaskClient.MP4_H264,0,CpuTaskClient.VERIFY_OUTPUT);verifier.awaitVerification(15000);}
        catch(Exception|Error failure){primary=failure;throw failure;}
        finally{
            boolean clean=false;
            try{clean=verifier.stopAndAwait(5000);if(!clean || !tracked.released())throw new IOException("E4_VALIDATOR_CLOSE_UNPROVEN");}
            catch(Exception|Error cleanup){if(primary!=null)primary.addSuppressed(cleanup);else throw cleanup;}
            finally{verifier.close();if(!clean)RETAINED_VERIFIERS.add(verifier);}
        }
        PipelineValidationReceipt proof=PipelineValidationReceipt.prove(verifier,thumbs,before,digestAfter.call(),bytes);
        return new Verification(verifier,proof);
    }
    public static int retainedVerifiers(){return RETAINED_VERIFIERS.size();}

    private static final class TrackedProvider implements AsyncReadBridge.Provider {
        final AsyncReadBridge.Provider delegate;final AtomicInteger opened=new AtomicInteger(),closed=new AtomicInteger(),calls=new AtomicInteger();
        final List<AsyncReadBridge.Handle> owners=new CopyOnWriteArrayList<>();
        TrackedProvider(AsyncReadBridge.Provider provider){delegate=Objects.requireNonNull(provider);}
        boolean released(){return opened.get()==closed.get() && calls.get()==0 && owners.isEmpty();}
        public CompletionStage<AsyncReadBridge.Handle> open(AsyncReadBridge.Cancellation token){
            calls.incrementAndGet();CompletableFuture<AsyncReadBridge.Handle> result=new CompletableFuture<>();
            try{delegate.open(token).whenComplete((handle,error)->{
                try{if(error!=null){result.completeExceptionally(error);return;}if(handle==null)throw new IOException("E4_SOURCE_NULL");
                    owners.add(handle);opened.incrementAndGet();
                    result.complete(new AsyncReadBridge.Handle(){
                        public Long length(){return handle.length();}
                        public CompletionStage<Integer> readAt(long at,byte[] target,int offset,int length,AsyncReadBridge.Cancellation cancellation){
                            calls.incrementAndGet();CompletableFuture<Integer> done=new CompletableFuture<>();
                            try{handle.readAt(at,target,offset,length,cancellation).whenComplete((value,readError)->{
                                calls.decrementAndGet();if(readError==null)done.complete(value);else done.completeExceptionally(readError);
                            });}catch(Throwable failure){calls.decrementAndGet();done.completeExceptionally(failure);}return done;
                        }
                        public CompletionStage<Void> closeAsync(){
                            calls.incrementAndGet();CompletableFuture<Void> done=new CompletableFuture<>();
                            try{handle.closeAsync().whenComplete((v,closeError)->{try{if(closeError==null){if(owners.remove(handle))closed.incrementAndGet();done.complete(null);}else done.completeExceptionally(closeError);}finally{calls.decrementAndGet();}});}
                            catch(Throwable failure){calls.decrementAndGet();done.completeExceptionally(failure);}return done;
                        }
                    });
                }catch(Throwable failure){result.completeExceptionally(failure);}finally{calls.decrementAndGet();}
            });}catch(Throwable failure){calls.decrementAndGet();result.completeExceptionally(failure);}return result;
        }
    }
}
