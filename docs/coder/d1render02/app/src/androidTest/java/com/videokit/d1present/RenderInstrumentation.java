package com.videokit.d1present;
import android.os.Bundle;
import androidx.test.runner.AndroidJUnitRunner;
import com.videokit.spike.e4.*;
/** Reuses the existing original-return finalizer; no new host control/diagnostic protocol. */
public final class RenderInstrumentation extends AndroidJUnitRunner {
    private E13FinishOwner finishOwner;
    @Override public void onCreate(Bundle args){
        finishOwner=new E13FinishOwner(new E13FinishOwner.Port(){
            public boolean canFinish(){return WorkSession.allReturned()&&E13SourceGroup.canFinish();}
            public boolean mainThread(){return android.os.Looper.myLooper()==android.os.Looper.getMainLooper();}
            public void awaitOriginalReturns()throws Exception{WorkSession.awaitOriginalReturns();E13SourceGroup.awaitOriginalReturns();}
            public void finish(int code,Object saved){RenderInstrumentation.super.finish(code,new Bundle((Bundle)saved));}
        });
        super.onCreate(args);
    }
    @Override public void finish(int code,Bundle result){
        if(finishOwner==null)throw new IllegalStateException("ORIGINAL_FINALIZER_MISSING");
        Bundle copy=result==null?new Bundle():new Bundle(result);
        if(copy.hasFileDescriptors())throw new IllegalStateException("RESULT_DESCRIPTORS_FORBIDDEN");
        finishOwner.request(code,copy);
    }
    @Override public boolean onException(Object object,Throwable failure){Bundle b=new Bundle();b.putString("stream","FAILURES!!! ORIGINAL_RENDER_EXCEPTION "+failure.getClass().getSimpleName());finish(0,b);return true;}
}
