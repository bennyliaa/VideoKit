package com.videokit.spike.c11;

import android.net.Uri;
import android.os.Looper;
import androidx.media3.datasource.BaseDataSource;
import androidx.media3.datasource.DataSpec;
import java.io.IOException;
import java.util.Map;

public final class RoutingDataSource extends BaseDataSource {
    public static final class Group {
        private final java.util.Set<RoutingDataSource> active=java.util.concurrent.ConcurrentHashMap.newKeySet();private volatile boolean cancelled;
        synchronized void add(RoutingDataSource source)throws IOException{if(cancelled)throw new IOException("CANCELLED");if(active.size()>=64 && !active.contains(source))throw new IOException("SOURCE_RESOURCE_EXHAUSTED");active.add(source);}
        boolean cancelled(){return cancelled;}
        public void cancel(){RoutingDataSource[] sources;synchronized(this){cancelled=true;sources=active.toArray(new RoutingDataSource[0]);active.clear();}StageLog.event("SOURCE_GROUP_CANCEL","sources="+sources.length);for(RoutingDataSource s:sources)s.close();}
    }
    private final AsyncReadBridge.Runtime runtime;private final LeaseRegistry leases;private final long generation;
    private final Map<String,AsyncReadBridge.Provider> sources;private AsyncReadBridge bridge;private Uri uri;private boolean started;private Group group;private long reads;
    public RoutingDataSource(AsyncReadBridge.Runtime runtime,LeaseRegistry leases,long generation,Map<String,AsyncReadBridge.Provider> sources){super(false);this.runtime=runtime;this.leases=leases;this.generation=generation;this.sources=sources;}
    public RoutingDataSource(AsyncReadBridge.Runtime runtime,LeaseRegistry leases,long generation,Map<String,AsyncReadBridge.Provider> sources,Group group){this(runtime,leases,generation,sources);this.group=group;}
    private void worker()throws IOException{if(Looper.myLooper()==Looper.getMainLooper())throw new IOException("MAIN_THREAD_IO_REJECTED");}
    @Override public long open(DataSpec spec)throws IOException{
        worker();AsyncReadBridge next;
        if(group!=null)group.add(this);StageLog.event("SOURCE_OPEN_BEGIN","subtitle="+spec.uri.toString().equals(MediaEngine.SRT)+" offset="+spec.position+" length="+spec.length);
        synchronized(this){
            if(group!=null && group.cancelled())throw new IOException("CANCELLED");if(bridge!=null)throw new IOException("SOURCE_ALREADY_OPEN");
            AsyncReadBridge.Provider provider=sources.get(spec.uri.toString());if(provider==null)throw new IOException("SOURCE_NOT_FOUND");
            next=new AsyncReadBridge(runtime,provider,leases,generation,5000);bridge=next;uri=spec.uri;
        }
        try{transferInitializing(spec);long length=next.open(spec.position,spec.length);synchronized(this){if(bridge!=next)throw new IOException("CANCELLED");started=true;}transferStarted(spec);StageLog.event("SOURCE_OPEN_DONE","length="+length);return length;}
        catch(IOException | RuntimeException e){StageLog.failure("SOURCE_OPEN_FAILED",e);next.close();synchronized(this){if(bridge==next){bridge=null;uri=null;}}throw e;}
    }
    @Override public int read(byte[] target,int offset,int length)throws IOException{
        worker();AsyncReadBridge current;synchronized(this){current=bridge;}if(current==null)throw new IOException("SESSION_RELEASED");
        if(++reads==1 || reads%128==0)StageLog.event("SOURCE_READ_BEGIN","count="+reads+" requested="+length);
        try{int n=current.read(target,offset,length);synchronized(this){if(bridge!=current)throw new IOException("CANCELLED");}if(n>0)bytesTransferred(n);return n;}catch(IOException e){StageLog.failure("SOURCE_READ_FAILED",e);throw e;}
    }
    @Override public synchronized Uri getUri(){return uri;}
    @Override public void close(){AsyncReadBridge current;boolean notify;synchronized(this){current=bridge;bridge=null;uri=null;notify=started;started=false;}if(group!=null)group.active.remove(this);if(current!=null)current.close();if(notify)transferEnded();StageLog.event("SOURCE_CLOSE_REQUEST","");}
}
