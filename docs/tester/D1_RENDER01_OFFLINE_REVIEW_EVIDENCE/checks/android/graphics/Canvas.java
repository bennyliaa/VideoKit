package android.graphics;
public final class Canvas {
 public static volatile int bitmapDraws;
 public void drawColor(int x){} public void save(){} public void translate(float x,float y){}
 public int getWidth(){return 256;} public int getHeight(){return 144;}
 public void rotate(float x){} public void scale(float x,float y){} public void restore(){}
 public void drawBitmap(Bitmap b,float x,float y,Object p){bitmapDraws++;}
}
