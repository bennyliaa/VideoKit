package com.videokit.spike.e4;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.*;

/** Derived C14 host authority. Constructor is IO-free; register task before initialize. Never deletes output. */
public final class E4FencedTask implements AutoCloseable {
    public enum State { WRITING, ABORT_PENDING, ABORTED, READY }
    public interface DirectorySync {void sync(Path directory)throws IOException;}
    public interface LeaseGuard {void fence(String epoch)throws IOException;void close()throws IOException;default void verifyExisting()throws IOException{throw new IOException("E5B_HANDLE_IDENTITY_REQUIRED");}default E5BFileId fileId()throws IOException{throw new IOException("E5B_HANDLE_IDENTITY_REQUIRED");}}
    public interface LeasePolicy {void createNew(Path path,E5BGuard.Role role,E4Owned<LeaseGuard> registered)throws Exception;void openExisting(Path path,E5BGuard.Role role,String epoch,E5BFileId expected,E4Owned<LeaseGuard> registered)throws Exception;}
    private final Path authorizedDirectory;public final String taskId;
    private final DirectorySync sync;private final LeasePolicy policy;
    private final List<E4Owned<?>> holders=new ArrayList<>();
    private final E4Owned<LeaseGuard> owner;
    private Path directory,output,journal,lease;private State state=State.WRITING;
    private E5BFileId ownerId,leaseId;private String epoch=UUID.randomUUID().toString();private boolean initialized,granted,closed,faulted;
    private Throwable firstFailure;
    public E4FencedTask(Path directory,String id,DirectorySync sync,LeasePolicy policy)throws IOException{
        if(!id.matches("[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"))throw new IOException("OUTPUT_TASK_INVALID");
        authorizedDirectory=directory;taskId=id;this.sync=sync;this.policy=policy;
        owner=register(new E4Owned<>(directory.resolve(id+".owner"),(LeaseGuard g)->g.close()));
    }
    private <T>E4Owned<T> register(E4Owned<T> holder)throws IOException{if(holders.size()>=24)throw new IOException("E4A_TASK_HOLDER_BUDGET");holders.add(holder);return holder;}
    private Path owned(String name)throws IOException{Path p=directory.resolve(name);if(Files.isSymbolicLink(p))throw new IOException("OUTPUT_LINK_REJECTED");return p;}
    public void initialize()throws Exception{
        if(initialized || faulted)throw new IOException("E4A_INITIALIZE_ONCE");
        try{
            Files.createDirectories(authorizedDirectory);directory=authorizedDirectory.toRealPath();output=owned(taskId+".mp4");journal=owned(taskId+".journal");lease=owned(taskId+".lease");
            if(Files.exists(journal) || Files.exists(output))throw new IOException("E4A_TASK_EXISTS_NO_REOPEN");
            policy.createNew(owned(taskId+".owner"),E5BGuard.Role.OWNER,owner);ownerId=owner.original().fileId();persist();initialized=true;
        }catch(Exception failure){faulted=true;firstFailure=failure;try{close();}catch(Exception cleanup){failure.addSuppressed(cleanup);}throw failure;}
    }
    private void active()throws IOException{if(closed || faulted || !initialized)throw new IOException("OUTPUT_STATE_UNKNOWN");}
    private E4Owned<LeaseGuard> lock(boolean create)throws Exception{
        owner.original().verifyExisting();E4Owned<LeaseGuard> holder=register(new E4Owned<>(lease,(LeaseGuard g)->g.close()));if(create)policy.createNew(lease,E5BGuard.Role.LEASE,holder);else policy.openExisting(lease,E5BGuard.Role.LEASE,epoch,leaseId,holder);return holder;
    }
    private void persist()throws Exception{
        Path temp=owned(taskId+".journal.tmp");
        E4Owned<FileOutputStream> holder=register(new E4Owned<>(temp,FileOutputStream::close));
        holder.allocate(()->new FileOutputStream(temp.toFile()));
        try{holder.initialize(raw->{DataOutputStream out=new DataOutputStream(raw);out.writeInt(0x45344131);out.writeUTF(taskId);out.writeInt(state.ordinal());out.writeUTF(epoch);out.writeBoolean(granted);out.flush();raw.getFD().sync();});holder.close();}
        catch(Exception failure){faulted=true;firstFailure=failure;throw failure;}
        try{Files.move(temp,journal,StandardCopyOption.ATOMIC_MOVE,StandardCopyOption.REPLACE_EXISTING);sync.sync(directory);}
        catch(Exception failure){faulted=true;firstFailure=failure;throw failure;}
    }
    public String issue()throws Exception{
        active();if(granted || state!=State.WRITING)throw new IOException("OUTPUT_GRANT_REJECTED");E4Owned<LeaseGuard> lock=lock(true);
        try{
            epoch=UUID.randomUUID().toString();lock.original().fence(epoch);leaseId=lock.original().fileId();
            E4Owned<FileOutputStream> file=register(new E4Owned<>(output,FileOutputStream::close));file.allocate(()->new FileOutputStream(output.toFile()));
            try{file.original().getFD().sync();}finally{file.close();}
            granted=true;persist();return epoch;
        }finally{lock.close();}
    }
    public String ready(String expected,boolean validated)throws Exception{
        active();if(!granted || state!=State.WRITING || !epoch.equals(expected) || !validated || Files.size(output)==0)throw new IOException("OUTPUT_NOT_READY");
        E4Owned<LeaseGuard> lock=lock(false);try{state=State.READY;persist();return "opaque-output-"+taskId;}finally{lock.close();}
    }
    public State abortRetaining()throws Exception{
        active();if(state==State.READY || state==State.ABORTED)return state;
        E4Owned<LeaseGuard> lock=lock(false);
        try{state=State.ABORT_PENDING;persist();epoch=UUID.randomUUID().toString();lock.original().fence(epoch);state=State.ABORTED;persist();return state;}finally{lock.close();}
    }
    public boolean workerLeaseClear()throws Exception{
        active();E4Owned<LeaseGuard> lock=null;
        try{lock=lock(false);lock.original().verifyExisting();return true;}catch(IOException busy){if("OUTPUT_WORKER_ACTIVE".equals(busy.getMessage()))return false;throw busy;}
        finally{if(lock!=null)lock.close();}
    }
    public Path authorizedOutput(){return output;}public Path authorizedLease(){return lease;}
    public State state(){return state;}
    public List<E4Owned<?>> originalHolders(){return Collections.unmodifiableList(holders);}
    public Throwable firstFailure(){return firstFailure;}
    public boolean allReturned(){for(E4Owned<?> h:holders)if(!h.returned())return false;return closed;}
    public void close()throws Exception{
        if(closed)return;
        // Failed initializer already attempted its close. UNKNOWN/CLOSING must never be retried.
        if(!owner.returned())owner.close();
        for(E4Owned<?> holder:holders)if(!holder.returned())throw new IOException("E4A_TASK_ORIGINAL_OWNER_PENDING");
        closed=true;
    }
}
