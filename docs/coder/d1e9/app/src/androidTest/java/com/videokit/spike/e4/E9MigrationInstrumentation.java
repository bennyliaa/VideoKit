package com.videokit.spike.e4;

import android.app.Instrumentation;
import android.content.*;
import android.os.*;
import android.util.Log;
import java.io.IOException;
import java.nio.file.Paths;
import java.util.*;

/** Real permission-protected managed actor; no JUnit completion and no file-selected activation. */
public final class E9MigrationInstrumentation extends Instrumentation {
    public static final String CONTROL="com.videokit.app.E9_MIGRATION_CONTROL";
    private E9MigrationRun original;private E9Record request;private Handler events;private BroadcastReceiver receiver;private boolean registered;private String mode;
    @Override public void onCreate(Bundle args){
        try{
            if(args==null||!"legacyN2Migration".equals(args.getString("e9Case"))||!"D1-E9-PREPARE-TABLET-20261018".equals(args.getString("e9Batch"))||args.containsKey("class"))throw new IOException("E9_FORMAL_SELECTION");
            mode=args.getString("e9Mode","");if(!Set.of("READ_ONLY_IDENTITY","REGISTERED_MIGRATION").contains(mode))throw new IOException("E9_EXPLICIT_MODE");
            request=E9Record.parse(E9Record.unpack(args.getString("e9Request",""),8192),8192);
            Context c=getTargetContext();E9AndroidIdentity identity=new E9AndroidIdentity(c,request);
            E9OwnedFiles files=new E9OwnedFiles(Paths.get(c.getApplicationInfo().dataDir,"files"),new E9AndroidFiles());
            original=new E9MigrationRun(request.get("handle"),SystemClock::elapsedRealtimeNanos,new E9MigrationTransaction(files,identity),this::finishOriginal);
            E9MigrationInstrumentationState.retain(original);start();
        }catch(Throwable t){
            if(original!=null){original.controlFault();publish();return;}
            if(E9MigrationInstrumentationState.hasOriginal()){Log.i("E9_MANAGED","PENDING_PRIOR_MANAGED_ACTOR_NO_FINISH");return;}
            // No identity/native/file operation has been launched. Still pass through the real return/finish boundary.
            try{
                original=new E9MigrationRun("00000000-0000-0000-0000-000000000000",SystemClock::elapsedRealtimeNanos,new E9MigrationRun.Operations(){
                    public E9Actor identify()throws Exception{throw new IOException("E9_REJECTED_BEFORE_IDENTITY_IO");}public boolean identityReturned(){return true;}public int identityOwned(){return 0;}
                    public void commit(E9Actor a,String r,E9Record b,E9MigrationRun.Stage s)throws Exception{throw new IOException("E9_NO_WRITE_REQUEST");}public boolean commitReturned(){return true;}public int commitOwned(){return 0;}public String deviceDigest(){return "ABSENT";}
                },this::finishOriginal);original.identify();E9Record snapshot=original.snapshot();original.acknowledgeFinish(snapshot.get("handle"),1,(int)snapshot.number("stateSeq",Integer.MAX_VALUE),original.returnProof().hash());
            }catch(Throwable ignored){if(original!=null)original.controlFault();publish();}
        }
    }
    @Override public void onStart(){
        try{
            events=new Handler(Looper.getMainLooper());receiver=new BroadcastReceiver(){@Override public void onReceive(Context c,Intent intent){handleControl(this,intent);}};
            IntentFilter filter=new IntentFilter(CONTROL);if(Build.VERSION.SDK_INT>=33)getTargetContext().registerReceiver(receiver,filter,"android.permission.DUMP",events,Context.RECEIVER_EXPORTED);else getTargetContext().registerReceiver(receiver,filter,"android.permission.DUMP",events);registered=true;
            armDeadline();new Thread(()->{try{original.identify();}catch(Throwable t){original.controlFault();}finally{if("READ_ONLY_IDENTITY".equals(mode))original.closeUnstartedWriteIngress();publish();}},"E9-original-identity").start();
        }catch(Throwable t){original.controlFault();publish();}
    }
    private void armDeadline()throws Exception{long left=original.remainingNanos();if(left>=0&&!events.postDelayed(()->{try{original.deadline();publish();}catch(Throwable t){original.controlFault();publish();}},Math.max(0,(left+999999)/1000000)))throw new IOException("E9_TIMER_REJECTED");}
    private void handleControl(BroadcastReceiver reply,Intent intent){
        try{
            if(!CONTROL.equals(intent.getAction()))throw new IOException("E9_CONTROL_ACTION");Bundle extras=intent.getExtras();if(extras==null||extras.hasFileDescriptors()||!Set.of("handle","seq","state","command","reserve","archived").containsAll(extras.keySet()))throw new IOException("E9_CONTROL_KEYS_OR_FD");
            String handle=intent.getStringExtra("handle"),command=intent.getStringExtra("command");int seq=intent.getIntExtra("seq",-1),state=intent.getIntExtra("state",-1);
            if("STATUS".equals(command))original.status(handle,seq,state);
            else if("STOP_DEPENDENCIES".equals(command))original.stop(handle,seq,state);
            else if("ACK_FINISH".equals(command))original.acknowledgeFinish(handle,seq,state,intent.getStringExtra("archived"));
            else if("EXECUTE_COMMIT".equals(command)){
                if(!"REGISTERED_MIGRATION".equals(mode))throw new IOException("E9_READONLY_MODE_CANNOT_WRITE");
                byte[] reserve=E9Record.unpack(intent.getStringExtra("reserve"),4096);original.bindAndReserve(reserve,handle,seq,state);armDeadline();new Thread(()->{try{original.execute();}catch(Throwable t){original.controlFault();}finally{publish();}},"E9-original-commit").start();
            }else throw new IOException("E9_CONTROL_COMMAND");
            reply.setResultCode(1);reply.setResultData("E9:"+E9Record.pack(transport().bytes()));publish();
        }catch(Throwable t){original.controlFault();publish();reply.setResultCode(0);try{reply.setResultData("E9:"+E9Record.pack(transport().bytes()));}catch(Throwable ignored){reply.setResultData("E9_CONTROL_UNKNOWN_NO_FINISH");}}
    }
    private E9Record transport()throws Exception{
        String actor="ABSENT",returned="ABSENT";try{actor=E9Record.pack(original.actor().record.bytes());}catch(IOException ignored){}try{returned=E9Record.pack(original.returnProof().bytes());}catch(IOException ignored){}
        return new E9Record(E9Record.map("kind","transport","snapshot",E9Record.pack(original.snapshot().bytes()),"actor",actor,"returned",returned,"mode",mode==null?"REJECTED":mode,"pid",Integer.toString(android.os.Process.myPid()),"uid",Integer.toString(android.os.Process.myUid())),8192);
    }
    private void publish(){try{if(original==null)return;Log.i("E9_MANAGED",new String(original.snapshot().bytes(),java.nio.charset.StandardCharsets.US_ASCII));Bundle b=new Bundle();b.putString("stream","E9:"+E9Record.pack(transport().bytes())+"\n");sendStatus(0,b);}catch(Throwable t){if(original!=null)original.controlFault();}}
    private void finishOriginal(E9Record ignored)throws Exception{
        Runnable close=()->{
            try{
                if(registered){getTargetContext().unregisterReceiver(receiver);registered=false;}
                E9Record proof=original.returnProof();String actor="UNBOUND";try{actor=original.actor().hash();}catch(IOException absent){}
                Log.i("E9_MANAGED","E9_FINAL_FINISH handle="+proofHandle()+" actor="+actor+" returned="+proof.hash());
                Bundle b=new Bundle();b.putString("stream","E9_FINAL "+E9Record.pack(proof.bytes())+"\n");
                E9MigrationInstrumentation.super.finish(proof.get("verdict").equals("QUALIFIED_MIGRATION")?-1:0,b);
            }catch(Throwable t){original.controlFault();publish();}
        };
        if(events==null)close.run();else if(!events.post(close))throw new IOException("E9_FINISH_QUEUE_UNKNOWN");
    }
    private String proofHandle()throws Exception{return original.snapshot().get("handle");}
    @Override public void finish(int code,Bundle result){if(original!=null){original.controlFault();publish();}}
    @Override public boolean onException(Object object,Throwable error){if(original!=null){original.controlFault();publish();}return true;}
    @Override public void onDestroy(){if(original!=null)try{if(!original.snapshot().get("finishClaimed").equals("true")){original.controlFault();publish();}}catch(Exception ignored){}}
}
