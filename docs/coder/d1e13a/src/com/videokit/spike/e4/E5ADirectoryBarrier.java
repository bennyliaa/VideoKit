package com.videokit.spike.e4;
import java.io.*;
import java.nio.file.Path;
import java.util.*;

/** Shared actual-resource lifecycle for Android directory FDs and local fault-test descriptor substitutes. */
public final class E5ADirectoryBarrier<D> {
    public interface Operations<D> {D open(Path path)throws Exception;void force(D descriptor)throws Exception;void close(D descriptor)throws Exception;}
    private static final class Slot<D>{D descriptor;}
    private final Operations<D> ops;private final List<E4Owned<Slot<D>>> owners=new ArrayList<>();
    public E5ADirectoryBarrier(Operations<D> operations){ops=operations;}
    public void sync(Path path)throws Exception {
        if(owners.size()>=16)throw new IOException("E5A_DIRECTORY_FD_BOUND");
        E4Owned<Slot<D>> h=new E4Owned<>(path,s->{if(s.descriptor!=null)ops.close(s.descriptor);});owners.add(h);h.allocate(Slot::new);
        h.initialize(s->{s.descriptor=ops.open(path);ops.force(s.descriptor);});h.close();
    }
    public boolean returned(){for(E4Owned<?> h:owners)if(!h.returned())return false;return true;}
    public List<? extends E4Owned<?>> owners(){return Collections.unmodifiableList(owners);}
}
