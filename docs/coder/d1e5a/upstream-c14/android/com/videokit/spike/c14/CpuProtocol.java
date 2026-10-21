package com.videokit.spike.c14;
final class CpuProtocol {
    static final String WORKER="videokit.c14.cpu.worker.v1", BROKER="videokit.c14.cpu.broker.v1";
    static final int HELLO=1, START=2, STOP=3, RESUME=4, SELF_SEGV=5, RELEASE_STOP_STALL=6, QUERY_CONTROL=7;
    static final int READ_AT=10, FRAME=11, EVENT=12, BUDGET=13, STAGE=14;
    static final int NORMAL=0, WAIT_FRAME=1, SEGV_FRAME=2, HANG_FRAME=3, FORGE_FRAME=4, FORGE_EPOCH=5, FORGE_IDENTITY=6, QUOTA_PROBE=7, STOP_STALL=8, STOP_ACK_LOSS=9;
    static final int FRAME_ACCEPTED=1, DONE=2, ERROR=3, SIGSEGV_ARMED=4, HANG_ARMED=5, QUOTA_PROVED=6;
    static final int AVI_MPEG4=1, MP4_H264=2;
    static final int PIPELINE_FRAME=10,VERIFY_OUTPUT=11,ORIENTATION=15,VERIFY_FRAME=16;
    private CpuProtocol() {}
    static void end(android.os.Parcel parcel){if(parcel.dataAvail()!=0)throw new SecurityException("CPU_TRAILING_DATA");}
}
