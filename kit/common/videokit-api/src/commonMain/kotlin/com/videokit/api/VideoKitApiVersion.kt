package com.videokit.api

/**
 * Semantic version of the VideoKit public API (04 §10).
 *
 * The API major version equals the artifact major version (02 §7 #1). Hosts may query
 * [VideoKit.apiVersion] at runtime and enable features by comparing versions.
 *
 * - **major**: removed fields, changed semantics or a changed state machine (with a migration note).
 * - **minor**: new optional fields, commands, error codes or capability items.
 * - **patch**: fixes that do not change semantics.
 */
public data class VideoKitApiVersion(
    /** Major version; incompatible changes. */
    val major: Int,
    /** Minor version; backwards compatible additions. */
    val minor: Int,
    /** Patch version; fixes without semantic change. */
    val patch: Int,
) : Comparable<VideoKitApiVersion> {
    init {
        require(major >= 0 && minor >= 0 && patch >= 0) { "Version components must not be negative" }
    }

    override fun compareTo(other: VideoKitApiVersion): Int = compareValuesBy(this, other, { it.major }, { it.minor }, { it.patch })

    /** Whether code written against [required] can run against this version (same major, not older). */
    public fun isCompatibleWith(required: VideoKitApiVersion): Boolean = major == required.major && this >= required

    /** `major.minor.patch`. */
    override fun toString(): String = "$major.$minor.$patch"

    public companion object {
        /** The API version implemented by this artifact. */
        public val CURRENT: VideoKitApiVersion = VideoKitApiVersion(1, 0, 0)

        /** Parses `major.minor.patch`; returns `null` for any other format. */
        public fun parse(text: String): VideoKitApiVersion? {
            val parts = text.trim().split('.')
            if (parts.size != 3) return null
            val numbers = parts.map { part -> part.toIntOrNull()?.takeIf { it >= 0 } ?: return null }
            return VideoKitApiVersion(numbers[0], numbers[1], numbers[2])
        }
    }
}
