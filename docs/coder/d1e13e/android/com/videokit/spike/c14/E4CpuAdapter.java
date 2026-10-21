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
        public final int sequence,pid,uid,num,den,best; public final String sourceTask,nativeDiagnostic;
        public final long sourceEpoch,ptsUs,raw; public final byte[] rgba,thumb;
        Sample(int sequence,CpuTaskClient cpu,CpuTaskClient.Frame frame,PipelinePacket packet){
            this.sequence=sequence;pid=cpu.workerPid();uid=cpu.workerUid();sourceTask=cpu.task;sourceEpoch=cpu.epoch;
            E6NativeDiagnostic d=cpu.nativeDiagnostic();nativeDiagnostic=d==null?"NOT_COLLECTED":d.safe();
            ptsUs=frame.ptsUs;raw=frame.sourceTimestamp;num=frame.timeBaseNum;den=frame.timeBaseDen;best=frame.bestEffort?1:0;
            rgba=packet.pixels();thumb=packet.thumb();
        }
    }
    public static final class Verification {
        public final int pid,uid,frames;public final String task,sha,nativeDiagnostic;public final long bytes;
        public final boolean fullEof,sourceClosed,originalDeath,slotReleased;
        private Verification(PipelineValidationReceipt proof,E6NativeDiagnostic d){
            pid=proof.pid;uid=proof.uid;task=proof.task;sha=proof.sha;bytes=proof.bytes;
            nativeDiagnostic=d==null?"NOT_COLLECTED":d.safe();frames=proof.frames;fullEof=proof.fullEof;
            sourceClosed=proof.sourceClosed;originalDeath=proof.originalDeath;slotReleased=proof.slotReleased;
        }
    }
    interface SourceOwner {
        String task();Sample read(int sequence)throws Exception;E6NativeDiagnostic snapshot();boolean stop()throws Exception;void close()throws Exception;void cancel();
    }
    interface ValidationOwner {
        String task();void startAndAwait(long[] timeline)throws Exception;boolean stop()throws Exception;void close()throws Exception;void retain();
        E6NativeDiagnostic snapshot();PipelineValidationReceipt.View view();
    }

    private final Context context;private final TrackedProvider provider;private final int kind;
    private volatile SourceOwner active;private volatile boolean closed;private int next=1;
    private final List<SourceOwner> retained=new CopyOnWriteArrayList<>();
    private static final List<CpuTaskClient> RETAINED_VERIFIERS=new CopyOnWriteArrayList<>();
    public E4CpuAdapter(Context context,AsyncReadBridge.Provider provider,int kind)throws IOException{
        com.videokit.spike.e4.E9Phase.requireProduct();
        if(kind!=CpuTaskClient.MP4_H264 && kind!=CpuTaskClient.AVI_MPEG4)throw new IOException("E4_SOURCE_KIND");
        this.context=context.getApplicationContext();this.provider=new TrackedProvider(provider);this.kind=kind;
    }
    private static void offMain()throws IOException{if(Looper.myLooper()==Looper.getMainLooper())throw new IOException("E4_CPU_MAIN_THREAD");}
    public Sample next(int sequence)throws Exception{
        com.videokit.spike.e4.E9Phase.requireProduct();
        offMain();if(closed || active!=null || sequence!=next || sequence>6)throw new IOException("E4_SOURCE_SEQUENCE_OR_PENDING");
        final CpuTaskClient cpu;
        try{cpu=new CpuTaskClient(context,provider);}catch(Exception|Error failure){throw new E6AFailure("SOURCE","NOT_CREATED",10,"CREATE",failure,List.of(),null);}
        return next(sequence,new SourceOwner(){
            public String task(){return cpu.task;}public E6NativeDiagnostic snapshot(){return cpu.nativeDiagnostic();}
            public boolean stop()throws Exception{return cpu.stopAndAwait(5000);}public void close(){cpu.close();}public void cancel(){cpu.cancel();}
            public Sample read(int sequence)throws Exception{
                cpu.start(kind,2000000L+(sequence-1)*PipelineRules.STEP_US,CpuTaskClient.PIPELINE_FRAME);CpuTaskClient.Frame frame=cpu.awaitResult(10000);
                if(!cpu.orientationVerified())throw new IOException("E4_SOURCE_ORIENTATION_UNPROVEN");
                PipelineRules.Identity id=new PipelineRules.Identity(cpu.task,cpu.epoch,cpu.workerPid(),cpu.workerUid());
                PipelinePacket packet=new PipelinePacket(id,id,sequence,frame.ptsUs,frame.sourceTimestamp,frame.timeBaseNum,frame.timeBaseDen,frame.bestEffort?1:0,frame.width,frame.height,frame.stride,0,frame.copyPixels());
                Sample result=new Sample(sequence,cpu,frame,packet);
                StageLog.event("E4_SOURCE_FRAME","sequence="+sequence+" task="+cpu.task+" epoch="+cpu.epoch+" pid="+result.pid+" uid="+result.uid+" pts_us="+frame.ptsUs+" raw="+result.raw+" num="+result.num+" den="+result.den+" sha="+packet.sha);return result;
            }
        });
    }
    // This is the production source ownership boundary, also invoked directly with bounded platform operations in local checks.
    Sample next(int sequence,SourceOwner cpu)throws Exception{
        offMain();if(active!=null || sequence!=next || sequence>6)throw new IOException("E4_SOURCE_SEQUENCE_OR_PENDING");
        active=cpu;Throwable primary=null;List<Throwable> cleanup=new ArrayList<>();Sample result=null;String phase="READ";boolean clean=false,closedOwner=false;
        try{if(closed){phase="BEFORE_READ";throw new IOException("E4_SOURCE_SEQUENCE_OR_PENDING");}result=cpu.read(sequence);next++;}catch(Exception|Error failure){primary=failure;}
        try{clean=cpu.stop();if(!clean)throw new IOException("E4_SOURCE_CLOSE_OR_DEATH_UNPROVEN");}catch(Exception|Error failure){if(primary==null){primary=failure;phase="STOP";}else cleanup.add(failure);}
        try{cpu.close();closedOwner=true;}catch(Exception|Error failure){if(primary==null){primary=failure;phase="CLOSE";}else cleanup.add(failure);}
        if(clean && closedOwner)active=null;else if(!retained.contains(cpu))retained.add(cpu);
        if(primary!=null)throw new E6AFailure("SOURCE",cpu.task(),10,phase,primary,cleanup,cpu.snapshot());
        return result;
    }
    public void cancel(){closed=true;SourceOwner cpu=active;if(cpu!=null)cpu.cancel();}
    public boolean sourceClosed(){return active==null && retained.isEmpty() && provider.released() && CpuTaskClient.quarantinedSources()==0;}
    public int handlesOpened(){return provider.opened.get();}public int handlesClosed(){return provider.closed.get();}
    public int pendingSourceCalls(){return provider.calls.get();}
    public void close()throws IOException{
        offMain();closed=true;long stop=System.nanoTime()+TimeUnit.SECONDS.toNanos(1);
        while(active==null && retained.isEmpty() && !sourceClosed() && System.nanoTime()<stop)try{Thread.sleep(5);}catch(InterruptedException error){Thread.currentThread().interrupt();throw new IOException("E4_SOURCE_PENDING_NO_REUSE",error);}
        if(!sourceClosed())throw new IOException("E4_SOURCE_PENDING_NO_REUSE");
    }
    public static Verification validate(Context context,AsyncReadBridge.Provider source,long[] timeline,List<byte[]> thumbs,String before,long bytes,Callable<String> digestAfter)throws Exception{
        com.videokit.spike.e4.E9Phase.requireProduct();
        offMain();
        try{PipelineRules.timeline(timeline);}catch(Exception|Error failure){throw new E6AFailure("VALIDATOR","NOT_CREATED",11,"TIMELINE",failure,List.of(),null);}
        TrackedProvider tracked=new TrackedProvider(source);final CpuTaskClient verifier;
        try{verifier=new CpuTaskClient(context,tracked);}catch(Exception|Error failure){throw new E6AFailure("VALIDATOR","NOT_CREATED",11,"CREATE",failure,List.of(),null);}
        return validate(new ValidationOwner(){
            public String task(){return verifier.task;}public E6NativeDiagnostic snapshot(){return verifier.nativeDiagnostic();}
            public void startAndAwait(long[] timeline)throws Exception{verifier.verificationTimeline(timeline);verifier.start(CpuTaskClient.MP4_H264,0,CpuTaskClient.VERIFY_OUTPUT);verifier.awaitVerification(15000);}
            public boolean stop()throws Exception{boolean clean=verifier.stopAndAwait(5000);if(!clean || !tracked.released())throw new IOException("E4_VALIDATOR_CLOSE_UNPROVEN");return clean;}
            public void close(){verifier.close();}public void retain(){if(!RETAINED_VERIFIERS.contains(verifier))RETAINED_VERIFIERS.add(verifier);}
            public PipelineValidationReceipt.View view(){return PipelineValidationReceipt.view(verifier);}
        },timeline,thumbs,before,bytes,digestAfter);
    }
    // The actual validation/cleanup/digest/receipt flow; no test-specific outcome or bypass is present.
    static Verification validate(ValidationOwner owner,long[] timeline,List<byte[]> thumbs,String before,long bytes,Callable<String> digestAfter)throws Exception{
        Throwable primary=null;List<Throwable> cleanup=new ArrayList<>();String phase="TIMELINE";boolean stopped=false,closed=false;
        try{PipelineRules.timeline(timeline);phase="NATIVE";owner.startAndAwait(timeline);}catch(Exception|Error failure){primary=failure;}
        try{stopped=owner.stop();if(!stopped)throw new IOException("E4_VALIDATOR_CLOSE_UNPROVEN");}catch(Exception|Error failure){if(primary==null){primary=failure;phase="STOP";}else cleanup.add(failure);}
        try{owner.close();closed=true;}catch(Exception|Error failure){if(primary==null){primary=failure;phase="CLOSE";}else cleanup.add(failure);}
        if(!stopped || !closed)owner.retain();
        if(primary!=null)throw new E6AFailure("VALIDATOR",owner.task(),11,phase,primary,cleanup,owner.snapshot());
        try{
            phase="DIGEST";String after=digestAfter.call();phase="RECEIPT";
            PipelineValidationReceipt proof=PipelineValidationReceipt.prove(owner.view(),thumbs,before,after,bytes);
            return new Verification(proof,owner.snapshot());
        }catch(Exception|Error failure){throw new E6AFailure("VALIDATOR",owner.task(),11,phase,failure,cleanup,owner.snapshot());}
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
