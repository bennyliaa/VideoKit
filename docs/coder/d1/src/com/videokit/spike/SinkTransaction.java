package com.videokit.spike;

import java.io.IOException;

/** Transaction experiment. Successful byte-copy is not an encoder validation. */
public final class SinkTransaction {
    public interface Sink {
        boolean randomWrite();
        void open() throws IOException;
        void write(byte[] data) throws IOException;
        void flush() throws IOException;
        void close() throws IOException;
        boolean validateReopened() throws IOException;
        String markReady() throws IOException;
        void abort() throws IOException;
    }
    private enum State { NEW, WRITING, FINALIZING, READY, READY_UNKNOWN, ABORTED }
    private State state = State.NEW;
    private volatile boolean cancelled;
    private final Object terminal = new Object();
    public void cancel() { synchronized (terminal) { if (state != State.READY) cancelled = true; } }
    public String run(Sink sink, byte[] bytes, boolean needsRandomWrite) throws IOException {
        synchronized (terminal) {
            if (state != State.NEW) throw new IOException("TASK_ALREADY_USED");
            if (needsRandomWrite && !sink.randomWrite()) throw new IOException("OUTPUT_CAPABILITY_UNSUPPORTED");
            state = State.WRITING;
        }
        boolean opened = false;
        boolean readyAttempted = false;
        try {
            checkCancellation();
            // Ownership starts before open: an open failure may leave a partial temporary target.
            opened = true;
            sink.open();
            checkCancellation();
            sink.write(bytes);
            checkCancellation();
            state = State.FINALIZING;
            sink.flush();
            sink.close();
            checkCancellation();
            if (!sink.validateReopened()) throw new IOException("OUTPUT_VALIDATION_FAILED");
            synchronized (terminal) {
                checkCancellation();
                readyAttempted = true;
                String token = sink.markReady();
                state = State.READY;
                return token;
            }
        } catch (IOException | RuntimeException failure) {
            if (readyAttempted) {
                // A remote ready callback may have succeeded before its response was lost.
                // Do not abort or retry with a new handle: query the same task/handle ID first.
                synchronized (terminal) { state = State.READY_UNKNOWN; }
                throw new IOException("OUTPUT_READY_UNKNOWN", failure);
            }
            if (opened) {
                try { sink.close(); } catch (Exception e) { failure.addSuppressed(e); }
                try { sink.abort(); } catch (Exception e) { failure.addSuppressed(e); }
            }
            synchronized (terminal) { state = State.ABORTED; }
            throw failure;
        }
    }
    private void checkCancellation() throws IOException {
        if (cancelled) throw new IOException("CANCELLED");
    }
}
