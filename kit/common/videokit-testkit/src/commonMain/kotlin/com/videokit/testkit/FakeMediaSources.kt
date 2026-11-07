package com.videokit.testkit

import com.videokit.api.MediaKind
import com.videokit.api.OpenPurpose
import com.videokit.api.Seekability
import com.videokit.api.SourceErrorCode
import com.videokit.api.VideoKitMediaSource
import com.videokit.api.VideoKitReadHandle
import com.videokit.api.VideoKitSourceException
import com.videokit.api.VideoKitSourceFactory
import com.videokit.testkit.internal.AtomicCounter
import com.videokit.testkit.internal.AtomicFlag
import com.videokit.testkit.internal.RecordList
import kotlinx.coroutines.awaitCancellation

/** Behaviour of a [CountingSourceFactory]. */
public sealed interface SourceBehavior {
    /** Serves [data]. */
    public data class Bytes(
        /** Content. */
        val data: ByteArray = DEMO_BYTES,
    ) : SourceBehavior {
        override fun equals(other: Any?): Boolean = other is Bytes && other.data.contentEquals(data)

        override fun hashCode(): Int = data.contentHashCode()
    }

    /** Delegates to another factory (for example the real media of a contract subject). */
    public data class Delegate(
        /** Delegate factory. */
        val factory: VideoKitSourceFactory,
    ) : SourceBehavior

    /** `open` throws a classified [VideoKitSourceException]. */
    public data class FailOnOpen(
        /** Code. */
        val code: SourceErrorCode,
    ) : SourceBehavior

    /** `readAt` throws a classified [VideoKitSourceException]. */
    public data class FailOnRead(
        /** Code. */
        val code: SourceErrorCode,
    ) : SourceBehavior

    /** `open` throws an unclassified exception whose message contains [secret] (must never leak). */
    public data class ThrowOnOpen(
        /** Text that must not appear in any diagnostic. */
        val secret: String,
    ) : SourceBehavior

    /** `readAt` never returns until cancelled. */
    public data object HangOnRead : SourceBehavior

    /** `open` never returns until cancelled. */
    public data object HangOnOpen : SourceBehavior

    public companion object {
        /** Demo bytes: an ASCII marker followed by zeros; not a real media file. */
        public val DEMO_BYTES: ByteArray = ("VIDEOKIT-DEMO-MEDIA-NOT-REAL".encodeToByteArray() + ByteArray(4_068))
    }
}

/**
 * A host-side [VideoKitSourceFactory] that counts opened and closed handles, so tests can check
 * that every handle is closed (original requirement §14.2).
 */
public class CountingSourceFactory(
    /** Behaviour. */
    public val behavior: SourceBehavior = SourceBehavior.Bytes(),
) : VideoKitSourceFactory {
    private val opened = AtomicCounter()
    private val closed = AtomicCounter()
    private val reads = AtomicCounter()

    private val purposeRecord = RecordList<OpenPurpose>()

    /** Purposes of all `open` calls, in order (snapshot). */
    public val purposes: List<OpenPurpose> get() = purposeRecord.snapshot

    /** Number of handles returned by `open`. */
    public val openCount: Int get() = opened.value.toInt()

    /** Number of handles closed. */
    public val closeCount: Int get() = closed.value.toInt()

    /** Handles currently open. */
    public val openHandles: Int get() = (opened.value - closed.value).toInt()

    /** Number of `readAt` calls. */
    public val readCount: Int get() = reads.value.toInt()

    override suspend fun open(purpose: OpenPurpose): VideoKitReadHandle {
        purposeRecord.add(purpose)
        val delegateHandle: VideoKitReadHandle? = when (val b = behavior) {
            is SourceBehavior.FailOnOpen -> throw VideoKitSourceException(b.code)
            is SourceBehavior.ThrowOnOpen -> throw IllegalStateException("cannot open smb://user:${b.secret}@nas/share/${b.secret}.mp4")
            SourceBehavior.HangOnOpen -> awaitCancellation()
            is SourceBehavior.Delegate -> b.factory.open(purpose)
            else -> null
        }
        opened.incrementAndGet()
        return CountingHandle(delegateHandle)
    }

    private inner class CountingHandle(private val delegate: VideoKitReadHandle?) : VideoKitReadHandle {
        private val isClosed = AtomicFlag()

        override val length: Long?
            get() = delegate?.length ?: (behavior as? SourceBehavior.Bytes)?.data?.size?.toLong()

        override suspend fun readAt(offset: Long, target: ByteArray, targetOffset: Int, length: Int): Int {
            check(!isClosed.value) { "handle used after close" }
            reads.incrementAndGet()
            return when (val b = behavior) {
                is SourceBehavior.FailOnRead -> throw VideoKitSourceException(b.code)

                SourceBehavior.HangOnRead -> awaitCancellation()

                is SourceBehavior.Bytes -> {
                    if (offset >= b.data.size) return -1
                    val count = minOf(length.toLong(), b.data.size - offset).toInt()
                    b.data.copyInto(target, targetOffset, offset.toInt(), offset.toInt() + count)
                    count
                }

                else -> delegate?.readAt(offset, target, targetOffset, length) ?: -1
            }
        }

        override fun close() {
            if (isClosed.setOnce()) {
                closed.incrementAndGet()
                delegate?.close()
            }
        }
    }
}

