package com.videokit.spike.c14;
import java.io.*;
import java.nio.charset.StandardCharsets;
public final class C14TraceSelfCheck {
    static int checks;static void yes(boolean value){if(!value)throw new AssertionError("case "+checks);checks++;}
    static void varint(ByteArrayOutputStream b,long n){while(n>=128){b.write((int)n&127|128);n>>>=7;}b.write((int)n);}
    static void number(ByteArrayOutputStream b,int f,long n){varint(b,f*8);varint(b,n);}
    static void text(ByteArrayOutputStream b,int f,String s){byte[] bytes=s.getBytes(StandardCharsets.UTF_8);varint(b,f*8+2);varint(b,bytes.length);b.write(bytes,0,bytes.length);}
    static byte[] proto(int pid,int uid,int signal,String process,String time){ByteArrayOutputStream b=new ByteArrayOutputStream();number(b,5,pid);number(b,7,uid);text(b,9,process);text(b,4,time);varint(b,82);varint(b,2);number(b,1,signal);return b.toByteArray();}
    static final String PROCESS="com.videokit.app:d1_cpu_worker:task";
    static final long TIME=java.time.OffsetDateTime.parse("2026-10-16T09:43:33.932+08:00").toInstant().toEpochMilli();
    static ExitTraceCapture capture(int status,byte[] bytes){return ExitTraceCapture.read(()->new ByteArrayInputStream(bytes),status,27146,99055,PROCESS,TIME-1000,TIME+1000);}
    public static void main(String[] args)throws Exception {
        byte[] valid=proto(27146,99055,11,PROCESS,"2026-10-16 09:43:33.932000000+0800");int[] opens={0},closes={0};
        ExitTraceCapture zero=ExitTraceCapture.read(()->{opens[0]++;return new ByteArrayInputStream(valid){public void close(){closes[0]++;}};},0,27146,99055,PROCESS,TIME-1000,TIME+1000);
        yes(opens[0]==1 && closes[0]==1);yes(zero.status.equals("TRACE_READ_PARSED"));yes(zero.witness.signal==11);yes(zero.relation.equals("TRACE_MATCHED_OS_SIGNAL_UNKNOWN"));yes(zero.sha.length()==64);yes(!ExitTraceRules.isSignal(true,5,0,11,zero.relation));
        ExitTraceCapture absent=ExitTraceCapture.read(()->null,0,27146,99055,PROCESS,TIME-1000,TIME+1000);yes(absent.status.equals("APP_TRACE_ABSENT"));yes(!ExitTraceRules.isSignal(true,5,0,11,absent.relation));
        yes(capture(11,valid).relation.equals("TRACE_MATCHED_SYSTEM"));yes(ExitTraceRules.isSignal(true,5,11,11,capture(11,valid).relation));
        yes(capture(6,valid).relation.equals("TRACE_SIGNAL_CONFLICT"));yes(!ExitTraceRules.isSignal(true,5,6,6,capture(6,valid).relation));
        for(int status:new int[]{0,11}){
            ExitTraceCapture wrong=capture(status,proto(27175,99056,11,PROCESS,"2026-10-16 09:43:33.932000000+0800"));yes(wrong.relation.equals("TRACE_IDENTITY_MISMATCH"));yes(!ExitTraceRules.isSignal(true,5,status,11,wrong.relation));
            wrong=capture(status,proto(27146,99055,11,"other:process","2026-10-16 09:43:33.932000000+0800"));yes(wrong.relation.equals("TRACE_PROCESS_MISMATCH"));
            wrong=capture(status,proto(27146,99055,11,PROCESS,"2026-10-16 09:00:00.000000000+0800"));yes(wrong.relation.equals("TRACE_TIME_MISMATCH"));
            wrong=capture(status,proto(27146,99055,11,PROCESS,""));yes(wrong.relation.equals("TRACE_TIME_MISSING"));
            wrong=capture(status,proto(27146,99055,11,PROCESS,"invalid"));yes(wrong.relation.equals("TRACE_TIME_INVALID"));
            byte[] truncated=java.util.Arrays.copyOf(valid,valid.length-1);yes(capture(status,truncated).status.equals("TRACE_TRUNCATED_OR_OVER_BUDGET"));
            yes(capture(status,new byte[262145]).status.equals("TRACE_TRUNCATED_OR_OVER_BUDGET"));
            yes(!ExitTraceRules.isSignal(true,5,status,11,"TRACE_PARSE_FAILED"));
        }
        ExitTraceCapture denied=ExitTraceCapture.read(()->{throw new SecurityException();},0,1,99001,PROCESS,1,2);yes(denied.status.equals("TRACE_PERMISSION_DENIED"));
        ExitTraceCapture failed=ExitTraceCapture.read(()->{throw new IOException();},0,1,99001,PROCESS,1,2);yes(failed.status.equals("TRACE_READ_FAILED"));
        failed=ExitTraceCapture.read(()->new InputStream(){public int read(){return 0;}public int read(byte[] b,int o,int n){return 0;}},0,1,99001,PROCESS,1,2);yes(failed.status.equals("TRACE_READ_FAILED"));
        ByteArrayOutputStream duplicate=new ByteArrayOutputStream();duplicate.write(valid);number(duplicate,5,27146);yes(capture(0,duplicate.toByteArray()).status.equals("TRACE_PARSE_FAILED"));
        duplicate=new ByteArrayOutputStream();duplicate.write(valid);text(duplicate,9,PROCESS);yes(capture(0,duplicate.toByteArray()).status.equals("TRACE_PARSE_FAILED"));
        yes(!ExitTraceRules.isSignal(false,5,11,11,"TRACE_MATCHED_SYSTEM"));yes(!ExitTraceRules.isSignal(true,1,11,11,"TRACE_MATCHED_SYSTEM"));yes(!ExitTraceRules.isSignal(true,5,9,11,"TRACE_MATCHED_SYSTEM"));
        yes(!ExitTraceRules.isSignal(true,5,-1,-1,"APP_TRACE_ABSENT"));yes(!ExitTraceRules.isSignal(true,5,11,11,"TRACE_SYSTEM_CHANGED_UNVERIFIED"));
        ExitTraceCapture closeFailed=ExitTraceCapture.read(()->new ByteArrayInputStream(valid){public void close()throws IOException{throw new IOException("close refused");}},11,27146,99055,PROCESS,TIME-1000,TIME+1000);
        yes(closeFailed.status.equals("TRACE_CLOSE_FAILED") && closeFailed.closeUnproven());yes(!ExitTraceRules.isSignal(true,5,11,11,closeFailed.relation));
        System.out.println("PASS "+checks+" actual bounded trace-reader/system-zero/conflict/identity/time counterexamples; Android trace availability NOT_RUN");
    }
}
