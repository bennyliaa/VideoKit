package com.videokit.flutter

import com.videokit.api.ActionPlacement
import com.videokit.api.CandidateDetectionResult
import com.videokit.api.CapabilityRequest
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
import com.videokit.api.FeatureAccess
import com.videokit.api.FeatureBadge
import com.videokit.api.FeatureKey
import com.videokit.api.FeatureMode
import com.videokit.api.FitMode
import com.videokit.api.HostActionRequest
import com.videokit.api.HostActionResult
import com.videokit.api.HostActionState
import com.videokit.api.HostActionStatus
import com.videokit.api.HostIcon
import com.videokit.api.ImageDetails
import com.videokit.api.KeyframeSource
import com.videokit.api.MaskAvatar
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
import com.videokit.api.RecoveryDecision
import com.videokit.api.ResourcePriority
import com.videokit.api.SeekMode
import com.videokit.api.Seekability
import com.videokit.api.SerializedEditProject
import com.videokit.api.SessionPhase
import com.videokit.api.SessionPurpose
import com.videokit.api.SessionVisibility
import com.videokit.api.SinkWriteMode
import com.videokit.api.Size
import com.videokit.api.SourceLatency
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
import com.videokit.api.UnsupportedReason
import com.videokit.api.VideoKitCapabilities
import com.videokit.api.VideoKitCommandResult
import com.videokit.api.VideoKitEditCommand
import com.videokit.api.VideoKitEditEvent
import com.videokit.api.VideoKitEditState
import com.videokit.api.VideoKitEvent
import com.videokit.api.VideoKitExportRequest
import com.videokit.api.VideoKitExportResult
import com.videokit.api.VideoKitExportedMedia
import com.videokit.api.VideoKitFeature
import com.videokit.api.VideoKitHostAction
import com.videokit.api.VideoKitMediaSource
import com.videokit.api.VideoKitOutputToken
import com.videokit.api.VideoKitPlaybackEvent
import com.videokit.api.VideoKitPlaybackState
import com.videokit.api.VideoKitSessionConfig
import com.videokit.api.VideoKitSessionState
import com.videokit.api.VideoKitSourceFactory
import com.videokit.api.VideoKitStableError
import com.videokit.flutter.gen.CandidateResultMsg
import com.videokit.flutter.gen.CapabilitiesMsg
import com.videokit.flutter.gen.CapabilityRequestMsg
import com.videokit.flutter.gen.ClipMsg
import com.videokit.flutter.gen.CommandResultKind
import com.videokit.flutter.gen.CommandResultMsg
import com.videokit.flutter.gen.CoverageRangeMsg
import com.videokit.flutter.gen.EditCommandMsg
import com.videokit.flutter.gen.EditEventMsg
import com.videokit.flutter.gen.EditPhaseMsg
import com.videokit.flutter.gen.EditProjectConfigMsg
import com.videokit.flutter.gen.EditResultKind
import com.videokit.flutter.gen.EditResultMsg
import com.videokit.flutter.gen.EditSourceMsg
import com.videokit.flutter.gen.EditStateMsg
import com.videokit.flutter.gen.EventMsg
import com.videokit.flutter.gen.ExportProgressMsg
import com.videokit.flutter.gen.ExportRequestMsg
import com.videokit.flutter.gen.ExportResultKind
import com.videokit.flutter.gen.ExportResultMsg
import com.videokit.flutter.gen.ExportedMediaMsg
import com.videokit.flutter.gen.FeatureAccessMsg
import com.videokit.flutter.gen.HostActionMsg
import com.videokit.flutter.gen.HostActionRequestMsg
import com.videokit.flutter.gen.HostActionResultMsg
import com.videokit.flutter.gen.HostActionStateMsg
import com.videokit.flutter.gen.HostIconMsg
import com.videokit.flutter.gen.ImageDetailsMsg
import com.videokit.flutter.gen.MaskAvatarMsg
import com.videokit.flutter.gen.MaskKeyframeMsg
import com.videokit.flutter.gen.MaskRegionMsg
import com.videokit.flutter.gen.MaskTrackMsg
import com.videokit.flutter.gen.MediaInfoMsg
import com.videokit.flutter.gen.MediaKindMsg
import com.videokit.flutter.gen.MediaProbeMsg
import com.videokit.flutter.gen.MediaSourceMsg
import com.videokit.flutter.gen.NavigationRequestMsg
import com.videokit.flutter.gen.OrientationStateMsg
import com.videokit.flutter.gen.PlaybackEventMsg
import com.videokit.flutter.gen.PlaybackStateMsg
import com.videokit.flutter.gen.PrecheckMsg
import com.videokit.flutter.gen.SeekModeMsg
import com.videokit.flutter.gen.SerializedProjectMsg
import com.videokit.flutter.gen.SessionConfigMsg
import com.videokit.flutter.gen.SessionPhaseMsg
import com.videokit.flutter.gen.SessionStateMsg
import com.videokit.flutter.gen.SourceProbeMsg
import com.videokit.flutter.gen.StableErrorMsg
import com.videokit.flutter.gen.ThumbnailResultMsg
import com.videokit.flutter.gen.TimeRangeMsg
import com.videokit.flutter.gen.TrackInfoMsg
import com.videokit.flutter.gen.TrackingCandidateMsg
import com.videokit.flutter.gen.TrackingRunMsg
import com.videokit.flutter.gen.TransformMsg

/**
 * Pure conversions between the Kit API types and the Pigeon messages (14 §8.4). Every message type that
 * crosses the channel has both directions, so the JVM tests can check field-by-field round trips.
 *
 * Open enums travel as Kotlin wire names; unknown names map to the documented fallback (04A §1.3):
 * error codes → INTERNAL_ERROR_REDACTED, stages → UNKNOWN, reasons → UNKNOWN, suggestions → NONE.
 */
internal object Mappers {
    // ------------------------------------------------------------------ enum helpers

    inline fun <reified T : Enum<T>> wire(name: String?, fallback: T): T = enumValues<T>().firstOrNull { it.name == name } ?: fallback

    fun MediaKind.toMsg(): MediaKindMsg = MediaKindMsg.valueOf(name)

    fun MediaKindMsg.toKind(): MediaKind = MediaKind.valueOf(name)

    fun SessionPhase.toMsg(): SessionPhaseMsg = SessionPhaseMsg.valueOf(name)

    fun SessionPhaseMsg.toPhase(): SessionPhase = SessionPhase.valueOf(name)

