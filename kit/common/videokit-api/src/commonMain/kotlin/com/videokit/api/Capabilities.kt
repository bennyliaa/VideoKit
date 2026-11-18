package com.videokit.api

/** Support level of a format or feature (04 §9.2). */
public enum class SupportLevel {
    /** Fully supported. */
    SUPPORTED,

    /** Partly supported (for example ASS without advanced effects). */
    PARTIAL,

    /** Not supported. */
    UNSUPPORTED,
}

/** Feature keys used in [VideoKitCapabilities.unavailableReasons] and [CapabilityRequest]. */
public enum class FeatureKey {
    /** Video playback. */
    VIDEO_PLAYBACK,

    /** Static images. */
    IMAGE_STATIC,

    /** Animated images. */
    IMAGE_ANIMATED,

    /** Large image tiling. */
    IMAGE_LARGE_TILING,

    /** Subtitles. */
    SUBTITLES,

    /** Audio track selection. */
    AUDIO_TRACK_SELECTION,

    /** Speed change. */
    SPEED_CONTROL,

    /** Exact seek. */
    EXACT_SEEK,

    /** Multi-view. */
    MULTI_VIEW,

    /** Single video clip editing. */
    EDIT_CLIPS,

    /** Multi-input concatenation. */
    EDIT_CONCAT,

    /** Manual mosaic/blur masks. */
    MANUAL_MASK,

    /** Face tracking. */
    FACE_TRACKING,

    /** Object tracking. */
    OBJECT_TRACKING,

    /** Export. */
    EXPORT,

    /** A feature this version does not know (decoding fallback, 04A T3); never reported by this version. */
    UNKNOWN,
    ;

    public companion object {
        /** Maps a feature name to a [FeatureKey]; unknown or future names map to [UNKNOWN]. */
        public fun fromWireName(name: String?): FeatureKey = entries.firstOrNull { it.name == name } ?: UNKNOWN
    }
}

/** A decoder or encoder entry. */
public data class CodecInfo(
    /** Codec MIME type, for example `video/avc`. */
    val mimeType: String,
    /** Whether hardware accelerated. */
    val hardwareAccelerated: Boolean,
    /** Maximum supported size, if known. */
    val maxSize: Size? = null,
    /** Maximum concurrent instances declared by the device; a hint only (07 §2). */
    val maxInstances: Int? = null,
)

/** Decoder summary (04 §9.2). */
public data class DecoderSummary(
    /** Video decoders. */
    val video: List<CodecInfo> = emptyList(),
    /** Audio decoders. */
    val audio: List<CodecInfo> = emptyList(),
)

/** Container × codec support entry (04 §9.2). */
public data class FormatSupport(
    /** Container, for example `mp4`, `mkv`, `m2ts`. */
    val container: String,
    /** Video codec MIME type, if the entry is about video. */
    val videoCodec: String? = null,
    /** Audio codec MIME type, if the entry is about audio. */
    val audioCodec: String? = null,
    /** Support level. */
    val level: SupportLevel,
    /** Reason when not fully supported. */
    val reason: UnsupportedReason? = null,
)

/** Playback features (04 §9.2). */
public data class PlaybackFeatures(
    /** Subtitle rendering. */
    val subtitles: SupportLevel = SupportLevel.UNSUPPORTED,
    /** Audio track selection. */
    val audioTrackSelection: Boolean = false,
    /** Selectable speeds. */
    val speeds: List<Float> = listOf(1f),
    /** Exact seek. */
    val exactSeek: Boolean = false,
)

/** Image features (04 §9.2). */
public data class ImageFeatures(
    /** Static images. */
    val staticImages: Boolean = false,
    /** Animated images. */
    val animatedImages: Boolean = false,
    /** Large image tiling. */
    val largeImageTiling: Boolean = false,
)

/** Edit features (04 §9.2). */
public data class EditFeatures(
    /** Single video clip editing. */
    val singleVideoClips: Boolean = false,
    /** Multi-input concatenation. */
    val multiInputConcat: Boolean = false,
    /** Manual masks. */
    val manualMasks: Boolean = false,
)

/** Encoder entry (04 §9.2). */
public data class EncoderSupport(
    /** Codec MIME type. */
    val mimeType: String,
    /** Whether hardware accelerated. */
    val hardwareAccelerated: Boolean,
    /** Maximum size, if known. */
    val maxSize: Size? = null,
)

/** Output format (container + codecs) offered for export (08 §8). */
public data class OutputFormat(
    /** Container, for example `mp4`. */
    val container: String,
    /** Video codec MIME type. */
    val videoCodec: String,
    /** Audio codec MIME type, if any. */
    val audioCodec: String?,
    /** Presets available with this format. */
    val presets: List<ExportPreset>,
)

