package com.videokit.media3

import android.content.Context
import android.net.Uri
import android.os.Handler
import android.os.HandlerThread
import android.os.Looper
import androidx.annotation.OptIn
import androidx.media3.common.AudioAttributes
import androidx.media3.common.C
import androidx.media3.common.Format
import androidx.media3.common.MediaItem
import androidx.media3.common.MimeTypes
import androidx.media3.common.PlaybackException
import androidx.media3.common.Player
import androidx.media3.common.TrackSelectionOverride
import androidx.media3.common.Tracks
import androidx.media3.common.VideoSize
import androidx.media3.common.util.UnstableApi
import androidx.media3.exoplayer.DefaultLoadControl
import androidx.media3.exoplayer.ExoPlaybackException
import androidx.media3.exoplayer.ExoPlayer
import androidx.media3.exoplayer.SeekParameters
import androidx.media3.exoplayer.source.ProgressiveMediaSource
import androidx.media3.extractor.DefaultExtractorsFactory
import com.videokit.api.ErrorStage
import com.videokit.api.MediaInfo
import com.videokit.api.OpenPurpose
import com.videokit.api.SeekMode
import com.videokit.api.Size
import com.videokit.api.TrackInfo
import com.videokit.api.VideoKitMediaSource
import com.videokit.api.VideoKitSurfaceTarget
import com.videokit.api.android.AndroidSurface
import com.videokit.core.runtime.StableErrors
import com.videokit.core.spi.EngineState
import com.videokit.core.spi.EngineStatus
import com.videokit.core.spi.PlaybackEngine
import com.videokit.core.spi.PlaybackHandle
import com.videokit.core.spi.PlaybackOpenOptions
import com.videokit.core.spi.SpiException
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.CompletableDeferred
import kotlinx.coroutines.CoroutineDispatcher
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.withContext
import kotlinx.coroutines.withTimeoutOrNull
import java.util.concurrent.CountDownLatch
import java.util.concurrent.TimeUnit
import kotlin.coroutines.CoroutineContext

/**
 * Tunables of the Media3 engine. Values are M1 defaults; S1 (host read and seek, 15 §4) measures and freezes them.
 */
public data class Media3EngineConfig(
    /** Timeout of opening the host read handle. */
    val openTimeoutMs: Long = 10_000L,
    /** Timeout of one host `readAt`. */
    val readTimeoutMs: Long = 10_000L,
    /** In-memory read-ahead per host read (no disk cache, 15 §2.1). */
    val prefetchBytes: Int = HostReader.DEFAULT_PREFETCH_BYTES,
    /** LoadControl buffer bounds (06 §3.6: bounded, never downloads a whole video). */
    val minBufferMs: Int = 15_000,
    val maxBufferMs: Int = 30_000,
    val bufferForPlaybackMs: Int = 2_500,
    val bufferForPlaybackAfterRebufferMs: Int = 5_000,
    /** Position update interval while playing (EngineState contract: at least every 250 ms). */
    val positionUpdateMs: Long = 100L,
    /** Upper bound of waiting for a seek to land. */
    val seekTimeoutMs: Long = 10_000L,
)

/**
 * [PlaybackEngine] with AndroidX Media3 ExoPlayer (15 §2.1, §2.2, §2.6): one player per session on its own looper
 * thread, progressive media through [HostDataSource] (host `readAt`, m2ts adapter), system decoders with fallback,
 * rendering into an [AndroidSurface] (Flutter SurfaceProducer or a host SurfaceView).
 */
@OptIn(UnstableApi::class)
public class Media3PlaybackEngine(context: Context, private val config: Media3EngineConfig = Media3EngineConfig()) : PlaybackEngine {
    private val appContext = context.applicationContext

    override fun supports(target: VideoKitSurfaceTarget): Boolean = target is AndroidSurface

    override suspend fun open(source: VideoKitMediaSource, options: PlaybackOpenOptions): PlaybackHandle {
        val m2ts = sniffM2ts(source)
        val handle = Media3PlaybackHandle(appContext, source, m2ts, options, config)
        try {
            handle.prepare()
            return handle
        } catch (failure: Throwable) {
            handle.close()
            throw failure
        }
    }

