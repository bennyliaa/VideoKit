package com.videokit.flutter

import com.videokit.api.ActionPlacement
import com.videokit.api.CandidateDetectionResult
import com.videokit.api.Clip
import com.videokit.api.CoverageQuality
import com.videokit.api.CoverageRange
import com.videokit.api.CoverageReport
import com.videokit.api.EditCommandResult
import com.videokit.api.EditEstimate
import com.videokit.api.EditFeatures
import com.videokit.api.EditPhase
import com.videokit.api.EditProjectConfig
import com.videokit.api.EditSource
import com.videokit.api.ErrorCode
import com.videokit.api.ErrorStage
import com.videokit.api.ExportPrecheck
import com.videokit.api.ExportPreset
import com.videokit.api.ExportProgress
import com.videokit.api.ExportStage
import com.videokit.api.FeatureKey
import com.videokit.api.FitMode
import com.videokit.api.HostActionRequest
import com.videokit.api.HostActionResult
import com.videokit.api.HostActionState
import com.videokit.api.HostActionStatus
import com.videokit.api.HostIcon
import com.videokit.api.ImageDetails
import com.videokit.api.ImageFeatures
import com.videokit.api.KeyframeSource
import com.videokit.api.MaskKeyframe
import com.videokit.api.MaskRegion
import com.videokit.api.MaskStyle
import com.videokit.api.MaskTrack
import com.videokit.api.MaskType
import com.videokit.api.MediaInfo
import com.videokit.api.MediaKind
import com.videokit.api.MediaOrientation
import com.videokit.api.MediaProbeResult
import com.videokit.api.MediaTransform
import com.videokit.api.NavigationDirection
import com.videokit.api.NavigationRequest
import com.videokit.api.NavigationResult
import com.videokit.api.OrientationRequest
import com.videokit.api.OrientationState
import com.videokit.api.PlaybackFeatures
import com.videokit.api.RecoveryDecision
import com.videokit.api.ResourcePriority
import com.videokit.api.Seekability
import com.videokit.api.SerializedEditProject
import com.videokit.api.SessionPhase
import com.videokit.api.SessionPurpose
import com.videokit.api.SessionVisibility
import com.videokit.api.SinkWriteMode
import com.videokit.api.Size
import com.videokit.api.SourceProbe
import com.videokit.api.SuggestedAction
import com.videokit.api.SupportLevel
import com.videokit.api.ThumbnailResult
import com.videokit.api.TimeRangeUs
import com.videokit.api.Timeline
import com.videokit.api.TrackInfo
import com.videokit.api.TrackingCandidate
import com.videokit.api.TrackingKind
import com.videokit.api.TrackingModuleStatus
import com.videokit.api.TrackingRun
import com.videokit.api.TrackingRunStatus
import com.videokit.api.TrackingStatus
import com.videokit.api.UnsupportedReason
import com.videokit.api.VideoKitCapabilities
import com.videokit.api.VideoKitCommandResult
import com.videokit.api.VideoKitEditCommand
import com.videokit.api.VideoKitEditState
import com.videokit.api.VideoKitEvent
import com.videokit.api.VideoKitExportRequest
import com.videokit.api.VideoKitExportResult
import com.videokit.api.VideoKitExportedMedia
import com.videokit.api.VideoKitHostAction
import com.videokit.api.VideoKitOutputToken
import com.videokit.api.VideoKitPlaybackEvent
import com.videokit.api.VideoKitPlaybackState
import com.videokit.api.VideoKitSessionConfig
import com.videokit.api.VideoKitSessionState
import com.videokit.api.VideoKitStableError
import com.videokit.flutter.Mappers.toAction
import com.videokit.flutter.Mappers.toCapabilities
import com.videokit.flutter.Mappers.toClip
import com.videokit.flutter.Mappers.toCommand
import com.videokit.flutter.Mappers.toConfig
import com.videokit.flutter.Mappers.toError
import com.videokit.flutter.Mappers.toEvent
import com.videokit.flutter.Mappers.toIcon
import com.videokit.flutter.Mappers.toMedia
import com.videokit.flutter.Mappers.toMsg
import com.videokit.flutter.Mappers.toPlaybackState
import com.videokit.flutter.Mappers.toPrecheck
import com.videokit.flutter.Mappers.toProbe
import com.videokit.flutter.Mappers.toRequest
import com.videokit.flutter.Mappers.toResult
import com.videokit.flutter.Mappers.toSerialized
import com.videokit.flutter.Mappers.toSource
import com.videokit.flutter.Mappers.toState
import com.videokit.flutter.Mappers.toTransform
import com.videokit.flutter.gen.EditCommandMsg
import com.videokit.flutter.gen.StableErrorMsg
import com.videokit.testkit.CountingSourceFactory
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNull
import org.junit.Test

