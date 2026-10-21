package com.videokit.spike.c14;
import android.media.MediaCodec;
/** Bounded typed public diagnostics; never arbitrary exception messages or MediaFormat.toString(). */
final class EncoderDiagnostics {
    static void event(String phase,EncoderNegotiation.Candidate c,Throwable error,String outcome,boolean first,int attempt,int pending,boolean creating,boolean released){
        MediaCodec.CodecException codec=null;Throwable cursor=error;for(int i=0;cursor!=null && i<8;i++,cursor=cursor.getCause())if(cursor instanceof MediaCodec.CodecException){codec=(MediaCodec.CodecException)cursor;break;}
        String detail="phase="+phase+" outcome="+outcome+" first_attempt_failure="+first+" attempt="+attempt+" codec="+(c==null?"NONE":c.codec.name)+" color="+(c==null?0:c.color)+" variant="+(c==null?0:c.variant)+" profile="+(c!=null && c.baseline?"BASELINE":"DEFAULT")+" width=256 height=144 fps_hint=5 bitrate=600000 iframe_seconds=1 optional_level=false optional_max_b=false optional_color_keys=false pending_owner_calls="+pending+" creating="+creating+" released="+released;
        if(codec!=null)detail+=" codec_error_code="+codec.getErrorCode()+" diagnostic="+EncoderNegotiation.diagnostic(codec.getDiagnosticInfo())+" recoverable="+codec.isRecoverable()+" transient="+codec.isTransient();
        else if(error!=null)detail+=" exception_class="+error.getClass().getSimpleName();
        StageLog.event("PIPE_ENCODER_DIAGNOSTIC",detail);
    }
    private EncoderDiagnostics(){}
}
