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
    private volatile boolean remotePending;private final String id=E13Stages.owner("probe");
    private final E13BindingOwner<ServiceConnection> binding;
    private final ServiceConnection connection=new ServiceConnection(){
        public void onServiceConnected(ComponentName n,IBinder b){binding.callback(()->{if(original==null)original=b;else if(original!=b)unknown=true;connected.countDown();E13Stages.at(id,"CONNECTED_SIGNALLED","");});}
        public void onServiceDisconnected(ComponentName n){binding.callback(()->connected.countDown());}
        public void onNullBinding(ComponentName n){binding.callback(()->connected.countDown());}
        public void onBindingDied(ComponentName n){binding.callback(()->connected.countDown());}
    };
    private E13PermissionProbe(Context c,ComponentName component){context=c;E13FinishOwner.admit(()->OWNERS.add(this));binding=new E13BindingOwner<>(connection,new E13BindingOwner.Port<ServiceConnection>(){
        public boolean bind(ServiceConnection original){return context.bindService(new Intent().setComponent(component),original,Context.BIND_AUTO_CREATE);}
        public void unbind(ServiceConnection original){context.unbindService(original);}
    });}
    private void bind()throws Exception {
        binding.bind();
        if(!binding.accepted() || !connected.await(5000,TimeUnit.MILLISECONDS) || original==null || unknown)throw new IOException("E13_CONTROL_BIND_UNPROVEN");
    }
    private void close(){if(calls!=0){unknown=true;return;}binding.close();tryReturn();}
    private void tryReturn(){if(calls==0 && binding!=null && binding.returned() && !unknown && !remotePending){if(OWNERS.remove(this))E13ReturnEvents.returned();}}
    public static boolean canFinish(){for(E13PermissionProbe p:OWNERS)p.tryReturn();return OWNERS.isEmpty() && E13BindingOwner.allReturned();}
    public static Bundle run(Context context,String scope)throws Exception {
        int fixtureUid=context.getPackageManager().getApplicationInfo("com.videokit.e13.sender",0).uid;
        if(fixtureUid==Process.myUid() || context.getPackageManager().checkSignatures(context.getPackageName(),"com.videokit.e13.sender")!=android.content.pm.PackageManager.SIGNATURE_NO_MATCH)throw new IOException("E13_FIXTURE_MUST_BE_DIFFERENT_SIGNATURE_UID");
        E13PermissionProbe positive=new E13PermissionProbe(context,new ComponentName(context,"com.videokit.spike.e4.E4CodecService"));
        try{
            positive.bind();positive.calls++;
            Bundle hello;E13Stages.at(positive.id,"HELLO_ENTER","uid="+Process.myUid()+" pid="+Process.myPid());try{hello=E4CodecWire.call(positive.original,E4CodecWire.HELLO,new Bundle());}finally{positive.calls--;E13Stages.at(positive.id,"HELLO_RETURN","");E13ReturnEvents.returned();}
            if(hello.getInt("uid")!=Process.myUid())throw new IOException("E13_AUTHORIZED_HELLO_UID");
        }finally{positive.close();}
        E13PermissionProbe negative=new E13PermissionProbe(context,new ComponentName("com.videokit.e13.sender","com.videokit.e13.sender.SenderService"));Bundle result;
        try{
            negative.bind();
            Parcel in=Parcel.obtain(),out=Parcel.obtain();negative.calls++;boolean originalReturned=false;
            try{
                in.writeInterfaceToken("com.videokit.E13_SENDER");in.writeString(scope);
                E13Stages.at(negative.id,"FIXTURE_TRANSACT_ENTER","");if(!negative.original.transact(1,in,out,0) || out.dataSize()>4096)throw new IOException("E13_SENDER_RESPONSE");E13Stages.at(negative.id,"FIXTURE_TRANSACT_RETURN","");out.readException();result=out.readBundle(E13PermissionProbe.class.getClassLoader());
                if(result!=null && scope.equals(result.getString("scope")) && result.getInt("fixtureUid")==fixtureUid && result.getString("ownerId")!=null && !result.getBoolean("resourcesReturned")){
                    String owner=result.getString("ownerId");int pid=result.getInt("fixturePid");negative.remotePending=true;
                    // At most two read-only snapshots of this SAME original. No replay/bind/unbind.
                    for(int query=0;query<2&&!result.getBoolean("resourcesReturned");query++){
                        Parcel q=Parcel.obtain(),r=Parcel.obtain();try{q.writeInterfaceToken("com.videokit.E13_SENDER");q.writeString(scope);q.writeString(owner);E13Stages.at(negative.id,"ORIGINAL_SNAPSHOT_ENTER","query="+query);if(!negative.original.transact(query==0?2:3,q,r,0)||r.dataSize()>4096)throw new IOException("E13_SNAPSHOT_RESPONSE");r.readException();Bundle fresh=r.readBundle(E13PermissionProbe.class.getClassLoader());if(fresh==null||r.dataAvail()!=0||!scope.equals(fresh.getString("scope"))||!owner.equals(fresh.getString("ownerId"))||fresh.getInt("fixtureUid")!=fixtureUid||fresh.getInt("fixturePid")!=pid||!Objects.equals(result.getString("kernelOutcome"),fresh.getString("kernelOutcome")))throw new IOException("E13_SNAPSHOT_ORIGINAL_IDENTITY");result=fresh;E13Stages.at(negative.id,"ORIGINAL_SNAPSHOT_RETURN","resourcesReturned="+result.getBoolean("resourcesReturned"));}catch(Exception error){negative.unknown=true;negative.remotePending=false;throw error;}finally{q.recycle();r.recycle();}
                    }
                    negative.remotePending=!result.getBoolean("resourcesReturned");
                    if("UNKNOWN".equals(result.getString("ownerOutcome"))){negative.unknown=true;negative.remotePending=false;}
                }
                originalReturned=result!=null && scope.equals(result.getString("scope")) && result.getInt("fixtureUid")==fixtureUid && result.getBoolean("resourcesReturned");
                if(result==null || out.dataAvail()!=0 || !scope.equals(result.getString("scope")) || result.getInt("fixtureUid")!=fixtureUid || result.getInt("fixtureUid")<10000 || result.getBoolean("bindAccepted") || !result.getBoolean("bindReturned") || !result.getBoolean("resourcesReturned") || result.getBoolean("internalTransactAttempted") || !Set.of("SECURITY_EXCEPTION","BIND_FALSE").contains(result.getString("kernelOutcome")))throw new IOException("E13_ORDINARY_SENDER_NOT_PROVEN");
            }finally{if(!originalReturned&&!negative.remotePending)negative.unknown=true;negative.calls--;in.recycle();out.recycle();E13ReturnEvents.returned();}
        }finally{negative.close();}
        if(!canFinish())throw new IOException("E13_BINDING_RETURN_UNKNOWN");result.putString("authorizedBindingState",positive.binding.state());result.putString("fixtureClientBindingState",negative.binding.state());return result;
    }
}
