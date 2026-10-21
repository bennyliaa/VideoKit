package com.videokit.spike.c08;
import androidx.media3.extractor.*;
import java.io.IOException;
import java.util.function.Consumer;
import java.util.function.LongSupplier;
import java.util.concurrent.TimeUnit;

/** Explicit first-read validation even when Media3's single-extractor selection skips sniff. */
public final class FormatGuardExtractor implements Extractor {
    public static final int MAX_SNIFF_BYTES=32768;
    private final Extractor actual;private final Consumer<String> events;private final LongSupplier clock;
    private boolean validated;private IOException rejected;private int attempts,matches;
    public FormatGuardExtractor(Extractor actual,Consumer<String> events){this(actual,events,System::nanoTime);}
    FormatGuardExtractor(Extractor actual,Consumer<String> events,LongSupplier clock){this.actual=java.util.Objects.requireNonNull(actual);this.events=java.util.Objects.requireNonNull(events);this.clock=clock;}
    public int attempts(){return attempts;}public int matches(){return matches;}
    public boolean validated(){return validated;}
    public boolean sniff(ExtractorInput input)throws IOException{
        if(rejected!=null)throw rejected;if(validated)return true;
        long position=input.getPosition();if(position!=0)throw remember("SOURCE_FORMAT_ORIGIN_REQUIRED",null);
        input.resetPeekPosition();long start=clock.getAsLong();attempts++;events.accept("SOURCE_FORMAT_SNIFF_BEGIN");
        try{
            boolean yes=actual.sniff(new ForwardingExtractorInput(input){
                long used;
                private void deadline()throws IOException{
                    if(Thread.currentThread().isInterrupted())throw new IOException("CANCELLED");
                    if(clock.getAsLong()-start>TimeUnit.SECONDS.toNanos(5))throw new IOException("SOURCE_FORMAT_SNIFF_TIMEOUT");
                }
                private void reserve(int length)throws IOException{
                    if(length<0 || length>MAX_SNIFF_BYTES-used)throw new IOException("SOURCE_FORMAT_SNIFF_BYTE_BUDGET");
                    deadline();used+=length;
                }
                // Sniff must peek, never consume or reposition the input.
                public int read(byte[] b,int o,int n)throws IOException{throw new IOException("SOURCE_FORMAT_SNIFF_CONSUMED_INPUT");}
                public boolean readFully(byte[] b,int o,int n,boolean allow)throws IOException{throw new IOException("SOURCE_FORMAT_SNIFF_CONSUMED_INPUT");}
                public void readFully(byte[] b,int o,int n)throws IOException{throw new IOException("SOURCE_FORMAT_SNIFF_CONSUMED_INPUT");}
                public int skip(int n)throws IOException{throw new IOException("SOURCE_FORMAT_SNIFF_CONSUMED_INPUT");}
                public boolean skipFully(int n,boolean allow)throws IOException{throw new IOException("SOURCE_FORMAT_SNIFF_CONSUMED_INPUT");}
                public void skipFully(int n)throws IOException{throw new IOException("SOURCE_FORMAT_SNIFF_CONSUMED_INPUT");}
                public int peek(byte[] b,int o,int n)throws IOException{reserve(n);int result=super.peek(b,o,n);deadline();if(result==0 && n>0)throw new IOException("SOURCE_FORMAT_NO_PROGRESS");return result;}
                public boolean peekFully(byte[] b,int o,int n,boolean allow)throws IOException{
                    reserve(n);int done=0;
                    while(done<n){deadline();int result=super.peek(b,o+done,n-done);deadline();
                        if(result==-1){if(done==0 && allow)return false;throw new java.io.EOFException();}
                        if(result<=0 || result>n-done)throw new IOException("SOURCE_FORMAT_NO_PROGRESS");done+=result;}
                    return true;
                }
                public void peekFully(byte[] b,int o,int n)throws IOException{peekFully(b,o,n,false);}
                public boolean advancePeekPosition(int n,boolean allow)throws IOException{
                    if(n<0 || n>MAX_SNIFF_BYTES-used)throw new IOException("SOURCE_FORMAT_SNIFF_BYTE_BUDGET");
                    byte[] scratch=new byte[Math.min(1024,n)];int done=0;
                    while(done<n){int count=Math.min(scratch.length,n-done);if(!peekFully(scratch,0,count,allow && done==0))return false;done+=count;}return true;
                }
                public void advancePeekPosition(int n)throws IOException{advancePeekPosition(n,false);}
                public <E extends Throwable> void setRetryPosition(long p,E error)throws E{throw error;}
            });
            if(clock.getAsLong()-start>TimeUnit.SECONDS.toNanos(5))throw new IOException("SOURCE_FORMAT_SNIFF_TIMEOUT");
            if(input.getPosition()!=position)throw new IOException("SOURCE_FORMAT_SNIFF_CONSUMED_INPUT");
            events.accept(yes?"SOURCE_FORMAT_SNIFF_MATCH":"SOURCE_FORMAT_SNIFF_MISMATCH");
            if(yes){validated=true;matches++;}else rejected=new IOException("SOURCE_FORMAT_MISMATCH");return yes;
        }catch(IOException error){throw remember(error.getMessage()!=null && error.getMessage().matches("[A-Z_0-9]+")?error.getMessage():"SOURCE_FORMAT_TRUNCATED_OR_INVALID",error);}
        catch(RuntimeException error){throw remember("SOURCE_FORMAT_INVALID",error);}
        finally{input.resetPeekPosition();events.accept("SOURCE_FORMAT_PEEK_RESET");}
    }
    private IOException remember(String code,Throwable cause){rejected=new IOException(code,cause);events.accept("SOURCE_FORMAT_REJECTED");return rejected;}
    public void init(ExtractorOutput out){actual.init(out);}
    public int read(ExtractorInput input,PositionHolder seek)throws IOException{
        if(rejected!=null)throw rejected;if(!validated && !sniff(input))throw rejected;
        return actual.read(input,seek);
    }
    public void seek(long position,long timeUs){actual.seek(position,timeUs);}
    public void release(){actual.release();}
}
