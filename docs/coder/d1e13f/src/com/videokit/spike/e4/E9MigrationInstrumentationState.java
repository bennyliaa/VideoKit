package com.videokit.spike.e4;

/** The actual original managed run, also visible to current-host admission; never a resource release counter. */
public final class E9MigrationInstrumentationState {
    private static volatile E9MigrationRun original;
    public static synchronized void retain(E9MigrationRun value){if(original!=null)throw new IllegalStateException("E9_MANAGED_RUN_ONCE");original=value;}
    public static boolean hasOriginal(){return original!=null;}
    public static boolean hasUnreturned(){E9MigrationRun r=original;if(r==null)return false;try{return !r.snapshot().get("safe").equals("true");}catch(Exception e){return true;}}
    private E9MigrationInstrumentationState(){}
}
