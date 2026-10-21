package com.videokit.spike.c13;
import android.content.Context;
import android.os.Looper;
import java.io.*;
import java.nio.file.Path;
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.*;

/** Six real isolated snapshots -> bounded raw queue -> public AVC encoder -> isolated full EOF validation. */
public final class RealFramePipeline implements AutoCloseable {
    private static final Semaphore BUDGET=new Semaphore(1);
    private static final Set<RealFramePipeline> OWNERS=ConcurrentHashMap.newKeySet();
    private static ThreadPoolExecutor executor(String name){return new ThreadPoolExecutor(1,1,0,TimeUnit.MILLISECONDS,new ArrayBlockingQueue<>(1),r->{Thread t=new Thread(r,name);t.setDaemon(true);return t;},new ThreadPoolExecutor.AbortPolicy());}
    private static final ThreadPoolExecutor RUNNER=executor("c13-pipeline-owner"),PRODUCER=executor("c13-frame-producer");
    public static final class Report {
        public final String id,status,error,token;public final boolean resourcesReleased,sourceReleased,codecReleased,writerReleased,framesReleased;
        public final int received,inputs,outputs,verified,queuePeak,consumers;public final long bytes;
        Report(RealFramePipeline p){id=p.id;error=p.first.get();token=p.token;sourceReleased=p.sourceReleased();codecReleased=p.encoder==null || p.encoder.released();writerReleased=p.sink!=null && p.sink.writerReleased();BoundedFrameQueue.Snapshot q=p.queue.snapshot();framesReleased=q.released();received=p.received;inputs=p.encoder==null?0:p.encoder.inputs();outputs=p.encoder==null?0:p.encoder.outputs();verified=p.verified;queuePeak=q.peak;consumers=q.consumers;bytes=p.outputBytes;resourcesReleased=p.released.get();status=resourcesReleased?(p.ready?"READY":error!=null && error.equals("PIPE_CAPABILITY_UNSUPPORTED")?"CAPABILITY_BLOCKED":"ABORTED"):"PENDING";}
    }
    private final Context context;private final AsyncReadBridge.Provider source;private final int kind;private final String fault;public final String id=UUID.randomUUID().toString();
    private final BoundedFrameQueue<PipelinePacket> queue=new BoundedFrameQueue<>();private final AtomicBoolean cancelled=new AtomicBoolean(),released=new AtomicBoolean();
    private final AtomicReference<String> first=new AtomicReference<>();private final CompletableFuture<Report> result=new CompletableFuture<>();
    private final List<CpuTaskClient> unreleased=new CopyOnWriteArrayList<>();private final List<byte[]> sourceThumbs=new ArrayList<>();private final long[] timeline=new long[PipelineRules.FRAMES];
    private volatile CpuTaskClient active;private volatile Future<?> producer;private volatile PipelineEncoder encoder;private volatile PipelineOutputSink sink;private volatile SinkCoordinator coordinator;
    private volatile boolean runnerFinished,ready,ownerClosed;private volatile String token;private volatile int received,verified;private volatile long outputBytes;
    private final long deadline=System.nanoTime()+TimeUnit.SECONDS.toNanos(60);
    public final CountDownLatch consumerEntered=new CountDownLatch(1);public volatile CountDownLatch consumerRelease;
    public RealFramePipeline(Context context,AsyncReadBridge.Provider source,int kind,Path authorizedOutputDirectory,String fault)throws IOException{
        this(context,source,kind,authorizedOutputDirectory,fault,null);
    }
    public RealFramePipeline(Context context,AsyncReadBridge.Provider source,int kind,Path authorizedOutputDirectory,String fault,CountDownLatch consumerGate)throws IOException{
        if(Looper.myLooper()==Looper.getMainLooper())throw new IOException("PIPE_MAIN_THREAD");if(!BUDGET.tryAcquire())throw new IOException("PIPE_ENCODER_OUTPUT_BUDGET_BUSY");try{PipelineOutputSink.preflightDirectory(authorizedOutputDirectory);}catch(IOException admission){BUDGET.release();throw admission;}
        this.context=context.getApplicationContext();this.source=source;this.kind=kind;this.fault=fault==null?"":fault;OWNERS.add(this);
        consumerRelease=consumerGate;
        try{sink=new PipelineOutputSink(authorizedOutputDirectory,id,this.fault);coordinator=new SinkCoordinator(id,sink,1000);coordinator.start();RUNNER.execute(this::run);}
        catch(Exception error){first.compareAndSet(null,"PIPE_OUTPUT_OPEN_UNPROVEN");runnerFinished=true;Report report=new Report(this);log(report);result.complete(report);throw new IOException("PIPE_OUTPUT_OPEN_UNPROVEN");}
    }
    private boolean cancellation(){if(System.nanoTime()>deadline){first.compareAndSet(null,"PIPE_DEADLINE");cancelled.set(true);}return cancelled.get();}
    private void error(Throwable error,String fallback){for(int n=0;n<8 && (error instanceof ExecutionException || error instanceof CompletionException) && error.getCause()!=null;n++)error=error.getCause();String message=error.getMessage();String code=message!=null && message.matches("(?:PIPE|CPU|SOURCE|OUTPUT)_[A-Z_0-9]{1,64}")?message:fallback;first.compareAndSet(null,code);StageLog.failure("PIPE_FAILURE",error);}
    private void produce(){PipelineRules.Order order=new PipelineRules.Order();
        try{for(int sequence=1;sequence<=PipelineRules.FRAMES;sequence++){
            if(cancellation())throw new IOException("PIPE_CANCELLED");CpuTaskClient cpu=new CpuTaskClient(context,source);active=cpu;
            Throwable primary=null;try{long target=2000000+(sequence-1)*PipelineRules.STEP_US;cpu.start(kind,target,CpuTaskClient.PIPELINE_FRAME);CpuTaskClient.Frame frame=cpu.awaitResult(10000);
                if(!cpu.orientationVerified())throw new IOException("PIPE_ORIENTATION_UNPROVEN");PipelineRules.Identity expected=new PipelineRules.Identity(cpu.task,cpu.epoch,cpu.workerPid(),cpu.workerUid()),claimed=new PipelineRules.Identity(cpu.task,fault.equals("frame-epoch")?cpu.epoch^1:cpu.epoch,cpu.workerPid(),cpu.workerUid());
                PipelineRules.identity(expected,claimed);PipelineRules.layout(frame.width,frame.height,frame.stride,frame.bytes(),0);int seq=fault.equals("late-frame") && sequence==2?1:sequence;order.admit(seq,frame.ptsUs);
                PipelinePacket packet=new PipelinePacket(expected,claimed,seq,frame.ptsUs,frame.sourceTimestamp,frame.timeBaseNum,frame.timeBaseDen,frame.bestEffort?1:0,frame.width,frame.height,frame.stride,0,frame.copyPixels());queue.offer(packet,500);received++;
                StageLog.event("PIPE_SOURCE_FRAME","export="+id+" sequence="+sequence+" task="+cpu.task+" epoch="+cpu.epoch+" pid="+cpu.workerPid()+" uid="+cpu.workerUid()+" pts_us="+frame.ptsUs+" raw="+frame.sourceTimestamp+" time_base="+frame.timeBaseNum+"/"+frame.timeBaseDen+" rgba_sha="+packet.sha);
            }catch(Exception|Error failure){primary=failure;error(failure,"PIPE_SOURCE_FAILED");throw failure;}
            finally{try{boolean clean=false;try{clean=cpu.stopAndAwait(5000);}finally{cpu.close();if(!clean)unreleased.add(cpu);else active=null;}if(!clean)throw new IOException("PIPE_CPU_RELEASE_UNPROVEN");}catch(Exception|Error cleanup){if(primary!=null)primary.addSuppressed(cleanup);else throw cleanup;}}
        }}catch(Throwable error){error(error,"PIPE_SOURCE_FAILED");queue.cancel();}
        finally{queue.finish();}
    }
    private void run(){
        try{
            encoder=new PipelineEncoder(sink,this::cancellation,fault);encoder.open();producer=PRODUCER.submit(this::produce);PipelineRules.Order order=new PipelineRules.Order();
            for(int sequence=1;sequence<=PipelineRules.FRAMES;sequence++){
                try(BoundedFrameQueue<PipelinePacket>.Lease lease=queue.take(12000)){
                    if(lease==null)throw new IOException("PIPE_SOURCE_FRAME_COUNT");PipelinePacket packet=lease.value();long pts=order.admit(packet.sequence,packet.pts);consumerEntered.countDown();
                    if(consumerRelease!=null && !consumerRelease.await(10,TimeUnit.SECONDS))throw new IOException("PIPE_CONSUMER_GATE_TIMEOUT");
                    if(fault.equals("consumer-slow") && sequence==1){long stop=System.nanoTime()+TimeUnit.SECONDS.toNanos(20);while(queue.snapshot().offers==0 && first.get()==null && !cancellation() && System.nanoTime()<stop)Thread.sleep(10);if(queue.snapshot().offers==0 && first.get()==null)throw new IOException("PIPE_QUEUE_PROBE_UNREACHED");Thread.sleep(700);}if(fault.equals("consumer-lost"))throw new IOException("PIPE_CONSUMER_LOST");if(cancellation() || first.get()!=null)throw new IOException("PIPE_CANCELLED");
                    encoder.frame(packet,pts);timeline[sequence-1]=pts;sourceThumbs.add(packet.thumb());
                }
            }
            producer.get(10000,TimeUnit.MILLISECONDS);if(first.get()!=null || !sourceReleased())throw new IOException("PIPE_SOURCE_RELEASE_UNPROVEN");
            encoder.finish(timeline[PipelineRules.FRAMES-1]);if(!encoder.close())throw new IOException("PIPE_CODEC_CLOSE_UNPROVEN");if(!sink.finishWriter())throw new IOException("PIPE_OUTPUT_FINALIZE_FAILED");
            sink.corruptForTest();PipelineRules.timeline(timeline);String before=sink.digest();outputBytes=sink.bytes();CpuTaskClient verifier=new CpuTaskClient(context,sink.validationSource());active=verifier;
            Throwable verificationFailure=null;try{verifier.verificationTimeline(timeline);verifier.start(CpuTaskClient.MP4_H264,0,CpuTaskClient.VERIFY_OUTPUT);verifier.awaitVerification(15000);verified=verifier.verificationFrames().size();}
            catch(Exception|Error failure){verificationFailure=failure;throw failure;}
            finally{try{boolean clean=false;try{clean=verifier.stopAndAwait(5000);}finally{verifier.close();if(!clean)unreleased.add(verifier);else active=null;}if(!clean)throw new IOException("PIPE_VERIFY_RELEASE_UNPROVEN");}catch(Exception|Error cleanup){if(verificationFailure!=null)verificationFailure.addSuppressed(cleanup);else throw cleanup;}}
            PipelineValidationReceipt proof=PipelineValidationReceipt.prove(verifier,sourceThumbs,before,sink.digest(),outputBytes);sink.accept(proof);coordinator.validating();
            if(cancellation())coordinator.cancel();try{token=coordinator.finalizeReady(true);}catch(IOException unknown){if(coordinator.state()!=SinkCoordinator.State.READY_UNKNOWN)throw unknown;if(coordinator.reconcile()!=SinkCoordinator.State.READY)throw unknown;token=coordinator.token();}
            ready=true;StageLog.event("PIPE_READY","export="+id+" frames="+verified+" audio_present=false output_bytes="+outputBytes+" source_unchanged_by_contract=true");
        }catch(Throwable error){error(error,"PIPE_ENCODER_OR_VALIDATION_FAILED");}
        finally{
            if(!ready){cancelled.set(true);queue.cancel();CpuTaskClient cpu=active;if(cpu!=null)cpu.cancel();}
            if(producer!=null)try{producer.get(5000,TimeUnit.MILLISECONDS);}catch(Exception pending){StageLog.event("PIPE_PRODUCER_PENDING","export="+id);}
            if(encoder!=null && !encoder.close())first.compareAndSet(null,"PIPE_CODEC_CLOSE_UNPROVEN");if(sink!=null){if(!sink.closeHandles())first.compareAndSet(null,"PIPE_OUTPUT_CLOSE_UNPROVEN");try{outputBytes=sink.bytes();}catch(IOException ignored){}
                if(!ready && sink.writerReleased())try{coordinator.cancel();coordinator.abortBeforeReady();if(coordinator.state()==SinkCoordinator.State.READY){ready=true;token=coordinator.token();}}catch(IOException pending){StageLog.failure("PIPE_ABORT_PENDING",pending);}
                if(coordinator!=null){long end=System.nanoTime()+TimeUnit.SECONDS.toNanos(1);while(coordinator.pendingCallbacks()!=0 && System.nanoTime()<end)try{Thread.sleep(5);}catch(InterruptedException interrupted){Thread.currentThread().interrupt();break;}if(coordinator.pendingCallbacks()==0)ownerClosed=sink.closeOwner();}
            }
            if(coordinator!=null)coordinator.closeExecutor();sourceThumbs.clear();runnerFinished=true;tryRelease();Report report=new Report(this);log(report);result.complete(report);
        }
    }
    private boolean sourceReleased(){return (producer==null || producer.isDone()) && unreleased.isEmpty() && active==null && CpuTaskClient.quarantinedSources()==0;}
    private void tryRelease(){if(runnerFinished && sourceReleased() && (encoder==null || encoder.released()) && sink!=null && sink.writerReleased() && ownerClosed && queue.snapshot().released() && (coordinator==null || coordinator.pendingCallbacks()==0) && released.compareAndSet(false,true)){OWNERS.remove(this);BUDGET.release();}}
    public void cancel(){if(!ready)first.compareAndSet(null,"PIPE_CANCELLED");cancelled.set(true);if(coordinator!=null)coordinator.cancel();queue.cancel();CpuTaskClient cpu=active;if(cpu!=null)cpu.cancel();}
    public Report await(long ms)throws Exception{try{return result.get(ms,TimeUnit.MILLISECONDS);}catch(TimeoutException timeout){cancel();throw new IOException("PIPE_PENDING");}}
    public Report query(){tryRelease();Report report=new Report(this);log(report);return report;}
    public Report recover(long ms)throws Exception{if(Looper.myLooper()==Looper.getMainLooper())throw new IOException("PIPE_MAIN_THREAD");if(ms<1 || ms>15000)throw new IOException("PIPE_RECOVERY_BUDGET");for(CpuTaskClient cpu:unreleased)if(cpu.recover(ms,true)){unreleased.remove(cpu);if(active==cpu)active=null;}if(runnerFinished && sourceReleased() && (encoder==null || encoder.released()) && sink!=null && sink.writerReleased() && coordinator!=null && coordinator.pendingCallbacks()==0)ownerClosed=sink.closeOwner();tryRelease();return query();}
    public int sinkFaultHits(){return sink==null?0:sink.hits;}public static int reservedEncoderOutputSlots(){return 1-BUDGET.availablePermits();}
    public static List<String> quarantinedIds(){List<String> ids=new ArrayList<>();for(RealFramePipeline p:OWNERS)ids.add(p.id);return List.copyOf(ids);}
    private void log(Report r){StageLog.event("PIPE_LEDGER","export="+id+" status="+r.status+" error="+r.error+" received="+r.received+" encoder_inputs="+r.inputs+" encoded_samples="+r.outputs+" verified="+r.verified+" queue_peak="+r.queuePeak+" frame_consumers="+r.consumers+" source_released="+r.sourceReleased+" codec_released="+r.codecReleased+" writer_released="+r.writerReleased+" frames_released="+r.framesReleased+" resources_released="+r.resourcesReleased+" encoder_output_slots="+reservedEncoderOutputSlots()+" surface_created=false audio_present=false");}
    @Override public void close(){if(!runnerFinished)cancel();}
}
