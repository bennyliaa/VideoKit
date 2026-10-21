package com.videokit.d1present;
import android.content.Context;
import com.videokit.spike.c14.*;
import java.io.*;
import java.nio.file.*;
import java.security.MessageDigest;
import java.util.*;
import java.util.concurrent.CopyOnWriteArrayList;

/** Existing C14 read-only isolated MP4/H264 raw source; no legacy output/registry/migration entry.
 * The generated visual fixture is explicitly separate from decoded media, never a decode PASS.
 */
public final class RawSources implements WorkSession.Factory {
    public static final String BASIC_SHA="720957c94b3665ff97bcc2f59ad5407c5ca54f566b59865723be9eecc0a6a1f9";
    private final Context context;private final boolean generated;
    private final List<CpuTaskClient> retained=new CopyOnWriteArrayList<>();
    private volatile boolean returned,cancelled;private final int rotation;
    private long heldCpuPixelBytes;
    public RawSources(Context context,boolean generated,int rotation){this.context=context.getApplicationContext();this.generated=generated;this.rotation=rotation;}
    public PresentationSource load(String task,String version,Limits.Pixels pixels,long deadline)throws Exception {
        List<RawFrame> frames=new ArrayList<>();
        try{
            Path input=context.getFilesDir().toPath().resolve("d1_render_fixtures/basic.mp4");
            if(!generated){
                if(!Files.isRegularFile(input,LinkOption.NOFOLLOW_LINKS)||Files.size(input)!=349102)throw new IOException("APPROVED_MP4_FIXTURE_MISSING");
                MessageDigest digest=MessageDigest.getInstance("SHA-256");try(InputStream s=Files.newInputStream(input)){byte[] b=new byte[65536];int n;while((n=s.read(b))!=-1){if(cancelled)throw new IOException("SESSION_CANCELLED");if(System.nanoTime()>deadline)throw new IOException("SOURCE_OBSERVATION_EXPIRED");digest.update(b,0,n);}}
                if(!hex(digest.digest()).equals(BASIC_SHA))throw new IOException("APPROVED_MP4_FIXTURE_HASH");
            }
            for(int i=0;i<6;i++){
                if(cancelled)throw new IOException("SESSION_CANCELLED");
                if(System.nanoTime()>deadline)throw new IOException("SOURCE_OBSERVATION_EXPIRED");
                if(generated){
                    int size=256*144*4;pixels.acquire(size);byte[] rgba=null;
                    try{rgba=new byte[size];
                    for(int y=0;y<144;y++)for(int x=0;x<256;x++){int at=(y*256+x)*4;rgba[at]=(byte)(x<128?255:i*35);rgba[at+1]=(byte)(y<72?255:0);rgba[at+2]=(byte)(i*40);rgba[at+3]=(byte)255;}
                        frames.add(new RawFrame(task,version,1,i*200000L,i*200000L,1,1000000,256,144,1024,rotation,rgba,pixels));}
                    finally{rgba=null;pixels.release(size);}
                }else{
                    // The C14 host-side original RGBA result is part of our own Java pixel budget too.
                    pixels.acquire(CpuFrameRules.BYTES);heldCpuPixelBytes+=CpuFrameRules.BYTES;
                    CpuTaskClient cpu=new CpuTaskClient(context,HostFixtures.file(input));retained.add(cpu);Throwable first=null;
                    try{
                        cpu.start(CpuTaskClient.MP4_H264,2000000L+i*200000L,CpuTaskClient.PIPELINE_FRAME);
                        CpuTaskClient.Frame frame=cpu.awaitResult(Math.max(1,Math.min(10000,(deadline-System.nanoTime())/1000000)));
                        if(!cpu.orientationVerified())throw new IOException("RAW_ORIENTATION_UNPROVEN");
                        // C14 decoder's fixed Frame is 256x144 RGBA. Worker-native and Binder/graphics
                        // platform allocations cannot be inferred from these managed-owned bytes.
                        pixels.acquire(CpuFrameRules.BYTES);byte[] copy=null;
                        try{copy=frame.copyPixels();frames.add(new RawFrame(task,version,1,frame.ptsUs,frame.sourceTimestamp,frame.timeBaseNum,frame.timeBaseDen,frame.width,frame.height,frame.stride,0,copy,pixels,cpu.task,cpu.epoch));}
                        finally{copy=null;pixels.release(CpuFrameRules.BYTES);}
                    }catch(Throwable error){first=error;}
                    boolean original=cpu.stopAndAwait(5000);cpu.close();
                    if(original){cpu.awaitOriginalInputThreads();retained.remove(cpu);cpu=null;pixels.release(CpuFrameRules.BYTES);heldCpuPixelBytes-=CpuFrameRules.BYTES;}
                    else throw new IOException("ORIGINAL_CPU_RETURN_UNKNOWN",first);
                    if(first!=null){if(first instanceof Exception)throw (Exception)first;throw (Error)first;}
                }
            }
            PresentationSource source=new PresentationSource(frames,PcmFixture.create());returned=true;return source;
        }catch(Throwable error){
            if(retained.isEmpty()&&CpuTaskClient.quarantinedSources()==0){for(RawFrame f:frames)f.release();if(heldCpuPixelBytes!=0){pixels.release(heldCpuPixelBytes);heldCpuPixelBytes=0;}returned=true;}
            // Unknown CPUs and their original frames remain strongly held by this original factory.
            else heldFrames=frames;
            throw error;
        }
    }
    private List<RawFrame> heldFrames;
    /** Intent only: no platform call, thread interrupt, close retry, or kill on the UI caller. */
    public void cancel(){cancelled=true;}
    public boolean returned(){return returned&&retained.isEmpty()&&CpuTaskClient.quarantinedSources()==0;}
    private static String hex(byte[] bytes){StringBuilder s=new StringBuilder();for(byte b:bytes)s.append(String.format(java.util.Locale.ROOT,"%02x",b&255));return s.toString();}
}
