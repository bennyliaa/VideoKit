package com.videokit.testkit

import com.videokit.api.CoverageQuality
import com.videokit.api.EditCommandResult
import com.videokit.api.EditPhase
import com.videokit.api.EditProjectConfig
import com.videokit.api.ErrorCode
import com.videokit.api.ExportPreset
import com.videokit.api.ExportStage
import com.videokit.api.KeyframeSource
import com.videokit.api.MaskRegion
import com.videokit.api.MaskType
import com.videokit.api.SerializedEditProject
import com.videokit.api.SessionPhase
import com.videokit.api.SinkWriteMode
import com.videokit.api.TimeRangeUs
import com.videokit.api.TrackingKind
import com.videokit.api.TrackingRunStatus
import com.videokit.api.UnsupportedReason
import com.videokit.api.VideoKitAbortReason
import com.videokit.api.VideoKitEditCommand
import com.videokit.api.VideoKitEditEvent
import com.videokit.api.VideoKitException
import com.videokit.api.VideoKitExportRequest
import com.videokit.api.VideoKitExportResult
import com.videokit.testkit.internal.MiniJson
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.async
import kotlinx.coroutines.flow.toList
import kotlinx.coroutines.launch
import kotlinx.coroutines.test.TestScope
import kotlinx.coroutines.test.UnconfinedTestDispatcher
import kotlinx.coroutines.test.runCurrent
import kotlinx.coroutines.test.runTest
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertFalse
import kotlin.test.assertTrue
import kotlin.test.fail

@OptIn(ExperimentalCoroutinesApi::class)
class FakeEditProjectTest {
    private fun TestScope.kit(scenario: FakeScenario = FakeScenario.normal(), trackingAvailable: Boolean = true) = FakeVideoKit(
        RecordingHostCallbacks(),
        FakeVideoKitOptions(scope = backgroundScope, scenarioResolver = {
            scenario
        }, trackingAvailable = trackingAvailable),
    )

    private suspend fun FakeVideoKit.projectWithClip(config: EditProjectConfig = EditProjectConfig()): Pair<FakeEditProject, String> {
        val project = createEditProject(config) as FakeEditProject
        val source = project.addSource(FakeMediaSources.video("clip-source"))
        assertTrue(project.apply(VideoKitEditCommand.AddClip(source.sourceId, 0, 20_000_000)) is EditCommandResult.Applied)
        return project to source.sourceId
    }

    @Test
    fun clipEditingSplitTrimMove() = runTest {
        val (project, sourceId) = kit().projectWithClip()
        val clipId = project.state.value.timeline.clips.single().clipId
        assertTrue(project.apply(VideoKitEditCommand.SplitAt(clipId, 5_000_000)) is EditCommandResult.Applied)
        val clips = project.state.value.timeline.clips
        assertEquals(listOf(5_000_000L, 15_000_000L), clips.map { it.durationUs })
        assertTrue(project.apply(VideoKitEditCommand.TrimClip(clips[1].clipId, 6_000_000, 10_000_000)) is EditCommandResult.Applied)
        assertTrue(project.apply(VideoKitEditCommand.MoveClip(clips[1].clipId, 0)) is EditCommandResult.Applied)
        assertEquals(clips[1].clipId, project.state.value.timeline.clips.first().clipId)
        assertEquals(9_000_000L, project.state.value.timeline.durationUs)
        assertTrue(project.apply(VideoKitEditCommand.SplitAt(clipId, 0)) is EditCommandResult.Rejected)
        assertTrue(project.apply(VideoKitEditCommand.MoveClip(clipId, 9)) is EditCommandResult.Rejected)
        assertTrue(project.apply(VideoKitEditCommand.AddClip(sourceId, 0, 1_000_000, index = 7)) is EditCommandResult.Rejected)
        val revision = project.state.value.revision
        assertTrue(project.undo() is EditCommandResult.Applied)
        assertEquals(revision + 1, project.state.value.revision)
        assertTrue(project.state.value.canRedo)
    }

