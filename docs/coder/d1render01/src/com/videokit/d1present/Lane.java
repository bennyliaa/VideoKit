package com.videokit.d1present;
import java.util.ArrayDeque;
import java.util.concurrent.TimeUnit;
/** Bounded waiting descriptors, exactly one work item leased to its owner at a time. */
public final class Lane<T> {
    private final int capacity;private final ArrayDeque<T> queue=new ArrayDeque<>();
    private T inFlight;private boolean ended;private int peak;
    public Lane(int c){if(c<1)throw new IllegalArgumentException();capacity=c;}
    public synchronized boolean offer(T t){if(t==null)throw new NullPointerException();if(ended||queue.size()==capacity)return false;queue.add(t);peak=Math.max(peak,queue.size());notifyAll();return true;}
    public synchronized T take(long deadline)throws InterruptedException {
        if(inFlight!=null)throw new IllegalStateException("SECOND_INFLIGHT");
        while(queue.isEmpty()&&!ended){long left=deadline-System.nanoTime();if(left<=0)return null;TimeUnit.NANOSECONDS.timedWait(this,left);}
        inFlight=queue.poll();return inFlight;
    }
    public synchronized void returned(T same){if(inFlight==null||inFlight!=same)throw new IllegalStateException("WRONG_ORIGINAL_ITEM");inFlight=null;notifyAll();}
    public synchronized void clearQueued(){queue.clear();notifyAll();}
    public synchronized void end(){ended=true;notifyAll();}
    public synchronized int queued(){return queue.size();}public synchronized int inFlight(){return inFlight==null?0:1;}public synchronized int peak(){return peak;}
}
