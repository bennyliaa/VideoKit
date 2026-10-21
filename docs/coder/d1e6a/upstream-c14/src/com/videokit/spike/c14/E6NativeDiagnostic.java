package com.videokit.spike.c14;
import java.io.IOException;
/** Fixed numeric-only cross-process evidence; no native strings, source path, or credentials. */
public final class E6NativeDiagnostic {
    public final int reason,site,stage,avError,packets,decoded,accepted,demuxEof,decoderEof,drain;
    public final long lastPts,readCalls,readBytes;
    public E6NativeDiagnostic(int reason,int site,int stage,int avError,int packets,int decoded,int accepted,int demuxEof,int decoderEof,int drain,long lastPts,long readCalls,long readBytes)throws IOException {
        if(reason<0 || reason>9 || site<0 || site>4096 || stage<0 || stage>6 || avError>0 || packets<0 || packets>4096 || decoded<0 || decoded>4096 || accepted<0 || accepted>6 || accepted>decoded || demuxEof<0 || demuxEof>1 || decoderEof<0 || decoderEof>1 || drain<0 || drain>1 || readCalls<0 || readCalls>8192 || readBytes<0 || readBytes>67108864)throw new IOException("E6_NATIVE_DIAG_PROTOCOL");
        this.reason=reason;this.site=site;this.stage=stage;this.avError=avError;this.packets=packets;this.decoded=decoded;this.accepted=accepted;this.demuxEof=demuxEof;this.decoderEof=decoderEof;this.drain=drain;this.lastPts=lastPts;this.readCalls=readCalls;this.readBytes=readBytes;
        if(site==0 && reason!=0)throw new IOException("E6_NATIVE_DIAG_PROTOCOL");
    }
    public String code(){String[] names={"SITE","DIMENSIONS","EXTRA_FRAME","PTS","MISSING_PTS","DEMUX","SEND","RECEIVE","DRAIN","INCOMPLETE_EOF"};return site==0?"E6_NATIVE_OK":reason==0?"E6_NATIVE_SITE_L"+site:"E6_NATIVE_"+names[reason];}
    public String safe(){return "code="+code()+" site="+site+" stage="+stage+" av_error="+avError+" packets="+packets+" decoded="+decoded+" accepted="+accepted+" last_pts_us="+lastPts+" demux_eof="+demuxEof+" decoder_eof="+decoderEof+" drain="+drain+" read_at_calls="+readCalls+" compressed_bytes="+readBytes;}
}
