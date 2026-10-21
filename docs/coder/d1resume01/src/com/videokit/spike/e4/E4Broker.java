package com.videokit.spike.e4;

import java.io.IOException;
import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/**
 * Task-local raw-frame/ownership accounting shared by Android adapters and JVM rule checks.
 * It is not a codec, Binder authentication mechanism, or proof of Android permission isolation.
 * Actual adapters must pass the original Binder calling UID and actual resource close actions.
 */
public final class E4Broker {
    public static final int MAX_RECORDS = 16, MAX_ACTIVE_TASKS = 4, MAX_RESOURCES_PER_TASK = 24;
    public enum State { NEW, ACTIVE, REJECTED, CANCEL_PENDING, CANCELLED, UNKNOWN, OUTPUT_CLOSED, READY }
    public enum ResourceKind { SOURCE, SINK, ENCODER, IMAGE, IPC }
    public enum CloseState { OPEN, CLOSING, CLOSED, UNKNOWN }
    public interface CloseAction { void close() throws Exception; }

    private static final class Task {
        final E4Protocol.Identity id;
        final boolean sourceRequired, hostLedger;
        final ArrayDeque<E4Protocol.Frame> queue = new ArrayDeque<>();
        final List<ResourceLease> resources = new ArrayList<>();
        State state = State.NEW;
        int accepted, encoded, remoteEncoded, inFlight, discarded, peakQueued, operations, validatorUid;
        long firstPts = -1, lastPts = -1, outputBytes;
        boolean inputDone, died;
        String firstError;
        Task(E4Protocol.Identity id, boolean sourceRequired, boolean hostLedger) {
            this.id = id; this.sourceRequired = sourceRequired; this.hostLedger = hostLedger;
        }
    }

    public static final class Snapshot {
        public final E4Protocol.Identity identity;
        public final State state;
        public final int accepted, encoded, remoteEncoded, queued, inFlight, discarded, peakQueued;
        public final int liveResources, unknownResources, operations;
        public final boolean inputDone, sourceClosed, sinkClosed, encoderReleased, workerDied, hostLedger;
        public final String firstError;
        public final long outputBytes;
        private Snapshot(Task task) {
            identity = task.id; state = task.state; accepted = task.accepted; encoded = task.encoded;
            remoteEncoded = task.remoteEncoded; hostLedger = task.hostLedger;
            queued = task.queue.size(); inFlight = task.inFlight; discarded = task.discarded;
            peakQueued = task.peakQueued; operations = task.operations; inputDone = task.inputDone;
            int live = 0, unknown = 0;
            for (ResourceLease lease : task.resources) {
                if (lease.status != CloseState.CLOSED) live++;
                if (lease.status == CloseState.UNKNOWN || lease.status == CloseState.CLOSING) unknown++;
            }
            liveResources = live; unknownResources = unknown;
            sourceClosed = kindClosed(task, ResourceKind.SOURCE, task.sourceRequired);
            sinkClosed = kindClosed(task, ResourceKind.SINK, true);
            encoderReleased = kindClosed(task, ResourceKind.ENCODER, true);
            workerDied = task.died; firstError = task.firstError; outputBytes = task.outputBytes;
        }
        public boolean resourcesReleased() { return liveResources == 0 && inFlight == 0 && operations == 0; }
    }

    public final class FrameLease implements AutoCloseable {
        private final Task task;
        private E4Protocol.Frame frame;
        private final Thread owner = Thread.currentThread();
        private FrameLease(Task task, E4Protocol.Frame frame) { this.task = task; this.frame = frame; }
        public E4Protocol.Frame frame() throws IOException {
            synchronized (E4Broker.this) {
                if (frame == null) throw new IOException("E4_FRAME_LEASE_CLOSED");
                return frame;
            }
        }
        /** Invoke only after the actual codec input operation returns success. */
        public void encodedAndClose() throws IOException { finish(true); }
        public void close() throws IOException { finish(false); }
        private void finish(boolean encoded) throws IOException {
            synchronized (E4Broker.this) {
                if (Thread.currentThread() != owner) throw new IOException("E4_FRAME_OWNER_THREAD");
                if (frame == null) return;
                if (encoded && (task.state != State.ACTIVE || task.died))
                    throw new IOException("E4_LATE_FRAME_RESULT");
                if (encoded) task.encoded++;
                else {
                    task.discarded++;
                    if (task.state == State.ACTIVE) unknown(task, "E4_UNENCODED_FRAME_RETURNED");
                }
                frame = null; task.inFlight--;
                if (task.inFlight < 0) throw new AssertionError("frame lease underflow");
                finishCancellation(task); E4Broker.this.notifyAll();
            }
        }
    }

