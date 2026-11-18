// Conversions between videokit_api types and the Pigeon channel messages (14 §8.5).
//
// Open enums travel as Kotlin wire names (UPPER_SNAKE, 04A §1.3); unknown names map to the documented
// fallbacks so an older Dart package keeps working against a newer native Kit.
import 'package:videokit_api/videokit_api.dart';
import 'package:videokit_flutter_platform_interface/videokit_flutter_platform_interface.dart';

/// `camelCase` enum name → Kotlin wire name `CAMEL_CASE`.
String wireOf(Enum value) {
  final name = value.name;
  final buffer = StringBuffer();
  for (var i = 0; i < name.length; i++) {
    final ch = name[i];
    final upper = ch.toUpperCase() == ch && ch.toLowerCase() != ch;
    final digit = ch.codeUnitAt(0) >= 0x30 && ch.codeUnitAt(0) <= 0x39;
    if (i > 0 && (upper || (digit && !_isDigit(name.codeUnitAt(i - 1))))) {
      buffer.write('_');
    }
    buffer.write(ch.toUpperCase());
  }
  return buffer.toString();
}

bool _isDigit(int c) => c >= 0x30 && c <= 0x39;

/// Wire name → enum value of [values], or [fallback] for unknown or missing names.
T enumOf<T extends Enum>(List<T> values, String? wire, T fallback) {
  if (wire == null) return fallback;
  for (final value in values) {
    if (wireOf(value) == wire || value.name == wire) return value;
  }
  return fallback;
}

// ------------------------------------------------------------------ errors and results

VideoKitStableError errorFromMsg(StableErrorMsg msg) => VideoKitStableError(
  code: enumOf(ErrorCode.values, msg.code, ErrorCode.internalErrorRedacted),
  stage: enumOf(ErrorStage.values, msg.stage, ErrorStage.unknown),
  retryable: msg.retryable,
  suggestedAction: enumOf(
    SuggestedAction.values,
    msg.suggestedAction,
    SuggestedAction.none,
  ),
  diagnostic: msg.diagnostic,
  params: Map<String, String>.of(msg.params),
);

StableErrorMsg errorToMsg(VideoKitStableError error) => StableErrorMsg(
  code: wireOf(error.code),
  stage: wireOf(error.stage),
  retryable: error.retryable,
  suggestedAction: wireOf(error.suggestedAction),
  diagnostic: error.diagnostic,
  params: Map<String, String>.of(error.params),
);

/// Error used when the channel itself fails (PlatformException, missing reply): INTERNAL_ERROR_REDACTED (14 §8.3).
VideoKitStableError channelError(Object failure) => VideoKitStableError(
  code: ErrorCode.internalErrorRedacted,
  stage: ErrorStage.unknown,
  diagnostic: 'CHANNEL:${failure.runtimeType}',
);

VideoKitCommandResult commandResultFromMsg(CommandResultMsg msg) =>
    switch (msg.kind) {
      CommandResultKind.executed => const Executed(),
      CommandResultKind.rejected => Rejected(
        msg.error == null
            ? channelError('MissingError')
            : errorFromMsg(msg.error!),
      ),
      CommandResultKind.superseded => const Superseded(),
      CommandResultKind.unsupported => Unsupported(
        enumOf(
          UnsupportedReason.values,
          msg.unsupportedReason,
          UnsupportedReason.unknown,
        ),
      ),
      CommandResultKind.sessionReleased => const SessionReleased(),
    };

// ------------------------------------------------------------------ session values

MediaKindMsg mediaKindToMsg(MediaKind kind) =>
    MediaKindMsg.values.byName(kind.name);

MediaKind mediaKindFromMsg(MediaKindMsg kind) =>
    MediaKind.values.byName(kind.name);

SessionPhase sessionPhaseFromMsg(SessionPhaseMsg phase) =>
    SessionPhase.values.byName(phase.name);

SeekModeMsg seekModeToMsg(SeekMode mode) =>
    SeekModeMsg.values.byName(mode.name);

TrackInfo trackFromMsg(TrackInfoMsg msg) => TrackInfo(
  id: msg.id,
  language: msg.language,
  label: msg.label,
  codec: msg.codec,
  supported: msg.supported,
  channelCount: msg.channelCount,
);

TransformMsg transformToMsg(MediaTransform t) => TransformMsg(
  scale: t.scale,
  panX: t.panX,
  panY: t.panY,
  rotationDeg: t.rotationDeg,
  fitMode: wireOf(t.fitMode),
);

