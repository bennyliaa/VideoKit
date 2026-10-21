package com.videokit.spike.e4;

/** Actual asynchronous job and finish boundary used by the non-JUnit runner. No wait/cancel loop. */
public final class E7ADiagnosticRun<T> implements Runnable {
    public static final long QUALIFICATION_NS=10_000_000_000L;
    public interface Clock { long now(); }
    public interface Operations<T> {
        void preflight() throws Exception;
        T open() throws Exception;
        void readAndVerify(T value) throws Exception;
        void close(T value) throws Exception;
        void afterClose() throws Exception;
        String diagnose() throws Exception;
    }
    public interface Finish { void run(Snapshot snapshot) throws Exception; }
    public static final class Snapshot {
        public final String handle,phase,verdict,reason,holder,diagnosis;
        public final int sequence; public final boolean operationsReturned,safeToFinish,finishClaimed;
        Snapshot(String h,String p,String v,String r,String holder,String d,int seq,boolean returned,boolean safe,boolean claimed){handle=h;phase=p;verdict=v;reason=r;this.holder=holder;diagnosis=d;sequence=seq;operationsReturned=returned;safeToFinish=safe;finishClaimed=claimed;}
        public String record(){return "E7A handle="+handle+" sequence="+sequence+" phase="+phase+" verdict="+verdict+" reason="+reason+" holder="+holder+" originalOperationsReturned="+operationsReturned+" safeToFinish="+safeToFinish+" finishClaimed="+finishClaimed+" admission=NONE "+diagnosis;}
    }
    private final String handle;private final Clock clock;private final Operations<T> ops;private final Finish finish;
    private final E4Owned<T> owner;private final long deadline;
    private String phase="RESERVED",verdict="RUNNING",reason="NONE",diagnosis="NOT_COLLECTED";
    private int sequence=1;private boolean launchAttempted,workerEntered,workerReturned,finishClaimed;
    private Throwable firstFailure;
    public E7ADiagnosticRun(String handle,Clock clock,Operations<T> operations,Finish finish){
        if(handle==null||!handle.matches("[a-f0-9-]{36}"))throw new IllegalArgumentException("HANDLE");
        this.handle=handle;this.clock=clock;ops=operations;this.finish=finish;deadline=clock.now()+QUALIFICATION_NS;
        owner=new E4Owned<>(handle,operations::close);
    }
    /** Reserve before Thread.start(), so the allocation/launch window can never look returned. */
    public synchronized void beginLaunch(){if(launchAttempted||workerReturned)throw new IllegalStateException("LAUNCH_ONCE");launchAttempted=true;phase="LAUNCH_WINDOW";sequence++;}
    public synchronized void abortBeforeLaunch(){
        if(launchAttempted){pending("LAUNCH_OUTCOME_UNKNOWN");return;}
        workerReturned=true;if(!verdict.equals("PENDING")){verdict="FAILED";reason="PRELAUNCH_REJECTED";}phase="RETURNED";sequence++;
    }
    private synchronized void phase(String value){phase=value;sequence++;}
    private synchronized void failure(Throwable value){if(firstFailure==null)firstFailure=value;if(value instanceof InterruptedException)pending("INTERRUPTED");}
    @Override public void run(){
        synchronized(this){if(!launchAttempted||workerEntered||workerReturned){pending("WORKER_ENTRY_REJECTED");return;}workerEntered=true;}
        try{
            if(Thread.currentThread().isInterrupted())throw new InterruptedException();
            phase("PREFLIGHT");ops.preflight();
            phase("OPEN");owner.allocate(ops::open);
            try{phase("READ");ops.readAndVerify(owner.original());}
            catch(Throwable t){failure(t);}
            finally{phase("CLOSE");try{owner.close();}catch(Throwable t){failure(t);}}
            if(firstFailure==null){phase("AFTER_CLOSE");ops.afterClose();phase("HISTORY_PROC");String d=ops.diagnose();if(d==null||d.length()>3072)throw new IllegalStateException("DIAGNOSIS_BOUND");diagnosis=d;}
        }catch(Throwable t){failure(t);}
        finally{
            synchronized(this){
                workerReturned=true;phase="RETURNED";
                if(Thread.currentThread().isInterrupted())pending("INTERRUPTED");
                if(!safeResources())pending("OWNER_RETURN_UNPROVEN");
                else {try{if(clock.now()>=deadline)pending("QUALIFICATION_DEADLINE");}catch(Throwable t){pending("CLOCK_UNAVAILABLE");}}
                if(!verdict.equals("PENDING")){verdict=firstFailure==null?"QUALIFIED_DIAGNOSTIC":"FAILED";reason=firstFailure==null?"ACTUAL_RETURNED":"ORIGINAL_FAILURE_RETURNED";}
                sequence++;
            }
        }
    }
    private boolean safeResources(){return workerReturned&&(owner.state()==E4Owned.State.EMPTY||owner.returned());}
    private void pending(String why){if(!verdict.equals("PENDING")){verdict="PENDING";reason=why;sequence++;}}
    public synchronized void deadline(){if(!workerReturned&&clock.now()>=deadline)pending("QUALIFICATION_DEADLINE");}
    public synchronized void stopDependencies(){pending("EXTERNAL_STOP_DEPENDENCIES");}
    public synchronized void controlFault(){pending("CONTROL_EXCEPTION");}
    public synchronized Snapshot snapshot(){return new Snapshot(handle,phase,verdict,reason,owner.state().name(),diagnosis,sequence,workerReturned,safeResources(),finishClaimed);}
    /** Only an exact external archive ACK and actual original returns can invoke platform finish. */
    public boolean acknowledgeFinish(String requestedHandle,int archivedSequence){
        Snapshot value;
        synchronized(this){
            if(!handle.equals(requestedHandle)||archivedSequence!=sequence||finishClaimed)return false;
            if(!safeResources()){pending("EARLY_FINISH_REJECTED");return false;}
            finishClaimed=true;sequence++;value=snapshot();
        }
        try{finish.run(value);return true;}catch(Throwable t){failure(t);controlFault();return false;}
    }
}
