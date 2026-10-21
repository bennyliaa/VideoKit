package com.videokit.spike.c14;
import java.io.IOException;
import java.util.*;
import com.videokit.spike.e4.E6FailureCodes;
/** Background native evidence never replaces the original business/Java first failure. */
public final class E6AFailure extends IOException {
    public final Throwable primary;public final List<Throwable> cleanup;
    public final String scope,task,phase;public final int mode;public final E6NativeDiagnostic snapshot;
    public E6AFailure(String scope,String task,int mode,String phase,Throwable primary,List<Throwable> cleanup,E6NativeDiagnostic snapshot){
        super(E6FailureCodes.safe(primary),primary);this.scope=scope;this.task=task;this.mode=mode;this.phase=phase;this.primary=primary;this.cleanup=List.copyOf(cleanup);this.snapshot=snapshot;
        if(!(scope.equals("SOURCE") && mode==10 || scope.equals("VALIDATOR") && mode==11) || !task.matches("(?:[a-f0-9]{32}|NOT_CREATED)") || !phase.matches("[A-Z_]{1,32}") || cleanup.size()>2)throw new IllegalArgumentException("E6A_FAILURE_SCOPE");
        for(Throwable t:cleanup)if(t!=primary)addSuppressed(t);
    }
    private static String type(Throwable t){String s=t.getClass().getName();return s.matches("[A-Za-z0-9_.$]{1,160}")?s:"UNAVAILABLE_TYPE";}
    public String safe(){
        StringBuilder s=new StringBuilder("scope=").append(scope).append(" task=").append(task).append(" mode=").append(mode).append(" phase=").append(phase).append(" primary=").append(getMessage()).append(" primary_type=").append(type(primary));
        s.append(" start=").append(phase.equals("CREATE") || phase.equals("TIMELINE") || phase.equals("BEFORE_READ")?"NOT_STARTED":"ENTERED");
        s.append(" background={").append(snapshot==null?"NOT_COLLECTED":snapshot.safe()).append('}');
        for(int i=0;i<cleanup.size();i++)s.append(" cleanup").append(i).append('=').append(E6FailureCodes.safe(cleanup.get(i))).append(':').append(type(cleanup.get(i)));
        return s.toString();
    }
}