MediaTransform transformFromMsg(TransformMsg msg) => MediaTransform(
  scale: msg.scale,
  panX: msg.panX,
  panY: msg.panY,
  rotationDeg: msg.rotationDeg,
  fitMode: enumOf(FitMode.values, msg.fitMode, FitMode.fit),
);

HostIconMsg hostIconToMsg(HostIcon icon) => switch (icon) {
  HostIconBuiltIn(:final iconKey) => HostIconMsg(builtInKey: iconKey),
  HostIconResource(:final resourceRef) => HostIconMsg(resourceRef: resourceRef),
};

HostIcon hostIconFromMsg(HostIconMsg msg) => msg.resourceRef != null
    ? HostIconResource(msg.resourceRef!)
    : HostIconBuiltIn(msg.builtInKey ?? '');

HostActionMsg hostActionToMsg(VideoKitHostAction a) => HostActionMsg(
  actionId: a.actionId,
  labelKey: a.labelKey,
  contentDescriptionKey: a.contentDescriptionKey,
  icon: hostIconToMsg(a.icon),
  enabled: a.enabled,
  selected: a.selected,
  pending: a.pending,
  badgeText: a.badgeText,
  displayPriority: a.displayPriority,
  placement: wireOf(a.placement),
);

VideoKitHostAction hostActionFromMsg(HostActionMsg msg) => VideoKitHostAction(
  actionId: msg.actionId,
  labelKey: msg.labelKey,
  contentDescriptionKey: msg.contentDescriptionKey,
  icon: hostIconFromMsg(msg.icon),
  enabled: msg.enabled,
  selected: msg.selected,
  pending: msg.pending,
  badgeText: msg.badgeText,
  displayPriority: msg.displayPriority,
  placement: enumOf(
    ActionPlacement.values,
    msg.placement,
    ActionPlacement.overflow,
  ),
);

VideoKitSessionState sessionStateFromMsg(
  SessionStateMsg msg,
) => VideoKitSessionState(
  phase: sessionPhaseFromMsg(msg.phase),
  mediaKind: msg.mediaKind == null ? null : mediaKindFromMsg(msg.mediaKind!),
  positionUs: msg.positionUs,
  durationUs: msg.durationUs,
  bufferedUs: msg.bufferedUs,
  seekingToUs: msg.seekingToUs,
  playWhenReady: msg.playWhenReady,
  speed: msg.speed,
  volume: msg.volume,
  muted: msg.muted,
  audioTracks: msg.audioTracks.map(trackFromMsg).toList(),
  subtitleTracks: msg.subtitleTracks.map(trackFromMsg).toList(),
  selectedAudioTrackId: msg.selectedAudioTrackId,
  selectedSubtitleTrackId: msg.selectedSubtitleTrackId,
  transform: transformFromMsg(msg.transform),
  orientation: OrientationState(
    request: enumOf(
      OrientationRequest.values,
      msg.orientation.request,
      OrientationRequest.auto,
    ),
    contentOrientation: enumOf(
      MediaOrientation.values,
      msg.orientation.contentOrientation,
      MediaOrientation.unknown,
    ),
    fullscreen: msg.orientation.fullscreen,
  ),
  visibility: enumOf(
    SessionVisibility.values,
    msg.visibility,
    SessionVisibility.visible,
  ),
  activeAudio: msg.activeAudio,
  controlsVisible: msg.controlsVisible,
  hiddenForLock: msg.hiddenForLock,
  looping: msg.looping,
  imageDetails: msg.imageDetails == null
      ? null
      : ImageDetails(
          frameCount: msg.imageDetails!.frameCount,
          decodedBytes: msg.imageDetails!.decodedBytes,
          sampleSize: msg.imageDetails!.sampleSize,
        ),
  mediaInfo: msg.mediaInfo == null ? null : mediaInfoFromMsg(msg.mediaInfo!),
  error: msg.error == null ? null : errorFromMsg(msg.error!),
  resourcesHeld: msg.resourcesHeld,
  hostActions: msg.hostActions
      .map(
        (s) => HostActionState(
          action: hostActionFromMsg(s.action),
          pending: s.pending,
          lastStatus: s.lastStatus == null
              ? null
              : enumOf(
                  HostActionStatus.values,
                  s.lastStatus,
                  HostActionStatus.failed,
                ),
          lastError: s.lastError == null ? null : errorFromMsg(s.lastError!),
        ),
      )
      .toList(),
);

