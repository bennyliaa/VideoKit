package com.videokit.d1present;
import java.io.IOException;
public final class Limits {
    public static final int FRAMES=6,WIDTH=1920,HEIGHT=1080,RGBA=8294400,RAW_QUEUE=2,PCM_QUEUE=4;
    public static final int RATE=48000,CHANNELS=2,PCM_BLOCK=3840,PCM_BYTES=576000;
    public static final long PIXELS=64L*1024*1024,WINDOW_NS=30000000000L;
    public static int layout(int w,int h,int stride,int bytes,int rotation)throws IOException {
        long n=(long)w*h*4;
        if(w<1||h<1||w>WIDTH||h>HEIGHT||stride!=w*4||n>RGBA||bytes!=n||
                (rotation!=0&&rotation!=90&&rotation!=180&&rotation!=270))throw new IOException("RAW_LAYOUT_REJECTED");
        return (int)n;
    }
    public static final class Pixels {
        private long held,peak;
        public synchronized void acquire(long n)throws IOException {
            if(n<0||n>PIXELS-held)throw new IOException("PIXEL_BUDGET_REJECTED");
            held+=n;peak=Math.max(peak,held);
        }
        public synchronized void release(long n){if(n<0||n>held)throw new IllegalStateException("PIXEL_UNDERFLOW");held-=n;}
        public synchronized long held(){return held;}public synchronized long peak(){return peak;}
    }
    private Limits(){}
}