/** Field-by-field round trips of every channel message (14 §11.2 "Mappers.kt 全字段往返"). */
class MappersTest {
    private val error = VideoKitStableError(
        code = ErrorCode.INVALID_ARGUMENT,
        stage = ErrorStage.EDIT,
        retryable = true,
        suggestedAction = SuggestedAction.CHOOSE_OTHER_SOURCE,
        diagnostic = "INVALID_ARGUMENT:X",
        params = mapOf("limit" to "12", "value" to "13"),
    )
    private val action = VideoKitHostAction(
        actionId = "tag",
        labelKey = "action.tag",
        contentDescriptionKey = "action.tag.cd",
        icon = HostIcon.Resource("drawable/ic_tag"),
        enabled = false,
        selected = true,
        pending = true,
        badgeText = "3",
        displayPriority = 7,
        placement = ActionPlacement.SECONDARY_BAR,
    )
    private val region = MaskRegion(0.125f, 0.25f, 0.5f, 0.375f, 15f)

    @Test
    fun stableErrorAndUnknownWireNames() {
        assertEquals(error, error.toMsg().toError())
        val future = StableErrorMsg("CODE_FROM_THE_FUTURE", "STAGE_FROM_THE_FUTURE", false, "ACTION_FROM_THE_FUTURE", null, emptyMap())
        val mapped = future.toError()
        assertEquals(ErrorCode.INTERNAL_ERROR_REDACTED, mapped.code)
        assertEquals(ErrorStage.UNKNOWN, mapped.stage)
        assertEquals(SuggestedAction.NONE, mapped.suggestedAction)
    }

    @Test
    fun commandResults() {
        listOf(
            VideoKitCommandResult.Executed,
            VideoKitCommandResult.Rejected(error),
            VideoKitCommandResult.Superseded,
            VideoKitCommandResult.Unsupported(UnsupportedReason.CONTENT_LOCKED),
            VideoKitCommandResult.SessionReleased,
        ).forEach { assertEquals(it, it.toMsg().toResult()) }
    }

    @Test
    fun sessionValues() {
        val transform = MediaTransform(2.5f, 0.25f, -0.5f, 270, FitMode.ORIGINAL)
        assertEquals(transform, transform.toMsg().toTransform())
        assertEquals(HostIcon.BuiltIn("favorite"), HostIcon.BuiltIn("favorite").toMsg().toIcon())
        assertEquals(action, action.toMsg().toAction())
        val config =
            VideoKitSessionConfig(SessionPurpose.MULTI_SLOT, ResourcePriority.OFFSCREEN, SessionVisibility.BACKGROUND, false, "slot-3")
        assertEquals(config, config.toMsg().toConfig())
    }