VideoSize? videoSizeFromMsg(SessionStateMsg msg) =>
    msg.videoWidth != null && msg.videoHeight != null
    ? VideoSize(msg.videoWidth!, msg.videoHeight!)
    : null;

PlaybackStateMsg playbackStateToMsg(VideoKitPlaybackState s) =>
    PlaybackStateMsg(
      schemaVersion: 1,
      sessionId: s.sessionId,
      mediaToken: s.mediaToken,
      zoom: s.zoom,
      panX: s.panX,
      panY: s.panY,
      rotationDeg: s.rotationDeg,
      fitMode: wireOf(s.fitMode),
      preferredOrientation: wireOf(s.preferredOrientation),
      fullscreen: s.fullscreen,
      positionUs: s.positionUs,
      speed: s.speed,
      volume: s.volume,
      muted: s.muted,
      subtitleTrackId: s.subtitleTrackId,
      subtitlesEnabled: s.subtitlesEnabled,
      audioTrackId: s.audioTrackId,
      lastViewedAtEpochMs: s.lastViewedAtEpochMs,
      looping: s.looping,
    );

VideoKitPlaybackState playbackStateFromMsg(PlaybackStateMsg msg) =>
    VideoKitPlaybackState(
      sessionId: msg.sessionId,
      mediaToken: msg.mediaToken,
      zoom: msg.zoom,
      panX: msg.panX,
      panY: msg.panY,
      rotationDeg: msg.rotationDeg,
      fitMode: enumOf(FitMode.values, msg.fitMode, FitMode.fit),
      preferredOrientation: enumOf(
        OrientationRequest.values,
        msg.preferredOrientation,
        OrientationRequest.auto,
      ),
      fullscreen: msg.fullscreen,
      positionUs: msg.positionUs,
      speed: msg.speed,
      volume: msg.volume,
      muted: msg.muted,
      subtitleTrackId: msg.subtitleTrackId,
      subtitlesEnabled: msg.subtitlesEnabled,
      audioTrackId: msg.audioTrackId,
      lastViewedAtEpochMs: msg.lastViewedAtEpochMs,
      looping: msg.looping,
    );

/// Unknown event types return `null` and are dropped: events are notices, never state (14 §3.2).
VideoKitEvent? eventFromMsg(EventMsg msg) => switch (msg.type) {
  'PLAYBACK_ENDED' => const PlaybackEnded(),
  'SOURCE_RELEASED' =>
    msg.mediaToken == null ? null : SourceReleased(msg.mediaToken!),
  'HOST_ACTION_FAILED' =>
    msg.actionId == null || msg.error == null
        ? null
        : HostActionFailed(msg.actionId!, errorFromMsg(msg.error!)),
  'TRANSIENT_NOTICE' =>
    msg.noticeCode == null ? null : TransientNotice(msg.noticeCode!),
  'ERROR_RAISED' =>
    msg.error == null ? null : ErrorRaised(errorFromMsg(msg.error!)),
  _ => null,
};

VideoKitPlaybackEvent? playbackEventFromMsg(PlaybackEventMsg msg) {
  final id = msg.sessionId;
  return switch (msg.type) {
    'POSITION_TICK' =>
      msg.positionUs == null ? null : PositionTick(id, msg.positionUs!),
    'PLAY_STATE_CHANGED' =>
      msg.phase == null
          ? null
          : PlayStateChanged(
              id,
              sessionPhaseFromMsg(msg.phase!),
              msg.playWhenReady ?? false,
            ),
    'BUFFERING_STARTED' => BufferingStarted(id, msg.positionUs ?? 0),
    'BUFFERING_ENDED' => BufferingEnded(id, msg.durationUs ?? 0),
    'USER_SEEK' =>
      msg.fromUs == null || msg.toUs == null
          ? null
          : UserSeek(id, msg.fromUs!, msg.toUs!),
    'VISIBILITY_CHANGED' => VisibilityChanged(
      id,
      enumOf(
        SessionVisibility.values,
        msg.visibility,
        SessionVisibility.visible,
      ),
    ),
    'FOREGROUND_CHANGED' =>
      msg.foreground == null ? null : ForegroundChanged(id, msg.foreground!),
    'WATCH_TIME_ACCUMULATED' =>
      msg.deltaUs == null ? null : WatchTimeAccumulated(id, msg.deltaUs!),
    'SESSION_ENDED' => SessionEnded(id),
    _ => null,
  };
}

