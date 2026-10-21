package com.videokit.spike.e4;

import java.io.IOException;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicReference;

/** Pure JVM ownership/protocol counterexamples. No Android, native, media, or isolation claim. */
public final class E4CoreSelfCheck {
    private static int assertions;
    private interface Checked { void run() throws Exception; }
    private static void check(boolean condition, String name) {
        assertions++;
        if (!condition) throw new AssertionError(name);
    }
    private static void reject(String code, Checked action) throws Exception {
        try { action.run(); }
        catch (IOException expected) {
            check(expected.getMessage() != null && expected.getMessage().startsWith(code),
                    "wrong rejection: " + expected.getMessage() + " expected " + code);
            return;
        }
        throw new AssertionError("missing rejection: " + code);
    }
    private static E4Protocol.Identity id(int task, int generation, int instance) throws Exception {
        return new E4Protocol.Identity(String.format("%032x", task), 7, generation,
                String.format("00000000-0000-0000-0000-%012x", instance), 10101, 10101);
    }
    private static byte[] pixels(int sequence) {
        byte[] pixels = new byte[E4Protocol.RGBA_BYTES];
        for (int i = 0; i < pixels.length; i += 4) {
            pixels[i] = (byte) (sequence * 17); pixels[i + 1] = (byte) (i / 4);
            pixels[i + 2] = (byte) (i / E4Protocol.STRIDE); pixels[i + 3] = (byte) 255;
        }
        return pixels;
    }
    private static E4Protocol.Frame frame(E4Protocol.Identity id, int sequence) throws Exception {
        return new E4Protocol.Frame(id, sequence, (sequence - 1) * 200000L, pixels(sequence));
    }
    private static final long[] TIMELINE = {0, 200000, 400000, 600000, 800000, 1000000};

