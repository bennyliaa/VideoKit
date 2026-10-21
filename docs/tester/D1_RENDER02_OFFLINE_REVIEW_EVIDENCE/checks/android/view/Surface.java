package android.view;
import android.graphics.*; import java.util.concurrent.*;
public final class Surface {
 public static CountDownLatch entered,proceed; public static volatile int posts; public static volatile boolean blockLock,blockPost;
 public static void reset(boolean afterBitmap){entered=new CountDownLatch(1);proceed=new CountDownLatch(1);posts=0;Canvas.bitmapDraws=0;blockLock=!afterBitmap;blockPost=afterBitmap;}
 public Surface(SurfaceTexture t){}
 private static void hold(){entered.countDown();try{if(!proceed.await(3,TimeUnit.SECONDS))throw new AssertionError("controlled latch not released");}catch(InterruptedException e){throw new AssertionError(e);}}
 public Canvas lockCanvas(Object rect){if(blockLock){blockLock=false;hold();}return new Canvas();}
 public void unlockCanvasAndPost(Canvas same){if(blockPost){blockPost=false;hold();}posts++;}public void release(){}
}