    fun SeekModeMsg.toMode(): SeekMode = SeekMode.valueOf(name)

    fun SeekMode.toMsg(): SeekModeMsg = SeekModeMsg.valueOf(name)

    fun EditPhase.toMsg(): EditPhaseMsg = EditPhaseMsg.valueOf(name)

    fun EditPhaseMsg.toPhase(): EditPhase = EditPhase.valueOf(name)

    // ------------------------------------------------------------------ errors and results

    fun VideoKitStableError.toMsg(): StableErrorMsg =
        StableErrorMsg(code.name, stage.name, retryable, suggestedAction.name, diagnostic, params)

    fun StableErrorMsg.toError(): VideoKitStableError = VideoKitStableError(
        code = ErrorCode.fromWireName(code),
        stage = ErrorStage.fromWireName(stage),
        retryable = retryable,
        suggestedAction = SuggestedAction.fromWireName(suggestedAction),
        diagnostic = diagnostic,
        params = params,
    )

    fun VideoKitCommandResult.toMsg(): CommandResultMsg = when (this) {
        VideoKitCommandResult.Executed -> CommandResultMsg(CommandResultKind.EXECUTED)
        is VideoKitCommandResult.Rejected -> CommandResultMsg(CommandResultKind.REJECTED, error = error.toMsg())
        VideoKitCommandResult.Superseded -> CommandResultMsg(CommandResultKind.SUPERSEDED)
        is VideoKitCommandResult.Unsupported -> CommandResultMsg(CommandResultKind.UNSUPPORTED, unsupportedReason = reason.name)
        VideoKitCommandResult.SessionReleased -> CommandResultMsg(CommandResultKind.SESSION_RELEASED)
    }

    fun CommandResultMsg.toResult(): VideoKitCommandResult = when (kind) {
        CommandResultKind.EXECUTED -> VideoKitCommandResult.Executed

        CommandResultKind.REJECTED -> VideoKitCommandResult.Rejected(
            error?.toError() ?: VideoKitStableError(ErrorCode.INTERNAL_ERROR_REDACTED, ErrorStage.UNKNOWN, false),
        )

        CommandResultKind.SUPERSEDED -> VideoKitCommandResult.Superseded

        CommandResultKind.UNSUPPORTED -> VideoKitCommandResult.Unsupported(UnsupportedReason.fromWireName(unsupportedReason))

        CommandResultKind.SESSION_RELEASED -> VideoKitCommandResult.SessionReleased
    }

    /** Internal failures inside a channel method become `rejected(INTERNAL_ERROR_REDACTED)` (14 §8.3). */
    fun internalFailure(failure: Throwable): CommandResultMsg = VideoKitCommandResult.Rejected(redacted(failure)).toMsg()

    fun redacted(failure: Throwable): VideoKitStableError = VideoKitStableError(
        ErrorCode.INTERNAL_ERROR_REDACTED,
        ErrorStage.UNKNOWN,
        false,
        diagnostic = "CHANNEL:${failure.javaClass.simpleName}",
    )

    // ------------------------------------------------------------------ session values

    fun TrackInfo.toMsg(): TrackInfoMsg = TrackInfoMsg(id, language, label, codec, supported, channelCount?.toLong())

    fun TrackInfoMsg.toTrack(): TrackInfo = TrackInfo(id, language, label, codec, supported, channelCount?.toInt())

    fun MediaTransform.toMsg(): TransformMsg =
        TransformMsg(scale.toDouble(), panX.toDouble(), panY.toDouble(), rotationDeg.toLong(), fitMode.name)

    fun TransformMsg.toTransform(): MediaTransform =
        MediaTransform(scale.toFloat(), panX.toFloat(), panY.toFloat(), rotationDeg.toInt(), wire(fitMode, FitMode.FIT))

    fun OrientationState.toMsg(): OrientationStateMsg = OrientationStateMsg(request.name, contentOrientation.name, fullscreen)

    fun OrientationStateMsg.toOrientation(): OrientationState = OrientationState(
        request = wire(request, OrientationRequest.AUTO),
        contentOrientation = wire(contentOrientation, MediaOrientation.UNKNOWN),
        fullscreen = fullscreen,
    )

    fun HostIcon.toMsg(): HostIconMsg = when (this) {
        is HostIcon.BuiltIn -> HostIconMsg(builtInKey = iconKey)
        is HostIcon.Resource -> HostIconMsg(resourceRef = resourceRef)
    }

    fun HostIconMsg.toIcon(): HostIcon = resourceRef?.let { HostIcon.Resource(it) } ?: HostIcon.BuiltIn(builtInKey ?: "")

    fun VideoKitHostAction.toMsg(): HostActionMsg = HostActionMsg(
        actionId, labelKey, contentDescriptionKey, icon.toMsg(), enabled, selected, pending, badgeText,
        displayPriority.toLong(), placement.name,
    )

    fun HostActionMsg.toAction(): VideoKitHostAction = VideoKitHostAction(
        actionId = actionId,
        labelKey = labelKey,
        contentDescriptionKey = contentDescriptionKey,
        icon = icon.toIcon(),
        enabled = enabled,
        selected = selected,
        pending = pending,
        badgeText = badgeText,
        displayPriority = displayPriority.toInt(),
        placement = wire(placement, ActionPlacement.OVERFLOW),
    )

    fun HostActionState.toMsg(): HostActionStateMsg = HostActionStateMsg(action.toMsg(), pending, lastStatus?.name, lastError?.toMsg())

    fun HostActionStateMsg.toState(): HostActionState = HostActionState(
        action = action.toAction(),
        pending = pending,
        lastStatus = lastStatus?.let { wire(it, HostActionStatus.FAILED) },
        lastError = lastError?.toError(),
    )

    fun VideoKitSessionConfig.toMsg(): SessionConfigMsg =
        SessionConfigMsg(purpose.name, priority.name, initialVisibility.name, initialActiveAudio, debugTag)

    fun SessionConfigMsg.toConfig(): VideoKitSessionConfig = VideoKitSessionConfig(
        purpose = wire(purpose, SessionPurpose.SINGLE),
        priority = wire(priority, ResourcePriority.VISIBLE),
        initialVisibility = wire(initialVisibility, SessionVisibility.VISIBLE),
        initialActiveAudio = initialActiveAudio,
        debugTag = debugTag,
    )

