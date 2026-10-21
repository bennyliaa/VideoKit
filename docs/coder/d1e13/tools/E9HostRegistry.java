package com.videokit.spike.e4;
import java.nio.charset.StandardCharsets;
import java.nio.file.Path;

/** Common ORIGINAL registry construction and entry lifetime, before the first registry filesystem IO. */
public final class E9HostRegistry {
    public static final class Owned {public final E9Registry.Store store;public final E9Registry registry;private Owned(E9Registry.Store s,E9Registry r){store=s;registry=r;}}
    public interface Entry {void run()throws Exception;}
    public static Owned create(E9PcSupervisor supervisor,Path path,E9Registry.Trust trust,E9Registry.Cut cut)throws Exception{
        E9Registry.Store store=new E9Registry.Store(path,cut);supervisor.retainRegistry(store);
        E9Registry registry=new E9Registry(store,trust);supervisor.retainRegistryAuthority(registry);return new Owned(store,registry);
    }
    /** Used by BOTH real CLI entry points, including config/open/export/release initialization failures. */
    public static void boundary(E9PcSupervisor supervisor,Entry entry)throws Exception{
        try{entry.run();}catch(Exception|Error failure){supervisor.stopDependencies("REGISTRY_ENTRY_FAILED");throw failure;}
        finally{System.err.println("E9_PC_REGISTRY_ENTRY_END "+new String(supervisor.closeIngressAndSupervise().bytes(),StandardCharsets.US_ASCII));}
    }
    private E9HostRegistry(){}
}
