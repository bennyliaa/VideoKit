package com.videokit.spike.c07;
import androidx.media3.extractor.*;
import java.io.*;
import java.util.*;
import java.util.concurrent.atomic.AtomicLong;

/** JVM boundary tests use controlled Extractor/Input doubles; actual Media3 sniff is device-only. */
public final class C07FormatGuardSelfCheck {
    static int checks;
    static void check(boolean yes,String name){checks++;if(!yes)throw new AssertionError(name);System.out.println("PASS "+name);}
    static class Input implements ExtractorInput {
        final byte[] data;int pos,peek;
        Input(byte[] data){this.data=data;}
        public long getPosition(){return pos;}public long getPeekPosition(){return peek;}public long getLength(){return data.length;}
        public void resetPeekPosition(){peek=pos;}
        public int read(byte[] b,int o,int n){int count=Math.min(n,data.length-pos);if(count==0)return -1;System.arraycopy(data,pos,b,o,count);pos+=count;peek=pos;return count;}
        public boolean readFully(byte[] b,int o,int n,boolean allow)throws IOException{if(pos==data.length && allow)return false;if(data.length-pos<n)throw new EOFException();read(b,o,n);return true;}
        public void readFully(byte[] b,int o,int n)throws IOException{readFully(b,o,n,false);}
        public int skip(int n){int count=Math.min(n,data.length-pos);pos+=count;peek=pos;return count;}
        public boolean skipFully(int n,boolean allow)throws IOException{if(pos==data.length && allow)return false;if(data.length-pos<n)throw new EOFException();skip(n);return true;}
        public void skipFully(int n)throws IOException{skipFully(n,false);}
        public int peek(byte[] b,int o,int n){int count=Math.min(n,data.length-peek);if(count==0)return -1;System.arraycopy(data,peek,b,o,count);peek+=count;return count;}
        public boolean peekFully(byte[] b,int o,int n,boolean allow)throws IOException{if(peek==data.length && allow)return false;if(data.length-peek<n)throw new EOFException();peek(b,o,n);return true;}
        public void peekFully(byte[] b,int o,int n)throws IOException{peekFully(b,o,n,false);}
        public boolean advancePeekPosition(int n,boolean allow)throws IOException{if(peek==data.length && allow)return false;if(data.length-peek<n)throw new EOFException();peek+=n;return true;}
        public void advancePeekPosition(int n)throws IOException{advancePeekPosition(n,false);}
        public <E extends Throwable> void setRetryPosition(long p,E error)throws E{pos=(int)p;peek=pos;throw error;}
    }
    interface Sniffer{boolean run(ExtractorInput in)throws IOException;}
    static final class Actual implements Extractor{
        final Sniffer sniffer;int reads,sniffs,releases;
        Actual(Sniffer sniffer){this.sniffer=sniffer;}
        public boolean sniff(ExtractorInput in)throws IOException{sniffs++;return sniffer.run(in);}
        public void init(ExtractorOutput out){}public int read(ExtractorInput in,PositionHolder seek){reads++;return RESULT_END_OF_INPUT;}
        public void seek(long p,long t){}public void release(){releases++;}
    }
    static IOException reject(FormatGuardExtractor guard,Input input)throws Exception{
        try{guard.read(input,new PositionHolder());throw new AssertionError("expected rejection");}catch(IOException expected){return expected;}
    }
    public static void main(String[] args)throws Exception{
        List<String> events=new ArrayList<>();Actual actual=new Actual(in->{byte[] b=new byte[4];in.peekFully(b,0,4);return Arrays.equals(b,new byte[]{1,2,3,4});});
        Input input=new Input(new byte[]{1,2,3,4});FormatGuardExtractor guard=new FormatGuardExtractor(actual,events::add);
        check(guard.read(input,new PositionHolder())==Extractor.RESULT_END_OF_INPUT,"single-candidate first read reaches delegate only after actual sniff");
        check(actual.sniffs==1 && actual.reads==1 && guard.matches()==1,"match evidence corresponds to actual sniffer call");
        check(input.pos==0 && input.peek==0,"successful peek reset preserves source bytes");
        guard.seek(0,10000000);guard.read(input,new PositionHolder());check(actual.sniffs==1 && actual.reads==2,"same-source seek does not bypass or repeat validation");
        check(events.indexOf("SOURCE_FORMAT_SNIFF_BEGIN")<events.indexOf("SOURCE_FORMAT_SNIFF_MATCH"),"real begin then match events");guard.release();check(actual.releases==1,"delegate release forwarded");
        Actual wrong=new Actual(in->false);FormatGuardExtractor bad=new FormatGuardExtractor(wrong,x->{});IOException cause=reject(bad,new Input(new byte[12]));
        check(cause.getMessage().equals("SOURCE_FORMAT_MISMATCH") && wrong.reads==0,"mismatch denies parser entry");check(reject(bad,new Input(new byte[]{1,2,3,4}))==cause && wrong.sniffs==1,"failed source cannot retry into valid bytes");
        Input shortInput=new Input(new byte[]{1});Actual truncated=new Actual(in->{in.peekFully(new byte[12],0,12);return true;});FormatGuardExtractor shortGuard=new FormatGuardExtractor(truncated,x->{});
        cause=reject(shortGuard,shortInput);check(cause.getCause() instanceof EOFException && truncated.reads==0,"truncated peek rejects with actual EOF cause");check(shortInput.peek==0 && shortInput.pos==0,"failed peek reset");
        Actual greedy=new Actual(in->{in.advancePeekPosition(20000);in.advancePeekPosition(20000);return true;});cause=reject(new FormatGuardExtractor(greedy,x->{}),new Input(new byte[50000]));check(cause.getMessage().equals("SOURCE_FORMAT_SNIFF_BYTE_BUDGET") && greedy.reads==0,"cumulative sniff byte budget blocks oversized probe");
        for(int mode=0;mode<3;mode++){final int m=mode;Actual consumer=new Actual(in->{if(m==0)in.read(new byte[1],0,1);else if(m==1)in.readFully(new byte[1],0,1);else in.skipFully(1);return true;});cause=reject(new FormatGuardExtractor(consumer,x->{}),new Input(new byte[12]));check(cause.getMessage().equals("SOURCE_FORMAT_SNIFF_CONSUMED_INPUT") && consumer.reads==0,"sniff cannot consume input variant "+mode);}
        AtomicLong time=new AtomicLong();Actual slow=new Actual(in->{time.set(6000000000L);return true;});cause=reject(new FormatGuardExtractor(slow,x->{},time::get),new Input(new byte[12]));check(cause.getMessage().equals("SOURCE_FORMAT_SNIFF_TIMEOUT") && slow.reads==0,"late true does not validate after deadline");
        Actual clockProbe=new Actual(in->{time.set(6000000000L);in.peek(new byte[1],0,1);return true;});time.set(0);cause=reject(new FormatGuardExtractor(clockProbe,x->{},time::get),new Input(new byte[12]));check(cause.getMessage().equals("SOURCE_FORMAT_SNIFF_TIMEOUT"),"deadline checked before delegated I/O");
        Actual interrupted=new Actual(in->{in.advancePeekPosition(1);return true;});Thread.currentThread().interrupt();try{cause=reject(new FormatGuardExtractor(interrupted,x->{}),new Input(new byte[12]));check(cause.getMessage().equals("CANCELLED") && interrupted.reads==0,"interrupted probe rejects before input");}finally{Thread.interrupted();}
        Actual originActual=new Actual(in->true);Input shifted=new Input(new byte[12]);shifted.pos=4;cause=reject(new FormatGuardExtractor(originActual,x->{}),shifted);check(cause.getMessage().equals("SOURCE_FORMAT_ORIGIN_REQUIRED") && originActual.sniffs==0,"cannot validate source from non-origin offset");
        Actual invalid=new Actual(in->{throw new IllegalArgumentException("private media path");});cause=reject(new FormatGuardExtractor(invalid,x->{}),new Input(new byte[12]));check(cause.getMessage().equals("SOURCE_FORMAT_INVALID") && invalid.reads==0,"runtime sniffer failure has stable redacted outer code");
        time.set(0);Input slowShort=new Input(new byte[32]){public int peek(byte[] b,int o,int n){time.addAndGet(2000000000L);return super.peek(b,o,Math.min(n,1));}};
        Actual shortReads=new Actual(in->{in.peekFully(new byte[12],0,12);return true;});cause=reject(new FormatGuardExtractor(shortReads,x->{},time::get),slowShort);check(cause.getMessage().equals("SOURCE_FORMAT_SNIFF_TIMEOUT") && shortReads.reads==0,"deadline enforced between underlying short reads");
        Actual zeroRead=new Actual(in->{in.peekFully(new byte[1],0,1);return true;});cause=reject(new FormatGuardExtractor(zeroRead,x->{}),new Input(new byte[12]){public int peek(byte[] b,int o,int n){return 0;}});check(cause.getMessage().equals("SOURCE_FORMAT_NO_PROGRESS"),"zero progress does not spin");
        CaptureFormatEvidence proof=new CaptureFormatEvidence();check(!proof.allMatched(),"absence of sniff is not proof");proof.record("SOURCE_FORMAT_SNIFF_BEGIN");check(!proof.allMatched(),"begin alone cannot pass");proof.record("SOURCE_FORMAT_SNIFF_MATCH");check(proof.allMatched(),"matched actual attempt can pass per-capture evidence");proof.record("SOURCE_FORMAT_SNIFF_BEGIN");check(!proof.allMatched(),"second unfinished input blocks evidence");proof.record("SOURCE_FORMAT_SNIFF_MATCH");proof.record("SOURCE_FORMAT_REJECTED");check(!proof.allMatched(),"rejection remains visible despite other matches");
        System.out.println("RESULT c07_format_guard_assertions="+checks+" failures=0 actual_Media3_fixture_sniff=DEVICE_NOT_RUN");
    }
}
