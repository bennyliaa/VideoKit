package com.videokit.spike.s6.video

import org.opencv.core.Core
import org.opencv.core.Mat
import org.opencv.core.Point
import org.opencv.core.Rect
import org.opencv.core.Scalar
import org.opencv.core.Size
import org.opencv.imgcodecs.Imgcodecs
import org.opencv.imgproc.Imgproc
import org.opencv.objdetect.FaceDetectorYN
import org.opencv.videoio.VideoCapture
import org.opencv.videoio.Videoio
import java.io.File
import kotlin.math.roundToInt

/**
 * S6 sample search (lead 2026-11-08, user-specified source): scans a video read-only with YuNet at [SAMPLES_PER_SECOND]
 * frames per second, counts faces per sample, and lists the intervals with 2–4 faces lasting at least [MIN_INTERVAL_S]
 * (short dropouts tolerated). For each interval it writes a contact sheet (8 frames with face boxes and times) to
 * `<out>/candidates/` and `candidates.json`; the lead picks the clips and the target person from the sheets.
 *
 * The source is only read (test_media is read-only); outputs are local test material, never committed or shared.
 *
 * Usage: `CandidateScan <video> <yunet.onnx> <out-dir>`.
 */
object CandidateScan {
    const val SAMPLES_PER_SECOND = 2.0
    const val MIN_INTERVAL_S = 10.0
    const val MIN_FACES = 2
    const val MAX_FACES = 4
    const val MAX_GAP_SAMPLES = 2

    /** 3 s at 2 samples per second. */
    const val REENTRY_MIN_SAMPLES = 6
    private const val DETECT_WIDTH = 640
    private const val SCORE = 0.8f
    private const val MIN_FACE_PX = 20.0
    private const val SHEET_FRAMES = 8
    private const val THUMB_W = 320

    data class Sample(val timeS: Double, val faces: List<Rect>)

    data class Interval(val startS: Double, val endS: Double, val samples: List<Sample>) {
        val durationS: Double get() = endS - startS
        val meanFaces: Double get() = samples.map { it.faces.size }.average()

        /** Changes of the face count: a rough indicator of people leaving and entering. */
        val countChanges: Int get() = samples.zipWithNext().count { (a, b) -> a.faces.size != b.faces.size }

        /**
         * Exit-and-return candidates (user focus): the face count drops for at least [REENTRY_MIN_SAMPLES] samples and
         * comes back to its earlier value; intervals are listed with the most of them first.
         */
        val reentries: Int get() {
            var count = 0
            var dropped = 0
            var before = samples.firstOrNull()?.faces?.size ?: 0
            for (sample in samples) {
                val n = sample.faces.size
                if (n < before) {
                    dropped++
                } else {
                    if (dropped >= REENTRY_MIN_SAMPLES) count++
                    dropped = 0
                    before = n
                }
            }
            return count
        }
    }

    @JvmStatic
    fun main(args: Array<String>) {
        require(args.size >= 3) { "usage: CandidateScan <video> <yunet.onnx> <out-dir>" }
        nu.pattern.OpenCV.loadLocally()
        val video = File(args[0])
        val out = File(args[2]).apply { mkdirs() }
        val samples = scan(video, File(args[1]))
        // Exit-and-return intervals first (user focus), then the longer ones.
        val intervals = intervals(samples).sortedWith(compareByDescending<Interval> { it.reentries }.thenByDescending { it.durationS })
        val sheets = File(out, "candidates").apply { mkdirs() }
        intervals.forEachIndexed { index, interval -> contactSheet(video, interval, File(sheets, sheetName(index, interval))) }
        File(out, "candidates.json").writeText(
            intervals.mapIndexed { index, it ->
                """  {"id":${index + 1},"startS":${"%.1f".format(it.startS)},"endS":${"%.1f".format(it.endS)},""" +
                    """"durationS":${"%.1f".format(it.durationS)},"meanFaces":${"%.2f".format(it.meanFaces)},""" +
                    """"countChanges":${it.countChanges},"reentries":${it.reentries},"sheet":"candidates/${sheetName(index, it)}"}"""
            }.joinToString(",\n", "[\n", "\n]\n"),
        )
        println("${samples.size} samples, ${intervals.size} candidate intervals → ${out.absolutePath}")
    }

    private fun sheetName(index: Int, interval: Interval) =
        "cand_%02d_%s-%s.jpg".format(index + 1, clock(interval.startS).replace(":", ""), clock(interval.endS).replace(":", ""))

