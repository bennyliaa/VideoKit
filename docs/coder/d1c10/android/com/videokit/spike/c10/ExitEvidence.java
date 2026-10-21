package com.videokit.spike.c10;
import android.app.*;
import android.content.Context;
import java.io.*;
import java.security.MessageDigest;
import java.util.concurrent.*;
/** Task PID/UID/time matched OS evidence. Unavailable, stale and unexplained deaths never qualify. */
public final class ExitEvidence {
    private static final Semaphore SLOT=new Semaphore(1);
    private static final ExecutorService IO=Executors.newSingleThreadExecutor(r->{Thread t=new Thread(r,"c10-exit-evidence");t.setDaemon(true);return t;});
    public final int pid,uid,reason,status;public final boolean matched;public final String cause,traceSha,traceStatus;
    private ExitEvidence(int pid,int uid,int reason,int status,boolean matched,String cause,String sha,String traceStatus){this.pid=pid;this.uid=uid;this.reason=reason;this.status=status;this.matched=matched;this.cause=cause;traceSha=sha;this.traceStatus=traceStatus;}
    private static ExitEvidence unknown(String code){return new ExitEvidence(-1,-1,-1,-1,false,code,"","UNAVAILABLE");}
    public static ExitEvidence collect(Context context,int pid,int uid,long startedAt)throws InterruptedException{
        if(!SLOT.tryAcquire())return unknown("EXIT_EVIDENCE_QUARANTINED");
        Future<ExitEvidence> f=IO.submit(()->{try{
            ActivityManager manager=context.getSystemService(ActivityManager.class);long stop=System.nanoTime()+TimeUnit.SECONDS.toNanos(3);
            final long observedAt=System.currentTimeMillis();ExitEvidence partial=null;
            do{ApplicationExitInfo selected=null;int matches=0;
                for(ApplicationExitInfo info:manager.getHistoricalProcessExitReasons(context.getPackageName(),pid,8)){
                    if(!ExitRecordRules.matches(pid,uid,startedAt,observedAt,info.getPid(),info.getRealUid(),info.getTimestamp()))continue;
                    selected=info;matches++;
                }
                if(matches>1)return unknown("EXIT_RECORD_AMBIGUOUS");
                if(selected!=null){ApplicationExitInfo info=selected;
                if(ExitRecordRules.awaitSignal(info.getReason(),info.getStatus())){
                    partial=new ExitEvidence(pid,uid,info.getReason(),0,true,"UNKNOWN","","PARTIAL_SIGNAL_UNKNOWN");
                    Thread.sleep(100);continue;
                }
                String cause="UNKNOWN",sha="",traceStatus="NOT_NATIVE_CRASH";
                if(info.getReason()==ApplicationExitInfo.REASON_CRASH_NATIVE)try(InputStream trace=info.getTraceInputStream()){
                    traceStatus="APP_TRACE_ABSENT";if(trace!=null){traceStatus="READING";ByteArrayOutputStream bytes=new ByteArrayOutputStream();byte[] buffer=new byte[4096];int n;while((n=trace.read(buffer,0,Math.min(buffer.length,262145-bytes.size())))!=-1){bytes.write(buffer,0,n);if(bytes.size()>262144)throw new IOException("TRACE_BUDGET");}
                        byte[] raw=bytes.toByteArray();TombstoneWitness witness=TombstoneWitness.parse(raw);traceStatus="IDENTITY_OR_SIGNAL_MISMATCH";if(witness.matches(pid,uid) && witness.signal==info.getStatus()){traceStatus="MATCHED_PROTO";cause=witness.cause;byte[] digest=MessageDigest.getInstance("SHA-256").digest(raw);StringBuilder hex=new StringBuilder();for(byte b:digest)hex.append(String.format(java.util.Locale.ROOT,"%02x",b&255));sha=hex.toString();}
                    }
                }catch(Exception error){traceStatus="READ_OR_PARSE_FAILED";StageLog.failure("EXIT_TRACE_UNAVAILABLE",error);}
                return new ExitEvidence(pid,uid,info.getReason(),info.getStatus(),true,cause,sha,traceStatus);
            }Thread.sleep(100);}while(System.nanoTime()<stop);return partial!=null?partial:unknown("EXIT_RECORD_UNAVAILABLE");
        }catch(Exception error){StageLog.failure("EXIT_EVIDENCE_UNAVAILABLE",error);return unknown("EXIT_EVIDENCE_UNAVAILABLE");}finally{SLOT.release();}});
        try{return f.get(4,TimeUnit.SECONDS);}catch(ExecutionException|TimeoutException e){return unknown("EXIT_EVIDENCE_UNAVAILABLE_OR_PENDING");}
    }
    public boolean isSignal(int signal){return matched && status==signal && (reason==ApplicationExitInfo.REASON_CRASH_NATIVE || reason==ApplicationExitInfo.REASON_SIGNALED);}
    public boolean explainedCodecNativeAbort(){return isSignal(6) && reason==ApplicationExitInfo.REASON_CRASH_NATIVE && !cause.equals("UNKNOWN") && !traceSha.isEmpty();}
    public void log(){StageLog.event("EXIT_EVIDENCE","pid="+pid+" uid="+uid+" matched="+matched+" reason="+reason+" signal="+status+" cause="+cause+" trace_status="+traceStatus+" trace_sha="+traceSha);}
}
