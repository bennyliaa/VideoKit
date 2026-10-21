package com.videokit.spike.c06;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.util.Arrays;
/** New C06 meaningful counterexamples; no OS exit records, actual signals or codec are simulated as device PASS. */
public final class C06FailureSelfCheck {
    private static int assertions;
    private static void check(boolean ok,String text){if(!ok)throw new AssertionError(text);assertions++;System.out.println("PASS "+text);}
    private static byte[] trace(int pid,int uid,int signal,String abort)throws IOException{
        ByteArrayOutputStream bytes=new ByteArrayOutputStream();bytes.write(40);number(bytes,pid);bytes.write(56);number(bytes,uid);bytes.write(82);bytes.write(2);bytes.write(8);bytes.write(signal);byte[] text=abort.getBytes(StandardCharsets.UTF_8);bytes.write(114);number(bytes,text.length);bytes.write(text);return bytes.toByteArray();
    }
    private static void number(OutputStream bytes,int value)throws IOException{while(value>127){bytes.write((value&127)|128);value>>>=7;}bytes.write(value);}
    private static void reject(byte[] bytes,String text){try{TombstoneWitness.parse(bytes);throw new AssertionError(text);}catch(IOException expected){check(true,text);}}
    public static void main(String[] args)throws Exception{
        byte[] good=trace(12345,99001,6,"Binder driver could not be opened. Terminating.");TombstoneWitness w=TombstoneWitness.parse(good);
        check(w.matches(12345,99001) && w.signal==6 && w.cause.equals("BINDER_DRIVER_OPEN_FATAL"),"matching native witness exposes only allowlisted cause");
        check(!w.matches(12346,99001),"other PID cannot qualify");check(!w.matches(12345,99002),"other isolated UID cannot qualify");
        check(TombstoneWitness.parse(trace(12345,99001,6,"arbitrary secret /private/media")).cause.equals("UNKNOWN"),"unrecognized abort text remains UNKNOWN and redacted");
        reject(Arrays.copyOf(good,good.length-1),"truncated tombstone rejected");reject(new byte[]{(byte)0x80},"truncated varint rejected");reject(new byte[]{114,(byte)0xff,127},"oversized length rejected");reject(new byte[262145],"whole trace budget enforced");
        reject(new byte[]{40,1,40,2},"duplicate identity rejected");reject(new byte[]{11},"unsupported group wire rejected");
        CodecProbeState p=new CodecProbeState();check(!p.explainedOutcome("WORKER_DIED",true),"no acknowledged codec stage cannot qualify native death");
        p.record("PROBE_LEASE_ACQUIRED");p.record("PROBE_CODEC_CREATE_BEGIN");check(!p.explainedOutcome("WORKER_DIED",false),"unexplained death rejected even with actual call stage");check(p.explainedOutcome("WORKER_DIED",true),"pending codec plus separately matched concrete native cause classified");
        check(!p.explainedOutcome("WORKER_START_FAILED",true),"bind or grant failure never native codec outcome");
        try{p.record("PROBE_CODEC_RELEASE_END");throw new AssertionError();}catch(SecurityException expected){check(true,"out-of-order release rejected");}
        p.record("PROBE_JAVA_FAILURE_IO_EXCEPTION");check(p.explainedOutcome("ISOLATED_CODEC_JAVA_CALL_FAILED",false),"actual typed Java failure accepted without claiming permission denial");check(!p.explainedOutcome("WORKER_DIED",true),"native death after Java result is not reclassified");
        try{p.record("PROBE_JAVA_FAILURE_IO_EXCEPTION");throw new AssertionError();}catch(SecurityException expected){check(true,"duplicate probe result rejected");}
        CodecProbeState available=new CodecProbeState();available.record("PROBE_LEASE_ACQUIRED");available.record("PROBE_CODEC_CREATE_BEGIN");available.record("PROBE_CODEC_CREATE_END");available.record("PROBE_CODEC_RELEASE_BEGIN");available.record("PROBE_CODEC_RELEASE_END");check(!available.explainedOutcome("ISOLATED_CODEC_CAPABILITY_AVAILABLE",true),"available codec is not a failure proof");
        FrameWindow window=FrameWindow.at(10000000);check(window.startMs==9000 && window.endMs==12000 && window.localUs==1000000 && window.requestedUs==10000000,"AVI original ten seconds preserved as nine-second clip plus one-second request");
        FrameWindow precise=FrameWindow.at(10000123);check(precise.startMs*1000+precise.localUs==10000123,"fractional microseconds not silently replaced");
        try{FrameWindow.at(0);throw new AssertionError();}catch(IllegalArgumentException expected){check(true,"zero-frame substitute rejected");}
        try{FrameWindow.at(Long.MAX_VALUE);throw new AssertionError();}catch(IllegalArgumentException expected){check(true,"time overflow rejected");}
        System.out.println("RESULT c06_failure_assertions="+assertions+" failures=0 Android_native_signal_codec_frame=NOT_RUN");
    }
}
