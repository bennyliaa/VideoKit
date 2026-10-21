package android.graphics;
public final class Bitmap {
 public enum Config {ARGB_8888}
 private final int bytes; private Bitmap(int w,int h){bytes=w*h*4;}
 public static Bitmap createBitmap(int w,int h,Config c){return new Bitmap(w,h);}
 public int getAllocationByteCount(){return bytes;}
 public void setPixels(int[] p,int off,int stride,int x,int y,int w,int h){}
 public void recycle(){}
}
