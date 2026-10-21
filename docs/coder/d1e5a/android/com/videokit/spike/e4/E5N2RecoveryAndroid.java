package com.videokit.spike.e4;

import android.app.ActivityManager;
import android.app.ApplicationExitInfo;
import android.content.Context;
import android.os.Process;
import android.system.*;
import java.io.*;
import java.nio.file.Path;
import java.util.*;
import com.videokit.spike.c14.AndroidLease;

/** Actual Android evidence adapter; no shell, ADB, fabricated death, reset, or media access. */
public final class E5N2RecoveryAndroid implements E5AFinalObservation.Platform {
    private final Context context;private final E5ADirectoryBarrier<FileDescriptor> directories;private String evidence="";
    public String evidence(){return evidence;}
    public E5N2RecoveryAndroid(Context c){context=c.getApplicationContext();directories=new E5ADirectoryBarrier<>(new E5ADirectoryBarrier.Operations<FileDescriptor>(){
        public FileDescriptor open(Path p)throws Exception{return Os.open(p.toString(),OsConstants.O_RDONLY|OsConstants.O_NOFOLLOW,0);}
        public void force(FileDescriptor d)throws Exception{if(!OsConstants.S_ISDIR(Os.fstat(d).st_mode))throw new IOException("E5A_DIRECTORY_ROLE");Os.fsync(d);}
        public void close(FileDescriptor d)throws Exception{Os.close(d);}
    });}
    public E5N2Recovery.Death death(int pid)throws Exception {
        if(E4Session.retainedSessions()!=0 || E4Session.reservedEncoderSlots()!=0)throw new IOException("E5_N2_RECOVERY_REQUIRES_IDLE_PRODUCT_HOST");
        if(Process.myUid()!=E5N2Recovery.UID || Process.myPid()==pid || !context.getPackageName().equals("com.videokit.app"))throw new IOException("E5_N2_ORIGINAL_APP_UID_REQUIRED");
        String name=pid==E5N2Recovery.HOST?"com.videokit.app":pid==E5N2Recovery.CODEC?"com.videokit.app:e4_codec":"";
        if(name.isEmpty())throw new IOException("E5_N2_PID_NOT_ALLOWED");
        List<ApplicationExitInfo> rows=context.getSystemService(ActivityManager.class).getHistoricalProcessExitReasons(context.getPackageName(),pid,8);
        ApplicationExitInfo found=null;int count=0;
        for(ApplicationExitInfo r:rows)if(r.getPid()==pid && r.getRealUid()==E5N2Recovery.UID && name.equals(r.getProcessName()) && r.getTimestamp()>=1792208947872L && r.getTimestamp()<=1792208970000L){found=r;count++;}
        evidence+= "pid="+pid+" queryRows="+rows.size()+" uniqueMatches="+count+";";
        if(count!=1)throw new IOException("E5_N2_UNIQUE_ACTUAL_EXIT_RECORD_REQUIRED");
        boolean absent=false;try{Os.lstat("/proc/"+pid);}catch(ErrnoException e){if(e.errno==OsConstants.ENOENT)absent=true;else throw new IOException("E5_N2_PROC_UNAVAILABLE",e);}
        if(!absent)throw new IOException("E5_N2_PID_VISIBLE_OR_REUSED");
        E5N2Recovery.Death proof=new E5N2Recovery.Death(pid,found.getRealUid(),found.getProcessName(),found.getTimestamp(),found.getReason(),found.getStatus(),true);
        evidence+=proof.record()+";";if(evidence.length()>2048)evidence=evidence.substring(0,2048);return proof;
    }
    public void lock(Path p,E4Owned<E4FencedTask.LeaseGuard> h)throws Exception {AndroidLease.exclusiveInto(p,h);}
    public E5AOwner recoveryOwner()throws Exception {return new E5AOwner(java.util.UUID.randomUUID().toString(),Process.myPid(),Process.myUid(),android.app.Application.getProcessName(),System.currentTimeMillis());}
    public void requireRecoveryWriterDead(E5AOwner owner)throws Exception {
        if(Process.myUid()!=E5N2Recovery.UID || !android.app.Application.getProcessName().equals("com.videokit.app") || !context.getPackageName().equals("com.videokit.app") || owner.pid==Process.myPid() || E4Session.retainedSessions()!=0 || E4Session.reservedEncoderSlots()!=0)throw new IOException("E5A_OBSERVER_REQUIRES_DISTINCT_IDLE_ORIGINAL_APP");
        List<ApplicationExitInfo> rows=context.getSystemService(ActivityManager.class).getHistoricalProcessExitReasons(context.getPackageName(),owner.pid,8);ApplicationExitInfo match=null;int n=0;
        for(ApplicationExitInfo r:rows)if(r.getPid()==owner.pid && r.getRealUid()==owner.uid && owner.process.equals(r.getProcessName()) && r.getTimestamp()>=owner.began && r.getTimestamp()<=System.currentTimeMillis()){match=r;n++;}
        if(n!=1 || match.getReason()<=0)throw new IOException("E5A_RECOVERY_WRITER_DEATH_UNPROVEN");
        try{Os.lstat("/proc/"+owner.pid);throw new IOException("E5A_RECOVERY_WRITER_VISIBLE_OR_REUSED");}catch(ErrnoException e){if(e.errno!=OsConstants.ENOENT)throw new IOException("E5A_RECOVERY_WRITER_PROC_UNAVAILABLE",e);}
        evidence+="recoveryAttempt="+owner.attempt+" recoveryPid="+owner.pid+" uid="+owner.uid+" process="+owner.process+" ownerRecordedAt="+owner.began+" exitTimestamp="+match.getTimestamp()+" reason="+match.getReason()+" status="+match.getStatus()+" absent=true;";
        if(evidence.length()>2048)evidence=evidence.substring(0,2048);
    }
    public void sync(Path p)throws Exception {directories.sync(p);}
    public boolean returned(){return directories.returned();}
}