    fun VideoKitSessionState.toMsg(): SessionStateMsg = SessionStateMsg(
        phase = phase.toMsg(),
        mediaKind = mediaKind?.toMsg(),
        positionUs = positionUs,
        durationUs = durationUs,
        bufferedUs = bufferedUs,
        playWhenReady = playWhenReady,
        speed = speed.toDouble(),
        volume = volume.toDouble(),
        muted = muted,
        audioTracks = audioTracks.map { it.toMsg() },
        subtitleTracks = subtitleTracks.map { it.toMsg() },
        selectedAudioTrackId = selectedAudioTrackId,
        selectedSubtitleTrackId = selectedSubtitleTrackId,
        transform = transform.toMsg(),
        orientation = orientation.toMsg(),
        visibility = visibility.name,
        activeAudio = activeAudio,
        controlsVisible = controlsVisible,
        error = error?.toMsg(),
        resourcesHeld = resourcesHeld,
        seekingToUs = seekingToUs,
        hostActions = hostActions.map { it.toMsg() },
        videoWidth = videoSize?.width?.toLong(),
        videoHeight = videoSize?.height?.toLong(),
        hiddenForLock = hiddenForLock,
        looping = looping,
        imageDetails = imageDetails?.let { ImageDetailsMsg(it.frameCount?.toLong(), it.decodedBytes, it.sampleSize?.toLong()) },
        mediaInfo = mediaInfo?.toMsg(),
    )

    fun SessionStateMsg.toState(): VideoKitSessionState = VideoKitSessionState(
        phase = phase.toPhase(),
        mediaKind = mediaKind?.toKind(),
        positionUs = positionUs,
        durationUs = durationUs,
        bufferedUs = bufferedUs,
        playWhenReady = playWhenReady,
        speed = speed.toFloat(),
        volume = volume.toFloat(),
        muted = muted,
        audioTracks = audioTracks.map { it.toTrack() },
        subtitleTracks = subtitleTracks.map { it.toTrack() },
        selectedAudioTrackId = selectedAudioTrackId,
        selectedSubtitleTrackId = selectedSubtitleTrackId,
        transform = transform.toTransform(),
        orientation = orientation.toOrientation(),
        visibility = wire(visibility, SessionVisibility.VISIBLE),
        activeAudio = activeAudio,
        controlsVisible = controlsVisible,
        error = error?.toError(),
        resourcesHeld = resourcesHeld,
        seekingToUs = seekingToUs,
        hostActions = hostActions.map { it.toState() },
        videoSize = if (videoWidth != null && videoHeight != null) Size(videoWidth.toInt(), videoHeight.toInt()) else null,
        hiddenForLock = hiddenForLock,
        looping = looping,
        imageDetails = imageDetails?.let { ImageDetails(it.frameCount?.toInt(), it.decodedBytes, it.sampleSize?.toInt()) },
        mediaInfo = mediaInfo?.toInfo(),
    )

    fun MediaInfo.toMsg(): MediaInfoMsg = MediaInfoMsg(
        container = container,
        videoCodec = videoCodec,
        audioCodec = audioCodec,
        width = width?.toLong(),
        height = height?.toLong(),
        frameRate = frameRate?.toDouble(),
        bitrateBps = bitrateBps,
        rotationDeg = rotationDeg?.toLong(),
        durationUs = durationUs,
        fileSizeBytes = fileSizeBytes,
    )

    fun MediaInfoMsg.toInfo(): MediaInfo = MediaInfo(
        container = container,
        videoCodec = videoCodec,
        audioCodec = audioCodec,
        width = width?.toInt(),
        height = height?.toInt(),
        frameRate = frameRate?.toFloat(),
        bitrateBps = bitrateBps,
        rotationDeg = rotationDeg?.toInt(),
        durationUs = durationUs,
        fileSizeBytes = fileSizeBytes,
    )

    fun ThumbnailResult.toMsg(): ThumbnailResultMsg = when (this) {
        is ThumbnailResult.Captured -> ThumbnailResultMsg(bytes, width.toLong(), height.toLong(), mimeType)
        is ThumbnailResult.Failed -> ThumbnailResultMsg(error = error.toMsg())
    }

    fun ThumbnailResultMsg.toResult(): ThumbnailResult {
        val data = bytes
        return if (data != null && width != null && height != null) {
            ThumbnailResult.Captured(data, width.toInt(), height.toInt(), mimeType ?: "image/jpeg")
        } else {
            ThumbnailResult.Failed(error?.toError() ?: redacted(IllegalStateException("THUMBNAIL_WITHOUT_DATA")))
        }
    }

    fun VideoKitPlaybackState.toMsg(): PlaybackStateMsg = PlaybackStateMsg(
        schemaVersion = schemaVersion.toLong(),
        sessionId = sessionId,
        mediaToken = mediaToken,
        zoom = zoom.toDouble(),
        panX = panX.toDouble(),
        panY = panY.toDouble(),
        rotationDeg = rotationDeg.toLong(),
        fitMode = fitMode.name,
        preferredOrientation = preferredOrientation.name,
        fullscreen = fullscreen,
        positionUs = positionUs,
        speed = speed?.toDouble(),
        volume = volume?.toDouble(),
        muted = muted,
        subtitleTrackId = subtitleTrackId,
        subtitlesEnabled = subtitlesEnabled,
        audioTrackId = audioTrackId,
        lastViewedAtEpochMs = lastViewedAtEpochMs,
        looping = looping,
    )

    fun PlaybackStateMsg.toPlaybackState(): VideoKitPlaybackState = VideoKitPlaybackState(
        schemaVersion = schemaVersion.toInt(),
        sessionId = sessionId,
        mediaToken = mediaToken,
        zoom = zoom.toFloat(),
        panX = panX.toFloat(),
        panY = panY.toFloat(),
        rotationDeg = rotationDeg.toInt(),
        fitMode = wire(fitMode, FitMode.FIT),
        preferredOrientation = wire(preferredOrientation, OrientationRequest.AUTO),
        fullscreen = fullscreen,
        positionUs = positionUs,
        speed = speed?.toFloat(),
        volume = volume?.toFloat(),
        muted = muted,
        subtitleTrackId = subtitleTrackId,
        subtitlesEnabled = subtitlesEnabled,
        audioTrackId = audioTrackId,
        lastViewedAtEpochMs = lastViewedAtEpochMs,
        looping = looping,
    )

