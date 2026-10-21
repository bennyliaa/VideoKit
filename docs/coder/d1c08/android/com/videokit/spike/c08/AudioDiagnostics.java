package com.videokit.spike.c08;
import androidx.media3.common.*;
import androidx.media3.exoplayer.analytics.AnalyticsListener;
/** Track/renderer/session/focus state is evidence of path, never an assertion that the user heard sound. */
public final class AudioDiagnostics implements AnalyticsListener {
    public static String tracks(Tracks tracks){int audio=0,supported=0,selected=0;for(Tracks.Group g:tracks.getGroups())if(g.getType()==C.TRACK_TYPE_AUDIO)for(int i=0;i<g.length;i++){
        Format f=g.getTrackFormat(i);audio++;if(g.isTrackSupported(i))supported++;if(g.isTrackSelected(i))selected++;
        StageLog.event("AUDIO_TRACK","mime="+f.sampleMimeType+" channels="+f.channelCount+" rate="+f.sampleRate+" support="+g.getTrackSupport(i)+" selected="+g.isTrackSelected(i));
    }return audio==0?"AUDIO_TRACK_MISSING":supported==0?"AUDIO_TRACK_UNSUPPORTED":selected==0?"AUDIO_TRACK_NOT_SELECTED":"AUDIO_PATH_SELECTED_SOUND_NOT_VERIFIED";}
    public void onTracksChanged(EventTime t,Tracks tracks){StageLog.event("AUDIO_TRACK_STATUS",tracks(tracks));}
    public void onAudioDecoderInitialized(EventTime t,String decoder,long initialized,long duration){StageLog.event("AUDIO_RENDERER_INIT","decoder="+decoder+" init_ms="+duration);}
    public void onAudioSessionIdChanged(EventTime t,int id){StageLog.event("AUDIO_SESSION","id="+id);}
    public void onAudioSinkError(EventTime t,Exception e){StageLog.failure("AUDIO_SINK_ERROR",e);}
    public void onAudioCodecError(EventTime t,Exception e){StageLog.failure("AUDIO_CODEC_ERROR",e);}
    public void onPlaybackSuppressionReasonChanged(EventTime t,int reason){StageLog.event("AUDIO_FOCUS_SUPPRESSION","reason="+reason);}
    public void onIsPlayingChanged(EventTime t,boolean playing){StageLog.event("IS_PLAYING","value="+playing);}
    public void onVolumeChanged(EventTime t,float volume){StageLog.event("PLAYER_VOLUME","value="+volume);}
}
