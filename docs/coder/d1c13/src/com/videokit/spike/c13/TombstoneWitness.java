package com.videokit.spike.c13;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
/** Independently authored bounded reader for the public AOSP tombstone protobuf fields.
 * Never retains raw process names, frames, file paths or arbitrary abort text. */
public final class TombstoneWitness {
    public final int pid,uid,signal;public final String cause,process,timestamp;
    private TombstoneWitness(int pid,int uid,int signal,String cause,String process,String timestamp){this.pid=pid;this.uid=uid;this.signal=signal;this.cause=cause;this.process=process;this.timestamp=timestamp;}
    private static final class Cursor {
        final byte[] data;final int end;int pos;
        Cursor(byte[] data,int start,int end){this.data=data;this.pos=start;this.end=end;}
        long varint()throws IOException{long value=0;for(int i=0;i<10;i++){if(pos>=end)throw new IOException("TRACE_TRUNCATED");int b=data[pos++]&255;if(i==9 && b>1)throw new IOException("TRACE_VARINT");value|=(long)(b&127)<<(i*7);if((b&128)==0)return value;}throw new IOException("TRACE_VARINT");}
        int length()throws IOException{long value=varint();if(value<0 || value>end-pos)throw new IOException("TRACE_LENGTH");return (int)value;}
        void skip(int wire)throws IOException{int n;if(wire==0){varint();return;}if(wire==1)n=8;else if(wire==5)n=4;else if(wire==2)n=length();else throw new IOException("TRACE_WIRE");if(n>end-pos)throw new IOException("TRACE_LENGTH");pos+=n;}
    }
    public static TombstoneWitness parse(byte[] bytes)throws IOException{
        if(bytes.length==0 || bytes.length>262144)throw new IOException("TRACE_BUDGET");Cursor c=new Cursor(bytes,0,bytes.length);int pid=-1,uid=-1,signal=-1,fields=0;String cause="UNKNOWN",process="",timestamp="";boolean signalField=false,abortField=false;
        while(c.pos<c.end){if(++fields>4096)throw new IOException("TRACE_FIELDS");long key=c.varint();int field=(int)(key>>>3),wire=(int)(key&7);if(field<1)throw new IOException("TRACE_FIELD");
            if((field==5 || field==7) && wire==0){long v=c.varint();if(v>Integer.MAX_VALUE || v<0)throw new IOException("TRACE_IDENTITY");if(field==5){if(pid!=-1)throw new IOException("TRACE_DUPLICATE");pid=(int)v;}else{if(uid!=-1)throw new IOException("TRACE_DUPLICATE");uid=(int)v;}}
            else if((field==4 || field==9) && wire==2){int len=c.length();if(len>(field==4?64:512))throw new IOException("TRACE_TEXT_BUDGET");String text=StandardCharsets.UTF_8.newDecoder().onMalformedInput(java.nio.charset.CodingErrorAction.REPORT).decode(java.nio.ByteBuffer.wrap(bytes,c.pos,len)).toString();c.pos+=len;
                if(field==4){if(!timestamp.isEmpty())throw new IOException("TRACE_DUPLICATE");timestamp=text;}else{if(!process.isEmpty())throw new IOException("TRACE_MULTIPLE_COMMAND_LINES");process=text;}}
            else if(field==10 && wire==2){if(signalField)throw new IOException("TRACE_DUPLICATE");signalField=true;int len=c.length();Cursor s=new Cursor(bytes,c.pos,c.pos+len);int count=0;while(s.pos<s.end){if(++count>64)throw new IOException("TRACE_FIELDS");long k=s.varint();if(k==8){long v=s.varint();if(signal!=-1 || v<0 || v>64)throw new IOException("TRACE_SIGNAL");signal=(int)v;}else {if(k>>>3==0)throw new IOException("TRACE_FIELD");s.skip((int)(k&7));}}c.pos+=len;}
            else if(field==14 && wire==2){if(abortField)throw new IOException("TRACE_DUPLICATE");abortField=true;int len=c.length();if(len>2048)throw new IOException("TRACE_ABORT_BUDGET");String text=new String(bytes,c.pos,len,StandardCharsets.UTF_8);c.pos+=len;
                if(text.contains("Binder driver could not be opened"))cause="BINDER_DRIVER_OPEN_FATAL";
            }else {if(field==4 || field==5 || field==7 || field==9 || field==10 || field==14)throw new IOException("TRACE_WIRE");c.skip(wire);}
        }
        return new TombstoneWitness(pid,uid,signal,cause,process,timestamp);
    }
    public boolean matches(int expectedPid,int expectedUid){return pid==expectedPid && uid==expectedUid;}
}
