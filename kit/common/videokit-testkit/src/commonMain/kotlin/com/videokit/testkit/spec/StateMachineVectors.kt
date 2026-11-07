package com.videokit.testkit.spec

import com.videokit.api.ActionPlacement
import com.videokit.api.EditCommandResult
import com.videokit.api.EditPhase
import com.videokit.api.EditProjectConfig
import com.videokit.api.ErrorCode
import com.videokit.api.HostActionResult
import com.videokit.api.HostActionStatus
import com.videokit.api.HostIcon
import com.videokit.api.MaskRegion
import com.videokit.api.MaskType
import com.videokit.api.SessionPhase
import com.videokit.api.SessionVisibility
import com.videokit.api.SourceErrorCode
import com.videokit.api.TimeRangeUs
import com.videokit.api.TrackingKind
import com.videokit.api.UnsupportedReason
import com.videokit.api.VideoKit
import com.videokit.api.VideoKitCommand
import com.videokit.api.VideoKitCommandResult
import com.videokit.api.VideoKitEditCommand
import com.videokit.api.VideoKitEditProject
import com.videokit.api.VideoKitEvent
import com.videokit.api.VideoKitException
import com.videokit.api.VideoKitExportRequest
import com.videokit.api.VideoKitExportResult
import com.videokit.api.VideoKitHostAction
import com.videokit.api.VideoKitMediaSource
import com.videokit.api.VideoKitSession
import com.videokit.api.VideoKitSessionConfig
import com.videokit.api.VideoKitStableError
import com.videokit.testkit.CountingSourceFactory
import com.videokit.testkit.RecordingHostCallbacks
import com.videokit.testkit.RecordingOutputSink
import com.videokit.testkit.SourceBehavior
import com.videokit.testkit.contract.ContractViolation
import com.videokit.testkit.contract.VideoKitContractSubject
import com.videokit.testkit.internal.AtomicCounter
import com.videokit.testkit.internal.MiniJson
import kotlinx.coroutines.CoroutineStart
import kotlinx.coroutines.coroutineScope
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.launch
import kotlinx.coroutines.withTimeoutOrNull

/** One case of a `spec/vectors/state-machine` file. */
public class StateMachineVector internal constructor(
    /** Case id. */
    public val id: String,
    internal val from: String,
    internal val media: String,
    internal val hostActions: List<String>,
    internal val hostActionAnswer: String,
    internal val steps: List<Map<*, *>>,
) {
    override fun toString(): String = id
}

/** Outcome of running one vector. */
public enum class VectorOutcome {
    /** All expectations held. */
    PASSED,

    /** The subject cannot reach the start state (for example ERROR_FATAL); reported, not hidden. */
    SKIPPED,
}

/**
 * Runner of the language independent state machine vectors in `spec/vectors/state-machine/` (02 §4.0.2,
 * 13 §3.2, 04A §1.4). The runner is platform independent: callers load the JSON text (on the JVM from the
 * `videokit.specDir` system property) and pass it in. A violated expectation throws [ContractViolation].
 */
public object StateMachineVectors {
    /** Kind of the session vector file. */
    public const val SESSION_KIND: String = "session-state-machine"

    /** Kind of the edit project vector file. */
    public const val EDIT_KIND: String = "edit-state-machine"

    private const val WAIT_MS = 15_000L
    private const val EVENT_SETTLE_MS = 1_000L
    private const val EVENT_POLL_MS = 10L
    private const val NEAR_END_US = 500_000L

    /** Parses a vector file of [expectedKind]. */
    public fun parse(json: String, expectedKind: String): List<StateMachineVector> {
        val root = MiniJson.parse(json) as? Map<*, *> ?: throw IllegalArgumentException("vector file is not an object")
        require(root["kind"] == expectedKind) { "expected kind $expectedKind but was ${root["kind"]}" }
        require((root["schemaVersion"] as? Long) == 1L) { "unsupported vector schemaVersion ${root["schemaVersion"]}" }
        return (root["cases"] as List<*>).map { item ->
            val case = item as Map<*, *>
            StateMachineVector(
                id = case["id"] as String,
                from = case["from"] as String,
                media = case["media"] as? String ?: "VIDEO",
                hostActions = (case["hostActions"] as? List<*>).orEmpty().map { it as String },
                hostActionAnswer = case["hostActionAnswer"] as? String ?: "COMPLETED",
                steps = (case["steps"] as List<*>).map { it as Map<*, *> },
            )
        }
    }

