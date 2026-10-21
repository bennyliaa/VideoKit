package com.videokit.spike.c14;
import java.io.*;
import java.util.*;
import java.util.concurrent.atomic.AtomicInteger;
import com.videokit.spike.e4.*;

/** Direct calls of the PUBLIC Context overload only. No owned-owner replacement is used. */
public final class E6BPublicPreflightSelfCheck {
    static int cases,assertions;
    static final AtomicInteger contexts=new AtomicInteger(),opens=new AtomicInteger(),digests=new AtomicInteger();
    static final android.content.Context CONTEXT=new android.content.Context(){public android.content.Context getApplicationContext(){contexts.incrementAndGet();throw new AssertionError("must stop before platform");}};
    static final AsyncReadBridge.Provider SOURCE=token->{opens.incrementAndGet();throw new AssertionError("no source read");};
    static void check(boolean value){assertions++;if(!value)throw new AssertionError();}
    static E4CpuAdapter.Verification publicCall(long[] timeline)throws Exception{
        return E4CpuAdapter.validate(CONTEXT,SOURCE,timeline,List.of(),"1".repeat(64),64,()->{digests.incrementAndGet();throw new AssertionError("no digest");});
    }
    static void bad(String name,long[] timeline)throws Exception{
        try{publicCall(timeline);throw new AssertionError("public preflight passed");}
        catch(E6AFailure f){
            check(f.primary==f.getCause());check(f.primary.getClass()==IOException.class && f.primary.getCause()==null);
            check(f.primary.getMessage().equals("PIPE_OUTPUT_TIMELINE") && f.getMessage().equals("PIPE_OUTPUT_TIMELINE"));
            StackTraceElement origin=f.primary.getStackTrace()[0];check(origin.getClassName().equals(PipelineRules.class.getName()) && origin.getMethodName().equals("timeline"));
            check(f.scope.equals("VALIDATOR") && f.mode==11 && f.phase.equals("TIMELINE"));check(f.task.equals("NOT_CREATED") && f.snapshot==null && f.cleanup.isEmpty());
            check(f.safe().contains("start=NOT_STARTED") && f.safe().contains("background={NOT_COLLECTED}"));
            E6ADiagnosticState report=new E6ADiagnosticState();report.validatorEnter();check(report.validator().contains("start=UNKNOWN"));report.failure(f);
            check(report.validator().contains("task=NOT_CREATED") && report.validator().contains("phase=TIMELINE") && report.validator().contains("start=NOT_STARTED") && !report.validator().contains("start=UNKNOWN"));
            check(report.source().equals("NOT_STARTED"));check(contexts.get()==0 && opens.get()==0 && digests.get()==0 && android.os.Binder.creations==0);
        }
        cases++;System.out.println("CASE PUBLIC_"+name+" PASS originalCauseIdentity=true scope=VALIDATOR phase=TIMELINE task=NOT_CREATED start=NOT_STARTED cpuCreation=0 context=0 sourceOpen=0 digest=0");
    }
    public static void main(String[] args)throws Exception{
        bad("NULL",null);bad("LENGTH",new long[]{0,1,2,3,4});bad("FIRST_NONZERO",new long[]{1,2,3,4,5,6});bad("NON_MONOTONIC",new long[]{0,1,2,2,4,5});bad("OUT_OF_WINDOW",new long[]{0,1,2,3,4,2000001});
        check(android.os.Binder.creations==0);
        try{publicCall(new long[]{0,200000,400000,600000,800000,1000000});throw new AssertionError("creation tripwire missing");}
        catch(E6AFailure f){check(f.primary==android.os.Binder.CREATION_SENTINEL && f.getCause()==android.os.Binder.CREATION_SENTINEL);check(f.phase.equals("CREATE") && f.task.equals("NOT_CREATED") && f.snapshot==null);check(android.os.Binder.creations==1 && opens.get()==0 && digests.get()==0 && contexts.get()==0);}
        cases++;System.out.println("CASE PUBLIC_VALID_TIMELINE_REACHES_REAL_CPU_CREATION PASS creationTripwire=1 platformCalls=0 businessSuccess=NOT_INFERRED");
        System.out.println("PASS public_entry_cases="+cases+" assertions="+assertions+" bad_timeline_cpu_creation=0 Android_Binder_JNI=NOT_RUN media_reads=0");
    }
}
