package com.videokit.spike.c09;

import android.net.Uri;
import android.os.*;
import androidx.media3.datasource.*;
import java.io.IOException;

/** Actual Media3 input in isolated worker. Each open gets an owner-bound broker handle. */
public final class BrokerDataSource extends BaseDataSource {
    private final IBinder broker;private final String task;private long handle;private Uri uri;private boolean opened;
    public BrokerDataSource(IBinder broker,String task){super(false);this.broker=broker;this.task=task;}
    private Parcel request(){Parcel p=Parcel.obtain();p.writeInterfaceToken(MediaProtocol.BROKER);p.writeString(task);return p;}
    private void call(int code,Parcel request,Parcel reply)throws IOException {
        try{if(!broker.transact(code,request,reply,0))throw new IOException("BROKER_PROTOCOL_FAILED");reply.readException();}
        catch(RemoteException e){throw new IOException("SOURCE_DISCONNECTED");}
        catch(RuntimeException e){String codeValue=e.getMessage();if(codeValue!=null && codeValue.matches("[A-Z_]{3,64}"))throw new IOException(codeValue);throw new IOException("SOURCE_IO_FAILED");}
    }
    @Override public long open(DataSpec spec)throws IOException {
        if(Looper.myLooper()==Looper.getMainLooper())throw new IOException("MAIN_THREAD_IO_REJECTED");if(opened)throw new IOException("SOURCE_ALREADY_OPEN");
        transferInitializing(spec);Parcel req=request(),reply=Parcel.obtain();
        try{req.writeString(spec.uri.toString());req.writeLong(spec.position);req.writeLong(spec.length);call(MediaProtocol.OPEN,req,reply);handle=reply.readLong();long length=reply.readLong();uri=spec.uri;opened=true;transferStarted(spec);return length;}
        finally{req.recycle();reply.recycle();}
    }
    @Override public int read(byte[] target,int offset,int length)throws IOException {
        java.util.Objects.checkFromIndexSize(offset,length,target.length);if(length==0)return 0;if(!opened)throw new IOException("SOURCE_NOT_OPEN");
        Parcel req=request(),reply=Parcel.obtain();try{int requested=Math.min(length,MediaProtocol.MAX_READ);req.writeLong(handle);req.writeInt(requested);call(MediaProtocol.READ,req,reply);int n=reply.readInt();byte[] data=reply.createByteArray();
            if(data==null || (n==-1?data.length!=0:n<=0 || n>requested || data.length!=n))throw new IOException("INVALID_READ_RESULT");if(n>0){System.arraycopy(data,0,target,offset,n);bytesTransferred(n);}return n;
        }finally{req.recycle();reply.recycle();}
    }
    @Override public Uri getUri(){return uri;}
    @Override public void close()throws IOException {
        if(!opened)return;opened=false;Parcel req=request(),reply=Parcel.obtain();try{req.writeLong(handle);call(MediaProtocol.CLOSE,req,reply);}finally{req.recycle();reply.recycle();uri=null;transferEnded();}
    }
}