/** State of a tracking module. */
public enum class TrackingModuleStatus {
    /** Installed and usable. */
    AVAILABLE,

    /** Not installed in this build. */
    NOT_INSTALLED,

    /** Installed but not usable on this device. */
    UNSUPPORTED,

    /** Disabled by the host. */
    DISABLED,
}

/** Tracking status (04 §9.2). */
public data class TrackingStatus(
    /** Face tracking module. */
    val face: TrackingModuleStatus = TrackingModuleStatus.NOT_INSTALLED,
    /** Object tracking module. */
    val objectTracking: TrackingModuleStatus = TrackingModuleStatus.NOT_INSTALLED,
    /** Suggested analysis resolution, if measured. */
    val suggestedResolution: Size? = null,
    /** Suggested number of concurrently tracked targets. */
    val maxConcurrentTargets: Int = 0,
)

/** What the export pipeline needs from an output sink (08 §5). */
public data class SinkRequirements(
    /** Whether random write or a file descriptor is needed for the default container. */
    val randomWriteOrFileDescriptor: Boolean = true,
    /** Whether a sequential-only sink can be used via a fallback (fragmented MP4 or private staging). */
    val sequentialFallbackAvailable: Boolean = false,
)

/** Probe result for one media source, returned when [CapabilityRequest.source] is set (04 §9.2). */
public data class MediaProbeResult(
    /** Media token of the probed source. */
    val mediaToken: String,
    /** Whether the media can be played/displayed. */
    val playable: SupportLevel,
    /** Whether the media can be decoded for editing/encoding; reported separately (original requirement §5.2). */
    val editable: SupportLevel,
    /** Whether the media qualifies for fast (no re-encode) concatenation; `null` when unknown. */
    val fastConcatEligible: Boolean? = null,
    /** Duration, if probed. */
    val durationUs: Long? = null,
    /** Content size after rotation, if probed. */
    val size: Size? = null,
    /** Error when the probe failed. */
    val error: VideoKitStableError? = null,
)

/** Capability report request (04 §9.2). */
public data class CapabilityRequest(
    /** Optional media source to probe. */
    val source: VideoKitMediaSource? = null,
)

/**
 * Capability report (04 §9.2, original requirement §19.4). "Playable" does not imply "encodable" or
 * "concatenable without re-encoding"; they are reported separately.
 */
public data class VideoKitCapabilities(
    /** Report schema version; see [CURRENT_SCHEMA_VERSION]. */
    val schemaVersion: Int = CURRENT_SCHEMA_VERSION,
    /** Decoder summary. */
    val decoders: DecoderSummary = DecoderSummary(),
    /** Container × codec support. */
    val containerCodecSupport: List<FormatSupport> = emptyList(),
    /** Suggested number of concurrent hardware video sessions. */
    val suggestedHardwareVideoSessions: Int = 0,
    /** Maximum suggested resolution. */
    val maxSuggestedResolution: Size = Size(0, 0),
    /** Maximum suggested frame rate. */
    val maxSuggestedFrameRate: Int = 0,
    /** Playback features. */
    val playbackFeatures: PlaybackFeatures = PlaybackFeatures(),
    /** Image features. */
    val imageFeatures: ImageFeatures = ImageFeatures(),
    /** Edit features. */
    val editFeatures: EditFeatures = EditFeatures(),
    /** Encoders. */
    val encoders: List<EncoderSupport> = emptyList(),
    /** Output formats. */
    val outputFormats: List<OutputFormat> = emptyList(),
    /** Tracking status. */
    val tracking: TrackingStatus = TrackingStatus(),
    /** Sink requirements. */
    val sinkRequirements: SinkRequirements = SinkRequirements(),
    /** Reasons of unavailable features. */
    val unavailableReasons: Map<FeatureKey, UnsupportedReason> = emptyMap(),
    /** Probe result when the request named a source. */
    val mediaProbe: MediaProbeResult? = null,
    /** Whether the report comes from a demo/fake backend (04A I6); demo capabilities are not device facts. */
    val isDemo: Boolean = false,
    /**
     * Features hidden by [VideoKitConfig.features], parents included (REQ-API-10 ①). Their [VideoKitFeature.capabilityKeys]
     * are reported unavailable with [UnsupportedReason.FEATURE_DISABLED]. The dynamic gate is not reflected here.
     */
    val hiddenFeatures: Set<VideoKitFeature> = emptySet(),
) {
    public companion object {
        /** Schema version written by this API version. */
        public const val CURRENT_SCHEMA_VERSION: Int = 1
    }
}
