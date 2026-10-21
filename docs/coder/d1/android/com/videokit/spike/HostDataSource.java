package com.videokit.spike;

import android.net.Uri;
import android.os.Looper;
import androidx.media3.datasource.BaseDataSource;
import androidx.media3.datasource.DataSpec;
import java.io.IOException;

/** Debug-only Media3 boundary. URI must contain an opaque token, never a source path. */
public final class HostDataSource extends BaseDataSource {
    public interface Factory { ReadBridge.Handle open() throws IOException; }
    private final Factory factory;
    private volatile ReadBridge bridge;
    private Uri uri;
    private boolean started;
    public HostDataSource(Factory factory) { super(false); this.factory=factory; }
    @Override public long open(DataSpec spec) throws IOException {
        if (Looper.myLooper()==Looper.getMainLooper()) throw new IOException("MAIN_THREAD_IO_REJECTED");
        if (bridge!=null) throw new IOException("SOURCE_ALREADY_OPEN");
        transferInitializing(spec);
        ReadBridge next=new ReadBridge(factory.open());
        try {
            long size=next.open(spec.position,spec.length);
            bridge=next;uri=spec.uri;started=true;transferStarted(spec);return size;
        } catch(IOException | RuntimeException e) {next.close();throw e;}
    }
    @Override public int read(byte[] target,int offset,int length)throws IOException {
        if (Looper.myLooper()==Looper.getMainLooper()) throw new IOException("MAIN_THREAD_IO_REJECTED");
        ReadBridge current=bridge;
        if(current==null)throw new IOException("SESSION_RELEASED");
        int n=current.read(target,offset,length);if(n>0)bytesTransferred(n);return n;
    }
    @Override public Uri getUri(){return uri;}
    @Override public void close() throws IOException {
        ReadBridge current=bridge;bridge=null;uri=null;
        try {if(current!=null)current.close();}
        finally {if(started){started=false;transferEnded();}}
    }
}
