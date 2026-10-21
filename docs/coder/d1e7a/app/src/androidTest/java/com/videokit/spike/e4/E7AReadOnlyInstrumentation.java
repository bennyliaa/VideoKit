package com.videokit.spike.e4;

import android.app.Instrumentation;
import android.content.*;
import android.os.*;
import android.system.*;
import android.util.Log;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.Path;
import java.util.UUID;

/** Explicit asynchronous instrumentation; no JUnit runner and no automatic finish-on-return. */
public final class E7AReadOnlyInstrumentation extends Instrumentation {
    public static final String CONTROL="com.videokit.app.E7A_DIAGNOSTIC_CONTROL";
    private E7ADiagnosticRun<FileDescriptor> original;
    private Handler events;private BroadcastReceiver control;private boolean registered;
    private final String OWNER="E5A_N2_RECOVERY_OWNER_V1 8c6673b7-38a5-4a24-838d-ca8466d8b75f 4869 10221 com.videokit.app 1792224193301\n";
    @Override public void onCreate(Bundle args){
        String handle=args==null?"":args.getString("e7aHandle","");
        try{
            if(!UUID.fromString(handle).toString().equals(handle)||!"originalRecoveryWriterReadOnly".equals(args.getString("e7aCase"))||!"D1-E7A-WRITER-DIAG-TABLET-20261017".equals(args.getString("e7aBatch"))||!"READ_ONLY_MANAGED_NO_ADMISSION".equals(args.getString("e7aScope"))||args.containsKey("class"))throw new IOException("E7A_ARGUMENTS");
            original=new E7ADiagnosticRun<>(handle,SystemClock::elapsedRealtimeNanos,new AndroidOperations(),this::finishPlatform);
            start();
        }catch(Throwable t){
            if(original==null)original=new E7ADiagnosticRun<>("00000000-0000-0000-0000-000000000000",SystemClock::elapsedRealtimeNanos,new AndroidOperations(),this::finishPlatform);
            original.abortBeforeLaunch();publish();E7ADiagnosticRun.Snapshot s=original.snapshot();original.acknowledgeFinish(s.handle,s.sequence);
        }
    }
    @Override public void onStart(){
        boolean attempted=false;
        try{
            if(android.os.Process.myUid()!=10221||!"com.videokit.app".equals(android.app.Application.getProcessName())||!"com.videokit.app".equals(getTargetContext().getPackageName())||E4Session.retainedSessions()!=0||E4Session.reservedEncoderSlots()!=0)throw new IOException("E7A_ORIGINAL_IDLE_APP");
            events=new Handler(Looper.getMainLooper());
            control=new BroadcastReceiver(){@Override public void onReceive(Context c,Intent intent){
                try{
                    if(!CONTROL.equals(intent.getAction())||!original.snapshot().handle.equals(intent.getStringExtra("handle"))){setResultCode(0);setResultData("REJECTED_HANDLE");return;}
                    String command=intent.getStringExtra("command");
                    if("STATUS".equals(command))original.deadline();
                    else if("STOP_DEPENDENCIES".equals(command))original.stopDependencies();
                    else if("ACK_FINISH".equals(command))original.acknowledgeFinish(intent.getStringExtra("handle"),intent.getIntExtra("archivedSequence",-1));
                    else{setResultCode(0);setResultData("REJECTED_COMMAND");return;}
                    setResultCode(1);setResultData(original.snapshot().record());publish();
                }catch(Throwable t){original.controlFault();publish();setResultCode(0);setResultData("CONTROL_EXCEPTION_NO_FINISH");}
            }};
            // Sender must hold this existing signature/privileged permission; app requests no new permission.
            IntentFilter filter=new IntentFilter(CONTROL);
            if(Build.VERSION.SDK_INT>=33)getTargetContext().registerReceiver(control,filter,"android.permission.DUMP",events,Context.RECEIVER_EXPORTED);
            else getTargetContext().registerReceiver(control,filter,"android.permission.DUMP",events);
            registered=true;
            if(!events.postDelayed(()->{try{original.deadline();publish();}catch(Throwable t){original.controlFault();publish();}},10000))throw new IOException("E7A_TIMER_UNAVAILABLE");
            publish();original.beginLaunch();attempted=true;
            new Thread(()->{try{original.run();}catch(Throwable t){original.controlFault();}finally{publish();}},"E7A-original-owner").start();
            // Returning from Instrumentation.onStart does not invoke finish. Only archive ACK may do so.
        }catch(Throwable t){
            if(attempted)original.controlFault();else original.abortBeforeLaunch();publish();
            // A failed launch with uncertain outcome is retained. A certified prelaunch rejection is safe.
            if(!attempted){E7ADiagnosticRun.Snapshot s=original.snapshot();original.acknowledgeFinish(s.handle,s.sequence);}
        }
    }
    private void publish(){
        try{String text=original.snapshot().record();if(text.length()>4096){original.controlFault();text="E7A DIAGNOSTIC_BOUND PENDING admission=NONE";}Log.i("E7A_READ_ONLY",text);Bundle b=new Bundle();b.putString("stream",text+"\n");sendStatus(0,b);}catch(Throwable t){if(original!=null)original.controlFault();}
    }
    /** Reject unsolicited framework/library finish, rather than inheriting a kill-on-finish path. */
    @Override public void finish(int code,Bundle results){if(original!=null){original.controlFault();publish();}}
    @Override public boolean onException(Object object,Throwable failure){if(original!=null){original.controlFault();publish();}return true;}
    @Override public void onDestroy(){if(original!=null&&!original.snapshot().finishClaimed){original.controlFault();publish();}}
    private void finishPlatform(E7ADiagnosticRun.Snapshot snapshot)throws Exception{
        Runnable complete=()->{
            try{
                if(registered){getTargetContext().unregisterReceiver(control);registered=false;}
                E7ADiagnosticRun.Snapshot current=original.snapshot();
                Bundle b=new Bundle();b.putString("stream",current.record()+" platformFinish=REQUESTED_AFTER_ORIGINAL_RETURNS\n");
                E7AReadOnlyInstrumentation.super.finish(current.verdict.equals("QUALIFIED_DIAGNOSTIC")?-1:0,b);
            }catch(Throwable t){original.controlFault();publish();}
        };
        // Queue behind the ordered control reply; no job is cancelled or closed here.
        if(events==null)complete.run();else if(!events.post(complete))throw new IOException("E7A_FINISH_QUEUE_UNAVAILABLE");
    }
    private final class AndroidOperations implements E7ADiagnosticRun.Operations<FileDescriptor> {
        Path path;StructStat before;
        public void preflight()throws Exception{
            Path base=getTargetContext().getFilesDir().toPath();path=base.resolve("e4a_output_budget/N2-e5-recovery/recovery.owner");
            for(Path p:new Path[]{base,base.resolve("e4a_output_budget"),path.getParent()}){StructStat st=Os.lstat(p.toString());if(!OsConstants.S_ISDIR(st.st_mode)||st.st_uid!=10221)throw new IOException("E7A_OWNER_DIRECTORY_ROLE");}
            before=Os.lstat(path.toString());role(before);
        }
        public FileDescriptor open()throws Exception{return Os.open(path.toString(),OsConstants.O_RDONLY|OsConstants.O_NOFOLLOW|OsConstants.O_NONBLOCK,0);}
        public void readAndVerify(FileDescriptor fd)throws Exception{
            StructStat opened=Os.fstat(fd);same(before,opened);byte[] bytes=new byte[257];int total=0;
            while(total<bytes.length){int n=Os.read(fd,bytes,total,bytes.length-total);if(n==0)break;total+=n;}
            if(total>256||!OWNER.equals(new String(bytes,0,total,StandardCharsets.US_ASCII)))throw new IOException("E7A_FIXED_OWNER_BYTES_MISMATCH");same(opened,Os.fstat(fd));
        }
        public void close(FileDescriptor fd)throws Exception{Os.close(fd);}
        public void afterClose()throws Exception{same(before,Os.lstat(path.toString()));}
        public String diagnose()throws Exception{
            E5N2RecoveryAndroid platform=new E5N2RecoveryAndroid(getTargetContext());String status="RETURNED_CURRENT_GATE";
            try{platform.requireRecoveryWriterDead(E5AOwner.parse(OWNER.getBytes(StandardCharsets.US_ASCII)));}catch(IOException rejected){status="BLOCKED_CURRENT_GATE";}
            return status+" "+platform.evidence()+" observation=NOT_CALLED persistentWrites=0 mediaReads=0";
        }
        private void role(StructStat s)throws IOException{if(!OsConstants.S_ISREG(s.st_mode)||s.st_uid!=10221||s.st_size<1||s.st_size>256)throw new IOException("E7A_OWNER_FILE_ROLE");}
        private void same(StructStat a,StructStat b)throws IOException{role(b);if(a.st_dev!=b.st_dev||a.st_ino!=b.st_ino||a.st_size!=b.st_size||a.st_mtime!=b.st_mtime||a.st_ctime!=b.st_ctime)throw new IOException("E7A_OWNER_FILE_CHANGED");}
    }
}