/// Native source reference of [ref] (04A I15, 14 §8.3), or `null` when M0 cannot send it (Dart readAt).
String? sourceRefToWire(VideoKitSourceRef ref) => switch (ref) {
  UriSourceRef(:final uri) => 'uri:$uri',
  RegisteredSourceRef(:final id) => 'registered:$id',
  DemoSourceRef(:final scenarioId) => 'demo:$scenarioId',
  DartSourceRef() => null,
};

MediaSourceMsg? mediaSourceToMsg(VideoKitMediaSource s) {
  final ref = sourceRefToWire(s.sourceRef);
  if (ref == null) return null;
  return MediaSourceMsg(
    mediaToken: s.mediaToken,
    mediaKind: mediaKindToMsg(s.mediaKind),
    displayName: s.displayName,
    knownLength: s.knownLength,
    mimeType: s.mimeType,
    extension: s.extension,
    randomAccess: s.seekability == Seekability.randomAccess,
    sourceRef: ref,
    // 04A P6: wire name LOCAL / SLOW.
    latencyHint: s.latencyHint.wireName,
  );
}

SessionConfigMsg sessionConfigToMsg(VideoKitSessionConfig c) =>
    SessionConfigMsg(
      purpose: 'SINGLE',
      priority: wireOf(c.priority),
      initialVisibility: wireOf(c.initialVisibility),
      // 04A A1: sessions start silent; the host grants audio with SetActiveAudio(true, epoch).
      initialActiveAudio: false,
      debugTag: c.debugLabel,
    );

// ------------------------------------------------------------------ host callbacks

HostActionRequest hostActionRequestFromMsg(HostActionRequestMsg msg) =>
    HostActionRequest(
      actionId: msg.actionId,
      sessionId: msg.sessionId,
      mediaToken: msg.mediaToken,
    );

HostActionResultMsg hostActionResultToMsg(HostActionResult r) =>
    HostActionResultMsg(
      status: wireOf(r.status),
      updatedAction: r.updatedAction == null
          ? null
          : hostActionToMsg(r.updatedAction!),
      messageKey: r.messageKey,
    );

NavigationRequest navigationRequestFromMsg(NavigationRequestMsg msg) =>
    NavigationRequest(
      sessionId: msg.sessionId,
      mediaToken: msg.mediaToken,
      direction: enumOf(
        NavigationDirection.values,
        msg.direction,
        NavigationDirection.next,
      ),
    );

// ------------------------------------------------------------------ capabilities

CapabilityRequestMsg capabilityRequestToMsg(CapabilityRequest r) =>
    CapabilityRequestMsg(
      source: r.source == null ? null : mediaSourceToMsg(r.source!),
    );

TrackingModuleStatus _moduleState(String wire) =>
    enumOf(TrackingModuleStatus.values, wire, TrackingModuleStatus.unsupported);

/// `HandshakeRequest.features` (REQ-API-10): the configured switches by wire
/// name; [VideoKitFeature.unknown] is never sent.
Map<String, String> featureModesToMsg(VideoKitFeatureConfig config) => {
  for (final entry in config.modes.entries)
    if (entry.key != VideoKitFeature.unknown)
      entry.key.wireName: entry.value.wireName,
};

/// The Dart host's gate answer for the native runtime (REQ-API-10).
FeatureAccessMsg featureAccessToMsg(FeatureAccess access) => FeatureAccessMsg(
  access: access.isAllowed ? 'ALLOWED' : 'DENIED',
  badge: access.badge?.wireName,
);

/// `CapabilitiesMsg.hiddenFeatures` (REQ-API-10); unknown names are dropped.
Set<VideoKitFeature> hiddenFeaturesFromMsg(List<String>? names) => {
  for (final name in names ?? const <String>[])
    if (VideoKitFeature.fromName(name) != VideoKitFeature.unknown)
      VideoKitFeature.fromName(name),
};

/// The wire carries the probe error; the Dart model keeps an [UnsupportedReason] (alignment item for 04A).
UnsupportedReason? _probeReason(MediaProbeMsg probe) {
  final error = probe.error;
  if (error == null) {
    return probe.playable == 'UNSUPPORTED' ? UnsupportedReason.unknown : null;
  }
  return switch (error.code) {
    'UNSUPPORTED_CONTAINER' ||
    'UNSUPPORTED_VIDEO_CODEC' ||
    'UNSUPPORTED_AUDIO_CODEC' => UnsupportedReason.format,
    'DECODER_UNAVAILABLE' ||
    'DECODER_RESOURCE_EXHAUSTED' => UnsupportedReason.deviceCapability,
    _ => UnsupportedReason.unknown,
  };
}