    @Test
    fun sessionStateRoundTrip() {
        val state = VideoKitSessionState(
            phase = SessionPhase.BUFFERING,
            mediaKind = MediaKind.VIDEO,
            positionUs = 1_234_567,
            durationUs = 9_000_000_000,
            bufferedUs = 2_000_000,
            playWhenReady = true,
            speed = 1.5f,
            volume = 0.25f,
            muted = true,
            audioTracks = listOf(
                TrackInfo("a1", "zh", null, "audio/ac3", false, channelCount = 6),
                TrackInfo("a2", "en", "Commentary", null, true),
            ),
            subtitleTracks = listOf(TrackInfo("s1", "ja", null, "text/x-ssa", true)),
            selectedAudioTrackId = "a2",
            selectedSubtitleTrackId = "s1",
            transform = MediaTransform(1.25f, 0.5f, 0.25f, 90, FitMode.FILL),
            orientation = OrientationState(OrientationRequest.LANDSCAPE, MediaOrientation.PORTRAIT, true),
            visibility = SessionVisibility.OFFSCREEN,
            activeAudio = false,
            controlsVisible = false,
            error = error,
            resourcesHeld = true,
            seekingToUs = 3_000_000,
            hostActions = listOf(HostActionState(action, pending = true, lastStatus = HostActionStatus.PENDING, lastError = error)),
            videoSize = Size(1080, 1920),
            hiddenForLock = true,
        )
        assertEquals(state, state.toMsg().toState())
        val image = VideoKitSessionState(
            mediaKind = MediaKind.IMAGE_ANIMATED,
            looping = true,
            imageDetails = ImageDetails(frameCount = 12, decodedBytes = 4_096L, sampleSize = 2),
        )
        assertEquals(image, image.toMsg().toState())
        val partial = VideoKitSessionState(mediaKind = MediaKind.IMAGE_STATIC, imageDetails = ImageDetails(frameCount = 1))
        val withInfo = VideoKitSessionState(
            mediaKind = MediaKind.VIDEO,
            mediaInfo = MediaInfo("mkv", "video/hevc", "audio/ac3", 3840, 2160, 23.976f, 40_000_000L, 90, 7_200_000_000L, 9_000_000_000L),
        )
        assertEquals(withInfo, withInfo.toMsg().toState())
        // 04A P1.
        val captured = ThumbnailResult.Captured(byteArrayOf(1, 2, 3), 160, 90)
        assertEquals(captured, captured.toMsg().toResult())
        val failed = ThumbnailResult.Failed(error)
        assertEquals(failed, failed.toMsg().toResult())
        assertEquals(partial, partial.toMsg().toState())
        val empty = VideoKitSessionState()
        assertEquals(empty, empty.toMsg().toState())
    }

    @Test
    fun playbackSnapshotRoundTrip() {
        val snapshot = VideoKitPlaybackState(
            schemaVersion = 1,
            sessionId = "s-1",
            mediaToken = "m-1",
            zoom = 2f,
            panX = 0.25f,
            panY = -0.25f,
            rotationDeg = 180,
            fitMode = FitMode.FILL,
            preferredOrientation = OrientationRequest.PORTRAIT,
            fullscreen = true,
            positionUs = 5_000_000,
            speed = 0.75f,
            volume = 0.5f,
            muted = false,
            subtitleTrackId = null,
            subtitlesEnabled = false,
            audioTrackId = "a2",
            lastViewedAtEpochMs = 1_700_000_000_000,
        )
        assertEquals(snapshot, snapshot.toMsg().toPlaybackState())
        val image = VideoKitPlaybackState()
        assertEquals(image, image.toMsg().toPlaybackState())
        // 04A L3.
        val looping = VideoKitPlaybackState(looping = true)
        assertEquals(looping, looping.toMsg().toPlaybackState())
    }

    @Test
    fun eventsAndUnknownEventTypes() {
        listOf(
            VideoKitEvent.PlaybackEnded,
            VideoKitEvent.SourceReleased("m-1"),
            VideoKitEvent.HostActionFailed("tag", error),
            VideoKitEvent.TransientNotice("AUDIO_UNSUPPORTED_PLAYING_SILENT"),
            VideoKitEvent.ErrorRaised(error),
        ).forEach { assertEquals(it, it.toMsg().toEvent()) }
        assertNull(com.videokit.flutter.gen.EventMsg(type = "EVENT_FROM_THE_FUTURE").toEvent())
    }

