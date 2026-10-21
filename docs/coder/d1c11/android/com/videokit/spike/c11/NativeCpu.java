package com.videokit.spike.c11;
/** Loaded exclusively from CpuIsolatedService. Host never calls this class. */
final class NativeCpu {
    static {System.loadLibrary("videokit_alloc");System.loadLibrary("avutil");System.loadLibrary("avcodec");System.loadLibrary("avformat");System.loadLibrary("swscale");System.loadLibrary("videokit_cpu");}
    static native int decode(CpuIsolatedService.Callbacks callbacks,long length,long targetUs,int kind);
    static native int quotaProbe();
    private NativeCpu() {}
}
