package com.videokit.spike.c12;
/** Revoking an accepted/unknown bind is independent of death, and proves no worker release. */
public final class BindingRevocation {
    public static final class Snapshot {
        public final boolean issued,inFlight,accepted,uncertain,requested,pending,closed;
        public final int attempts;public final String result;
        Snapshot(BindingRevocation b){issued=b.issued;inFlight=b.inFlight;accepted=b.accepted;uncertain=b.uncertain;requested=b.requested;pending=b.pending;closed=b.closed;attempts=b.attempts;result=b.result;}
    }
    private boolean issued,inFlight,accepted,uncertain,requested,pending,closed;private int attempts;private String result="NOT_REQUESTED";
    public synchronized void beginBind(){if(issued)throw new IllegalStateException("CPU_BIND_ALREADY_ISSUED");issued=true;inFlight=true;}
    public synchronized void returned(boolean accepted){inFlight=false;this.accepted=accepted;}
    public synchronized void returnedUnknown(){inFlight=false;uncertain=true;}
    public synchronized boolean request(){boolean first=!requested;requested=true;return first;}
    public synchronized boolean queue(){if(!requested || !issued || inFlight || (!accepted && !uncertain) || pending || closed || attempts>=3)return false;pending=true;attempts++;result="QUEUED";return true;}
    public synchronized void finished(boolean success,String result){if(!pending)throw new IllegalStateException("CPU_UNBIND_NOT_PENDING");pending=false;closed|=success;this.result=result;}
    public synchronized Snapshot snapshot(){return new Snapshot(this);}
}