    /** Runs one session vector against a fresh instance from [subject]. */
    public suspend fun runSession(vector: StateMachineVector, subject: VideoKitContractSubject): VectorOutcome = coroutineScope {
        val callbacks = RecordingHostCallbacks()
        val answer = HostActionStatus.valueOf(vector.hostActionAnswer)
        callbacks.hostActionAnswer = { HostActionResult(answer) }
        val kit = subject.create(callbacks)
        try {
            val session = kit.createSession(VideoKitSessionConfig())
            // Counts PlaybackEnded for `expect.playbackEnded` (04A L1); subscribed before anything can end.
            val ended = AtomicCounter()
            val events = launch(start = CoroutineStart.UNDISPATCHED) {
                session.events.collect { if (it == VideoKitEvent.PlaybackEnded) ended.incrementAndGet() }
            }
            try {
                if (!prepareSession(session, vector, subject)) return@coroutineScope VectorOutcome.SKIPPED
                vector.steps.forEachIndexed { index, step ->
                    val where = "${vector.id} step ${index + 1} (${step["command"]})"
                    val result = executeSessionStep(session, step, vector, subject)
                    val expect = step["expect"] as Map<*, *>
                    checkResult(where, sessionResultKind(result), expect["result"] as String)
                    checkCode(where, (result as? VideoKitCommandResult.Rejected)?.error, expect)
                    (expect["reason"] as? String)?.let { reason ->
                        val actual = (result as? VideoKitCommandResult.Unsupported)?.reason
                        if (actual != UnsupportedReason.fromWireName(reason)) {
                            throw ContractViolation("$where: reason expected $reason but was $actual")
                        }
                    }
                    (expect["hostCalls"] as? Long)?.let { calls ->
                        val actual = callbacks.hostActionRequests.size.toLong()
                        if (actual != calls) throw ContractViolation("$where: host calls expected $calls but was $actual")
                    }
                    (expect["phase"] as? String)?.let { phase -> awaitSessionPhase(session, SessionPhase.valueOf(phase), where) }
                    checkLooping(where, session, expect, ended)
                }
                VectorOutcome.PASSED
            } finally {
                events.cancel()
            }
        } finally {
            kit.close()
        }
    }

    /** `expect.looping`, `expect.atEnd` and `expect.playbackEnded` (04A L1). */
    private suspend fun checkLooping(where: String, session: VideoKitSession, expect: Map<*, *>, ended: AtomicCounter) {
        (expect["looping"] as? Boolean)?.let { looping ->
            val actual = session.state.value.looping
            if (actual != looping) throw ContractViolation("$where: looping expected $looping but was $actual")
        }
        (expect["atEnd"] as? Boolean)?.let { atEnd ->
            val state = session.state.value
            val actual = state.durationUs != null && state.positionUs == state.durationUs
            if (actual != atEnd) {
                throw ContractViolation("$where: atEnd expected $atEnd but position ${state.positionUs} of ${state.durationUs}")
            }
        }
        (expect["playbackEnded"] as? Long)?.let { count ->
            // The event is emitted together with the ENDED state; give the collector a moment to catch up.
            withTimeoutOrNull(EVENT_SETTLE_MS) { while (ended.value < count) delay(EVENT_POLL_MS) }
            if (ended.value != count) throw ContractViolation("$where: PlaybackEnded expected $count times but was ${ended.value}")
        }
    }

    /** Runs one edit project vector against a fresh instance from [subject]. */
    public suspend fun runEdit(vector: StateMachineVector, subject: VideoKitContractSubject): VectorOutcome {
        val kit = subject.create(RecordingHostCallbacks())
        try {
            val project = kit.createEditProject(EditProjectConfig())
            prepareProject(project, vector, subject)
            vector.steps.forEachIndexed { index, step ->
                val where = "${vector.id} step ${index + 1} (${step["command"]})"
                val (kind, error) = executeEditStep(kit, project, step, subject)
                val expect = step["expect"] as Map<*, *>
                checkResult(where, kind, expect["result"] as String)
                checkCode(where, error, expect)
                (expect["phase"] as? String)?.let { phase -> awaitEditPhase(project, EditPhase.valueOf(phase), where) }
            }
            return VectorOutcome.PASSED
        } finally {
            kit.close()
        }
    }

    // ------------------------------------------------------------------ sessions

