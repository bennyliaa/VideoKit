package com.videokit.e13.sender;
import android.app.Service;
import android.content.*;
import android.os.*;
import android.os.Process;
import com.videokit.spike.e4.E13BindingOwner;
import java.util.concurrent.atomic.AtomicBoolean;
/** Debug-only ordinary UID. Only probes the fixed non-exported VideoKit codec component. */
public final class SenderService extends Service {
    private final AtomicBoolean consumed=new AtomicBoolean();
    private final class TargetBinding implements ServiceConnection {
        final E13BindingOwner<ServiceConnection> owner=new E13BindingOwner<>(this,new E13BindingOwner.Port<ServiceConnection>(){
            public boolean bind(ServiceConnection original){return SenderService.this.bindService(new Intent().setComponent(new ComponentName("com.videokit.app","com.videokit.spike.e4.E4CodecService")),original,Context.BIND_AUTO_CREATE);}
            public void unbind(ServiceConnection original){SenderService.this.unbindService(original);}
        });
        public void onServiceConnected(ComponentName n,IBinder b){owner.callback(()->{});}
        public void onServiceDisconnected(ComponentName n){owner.callback(()->{});}
        public void onNullBinding(ComponentName n){owner.callback(()->{});}
        public void onBindingDied(ComponentName n){owner.callback(()->{});}
    }
    private final Binder endpoint=new Binder(){
        @Override protected boolean onTransact(int code,Parcel in,Parcel out,int flags)throws RemoteException {
            if(code!=1 || flags!=0 || out==null || in.dataSize()>1024)return false;
            in.enforceInterface("com.videokit.E13_SENDER");String scope=in.readString();if(scope==null || !scope.matches("[0-9a-f]{64}") || in.dataAvail()!=0 || !consumed.compareAndSet(false,true))throw new SecurityException("E13_FIXTURE_SCOPE_OR_REPLAY");
            TargetBinding original=new TargetBinding();long callerIdentity=Binder.clearCallingIdentity();
            try{if(Binder.getCallingUid()!=Process.myUid())throw new IllegalStateException("E13_NOT_ORDINARY_SELF");original.owner.bind();}
            finally{try{original.owner.close();}finally{Binder.restoreCallingIdentity(callerIdentity);}}
            Bundle result=new Bundle();result.putInt("fixtureUid",Process.myUid());result.putInt("fixturePid",Process.myPid());result.putString("scope",scope);result.putBoolean("internalTransactAttempted",false);
            String failure=original.owner.bindError();result.putString("kernelOutcome",original.owner.accepted()?"UNEXPECTED_BIND_ACCEPTED":failure.equals(SecurityException.class.getName())?"SECURITY_EXCEPTION":failure.equals("NONE")?"BIND_FALSE":"RETURNED_OTHER_EXCEPTION");
            result.putBoolean("bindReturned",original.owner.bindReturned());result.putBoolean("bindAccepted",original.owner.accepted());result.putBoolean("resourcesReturned",original.owner.returned());result.putString("bindingState",original.owner.state());
            out.writeNoException();out.writeBundle(result);return true;
        }
    };
    @Override public IBinder onBind(Intent intent){return endpoint;}
}
