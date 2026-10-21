package com.videokit.spike.e4;

import java.io.IOException;
import java.nio.file.Path;
import java.util.*;

/** Real operation owner: retain handle before open, preserve UNKNOWN, never force a close ACK. */
public final class E9OwnedFiles {
    public enum Mode { READ,CURRENT,LEDGER,CREATE,DIRECTORY,LIST }
    public static class Handle {public final Path path;public final Mode mode;public boolean openEntered,openReturned,closeEntered,closeReturned;public Handle(Path p,Mode m){path=p;mode=m;}}
    public interface Port {
        Handle allocate(Path p,Mode mode); // Must allocate an IO-free mutable handle.
        E5BFileId pathStat(Path p)throws Exception;E5BFileId handleStat(Handle h)throws Exception;
        boolean exists(Path p)throws Exception;void directory(Path p)throws Exception;void mkdirNew(Path p)throws Exception;
        void open(Handle h)throws Exception;byte[] read(Handle h,int max)throws Exception;void write(Handle h,byte[] data)throws Exception;
        void force(Handle h)throws Exception;void close(Handle h)throws Exception;java.util.List<String> entries(Handle h,int max)throws Exception;
        void existingGuard(Path p,E5BGuard.Role role,String fence,E5BFileId expected,E4Owned<E4FencedTask.LeaseGuard> holder)throws Exception;
    }
    public final Path root;private final Port port;private final List<E4Owned<?>> owners=new ArrayList<>();
    private final List<E4Owned<E4FencedTask.LeaseGuard>> guards=new ArrayList<>();private boolean closing;
    public E9OwnedFiles(Path root,Port port){this.root=root.toAbsolutePath().normalize();this.port=Objects.requireNonNull(port);}
    public Path path(String relative)throws IOException{if(relative==null||!relative.matches("[a-zA-Z0-9_./-]{1,160}")||relative.contains("..")||relative.startsWith("/"))throw new IOException("E9_FIXED_PATH");Path p=root.resolve(relative).normalize();if(!p.startsWith(root))throw new IOException("E9_FIXED_PATH");return p;}
    public synchronized <T>E4Owned<T> register(Object parameters,E4Owned.Action<T> closer)throws IOException{if(closing||owners.size()>=48)throw new IOException("E9_HOLDER_BOUND_OR_CLOSING");E4Owned<T> h=new E4Owned<>(parameters,closer);owners.add(h);return h;}
    public synchronized int registered(){return owners.size();}
    public synchronized boolean returned(){for(E4Owned<?> h:owners)if(!h.returned())return false;return true;}
    public synchronized int unknown(){int n=0;for(E4Owned<?> h:owners)if(!h.returned())n++;return n;}
    public boolean exists(String rel)throws Exception{return port.exists(path(rel));}
    public void directory(String rel)throws Exception{port.directory(path(rel));}
    public void mkdirNew(String rel)throws Exception{port.mkdirNew(path(rel));}
    public E4Owned<Handle> open(String rel,Mode mode,int max)throws Exception{
        Path p=path(rel);E5BFileId before=mode==Mode.CREATE?null:port.pathStat(p);
        if(before!=null){if((mode==Mode.DIRECTORY||mode==Mode.LIST)){if(before.kind!=E5BFileId.DIRECTORY||before.uid!=10221)throw new IOException("E9_DIRECTORY_ROLE");}else{if(before.kind!=E5BFileId.REGULAR||before.uid!=10221||before.size<0||before.size>max)throw new IOException("E9_FILE_ROLE_OR_BOUND");}}
        E4Owned<Handle> h=register(p,value->{value.closeEntered=true;port.close(value);if(!value.openReturned)throw new IOException("E9_OPEN_OUTCOME_UNKNOWN");value.closeReturned=true;});
        h.allocate(()->port.allocate(p,mode));
        h.initialize(value->{value.openEntered=true;port.open(value);value.openReturned=true;E5BFileId actual=port.handleStat(value);if((mode==Mode.DIRECTORY||mode==Mode.LIST)){if(actual.kind!=E5BFileId.DIRECTORY||actual.uid!=10221)throw new IOException("E9_DIRECTORY_ROLE");}else if(actual.kind!=E5BFileId.REGULAR||actual.uid!=10221||actual.size>max)throw new IOException("E9_FILE_ROLE_OR_BOUND");if(before!=null&&(!actual.same(before)||actual.size!=before.size))throw new IOException("E9_HANDLE_REPLACED");if(!actual.same(port.pathStat(p)))throw new IOException("E9_PATH_REPLACED");});
        return h;
    }
    public byte[] read(E4Owned<Handle> holder,int max)throws Exception{byte[] b=port.read(holder.original(),max);if(b==null||b.length>max)throw new IOException("E9_READ_BOUND");return b;}
    public byte[] read(String rel,int max,boolean force)throws Exception{
        E4Owned<Handle> h=open(rel,force?Mode.CURRENT:Mode.READ,max);Throwable first=null;try{byte[] b=read(h,max);if(force){port.force(h.original());if(!Arrays.equals(b,read(h,max)))throw new IOException("E9_FORCE_READBACK");}if(!port.handleStat(h.original()).same(port.pathStat(path(rel))))throw new IOException("E9_READ_PATH_RACE");return b;}catch(Exception|Error e){first=e;throw e;}finally{close(h,first);}
    }
    public void create(String rel,byte[] bytes,int max)throws Exception{
        if(bytes==null||bytes.length>max)throw new IOException("E9_WRITE_BOUND");E4Owned<Handle> h=open(rel,Mode.CREATE,max);Throwable first=null;
        try{port.write(h.original(),bytes);port.force(h.original());if(!Arrays.equals(bytes,read(h,max))||!port.handleStat(h.original()).same(port.pathStat(path(rel))))throw new IOException("E9_CREATE_READBACK");}catch(Exception|Error e){first=e;throw e;}finally{close(h,first);}
    }
    public java.util.List<String> entries(String rel,int max)throws Exception{E4Owned<Handle> h=open(rel,Mode.LIST,0);Throwable first=null;try{java.util.List<String> names=port.entries(h.original(),max);if(names.size()>max)throw new IOException("E9_DIRECTORY_ENTRY_BOUND");return names;}catch(Exception|Error e){first=e;throw e;}finally{close(h,first);}}
    public void force(E4Owned<Handle> h)throws Exception{port.force(h.original());}
    public void sync(String rel)throws Exception{E4Owned<Handle> h=open(rel,Mode.DIRECTORY,0);Throwable first=null;try{port.force(h.original());}catch(Exception|Error e){first=e;throw e;}finally{close(h,first);}}
    private static void close(E4Owned<Handle> h,Throwable first)throws Exception{try{h.close();}catch(Exception|Error e){if(first!=null)first.addSuppressed(e);else throw e;}}
    public E4Owned<E4FencedTask.LeaseGuard> guard(String rel,E5BGuard.Role role,String fence,E5BFileId expected)throws Exception{
        E4Owned<E4FencedTask.LeaseGuard> h=register(path(rel),E4FencedTask.LeaseGuard::close);guards.add(h);port.existingGuard(path(rel),role,fence,expected,h);return h;
    }
    /** Close actual metadata first, guards last. In-flight/UNKNOWN is never treated as closeable success. */
    public void closeReturnedResources()throws Exception{
        closing=true;Exception first=null;
        for(int i=owners.size()-1;i>=0;i--){E4Owned<?> h=owners.get(i);if(guards.contains(h))continue;if(h.state()==E4Owned.State.OPEN||h.state()==E4Owned.State.READY)try{h.close();}catch(Exception e){if(first==null)first=e;else first.addSuppressed(e);}}
        boolean dataReturned=true;for(E4Owned<?> h:owners)if(!guards.contains(h)&&!h.returned())dataReturned=false;
        if(dataReturned)for(int i=guards.size()-1;i>=0;i--){E4Owned<?> h=guards.get(i);if(h.state()==E4Owned.State.OPEN||h.state()==E4Owned.State.READY)try{h.close();}catch(Exception e){if(first==null)first=e;else first.addSuppressed(e);}}
        if(first!=null)throw first;if(!returned())throw new IOException("E9_ORIGINAL_OWNER_RETURN_UNPROVEN");
    }
}
