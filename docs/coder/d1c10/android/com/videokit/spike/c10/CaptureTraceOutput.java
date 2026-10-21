package com.videokit.spike.c10;
import androidx.media3.extractor.*;
import androidx.media3.common.*;
import androidx.media3.common.util.ParsableByteArray;
import java.io.IOException;
import java.util.*;
/** Capture-only transparent demux instrumentation; bytes/offsets/crypto are forwarded unchanged. */
final class CaptureTraceOutput implements ExtractorOutput {
    private final ExtractorOutput delegate;private final Map<Integer,TrackOutput> tracks=new HashMap<>();
    CaptureTraceOutput(ExtractorOutput delegate){this.delegate=delegate;}
    public TrackOutput track(int id,int type){
        TrackOutput existing=tracks.get(id);if(existing!=null)return existing;if(tracks.size()>=32)throw new IllegalStateException("FRAME_CAPTURE_TRACK_BUDGET");
        TrackOutput target=delegate.track(id,type);StageLog.event("CAPTURE_TRACK_CREATED","id="+id+" type="+type);
        TrackOutput wrapped=new TrackOutput(){long samples;
            public void format(Format format){String mime=format.sampleMimeType;StageLog.event("CAPTURE_INPUT_FORMAT","track="+id+" mime="+(mime!=null && mime.length()<80 && mime.matches("[a-z0-9.+-]+/[a-z0-9.+-]+")?mime:"UNKNOWN")+" width="+format.width+" height="+format.height);target.format(format);}
            public void durationUs(long duration){target.durationUs(duration);}
            public int sampleData(DataReader input,int length,boolean allow,int part)throws IOException{return target.sampleData(input,length,allow,part);}
            public void sampleData(ParsableByteArray input,int length,int part){target.sampleData(input,length,part);}
            public void sampleMetadata(long time,int flags,int size,int offset,CryptoData crypto){if(++samples==1 || samples%128==0)StageLog.event("CAPTURE_INPUT_SAMPLE","track="+id+" type="+type+" count="+samples+" pts_us="+time+" bytes="+size);target.sampleMetadata(time,flags,size,offset,crypto);}
        };tracks.put(id,wrapped);return wrapped;
    }
    public void endTracks(){StageLog.event("CAPTURE_TRACKS_END","count="+tracks.size());delegate.endTracks();}
    public void seekMap(SeekMap seek){StageLog.event("CAPTURE_SEEK_MAP","seekable="+seek.isSeekable()+" duration_us="+seek.getDurationUs());delegate.seekMap(seek);}
}
