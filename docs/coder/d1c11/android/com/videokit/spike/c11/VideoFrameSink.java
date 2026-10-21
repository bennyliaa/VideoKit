package com.videokit.spike.c11;
import android.os.ParcelFileDescriptor;
import android.system.Os;
import androidx.media3.common.*;
import androidx.media3.muxer.*;
import com.google.common.collect.ImmutableList;
import java.io.*;
import java.nio.ByteBuffer;
/** Host debug capture evidence only; never implements product edit SinkCoordinator.Host or READY/token. */
public final class VideoFrameSink {
    private final File output;private FileOutputStream stream;private ParcelFileDescriptor sync;
    private volatile boolean opened,finalized,descriptorsClosed,validated;private volatile long bytes,samples;private int track=-1;
    public VideoFrameSink(File ownedOutput,String task)throws IOException{
        output=ownedOutput;try(DataOutputStream journal=new DataOutputStream(new FileOutputStream(new File(output.getPath()+".capture")))){journal.writeUTF("VIDEO_CAPTURE_ONLY");journal.writeUTF(task);journal.flush();}
    }
    public Muxer.Factory muxers(){return new Muxer.Factory(){
        public Muxer create(String ignored)throws MuxerException{
            if(opened)throw new MuxerException("FRAME_CAPTURE_REOPEN",new IOException());opened=true;StageLog.event("CAPTURE_MUXER_CREATE_BEGIN","");
            try{stream=new FileOutputStream(output);sync=ParcelFileDescriptor.dup(stream.getFD());Muxer actual=new Mp4Muxer.Builder(stream).build();return new Muxer(){
                public int addTrack(Format format)throws MuxerException{if(track!=-1 || !"video/avc".equals(format.sampleMimeType) || format.width!=256 || format.height!=144)throw new MuxerException("FRAME_CAPTURE_TRACK_REJECTED",new IOException());track=actual.addTrack(format);actual.addMetadataEntry(new androidx.media3.container.Mp4OrientationData(format.rotationDegrees));StageLog.event("CAPTURE_MUXER_TRACK","mime=video/avc width=256 height=144");return track;}
                public void writeSampleData(int id,ByteBuffer data,BufferInfo info)throws MuxerException{if(id!=track || track<0 || info.size<1 || info.size>1048576 || samples>=100000 || bytes+info.size>2097152)throw new MuxerException("FRAME_CAPTURE_SAMPLE_BUDGET",new IOException());actual.writeSampleData(id,data,info);bytes+=info.size;if(++samples==1 || samples%128==0)StageLog.event("CAPTURE_OUTPUT_SAMPLE","count="+samples+" pts_us="+info.presentationTimeUs+" bytes="+bytes);}
                public void addMetadataEntry(Metadata.Entry entry){if(MuxerUtil.isMetadataSupported(entry))actual.addMetadataEntry(entry);}
                public void close()throws MuxerException{Exception failure=null;try{actual.close();Os.fsync(sync.getFileDescriptor());finalized=true;StageLog.event("CAPTURE_MUXER_FSYNC","samples="+samples+" bytes="+bytes);}catch(Exception error){failure=error;}finally{try{if(sync!=null)sync.close();if(stream!=null)stream.close();descriptorsClosed=true;}catch(IOException error){if(failure==null)failure=error;else failure.addSuppressed(error);}}
                    if(failure!=null)throw new MuxerException("FRAME_CAPTURE_FINALIZE_FAILED",failure);
                }
            };}catch(IOException error){throw new MuxerException("FRAME_CAPTURE_OPEN_FAILED",error);}
        }
        public ImmutableList<String> getSupportedSampleMimeTypes(int type){return type==C.TRACK_TYPE_VIDEO?ImmutableList.of("video/avc"):ImmutableList.of();}
        public boolean supportsWritingNegativeTimestampsInEditList(){return true;}
    };}
    public boolean validate(long duration)throws IOException{
        if(!finalized || !descriptorsClosed || samples<1 || bytes<1)throw new IOException("FRAME_CAPTURE_NOT_FINALIZED");
        try(FileInputStream input=new FileInputStream(output)){validated=VideoCaptureOutputValidator.validate(input.getFD(),duration);return validated;}
    }
    public boolean closeForQuarantine(){boolean done=true;try{if(sync!=null)sync.close();}catch(IOException e){done=false;}try{if(stream!=null)stream.close();}catch(IOException e){done=false;}descriptorsClosed=done;return done;}
    public boolean validated(){return validated;}public long samples(){return samples;}public long bytes(){return bytes;}public String path(){return output.getAbsolutePath();}
}
