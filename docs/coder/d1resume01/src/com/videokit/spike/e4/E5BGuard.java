package com.videokit.spike.e4;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.Path;
import java.util.UUID;

/** Shared actual-handle verification. Existing and new creation have separate operations and entry points. */
public final class E5BGuard<D> implements E4FencedTask.LeaseGuard {
    public enum Role {OWNER,LEASE}
    public interface IO<D> {
        D allocate();E5BFileId pathStatNoFollow(Path p)throws Exception;
        void openExistingNoFollow(Path p,D holder)throws Exception;void createNewNoFollow(Path p,D holder)throws Exception;
        E5BFileId handleStat(D holder)throws Exception;byte[] readLease(D holder)throws Exception;
        void lock(D holder)throws Exception;void unlock(D holder)throws Exception;void close(D holder)throws Exception;
        void fence(D holder,byte[] bytes)throws Exception;
    }
    private final Path path;private final Role role;private final int uid;private final IO<D> io;private final D descriptor;
    private E5BFileId pinned;private String epoch;private boolean locked,closeAttempted,closed,creating;
    private E5BGuard(Path p,Role r,int u,IO<D> ops){path=p;role=r;uid=u;io=ops;descriptor=ops.allocate();}
    public static <D>void existing(Path p,Role role,String epoch,E5BFileId expected,int uid,IO<D> io,E4Owned<E4FencedTask.LeaseGuard> holder)throws Exception {
        if(role==Role.LEASE && (epoch==null || !UUID.fromString(epoch).toString().equals(epoch)))throw new IOException("E5B_EXISTING_FENCE_REQUIRED");E5BGuard<D> g=new E5BGuard<>(p,role,uid,io);g.epoch=epoch;holder.allocate(()->g);
        holder.initialize(ignored->{E5BFileId before=io.pathStatNoFollow(p);g.checkRole(before);io.openExistingNoFollow(p,g.descriptor);E5BFileId actual=io.handleStat(g.descriptor);g.checkRole(actual);if(!actual.same(before) || expected!=null && !actual.same(expected))throw new IOException("E5B_EXISTING_GUARD_IDENTITY_CHANGED");g.pinned=actual;g.verifyExisting();io.lock(g.descriptor);g.locked=true;g.verifyExisting();});
    }
    public static <D>void createNew(Path p,Role role,int uid,IO<D> io,E4Owned<E4FencedTask.LeaseGuard> holder)throws Exception {
        E5BGuard<D> g=new E5BGuard<>(p,role,uid,io);g.creating=true;holder.allocate(()->g);
        holder.initialize(ignored->{io.createNewNoFollow(p,g.descriptor);g.pinned=io.handleStat(g.descriptor);g.verifyExisting();io.lock(g.descriptor);g.locked=true;g.verifyExisting();});
    }
    private void checkRole(E5BFileId id)throws IOException{id.role(role==Role.OWNER || creating && epoch==null?0:36,uid);}
    public E5BFileId fileId()throws IOException{verifyExisting();return pinned;}
    public void verifyExisting()throws IOException {
        if(closed || pinned==null)throw new IOException("E5B_GUARD_NOT_OPEN");
        try{E5BFileId actual=io.handleStat(descriptor),current=io.pathStatNoFollow(path);checkRole(actual);checkRole(current);if(!actual.same(pinned) || !current.same(pinned))throw new IOException("E5B_EXISTING_GUARD_IDENTITY_CHANGED");
            if(role==Role.LEASE && epoch!=null && !epoch.equals(new String(io.readLease(descriptor),StandardCharsets.US_ASCII)))throw new IOException("E5B_EXISTING_GUARD_FENCE_MISMATCH");
        }catch(IOException e){throw e;}catch(Exception e){throw new IOException("E5B_GUARD_HANDLE_VERIFY",e);}
    }
    public void fence(String next)throws IOException {
        if(role!=Role.LEASE || !locked || !UUID.fromString(next).toString().equals(next))throw new IOException("E5B_GUARD_FENCE_REJECTED");verifyExisting();
        try{io.fence(descriptor,next.getBytes(StandardCharsets.US_ASCII));epoch=next;creating=false;verifyExisting();}catch(IOException e){throw e;}catch(Exception e){throw new IOException("E5B_GUARD_FENCE_WRITE",e);}
    }
    public void close()throws IOException {
        if(closed)return;if(closeAttempted)throw new IOException("E5B_ORIGINAL_GUARD_CLOSE_UNKNOWN");closeAttempted=true;Exception first=null;
        if(pinned!=null && locked)try{verifyExisting();}catch(Exception e){first=e;}
        if(locked)try{io.unlock(descriptor);locked=false;}catch(Exception e){if(first==null)first=e;else first.addSuppressed(e);}
        try{io.close(descriptor);closed=true;}catch(Exception e){if(first==null)first=e;else first.addSuppressed(e);}
        if(first!=null)throw new IOException("E5B_GUARD_CLOSE_OR_IDENTITY_UNPROVEN",first);
    }
    public static final class Policy<D> implements E4FencedTask.LeasePolicy {
        private final int uid;private final IO<D> io;
        public Policy(int uid,IO<D> io){this.uid=uid;this.io=io;}
        public void createNew(Path p,Role r,E4Owned<E4FencedTask.LeaseGuard> h)throws Exception{E5BGuard.createNew(p,r,uid,io,h);}
        public void openExisting(Path p,Role r,String epoch,E5BFileId id,E4Owned<E4FencedTask.LeaseGuard> h)throws Exception{E5BGuard.existing(p,r,epoch,id,uid,io,h);}
    }
}
