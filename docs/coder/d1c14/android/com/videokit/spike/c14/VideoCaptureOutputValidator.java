package com.videokit.spike.c14;

import android.media.*;
import java.io.*;
import java.nio.ByteBuffer;
import java.util.concurrent.TimeUnit;

/** Separate video-only capture contract; same strict video sample/PTS/full decode gates. Never validates formal edits. */
public final class VideoCaptureOutputValidator {
    public static boolean validate(FileDescriptor fd,long expectedMs)throws IOException{
        MediaExtractor ex=new MediaExtractor();int video=-1,vc=0,ac=0;long lastVideo=-1,videoCount=0;
        try{
            ex.setDataSource(fd);ByteBuffer bytes=ByteBuffer.allocate(1048576);
            for(int i=0;i<ex.getTrackCount();i++){
                MediaFormat f=ex.getTrackFormat(i);String mime=f.getString(MediaFormat.KEY_MIME);
                boolean isVideo=mime!=null && mime.startsWith("video/");
                if(isVideo){vc++;video=i;}else if(mime!=null && mime.startsWith("audio/"))throw new IOException("FRAME_CAPTURE_AUDIO_FORBIDDEN");else throw new IOException("OUTPUT_UNEXPECTED_TRACK");
                OutputValidationRules.Track rule=new OutputValidationRules.Track(isVideo,mime,isVideo?f.getInteger(MediaFormat.KEY_WIDTH):0,isVideo?f.getInteger(MediaFormat.KEY_HEIGHT):0,f.getLong(MediaFormat.KEY_DURATION),expectedMs*1000);
                ex.selectTrack(i);ex.seekTo(0,MediaExtractor.SEEK_TO_PREVIOUS_SYNC);
                while(ex.getSampleTime()>=0){bytes.clear();int n=ex.readSampleData(bytes,0);if(n<0)break;rule.sample(ex.getSampleTime(),n,expectedMs*1000);ex.advance();}
                rule.finish(expectedMs*1000);if(isVideo){lastVideo=rule.last();videoCount=rule.count();}ex.unselectTrack(i);
            }
            FrameCaptureRules.tracks(vc,ac);return decode(fd,video,lastVideo,videoCount);
        }catch(IllegalArgumentException|IllegalStateException e){throw new IOException("OUTPUT_VALIDATION_FAILED",e);}finally{ex.release();}
    }
    private static boolean decode(FileDescriptor fd,int track,long lastSample,long expectedFrames)throws IOException{
        MediaExtractor ex=new MediaExtractor();MediaCodec codec=null;boolean started=false,inputEos=false,outputEos=false;long decoded=0,last=-1;
        try{
            ex.setDataSource(fd);ex.selectTrack(track);MediaFormat format=ex.getTrackFormat(track);
            codec=MediaCodec.createDecoderByType("video/avc");codec.configure(format,null,null,0);codec.start();started=true;
            MediaCodec.BufferInfo info=new MediaCodec.BufferInfo();long stop=System.nanoTime()+TimeUnit.SECONDS.toNanos(15);
            while(!outputEos){
                if(System.nanoTime()>stop)throw new IOException("OUTPUT_DECODE_TIMEOUT");
                if(!inputEos){int index=codec.dequeueInputBuffer(1000);if(index>=0){ByteBuffer buffer=codec.getInputBuffer(index);if(buffer==null)throw new IOException("OUTPUT_DECODE_BUFFER");int n=ex.readSampleData(buffer,0);if(n<0){codec.queueInputBuffer(index,0,0,0,MediaCodec.BUFFER_FLAG_END_OF_STREAM);inputEos=true;}else{codec.queueInputBuffer(index,0,n,ex.getSampleTime(),0);ex.advance();}}}
                int index=codec.dequeueOutputBuffer(info,1000);
                if(index==MediaCodec.INFO_OUTPUT_FORMAT_CHANGED){MediaFormat out=codec.getOutputFormat();if(out.getInteger(MediaFormat.KEY_WIDTH)!=256 || out.getInteger(MediaFormat.KEY_HEIGHT)!=144)throw new IOException("OUTPUT_DECODE_DIMENSIONS");}
                else if(index>=0){try{if(info.size>0 && (info.flags&MediaCodec.BUFFER_FLAG_CODEC_CONFIG)==0){if(info.presentationTimeUs<0 || (last>=0 && info.presentationTimeUs<=last))throw new IOException("OUTPUT_DECODE_PTS");last=info.presentationTimeUs;decoded++;if(decoded>100000)throw new IOException("OUTPUT_DECODE_BUDGET");}}finally{codec.releaseOutputBuffer(index,false);}outputEos=(info.flags&MediaCodec.BUFFER_FLAG_END_OF_STREAM)!=0;}
            }
            if(decoded!=expectedFrames || decoded==0 || last<lastSample-100000)throw new IOException("OUTPUT_DECODE_EMPTY_OR_TRUNCATED");return true;
        }catch(RuntimeException e){throw new IOException("OUTPUT_DECODE_FAILED",e);}finally{if(codec!=null){try{if(started)codec.stop();}finally{codec.release();}}ex.release();}
    }
    private VideoCaptureOutputValidator(){}
}