    /** Holds the original owner and close action until close actually returns successfully. */
    public final class ResourceLease implements AutoCloseable {
        public final ResourceKind kind;
        private final Task task;
        private final Thread ownerThread = Thread.currentThread();
        private Object actualOwner;
        private CloseAction action;
        private CloseState status = CloseState.OPEN;
        private ResourceLease(Task task, ResourceKind kind, Object owner, CloseAction action) {
            this.task = task; this.kind = kind; actualOwner = owner; this.action = action;
        }
        public CloseState state() { synchronized (E4Broker.this) { return status; } }
        public boolean retainsOwner() { synchronized (E4Broker.this) { return actualOwner != null; } }
        public void close() throws Exception {
            CloseAction original;
            synchronized (E4Broker.this) {
                if (Thread.currentThread() != ownerThread) throw new IOException("E4_RESOURCE_OWNER_THREAD");
                if (status == CloseState.CLOSED) return;
                if (status != CloseState.OPEN) throw new IOException("E4_RESOURCE_CLOSE_UNPROVEN");
                status = CloseState.CLOSING; original = action;
            }
            try { original.close(); }
            catch (Exception | Error failure) {
                synchronized (E4Broker.this) {
                    status = CloseState.UNKNOWN; unknown(task, "E4_RESOURCE_CLOSE_UNPROVEN");
                    E4Broker.this.notifyAll();
                }
                throw failure;
            }
            synchronized (E4Broker.this) {
                status = CloseState.CLOSED; actualOwner = null; action = null;
                finishCancellation(task); E4Broker.this.notifyAll();
            }
        }
    }

    /** Models an actual owner operation; cancel and service death never complete it. */
    public final class OperationLease implements AutoCloseable {
        private final Task task;
        private final Thread owner = Thread.currentThread();
        private boolean closed;
        private OperationLease(Task task) { this.task = task; }
        public void close() throws IOException {
            synchronized (E4Broker.this) {
                if (Thread.currentThread() != owner) throw new IOException("E4_OPERATION_OWNER_THREAD");
                if (!closed) { closed = true; task.operations--; finishCancellation(task); E4Broker.this.notifyAll(); }
            }
        }
    }

    private final Map<String, Task> records = new LinkedHashMap<>();
    private final Map<String, E4Protocol.Identity> current = new LinkedHashMap<>();

    public synchronized void create(E4Protocol.Identity id) throws IOException { create(id, false); }
    public synchronized void create(E4Protocol.Identity id, boolean sourceRequired) throws IOException {
        createInternal(id, sourceRequired, false);
    }
    public synchronized void createHost(E4Protocol.Identity id, boolean sourceRequired) throws IOException {
        createInternal(id, sourceRequired, true);
    }
    private void createInternal(E4Protocol.Identity id, boolean sourceRequired, boolean hostLedger) throws IOException {
        if (id == null) throw new IOException("E4_IDENTITY_INVALID");
        if (records.containsKey(id.key())) throw new IOException("E4_TASK_ALREADY_REGISTERED");
        if (records.size() >= MAX_RECORDS) throw new IOException("E4_HISTORY_BUDGET");
        int active = 0;
        for (Task task : records.values()) if (!released(task)) active++;
        if (active >= MAX_ACTIVE_TASKS) throw new IOException("E4_TASK_RESOURCE_BUDGET");
        E4Protocol.Identity prior = current.get(id.task);
        if (prior != null) {
            if (id.generation <= prior.generation || id.epoch < prior.epoch
                    || id.serviceInstance.equals(prior.serviceInstance)) throw new IOException("E4_GENERATION_NOT_NEW");
            Task old = records.get(prior.key());
            if (old != null && old.state != State.READY && old.state != State.CANCELLED && old.state != State.REJECTED)
                unknown(old, "E4_SUPERSEDED_GENERATION");
        }
        Task task = new Task(id, sourceRequired, hostLedger); records.put(id.key(), task); current.put(id.task, id);
    }

