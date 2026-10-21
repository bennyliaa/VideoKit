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
public final class E5N2RecoveryAndroid implements E5N2Recovery.Platform {
    private final Context context;private final List<E4Owned<Dir>> dirs=new ArrayList<>();private String evidence="";
    public String evidence(){return evidence;}
    public E5N2RecoveryAndroid(Context c){context=c.getApplicationContext();}
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
    public void sync(Path p)throws Exception {
        if(dirs.size()>=16)throw new IOException("E5_N2_DIRECTORY_SYNC_BOUND");
        E4Owned<Dir> h=new E4Owned<>(p,Dir::close);dirs.add(h);h.allocate(Dir::new);
        h.initialize(d->{d.fd=Os.open(p.toString(),OsConstants.O_RDONLY|OsConstants.O_NOFOLLOW,0);if(!OsConstants.S_ISDIR(Os.fstat(d.fd).st_mode))throw new IOException("E5_N2_DIRECTORY_ROLE");Os.fsync(d.fd);});h.close();
    }
    public boolean returned(){for(E4Owned<Dir> h:dirs)if(!h.returned())return false;return true;}
    private static final class Dir {FileDescriptor fd;void close()throws Exception{if(fd!=null)Os.close(fd);}}
}
