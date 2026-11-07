package com.videokit.api

/**
 * Registered codes of [VideoKitEvent.TransientNotice] (04A K1, `spec/notices.json`): upper snake case, verified
 * against the registry by the Kit and Dart tests. The UI maps known codes to text and ignores unknown ones; new codes
 * are appended (minor API version change).
 */
public object NoticeCodes {
    /** A seek target was clamped to the media bounds. */
    public const val SEEK_CLAMPED: String = "SEEK_CLAMPED"

    /** The session was degraded because resources were short (07 §3: decoder not reopened, lower quality). */
    public const val RESOURCE_DEGRADED: String = "RESOURCE_DEGRADED"

    /** There is no media in the requested navigation direction. */
    public const val NAVIGATION_UNAVAILABLE: String = "NAVIGATION_UNAVAILABLE"

    /** The image decode resolution was reduced to stay within the image memory budget (04A I4). */
    public const val IMAGE_MEMORY_REDUCED_QUALITY: String = "IMAGE_MEMORY_REDUCED_QUALITY"

    /** The audio track cannot be decoded; the picture plays silently (15 §2.2). */
    public const val AUDIO_UNSUPPORTED_PLAYING_SILENT: String = "AUDIO_UNSUPPORTED_PLAYING_SILENT"

    /** Another app took the system audio focus; playback paused (07 §4). */
    public const val AUDIO_FOCUS_LOST: String = "AUDIO_FOCUS_LOST"

    /** All codes in registry order. */
    public val ALL: List<String> = listOf(
        SEEK_CLAMPED,
        RESOURCE_DEGRADED,
        NAVIGATION_UNAVAILABLE,
        IMAGE_MEMORY_REDUCED_QUALITY,
        AUDIO_UNSUPPORTED_PLAYING_SILENT,
        AUDIO_FOCUS_LOST,
    )
}
