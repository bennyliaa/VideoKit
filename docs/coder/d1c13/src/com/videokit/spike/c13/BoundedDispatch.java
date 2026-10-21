package com.videokit.spike.c13;
import java.io.IOException;
import java.util.concurrent.*;
/** Bounds waiting and cancels queued work; never interrupts an application Looper or claims native work ended. */
public final class BoundedDispatch {
    public static void run(Executor executor,Runnable action,long timeoutMs)throws IOException{
        FutureTask<Void> job=new FutureTask<>(action,null);executor.execute(job);
        try{job.get(timeoutMs,TimeUnit.MILLISECONDS);}
        catch(TimeoutException e){job.cancel(false);throw new IOException("MAIN_LOOPER_TIMEOUT",e);}
        catch(InterruptedException e){job.cancel(false);Thread.currentThread().interrupt();throw new IOException("CANCELLED",e);}
        catch(ExecutionException e){throw new IOException("MAIN_ACTION_FAILED",e.getCause());}
    }
    private BoundedDispatch(){}
}