    fun VideoKitEvent.toMsg(): EventMsg = when (this) {
        VideoKitEvent.PlaybackEnded -> EventMsg(type = "PLAYBACK_ENDED")
        is VideoKitEvent.SourceReleased -> EventMsg(type = "SOURCE_RELEASED", mediaToken = mediaToken)
        is VideoKitEvent.HostActionFailed -> EventMsg(type = "HOST_ACTION_FAILED", actionId = actionId, error = error.toMsg())
        is VideoKitEvent.TransientNotice -> EventMsg(type = "TRANSIENT_NOTICE", noticeCode = code)
        is VideoKitEvent.ErrorRaised -> EventMsg(type = "ERROR_RAISED", error = error.toMsg())
    }

    /** Unknown event types are dropped (`null`): events are one-off notices, never state (14 §3.2). */
    fun EventMsg.toEvent(): VideoKitEvent? = when (type) {
        "PLAYBACK_ENDED" -> VideoKitEvent.PlaybackEnded
        "SOURCE_RELEASED" -> mediaToken?.let { VideoKitEvent.SourceReleased(it) }
        "HOST_ACTION_FAILED" -> if (actionId != null && error != null) VideoKitEvent.HostActionFailed(actionId, error.toError()) else null
        "TRANSIENT_NOTICE" -> noticeCode?.let { VideoKitEvent.TransientNotice(it) }
        "ERROR_RAISED" -> error?.let { VideoKitEvent.ErrorRaised(it.toError()) }
        else -> null
    }

    /** 04A P6: wire name LOCAL / SLOW; missing or unknown is LOCAL. */
    fun MediaSourceMsg.latency(): SourceLatency = wire(latencyHint, SourceLatency.LOCAL)

    fun MediaSourceMsg.toSource(factory: VideoKitSourceFactory): VideoKitMediaSource = VideoKitMediaSource(
        mediaToken = mediaToken,
        mediaKind = mediaKind.toKind(),
        displayName = displayName,
        knownLength = knownLength,
        mimeType = mimeType,
        extension = extension,
        seekability = if (randomAccess) Seekability.RANDOM_ACCESS else Seekability.SEQUENTIAL_ONLY,
        sourceFactory = factory,
        latencyHint = latency(),
    )

    fun VideoKitMediaSource.toMsg(sourceRef: String): MediaSourceMsg = MediaSourceMsg(
        mediaToken = mediaToken,
        mediaKind = mediaKind.toMsg(),
        displayName = displayName,
        knownLength = knownLength,
        mimeType = mimeType,
        extension = extension,
        randomAccess = seekability == Seekability.RANDOM_ACCESS,
        sourceRef = sourceRef,
        latencyHint = latencyHint.name,
    )

    // ------------------------------------------------------------------ capabilities

    fun CapabilityRequestMsg.toRequest(sourceFor: (MediaSourceMsg) -> VideoKitMediaSource?): CapabilityRequest =
        CapabilityRequest(source = source?.let(sourceFor))

    fun MediaProbeResult.toMsg(): MediaProbeMsg = MediaProbeMsg(
        mediaToken = mediaToken,
        playable = playable.name,
        editable = editable.name,
        fastConcatEligible = fastConcatEligible,
        durationUs = durationUs,
        width = size?.width?.toLong(),
        height = size?.height?.toLong(),
        error = error?.toMsg(),
    )

    fun MediaProbeMsg.toProbe(): MediaProbeResult = MediaProbeResult(
        mediaToken = mediaToken,
        playable = wire(playable, SupportLevel.UNSUPPORTED),
        editable = wire(editable, SupportLevel.UNSUPPORTED),
        fastConcatEligible = fastConcatEligible,
        durationUs = durationUs,
        size = if (width != null && height != null) Size(width.toInt(), height.toInt()) else null,
        error = error?.toError(),
    )

    fun VideoKitCapabilities.toMsg(): CapabilitiesMsg = CapabilitiesMsg(
        schemaVersion = schemaVersion.toLong(),
        isDemo = isDemo,
        suggestedHardwareVideoSessions = suggestedHardwareVideoSessions.toLong(),
        maxWidth = maxSuggestedResolution.width.toLong(),
        maxHeight = maxSuggestedResolution.height.toLong(),
        maxFrameRate = maxSuggestedFrameRate.toLong(),
        subtitles = playbackFeatures.subtitles.name,
        audioTrackSelection = playbackFeatures.audioTrackSelection,
        speeds = playbackFeatures.speeds.map { it.toDouble() },
        exactSeek = playbackFeatures.exactSeek,
        staticImages = imageFeatures.staticImages,
        animatedImages = imageFeatures.animatedImages,
        largeImageTiling = imageFeatures.largeImageTiling,
        singleVideoClips = editFeatures.singleVideoClips,
        multiInputConcat = editFeatures.multiInputConcat,
        manualMasks = editFeatures.manualMasks,
        faceTracking = tracking.face.name,
        objectTracking = tracking.objectTracking.name,
        unavailableReasons = unavailableReasons.entries.associate { (key, reason) -> key.name to reason.name },
        mediaProbe = mediaProbe?.toMsg(),
        hiddenFeatures = VideoKitFeature.CONFIGURABLE.filter { it in hiddenFeatures }.map { it.name },
    )

    /** The summary carried by protocol 1 (codec and format lists are not part of it). */
    fun CapabilitiesMsg.toCapabilities(): VideoKitCapabilities = VideoKitCapabilities(
        schemaVersion = schemaVersion.toInt(),
        isDemo = isDemo,
        suggestedHardwareVideoSessions = suggestedHardwareVideoSessions.toInt(),
        maxSuggestedResolution = Size(maxWidth.toInt(), maxHeight.toInt()),
        maxSuggestedFrameRate = maxFrameRate.toInt(),
        playbackFeatures = com.videokit.api.PlaybackFeatures(
            subtitles = wire(subtitles, SupportLevel.UNSUPPORTED),
            audioTrackSelection = audioTrackSelection,
            speeds = speeds.map { it.toFloat() },
            exactSeek = exactSeek,
        ),
        imageFeatures = com.videokit.api.ImageFeatures(staticImages, animatedImages, largeImageTiling),
        editFeatures = com.videokit.api.EditFeatures(singleVideoClips, multiInputConcat, manualMasks),
        tracking = com.videokit.api.TrackingStatus(
            face = wire(faceTracking, TrackingModuleStatus.NOT_INSTALLED),
            objectTracking = wire(objectTracking, TrackingModuleStatus.NOT_INSTALLED),
        ),
        // Unknown feature keys decode to FeatureKey.UNKNOWN (04A T3).
        unavailableReasons = unavailableReasons.entries
            .associate { (key, reason) -> FeatureKey.fromWireName(key) to UnsupportedReason.fromWireName(reason) },
        mediaProbe = mediaProbe?.toProbe(),
        hiddenFeatures = hiddenFeatures.orEmpty().map(VideoKitFeature::fromWireName).filter { it != VideoKitFeature.UNKNOWN }.toSet(),
    )