    /** Sequential decode (more reliable than seeking in AVI); every n-th frame is detected. */
    fun scan(video: File, model: File): List<Sample> {
        val capture = VideoCapture(video.absolutePath)
        check(capture.isOpened) { "cannot open ${video.name}" }
        val fps = capture.get(Videoio.CAP_PROP_FPS).takeIf { it > 1 } ?: 25.0
        val every = (fps / SAMPLES_PER_SECOND).roundToInt().coerceAtLeast(1)
        val detector = FaceDetectorYN.create(model.absolutePath, "", Size(DETECT_WIDTH.toDouble(), 360.0), SCORE, 0.3f, 50)
        val frame = Mat()
        val small = Mat()
        val faces = Mat()
        val samples = ArrayList<Sample>()
        var index = 0L
        try {
            while (capture.read(frame)) {
                if (index++ % every != 0L) continue
                val scale = DETECT_WIDTH.toDouble() / frame.cols()
                Imgproc.resize(frame, small, Size(DETECT_WIDTH.toDouble(), (frame.rows() * scale).roundToInt().toDouble()))
                detector.setInputSize(small.size())
                detector.detect(small, faces)
                val boxes = (0 until faces.rows()).mapNotNull { row ->
                    val w = faces.get(row, 2)[0] / scale
                    val h = faces.get(row, 3)[0] / scale
                    if (w < MIN_FACE_PX || h < MIN_FACE_PX) return@mapNotNull null
                    Rect((faces.get(row, 0)[0] / scale).toInt(), (faces.get(row, 1)[0] / scale).toInt(), w.toInt(), h.toInt())
                }
                samples += Sample((index - 1) / fps, boxes)
            }
        } finally {
            capture.release()
        }
        return samples
    }

    /** Runs of samples with MIN_FACES..MAX_FACES faces, gaps of up to [MAX_GAP_SAMPLES] samples bridged. */
    fun intervals(samples: List<Sample>): List<Interval> {
        val result = ArrayList<Interval>()
        var start = -1
        var gap = 0
        for (i in samples.indices) {
            val ok = samples[i].faces.size in MIN_FACES..MAX_FACES
            when {
                ok && start < 0 -> {
                    start = i
                    gap = 0
                }
                ok -> gap = 0
                start >= 0 && ++gap > MAX_GAP_SAMPLES -> {
                    add(result, samples, start, i - gap)
                    start = -1
                }
            }
        }
        if (start >= 0) add(result, samples, start, samples.lastIndex - gap)
        return result
    }

    private fun add(result: MutableList<Interval>, samples: List<Sample>, from: Int, to: Int) {
        if (to <= from) return
        val interval = Interval(samples[from].timeS, samples[to].timeS, samples.subList(from, to + 1))
        if (interval.durationS >= MIN_INTERVAL_S) result += interval
    }

    /** 8 evenly spaced frames of [interval] with face boxes, numbered and timed, in a 4×2 grid. */
    private fun contactSheet(video: File, interval: Interval, out: File) {
        val capture = VideoCapture(video.absolutePath)
        try {
            val thumbs = (0 until SHEET_FRAMES).map { k ->
                val sample = interval.samples[(interval.samples.size - 1) * k / (SHEET_FRAMES - 1)]
                capture.set(Videoio.CAP_PROP_POS_MSEC, sample.timeS * 1000)
                val frame = Mat()
                if (!capture.read(frame)) frame.create(360, 640, org.opencv.core.CvType.CV_8UC3)
                sample.faces.forEachIndexed { n, face ->
                    Imgproc.rectangle(frame, face, Scalar(0.0, 255.0, 0.0), 3)
                    Imgproc.putText(frame, "${n + 1}", Point(face.x.toDouble(), face.y - 8.0), Imgproc.FONT_HERSHEY_SIMPLEX, 1.2, Scalar(0.0, 255.0, 0.0), 3)
                }
                Imgproc.putText(frame, clock(sample.timeS), Point(16.0, 48.0), Imgproc.FONT_HERSHEY_SIMPLEX, 1.4, Scalar(0.0, 255.0, 255.0), 3)
                val thumb = Mat()
                Imgproc.resize(frame, thumb, Size(THUMB_W.toDouble(), (frame.rows() * THUMB_W.toDouble() / frame.cols()).roundToInt().toDouble()))
                thumb
            }
            val rows = thumbs.chunked(SHEET_FRAMES / 2).map { row -> Mat().also { Core.hconcat(row, it) } }
            val sheet = Mat().also { Core.vconcat(rows, it) }
            Imgcodecs.imwrite(out.absolutePath, sheet)
        } finally {
            capture.release()
        }
    }

    fun clock(seconds: Double): String {
        val s = seconds.toInt()
        return "%02d:%02d:%02d".format(s / 3600, s / 60 % 60, s % 60)
    }
}
