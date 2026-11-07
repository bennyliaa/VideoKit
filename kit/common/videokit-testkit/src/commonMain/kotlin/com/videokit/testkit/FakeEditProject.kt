package com.videokit.testkit

import com.videokit.api.CandidateDetectionResult
import com.videokit.api.Clip
import com.videokit.api.CoverageQuality
import com.videokit.api.CoverageRange
import com.videokit.api.CoverageReport
import com.videokit.api.EditCommandResult
import com.videokit.api.EditEstimate
import com.videokit.api.EditPhase
import com.videokit.api.EditProjectConfig
import com.videokit.api.EditSource
import com.videokit.api.ErrorCode
import com.videokit.api.ErrorStage
import com.videokit.api.ExportPrecheck
import com.videokit.api.ExportPreset
import com.videokit.api.ExportProgress
import com.videokit.api.ExportStage
import com.videokit.api.KeyframeSource
import com.videokit.api.MaskKeyframe
import com.videokit.api.MaskRegion
import com.videokit.api.MaskTrack
import com.videokit.api.MaskType
import com.videokit.api.MediaKind
import com.videokit.api.OpenPurpose
import com.videokit.api.OutputOpenRequest
import com.videokit.api.SerializedEditProject
import com.videokit.api.SinkWriteMode
import com.videokit.api.SourceProbe
import com.videokit.api.SourceToken
import com.videokit.api.TimeRangeUs
import com.videokit.api.Timeline
import com.videokit.api.TrackingCandidate
import com.videokit.api.TrackingKind
import com.videokit.api.TrackingRun
import com.videokit.api.TrackingRunStatus
import com.videokit.api.UnsupportedReason
import com.videokit.api.VideoKitAbortReason
import com.videokit.api.VideoKitEditCommand
import com.videokit.api.VideoKitEditEvent
import com.videokit.api.VideoKitEditProject
import com.videokit.api.VideoKitEditState
import com.videokit.api.VideoKitException
import com.videokit.api.VideoKitExportRequest
import com.videokit.api.VideoKitExportResult
import com.videokit.api.VideoKitExportedMedia
import com.videokit.api.VideoKitMediaSource
import com.videokit.api.VideoKitOutputMetadata
import com.videokit.api.VideoKitOutputSink
import com.videokit.api.VideoKitSession
import com.videokit.api.VideoKitStableError
import com.videokit.api.VideoKitWriteHandle
import com.videokit.testkit.internal.AtomicFlag
import com.videokit.testkit.internal.AtomicValue
import com.videokit.testkit.internal.Errors
import com.videokit.testkit.internal.typeName
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.CompletableDeferred
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.CoroutineStart
import kotlinx.coroutines.Deferred
import kotlinx.coroutines.Job
import kotlinx.coroutines.NonCancellable
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.TimeoutCancellationException
import kotlinx.coroutines.async
import kotlinx.coroutines.cancel
import kotlinx.coroutines.cancelAndJoin
import kotlinx.coroutines.channels.BufferOverflow
import kotlinx.coroutines.currentCoroutineContext
import kotlinx.coroutines.delay
import kotlinx.coroutines.ensureActive
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.MutableSharedFlow
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asSharedFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.isActive
import kotlinx.coroutines.launch
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock
import kotlinx.coroutines.withContext
import kotlinx.coroutines.withTimeout

/**
 * In-memory Fake edit project (14 §11.1): timeline, masks, an undo stack, simulated tracking with a
 * coverage report, and staged, cancellable exports that write demo bytes to the host sink.
 * Sources are never modified; partial output is never marked ready.
 */
