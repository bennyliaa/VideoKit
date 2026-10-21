package com.videokit.spike.e4;
import android.os.Bundle;
import android.util.Log;
import androidx.test.runner.AndroidJUnitRunner;
import java.util.*;

/** Only exact E11 product cases. Legacy migration/whole-class/fault selection is rejected pre-platform. */
public final class E11ActivationInstrumentation extends AndroidJUnitRunner {
    @Override public void onCreate(Bundle args){
        try{
            if(args==null||args.hasFileDescriptors())throw new IllegalArgumentException("E11_ARGUMENT_SCOPE");Map<String,String> selected=new TreeMap<>();
            for(String k:args.keySet()){Object value=args.get(k);if(!(value instanceof String))throw new IllegalArgumentException("E11_STRING_ARGUMENTS_ONLY");selected.put(k,(String)value);}
            E11Selection.require(selected);super.onCreate(args);
        }catch(Throwable failure){Bundle result=new Bundle();result.putString("stream","E11 BLOCKED_SELECTION "+failure.getClass().getSimpleName()+"\n");finish(0,result);}
    }
    @Override public void finish(int code,Bundle result){
        E5AAdmission.invalidateCurrent();
        if(!E11ActivationLifetime.canFinish()){Log.i("E11_MANAGED","PENDING_ORIGINAL_OWNERS_NO_FINISH");return;}
        super.finish(code,result);
    }
    @Override public boolean onException(Object source,Throwable error){E5AAdmission.invalidateCurrent();if(!E11ActivationLifetime.canFinish()){Log.i("E11_MANAGED","PENDING_EXCEPTION_ORIGINAL_OWNERS_NO_FINISH");return true;}return super.onException(source,error);}
}