    private static void wireAndBudgets() throws Exception {
        E4Protocol.Identity id = id(1, 1, 1);
        reject("E4_IDENTITY_INVALID", () -> new E4Protocol.Identity("bad", 1, 1, id.serviceInstance, 1, 1));
        reject("E4_IDENTITY_INVALID", () -> new E4Protocol.Identity(id.task, 0, 1, id.serviceInstance, 1, 1));
        reject("E4_IDENTITY_INVALID", () -> new E4Protocol.Identity(id.task, 1, 0, id.serviceInstance, 1, 1));
        reject("E4_IDENTITY_INVALID", () -> new E4Protocol.Identity(id.task, 1, 1, "unbound", 1, 1));
        byte[] mutable = pixels(1);
        E4Protocol.Frame owned = new E4Protocol.Frame(id, 1, 0, mutable);
        String digest = owned.sha256; mutable[0] ^= 1;
        check(digest.equals(E4Protocol.sha(owned.pixels())), "input bytes cloned");
        byte[] exported = owned.pixels(); exported[1] ^= 1;
        check(digest.equals(E4Protocol.sha(owned.pixels())), "returned bytes cloned");
        reject("E4_FRAME_LAYOUT", () -> new E4Protocol.Frame(id, 1, 0, new byte[1]));
        reject("E4_FRAME_LAYOUT", () -> new E4Protocol.Frame(id, 1, 0, 256, 144, 1024, 90, pixels(1)));
        byte[] transparent = pixels(1); transparent[3] = 0;
        reject("E4_FRAME_ALPHA", () -> new E4Protocol.Frame(id, 1, 0, transparent));
        reject("E4_FRAME_IDENTITY_OR_TIME", () -> new E4Protocol.Frame(id, 7, 0, pixels(1)));

        E4Broker broker = new E4Broker(); broker.create(id);
        reject("E4_TASK_NOT_ACTIVE_NEW", () -> broker.offer(id.hostUid, id, owned));
        reject("E4_SERVICE_BINDER_UID", () -> broker.serviceReady(123, id, true));
        broker.serviceReady(id.serviceUid, id, true);
        reject("E4_HOST_BINDER_UID", () -> broker.offer(123, id, owned));
        reject("E4_FRAME_IDENTITY", () -> broker.offer(id.hostUid, id, frame(id(2, 1, 2), 1)));
        broker.offer(id.hostUid, id, owned); broker.offer(id.hostUid, id, frame(id, 2));
        reject("E4_FRAME_QUEUE_FULL", () -> broker.offer(id.hostUid, id, frame(id, 3)));
        check(broker.snapshot(id).accepted == 2 && broker.snapshot(id).queued == 2, "queue refusal consumes no frame");
        E4Broker.FrameLease first = broker.poll(id);
        check(first.frame().sequence == 1, "strict first frame");
        reject("E4_FRAME_CONSUMER_BUSY", () -> broker.poll(id));
        broker.offer(id.hostUid, id, frame(id, 3));
        check(broker.snapshot(id).queued == 2 && broker.snapshot(id).inFlight == 1, "queue2 plus one exact consumer");
        first.encodedAndClose(); first.close();
        check(broker.snapshot(id).encoded == 1 && broker.snapshot(id).inFlight == 0, "consumer closes exactly once");
        reject("E4_FRAME_LEASE_CLOSED", first::frame);
        for (int sequence = 2; sequence <= 6; sequence++) {
            if (sequence >= 4) broker.offer(id.hostUid, id, frame(id, sequence));
            E4Broker.FrameLease lease = broker.poll(id);
            check(lease.frame().sequence == sequence, "ordered drain " + sequence); lease.encodedAndClose();
        }
        check(broker.poll(id) == null, "empty poll has no fabricated EOS");
        reject("E4_OUTPUT_CLOSE_UNPROVEN", () -> broker.codecFinished(id.serviceUid, id, 42));
        broker.endFrames(id.hostUid, id);
        AtomicInteger closes = new AtomicInteger();
        E4Broker.ResourceLease sink = broker.registerResource(id, E4Broker.ResourceKind.SINK, closes, closes::incrementAndGet);
        E4Broker.ResourceLease encoder = broker.registerResource(id, E4Broker.ResourceKind.ENCODER, closes, closes::incrementAndGet);
        reject("E4_ENCODER_LEASE_BUSY", () -> broker.registerResource(id, E4Broker.ResourceKind.ENCODER, new Object(), () -> { }));
        reject("E4_OUTPUT_CLOSE_UNPROVEN", () -> broker.codecFinished(id.serviceUid, id, 42));
        sink.close(); encoder.close(); sink.close();
        check(closes.get() == 2 && !sink.retainsOwner() && !encoder.retainsOwner(), "close action once and then release owner");
        broker.codecFinished(id.serviceUid, id, 42);
        check(broker.snapshot(id).state == E4Broker.State.OUTPUT_CLOSED, "codec never makes READY");
        reject("E4_VALIDATION_NOT_PROVEN", () -> broker.validatedOutput(99001, id, 6, TIMELINE, true));
        reject("E4_VALIDATOR_IDENTITY", () -> broker.authorizeValidator(id.hostUid, id, id.hostUid));
        broker.authorizeValidator(id.hostUid, id, 99001);
        reject("E4_VALIDATION_NOT_PROVEN", () -> broker.validatedOutput(id.hostUid, id, 6, TIMELINE, true));
        reject("E4_VALIDATION_NOT_PROVEN", () -> broker.validatedOutput(99001, id, 6, TIMELINE, false));
        reject("E4_OUTPUT_TIMELINE", () -> broker.validatedOutput(99001, id, 6, new long[]{0, 1, 1, 3, 4, 5}, true));
        broker.validatedOutput(99001, id, 6, TIMELINE, true);
        check(broker.snapshot(id).state == E4Broker.State.READY, "independent validated callback gate");
        check(broker.snapshot(id).peakQueued == 2 && broker.snapshot(id).resourcesReleased(), "normal bounded ownership release");
    }

