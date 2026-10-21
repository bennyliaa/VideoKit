package com.videokit.spike.c06;
/** Only a debug ordinary worker's own PID can execute this non-returning signal injection. */
public final class NativeFault {
    static {System.loadLibrary("videokit_d1_lease");}
    public static native void segvOwnProcess();
    private NativeFault(){}
}
