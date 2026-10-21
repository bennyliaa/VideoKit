package com.videokit.d1present;
import java.util.*;import android.graphics.*;import android.view.Surface;import com.videokit.spike.e4.E13SourceGroup;
public final class NormalRendererCheck {
 public static void main(String[] args)throws Exception {
  Surface.reset(false);Surface.blockLock=false;Surface.blockPost=false;
  PlatformRenderer renderer=new PlatformRenderer();
  WorkSession.Factory f=new WorkSession.Factory(){volatile boolean done;public PresentationSource load(String t,String v,Limits.Pixels p,long deadline)throws Exception{List<RawFrame> frames=new ArrayList<>();for(int i=0;i<6;i++)frames.add(new RawFrame(t,v,1,i*1000,i,1,1000,4,4,16,0,new byte[64],p));done=true;return new PresentationSource(frames,PcmFixture.create());}public boolean returned(){return done;}};
  WorkSession.AudioPort audio=new WorkSession.AudioPort(){boolean done;public int write(byte[] b,int n,long epoch,PlaybackGate gate,java.util.function.BooleanSupplier audible,long deadline){if(audible.getAsBoolean())throw new AssertionError("normal entry became audible");return n;}public void drain(long d,PlaybackGate g,java.util.function.BooleanSupplier a){}public void close(){done=true;}public boolean returned(){return done;}};
  WorkSession s=new WorkSession(7,8,"normal-independent",f,renderer,audio);renderer.budget(s.pixels);renderer.attach(new SurfaceTexture(),s.gate);s.start();
  if(!s.await(3000)||s.failure()!=null||s.drawn()!=6||Canvas.bitmapDraws!=6||Surface.posts!=6||s.frameReceipts().size()!=6||s.pcmSubmitted()!=576000||!s.sourceReleased()||s.pixels.held()!=0||!WorkSession.allReturned()||!E13SourceGroup.canFinish())throw new AssertionError(s.state());
  System.out.println("PASS independent_normal_actual_renderer draws=6 posts=6 receipts=6 pcm=576000 defaultMuted=true originalsReturned=true");
 }
}