    private static void readinessAndFailure() throws Exception {
        E4Broker broker = new E4Broker(); E4Protocol.Identity id = id(3, 1, 3); broker.create(id);
        AtomicInteger returned = new AtomicInteger();
        E4Broker.ResourceLease preReady = broker.registerResource(id, E4Broker.ResourceKind.SINK, returned, returned::incrementAndGet);
        reject("E4_REJECTION_CLOSE_UNPROVEN", () -> broker.serviceReady(id.serviceUid, id, false));
        check(broker.snapshot(id).state == E4Broker.State.NEW && preReady.retainsOwner(), "pre-ready object remains owned");
        preReady.close(); broker.serviceReady(id.serviceUid, id, false);
        check(broker.snapshot(id).state == E4Broker.State.REJECTED && returned.get() == 1, "refused only after close return");
        reject("E4_TASK_NOT_ACTIVE_REJECTED", () -> broker.offer(id.hostUid, id, frame(id, 1)));

        E4Protocol.Identity bad = id(4, 1, 4); broker.create(bad); broker.serviceReady(bad.serviceUid, bad, true);
        Object original = new Object(); AtomicInteger closeCalls = new AtomicInteger();
        E4Broker.ResourceLease failed = broker.registerResource(bad, E4Broker.ResourceKind.ENCODER, original, () -> {
            closeCalls.incrementAndGet(); throw new IOException("OWNED_SYNTHETIC_CLOSE_FAILURE");
        });
        reject("OWNED_SYNTHETIC_CLOSE_FAILURE", failed::close);
        check(failed.state() == E4Broker.CloseState.UNKNOWN && failed.retainsOwner(), "failed close retains exact original owner");
        check(broker.snapshot(bad).state == E4Broker.State.UNKNOWN && broker.snapshot(bad).liveResources == 1, "failed close never releases credit");
        reject("E4_RESOURCE_CLOSE_UNPROVEN", failed::close);
        check(closeCalls.get() == 1, "unknown close is never retried");
        reject("E4_ENCODER_LEASE_BUSY", () -> broker.registerResource(bad, E4Broker.ResourceKind.ENCODER, new Object(), () -> { }));
        broker.cancel(bad.hostUid, bad);
        check(broker.snapshot(bad).state == E4Broker.State.UNKNOWN && failed.retainsOwner(), "cancel cannot make unknown ready or released");
    }

    private static void cancellationAndGenerations() throws Exception {
        E4Broker broker = new E4Broker(); E4Protocol.Identity old = id(5, 1, 5); broker.create(old);
        broker.serviceReady(old.serviceUid, old, true);
        AtomicInteger closes = new AtomicInteger();
        E4Broker.ResourceLease sink = broker.registerResource(old, E4Broker.ResourceKind.SINK, closes, closes::incrementAndGet);
        broker.offer(old.hostUid, old, frame(old, 1)); broker.offer(old.hostUid, old, frame(old, 2));
        E4Broker.FrameLease consumer = broker.poll(old); E4Broker.OperationLease operation = broker.beginOperation(old);
        broker.cancel(old.hostUid, old);
        E4Broker.Snapshot pending = broker.snapshot(old);
        check(pending.state == E4Broker.State.CANCEL_PENDING && pending.queued == 0 && pending.inFlight == 1
                && pending.liveResources == 1 && pending.operations == 1, "cancel only discards host owned queued copies");
        reject("E4_TASK_NOT_ACTIVE_CANCEL_PENDING", () -> broker.offer(old.hostUid, old, frame(old, 3)));
        reject("E4_LATE_FRAME_RESULT", consumer::encodedAndClose);
        check(broker.snapshot(old).inFlight == 1 && broker.snapshot(old).encoded == 0, "late success cannot clear original consumer");
        consumer.close(); sink.close();
        check(broker.snapshot(old).state == E4Broker.State.CANCEL_PENDING && broker.snapshot(old).operations == 1,
                "actual operation still pending after descriptor/frame close");
        operation.close();
        check(broker.snapshot(old).state == E4Broker.State.CANCELLED && closes.get() == 1, "cancel finishes only actual returns");

        E4Protocol.Identity fresh = id(5, 2, 6); broker.create(fresh); broker.serviceReady(fresh.serviceUid, fresh, true);
        reject("E4_OLD_GENERATION", () -> broker.offer(old.hostUid, old, frame(old, 3)));
        reject("E4_OLD_GENERATION", () -> broker.codecFinished(old.serviceUid, old, 1));
        reject("E4_GENERATION_NOT_NEW", () -> broker.create(id(5, 2, 7)));
        reject("E4_GENERATION_NOT_NEW", () -> broker.create(id(5, 3, 6)));
        check(broker.snapshot(fresh).state == E4Broker.State.ACTIVE, "old results do not corrupt new generation");

        E4Protocol.Identity other = id(6, 1, 8); broker.create(other); broker.serviceReady(other.serviceUid, other, true);
        E4Broker.ResourceLease retained = broker.registerResource(fresh, E4Broker.ResourceKind.ENCODER, new Object(), () -> { });
        check(broker.workerDied(fresh.serviceInstance) == 1, "death scopes original incarnation");
        check(broker.snapshot(fresh).state == E4Broker.State.UNKNOWN && retained.retainsOwner(), "death not a resource close receipt");
        broker.offer(other.hostUid, other, frame(other, 1)); E4Broker.FrameLease independent = broker.poll(other);
        independent.encodedAndClose();
        check(broker.snapshot(other).state == E4Broker.State.ACTIVE && broker.snapshot(other).encoded == 1,
                "unrelated actual ledger remains runnable");
        retained.close();
        check(broker.snapshot(fresh).state == E4Broker.State.UNKNOWN, "later close does not erase worker death");
    }