    /** Media of the case: `VIDEO` (default), `IMAGE_STATIC` or `IMAGE_ANIMATED`; `null` if the subject has none. */
    private fun mediaFor(vector: StateMachineVector, subject: VideoKitContractSubject, token: String): VideoKitMediaSource? =
        when (vector.media) {
            "IMAGE_STATIC" -> subject.playableImage(token)
            "IMAGE_ANIMATED" -> subject.playableAnimatedImage(token)
            "VIDEO" -> subject.playableVideo(token)
            else -> throw IllegalArgumentException("${vector.id}: unknown media ${vector.media}")
        }

    private suspend fun prepareSession(session: VideoKitSession, vector: StateMachineVector, subject: VideoKitContractSubject): Boolean {
        val media = mediaFor(vector, subject, "vector-media") ?: return false
        when (vector.from) {
            "CREATED" -> Unit

            "READY" -> bindReady(session, media, vector)

            "PLAYING" -> {
                bindReady(session, media, vector)
                session.execute(VideoKitCommand.Play)
                awaitSessionPhase(session, SessionPhase.PLAYING, "${vector.id} setup")
            }

            "PAUSED" -> {
                bindReady(session, media, vector)
                session.execute(VideoKitCommand.Play)
                session.execute(VideoKitCommand.Pause)
                awaitSessionPhase(session, SessionPhase.PAUSED, "${vector.id} setup")
            }

            "ENDED" -> {
                bindReady(session, media, vector)
                val duration = session.state.value.durationUs ?: throw ContractViolation("${vector.id}: no duration")
                session.execute(VideoKitCommand.SeekTo(duration - 500_000L))
                session.execute(VideoKitCommand.Play)
                subject.advanceMediaTime(1_000_000L)
                awaitSessionPhase(session, SessionPhase.ENDED, "${vector.id} setup")
            }

            "ERROR_RECOVERABLE" -> {
                val broken = media.copy(sourceFactory = CountingSourceFactory(SourceBehavior.FailOnOpen(SourceErrorCode.DISCONNECTED)))
                session.bind(broken, null, emptyList())
                awaitSessionPhase(session, SessionPhase.ERROR_RECOVERABLE, "${vector.id} setup")
            }

            "ERROR_FATAL" -> if (!subject.driveToFatalError(session)) return false

            "RELEASED" -> {
                bindReady(session, media, vector)
                session.release()
            }

            else -> throw IllegalArgumentException("${vector.id}: unknown start state ${vector.from}")
        }
        return true
    }

    private suspend fun bindReady(session: VideoKitSession, media: VideoKitMediaSource, vector: StateMachineVector) {
        val result = session.bind(media, null, vector.hostActions.map { hostAction(it) })
        if (result != VideoKitCommandResult.Executed) throw ContractViolation("${vector.id} setup: bind returned $result")
        awaitSessionPhase(session, SessionPhase.READY, "${vector.id} setup")
    }

    private fun hostAction(id: String, pending: Boolean = false): VideoKitHostAction = VideoKitHostAction(
        actionId = id,
        labelKey = "action.$id",
        contentDescriptionKey = "action.$id.description",
        icon = HostIcon.BuiltIn(id),
        pending = pending,
        placement = ActionPlacement.PRIMARY_BAR,
    )

    private suspend fun executeSessionStep(
        session: VideoKitSession,
        step: Map<*, *>,
        vector: StateMachineVector,
        subject: VideoKitContractSubject,
    ): VideoKitCommandResult = when (val command = step["command"] as String) {
        "BIND" -> session.bind(
            mediaFor(vector, subject, "vector-rebind") ?: throw ContractViolation("${vector.id}: no ${vector.media} media"),
            null,
            vector.hostActions.map { hostAction(it) },
        )

        "SEEK_NEAR_END" -> {
            // 0.5 s before the end, so one ADVANCE of 1 s crosses it (04A L1 vectors).
            val duration = session.state.value.durationUs ?: throw ContractViolation("${vector.id}: no duration")
            session.execute(VideoKitCommand.SeekTo(duration - NEAR_END_US))
        }

        "ADVANCE" -> {
            subject.advanceMediaTime(step.long("us"))
            VideoKitCommandResult.Executed
        }

        "RELEASE" -> session.execute(VideoKitCommand.Release)

        "REQUEST_HOST_ACTION" -> session.requestHostAction(step["actionId"] as String)

        "HOST_ACTIONS_SETTLED" -> {
            // The host reports that its pending actions finished (pending = false).
            session.updateHostActions(vector.hostActions.map { hostAction(it, pending = false) })
            VideoKitCommandResult.Executed
        }

        else -> session.execute(sessionCommand(command, step))
    }

