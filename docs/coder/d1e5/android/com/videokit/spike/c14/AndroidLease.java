package com.videokit.spike.c14;

import android.os.ParcelFileDescriptor;
import java.io.*;
import java.nio.file.Path;

/** Linux flock ownership is tied to the open-file description, survives Binder/dup intermediate closes. */
public final class AndroidLease {
    static {System.loadLibrary("videokit_d1_lease");}
    private static native int tryLock(int fd,boolean exclusive);
    private static native int unlock(int fd);
    private static void acquire(ParcelFileDescriptor fd,boolean exclusive)throws IOException {
        int status=tryLock(fd.getFd(),exclusive);if(status!=0)throw new IOException(status==1?(exclusive?"OUTPUT_WORKER_ACTIVE":"OUTPUT_LEASE_BUSY"):"OUTPUT_NATIVE_LOCK_FAILED");
    }
    /** The caller registers holder before this method allocates the guard or opens its PFD. */
    public static void exclusiveInto(Path path,com.videokit.spike.e4.E4Owned<com.videokit.spike.e4.E4FencedTask.LeaseGuard> holder)throws Exception {
        final class Guard implements com.videokit.spike.e4.E4FencedTask.LeaseGuard {
            ParcelFileDescriptor fd;boolean acquireEntered;
            public void fence(String epoch)throws IOException {
                byte[] bytes=epoch.getBytes(java.nio.charset.StandardCharsets.US_ASCII);
                try{android.system.Os.ftruncate(fd.getFileDescriptor(),0);int at=0;
                    while(at<bytes.length){int n=android.system.Os.pwrite(fd.getFileDescriptor(),bytes,at,bytes.length-at,at);if(n<=0)throw new IOException("OUTPUT_FENCE_WRITE");at+=n;}
                    android.system.Os.fsync(fd.getFileDescriptor());
                }catch(android.system.ErrnoException e){throw new IOException("OUTPUT_FENCE_WRITE",e);}
            }
            public void close()throws IOException {
                IOException first=null;
                if(fd!=null){if(acquireEntered)try{if(unlock(fd.getFd())!=0)first=new IOException("OUTPUT_NATIVE_UNLOCK_FAILED");}catch(RuntimeException e){first=new IOException("OUTPUT_UNLOCK_UNKNOWN",e);}
                    try{fd.close();}catch(IOException e){if(first==null)first=e;else first.addSuppressed(e);}}
                if(first!=null)throw first;
            }
        }
        Guard guard=new Guard();holder.allocate(()->guard);
        holder.initialize(owned->{guard.fd=ParcelFileDescriptor.open(path.toFile(),ParcelFileDescriptor.MODE_CREATE|ParcelFileDescriptor.MODE_READ_WRITE);guard.acquireEntered=true;acquire(guard.fd,true);});
    }
    public static final class WorkerLease implements AutoCloseable {
        private final ParcelFileDescriptor fd;private final FileInputStream stream;private boolean closed;
        private WorkerLease(ParcelFileDescriptor fd,FileInputStream stream){this.fd=fd;this.stream=stream;}
        public static WorkerLease acquire(ParcelFileDescriptor fd,String epoch)throws IOException {
            FileInputStream stream=new ParcelFileDescriptor.AutoCloseInputStream(fd);
            try{AndroidLease.acquire(fd,false);FencedTask.verifyEpoch(stream.getChannel(),epoch);return new WorkerLease(fd,stream);}
            catch(IOException e){try{unlock(fd.getFd());}finally{stream.close();}throw e;}
        }
        @Override public void close()throws IOException {if(!closed){closed=true;int result=unlock(fd.getFd());stream.close();if(result!=0)throw new IOException("OUTPUT_NATIVE_UNLOCK_FAILED");}}
    }
}
