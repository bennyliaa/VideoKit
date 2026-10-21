package com.videokit.spike.c06;

/** Debug IPC. No paths, credentials or source FDs cross the input broker. */
public final class MediaProtocol {
    public static final String WORKER="videokit.d1.c06.media.worker",BROKER="videokit.d1.c06.media.broker",CALLBACK="videokit.d1.c06.media.callback";
    public static final int HELLO=1,START=2,CANCEL=3,EXIT=4,SIGSEGV=5,RESUME=6;
    public static final int OPEN=1,READ=2,CLOSE=3;
    public static final int SAMPLE=1,DONE=2,ERROR=3,PROBE_STAGE=4;
    public static final int EXPORT=0,GATE_AFTER_SAMPLE=1,CAPABILITY_PROBE=2;
    public static final int MAX_READ=65536;
    public static final String INPUT_MP4="vkspike://source/mp4";
    private MediaProtocol(){}
}
