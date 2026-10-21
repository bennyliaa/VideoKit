package com.videokit.d1present;
import java.io.IOException;
/** Owned immutable pixels. The source's media PTS is never reconstructed from frame number. */
public final class RawFrame {
    public final String task,sourceVersion,producerTask;public final long epoch,ptsUs,rawTimestamp,producerEpoch;public final int timeBaseNum,timeBaseDen,width,height,stride,rotation;
    byte[] pixels;private final Limits.Pixels budget;private boolean released;
    public RawFrame(String task,String version,long epoch,long pts,long raw,int num,int den,int width,int height,int stride,int rotation,byte[] rgba,Limits.Pixels budget)throws IOException {
        this(task,version,epoch,pts,raw,num,den,width,height,stride,rotation,rgba,budget,task,epoch);
    }
    public RawFrame(String task,String version,long epoch,long pts,long raw,int num,int den,int width,int height,int stride,int rotation,byte[] rgba,Limits.Pixels budget,String producerTask,long producerEpoch)throws IOException {
        int n=Limits.layout(width,height,stride,rgba==null?-1:rgba.length,rotation);
        if(task==null||version==null||producerTask==null||producerEpoch<=0||epoch<=0||pts<0||raw<0||num<=0||den<=0)throw new IOException("RAW_IDENTITY_OR_PTS");
        java.math.BigInteger expected=java.math.BigInteger.valueOf(raw).multiply(java.math.BigInteger.valueOf(num)).multiply(java.math.BigInteger.valueOf(1000000)).add(java.math.BigInteger.valueOf(den/2)).divide(java.math.BigInteger.valueOf(den));
        if(!expected.equals(java.math.BigInteger.valueOf(pts)))throw new IOException("RAW_TIMEBASE");
        budget.acquire(n);byte[] copy;try{copy=rgba.clone();}catch(Throwable error){budget.release(n);throw error;}
        this.task=task;sourceVersion=version;this.epoch=epoch;ptsUs=pts;rawTimestamp=raw;timeBaseNum=num;timeBaseDen=den;
        this.producerTask=producerTask;this.producerEpoch=producerEpoch;
        this.width=width;this.height=height;this.stride=stride;this.rotation=rotation;pixels=copy;this.budget=budget;
    }
    synchronized void release(){if(released)return;released=true;int n=pixels.length;pixels=null;budget.release(n);}
}
