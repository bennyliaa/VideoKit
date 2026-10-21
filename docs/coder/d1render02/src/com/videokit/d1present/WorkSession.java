package com.videokit.d1present;
import com.videokit.spike.e4.E13SourceGroup;
import java.io.IOException;
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.*;

/** One finite session. Platform calls occur only in the two original owner threads.
 * The reaper joins those SAME threads before closing either original source consumer.
 * Timeout/cancel invalidates admission; it never proves native/platform return.
 */
public final class WorkSession {
    public interface Factory {PresentationSource load(String task,String version,Limits.Pixels pixels,long deadline)throws Exception;boolean returned();default void cancel(){}}
    public interface RenderPort {
        boolean draw(byte[] rgba,RawFrame frame,long epoch,long surface,PlaybackGate gate)throws Exception;
        void close()throws Exception;boolean returned();
    }
    public interface AudioPort {
        int write(byte[] pcm,int bytes,long epoch,PlaybackGate gate,java.util.function.BooleanSupplier audible,long deadline)throws Exception;
        void drain(long deadline,PlaybackGate gate,java.util.function.BooleanSupplier audible)throws Exception;
        void close()throws Exception;boolean returned();
    }
    private static final Set<WorkSession> KEEPERS=ConcurrentHashMap.newKeySet();
    public final String task=UUID.randomUUID().toString(),sourceVersion;
    public final PlaybackGate gate;public final Limits.Pixels pixels=new Limits.Pixels();
    public final Lane<VideoJob> video=new Lane<>(2);public final Lane<AudioJob> audio=new Lane<>(4);
    private final Factory factory;private final RenderPort renderPort;private final AudioPort audioPort;
    private final E13SourceGroup group;private final E13SourceGroup.Identity sourceIdentity;
    private volatile PresentationSource source;private volatile E13SourceGroup.Consumer renderSource,audioSource;
    private final AtomicBoolean audible=new AtomicBoolean();private final CountDownLatch terminal=new CountDownLatch(1);
    private final List<String> frameReceipts=new ArrayList<>(6);
    private final List<String> consumerReceipts=new ArrayList<>(3);
    private final Semaphore originalChange=new Semaphore(0);private final AtomicReference<String> failure=new AtomicReference<>();
    private Thread coordinator,renderThread,audioThread;private Future<PresentationSource> loader;
    private volatile boolean returned,renderConsumerReturned,audioConsumerReturned,stopped,bodyCompleted;private volatile int drawn,pcmSubmitted,oldRejected;
    private final long deadline;
    public WorkSession(int uid,int pid,String version,Factory factory,RenderPort render,AudioPort audio)throws IOException {
        sourceVersion=Objects.requireNonNull(version);this.factory=Objects.requireNonNull(factory);renderPort=Objects.requireNonNull(render);audioPort=Objects.requireNonNull(audio);
        synchronized(KEEPERS){if(!KEEPERS.isEmpty())throw new IOException("ONE_PRESENTATION_SESSION_PENDING");KEEPERS.add(this);}
        gate=new PlaybackGate(task,version);
        sourceIdentity=new E13SourceGroup.Identity(uid,pid,task,1,version);group=new E13SourceGroup(sourceIdentity);
        deadline=System.nanoTime()+Limits.WINDOW_NS;
    }
    public synchronized void start()throws IOException {
        if(coordinator!=null)throw new IOException("SESSION_ONCE");
        coordinator=new Thread(this::run,"d1-presentation-original-coordinator");coordinator.start();
    }
    private void fail(Throwable t){
        Throwable original=t;for(int i=0;i<8&&(original instanceof ExecutionException||original instanceof CompletionException)&&original.getCause()!=null;i++)original=original.getCause();
        String message=original.getMessage();String code=message!=null&&message.matches("[A-Z][A-Z0-9_]{2,80}")?message:
            original instanceof IOException?"IO_FAILURE_REDACTED":"PLATFORM_FAILURE_REDACTED";
        failure.compareAndSet(null,code);factory.cancel();gate.cancel();video.clearQueued();audio.clearQueued();video.end();audio.end();
    }
    private void within()throws IOException{if(System.nanoTime()>deadline)throw new IOException("PRESENTATION_OBSERVATION_EXPIRED");if(gate.cancelled())throw new IOException("SESSION_CANCELLED");}
    private void run(){
        try{
            loader=group.submit(()->factory.load(task,sourceVersion,pixels,deadline));
            source=loader.get();within();
            RawFrame first=source.frames.get(0);
            if(!first.task.equals(task)||!first.sourceVersion.equals(sourceVersion)||first.epoch!=sourceIdentity.epoch)
                throw new IOException("SOURCE_TASK_VERSION_REJECTED");
            if(!PcmFixture.sha(source.pcm).equals(PcmFixture.SHA256))throw new IOException("PCM_FIXTURE_HASH_REJECTED");
            renderSource=group.consumer(sourceIdentity,source);audioSource=group.consumer(sourceIdentity,source);
            renderSource.open(sourceIdentity);audioSource.open(sourceIdentity);
            renderThread=new Thread(this::render,"d1-original-render-owner");audioThread=new Thread(this::sound,"d1-original-audio-owner");
            renderThread.start();audioThread.start();
            for(int i=0;i<source.frames.size();i++){
                VideoJob job=new VideoJob(i,gate.epoch(),gate.surface());
                while(!video.offer(job)){within();job=new VideoJob(i,gate.epoch(),gate.surface());Thread.sleep(2);}
            }video.end();
            for(int offset=0;offset<source.pcm.length;offset+=Limits.PCM_BLOCK){
                AudioJob job=new AudioJob(offset,Math.min(Limits.PCM_BLOCK,source.pcm.length-offset),gate.epoch());
                while(!audio.offer(job)){within();job=new AudioJob(offset,Math.min(Limits.PCM_BLOCK,source.pcm.length-offset),gate.epoch());Thread.sleep(2);}
            }audio.end();
        }catch(Throwable t){fail(t);}
        finally{
            video.end();audio.end();
            try{
                // Never join on UI; any unknown platform call leaves this exact coordinator strong-held.
                if(renderThread!=null)renderThread.join();
                if(renderSource!=null&&renderPort.returned()){renderSource.close();renderConsumerReturned=true;consumerReceipt("RENDER_ORIGINAL_THREAD_JOINED_AND_CONSUMER_CLOSED");}
                if(audioThread!=null)audioThread.join();
                if(audioSource!=null&&audioPort.returned()){audioSource.close();audioConsumerReturned=true;consumerReceipt("AUDIO_ORIGINAL_THREAD_JOINED_AND_CONSUMER_CLOSED");}
                // A pre-start failure still owns ports supplied by the Activity; close only off UI.
                if(renderThread==null){renderPort.close();renderConsumerReturned=renderPort.returned();}
                if(audioThread==null){audioPort.close();audioConsumerReturned=audioPort.returned();}
                if(!factory.returned()||!renderPort.returned()||!audioPort.returned()){
                    failure.compareAndSet(null,"ORIGINAL_PLATFORM_OR_CPU_RETURN_UNKNOWN");
                    for(;;)originalChange.acquire(); // Retain exact original owners; no timer-to-release/retry.
                }
                group.closeAll();
                // This includes original loader thread and the bridge's ORIGINAL executors.
                group.awaitOriginalReturns();
                if(!group.tryReturn())throw new IOException("SOURCE_ORIGINAL_RETURN_UNPROVEN");
                if(source!=null)source.dispose();
                bodyCompleted=true; // An external observer must still join this SAME coordinator.
            }catch(Throwable unknown){failure.compareAndSet(null,"REAPER_ORIGINAL_RETURN_UNKNOWN");}
            stopped=true;
        }
    }
    private void read(E13SourceGroup.Consumer consumer,long at,byte[] out,int count)throws IOException {
        consumer.seek(sourceIdentity,at);int total=0;
        while(total<count){int n=consumer.read(sourceIdentity,out,total,Math.min(65536,count-total));if(n<1)throw new IOException("PRESENTATION_SHORT_SOURCE");total+=n;}
    }
    private void render(){
        try{
            long began=System.nanoTime(),activeEpoch=gate.epoch();int epochIndex=0;VideoJob j;
            while((j=video.take(deadline))!=null){
                try{
                    long e=j.epoch,s=j.surface;
                    if(!gate.current(e)||s!=gate.surface()){
                        oldRejected++;if(gate.cancelled())continue;
                        // Explicit accepted seek/Surface intent creates a NEW admission, never relabels
                        // the rejected original frame as returned or submits its old generation.
                        e=gate.epoch();s=gate.surface();
                    }
                    if(activeEpoch!=e){activeEpoch=e;epochIndex=0;began=System.nanoTime();}
                    int index=Math.min(epochIndex++,source.frames.size()-1);RawFrame f=source.frames.get(index);long target=began+(f.ptsUs-source.frames.get(0).ptsUs)*1000;
                    while(System.nanoTime()<target&&gate.current(e)&&System.nanoTime()<deadline)Thread.sleep(2);
                    while(gate.paused()&&gate.current(e)){within();Thread.sleep(2);}
                    if(!gate.accepts(e,s)){oldRejected++;continue;}
                    within();int n=f.pixels.length;pixels.acquire(n);byte[] bytes=null;
                    try{bytes=new byte[n];read(renderSource,source.offset(index),bytes,n);if(gate.accepts(e,s)&&renderPort.draw(bytes,f,e,s,gate)){
                        drawn++;synchronized(frameReceipts){frameReceipts.add("task="+task+" sourceVersion="+sourceVersion+" producer="+f.producerTask+" producerEpoch="+f.producerEpoch+" raw="+f.rawTimestamp+" timeBase="+f.timeBaseNum+"/"+f.timeBaseDen+" ptsUs="+f.ptsUs+" rotation="+f.rotation+" playEpoch="+e+" surfaceGeneration="+s+" bitmapDrawn=true postReturned=true currentAfterPost="+gate.accepts(e,s));}
                    }else oldRejected++;}
                    finally{bytes=null;pixels.release(n);}
                }finally{video.returned(j);}
            }
        }catch(Throwable t){fail(t);}finally{try{renderPort.close();}catch(Throwable t){fail(t);}}
    }
    private void sound(){
        try{
            byte[] block=new byte[Limits.PCM_BLOCK];AudioJob j;
            while((j=audio.take(deadline))!=null){
                try{within();if(!gate.current(j.epoch)){oldRejected++;continue;}
                    read(audioSource,source.pcmOffset+j.offset,block,j.count);
                    pcmSubmitted+=audioPort.write(block,j.count,j.epoch,gate,audible::get,deadline);
                }finally{audio.returned(j);}
            }if(!gate.cancelled())audioPort.drain(deadline,gate,audible::get);
        }catch(Throwable t){fail(t);}finally{try{audioPort.close();}catch(Throwable t){fail(t);}}
    }
    public void mute(boolean muted){audible.set(!muted);}public boolean audibleRequested(){return audible.get();}
    public void pause(boolean value)throws IOException{gate.pause(value);}
    public long seek()throws IOException{long e=gate.seek();video.clearQueued();audio.clearQueued();return e;}
    public void cancel(){factory.cancel();gate.cancel();video.clearQueued();audio.clearQueued();video.end();audio.end();}
    public boolean await(long millis)throws InterruptedException{Thread t=coordinator;if(t==null)return false;t.join(millis);return tryReturn();}
    private synchronized boolean tryReturn(){if(returned)return true;Thread t=coordinator;if(t==null||t.isAlive()||!bodyCompleted)return false;try{t.join();}catch(InterruptedException e){Thread.currentThread().interrupt();return false;}returned=true;KEEPERS.remove(this);terminal.countDown();return true;}
    public boolean returned(){return tryReturn();}public boolean sourceReleased(){return group.snapshot().released();}
    public boolean renderConsumerReturned(){return renderConsumerReturned;}public boolean audioConsumerReturned(){return audioConsumerReturned;}
    public String failure(){return failure.get();}
    public int drawn(){return drawn;}public int pcmSubmitted(){return pcmSubmitted;}
    public List<String> frameReceipts(){synchronized(frameReceipts){return List.copyOf(frameReceipts);}}
    private void consumerReceipt(String stage){com.videokit.spike.c14.LeaseRegistry.Snapshot s=group.snapshot();synchronized(consumerReceipts){if(consumerReceipts.size()<3)consumerReceipts.add(stage+" generation="+s.generation+" retired="+s.retired+" consumers="+s.consumers+" operations="+s.operations+" failedCloses="+s.failedCloses+" sourceReleased="+s.released());}}
    public List<String> consumerReceipts(){synchronized(consumerReceipts){return List.copyOf(consumerReceipts);}}
    public String state(){tryReturn();return "task="+task+" version="+sourceVersion+" epoch="+gate.epoch()+" surface="+gate.surface()+" renderAck="+gate.renderAcknowledged()+" audioAck="+gate.audioAcknowledged()+" drawn="+drawn+" pcmSubmitted="+pcmSubmitted+" oldRejected="+oldRejected+" rawQueue="+video.queued()+" rawInFlight="+video.inFlight()+" pcmQueue="+audio.queued()+" pcmInFlight="+audio.inFlight()+" pixelHeld="+pixels.held()+" pixelPeak="+pixels.peak()+" renderReturned="+renderConsumerReturned+" audioReturned="+audioConsumerReturned+" sourceReleased="+sourceReleased()+" originalsReturned="+returned+" coordinatorBodyEnded="+stopped+" error="+failure.get();}
    public static boolean allReturned(){for(WorkSession s:KEEPERS)s.tryReturn();return KEEPERS.isEmpty();}
    public static void awaitOriginalReturns()throws InterruptedException{for(WorkSession s:KEEPERS){Thread t=s.coordinator;if(t!=null&&t!=Thread.currentThread())t.join();s.tryReturn();}}
    public static final class VideoJob {final int index;final long epoch,surface;VideoJob(int i,long e,long s){index=i;epoch=e;surface=s;}}
    public static final class AudioJob {final int offset,count;final long epoch;AudioJob(int o,int n,long e){offset=o;count=n;epoch=e;}}
}