    @Test
    fun manualMaskKeyframes() = runTest {
        val (project, _) = kit().projectWithClip()
        val region = MaskRegion(0.1f, 0.1f, 0.2f, 0.2f)
        assertTrue(
            project.apply(VideoKitEditCommand.AddMask(MaskType.MANUAL, region, TimeRangeUs(0, 30_000_000))) is EditCommandResult.Rejected,
        )
        assertTrue(
            project.apply(
                VideoKitEditCommand.AddMask(MaskType.MANUAL, MaskRegion(0.9f, 0f, 0.2f, 0.2f), TimeRangeUs(0, 1_000_000)),
            ) is EditCommandResult.Rejected,
        )
        assertTrue(
            project.apply(VideoKitEditCommand.AddMask(MaskType.MANUAL, region, TimeRangeUs(0, 10_000_000))) is EditCommandResult.Applied,
        )
        val maskId = project.state.value.masks.single().maskId
        assertTrue(
            project.apply(VideoKitEditCommand.UpdateMaskKeyframe(maskId, 5_000_000, region.copy(x = 0.3f))) is EditCommandResult.Applied,
        )
        assertEquals(listOf(0L, 5_000_000L), project.state.value.masks.single().keyframes.map { it.atUs })
        assertTrue(project.apply(VideoKitEditCommand.RemoveMaskKeyframe(maskId, 0)) is EditCommandResult.Applied)
        assertTrue(project.apply(VideoKitEditCommand.RemoveMaskKeyframe(maskId, 5_000_000)) is EditCommandResult.Rejected)
        assertTrue(project.apply(VideoKitEditCommand.SetMaskEnabled(maskId, false)) is EditCommandResult.Applied)
        assertTrue(
            project.apply(VideoKitEditCommand.SetMaskStyle(maskId, com.videokit.api.MaskStyle.BLUR, 2f)) is EditCommandResult.Rejected,
        )
        assertTrue(project.apply(VideoKitEditCommand.StartTracking(maskId, TrackingKind.FACE)) is EditCommandResult.Rejected)
        assertTrue(project.apply(VideoKitEditCommand.RemoveMask(maskId)) is EditCommandResult.Applied)
        assertTrue(project.state.value.masks.isEmpty())
    }

    @Test
    fun trackingProducesCoverageWithLostRanges() = runTest {
        val kit = kit(FakeScenario.normal().trackingLost(listOf(TimeRangeUs(2_000_000, 4_000_000))))
        val (project, _) = kit.projectWithClip()
        val events = mutableListOf<VideoKitEditEvent>()
        backgroundScope.launch(UnconfinedTestDispatcher(testScheduler)) { project.events.toList(events) }
        project.apply(VideoKitEditCommand.AddMask(MaskType.FACE, MaskRegion(0.4f, 0.4f, 0.2f, 0.2f), TimeRangeUs(0, 6_000_000)))
        val maskId = project.state.value.masks.single().maskId
        val badSeed = VideoKitEditCommand.StartTracking(maskId, TrackingKind.OBJECT, seedRegion = MaskRegion(0.9f, 0.9f, 0.5f, 0.5f))
        assertTrue(project.apply(badSeed) is EditCommandResult.Rejected)
        assertTrue(project.apply(VideoKitEditCommand.StartTracking(maskId, TrackingKind.FACE)) is EditCommandResult.Applied)
        assertEquals(EditPhase.TRACKING, project.state.value.phase)
        assertTrue(project.apply(VideoKitEditCommand.RemoveClip("x")) is EditCommandResult.Rejected)
        settle()
        val state = project.state.value
        assertEquals(EditPhase.READY, state.phase)
        val run = state.tracking.getValue(maskId)
        assertEquals(TrackingRunStatus.COMPLETED, run.status)
        assertEquals(
            listOf(CoverageQuality.TRACKED, CoverageQuality.LOST, CoverageQuality.TRACKED),
            run.coverage!!.ranges.map { it.quality },
        )
        assertTrue(state.masks.single().keyframes.any { it.source == KeyframeSource.TRACKER })
        assertTrue(events.contains(VideoKitEditEvent.TrackingLost(maskId, TimeRangeUs(2_000_000, 4_000_000))))
        val precheck = project.checkExport(VideoKitExportRequest(), RecordingOutputSink())
        assertTrue(precheck.ok)
        assertEquals(listOf("TRACKING_LOST_RANGES:$maskId"), precheck.warnings)
    }

