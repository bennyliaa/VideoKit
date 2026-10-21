package com.videokit.spike;

import java.io.IOException;
import java.util.Objects;

/** D1 synchronous worker-thread prototype; not the frozen public suspend API. */
public final class ReadBridge implements AutoCloseable {
    public interface Handle extends AutoCloseable {
        Long length();
        int readAt(long position, byte[] buffer, int offset, int length) throws IOException;
        /** Must interrupt transport I/O and be idempotent; no UI-thread dependency. */
        void close() throws IOException;
    }
    private final Handle handle;
    private boolean closed;
    private int active;
    private long position;
    private long remaining = -1;
    public ReadBridge(Handle handle) { this.handle = Objects.requireNonNull(handle); }
    public synchronized long open(long offset, long requested) throws IOException {
        if (closed) throw new IOException("SESSION_RELEASED");
        if (active != 0) throw new IOException("READ_IN_FLIGHT");
        if (offset < 0 || requested < -1) throw new IOException("INVALID_RANGE");
        Long size = handle.length();
        if (size != null && (size < 0 || offset > size)) throw new IOException("INVALID_RANGE");
        position = offset;
        remaining = requested;
        if (size != null) remaining = requested < 0 ? size - offset : Math.min(requested, size - offset);
        return remaining;
    }
    public int read(byte[] target, int offset, int length) throws IOException {
        Objects.checkFromIndexSize(offset, length, target.length);
        final long at;
        final int count;
        synchronized (this) {
            if (closed) throw new IOException("SESSION_RELEASED");
            if (length == 0) return 0;
            if (remaining == 0) return -1;
            if (active != 0) throw new IOException("READ_IN_FLIGHT");
            count = (int)Math.min(Math.min(length, 65536), remaining < 0 ? Long.MAX_VALUE : remaining);
            at = position;
            active++;
        }
        // Private buffer prevents a stale completion from modifying caller memory.
        byte[] temporary = new byte[count];
        try {
            int n = handle.readAt(at, temporary, 0, count);
            synchronized (this) {
                if (closed) throw new IOException("CANCELLED");
                if (n < -1 || n == 0 || n > count) throw new IOException("INVALID_READ_RESULT");
                if (n > 0) {
                    long next;
                    try { next = Math.addExact(position, n); }
                    catch (ArithmeticException e) { throw new IOException("INVALID_RANGE"); }
                    System.arraycopy(temporary, 0, target, offset, n);
                    position = next;
                    if (remaining >= 0) remaining -= n;
                }
                return n;
            }
        } finally {
            synchronized (this) { active--; notifyAll(); }
        }
    }
    public void close() throws IOException {
        synchronized (this) { if (closed) return; closed = true; }
        handle.close();
    }
    public synchronized boolean awaitDrained(long timeoutMs) throws InterruptedException {
        long deadline = System.nanoTime() + timeoutMs * 1000000;
        while (active != 0) {
            long left = deadline - System.nanoTime();
            if (left <= 0) return false;
            wait(Math.max(1, left / 1000000));
        }
        return true;
    }
}
