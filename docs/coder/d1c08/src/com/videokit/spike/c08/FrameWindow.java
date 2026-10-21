package com.videokit.spike.c08;
/** A three-second source window preserving the requested source timestamp; no zero-frame substitute. */
public final class FrameWindow {
    public final long startMs,endMs,localUs,requestedUs;
    private FrameWindow(long start,long requested){startMs=start;endMs=start+3000;requestedUs=requested;localUs=requested-start*1000;}
    public static FrameWindow at(long requestedUs){
        if(requestedUs<1000000 || requestedUs>Long.MAX_VALUE-3000000)throw new IllegalArgumentException("FRAME_REQUEST_TIME");
        long startMs=(requestedUs-1000000)/1000;return new FrameWindow(startMs,requestedUs);
    }
}