    @Test
    fun trackingCanBeCancelledAndRespectsAvailability() = runTest {
        val (project, _) = kit().projectWithClip()
        project.apply(VideoKitEditCommand.AddMask(MaskType.OBJECT, MaskRegion(0.4f, 0.4f, 0.2f, 0.2f), TimeRangeUs(0, 6_000_000)))
        val maskId = project.state.value.masks.single().maskId
        project.apply(VideoKitEditCommand.StartTracking(maskId, TrackingKind.FACE))
        runCurrent()
        assertTrue(project.apply(VideoKitEditCommand.CancelTracking(maskId)) is EditCommandResult.Applied)
        assertEquals(EditPhase.READY, project.state.value.phase)
        assertEquals(TrackingRunStatus.CANCELLED, project.state.value.tracking.getValue(maskId).status)

        val (disabled, _) = kit().projectWithClip(EditProjectConfig(trackingAllowed = false))
        disabled.apply(VideoKitEditCommand.AddMask(MaskType.FACE, MaskRegion(0.4f, 0.4f, 0.2f, 0.2f), TimeRangeUs(0, 6_000_000)))
        assertEquals(
            EditCommandResult.Unsupported(UnsupportedReason.HOST_DISABLED),
            disabled.apply(VideoKitEditCommand.StartTracking(disabled.state.value.masks.single().maskId, TrackingKind.FACE)),
        )
        val (missing, _) = kit(trackingAvailable = false).projectWithClip()
        missing.apply(VideoKitEditCommand.AddMask(MaskType.FACE, MaskRegion(0.4f, 0.4f, 0.2f, 0.2f), TimeRangeUs(0, 6_000_000)))
        assertEquals(
            EditCommandResult.Unsupported(UnsupportedReason.MODULE_NOT_INSTALLED),
            missing.apply(VideoKitEditCommand.StartTracking(missing.state.value.masks.single().maskId, TrackingKind.FACE)),
        )
    }

    @Test
    fun exportWritesDemoBytesInStagesWithRandomWrite() = runTest {
        val (project, _) = kit().projectWithClip()
        val sink = RecordingOutputSink()
        val events = mutableListOf<VideoKitEditEvent>()
        backgroundScope.launch(UnconfinedTestDispatcher(testScheduler)) { project.events.toList(events) }
        val result = (
            project.export(
                VideoKitExportRequest(preset = ExportPreset.P720, exportId = "e1"),
                sink,
            ) as VideoKitExportResult.Succeeded
            ).media
        assertEquals(1280 to 720, result.width to result.height)
        assertTrue(FakeScenario.DEMO_OUTPUT_WARNING in result.warnings)
        assertTrue(result.isDemo && sink.readyCalls.single().second.isDemo)
        assertEquals(SinkWriteMode.RANDOM_WRITE, sink.openRequests.single().writeMode)
        val handle = sink.handles.single()
        assertTrue(handle.closed)
        assertEquals(1, handle.randomWriteCount)
        assertTrue(handle.bytes.decodeToString().startsWith("VIDEOKIT-DEMO-EXPORT-NOT-REAL-MEDIA"))
        assertEquals(handle.bytes.size.toLong(), result.sizeBytes)
        val stages = events.filterIsInstance<VideoKitEditEvent.ExportStageChanged>().map { it.stage }
        assertEquals(listOf(ExportStage.PREPARING, ExportStage.ENCODING, ExportStage.VERIFYING, ExportStage.WRITING), stages)
        assertTrue(events.last() is VideoKitEditEvent.ExportCompleted)
        assertEquals(EditPhase.COMPLETED, project.state.value.phase)
        // Editing after completion returns to READY.
        val clipId = project.state.value.timeline.clips.single().clipId
        assertTrue(project.apply(VideoKitEditCommand.SplitAt(clipId, 1_000_000)) is EditCommandResult.Applied)
        assertEquals(EditPhase.READY, project.state.value.phase)
    }

    @Test
    fun scenarioExportFailureAborts() = runTest {
        val (project, _) = kit(FakeScenario.normal().exportFails(ExportStage.VERIFYING, ErrorCode.EXPORT_FAILED)).projectWithClip()
        val sink = RecordingOutputSink()
        val result = project.export(VideoKitExportRequest(), sink) as VideoKitExportResult.Failed
        assertEquals(ErrorCode.EXPORT_FAILED, result.error.code)
        assertEquals(ExportStage.VERIFYING, result.stage)
        assertEquals(EditPhase.FAILED, project.state.value.phase)
        assertEquals(VideoKitAbortReason.EXPORT_FAILED, sink.abortCalls.single().second)
        assertTrue(sink.readyCalls.isEmpty())
    }

