package com.videokit.fixturetool;

import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.channels.NonReadableChannelException;
import java.util.Map;
import java.util.List;
import java.util.ArrayList;
import org.jcodec.common.io.SeekableByteChannel;

/** A budget adapter, not an isolation boundary. Only the original generation
 * worker may invoke the actual native channel. No retry after an uncertain call. */
final class AttemptBudgetChannel implements SeekableByteChannel {
    static final long MAX_ATTEMPT = 16L * 1024 * 1024;
    static final int BLOCK = 65536;
    private final SixFrameDriver.Job owner;
    private long attempted, acknowledged, rewriteAttempted, nativeCalls, partialCalls;
    private long logicalPosition, highWater, positionCalls, positionReturns, extent;
    private int inFlight, peak;
    private boolean failed;
    private boolean physicalPositionUnknown;
    private final List<Map<String,Object>> events = new ArrayList<>();

    AttemptBudgetChannel(SixFrameDriver.Job owner) { this.owner = owner; }

    private void admitted() throws IOException {
        owner.requireOriginalWorker();
        owner.checkAdmission();
        if (failed || !owner.writer.usable()) throw new IOException("WRITER_NOT_ADMITTED");
    }

    @Override public int write(ByteBuffer source) throws IOException {
        admitted();
        if (source == null) throw new IOException("NULL_WRITE");
        int total = 0;
        while (source.hasRemaining()) {
            admitted();
            int count = Math.min(BLOCK, source.remaining());
            int sourcePositionBefore = source.position();
            ByteBuffer part = source.slice(); part.limit(count);
            Map<String,Object> event;
            synchronized (this) {
                if (inFlight != 0 || events.size() >= 512 || attempted > MAX_ATTEMPT - count
                        || logicalPosition > MAX_ATTEMPT - count) {
                    failed = true; owner.fail("OUTPUT_ATTEMPT_OR_RANGE_LIMIT");
                    throw new IOException("OUTPUT_ATTEMPT_OR_RANGE_LIMIT");
                }
                // Charge each native attempt BEFORE the call, including rewrites
                // and the unacknowledged suffix of a partial/throwing write.
                attempted += count;
                if (logicalPosition < highWater) rewriteAttempted += count;
                nativeCalls++; inFlight = 1; peak = Math.max(peak, inFlight);
                event = ReceiptJson.map("nativeCall",nativeCalls,"requestedAndReserved",count,"attemptedCumulative",attempted,
                    "knownReturnedBefore",acknowledged,"lastKnownPositionBefore",logicalPosition,
                    "sourceBufferPositionBefore",sourcePositionBefore,"outcome","ENTERED_UNRETURNED");
                events.add(event);
            }
            int returned;
            try {
                returned = owner.writer.writeOnce(part);
                if (returned < 1 || returned > count || part.position() != returned) {
                    throw new IOException("NATIVE_WRITE_INVALID_OR_ZERO_PROGRESS");
                }
                source.position(source.position() + returned);
                total += returned;
                synchronized (this) {
                    acknowledged += returned; logicalPosition += returned;
                    highWater = Math.max(highWater, logicalPosition);
                    extent = Math.max(extent, logicalPosition);
                    if (returned < count) partialCalls++;
                    event.put("outcome","VALID_NATIVE_RETURN");event.put("returned",returned);
                    event.put("sourceBufferPositionAfter",source.position());event.put("knownReturnedAfter",acknowledged);
                    event.put("knownPositionAfter",logicalPosition);event.put("knownExtentAfter",extent);
                }
            } catch (Throwable error) {
                synchronized (this) { failed = true;physicalPositionUnknown=true;event.put("outcome","PHYSICAL_AMOUNT_AND_POSITION_UNKNOWN"); }
                owner.fail("NATIVE_WRITE_FAILED_OR_UNKNOWN");
                throw new IOException("NATIVE_WRITE_FAILED_OR_UNKNOWN", error);
            } finally {
                synchronized (this) { inFlight = 0; }
            }
        }
        // JCodec's constructor/header writes may issue one write call and assume
        // consumption. Internally drain partial native writes, without refunding
        // their already charged suffix, instead of silently losing header bytes.
        return total;
    }

    @Override public int read(ByteBuffer destination) throws IOException {
        throw new NonReadableChannelException();
    }
    @Override public long position() throws IOException {
        admitted();
        long actual;
        try { actual = owner.writer.position(); }
        catch(Throwable error){synchronized(this){failed=true;physicalPositionUnknown=true;}owner.fail("NATIVE_POSITION_UNKNOWN");throw new IOException("NATIVE_POSITION_UNKNOWN",error);}
        if (actual != logicalPosition) { synchronized(this){failed=true;physicalPositionUnknown=true;}owner.fail("POSITION_MISMATCH"); throw new IOException("POSITION_MISMATCH"); }
        return actual;
    }
    @Override public SeekableByteChannel setPosition(long position) throws IOException {
        admitted();
        if (position < 0 || position > MAX_ATTEMPT) throw new IOException("SEEK_RANGE");
        synchronized (this) { positionCalls++; }
        try { owner.writer.position(position); }
        catch (Throwable error) {
            synchronized (this) { failed = true;physicalPositionUnknown=true; }
            owner.fail("NATIVE_SEEK_UNKNOWN"); throw new IOException("NATIVE_SEEK_UNKNOWN",error);
        }
        synchronized (this) { logicalPosition = position; positionReturns++; }
        return this;
    }
    @Override public long size() throws IOException {
        admitted(); return owner.writer.size();
    }
    @Override public SeekableByteChannel truncate(long ignored) throws IOException {
        throw new IOException("TRUNCATE_NOT_ADMITTED");
    }
    @Override public boolean isOpen() { return owner.writer.usable(); }
    @Override public void close() throws IOException {
        // No library close grants ownership transfer; this is the SAME guarded
        // original close used by the worker's finally, never a second native close.
        owner.requireOriginalWorker(); owner.writer.closeOriginalOnce();
    }
    synchronized Map<String,Object> receipt(boolean includeEvents) {
        Map<String,Object> result=ReceiptJson.map("attemptedBytes", attempted, "acknowledgedLowerBound", acknowledged,
            "headerOrOtherRewriteAttemptedBytes", rewriteAttempted, "nativeWriteCalls", nativeCalls,
            "partialNativeCalls", partialCalls, "nativeInFlight", inFlight, "peakNativeInFlight", peak,
            "queued", 0, "lastAcknowledgedLogicalPosition", logicalPosition, "actualPhysicalPosition", physicalPositionUnknown?"UNKNOWN":logicalPosition, "actualPhysicalExtent", physicalPositionUnknown?"UNKNOWN":extent, "highestAcknowledgedPosition", highWater,
            "acknowledgedExtentLowerBound", extent, "seekCallsAttempted", positionCalls, "seekCallsReturned", positionReturns,
            "failedOrUncertain", failed, "budgetRefundedBytes", 0);
        if(includeEvents)result.put("nativeWriteEvents",new ArrayList<>(events));
        return result;
    }
}
