package com.videokit.api

/** Kind of media bound to a session (04 §5, original requirement §14.1). */
public enum class MediaKind {
    /** Video (with or without audio). */
    VIDEO,

    /** Static image. */
    IMAGE_STATIC,

    /** Animated image (GIF, animated WebP/AVIF). */
    IMAGE_ANIMATED,

    /** Image whose static/animated nature is not known yet. */
    IMAGE_UNKNOWN,
    ;

    /** Whether this kind is an image kind. */
    public val isImage: Boolean get() = this != VIDEO
}

/** Whether a source supports random access reads (04 §5). */
public enum class Seekability {
    /** `readAt` may be called with any offset. */
    RANDOM_ACCESS,

    /** Only sequential reads from offset 0 are efficient; seeking is reported as unsupported. */
    SEQUENTIAL_ONLY,
}

/** How fast a source delivers bytes, as the host knows it (04A P6). */
public enum class SourceLatency {
    /** Local storage (default). */
    LOCAL,

    /**
     * Network or remote storage (for example SMB): seek preview frames are off by default and only the time bubble is
     * shown; single thumbnails are still allowed within their hard timeout (04A P5).
     */
    SLOW,
}

/** Why VideoKit opens a read handle (04 §5). The host may track and close handles per purpose. */
public enum class OpenPurpose {
    /** Short probe of the container and tracks. */
    PROBE,

    /** Playback or image display. */
    PLAYBACK,

    /** Edit preview and timeline operations. */
    EDIT,

    /** Export encoding. */
    EXPORT,
}

/**
 * VideoKit's own media descriptor (04 §5, original requirement §14.1). It never contains host paths,
 * SMB URLs, credentials or host database objects.
 */
public data class VideoKitMediaSource(
    /** Opaque, host generated token identifying the media for this session. */
    val mediaToken: String,
    /** Media kind. */
    val mediaKind: MediaKind,
    /** Display name; for display only, never logged. */
    val displayName: String? = null,
    /** Known length in bytes, if any. */
    val knownLength: Long? = null,
    /** MIME type hint; not trusted as the only evidence. */
    val mimeType: String? = null,
    /** File extension hint; not trusted as the only evidence. */
    val extension: String? = null,
    /** Random access support of the source. */
    val seekability: Seekability,
    /** Factory creating short-lived read handles. */
    val sourceFactory: VideoKitSourceFactory,
    /** How fast the source is (04A P6); [SourceLatency.SLOW] turns seek preview frames off by default. */
    val latencyHint: SourceLatency = SourceLatency.LOCAL,
)

/** Creates short-lived read handles for a source (04 §5). */
public fun interface VideoKitSourceFactory {
    /**
     * Opens a new read handle. May throw [VideoKitSourceException] to report a classified failure.
     * VideoKit closes every handle it opens, including on cancellation and release.
     */
    public suspend fun open(purpose: OpenPurpose): VideoKitReadHandle
}

/**
 * Random access read handle implemented by the host (04 §5, original requirement §14.2).
 *
 * VideoKit calls [readAt] on an IO dispatcher and cancels it on timeout. Offsets are `Long`
 * (files larger than 2 GiB are supported); a single read length is an `Int`.
 */
public interface VideoKitReadHandle : AutoCloseable {
    /** Total length in bytes, or `null` when unknown. */
    public val length: Long?

    /**
     * Reads up to [length] bytes starting at [offset] into [target] at [targetOffset].
     *
     * @return the number of bytes read (a short read is normal), or `-1` at end of stream.
     * @throws VideoKitSourceException for classified source failures.
     */
    public suspend fun readAt(offset: Long, target: ByteArray, targetOffset: Int, length: Int): Int
}
