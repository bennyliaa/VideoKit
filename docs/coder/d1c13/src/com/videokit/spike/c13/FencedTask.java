package com.videokit.spike.c13;

import java.io.*;
import java.nio.ByteBuffer;
import java.nio.channels.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.UUID;

/** Host-only authorized temporary target. No input path is accepted, serialized, or derived here. */
public final class FencedTask implements AutoCloseable {
    public enum State { WRITING, ABORT_PENDING, ABORTED, READY }
    public interface DirectorySync {void sync(Path directory)throws IOException;}
    public interface LeaseGuard extends AutoCloseable {void fence(String epoch)throws IOException;void close()throws IOException;}
    public interface LeasePolicy {LeaseGuard exclusive(Path leaseFile)throws IOException;}
    private final Path directory,output,journal,lease;
    private final String taskId;
    private final DirectorySync directorySync;
    private final LeasePolicy leasePolicy;
    private final LeaseGuard ownerGuard;
    private State state;private String epoch;private boolean granted,closed,faulted;

    public FencedTask(Path explicitlyAuthorizedDirectory,String taskId,DirectorySync directorySync)throws IOException {
        this(explicitlyAuthorizedDirectory,taskId,directorySync,desktopLeasePolicy());
    }
    private static LeasePolicy desktopLeasePolicy()throws IOException {
        if("Dalvik".equals(System.getProperty("java.vm.name")))throw new IOException("ANDROID_LEASE_POLICY_REQUIRED");
        return path->{RandomAccessFile file=new RandomAccessFile(path.toFile(),"rw");FileLock held;
            try{held=file.getChannel().tryLock();if(held==null)throw new IOException("OUTPUT_WORKER_ACTIVE");}
            catch(OverlappingFileLockException e){file.close();throw new IOException("OUTPUT_WORKER_ACTIVE");}
            catch(IOException e){file.close();throw e;}
            return new LeaseGuard(){public void fence(String epoch)throws IOException{file.setLength(0);file.write(epoch.getBytes(StandardCharsets.US_ASCII));file.getFD().sync();}public void close()throws IOException{try{held.release();}finally{file.close();}}};
        };
    }
    public FencedTask(Path explicitlyAuthorizedDirectory,String taskId,DirectorySync directorySync,LeasePolicy leasePolicy)throws IOException {
        if(!taskId.matches("[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"))throw new IOException("OUTPUT_TASK_INVALID");
        this.taskId=taskId;this.directorySync=directorySync;this.leasePolicy=leasePolicy;
        Files.createDirectories(explicitlyAuthorizedDirectory);directory=explicitlyAuthorizedDirectory.toRealPath();
        output=owned(taskId+".mp4");journal=owned(taskId+".journal");lease=owned(taskId+".lease");
        Path owner=owned(taskId+".owner");
        try{ownerGuard=leasePolicy.exclusive(owner);}catch(IOException e){if("OUTPUT_WORKER_ACTIVE".equals(e.getMessage()))throw new IOException("OUTPUT_OWNER_BUSY");throw e;}
        try {
            if(Files.exists(journal)){load();try(RandomAccessFile record=new RandomAccessFile(journal.toFile(),"rw")){record.getFD().sync();}directorySync.sync(directory);}else {state=State.WRITING;epoch=UUID.randomUUID().toString();persist();}
        }catch(IOException e){close();throw e;}
    }
    private Path owned(String name)throws IOException {
        Path p=directory.resolve(name);if(Files.isSymbolicLink(p))throw new IOException("OUTPUT_LINK_REJECTED");return p;
    }
    private void active()throws IOException {if(closed)throw new IOException("OUTPUT_OWNER_RELEASED");if(faulted)throw new IOException("OUTPUT_STATE_UNKNOWN");}
    private void load()throws IOException {
        try(DataInputStream in=new DataInputStream(Files.newInputStream(journal))) {
            if(in.readInt()!=0x564b4433 || !taskId.equals(in.readUTF()))throw new IOException("OUTPUT_TASK_MISMATCH");
            int ordinal=in.readInt();if(ordinal<0 || ordinal>=State.values().length)throw new IOException("OUTPUT_JOURNAL_INVALID");
            state=State.values()[ordinal];epoch=in.readUTF();granted=in.readBoolean();
            if(!epoch.matches("[0-9a-f-]{36}"))throw new IOException("OUTPUT_JOURNAL_INVALID");
        }
    }
    private void persist()throws IOException {
        try{persistRecord();}catch(IOException e){faulted=true;throw e;}
    }
    private void persistRecord()throws IOException {
        Path temporary=owned(taskId+".journal.tmp");
        try(FileOutputStream raw=new FileOutputStream(temporary.toFile());DataOutputStream data=new DataOutputStream(raw)) {
            data.writeInt(0x564b4433);data.writeUTF(taskId);data.writeInt(state.ordinal());data.writeUTF(epoch);data.writeBoolean(granted);data.flush();raw.getFD().sync();
        }
        try{Files.move(temporary,journal,StandardCopyOption.ATOMIC_MOVE,StandardCopyOption.REPLACE_EXISTING);directorySync.sync(directory);}
        catch(IOException e){throw new IOException("OUTPUT_JOURNAL_DURABILITY_UNKNOWN",e);}
    }
    /** One grant per task; fence is durable before any descriptor leaves the host. */
    public synchronized String issue()throws IOException {
        active();if(state!=State.WRITING || granted)throw new IOException("OUTPUT_GRANT_REJECTED");
        try(LeaseGuard lock=leasePolicy.exclusive(lease)) {
            epoch=UUID.randomUUID().toString();lock.fence(epoch);
            try(FileOutputStream create=new FileOutputStream(output.toFile())){create.getFD().sync();}
            granted=true;persist();return epoch;
        }
    }
    public synchronized State query()throws IOException {active();return state;}
    public synchronized String token()throws IOException {active();return state==State.READY?"opaque-output-"+taskId:null;}
    public synchronized String epoch()throws IOException {active();return epoch;}
    /** Only authenticated worker completion can supply validation. Lock proves it has relinquished writers. */
    public synchronized String ready(String expectedEpoch,boolean workerValidated)throws IOException {
        active();if(state==State.READY)return token();
        if(state!=State.WRITING || !granted || !epoch.equals(expectedEpoch) || !workerValidated || Files.size(output)==0)throw new IOException("OUTPUT_NOT_READY");
        try(LeaseGuard lock=leasePolicy.exclusive(lease)) {
            state=State.READY;persist();return token();
        }
    }
    /** Abort may be pending while a worker retains a writer; never delete on timeout alone. */
    public synchronized State abort()throws IOException {
        active();if(state==State.READY || state==State.ABORTED)return state;
        if(state!=State.ABORT_PENDING){state=State.ABORT_PENDING;persist();}
        try(LeaseGuard lock=leasePolicy.exclusive(lease)) {
            epoch=UUID.randomUUID().toString();lock.fence(epoch); // Invalidates late START messages, including those not yet acknowledged.
            Files.deleteIfExists(output);directorySync.sync(directory);state=State.ABORTED;persist();return state;
        }
    }
    public synchronized boolean workerLeaseClear()throws IOException {
        active();try(LeaseGuard lock=leasePolicy.exclusive(lease)){return true;}
        catch(IOException e){if("OUTPUT_WORKER_ACTIVE".equals(e.getMessage()))return false;throw e;}
    }
    // These capabilities are host-adapter internals, never public SDK source metadata or binder strings.
    public Path authorizedOutput(){return output;}public Path authorizedLease(){return lease;}
    @Override public synchronized void close()throws IOException {if(!closed){closed=true;ownerGuard.close();}}

