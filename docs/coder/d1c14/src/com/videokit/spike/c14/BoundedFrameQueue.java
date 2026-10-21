package com.videokit.spike.c14;
import java.io.*;
import java.util.*;
import java.util.concurrent.TimeUnit;
public final class BoundedFrameQueue<T> {
    public static final class Snapshot {public final int queued,consumers,offers,peak;public final boolean cancelled,done;
        Snapshot(BoundedFrameQueue<?> q){queued=q.queue.size();consumers=q.consumers;offers=q.offers;peak=q.peak;cancelled=q.cancelled;done=q.done;}
        public boolean released(){return (cancelled || done) && queued==0 && consumers==0 && offers==0;}}
    public final class Lease implements AutoCloseable {private T value;private Lease(T value){this.value=value;}public T value(){if(value==null)throw new IllegalStateException("PIPE_FRAME_LEASE_RELEASED");return value;}public void close(){synchronized(BoundedFrameQueue.this){if(value!=null){value=null;consumers--;BoundedFrameQueue.this.notifyAll();}}}}
    private final ArrayDeque<T> queue=new ArrayDeque<>();private int consumers,offers,peak;private boolean cancelled,done;
    public synchronized void offer(T value,long ms)throws IOException,InterruptedException{
        if(ms<1 || ms>500)throw new IllegalArgumentException("PIPE_QUEUE_BUDGET");long deadline=System.nanoTime()+TimeUnit.MILLISECONDS.toNanos(ms);offers++;
        try{while(queue.size()>=PipelineRules.QUEUE && !cancelled){long remain=deadline-System.nanoTime();if(remain<=0)throw new IOException("PIPE_FRAME_QUEUE_FULL");TimeUnit.NANOSECONDS.timedWait(this,remain);}if(cancelled || done)throw new IOException("PIPE_CANCELLED");queue.addLast(Objects.requireNonNull(value));peak=Math.max(peak,queue.size());notifyAll();}finally{offers--;notifyAll();}
    }
    public synchronized Lease take(long ms)throws IOException,InterruptedException{
        long deadline=System.nanoTime()+TimeUnit.MILLISECONDS.toNanos(ms);while(queue.isEmpty() && !done && !cancelled){long remain=deadline-System.nanoTime();if(remain<=0)throw new IOException("PIPE_CONSUMER_TIMEOUT");TimeUnit.NANOSECONDS.timedWait(this,remain);}
        if(cancelled)throw new IOException("PIPE_CANCELLED");if(queue.isEmpty())return null;if(consumers!=0)throw new IOException("PIPE_CONSUMER_IN_FLIGHT");T value=queue.removeFirst();consumers++;notifyAll();return new Lease(value);
    }
    public synchronized void finish(){done=true;notifyAll();}public synchronized void cancel(){cancelled=true;queue.clear();notifyAll();}public synchronized Snapshot snapshot(){return new Snapshot(this);}
}