/** Ready-made host sources for tests and demos. */
public object FakeMediaSources {
    /** A demo video source; pass a [CountingSourceFactory] to inspect handle usage. */
    public fun video(
        token: String,
        factory: VideoKitSourceFactory = CountingSourceFactory(),
        seekability: Seekability = Seekability.RANDOM_ACCESS,
        displayName: String? = null,
    ): VideoKitMediaSource = VideoKitMediaSource(
        mediaToken = token,
        mediaKind = MediaKind.VIDEO,
        displayName = displayName,
        knownLength = SourceBehavior.DEMO_BYTES.size.toLong(),
        mimeType = "video/mp4",
        extension = "mp4",
        seekability = seekability,
        sourceFactory = factory,
    )

    /** A demo image source. */
    public fun image(
        token: String,
        kind: MediaKind = MediaKind.IMAGE_STATIC,
        factory: VideoKitSourceFactory = CountingSourceFactory(),
        displayName: String? = null,
    ): VideoKitMediaSource {
        require(kind.isImage) { "kind must be an image kind" }
        return VideoKitMediaSource(
            mediaToken = token,
            mediaKind = kind,
            displayName = displayName,
            knownLength = SourceBehavior.DEMO_BYTES.size.toLong(),
            mimeType = if (kind == MediaKind.IMAGE_ANIMATED) "image/gif" else "image/jpeg",
            extension = if (kind == MediaKind.IMAGE_ANIMATED) "gif" else "jpg",
            seekability = Seekability.RANDOM_ACCESS,
            sourceFactory = factory,
        )
    }
}

/**
 * Source factory of a demo source selected by scenario id (04A B9): the Flutter plugin maps the Dart
 * `DemoSourceRef(scenarioId)` (wire form `demo:<scenarioId>`) to it. It serves [SourceBehavior.DEMO_BYTES].
 */
public class DemoSourceFactory(
    /** Scenario id from [FakeScenario.NAMES]; unknown ids play [FakeScenario.normal]. */
    public val scenarioId: String,
) : VideoKitSourceFactory {
    private val delegate = CountingSourceFactory()

    override suspend fun open(purpose: OpenPurpose): VideoKitReadHandle = delegate.open(purpose)

    /** Handles currently open (diagnostics). */
    public val openHandles: Int get() = delegate.openHandles
}

/** Builds a demo source for [scenarioId] (`demo:<scenarioId>` references). */
public fun FakeMediaSources.demo(
    scenarioId: String,
    token: String,
    kind: MediaKind = MediaKind.VIDEO,
    displayName: String? = null,
): VideoKitMediaSource = if (kind == MediaKind.VIDEO) {
    video(token, DemoSourceFactory(scenarioId), displayName = displayName)
} else {
    image(token, kind, DemoSourceFactory(scenarioId), displayName)
}