/// Protocol 1 carries the capability summary; codec and format lists stay empty on the Dart side.
VideoKitCapabilities capabilitiesFromMsg(CapabilitiesMsg msg) =>
    VideoKitCapabilities(
      schemaVersion: msg.schemaVersion,
      suggestedHardwareVideoSessions: msg.suggestedHardwareVideoSessions,
      maxSuggestedResolution: VideoSize(msg.maxWidth, msg.maxHeight),
      maxSuggestedFrameRate: msg.maxFrameRate,
      playbackFeatures: PlaybackFeatures(
        subtitles: msg.subtitles != 'UNSUPPORTED',
        multipleAudioTracks: msg.audioTrackSelection,
        speedControl: msg.speeds.length > 1,
        exactSeek: msg.exactSeek,
        speeds: msg.speeds,
      ),
      imageFeatures: ImageFeatures(
        staticImages: msg.staticImages,
        animatedImages: msg.animatedImages,
        largeImageTiling: msg.largeImageTiling,
      ),
      editFeatures: EditFeatures(
        singleVideoClips: msg.singleVideoClips,
        multiInputConcat: msg.multiInputConcat,
        masks: msg.manualMasks,
      ),
      tracking: TrackingStatus(
        face: _moduleState(msg.faceTracking),
        objectTracking: _moduleState(msg.objectTracking),
      ),
      unavailableReasons: {
        for (final entry in msg.unavailableReasons.entries)
          enumOf(FeatureKey.values, entry.key, FeatureKey.unknown): enumOf(
            UnsupportedReason.values,
            entry.value,
            UnsupportedReason.unknown,
          ),
      },
      mediaProbe: msg.mediaProbe == null
          ? null
          : MediaProbeResult(
              playable: msg.mediaProbe!.playable != 'UNSUPPORTED',
              fastConcatEligible: msg.mediaProbe!.fastConcatEligible ?? false,
              reason: _probeReason(msg.mediaProbe!),
            ),
      isDemo: msg.isDemo,
    );

// ------------------------------------------------------------------ edit projects

EditProjectConfigMsg editConfigToMsg(EditProjectConfig c) =>
    EditProjectConfigMsg(
      allowedPresets: List<String>.of(c.allowedPresetIds),
      trackingAllowed: true,
      initialPositionUs: null,
    );

MaskRegionMsg regionToMsg(MaskRegion r) => MaskRegionMsg(
  x: r.x,
  y: r.y,
  width: r.width,
  height: r.height,
  rotationDeg: r.rotationDeg,
);

MaskRegion regionFromMsg(MaskRegionMsg m) => MaskRegion(
  x: m.x,
  y: m.y,
  width: m.width,
  height: m.height,
  rotationDeg: m.rotationDeg,
);

