package com.videokit.spike.s7

import java.io.File
import javax.imageio.ImageIO

/**
 * Runs the model-independent parts of S7 on the synthetic set and writes `results.json` plus the images to `args[0]`:
 * 1. head range from the face box ([HeadExpansion]) against the ground-truth head box (IoU);
 * 2. host-supplied PNG path (04A E6): the opaque bounding box of the RGBA ground truth must equal the head box, and its
 *    soft-edge width is reported;
 * 3. a naive baseline matte (solid ellipse over the expanded head range) scored with [MattingMetrics], to show what
 *    the metrics penalize. Model mattes (MODNet, PP-HumanSeg, MediaPipe) are added once the weights are approved.
 */
fun main(args: Array<String>) {
    val out = File(args.getOrNull(0) ?: "build/s7").apply { mkdirs() }
    val expansion = HeadExpansion()
    val rows = ArrayList<String>()
    println("sample | headIoU | hostPngIoU | edgePx | baseline edgeMae | hairMae | bgResidue | fgLoss")
    for (sample in SyntheticSet.all()) {
        ImageIO.write(sample.image, "png", File(out, "${sample.name}.png"))
        val rgba = SyntheticSet.asRgba(sample)
        ImageIO.write(rgba, "png", File(out, "${sample.name}_truth.png"))
        val head = expansion.headOf(sample.face, SyntheticSet.W, SyntheticSet.H)
        val headIou = head.iou(sample.head)
        val reread = ImageIO.read(File(out, "${sample.name}_truth.png"))
        val hostBounds = HostPng.opaqueBounds(reread)
        val hostIou = hostBounds?.iou(sample.head) ?: 0.0
        val edge = HostPng.edgeWidth(reread)
        val baseline = ellipseMatte(head)
        val scores = MattingMetrics.score(baseline, sample.alpha, SyntheticSet.W, SyntheticSet.H, sample.hair)
        println(
            "${sample.name} | ${"%.3f".format(headIou)} | ${"%.3f".format(hostIou)} | $edge | ${"%.3f".format(scores.edgeMae)} | " +
                "${scores.hairMae?.let { "%.3f".format(it) }} | ${"%.3f".format(scores.backgroundResidue)} | ${"%.3f".format(scores.foregroundLoss)}",
        )
        rows += """{"sample":"${sample.name}","headIou":$headIou,"hostPngIou":$hostIou,"hostPngBounds":"$hostBounds","truthHead":"${sample.head}",""" +
            """"edgeWidthPx":$edge,"baseline":{"sad":${scores.sad},"mse":${scores.mse},"edgeMae":${scores.edgeMae},""" +
            """"hairMae":${scores.hairMae},"backgroundResidue":${scores.backgroundResidue},"backgroundLeak":${scores.backgroundLeak},""" +
            """"foregroundLoss":${scores.foregroundLoss}}}"""
    }
    File(out, "results.json").writeText(rows.joinToString(",\n", "[\n", "\n]\n"))
    println("results: ${File(out, "results.json").absolutePath}")
}

/** Naive matte: 1 inside the ellipse inscribed in [head], 0 outside (no soft edge, no strands). */
private fun ellipseMatte(head: Rect): FloatArray {
    val cx = head.x + head.w / 2.0
    val cy = head.y + head.h / 2.0
    return FloatArray(SyntheticSet.W * SyntheticSet.H) { i ->
        val x = i % SyntheticSet.W + 0.5
        val y = i / SyntheticSet.W + 0.5
        val dx = (x - cx) / (head.w / 2.0)
        val dy = (y - cy) / (head.h / 2.0)
        if (dx * dx + dy * dy <= 1.0) 1f else 0f
    }
}
