package com.videokit.testkit.spec

import com.videokit.api.EditCommandResult
import com.videokit.api.EditPhase
import com.videokit.api.EditProjectConfig
import com.videokit.api.MaskRegion
import com.videokit.api.MaskType
import com.videokit.api.SessionPhase
import com.videokit.api.SourceErrorCode
import com.videokit.api.TimeRangeUs
import com.videokit.api.UnsupportedReason
import com.videokit.api.VideoKitCommand
import com.videokit.api.VideoKitCommandResult
import com.videokit.api.VideoKitEditCommand
import com.videokit.api.VideoKitEditProject
import com.videokit.api.VideoKitException
import com.videokit.api.VideoKitSession
import com.videokit.api.VideoKitSessionConfig
import com.videokit.api.Visibility
import com.videokit.testkit.RecordingHostCallbacks
import com.videokit.testkit.SourceBehavior
import com.videokit.testkit.contract.ContractViolation
import com.videokit.testkit.contract.VideoKitContractSubject
import com.videokit.testkit.internal.MiniJson
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.withTimeoutOrNull

/** One case of a `spec/vectors/state-machine` file. */
public class StateMachineVector internal constructor(
    /** Case id. */
    public val id: String,
    internal val from: String,
    internal val media: String,
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
 * 13 §3.2). The runner is platform independent: callers load the JSON text (on the JVM from the
 * `videokit.specDir` system property) and pass it in. A violated expectation throws [ContractViolation].
 */
public object StateMachineVectors {
    /** Kind of the session vector file. */
    public const val SESSION_KIND: String = "session-state-machine"

    /** Kind of the edit project vector file. */
    public const val EDIT_KIND: String = "edit-state-machine"