EditCommandMsg editCommandToMsg(VideoKitEditCommand c) => switch (c) {
  AddClip() => EditCommandMsg(
    kind: 'AddClip',
    sourceId: c.sourceId,
    inUs: c.inUs,
    outUs: c.outUs,
    index: c.index,
  ),
  SplitAt() => EditCommandMsg(kind: 'SplitAt', clipId: c.clipId, atUs: c.atUs),
  TrimClip() => EditCommandMsg(
    kind: 'TrimClip',
    clipId: c.clipId,
    inUs: c.inUs,
    outUs: c.outUs,
  ),
  RemoveClip() => EditCommandMsg(kind: 'RemoveClip', clipId: c.clipId),
  MoveClip() => EditCommandMsg(
    kind: 'MoveClip',
    clipId: c.clipId,
    toIndex: c.toIndex,
  ),
  AddMask() => EditCommandMsg(
    kind: 'AddMask',
    maskType: wireOf(c.type),
    region: regionToMsg(c.region),
    startUs: c.startUs,
    endUs: c.endUs,
    style: wireOf(c.style),
    strength: c.strength,
  ),
  UpdateMaskKeyframe() => EditCommandMsg(
    kind: 'UpdateMaskKeyframe',
    maskId: c.maskId,
    atUs: c.atUs,
    region: regionToMsg(c.region),
  ),
  RemoveMaskKeyframe() => EditCommandMsg(
    kind: 'RemoveMaskKeyframe',
    maskId: c.maskId,
    atUs: c.atUs,
  ),
  SetMaskStyle() => EditCommandMsg(
    kind: 'SetMaskStyle',
    maskId: c.maskId,
    style: wireOf(c.style),
    strength: c.strength,
  ),
  SetMaskEnabled() => EditCommandMsg(
    kind: 'SetMaskEnabled',
    maskId: c.maskId,
    enabled: c.enabled,
  ),
  RemoveMask() => EditCommandMsg(kind: 'RemoveMask', maskId: c.maskId),
  // 04A E6 (M4-B2): the native side answers Unsupported until VK-M5A.
  SetMaskAvatar() => EditCommandMsg(
    kind: 'SetMaskAvatar',
    maskId: c.maskId,
    avatar: maskAvatarToMsg(c.avatar),
  ),
  // The Kotlin command only carries the mask id; kind/seed come from the mask (04A I11 alignment item).
  StartTracking() => EditCommandMsg(
    kind: 'StartTracking',
    maskId: c.maskId,
    trackingKind: wireOf(c.kind),
    region: c.seedRegion == null ? null : regionToMsg(c.seedRegion!),
    targetId: c.targetId,
  ),
  CorrectTracking() => EditCommandMsg(
    kind: 'CorrectTracking',
    maskId: c.maskId,
    atUs: c.atUs,
    region: regionToMsg(c.region),
  ),
  CancelTracking() => EditCommandMsg(kind: 'CancelTracking', maskId: c.maskId),
  AcceptTrackingRange() => EditCommandMsg(
    kind: 'AcceptTrackingRange',
    maskId: c.maskId,
    startUs: c.startUs,
    endUs: c.endUs,
  ),
};

EditCommandResult editResultFromMsg(EditResultMsg msg) => switch (msg.kind) {
  EditResultKind.applied => EditApplied(
    msg.revision ?? 0,
    createdId: msg.createdId,
  ),
  EditResultKind.rejected => EditRejected(
    msg.error == null ? channelError('MissingError') : errorFromMsg(msg.error!),
  ),
  EditResultKind.unsupported => EditUnsupported(
    enumOf(
      UnsupportedReason.values,
      msg.unsupportedReason,
      UnsupportedReason.unknown,
    ),
  ),
  EditResultKind.projectReleased => const EditProjectReleased(),
};

TrackingState _trackingState(String? wire) => switch (wire) {
  'TRACKED' => TrackingState.tracked,
  'LOW_CONFIDENCE' => TrackingState.lowConfidence,
  'AMBIGUOUS' => TrackingState.ambiguous,
  'LOST' => TrackingState.lost,
  _ => TrackingState.notAnalyzed,
};

ExportStage exportStageFromWire(String? wire) =>
    enumOf(ExportStage.values, wire, ExportStage.preparing);

