package com.videokit.spike.e4;

import android.graphics.ImageFormat;
import android.media.Image;
import android.media.MediaCodec;
import android.media.MediaCodecInfo;
import android.media.MediaFormat;
import android.os.Looper;
import android.os.Bundle;
import androidx.media3.common.Format;
import java.io.IOException;
import java.nio.ByteBuffer;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.TimeUnit;
import java.util.function.BooleanSupplier;

/** Adapted fixed-format algorithms from frozen C14 PipelineEncoder.java/PipelineRules.java.
 * Every platform call and image close belongs to the service owner. */
final class E4Encoder {
    interface Events {void event(String phase,String outcome,String error);}
    private final E4Broker broker;private final E4Protocol.Identity identity;private final E4CodecSink sink;
    private final BooleanSupplier cancelled;private final Events events;private final String fault;
    private final Thread owner=Thread.currentThread();
    private volatile MediaCodec codec;private volatile Image image;private E4Broker.ResourceLease imageLease;
    private volatile boolean creating,started,closed=true,unknown,closeAttempted,rgbaHeld,yuvHeld;
    private volatile int activeCalls,inputs,outputs;
    private boolean eos;private int color,track=-1;private long firstPts=-1,lastPts=-1;
    private volatile E4EncoderNegotiation negotiation;
    private volatile E4EncoderNegotiation.Candidate selected;
    private volatile String phase="NEW",codecName="NONE";
    private volatile String exceptionClass="",diagnosticInfo="UNAVAILABLE",firstAttemptError="";
    private volatile boolean errorCodePresent,recoverable,transientError;private volatile int codecErrorCode;
    E4Encoder(E4Broker broker,E4Protocol.Identity id,E4CodecSink sink,BooleanSupplier cancelled,String fault,Events events){
        this.broker=broker;identity=id;this.sink=sink;this.cancelled=cancelled;this.fault=fault;this.events=events;
    }
    private void owner()throws IOException {if(Thread.currentThread()!=owner || Looper.myLooper()==Looper.getMainLooper())throw new IOException("E4_CODEC_OWNER_REQUIRED");}
    private void check()throws IOException {owner();if(cancelled.getAsBoolean())throw new IOException("E4_CANCELLED");}
    void open()throws Exception {
        check();E4EncoderCapabilities caps=new E4EncoderCapabilities();
        negotiation=new E4EncoderNegotiation(new E4EncoderNegotiation.Driver(){
            public boolean supported(E4EncoderNegotiation.Candidate c)throws Exception {phase="CAPABILITY";activeCalls++;try{return !fault.equals("capability-deny") && caps.supported(c);}finally{activeCalls--;}}
            public void create(E4EncoderNegotiation.Candidate c)throws Exception {phase="CREATE";color=c.color;codecName=c.codec.name;creating=true;closed=false;closeAttempted=false;activeCalls++;try{codec=MediaCodec.createByCodecName(codecName);creating=false;}finally{activeCalls--;}}
            public void configure(E4EncoderNegotiation.Candidate c)throws Exception {phase="CONFIGURE";activeCalls++;try{codec.configure(E4EncoderCapabilities.format(c),null,null,MediaCodec.CONFIGURE_FLAG_ENCODE);if(fault.equals("configure-first") && negotiation.attempts()==1)throw new IOException("E4_DEBUG_CONFIGURE_FIRST");}finally{activeCalls--;}}
            public void start(E4EncoderNegotiation.Candidate c)throws Exception {phase="START";activeCalls++;try{codec.start();started=true;}finally{activeCalls--;}}
            public void release()throws Exception {if(!releaseCandidate())throw new IOException("E4_CODEC_CLOSE_UNPROVEN");}
            public boolean released(){return E4Encoder.this.released();}
            public void event(String at,E4EncoderNegotiation.Candidate c,Throwable error,String outcome,boolean first){if(error!=null)recordFailure(error);if(first)firstAttemptError=safeError(error);events.event(at,outcome,safeError(error));}
        },cancelled,System::nanoTime);
        phase="ENUMERATE";activeCalls++;
        List<E4EncoderNegotiation.Candidate> plan;
        try{plan=caps.enumerate(at->phase=at);}finally{activeCalls--;}
        selected=negotiation.run(plan);check();phase="MUX";activeCalls++;
        try{sink.open();}finally{activeCalls--;}
    }
    private int input()throws Exception {
        long stop=System.nanoTime()+TimeUnit.SECONDS.toNanos(3);
        for(int n=0;n<400;n++){check();int i=codec.dequeueInputBuffer(10000);if(i>=0)return i;drain(false);if(System.nanoTime()>stop)break;}
        throw new IOException("E4_INPUT_TIMEOUT_PENDING");
    }
    void frame(E4Protocol.Frame frame)throws Exception {
        check();if(inputs>=6 || frame.sequence!=inputs+1)throw new IOException("E4_INPUT_FRAME_ORDER");
        phase="INPUT";activeCalls++;Throwable failure=null;
        try{
            long pts=firstPts<0?0:frame.ptsUs-firstPts;
            if(pts<0 || pts>2000000 || lastPts>=0 && pts<=lastPts)throw new IOException("E4_INPUT_TIMELINE");
            int index=input();byte[] rgba=frame.pixels();rgbaHeld=true;byte[] yuv=yuv(rgba,color==19?19:21);yuvHeld=true;
            if(color==MediaCodecInfo.CodecCapabilities.COLOR_FormatYUV420Flexible){
                image=codec.getInputImage(index);if(image==null)throw new IOException("E4_INPUT_IMAGE_UNSUPPORTED");
                final Image owned=image;
                imageLease=broker.registerResource(identity,E4Broker.ResourceKind.IMAGE,owned,()->{owned.close();image=null;});
                fillImage(owned,yuv);
            }else{
                ByteBuffer out=codec.getInputBuffer(index);
                if(out==null || out.capacity()<yuv.length || out.capacity()>1048576)throw new IOException("E4_INPUT_BUFFER_BOUNDS");
                out.clear();out.put(yuv);
            }
            codec.queueInputBuffer(index,0,yuv.length,pts,0);inputs++;if(firstPts<0)firstPts=frame.ptsUs;lastPts=pts;
        }catch(Exception|Error error){failure=error;throw error;}
        finally{
            rgbaHeld=false;yuvHeld=false;
            try{if(imageLease!=null){imageLease.close();imageLease=null;}}
            catch(Exception cleanup){unknown=true;if(failure!=null)failure.addSuppressed(cleanup);else throw cleanup;}
            finally{activeCalls--;}
        }
        drain(false);
    }
    private void drain(boolean untilEos)throws Exception {
        check();phase="OUTPUT";activeCalls++;
        try{
            long deadline=System.nanoTime()+TimeUnit.SECONDS.toNanos(5);MediaCodec.BufferInfo info=new MediaCodec.BufferInfo();
            for(int polls=0;!eos && polls<1000;polls++){
                check();if(System.nanoTime()>deadline)throw new IOException("E4_OUTPUT_TIMEOUT_PENDING");
                int index=codec.dequeueOutputBuffer(info,untilEos?10000:0);
                if(index==MediaCodec.INFO_TRY_AGAIN_LATER){if(!untilEos)return;continue;}
                if(index==MediaCodec.INFO_OUTPUT_FORMAT_CHANGED){if(track>=0)throw new IOException("E4_OUTPUT_FORMAT_CHANGED");track=sink.addTrack(outputFormat(codec.getOutputFormat()));continue;}
                if(index>=0){try{
                    if(info.size<0 || info.offset<0 || info.size>262144)throw new IOException("E4_OUTPUT_SAMPLE_BOUNDS");
                    if(info.size>0 && (info.flags&MediaCodec.BUFFER_FLAG_CODEC_CONFIG)==0){
                        ByteBuffer value=codec.getOutputBuffer(index);
                        if(track<0 || value==null || (long)info.offset+info.size>value.limit() || outputs>=6)throw new IOException("E4_OUTPUT_SAMPLE_BOUNDS");
                        ByteBuffer sample=value.duplicate();sample.position(info.offset);sample.limit(info.offset+info.size);sink.sample(track,sample.slice(),info);outputs++;
                    }
                    eos=(info.flags&MediaCodec.BUFFER_FLAG_END_OF_STREAM)!=0;
                }finally{codec.releaseOutputBuffer(index,false);}}
            }
            if(untilEos && !eos)throw new IOException("E4_OUTPUT_POLL_BUDGET_PENDING");
        }finally{activeCalls--;}
    }
    void finish()throws Exception {
        check();if(inputs!=6)throw new IOException("E4_INPUT_INCOMPLETE");phase="EOS";activeCalls++;
        try{int index=input();codec.queueInputBuffer(index,0,0,lastPts+200000,MediaCodec.BUFFER_FLAG_END_OF_STREAM);}finally{activeCalls--;}
        drain(true);if(outputs!=6)throw new IOException("E4_OUTPUT_FRAME_COUNT");sink.finish();
    }
    private boolean releaseCandidate()throws Exception {
        owner();if(released())return true;if(unknown || closeAttempted || creating && codec==null)return false;closeAttempted=true;phase="CLOSE";activeCalls++;
        try{
            if(imageLease!=null){imageLease.close();imageLease=null;}
            if(codec!=null){if(started){codec.stop();started=false;}codec.release();codec=null;}
            closed=true;
            if(fault.equals("close-unproven")){unknown=true;throw new IOException("E4_DEBUG_CLOSE_ACK_UNPROVEN");}
            return releasedIgnoringCall();
        }catch(Exception failure){unknown=true;throw failure;}finally{activeCalls--;}
    }
    boolean close(){try{return releaseCandidate();}catch(Exception error){events.event("CLOSE","UNPROVEN",safeError(error));return false;}}
    boolean releasedIgnoringCall(){return closed && !creating && !unknown && image==null;}
    boolean released(){return releasedIgnoringCall() && activeCalls==0;}
    int inputs(){return inputs;}int outputs(){return outputs;}int nativeCalls(){return activeCalls;}
    int attempts(){return negotiation==null?0:negotiation.attempts();}String codecName(){return codecName;}
    String phase(){return phase;}boolean selected(){return selected!=null;}boolean rgbaHeld(){return rgbaHeld;}boolean yuvHeld(){return yuvHeld;}
    boolean imageHeld(){return image!=null;}boolean creating(){return creating;}
    static String safeError(Throwable error){String value=error==null?"":error.getMessage();return value!=null && value.matches("(?:E4|PIPE)_[A-Z_0-9]{1,80}")?value:error==null?"":"E4_PLATFORM_CALL_FAILED";}
    void recordFailure(Throwable error){
        if(errorCodePresent)return; // Preserve the first real public codec error rather than replacing it during cleanup.
        Throwable value=error;
        for(int i=0;i<4 && value!=null;i++,value=value.getCause()){
            String name=value.getClass().getName();if(name.matches("[A-Za-z0-9_.$]{1,160}"))exceptionClass=name;
            if(value instanceof MediaCodec.CodecException){MediaCodec.CodecException c=(MediaCodec.CodecException)value;
                codecErrorCode=c.getErrorCode();errorCodePresent=true;recoverable=c.isRecoverable();transientError=c.isTransient();
                String text=c.getDiagnosticInfo();diagnosticInfo=text!=null && text.matches("android\\.media\\.MediaCodec\\.error_[A-Za-z0-9_-]{1,64}")?text:"UNAVAILABLE_PATTERN";return;
            }
        }
    }
    Bundle diagnostics(){Bundle b=new Bundle();E4EncoderNegotiation.Candidate c=selected;
        b.putString("phase",phase);b.putString("firstAttemptError",firstAttemptError);b.putBoolean("selected",c!=null);
        b.putBoolean("hardware",c!=null && c.codec.hardware);b.putBoolean("software",c!=null && c.codec.software);b.putInt("colorFormat",color);
        b.putInt("proposalCount",negotiation==null?0:negotiation.proposals());b.putString("exceptionClass",exceptionClass);b.putString("diagnosticInfo",diagnosticInfo);
        b.putBoolean("codecErrorCodePresent",errorCodePresent);if(errorCodePresent)b.putInt("codecErrorCode",codecErrorCode);
        b.putBoolean("codecRecoverable",recoverable);b.putBoolean("codecTransient",transientError);return b;
    }
    private static Format outputFormat(MediaFormat f)throws Exception {
        if(!"video/avc".equals(f.getString(MediaFormat.KEY_MIME)) || f.getInteger(MediaFormat.KEY_WIDTH)!=256 || f.getInteger(MediaFormat.KEY_HEIGHT)!=144)throw new IOException("E4_OUTPUT_FORMAT_INVALID");
        List<byte[]> csd=new ArrayList<>();int size=0;
        for(int i=0;i<2;i++){ByteBuffer b=f.getByteBuffer("csd-"+i);if(b!=null){ByteBuffer c=b.duplicate();int n=c.remaining();if(n<1 || n>65536-size)throw new IOException("E4_CSD_BUDGET");byte[] bytes=new byte[n];c.get(bytes);csd.add(bytes);size+=n;}}
        if(csd.isEmpty())throw new IOException("E4_CSD_MISSING");
        return new Format.Builder().setSampleMimeType("video/avc").setWidth(256).setHeight(144).setRotationDegrees(0).setFrameRate(5).setInitializationData(csd).build();
    }
    private static void plane(int w,int h,int row,int pixel,int base,int limit)throws IOException {
        long last=(long)base+(long)(h-1)*row+(long)(w-1)*pixel;
        if(row<1 || pixel<1 || pixel>4 || row<(long)w*pixel || base<0 || limit>1048576 || last<0 || last>=limit)throw new IOException("E4_IMAGE_PLANE_BOUNDS");
    }
    private static void fillImage(Image image,byte[] nv12)throws IOException {
        if(image.getFormat()!=ImageFormat.YUV_420_888 || image.getWidth()!=256 || image.getHeight()!=144 || image.getPlanes().length!=3)throw new IOException("E4_IMAGE_LAYOUT");
        Image.Plane[] planes=image.getPlanes();
        for(int p=0;p<3;p++){ByteBuffer b=planes[p].getBuffer();plane(p==0?256:128,p==0?144:72,planes[p].getRowStride(),planes[p].getPixelStride(),b.position(),b.limit());}
        for(int p=0;p<3;p++){ByteBuffer b=planes[p].getBuffer();for(int i=b.position();i<b.limit();i++)b.put(i,(byte)(p==0?16:128));}
        for(int p=0;p<3;p++){ByteBuffer b=planes[p].getBuffer();int base=b.position(),w=p==0?256:128,h=p==0?144:72;
            for(int y=0;y<h;y++)for(int x=0;x<w;x++){int source=p==0?y*256+x:36864+2*(y*128+x)+(p==1?0:1);b.put(base+y*planes[p].getRowStride()+x*planes[p].getPixelStride(),nv12[source]);}}
    }
    private static byte[] yuv(byte[] rgba,int color)throws IOException {
        if(rgba.length!=147456 || color!=19 && color!=21)throw new IOException("E4_RGBA_LAYOUT");byte[] out=new byte[55296];
        for(int y=0;y<144;y++)for(int x=0;x<256;x++){int p=(y*256+x)*4,r=rgba[p]&255,g=rgba[p+1]&255,b=rgba[p+2]&255;out[y*256+x]=(byte)clamp(((66*r+129*g+25*b+128)>>8)+16);}
        for(int y=0;y<144;y+=2)for(int x=0;x<256;x+=2){int r=0,g=0,b=0;for(int dy=0;dy<2;dy++)for(int dx=0;dx<2;dx++){int p=((y+dy)*256+x+dx)*4;r+=rgba[p]&255;g+=rgba[p+1]&255;b+=rgba[p+2]&255;}
            r/=4;g/=4;b/=4;int u=clamp(((-38*r-74*g+112*b+128)>>8)+128),v=clamp(((112*r-94*g-18*b+128)>>8)+128),i=y/2*128+x/2;
            if(color==19){out[36864+i]=(byte)u;out[46080+i]=(byte)v;}else{out[36864+2*i]=(byte)u;out[36864+2*i+1]=(byte)v;}}
        return out;
    }
    private static int clamp(int n){return Math.max(0,Math.min(255,n));}
}
