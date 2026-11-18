package com.videokit.spike.s6

import java.io.File

/** Metrics of one scenario run (S6 brief §2, §3). */
data class Metrics(
    val frames: Int,
    /** Times the confident track (TRACKED / LOW_CONFIDENCE) started following another person (09 §5 ID switch). */
    val idSwitches: Int,
    /** Confident frames on another person: the mask would sit on the wrong person. */
    val wrongFrames: Int,
    /** Frames that should be marked: the target is not detectable, or the decision is on another person. */
    val shouldMark: Int,
    /** Of [shouldMark]: frames on another person that were not marked AMBIGUOUS / LOST (the dangerous misses). */
    val missedWrong: Int,
    /** Of [shouldMark]: frames not marked AMBIGUOUS / LOST at all (LOW_CONFIDENCE coasting counts as not marked). */
    val missedStrict: Int,
    /** Frames where the target was detected but the state was AMBIGUOUS / LOST (cost: the user has to confirm). */
    val overMarked: Int,
    val targetVisible: Int,
) {
    operator fun plus(o: Metrics) = Metrics(
        frames + o.frames, idSwitches + o.idSwitches, wrongFrames + o.wrongFrames, shouldMark + o.shouldMark,
        missedWrong + o.missedWrong, missedStrict + o.missedStrict, overMarked + o.overMarked, targetVisible + o.targetVisible,
    )
}

const val TARGET = 0

fun run(frames: List<List<Detection>>, features: Features, thresholds: Thresholds = Thresholds()): Metrics {
    val start = frames.indexOfFirst { f -> f.any { it.truthId == TARGET } }
    val associator = Associator(frames[start].first { it.truthId == TARGET }, features, thresholds)
    var switches = 0
    var wrong = 0
    var shouldMark = 0
    var missedWrong = 0
    var missedStrict = 0
    var overMarked = 0
    var visible = 0
    var onTarget = true
    for (t in start + 1 until frames.size) {
        val detections = frames[t]
        val decision = associator.next(detections)
        val present = detections.any { it.truthId == TARGET }
        if (present) visible++
        val confident = decision.state == TargetState.TRACKED || decision.state == TargetState.LOW_CONFIDENCE
        val marked = !confident
        val onWrong = decision.chosen != null && decision.chosen.truthId != TARGET
        if (confident && onWrong) {
            wrong++
            if (onTarget) switches++
            onTarget = false
        } else if (confident && decision.chosen?.truthId == TARGET) {
            onTarget = true
        }
        if (!present || onWrong) {
            shouldMark++
            if (!marked && onWrong) missedWrong++
            if (!marked) missedStrict++
        }
        if (present && marked) overMarked++
    }
    return Metrics(frames.size - start - 1, switches, wrong, shouldMark, missedWrong, missedStrict, overMarked, visible)
}

val combos = listOf(
    Features(motion = true, iou = true, face = false, torso = false, markUncertain = false),
    Features(motion = true, iou = true, face = false, torso = false),
    Features(motion = true, iou = true, face = false, torso = true),
    Features(motion = true, iou = true, face = true, torso = false),
    Features(motion = true, iou = true, face = true, torso = true),
    Features(motion = true, iou = true, face = true, torso = true, markUncertain = false),
)

/** Runs every scenario × feature combination over [seeds] seeds; prints a table and writes JSON to `args[0]`. */
fun main(args: Array<String>) {
    val seeds = (args.getOrNull(1)?.toIntOrNull() ?: 20)
    val out = File(args.getOrNull(0) ?: "build/s6_results.json")
    val rows = ArrayList<String>()
    println("scenario | features | idSwitches | wrongFrames | missedWrong/shouldMark | missedStrict/shouldMark | overMarked/visible")
    for (scenario in Simulator.scenarios) {
        for (features in combos) {
            val total = (1..seeds).map { seed -> run(Simulator.frames(scenario, seed), features) }.reduce(Metrics::plus)
            fun pct(a: Int, b: Int) = if (b == 0) "0.0" else "%.1f".format(100.0 * a / b)
            println(
                "${scenario.name} | ${features.label} | ${total.idSwitches} | ${total.wrongFrames} | " +
                    "${pct(total.missedWrong, total.shouldMark)}% | ${pct(total.missedStrict, total.shouldMark)}% | " +
                    "${pct(total.overMarked, total.targetVisible)}%",
            )
            rows += """{"scenario":"${scenario.name}","features":"${features.label}","seeds":$seeds,"frames":${total.frames},""" +
                """"idSwitches":${total.idSwitches},"wrongFrames":${total.wrongFrames},"shouldMark":${total.shouldMark},""" +
                """"missedWrong":${total.missedWrong},"missedStrict":${total.missedStrict},"overMarked":${total.overMarked},""" +
                """"targetVisible":${total.targetVisible}}"""
        }
    }
    // Re-acquisition after leaving the frame (user focus): per scenario with returns.
    println()
    println("scenario | features | returns | reacquired | median latency (frames) | wrongAttach (must be 0) | askedUser | face hidden: returns / reacquired / wrong")
    for (scenario in Simulator.scenarios) {
        for (features in combos) {
            val r = (1..seeds).map { seed -> reacquisition(Simulator.frames(scenario, seed), features) }.reduce(ReacquireStats::plus)
            if (r.returns == 0) continue
            val median = r.latencyFrames.sorted().let { if (it.isEmpty()) -1 else it[it.size / 2] }
            println(
                "${scenario.name} | ${features.label} | ${r.returns} | ${r.reacquired} | $median | ${r.wrongAttach} | ${r.askedUser} | " +
                    "${r.faceHiddenReturns} / ${r.faceHiddenReacquired} / ${r.faceHiddenWrongAttach}",
            )
            rows += """{"scenario":"${scenario.name}","features":"${features.label}","reacquire":{"returns":${r.returns},""" +
                """"reacquired":${r.reacquired},"medianLatencyFrames":$median,"wrongAttach":${r.wrongAttach},"askedUser":${r.askedUser},""" +
                """"faceHiddenReturns":${r.faceHiddenReturns},"faceHiddenReacquired":${r.faceHiddenReacquired},""" +
                """"faceHiddenWrongAttach":${r.faceHiddenWrongAttach}}}"""
        }
    }
    out.parentFile?.mkdirs()
    out.writeText(rows.joinToString(",\n", "[\n", "\n]\n"))
    println("results: ${out.absolutePath}")
}
