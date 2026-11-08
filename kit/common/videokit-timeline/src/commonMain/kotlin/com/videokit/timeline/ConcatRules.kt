package com.videokit.timeline

import com.videokit.api.Clip
import com.videokit.api.EditSource
import com.videokit.api.ExportPreset
import com.videokit.api.ExportWarnings
import com.videokit.api.SourceProbe
import kotlin.math.abs
import kotlin.math.max

/** How the clips are joined (08 §3.1, 04A E1). */
public enum class ConcatPath {
    /** Remux without re-encoding. */
    FAST,

    /** Decode and re-encode to the export preset. */
    TRANSCODE,
}

/**
 * Why the fast path was not chosen (04A E1 `concatReasons`), upper snake case like the other registered codes.
 * Listed in this order; a decision lists each reason once.
 */
public enum class ConcatReason {
    /** The timeline has no clips. */
    EMPTY_TIMELINE,

    /** A clip names a source that is not in the project or has no probe data. */
    SOURCE_UNKNOWN,

    /** A probe lacks a value the comparison needs (video codec, size, frame rate, or the audio codec of a source with audio). */
    PROBE_INCOMPLETE,

    /** The sources use different video codecs. */
    VIDEO_CODEC_DIFFERS,

    /** The sources have different coded sizes. */
    RESOLUTION_DIFFERS,

    /** The sources have different frame rates. */
    FRAME_RATE_DIFFERS,

    /** The sources have different rotation metadata (08 §3.1: fast only when the rotation is the same). */
    ROTATION_DIFFERS,

    /** The sources use different audio codecs. */
    AUDIO_CODEC_DIFFERS,

    /** Some sources have audio and some do not: silence must be encoded (08 §3.1). */
    AUDIO_PRESENCE_DIFFERS,

    /** The source codecs are not the preset's output format (MP4 / H.264 / AAC, 08 §8). */
    OUTPUT_FORMAT_DIFFERS,

    /** The preset changes the resolution (long edge above the preset's). */
    OUTPUT_RESIZE,

    /** Enabled masks must be rendered into the pixels (08 §4). */
    MASKS_ENABLED,

    /** The key frame positions of a source with a cut are unknown. */
    KEYFRAMES_UNKNOWN,

    /** Precise cuts were requested and a clip does not start on a key frame (08 §3). */
    CUT_NOT_ON_KEYFRAME,
}

/** Input of [ConcatRules.decide]. */
public data class ConcatRequest(
    /** Ordered clips. */
    val clips: List<Clip>,
    /** Project sources with probe data. */
    val sources: List<EditSource>,
    /**
     * Key frame times (source time, microseconds) per source id, as far as known. A source without an entry has
     * unknown key frames; a cut inside it (clip in point > 0) then forces [ConcatPath.TRANSCODE].
     */
    val keyframesUs: Map<String, List<Long>> = emptyMap(),
    /** Export preset. */
    val preset: ExportPreset = ExportPreset.ORIGINAL,
    /** Whether any enabled mask is on the timeline. */
    val masksEnabled: Boolean = false,
    /** Whether the user requires exact cut points; otherwise fast cuts snap to the previous key frame. */
    val preciseCuts: Boolean = false,
)

/** Result of [ConcatRules.decide]. */
public data class ConcatDecision(
    /** Chosen path. */
    val path: ConcatPath,
    /** Why [ConcatPath.FAST] was not chosen; empty for FAST. */
    val reasons: List<ConcatReason>,
    /**
     * The clips as they will be cut: for FAST, in points moved back to the previous key frame where needed (the UI
     * shows the difference, 08 §3); for TRANSCODE, the clips unchanged.
     */
    val effectiveClips: List<Clip>,
    /** Export warnings, for example [ExportWarnings.BOUNDARY_ALIGNED_TO_KEYFRAME] when a FAST cut moved. */
    val warnings: List<String> = emptyList(),
)

/**
 * The pure part of the concat path decision (08 §3.1, M4-B1): compares the probe data of the clips' sources, the
 * preset, the masks and the key frames. Not connected to an engine yet; the engine batch after S3 feeds it real key
 * frame tables and reports the result in `ExportPrecheck` (04A E1).
 *
 * FAST requires: every clip's source known and probed; identical video codec, coded size, frame rate (within
 * [FRAME_RATE_TOLERANCE]) and rotation; either no source with audio or all with the same audio codec; H.264 video
 * and AAC audio (the preset container is MP4); no resize by the preset; no enabled mask; and for every clip starting
 * after the source start, known key frames. Clips of a single source trivially share the source parameters.
 *
 * Not compared because [SourceProbe] does not carry them yet: container, codec profile/level, audio sample rate and
 * channel count. The engine batch must add them before FAST is offered (open point in reports\M4-B1).
 */
public object ConcatRules {
    /** Frame rates closer than this (frames per second) count as equal. */
    public const val FRAME_RATE_TOLERANCE: Float = 0.01f

    /** Video codec of the MP4 presets (08 §8). */
    public const val OUTPUT_VIDEO_CODEC: String = "video/avc"

    /** Audio codec of the MP4 presets (08 §8). */
    public const val OUTPUT_AUDIO_CODEC: String = "audio/mp4a-latm"

