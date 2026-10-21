package com.videokit.spike.c14;
import java.io.*;
import java.security.*;
import java.util.*;
/** Fixed experimental raw-data contract; no container/codec parser or synthetic video generator. */
public final class PipelineRules {
    public static final int FRAMES=6,QUEUE=2,WIDTH=256,HEIGHT=144,RGBA=WIDTH*HEIGHT*4,YUV=WIDTH*HEIGHT*3/2,MAX_SAMPLE=262144,MAX_CSD=65536,MAX_OUTPUT=2097152;
    public static final long STEP_US=200000,MAX_RELATIVE_US=2000000;
    public static final class Identity {
        public final String task;public final long epoch;public final int pid,uid;
        public Identity(String task,long epoch,int pid,int uid){this.task=task;this.epoch=epoch;this.pid=pid;this.uid=uid;}
    }
    public static void layout(int width,int height,int stride,int length,int rotation)throws IOException{
        if(width!=WIDTH || height!=HEIGHT || stride!=WIDTH*4 || length!=RGBA || rotation!=0 || (long)stride*height!=length)throw new IOException("PIPE_FRAME_LAYOUT_OR_ROTATION");
    }
    public static void identity(Identity expected,Identity actual)throws IOException{
        if(expected==null || actual==null || actual.task==null || !actual.task.matches("[a-f0-9]{32}") || !actual.task.equals(expected.task) || actual.epoch<=0 || actual.epoch!=expected.epoch || actual.pid<=0 || actual.uid<=0 || actual.uid%100000<90000 || actual.pid!=expected.pid || actual.uid!=expected.uid)throw new IOException("PIPE_FRAME_IDENTITY");
    }
    public static void plane(int width,int height,int row,int pixel,int base,int limit)throws IOException{long last=(long)base+(long)(height-1)*row+(long)(width-1)*pixel;if(width<1 || width>WIDTH || height<1 || height>HEIGHT || row<1 || pixel<1 || pixel>4 || row<(long)width*pixel || base<0 || limit>1048576 || last<0 || last>=limit)throw new IOException("PIPE_ENCODER_IMAGE_BOUNDS");}
    public static final class Order {
        private int count;private long last=-1,first=-1,total;
        public synchronized long admit(int sequence,long pts)throws IOException{
            if(sequence!=count+1 || sequence>FRAMES || pts<0 || pts>CpuFrameRules.MAX_PTS_US || (last>=0 && pts<=last))throw new IOException("PIPE_FRAME_ORDER");
            long start=first<0?pts:first;if(pts-start>MAX_RELATIVE_US || total+RGBA>(long)FRAMES*RGBA)throw new IOException("PIPE_FRAME_TOTAL_BUDGET");
            first=start;last=pts;count++;total+=RGBA;return pts-start;
        }
        public synchronized int count(){return count;}
    }
    public static String sha(byte[] bytes){try{StringBuilder out=new StringBuilder();for(byte b:MessageDigest.getInstance("SHA-256").digest(bytes))out.append(String.format(Locale.ROOT,"%02x",b&255));return out.toString();}catch(NoSuchAlgorithmException error){throw new AssertionError(error);}}
    public static byte[] thumb(byte[] rgba)throws IOException{
        if(rgba.length!=RGBA)throw new IOException("PIPE_FRAME_LENGTH");byte[] result=new byte[144];
        for(int gy=0;gy<9;gy++)for(int gx=0;gx<16;gx++){int sum=0;for(int y=gy*16;y<gy*16+16;y++)for(int x=gx*16;x<gx*16+16;x++){int p=(y*WIDTH+x)*4;sum+=(77*(rgba[p]&255)+150*(rgba[p+1]&255)+29*(rgba[p+2]&255))>>8;}result[gy*16+gx]=(byte)(sum/256);}return result;
    }
    public static double error(byte[] a,byte[] b)throws IOException{if(a.length!=144 || b.length!=144)throw new IOException("PIPE_THUMB_LENGTH");int sum=0;for(int i=0;i<144;i++)sum+=Math.abs((a[i]&255)-(b[i]&255));return sum/144.0;}
    public static byte[] yuv(byte[] rgba,int color)throws IOException{
        if(rgba.length!=RGBA || (color!=19 && color!=21))throw new IOException("PIPE_ENCODER_INPUT_FORMAT");byte[] out=new byte[YUV];int luma=WIDTH*HEIGHT;
        for(int y=0;y<HEIGHT;y++)for(int x=0;x<WIDTH;x++){int p=(y*WIDTH+x)*4,r=rgba[p]&255,g=rgba[p+1]&255,b=rgba[p+2]&255;out[y*WIDTH+x]=(byte)clamp(((66*r+129*g+25*b+128)>>8)+16);}
        for(int y=0;y<HEIGHT;y+=2)for(int x=0;x<WIDTH;x+=2){int r=0,g=0,b=0;for(int dy=0;dy<2;dy++)for(int dx=0;dx<2;dx++){int p=((y+dy)*WIDTH+x+dx)*4;r+=rgba[p]&255;g+=rgba[p+1]&255;b+=rgba[p+2]&255;}r/=4;g/=4;b/=4;int u=clamp(((-38*r-74*g+112*b+128)>>8)+128),v=clamp(((112*r-94*g-18*b+128)>>8)+128),i=(y/2)*(WIDTH/2)+x/2;if(color==19){out[luma+i]=(byte)u;out[luma+luma/4+i]=(byte)v;}else{out[luma+2*i]=(byte)u;out[luma+2*i+1]=(byte)v;}}
        return out;
    }
    private static int clamp(int n){return Math.max(0,Math.min(255,n));}
    public static void timeline(long[] timeline)throws IOException{if(timeline==null || timeline.length!=FRAMES || timeline[0]!=0)throw new IOException("PIPE_OUTPUT_TIMELINE");for(int i=0;i<timeline.length;i++)if(timeline[i]<0 || timeline[i]>MAX_RELATIVE_US || (i>0 && timeline[i]<=timeline[i-1]))throw new IOException("PIPE_OUTPUT_TIMELINE");}
    public static void content(List<byte[]> source,List<byte[]> decoded)throws IOException{
        if(source.size()!=FRAMES || decoded.size()!=FRAMES)throw new IOException("PIPE_OUTPUT_FRAME_COUNT");double change=0,outputChange=0;
        for(int i=0;i<FRAMES;i++){double own=error(source.get(i),decoded.get(i));if(own>24)throw new IOException("PIPE_OUTPUT_CONTENT_ERROR");
            for(int j=0;j<FRAMES;j++){double separation=error(source.get(i),source.get(j));change=Math.max(change,separation);outputChange=Math.max(outputChange,error(decoded.get(i),decoded.get(j)));if(separation>=4 && own>error(source.get(j),decoded.get(i))+2)throw new IOException("PIPE_OUTPUT_FRAME_MAPPING");}}
        if(change<4 || outputChange<2)throw new IOException("PIPE_CONTENT_NOT_DISTINGUISHABLE");
    }
    private PipelineRules(){}
}