    /** Whether [source] is m2ts (by name and by the packet layout of its first bytes). */
    private suspend fun sniffM2ts(source: VideoKitMediaSource): Boolean {
        val named = listOfNotNull(source.extension, source.displayName?.substringAfterLast('.', ""))
            .any { it.equals("m2ts", ignoreCase = true) || it.equals("mts", ignoreCase = true) }
        if (!named) return false
        val header = ByteArray(M2ts.SNIFF_BYTES)
        val read = try {
            val probe = source.sourceFactory.open(OpenPurpose.PROBE)
            try {
                readFully(probe, header)
            } finally {
                probe.close()
            }
        } catch (cancelled: CancellationException) {
            throw cancelled
        } catch (failure: Exception) {
            throw SpiException(StableErrors.fromSourceFailure(failure, ErrorStage.PROBE))
        }
        return M2ts.isM2ts(header, read)
    }

    private suspend fun readFully(handle: com.videokit.api.VideoKitReadHandle, target: ByteArray): Int {
        var total = 0
        while (total < target.size) {
            val read = handle.readAt(total.toLong(), target, total, target.size - total)
            if (read <= 0) break
            total += read
        }
        return total
    }
}

/** A coroutine dispatcher on [handler]'s looper (no kotlinx-coroutines-android needed). */
internal class HandlerDispatcher(private val handler: Handler) : CoroutineDispatcher() {
    override fun isDispatchNeeded(context: CoroutineContext): Boolean = Looper.myLooper() != handler.looper

    override fun dispatch(context: CoroutineContext, block: Runnable) {
        if (!handler.post(block)) throw CancellationException("player thread stopped")
    }
}