    // ------------------------------------------------------------------ feature switches and gate (REQ-API-10)

    /** `FeatureAccessMsg.access` of an allowed answer. */
    const val ALLOWED: String = "ALLOWED"

    /** `FeatureAccessMsg.access` of a denied answer. */
    const val DENIED: String = "DENIED"

    /** `HandshakeRequest.features`: unknown feature names are dropped, unknown modes read as ENABLED. */
    fun features(wire: Map<String, String>?): Map<VideoKitFeature, FeatureMode> = wire.orEmpty().entries
        .map { (name, mode) -> VideoKitFeature.fromWireName(name) to FeatureMode.fromWireName(mode) }
        .filter { it.first != VideoKitFeature.UNKNOWN }
        .toMap()

    /** The Dart host's answer; anything but `ALLOWED` is denied. */
    fun featureAccess(msg: FeatureAccessMsg): FeatureAccess {
        val badge = FeatureBadge.fromWireName(msg.badge)
        return if (msg.access == ALLOWED) FeatureAccess.Allowed(badge) else FeatureAccess.Denied(badge)
    }

    // ------------------------------------------------------------------ host callbacks

    fun HostActionRequest.toMsg(): HostActionRequestMsg = HostActionRequestMsg(actionId, sessionId, mediaToken)

    fun HostActionRequestMsg.toRequest(): HostActionRequest = HostActionRequest(actionId, sessionId, mediaToken)

    fun HostActionResult.toMsg(): HostActionResultMsg = HostActionResultMsg(status.name, updatedAction?.toMsg(), messageKey)

    fun HostActionResultMsg.toResult(): HostActionResult =
        HostActionResult(wire(status, HostActionStatus.FAILED), updatedAction?.toAction(), messageKey)

    fun NavigationRequest.toMsg(): NavigationRequestMsg = NavigationRequestMsg(sessionId, mediaToken, direction.name)

    fun NavigationRequestMsg.toRequest(): NavigationRequest =
        NavigationRequest(sessionId, mediaToken, wire(direction, NavigationDirection.NEXT))

    fun navigationResult(name: String?): NavigationResult = wire(name, NavigationResult.FAILED)

    fun recoveryDecision(name: String?): RecoveryDecision = wire(name, RecoveryDecision.KEEP_ERROR)

    fun VideoKitPlaybackEvent.toMsg(): PlaybackEventMsg = when (this) {
        is VideoKitPlaybackEvent.PositionTick -> PlaybackEventMsg(sessionId, "POSITION_TICK", positionUs = positionUs)

        is VideoKitPlaybackEvent.PlayStateChanged ->
            PlaybackEventMsg(sessionId, "PLAY_STATE_CHANGED", phase = phase.toMsg(), playWhenReady = playWhenReady)

        is VideoKitPlaybackEvent.BufferingStarted -> PlaybackEventMsg(sessionId, "BUFFERING_STARTED", positionUs = positionUs)

        is VideoKitPlaybackEvent.BufferingEnded -> PlaybackEventMsg(sessionId, "BUFFERING_ENDED", durationUs = durationUs)

        is VideoKitPlaybackEvent.UserSeek -> PlaybackEventMsg(sessionId, "USER_SEEK", fromUs = fromUs, toUs = toUs)

        is VideoKitPlaybackEvent.VisibilityChanged -> PlaybackEventMsg(sessionId, "VISIBILITY_CHANGED", visibility = visibility.name)

        is VideoKitPlaybackEvent.ForegroundChanged -> PlaybackEventMsg(sessionId, "FOREGROUND_CHANGED", foreground = foreground)

        is VideoKitPlaybackEvent.WatchTimeAccumulated -> PlaybackEventMsg(sessionId, "WATCH_TIME_ACCUMULATED", deltaUs = deltaUs)

        is VideoKitPlaybackEvent.SessionEnded -> PlaybackEventMsg(sessionId, "SESSION_ENDED", mediaToken = mediaToken)
    }

    fun PlaybackEventMsg.toEvent(): VideoKitPlaybackEvent? = when (type) {
        "POSITION_TICK" -> positionUs?.let { VideoKitPlaybackEvent.PositionTick(sessionId, it) }
        "PLAY_STATE_CHANGED" -> phase?.let { VideoKitPlaybackEvent.PlayStateChanged(sessionId, it.toPhase(), playWhenReady ?: false) }
        "BUFFERING_STARTED" -> positionUs?.let { VideoKitPlaybackEvent.BufferingStarted(sessionId, it) }
        "BUFFERING_ENDED" -> durationUs?.let { VideoKitPlaybackEvent.BufferingEnded(sessionId, it) }
        "USER_SEEK" -> if (fromUs != null && toUs != null) VideoKitPlaybackEvent.UserSeek(sessionId, fromUs, toUs) else null
        "VISIBILITY_CHANGED" -> visibility?.let { VideoKitPlaybackEvent.VisibilityChanged(sessionId, wire(it, SessionVisibility.VISIBLE)) }
        "FOREGROUND_CHANGED" -> foreground?.let { VideoKitPlaybackEvent.ForegroundChanged(sessionId, it) }
        "WATCH_TIME_ACCUMULATED" -> deltaUs?.let { VideoKitPlaybackEvent.WatchTimeAccumulated(sessionId, it) }
        "SESSION_ENDED" -> VideoKitPlaybackEvent.SessionEnded(sessionId, mediaToken)
        else -> null
    }

    // ------------------------------------------------------------------ edit projects

    fun EditProjectConfig.toMsg(): EditProjectConfigMsg =
        EditProjectConfigMsg(allowedPresets.map { it.name }.sorted(), trackingAllowed, initialPositionUs)

    fun EditProjectConfigMsg.toConfig(): EditProjectConfig = EditProjectConfig(
        allowedPresets = allowedPresets.mapNotNull { name -> enumValues<ExportPreset>().firstOrNull { it.name == name } }.toSet(),
        trackingAllowed = trackingAllowed,
        initialPositionUs = initialPositionUs,
    )

    fun MaskRegion.toMsg(): MaskRegionMsg =
        MaskRegionMsg(x.toDouble(), y.toDouble(), width.toDouble(), height.toDouble(), rotationDeg.toDouble())

