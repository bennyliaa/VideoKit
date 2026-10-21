package com.videokit.d1present;
import java.util.*;import java.util.concurrent.*;import android.graphics.*;import android.view.Surface;
import com.videokit.spike.e4.E13SourceGroup;
public final class Render02Check {
 static void need(boolean b,String s){if(!b)throw new AssertionError(s);}
 static RawFrame frame(String t,String v,Limits.Pixels p,int i)throws Exception{return new RawFrame(t,v,1,i*1000,i,1,1000,4,4,16,0,new byte[64],p);}
 static WorkSession session(PlatformRenderer r)throws Exception{
  WorkSession.Factory f=new WorkSession.Factory(){volatile boolean done;public PresentationSource load(String t,String v,Limits.Pixels p,long d)throws Exception{List<RawFrame> fs=new ArrayList<>();for(int i=0;i<6;i++)fs.add(frame(t,v,p,i));done=true;return new PresentationSource(fs,PcmFixture.create());}public boolean returned(){return done;}};
  WorkSession.AudioPort a=new WorkSession.AudioPort(){boolean done;public int write(byte[] b,int n,long e,PlaybackGate g,java.util.function.BooleanSupplier audible,long d){return g.current(e)?n:0;}public void drain(long d,PlaybackGate g,java.util.function.BooleanSupplier a){}public void close(){done=true;}public boolean returned(){return done;}};
  WorkSession s=new WorkSession(7,8,"render02-control",f,r,a);r.budget(s.pixels);r.attach(new SurfaceTexture(),s.gate);return s;
 }
 static void race(boolean afterBitmap)throws Exception{
  Surface.reset(!afterBitmap,afterBitmap);PlatformRenderer r=new PlatformRenderer();WorkSession s=session(r);s.start();
  try{need(Surface.entered.await(2,TimeUnit.SECONDS),"original platform entered");s.cancel();need(!s.returned()&&!s.sourceReleased(),"inflight original remains held");}finally{Surface.proceed.countDown();}
  need(s.await(3000),s.state());need(s.sourceReleased()&&s.pixels.held()==0,"real source and pixels returned");
  int actual=afterBitmap?1:0;need(s.drawn()==actual&&Canvas.bitmapDraws==actual&&Surface.posts==1,"actual bitmap vs cleanup: "+s.state()+r.state());
  need(s.frameReceipts().size()==actual,"receipt count");if(afterBitmap)need(s.frameReceipts().get(0).contains("currentAfterPost=false"),"actual old event preserved");
  System.out.println("PASS "+(afterBitmap?"cancel_after_bitmap_preserves_old_post":"cancel_late_lock_cleanup_is_not_frame")+" "+r.state());
 }
 static void normal()throws Exception{Surface.reset(false,false);PlatformRenderer r=new PlatformRenderer();WorkSession s=session(r);s.start();need(s.await(3000),s.state());need(s.failure()==null&&s.drawn()==6&&Canvas.bitmapDraws==6&&Surface.posts==6,"six normal actual frames");need(s.frameReceipts().size()==6&&s.pixels.held()==0&&s.sourceReleased(),"normal receipts and original return");System.out.println("PASS normal_six_actual_frames "+r.state());}
 static void directSeekOrDestroy(boolean destroy)throws Exception{
  Surface.reset(destroy,!destroy);PlatformRenderer r=new PlatformRenderer();Limits.Pixels p=new Limits.Pixels();r.budget(p);PlaybackGate g=new PlaybackGate("direct","v");SurfaceTexture old=new SurfaceTexture();long sg=r.attach(old,g),ep=g.epoch();RawFrame f=frame("direct","v",p,0);Throwable[] failure={null};boolean[] result={false,false};
  Thread owner=new Thread(()->{try{result[0]=r.draw(f.pixels,f,ep,sg,g);result[1]=r.draw(f.pixels,f,g.epoch(),g.surface(),g);r.close();}catch(Throwable t){failure[0]=t;}});
  owner.start();try{need(Surface.entered.await(2,TimeUnit.SECONDS),"controlled owner blocked");if(destroy){need(!r.destroyed(old,g),"original owns transferred texture");r.attach(new SurfaceTexture(),g);}else g.seek();need(!r.returned(),"original not falsely returned");}finally{Surface.proceed.countDown();}
  owner.join(3000);need(!owner.isAlive()&&failure[0]==null,"same owner returned: "+failure[0]);need(result[0]==!destroy&&result[1],"old versus new admission");need(Canvas.bitmapDraws==(destroy?1:2)&&Surface.posts==2,"actual draws and posts distinct");need(r.returned(),"renderer owner returned");if(destroy)need(old.releases==1,"transferred texture released exactly once by owner");f.release();need(p.held()==0,"pixels returned");System.out.println("PASS "+(destroy?"destroy_late_lock_new_surface":"seek_after_bitmap_old_event_new_epoch")+" "+r.state());
 }
 static void manual(){ManualListenWindow w=new ManualListenWindow();need(!w.claimClick(0)&&!w.startedFromClick(),"idle no sound");w.arm(100);need(!w.startedFromClick(),"arm no start");need(w.claimClick(101)&&!w.claimClick(102),"single click");w.started();need(w.closeIdle(),"started from explicit click");ManualListenWindow late=new ManualListenWindow();late.arm(0);need(!late.claimClick(ManualListenWindow.IDLE_NS)&&!late.closeIdle(),"deadline no click");ManualListenWindow stopped=new ManualListenWindow();stopped.arm(0);stopped.closeIdle();need(!stopped.claimClick(1),"close wins late UI click");try{new ManualListenWindow().started();throw new AssertionError("no click");}catch(IllegalStateException expected){}System.out.println("PASS bounded_manual_idle_click_timeout_policy");}
 public static void main(String[] args)throws Exception{race(false);race(true);normal();directSeekOrDestroy(false);directSeekOrDestroy(true);manual();need(WorkSession.allReturned()&&E13SourceGroup.canFinish(),"no original owner leaked");System.out.println("CONTROLLED_JVM_ONLY actualAndroidVisualAndSound=NOT_RUN");}
}
