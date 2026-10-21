package com.videokit.spike.e4;

import android.media.MediaCodec;
import android.os.ParcelFileDescriptor;
import android.system.Os;
import android.system.OsConstants;
import androidx.media3.common.Format;
import androidx.media3.muxer.FragmentedMp4Muxer;
import com.videokit.spike.c14.AndroidLease;
import java.io.IOException;
import java.io.OutputStream;
import java.nio.ByteBuffer;
import java.nio.channels.WritableByteChannel;

/** Adapted fMP4/channel/lease composition from frozen C14 PipelineOutputSink.java/
 * BoundedOutputChannel.java. Owns only granted descriptors. It cannot open a path. */
final class E4CodecSink {
    static final int MAX_OUTPUT=2097152,MAX_SAMPLE=262144;
    private final ParcelFileDescriptor sinkFd,leaseFd;
    private final String epoch;
    private ParcelFileDescriptor sync;
    private AndroidLease.WorkerLease lease;
    private ParcelFileDescriptor.AutoCloseOutputStream stream;
    private FragmentedMp4Muxer muxer;
    private BoundedChannel channel;
    private volatile boolean opening,opened,muxerClosed=true,sinkClosed,leaseClosed,syncClosed=true,closeAttempted,unknown,flushed;
    private volatile int samples,activeCalls;
    private long last=-1;private int trackToken=-1;
    E4CodecSink(ParcelFileDescriptor sink,ParcelFileDescriptor lease,String epoch)throws IOException {
        if(sink==null || lease==null || epoch==null || !epoch.matches("[A-Za-z0-9-]{1,64}"))throw new IOException("E4_SINK_GRANT_INVALID");
        sinkFd=sink;leaseFd=lease;this.epoch=epoch;
    }
    void open()throws Exception {
        activeCalls++;try{
        if(opened || opening || closeAttempted)throw new IOException("E4_SINK_REOPEN");opening=true;
        android.system.StructStat s=Os.fstat(sinkFd.getFileDescriptor()),l=Os.fstat(leaseFd.getFileDescriptor());
        int flags=Os.fcntlInt(sinkFd.getFileDescriptor(),OsConstants.F_GETFL,0),mode=flags&OsConstants.O_ACCMODE;
        if(!OsConstants.S_ISREG(s.st_mode) || !OsConstants.S_ISREG(l.st_mode) || s.st_size!=0 ||
                s.st_dev==l.st_dev && s.st_ino==l.st_ino || mode==OsConstants.O_RDONLY || (flags&OsConstants.O_APPEND)!=0)throw new IOException("E4_SINK_NOT_EMPTY_WRITABLE_REGULAR");
        lease=AndroidLease.WorkerLease.acquire(leaseFd,epoch);
        sync=ParcelFileDescriptor.dup(sinkFd.getFileDescriptor());syncClosed=false;
        stream=new ParcelFileDescriptor.AutoCloseOutputStream(sinkFd);channel=new BoundedChannel(stream);
        muxerClosed=false;
        muxer=com.videokit.spike.c14.E6Muxer.create(channel);
        opening=false;opened=true;
        }finally{activeCalls--;}
    }
    int addTrack(Format format)throws Exception {
        if(muxer==null || !"video/avc".equals(format.sampleMimeType) || format.width!=256 || format.height!=144 || format.rotationDegrees!=0)
            throw new IOException("E4_MUX_TRACK_INVALID");
        activeCalls++;try{if(trackToken>=0)throw new IOException("E6_MUX_TRACK_ONCE");trackToken=muxer.addTrack(format);return trackToken;}finally{activeCalls--;}
    }
    void sample(int track,ByteBuffer data,MediaCodec.BufferInfo info)throws Exception {
        if(samples>=6 || info.size<1 || info.size>MAX_SAMPLE || info.presentationTimeUs<0 || info.presentationTimeUs>2000000 ||
                last>=0 && info.presentationTimeUs<=last)throw new IOException("E4_MUX_SAMPLE_BUDGET");
        activeCalls++;try{muxer.writeSampleData(track,data,new androidx.media3.muxer.BufferInfo(info.presentationTimeUs,info.size,info.flags));}finally{activeCalls--;}
        samples++;last=info.presentationTimeUs;
    }
    void finish()throws Exception {
        activeCalls++;try{
        if(!opened || samples!=6 || closeAttempted)throw new IOException("E4_MUX_INCOMPLETE");
        if(muxer!=null && !muxerClosed){com.videokit.spike.c14.E6Muxer.finish(muxer,trackToken,samples,last);muxerClosed=true;}
        Os.fsync(sync.getFileDescriptor());flushed=true;
        }finally{activeCalls--;}
    }
    /** A failed close is sticky: retaining the original owner is stronger than a retry claim. */
    boolean close() {
        if(released())return true;if(closeAttempted || unknown)return false;closeAttempted=true;activeCalls++;
        try{
        try{if(muxer!=null && !muxerClosed){muxer.close();muxerClosed=true;}}catch(Exception e){unknown=true;}
        try{if(!sinkClosed){if(channel!=null)channel.close();else if(stream!=null)stream.close();else sinkFd.close();sinkClosed=true;}}catch(Exception e){unknown=true;}
        try{if(!syncClosed){sync.close();syncClosed=true;}}catch(Exception e){unknown=true;}
        try{if(!leaseClosed){if(lease!=null)lease.close();else leaseFd.close();leaseClosed=true;}}catch(Exception e){unknown=true;}
        if(opening && muxer==null)unknown=true;
        return releasedIgnoringCall();
        }finally{activeCalls--;}
    }
    private boolean releasedIgnoringCall(){return sinkClosed && syncClosed && leaseClosed && muxerClosed && !unknown && !opening;}
    boolean released(){return releasedIgnoringCall() && activeCalls==0;}
    boolean opened(){return opened && !opening && !closeAttempted;}
    int activeCalls(){return activeCalls;}
    boolean leaseReleased(){return leaseClosed && !unknown;}
    boolean flushed(){return flushed;}
    long bytes(){return channel==null?0:channel.bytes;}
    int samples(){return samples;}
    private static final class BoundedChannel implements WritableByteChannel {
        final OutputStream output;final byte[] scratch=new byte[16384];volatile long bytes;boolean open=true;
        BoundedChannel(OutputStream output){this.output=output;}
        public int write(ByteBuffer data)throws IOException {
            if(!open)throw new IOException("E4_SINK_CLOSED");int count=data.remaining();
            if(count>MAX_OUTPUT-bytes)throw new IOException("E4_OUTPUT_BYTE_BUDGET");
            while(data.hasRemaining()){int n=Math.min(data.remaining(),scratch.length);data.get(scratch,0,n);bytes+=n;output.write(scratch,0,n);}return count;
        }
        public boolean isOpen(){return open;}
        public void close()throws IOException {if(open){output.close();open=false;}}
    }
}