    public synchronized void serviceReady(int originalBinderUid, E4Protocol.Identity id, boolean supported)
            throws IOException {
        Task task = activeIdentity(id); id.requireService(originalBinderUid);
        if (task.state != State.NEW) throw new IOException("E4_READY_STATE");
        if (!supported) {
            if (!new Snapshot(task).resourcesReleased()) throw new IOException("E4_REJECTION_CLOSE_UNPROVEN");
            task.state = State.REJECTED; first(task, "E4_CAPABILITY_UNSUPPORTED"); return;
        }
        task.state = State.ACTIVE;
    }

    public synchronized void offer(int originalBinderUid, E4Protocol.Identity id, E4Protocol.Frame frame)
            throws IOException {
        Task task = activeIdentity(id); id.requireHost(originalBinderUid); requireActive(task);
        if (task.hostLedger) throw new IOException("E4_HOST_HAS_NO_CODEC_QUEUE");
        if (frame == null || !id.matches(frame.identity)) throw new IOException("E4_FRAME_IDENTITY");
        if (task.inputDone || frame.sequence != task.accepted + 1 || frame.sequence > E4Protocol.FRAMES)
            throw new IOException("E4_FRAME_SEQUENCE");
        if (task.queue.size() >= E4Protocol.QUEUE) throw new IOException("E4_FRAME_QUEUE_FULL");
        if ((task.lastPts >= 0 && frame.ptsUs <= task.lastPts)
                || (task.firstPts >= 0 && frame.ptsUs - task.firstPts > E4Protocol.MAX_RELATIVE_US))
            throw new IOException("E4_FRAME_PTS");
        if (task.firstPts < 0) task.firstPts = frame.ptsUs;
        task.lastPts = frame.ptsUs; task.accepted++; task.queue.addLast(frame);
        task.peakQueued = Math.max(task.peakQueued, task.queue.size()); notifyAll();
    }

    public synchronized FrameLease poll(E4Protocol.Identity id) throws IOException {
        Task task = activeIdentity(id); requireActive(task);
        if (task.hostLedger) throw new IOException("E4_HOST_HAS_NO_CODEC_QUEUE");
        if (task.inFlight != 0) throw new IOException("E4_FRAME_CONSUMER_BUSY");
        if (task.queue.isEmpty()) return null;
        task.inFlight++; return new FrameLease(task, task.queue.removeFirst());
    }

    /** Host records an acknowledged forwarding, never a local codec input or consumer release. */
    public synchronized void forwardedFrame(int originalHostUid, E4Protocol.Identity id, E4Protocol.Frame frame)
            throws IOException {
        Task task = activeIdentity(id); id.requireHost(originalHostUid); requireActive(task);
        if (!task.hostLedger || frame == null || !id.matches(frame.identity)) throw new IOException("E4_FORWARD_IDENTITY");
        if (task.inputDone || frame.sequence != task.accepted + 1 || frame.sequence > E4Protocol.FRAMES)
            throw new IOException("E4_FRAME_SEQUENCE");
        if ((task.lastPts >= 0 && frame.ptsUs <= task.lastPts)
                || (task.firstPts >= 0 && frame.ptsUs - task.firstPts > E4Protocol.MAX_RELATIVE_US))
            throw new IOException("E4_FRAME_PTS");
        if (task.firstPts < 0) task.firstPts = frame.ptsUs;
        task.lastPts = frame.ptsUs; task.accepted++;
    }

    public synchronized void endFrames(int originalBinderUid, E4Protocol.Identity id) throws IOException {
        Task task = activeIdentity(id); id.requireHost(originalBinderUid); requireActive(task);
        if (task.accepted != E4Protocol.FRAMES || task.inputDone) throw new IOException("E4_FRAME_COUNT");
        task.inputDone = true; notifyAll();
    }