    private fun sessionCommand(command: String, step: Map<*, *>): VideoKitCommand = when (command) {
        "PLAY" -> VideoKitCommand.Play
        "PAUSE" -> VideoKitCommand.Pause
        "SEEK_TO" -> VideoKitCommand.SeekTo(step.long("positionUs"))
        "SET_SPEED" -> VideoKitCommand.SetSpeed(step.float("speed"))
        "SET_VOLUME" -> VideoKitCommand.SetVolume(step.float("volume"))
        "SET_MUTED" -> VideoKitCommand.SetMuted(step["muted"] as Boolean)
        "SET_LOOPING" -> VideoKitCommand.SetLooping(step["looping"] as Boolean)
        "SELECT_AUDIO_TRACK" -> VideoKitCommand.SelectAudioTrack(step["trackId"] as String?)
        "SELECT_SUBTITLE_TRACK" -> VideoKitCommand.SelectSubtitleTrack(step["trackId"] as String?)
        "SET_VISIBILITY" -> VideoKitCommand.SetVisibility(SessionVisibility.valueOf(step["visibility"] as String))
        "SET_FULLSCREEN" -> VideoKitCommand.SetFullscreen(step["fullscreen"] as Boolean)
        "SET_ACTIVE_AUDIO" -> VideoKitCommand.SetActiveAudio(step["active"] as Boolean, step.long("audioEpoch"))
        "HIDE_CONTENT_FOR_LOCK" -> VideoKitCommand.HideContentForLock(step["hidden"] as Boolean)
        else -> throw IllegalArgumentException("unknown session command $command")
    }

    private fun sessionResultKind(result: VideoKitCommandResult): String = when (result) {
        VideoKitCommandResult.Executed -> "EXECUTED"
        is VideoKitCommandResult.Rejected -> "REJECTED"
        VideoKitCommandResult.Superseded -> "SUPERSEDED"
        is VideoKitCommandResult.Unsupported -> "UNSUPPORTED"
        VideoKitCommandResult.SessionReleased -> "SESSION_RELEASED"
    }

    private suspend fun awaitSessionPhase(session: VideoKitSession, phase: SessionPhase, where: String) {
        withTimeoutOrNull(WAIT_MS) { session.state.first { it.phase == phase } }
            ?: throw ContractViolation("$where: phase expected $phase but was ${session.state.value.phase}")
    }

    // ------------------------------------------------------------------ edit projects

    private suspend fun prepareProject(project: VideoKitEditProject, vector: StateMachineVector, subject: VideoKitContractSubject) {
        when (vector.from) {
            "EMPTY" -> Unit

            "READY_WITH_SOURCE" -> project.addSource(subject.playableVideo("vector-edit"))

            "READY_WITH_CLIP", "RELEASED" -> {
                val token = project.addSource(subject.playableVideo("vector-edit"))
                val result = project.apply(VideoKitEditCommand.AddClip(token.sourceId, 0L, 3_000_000L))
                if (result !is EditCommandResult.Applied) throw ContractViolation("${vector.id} setup: AddClip returned $result")
                if (vector.from == "RELEASED") {
                    project.close()
                    awaitEditPhase(project, EditPhase.RELEASED, "${vector.id} setup")
                }
            }

            else -> throw IllegalArgumentException("${vector.id}: unknown start state ${vector.from}")
        }
    }

