package com.videokit.spike.c05;
import android.net.Uri;
import androidx.media3.extractor.*;
import java.io.IOException;
import java.util.*;
import java.util.concurrent.TimeUnit;
/** Cooperative extractor-stage budget. Cannot interrupt a stuck native/CPU call; source cancellation and outer deadlines are separate. */
public final class TracingExtractors implements ExtractorsFactory {
    private final DefaultExtractorsFactory actual=new DefaultExtractorsFactory();
    public Extractor[] createExtractors(){return wrap(actual.createExtractors());}
    public Extractor[] createExtractors(Uri uri,Map<String,List<String>> headers){return wrap(actual.createExtractors(uri,headers));}
    private Extractor[] wrap(Extractor[] all){for(int i=0;i<all.length;i++){Extractor ex=all[i];all[i]=new Extractor(){
        long start=System.nanoTime(),reads;
        private void budget()throws IOException{if(Thread.currentThread().isInterrupted() || System.nanoTime()-start>TimeUnit.SECONDS.toNanos(30))throw new IOException("EXTRACTOR_STAGE_TIMEOUT");}
        public boolean sniff(ExtractorInput in)throws IOException{String name=ex.getClass().getSimpleName();StageLog.event("EXTRACTOR_SNIFF_BEGIN",name);budget();try{boolean yes=ex.sniff(in);StageLog.event("EXTRACTOR_SNIFF_END",name+" matched="+yes);return yes;}catch(IOException|RuntimeException e){StageLog.failure("EXTRACTOR_SNIFF_FAILED",e);throw e;}}
        public void init(ExtractorOutput output){StageLog.event("EXTRACTOR_INIT",ex.getClass().getSimpleName());ex.init(output);}
        public int read(ExtractorInput in,PositionHolder seek)throws IOException{budget();if(++reads==1 || reads%128==0)StageLog.event("EXTRACTOR_READ",ex.getClass().getSimpleName()+" count="+reads+" offset="+in.getPosition());try{int result=ex.read(in,seek);budget();return result;}catch(IOException|RuntimeException e){StageLog.failure("EXTRACTOR_READ_FAILED",e);throw e;}}
        public void seek(long position,long timeUs){start=System.nanoTime();reads=0;StageLog.event("EXTRACTOR_SEEK", "offset="+position+" pts_us="+timeUs);ex.seek(position,timeUs);}
        public void release(){StageLog.event("EXTRACTOR_RELEASE",ex.getClass().getSimpleName());ex.release();}
    };}return all;}
}
