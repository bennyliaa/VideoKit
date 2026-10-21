package com.videokit.spike.c08;
/** Separate video-only evidence contract. Never used by formal dual-track edit/export validation. */
public final class FrameCaptureRules {
    public static void tracks(int video,int audio){if(video!=1 || audio!=0)throw new IllegalArgumentException("FRAME_CAPTURE_TRACK_SET_MISMATCH");}
    private FrameCaptureRules(){}
}
