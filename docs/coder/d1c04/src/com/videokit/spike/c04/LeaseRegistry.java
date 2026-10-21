package com.videokit.spike.c04;

import java.io.IOException;
import java.util.LinkedHashMap;
import java.util.Map;

/** Retains undrained generations. Released means every consumer and operation has finished. */
public final class LeaseRegistry {
    public static final class Snapshot {
        public final long generation; public final int consumers,operations,failedCloses; public final boolean retired,closeFailed;
        Snapshot(long g,Entry e){generation=g;consumers=e.consumers;operations=e.operations;retired=e.retired;failedCloses=e.failedCloses;closeFailed=e.failedCloses>0;}
        public boolean released(){return retired && consumers==0 && operations==0 && !closeFailed;}
    }
    private static final class Entry {int consumers,operations,failedCloses;boolean retired;}
    private final Map<Long,Entry> entries=new LinkedHashMap<>();private long next;
    public synchronized long create()throws IOException{
        if(entries.size()>=128){entries.entrySet().removeIf(e->new Snapshot(e.getKey(),e.getValue()).released());}
        if(entries.size()>=128)throw new IOException("SOURCE_RESOURCE_EXHAUSTED");
        long id=++next;entries.put(id,new Entry());return id;
    }
    private Entry entry(long g){Entry e=entries.get(g);if(e==null)throw new IllegalArgumentException("unknown generation");return e;}
    public synchronized void acquire(long g)throws IOException{Entry e=entries.get(g);if(e==null || e.retired)throw new IOException("SESSION_RELEASED");if(e.consumers>=32 || entries.values().stream().mapToInt(v->v.consumers).sum()>=64)throw new IOException("SOURCE_RESOURCE_EXHAUSTED");e.consumers++;}
    public synchronized void begin(long g,boolean cleanup)throws IOException{int limit=cleanup?96:64;if(entries.values().stream().mapToInt(v->v.operations).sum()>=limit)throw new IOException("SOURCE_RESOURCE_EXHAUSTED");entry(g).operations++;}
    public synchronized void end(long g){Entry e=entry(g);if(--e.operations<0)throw new IllegalStateException("operation underflow");notifyAll();}
    public synchronized void releaseConsumer(long g){Entry e=entry(g);if(--e.consumers<0)throw new IllegalStateException("consumer underflow");notifyAll();}
    public synchronized void retire(long g){entry(g).retired=true;notifyAll();}
    public synchronized boolean active(long g){Entry e=entries.get(g);return e!=null && !e.retired;}
    public synchronized void closeFailed(long g){entry(g).failedCloses++;notifyAll();}
    public synchronized void closeRecovered(long g){if(--entry(g).failedCloses<0)throw new IllegalStateException("close recovery underflow");notifyAll();}
    public synchronized Snapshot query(long g){Entry e=entries.get(g);if(e==null && g>0 && g<=next){e=new Entry();e.retired=true;}return new Snapshot(g,e==null?entry(g):e);}
    public synchronized boolean awaitReleased(long g,long deadlineMs)throws InterruptedException{
        long stop=System.nanoTime()+deadlineMs*1000000;
        while(!query(g).released()){long left=stop-System.nanoTime();if(left<=0)return false;wait(Math.max(1,left/1000000));}return true;
    }
}
