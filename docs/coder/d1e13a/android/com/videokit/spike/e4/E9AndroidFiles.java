package com.videokit.spike.e4;

import android.os.ParcelFileDescriptor;
import android.system.*;
import java.io.*;
import java.nio.channels.*;
import java.nio.file.*;
import java.util.*;

/** Actual Android original-handle IO. Ledger uses the original FileChannel exclusive-lock primitive. */
public final class E9AndroidFiles implements E9CurrentObservation.Platform {
    private static final class NativeHandle extends E9OwnedFiles.Handle {
        FileDescriptor raw;ParcelFileDescriptor duplicate;ParcelFileDescriptor.AutoCloseOutputStream output;FileLock lock;DirectoryStream<Path> entries;
        boolean duplicateEntered,duplicateReturned,streamEntered,streamReturned,rawCloseAttempted,duplicateCloseAttempted,streamCloseAttempted,unlockAttempted;
        NativeHandle(Path p,E9OwnedFiles.Mode m){super(p,m);}
    }
    public void requireIdleOriginalHost()throws Exception{if(android.os.Process.myUid()!=10221||!"com.videokit.app".equals(android.app.Application.getProcessName())||E4Session.retainedSessions()!=0||E4Session.reservedEncoderSlots()!=0||E9MigrationInstrumentationState.hasUnreturned())throw new IOException("E9_REQUIRES_IDLE_ORIGINAL_APP");}
    public E9OwnedFiles.Handle allocate(Path p,E9OwnedFiles.Mode mode){return new NativeHandle(p,mode);}
    private E5BFileId id(StructStat s){int kind=OsConstants.S_ISREG(s.st_mode)?E5BFileId.REGULAR:OsConstants.S_ISDIR(s.st_mode)?E5BFileId.DIRECTORY:OsConstants.S_ISLNK(s.st_mode)?E5BFileId.LINK:E5BFileId.OTHER;return new E5BFileId(s.st_dev,s.st_ino,s.st_size,s.st_uid,kind);}
    public E5BFileId pathStat(Path p)throws Exception{return id(Os.lstat(p.toString()));}
    public E5BFileId handleStat(E9OwnedFiles.Handle handle)throws Exception{return id(Os.fstat(((NativeHandle)handle).raw));}
    public boolean exists(Path p)throws Exception{try{Os.lstat(p.toString());return true;}catch(ErrnoException e){if(e.errno==OsConstants.ENOENT)return false;throw e;}}
    public void directory(Path p)throws Exception{E5BFileId i=pathStat(p);if(i.kind!=E5BFileId.DIRECTORY||i.uid!=10221)throw new IOException("E9_DIRECTORY_IDENTITY");}
    public void mkdirNew(Path p)throws Exception{Os.mkdir(p.toString(),0700);directory(p);}
    public void open(E9OwnedFiles.Handle handle)throws Exception{
        NativeHandle h=(NativeHandle)handle;boolean dir=h.mode==E9OwnedFiles.Mode.DIRECTORY||h.mode==E9OwnedFiles.Mode.LIST;
        int flags=(dir||h.mode==E9OwnedFiles.Mode.READ?OsConstants.O_RDONLY:OsConstants.O_RDWR)|OsConstants.O_NOFOLLOW|OsConstants.O_NONBLOCK|OsConstants.O_CLOEXEC;
        // Public SDK has no O_DIRECTORY. The original fstat/path checks enforce directory role.
        if(h.mode==E9OwnedFiles.Mode.CREATE)flags|=OsConstants.O_CREAT|OsConstants.O_EXCL;
        h.raw=Os.open(h.path.toString(),flags,0600);h.openReturned=true;
        if(h.mode==E9OwnedFiles.Mode.LEDGER||h.mode==E9OwnedFiles.Mode.LIST){
            h.duplicateEntered=true;h.duplicate=ParcelFileDescriptor.dup(h.raw);h.duplicateReturned=true;
            if(!id(Os.fstat(h.raw)).same(id(Os.fstat(h.duplicate.getFileDescriptor()))))throw new IOException("E9_DUP_IDENTITY");
        }
        if(h.mode==E9OwnedFiles.Mode.LEDGER){h.streamEntered=true;h.output=new ParcelFileDescriptor.AutoCloseOutputStream(h.duplicate);h.streamReturned=true;h.lock=h.output.getChannel().tryLock();if(h.lock==null)throw new IOException("E9_LEDGER_BUSY");}
        if(h.mode==E9OwnedFiles.Mode.LIST){h.streamEntered=true;h.entries=Files.newDirectoryStream(Paths.get("/proc/self/fd/"+h.duplicate.getFd()));h.streamReturned=true;}
    }
    public byte[] read(E9OwnedFiles.Handle handle,int max)throws Exception{
        NativeHandle h=(NativeHandle)handle;byte[] b=new byte[max+1];int at=0;
        while(at<b.length){int n=Os.pread(h.raw,b,at,b.length-at,at);if(n<=0)break;at+=n;}
        if(at>max)throw new IOException("E9_READ_GREW");return Arrays.copyOf(b,at);
    }
    public void write(E9OwnedFiles.Handle handle,byte[] bytes)throws Exception{NativeHandle h=(NativeHandle)handle;if(h.mode!=E9OwnedFiles.Mode.CREATE)throw new IOException("E9_ONLY_CREATE_NEW_WRITES");int at=0;while(at<bytes.length){int n=Os.pwrite(h.raw,bytes,at,bytes.length-at,at);if(n<=0)throw new IOException("E9_WRITE_PROGRESS");at+=n;}}
    public void force(E9OwnedFiles.Handle h)throws Exception{Os.fsync(((NativeHandle)h).raw);}
    public List<String> entries(E9OwnedFiles.Handle handle,int max)throws Exception{NativeHandle h=(NativeHandle)handle;if(h.entries==null)throw new IOException("E9_LIST_NOT_OPEN");List<String> result=new ArrayList<>();for(Path p:h.entries){if(result.size()>=max)throw new IOException("E9_DIRECTORY_ENTRY_BOUND");result.add(p.getFileName().toString());}return result;}
    public void close(E9OwnedFiles.Handle handle)throws Exception{
        NativeHandle h=(NativeHandle)handle;Exception first=null;
        if(h.lock!=null&&!h.unlockAttempted){h.unlockAttempted=true;try{h.lock.release();}catch(Exception e){first=e;}}
        if(h.streamEntered&&!h.streamCloseAttempted){h.streamCloseAttempted=true;try{if(!h.streamReturned)throw new IOException("E9_STREAM_ALLOCATION_UNKNOWN");if(h.entries!=null)h.entries.close();if(h.output!=null){h.duplicateCloseAttempted=true;h.output.close();}}catch(Exception e){if(first==null)first=e;else first.addSuppressed(e);}}
        if(h.duplicate!=null&&!h.duplicateCloseAttempted){h.duplicateCloseAttempted=true;try{h.duplicate.close();}catch(Exception e){if(first==null)first=e;else first.addSuppressed(e);}}
        if(h.raw!=null&&!h.rawCloseAttempted){h.rawCloseAttempted=true;try{Os.close(h.raw);}catch(Exception e){if(first==null)first=e;else first.addSuppressed(e);}}
        if(h.duplicateEntered&&!h.duplicateReturned){IOException e=new IOException("E9_DUP_ALLOCATION_UNKNOWN");if(first==null)first=e;else first.addSuppressed(e);}
        if(first!=null)throw first;
    }
    public void existingGuard(Path p,E5BGuard.Role role,String fence,E5BFileId expected,E4Owned<E4FencedTask.LeaseGuard> holder)throws Exception{E5BGuard.existing(p,role,fence,expected,10221,new E5BAndroidGuardIO(),holder);}
}
