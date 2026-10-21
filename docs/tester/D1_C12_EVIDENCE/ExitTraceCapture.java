package com.videokit.spike.c12;
import java.io.*;
import java.security.*;
/** Shared bounded input path used by Android and local counterexamples. No external/raw-log source. */
public final class ExitTraceCapture {
    public interface Source {InputStream open()throws IOException;}
    public final String status,relation,sha,cause;public final TombstoneWitness witness;
    private InputStream unprovenClose;
    public boolean closeUnproven(){return unprovenClose!=null;}
    private ExitTraceCapture(String status,String relation,String sha,TombstoneWitness witness){this.status=status;this.relation=relation;this.sha=sha;this.witness=witness;cause=witness!=null && relation.startsWith("TRACE_MATCHED")?witness.cause:"UNKNOWN";}
    public static ExitTraceCapture read(Source source,int osStatus,int pid,int uid,String process,long start,long observed){
        InputStream input=null;ExitTraceCapture result;
        try{input=source.open();result=input==null?new ExitTraceCapture("APP_TRACE_ABSENT","APP_TRACE_ABSENT","",null):readOpen(input,osStatus,pid,uid,process,start,observed);}
        catch(SecurityException error){result=new ExitTraceCapture("TRACE_PERMISSION_DENIED","TRACE_PERMISSION_DENIED","",null);}
        catch(Exception error){result=new ExitTraceCapture("TRACE_READ_FAILED","TRACE_READ_FAILED","",null);}
        if(input!=null)try{input.close();}catch(Exception error){ExitTraceCapture failed=new ExitTraceCapture("TRACE_CLOSE_FAILED","TRACE_CLOSE_FAILED",result.sha,result.witness);failed.unprovenClose=input;return failed;}
        return result;
    }
    private static ExitTraceCapture readOpen(InputStream input,int osStatus,int pid,int uid,String process,long start,long observed){
        String status="TRACE_OPENING",sha="";TombstoneWitness witness=null;
        try{
            status="TRACE_READING";ByteArrayOutputStream bytes=new ByteArrayOutputStream();byte[] buffer=new byte[4096];int count;
            while((count=input.read(buffer,0,Math.min(buffer.length,262145-bytes.size())))!=-1){if(count==0)throw new IOException("TRACE_ZERO_READ");bytes.write(buffer,0,count);if(bytes.size()>262144)throw new IOException("TRACE_BUDGET");}
            byte[] raw=bytes.toByteArray();StringBuilder hex=new StringBuilder();for(byte b:MessageDigest.getInstance("SHA-256").digest(raw))hex.append(String.format(java.util.Locale.ROOT,"%02x",b&255));sha=hex.toString();
            status="TRACE_PARSE_FAILED";witness=TombstoneWitness.parse(raw);
            return new ExitTraceCapture("TRACE_READ_PARSED",ExitTraceRules.relation(osStatus,pid,uid,process,start,observed,witness),sha,witness);
        }catch(SecurityException error){status="TRACE_PERMISSION_DENIED";}
        catch(IOException error){String code=error.getMessage();status="TRACE_BUDGET".equals(code) || "TRACE_TRUNCATED".equals(code) || "TRACE_LENGTH".equals(code)?"TRACE_TRUNCATED_OR_OVER_BUDGET":status.equals("TRACE_PARSE_FAILED")?"TRACE_PARSE_FAILED":"TRACE_READ_FAILED";}
        catch(Exception error){status="TRACE_READ_FAILED";}
        return new ExitTraceCapture(status,status,sha,witness);
    }
}