    fun MaskRegionMsg.toRegion(): MaskRegion =
        MaskRegion(x.toFloat(), y.toFloat(), width.toFloat(), height.toFloat(), rotationDeg.toFloat())

    fun TimeRangeUs.toMsg(): TimeRangeMsg = TimeRangeMsg(startUs, endUs)

    fun TimeRangeMsg.toRange(): TimeRangeUs = TimeRangeUs(startUs, endUs)

    fun VideoKitEditCommand.toMsg(): EditCommandMsg = when (this) {
        is VideoKitEditCommand.AddClip -> EditCommandMsg(
            "AddClip",
            sourceId = sourceId,
            inUs = inUs,
            outUs = outUs,
            index = index?.toLong(),
        )

        is VideoKitEditCommand.SplitAt -> EditCommandMsg("SplitAt", clipId = clipId, atUs = atUs)

        is VideoKitEditCommand.TrimClip -> EditCommandMsg("TrimClip", clipId = clipId, inUs = inUs, outUs = outUs)

        is VideoKitEditCommand.RemoveClip -> EditCommandMsg("RemoveClip", clipId = clipId)

        is VideoKitEditCommand.MoveClip -> EditCommandMsg("MoveClip", clipId = clipId, toIndex = toIndex.toLong())

        is VideoKitEditCommand.AddMask -> EditCommandMsg(
            "AddMask",
            maskType = type.name,
            region = region.toMsg(),
            startUs = rangeUs.startUs,
            endUs = rangeUs.endUs,
            style = style.name,
            strength = strength.toDouble(),
        )

        is VideoKitEditCommand.UpdateMaskKeyframe -> EditCommandMsg(
            "UpdateMaskKeyframe",
            maskId = maskId,
            atUs = atUs,
            region = region.toMsg(),
        )

        is VideoKitEditCommand.RemoveMaskKeyframe -> EditCommandMsg("RemoveMaskKeyframe", maskId = maskId, atUs = atUs)

        is VideoKitEditCommand.SetMaskStyle -> EditCommandMsg(
            "SetMaskStyle",
            maskId = maskId,
            style = style.name,
            strength = strength.toDouble(),
        )

        is VideoKitEditCommand.SetMaskEnabled -> EditCommandMsg("SetMaskEnabled", maskId = maskId, enabled = enabled)

        is VideoKitEditCommand.SetMaskAvatar -> EditCommandMsg("SetMaskAvatar", maskId = maskId, avatar = avatar.toMsg())

        is VideoKitEditCommand.RemoveMask -> EditCommandMsg("RemoveMask", maskId = maskId)

        is VideoKitEditCommand.StartTracking ->
            EditCommandMsg("StartTracking", maskId = maskId, trackingKind = kind.name, region = seedRegion?.toMsg(), targetId = targetId)

        is VideoKitEditCommand.CorrectTracking -> EditCommandMsg("CorrectTracking", maskId = maskId, atUs = atUs, region = region.toMsg())

        is VideoKitEditCommand.CancelTracking -> EditCommandMsg("CancelTracking", maskId = maskId)

        is VideoKitEditCommand.AcceptTrackingRange ->
            EditCommandMsg("AcceptTrackingRange", maskId = maskId, startUs = rangeUs.startUs, endUs = rangeUs.endUs)
    }

    /** Returns `null` for unknown kinds or missing required fields; the caller answers `rejected(INVALID_ARGUMENT)`. */
    fun EditCommandMsg.toCommand(): VideoKitEditCommand? = runCatching {
        when (kind) {
            "AddClip" -> VideoKitEditCommand.AddClip(sourceId!!, inUs!!, outUs!!, index?.toInt())

            "SplitAt" -> VideoKitEditCommand.SplitAt(clipId!!, atUs!!)

            "TrimClip" -> VideoKitEditCommand.TrimClip(clipId!!, inUs!!, outUs!!)

            "RemoveClip" -> VideoKitEditCommand.RemoveClip(clipId!!)

            "MoveClip" -> VideoKitEditCommand.MoveClip(clipId!!, toIndex!!.toInt())

            "AddMask" -> VideoKitEditCommand.AddMask(
                type = wire(maskType, MaskType.MANUAL),
                region = region!!.toRegion(),
                rangeUs = TimeRangeUs(startUs!!, endUs!!),
                style = wire(style, MaskStyle.MOSAIC),
                strength = (strength ?: 0.5).toFloat(),
            )

            "UpdateMaskKeyframe" -> VideoKitEditCommand.UpdateMaskKeyframe(maskId!!, atUs!!, region!!.toRegion())

            "RemoveMaskKeyframe" -> VideoKitEditCommand.RemoveMaskKeyframe(maskId!!, atUs!!)

            "SetMaskStyle" -> VideoKitEditCommand.SetMaskStyle(maskId!!, wire(style, MaskStyle.MOSAIC), strength!!.toFloat())

            "SetMaskEnabled" -> VideoKitEditCommand.SetMaskEnabled(maskId!!, enabled!!)

            "SetMaskAvatar" -> VideoKitEditCommand.SetMaskAvatar(maskId!!, avatar!!.toAvatar())

            "RemoveMask" -> VideoKitEditCommand.RemoveMask(maskId!!)

            "StartTracking" -> VideoKitEditCommand.StartTracking(
                maskId!!,
                enumValues<TrackingKind>().first { it.name == trackingKind },
                region?.toRegion(),
                targetId,
            )

            "CorrectTracking" -> VideoKitEditCommand.CorrectTracking(maskId!!, atUs!!, region!!.toRegion())

            "CancelTracking" -> VideoKitEditCommand.CancelTracking(maskId!!)

            "AcceptTrackingRange" -> VideoKitEditCommand.AcceptTrackingRange(maskId!!, TimeRangeUs(startUs!!, endUs!!))

            else -> null
        }
    }.getOrNull()

    fun EditCommandResult.toMsg(): EditResultMsg = when (this) {
        is EditCommandResult.Applied -> EditResultMsg(EditResultKind.APPLIED, revision = revision, createdId = createdId)
        is EditCommandResult.Rejected -> EditResultMsg(EditResultKind.REJECTED, error = error.toMsg())
        is EditCommandResult.Unsupported -> EditResultMsg(EditResultKind.UNSUPPORTED, unsupportedReason = reason.name)
        EditCommandResult.ProjectReleased -> EditResultMsg(EditResultKind.PROJECT_RELEASED)
    }

