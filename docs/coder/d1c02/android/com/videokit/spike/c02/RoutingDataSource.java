package com.videokit.spike.c02;

import android.net.Uri;
import android.os.Looper;
import androidx.media3.datasource.BaseDataSource;
import androidx.media3.datasource.DataSpec;
import java.io.IOException;
import java.util.Map;

public final class RoutingDataSource extends BaseDataSource {
    private final AsyncReadBridge.Runtime runtime;private final LeaseRegistry leases;private final long generation;
    private final Map<String,AsyncReadBridge.Provider> sources;private AsyncReadBridge bridge;private Uri uri;private boolean started;
    public RoutingDataSource(AsyncReadBridge.Runtime runtime,LeaseRegistry leases,long generation,Map<String,AsyncReadBridge.Provider> sources){super(false);this.runtime=runtime;this.leases=leases;this.generation=generation;this.sources=sources;}
    private void worker()throws IOException{if(Looper.myLooper()==Looper.getMainLooper())throw new IOException("MAIN_THREAD_IO_REJECTED");}
    @Override public long open(DataSpec spec)throws IOException{
        worker();AsyncReadBridge next;
        synchronized(this){
            if(bridge!=null)throw new IOException("SOURCE_ALREADY_OPEN");
            AsyncReadBridge.Provider provider=sources.get(spec.uri.toString());if(provider==null)throw new IOException("SOURCE_NOT_FOUND");
            transferInitializing(spec);next=new AsyncReadBridge(runtime,provider,leases,generation,5000);bridge=next;uri=spec.uri;
        }
        try{long length=next.open(spec.position,spec.length);synchronized(this){if(bridge!=next)throw new IOException("CANCELLED");started=true;transferStarted(spec);}return length;}
        catch(IOException | RuntimeException e){next.close();synchronized(this){if(bridge==next){bridge=null;uri=null;}}throw e;}
    }
    @Override public int read(byte[] target,int offset,int length)throws IOException{
        worker();AsyncReadBridge current;synchronized(this){current=bridge;}if(current==null)throw new IOException("SESSION_RELEASED");
        int n=current.read(target,offset,length);synchronized(this){if(bridge!=current)throw new IOException("CANCELLED");if(n>0)bytesTransferred(n);}return n;
    }
    @Override public synchronized Uri getUri(){return uri;}
    @Override public void close(){AsyncReadBridge current;synchronized(this){current=bridge;bridge=null;uri=null;if(started){started=false;transferEnded();}}if(current!=null)current.close();}
}
