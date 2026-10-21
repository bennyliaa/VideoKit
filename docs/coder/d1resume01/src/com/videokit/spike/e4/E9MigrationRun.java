package com.videokit.spike.e4;

import java.io.IOException;
import java.util.*;

/** Actual managed two-phase actor. Queue reservation, returns, deadlines and finish are one boundary. */
public final class E9MigrationRun {
    public static final long QUALIFY_NS=10_000_000_000L;
    public interface Clock {long now();}
    public interface Operations {
        E9Actor identify()throws Exception;boolean identityReturned();int identityOwned();
        void commit(E9Actor actor,String reserve,E9Record binding,Stage stage)throws Exception;
        boolean commitReturned();int commitOwned();String deviceDigest();
        default String deviceRecord(){return "ABSENT";}
        default String recoveryDigest(){return "NONE";}
    }
    public interface Stage {void at(String name);}
    public interface Finish {void run(E9Record proof)throws Exception;}
    private final Operations operations;private final Clock clock;private final Finish finish;private final String handle;
    private E9Actor actor;private E9Record reserve,returnProof;private String phase="IDENTITY_RESERVED",verdict="RUNNING",reason="NONE";
    private int stateSeq=1,commandSeq,requests,statuses;private boolean identityEntered,identityIoStarted,identityDone,executeReserved,executeEntered,executeDone,commandClosed,finishClaimed;
    private long identityAt,identityNanos,executeAt,executeNanos;private boolean pending;private Throwable firstFailure;private final List<Throwable> cleanup=new ArrayList<>();
    public E9MigrationRun(String handle,Clock clock,Operations operations,Finish finish)throws IOException{E9Record.uuid(handle);this.handle=handle;this.clock=clock;this.operations=operations;this.finish=finish;identityAt=clock.now();}
    private void pend(String why){if(!pending){pending=true;reason=why;}verdict="PENDING";returnProof=null;}
    public synchronized void controlFault(){pend("CONTROL_UNKNOWN");stateSeq++;makeReturnIfSafe();}
    private synchronized void stage(String next){phase=next;stateSeq++;}
    private synchronized void failure(Throwable value){if(firstFailure==null)firstFailure=value;else cleanup.add(value);if(value instanceof InterruptedException)pend("INTERRUPTED");}
    public Throwable firstFailure(){return firstFailure;}public List<Throwable> cleanupFailures(){return List.copyOf(cleanup);}
    public void identify(){
        synchronized(this){if(identityEntered||identityDone||commandClosed){pend("IDENTITY_REENTRY");return;}identityEntered=true;phase="IDENTITY_ACTIVE";stateSeq++;}
        try{if(elapsed(identityAt)>=QUALIFY_NS||pending)throw new IOException("E9_IDENTITY_DEADLINE_BEFORE_IO");identityIoStarted=true;E9Actor sampled=operations.identify();if(!sampled.handle.equals(handle))throw new IOException("E9_IDENTITY_HANDLE");synchronized(this){actor=sampled;}}
        catch(Throwable t){failure(t);}
        finally{synchronized(this){identityDone=true;identityNanos=elapsed(identityAt);if(identityIoStarted&&!operations.identityReturned())pend("IDENTITY_OWNER_UNKNOWN");if(identityNanos>=QUALIFY_NS)pend("IDENTITY_DEADLINE");if(Thread.currentThread().isInterrupted())pend("INTERRUPTED");phase="IDENTITY_RETURNED";if(!pending){verdict=firstFailure==null&&actor!=null?"IDENTITY_QUALIFIED":"FAILED";reason=firstFailure==null?"ACTUAL_IDENTITY_RETURNED":"IDENTITY_FAILED";}stateSeq++;makeReturnIfSafe();}}
    }
    private long elapsed(long at){try{long n=clock.now()-at;if(n<0){pend("CLOCK_UNAVAILABLE");return Long.MAX_VALUE;}return n;}catch(Throwable t){pend("CLOCK_UNAVAILABLE");return Long.MAX_VALUE;}}
    public synchronized E9Actor actor()throws IOException{if(actor==null)throw new IOException("E9_IDENTITY_NOT_AVAILABLE");return actor;}
    public synchronized void deadline(){if(!identityDone&&elapsed(identityAt)>=QUALIFY_NS)pend("IDENTITY_DEADLINE");if(executeReserved&&!executeDone&&elapsed(executeAt)>=QUALIFY_NS)pend("COMMIT_DEADLINE");}
    public synchronized long remainingNanos(){if(!identityDone)return Math.max(0,QUALIFY_NS-elapsed(identityAt));if(executeReserved&&!executeDone)return Math.max(0,QUALIFY_NS-elapsed(executeAt));return -1;}
    private void count(String command,String requestedHandle,int seq,int expectedState)throws IOException{
        if(!handle.equals(requestedHandle)||seq!=commandSeq+1||expectedState!=stateSeq||(commandClosed&&!Set.of("ACK_FINISH","STATUS").contains(command))||requests>=8)throw new IOException("E9_COMMAND_BINDING_OR_BUDGET");
        commandSeq=seq;requests++;if(command.equals("STATUS")&&++statuses>3){pend("STATUS_BUDGET");throw new IOException("E9_STATUS_BUDGET");}
    }
    public synchronized E9Record status(String requestedHandle,int seq,int expectedState)throws IOException{count("STATUS",requestedHandle,seq,expectedState);deadline();return snapshot();}
    /** Independent read-only bootstrap/status ingress; current state is sampled under this same lock. */
    public synchronized E9Record observeStatus(String requestedHandle,int seq)throws IOException{
        if(seq<1||seq>8||!handle.equals(requestedHandle))throw new IOException("E9_STATUS_REQUEST_RANGE_OR_HANDLE");
        int lost=seq-commandSeq-1;
        if(lost>0){if(!handle.equals(requestedHandle)||seq>8||requests+lost+1>8||statuses+lost+1>3)throw new IOException("E9_STATUS_GAP_EXCEEDS_BUDGET");commandSeq+=lost;requests+=lost;statuses+=lost;}
        return status(requestedHandle,seq,stateSeq);
    }
    /** Called only by the OS-permission-checked management ingress, with an external BOUND record. */
    public synchronized void bindAndReserve(byte[] raw,String requestedHandle,int seq,int expectedState)throws IOException{
        count("EXECUTE_COMMIT",requestedHandle,seq,expectedState);
        if(!identityDone||actor==null||!verdict.equals("IDENTITY_QUALIFIED")||pending||executeReserved||!operations.identityReturned())throw new IOException("E9_BIND_REQUIRES_QUALIFIED_IDENTITY");
        E9Record r=E9Record.parse(raw,4096);r.exact("kind","actor","descriptor","authorization","preparePlan","state","ordinal","predecessor","recoveryEvidence","recoveryDisposition","registry","predecessorIntent");
        if(!r.get("kind").equals("reserve")||!r.get("actor").equals(actor.hash())||!r.get("descriptor").equals(actor.descriptor)||!r.get("registry").equals(actor.record.get("registry"))||!r.get("state").equals("BOUND")||r.number("ordinal",2)!=actor.ordinal)throw new IOException("E9_RESERVE_BINDING");
        E9Record.digest(r.get("authorization"));E9Record.digest(r.get("preparePlan"));
        if(actor.ordinal==1){if(!r.get("predecessor").equals("NONE")||!r.get("recoveryEvidence").equals("NONE")||!r.get("recoveryDisposition").equals("NONE")||!r.get("predecessorIntent").equals("NONE"))throw new IOException("E9_FIRST_ACTOR_NO_RECOVERY");}
        else {E9Record.digest(r.get("predecessor"));E9Record.digest(r.get("recoveryEvidence"));if(!Set.of("RETURNED_LATE_NONQUALIFIED","TERMINATED_WITHOUT_RETURN").contains(r.get("recoveryDisposition")))throw new IOException("E9_RECOVERY_DISPOSITION");if(!r.get("recoveryEvidence").equals(operations.recoveryDigest()))throw new IOException("E9_RECOVERY_EVIDENCE_MISMATCH");if(!r.get("predecessorIntent").equals("ABSENT"))E9Record.digest(r.get("predecessorIntent"));}
        reserve=r;executeReserved=true;executeAt=clock.now();returnProof=null;phase="EXECUTE_RESERVED";verdict="RUNNING";reason="NONE";stateSeq++;
    }
    public void execute(){
        synchronized(this){if(!executeReserved||executeEntered||executeDone||commandClosed){pend("EXECUTE_REENTRY_OR_NO_RESERVE");return;}executeEntered=true;phase="EXECUTE_ACTIVE";stateSeq++;}
        try{if(elapsed(executeAt)>=QUALIFY_NS||pending)throw new IOException("E9_COMMIT_DEADLINE_BEFORE_IO");operations.commit(actor,reserve.hash(),reserve,this::stage);}
        catch(Throwable t){failure(t);}
        finally{synchronized(this){executeDone=true;executeNanos=elapsed(executeAt);if(!operations.commitReturned())pend("COMMIT_OWNER_UNKNOWN");if(executeNanos>=QUALIFY_NS)pend("COMMIT_DEADLINE");if(Thread.currentThread().isInterrupted())pend("INTERRUPTED");phase="RETURNED";if(!pending){verdict=firstFailure==null?"QUALIFIED_MIGRATION":"FAILED";reason=firstFailure==null?"ACTUAL_ALL_RETURNED":"ORIGINAL_FAILURE_RETURNED";}stateSeq++;makeReturnIfSafe();}}
    }
    private boolean actualSafe(){return identityDone&&(!identityIoStarted||operations.identityReturned())&&(!executeReserved||executeDone&&operations.commitReturned());}
    private void makeReturnIfSafe(){
        if(!actualSafe())return;
        if(actor==null){try{returnProof=new E9Record(E9Record.map("kind","unboundReturned","handle",handle,"stateSeq",Integer.toString(stateSeq),"phase","IDENTITY","verdict",pending?"PENDING":"FAILED","owned",Integer.toString(operations.identityOwned()),"unreturned","0","executeDone","false"),4096);}catch(IOException e){pend("UNBOUND_RETURN_FRAME");}return;}
        try{returnProof=new E9Record(E9Record.map("kind","returned","actor",actor.hash(),"stateSeq",Integer.toString(stateSeq),"identityNanos",Long.toString(identityNanos),"executeNanos",Long.toString(executeNanos),"verdict",verdict,"reason",reason,"phase",executeDone?"COMMIT":"IDENTITY","owned",Integer.toString(operations.identityOwned()+operations.commitOwned()),"unreturned","0","executeDone",Boolean.toString(executeDone),"device",operations.deviceDigest(),"deviceRecord",operations.deviceRecord(),"environment",actor.record.get("environment")),8192);}catch(IOException e){pend("RETURN_FRAME_BOUND");}
    }
    public synchronized E9Record returnProof()throws IOException{if(returnProof==null)throw new IOException("E9_NO_ACTUAL_RETURN_PROOF");return returnProof;}
    public synchronized E9Record snapshot()throws IOException{
        return new E9Record(E9Record.map("kind","snapshot","handle",handle,"actor",actor==null?"ABSENT":actor.hash(),"phase",phase,"verdict",verdict,"reason",reason,"stateSeq",Integer.toString(stateSeq),"commandSeq",Integer.toString(commandSeq),"requests",Integer.toString(requests),"statuses",Integer.toString(statuses),"safe",Boolean.toString(actualSafe()),"owned",Integer.toString(operations.identityOwned()+operations.commitOwned()),"executeReserved",Boolean.toString(executeReserved),"finishClaimed",Boolean.toString(finishClaimed),"returned",returnProof==null?"ABSENT":returnProof.hash()),4096);
    }
    public synchronized void stop(String requestedHandle,int seq,int expectedState)throws IOException{count("STOP_DEPENDENCIES",requestedHandle,seq,expectedState);pend("EXTERNAL_STOP");stateSeq++;makeReturnIfSafe();}
    /** No queued execute or in-flight original can be finished, even if its FD holder is still EMPTY. */
    public boolean acknowledgeFinish(String requestedHandle,int seq,int expectedState,String archivedReturn)throws IOException{
        E9Record proof;
        synchronized(this){count("ACK_FINISH",requestedHandle,seq,expectedState);if(finishClaimed||!actualSafe()||returnProof==null||!returnProof.hash().equals(archivedReturn)){pend("EARLY_OR_WRONG_ARCHIVE_ACK");throw new IOException("E9_FINISH_DENIED");}finishClaimed=true;commandClosed=true;stateSeq++;proof=returnProof;}
        try{finish.run(proof);return true;}catch(Throwable t){failure(t);controlFault();return false;}
    }
    public synchronized void closeUnstartedWriteIngress(){if(executeReserved){pend("RESERVED_OPERATION_MUST_RETURN");return;}commandClosed=true;if(!actualSafe())pend("IDENTITY_OWNER_UNKNOWN");else{if(!pending){verdict=actor!=null&&firstFailure==null?"IDENTITY_QUALIFIED":"FAILED";reason="NO_WRITE_INGRESS_CLOSED";}stateSeq++;makeReturnIfSafe();}}
}