    @Test
    fun playbackEvents() {
        listOf(
            VideoKitPlaybackEvent.PositionTick("s", 1),
            VideoKitPlaybackEvent.PlayStateChanged("s", SessionPhase.PAUSED, false),
            VideoKitPlaybackEvent.BufferingStarted("s", 2),
            VideoKitPlaybackEvent.BufferingEnded("s", 3),
            VideoKitPlaybackEvent.UserSeek("s", 4, 5),
            VideoKitPlaybackEvent.VisibilityChanged("s", SessionVisibility.BACKGROUND),
            VideoKitPlaybackEvent.ForegroundChanged("s", false),
            VideoKitPlaybackEvent.WatchTimeAccumulated("s", 6),
            VideoKitPlaybackEvent.SessionEnded("s", "m"),
            VideoKitPlaybackEvent.SessionEnded("s", null),
        ).forEach { assertEquals(it, it.toMsg().toEvent()) }
    }

    @Test
    fun mediaSourceDescriptor() {
        val factory = CountingSourceFactory()
        val msg = com.videokit.flutter.gen.MediaSourceMsg(
            "tok",
            com.videokit.flutter.gen.MediaKindMsg.IMAGE_ANIMATED,
            "a.gif",
            42,
            "image/gif",
            "gif",
            false,
            "demo:normal",
        )
        val source = msg.toSource(factory)
        assertEquals(MediaKind.IMAGE_ANIMATED, source.mediaKind)
        assertEquals(Seekability.SEQUENTIAL_ONLY, source.seekability)
        assertEquals(msg, source.toMsg("demo:normal"))
    }

    @Test
    fun capabilitiesSummary() {
        val caps = VideoKitCapabilities(
            schemaVersion = 1,
            suggestedHardwareVideoSessions = 4,
            maxSuggestedResolution = Size(3840, 2160),
            maxSuggestedFrameRate = 60,
            playbackFeatures = PlaybackFeatures(SupportLevel.PARTIAL, true, listOf(0.5f, 1f, 2f), true),
            imageFeatures = ImageFeatures(true, true, false),
            editFeatures = EditFeatures(true, false, true),
            tracking = TrackingStatus(TrackingModuleStatus.AVAILABLE, TrackingModuleStatus.DISABLED),
            unavailableReasons = mapOf(FeatureKey.EDIT_CONCAT to UnsupportedReason.HOST_DISABLED),
            mediaProbe = MediaProbeResult("m", SupportLevel.SUPPORTED, SupportLevel.UNSUPPORTED, true, 9, Size(640, 480), error),
            isDemo = true,
        )
        assertEquals(caps, caps.toMsg().toCapabilities())
        val probe = MediaProbeResult("m2", SupportLevel.PARTIAL, SupportLevel.PARTIAL)
        assertEquals(probe, probe.toMsg().toProbe())
    }

    @Test
    fun hostCallbackMessages() {
        val request = HostActionRequest("tag", "s", "m")
        assertEquals(request, request.toMsg().toRequest())
        val result = HostActionResult(HostActionStatus.CANCELLED, action, "notice.cancelled")
        assertEquals(result, result.toMsg().toResult())
        val navigation = NavigationRequest("s", null, NavigationDirection.PREVIOUS)
        assertEquals(navigation, navigation.toMsg().toRequest())
        assertEquals(NavigationResult.FAILED, Mappers.navigationResult("FUTURE"))
        assertEquals(RecoveryDecision.KEEP_ERROR, Mappers.recoveryDecision(null))
        assertEquals(RecoveryDecision.RETRY, Mappers.recoveryDecision("RETRY"))
    }

