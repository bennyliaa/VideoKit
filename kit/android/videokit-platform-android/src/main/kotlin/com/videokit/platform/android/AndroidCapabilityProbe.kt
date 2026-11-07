package com.videokit.platform.android

import android.content.Context
import android.media.MediaCodecInfo
import android.media.MediaCodecList
import com.videokit.api.CodecInfo
import com.videokit.api.DecoderSummary
import com.videokit.api.ErrorCode
import com.videokit.api.ErrorStage
import com.videokit.api.FormatSupport
import com.videokit.api.ImageFeatures
import com.videokit.api.MediaKind
import com.videokit.api.MediaProbeResult
import com.videokit.api.OpenPurpose
import com.videokit.api.PlaybackFeatures
import com.videokit.api.Size
import com.videokit.api.SupportLevel
import com.videokit.api.UnsupportedReason
import com.videokit.api.VideoKitCapabilities
import com.videokit.api.VideoKitMediaSource
import com.videokit.api.VideoKitReadHandle
import com.videokit.core.runtime.StableErrors
import com.videokit.core.spi.CapabilityProbe
import com.videokit.core.spi.SpiException
import com.videokit.image.ImageFormats
import kotlinx.coroutines.CancellationException

/**
 * Android [CapabilityProbe] (02 §4.2, 15 §2.2), basic version of VK-M1:
 * - device: system decoders from [MediaCodecList] (hardware flag, size limits, declared instance counts), the
 *   containers Media3 reads, codec support by decoder presence, and a suggested number of hardware video sessions
 *   from the declared AVC instance count (a hint; S5 calibrates it, 07 §2);
 * - media: the container from the first bytes of the source (the codec-level probe of the tracks needs the Media3
 *   extractors and is part of the playback open; S2 builds the full matrix).
 */
internal class AndroidCapabilityProbe(@Suppress("unused") private val context: Context) : CapabilityProbe {
    private val decoders: List<MediaCodecInfo> by lazy {
        MediaCodecList(MediaCodecList.REGULAR_CODECS).codecInfos.filterNot { it.isEncoder }
    }

    override suspend fun device(): VideoKitCapabilities {
        val video = mutableListOf<CodecInfo>()
        val audio = mutableListOf<CodecInfo>()
        decoders.forEach { codec ->
            codec.supportedTypes.forEach { type ->
                val caps = runCatching { codec.getCapabilitiesForType(type) }.getOrNull()
                val info = CodecInfo(
                    mimeType = type,
                    hardwareAccelerated = codec.isHardwareAccelerated,
                    maxSize = caps?.videoCapabilities?.let { Size(it.supportedWidths.upper, it.supportedHeights.upper) },
                    maxInstances = caps?.maxSupportedInstances,
                )
                when {
                    type.startsWith("video/") -> video += info
                    type.startsWith("audio/") -> audio += info
                }
            }
        }
        val suggested = suggestedVideoSessions()
        val maxSize =
            video.filter { it.hardwareAccelerated }.mapNotNull { it.maxSize }.maxByOrNull { it.width.toLong() * it.height }
                ?: Size(1920, 1080)
        return VideoKitCapabilities(
            decoders = DecoderSummary(video, audio),
            containerCodecSupport = formatSupport(video.map { it.mimeType }.toSet() + audio.map { it.mimeType }.toSet()),
            suggestedHardwareVideoSessions = suggested,
            maxSuggestedResolution = maxSize,
            maxSuggestedFrameRate = 60,
            playbackFeatures = PlaybackFeatures(
                // Media3 renders SRT, WebVTT, TTML, PGS, DVB fully and SSA/ASS with basic styling only (15 §2.1).
                subtitles = SupportLevel.PARTIAL,
                audioTrackSelection = true,
                speeds = listOf(0.25f, 0.5f, 0.75f, 1f, 1.25f, 1.5f, 2f, 3f, 4f),
                exactSeek = true,
            ),
            // ImageDecoder covers JPG, PNG, WebP, HEIF, AVIF, BMP and animations from API 31 (15 §2.3).
            imageFeatures = ImageFeatures(staticImages = true, animatedImages = true, largeImageTiling = true),
        )
    }

    /**
     * Suggested concurrent hardware video sessions (07 §2, 15 §2.7): 1080p30 AVC streams the hardware decoders
     * cover by their performance points, capped by the declared instance count; the declared count alone when the
     * codec publishes no performance points. A hint only: [com.videokit.core.runtime.DefaultResourceBudget] lowers it
     * after failed creations, and S5 calibrates the estimate on devices.
     */
    fun suggestedVideoSessions(): Int {
        val estimates = decoders.filter { it.isHardwareAccelerated && AVC in it.supportedTypes }.mapNotNull { codec ->
            val caps = runCatching { codec.getCapabilitiesForType(AVC) }.getOrNull() ?: return@mapNotNull null
            DecoderCapacity.streams1080p30(caps.videoCapabilities?.supportedPerformancePoints, caps.maxSupportedInstances)
        }
        return estimates.maxOrNull()?.coerceIn(1, HARD_SESSION_LIMIT) ?: DEFAULT_SESSIONS
    }

