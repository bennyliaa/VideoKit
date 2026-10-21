package com.videokit.d1present;
import android.graphics.*;
import android.view.Surface;
import java.io.IOException;
import java.util.*;

/** Canvas/Bitmap calls run only in the dedicated presentation-process render owner.
 * TextureView destruction returns false while its original Surface producer is held: the
 * ORIGINAL owner releases Surface, then the transferred SurfaceTexture after unlock returns.
 */
public final class PlatformRenderer implements WorkSession.RenderPort {
    private static final class Ticket {
        final SurfaceTexture texture;final long generation;boolean destroyed,finished,textureReturned;
        Surface surface;
        Ticket(SurfaceTexture t,long g){texture=t;generation=g;}
    }
    private final List<Ticket> tickets=new ArrayList<>();private Limits.Pixels pixels;
    private volatile boolean closed,unknown;private Ticket active;private Bitmap heldBitmap;private int[] heldArgb;private long bitmapBytes,argbBytes;
    private Thread owner;private int submitted;private long lastPts=-1;private Canvas heldCanvas;
    public void budget(Limits.Pixels p){pixels=p;}
    /** UI metadata only; no Surface/Bitmap native call or wait. Bounded to eight availability events. */
    public synchronized long attach(SurfaceTexture texture,PlaybackGate gate)throws IOException {
        if(closed||unknown||tickets.size()>=8)throw new IOException("RENDER_SURFACE_ADMISSION");
        long generation=gate.attach();tickets.add(new Ticket(texture,generation));return generation;
    }
    public synchronized boolean destroyed(SurfaceTexture same,PlaybackGate gate){
        for(Ticket t:tickets)if(t.texture==same){gate.detach(t.generation);if(t.finished)return true;t.destroyed=true;return false;}
        return true; // A UI-owned texture never adopted by this render owner.
    }
    private void requireOwner(){if(owner==null)owner=Thread.currentThread();if(owner!=Thread.currentThread())throw new IllegalStateException("RENDER_ORIGINAL_THREAD");}
    private Ticket ticket(long generation){synchronized(this){for(Ticket t:tickets)if(t.generation==generation&&!t.destroyed&&!t.finished)return t;return null;}}
    private void retire(Ticket t)throws Exception {
        if(t==null||t.finished)return;
        try{
            if(t.surface!=null){t.surface.release();t.surface=null;}
            boolean transfer;synchronized(this){transfer=t.destroyed;if(!transfer)t.finished=true;}
            if(transfer){t.texture.release();synchronized(this){t.textureReturned=true;t.finished=true;}}
        }catch(Throwable failure){unknown=true;throw failure;}
    }
    public boolean draw(byte[] rgba,RawFrame frame,long epoch,long generation,PlaybackGate gate)throws Exception {
        requireOwner();if(pixels==null)throw new IOException("RENDER_BUDGET_NOT_BOUND");
        if(submitted>=6)throw new IOException("RENDER_FRAME_BUDGET");
        if(!gate.accepts(epoch,generation))return false;
        Ticket chosen=ticket(generation);if(chosen==null)return false;
        List<Ticket> original;synchronized(this){original=List.copyOf(tickets);}
        for(Ticket old:original){boolean destroyed;synchronized(this){destroyed=old.destroyed;}if(destroyed&&!old.finished)retire(old);}
        if(active!=chosen){retire(active);active=chosen;}
        if(active.surface==null)try{active.surface=new Surface(active.texture);}catch(Throwable failure){unknown=true;throw failure;}
        gate.renderAck(epoch,generation);
        int n=Limits.layout(frame.width,frame.height,frame.stride,rgba.length,frame.rotation);
        Canvas canvas=null;boolean unlocked=true;
        try{
            pixels.acquire(n);argbBytes=n;heldArgb=new int[n/4];
            for(int i=0,j=0;i<rgba.length;i+=4,j++)heldArgb[j]=((rgba[i+3]&255)<<24)|((rgba[i]&255)<<16)|((rgba[i+1]&255)<<8)|(rgba[i+2]&255);
            // Reserve a conservative native bitmap allowance before allocation, then measure the
            // actual owned pixel allocation. Driver/BufferQueue overhead remains a separate gap.
            pixels.acquire(2L*n);bitmapBytes=2L*n;heldBitmap=Bitmap.createBitmap(frame.width,frame.height,Bitmap.Config.ARGB_8888);
            int actualBitmapBytes=heldBitmap.getAllocationByteCount();
            if(actualBitmapBytes<1||actualBitmapBytes>bitmapBytes)throw new IOException("BITMAP_ALLOCATION_OUTSIDE_ALLOWANCE");
            pixels.release(bitmapBytes-actualBitmapBytes);bitmapBytes=actualBitmapBytes;
            heldBitmap.setPixels(heldArgb,0,frame.width,0,0,frame.width,frame.height);
            if(!gate.accepts(epoch,generation))return false;
            canvas=active.surface.lockCanvas(null);heldCanvas=canvas;if(canvas==null)throw new IOException("CANVAS_NOT_ACQUIRED");unlocked=false;
            if(gate.accepts(epoch,generation)){
                canvas.drawColor(Color.BLACK);canvas.save();canvas.translate(canvas.getWidth()/2f,canvas.getHeight()/2f);
                boolean rotated=frame.rotation==90||frame.rotation==270;
                float scale=Math.min(canvas.getWidth()/(float)(rotated?frame.height:frame.width),canvas.getHeight()/(float)(rotated?frame.width:frame.height));
                canvas.rotate(frame.rotation);canvas.scale(scale,scale);canvas.translate(-frame.width/2f,-frame.height/2f);
                canvas.drawBitmap(heldBitmap,0,0,null);canvas.restore();submitted++;lastPts=frame.ptsUs;
            }
            // Exactly the acquired canvas, never a second lock/release to manufacture an ACK.
            active.surface.unlockCanvasAndPost(canvas);heldCanvas=null;unlocked=true;return true;
        }catch(Throwable t){if(!unlocked)unknown=true;throw t;}
        finally{
            if(unlocked){if(heldBitmap!=null){heldBitmap.recycle();heldBitmap=null;}if(bitmapBytes!=0){pixels.release(bitmapBytes);bitmapBytes=0;}
                heldArgb=null;if(argbBytes!=0){pixels.release(argbBytes);argbBytes=0;}}
        }
    }
    public void close()throws Exception {
        requireOwner();if(closed)return;if(unknown)throw new IOException("CANVAS_ORIGINAL_RETURN_UNKNOWN");
        try{List<Ticket> original;synchronized(this){original=List.copyOf(tickets);}for(Ticket t:original)retire(t);closed=true;}
        catch(Throwable t){unknown=true;throw t;}
    }
    public synchronized boolean returned(){return closed&&!unknown&&heldBitmap==null&&bitmapBytes==0&&argbBytes==0&&tickets.stream().allMatch(t->t.finished);}
    public String state(){return "submitted="+submitted+" lastActualPtsUs="+lastPts+" closed="+closed+" unknown="+unknown+" (submission is not screenshot proof)";}
}
