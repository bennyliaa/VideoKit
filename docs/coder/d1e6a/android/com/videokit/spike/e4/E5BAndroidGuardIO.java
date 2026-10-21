package com.videokit.spike.e4;

import android.os.ParcelFileDescriptor;
import android.system.*;
import com.videokit.spike.c14.AndroidLease;
import java.io.*;
import java.nio.file.Path;
import java.util.Arrays;

/** Existing opens have no O_CREAT/O_TRUNC. Each raw FD and dup is stored before further platform calls. */
public final class E5BAndroidGuardIO implements E5BGuard.IO<E5BAndroidGuardIO.Descriptor> {
    public static final class Descriptor {FileDescriptor raw;ParcelFileDescriptor duplicate;boolean rawCloseAttempted,duplicateCloseAttempted;}
    public Descriptor allocate(){return new Descriptor();}
    private static E5BFileId id(StructStat s){int kind=OsConstants.S_ISREG(s.st_mode)?E5BFileId.REGULAR:OsConstants.S_ISLNK(s.st_mode)?E5BFileId.LINK:OsConstants.S_ISDIR(s.st_mode)?E5BFileId.DIRECTORY:E5BFileId.OTHER;return new E5BFileId(s.st_dev,s.st_ino,s.st_size,s.st_uid,kind);}
    public E5BFileId pathStatNoFollow(Path p)throws Exception{return id(Os.lstat(p.toString()));}
    public void openExistingNoFollow(Path p,Descriptor d)throws Exception{
        d.raw=Os.open(p.toString(),OsConstants.O_RDWR|OsConstants.O_NOFOLLOW|OsConstants.O_CLOEXEC|OsConstants.O_NONBLOCK,0);
        duplicate(d);
    }
    public void createNewNoFollow(Path p,Descriptor d)throws Exception{
        d.raw=Os.open(p.toString(),OsConstants.O_RDWR|OsConstants.O_CREAT|OsConstants.O_EXCL|OsConstants.O_NOFOLLOW|OsConstants.O_CLOEXEC|OsConstants.O_NONBLOCK,0600);
        duplicate(d);
    }
    private static void duplicate(Descriptor d)throws Exception {d.duplicate=ParcelFileDescriptor.dup(d.raw);int flags=Os.fcntlInt(d.duplicate.getFileDescriptor(),OsConstants.F_GETFD,0);Os.fcntlInt(d.duplicate.getFileDescriptor(),OsConstants.F_SETFD,flags|OsConstants.FD_CLOEXEC);}
    public E5BFileId handleStat(Descriptor d)throws Exception{return id(Os.fstat(d.raw));}
    public byte[] readLease(Descriptor d)throws Exception {
        byte[] b=new byte[37];int at=0;while(at<b.length){int n=Os.pread(d.raw,b,at,b.length-at,at);if(n<=0)break;at+=n;}return Arrays.copyOf(b,at);
    }
    public void lock(Descriptor d)throws Exception {AndroidLease.lockRegisteredDescriptor(d.duplicate);}
    public void unlock(Descriptor d)throws Exception {AndroidLease.unlockRegisteredDescriptor(d.duplicate);}
    public void fence(Descriptor d,byte[] b)throws Exception{Os.ftruncate(d.raw,0);int at=0;while(at<b.length){int n=Os.pwrite(d.raw,b,at,b.length-at,at);if(n<=0)throw new IOException("E5B_GUARD_FENCE_WRITE");at+=n;}Os.fsync(d.raw);}
    public void close(Descriptor d)throws Exception {
        Exception first=null;
        if(d.duplicate!=null && !d.duplicateCloseAttempted){d.duplicateCloseAttempted=true;try{d.duplicate.close();}catch(Exception e){first=e;}}
        if(d.raw!=null && !d.rawCloseAttempted){d.rawCloseAttempted=true;try{Os.close(d.raw);}catch(Exception e){if(first==null)first=e;else first.addSuppressed(e);}}
        if(first!=null)throw first;
    }
}