VideoKitEditState editStateFromMsg(EditStateMsg msg) {
  final masks = msg.masks
      .map(
        (m) => MaskTrack(
          maskId: m.maskId,
          type: enumOf(MaskType.values, m.type, MaskType.manual),
          startUs: m.range.startUs,
          endUs: m.range.endUs,
          style: m.avatar == null && m.style == 'IMAGE'
              ? MaskStyle.mosaic
              : enumOf(MaskStyle.values, m.style, MaskStyle.mosaic),
          strength: m.strength,
          enabled: m.enabled,
          keyframes: m.keyframes
              .map(
                (k) => MaskKeyframe(
                  atUs: k.atUs,
                  region: regionFromMsg(k.region),
                  source: enumOf(
                    KeyframeSource.values,
                    k.source,
                    KeyframeSource.user,
                  ),
                  state: k.quality == null ? null : _trackingState(k.quality),
                  rollDeg: k.rollDeg,
                ),
              )
              .toList(),
          // 04A E4: accepted ranges belong to the mask.
          acceptedRanges: m.acceptedRanges
              .map((r) => TimeRangeUs(r.startUs, r.endUs))
              .toList(),
          avatar: m.avatar == null ? null : maskAvatarFromMsg(m.avatar!),
        ),
      )
      .toList();
  final accepted = {for (final m in msg.masks) m.maskId: m.acceptedRanges};
  final maskTypes = {for (final m in masks) m.maskId: m.type};
  return VideoKitEditState(
    phase: EditPhase.values.byName(msg.phase.name),
    revision: msg.revision,
    timeline: Timeline(
      sources: msg.sources
          .map(
            (s) => EditSource(
              sourceId: s.sourceId,
              mediaToken: s.mediaToken,
              displayName: s.displayName,
              mismatch: s.mismatch,
              // 04A E4: not probed yet is null, and an unknown codec is null.
              probe: s.probe == null ? null : sourceProbeFromMsg(s.probe!),
            ),
          )
          .toList(),
      clips: msg.clips
          .map(
            (c) => EditClip(
              clipId: c.clipId,
              sourceId: c.sourceId,
              inUs: c.inUs,
              outUs: c.outUs,
            ),
          )
          .toList(),
    ),
    masks: masks,
    tracking: {
      for (final run in msg.tracking)
        run.maskId: TrackingRun(
          maskId: run.maskId,
          requestId: run.maskId,
          projectRevision: msg.revision,
          kind: maskTypes[run.maskId] == MaskType.object
              ? TrackingKind.object
              : TrackingKind.face,
          status: enumOf(
            TrackingRunStatus.values,
            run.status,
            TrackingRunStatus.failed,
          ),
          progress: run.progress,
          error: run.error == null ? null : errorFromMsg(run.error!),
          coverage: CoverageReport(
            segments: run.coverage
                .map(
                  (c) => CoverageRange(
                    startUs: c.range.startUs,
                    endUs: c.range.endUs,
                    state: _trackingState(c.quality),
                    accepted: (accepted[run.maskId] ?? const []).any(
                      (a) =>
                          c.range.startUs >= a.startUs &&
                          c.range.endUs <= a.endUs,
                    ),
                  ),
                )
                .toList(),
          ),
        ),
    },
    export: msg.exportProgress == null
        ? null
        : ExportProgress(
            exportId: msg.exportProgress!.exportId,
            stage: exportStageFromWire(msg.exportProgress!.stage),
            fraction: msg.exportProgress!.fraction,
            processedUs: msg.exportProgress!.processedUs,
            outputBytes: msg.exportProgress!.outputBytes,
            remainingUs: msg.exportProgress!.remainingEstimateUs,
            cancellable: msg.exportProgress!.cancellable,
          ),
    canUndo: msg.canUndo,
    canRedo: msg.canRedo,
    estimate: EditEstimate(
      durationUs: msg.estimateDurationUs,
      sizeBytes: msg.estimateSizeBytes,
    ),
    error: msg.error == null ? null : errorFromMsg(msg.error!),
  );
}

ExportRequestMsg exportRequestToMsg(
  VideoKitExportRequest r,
  VideoKitOutputSink sink,
  String fallbackId,
) => ExportRequestMsg(
  exportId: r.exportId ?? fallbackId,
  preset: r.presetId,
  fileNameHint: null,
  sinkRef: sink.sinkRef,
);

ExportPrecheck precheckFromMsg(PrecheckMsg msg) => ExportPrecheck(
  problems: msg.problems.map(errorFromMsg).toList(),
  warnings: List<String>.of(msg.warnings),
  writeMode: msg.writeMode == null
      ? null
      : enumOf(SinkWriteMode.values, msg.writeMode, SinkWriteMode.sequential),
  estimate: EditEstimate(
    durationUs: msg.estimateDurationUs,
    sizeBytes: msg.estimateSizeBytes,
  ),
  // 04A T2: Kotlin CoverageRange + maskId → Dart UncoveredRange.
  uncoveredRanges: [
    for (final r in msg.uncoveredRanges)
      UncoveredRange(
        maskId: r.maskId ?? '',
        startUs: r.range.startUs,
        endUs: r.range.endUs,
        state: _trackingState(r.quality),
      ),
  ],
);

MediaOrientation _orientation(int width, int height, int rotationDeg) {
  final swap = rotationDeg % 180 != 0;
  final w = swap ? height : width;
  final h = swap ? width : height;
  if (w <= 0 || h <= 0) return MediaOrientation.unknown;
  if (w == h) return MediaOrientation.square;
  return w > h ? MediaOrientation.landscape : MediaOrientation.portrait;
}

