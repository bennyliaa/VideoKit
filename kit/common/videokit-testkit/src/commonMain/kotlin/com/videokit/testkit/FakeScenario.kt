package com.videokit.testkit

import com.videokit.api.ErrorCode
import com.videokit.api.ExportStage
import com.videokit.api.Size
import com.videokit.api.TimeRangeUs
import com.videokit.api.TrackInfo
import com.videokit.api.VideoKitMediaSource

/** Buffering episode of a scenario: at media time [atUs] the session buffers for [forUs] clock time. */
public data class BufferingSpec(
    /** Media position that triggers buffering. */
    val atUs: Long,
    /** Buffering duration in clock microseconds. */
    val forUs: Long,
)

/** Export failure injected by a scenario. */
public data class ExportFailureSpec(
    /** Stage in which the export fails. */
    val stage: ExportStage,
    /** Stable error code reported. */
    val code: ErrorCode,
)

/**
 * Declarative script of Fake behaviour (14 §11.1), composable by chaining:
 * `FakeScenario.normal().slowLoad(3_000).buffering(atUs = 20_000_000, forUs = 2_000_000)`.
 *
 * Demo data never pretends to be real playback, tracking or export: every Fake session reports
 * `isDemo = true` and exports carry the warning [DEMO_OUTPUT_WARNING].
 */
