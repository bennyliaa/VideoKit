package com.videokit.d1media3.android02.test;
import android.app.*;import android.content.*;import android.content.pm.*;import android.os.*;
import com.videokit.d1android.*;import com.videokit.d1input.*;import com.videokit.spike.e4.*;
import java.nio.charset.StandardCharsets;import java.util.*;import java.util.concurrent.atomic.*;import org.json.*;

/** Built-in Android Instrumentation only: no AndroidX runner, UI, decoder,
 * ordinary isolated codec/GPU probe, network source or production endpoint. */
public final class Media3Instrumentation extends Instrumentation {
 private static final AtomicReference<ExperimentJob> ORIGINAL_CASE=new AtomicReference<>();
 private static final String CERT="5e841a04968f3f790f6996ca5e286d8c2734338542486909f9a136717dde808f";
 private E13FinishOwner finishOwner;private volatile ExperimentJob job;
 @Override public void onCreate(Bundle args){
  super.onCreate(args);
  synchronized(Media3Instrumentation.class){admit(args);}
 }
 private void admit(Bundle args){
  if(ORIGINAL_CASE.get()!=null){Bundle b=new Bundle();b.putString("status","UNKNOWN_EXISTING_ORIGINAL_CASE_RETAINED");sendStatus(-2,b);return;}
  finishOwner=new E13FinishOwner(new E13FinishOwner.Port(){
   public boolean mainThread(){return Looper.myLooper()==Looper.getMainLooper();}
   public boolean canFinish(){ExperimentJob j=job;return j==null?E13SourceGroup.canFinish()&&HostInputFactory.admittedSources()==0&&TemporaryOutput.retained()==0:j.canFinish();}
   public void awaitOriginalReturns()throws Exception{ExperimentJob j=job;if(j!=null)j.awaitOriginalReturns();else E13SourceGroup.awaitOriginalReturns();}
   public void finish(int code,Object saved)throws Exception{
    Bundle b=new Bundle((Bundle)saved);ExperimentJob j=job;String requested=b.getString("status","UNKNOWN_REQUESTED_STATUS");
    int finalCode=code;
    if(j!=null){JSONObject r=new JSONObject(j.receipt(true)).put("requestedStatus",requested).put("runnerFinishGate","SAME_ORIGINAL_CASE_AND_E13_RETURNED");if(finishOwner.failed())r.put("status","UNKNOWN_RUNNER_FINALIZER_FAILURE");else if(requested.startsWith("UNKNOWN"))r.put("status",requested);String text=bounded(r.toString());String semantic=new JSONObject(text).optString("status","UNKNOWN_RECEIPT_STATUS");b.putString("receipt",text);b.putString("status",semantic);if(!isObservation(semantic))finalCode=Activity.RESULT_CANCELED;}
    // This is the sole platform finish. Neither timer nor process disappearance
    // reaches it before the existing original-return finalizer accepts the port.
    Media3Instrumentation.super.finish(finishOwner.failed()?Activity.RESULT_CANCELED:finalCode,b);
    if(j!=null)ORIGINAL_CASE.compareAndSet(j,null);
   }
  });
  try{
   E13FinishOwner.requireAdmission();if(args==null||args.hasFileDescriptors())throw new IllegalArgumentException("EXPERIMENT_ARGUMENT_REJECTED");Map<String,String> values=new HashMap<>();for(String key:args.keySet()){Object value=args.get(key);if(!(value instanceof String))throw new IllegalArgumentException("EXPERIMENT_ARGUMENT_REJECTED");values.put(key,(String)value);}
   ExperimentContract.Method method=ExperimentContract.admit(values);JSONObject identity=ownIdentity();ExperimentJob created=new ExperimentJob(this,method,values.get("runId"),identity);job=created;if(!ORIGINAL_CASE.compareAndSet(null,created))throw new IllegalStateException("ORIGINAL_CASE_ALREADY_RETAINED");start();
  }catch(Throwable e){Bundle b=new Bundle();b.putString("status","BLOCKED_ARGUMENT_OR_EMPTY_SANDBOX_IDENTITY");b.putString("failureClass",e.getClass().getSimpleName());finish(Activity.RESULT_CANCELED,b);}
 }
 private JSONObject ownIdentity()throws Exception{
  Context target=getTargetContext(),test=getContext();String process=Application.getProcessName();if(!ExperimentContract.APP.equals(target.getPackageName())||!ExperimentContract.TEST.equals(test.getPackageName())||!ExperimentContract.PROCESS.equals(process)||target.getApplicationInfo().uid!=android.os.Process.myUid())throw new IllegalStateException("EMPTY_EXPERIMENT_IDENTITY_REQUIRED");
  JSONObject identity=new JSONObject().put("targetPackage",target.getPackageName()).put("testPackage",test.getPackageName()).put("processName",process).put("uid",android.os.Process.myUid()).put("pid",android.os.Process.myPid()).put("sameUidIsRceIsolation",false).put("media3PinnedVersion","1.9.3").put("entryClass",getClass().getName());
  PackageManager pm=target.getPackageManager();for(String name:new String[]{ExperimentContract.APP,ExperimentContract.TEST}){PackageInfo p=pm.getPackageInfo(name,PackageManager.GET_SIGNING_CERTIFICATES);if(p.getLongVersionCode()!=1||!ExperimentContract.VERSION.equals(p.versionName)||p.signingInfo==null||p.signingInfo.getApkContentsSigners().length!=1)throw new IllegalStateException("EXACT_VERSION_AND_SINGLE_SIGNER_REQUIRED");String cert=VerifiedFixtureCopy.hash(p.signingInfo.getApkContentsSigners()[0].toByteArray());if(!CERT.equals(cert))throw new IllegalStateException("EXACT_SIGNER_REQUIRED");identity.put(name,new JSONObject().put("versionCode",p.getLongVersionCode()).put("versionName",p.versionName).put("signerSha256",cert));}
  return identity.put("apkHashes","EXTERNAL_FROZEN_INSTALL_AND_CAPTURE_BINDING_REQUIRED");
 }
 @Override public void onStart(){
  ExperimentJob j=job;if(j==null)return;
  try{Thread worker=new Thread(j::run,"d1media3-android02-"+j.method.name());j.originalWorker=worker;worker.setUncaughtExceptionHandler((t,e)->{j.fail("UNCAUGHT_ORIGINAL_WORKER_UNKNOWN");E13ReturnEvents.returned();});j.startedNano=System.nanoTime();worker.start();worker.join(ExperimentContract.METHOD_DEADLINE_MS);
   if(worker.isAlive()||!j.workerBodyReturned||j.completedNano-j.startedNano<0||j.completedNano-j.startedNano>=60000000000L){j.deadline();Bundle pending=new Bundle();pending.putString("status","UNKNOWN_DEADLINE_ORIGINAL_RETURN_PENDING");pending.putString("receipt",bounded(j.receipt(false)));sendStatus(-2,pending);finish(Activity.RESULT_CANCELED,pending);return;}
   Bundle result=new Bundle();String text=bounded(j.receipt(false));String status=j.canFinish()?new JSONObject(text).optString("status","UNKNOWN_RECEIPT_STATUS"):"UNKNOWN_ORIGINAL_RETURN_PENDING";result.putString("status",status);result.putString("receipt",text);if(!j.canFinish())sendStatus(-2,result);finish(isObservation(status)?Activity.RESULT_OK:Activity.RESULT_CANCELED,result);
  }catch(Throwable e){j.fail("RUNNER_ORIGINAL_WAIT_UNKNOWN");Bundle b=new Bundle();b.putString("status","UNKNOWN_RUNNER_ORIGINAL_WAIT");sendStatus(-2,b);finish(Activity.RESULT_CANCELED,b);}
 }
 private static boolean isObservation(String status){return status.equals("OBSERVED_ALL_SCOPE_HOST_STRUCTURE_ONLY")||status.equals("OBSERVED_HOST_STRUCTURE_ONLY")||status.equals("OBSERVED_HOST_MUX_STRUCTURE_ONLY")||status.equals("PREOPEN_GUARDS_OBSERVED");}
 private static String bounded(String text){if(text.getBytes(StandardCharsets.UTF_8).length<=ExperimentContract.RECEIPT_UTF8_MAX)return text;return "{\"status\":\"FAILED_RECEIPT_BYTE_BUDGET\",\"observationComplete\":false}";}
 @Override public void finish(int code,Bundle result){if(finishOwner==null)throw new IllegalStateException("ORIGINAL_FINALIZER_MISSING");Bundle copy=result==null?new Bundle():new Bundle(result);if(copy.hasFileDescriptors())throw new IllegalArgumentException("RESULT_DESCRIPTORS_FORBIDDEN");finishOwner.request(code,copy);}
 @Override public boolean onException(Object object,Throwable error){ExperimentJob j=job;if(j!=null)j.fail("ANDROID_RUNTIME_ORIGINAL_UNKNOWN");if(finishOwner==null)return false;finishOwner.fail("ANDROID_RUNTIME_ORIGINAL_UNKNOWN");Bundle b=new Bundle();b.putString("status","UNKNOWN_ANDROID_RUNTIME_ORIGINAL");sendStatus(-2,b);finish(Activity.RESULT_CANCELED,b);return true;}
}
