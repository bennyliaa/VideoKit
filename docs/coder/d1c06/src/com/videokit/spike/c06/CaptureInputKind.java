package com.videokit.spike.c06;
/** Explicit fixture route contract; typed capture never silently substitutes the MP4 control for AVI. */
public enum CaptureInputKind {
    AVI,MP4;
    public static CaptureInputKind fromRoute(String uri){
        if("vkspike://source/avi".equals(uri))return AVI;
        if("vkspike://source/mp4".equals(uri))return MP4;
        throw new IllegalArgumentException("FRAME_CAPTURE_SOURCE_REJECTED");
    }
}