    override suspend fun media(source: VideoKitMediaSource): MediaProbeResult {
        val image = source.mediaKind != MediaKind.VIDEO
        val header = ByteArray(ContainerSniffer.HEADER_BYTES)
        val read = try {
            val handle = source.sourceFactory.open(OpenPurpose.PROBE)
            try {
                readFully(handle, header)
            } finally {
                handle.close()
            }
        } catch (cancelled: CancellationException) {
            throw cancelled
        } catch (failure: Exception) {
            throw SpiException(StableErrors.fromSourceFailure(failure, ErrorStage.PROBE))
        }
        if (image) return imageProbe(source, header.copyOf(read.coerceAtLeast(0)))
        val container = ContainerSniffer.detect(header, read)
        return if (container == null) {
            MediaProbeResult(
                mediaToken = source.mediaToken,
                playable = SupportLevel.UNSUPPORTED,
                editable = SupportLevel.UNSUPPORTED,
                error = StableErrors.of(ErrorCode.UNSUPPORTED_CONTAINER, ErrorStage.PROBE, "PROBE:UNKNOWN_CONTAINER"),
            )
        } else {
            // Editing is not available before VK-M4; m2ts plays through the adapter pending S2 (15 §2.2).
            MediaProbeResult(
                mediaToken = source.mediaToken,
                playable = if (container == "m2ts") SupportLevel.PARTIAL else SupportLevel.SUPPORTED,
                editable = SupportLevel.UNSUPPORTED,
            )
        }
    }

    /** Images (06 §6.1): the format from the header; decoding problems show when the image is bound. */
    private fun imageProbe(source: VideoKitMediaSource, header: ByteArray): MediaProbeResult {
        val format = ImageFormats.sniff(header)
        return MediaProbeResult(
            mediaToken = source.mediaToken,
            playable = if (format != null) SupportLevel.SUPPORTED else SupportLevel.UNSUPPORTED,
            editable = SupportLevel.UNSUPPORTED,
            error = if (format == null) StableErrors.of(ErrorCode.UNSUPPORTED_CONTAINER, ErrorStage.PROBE, "PROBE:UNKNOWN_IMAGE") else null,
        )
    }

    private fun formatSupport(mimeTypes: Set<String>): List<FormatSupport> {
        val containers = CONTAINERS.map { container ->
            FormatSupport(
                container = container,
                level = if (container == "m2ts") SupportLevel.PARTIAL else SupportLevel.SUPPORTED,
            )
        }
        val codecs = (VIDEO_CODECS + AUDIO_CODECS).map { mime ->
            val present = mime in mimeTypes
            FormatSupport(
                container = ANY_CONTAINER,
                videoCodec = mime.takeIf { it.startsWith("video/") },
                audioCodec = mime.takeIf { it.startsWith("audio/") },
                level = if (present) SupportLevel.SUPPORTED else SupportLevel.UNSUPPORTED,
                reason = if (present) null else UnsupportedReason.DEVICE_CAPABILITY,
            )
        }
        return containers + codecs
    }

    private suspend fun readFully(handle: VideoKitReadHandle, target: ByteArray): Int {
        var total = 0
        while (total < target.size) {
            val read = handle.readAt(total.toLong(), target, total, target.size - total)
            if (read <= 0) break
            total += read
        }
        return total
    }

    private companion object {
        const val AVC = "video/avc"
        const val DEFAULT_SESSIONS = 4
        const val HARD_SESSION_LIMIT = 12
        const val ANY_CONTAINER = "*"
        val CONTAINERS = listOf("mp4", "m4v", "mov", "mkv", "webm", "avi", "ts", "m2ts")
        val VIDEO_CODECS = listOf(
            "video/avc", "video/hevc", "video/x-vnd.on2.vp8", "video/x-vnd.on2.vp9", "video/av01",
            "video/mp4v-es", "video/3gpp", "video/mpeg2", "video/wvc1",
        )
        val AUDIO_CODECS = listOf(
            "audio/mp4a-latm", "audio/mpeg", "audio/opus", "audio/vorbis", "audio/flac", "audio/raw",
            "audio/ac3", "audio/eac3", "audio/vnd.dts", "audio/true-hd",
        )
    }
}
