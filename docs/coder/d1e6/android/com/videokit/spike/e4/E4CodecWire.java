package com.videokit.spike.e4;

import android.os.Bundle;
import android.os.IBinder;
import android.os.Parcel;
import android.os.RemoteException;
import java.io.IOException;
import java.util.Set;

/** Experimental private, bounded same-APK control protocol. No URI, path or credential fields. */
public final class E4CodecWire {
    public static final String DESCRIPTOR="com.videokit.spike.e4.CODEC_V1";
    public static final String CALLBACK="com.videokit.spike.e4.CODEC_CALLBACK_V1";
    public static final int CALLBACK_ACK=0x45344342;
    public static final int HELLO=1,BEGIN=2,FRAME=3,FINISH=4,CANCEL=5,QUERY=6,DEBUG=7;
    public static final int MAX_PARCEL=196608;
    private static final Set<String> ID=Set.of("task","epoch","generation","serviceInstance","hostUid","serviceUid");
    public static Bundle identity(E4Protocol.Identity id){
        Bundle b=new Bundle();b.putString("task",id.task);b.putLong("epoch",id.epoch);b.putLong("generation",id.generation);
        b.putString("serviceInstance",id.serviceInstance);b.putInt("hostUid",id.hostUid);b.putInt("serviceUid",id.serviceUid);return b;
    }
    public static E4Protocol.Identity identity(Bundle b)throws IOException {
        return new E4Protocol.Identity(b.getString("task"),b.getLong("epoch"),b.getLong("generation"),
                b.getString("serviceInstance"),b.getInt("hostUid"),b.getInt("serviceUid"));
    }
    public static void keys(Bundle b,int code)throws IOException {
        if(b==null)throw new IOException("E4_NULL_REQUEST");
        Set<String> extra=code==BEGIN?Set.of("callback","sink","lease","leaseEpoch"):code==FRAME?
                Set.of("sequence","ptsUs","width","height","stride","rotation","rgba"):code==DEBUG?Set.of("fault","armToken"):Set.of();
        for(String key:b.keySet())if(!(code!=HELLO && ID.contains(key)) && !extra.contains(key))throw new IOException("E4_UNKNOWN_FIELD");
        if(code!=HELLO && !b.keySet().containsAll(ID))throw new IOException("E4_IDENTITY_MISSING");
    }
    public static Bundle call(IBinder service,int code,Bundle request)throws RemoteException {
        Parcel in=Parcel.obtain(),out=Parcel.obtain();
        try{in.writeInterfaceToken(DESCRIPTOR);in.writeBundle(request);if(in.dataSize()>MAX_PARCEL)throw new IllegalArgumentException("E4_PARCEL_BUDGET");
            if(!service.transact(code,in,out,0))throw new RemoteException("E4_TRANSACT_REJECTED");if(out.dataSize()>16384)throw new RemoteException("E4_REPLY_BUDGET");out.readException();
            if(out.dataAvail()>16384)throw new RemoteException("E4_REPLY_BUDGET");
            Bundle b=out.readBundle(E4CodecWire.class.getClassLoader());if(b==null || out.dataAvail()!=0)throw new RemoteException("E4_REPLY_INVALID");return b;
        }finally{in.recycle();out.recycle();}
    }
    public static void callback(IBinder target,Bundle event)throws RemoteException {
        Parcel out=Parcel.obtain(),ack=Parcel.obtain();try{out.writeInterfaceToken(CALLBACK);out.writeBundle(event);
            if(out.dataSize()>16384)throw new RemoteException("E4_CALLBACK_BUDGET");
            // A synchronous call preserves the original Binder UID and yields an explicit bounded ACK.
            // There is no timeout-to-release conversion: a stuck receiver leaves the original call pending.
            if(!target.transact(1,out,ack,0))throw new RemoteException("E4_CALLBACK_REJECTED");
            if(ack.dataSize()>16384)throw new RemoteException("E4_CALLBACK_ACK_BUDGET");ack.readException();
            if(ack.readInt()!=CALLBACK_ACK || ack.readInt()!=event.getInt("hostUid") ||
                    !event.getString("serviceInstance","").equals(ack.readString()) || ack.dataAvail()!=0)
                throw new RemoteException("E4_CALLBACK_ACK_IDENTITY");
        }finally{out.recycle();ack.recycle();}
    }
    private E4CodecWire(){}
}