    private const val WAIT_MS = 15_000L

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
                steps = (case["steps"] as List<*>).map { it as Map<*, *> },
            )
        }
    }

    /** Runs one session vector against a fresh instance from [subject]. */
    public suspend fun runSession(vector: StateMachineVector, subject: VideoKitContractSubject): VectorOutcome {
        val kit = subject.create(RecordingHostCallbacks())
        try {
            val session = kit.createSession(VideoKitSessionConfig())
            if (!prepareSession(session, vector, subject)) return VectorOutcome.SKIPPED
            vector.steps.forEachIndexed { index, step ->
                val result = executeSessionStep(session, step, vector, subject)
                val expect = step["expect"] as Map<*, *>
                val where = "${vector.id} step ${index + 1} (${step["command"]})"
                checkResult(where, sessionResultKind(result), expect["result"] as String)
                (expect["reason"] as? String)?.let { reason ->
                    val actual = (result as? VideoKitCommandResult.Unsupported)?.reason
                    if (actual !=
                        UnsupportedReason.fromWireName(reason)
                    ) {
                        throw ContractViolation("$where: reason expected $reason but was $actual")
                    }
                }
                (expect["phase"] as? String)?.let { phase -> awaitSessionPhase(session, SessionPhase.valueOf(phase), where) }
            }
            return VectorOutcome.PASSED
        } finally {
            kit.close()
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
                val result = executeEditStep(project, step, subject)
                val expect = step["expect"] as Map<*, *>
                checkResult(where, result, expect["result"] as String)
                (expect["phase"] as? String)?.let { phase -> awaitEditPhase(project, EditPhase.valueOf(phase), where) }
            }
            return VectorOutcome.PASSED
        } finally {
            kit.close()
        }
    }

    // ------------------------------------------------------------------ sessions

    private suspend fun prepareSession(session: VideoKitSession, vector: StateMachineVector, subject: VideoKitContractSubject): Boolean {
        val media = if (vector.media == "IMAGE_STATIC") subject.playableImage("vector-image") else subject.playableVideo("vector-video")
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
                val broken = media.copy(
                    sourceFactory = com.videokit.testkit.CountingSourceFactory(SourceBehavior.FailOnOpen(SourceErrorCode.DISCONNECTED)),
                )
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

    private suspend fun bindReady(session: VideoKitSession, media: com.videokit.api.VideoKitMediaSource, vector: StateMachineVector) {
        val result = session.bind(media, null, emptyList())
        if (result != VideoKitCommandResult.Executed) throw ContractViolation("${vector.id} setup: bind returned $result")
        awaitSessionPhase(session, SessionPhase.READY, "${vector.id} setup")
    }

    private suspend fun executeSessionStep(
        session: VideoKitSession,
        step: Map<*, *>,
        vector: StateMachineVector,
        subject: VideoKitContractSubject,
    ): VideoKitCommandResult = when (val command = step["command"] as String) {
        "BIND" -> session.bind(
            if (vector.media == "IMAGE_STATIC") subject.playableImage("vector-rebind") else subject.playableVideo("vector-rebind"),
            null,
            emptyList(),
        )

        "RELEASE" -> session.execute(VideoKitCommand.Release)

        else -> session.execute(sessionCommand(command, step))
    }

    private fun sessionCommand(command: String, step: Map<*, *>): VideoKitCommand = when (command) {
        "PLAY" -> VideoKitCommand.Play
        "PAUSE" -> VideoKitCommand.Pause
        "SEEK_TO" -> VideoKitCommand.SeekTo(step.long("positionUs"))
        "SET_SPEED" -> VideoKitCommand.SetSpeed(step.float("speed"))
        "SET_VOLUME" -> VideoKitCommand.SetVolume(step.float("volume"))
        "SET_MUTED" -> VideoKitCommand.SetMuted(step["muted"] as Boolean)
        "SELECT_AUDIO_TRACK" -> VideoKitCommand.SelectAudioTrack(step["trackId"] as String?)
        "SELECT_SUBTITLE_TRACK" -> VideoKitCommand.SelectSubtitleTrack(step["trackId"] as String?)
        "SET_VISIBILITY" -> VideoKitCommand.SetVisibility(Visibility.valueOf(step["visibility"] as String))
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

    private suspend fun executeEditStep(project: VideoKitEditProject, step: Map<*, *>, subject: VideoKitContractSubject): String {
        val state = project.state.value
        val firstClip = state.timeline.clips.firstOrNull()?.clipId ?: "no-clip"
        val firstMask = state.masks.firstOrNull()?.maskId ?: "no-mask"
        val command: VideoKitEditCommand = when (val name = step["command"] as String) {
            "ADD_SOURCE" -> return try {
                project.addSource(subject.playableVideo("vector-added"))
                "APPLIED"
            } catch (_: VideoKitException) {
                "REJECTED"
            }

            "CLOSE" -> {
                project.close()
                return "APPLIED"
            }

            "UNDO" -> return editResultKind(project.undo())

            "REDO" -> return editResultKind(project.redo())

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

            "START_TRACKING_FIRST_MASK" -> VideoKitEditCommand.StartTracking(firstMask)

            "CANCEL_TRACKING_FIRST_MASK" -> VideoKitEditCommand.CancelTracking(firstMask)

            else -> throw IllegalArgumentException("unknown edit command $name")
        }
        return editResultKind(project.apply(command))
    }

    private fun editResultKind(result: EditCommandResult): String = when (result) {
        is EditCommandResult.Applied -> "APPLIED"
        is EditCommandResult.Rejected -> "REJECTED"
        is EditCommandResult.Unsupported -> "UNSUPPORTED"
        EditCommandResult.ProjectReleased -> "PROJECT_RELEASED"
    }

    private suspend fun awaitEditPhase(project: VideoKitEditProject, phase: EditPhase, where: String) {
        withTimeoutOrNull(WAIT_MS) { project.state.first { it.phase == phase } }
            ?: throw ContractViolation("$where: phase expected $phase but was ${project.state.value.phase}")
    }

    // ------------------------------------------------------------------ helpers

    private fun checkResult(where: String, actual: String, expected: String) {
        if (actual != expected) throw ContractViolation("$where: result expected $expected but was $actual")
    }

    private fun Map<*, *>.long(key: String): Long = (this[key] as Number).toLong()

    private fun Map<*, *>.float(key: String): Float = (this[key] as Number).toFloat()
}
