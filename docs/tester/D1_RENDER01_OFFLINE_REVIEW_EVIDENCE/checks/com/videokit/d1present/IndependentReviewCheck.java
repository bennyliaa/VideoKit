package com.videokit.d1present;
import com.videokit.spike.c14.*;
import com.videokit.spike.e4.*;
import java.util.*;
import java.io.*;
import java.util.concurrent.*;
import android.graphics.*;
import android.view.Surface;
public final class IndependentReviewCheck {
 static void need(boolean x,String s){if(!x)throw new AssertionError(s);}
 static RawFrame frame(String task,String v,Limits.Pixels p,long raw)throws Exception{return new RawFrame(task,v,1,raw*1000,raw,1,1000,4,4,16,0,new byte[64],p);}
 static void providerBoundary()throws Exception {
  Limits.Pixels p=new Limits.Pixels();RawFrame f=frame("t","v",p,1);PresentationSource source=new PresentationSource(List.of(f),PcmFixture.create());
  E13SourceGroup.Identity id=new E13SourceGroup.Identity(7,8,"t",1,"v");E13SourceGroup g=new E13SourceGroup(id);
  E13SourceGroup.Consumer a=g.consumer(id,source),b=g.consumer(id,source);
  a.open(id);b.open(id);byte[] out=new byte[10];a.seek(id,60);need(a.read(id,out,0,10)==10,"cross segment read");
  byte[] pcm=PcmFixture.create();need(Arrays.equals(Arrays.copyOfRange(out,4,10),Arrays.copyOfRange(pcm,0,6)),"raw to exact pcm boundary");
  try{a.seek(new E13SourceGroup.Identity(7,9,"t",1,"v"),0);throw new AssertionError("wrong pid admitted");}catch(IOException expected){}
  try{source.dispose();throw new AssertionError("pending handle disposed");}catch(IllegalStateException expected){}
  a.close();need(!g.snapshot().released(),"first consumer cannot release");b.seek(id,source.length-1);need(b.read(id,new byte[1])==1,"remaining consumer usable");
  b.close();g.closeAll();E13SourceGroup.awaitOriginalReturns();need(g.tryReturn(),"real original threads returned");source.dispose();need(p.held()==0,"real owned arrays released");
  try{frame("t","v",p,-1);throw new AssertionError("negative timestamp admitted");}catch(IOException expected){}
  System.out.println("PASS independent_cross_segment_identity_pending_dispose_and_original_return");
 }
 static void lateCanvasCounter()throws Exception {
  PlatformRenderer renderer=new PlatformRenderer();WorkSession.Factory factory=new WorkSession.Factory(){
   volatile boolean returned;
   public PresentationSource load(String t,String v,Limits.Pixels p,long deadline)throws Exception{List<RawFrame> fs=new ArrayList<>();for(int i=0;i<6;i++)fs.add(frame(t,v,p,i));returned=true;return new PresentationSource(fs,PcmFixture.create());}
   public boolean returned(){return returned;}
  };
  WorkSession.AudioPort audio=new WorkSession.AudioPort(){boolean done;public int write(byte[] b,int n,long e,PlaybackGate gate,java.util.function.BooleanSupplier a,long deadline){return gate.current(e)?n:0;}public void drain(long d,PlaybackGate g,java.util.function.BooleanSupplier a){}public void close(){done=true;}public boolean returned(){return done;}};
  WorkSession s=new WorkSession(7,8,"review-late-canvas",factory,renderer,audio);renderer.budget(s.pixels);renderer.attach(new SurfaceTexture(),s.gate);s.start();
  try{need(Surface.entered.await(2,TimeUnit.SECONDS),"production renderer entered controlled lockCanvas");s.cancel();need(!s.returned()&&!s.sourceReleased(),"cancel cannot release in-flight original");}finally{Surface.proceed.countDown();}
  need(s.await(3000),s.state());need(s.sourceReleased()&&s.pixels.held()==0,"same originals returned after controlled call");
  need(Canvas.bitmapDraws==0&&Surface.posts==1&&s.drawn()==1,"expected counter defect was not reproduced: "+s.state());
  System.out.println("REPRODUCED RENDER01-R02 actualWorkSessionDrawn="+s.drawn()+" controlledCanvasBitmapDraws="+Canvas.bitmapDraws+" posts="+Surface.posts+" originalsReturned="+s.returned());
  need(WorkSession.allReturned()&&E13SourceGroup.canFinish(),"review check leaves no original owner");
 }
 public static void main(String[] args)throws Exception{providerBoundary();lateCanvasCounter();System.out.println("JVM_CONTROLLED_PORTS_ONLY_ANDROID_EFFECT_NOT_RUN");}
}
