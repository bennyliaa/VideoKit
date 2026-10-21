package com.videokit.fixturetool;
import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.channels.NonReadableChannelException;
import java.util.*;
import org.jcodec.common.io.SeekableByteChannel;

/** Same original worker/port. Native return and result adoption are distinct. */
final class AttemptBudgetChannel implements SeekableByteChannel {
    static final long MAX_ATTEMPT=16L*1024*1024;
    static final int BLOCK=65536, EVENT_MAX=512;
    interface NativePort {
        int nativeWrite(ByteBuffer b)throws IOException;
        long nativePosition()throws IOException;
        void nativeSeek(long n)throws IOException;
        long nativeSize()throws IOException;
        void nativeForce()throws IOException;
        void nativeCloseOnce()throws IOException;
        boolean nativeUsable();
        boolean originalReturned();
    }
    interface Owner {
        void requireOriginalWorker()throws IOException;
        void checkAdmission()throws IOException;
        void fail(String code);
        NativePort nativePort();
        /** Production no-op; controlled original callback tail in non-media checks. */
        default void afterNativeReturn(String operation)throws IOException { }
    }
    private final Owner owner;
    private final long initialMeterOnlyReservation;
    private long attempted,acknowledged,rewriteAttempted,nativeCalls,nativeReturns,adoptions,throwsCount;
    private long logicalPosition,highWater,extent,seekAttempts,seekReturns;
    private int inFlight,pendingAdoption,peak;
    private boolean failed,physicalUnknown,closeAttempted,closed,forceAdopted;
    private String activeOperation="NONE";
    private final List<Map<String,Object>> events=new ArrayList<>();
    private Map<String,Object> closeEvent;
    AttemptBudgetChannel(Owner owner){this(owner,0);}
    /** Conservative meter seam: prior reserved budget is not reported as I/O.
     * Production constructs with0; checks can exercise16MiB without allocating it. */
    AttemptBudgetChannel(Owner owner,long priorReserved){
        if(owner==null||priorReserved<0||priorReserved>MAX_ATTEMPT)throw new IllegalArgumentException("METER_RANGE");
        this.owner=owner;attempted=priorReserved;initialMeterOnlyReservation=priorReserved;
    }
    private void admitted()throws IOException {
        owner.requireOriginalWorker();owner.checkAdmission();
        synchronized(this){if(failed||closed||!owner.nativePort().nativeUsable())throw new IOException("WRITER_NOT_ADMITTED");}
    }
    private synchronized Map<String,Object> begin(String op,int request)throws IOException {
        if(inFlight!=0||pendingAdoption!=0||events.size()>=EVENT_MAX)throw rejection("OPERATION_OR_EVENT_CAP");
        if(request<0||request>BLOCK||attempted>MAX_ATTEMPT-request||logicalPosition>MAX_ATTEMPT-request)throw rejection("OUTPUT_ATTEMPT_OR_RANGE_LIMIT");
        if(request>0){attempted+=request;if(logicalPosition<highWater)rewriteAttempted+=request;}
        activeOperation=op;inFlight=1;pendingAdoption=1;peak=Math.max(peak,inFlight);nativeCalls++;
        Map<String,Object> event=ReceiptJson.map("operation",op,"nativeCall",nativeCalls,"requestedAndReserved",request,
            "attemptedCumulative",attempted,"knownReturnedBefore",acknowledged,"lastAcknowledgedPositionBefore",logicalPosition,"outcome","ENTERED_UNRETURNED");
        events.add(event);return event;
    }
    private IOException rejection(String code){failed=true;owner.fail(code);return new IOException(code);}
    private synchronized void returned(Map<String,Object> event){nativeReturns++;inFlight=0;event.put("outcome","NATIVE_RETURN_OBSERVED_ADOPTION_PENDING");}
    private synchronized void adopted(Map<String,Object> event){adoptions++;pendingAdoption=0;activeOperation="NONE";event.put("outcome","RESULT_ADOPTED");}
    private IOException uncertain(Map<String,Object> event,Throwable error,boolean ret){
        synchronized(this){failed=true;physicalUnknown=true;inFlight=0;pendingAdoption=0;activeOperation="NONE";
            if(!ret)throwsCount++;event.put("outcome",ret?"ADOPTION_FAILED_PHYSICAL_UNKNOWN":"NATIVE_THROW_PHYSICAL_UNKNOWN");}
        owner.fail("NATIVE_OR_ADOPTION_UNKNOWN");return new IOException("NATIVE_OR_ADOPTION_UNKNOWN",error);
    }
    @Override public int write(ByteBuffer source)throws IOException {
        admitted();if(source==null)throw new IOException("NULL_WRITE");int total=0;
        while(source.hasRemaining()){
            admitted();int count=Math.min(BLOCK,source.remaining()),before=source.position();ByteBuffer part=source.slice();part.limit(count);
            Map<String,Object> event=begin("WRITE",count);boolean ret=false;
            try{
                int n=owner.nativePort().nativeWrite(part);ret=true;returned(event);owner.afterNativeReturn("WRITE");
                synchronized(this){
                    if(n<1||n>count||part.position()!=n)throw new IOException("INVALID_OR_ZERO_WRITE");
                    source.position(before+n);total+=n;acknowledged+=n;logicalPosition+=n;highWater=Math.max(highWater,logicalPosition);extent=Math.max(extent,logicalPosition);
                    event.put("returned",n);event.put("sourceBufferPositionBefore",before);event.put("sourceBufferPositionAfter",source.position());
                    event.put("knownReturnedAfter",acknowledged);event.put("knownPositionAfter",logicalPosition);event.put("knownExtentAfter",extent);adopted(event);
                }
            }catch(Throwable error){throw uncertain(event,error,ret);}
        }
        return total;
    }
    @Override public long position()throws IOException {
        admitted();Map<String,Object> e=begin("POSITION",0);boolean ret=false;
        try{long n=owner.nativePort().nativePosition();ret=true;returned(e);owner.afterNativeReturn("POSITION");synchronized(this){if(n!=logicalPosition)throw new IOException("POSITION_MISMATCH");adopted(e);}return n;}
        catch(Throwable error){throw uncertain(e,error,ret);}
    }
    @Override public SeekableByteChannel setPosition(long n)throws IOException {
        admitted();if(n<0||n>MAX_ATTEMPT)throw new IOException("SEEK_RANGE");Map<String,Object> e=begin("SEEK",0);boolean ret=false;
        synchronized(this){seekAttempts++;}
        try{owner.nativePort().nativeSeek(n);ret=true;returned(e);owner.afterNativeReturn("SEEK");synchronized(this){logicalPosition=n;seekReturns++;adopted(e);}return this;}
        catch(Throwable error){throw uncertain(e,error,ret);}
    }
    @Override public long size()throws IOException {
        admitted();Map<String,Object> e=begin("SIZE",0);boolean ret=false;
        try{long n=owner.nativePort().nativeSize();ret=true;returned(e);owner.afterNativeReturn("SIZE");synchronized(this){if(n<0||n>MAX_ATTEMPT)throw new IOException("SIZE_RANGE");e.put("nativeSize",n);adopted(e);}return n;}
        catch(Throwable error){throw uncertain(e,error,ret);}
    }
    void forceOriginal()throws IOException {
        admitted();Map<String,Object> e=begin("FORCE",0);boolean ret=false;
        try{owner.nativePort().nativeForce();ret=true;returned(e);owner.afterNativeReturn("FORCE");synchronized(this){forceAdopted=true;adopted(e);}}
        catch(Throwable error){throw uncertain(e,error,ret);}
    }
    @Override public void close()throws IOException {
        owner.requireOriginalWorker();
        synchronized(this){if(closeAttempted||closed)return;closeAttempted=true;}
        Map<String,Object> e;
        synchronized(this){
            if(inFlight!=0||pendingAdoption!=0){physicalUnknown=true;owner.fail("ORIGINAL_OPERATION_PENDING");throw new IOException("ORIGINAL_OPERATION_PENDING");}
            // Original cleanup cannot be denied by the512 admission-event cap.
            // Exactly one bounded terminal record, no second native close.
            activeOperation="CLOSE";inFlight=1;pendingAdoption=1;peak=Math.max(peak,inFlight);nativeCalls++;
            e=ReceiptJson.map("operation","CLOSE","nativeCall",nativeCalls,"outcome","ENTERED_UNRETURNED");closeEvent=e;
        }
        boolean ret=false;
        try{owner.nativePort().nativeCloseOnce();ret=true;returned(e);owner.afterNativeReturn("CLOSE");synchronized(this){if(!owner.nativePort().originalReturned())throw new IOException("ORIGINAL_CLOSE_UNKNOWN");closed=true;adopted(e);}}
        catch(Throwable error){throw uncertain(e,error,ret);}
    }
    @Override public int read(ByteBuffer data)throws IOException {throw new NonReadableChannelException();}
    @Override public SeekableByteChannel truncate(long n)throws IOException {throw new IOException("TRUNCATE_NOT_ADMITTED");}
    @Override public boolean isOpen(){return owner.nativePort().nativeUsable();}
    synchronized Map<String,Object> receipt(boolean includeEvents){
        boolean unresolved=inFlight!=0||pendingAdoption!=0;
        Map<String,Object> r=ReceiptJson.map("attemptedBytes",attempted,"initialMeterOnlyReservation",initialMeterOnlyReservation,"acknowledgedLowerBound",acknowledged,
            "headerOrOtherRewriteAttemptedBytes",rewriteAttempted,"nativeCallsEntered",nativeCalls,"nativeReturnsObserved",nativeReturns,"resultsAdopted",adoptions,
            "nativeThrowsObserved",throwsCount,"nativeInFlight",inFlight,"resultAdoptionPending",pendingAdoption,"activeOperation",activeOperation,
            "peakNativeInFlight",peak,"queued",0,"lastAcknowledgedLogicalPosition",logicalPosition,"acknowledgedExtentLowerBound",extent,
            "actualPhysicalPosition",physicalUnknown||unresolved?"UNKNOWN":logicalPosition,"actualPhysicalExtent",physicalUnknown||unresolved?"UNKNOWN":extent,
            "physicalValueScope",closed?"LAST_CONFIRMED_BEFORE_ORIGINAL_CLOSE":"CURRENT_ONLY_IF_NO_UNRESOLVED_OPERATION",
            "seekCallsAttempted",seekAttempts,"seekResultsAdopted",seekReturns,"forceResultAdopted",forceAdopted,"originalCloseResultAdopted",closed,
            "failedOrUncertain",failed,"physicalUnknownSticky",physicalUnknown,"budgetRefundedBytes",0);
        if(includeEvents&&!unresolved){List<Map<String,Object>> copies=new ArrayList<>();for(Map<String,Object> e:events)copies.add(new LinkedHashMap<>(e));r.put("nativeOperationEvents",copies);if(closeEvent!=null)r.put("terminalCloseEvent",new LinkedHashMap<>(closeEvent));}
        else if(includeEvents)r.put("eventsSuppressedWhilePending",true);
        return r;
    }
}
