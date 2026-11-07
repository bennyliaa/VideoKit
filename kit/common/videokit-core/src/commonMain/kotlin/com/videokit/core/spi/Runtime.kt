package com.videokit.core.spi

import kotlinx.coroutines.CoroutineDispatcher

/**
 * Platform engine interfaces (SPI) of VideoKit (02 §4.2). Status: **M0 draft**, reviewed together with
 * the API freeze; implementations arrive from M1 (the `kit/android` modules).
 *
 * Rules for every SPI:
 * - thin: only what the platform must provide, no business rules (those live in the platform independent
 *   modules and are verified with `spec/vectors`);
 * - no platform types (no Android, JVM-only, Apple or Windows types); render targets are
 *   [com.videokit.api.VideoKitSurfaceTarget] and inputs are [com.videokit.api.VideoKitMediaSource];
 * - failures are reported as [SpiException] carrying a [com.videokit.api.VideoKitStableError];
 * - long operations are cancellable `suspend` functions; handles are [AutoCloseable] and close idempotently.
 */
public class SpiException(
    /** Stable error. */
    public val error: com.videokit.api.VideoKitStableError,
) : Exception("SPI failure ${error.code} at ${error.stage}")

/** Time source (02 §4.2 `Clock`); injectable so tests control time. */
public interface Clock {
    /** Monotonic time in microseconds; only differences are meaningful. */
    public fun monotonicUs(): Long

    /** Wall clock time in epoch milliseconds. */
    public fun epochMs(): Long
}

/** Dispatchers used by the runtime (02 §4.2 `Scheduler`, 02 §5). */
public interface Scheduler {
    /** Dispatcher for blocking I/O such as host `readAt` calls. */
    public val io: CoroutineDispatcher

    /** Dispatcher for CPU work. */
    public val compute: CoroutineDispatcher

    /** A dispatcher that runs one task at a time (per-session serial command executor). */
    public fun serial(name: String): CoroutineDispatcher
}

/**
 * The set of platform engines a platform module injects into the runtime (02 §4.2). Optional engines are
 * `null` when the platform or build does not provide them; the capability report then says so.
 */
public data class PlatformEngines(
    /** Playback. */
    val playback: PlaybackEngine,
    /** Images. */
    val images: ImageEngine,
    /** Capability probing. */
    val capabilities: CapabilityProbe,
    /** Time. */
    val clock: Clock,
    /** Dispatchers. */
    val scheduler: Scheduler,
    /** Frame extraction (thumbnails, tracking frames). */
    val frames: FrameSource? = null,
    /** Export pipeline. */
    val exporter: CompositionExporter? = null,
    /** GPU effects. */
    val effects: EffectRenderer? = null,
    /** Tracking inference. */
    val tracker: TrackerBackend? = null,
    /** Isolation of high-risk tasks. */
    val isolation: IsolationHost? = null,
)