    public synchronized ResourceLease registerResource(E4Protocol.Identity id, ResourceKind kind,
                                                       Object actualOwner, CloseAction close) throws IOException {
        Task task = activeIdentity(id);
        if (task.state != State.NEW && task.state != State.ACTIVE && task.state != State.CANCEL_PENDING
                && task.state != State.UNKNOWN) throw new IOException("E4_RESOURCE_TERMINAL_TASK");
        if (kind == null || actualOwner == null || close == null) throw new IOException("E4_RESOURCE_INVALID");
        if (task.hostLedger && (kind == ResourceKind.ENCODER || kind == ResourceKind.IMAGE))
            throw new IOException("E4_HOST_CANNOT_OWN_CODEC_RESOURCE");
        if (task.resources.size() >= MAX_RESOURCES_PER_TASK) throw new IOException("E4_RESOURCE_BUDGET");
        int liveKind = 0;
        for (ResourceLease lease : task.resources)
            if (lease.kind == kind && lease.status != CloseState.CLOSED) liveKind++;
        int limit = kind == ResourceKind.IPC ? 8 : 1;
        if (liveKind >= limit) throw new IOException("E4_" + kind + "_LEASE_BUSY");
        ResourceLease lease = new ResourceLease(task, kind, actualOwner, close); task.resources.add(lease); return lease;
    }

    public synchronized OperationLease beginOperation(E4Protocol.Identity id) throws IOException {
        Task task = activeIdentity(id); requireActive(task);
        if (task.operations >= 8) throw new IOException("E4_OPERATION_BUDGET");
        task.operations++; return new OperationLease(task);
    }

    public synchronized void cancel(int originalBinderUid, E4Protocol.Identity id) throws IOException {
        Task task = activeIdentity(id); id.requireHost(originalBinderUid);
        if (task.state == State.READY || task.state == State.CANCELLED || task.state == State.REJECTED) return;
        if (task.state != State.UNKNOWN) task.state = State.CANCEL_PENDING;
        first(task, "E4_CANCELLED"); discardQueued(task); finishCancellation(task); notifyAll();
    }

    /** Binder death is an incarnation observation, never a resource-close acknowledgment. */
    public synchronized int workerDied(String serviceInstance) throws IOException {
        if (serviceInstance == null) throw new IOException("E4_INSTANCE_INVALID");
        int affected = 0;
        for (Task task : records.values()) {
            if (task.id.serviceInstance.equals(serviceInstance) && task.state != State.READY
                    && task.state != State.CANCELLED && task.state != State.REJECTED) {
                task.died = true; unknown(task, "WORKER_DIED"); discardQueued(task); affected++;
            }
        }
        notifyAll(); return affected;
    }

    public synchronized void codecFinished(int originalBinderUid, E4Protocol.Identity id, long outputBytes)
            throws IOException {
        Task task = activeIdentity(id); id.requireService(originalBinderUid); requireActive(task);
        if (task.hostLedger) throw new IOException("E4_HOST_CANNOT_PROVE_LOCAL_CODEC");
        Snapshot proof = new Snapshot(task);
        if (!task.inputDone || task.accepted != E4Protocol.FRAMES || task.encoded != E4Protocol.FRAMES
                || !task.queue.isEmpty() || !proof.resourcesReleased() || !proof.sinkClosed
                || !proof.encoderReleased || !proof.sourceClosed || outputBytes < 1
                || outputBytes > E4Protocol.MAX_OUTPUT_BYTES) throw new IOException("E4_OUTPUT_CLOSE_UNPROVEN");
        task.outputBytes = outputBytes; task.state = State.OUTPUT_CLOSED;
    }

    /**
     * An authenticated service report is retained as remote evidence, not host-measured resources.
     * Locally owned Source/Sink handles must independently finish their real close actions.
     */
    public synchronized void remoteOutputClosed(int originalServiceUid, E4Protocol.Identity id,
                                                int encodedFrames, int remoteLiveResources,
                                                int remoteUnknownResources, boolean remoteSinkClosed,
                                                boolean remoteEncoderClosed, long outputBytes) throws IOException {
        Task task = activeIdentity(id); id.requireService(originalServiceUid); requireActive(task);
        Snapshot local = new Snapshot(task);
        if (!task.hostLedger || !task.inputDone || task.accepted != E4Protocol.FRAMES
                || encodedFrames != E4Protocol.FRAMES || remoteLiveResources != 0 || remoteUnknownResources != 0
                || !remoteSinkClosed || !remoteEncoderClosed || !local.resourcesReleased()
                || !local.sourceClosed || !local.sinkClosed || outputBytes < 1
                || outputBytes > E4Protocol.MAX_OUTPUT_BYTES) throw new IOException("E4_REMOTE_OUTPUT_CLOSE_UNPROVEN");
        task.remoteEncoded = encodedFrames; task.outputBytes = outputBytes; task.state = State.OUTPUT_CLOSED;
    }