VideoKitExportResult exportResultFromMsg(ExportResultMsg msg) =>
    switch (msg.kind) {
      ExportResultKind.succeeded when msg.media != null => ExportSucceeded(
        msg.exportId,
        VideoKitExportedMedia(
          outputToken: msg.media!.outputToken,
          container: msg.media!.container,
          extension: msg.media!.extension,
          videoCodec: msg.media!.videoCodec,
          audioCodec: msg.media!.audioCodec,
          width: msg.media!.width,
          height: msg.media!.height,
          orientation: _orientation(
            msg.media!.width,
            msg.media!.height,
            msg.media!.rotationDeg,
          ),
          durationUs: msg.media!.durationUs,
          sizeBytes: msg.media!.sizeBytes,
          frameRate: msg.media!.frameRate,
          audioPresent: msg.media!.audioPresent,
          createdAt: DateTime.fromMillisecondsSinceEpoch(
            msg.media!.createdAtEpochMs,
            isUtc: true,
          ),
          sourceTokens: msg.media!.sourceTokens,
          editProjectId: msg.media!.editProjectId,
          exportPresetId: msg.media!.exportPreset,
          warnings: msg.media!.warnings,
          isDemo: msg.media!.isDemo,
        ),
      ),
      ExportResultKind.succeeded => ExportFailed(
        msg.exportId,
        channelError('MissingMedia'),
      ),
      ExportResultKind.failed => ExportFailed(
        msg.exportId,
        msg.error == null
            ? channelError('MissingError')
            : errorFromMsg(msg.error!),
        stage: msg.stage == null ? null : exportStageFromWire(msg.stage),
      ),
      ExportResultKind.cancelled => ExportCancelled(
        msg.exportId,
        partialOutputRemoved: msg.partialOutputRemoved ?? true,
      ),
    };

CandidateDetectionResult candidatesFromMsg(CandidateResultMsg msg) =>
    CandidateDetectionResult(
      candidates: msg.candidates
          .map(
            (c) => TrackingCandidate(
              candidateId: c.candidateId,
              kind: enumOf(TrackingKind.values, c.kind, TrackingKind.face),
              region: regionFromMsg(c.region),
              confidence: c.confidence,
            ),
          )
          .toList(),
      error: msg.error == null ? null : errorFromMsg(msg.error!),
    );

/// 04A P2.
MediaInfo mediaInfoFromMsg(MediaInfoMsg m) => MediaInfo(
  container: m.container,
  videoCodec: m.videoCodec,
  audioCodec: m.audioCodec,
  width: m.width,
  height: m.height,
  frameRate: m.frameRate,
  bitrateBps: m.bitrateBps,
  rotationDeg: m.rotationDeg,
  durationUs: m.durationUs,
  fileSizeBytes: m.fileSizeBytes,
);

/// 04A P1: a captured JPEG, or the stable error.
ThumbnailResult thumbnailFromMsg(ThumbnailResultMsg m) {
  final bytes = m.bytes;
  final width = m.width;
  final height = m.height;
  if (bytes != null && width != null && height != null) {
    return ThumbnailCaptured(
      bytes: bytes,
      width: width,
      height: height,
      mimeType: m.mimeType ?? 'image/jpeg',
    );
  }
  return ThumbnailFailed(
    m.error == null
        ? channelError('ThumbnailWithoutData')
        : errorFromMsg(m.error!),
  );
}

/// [SourceProbe] of [msg]; an unknown (null or empty) codec stays null (04A E4).
SourceProbe sourceProbeFromMsg(SourceProbeMsg msg) => SourceProbe(
  durationUs: msg.durationUs,
  width: msg.width,
  height: msg.height,
  rotationDeg: msg.rotationDeg,
  fps: msg.frameRate,
  videoCodec: (msg.videoCodec?.isEmpty ?? true) ? null : msg.videoCodec,
  audioCodec: (msg.audioCodec?.isEmpty ?? true) ? null : msg.audioCodec,
  hasAudio: msg.hasAudio,
);

/// [MaskAvatarMsg] of [avatar] (04A E6, M4-B2).
MaskAvatarMsg maskAvatarToMsg(MaskAvatar avatar) => MaskAvatarMsg(
  avatarToken: avatar.avatarToken,
  scale: avatar.scale,
  offsetX: avatar.offsetX,
  offsetY: avatar.offsetY,
  followRotation: avatar.followRotation,
);

/// [MaskAvatar] of [msg] (04A E6, M4-B2).
MaskAvatar maskAvatarFromMsg(MaskAvatarMsg msg) => MaskAvatar(
  avatarToken: msg.avatarToken,
  scale: msg.scale,
  offsetX: msg.offsetX,
  offsetY: msg.offsetY,
  followRotation: msg.followRotation,
);
