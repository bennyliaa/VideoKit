package com.videokit.spike.e4;
import android.content.*;
import android.os.*;
import android.os.Process;
import java.io.IOException;
import java.util.*;
import java.util.concurrent.*;
/** Fixed control bindings only, no source/Sink/encoder. Strongly retained until original calls/unbind return. */
public final class E13PermissionProbe {
    private static final Set<E13PermissionProbe> OWNERS=ConcurrentHashMap.newKeySet();
    private final Context context;private final CountDownLatch connected=new CountDownLatch(1);
    private volatile IBinder original;private volatile boolean unknown;private volatile int calls;
    private final E13BindingOwner<ServiceConnection> binding;
    private final ServiceConnection connection=new ServiceConnection(){
        public void onServiceConnected(ComponentName n,IBinder b){binding.callback(()->{if(original==null)original=b;else if(original!=b)unknown=true;connected.countDown();});}
        public void onServiceDisconnected(ComponentName n){binding.callback(()->connected.countDown());}
        public void onNullBinding(ComponentName n){binding.callback(()->connected.countDown());}
        public void onBindingDied(ComponentName n){binding.callback(()->connected.countDown());}
    };
    private E13PermissionProbe(Context c,ComponentName component){context=c;OWNERS.add(this);binding=new E13BindingOwner<>(connection,new E13BindingOwner.Port<ServiceConnection>(){
        public boolean bind(ServiceConnection original){return context.bindService(new Intent().setComponent(component),original,Context.BIND_AUTO_CREATE);}
        public void unbind(ServiceConnection original){context.unbindService(original);}
    });}
    private void bind()throws Exception {
        binding.bind();
        if(!binding.accepted() || !connected.await(5000,TimeUnit.MILLISECONDS) || original==null || unknown)throw new IOException("E13_CONTROL_BIND_UNPROVEN");
    }
    private void close(){if(calls!=0){unknown=true;return;}binding.close();tryReturn();}
    private void tryReturn(){if(calls==0 && binding!=null && binding.returned() && !unknown)OWNERS.remove(this);}
    public static boolean canFinish(){for(E13PermissionProbe p:OWNERS)p.tryReturn();return OWNERS.isEmpty() && E13BindingOwner.allReturned();}
    public static Bundle run(Context context,String scope)throws Exception {
        int fixtureUid=context.getPackageManager().getApplicationInfo("com.videokit.e13.sender",0).uid;
        if(fixtureUid==Process.myUid() || context.getPackageManager().checkSignatures(context.getPackageName(),"com.videokit.e13.sender")!=android.content.pm.PackageManager.SIGNATURE_NO_MATCH)throw new IOException("E13_FIXTURE_MUST_BE_DIFFERENT_SIGNATURE_UID");
        E13PermissionProbe positive=new E13PermissionProbe(context,new ComponentName(context,"com.videokit.spike.e4.E4CodecService"));
        try{
            positive.bind();positive.calls++;
            Bundle hello;try{hello=E4CodecWire.call(positive.original,E4CodecWire.HELLO,new Bundle());}finally{positive.calls--;}
            if(hello.getInt("uid")!=Process.myUid())throw new IOException("E13_AUTHORIZED_HELLO_UID");
        }finally{positive.close();}
        E13PermissionProbe negative=new E13PermissionProbe(context,new ComponentName("com.videokit.e13.sender","com.videokit.e13.sender.SenderService"));Bundle result;
        try{
            negative.bind();
            Parcel in=Parcel.obtain(),out=Parcel.obtain();negative.calls++;boolean originalReturned=false;
            try{
                in.writeInterfaceToken("com.videokit.E13_SENDER");in.writeString(scope);
                if(!negative.original.transact(1,in,out,0) || out.dataSize()>4096)throw new IOException("E13_SENDER_RESPONSE");out.readException();result=out.readBundle(E13PermissionProbe.class.getClassLoader());
                originalReturned=result!=null && scope.equals(result.getString("scope")) && result.getInt("fixtureUid")==fixtureUid && result.getBoolean("resourcesReturned");
                if(result==null || out.dataAvail()!=0 || !scope.equals(result.getString("scope")) || result.getInt("fixtureUid")!=fixtureUid || result.getInt("fixtureUid")<10000 || result.getBoolean("bindAccepted") || !result.getBoolean("bindReturned") || !result.getBoolean("resourcesReturned") || result.getBoolean("internalTransactAttempted") || !Set.of("SECURITY_EXCEPTION","BIND_FALSE").contains(result.getString("kernelOutcome")))throw new IOException("E13_ORDINARY_SENDER_NOT_PROVEN");
            }finally{if(!originalReturned)negative.unknown=true;negative.calls--;in.recycle();out.recycle();}
        }finally{negative.close();}
        if(!canFinish())throw new IOException("E13_BINDING_RETURN_UNKNOWN");result.putString("authorizedBindingState",positive.binding.state());result.putString("fixtureClientBindingState",negative.binding.state());return result;
    }
}