    @Test
    fun editCommandsAllKinds() {
        listOf(
            VideoKitEditCommand.AddClip("src-1", 0, 1_000, index = 2),
            VideoKitEditCommand.AddClip("src-1", 0, 1_000),
            VideoKitEditCommand.SplitAt("clip-1", 500),
            VideoKitEditCommand.TrimClip("clip-1", 10, 20),
            VideoKitEditCommand.RemoveClip("clip-1"),
            VideoKitEditCommand.MoveClip("clip-1", 3),
            VideoKitEditCommand.AddMask(MaskType.OBJECT, region, TimeRangeUs(1, 2), MaskStyle.BLUR, 0.75f),
            VideoKitEditCommand.UpdateMaskKeyframe("mask-1", 7, region),
            VideoKitEditCommand.RemoveMaskKeyframe("mask-1", 7),
            VideoKitEditCommand.SetMaskStyle("mask-1", MaskStyle.MOSAIC, 0.25f),
            VideoKitEditCommand.SetMaskEnabled("mask-1", false),
            VideoKitEditCommand.RemoveMask("mask-1"),
            VideoKitEditCommand.StartTracking("mask-1", TrackingKind.FACE),
            VideoKitEditCommand.StartTracking("mask-1", TrackingKind.OBJECT, MaskRegion(0.1f, 0.2f, 0.3f, 0.4f), "candidate-1"),
            VideoKitEditCommand.CorrectTracking("mask-1", 8, region),
            VideoKitEditCommand.CancelTracking("mask-1"),
            VideoKitEditCommand.AcceptTrackingRange("mask-1", TimeRangeUs(3, 4)),
        ).forEach { assertEquals(it, it.toMsg().toCommand()) }
        assertNull(EditCommandMsg(kind = "CommandFromTheFuture").toCommand())
        assertNull(EditCommandMsg(kind = "AddClip").toCommand())
    }

    @Test
    fun editResultsAndConfig() {
        listOf(
            EditCommandResult.Applied(7, "clip-9"),
            EditCommandResult.Applied(8),
            EditCommandResult.Rejected(error),
            EditCommandResult.Unsupported(UnsupportedReason.MODULE_NOT_INSTALLED),
            EditCommandResult.ProjectReleased,
        ).forEach { assertEquals(it, it.toMsg().toResult()) }
        val config = EditProjectConfig(setOf(ExportPreset.P720, ExportPreset.P1080), trackingAllowed = false, initialPositionUs = 5)
        assertEquals(config, config.toMsg().toConfig())
        val serialized = SerializedEditProject(1, """{"schemaVersion":1}""")
        assertEquals(serialized, serialized.toMsg().toSerialized())
    }

    @Test
    fun editStateRoundTrip() {
        val state = VideoKitEditState(
            phase = EditPhase.EXPORTING,
            revision = 42,
            timeline = Timeline(
                sources = listOf(
                    EditSource(
                        "src-1",
                        "m-1",
                        "a.mp4",
                        SourceProbe(9_000_000, 1920, 1080, 90, 29.97f, "video/hevc", "audio/opus", true),
                        mismatch = true,
                    ),
                    EditSource("src-2", "m-2"),
                ),
                clips = listOf(Clip("clip-1", "src-1", 0, 1_000_000), Clip("clip-2", "src-2", 5, 6)),
            ),
            masks = listOf(
                MaskTrack(
                    maskId = "mask-1",
                    type = MaskType.FACE,
                    style = MaskStyle.BLUR,
                    strength = 0.75f,
                    enabled = false,
                    rangeUs = TimeRangeUs(0, 2_000_000),
                    keyframes = listOf(
                        MaskKeyframe(0, region, KeyframeSource.USER),
                        MaskKeyframe(1_000_000, region.copy(x = 0.2f), KeyframeSource.TRACKER, CoverageQuality.AMBIGUOUS),
                    ),
                    acceptedRangesUs = listOf(TimeRangeUs(500_000, 600_000)),
                ),
            ),
            tracking = mapOf(
                "mask-1" to TrackingRun(
                    "mask-1",
                    TrackingRunStatus.COMPLETED,
                    1f,
                    CoverageReport(
                        listOf(
                            CoverageRange(TimeRangeUs(0, 1), CoverageQuality.TRACKED),
                            CoverageRange(TimeRangeUs(1, 2), CoverageQuality.LOST),
                        ),
                    ),
                    error,
                ),
                "mask-2" to TrackingRun("mask-2", TrackingRunStatus.RUNNING, 0.5f),
            ),
            export = ExportProgress("e-1", ExportStage.ENCODING, 0.5f, 1_000_000, 30, 4_096, 2_000_000, cancellable = false),
            canUndo = true,
            canRedo = true,
            estimate = EditEstimate(1_000_000, 123_456),
            error = error,
        )
        assertEquals(state, state.toMsg().toState())
        assertEquals(VideoKitEditState(), VideoKitEditState().toMsg().toState())
    }

