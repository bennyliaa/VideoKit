package com.videokit.spike.c05;
import android.graphics.Bitmap;
import android.media.MediaMetadataRetriever;
import java.io.*;
import java.util.concurrent.*;

/** Host-only feasibility comparison, not the final isolated pipeline. Timeout retains actual native FD ownership. */
public final class AuthorizedFrameProbe {
    private static final java.util.concurrent.Semaphore SLOT=new java.util.concurrent.Semaphore(1);
    private static final ExecutorService IO=Executors.newSingleThreadExecutor(r->{Thread t=new Thread(r,"d1-frame-probe");t.setDaemon(true);return t;});
    private static final LeaseRegistry LEASES=new LeaseRegistry();
    private static final class Ticket {boolean abandoned;final CompletableFuture<Bitmap> result=new CompletableFuture<>();}
    public static Bitmap read(File authorizedFixture,long requestedUs,long deadlineMs)throws IOException,InterruptedException{
        return readWithOption(authorizedFixture,requestedUs,deadlineMs,MediaMetadataRetriever.OPTION_CLOSEST_SYNC);
    }
    public static Bitmap readClosest(File authorizedFixture,long requestedUs,long deadlineMs)throws IOException,InterruptedException{
        return readWithOption(authorizedFixture,requestedUs,deadlineMs,MediaMetadataRetriever.OPTION_CLOSEST);
    }
    private static Bitmap readWithOption(File authorizedFixture,long requestedUs,long deadlineMs,int option)throws IOException,InterruptedException{
        if(!SLOT.tryAcquire())throw new IOException("FRAME_PROBE_RESOURCE_EXHAUSTED");
        long generation;try{generation=LEASES.create();LEASES.acquire(generation);LEASES.begin(generation,false);}catch(IOException e){SLOT.release();throw e;}
        Ticket ticket=new Ticket();
        IO.execute(()->{Bitmap frame=null;MediaMetadataRetriever retriever=null;FileInputStream input=null;Throwable failure=null;boolean actualClosed=true;
            try{
                retriever=new MediaMetadataRetriever();input=new FileInputStream(authorizedFixture);StageLog.event("FRAME_SOURCE_OPEN","generation="+generation+" requested_us="+requestedUs);retriever.setDataSource(input.getFD());
                StageLog.event("FRAME_METADATA","width="+retriever.extractMetadata(MediaMetadataRetriever.METADATA_KEY_VIDEO_WIDTH)+" height="+retriever.extractMetadata(MediaMetadataRetriever.METADATA_KEY_VIDEO_HEIGHT)+" duration="+retriever.extractMetadata(MediaMetadataRetriever.METADATA_KEY_DURATION));
                StageLog.event("FRAME_SCALED_BEGIN","");frame=retriever.getScaledFrameAtTime(requestedUs,option,256,144);StageLog.event("FRAME_SCALED_END","null="+(frame==null));
                if(frame==null){StageLog.event("FRAME_UNSCALED_SAME_TIME_BEGIN","");Bitmap original=retriever.getFrameAtTime(requestedUs,option);if(original!=null)try{if((long)original.getWidth()*original.getHeight()>4194304)throw new IOException("FRAME_PIXEL_BUDGET");frame=Bitmap.createScaledBitmap(original,256,144,true);if(frame==original)original=null;}finally{if(original!=null)original.recycle();}StageLog.event("FRAME_UNSCALED_SAME_TIME_END","null="+(frame==null));}
                if(frame==null)throw new IOException("FRAME_AT_REQUESTED_TIME_UNAVAILABLE");
            }catch(Exception e){failure=e;StageLog.failure("FRAME_DECODE_FAILED",e);}
            finally{
                try{if(retriever!=null)retriever.release();}catch(Exception e){actualClosed=false;failure=new IOException("FRAME_RESOURCE_RELEASE_UNKNOWN",e);}
                if(input!=null)try{input.close();}catch(IOException e){actualClosed=false;failure=new IOException("FRAME_RESOURCE_RELEASE_UNKNOWN",e);}
                if(!actualClosed)LEASES.closeFailed(generation);LEASES.end(generation);LEASES.releaseConsumer(generation);LEASES.retire(generation);if(actualClosed)SLOT.release();
                StageLog.event("FRAME_RESOURCE_QUERY","generation="+generation+" released="+LEASES.query(generation).released());
                synchronized(ticket){if(ticket.abandoned || failure!=null){if(frame!=null)frame.recycle();if(failure!=null)ticket.result.completeExceptionally(failure);}else ticket.result.complete(frame);}
            }
        });
        try{return ticket.result.get(deadlineMs,TimeUnit.MILLISECONDS);}
        catch(ExecutionException e){Throwable cause=e.getCause();throw cause instanceof IOException?(IOException)cause:new IOException("FRAME_DECODE_FAILED",cause);}
        catch(TimeoutException|InterruptedException e){synchronized(ticket){ticket.abandoned=true;if(ticket.result.isDone() && !ticket.result.isCompletedExceptionally()){Bitmap late=ticket.result.getNow(null);if(late!=null)late.recycle();}ticket.result.completeExceptionally(new IOException("FRAME_DECODE_TIMEOUT"));}StageLog.event("FRAME_WAIT_ENDED","generation="+generation+" actual_released="+LEASES.query(generation).released());if(e instanceof InterruptedException){Thread.currentThread().interrupt();throw (InterruptedException)e;}throw new IOException("FRAME_DECODE_TIMEOUT",e);}
    }
    private AuthorizedFrameProbe(){}
}
