package com.videokit.spike.c14;
import java.io.*;
/** Immutable owned copy. No pixel reference is exported; caller receives only another bounded copy. */
public final class PipelinePacket {
    public final PipelineRules.Identity identity;public final int sequence;public final long pts,raw;public final int num,den,best;
    private final byte[] rgba;public final String sha;private final byte[] thumb;
    public PipelinePacket(PipelineRules.Identity expected,PipelineRules.Identity actual,int sequence,long pts,long raw,int num,int den,int best,int width,int height,int stride,int rotation,byte[] pixels)throws IOException{
        PipelineRules.identity(expected,actual);if(pixels==null)throw new IOException("PIPE_FRAME_LENGTH");PipelineRules.layout(width,height,stride,pixels.length,rotation);if(sequence<1 || sequence>PipelineRules.FRAMES)throw new IOException("PIPE_FRAME_ORDER");CpuFrameRules.timestamp(raw,num,den,pts,best,1);
        if(pts<0 || pts>CpuFrameRules.MAX_PTS_US)throw new IOException("PIPE_FRAME_PTS");this.identity=actual;this.sequence=sequence;this.pts=pts;this.raw=raw;this.num=num;this.den=den;this.best=best;rgba=pixels.clone();for(int i=3;i<rgba.length;i+=4)if((rgba[i]&255)!=255)throw new IOException("PIPE_FRAME_ALPHA");sha=PipelineRules.sha(rgba);thumb=PipelineRules.thumb(rgba);
    }
    public byte[] pixels(){return rgba.clone();}public byte[] thumb(){return thumb.clone();}
}