    fun EditResultMsg.toResult(): EditCommandResult = when (kind) {
        EditResultKind.APPLIED -> EditCommandResult.Applied(revision ?: 0L, createdId)

        EditResultKind.REJECTED -> EditCommandResult.Rejected(
            error?.toError() ?: VideoKitStableError(ErrorCode.INTERNAL_ERROR_REDACTED, ErrorStage.UNKNOWN, false),
        )

        EditResultKind.UNSUPPORTED -> EditCommandResult.Unsupported(UnsupportedReason.fromWireName(unsupportedReason))

        EditResultKind.PROJECT_RELEASED -> EditCommandResult.ProjectReleased
    }

    fun SourceProbe.toMsg(): SourceProbeMsg = SourceProbeMsg(
        durationUs,
        width.toLong(),
        height.toLong(),
        rotationDeg.toLong(),
        frameRate?.toDouble(),
        videoCodec,
        audioCodec,
        hasAudio,
    )

    fun SourceProbeMsg.toProbe(): SourceProbe = SourceProbe(
        durationUs,
        width.toInt(),
        height.toInt(),
        rotationDeg.toInt(),
        frameRate?.toFloat(),
        videoCodec,
        audioCodec,
        hasAudio,
    )

    fun EditSource.toMsg(): EditSourceMsg = EditSourceMsg(sourceId, mediaToken, displayName, probe?.toMsg(), mismatch)

    fun EditSourceMsg.toSource(): EditSource = EditSource(sourceId, mediaToken, displayName, probe?.toProbe(), mismatch)

    fun Clip.toMsg(): ClipMsg = ClipMsg(clipId, sourceId, inUs, outUs)

    fun ClipMsg.toClip(): Clip = Clip(clipId, sourceId, inUs, outUs)

    fun MaskKeyframe.toMsg(): MaskKeyframeMsg = MaskKeyframeMsg(atUs, region.toMsg(), source.name, quality?.name, rollDeg?.toDouble())

    fun MaskKeyframeMsg.toKeyframe(): MaskKeyframe = MaskKeyframe(
        atUs = atUs,
        region = region.toRegion(),
        source = wire(source, KeyframeSource.USER),
        quality = quality?.let { wire(it, CoverageQuality.NOT_ANALYZED) }, // unknown: NOT_ANALYZED (schema R4, as Dart)
        rollDeg = rollDeg?.toFloat(),
    )

    fun MaskAvatar.toMsg(): MaskAvatarMsg =
        MaskAvatarMsg(avatarToken, scale.toDouble(), offsetX.toDouble(), offsetY.toDouble(), followRotation)

    fun MaskAvatarMsg.toAvatar(): MaskAvatar =
        MaskAvatar(avatarToken, scale.toFloat(), offsetX.toFloat(), offsetY.toFloat(), followRotation)

    fun MaskTrack.toMsg(): MaskTrackMsg = MaskTrackMsg(
        maskId,
        type.name,
        style.name,
        strength.toDouble(),
        enabled,
        rangeUs.toMsg(),
        keyframes.map {
            it.toMsg()
        },
        acceptedRangesUs.map { it.toMsg() },
        avatar?.toMsg(),
    )

    fun MaskTrackMsg.toMask(): MaskTrack = MaskTrack(
        maskId = maskId,
        type = wire(type, MaskType.MANUAL),
        // IMAGE without an avatar reads as MOSAIC (schema R7), as in Dart.
        style = wire(style, MaskStyle.MOSAIC).let { if (it == MaskStyle.IMAGE && avatar == null) MaskStyle.MOSAIC else it },
        strength = strength.toFloat(),
        enabled = enabled,
        rangeUs = range.toRange(),
        keyframes = keyframes.map { it.toKeyframe() },
        acceptedRangesUs = acceptedRanges.map { it.toRange() },
        avatar = avatar?.toAvatar(),
    )

    fun CoverageRange.toMsg(): CoverageRangeMsg = CoverageRangeMsg(rangeUs.toMsg(), quality.name, maskId)

    fun CoverageRangeMsg.toCoverage(): CoverageRange = CoverageRange(range.toRange(), wire(quality, CoverageQuality.NOT_ANALYZED), maskId)

    fun TrackingRun.toMsg(): TrackingRunMsg = TrackingRunMsg(
        maskId = maskId,
        status = status.name,
        progress = progress?.toDouble(),
        coverage = coverage?.ranges.orEmpty().map { it.toMsg() },
        error = error?.toMsg(),
    )

    fun TrackingRunMsg.toRun(): TrackingRun = TrackingRun(
        maskId = maskId,
        status = wire(status, TrackingRunStatus.FAILED),
        progress = progress?.toFloat(),
        coverage = if (coverage.isEmpty()) {
            null
        } else {
            CoverageReport(
                coverage.map {
                    it.toCoverage()
                },
            )
        },
        error = error?.toError(),
    )

    fun ExportProgress.toMsg(): ExportProgressMsg = ExportProgressMsg(
        exportId,
        stage.name,
        fraction?.toDouble(),
        processedUs,
        processedFrames,
        outputBytes,
        remainingEstimateUs,
        cancellable,
    )

    fun ExportProgressMsg.toProgress(): ExportProgress = ExportProgress(
        exportId = exportId,
        stage = wire(stage, ExportStage.PREPARING),
        fraction = fraction?.toFloat(),
        processedUs = processedUs,
        processedFrames = processedFrames,
        outputBytes = outputBytes,
        remainingEstimateUs = remainingEstimateUs,
        cancellable = cancellable,
    )

    fun VideoKitEditState.toMsg(): EditStateMsg = EditStateMsg(
        phase = phase.toMsg(),
        revision = revision,
        sources = timeline.sources.map { it.toMsg() },
        clips = timeline.clips.map { it.toMsg() },
        masks = masks.map { it.toMsg() },
        tracking = tracking.values.sortedBy { it.maskId }.map { it.toMsg() },
        exportProgress = export?.toMsg(),
        canUndo = canUndo,
        canRedo = canRedo,
        estimateDurationUs = estimate.durationUs,
        estimateSizeBytes = estimate.sizeBytes,
        error = error?.toMsg(),
    )

    fun EditStateMsg.toState(): VideoKitEditState = VideoKitEditState(
        phase = phase.toPhase(),
        revision = revision,
        timeline = Timeline(sources.map { it.toSource() }, clips.map { it.toClip() }),
        masks = masks.map { it.toMask() },
        tracking = tracking.map { it.toRun() }.associateBy { it.maskId },
        export = exportProgress?.toProgress(),
        canUndo = canUndo,
        canRedo = canRedo,
        estimate = EditEstimate(estimateDurationUs, estimateSizeBytes),
        error = error?.toError(),
    )

