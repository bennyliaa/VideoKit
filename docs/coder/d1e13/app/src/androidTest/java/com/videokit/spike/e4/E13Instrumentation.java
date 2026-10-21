package com.videokit.spike.e4;
import android.os.Bundle;
import android.util.Log;
import androidx.test.runner.AndroidJUnitRunner;
import java.util.*;
public final class E13Instrumentation extends AndroidJUnitRunner {
    private String scope,method;
    public static boolean canFinish(){return E11ActivationLifetime.canFinish() && E13SourceGroup.canFinish() && E13PermissionProbe.canFinish();}
    @Override public void onCreate(Bundle args){
        try{if(args==null || args.hasFileDescriptors())throw new IllegalArgumentException("E13_ARGUMENTS");Map<String,String> a=new TreeMap<>();for(String k:args.keySet()){Object v=args.get(k);if(!(v instanceof String))throw new IllegalArgumentException("E13_STRINGS_ONLY");a.put(k,(String)v);}E13Selection.require(a);scope=a.get("e13ScopeSha256");method=a.get("e13Case");super.onCreate(args);}
        catch(Throwable error){Bundle r=new Bundle();r.putString("stream","E13 BLOCKED_SELECTION "+error.getClass().getSimpleName()+"\n");finish(0,r);}
    }
    @Override public void finish(int code,Bundle result){E5AAdmission.invalidateCurrent();if(!canFinish()){Log.i("E13_MANAGED","PENDING_ORIGINAL_OWNERS_NO_FINISH scope="+scope+" case="+method+E13SourceGroup.pendingSummary());return;}if(scope!=null){Bundle proof=new Bundle();proof.putString("stream","E13_PLATFORM_FINISH_ADMITTED scope="+scope+" case="+method+" ownersReturned=true\n");sendStatus(0,proof);}super.finish(code,result);}
    @Override public boolean onException(Object source,Throwable error){E5AAdmission.invalidateCurrent();if(!canFinish()){Log.i("E13_MANAGED","PENDING_EXCEPTION_ORIGINAL_OWNERS_NO_FINISH scope="+scope+" case="+method+E13SourceGroup.pendingSummary());return true;}return super.onException(source,error);}
}