    @Test
    fun slowCancellationShowsCancelling() = runTest {
        val (project, _) = kit(FakeScenario.normal().exportCancelSlow(3_000)).projectWithClip()
        val sink = RecordingOutputSink()
        val export = async { project.export(VideoKitExportRequest(exportId = "slow"), sink) }
        testScheduler.advanceTimeBy(250)
        runCurrent()
        val cancel = async { project.cancelExport("slow") }
        runCurrent()
        assertEquals(EditPhase.CANCELLING, project.state.value.phase)
        testScheduler.advanceTimeBy(3_100)
        runCurrent()
        cancel.await()
        assertEquals(EditPhase.CANCELLED, project.state.value.phase)
        assertEquals(VideoKitExportResult.Cancelled("slow", partialOutputRemoved = true), export.await())
    }

    @Test
    fun restoredProjectMatchesSourcesAndDetectsMismatch() = runTest {
        val kit = kit()
        val (project, _) = kit.projectWithClip()
        val snapshot = project.snapshot()
        val restored = kit.restoreEditProject(snapshot, EditProjectConfig()) as FakeEditProject
        // Sources are not attached after restore: export is not possible until the host adds them again.
        assertFalse(restored.checkExport(VideoKitExportRequest(), RecordingOutputSink()).ok)
        val events = mutableListOf<VideoKitEditEvent>()
        backgroundScope.launch(UnconfinedTestDispatcher(testScheduler)) { restored.events.toList(events) }
        val longer = FakeVideoKit(RecordingHostCallbacks(), restoredKitOptions(FakeScenario.normal().copy(durationUs = 1_000_000_000)))
        val other = longer.restoreEditProject(snapshot, EditProjectConfig())
        other.addSource(FakeMediaSources.video("clip-source"))
        assertTrue(other.state.value.timeline.sources.single().mismatch)
        restored.addSource(FakeMediaSources.video("clip-source"))
        assertFalse(restored.state.value.timeline.sources.single().mismatch)
        assertTrue(restored.checkExport(VideoKitExportRequest(), RecordingOutputSink()).ok)
        // New ids after restore do not collide with restored ids.
        restored.apply(VideoKitEditCommand.AddClip(restored.state.value.timeline.sources.single().sourceId, 0, 1_000_000))
        val ids = restored.state.value.timeline.clips.map { it.clipId }
        assertEquals(ids.size, ids.distinct().size)
    }

    private fun TestScope.restoredKitOptions(scenario: FakeScenario) =
        FakeVideoKitOptions(scope = backgroundScope, scenarioResolver = { scenario })

    @Test
    fun snapshotIgnoresUnknownFieldsAndRejectsCorruptPayloads() = runTest {
        val kit = kit()
        val (project, _) = kit.projectWithClip()
        val snapshot = project.snapshot()

        @Suppress("UNCHECKED_CAST")
        val root = MiniJson.parse(snapshot.json) as MutableMap<String, Any?>
        root["fieldFromAFutureMinor"] = mapOf("x" to 1L)
        val extended = SerializedEditProject(snapshot.schemaVersion, MiniJson.write(root))
        val restored = kit.restoreEditProject(extended, EditProjectConfig())
        assertEquals(project.state.value.timeline.clips, restored.state.value.timeline.clips)
        try {
            kit.restoreEditProject(SerializedEditProject(1, "{not json"), EditProjectConfig())
            fail("expected VideoKitException")
        } catch (expected: VideoKitException) {
            assertTrue(expected.error.diagnostic!!.startsWith("SNAPSHOT_CORRUPT"))
        }
        try {
            kit.restoreEditProject(SerializedEditProject(0, snapshot.json), EditProjectConfig())
            fail("expected VideoKitException")
        } catch (expected: VideoKitException) {
            assertEquals("UNSUPPORTED_SCHEMA_VERSION:0", expected.error.diagnostic)
        }
    }

