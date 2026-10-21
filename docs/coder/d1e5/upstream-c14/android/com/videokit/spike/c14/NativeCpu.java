package com.videokit.spike.c14;
/** Loaded exclusively from CpuIsolatedService. Host never calls this class. */
final class NativeCpu {
    static {System.loadLibrary("videokit_alloc");System.loadLibrary("avutil");System.loadLibrary("avcodec");System.loadLibrary("avformat");System.loadLibrary("swscale");System.loadLibrary("videokit_cpu");}
    static native int decode(CpuIsolatedService.Callbacks callbacks,long length,long targetUs,int kind);
    static native int quotaProbe();
    static native int decodePipelineFrame(CpuIsolatedService.Callbacks callbacks,long length,long targetUs,int kind);
    static native int verifyOutput(CpuIsolatedService.Callbacks callbacks,long length,long[] expectedPts);
    private NativeCpu() {}
}
