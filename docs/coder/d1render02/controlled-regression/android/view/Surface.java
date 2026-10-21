package android.view;
import android.graphics.*;import java.util.concurrent.*;
public final class Surface {
 public static volatile CountDownLatch entered,proceed;public static volatile int posts,releases;public static volatile boolean blockLock,blockPost;
 public static void reset(boolean lock,boolean post){entered=new CountDownLatch(1);proceed=new CountDownLatch(1);posts=0;releases=0;blockLock=lock;blockPost=post;Canvas.bitmapDraws=0;}
 static void hold(){entered.countDown();try{if(!proceed.await(3,TimeUnit.SECONDS))throw new AssertionError("original call not released");}catch(InterruptedException e){throw new AssertionError(e);}}
 public Surface(SurfaceTexture t){}public Canvas lockCanvas(Object r){if(blockLock){blockLock=false;hold();}return new Canvas();}
 public void unlockCanvasAndPost(Canvas same){if(blockPost){blockPost=false;hold();}posts++;}public void release(){releases++;}
}