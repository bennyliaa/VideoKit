package com.videokit.spike.c14;

/** Debug-only own-process hook; callable only through E4CodecService's authenticated arm. */
public final class E4DebugFaultBoundary {
    public static void selfSegv(){
        if(!com.videokit.spike.e4.BuildConfig.DEBUG || !android.app.Application.getProcessName().endsWith(":e4_codec"))throw new SecurityException("E4_OWN_DEBUG_CODEC_PROCESS_ONLY");
        NativeFault.segvOwnProcess();
    }
    private E4DebugFaultBoundary(){}
}