    @Test
    fun exportMessages() {
        val request = VideoKitExportRequest(ExportPreset.P1080, "e-1", "holiday")
        assertEquals(request, request.toMsg("demo:memory").toRequest())
        val precheck =
            ExportPrecheck(
                false,
                SinkWriteMode.FILE_DESCRIPTOR,
                EditEstimate(10, null),
                listOf(error),
                listOf("TRACKING_INCOMPLETE:mask-1"),
                listOf(CoverageRange(TimeRangeUs(1, 2), CoverageQuality.LOST, maskId = "mask-1")),
            )
        assertEquals(precheck, precheck.toMsg().toPrecheck())
        val media = VideoKitExportedMedia(
            outputToken = VideoKitOutputToken("token-1"),
            container = "mp4",
            extension = "mp4",
            videoCodec = "video/avc",
            audioCodec = null,
            width = 1280,
            height = 720,
            rotationDeg = 90,
            durationUs = 3_000_000,
            sizeBytes = 40_960,
            frameRate = 30f,
            audioPresent = false,
            createdAtEpochMs = 1_700_000_000_000,
            sourceTokens = listOf("m-1", "m-2"),
            editProjectId = "p-1",
            exportPreset = ExportPreset.P720,
            warnings = listOf("DEMO_OUTPUT_NOT_REAL_MEDIA"),
            isDemo = true,
        )
        assertEquals(media, media.toMsg().toMedia())
        listOf(
            VideoKitExportResult.Succeeded("e-1", media),
            VideoKitExportResult.Failed("e-1", error, ExportStage.VERIFYING),
            VideoKitExportResult.Failed("e-1", error),
            VideoKitExportResult.Cancelled("e-1", partialOutputRemoved = false),
        ).forEach { assertEquals(it, it.toMsg().toResult()) }
    }

    @Test
    fun candidateResults() {
        val result = CandidateDetectionResult(
            listOf(TrackingCandidate("c-1", TrackingKind.FACE, region, 0.5f), TrackingCandidate("c-2", TrackingKind.OBJECT, region)),
            error,
        )
        assertEquals(result, result.toMsg().toResult())
    }

    @Test
    fun editEventsCarryTheirKeys() {
        assertEquals("EXPORT_STAGE_CHANGED", com.videokit.api.VideoKitEditEvent.ExportStageChanged("e", ExportStage.VERIFYING).toMsg().type)
        assertEquals("RESOURCES_RELEASED", com.videokit.api.VideoKitEditEvent.ResourcesReleased.toMsg().type)
        val lost = com.videokit.api.VideoKitEditEvent.TrackingLost("mask-1", TimeRangeUs(1, 2)).toMsg()
        assertEquals("mask-1" to 1L, lost.maskId to lost.range?.startUs)
    }

    @Test
    fun clipMessage() {
        val clip = Clip("c", "s", 1, 2)
        assertEquals(clip, clip.toMsg().toClip())
    }
}