    fun VideoKitEditEvent.toMsg(): EditEventMsg = when (this) {
        is VideoKitEditEvent.SourceProbed -> EditEventMsg("SOURCE_PROBED", sourceId = sourceId)
        is VideoKitEditEvent.SourceMismatch -> EditEventMsg("SOURCE_MISMATCH", sourceId = sourceId)
        is VideoKitEditEvent.TrackingLost -> EditEventMsg("TRACKING_LOST", maskId = maskId, range = rangeUs.toMsg())
        is VideoKitEditEvent.ExportStageChanged -> EditEventMsg("EXPORT_STAGE_CHANGED", exportId = exportId, stage = stage.name)
        is VideoKitEditEvent.ExportCompleted -> EditEventMsg("EXPORT_COMPLETED", exportId = result.exportId)
        is VideoKitEditEvent.ExportFailed -> EditEventMsg("EXPORT_FAILED", exportId = exportId, error = error.toMsg())
        is VideoKitEditEvent.ExportCancelled -> EditEventMsg("EXPORT_CANCELLED", exportId = exportId)
        is VideoKitEditEvent.Warning -> EditEventMsg("WARNING", code = code)
        VideoKitEditEvent.ResourcesReleased -> EditEventMsg("RESOURCES_RELEASED")
    }

    fun SerializedEditProject.toMsg(): SerializedProjectMsg = SerializedProjectMsg(schemaVersion.toLong(), json)

    fun SerializedProjectMsg.toSerialized(): SerializedEditProject = SerializedEditProject(schemaVersion.toInt(), json)

    fun ExportRequestMsg.toRequest(): VideoKitExportRequest =
        VideoKitExportRequest(preset = wire(preset, ExportPreset.ORIGINAL), exportId = exportId, fileNameHint = fileNameHint)

    fun VideoKitExportRequest.toMsg(sinkRef: String): ExportRequestMsg = ExportRequestMsg(exportId, preset.name, fileNameHint, sinkRef)

    fun ExportPrecheck.toMsg(): PrecheckMsg = PrecheckMsg(
        ok = ok,
        writeMode = writeMode?.name,
        estimateDurationUs = estimate.durationUs,
        estimateSizeBytes = estimate.sizeBytes,
        problems = problems.map { it.toMsg() },
        warnings = warnings,
        uncoveredRanges = uncoveredRanges.map { it.toMsg() },
    )

    fun PrecheckMsg.toPrecheck(): ExportPrecheck = ExportPrecheck(
        ok = ok,
        writeMode = writeMode?.let { name -> enumValues<SinkWriteMode>().firstOrNull { it.name == name } },
        estimate = EditEstimate(estimateDurationUs, estimateSizeBytes),
        problems = problems.map { it.toError() },
        warnings = warnings,
        uncoveredRanges = uncoveredRanges.map { it.toCoverage() },
    )

    fun VideoKitExportedMedia.toMsg(): ExportedMediaMsg = ExportedMediaMsg(
        outputToken = outputToken.value,
        container = container,
        extension = extension,
        videoCodec = videoCodec,
        audioCodec = audioCodec,
        width = width.toLong(),
        height = height.toLong(),
        rotationDeg = rotationDeg.toLong(),
        durationUs = durationUs,
        sizeBytes = sizeBytes,
        frameRate = frameRate?.toDouble(),
        audioPresent = audioPresent,
        createdAtEpochMs = createdAtEpochMs,
        sourceTokens = sourceTokens,
        editProjectId = editProjectId,
        exportPreset = exportPreset.name,
        warnings = warnings,
        isDemo = isDemo,
    )

    fun ExportedMediaMsg.toMedia(): VideoKitExportedMedia = VideoKitExportedMedia(
        outputToken = VideoKitOutputToken(outputToken),
        container = container,
        extension = extension,
        videoCodec = videoCodec,
        audioCodec = audioCodec,
        width = width.toInt(),
        height = height.toInt(),
        rotationDeg = rotationDeg.toInt(),
        durationUs = durationUs,
        sizeBytes = sizeBytes,
        frameRate = frameRate?.toFloat(),
        audioPresent = audioPresent,
        createdAtEpochMs = createdAtEpochMs,
        sourceTokens = sourceTokens,
        editProjectId = editProjectId,
        exportPreset = wire(exportPreset, ExportPreset.ORIGINAL),
        warnings = warnings,
        isDemo = isDemo,
    )

    fun VideoKitExportResult.toMsg(): ExportResultMsg = when (this) {
        is VideoKitExportResult.Succeeded -> ExportResultMsg(ExportResultKind.SUCCEEDED, exportId, media = media.toMsg())

        is VideoKitExportResult.Failed -> ExportResultMsg(ExportResultKind.FAILED, exportId, error = error.toMsg(), stage = stage?.name)

        is VideoKitExportResult.Cancelled ->
            ExportResultMsg(ExportResultKind.CANCELLED, exportId, partialOutputRemoved = partialOutputRemoved)
    }

    fun ExportResultMsg.toResult(): VideoKitExportResult = when (kind) {
        ExportResultKind.SUCCEEDED -> media?.let { VideoKitExportResult.Succeeded(exportId, it.toMedia()) }
            ?: VideoKitExportResult.Failed(exportId, VideoKitStableError(ErrorCode.INTERNAL_ERROR_REDACTED, ErrorStage.EXPORT, false))

        ExportResultKind.FAILED -> VideoKitExportResult.Failed(
            exportId,
            error?.toError() ?: VideoKitStableError(ErrorCode.EXPORT_FAILED, ErrorStage.EXPORT, true),
            stage?.let { wire(it, ExportStage.PREPARING) },
        )

        ExportResultKind.CANCELLED -> VideoKitExportResult.Cancelled(exportId, partialOutputRemoved ?: true)
    }

    fun CandidateDetectionResult.toMsg(): CandidateResultMsg = CandidateResultMsg(
        candidates = candidates.map { TrackingCandidateMsg(it.candidateId, it.kind.name, it.region.toMsg(), it.confidence?.toDouble()) },
        error = error?.toMsg(),
    )

    fun CandidateResultMsg.toResult(): CandidateDetectionResult = CandidateDetectionResult(
        candidates = candidates.map {
            TrackingCandidate(it.candidateId, wire(it.kind, TrackingKind.FACE), it.region.toRegion(), it.confidence?.toFloat())
        },
        error = error?.toError(),
    )
}
