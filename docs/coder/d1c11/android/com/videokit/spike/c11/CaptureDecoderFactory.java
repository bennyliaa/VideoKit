package com.videokit.spike.c11;
import android.media.metrics.LogSessionId;
import android.view.Surface;
import androidx.media3.common.Format;
import androidx.media3.transformer.*;
/** Capture-only actual decoder creation stages; no fake progress or deadline extension. */
final class CaptureDecoderFactory implements Codec.DecoderFactory {
    private final Codec.DecoderFactory actual;
    CaptureDecoderFactory(Codec.DecoderFactory actual){this.actual=actual;}
    public Codec createForVideoDecoding(Format format,Surface surface,boolean hdr,LogSessionId session)throws ExportException{
        StageLog.event("CAPTURE_VIDEO_DECODER_BEGIN","mime="+format.sampleMimeType+" width="+format.width+" height="+format.height);
        try{Codec codec=actual.createForVideoDecoding(format,surface,hdr,session);StageLog.event("CAPTURE_VIDEO_DECODER_CREATED","");return codec;}
        catch(ExportException error){StageLog.failure("CAPTURE_VIDEO_DECODER_FAILED",error);throw error;}
    }
    public Codec createForAudioDecoding(Format format,LogSessionId session)throws ExportException{
        StageLog.event("CAPTURE_UNEXPECTED_AUDIO_DECODER_BEGIN","");return actual.createForAudioDecoding(format,session);
    }
}
