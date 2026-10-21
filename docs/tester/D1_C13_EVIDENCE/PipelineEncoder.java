package com.videokit.spike.c13;
import android.media.*;
import android.graphics.ImageFormat;
import android.os.Looper;
import androidx.media3.common.Format;
import java.io.*;
import java.nio.*;
import java.util.*;
import java.util.concurrent.TimeUnit;
import java.util.function.BooleanSupplier;
/** Public system AVC encoder accepts only bounded raw pixels. Never opens or parses compressed source. */
final class PipelineEncoder {
    private MediaCodec codec;private boolean started;private volatile boolean closed=true,creating;private volatile Image heldImage;private int color,track=-1;private volatile int inputs,outputs;private boolean eos;
    private final PipelineOutputSink sink;private final BooleanSupplier cancelled;private final String fault;String codecName="";
    PipelineEncoder(PipelineOutputSink sink,BooleanSupplier cancelled,String fault){this.sink=sink;this.cancelled=cancelled;this.fault=fault;}
    void open()throws Exception{
        if(Looper.myLooper()==Looper.getMainLooper())throw new IOException("PIPE_ENCODER_MAIN_THREAD");
        MediaCodecInfo[] infos=new MediaCodecList(MediaCodecList.REGULAR_CODECS).getCodecInfos();if(infos.length>128)throw new IOException("PIPE_CAPABILITY_UNSUPPORTED");
        MediaCodecInfo chosen=null;
        for(MediaCodecInfo info:infos){if(!info.isEncoder())continue;for(String mime:info.getSupportedTypes())if(mime.equalsIgnoreCase("video/avc")){
            MediaCodecInfo.CodecCapabilities caps=info.getCapabilitiesForType(mime);if(!caps.getVideoCapabilities().areSizeAndRateSupported(256,144,5))continue;
            int found=0;for(int format:caps.colorFormats)if(format==19 || format==21){found=format;break;}if(found==0)for(int format:caps.colorFormats)if(format==MediaCodecInfo.CodecCapabilities.COLOR_FormatYUV420Flexible){found=format;break;}
            if(found!=0){chosen=info;color=found;break;}
        }if(chosen!=null)break;}
        if(chosen==null)throw new IOException("PIPE_CAPABILITY_UNSUPPORTED");codecName=chosen.getName();
        MediaFormat format=MediaFormat.createVideoFormat("video/avc",256,144);format.setInteger(MediaFormat.KEY_COLOR_FORMAT,color);format.setInteger(MediaFormat.KEY_BIT_RATE,600000);format.setInteger(MediaFormat.KEY_FRAME_RATE,5);format.setInteger(MediaFormat.KEY_I_FRAME_INTERVAL,1);format.setInteger(MediaFormat.KEY_MAX_B_FRAMES,0);format.setInteger(MediaFormat.KEY_PROFILE,MediaCodecInfo.CodecProfileLevel.AVCProfileBaseline);format.setInteger(MediaFormat.KEY_COLOR_STANDARD,MediaFormat.COLOR_STANDARD_BT601_PAL);format.setInteger(MediaFormat.KEY_COLOR_RANGE,MediaFormat.COLOR_RANGE_LIMITED);format.setInteger(MediaFormat.KEY_COLOR_TRANSFER,MediaFormat.COLOR_TRANSFER_SDR_VIDEO);
        creating=true;closed=false;codec=MediaCodec.createByCodecName(codecName);creating=false;codec.configure(format,null,null,MediaCodec.CONFIGURE_FLAG_ENCODE);codec.start();started=true;
        sink.open();StageLog.event("PIPE_ENCODER_OPEN","codec="+codecName+" color_format="+color+" width=256 height=144 surface_created=false audio_present=false");
    }
    private void check()throws IOException{if(cancelled.getAsBoolean())throw new IOException("PIPE_CANCELLED");}
    private int input()throws Exception{long stop=System.nanoTime()+TimeUnit.SECONDS.toNanos(3);while(true){check();int index=codec.dequeueInputBuffer(10000);if(index>=0)return index;drain(false);if(System.nanoTime()>stop)throw new IOException("PIPE_ENCODER_INPUT_TIMEOUT");}}
    void frame(PipelinePacket packet,long pts)throws Exception{
        check();if(inputs>=PipelineRules.FRAMES)throw new IOException("PIPE_ENCODER_FRAME_BUDGET");if(fault.equals("encoder-reject"))throw new IOException("PIPE_ENCODER_INPUT_REJECTED");int index=input();byte[] rgba=packet.pixels(),yuv=PipelineRules.yuv(rgba,color==19?19:21);
        Throwable primary=null;try{if(color==MediaCodecInfo.CodecCapabilities.COLOR_FormatYUV420Flexible){heldImage=codec.getInputImage(index);if(heldImage==null)throw new IOException("PIPE_CAPABILITY_UNSUPPORTED");fillImage(heldImage,yuv);}
            else{ByteBuffer data=codec.getInputBuffer(index);if(data==null || data.capacity()<yuv.length || data.capacity()>1048576)throw new IOException("PIPE_ENCODER_INPUT_BOUNDS");data.clear();data.put(yuv);}
            codec.queueInputBuffer(index,0,yuv.length,pts,0);
        }catch(Exception|Error failure){primary=failure;throw failure;}finally{if(heldImage!=null)try{heldImage.close();heldImage=null;}catch(Exception|Error cleanup){if(primary!=null)primary.addSuppressed(cleanup);else throw cleanup;}}
        inputs++;StageLog.event("PIPE_ENCODE_INPUT","sequence="+inputs+" source_task="+packet.identity.task+" source_epoch="+packet.identity.epoch+" source_pid="+packet.identity.pid+" source_uid="+packet.identity.uid+" source_pts="+packet.pts+" raw="+packet.raw+" time_base="+packet.num+"/"+packet.den+" best_effort="+packet.best+" pts_us="+pts+" rgba_sha="+packet.sha);
        if(fault.equals("encoder-error"))throw new IOException("PIPE_ENCODER_INJECTED_ERROR");drain(false);
    }
    private void fillImage(Image image,byte[] nv12)throws IOException{
        if(image.getFormat()!=ImageFormat.YUV_420_888 || image.getWidth()!=256 || image.getHeight()!=144 || image.getPlanes().length!=3)throw new IOException("PIPE_ENCODER_IMAGE_LAYOUT");Image.Plane[] planes=image.getPlanes();
        for(int p=0;p<3;p++){ByteBuffer out=planes[p].getBuffer();PipelineRules.plane(p==0?256:128,p==0?144:72,planes[p].getRowStride(),planes[p].getPixelStride(),out.position(),out.limit());}
        // Clear padding before writing any planes: UV views may alias each other.
        for(int p=0;p<3;p++){ByteBuffer out=planes[p].getBuffer();for(int i=out.position();i<out.limit();i++)out.put(i,(byte)(p==0?16:128));}
        for(int p=0;p<3;p++){int w=p==0?256:128,h=p==0?144:72,row=planes[p].getRowStride(),pixel=planes[p].getPixelStride();ByteBuffer out=planes[p].getBuffer();int base=out.position();
            for(int y=0;y<h;y++)for(int x=0;x<w;x++){int source=p==0?y*256+x:256*144+2*(y*128+x)+(p==1?0:1);out.put(base+y*row+x*pixel,nv12[source]);}
        }
    }
    private Format outputFormat(MediaFormat format)throws IOException{
        if(!"video/avc".equals(format.getString(MediaFormat.KEY_MIME)) || format.getInteger(MediaFormat.KEY_WIDTH)!=256 || format.getInteger(MediaFormat.KEY_HEIGHT)!=144)throw new IOException("PIPE_ENCODER_OUTPUT_FORMAT");List<byte[]> csd=new ArrayList<>();int bytes=0;
        for(int i=0;i<2;i++){ByteBuffer value=format.getByteBuffer("csd-"+i);if(value!=null){ByteBuffer copy=value.duplicate();int n=copy.remaining();if(n<1 || n>PipelineRules.MAX_CSD-bytes)throw new IOException("PIPE_ENCODER_CSD_BUDGET");byte[] part=new byte[n];copy.get(part);csd.add(part);bytes+=n;}}
        if(csd.isEmpty())throw new IOException("PIPE_ENCODER_CSD_MISSING");return new Format.Builder().setSampleMimeType("video/avc").setWidth(256).setHeight(144).setRotationDegrees(0).setFrameRate(5).setInitializationData(csd).build();
    }
    private void drain(boolean untilEos)throws Exception{
        long stop=System.nanoTime()+TimeUnit.SECONDS.toNanos(5);MediaCodec.BufferInfo info=new MediaCodec.BufferInfo();int polls=0;
        while(!eos){check();if(++polls>1000 || System.nanoTime()>stop)throw new IOException("PIPE_ENCODER_OUTPUT_TIMEOUT");int index=codec.dequeueOutputBuffer(info,untilEos?10000:0);
            if(index==MediaCodec.INFO_TRY_AGAIN_LATER){if(!untilEos)return;continue;}
            if(index==MediaCodec.INFO_OUTPUT_FORMAT_CHANGED){if(track!=-1)throw new IOException("PIPE_ENCODER_FORMAT_CHANGED");track=sink.addTrack(outputFormat(codec.getOutputFormat()));continue;}
            if(index>=0){try{if(info.size<0 || info.offset<0 || info.size>PipelineRules.MAX_SAMPLE)throw new IOException("PIPE_ENCODER_OUTPUT_BOUNDS");
                if(info.size>0 && (info.flags&MediaCodec.BUFFER_FLAG_CODEC_CONFIG)==0){ByteBuffer data=codec.getOutputBuffer(index);if(track<0 || data==null || (long)info.offset+info.size>data.limit())throw new IOException("PIPE_ENCODER_OUTPUT_BOUNDS");ByteBuffer sample=data.duplicate();sample.position(info.offset);sample.limit(info.offset+info.size);sink.sample(track,sample.slice(),info);outputs++;StageLog.event("PIPE_ENCODE_SAMPLE","sequence="+outputs+" pts_us="+info.presentationTimeUs+" bytes="+info.size);}
                eos=(info.flags&MediaCodec.BUFFER_FLAG_END_OF_STREAM)!=0;
            }finally{codec.releaseOutputBuffer(index,false);}}
        }
    }
    void finish(long lastPts)throws Exception{int index=input();codec.queueInputBuffer(index,0,0,lastPts+PipelineRules.STEP_US,MediaCodec.BUFFER_FLAG_END_OF_STREAM);drain(true);if(inputs!=PipelineRules.FRAMES || outputs!=PipelineRules.FRAMES)throw new IOException("PIPE_ENCODER_FRAME_COUNT");}
    boolean close(){if(!closed && codec!=null)try{if(started){codec.stop();started=false;}codec.release();closed=true;}catch(Exception error){StageLog.failure("PIPE_CODEC_CLOSE_UNPROVEN",error);}if(heldImage!=null)try{heldImage.close();heldImage=null;}catch(Exception error){StageLog.failure("PIPE_IMAGE_CLOSE_UNPROVEN",error);}return released();}
    boolean released(){return closed && !creating && heldImage==null;}int inputs(){return inputs;}int outputs(){return outputs;}
}
