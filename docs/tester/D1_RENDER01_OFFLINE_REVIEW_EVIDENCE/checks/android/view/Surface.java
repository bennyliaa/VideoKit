package android.view;
import android.graphics.*;
import java.util.concurrent.*;
public final class Surface {
 public static final CountDownLatch entered=new CountDownLatch(1),proceed=new CountDownLatch(1);
 public static volatile int posts;
 public Surface(SurfaceTexture texture){}
 public Canvas lockCanvas(Object rect){entered.countDown();try{if(!proceed.await(3,TimeUnit.SECONDS))throw new AssertionError("controlled latch not released");}catch(InterruptedException e){throw new AssertionError(e);}return new Canvas();}
 public void unlockCanvasAndPost(Canvas same){posts++;} public void release(){}
}
