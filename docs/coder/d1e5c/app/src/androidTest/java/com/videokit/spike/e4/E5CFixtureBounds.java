package com.videokit.spike.e4;

/** Fixed, independent fixture accounting. Never accepts a caller supplied path or budget. */
public final class E5CFixtureBounds {
    public static final int NODES=64, DATA=256*1024, FILE=64*1024, LOG=4*1024*1024;
    public static final long DEADLINE_NS=60_000_000_000L;
    private int nodes; private long bytes;
    public void add(long size) {
        if(size<0 || size>FILE || nodes>=NODES || bytes>DATA-size)throw new IllegalStateException("E5C_FIXTURE_BOUND");
        nodes++;bytes+=size;
    }
    public int nodes(){return nodes;} public long bytes(){return bytes;}
    public static void deadline(long start,long now){if(now-start>=DEADLINE_NS)throw new IllegalStateException("E5C_DEADLINE_PENDING");}
}