    private static void hostRemoteEvidence() throws Exception {
        E4Broker broker = new E4Broker(); E4Protocol.Identity id = id(7, 1, 9); broker.createHost(id, true);
        AtomicInteger closed = new AtomicInteger();
        E4Broker.ResourceLease source = broker.registerResource(id, E4Broker.ResourceKind.SOURCE, closed, closed::incrementAndGet);
        E4Broker.ResourceLease sink = broker.registerResource(id, E4Broker.ResourceKind.SINK, closed, closed::incrementAndGet);
        reject("E4_HOST_CANNOT_OWN_CODEC_RESOURCE", () -> broker.registerResource(id, E4Broker.ResourceKind.ENCODER, new Object(), () -> { }));
        broker.serviceReady(id.serviceUid, id, true);
        reject("E4_HOST_HAS_NO_CODEC_QUEUE", () -> broker.offer(id.hostUid, id, frame(id, 1)));
        reject("E4_HOST_HAS_NO_CODEC_QUEUE", () -> broker.poll(id));
        for (int sequence = 1; sequence <= 6; sequence++) broker.forwardedFrame(id.hostUid, id, frame(id, sequence));
        broker.endFrames(id.hostUid, id);
        reject("E4_REMOTE_OUTPUT_CLOSE_UNPROVEN", () -> broker.remoteOutputClosed(id.serviceUid, id, 6, 0, 0, true, true, 500));
        source.close(); sink.close();
        reject("E4_SERVICE_BINDER_UID", () -> broker.remoteOutputClosed(42, id, 6, 0, 0, true, true, 500));
        reject("E4_REMOTE_OUTPUT_CLOSE_UNPROVEN", () -> broker.remoteOutputClosed(id.serviceUid, id, 6, 1, 0, true, true, 500));
        reject("E4_REMOTE_OUTPUT_CLOSE_UNPROVEN", () -> broker.remoteOutputClosed(id.serviceUid, id, 6, 0, 1, true, true, 500));
        reject("E4_REMOTE_OUTPUT_CLOSE_UNPROVEN", () -> broker.remoteOutputClosed(id.serviceUid, id, 5, 0, 0, true, true, 500));
        reject("E4_REMOTE_OUTPUT_CLOSE_UNPROVEN", () -> broker.remoteOutputClosed(id.serviceUid, id, 6, 0, 0, false, true, 500));
        reject("E4_REMOTE_OUTPUT_CLOSE_UNPROVEN", () -> broker.remoteOutputClosed(id.serviceUid, id, 6, 0, 0, true, false, 500));
        reject("E4_REMOTE_OUTPUT_CLOSE_UNPROVEN", () -> broker.remoteOutputClosed(id.serviceUid, id, 6, 0, 0, true, true, 0));
        broker.remoteOutputClosed(id.serviceUid, id, 6, 0, 0, true, true, 500);
        E4Broker.Snapshot proof = broker.snapshot(id);
        check(proof.state == E4Broker.State.OUTPUT_CLOSED && proof.encoded == 0 && proof.remoteEncoded == 6
                && !proof.encoderReleased && proof.sourceClosed && proof.sinkClosed,
                "remote report never becomes locally measured codec resources");
        broker.authorizeValidator(id.hostUid, id, 99002);
        broker.validatedOutput(99002, id, 6, TIMELINE, true);
        check(broker.snapshot(id).state == E4Broker.State.READY && closed.get() == 2, "host gate needs own close and independent validator");
    }

