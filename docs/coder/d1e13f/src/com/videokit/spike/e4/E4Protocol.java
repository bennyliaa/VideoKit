package com.videokit.spike.e4;

import java.io.IOException;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.Locale;

/** Finite raw-frame wire contract. This class never accepts paths or compressed bytes. */
public final class E4Protocol {
    public static final int VERSION = 1, FRAMES = 6, QUEUE = 2, ENCODERS = 1;
    public static final int WIDTH = 256, HEIGHT = 144, STRIDE = WIDTH * 4;
    public static final int RGBA_BYTES = STRIDE * HEIGHT, MAX_OUTPUT_BYTES = 2 * 1024 * 1024;
    public static final long MAX_PTS_US = 86_400_000_000L, MAX_RELATIVE_US = 2_000_000L;

    public static final class Identity {
        public final String task, serviceInstance;
        public final long epoch, generation;
        public final int hostUid, serviceUid;

        public Identity(String task, long epoch, long generation, String serviceInstance,
                        int hostUid, int serviceUid) throws IOException {
            if (task == null || !task.matches("[0-9a-f]{32}") || epoch <= 0 || generation <= 0
                    || serviceInstance == null
                    || !serviceInstance.matches("[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")
                    || hostUid <= 0 || serviceUid <= 0) {
                throw new IOException("E4_IDENTITY_INVALID");
            }
            this.task = task; this.epoch = epoch; this.generation = generation;
            this.serviceInstance = serviceInstance; this.hostUid = hostUid; this.serviceUid = serviceUid;
        }

        public boolean matches(Identity actual) {
            return actual != null && task.equals(actual.task) && epoch == actual.epoch
                    && generation == actual.generation && serviceInstance.equals(actual.serviceInstance)
                    && hostUid == actual.hostUid && serviceUid == actual.serviceUid;
        }

        public void requireHost(int originalBinderUid) throws IOException {
            if (originalBinderUid != hostUid) throw new IOException("E4_HOST_BINDER_UID");
        }

        public void requireService(int originalBinderUid) throws IOException {
            if (originalBinderUid != serviceUid) throw new IOException("E4_SERVICE_BINDER_UID");
        }

        public String key() { return task + ":" + epoch + ":" + generation + ":" + serviceInstance; }
    }

    /** Owns one validated bounded copy; callers can only request another bounded copy. */
    public static final class Frame {
        public final Identity identity;
        public final int sequence, width, height, stride, rotation;
        public final long ptsUs;
        public final String sha256;
        private final byte[] rgba;

        public Frame(Identity identity, int sequence, long ptsUs, int width, int height,
                     int stride, int rotation, byte[] rgba) throws IOException {
            if (identity == null || sequence < 1 || sequence > FRAMES || ptsUs < 0 || ptsUs > MAX_PTS_US)
                throw new IOException("E4_FRAME_IDENTITY_OR_TIME");
            if (width != WIDTH || height != HEIGHT || stride != STRIDE || rotation != 0
                    || rgba == null || rgba.length != RGBA_BYTES || (long) stride * height != rgba.length)
                throw new IOException("E4_FRAME_LAYOUT");
            this.identity = identity; this.sequence = sequence; this.ptsUs = ptsUs;
            this.width = width; this.height = height; this.stride = stride; this.rotation = rotation;
            this.rgba = rgba.clone();
            for (int i = 3; i < this.rgba.length; i += 4)
                if ((this.rgba[i] & 255) != 255) throw new IOException("E4_FRAME_ALPHA");
            sha256 = sha(this.rgba);
        }

        public Frame(Identity identity, int sequence, long ptsUs, byte[] rgba) throws IOException {
            this(identity, sequence, ptsUs, WIDTH, HEIGHT, STRIDE, 0, rgba);
        }

        public byte[] pixels() { return rgba.clone(); }
        public int byteCount() { return rgba.length; }
    }

    public static void timeline(long[] pts) throws IOException {
        if (pts == null || pts.length != FRAMES || pts[0] != 0) throw new IOException("E4_OUTPUT_TIMELINE");
        for (int i = 0; i < pts.length; i++)
            if (pts[i] < 0 || pts[i] > MAX_RELATIVE_US || (i > 0 && pts[i] <= pts[i - 1]))
                throw new IOException("E4_OUTPUT_TIMELINE");
    }

    public static String sha(byte[] value) {
        try {
            StringBuilder result = new StringBuilder(64);
            for (byte part : MessageDigest.getInstance("SHA-256").digest(value))
                result.append(String.format(Locale.ROOT, "%02x", part & 255));
            return result.toString();
        } catch (NoSuchAlgorithmException impossible) { throw new AssertionError(impossible); }
    }

    private E4Protocol() { }
}
