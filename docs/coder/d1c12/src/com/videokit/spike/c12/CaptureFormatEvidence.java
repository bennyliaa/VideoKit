package com.videokit.spike.c12;
import java.util.concurrent.atomic.AtomicInteger;
/** Per-capture evidence, never a global counter or a product READY decision. */
public final class CaptureFormatEvidence {
    private final AtomicInteger starts=new AtomicInteger(),matches=new AtomicInteger(),rejects=new AtomicInteger();
    public void record(String stage){if(stage.equals("SOURCE_FORMAT_SNIFF_BEGIN"))starts.incrementAndGet();else if(stage.equals("SOURCE_FORMAT_SNIFF_MATCH"))matches.incrementAndGet();else if(stage.equals("SOURCE_FORMAT_REJECTED") || stage.equals("SOURCE_FORMAT_SNIFF_MISMATCH"))rejects.incrementAndGet();}
    public boolean allMatched(){return starts.get()>0 && matches.get()==starts.get() && rejects.get()==0;}
    public int starts(){return starts.get();}public int matches(){return matches.get();}public int rejects(){return rejects.get();}
}
