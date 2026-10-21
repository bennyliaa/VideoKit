package com.videokit.e13.sender;
import android.app.Service;
import android.content.*;
import android.os.*;
import android.os.Process;
import com.videokit.spike.e4.E13BindingOwner;
import com.videokit.spike.e4.E13Stages;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.Objects;
/** Debug-only ordinary UID. Only probes the fixed non-exported VideoKit codec component. */
public final class SenderService extends Service {
    private final AtomicBoolean consumed=new AtomicBoolean();
    private final java.util.concurrent.atomic.AtomicInteger snapshots=new java.util.concurrent.atomic.AtomicInteger();
    private volatile TargetBinding target;private volatile String originalScope;
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
            if((code!=1&&code!=2&&code!=3) || flags!=0 || out==null || in.dataSize()>1024)return false;
            if(Binder.getCallingUid()!=10221)throw new SecurityException("E13_FIXTURE_CALLER_UID");
            in.enforceInterface("com.videokit.E13_SENDER");String scope=in.readString();
            if(code==2||code==3){String owner=in.readString();TargetBinding held=target;if(in.dataAvail()!=0||held==null||!Objects.equals(scope,originalScope)||!held.owner.id.equals(owner)||snapshots.incrementAndGet()>2)throw new SecurityException("E13_ORIGINAL_SNAPSHOT_IDENTITY_OR_BOUND");if(code==3){E13Stages.at(held.owner.id,"ORIGINAL_ACK_WAIT_ENTER","");try{held.owner.awaitOriginalReturnOrUnknown();}catch(InterruptedException e){Thread.currentThread().interrupt();throw new RemoteException("E13_ORIGINAL_ACK_INTERRUPTED_UNKNOWN");}E13Stages.at(held.owner.id,"ORIGINAL_ACK_WAIT_RETURN","");}writeSnapshot(out,held,scope);return true;}
            if(scope==null || !scope.matches("[0-9a-f]{64}") || in.dataAvail()!=0 || !consumed.compareAndSet(false,true))throw new SecurityException("E13_FIXTURE_SCOPE_OR_REPLAY");
            E13Stages.begin(scope,"ordinarySenderCannotBindCodec");E13Stages.identity(Process.myUid(),Process.myPid());E13Stages.sink(s->android.util.Log.i("E13_STAGE",s));
            TargetBinding original=new TargetBinding();originalScope=scope;target=original;long callerIdentity=Binder.clearCallingIdentity();
            try{if(Binder.getCallingUid()!=Process.myUid())throw new IllegalStateException("E13_NOT_ORDINARY_SELF");original.owner.bind();}
            finally{try{original.owner.close();}finally{Binder.restoreCallingIdentity(callerIdentity);}}
            writeSnapshot(out,original,scope);return true;
        }
    };
    private void writeSnapshot(Parcel out,TargetBinding original,String scope){
            Bundle result=new Bundle();result.putInt("fixtureUid",Process.myUid());result.putInt("fixturePid",Process.myPid());result.putString("scope",scope);result.putString("ownerId",original.owner.id);result.putBoolean("internalTransactAttempted",false);
            String failure=original.owner.bindError();result.putString("kernelOutcome",original.owner.accepted()?"UNEXPECTED_BIND_ACCEPTED":failure.equals(SecurityException.class.getName())?"SECURITY_EXCEPTION":failure.equals("NONE")?"BIND_FALSE":"RETURNED_OTHER_EXCEPTION");
            result.putBoolean("bindReturned",original.owner.bindReturned());result.putBoolean("bindAccepted",original.owner.accepted());result.putBoolean("resourcesReturned",original.owner.returned());result.putString("bindingState",original.owner.state());
            result.putString("ownerOutcome",original.owner.returned()?"RETURNED":original.owner.permanentlyUnknown()?"UNKNOWN":"PENDING");
            out.writeNoException();out.writeBundle(result);if(out.dataSize()>4096)throw new IllegalStateException("E13_SNAPSHOT_REPLY_BOUND");
    }
    @Override public IBinder onBind(Intent intent){return endpoint;}
}
