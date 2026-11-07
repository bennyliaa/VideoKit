package com.videokit.api

/**
 * Registered export warning codes (04A K3, `spec/notices.json` group `exportWarnings`): upper snake case. A warning
 * on the wire is the code alone or `CODE:argument` for codes that name an object (for example the mask id); use
 * [codeOf] to get the code. The UI explains known codes and shows unknown ones generically.
 */
public object ExportWarnings {
    /** A fast concatenation boundary was moved to the nearest key frame (08 §7). */
    public const val BOUNDARY_ALIGNED_TO_KEYFRAME: String = "BOUNDARY_ALIGNED_TO_KEYFRAME"

    /** Silence was inserted for an input without audio (08 §7). */
    public const val SILENCE_INSERTED: String = "SILENCE_INSERTED"

    /** `TRACKING_INCOMPLETE:<maskId>`: the tracking of a mask did not complete. */
    public const val TRACKING_INCOMPLETE: String = "TRACKING_INCOMPLETE"

    /** `TRACKING_COVERAGE_ACCEPTED:<maskId>`: the user accepted uncovered tracking ranges; not fully masked (09 §4). */
    public const val TRACKING_COVERAGE_ACCEPTED: String = "TRACKING_COVERAGE_ACCEPTED"

    /** `TRACKING_LOST_RANGES:<maskId>`: the tracking of a mask has lost ranges that were not accepted. */
    public const val TRACKING_LOST_RANGES: String = "TRACKING_LOST_RANGES"

    /** Demo backend: no real media file was produced. */
    public const val DEMO_OUTPUT_NOT_REAL_MEDIA: String = "DEMO_OUTPUT_NOT_REAL_MEDIA"

    /** The engine refused fast (remux) concatenation; the export transcodes instead. */
    public const val FAST_CONCAT_REJECTED: String = "FAST_CONCAT_REJECTED"

    /** All codes in registry order. */
    public val ALL: List<String> = listOf(
        BOUNDARY_ALIGNED_TO_KEYFRAME,
        SILENCE_INSERTED,
        TRACKING_INCOMPLETE,
        TRACKING_COVERAGE_ACCEPTED,
        TRACKING_LOST_RANGES,
        DEMO_OUTPUT_NOT_REAL_MEDIA,
        FAST_CONCAT_REJECTED,
    )

    /** The code of a wire warning (`CODE` or `CODE:argument`). */
    public fun codeOf(warning: String): String = warning.substringBefore(':')

    /** `CODE:argument`. */
    public fun withArgument(code: String, argument: String): String = "$code:$argument"
}