    public static final class WorkerLease implements AutoCloseable {
        private final FileLock lock;
        private WorkerLease(FileLock lock){this.lock=lock;}
        /** The worker gets a read-only lease FD and holds a shared lock until ALL output FDs are closed. */
        public static WorkerLease acquire(FileChannel channel,String expectedEpoch)throws IOException {
            FileLock held;
            try{held=channel.tryLock(0,Long.MAX_VALUE,true);if(held==null)throw new IOException("OUTPUT_LEASE_BUSY");}
            catch(OverlappingFileLockException e){throw new IOException("OUTPUT_LEASE_BUSY");}
            try {
                verifyEpoch(channel,expectedEpoch);return new WorkerLease(held);
            }catch(IOException e){held.release();throw e;}
        }
        @Override public void close()throws IOException {lock.release();}
    }
    public static void verifyEpoch(FileChannel channel,String expectedEpoch)throws IOException {
        long size=channel.size();if(size<1 || size>128)throw new IOException("OUTPUT_FENCE_INVALID");
        ByteBuffer data=ByteBuffer.allocate((int)size);while(data.hasRemaining())if(channel.read(data,data.position())<=0)throw new IOException("OUTPUT_FENCE_INVALID");
        if(!expectedEpoch.equals(new String(data.array(),StandardCharsets.US_ASCII)))throw new IOException("OUTPUT_FENCED");
    }
}
