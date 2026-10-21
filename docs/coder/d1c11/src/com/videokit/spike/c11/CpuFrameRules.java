package com.videokit.spike.c11;
import java.io.IOException;
import java.math.BigInteger;
/** Wire rules shared by host and local counterexamples. No compressed-data parser. */
public final class CpuFrameRules {
    public static final int MAGIC=0x564b4339, VERSION=1, WIDTH=256, HEIGHT=144, STRIDE=WIDTH*4, BYTES=STRIDE*HEIGHT;
    public static final int ACK=0x564b4f4b;
    public static final int MAX_READ=65536, MAX_PACKETS=4096;
    public static final long MAX_PTS_US=86400000000L, MAX_SOURCE=1L<<40, READ_BUDGET=64L<<20;
    private CpuFrameRules() {}
    public static void sourceLength(long size)throws IOException {if(size<1 || size>MAX_SOURCE)throw new IOException("CPU_SOURCE_LENGTH_REQUIRED");}
    public static void allocationQuota(long peak,long current)throws IOException {if(current<BYTES || peak<current || peak>64L*1024*1024)throw new IOException("CPU_ALLOCATION_QUOTA");}
    public static void acknowledgement(int marker,int bytes)throws IOException {if(marker!=ACK || bytes<4 || bytes>64)throw new IOException("CPU_WORKER_ACK_PROTOCOL");}
    public static void timestamp(long raw,int num,int den,long micros,int bestEffort,long peakKiB)throws IOException {
        if(raw<0 || num<=0 || den<=0 || bestEffort<0 || bestEffort>1 || peakKiB<1 || peakKiB>262144)
            throw new IOException("CPU_FRAME_SOURCE_TIMING_OR_MEMORY");
        BigInteger expected=BigInteger.valueOf(raw).multiply(BigInteger.valueOf(num)).multiply(BigInteger.valueOf(1000000))
            .add(BigInteger.valueOf(den/2)).divide(BigInteger.valueOf(den));
        if(!expected.equals(BigInteger.valueOf(micros)))throw new IOException("CPU_FRAME_TIMEBASE");
    }
    public static long seek(long current,long offset,int whence,long size)throws IOException {
        if(size<1 || size>MAX_SOURCE || current<0 || current>size)throw new IOException("CPU_SEEK_BOUNDS");
        if(whence==0x10000)return size;
        long origin=whence==0?0:whence==1?current:whence==2?size:-1;
        if(origin<0)throw new IOException("CPU_SEEK_WHENCE");
        try {long at=Math.addExact(origin,offset);if(at<0 || at>size)throw new IOException("CPU_SEEK_BOUNDS");return at;}
        catch(ArithmeticException error){throw new IOException("CPU_SEEK_OVERFLOW");}
    }
    public static void frame(int magic,int version,String task,String expectedTask,long epoch,long expectedEpoch,
            int pid,int uid,int expectedPid,int expectedUid,int width,int height,int stride,int offset,int length,
            long pts,long target,int sequence)throws IOException {
        if(magic!=MAGIC || version!=VERSION || task==null || task.length()>64 || !task.equals(expectedTask)
                || epoch<=0 || epoch!=expectedEpoch || pid<=0 || uid<=0 || pid!=expectedPid || uid!=expectedUid)
            throw new IOException("CPU_FRAME_IDENTITY");
        long end=(long)offset+length, pixels=(long)stride*height;
        if(width!=WIDTH || height!=HEIGHT || stride!=STRIDE || offset!=0 || length!=BYTES
                || end!=BYTES || pixels!=BYTES || sequence!=1)throw new IOException("CPU_FRAME_LAYOUT");
        if(target<0 || target>MAX_PTS_US-2000000 || pts<target || pts>target+2000000 || pts>MAX_PTS_US)
            throw new IOException("CPU_FRAME_PTS");
    }
}
