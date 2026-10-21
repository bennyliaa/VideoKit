package com.videokit.spike.c05;

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
    public static FencedTask.LeaseGuard exclusive(Path path)throws IOException {
        ParcelFileDescriptor fd=ParcelFileDescriptor.open(path.toFile(),ParcelFileDescriptor.MODE_CREATE|ParcelFileDescriptor.MODE_READ_WRITE);
        try{acquire(fd,true);}catch(IOException e){fd.close();throw e;}
        return new FencedTask.LeaseGuard(){
            public void fence(String epoch)throws IOException{
                try(FileOutputStream writer=new ParcelFileDescriptor.AutoCloseOutputStream(ParcelFileDescriptor.dup(fd.getFileDescriptor()))){writer.getChannel().truncate(0);writer.getChannel().position(0);writer.write(epoch.getBytes(java.nio.charset.StandardCharsets.US_ASCII));writer.getFD().sync();}
            }
            public void close()throws IOException{int result=unlock(fd.getFd());fd.close();if(result!=0)throw new IOException("OUTPUT_NATIVE_UNLOCK_FAILED");}
        };
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
