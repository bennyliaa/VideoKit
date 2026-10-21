package com.videokit.spike.c07;
/** Small synchronous task-owned evidence ledger; unknown deaths remain unknown. */
public final class CodecProbeState {
    private String last="NEW",javaCause="";private int events;
    public synchronized void record(String value){
        boolean allowed=last.equals("NEW") && value.equals("PROBE_LEASE_ACQUIRED")
            || last.equals("PROBE_LEASE_ACQUIRED") && value.equals("PROBE_CODEC_CREATE_BEGIN")
            || last.equals("PROBE_CODEC_CREATE_BEGIN") && (value.equals("PROBE_CODEC_CREATE_END") || value.matches("PROBE_JAVA_FAILURE_(IO|SECURITY|RUNTIME)_EXCEPTION"))
            || last.equals("PROBE_CODEC_CREATE_END") && value.equals("PROBE_CODEC_RELEASE_BEGIN")
            || last.equals("PROBE_CODEC_RELEASE_BEGIN") && value.matches("PROBE_CODEC_RELEASE_(END|FAILED)");
        if(!allowed || ++events>6)throw new SecurityException("CODEC_PROBE_STAGE_REJECTED");last=value;if(value.startsWith("PROBE_JAVA_FAILURE_"))javaCause=value;
    }
    public synchronized String last(){return last;}
    public synchronized boolean nativeCallPending(){return last.equals("PROBE_CODEC_CREATE_BEGIN");}
    public synchronized boolean javaFailureObserved(){return !javaCause.isEmpty();}
    public synchronized boolean explainedOutcome(String code,boolean matchedNativeCause){
        return code.equals("ISOLATED_CODEC_JAVA_CALL_FAILED") && javaFailureObserved()
            || code.equals("WORKER_DIED") && nativeCallPending() && matchedNativeCause;
    }
}
