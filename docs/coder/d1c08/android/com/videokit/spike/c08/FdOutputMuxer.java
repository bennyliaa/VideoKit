package com.videokit.spike.c08;

import android.media.*;
import android.os.ParcelFileDescriptor;
import android.system.Os;
import androidx.media3.common.*;
import androidx.media3.muxer.*;
import com.google.common.collect.ImmutableList;
import java.io.*;
import java.nio.ByteBuffer;
import java.util.concurrent.*;
import java.util.concurrent.atomic.*;

/** Isolated-worker encoder output. Only host-granted descriptors, no paths or arbitrary temp files. */
public final class FdOutputMuxer implements Muxer.Factory,AutoCloseable {
    private final ParcelFileDescriptor output;private final Runnable processed;private final boolean pause;
    private final CountDownLatch gate=new CountDownLatch(1);private final AtomicBoolean notified=new AtomicBoolean(),created=new AtomicBoolean(),closed=new AtomicBoolean();
    private ParcelFileDescriptor syncFd,validationFd;private Muxer actual;private FileOutputStream stream;
    private final AtomicLong samples=new AtomicLong(),bytes=new AtomicLong();private volatile boolean fsynced;
    private final java.util.Set<Integer> videoTracks=ConcurrentHashMap.newKeySet();private final AtomicLong videoSamples=new AtomicLong();
    public FdOutputMuxer(ParcelFileDescriptor output,boolean pause,Runnable processed){this.output=output;this.pause=pause;this.processed=processed;}
    @Override public Muxer create(String ignored)throws MuxerException {
        StageLog.event("WORKER_MUXER_CREATE_BEGIN","");
        if(!created.compareAndSet(false,true))throw new MuxerException("OUTPUT_REOPEN_REJECTED",new IOException());
        try {
            syncFd=ParcelFileDescriptor.dup(output.getFileDescriptor());validationFd=ParcelFileDescriptor.dup(output.getFileDescriptor());
            stream=new ParcelFileDescriptor.AutoCloseOutputStream(output);actual=new Mp4Muxer.Builder(stream).build();
            return new Muxer(){
                public int addTrack(Format format)throws MuxerException{StageLog.event("WORKER_MUXER_TRACK","mime="+format.sampleMimeType+" width="+format.width+" height="+format.height);int id=actual.addTrack(format);if("video/avc".equals(format.sampleMimeType)){videoTracks.add(id);actual.addMetadataEntry(new androidx.media3.container.Mp4OrientationData(format.rotationDegrees));}return id;}
                public void addMetadataEntry(Metadata.Entry entry){if(MuxerUtil.isMetadataSupported(entry))actual.addMetadataEntry(entry);else StageLog.event("MUXER_UNSUPPORTED_METADATA_IGNORED",entry.getClass().getSimpleName());}
                public void writeSampleData(int track,ByteBuffer data,BufferInfo info)throws MuxerException {
                    actual.writeSampleData(track,data,info);samples.incrementAndGet();bytes.addAndGet(info.size);
                    if(videoTracks.contains(track))videoSamples.incrementAndGet();
                    if(info.size>0 && videoTracks.contains(track) && notified.compareAndSet(false,true)){
                        processed.run();if(pause)try{if(!gate.await(30,TimeUnit.SECONDS))throw new IOException("OUTPUT_SAMPLE_GATE_TIMEOUT");}
                        catch(Exception e){if(e instanceof InterruptedException)Thread.currentThread().interrupt();throw new MuxerException("OUTPUT_CANCELLED_OR_GATE_TIMEOUT",e);}
                    }
                }
                public void close()throws MuxerException {if(closed.compareAndSet(false,true))try{actual.close();Os.fsync(syncFd.getFileDescriptor());fsynced=true;}catch(Exception e){throw new MuxerException("OUTPUT_FINALIZE_FAILED",e);}finally{closeQuiet(syncFd);closeQuiet(stream);}}
            };
        }catch(IOException e){throw new MuxerException("OUTPUT_FD_FAILED",e);}
    }
    @Override public ImmutableList<String>getSupportedSampleMimeTypes(int type){return type==C.TRACK_TYPE_VIDEO?ImmutableList.of("video/avc"):type==C.TRACK_TYPE_AUDIO?ImmutableList.of("audio/mp4a-latm"):ImmutableList.of();}
    @Override public boolean supportsWritingNegativeTimestampsInEditList(){return true;}
    /** Reopening, sample accounting and actual video decoding remain in worker UID. */
    public boolean validate(long expectedMs)throws IOException {
        if(!closed.get() || !fsynced || videoSamples.get()==0 || bytes.get()==0 || validationFd==null)return false;
        return AndroidOutputValidator.validate(validationFd.getFileDescriptor(),expectedMs);
    }
    public long bytes(){return bytes.get();}public long samples(){return samples.get();}public long videoSamples(){return videoSamples.get();}public boolean fsynced(){return fsynced;}
    public void releaseGate(){gate.countDown();}
    private static boolean closeQuiet(AutoCloseable value){if(value!=null)try{value.close();}catch(Exception ignored){return false;}return true;}
    public boolean closeDescriptors(){releaseGate();boolean success=true;success&=closeQuiet(stream);success&=closeQuiet(output);success&=closeQuiet(syncFd);success&=closeQuiet(validationFd);return success;}
    @Override public void close(){closeDescriptors();}
}
