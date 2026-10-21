package com.videokit.spike.e4;
import android.os.Bundle;
import android.util.Log;
import androidx.test.runner.AndroidJUnitRunner;
import java.util.*;
public final class E13Instrumentation extends AndroidJUnitRunner {
    private String scope,method;
    private E13FinishOwner completion;private volatile long qualifiedAt;private volatile boolean originalFailure,resultUnknown;private Bundle originalUnknownResult;
    public void prepared(){qualifiedAt=System.nanoTime();}
    public void originalFailure(String why){originalFailure=true;if(completion!=null)completion.fail(why);}
    public static boolean canFinish(){return E11ActivationLifetime.canFinish() && E13SourceGroup.canFinish() && E13PermissionProbe.canFinish();}
    @Override public void onCreate(Bundle args){
        completion=new E13FinishOwner(new E13FinishOwner.Port(){
            public boolean canFinish(){return !resultUnknown&&E13Instrumentation.canFinish();}
            public boolean mainThread(){return android.os.Looper.myLooper()==android.os.Looper.getMainLooper();}
            public void awaitOriginalReturns()throws Exception{E13SourceGroup.awaitOriginalReturns();}
            public void finish(int code,Object saved){Bundle value=new Bundle((Bundle)saved);boolean failed=originalFailure||completion.failed()||qualifiedAt==0||System.nanoTime()-qualifiedAt>30000000000L;if(failed){value.putString("stream",value.getString("stream","")+"\nFAILURES!!! E13_ORIGINAL_FAILURE_OR_QUALIFICATION_TIMEOUT\n");}if(scope!=null){Bundle proof=new Bundle();proof.putString("stream","E13_PLATFORM_FINISH_ADMITTED scope="+scope+" case="+method+" ownersReturned=true\n");sendStatus(0,proof);}E13Instrumentation.super.finish(code,value);}
        });
        E13Stages.sink(s->Log.i("E13_STAGE",s));
        E13Stages.identity(android.os.Process.myUid(),android.os.Process.myPid());
        try{if(args==null || args.hasFileDescriptors())throw new IllegalArgumentException("E13_ARGUMENTS");Map<String,String> a=new TreeMap<>();for(String k:args.keySet()){Object v=args.get(k);if(!(v instanceof String))throw new IllegalArgumentException("E13_STRINGS_ONLY");a.put(k,(String)v);}E13Selection.require(a);scope=a.get("e13ScopeSha256");method=a.get("e13Case");E13Stages.begin(scope,method);E13Stages.at(completion.id,"RUNNER_CREATE","uid="+android.os.Process.myUid()+" pid="+android.os.Process.myPid());super.onCreate(args);}
        catch(Throwable error){Bundle r=new Bundle();r.putString("stream","E13 BLOCKED_SELECTION "+error.getClass().getSimpleName()+"\n");finish(0,r);}
    }
    @Override public void finish(int code,Bundle result){E5AAdmission.invalidateCurrent();if(completion==null)throw new IllegalStateException("E13_ORIGINAL_RUNNER_NOT_CREATED");Bundle snapshot;try{if(result!=null&&result.hasFileDescriptors()){originalUnknownResult=result;resultUnknown=true;throw new IllegalArgumentException("RESULT_ORIGINAL_DESCRIPTOR_UNKNOWN");}snapshot=deepCopy(result);}catch(Throwable bad){originalFailure("RESULT_COPY_OR_BOUND");snapshot=new Bundle();snapshot.putString("stream","FAILURES!!! E13_RESULT_COPY_OR_BOUND\n");}if(code!=android.app.Activity.RESULT_OK||snapshot.getString("stream","").contains("FAILURES!!!"))originalFailure("ORIGINAL_RESULT_FAILURE");completion.request(code,snapshot);}
    private static Bundle deepCopy(Bundle value){android.os.Parcel p=android.os.Parcel.obtain();try{p.writeBundle(value==null?new Bundle():value);if(p.dataSize()>16384)throw new IllegalArgumentException("E13_RESULT_BOUND");p.setDataPosition(0);return p.readBundle(E13Instrumentation.class.getClassLoader());}finally{p.recycle();}}
    @Override public boolean onException(Object source,Throwable error){E5AAdmission.invalidateCurrent();originalFailure(error.getClass().getName());Bundle result=new Bundle();result.putString("stream","FAILURES!!! E13_ORIGINAL_EXCEPTION "+error.getClass().getName()+"\n");finish(0,result);return true;}
}
