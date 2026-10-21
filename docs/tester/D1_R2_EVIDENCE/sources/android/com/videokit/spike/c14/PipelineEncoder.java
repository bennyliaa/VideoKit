package com.videokit.spike.c14;
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
    private volatile MediaCodec codec;private volatile boolean rgbaHeld,yuvHeld;private boolean started;private volatile boolean closed=true,creating;private volatile Image heldImage;private int color,track=-1;private volatile int inputs,outputs;private boolean eos;
    private final PipelineOutputSink sink;private final BooleanSupplier cancelled;private final String fault;volatile String codecName="";
    private final java.util.concurrent.CountDownLatch negotiationEntered,negotiationRelease;
    PipelineEncoder(PipelineOutputSink sink,BooleanSupplier cancelled,String fault,java.util.concurrent.CountDownLatch entered,java.util.concurrent.CountDownLatch release){this.sink=sink;this.cancelled=cancelled;this.fault=fault;negotiationEntered=entered;negotiationRelease=release;}
    private volatile boolean closeUnproven,actualReleasedForTest;private final java.util.concurrent.atomic.AtomicInteger activeCalls=new java.util.concurrent.atomic.AtomicInteger();
    private volatile String phase="ENUMERATE";private volatile EncoderNegotiation negotiation;private volatile EncoderNegotiation.Candidate candidate;
    private final EncoderCapabilities capabilities=new EncoderCapabilities();
    void open()throws Exception{
        if(Looper.myLooper()==Looper.getMainLooper())throw new IOException("PIPE_ENCODER_MAIN_THREAD");
        negotiation=new EncoderNegotiation(new EncoderNegotiation.Driver(){
            public boolean supported(EncoderNegotiation.Candidate c)throws Exception{phase="CAPABILITY";activeCalls.incrementAndGet();try{return !fault.equals("capability-deny") && capabilities.supported(c);}finally{activeCalls.decrementAndGet();}}
            public void create(EncoderNegotiation.Candidate c)throws Exception{candidate=c;phase="CREATE";color=c.color;codecName=c.codec.name;creating=true;closed=false;activeCalls.incrementAndGet();try{codec=MediaCodec.createByCodecName(codecName);creating=false;}finally{activeCalls.decrementAndGet();}}
            public void configure(EncoderNegotiation.Candidate c)throws Exception{phase="CONFIGURE";activeCalls.incrementAndGet();try{codec.configure(EncoderCapabilities.format(c),null,null,MediaCodec.CONFIGURE_FLAG_ENCODE);if(fault.equals("configure-cancel-gate")){negotiationEntered.countDown();if(!negotiationRelease.await(10,TimeUnit.SECONDS))throw new IOException("PIPE_ENCODER_GATE_TIMEOUT");}if(fault.equals("configure-all") || fault.equals("configure-close-ack-loss") || (fault.equals("configure-first") && negotiation.attempts()==1))throw new IOException("PIPE_ENCODER_CONFIGURE_INJECTED");}finally{activeCalls.decrementAndGet();}}
            public void start(EncoderNegotiation.Candidate c)throws Exception{phase="START";activeCalls.incrementAndGet();try{codec.start();started=true;}finally{activeCalls.decrementAndGet();}}
            public void release()throws Exception{releaseCandidate();}
            public boolean released(){return PipelineEncoder.this.released();}
            public void event(String at,EncoderNegotiation.Candidate c,Throwable error,String outcome,boolean first){EncoderDiagnostics.event(at,c,error,outcome,first,negotiation.attempts(),activeCalls.get(),creating,PipelineEncoder.this.released());}
        },cancelled,System::nanoTime);
        List<EncoderNegotiation.Candidate> plan;
        try{phase="ENUMERATE";activeCalls.incrementAndGet();try{plan=capabilities.enumerate(at->phase=at);}finally{activeCalls.decrementAndGet();}}catch(Exception error){EncoderDiagnostics.event(phase,null,error,"FAILED",true,0,activeCalls.get(),creating,released());throw new EncoderNegotiation.Failure(error.getMessage()!=null && error.getMessage().startsWith("PIPE_")?error.getMessage():"PIPE_ENCODER_ENUMERATE_FAILED",phase,error);}
        candidate=negotiation.run(plan);check();phase="MUX";try{sink.open();}catch(Exception error){throw diagnosed(error,"MUX");}StageLog.event("PIPE_ENCODER_OPEN","codec="+codecName+" hardware="+candidate.codec.hardware+" software="+candidate.codec.software+" color_format="+color+" attempts="+negotiation.attempts()+" first_attempt_error="+negotiation.firstError()+" width=256 height=144 surface_created=false audio_present=false");
    }
    private IOException diagnosed(Exception error,String at){if(error instanceof EncoderNegotiation.Failure)return (EncoderNegotiation.Failure)error;EncoderDiagnostics.event(at,candidate,error,"FAILED",false,attempts(),activeCalls.get(),creating,released());String code=error.getMessage();return new EncoderNegotiation.Failure(code!=null && code.matches("PIPE_[A-Z_0-9]{1,64}")?code:"PIPE_ENCODER_"+at+"_FAILED",at,error);}
    private void releaseCandidate()throws Exception{
        if(closeUnproven || (codec==null && creating))throw new IOException("PIPE_CODEC_CLOSE_UNPROVEN");if(closed && heldImage==null)return;phase="CLOSE";
        try{activeCalls.incrementAndGet();if(heldImage!=null){heldImage.close();heldImage=null;}if(codec!=null){if(started){codec.stop();started=false;}codec.release();if(fault.equals("configure-close-ack-loss")){actualReleasedForTest=true;closeUnproven=true;throw new IOException("PIPE_CODEC_CLOSE_UNPROVEN");}codec=null;}closed=true;}
        catch(Exception error){closeUnproven=true;throw error;}finally{activeCalls.decrementAndGet();}
    }
    String phase(){return phase;}
    void diagnosePhase(String at,Throwable error){EncoderDiagnostics.event(at,candidate,error,"FAILED",false,attempts(),activeCalls.get(),creating,released());}boolean selected(){return negotiation!=null && negotiation.selected()!=null;}boolean hardware(){return selected() && candidate.codec.hardware;}boolean software(){return selected() && candidate.codec.software;}boolean heldImage(){return heldImage!=null;}boolean heldCodec(){return codec!=null;}boolean heldRgba(){return rgbaHeld;}boolean heldYuv(){return yuvHeld;}
    int attempts(){return negotiation==null?0:negotiation.attempts();}String firstAttemptError(){return negotiation==null?null:negotiation.firstError();}int pendingCalls(){return activeCalls.get();}boolean creating(){return creating;}
    void confirmActualReleaseForTest()throws IOException{if(!fault.equals("configure-close-ack-loss") || !actualReleasedForTest || activeCalls.get()!=0)throw new IOException("PIPE_TEST_RELEASE_NOT_PROVEN");codec=null;closed=true;creating=false;closeUnproven=false;actualReleasedForTest=false;}
    private void check()throws IOException{if(cancelled.getAsBoolean())throw new IOException("PIPE_CANCELLED");}
    private int input()throws Exception{long stop=System.nanoTime()+TimeUnit.SECONDS.toNanos(3);while(true){check();int index=codec.dequeueInputBuffer(10000);if(index>=0)return index;drain(false);if(System.nanoTime()>stop)throw new IOException("PIPE_ENCODER_INPUT_TIMEOUT");}}
    void frame(PipelinePacket packet,long pts)throws Exception{phase="INPUT";activeCalls.incrementAndGet();try{frameImpl(packet,pts);}catch(Exception error){throw diagnosed(error,phase);}finally{rgbaHeld=false;yuvHeld=false;activeCalls.decrementAndGet();}}
    private void frameImpl(PipelinePacket packet,long pts)throws Exception{
        check();if(inputs>=PipelineRules.FRAMES)throw new IOException("PIPE_ENCODER_FRAME_BUDGET");if(fault.equals("encoder-reject"))throw new IOException("PIPE_ENCODER_INPUT_REJECTED");int index=input();byte[] rgba=packet.pixels();rgbaHeld=true;byte[] yuv=PipelineRules.yuv(rgba,color==19?19:21);yuvHeld=true;
        Throwable primary=null;try{if(color==MediaCodecInfo.CodecCapabilities.COLOR_FormatYUV420Flexible){heldImage=codec.getInputImage(index);if(heldImage==null)throw new IOException("PIPE_ENCODER_INPUT_IMAGE_UNSUPPORTED");fillImage(heldImage,yuv);}
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
        if(!"video/avc".equals(format.getString(MediaFormat.KEY_MIME)) || format.getInteger(MediaFormat.KEY_WIDTH)!=256 || format.getInteger(MediaFormat.KEY_HEIGHT)!=144)throw new IOException("PIPE_ENCODER_OUTPUT_FORMAT");StageLog.event("PIPE_ENCODER_OUTPUT_FORMAT","codec="+codecName+" width=256 height=144 profile="+(format.containsKey(MediaFormat.KEY_PROFILE)?format.getInteger(MediaFormat.KEY_PROFILE):-1)+" level="+(format.containsKey(MediaFormat.KEY_LEVEL)?format.getInteger(MediaFormat.KEY_LEVEL):-1)+" audio_present=false");List<byte[]> csd=new ArrayList<>();int bytes=0;
        for(int i=0;i<2;i++){ByteBuffer value=format.getByteBuffer("csd-"+i);if(value!=null){ByteBuffer copy=value.duplicate();int n=copy.remaining();if(n<1 || n>PipelineRules.MAX_CSD-bytes)throw new IOException("PIPE_ENCODER_CSD_BUDGET");byte[] part=new byte[n];copy.get(part);csd.add(part);bytes+=n;}}
        if(csd.isEmpty())throw new IOException("PIPE_ENCODER_CSD_MISSING");return new Format.Builder().setSampleMimeType("video/avc").setWidth(256).setHeight(144).setRotationDegrees(0).setFrameRate(5).setInitializationData(csd).build();
    }
    private void drain(boolean untilEos)throws Exception{String previous=phase;phase="OUTPUT";activeCalls.incrementAndGet();try{drainImpl(untilEos);}catch(Exception error){throw diagnosed(error,"OUTPUT");}finally{activeCalls.decrementAndGet();phase=previous;}}
    private void drainImpl(boolean untilEos)throws Exception{
        long stop=System.nanoTime()+TimeUnit.SECONDS.toNanos(5);MediaCodec.BufferInfo info=new MediaCodec.BufferInfo();int polls=0;
        while(!eos){check();if(++polls>1000 || System.nanoTime()>stop)throw new IOException("PIPE_ENCODER_OUTPUT_TIMEOUT");int index=codec.dequeueOutputBuffer(info,untilEos?10000:0);
            if(index==MediaCodec.INFO_TRY_AGAIN_LATER){if(!untilEos)return;continue;}
            if(index==MediaCodec.INFO_OUTPUT_FORMAT_CHANGED){if(track!=-1)throw new IOException("PIPE_ENCODER_FORMAT_CHANGED");track=sink.addTrack(outputFormat(codec.getOutputFormat()));continue;}
            if(index>=0){try{if(info.size<0 || info.offset<0 || info.size>PipelineRules.MAX_SAMPLE)throw new IOException("PIPE_ENCODER_OUTPUT_BOUNDS");
                if(info.size>0 && (info.flags&MediaCodec.BUFFER_FLAG_CODEC_CONFIG)==0){ByteBuffer data=codec.getOutputBuffer(index);if(track<0 || data==null || (long)info.offset+info.size>data.limit())throw new IOException("PIPE_ENCODER_OUTPUT_BOUNDS");ByteBuffer sample=data.duplicate();sample.position(info.offset);sample.limit(info.offset+info.size);phase="MUX";try{sink.sample(track,sample.slice(),info);}catch(Exception error){throw diagnosed(error,"MUX");}finally{phase="OUTPUT";}outputs++;StageLog.event("PIPE_ENCODE_SAMPLE","sequence="+outputs+" pts_us="+info.presentationTimeUs+" bytes="+info.size);}
                eos=(info.flags&MediaCodec.BUFFER_FLAG_END_OF_STREAM)!=0;
            }finally{codec.releaseOutputBuffer(index,false);}}
        }
    }
    void finish(long lastPts)throws Exception{phase="INPUT";activeCalls.incrementAndGet();try{int index=input();codec.queueInputBuffer(index,0,0,lastPts+PipelineRules.STEP_US,MediaCodec.BUFFER_FLAG_END_OF_STREAM);phase="OUTPUT";drain(true);if(inputs!=PipelineRules.FRAMES || outputs!=PipelineRules.FRAMES)throw new IOException("PIPE_ENCODER_FRAME_COUNT");}catch(Exception error){throw diagnosed(error,phase);}finally{activeCalls.decrementAndGet();}}
    boolean close(){if(released())return true;if(closeUnproven)return false;try{releaseCandidate();EncoderDiagnostics.event("CLOSE",candidate,null,"RELEASED",false,attempts(),activeCalls.get(),creating,released());}catch(Exception error){EncoderDiagnostics.event("CLOSE",candidate,error,"UNPROVEN",false,attempts(),activeCalls.get(),creating,released());}return released();}
    boolean released(){return closed && !creating && !closeUnproven && activeCalls.get()==0 && heldImage==null;}int inputs(){return inputs;}int outputs(){return outputs;}
}
