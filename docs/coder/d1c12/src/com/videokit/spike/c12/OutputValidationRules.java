package com.videokit.spike.c12;

/** Pure preset and sample accounting, shared by host and companion validators. */
public final class OutputValidationRules {
    public static final class Track {
        public final boolean video; private long count,last=-1,first=-1;
        public Track(boolean video,String mime,int width,int height,long durationUs,long expectedUs){
            this.video=video;
            if(!(video?"video/avc":"audio/mp4a-latm").equals(mime))throw new IllegalArgumentException("OUTPUT_CODEC_MISMATCH");
            if(video && (width!=256 || height!=144))throw new IllegalArgumentException("OUTPUT_DIMENSIONS_MISMATCH");
            if(durationUs<=0 || Math.abs(durationUs-expectedUs)>150000)throw new IllegalArgumentException("OUTPUT_DURATION_MISMATCH");
        }
        public void sample(long pts,int size,long expectedUs){
            if(size<=0 || size>1048576 || pts<0 || pts>expectedUs+150000 || (last>=0 && pts<=last))throw new IllegalArgumentException("OUTPUT_SAMPLE_OR_PTS_INVALID");
            if(++count>100000)throw new IllegalArgumentException("OUTPUT_VALIDATION_BUDGET");
            if(first<0)first=pts;last=pts;
        }
        public void finish(long expectedUs){
            if(count==0 || first>150000 || last<expectedUs-200000)throw new IllegalArgumentException("OUTPUT_TRACK_EMPTY_OR_TRUNCATED");
        }
        public long count(){return count;}public long last(){return last;}
    }
    public static void tracks(int video,int audio){if(video!=1 || audio!=1)throw new IllegalArgumentException("OUTPUT_TRACK_SET_MISMATCH");}
    private OutputValidationRules(){}
}
