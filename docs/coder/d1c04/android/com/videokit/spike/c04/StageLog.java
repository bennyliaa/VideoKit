package com.videokit.spike.c04;
import android.util.Log;
import java.util.concurrent.atomic.AtomicInteger;
/** Monotonic diagnostics; no URI, path, credentials, or raw exception message logged. */
public final class StageLog {
    private static final AtomicInteger count=new AtomicInteger();
    public static void event(String stage,String detail){if(count.incrementAndGet()<=12000)Log.i("VideoKitD1", "mono_ns="+System.nanoTime()+" stage="+stage+" thread="+Thread.currentThread().getId()+" "+detail);}
    public static void failure(String stage,Throwable error){
        StringBuilder chain=new StringBuilder();for(int i=0;error!=null && i<12;i++,error=error.getCause()){
            chain.append(error.getClass().getName()).append(':');String msg=error.getMessage();
            chain.append(msg!=null && msg.matches("[A-Z_0-9]{3,80}")?msg:"REDACTED").append('>');
            StackTraceElement[] frames=error.getStackTrace();for(int f=0;f<Math.min(8,frames.length);f++)chain.append(frames[f].getClassName()).append('.').append(frames[f].getMethodName()).append(':').append(frames[f].getLineNumber()).append('>');
        }event(stage,"cause_chain="+chain);
    }
    public static void mainBlocked(){StringBuilder stack=new StringBuilder();StackTraceElement[] frames=android.os.Looper.getMainLooper().getThread().getStackTrace();for(int i=0;i<Math.min(12,frames.length);i++)stack.append(frames[i].getClassName()).append('.').append(frames[i].getMethodName()).append('>');event("MAIN_LOOPER_TIMEOUT","stack="+stack);}
    private StageLog(){}
}
