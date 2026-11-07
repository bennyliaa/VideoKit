package com.videokit.flutter

import android.content.Context
import com.videokit.api.ErrorCode
import com.videokit.api.MediaKind
import com.videokit.api.SessionPhase
import com.videokit.api.VideoKit
import com.videokit.api.VideoKitConfig
import com.videokit.api.VideoKitMediaSource
import com.videokit.api.VideoKitOutputSink
import com.videokit.api.VideoKitSessionConfig
import com.videokit.flutter.gen.CapabilityRequestMsg
import com.videokit.flutter.gen.CommandResultKind
import com.videokit.flutter.gen.CommandResultMsg
import com.videokit.flutter.gen.EditCommandMsg
import com.videokit.flutter.gen.EditProjectConfigMsg
import com.videokit.flutter.gen.EditResultKind
import com.videokit.flutter.gen.ExportRequestMsg
import com.videokit.flutter.gen.ExportResultKind
import com.videokit.flutter.gen.FlutterError
import com.videokit.flutter.gen.HandshakeRequest
import com.videokit.flutter.gen.MediaKindMsg
import com.videokit.flutter.gen.MediaSourceMsg
import com.videokit.flutter.gen.SessionConfigMsg
import com.videokit.flutter.gen.SessionPhaseMsg
import com.videokit.flutter.gen.SessionUpdateMessage
import com.videokit.testkit.FakeMediaSources
import com.videokit.testkit.FakeVideoKit
import com.videokit.testkit.FakeVideoKitOptions
import com.videokit.testkit.RecordingHostCallbacks
import com.videokit.testkit.RecordingOutputSink
import com.videokit.testkit.demo
import io.flutter.plugin.common.BinaryMessenger
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.runBlocking
import kotlinx.coroutines.withTimeout
import org.junit.After
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertTrue
import org.junit.Assert.fail
import org.junit.Before
import org.junit.Test
import java.nio.ByteBuffer
import java.util.concurrent.CopyOnWriteArrayList

/**
 * The channel implementation over the Kotlin Fake (14 §8.3), on the JVM: handshake, unknown ids, command
 * results, source and sink references, edit and export flow, sampled updates. No device, no Flutter engine.
 */
class HostApiImplTest {
    /** Messenger that answers every Dart call with "no handler" (callbacks then fail as HOST_CALLBACK_FAILED). */
    private val messenger = object : BinaryMessenger {
        override fun send(channel: String, message: ByteBuffer?) = Unit

        override fun send(channel: String, message: ByteBuffer?, callback: BinaryMessenger.BinaryReply?) {
            callback?.reply(null)
        }

        override fun setMessageHandler(channel: String, handler: BinaryMessenger.BinaryMessageHandler?) = Unit
    }

    private val updates = CopyOnWriteArrayList<SessionUpdateMessage>()
    private lateinit var engine: EngineRuntime
    private lateinit var api: HostApiImpl

    private val testBackend = object : VideoKitBackend {
        override val isDemo: Boolean = true

        override fun create(context: Context, config: VideoKitConfig): VideoKit = FakeVideoKit.fromConfig(config, FakeVideoKitOptions())

        override fun demoSource(scenarioId: String, token: String, kind: MediaKind): VideoKitMediaSource =
            FakeMediaSources.demo(scenarioId, token, kind)

        override fun demoSink(): VideoKitOutputSink = RecordingOutputSink()
    }

    @Before
    fun setUp() {
        VideoKitFlutter.setBackend(testBackend)
        engine = EngineRuntime(
            engineKey = "test-engine",
            context = object : android.content.ContextWrapper(null) {},
            messenger = messenger,
            textures = null,
            main = MainThreadRunner { it() },
            nowMs = { System.currentTimeMillis() },
            mainDispatcher = Dispatchers.Unconfined,
        )
        engine.sessionFanout.listen(com.videokit.flutter.gen.PigeonEventSink(RecordingEventSink(updates)))
        api = HostApiImpl(engine)
    }

    @After
    fun tearDown() {
        engine.close()
        VideoKitFlutter.setBackend(null)
    }

    private fun handshake() = api.handshake(HandshakeRequest(1, "1.0.0-dev.1", 10_000, 3_000, 3_000, 2_000))

    private fun <T> await(call: suspend () -> T): T = runBlocking { withTimeout(10_000) { call() } }

    private fun source(ref: String, token: String = "tok") =
        MediaSourceMsg(token, MediaKindMsg.VIDEO, null, null, "video/mp4", "mp4", true, ref)

