package com.videokit.spike.e4;

import java.io.IOException;
import java.nio.charset.StandardCharsets;

/** Shared real proc parser/probe interpretation; no wall-clock PID generation guess. */
public final class E9ProcessIdentity {
    public static String start(byte[] raw,int expectedPid)throws IOException{
        if(raw==null||raw.length<8||raw.length>4096)throw new IOException("E9_PROC_BOUND");String s=new String(raw,StandardCharsets.US_ASCII);int open=s.indexOf('('),close=s.lastIndexOf(')');
        if(open<1||close<=open||!s.substring(0,open).trim().equals(Integer.toString(expectedPid)))throw new IOException("E9_PROC_PID_OR_COMM");
        String[] fields=s.substring(close+1).trim().split(" +");if(fields.length<20||!fields[19].matches("[1-9][0-9]{0,18}"))throw new IOException("E9_PROC_START");try{if(Long.parseLong(fields[19])<1)throw new IOException("E9_PROC_START");}catch(NumberFormatException e){throw new IOException("E9_PROC_START");}return fields[19];
    }
    public static E9Record termination(E9Actor old,String kind,String before,String after,byte[] proc,boolean actualEnoent)throws IOException{
        if(!kind.equals(old.record.get("bootKind"))||!before.equals(after))throw new IOException("E9_TORN_OR_DIFFERENT_BOOT_SOURCE");if(kind.equals("KERNEL_BOOT_ID"))E9Record.uuid(before);else if(!before.matches("0|[1-9][0-9]{0,9}"))throw new IOException("E9_BOOT_COUNT");
        String outcome,start,source;
        if(!before.equals(old.boot)){outcome="BOOT_CHANGED";start="NOT_REQUESTED";source="DOUBLE_SAMPLED_OS_BOOT";}
        else if(actualEnoent){if(proc!=null)throw new IOException("E9_PROC_CONFLICT");outcome="PID_ABSENT";start="ENOENT";source="DOUBLE_SAMPLED_PROC";}
        else {start=start(proc,old.pid);if(start.equals(old.start))throw new IOException("E9_ORIGINAL_PROCESS_STILL_ALIVE");outcome="PID_REUSED";source="DOUBLE_SAMPLED_PROC";}
        E9Record evidence=new E9Record(E9Record.map("actor",old.hash(),"bootKind",kind,"currentBoot",before,"currentStart",start,"outcome",outcome,"source",source),2048);
        E9Record result=new E9Record(E9Record.map("kind","termination","actor",old.hash(),"bootKind",kind,"currentBoot",before,"currentStart",start,"outcome",outcome,"source",source,"evidence",evidence.hash(),"participants","SELF_NO_FD_TRANSFER","environment",old.record.get("environment")),4096);
        return E9Evidence.termination(old,result.bytes());
    }
    private E9ProcessIdentity(){}
}