    @Test
    fun previewSessionFollowsTimelineDuration() = runTest {
        val (project, _) = kit().projectWithClip()
        val preview = project.previewSession()
        settle()
        assertEquals(SessionPhase.READY, preview.state.value.phase)
        assertEquals(20_000_000L, preview.state.value.durationUs)
        assertTrue(preview === project.previewSession())
        val clipId = project.state.value.timeline.clips.single().clipId
        project.apply(VideoKitEditCommand.TrimClip(clipId, 0, 4_000_000))
        settle()
        assertEquals(4_000_000L, preview.state.value.durationUs)
        project.releaseAndAwait()
        assertEquals(SessionPhase.RELEASED, preview.state.value.phase)
    }

    @Test
    fun imageSourcesCannotBeEdited() = runTest {
        val project = kit().createEditProject(EditProjectConfig())
        try {
            project.addSource(FakeMediaSources.image("img"))
            fail("expected VideoKitException")
        } catch (expected: VideoKitException) {
            assertEquals(ErrorCode.UNSUPPORTED_CONTAINER, expected.error.code)
        }
        assertEquals(EditPhase.CREATED, project.state.value.phase)
    }

    @Test
    fun appliedResultsCarryCreatedIds() = runTest {
        val kit = kit()
        val project = kit.createEditProject(EditProjectConfig())
        val source = project.addSource(FakeMediaSources.video("ids"))
        val added = project.apply(VideoKitEditCommand.AddClip(source.sourceId, 0, 4_000_000)) as EditCommandResult.Applied
        assertEquals(project.state.value.timeline.clips.single().clipId, added.createdId)
        val split = project.apply(VideoKitEditCommand.SplitAt(added.createdId!!, 1_000_000)) as EditCommandResult.Applied
        assertEquals(project.state.value.timeline.clips[1].clipId, split.createdId)
        val mask = project.apply(
            VideoKitEditCommand.AddMask(MaskType.MANUAL, MaskRegion(0.1f, 0.1f, 0.2f, 0.2f), TimeRangeUs(0, 1_000_000)),
        ) as EditCommandResult.Applied
        assertEquals(project.state.value.masks.single().maskId, mask.createdId)
        val trim = project.apply(VideoKitEditCommand.TrimClip(added.createdId!!, 0, 500_000)) as EditCommandResult.Applied
        assertEquals(null, trim.createdId)
    }

    @Test
    fun candidateDetectionAndAcceptedRanges() = runTest {
        val (project, _) = kit(FakeScenario.normal().trackingLost(listOf(TimeRangeUs(2_000_000, 3_000_000)))).projectWithClip()
        val found = project.detectCandidates(1_000_000)
        assertEquals(null, found.error)
        assertEquals(2, found.candidates.size)
        assertEquals(found, project.detectCandidates(1_000_000))
        assertEquals(ErrorCode.INVALID_ARGUMENT, project.detectCandidates(-1).error?.code)
        val (unavailable, _) = kit(trackingAvailable = false).projectWithClip()
        assertEquals(ErrorCode.TRACKING_MODEL_UNAVAILABLE, unavailable.detectCandidates(1_000_000).error?.code)

        project.apply(VideoKitEditCommand.AddMask(MaskType.FACE, MaskRegion(0.4f, 0.4f, 0.2f, 0.2f), TimeRangeUs(0, 6_000_000)))
        val maskId = project.state.value.masks.single().maskId
        project.apply(VideoKitEditCommand.StartTracking(maskId, TrackingKind.FACE))
        settle()
        assertEquals(listOf("TRACKING_LOST_RANGES:$maskId"), project.checkExport(VideoKitExportRequest(), RecordingOutputSink()).warnings)
        assertTrue(
            project.apply(VideoKitEditCommand.AcceptTrackingRange(maskId, TimeRangeUs(2_000_000, 3_000_000))) is EditCommandResult.Applied,
        )
        assertEquals(listOf(TimeRangeUs(2_000_000, 3_000_000)), project.state.value.masks.single().acceptedRangesUs)
        assertEquals(
            listOf("TRACKING_COVERAGE_ACCEPTED:$maskId"),
            project.checkExport(VideoKitExportRequest(), RecordingOutputSink()).warnings,
        )
        // Accepted ranges survive a snapshot round trip.
        val restored = kit().restoreEditProject(project.snapshot(), EditProjectConfig())
        assertEquals(project.state.value.masks, restored.state.value.masks)
    }
}