/** One ExoPlayer playback (see [Media3PlaybackEngine]). */
@OptIn(UnstableApi::class)
internal class Media3PlaybackHandle(
    private val context: Context,
    private val source: VideoKitMediaSource,
    private val m2ts: Boolean,
    private val options: PlaybackOpenOptions,
    private val config: Media3EngineConfig,
) : PlaybackHandle {
    private val thread = HandlerThread("videokit-player").apply { start() }
    private val handler = Handler(thread.looper)
    private val dispatcher = HandlerDispatcher(handler)
    private val pool = HostHandlePool(source.sourceFactory, config.openTimeoutMs)
    private val mutableState = MutableStateFlow(
        EngineState(EngineStatus.PREPARING, false, 0L, null, null, null, emptyList(), emptyList()),
    )

    // Player thread only.
    private var player: ExoPlayer? = null
    private var prepared = false
    private var failure: EngineState? = null
    private var tracks: Map<String, TrackRef> = emptyMap()
    private var audioTracks: List<TrackInfo> = emptyList()
    private var subtitleTracks: List<TrackInfo> = emptyList()
    private var selectedAudio: String? = null
    private var selectedSubtitle: String? = null
    private var videoSize: Size? = null
    private var videoFormat: Format? = null
    private var audioTrackFormat: Format? = null
    private var pendingSeek: CompletableDeferred<Unit>? = null
    private var focusLosses = 0
    private var seekDiscontinuity = false
    private var audioEnabled = options.audioEnabled
    private val positionUpdater = object : Runnable {
        override fun run() {
            publish()
            if (player?.isPlaying == true) handler.postDelayed(this, config.positionUpdateMs)
        }
    }

    @Volatile
    private var closed = false

    override val state: StateFlow<EngineState> = mutableState.asStateFlow()

    /** Builds and prepares the player; returns when it is ready or throws [SpiException]. */
    suspend fun prepare() {
        withContext(dispatcher) { createPlayer() }
        // R2-03: done once the media is parsed (BUFFERING after the tracks are known), not only when enough is buffered to
        // play: on slow host sources buffering may take longer than the open timeout.
        val ready = mutableState.first { it.status != EngineStatus.PREPARING }
        if (ready.status == EngineStatus.FAILED) {
            throw SpiException(
                ready.error ?: StableErrors.of(com.videokit.api.ErrorCode.INTERNAL_ERROR_REDACTED, ErrorStage.BIND, "MEDIA3:PREPARE"),
            )
        }
    }

    private fun createPlayer() {
        val loadControl = DefaultLoadControl.Builder()
            .setBufferDurationsMs(
                config.minBufferMs,
                config.maxBufferMs,
                config.bufferForPlaybackMs,
                config.bufferForPlaybackAfterRebufferMs,
            )
            .build()
        val extractors = DefaultExtractorsFactory()
        val dataSources = HostDataSource.Factory(pool, config.readTimeoutMs, config.prefetchBytes, m2ts)
        val mediaSource = ProgressiveMediaSource.Factory(dataSources, extractors)
            // The URI only identifies the item; bytes always come from the host handle.
            .createMediaSource(MediaItem.fromUri(Uri.parse("videokit://media/" + Uri.encode(source.mediaToken))))
        val exo = ExoPlayer.Builder(context)
            .setLooper(thread.looper)
            .setLoadControl(loadControl)
            .setHandleAudioBecomingNoisy(true)
            .build()
        player = exo
        exo.addListener(listener)
        exo.setAudioAttributes(AUDIO_ATTRIBUTES, options.audioEnabled && options.handleAudioFocus)
        exo.trackSelectionParameters = exo.trackSelectionParameters.buildUpon()
            .setTrackTypeDisabled(C.TRACK_TYPE_TEXT, true)
            .setTrackTypeDisabled(C.TRACK_TYPE_AUDIO, !options.audioEnabled)
            .build()
        exo.repeatMode = if (options.looping) Player.REPEAT_MODE_ONE else Player.REPEAT_MODE_OFF
        exo.setMediaSource(mediaSource, options.startPositionUs / 1_000L)
        exo.prepare()
    }

    private val listener = object : Player.Listener {
        override fun onPlaybackStateChanged(playbackState: Int) {
            if (playbackState == Player.STATE_READY) prepared = true
            if (playbackState == Player.STATE_READY || playbackState == Player.STATE_ENDED) completeSeekIfLanded()
            publish()
        }

        override fun onIsPlayingChanged(isPlaying: Boolean) {
            handler.removeCallbacks(positionUpdater)
            if (isPlaying) handler.post(positionUpdater)
            publish()
        }

        override fun onPlayWhenReadyChanged(playWhenReady: Boolean, reason: Int) {
            // Another app took the audio focus for good: ExoPlayer paused; the session reports it (07 §4).
            if (!playWhenReady && reason == Player.PLAY_WHEN_READY_CHANGE_REASON_AUDIO_FOCUS_LOSS) focusLosses++
            publish()
        }

        override fun onTracksChanged(tracks: Tracks) {
            // R2-03: the media is parsed (tracks and duration known): the open is done; buffering continues as BUFFERING.
            if (!tracks.isEmpty) prepared = true
            readTracks(tracks)
            publish()
        }

        override fun onVideoSizeChanged(size: VideoSize) {
            videoSize = if (size.width > 0 && size.height > 0) Size(size.width, size.height) else null
            publish()
        }

        override fun onPositionDiscontinuity(oldPosition: Player.PositionInfo, newPosition: Player.PositionInfo, reason: Int) {
            if (reason == Player.DISCONTINUITY_REASON_SEEK) {
                seekDiscontinuity = true
                completeSeekIfLanded()
            }
            publish()
        }

        override fun onPlayerError(error: PlaybackException) {
            val trackType = (error as? ExoPlaybackException)
                ?.takeIf { it.type == ExoPlaybackException.TYPE_RENDERER }
                ?.rendererFormat
                ?.sampleMimeType
                ?.let { MimeTypes.getTrackType(it) }
            val stable = PlaybackErrors.map(error.errorCode, error.cause ?: error, trackType)
            failure =
                EngineState(EngineStatus.FAILED, false, currentPositionUs(), null, null, videoSize, audioTracks, subtitleTracks, stable)
            pendingSeek?.complete(Unit)
            pendingSeek = null
            publish()
        }
    }

    private fun completeSeekIfLanded() {
        val exo = player ?: return
        val landed = seekDiscontinuity && (exo.playbackState == Player.STATE_READY || exo.playbackState == Player.STATE_ENDED)
        if (landed) {
            pendingSeek?.complete(Unit)
            pendingSeek = null
            seekDiscontinuity = false
        }
    }

    private fun readTracks(all: Tracks) {
        val refs = mutableMapOf<String, TrackRef>()
        val audio = mutableListOf<TrackInfo>()
        val text = mutableListOf<TrackInfo>()
        var audioSelected: String? = null
        var textSelected: String? = null
        var video: Format? = null
        var audioFormat: Format? = null
        all.groups.forEachIndexed { groupIndex, group ->
            val chosen = (0 until group.length).firstOrNull { group.isTrackSelected(it) } ?: 0.takeIf { group.length > 0 }
            // The selected track of a group wins; otherwise its first track, if nothing was found yet.
            val selected = chosen != null && group.isTrackSelected(chosen)
            when (group.type) {
                C.TRACK_TYPE_VIDEO -> if (video == null || selected) video = chosen?.let(group::getTrackFormat)
                C.TRACK_TYPE_AUDIO -> if (audioFormat == null || selected) audioFormat = chosen?.let(group::getTrackFormat)
            }
            val prefix = when (group.type) {
                C.TRACK_TYPE_AUDIO -> "audio"
                C.TRACK_TYPE_TEXT -> "text"
                else -> return@forEachIndexed
            }
            for (index in 0 until group.length) {
                val format = group.getTrackFormat(index)
                val id = "$prefix:$groupIndex:$index"
                refs[id] = TrackRef(group, index)
                val channels = format.channelCount.takeIf { group.type == C.TRACK_TYPE_AUDIO && it != Format.NO_VALUE && it > 0 }
                val info = TrackInfo(id, format.language, format.label, format.sampleMimeType, group.isTrackSupported(index), channels)
                if (group.type == C.TRACK_TYPE_AUDIO) {
                    audio += info
                    if (group.isTrackSelected(index)) audioSelected = id
                } else {
                    text += info
                    if (group.isTrackSelected(index)) textSelected = id
                }
            }
        }
        tracks = refs
        videoFormat = video
        audioTrackFormat = audioFormat
        audioTracks = audio
        subtitleTracks = text
        selectedAudio = audioSelected ?: selectedAudio.takeIf { it in refs }
        selectedSubtitle = textSelected
    }

    /** Publishes the current player state (player thread). */
    private fun publish() {
        val exo = player ?: return
        failure?.let {
            mutableState.value = it
            return
        }
        val status = when (exo.playbackState) {
            Player.STATE_READY -> EngineStatus.READY
            Player.STATE_ENDED -> EngineStatus.ENDED
            Player.STATE_BUFFERING -> if (prepared) EngineStatus.BUFFERING else EngineStatus.PREPARING
            else -> EngineStatus.PREPARING
        }
        mutableState.value = EngineState(
            status = status,
            playing = exo.playWhenReady && status != EngineStatus.ENDED,
            positionUs = currentPositionUs(),
            durationUs = exo.duration.takeIf { it != C.TIME_UNSET }?.times(1_000L),
            bufferedUs = exo.bufferedPosition * 1_000L,
            videoSize = videoSize,
            audioTracks = audioTracks,
            subtitleTracks = subtitleTracks,
            selectedAudioTrackId = selectedAudio,
            selectedSubtitleTrackId = selectedSubtitle,
            mediaInfo = mediaInfo(exo),
            audioFocusLosses = focusLosses,
        )
    }

    private fun currentPositionUs(): Long = (player?.currentPosition ?: 0L) * 1_000L

    /** Media parameters from the track formats (04A P2); `null` until the tracks are known. */
    private fun mediaInfo(exo: ExoPlayer): MediaInfo? {
        val video = videoFormat
        val audio = audioTrackFormat
        if (video == null && audio == null) return null
        val bitrate = (video?.averageBitrate?.takeIf { it > 0 } ?: video?.bitrate?.takeIf { it > 0 })?.toLong()
        return MediaInfo(
            container = containerName(video?.containerMimeType ?: audio?.containerMimeType),
            videoCodec = video?.sampleMimeType,
            audioCodec = audio?.sampleMimeType,
            width = video?.width?.takeIf { it > 0 },
            height = video?.height?.takeIf { it > 0 },
            frameRate = video?.frameRate?.takeIf { it > 0f },
            bitrateBps = bitrate,
            rotationDeg = video?.rotationDegrees,
            durationUs = exo.duration.takeIf { it != C.TIME_UNSET }?.times(1_000L),
            fileSizeBytes = pool.length,
        )
    }

    /** Container name of a Media3 container MIME type; the source extension when Media3 does not say. */
    private fun containerName(mime: String?): String? = when (mime) {
        MimeTypes.VIDEO_MP4, MimeTypes.AUDIO_MP4 -> if (source.extension.equals("mov", ignoreCase = true)) "mov" else "mp4"
        MimeTypes.VIDEO_MATROSKA, MimeTypes.AUDIO_MATROSKA -> "mkv"
        MimeTypes.VIDEO_WEBM, MimeTypes.AUDIO_WEBM -> "webm"
        MimeTypes.VIDEO_MP2T -> if (m2ts) "m2ts" else "ts"
        MimeTypes.VIDEO_AVI -> "avi"
        else -> source.extension?.lowercase()
    }

    private suspend fun <T> onPlayer(block: (ExoPlayer) -> T): T? = if (closed) {
        null
    } else {
        withContext(dispatcher) { player?.let(block) }
    }

    override suspend fun play() {
        onPlayer { it.play() }
    }

    override suspend fun pause() {
        onPlayer { it.pause() }
    }

    override suspend fun seekTo(positionUs: Long, mode: SeekMode) {
        val landed = CompletableDeferred<Unit>()
        onPlayer { exo ->
            // Preview / closest sync: cheap key-frame seeks while dragging; exact when the user lets go (15 §2.1).
            exo.setSeekParameters(if (mode == SeekMode.EXACT) SeekParameters.EXACT else SeekParameters.CLOSEST_SYNC)
            pendingSeek?.complete(Unit)
            pendingSeek = landed
            seekDiscontinuity = false
            exo.seekTo(positionUs / 1_000L)
        } ?: return
        withTimeoutOrNull(config.seekTimeoutMs) { landed.await() }
        onPlayer { publish() }
    }

    override suspend fun setSpeed(speed: Float) {
        // PlaybackParameters keep the pitch (06 §4: pitch preserved).
        onPlayer { it.setPlaybackSpeed(speed) }
    }

    override suspend fun setVolume(volume: Float) {
        onPlayer { it.volume = volume }
    }

    override suspend fun setAudioEnabled(enabled: Boolean) {
        onPlayer { exo ->
            audioEnabled = enabled
            // Silent multi-view slots deselect the audio track (releasing the decoder) and never hold focus (15 §2.1).
            exo.trackSelectionParameters =
                exo.trackSelectionParameters.buildUpon().setTrackTypeDisabled(C.TRACK_TYPE_AUDIO, !enabled).build()
            exo.setAudioAttributes(AUDIO_ATTRIBUTES, enabled && options.handleAudioFocus)
        }
    }

    override suspend fun selectAudioTrack(trackId: String?) {
        onPlayer { exo ->
            val builder = exo.trackSelectionParameters.buildUpon()
            val ref = trackId?.let { tracks[it] }
            if (ref == null) {
                builder.clearOverridesOfType(C.TRACK_TYPE_AUDIO)
            } else {
                builder.setOverrideForType(TrackSelectionOverride(ref.group.mediaTrackGroup, ref.index))
            }
            exo.trackSelectionParameters = builder.setTrackTypeDisabled(C.TRACK_TYPE_AUDIO, !audioEnabled).build()
            selectedAudio = ref?.let { trackId }
            publish()
        }
    }

    override suspend fun selectSubtitleTrack(trackId: String?) {
        onPlayer { exo ->
            val builder = exo.trackSelectionParameters.buildUpon()
            val ref = trackId?.let { tracks[it] }
            if (ref == null) {
                builder.clearOverridesOfType(C.TRACK_TYPE_TEXT).setTrackTypeDisabled(C.TRACK_TYPE_TEXT, true)
            } else {
                builder.setTrackTypeDisabled(
                    C.TRACK_TYPE_TEXT,
                    false,
                ).setOverrideForType(TrackSelectionOverride(ref.group.mediaTrackGroup, ref.index))
            }
            exo.trackSelectionParameters = builder.build()
            selectedSubtitle = ref?.let { trackId }
            publish()
        }
    }

    override suspend fun setLooping(looping: Boolean) {
        onPlayer { it.repeatMode = if (looping) Player.REPEAT_MODE_ONE else Player.REPEAT_MODE_OFF }
    }

    override fun attach(target: VideoKitSurfaceTarget) {
        val surface = (target as? AndroidSurface)?.surface ?: return
        handler.post { if (!closed) player?.setVideoSurface(surface) }
    }

    override fun detach() {
        handler.post { if (!closed) player?.clearVideoSurface() }
    }

    /**
     * Releases in the order of 06 §7: the player (decoders, surface, loads) on its thread, then the host read handle,
     * then the thread. Blocks until done or [RELEASE_TIMEOUT_MS].
     */
    override fun close() {
        if (closed) return
        closed = true
        val release = Runnable {
            handler.removeCallbacks(positionUpdater)
            runCatching { player?.release() }
            player = null
            pendingSeek?.complete(Unit)
            pendingSeek = null
        }
        if (Looper.myLooper() == thread.looper) {
            release.run()
        } else {
            val released = CountDownLatch(1)
            val posted = handler.post {
                release.run()
                released.countDown()
            }
            if (posted) released.await(RELEASE_TIMEOUT_MS, TimeUnit.MILLISECONDS)
        }
        pool.close()
        thread.quitSafely()
    }

    private class TrackRef(val group: Tracks.Group, val index: Int)

    private companion object {
        const val RELEASE_TIMEOUT_MS = 5_000L
        val AUDIO_ATTRIBUTES: AudioAttributes = AudioAttributes.Builder()
            .setUsage(C.USAGE_MEDIA)
            .setContentType(C.AUDIO_CONTENT_TYPE_MOVIE)
            .build()
    }
}
