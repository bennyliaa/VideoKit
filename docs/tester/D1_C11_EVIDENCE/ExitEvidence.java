package com.videokit.spike.c11;
import android.app.*;
import android.content.Context;
import android.os.Looper;
import java.io.*;
import java.security.MessageDigest;
import java.util.concurrent.*;
/** OS fields remain raw. App trace is separately collected, including while OS signal is zero. */
public final class ExitEvidence {
    private static final Semaphore SLOT=new Semaphore(1);
    private static final ExecutorService IO=Executors.newSingleThreadExecutor(r->{Thread t=new Thread(r,"c11-exit-evidence");t.setDaemon(true);return t;});
    private static volatile ExitTraceCapture retainedUnprovenTrace;
    public final int pid,uid,reason,status,tracePid,traceUid,traceSignal;
    public final boolean matched;public final String cause,traceSha,traceStatus,traceRelation,traceProcessSha,verdict;
    private final TombstoneWitness traceWitness;
    private ExitEvidence(int pid,int uid,int reason,int status,boolean matched,String cause,String sha,String readStatus,String relation,TombstoneWitness trace){
        this.pid=pid;this.uid=uid;this.reason=reason;this.status=status;this.matched=matched;this.cause=cause;traceSha=sha;traceStatus=readStatus;traceRelation=relation;
        traceWitness=trace;tracePid=trace==null?-1:trace.pid;traceUid=trace==null?-1:trace.uid;traceSignal=trace==null?-1:trace.signal;traceProcessSha=trace==null?"":digest(trace.process.getBytes(java.nio.charset.StandardCharsets.UTF_8));
        verdict=!matched || status==0 || !ExitTraceRules.isSignal(matched,reason,status,status,relation)?"UNKNOWN_FAIL":"SYSTEM_SIGNAL_PROVEN";
    }
    private static ExitEvidence unknown(String code){return new ExitEvidence(-1,-1,-1,-1,false,"UNKNOWN","",code,"UNAVAILABLE",null);}
    private static String digest(byte[] bytes){try{StringBuilder out=new StringBuilder();for(byte b:MessageDigest.getInstance("SHA-256").digest(bytes))out.append(String.format(java.util.Locale.ROOT,"%02x",b&255));return out.toString();}catch(java.security.NoSuchAlgorithmException impossible){throw new AssertionError(impossible);}}
    public static ExitEvidence collect(Context context,int pid,int uid,long startedAt)throws InterruptedException{return collect(context,pid,uid,startedAt,null);}
    public static ExitEvidence collect(Context context,int pid,int uid,long startedAt,String expectedProcess)throws InterruptedException{
        if(Looper.myLooper()==Looper.getMainLooper())return unknown("EXIT_EVIDENCE_MAIN_THREAD_REJECTED");
        if(!SLOT.tryAcquire())return unknown(retainedUnprovenTrace!=null?"EXIT_TRACE_CLOSE_QUARANTINED":"EXIT_EVIDENCE_QUARANTINED_PENDING");
        Future<ExitEvidence> future;
        try{future=IO.submit(()->{try{
            ActivityManager manager=context.getSystemService(ActivityManager.class);long deadline=System.nanoTime()+TimeUnit.SECONDS.toNanos(3);
            final long observedAt=System.currentTimeMillis();ExitEvidence latest=null;int traceAttempts=0;
            do{
                ApplicationExitInfo selected=null;int matches=0;
                for(ApplicationExitInfo info:manager.getHistoricalProcessExitReasons(context.getPackageName(),pid,8)){
                    if(!ExitRecordRules.matches(pid,uid,startedAt,observedAt,info.getPid(),info.getRealUid(),info.getTimestamp()))continue;
                    if(expectedProcess!=null && !expectedProcess.equals(info.getProcessName()))continue;
                    selected=info;matches++;
                }
                if(matches>1)return unknown("EXIT_RECORD_AMBIGUOUS");
                if(selected!=null){
                    ApplicationExitInfo info=selected;
                    if(traceAttempts<3){
                        latest=read(info,pid,uid,startedAt,observedAt,expectedProcess);traceAttempts++;latest.log();
                        if(retainedUnprovenTrace!=null)return latest;
                    }
                    else if(latest.status!=info.getStatus() || latest.reason!=info.getReason()){
                        latest=latest.withSystem(info);latest.log();
                    }
                    if(!ExitRecordRules.awaitSignal(info.getReason(),info.getStatus()) && !latest.traceStatus.equals("APP_TRACE_ABSENT"))return latest;
                    if(traceAttempts>=3 && !ExitRecordRules.awaitSignal(info.getReason(),info.getStatus()))return latest;
                }
                Thread.sleep(100);
            }while(System.nanoTime()<deadline);
            return latest!=null?latest:unknown("EXIT_RECORD_UNAVAILABLE");
        }catch(SecurityException error){return unknown("EXIT_RECORD_PERMISSION_DENIED");}
        catch(Exception error){StageLog.failure("EXIT_EVIDENCE_UNAVAILABLE",error);return unknown("EXIT_EVIDENCE_UNAVAILABLE");}
        finally{if(retainedUnprovenTrace==null)SLOT.release();}});}catch(RejectedExecutionException error){SLOT.release();return unknown("EXIT_EVIDENCE_QUEUE_REJECTED");}
        try{return future.get(4,TimeUnit.SECONDS);}
        catch(TimeoutException error){return unknown("EXIT_EVIDENCE_PENDING");}
        catch(ExecutionException error){return unknown("EXIT_EVIDENCE_EXECUTION_FAILED");}
    }
    private static ExitEvidence read(ApplicationExitInfo info,int pid,int uid,long start,long observed,String expectedProcess){
        if(info.getReason()!=ApplicationExitInfo.REASON_CRASH_NATIVE)return new ExitEvidence(pid,uid,info.getReason(),info.getStatus(),true,"UNKNOWN","","NOT_NATIVE_CRASH","NOT_NATIVE_CRASH",null);
        ExitTraceCapture trace=ExitTraceCapture.read(info::getTraceInputStream,info.getStatus(),pid,uid,expectedProcess==null?info.getProcessName():expectedProcess,start,observed);
        if(trace.closeUnproven())retainedUnprovenTrace=trace;
        return new ExitEvidence(pid,uid,info.getReason(),info.getStatus(),true,trace.cause,trace.sha,trace.status,trace.relation,trace.witness);
    }
    private ExitEvidence withSystem(ApplicationExitInfo info){
        return new ExitEvidence(pid,uid,info.getReason(),info.getStatus(),matched,"UNKNOWN",traceSha,traceStatus,"TRACE_SYSTEM_CHANGED_UNVERIFIED",traceWitness);
    }
    public boolean isSignal(int signal){return signal>0 && ExitTraceRules.isSignal(matched,reason,status,signal,traceRelation);}
    public boolean explainedCodecNativeAbort(){return isSignal(6) && reason==ApplicationExitInfo.REASON_CRASH_NATIVE && traceRelation.equals("TRACE_MATCHED_SYSTEM") && !cause.equals("UNKNOWN") && !traceSha.isEmpty();}
    public void log(){StageLog.event("EXIT_EVIDENCE","pid="+pid+" uid="+uid+" matched="+matched+" reason="+reason+" signal="+status+" cause="+cause+" trace_status="+traceStatus+" trace_relation="+traceRelation+" trace_source=APPLICATION_EXIT_INFO_PROTO trace_pid="+tracePid+" trace_uid="+traceUid+" trace_signal="+traceSignal+" trace_process_sha="+traceProcessSha+" trace_sha="+traceSha+" verdict="+verdict);}
}