    /** Decides the path for [request]. */
    public fun decide(request: ConcatRequest): ConcatDecision {
        val reasons = mutableSetOf<ConcatReason>()
        val clips = request.clips
        if (clips.isEmpty()) return transcode(request, setOf(ConcatReason.EMPTY_TIMELINE))
        val bySource = request.sources.associateBy { it.sourceId }
        val probes = clips.map { clip -> bySource[clip.sourceId]?.probe }
        if (probes.any { it == null }) reasons += ConcatReason.SOURCE_UNKNOWN
        val distinct = clips.map { it.sourceId }.toSet().mapNotNull { bySource[it]?.probe }

        probes.filterNotNull().forEach { probe ->
            val incomplete = probe.videoCodec == null || probe.width <= 0 || probe.height <= 0 || probe.frameRate == null
            if (incomplete) reasons += ConcatReason.PROBE_INCOMPLETE
            if (probe.hasAudio && probe.audioCodec == null) reasons += ConcatReason.PROBE_INCOMPLETE
        }
        if (distinct.size > 1) compareSources(distinct, reasons)
        outputFormat(distinct, request.preset, reasons)
        if (request.masksEnabled) reasons += ConcatReason.MASKS_ENABLED

        // Cuts: a clip that starts inside its source must start on a key frame, or snap to one.
        val warnings = ArrayList<String>()
        val effective = clips.map { clip ->
            if (clip.inUs == 0L) return@map clip
            val keyframes = request.keyframesUs[clip.sourceId]
            if (keyframes == null) {
                reasons += ConcatReason.KEYFRAMES_UNKNOWN
                return@map clip
            }
            val previous = keyframes.filter { it <= clip.inUs }.maxOrNull() ?: 0L
            when {
                previous == clip.inUs -> clip

                request.preciseCuts -> {
                    reasons += ConcatReason.CUT_NOT_ON_KEYFRAME
                    clip
                }

                else -> clip.copy(inUs = previous)
            }
        }
        if (reasons.isNotEmpty()) return transcode(request, reasons)
        if (effective != clips) warnings += ExportWarnings.BOUNDARY_ALIGNED_TO_KEYFRAME
        return ConcatDecision(ConcatPath.FAST, emptyList(), effective, warnings)
    }

    private fun compareSources(probes: List<SourceProbe>, reasons: MutableSet<ConcatReason>) {
        val first = probes.first()
        probes.drop(1).forEach { probe ->
            if (probe.videoCodec != null && first.videoCodec != null && !sameCodec(probe.videoCodec, first.videoCodec)) {
                reasons += ConcatReason.VIDEO_CODEC_DIFFERS
            }
            if (probe.width != first.width || probe.height != first.height) reasons += ConcatReason.RESOLUTION_DIFFERS
            val rate = probe.frameRate
            val firstRate = first.frameRate
            if (rate != null && firstRate != null && abs(rate - firstRate) > FRAME_RATE_TOLERANCE) {
                reasons += ConcatReason.FRAME_RATE_DIFFERS
            }
            if (normalized(probe.rotationDeg) != normalized(first.rotationDeg)) reasons += ConcatReason.ROTATION_DIFFERS
        }
        val withAudio = probes.filter { it.hasAudio }
        if (withAudio.isNotEmpty() && withAudio.size != probes.size) reasons += ConcatReason.AUDIO_PRESENCE_DIFFERS
        if (withAudio.mapNotNull { it.audioCodec?.lowercase() }.toSet().size > 1) reasons += ConcatReason.AUDIO_CODEC_DIFFERS
    }

    private fun outputFormat(probes: List<SourceProbe>, preset: ExportPreset, reasons: MutableSet<ConcatReason>) {
        probes.forEach { probe ->
            val video = probe.videoCodec
            if (video != null && !sameCodec(video, OUTPUT_VIDEO_CODEC)) reasons += ConcatReason.OUTPUT_FORMAT_DIFFERS
            val audio = probe.audioCodec
            if (probe.hasAudio && audio != null && !sameCodec(audio, OUTPUT_AUDIO_CODEC)) reasons += ConcatReason.OUTPUT_FORMAT_DIFFERS
            val limit = longEdgeLimit(preset)
            if (limit != null && max(probe.width, probe.height) > limit) reasons += ConcatReason.OUTPUT_RESIZE
        }
    }

    /** Long edge of [preset]; `null` keeps the source size (ORIGINAL). Smaller sources are not upscaled. */
    public fun longEdgeLimit(preset: ExportPreset): Int? = when (preset) {
        ExportPreset.ORIGINAL -> null
        ExportPreset.P1080 -> 1920
        ExportPreset.P720 -> 1280
    }

    private fun transcode(request: ConcatRequest, reasons: Set<ConcatReason>): ConcatDecision =
        ConcatDecision(ConcatPath.TRANSCODE, reasons.sorted(), request.clips)

    private fun sameCodec(a: String?, b: String?): Boolean = a != null && b != null && a.equals(b, ignoreCase = true)

    private fun normalized(rotationDeg: Int): Int = ((rotationDeg % 360) + 360) % 360
}
