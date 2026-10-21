package com.videokit.e13.sender;
import android.app.Service;
import android.content.*;
import android.os.*;
import android.os.Process;
import java.util.concurrent.atomic.AtomicBoolean;
/** Debug-only ordinary UID. Only probes the fixed non-exported VideoKit codec component. */
public final class SenderService extends Service {
    private final AtomicBoolean consumed=new AtomicBoolean();
    private final java.util.Set<ServiceConnection> originalConnections=java.util.concurrent.ConcurrentHashMap.newKeySet();
    private final Binder endpoint=new Binder(){
        @Override protected boolean onTransact(int code,Parcel in,Parcel out,int flags)throws RemoteException {
            if(code!=1 || flags!=0 || out==null || in.dataSize()>1024)return false;
            in.enforceInterface("com.videokit.E13_SENDER");String scope=in.readString();if(scope==null || !scope.matches("[0-9a-f]{64}") || in.dataAvail()!=0 || !consumed.compareAndSet(false,true))throw new SecurityException("E13_FIXTURE_SCOPE_OR_REPLAY");
            Bundle result=new Bundle();result.putInt("fixtureUid",Process.myUid());result.putInt("fixturePid",Process.myPid());result.putString("scope",scope);result.putBoolean("internalTransactAttempted",false);
            ServiceConnection original=new ServiceConnection(){public void onServiceConnected(ComponentName n,IBinder b){}public void onServiceDisconnected(ComponentName n){}};
            originalConnections.add(original);
            boolean accepted=false,returned=false;long callerIdentity=Binder.clearCallingIdentity();
            try{
                if(Binder.getCallingUid()!=Process.myUid())throw new IllegalStateException("E13_NOT_ORDINARY_SELF");
                accepted=bindService(new Intent().setComponent(new ComponentName("com.videokit.app","com.videokit.spike.e4.E4CodecService")),original,Context.BIND_AUTO_CREATE);
                result.putString("kernelOutcome",accepted?"UNEXPECTED_BIND_ACCEPTED":"BIND_FALSE");returned=true;
            }catch(SecurityException denied){result.putString("kernelOutcome","SECURITY_EXCEPTION");returned=true;}
            finally{try{if(accepted){try{unbindService(original);}catch(RuntimeException unknown){returned=false;}}if(returned)originalConnections.remove(original);}finally{Binder.restoreCallingIdentity(callerIdentity);}}
            result.putBoolean("bindReturned",returned);result.putBoolean("bindAccepted",accepted);result.putBoolean("resourcesReturned",returned);
            out.writeNoException();out.writeBundle(result);return true;
        }
    };
    @Override public IBinder onBind(Intent intent){return endpoint;}
}
