package com.videokit.spike.c14;
import java.io.IOException;
import java.util.concurrent.atomic.AtomicReference;
/** The complete production diagnostic receive boundary: authentication, parse/end, consistency, then publish. */
final class E6ADiagnosticInbox {
    interface State {int pid();int uid();String task();long epoch();boolean revoked();int stage();int mode();int frames();}
    interface Payload {E6NativeDiagnostic parse()throws Exception;void end()throws Exception;}
    private final State state;private final AtomicReference<E6NativeDiagnostic> first=new AtomicReference<>();
    E6ADiagnosticInbox(State state){this.state=state;}
    E6NativeDiagnostic snapshot(){return first.get();}
    E6NativeDiagnostic receive(int pid,int uid,String task,long epoch,int size,Payload payload)throws Exception {
        if(size<0 || size>1024)throw new IOException("CPU_PARCEL_BUDGET");
        if(pid<=0 || uid<=0 || pid!=state.pid() || uid!=state.uid() || !state.task().equals(task) || epoch!=state.epoch() || state.revoked())throw new IOException("CPU_BROKER_IDENTITY");
        E6NativeDiagnostic d=payload.parse();payload.end();
        if(d==null || d.stage!=state.stage() || state.mode()==11 && d.accepted!=state.frames())throw new IOException("E6_NATIVE_DIAG_PHASE");
        if(!first.compareAndSet(null,d))throw new IOException("E6_NATIVE_DIAG_ONCE");
        return d;
    }
}
