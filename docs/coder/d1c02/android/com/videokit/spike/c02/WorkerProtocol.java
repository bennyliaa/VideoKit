package com.videokit.spike.c02;

import android.os.IBinder;
public final class WorkerProtocol {
    public static final String WORKER="com.videokit.spike.c02.WORKER",BROKER="com.videokit.spike.c02.BROKER";
    public static final int HELLO=IBinder.FIRST_CALL_TRANSACTION,RUN=HELLO+1,STOP=HELLO+2,READ=HELLO+3;
    public static final int NORMAL=0,EXIT=1,SIGSEGV=2,PRESSURE=3,HANG=4;
    public static final int MAX_BUFFER=65536,MAX_PRESSURE=8*1024*1024;
    private WorkerProtocol(){}
}