    private fun session(): String {
        val created = api.createSession(SessionConfigMsg("SINGLE", "VISIBLE", "VISIBLE", true, null))
        return created.id ?: fail("createSession failed: ${created.error}") as String
    }

    @Test
    fun handshakeReportsDemoBackendAndProtocol() {
        val response = handshake()
        assertEquals(CHANNEL_PROTOCOL_VERSION, response.protocolVersion)
        assertEquals("1.0.0", response.apiVersion)
        assertTrue(response.demoBackend)
    }

    @Test
    fun handshakeWithoutBackendFailsClearly() {
        VideoKitFlutter.setBackend(null)
        // In unit tests the debug source set is on the classpath, so the debug Fake would be found; force none.
        val bare =
            EngineRuntime(
                "bare",
                object : android.content.ContextWrapper(null) {},
                messenger,
                null,
                MainThreadRunner {
                    it()
                },
                mainDispatcher = Dispatchers.Unconfined,
            )
        val backend = VideoKitFlutter.resolveBackend()
        if (backend == null) {
            try {
                HostApiImpl(bare).handshake(HandshakeRequest(1, "x", 1, 1, 1, 1))
                fail("expected FlutterError")
            } catch (expected: FlutterError) {
                assertEquals(VideoKitFlutter.NO_BACKEND, expected.code)
            }
        } else {
            assertTrue("only the debug Fake may be found implicitly", backend.isDemo)
        }
        bare.close()
    }

    @Test
    fun callsBeforeHandshakeAreProtocolErrors() {
        try {
            api.createSession(SessionConfigMsg("SINGLE", "VISIBLE", "VISIBLE", true, null))
            fail("expected FlutterError")
        } catch (expected: FlutterError) {
            assertEquals("VIDEOKIT_NOT_INITIALIZED", expected.code)
        }
    }

    @Test
    fun unknownSessionIdsAnswerSessionReleased() {
        handshake()
        val result: CommandResultMsg = await { api.play("no-such-session") }
        assertEquals(CommandResultKind.SESSION_RELEASED, result.kind)
        assertEquals(null, await { api.captureState("no-such-session") })
    }

    @Test
    fun demoSourceBindsAndCommandsRunThroughTheChannel() {
        handshake()
        val id = session()
        val bound: CommandResultMsg = await { api.bind(id, source("demo:normal"), null, emptyList()) }
        assertEquals(CommandResultKind.EXECUTED, bound.kind)
        assertEquals(CommandResultKind.EXECUTED, await<CommandResultMsg> { api.play(id) }.kind)
        val rejected: CommandResultMsg = await { api.setSpeed(id, 100.0) }
        assertEquals(CommandResultKind.REJECTED, rejected.kind)
        assertEquals(ErrorCode.INVALID_ARGUMENT.name, rejected.error?.code)
        val unknownVisibility: CommandResultMsg = await { api.setVisibility(id, "VISIBILITY_FROM_THE_FUTURE") }
        assertEquals(ErrorCode.INVALID_ARGUMENT.name, unknownVisibility.error?.code)
        runBlocking {
            withTimeout(5_000) { while (updates.none { it.state?.phase == SessionPhaseMsg.PLAYING }) kotlinx.coroutines.delay(10) }
        }
        val seqs = updates.filter { it.sessionId == id }.map { it.seq }
        assertEquals(seqs.sorted(), seqs)
        assertEquals(seqs.distinct(), seqs)
        val snapshot = await { api.release(id) }
        assertNotNull(snapshot)
        assertEquals(CommandResultKind.SESSION_RELEASED, await<CommandResultMsg> { api.play(id) }.kind)
    }

    @Test
    fun unknownSourceRefIsInvalidArgument() {
        handshake()
        val id = session()
        val result: CommandResultMsg = await { api.bind(id, source("ftp:nope"), null, emptyList()) }
        assertEquals(CommandResultKind.REJECTED, result.kind)
        assertEquals(ErrorCode.INVALID_ARGUMENT.name, result.error?.code)
    }

    @Test
    fun capabilitiesProbeADemoSource() {
        handshake()
        val caps = await { api.capabilities(CapabilityRequestMsg(source("demo:unsupported"))) }
        assertTrue(caps.isDemo)
        assertEquals("UNSUPPORTED", caps.mediaProbe?.playable)
    }

