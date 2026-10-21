package com.videokit.d1present;
import com.videokit.spike.c14.AsyncReadBridge;
import java.io.IOException;
import java.util.*;
import java.util.concurrent.*;
/** Read-only, finite raw+generated-PCM view, not a new media container or compressed audio decoder.
 * Both consumers open the SAME provider/version, and offsets refer to its immutable owned segments.
 */
public final class PresentationSource implements AsyncReadBridge.Provider {
    public final List<RawFrame> frames;byte[] pcm;public final long pcmOffset,length;
    private final long[] offsets;private int opens,closes,reads;private boolean disposed;
    public PresentationSource(List<RawFrame> frames,byte[] pcm)throws IOException {
        if(frames.isEmpty()||frames.size()>6||pcm.length!=Limits.PCM_BYTES)throw new IOException("SOURCE_BUDGET");
        this.frames=List.copyOf(frames);this.pcm=pcm;offsets=new long[frames.size()];long n=0,last=-1;
        RawFrame first=frames.get(0);
        for(int i=0;i<frames.size();i++){RawFrame f=frames.get(i);if(!f.task.equals(first.task)||!f.sourceVersion.equals(first.sourceVersion)||f.epoch!=first.epoch||f.ptsUs<=last)throw new IOException("SOURCE_FRAME_ORDER_OR_VERSION");offsets[i]=n;n+=f.pixels.length;last=f.ptsUs;}
        pcmOffset=n;length=n+pcm.length;
    }
    public long offset(int index){return offsets[index];}
    public synchronized CompletionStage<AsyncReadBridge.Handle> open(AsyncReadBridge.Cancellation c){
        if(disposed||c.cancelled()||opens>=2)return failed(new IOException("SOURCE_ADMISSION"));opens++;
        return CompletableFuture.completedFuture(new AsyncReadBridge.Handle(){
            private boolean closed;
            public Long length(){return length;}
            public synchronized CompletionStage<Integer> readAt(long at,byte[] target,int off,int n,AsyncReadBridge.Cancellation token){
                if(closed||token.cancelled()||at<0||n<1||off<0||off+n>target.length)return failed(new IOException("SOURCE_RANGE_OR_CLOSED"));
                if(at>=length)return CompletableFuture.completedFuture(-1);
                int count=(int)Math.min(n,length-at),done=0;
                while(done<count){long p=at+done;byte[] bytes;long base;
                    if(p>=pcmOffset){bytes=pcm;base=pcmOffset;}else{int index=0;while(index+1<offsets.length&&offsets[index+1]<=p)index++;bytes=PresentationSource.this.frames.get(index).pixels;base=offsets[index];}
                    int size=Math.min(count-done,bytes.length-(int)(p-base));System.arraycopy(bytes,(int)(p-base),target,off+done,size);done+=size;
                }synchronized(PresentationSource.this){reads++;}return CompletableFuture.completedFuture(done);
            }
            public synchronized CompletionStage<Void> closeAsync(){if(!closed){closed=true;synchronized(PresentationSource.this){closes++;}}return CompletableFuture.completedFuture(null);}
        });
    }
    public synchronized void dispose(){if(disposed)return;if(opens!=closes)throw new IllegalStateException("SOURCE_HANDLES_PENDING");disposed=true;for(RawFrame f:frames)f.release();pcm=null;}
    public synchronized int opens(){return opens;}public synchronized int closes(){return closes;}public synchronized int reads(){return reads;}
    private static <T>CompletableFuture<T> failed(Throwable t){CompletableFuture<T> f=new CompletableFuture<>();f.completeExceptionally(t);return f;}
}
