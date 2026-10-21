package com.videokit.spike.e4;
import java.io.*;
import java.nio.ByteBuffer;
import java.nio.channels.FileChannel;
import java.nio.file.*;
import java.util.*;

/** One original host file, not approval/return proof. Its path is pinned INSIDE deployment config. */
public final class E11DeploymentOnce {
    public interface Cut {void at(String stage)throws Exception;}
    private static final class IO {FileChannel channel;boolean knownNoOpen;}
    private final Path path;private final Cut cut;private final E4Owned<IO> owner;private volatile boolean attempted;
    private enum Role { E11, E13A, E13E }
    public static E11DeploymentOnce e13Lifecycle(Path path,E9PcSupervisor supervisor)throws Exception{return new E11DeploymentOnce(path,supervisor,s->{},Role.E13E);}
    private final Role role;
    /** Exact new role, selected only by the E13 entry; never a caller-provided basename. */
    public static E11DeploymentOnce e13Activation(Path path,E9PcSupervisor supervisor)throws Exception{return e13Activation(path,supervisor,s->{});}
    static E11DeploymentOnce e13Activation(Path path,E9PcSupervisor supervisor,Cut cut)throws Exception{return new E11DeploymentOnce(path,supervisor,cut,Role.E13A);}
    public E11DeploymentOnce(Path path,E9PcSupervisor supervisor)throws Exception{this(path,supervisor,s->{});}
    public E11DeploymentOnce(Path path,E9PcSupervisor supervisor,Cut cut)throws Exception{
        this(path,supervisor,cut,Role.E11);
    }
    private E11DeploymentOnce(Path path,E9PcSupervisor supervisor,Cut cut,Role role)throws Exception{
        this.path=path.toAbsolutePath().normalize();this.cut=cut;this.role=role;
        owner=new E4Owned<>(this.path,io->{cut.at("CLOSE_BEFORE");if(io.channel!=null)io.channel.close();else if(!io.knownNoOpen)throw new IOException("E11_ONCE_OPEN_OUTCOME_UNKNOWN");cut.at("CLOSE_AFTER");});
        supervisor.retainAuthority(this,null,this::returned); // Strong authority BEFORE any open/allocation.
    }
    public boolean returned(){return !attempted||owner.returned();}public String state(){return owner.state().name();}
    public void record(byte[] exactIntent)throws Exception{
        if(attempted)throw new IOException("E11_ONCE_OBJECT_REENTRY");if(exactIntent==null||exactIntent.length<1||exactIntent.length>4096)throw new IOException("E11_ONCE_RECORD_BOUND");E9Record.parse(exactIntent,4096);
        String basename=role==Role.E11?"activation-deployment.once":role==Role.E13A?"e13a-activation-deployment.once":"e13e-lifecycle-deployment.once";
        if(!path.getFileName().toString().equals(basename))throw new IOException("E11_ONCE_FIXED_ROLE");
        if(role==Role.E13A&&!E9Record.parse(exactIntent,4096).get("kind").equals("e13ActivationDispatchIntent"))throw new IOException("E13_ONCE_INTENT_ROLE");
        if(role==Role.E13E&&!E9Record.parse(exactIntent,4096).get("kind").equals("e13LifecycleDispatchIntent"))throw new IOException("E13E_ONCE_INTENT_ROLE");
        Path parent=path.getParent();if(parent==null||!Files.isDirectory(parent,LinkOption.NOFOLLOW_LINKS))throw new IOException("E11_ONCE_EXISTING_PARENT_REQUIRED");
        for(Path p=path;p!=null;p=p.getParent())if(Files.isSymbolicLink(p))throw new IOException("E11_ONCE_NO_SYMLINK");
        if(Files.exists(path,LinkOption.NOFOLLOW_LINKS))throw new IOException("E11_DEPLOYMENT_ALREADY_RESERVED_NO_RETRY");
        attempted=true;owner.allocate(IO::new);Throwable first=null;
        try{
            owner.initialize(io->{try{io.channel=FileChannel.open(path,StandardOpenOption.CREATE_NEW,StandardOpenOption.READ,StandardOpenOption.WRITE,LinkOption.NOFOLLOW_LINKS);}catch(FileAlreadyExistsException knownRace){io.knownNoOpen=true;throw knownRace;}});
            cut.at("WRITE");ByteBuffer data=ByteBuffer.wrap(exactIntent);while(data.hasRemaining())if(owner.original().channel.write(data)<=0)throw new IOException("E11_ONCE_WRITE_PROGRESS");
            cut.at("FORCE");owner.original().channel.force(true);owner.original().channel.position(0);ByteBuffer check=ByteBuffer.allocate(exactIntent.length);while(check.hasRemaining())if(owner.original().channel.read(check)<=0)throw new EOFException("E11_ONCE_READBACK");if(owner.original().channel.size()!=exactIntent.length||!Arrays.equals(check.array(),exactIntent))throw new IOException("E11_ONCE_READBACK");
        }catch(Exception|Error failure){first=failure;throw failure;}
        finally{if(owner.state()==E4Owned.State.OPEN||owner.state()==E4Owned.State.READY||owner.state()==E4Owned.State.INITIALIZING)try{owner.close();}catch(Exception|Error close){if(first!=null)first.addSuppressed(close);else throw close;}}
        if(!returned())throw new IOException("E11_ONCE_ORIGINAL_RETURN_REQUIRED");
    }
}
