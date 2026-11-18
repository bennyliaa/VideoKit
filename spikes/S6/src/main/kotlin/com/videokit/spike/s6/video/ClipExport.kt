package com.videokit.spike.s6.video

import org.opencv.core.Mat
import org.opencv.core.Size
import org.opencv.videoio.VideoCapture
import org.opencv.videoio.VideoWriter
import org.opencv.videoio.Videoio
import java.io.File
import java.security.MessageDigest

/**
 * Exports one test clip (re-encoded, at most 60 s) from a read-only source video and appends it to
 * `<out>/MANIFEST.md`: source file, start and end, the target person, SHA-256 of the clip. Local test material only
 * (the documentary is copyrighted): never committed or shared.
 *
 * Usage: `ClipExport <video> <out-dir> <name> <startS> <endS> "<target description>"`.
 */
object ClipExport {
    const val MAX_SECONDS = 60.0

    @JvmStatic
    fun main(args: Array<String>) {
        require(args.size >= 6) { "usage: ClipExport <video> <out-dir> <name> <startS> <endS> <target>" }
        nu.pattern.OpenCV.loadLocally()
        val source = File(args[0])
        val out = File(args[1]).apply { mkdirs() }
        val start = args[3].toDouble()
        val end = args[4].toDouble()
        require(end > start && end - start <= MAX_SECONDS) { "clip must be 0-$MAX_SECONDS s" }
        val clip = File(out, "${args[2]}.mp4")
        val frames = export(source, clip, start, end)
        val manifest = File(out, "MANIFEST.md")
        if (!manifest.exists()) {
            manifest.writeText(
                "# S6 multi-person test clips\n\n" +
                    "Local test material for S6 (identity keeping); cut from a copyrighted documentary: never committed or shared.\n\n" +
                    "| Clip | Source | Start | End | Frames | Target person | SHA-256 |\n| --- | --- | --- | --- | --- | --- | --- |\n",
            )
        }
        manifest.appendText(
            "| ${clip.name} | ${source.name} | ${CandidateScan.clock(start)} | ${CandidateScan.clock(end)} | $frames | ${args[5]} | ${sha256(clip)} |\n",
        )
        println("${clip.absolutePath}: $frames frames")
    }

    fun export(source: File, clip: File, startS: Double, endS: Double): Int {
        val capture = VideoCapture(source.absolutePath)
        check(capture.isOpened) { "cannot open ${source.name}" }
        val fps = capture.get(Videoio.CAP_PROP_FPS).takeIf { it > 1 } ?: 25.0
        val size = Size(capture.get(Videoio.CAP_PROP_FRAME_WIDTH), capture.get(Videoio.CAP_PROP_FRAME_HEIGHT))
        val writer = VideoWriter(clip.absolutePath, VideoWriter.fourcc('m', 'p', '4', 'v'), fps, size)
        check(writer.isOpened) { "cannot write ${clip.name}" }
        val frame = Mat()
        var written = 0
        try {
            // Decode from the start (seeking in AVI is not frame accurate); skip to the start time.
            var index = 0L
            val first = (startS * fps).toLong()
            val last = (endS * fps).toLong()
            while (index <= last && capture.read(frame)) {
                if (index >= first) {
                    writer.write(frame)
                    written++
                }
                index++
            }
        } finally {
            writer.release()
            capture.release()
        }
        return written
    }

    private fun sha256(file: File): String {
        val digest = MessageDigest.getInstance("SHA-256")
        file.inputStream().use { input ->
            val buffer = ByteArray(1 shl 16)
            while (true) {
                val n = input.read(buffer)
                if (n < 0) break
                digest.update(buffer, 0, n)
            }
        }
        return digest.digest().joinToString("") { "%02x".format(it) }
    }
}