public data class FakeScenario(
    /** Scenario name (for diagnostics and `demo:<name>` media tokens). */
    val name: String = "normal",
    /** Video duration; animated images use [animationLoopUs]. */
    val durationUs: Long = 120_000_000L,
    /** Animated image loop length. */
    val animationLoopUs: Long = 2_000_000L,
    /** Content size. */
    val videoSize: Size = Size(1920, 1080),
    /** Audio tracks. */
    val audioTracks: List<TrackInfo> = DEFAULT_AUDIO_TRACKS,
    /** Subtitle tracks. */
    val subtitleTracks: List<TrackInfo> = DEFAULT_SUBTITLE_TRACKS,
    /** Bind latency (coroutine time). */
    val loadDelayMs: Long = 200L,
    /** Seek latency (coroutine time); rapid seeks within it are superseded. */
    val seekDelayMs: Long = 50L,
    /** Buffering episode, if any. */
    val buffering: BufferingSpec? = null,
    /** Bind fails with UNSUPPORTED_VIDEO_CODEC. */
    val unsupportedVideoCodec: Boolean = false,
    /** Bind fails with UNSUPPORTED_CONTAINER. */
    val unsupportedContainer: Boolean = false,
    /** Audio cannot be decoded: video plays silently with a notice. */
    val unsupportedAudioCodec: Boolean = false,
    /** Fatal CORRUPT_MEDIA at this media position. */
    val corruptAtUs: Long? = null,
    /** Recoverable SOURCE_DISCONNECTED at this media position. */
    val disconnectAtUs: Long? = null,
    /** Bind fails with DECODER_RESOURCE_EXHAUSTED. */
    val resourceExhausted: Boolean = false,
    /** Host actions whose request simulates a host that never answers. */
    val hostActionTimeoutIds: Set<String> = emptySet(),
    /** Tracking reports these ranges as LOST. */
    val trackingLostRanges: List<TimeRangeUs> = emptyList(),
    /** Delay of each tracking step (10 steps per run). */
    val trackingStepMs: Long = 100L,
    /** Export failure, if any. */
    val exportFailure: ExportFailureSpec? = null,
    /** Delay of each export stage. */
    val exportStageDelayMs: Long = 200L,
    /** Extra delay before a cancellation is confirmed. */
    val exportCancelDelayMs: Long = 0L,
) {
    /** Bind takes [ms] milliseconds. */
    public fun slowLoad(ms: Long = 3_000L): FakeScenario = copy(name = "$name+slowLoad", loadDelayMs = ms)

    /** Buffers for [forUs] at media position [atUs]. */
    public fun buffering(atUs: Long = 20_000_000L, forUs: Long = 2_000_000L): FakeScenario =
        copy(name = "$name+buffering", buffering = BufferingSpec(atUs, forUs))

    /** The video codec is unsupported. */
    public fun unsupportedVideoCodec(): FakeScenario = copy(name = "$name+unsupportedVideoCodec", unsupportedVideoCodec = true)

    /** The container is unsupported. */
    public fun unsupportedContainer(): FakeScenario = copy(name = "$name+unsupportedContainer", unsupportedContainer = true)

    /** The audio codec is unsupported. */
    public fun unsupportedAudioCodec(): FakeScenario = copy(name = "$name+unsupportedAudioCodec", unsupportedAudioCodec = true)

    /** The media is corrupt at [atUs]. */
    public fun corrupt(atUs: Long = 45_000_000L): FakeScenario = copy(name = "$name+corrupt", corruptAtUs = atUs)

    /** The source disconnects at [atUs]. */
    public fun disconnect(atUs: Long = 30_000_000L): FakeScenario = copy(name = "$name+disconnect", disconnectAtUs = atUs)

    /** Decoder resources are exhausted. */
    public fun resourceExhausted(): FakeScenario = copy(name = "$name+resourceExhausted", resourceExhausted = true)

    /** Requests of [actionId] time out. */
    public fun hostActionTimeout(actionId: String): FakeScenario =
        copy(name = "$name+hostActionTimeout", hostActionTimeoutIds = hostActionTimeoutIds + actionId)

    /** Tracking loses the target in [ranges]. */
    public fun trackingLost(ranges: List<TimeRangeUs>): FakeScenario = copy(name = "$name+trackingLost", trackingLostRanges = ranges)

    /** The export fails at [stage] with [code]. */
    public fun exportFails(stage: ExportStage = ExportStage.ENCODING, code: ErrorCode = ErrorCode.OUTPUT_SPACE_INSUFFICIENT): FakeScenario =
        copy(name = "$name+exportFails", exportFailure = ExportFailureSpec(stage, code))

    /** Cancelling the export takes [ms] milliseconds. */
    public fun exportCancelSlow(ms: Long = 3_000L): FakeScenario = copy(name = "$name+exportCancelSlow", exportCancelDelayMs = ms)

    public companion object {
        /** Warning attached to every Fake export result. */
        public const val DEMO_OUTPUT_WARNING: String = "DEMO_OUTPUT_NOT_REAL_MEDIA"

        /** Prefix of media tokens that select a named scenario, for example `demo:buffering`. */
        public const val DEMO_TOKEN_PREFIX: String = "demo:"

        /** Default audio tracks. No labels: the Kit outputs no display text; the UI names tracks from the language code (13 §3.1). */
        public val DEFAULT_AUDIO_TRACKS: List<TrackInfo> = listOf(
            TrackInfo(id = "a1", language = "zh", codec = "audio/mp4a-latm"),
            TrackInfo(id = "a2", language = "en", codec = "audio/ac3"),
        )

        /** Default subtitle tracks. */
        public val DEFAULT_SUBTITLE_TRACKS: List<TrackInfo> = listOf(
            TrackInfo(id = "s1", language = "zh", codec = "application/x-subrip"),
            TrackInfo(id = "s2", language = "en", codec = "text/x-ssa"),
        )

        /** Normal playback. */
        public fun normal(): FakeScenario = FakeScenario()

        /** Scenario ids, identical to the Dart Fake catalogue (`Scenarios.catalog`, 04A B9). */
        public val NAMES: List<String> = listOf(
            "normal", "slowLoad", "buffering", "unsupported", "unsupportedContainer", "unsupportedAudio", "corrupt",
            "disconnect", "resourceExhausted", "hostActionTimeout", "trackingLost", "exportFails", "exportCancelSlow",
        )

        /** Scenario for an id in [NAMES] (older Kotlin names are accepted as aliases); `null` for unknown ids. */
        public fun named(name: String): FakeScenario? = when (name) {
            "normal" -> normal()
            "slowLoad" -> normal().slowLoad()
            "buffering" -> normal().buffering()
            "unsupported", "unsupportedVideoCodec" -> normal().unsupportedVideoCodec()
            "unsupportedContainer" -> normal().unsupportedContainer()
            "unsupportedAudio", "unsupportedAudioCodec" -> normal().unsupportedAudioCodec()
            "corrupt" -> normal().corrupt()
            "disconnect" -> normal().disconnect()
            "resourceExhausted" -> normal().resourceExhausted()
            "hostActionTimeout" -> normal().hostActionTimeout("delete")
            "trackingLost" -> normal().trackingLost(listOf(TimeRangeUs(10_000_000L, 15_000_000L)))
            "exportFails" -> normal().exportFails()
            "exportCancelSlow" -> normal().exportCancelSlow()
            else -> null
        }

        /**
         * Default scenario resolver (04A B9): a [DemoSourceFactory] (the plugin maps `demo:<scenarioId>` source
         * references to it) or a media token `demo:<scenarioId>[:<suffix>]` selects [named]; everything else
         * plays [normal].
         */
        public fun forSource(source: VideoKitMediaSource): FakeScenario {
            (source.sourceFactory as? DemoSourceFactory)?.let { return named(it.scenarioId) ?: normal() }
            val token = source.mediaToken
            if (!token.startsWith(DEMO_TOKEN_PREFIX)) return normal()
            val name = token.removePrefix(DEMO_TOKEN_PREFIX).substringBefore(':')
            return named(name) ?: normal()
        }
    }
}