    @Test
    fun editAndExportFlow() {
        handshake()
        val project = api.createEditProject(EditProjectConfigMsg(emptyList(), true, null)).id!!
        val sourceId = await { api.addSource(project, source("demo:normal", "edit-tok")) }.id!!
        val added = await { api.applyEdit(project, EditCommandMsg("AddClip", sourceId = sourceId, inUs = 0, outUs = 2_000_000)) }
        assertEquals(EditResultKind.APPLIED, added.kind)
        assertNotNull(added.createdId)
        val bad = await { api.applyEdit(project, EditCommandMsg("CommandFromTheFuture")) }
        assertEquals(ErrorCode.INVALID_ARGUMENT.name, bad.error?.code)
        val precheck = await { api.checkExport(project, ExportRequestMsg("e-1", "P720", null, "demo:memory")) }
        assertTrue(precheck.ok)
        val exported = await { api.exportProject(project, ExportRequestMsg("e-1", "P720", null, "demo:memory")) }
        assertEquals(ExportResultKind.SUCCEEDED, exported.kind)
        assertEquals(true, exported.media?.isDemo)
        val noSink = await { api.exportProject(project, ExportRequestMsg("e-2", "P720", null, "registered:none")) }
        assertEquals(ExportResultKind.FAILED, noSink.kind)
        assertEquals(ErrorCode.INVALID_ARGUMENT.name, noSink.error?.code)
        val candidates = await { api.detectCandidates(project, 1_000_000) }
        assertEquals(2, candidates.candidates.size)
        assertNotNull(await { api.snapshot(project) })
        val preview = api.previewSession(project).id
        assertNotNull(preview)
        await<Unit> { api.closeEditProject(project) }
        assertEquals(EditResultKind.PROJECT_RELEASED, await { api.undo(project) }.kind)
    }

    @Test
    fun sharedHostKitSessionsAreAdoptedNotReleased() = runBlocking {
        // add-to-app (14 §9.1): one host-owned VideoKit shared by every engine.
        val hostKit = FakeVideoKit(RecordingHostCallbacks())
        VideoKitFlutter.setBackend(
            object : VideoKitBackend {
                override val isDemo: Boolean = true
                override val ownsKits: Boolean = false

                override fun create(context: Context, config: VideoKitConfig): VideoKit = hostKit
            },
        )
        val shared = EngineRuntime(
            "shared",
            object : android.content.ContextWrapper(null) {},
            messenger,
            null,
            MainThreadRunner { it() },
            mainDispatcher = Dispatchers.Unconfined,
        )
        val hostApi = HostApiImpl(shared)
        hostApi.handshake(HandshakeRequest(1, "1.0.0-dev.1", 10_000, 3_000, 3_000, 2_000))
        val hostSession = hostKit.createSession(VideoKitSessionConfig())
        hostSession.bind(FakeMediaSources.demo("normal", "host-tok", MediaKind.VIDEO), null, emptyList())

        assertEquals(ErrorCode.SESSION_RELEASED.name, hostApi.adoptSession(hostSession.sessionId).error?.code)
        VideoKitFlutter.shareSession(hostSession)
        assertEquals(hostSession.sessionId, hostApi.adoptSession(hostSession.sessionId).id)
        assertEquals(CommandResultKind.EXECUTED, hostApi.play(hostSession.sessionId).kind)
        // Dart release only stops observing; the host's session keeps playing.
        assertNotNull(hostApi.release(hostSession.sessionId))
        assertTrue(hostSession.state.value.phase != SessionPhase.RELEASED)
        assertEquals(CommandResultKind.SESSION_RELEASED, hostApi.play(hostSession.sessionId).kind)

        // Engine detach releases what the engine created, never the host's session or the shared kit.
        assertEquals(hostSession.sessionId, hostApi.adoptSession(hostSession.sessionId).id)
        val engineOwnedId = hostApi.createSession(SessionConfigMsg("SINGLE", "VISIBLE", "VISIBLE", true, null)).id!!
        val engineOwned = shared.sessions.getValue(engineOwnedId).session
        shared.close()
        withTimeout(5_000) {
            while (engineOwned.state.value.phase != SessionPhase.RELEASED) kotlinx.coroutines.delay(10)
        }
        assertTrue(hostSession.state.value.phase != SessionPhase.RELEASED)
        assertTrue(hostKit.createSession(VideoKitSessionConfig()).sessionId.isNotEmpty())
        VideoKitFlutter.unshareSession(hostSession.sessionId)
        hostKit.close()
    }
}

/** Collects the messages of a Pigeon event sink. */
private class RecordingEventSink(private val into: MutableList<SessionUpdateMessage>) : io.flutter.plugin.common.EventChannel.EventSink {
    override fun success(event: Any?) {
        (event as? SessionUpdateMessage)?.let(into::add)
    }

    override fun error(errorCode: String?, errorMessage: String?, errorDetails: Any?) = Unit

    override fun endOfStream() = Unit
}