    /** Executes one edit step; returns the result kind and the error, if any. */
    private suspend fun executeEditStep(
        kit: VideoKit,
        project: VideoKitEditProject,
        step: Map<*, *>,
        subject: VideoKitContractSubject,
    ): Pair<String, VideoKitStableError?> {
        val state = project.state.value
        val firstClip = state.timeline.clips.firstOrNull()?.clipId ?: "no-clip"
        val firstMask = state.masks.firstOrNull()?.maskId ?: "no-mask"
        val command: VideoKitEditCommand = when (val name = step["command"] as String) {
            "ADD_SOURCE" -> return try {
                project.addSource(subject.playableVideo("vector-added"))
                "APPLIED" to null
            } catch (failure: VideoKitException) {
                "REJECTED" to failure.error
            }

            "CLOSE" -> {
                project.close()
                return "APPLIED" to null
            }

            "EXPORT" -> return when (val result = project.export(VideoKitExportRequest(), RecordingOutputSink())) {
                is VideoKitExportResult.Succeeded -> "SUCCEEDED" to null
                is VideoKitExportResult.Failed -> "FAILED" to result.error
                is VideoKitExportResult.Cancelled -> "CANCELLED" to null
            }

            "RESTORE_FUTURE_SNAPSHOT" -> return try {
                val snapshot = project.snapshot()
                kit.restoreEditProject(snapshot.copy(schemaVersion = snapshot.schemaVersion + 1), EditProjectConfig())
                "APPLIED" to null
            } catch (failure: VideoKitException) {
                "REJECTED" to failure.error
            }

            "DETECT_CANDIDATES" -> return project.detectCandidates(step.long("atUs")).let { result ->
                val error = result.error
                if (error == null && result.candidates.isNotEmpty()) "APPLIED" to null else "REJECTED" to error
            }

            "UNDO" -> return editResult(project.undo())

            "REDO" -> return editResult(project.redo())

            "ADD_CLIP" -> VideoKitEditCommand.AddClip(
                sourceId = if (step["source"] ==
                    "first"
                ) {
                    state.timeline.sources.firstOrNull()?.sourceId ?: "no-source"
                } else {
                    "unknown-source"
                },
                inUs = step.long("inUs"),
                outUs = step.long("outUs"),
                index = (step["index"] as? Long)?.toInt(),
            )

            "SPLIT_FIRST" -> VideoKitEditCommand.SplitAt(firstClip, step.long("atUs"))

            "TRIM_FIRST" -> VideoKitEditCommand.TrimClip(firstClip, step.long("inUs"), step.long("outUs"))

            "REMOVE_FIRST" -> VideoKitEditCommand.RemoveClip(firstClip)

            "MOVE_FIRST" -> VideoKitEditCommand.MoveClip(firstClip, step.long("toIndex").toInt())

            "ADD_MASK" -> VideoKitEditCommand.AddMask(
                type = MaskType.valueOf(step["type"] as String),
                region = MaskRegion(step.float("x"), step.float("y"), step.float("width"), step.float("height")),
                rangeUs = TimeRangeUs(step.long("startUs"), step.long("endUs")),
            )

            "START_TRACKING_FIRST_MASK" -> VideoKitEditCommand.StartTracking(
                firstMask,
                TrackingKind.valueOf(step["kind"] as? String ?: "FACE"),
            )

            "CANCEL_TRACKING_FIRST_MASK" -> VideoKitEditCommand.CancelTracking(firstMask)

            "ACCEPT_TRACKING_RANGE_FIRST_MASK" ->
                VideoKitEditCommand.AcceptTrackingRange(firstMask, TimeRangeUs(step.long("startUs"), step.long("endUs")))

            else -> throw IllegalArgumentException("unknown edit command $name")
        }
        return editResult(project.apply(command))
    }

    private fun editResult(result: EditCommandResult): Pair<String, VideoKitStableError?> = when (result) {
        is EditCommandResult.Applied -> "APPLIED" to null
        is EditCommandResult.Rejected -> "REJECTED" to result.error
        is EditCommandResult.Unsupported -> "UNSUPPORTED" to null
        EditCommandResult.ProjectReleased -> "PROJECT_RELEASED" to null
    }

    private suspend fun awaitEditPhase(project: VideoKitEditProject, phase: EditPhase, where: String) {
        withTimeoutOrNull(WAIT_MS) { project.state.first { it.phase == phase } }
            ?: throw ContractViolation("$where: phase expected $phase but was ${project.state.value.phase}")
    }

    // ------------------------------------------------------------------ helpers

    private fun checkResult(where: String, actual: String, expected: String) {
        if (actual != expected) throw ContractViolation("$where: result expected $expected but was $actual")
    }

    /** `expect.code` (optional): the stable error code of a REJECTED or FAILED result. */
    private fun checkCode(where: String, error: VideoKitStableError?, expect: Map<*, *>) {
        val code = expect["code"] as? String ?: return
        if (error?.code != ErrorCode.fromWireName(code)) throw ContractViolation("$where: code expected $code but was ${error?.code}")
    }

    private fun Map<*, *>.long(key: String): Long = (this[key] as Number).toLong()

    private fun Map<*, *>.float(key: String): Float = (this[key] as Number).toFloat()
}
