package com.videokit.spike.c14;
/** Trace is diagnostic evidence only. It NEVER promotes raw OS signal zero to a passing signal. */
public final class ExitTraceRules {
    private ExitTraceRules(){}
    public static String relation(int osStatus,int expectedPid,int expectedUid,String expectedProcess,TombstoneWitness trace){
        if(!trace.matches(expectedPid,expectedUid))return "TRACE_IDENTITY_MISMATCH";
        if(expectedProcess==null || !expectedProcess.equals(trace.process))return "TRACE_PROCESS_MISMATCH";
        if(trace.signal<1)return "TRACE_SIGNAL_MISSING";
        return osStatus==0?"TRACE_MATCHED_OS_SIGNAL_UNKNOWN":osStatus==trace.signal?"TRACE_MATCHED_SYSTEM":"TRACE_SIGNAL_CONFLICT";
    }
    public static String relation(int osStatus,int pid,int uid,String process,long start,long observed,TombstoneWitness trace){
        String relation=relation(osStatus,pid,uid,process,trace);
        if(!relation.startsWith("TRACE_MATCHED"))return relation;
        if(trace.timestamp.isEmpty())return "TRACE_TIME_MISSING";
        try{String value=trace.timestamp.replace(' ','T').replaceAll("([+-][0-9]{2})([0-9]{2})$","$1:$2");long time=java.time.OffsetDateTime.parse(value).toInstant().toEpochMilli();
            if(time<start || time>observed)return "TRACE_TIME_MISMATCH";
        }catch(java.time.DateTimeException error){return "TRACE_TIME_INVALID";}
        return relation;
    }
    public static boolean isSignal(boolean matched,int reason,int status,int requested,String traceStatus){
        return matched && status>0 && requested>0 && status==requested && (reason==5 || reason==2)
            && !traceStatus.equals("TRACE_SIGNAL_CONFLICT") && !traceStatus.equals("TRACE_IDENTITY_MISMATCH")
            && !traceStatus.equals("TRACE_PROCESS_MISMATCH") && !traceStatus.equals("TRACE_PARSE_FAILED")
            && !traceStatus.equals("TRACE_TRUNCATED_OR_OVER_BUDGET") && !traceStatus.equals("TRACE_SIGNAL_MISSING")
            && !traceStatus.equals("TRACE_PERMISSION_DENIED") && !traceStatus.equals("TRACE_READ_FAILED")
            && !traceStatus.startsWith("TRACE_TIME_") && !traceStatus.equals("TRACE_SYSTEM_CHANGED_UNVERIFIED")
            && !traceStatus.equals("TRACE_CLOSE_FAILED");
    }
}
