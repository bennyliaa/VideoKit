package com.videokit.export.android

import android.media.MediaExtractor
import android.media.MediaFormat
import java.io.FileDescriptor
import kotlin.math.abs

/**
 * Checks of a finished output in the main process before it is accepted (08 §6 VERIFYING, M6-B1; thresholds from
 * S4 attempt 5): a video track with the expected duration, PTS without duplicates or large gaps, and audio (when
 * present) as long as the video. The worker's DONE is never trusted on its own (15 §2.8 constraint 4).
 */
internal object OutputCheck {
    /** Duration difference to the expected clip and between audio and video. */
    const val DURATION_TOLERANCE_US = 100_000L

    /** First video PTS. */
    const val FIRST_PTS_TOLERANCE_US = 50_000L

    /** A gap above this many median frame intervals counts as dropped frames. */
    const val MAX_GAP_FRAMES = 3

    data class Result(
        val ok: Boolean,
        /** Failure code for the diagnostic, null when [ok]. */
        val failure: String?,
        val videoDurationUs: Long,
        val audioDurationUs: Long?,
        val videoFrames: Int,
        val width: Int,
        val height: Int,
        val frameRate: Float?,
    )

    fun check(fd: FileDescriptor, expectedDurationUs: Long): Result {
        val extractor = MediaExtractor()
        try {
            extractor.setDataSource(fd)
            val formats = (0 until extractor.trackCount).map { extractor.getTrackFormat(it) }
            val video = formats.indexOfFirst { it.getString(MediaFormat.KEY_MIME)?.startsWith("video/") == true }
            val audio = formats.indexOfFirst { it.getString(MediaFormat.KEY_MIME)?.startsWith("audio/") == true }
            if (video < 0) return failed("NO_VIDEO_TRACK")
            val pts = times(extractor, video).sorted()
            val videoUs = duration(formats[video]) ?: (pts.lastOrNull() ?: 0L)
            val audioUs = if (audio >= 0) duration(formats[audio]) ?: times(extractor, audio).lastOrNull() else null
            val gaps = pts.zipWithNext { a, b -> b - a }
            val frameUs = gaps.sorted().getOrNull(gaps.size / 2) ?: 0L
            val width = formats[video].intOr(MediaFormat.KEY_WIDTH)
            val height = formats[video].intOr(MediaFormat.KEY_HEIGHT)
            val rate = if (frameUs > 0) 1_000_000f / frameUs else null
            val failure = when {
                pts.isEmpty() -> "NO_VIDEO_SAMPLES"
                abs(videoUs - expectedDurationUs) > DURATION_TOLERANCE_US -> "DURATION"
                pts.first() > FIRST_PTS_TOLERANCE_US -> "FIRST_PTS"
                pts.size != pts.toSet().size -> "DUPLICATE_PTS"
                frameUs > 0 && gaps.any { it > frameUs * MAX_GAP_FRAMES } -> "PTS_GAP"
                audioUs != null && abs(audioUs - videoUs) > DURATION_TOLERANCE_US -> "AV_DURATION"
                else -> null
            }
            return Result(failure == null, failure, videoUs, audioUs, pts.size, width, height, rate)
        } catch (failure: Exception) {
            return failed("UNREADABLE:${failure.javaClass.simpleName}")
        } finally {
            extractor.release()
        }
    }

    private fun failed(code: String) = Result(false, code, -1L, null, 0, 0, 0, null)

    private fun times(extractor: MediaExtractor, track: Int): List<Long> {
        extractor.selectTrack(track)
        extractor.seekTo(0, MediaExtractor.SEEK_TO_PREVIOUS_SYNC)
        val out = ArrayList<Long>()
        while (extractor.sampleTime >= 0) {
            out += extractor.sampleTime
            extractor.advance()
        }
        extractor.unselectTrack(track)
        return out
    }

    private fun duration(format: MediaFormat): Long? =
        if (format.containsKey(MediaFormat.KEY_DURATION)) format.getLong(MediaFormat.KEY_DURATION) else null

    private fun MediaFormat.intOr(key: String): Int = if (containsKey(key)) getInteger(key) else 0
}
