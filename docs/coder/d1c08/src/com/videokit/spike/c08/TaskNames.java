package com.videokit.spike.c08;
import java.util.UUID;
/** Deterministic package-safe instance name; task identity remains the original UUID on IPC/journal. */
public final class TaskNames {
    public static String instance(String prefix,String id){
        if(!prefix.matches("[a-z]{1,16}") || !UUID.fromString(id).toString().equals(id))throw new IllegalArgumentException("INVALID_TASK_ID");
        return prefix+"_"+id.replace("-","");
    }
    private TaskNames(){}
}
