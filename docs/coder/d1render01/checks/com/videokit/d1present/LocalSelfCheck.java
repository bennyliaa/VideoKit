package com.videokit.d1present;
import com.videokit.spike.c14.*;
import com.videokit.spike.e4.*;
import java.io.*;
import java.nio.file.*;
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.*;

/** Tests real core/bridge/thread ownership with bounded ports; no Android platform/effect claims. */
public final class LocalSelfCheck {
    private static void need(boolean v,String why){if(!v)throw new AssertionError(why);}
    private interface Throwing{void run()throws Exception;}
    private static void rejects(Throwing action)throws Exception {try{action.run();throw new AssertionError("expected rejection");}catch(IOException|IllegalStateException expected){}}
    private static PresentationSource data(String task,String version,Limits.Pixels pixels)throws Exception {
        List<RawFrame> frames=new ArrayList<>();for(int i=0;i<6;i++){
            byte[] rgba=new byte[4*4*4];Arrays.fill(rgba,(byte)(i*19));for(int a=3;a<rgba.length;a+=4)rgba[a]=(byte)255;
            frames.add(new RawFrame(task,version,1,i*1000,i,1,1000,4,4,16,0,rgba,pixels));
        }return new PresentationSource(frames,PcmFixture.create());
    }
    private static final class Factory implements WorkSession.Factory {
        volatile boolean returned;PresentationSource source;boolean wrongVersion;
        public PresentationSource load(String task,String version,Limits.Pixels pixels,long deadline)throws Exception {source=data(task,wrongVersion?version+"-wrong":version,pixels);returned=true;return source;}
        public boolean returned(){return returned;}
    }
    private static final class Renderer implements WorkSession.RenderPort {
        final CountDownLatch entered=new CountDownLatch(1),release=new CountDownLatch(1),closeEntered=new CountDownLatch(1),closeRelease=new CountDownLatch(1);
        boolean holdDraw,holdClose;volatile boolean returned;int draws;
        public boolean draw(byte[] bytes,RawFrame frame,long e,long s,PlaybackGate gate)throws Exception {
            need(bytes.length==64,"actual raw view layout");entered.countDown();if(holdDraw)release.await();
            if(!gate.accepts(e,s))return false;draws++;return true;
        }
        public void close()throws Exception {closeEntered.countDown();if(holdClose)closeRelease.await();returned=true;}
        public boolean returned(){return returned;}
    }
    private static final class Audio implements WorkSession.AudioPort {
        final CountDownLatch closeEntered=new CountDownLatch(1),release=new CountDownLatch(1);
        boolean holdClose;volatile boolean returned;int bytes;boolean heardRequested;
        public int write(byte[] b,int n,long e,PlaybackGate gate,java.util.function.BooleanSupplier audible,long deadline){
            need(n<=3840&&n%4==0,"PCM block budget");if(!gate.current(e))return 0;heardRequested|=audible.getAsBoolean();bytes+=n;return n;
        }
        public void drain(long deadline,PlaybackGate gate,java.util.function.BooleanSupplier audible){}
        public void close()throws Exception {closeEntered.countDown();if(holdClose)release.await();returned=true;}
        public boolean returned(){return returned;}
    }
    private static WorkSession session(Factory f,Renderer r,Audio a)throws Exception {WorkSession s=new WorkSession(10001,123,"selfcheck-source-v1",f,r,a);s.gate.attach();s.start();return s;}
    private static void queueAndGeneration()throws Exception {
        Lane<Object> q=new Lane<>(2);Object a=new Object(),b=new Object(),c=new Object();need(q.offer(a)&&q.offer(b)&&!q.offer(c),"queue2 actual backpressure");
        need(q.take(System.nanoTime()+1000000)==a,"same queued object");rejects(()->q.take(System.nanoTime()));
        q.clearQueued();need(q.inFlight()==1&&q.queued()==0,"clear must retain actual inFlight");q.returned(a);q.end();need(q.take(System.nanoTime())==null,"ended empty");
        PlaybackGate g=new PlaybackGate("task","version");long surf=g.attach(),e=g.epoch();need(g.accepts(e,surf),"initial current");g.pause(true);need(!g.accepts(e,surf),"pause");g.pause(false);g.seek();need(!g.accepts(e,surf),"seek old epoch");g.detach(surf);need(!g.accepts(g.epoch(),surf),"destroy old Surface generation");g.cancel();rejects(g::attach);
        Limits.layout(1920,1080,7680,8294400,270);rejects(()->Limits.layout(1921,1080,7684,8298720,0));rejects(()->Limits.layout(Integer.MAX_VALUE,2,0,4,0));
        Limits.Pixels p=new Limits.Pixels();p.acquire(Limits.PIXELS);rejects(()->p.acquire(1));need(p.held()==Limits.PIXELS,"rejected allocation never charged");p.release(Limits.PIXELS);
        PlaybackGate ack=new PlaybackGate("ack","v");long s=ack.attach();ack.renderAck(1,s);ack.audioAck(1);need(ack.renderAcknowledged()&&ack.audioAcknowledged(),"actual owner ACK");ack.seek();need(!ack.renderAcknowledged()&&!ack.audioAcknowledged(),"UI intent never synthesizes owner ACK");
        System.out.println("PASS queue_generation_layout_budget");
    }
    private static void focusPolicy()throws Exception {
        AudioFocusPolicy p=new AudioFocusPolicy();need(!p.requestNeeded(false)&&p.gain(false)==0,"default no focus/muted");
        p.audible(true);need(p.requestNeeded(false),"explicit listen requests focus once");p.requestEntered();p.requestReturned(false);
        need(!p.requestNeeded(false)&&p.gain(false)==0,"focus denial must stay muted without per-block request retry");
        p.audible(false);p.audible(true);p.requestEntered();p.requestReturned(true);need(p.gain(false)>0&&p.gain(true)==0,"granted/paused policy");
        p.lost();need(p.gain(false)==0&&!p.requestNeeded(false),"loss cannot auto restart or request loop");p.audible(false);need(p.gain(false)==0,"all mute");p.closed();p.audible(true);need(!p.requestNeeded(false)&&p.gain(false)==0,"closed never audible");
        System.out.println("PASS actual_audio_focus_policy_denial_loss_mute_no_retry");
    }
    private static void dualConsumersAudioLast()throws Exception {
        Factory f=new Factory();Renderer r=new Renderer();Audio a=new Audio();a.holdClose=true;WorkSession s=session(f,r,a);
        try{
            need(a.closeEntered.await(2,TimeUnit.SECONDS),"audio close entered");need(r.closeEntered.await(2,TimeUnit.SECONDS),"render close entered");
            long end=System.nanoTime()+1000000000;while(!s.renderConsumerReturned()&&System.nanoTime()<end)Thread.sleep(1);
            need(s.renderConsumerReturned(),"render thread actually joined then consumer closed");need(!s.audioConsumerReturned()&&!s.sourceReleased()&&!s.returned(),"one close cannot release whole source");
        }finally{a.release.countDown();}
        need(s.await(2000),s.state());need(s.failure()==null&&s.sourceReleased(),s.state());need(f.source.opens()==2&&f.source.closes()==2,"same provider exactly two physical handles");
        need(s.pixels.held()==0&&f.source.frames.get(0).pixels==null,"actual retained pixels dropped, not only counters");need(a.bytes==576000&&!a.heardRequested,"default mute/3sec bound");
        need(s.video.peak()<=2&&s.audio.peak()<=4,"actual queue peaks");System.out.println("PASS real_shared_source_audio_last "+s.state());
    }
    private static void cancelInFlightAndOriginalThreadTail()throws Exception {
        Factory f=new Factory();Renderer r=new Renderer();r.holdDraw=true;r.holdClose=true;Audio a=new Audio();WorkSession s=session(f,r,a);
        try{
            need(r.entered.await(2,TimeUnit.SECONDS),"original draw entered");long e=s.gate.epoch(),surface=s.gate.surface();
            long at=System.nanoTime();s.cancel();need(System.nanoTime()-at<100000000,"cancel metadata call is bounded");
            need(!s.gate.accepts(e,surface),"late draw old generation rejected");need(s.video.inFlight()==1&&!s.sourceReleased()&&!s.returned(),"cancel is not actual draw return");
            r.release.countDown();need(r.closeEntered.await(2,TimeUnit.SECONDS),"original close tail entered");
            need(!s.renderConsumerReturned()&&!s.returned(),"owner body/close entry is not original thread termination");
        }finally{r.release.countDown();r.closeRelease.countDown();}
        need(s.await(2000),s.state());need(s.sourceReleased()&&s.pixels.held()==0,"cancel actual cleanup");System.out.println("PASS cancel_late_frame_and_original_thread_tail");
    }
    private static void wrongVersionBeforePlatform()throws Exception {
        Factory f=new Factory();f.wrongVersion=true;Renderer r=new Renderer();Audio a=new Audio();WorkSession s=session(f,r,a);
        need(s.await(2000),s.state());need("SOURCE_TASK_VERSION_REJECTED".equals(s.failure()),s.state());
        need(r.draws==0&&a.bytes==0&&f.source.opens()==0,"wrong source never opened or delivered to platform ports");
        need(s.sourceReleased()&&s.pixels.held()==0,"rejected owned buffers really disposed");System.out.println("PASS wrong_source_version_rejected_before_platform");
    }
    private static void loaderCauseAndPathRedaction()throws Exception {
        for(String message:List.of("SOURCE_LAYOUT_REJECTED","synthetic-private-path/credential-should-not-be-reported")){
            WorkSession.Factory f=new WorkSession.Factory(){public PresentationSource load(String t,String v,Limits.Pixels p,long deadline)throws Exception{throw new IOException(message);}public boolean returned(){return true;}};
            Renderer r=new Renderer();Audio a=new Audio();WorkSession s=new WorkSession(10001,123,"cause-test",f,r,a);s.start();
            need(s.await(2000),s.state());String expected=message.equals("SOURCE_LAYOUT_REJECTED")?message:"IO_FAILURE_REDACTED";
            need(expected.equals(s.failure()),"actual Future cause must map to stable/redacted code");need(s.sourceReleased()&&s.pixels.held()==0&&r.draws==0&&a.bytes==0,"failed load closes only real originals");
        }
        System.out.println("PASS actual_loader_future_cause_and_path_redaction");
    }
    private static void closeFailureAndLateReturn()throws Exception {
        E13SourceGroup.Identity id=new E13SourceGroup.Identity(10001,23,"close-test",1,"v1");E13SourceGroup g=new E13SourceGroup(id);
        AtomicInteger opens=new AtomicInteger();List<CompletableFuture<Void>> closes=new ArrayList<>();AtomicInteger firstAttempts=new AtomicInteger();
        AsyncReadBridge.Provider provider=c->{int index=opens.getAndIncrement();CompletableFuture<Void> close=new CompletableFuture<>();closes.add(close);
            return CompletableFuture.completedFuture(new AsyncReadBridge.Handle(){public Long length(){return 8L;}public CompletionStage<Integer> readAt(long p,byte[] b,int o,int n,AsyncReadBridge.Cancellation token){Arrays.fill(b,o,o+n,(byte)7);return CompletableFuture.completedFuture(n);}public CompletionStage<Void> closeAsync(){if(index==0&&firstAttempts.incrementAndGet()==1){CompletableFuture<Void> fail=new CompletableFuture<>();fail.completeExceptionally(new IOException("FINITE_CLOSE_FAILURE"));return fail;}return close;}});};
        E13SourceGroup.Consumer a=g.consumer(id,provider),b=g.consumer(id,provider);
        try{
            a.open(id);b.open(id);a.close();long end=System.nanoTime()+1000000000;while(a.closeState()!=AsyncReadBridge.CloseState.FAILED&&System.nanoTime()<end)Thread.sleep(1);
            need(g.snapshot().closeFailed&&!g.snapshot().released(),"failed original close retained");
            b.close();CompletableFuture<Void> retry=a.retryFailedClose();need(!retry.isDone(),"same original retry pending");closes.get(0).complete(null);retry.get(1,TimeUnit.SECONDS);
            need(!g.snapshot().released(),"other original handle pending retains source");closes.get(1).complete(null);
            need(g.awaitReturn(1000),"both original operations actually returned");
        }finally{for(CompletableFuture<Void> close:closes)close.complete(null);g.closeAll();a.retryFailedClose().get(1,TimeUnit.SECONDS);g.awaitReturn(1000);}
        need(firstAttempts.get()==2&&opens.get()==2,"one explicit retry on actual original close");System.out.println("PASS close_failure_late_return_same_registry");
    }
    public static void main(String[] args)throws Exception {
        queueAndGeneration();focusPolicy();RuntimeOriginalThreadCheck.run();dualConsumersAudioLast();cancelInFlightAndOriginalThreadTail();wrongVersionBeforePlatform();loaderCauseAndPathRedaction();closeFailureAndLateReturn();
        byte[] pcm=PcmFixture.create();need(pcm.length==576000&&Arrays.equals(pcm,PcmFixture.create()),"deterministic exact PCM");
        int peak=0;for(int i=0;i<pcm.length;i+=2)peak=Math.max(peak,Math.abs((short)((pcm[i]&255)|(pcm[i+1]<<8))));need(peak<=257,"low amplitude source");
        if(args.length==1){Path out=Paths.get(args[0]);Files.createDirectories(out.getParent());Files.write(out,pcm,StandardOpenOption.CREATE_NEW);}
        need(WorkSession.allReturned()&&E13SourceGroup.canFinish(),"no selfcheck original owners retained");
        System.out.println("PASS pcm_identity sha256="+PcmFixture.sha(pcm)+" bytes="+pcm.length+" peak="+peak+" seed="+PcmFixture.SEED);
        System.out.println("PASS_OFFLINE_CORE_ONLY Android/Surface/AudioTrack/screenshots/listening NOT_RUN");
    }
}