    /**
     * The trusted CPU adapter authenticates its ordinary isolated worker before parsing internally.
     * After that adapter returns its original authenticated receipt, the host binds its original UID
     * here immediately before forwarding validation. This pure method supplies no Binder proof.
     */
    public synchronized void authorizeValidator(int originalHostUid, E4Protocol.Identity id, int isolatedUid)
            throws IOException {
        Task task = activeIdentity(id); id.requireHost(originalHostUid);
        if (task.validatorUid != 0 || isolatedUid <= 0 || isolatedUid == id.hostUid
                || isolatedUid % 100000 < 90000) throw new IOException("E4_VALIDATOR_IDENTITY");
        task.validatorUid = isolatedUid;
    }

    /** Only invoke after actual isolated output parse/timeline/content verification returns. */
    public synchronized void validatedOutput(int originalBinderUid, E4Protocol.Identity id,
                                             int frames, long[] timeline, boolean contentConfirmed)
            throws IOException {
        Task task = activeIdentity(id);
        if (task.state != State.OUTPUT_CLOSED || task.validatorUid == 0
                || originalBinderUid != task.validatorUid || frames != E4Protocol.FRAMES || !contentConfirmed)
            throw new IOException("E4_VALIDATION_NOT_PROVEN");
        E4Protocol.timeline(timeline);
        Snapshot proof = new Snapshot(task);
        if (!proof.resourcesReleased() || !proof.sourceClosed || !proof.sinkClosed || task.died)
            throw new IOException("E4_RESOURCE_CLOSE_UNPROVEN");
        task.state = State.READY;
    }

    public synchronized Snapshot snapshot(E4Protocol.Identity id) throws IOException { return new Snapshot(exact(id)); }

    private Task activeIdentity(E4Protocol.Identity id) throws IOException {
        Task task = exact(id);
        if (!id.matches(current.get(id.task))) throw new IOException("E4_OLD_GENERATION");
        return task;
    }
    private Task exact(E4Protocol.Identity id) throws IOException {
        Task task = id == null ? null : records.get(id.key());
        if (task == null || !task.id.matches(id)) throw new IOException("E4_TASK_IDENTITY");
        return task;
    }
    private static void requireActive(Task task) throws IOException {
        if (task.state != State.ACTIVE || task.died) throw new IOException("E4_TASK_NOT_ACTIVE_" + task.state);
    }
    private static void discardQueued(Task task) { task.discarded += task.queue.size(); task.queue.clear(); }
    private static void first(Task task, String error) { if (task.firstError == null) task.firstError = error; }
    private static void unknown(Task task, String error) { first(task, error); task.state = State.UNKNOWN; }
    private static boolean kindClosed(Task task, ResourceKind kind, boolean required) {
        boolean seen = false;
        for (ResourceLease lease : task.resources) if (lease.kind == kind) {
            seen = true; if (lease.status != CloseState.CLOSED) return false;
        }
        return seen || !required;
    }
    private static boolean released(Task task) {
        if (task.state != State.READY && task.state != State.CANCELLED && task.state != State.REJECTED) return false;
        if (!task.queue.isEmpty() || task.inFlight != 0 || task.operations != 0) return false;
        for (ResourceLease lease : task.resources) if (lease.status != CloseState.CLOSED) return false;
        return true;
    }
    private static void finishCancellation(Task task) {
        if (task.state != State.CANCEL_PENDING || task.inFlight != 0 || task.operations != 0) return;
        for (ResourceLease lease : task.resources) if (lease.status != CloseState.CLOSED) return;
        task.state = State.CANCELLED;
    }
}