public class FakeEditProject internal constructor(
    override val projectId: String,
    private val config: EditProjectConfig,
    private val kit: FakeVideoKit,
    restored: ProjectModel?,
) : VideoKitEditProject {
    private val options = kit.options
    private val scope = CoroutineScope(kit.scope.coroutineContext + SupervisorJob(kit.scope.coroutineContext[Job]))
    private val mutex = Mutex()
    private val mutableEvents =
        MutableSharedFlow<VideoKitEditEvent>(extraBufferCapacity = 64, onBufferOverflow = BufferOverflow.DROP_OLDEST)
    private val releasedFlag = AtomicFlag()
    private val releaseDone = CompletableDeferred<Unit>()

    private data class Content(val clips: List<Clip>, val masks: List<MaskTrack>)

    // Guarded by mutex.
    private var phase: EditPhase = if (restored?.sources?.isNotEmpty() == true) EditPhase.READY else EditPhase.CREATED
    private var revision: Long = restored?.revision ?: 0L
    private var sources: List<EditSource> = restored?.sources.orEmpty()
    private var content = Content(restored?.clips.orEmpty(), restored?.masks.orEmpty())
    private var tracking: Map<String, TrackingRun> = restored?.tracking.orEmpty()
    private var exportProgress: ExportProgress? = null
    private var error: VideoKitStableError? = null
    private val createdAtMs: Long = restored?.createdAtMs ?: options.wallClockMs()
    private val undoStack = ArrayDeque<Content>()
    private val redoStack = ArrayDeque<Content>()
    private val liveSources = HashMap<String, VideoKitMediaSource>()
    private val scenarios = HashMap<String, FakeScenario>()
    private val trackingJobs = HashMap<String, Job>()
    private var nextId: Long = 1L + (restored?.let { maxIdIn(it) } ?: 0L)
    private var exportJob: Deferred<VideoKitExportResult>? = null
    private var exportId: String? = null
    private val preview = AtomicValue<FakeSession?>(null)

    private val mutableState = MutableStateFlow(buildState())

    override val state: StateFlow<VideoKitEditState> = mutableState.asStateFlow()

    override val events: Flow<VideoKitEditEvent> = mutableEvents.asSharedFlow()

    // ---------------------------------------------------------------- sources

    override suspend fun addSource(source: VideoKitMediaSource): SourceToken {
        val previousPhase = mutex.withLock {
            requireNotReleased()
            if (phase in BUSY_PHASES) throw VideoKitException(Errors.illegalState(ErrorStage.EDIT, "ADD_SOURCE_IN_$phase"))
            if (source.mediaKind != MediaKind.VIDEO) {
                throw VideoKitException(Errors.of(ErrorCode.UNSUPPORTED_CONTAINER, ErrorStage.EDIT, "EDIT_REQUIRES_VIDEO"))
            }
            phase.also {
                phase = EditPhase.PREPARING
                publish()
            }
        }
        try {
            withTimeout(options.sourceTimeoutMs) {
                val handle = source.sourceFactory.open(OpenPurpose.PROBE)
                try {
                    handle.readAt(0, ByteArray(PROBE_BYTES), 0, PROBE_BYTES)
                } finally {
                    handle.close()
                }
            }
        } catch (failure: Exception) {
            if (failure is CancellationException && failure !is TimeoutCancellationException) {
                withContext(NonCancellable) { mutex.withLock { restorePhase(previousPhase) } }
                throw failure
            }
            val mapped = Errors.fromSourceFailure(failure, ErrorStage.PROBE)
            mutex.withLock {
                restorePhase(previousPhase)
                error = mapped
                publish()
            }
            throw VideoKitException(mapped)
        }
        val scenario = options.scenarioResolver(source)
        val probe = SourceProbe(
            durationUs = scenario.durationUs,
            width = scenario.videoSize.width,
            height = scenario.videoSize.height,
            rotationDeg = 0,
            frameRate = 30f,
            videoCodec = "video/avc",
            audioCodec = if (scenario.audioTracks.isNotEmpty()) "audio/mp4a-latm" else null,
            hasAudio = scenario.audioTracks.isNotEmpty(),
        )
        return mutex.withLock {
            requireNotReleased()
            val restoredSource = sources.firstOrNull { it.mediaToken == source.mediaToken && it.sourceId !in liveSources }
            val sourceId: String
            if (restoredSource != null) {
                sourceId = restoredSource.sourceId
                val mismatch = restoredSource.probe != null && restoredSource.probe != probe
                sources = sources.map { if (it.sourceId == sourceId) it.copy(probe = probe, mismatch = mismatch) else it }
                if (mismatch) mutableEvents.tryEmit(VideoKitEditEvent.SourceMismatch(sourceId))
            } else {
                sourceId = "src-${nextId++}"
                sources = sources + EditSource(sourceId, source.mediaToken, source.displayName, probe)
            }
            liveSources[sourceId] = source
            scenarios[sourceId] = scenario
            revision++
            phase = EditPhase.READY
            error = null
            mutableEvents.tryEmit(VideoKitEditEvent.SourceProbed(sourceId))
            publish()
            SourceToken(sourceId)
        }
    }

    private fun restorePhase(previous: EditPhase) {
        phase = if (previous == EditPhase.PREPARING) EditPhase.READY else previous
        if (phase == EditPhase.READY && sources.isEmpty()) phase = EditPhase.CREATED
        publish()
    }

    // ---------------------------------------------------------------- commands

    override suspend fun apply(command: VideoKitEditCommand): EditCommandResult = mutex.withLock {
        if (releasedFlag.value) return@withLock EditCommandResult.ProjectReleased
        if (phase == EditPhase.TRACKING && command !is VideoKitEditCommand.CancelTracking) {
            return@withLock rejected("${commandName(command)}_IN_TRACKING")
        }
        if (phase in setOf(EditPhase.PREPARING, EditPhase.EXPORTING, EditPhase.CANCELLING)) {
            return@withLock rejected("${commandName(command)}_IN_$phase")
        }
        when (command) {
            is VideoKitEditCommand.StartTracking -> startTrackingLocked(command)

            is VideoKitEditCommand.CancelTracking -> cancelTrackingLocked(command.maskId)

            else -> when (val outcome = edit(command)) {
                is Edit.Ok -> commitLocked(outcome.content, outcome.createdId)
                is Edit.Fail -> outcome.result
            }
        }
    }

    private sealed interface Edit {
        data class Ok(val content: Content, val createdId: String? = null) : Edit

        data class Fail(val result: EditCommandResult) : Edit
    }

    private fun edit(command: VideoKitEditCommand): Edit {
        val clips = content.clips
        val masks = content.masks
        fun fail(what: String) = Edit.Fail(EditCommandResult.Rejected(Errors.invalidArgument(ErrorStage.EDIT, what)))
        fun maskOf(id: String) = masks.firstOrNull { it.maskId == id }
        fun replaceMask(mask: MaskTrack) = Edit.Ok(content.copy(masks = masks.map { if (it.maskId == mask.maskId) mask else it }))
        return when (command) {
            is VideoKitEditCommand.AddClip -> {
                val duration = sources.firstOrNull { it.sourceId == command.sourceId }?.probe?.durationUs ?: return fail("UNKNOWN_SOURCE")
                if (command.inUs < 0 || command.inUs >= command.outUs || command.outUs > duration) return fail("CLIP_RANGE")
                val index = command.index ?: clips.size
                if (index !in 0..clips.size) return fail("CLIP_INDEX")
                val clip = Clip("clip-${nextId++}", command.sourceId, command.inUs, command.outUs)
                Edit.Ok(content.copy(clips = clips.toMutableList().apply { add(index, clip) }), createdId = clip.clipId)
            }

            is VideoKitEditCommand.SplitAt -> {
                val index = clips.indexOfFirst { it.clipId == command.clipId }.takeIf { it >= 0 } ?: return fail("UNKNOWN_CLIP")
                val clip = clips[index]
                if (command.atUs <= clip.inUs || command.atUs >= clip.outUs) return fail("SPLIT_POINT")
                val first = clip.copy(outUs = command.atUs)
                val second = Clip("clip-${nextId++}", clip.sourceId, command.atUs, clip.outUs)
                Edit.Ok(
                    content.copy(
                        clips = clips.toMutableList().apply {
                            set(index, first)
                            add(index + 1, second)
                        },
                    ),
                    createdId = second.clipId,
                )
            }

            is VideoKitEditCommand.TrimClip -> {
                val clip = clips.firstOrNull { it.clipId == command.clipId } ?: return fail("UNKNOWN_CLIP")
                val duration = sources.firstOrNull { it.sourceId == clip.sourceId }?.probe?.durationUs ?: return fail("UNKNOWN_SOURCE")
                if (command.inUs < 0 || command.inUs >= command.outUs || command.outUs > duration) return fail("CLIP_RANGE")
                Edit.Ok(
                    content.copy(
                        clips = clips.map {
                            if (it.clipId ==
                                clip.clipId
                            ) {
                                it.copy(inUs = command.inUs, outUs = command.outUs)
                            } else {
                                it
                            }
                        },
                    ),
                )
            }

            is VideoKitEditCommand.RemoveClip -> {
                if (clips.none { it.clipId == command.clipId }) return fail("UNKNOWN_CLIP")
                Edit.Ok(content.copy(clips = clips.filterNot { it.clipId == command.clipId }))
            }

            is VideoKitEditCommand.MoveClip -> {
                val index = clips.indexOfFirst { it.clipId == command.clipId }.takeIf { it >= 0 } ?: return fail("UNKNOWN_CLIP")
                if (command.toIndex !in clips.indices) return fail("CLIP_INDEX")
                Edit.Ok(content.copy(clips = clips.toMutableList().apply { add(command.toIndex, removeAt(index)) }))
            }

            is VideoKitEditCommand.AddMask -> {
                val timelineDuration = clips.sumOf { it.durationUs }
                if (!command.region.isValid) return fail("MASK_REGION")
                if (!command.rangeUs.isValid || command.rangeUs.endUs > timelineDuration) return fail("MASK_RANGE")
                if (!command.strength.isFinite() || command.strength !in 0f..1f) return fail("MASK_STRENGTH")
                val mask = MaskTrack(
                    maskId = "mask-${nextId++}",
                    type = command.type,
                    style = command.style,
                    strength = command.strength,
                    rangeUs = command.rangeUs,
                    keyframes = listOf(MaskKeyframe(command.rangeUs.startUs, command.region, KeyframeSource.USER)),
                )
                Edit.Ok(content.copy(masks = masks + mask), createdId = mask.maskId)
            }

            is VideoKitEditCommand.UpdateMaskKeyframe -> {
                val mask = maskOf(command.maskId) ?: return fail("UNKNOWN_MASK")
                if (!command.region.isValid) return fail("MASK_REGION")
                if (command.atUs < mask.rangeUs.startUs || command.atUs > mask.rangeUs.endUs) return fail("KEYFRAME_TIME")
                replaceMask(mask.withKeyframe(MaskKeyframe(command.atUs, command.region, KeyframeSource.USER)))
            }

            is VideoKitEditCommand.CorrectTracking -> {
                val mask = maskOf(command.maskId) ?: return fail("UNKNOWN_MASK")
                if (mask.type == MaskType.MANUAL) return fail("MASK_NOT_TRACKED")
                if (!command.region.isValid) return fail("MASK_REGION")
                if (command.atUs < mask.rangeUs.startUs || command.atUs > mask.rangeUs.endUs) return fail("KEYFRAME_TIME")
                replaceMask(mask.withKeyframe(MaskKeyframe(command.atUs, command.region, KeyframeSource.USER)))
            }

            is VideoKitEditCommand.RemoveMaskKeyframe -> {
                val mask = maskOf(command.maskId) ?: return fail("UNKNOWN_MASK")
                if (mask.keyframes.none { it.atUs == command.atUs }) return fail("UNKNOWN_KEYFRAME")
                if (mask.keyframes.size <= 1) return fail("LAST_KEYFRAME")
                replaceMask(mask.copy(keyframes = mask.keyframes.filterNot { it.atUs == command.atUs }))
            }

            is VideoKitEditCommand.SetMaskStyle -> {
                val mask = maskOf(command.maskId) ?: return fail("UNKNOWN_MASK")
                if (!command.strength.isFinite() || command.strength !in 0f..1f) return fail("MASK_STRENGTH")
                replaceMask(mask.copy(style = command.style, strength = command.strength))
            }

            is VideoKitEditCommand.SetMaskEnabled -> {
                val mask = maskOf(command.maskId) ?: return fail("UNKNOWN_MASK")
                replaceMask(mask.copy(enabled = command.enabled))
            }

            is VideoKitEditCommand.RemoveMask -> {
                if (maskOf(command.maskId) == null) return fail("UNKNOWN_MASK")
                trackingJobs.remove(command.maskId)?.cancel()
                tracking = tracking - command.maskId
                Edit.Ok(content.copy(masks = masks.filterNot { it.maskId == command.maskId }))
            }

            is VideoKitEditCommand.AcceptTrackingRange -> {
                val mask = maskOf(command.maskId) ?: return fail("UNKNOWN_MASK")
                if (mask.type == MaskType.MANUAL) return fail("MASK_NOT_TRACKED")
                val range = command.rangeUs
                if (!range.isValid || range.startUs < mask.rangeUs.startUs || range.endUs > mask.rangeUs.endUs) return fail("ACCEPT_RANGE")
                replaceMask(mask.copy(acceptedRangesUs = (mask.acceptedRangesUs + range).sortedBy { it.startUs }))
            }

            is VideoKitEditCommand.StartTracking, is VideoKitEditCommand.CancelTracking -> error("handled by apply")
        }
    }

    private fun commitLocked(newContent: Content, createdId: String? = null): EditCommandResult {
        undoStack.addLast(content)
        while (undoStack.size > UNDO_LIMIT) undoStack.removeFirst()
        redoStack.clear()
        content = newContent
        return bumpLocked(createdId)
    }

    private fun bumpLocked(createdId: String? = null): EditCommandResult {
        revision++
        if (phase in FINISHED_PHASES || (phase == EditPhase.CREATED && sources.isNotEmpty())) phase = EditPhase.READY
        error = null
        publish()
        syncPreview()
        return EditCommandResult.Applied(revision, createdId)
    }

    override suspend fun undo(): EditCommandResult = mutex.withLock {
        if (releasedFlag.value) return@withLock EditCommandResult.ProjectReleased
        if (phase in BUSY_PHASES) return@withLock rejected("UNDO_IN_$phase")
        val previous = undoStack.removeLastOrNull() ?: return@withLock rejected("NOTHING_TO_UNDO")
        redoStack.addLast(content)
        content = previous
        bumpLocked()
    }

    override suspend fun redo(): EditCommandResult = mutex.withLock {
        if (releasedFlag.value) return@withLock EditCommandResult.ProjectReleased
        if (phase in BUSY_PHASES) return@withLock rejected("REDO_IN_$phase")
        val next = redoStack.removeLastOrNull() ?: return@withLock rejected("NOTHING_TO_REDO")
        undoStack.addLast(content)
        content = next
        bumpLocked()
    }

    // ---------------------------------------------------------------- tracking

    private fun startTrackingLocked(command: VideoKitEditCommand.StartTracking): EditCommandResult {
        val maskId = command.maskId
        if (command.seedRegion?.isValid == false) return rejectedArgument("SEED_REGION")
        val mask = content.masks.firstOrNull { it.maskId == maskId } ?: return rejectedArgument("UNKNOWN_MASK")
        if (mask.type == MaskType.MANUAL) return rejectedArgument("MASK_NOT_TRACKABLE")
        if (!config.trackingAllowed) return EditCommandResult.Unsupported(UnsupportedReason.HOST_DISABLED)
        if (!options.trackingAvailable) return EditCommandResult.Unsupported(UnsupportedReason.MODULE_NOT_INSTALLED)
        if (trackingJobs.containsKey(maskId)) return rejected("TRACKING_ALREADY_RUNNING")
        phase = EditPhase.TRACKING
        tracking = tracking + (maskId to TrackingRun(maskId, TrackingRunStatus.RUNNING, progress = 0f))
        val scenario = content.clips.firstOrNull()?.let { scenarios[it.sourceId] } ?: FakeScenario.normal()
        trackingJobs[maskId] = scope.launch { runTracking(maskId, scenario) }
        revision++
        publish()
        return EditCommandResult.Applied(revision)
    }

    private suspend fun runTracking(maskId: String, scenario: FakeScenario) {
        for (step in 1..TRACKING_STEPS) {
            delay(scenario.trackingStepMs)
            mutex.withLock {
                tracking = tracking + (maskId to TrackingRun(maskId, TrackingRunStatus.RUNNING, progress = step / TRACKING_STEPS.toFloat()))
                publish()
            }
        }
        mutex.withLock {
            trackingJobs.remove(maskId)
            val mask = content.masks.firstOrNull { it.maskId == maskId } ?: return
            val coverage = coverageFor(mask.rangeUs, scenario.trackingLostRanges)
            val base = mask.keyframes.first().region
            val trackerKeyframes = generateSequence(mask.rangeUs.startUs + TRACKING_KEYFRAME_US) { it + TRACKING_KEYFRAME_US }
                .takeWhile { it < mask.rangeUs.endUs }
                .filter { at -> mask.keyframes.none { it.atUs == at } }
                .mapIndexed { index, at ->
                    val drift = ((index + 1) * 0.01f).coerceAtMost(1f - base.x - base.width)
                    val quality = coverage.ranges.firstOrNull { at in it.rangeUs }?.quality ?: CoverageQuality.TRACKED
                    MaskKeyframe(at, base.copy(x = base.x + drift.coerceAtLeast(0f)), KeyframeSource.TRACKER, quality)
                }
                .toList()
            val updated = mask.copy(keyframes = (mask.keyframes + trackerKeyframes).sortedBy { it.atUs })
            undoStack.addLast(content)
            redoStack.clear()
            content = content.copy(masks = content.masks.map { if (it.maskId == maskId) updated else it })
            tracking = tracking + (maskId to TrackingRun(maskId, TrackingRunStatus.COMPLETED, progress = 1f, coverage = coverage))
            coverage.ranges.filter { it.quality == CoverageQuality.LOST }.forEach {
                mutableEvents.tryEmit(VideoKitEditEvent.TrackingLost(maskId, it.rangeUs))
            }
            revision++
            if (trackingJobs.isEmpty() && phase == EditPhase.TRACKING) phase = EditPhase.READY
            publish()
        }
    }

    private fun cancelTrackingLocked(maskId: String): EditCommandResult {
        val job = trackingJobs.remove(maskId) ?: return rejected("TRACKING_NOT_RUNNING")
        job.cancel()
        tracking = tracking + (maskId to TrackingRun(maskId, TrackingRunStatus.CANCELLED))
        if (trackingJobs.isEmpty() && phase == EditPhase.TRACKING) phase = EditPhase.READY
        revision++
        publish()
        return EditCommandResult.Applied(revision)
    }

    private fun coverageFor(range: TimeRangeUs, lost: List<TimeRangeUs>): CoverageReport {
        val cuts = lost.mapNotNull { l ->
            val start = maxOf(l.startUs, range.startUs)
            val end = minOf(l.endUs, range.endUs)
            if (start < end) TimeRangeUs(start, end) else null
        }.sortedBy { it.startUs }
        val ranges = mutableListOf<CoverageRange>()
        var cursor = range.startUs
        cuts.forEach { cut ->
            if (cut.startUs > cursor) ranges += CoverageRange(TimeRangeUs(cursor, cut.startUs), CoverageQuality.TRACKED)
            ranges += CoverageRange(cut, CoverageQuality.LOST)
            cursor = maxOf(cursor, cut.endUs)
        }
        if (cursor < range.endUs) ranges += CoverageRange(TimeRangeUs(cursor, range.endUs), CoverageQuality.TRACKED)
        return CoverageReport(ranges)
    }

    // ---------------------------------------------------------------- snapshot & preview

    /**
     * Demo candidate detection (04A I10): two deterministic face candidates at any time inside the timeline.
     * Errors are returned in the result: tracking unavailable or disallowed, or [atUs] outside the timeline.
     */
    override suspend fun detectCandidates(atUs: Long): CandidateDetectionResult = mutex.withLock {
        if (releasedFlag.value) {
            return@withLock CandidateDetectionResult(error = Errors.of(ErrorCode.SESSION_RELEASED, ErrorStage.TRACKING, "PROJECT_RELEASED"))
        }
        if (!options.trackingAvailable || !config.trackingAllowed) {
            return@withLock CandidateDetectionResult(error = Errors.of(ErrorCode.TRACKING_MODEL_UNAVAILABLE, ErrorStage.TRACKING, "DEMO"))
        }
        val duration = content.clips.sumOf { it.durationUs }
        if (atUs < 0 || atUs >= duration) {
            return@withLock CandidateDetectionResult(error = Errors.invalidArgument(ErrorStage.TRACKING, "DETECT_TIME"))
        }
        val drift = (atUs % 4_000_000L) / 4_000_000f * 0.1f
        CandidateDetectionResult(
            candidates = listOf(
                TrackingCandidate("candidate-1", TrackingKind.FACE, MaskRegion(0.2f + drift, 0.25f, 0.15f, 0.2f), confidence = 0.93f),
                TrackingCandidate("candidate-2", TrackingKind.FACE, MaskRegion(0.6f - drift, 0.3f, 0.12f, 0.16f), confidence = 0.71f),
            ),
        )
    }

    override suspend fun snapshot(): SerializedEditProject = mutex.withLock {
        ProjectCodec.encode(
            ProjectModel(
                projectId = projectId,
                revision = revision,
                createdAtMs = createdAtMs,
                updatedAtMs = options.wallClockMs(),
                sources = sources.map { it.copy(mismatch = false) },
                clips = content.clips,
                masks = content.masks,
                tracking = tracking,
                exportPreset = null,
            ),
        )
    }

    override fun previewSession(): VideoKitSession {
        preview.value?.let { return it }
        if (releasedFlag.value) throw VideoKitException(Errors.of(ErrorCode.SESSION_RELEASED, ErrorStage.EDIT, "PROJECT_RELEASED"))
        val session = kit.newPreviewSession()
        if (!preview.compareAndSet(null, session)) {
            // Another caller won the race; drop the extra session.
            session.close()
            return preview.value ?: throw VideoKitException(Errors.of(ErrorCode.SESSION_RELEASED, ErrorStage.EDIT, "PROJECT_RELEASED"))
        }
        scope.launch {
            session.bind(FakeMediaSources.video("project:$projectId"), null, emptyList())
            syncPreview()
        }
        return session
    }

    private fun syncPreview() {
        val session = preview.value ?: return
        val duration = content.clips.sumOf { it.durationUs }.coerceAtLeast(1L)
        scope.launch { session.updatePreviewDuration(duration) }
    }

    // ---------------------------------------------------------------- export

    override suspend fun checkExport(request: VideoKitExportRequest, sink: VideoKitOutputSink): ExportPrecheck = mutex.withLock {
        precheckLocked(request, sink)
    }

    private fun precheckLocked(request: VideoKitExportRequest, sink: VideoKitOutputSink): ExportPrecheck {
        val problems = mutableListOf<VideoKitStableError>()
        val warnings = mutableListOf<String>()
        if (releasedFlag.value) problems += Errors.of(ErrorCode.SESSION_RELEASED, ErrorStage.EXPORT, "PROJECT_RELEASED")
        if (phase !in EXPORTABLE_PHASES) problems += Errors.illegalState(ErrorStage.EXPORT, "EXPORT_IN_$phase")
        if (content.clips.isEmpty()) problems += Errors.of(ErrorCode.EXPORT_FAILED, ErrorStage.EXPORT, "EMPTY_TIMELINE")
        if (content.clips.any { it.sourceId !in liveSources }) {
            problems +=
                Errors.of(ErrorCode.SOURCE_NOT_FOUND, ErrorStage.EXPORT, "SOURCE_NOT_ATTACHED")
        }
        if (config.allowedPresets.isNotEmpty() && request.preset !in config.allowedPresets) {
            problems += Errors.of(ErrorCode.OUTPUT_CAPABILITY_UNSUPPORTED, ErrorStage.EXPORT, "PRESET_NOT_ALLOWED")
        }
        val caps = sink.capabilities
        val mode = when {
            caps.fileDescriptor -> SinkWriteMode.FILE_DESCRIPTOR
            caps.randomWrite -> SinkWriteMode.RANDOM_WRITE
            caps.sequentialWrite -> SinkWriteMode.SEQUENTIAL
            else -> null
        }
        if (mode == null) problems += Errors.of(ErrorCode.OUTPUT_CAPABILITY_UNSUPPORTED, ErrorStage.SINK, "NO_WRITE_MODE")
        val estimate = estimateFor(request.preset)
        val free = caps.knownFreeSpaceBytes
        val needed = estimate.sizeBytes
        if (free != null && needed != null && free < needed) {
            problems += Errors.of(ErrorCode.OUTPUT_SPACE_INSUFFICIENT, ErrorStage.SINK, "FREE_SPACE")
        }
        val uncovered = mutableListOf<CoverageRange>()
        content.masks.filter { it.type != MaskType.MANUAL && it.enabled }.forEach { mask ->
            tracking[mask.maskId]?.coverage?.ranges.orEmpty()
                .filter { range -> range.quality != CoverageQuality.TRACKED && !mask.isAccepted(range.rangeUs) }
                .forEach { range -> uncovered += range.copy(maskId = mask.maskId) }
            val run = tracking[mask.maskId]
            when {
                run?.status != TrackingRunStatus.COMPLETED -> warnings += "TRACKING_INCOMPLETE:${mask.maskId}"

                run.coverage?.ranges?.any { it.quality == CoverageQuality.LOST } == true -> {
                    val lost = run.coverage?.ranges.orEmpty().filter { it.quality == CoverageQuality.LOST }.map { it.rangeUs }
                    val allAccepted = lost.all { range ->
                        mask.isAccepted(range)
                    }
                    warnings += if (allAccepted) "TRACKING_COVERAGE_ACCEPTED:${mask.maskId}" else "TRACKING_LOST_RANGES:${mask.maskId}"
                }
            }
        }
        return ExportPrecheck(
            ok = problems.isEmpty(),
            writeMode = mode.takeIf {
                problems.isEmpty()
            },
            estimate = estimate,
            problems = problems,
            warnings = warnings,
            uncoveredRanges = uncovered,
        )
    }

    private fun estimateFor(preset: ExportPreset): EditEstimate {
        val durationUs = content.clips.sumOf { it.durationUs }
        val videoBitsPerSecond = when (preset) {
            ExportPreset.ORIGINAL -> 16_000_000L
            ExportPreset.P1080 -> 10_000_000L
            ExportPreset.P720 -> 5_000_000L
        }
        val bytes = durationUs * (videoBitsPerSecond + AUDIO_BITS_PER_SECOND) / 8L / 1_000_000L + CONTAINER_OVERHEAD_BYTES
        return EditEstimate(durationUs, bytes)
    }

    override suspend fun export(request: VideoKitExportRequest, sink: VideoKitOutputSink): VideoKitExportResult {
        val job = mutex.withLock {
            requireNotReleased()
            if (exportJob != null) {
                return VideoKitExportResult.Failed(request.exportId, Errors.illegalState(ErrorStage.EXPORT, "EXPORT_IN_PROGRESS"))
            }
            val precheck = precheckLocked(request, sink)
            if (!precheck.ok) return VideoKitExportResult.Failed(request.exportId, precheck.problems.first(), ExportStage.PREPARING)
            phase = EditPhase.EXPORTING
            error = null
            exportProgress = ExportProgress(request.exportId, ExportStage.PREPARING)
            mutableEvents.tryEmit(VideoKitEditEvent.ExportStageChanged(request.exportId, ExportStage.PREPARING))
            publish()
            scope.async(start = CoroutineStart.LAZY) { runExport(request, sink, precheck) }.also {
                exportJob = it
                exportId = request.exportId
            }
        }
        job.start()
        return try {
            job.await()
        } catch (cancelled: CancellationException) {
            if (currentCoroutineContext().isActive) {
                // The export itself was cancelled (cancelExport or release), not the caller: a result, not a throw (04A I5).
                withContext(NonCancellable) {
                    job.join()
                    finishIfCancelledBeforeStart(request.exportId)
                }
                return VideoKitExportResult.Cancelled(request.exportId, partialOutputRemoved = true)
            }
            withContext(NonCancellable) {
                job.cancelAndJoin()
                finishIfCancelledBeforeStart(request.exportId)
            }
            throw cancelled
        }
    }

    /** A lazily started export that was cancelled before its body ran never opened the sink; finish its state here. */
    private suspend fun finishIfCancelledBeforeStart(id: String) {
        mutex.withLock {
            if (exportId != id) return
            exportJob = null
            exportId = null
            if (!releasedFlag.value) {
                phase = EditPhase.CANCELLED
                error = Errors.of(ErrorCode.CANCELLED, ErrorStage.EXPORT, "EXPORT_CANCELLED")
            }
            mutableEvents.tryEmit(VideoKitEditEvent.ExportCancelled(id))
            publish()
        }
    }

    private suspend fun runExport(
        request: VideoKitExportRequest,
        sink: VideoKitOutputSink,
        precheck: ExportPrecheck,
    ): VideoKitExportResult {
        val scenario = content.clips.firstOrNull()?.let { scenarios[it.sourceId] } ?: FakeScenario.normal()
        val failure = scenario.exportFailure
        val durationUs = precheck.estimate.durationUs
        val mode = precheck.writeMode ?: SinkWriteMode.SEQUENTIAL
        var handle: VideoKitWriteHandle? = null
        var written = 0L
        var currentStage = ExportStage.PREPARING
        suspend fun stage(stage: ExportStage, fraction: Float?, processedUs: Long) {
            currentStage = stage
            mutex.withLock {
                val stageChanged = exportProgress?.stage != stage
                exportProgress = ExportProgress(
                    exportId = request.exportId,
                    stage = stage,
                    fraction = fraction,
                    processedUs = processedUs,
                    outputBytes = written,
                    cancellable = stage != ExportStage.WRITING,
                )
                if (stageChanged) mutableEvents.tryEmit(VideoKitEditEvent.ExportStageChanged(request.exportId, stage))
                publish()
            }
            if (failure?.stage == stage) {
                val failureStage = if (failure.code.name.startsWith("OUTPUT")) ErrorStage.SINK else ErrorStage.EXPORT
                throw VideoKitException(Errors.of(failure.code, failureStage, "SCENARIO"))
            }
        }
        try {
            handle = sink.openTemporary(
                OutputOpenRequest(request.exportId, "video/mp4", "mp4", mode, precheck.estimate.sizeBytes, request.fileNameHint),
            )
            stage(ExportStage.PREPARING, 0f, 0L)
            delay(scenario.exportStageDelayMs)
            if (content.masks.any { it.type != MaskType.MANUAL && it.enabled }) {
                stage(ExportStage.TRACKING, 0f, 0L)
                delay(scenario.exportStageDelayMs)
            }
            for (chunk in 0 until EXPORT_CHUNKS) {
                stage(ExportStage.ENCODING, chunk / EXPORT_CHUNKS.toFloat(), durationUs * chunk / EXPORT_CHUNKS)
                val payload = demoChunk(request.exportId, chunk)
                handle.write(payload, 0, payload.size)
                written += payload.size
                delay(scenario.exportStageDelayMs / EXPORT_CHUNKS)
            }
            if (mode == SinkWriteMode.RANDOM_WRITE) handle.writeAt(0L, DEMO_HEADER, 0, DEMO_HEADER.size)
            handle.flush()
            stage(ExportStage.VERIFYING, 1f, durationUs)
            delay(scenario.exportStageDelayMs)
            stage(ExportStage.WRITING, 1f, durationUs)
            currentCoroutineContext().ensureActive()
            val size = outputSize(request.preset)
            val hasAudio = sources.any { it.probe?.hasAudio == true }
            val metadata = VideoKitOutputMetadata(
                container = "mp4",
                extension = "mp4",
                videoCodec = "video/avc",
                audioCodec = if (hasAudio) "audio/mp4a-latm" else null,
                width = size.first,
                height = size.second,
                rotationDeg = 0,
                durationUs = durationUs,
                sizeBytes = written,
                frameRate = 30f,
                audioPresent = hasAudio,
                isDemo = true,
            )
            val token = sink.markReady(handle.handleId, metadata)
            val media = VideoKitExportedMedia(
                outputToken = token,
                container = metadata.container,
                extension = metadata.extension,
                videoCodec = metadata.videoCodec,
                audioCodec = metadata.audioCodec,
                width = metadata.width,
                height = metadata.height,
                rotationDeg = metadata.rotationDeg,
                durationUs = metadata.durationUs,
                sizeBytes = metadata.sizeBytes,
                frameRate = metadata.frameRate,
                audioPresent = metadata.audioPresent,
                createdAtEpochMs = options.wallClockMs(),
                sourceTokens = content.clips
                    .mapNotNull { clip -> sources.firstOrNull { it.sourceId == clip.sourceId }?.mediaToken }
                    .distinct(),
                editProjectId = projectId,
                exportPreset = request.preset,
                warnings = listOf(FakeScenario.DEMO_OUTPUT_WARNING) + precheck.warnings,
                isDemo = true,
            )
            val result = VideoKitExportResult.Succeeded(request.exportId, media)
            mutex.withLock {
                phase = EditPhase.COMPLETED
                exportJob = null
                exportId = null
                mutableEvents.tryEmit(VideoKitEditEvent.ExportCompleted(result))
                publish()
            }
            return result
        } catch (cancelled: CancellationException) {
            withContext(NonCancellable) {
                val releasing = releasedFlag.value
                mutex.withLock {
                    if (!releasing) phase = EditPhase.CANCELLING
                    publish()
                }
                if (!releasing) delay(scenario.exportCancelDelayMs)
                handle?.let {
                    runCatching { sink.abort(it.handleId, if (releasing) VideoKitAbortReason.RELEASED else VideoKitAbortReason.CANCELLED) }
                }
                mutex.withLock {
                    if (!releasing) {
                        phase = EditPhase.CANCELLED
                        error = Errors.of(ErrorCode.CANCELLED, ErrorStage.EXPORT, "EXPORT_CANCELLED")
                    }
                    exportJob = null
                    exportId = null
                    mutableEvents.tryEmit(VideoKitEditEvent.ExportCancelled(request.exportId))
                    publish()
                }
            }
            throw cancelled
        } catch (failed: Exception) {
            val mapped = if (failed is VideoKitException) failed.error else Errors.fromSinkFailure(failed)
            withContext(NonCancellable) {
                handle?.let { runCatching { sink.abort(it.handleId, VideoKitAbortReason.EXPORT_FAILED) } }
                mutex.withLock {
                    phase = EditPhase.FAILED
                    error = mapped
                    exportJob = null
                    exportId = null
                    mutableEvents.tryEmit(VideoKitEditEvent.ExportFailed(request.exportId, mapped))
                    publish()
                }
            }
            return VideoKitExportResult.Failed(request.exportId, mapped, currentStage)
        } finally {
            handle?.let { runCatching { it.close() } }
        }
    }

    override suspend fun cancelExport(exportId: String) {
        val job = mutex.withLock { exportJob?.takeIf { this.exportId == exportId } } ?: return
        job.cancel()
        withContext(NonCancellable) { job.join() }
    }

    private fun outputSize(preset: ExportPreset): Pair<Int, Int> {
        val probe = content.clips.firstOrNull()?.let { clip -> sources.firstOrNull { it.sourceId == clip.sourceId }?.probe }
        val width = probe?.width ?: 1920
        val height = probe?.height ?: 1080
        val longEdge = when (preset) {
            ExportPreset.ORIGINAL -> return width to height
            ExportPreset.P1080 -> 1920
            ExportPreset.P720 -> 1280
        }
        val scale = longEdge / maxOf(width, height).toFloat()
        if (scale >= 1f) return width to height
        return (width * scale).toInt() / 2 * 2 to (height * scale).toInt() / 2 * 2
    }

    // ---------------------------------------------------------------- release

    override fun close() {
        if (!releasedFlag.setOnce()) return
        kit.scope.launch { releaseInternal() }
    }

    /** Releases the project and waits until all resources are released. Idempotent. */
    public suspend fun releaseAndAwait() {
        if (releasedFlag.setOnce()) releaseInternal() else releaseDone.await()
    }

    private suspend fun releaseInternal() {
        withContext(NonCancellable) {
            val (jobs, export) = mutex.withLock {
                phase = EditPhase.RELEASING
                publish()
                trackingJobs.values.toList().also { trackingJobs.clear() } to exportJob
            }
            jobs.forEach { it.cancelAndJoin() }
            export?.cancelAndJoin()
            preview.value?.release()
            mutex.withLock {
                liveSources.clear()
                phase = EditPhase.RELEASED
                publish()
            }
            mutableEvents.tryEmit(VideoKitEditEvent.ResourcesReleased)
            kit.onProjectReleased(projectId)
            releaseDone.complete(Unit)
        }
        scope.cancel()
    }

    // ---------------------------------------------------------------- helpers

    private fun requireNotReleased() {
        if (releasedFlag.value) throw VideoKitException(Errors.of(ErrorCode.SESSION_RELEASED, ErrorStage.EDIT, "PROJECT_RELEASED"))
    }

    private fun publish() {
        mutableState.value = buildState()
    }

    private fun buildState(): VideoKitEditState = VideoKitEditState(
        phase = phase,
        revision = revision,
        timeline = Timeline(sources, content.clips),
        masks = content.masks,
        tracking = tracking,
        export = exportProgress,
        canUndo = undoStack.isNotEmpty(),
        canRedo = redoStack.isNotEmpty(),
        estimate = estimateFor(ExportPreset.ORIGINAL),
        error = error,
    )

    private fun rejected(what: String): EditCommandResult = EditCommandResult.Rejected(Errors.illegalState(ErrorStage.EDIT, what))

    private fun rejectedArgument(what: String): EditCommandResult =
        EditCommandResult.Rejected(Errors.invalidArgument(ErrorStage.EDIT, what))

    private fun MaskTrack.isAccepted(range: TimeRangeUs): Boolean =
        acceptedRangesUs.any { range.startUs >= it.startUs && range.endUs <= it.endUs }

    private fun MaskTrack.withKeyframe(keyframe: MaskKeyframe): MaskTrack =
        copy(keyframes = (keyframes.filterNot { it.atUs == keyframe.atUs } + keyframe).sortedBy { it.atUs })

    private companion object {
        const val PROBE_BYTES = 64
        const val UNDO_LIMIT = 100
        const val TRACKING_STEPS = 10
        const val TRACKING_KEYFRAME_US = 1_000_000L
        const val EXPORT_CHUNKS = 10
        const val AUDIO_BITS_PER_SECOND = 128_000L
        const val CONTAINER_OVERHEAD_BYTES = 64_000L
        val DEMO_HEADER: ByteArray = "VIDEOKIT-DEMO-EXPORT-NOT-REAL-MEDIA".encodeToByteArray()
        val BUSY_PHASES =
            setOf(
                EditPhase.PREPARING,
                EditPhase.TRACKING,
                EditPhase.EXPORTING,
                EditPhase.CANCELLING,
                EditPhase.RELEASING,
                EditPhase.RELEASED,
            )
        val FINISHED_PHASES = setOf(EditPhase.COMPLETED, EditPhase.FAILED, EditPhase.CANCELLED)
        val EXPORTABLE_PHASES = setOf(EditPhase.READY, EditPhase.COMPLETED, EditPhase.FAILED, EditPhase.CANCELLED)

        fun demoChunk(exportId: String, index: Int): ByteArray {
            val text = "VIDEOKIT-DEMO-EXPORT-NOT-REAL-MEDIA export=$exportId chunk=$index\n"
            return text.encodeToByteArray().let { line -> ByteArray(CHUNK_BYTES) { line[it % line.size] } }
        }

        const val CHUNK_BYTES = 4_096

        fun commandName(command: VideoKitEditCommand): String = command.typeName().uppercase()

        fun maxIdIn(model: ProjectModel): Long {
            val ids = model.sources.map { it.sourceId } + model.clips.map { it.clipId } + model.masks.map { it.maskId }
            return ids.mapNotNull { it.substringAfterLast('-').toLongOrNull() }.maxOrNull() ?: 0L
        }
    }
}