    private static void pendingActualReturn() throws Exception {
        E4Broker broker = new E4Broker(); E4Protocol.Identity id = id(8, 1, 10); broker.create(id);
        broker.serviceReady(id.serviceUid, id, true);
        CountDownLatch entered = new CountDownLatch(1), returnAllowed = new CountDownLatch(1);
        AtomicReference<E4Broker.ResourceLease> leaseRef = new AtomicReference<>();
        AtomicReference<Throwable> failure = new AtomicReference<>();
        Thread owner = new Thread(() -> {
            try {
                E4Broker.ResourceLease lease = broker.registerResource(id, E4Broker.ResourceKind.SINK, new Object(), () -> {
                    entered.countDown();
                    if (!returnAllowed.await(2, TimeUnit.SECONDS)) throw new IOException("SELF_CHECK_CLOSE_WAIT");
                });
                leaseRef.set(lease); lease.close();
            } catch (Throwable problem) { failure.set(problem); }
        }, "e4-owned-synthetic-close");
        owner.setDaemon(true); owner.start();
        try {
            check(entered.await(2, TimeUnit.SECONDS), "owned close entered");
            E4Broker.ResourceLease lease = leaseRef.get();
            check(lease != null && lease.state() == E4Broker.CloseState.CLOSING && lease.retainsOwner(), "close invocation is not return");
            reject("E4_RESOURCE_OWNER_THREAD", lease::close);
            broker.cancel(id.hostUid, id);
            check(broker.snapshot(id).state == E4Broker.State.CANCEL_PENDING && broker.snapshot(id).liveResources == 1
                    && broker.snapshot(id).unknownResources == 1, "timeout/cancel preserves closing owner");
            check(broker.workerDied(id.serviceInstance) == 1 && broker.snapshot(id).state == E4Broker.State.UNKNOWN,
                    "death observation while original close is in flight");
        } finally { returnAllowed.countDown(); }
        owner.join(2000);
        check(!owner.isAlive() && failure.get() == null, "original close actually returned and owner ended");
        check(leaseRef.get().state() == E4Broker.CloseState.CLOSED && !leaseRef.get().retainsOwner()
                && broker.snapshot(id).state == E4Broker.State.UNKNOWN, "actual return releases owner but never erases death");
    }

    private static void capacityAndIdentity() throws Exception {
        E4Broker broker = new E4Broker();
        for (int number = 1; number <= E4Broker.MAX_ACTIVE_TASKS; number++) {
            E4Protocol.Identity id = id(20 + number, 1, 20 + number);
            broker.create(id); broker.serviceReady(id.serviceUid, id, true);
            broker.workerDied(id.serviceInstance);
        }
        reject("E4_TASK_RESOURCE_BUDGET", () -> broker.create(id(99, 1, 99)));
        E4Protocol.Identity known = id(21, 1, 21);
        E4Protocol.Identity wrongEpoch = new E4Protocol.Identity(known.task, 8, known.generation,
                known.serviceInstance, known.hostUid, known.serviceUid);
        reject("E4_TASK_IDENTITY", () -> broker.snapshot(wrongEpoch));
        E4Protocol.Identity wrongUid = new E4Protocol.Identity(known.task, known.epoch, known.generation,
                known.serviceInstance, known.hostUid, 123);
        reject("E4_TASK_IDENTITY", () -> broker.snapshot(wrongUid));
        check(broker.snapshot(known).state == E4Broker.State.UNKNOWN, "failed admission preserves original retained record");
    }

    public static void main(String[] args) throws Exception {
        if (args.length != 0) throw new IllegalArgumentException("no external inputs");
        wireAndBudgets(); readinessAndFailure(); cancellationAndGenerations();
        hostRemoteEvidence(); pendingActualReturn(); capacityAndIdentity();
        System.out.println("{\"scope\":\"E4_PURE_JVM_PROTOCOL_OWNERSHIP_ONLY\",\"assertions\":" + assertions
                + ",\"result\":\"PASS\",\"androidCodec\":\"NOT_RUN\",\"binderIsolation\":\"NOT_RUN\"}");
    }

    private E4CoreSelfCheck() { }
}
