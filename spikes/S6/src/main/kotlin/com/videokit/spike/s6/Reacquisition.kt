package com.videokit.spike.s6

/**
 * Re-acquisition after the target left the frame or was hidden (user focus, lead 2026-11-08): per return of the
 * target, whether the track ends up on the same person again, how long that takes, whether it ever attached to someone
 * else (must be 0), and whether it waited marked LOST / AMBIGUOUS for the user instead. Returns with the face hidden
 * (turned away) are counted separately.
 *
 * A return starts at the first frame the target is detected again after at least [MIN_ABSENCE] frames without it, and
 * ends before its next absence or at the end of the clip.
 */
data class ReacquireStats(
    val returns: Int,
    val reacquired: Int,
    /** Frames from the return to the first confident frame on the target, per reacquired return. */
    val latencyFrames: List<Int>,
    /** Returns during which a confident frame was on another person (hard requirement: 0). */
    val wrongAttach: Int,
    /** Returns that were marked LOST / AMBIGUOUS (asking the user) for at least one frame before any decision. */
    val askedUser: Int,
    val faceHiddenReturns: Int,
    val faceHiddenReacquired: Int,
    val faceHiddenWrongAttach: Int,
) {
    operator fun plus(o: ReacquireStats) = ReacquireStats(
        returns + o.returns, reacquired + o.reacquired, latencyFrames + o.latencyFrames, wrongAttach + o.wrongAttach,
        askedUser + o.askedUser, faceHiddenReturns + o.faceHiddenReturns, faceHiddenReacquired + o.faceHiddenReacquired,
        faceHiddenWrongAttach + o.faceHiddenWrongAttach,
    )

    companion object {
        const val MIN_ABSENCE = 15
        val EMPTY = ReacquireStats(0, 0, emptyList(), 0, 0, 0, 0, 0)
    }
}

/** Runs the association over [frames] and evaluates every return of the target. */
fun reacquisition(frames: List<List<Detection>>, features: Features, thresholds: Thresholds = Thresholds()): ReacquireStats {
    val start = frames.indexOfFirst { f -> f.any { it.truthId == TARGET } }
    val associator = Associator(frames[start].first { it.truthId == TARGET }, features, thresholds)
    data class Frame(val present: Boolean, val faceVisible: Boolean, val decision: FrameDecision)
    val trace = (start + 1 until frames.size).map { t ->
        val target = frames[t].firstOrNull { it.truthId == TARGET }
        Frame(target != null, target?.face != null, associator.next(frames[t]))
    }
    var stats = ReacquireStats.EMPTY
    var absent = 0
    var t = 0
    while (t < trace.size) {
        if (!trace[t].present) {
            absent++
            t++
            continue
        }
        if (absent < ReacquireStats.MIN_ABSENCE) {
            absent = 0
            t++
            continue
        }
        // A return at t: follow it until the target is gone again (MIN_ABSENCE frames) or the clip ends.
        absent = 0
        val faceHidden = !trace[t].faceVisible
        var end = t
        var gone = 0
        while (end < trace.size && gone < ReacquireStats.MIN_ABSENCE) {
            gone = if (trace[end].present) 0 else gone + 1
            end++
        }
        val window = trace.subList(t, end)
        fun confident(f: Frame) = f.decision.state == TargetState.TRACKED || f.decision.state == TargetState.LOW_CONFIDENCE
        val firstOnTarget = window.indexOfFirst { confident(it) && it.decision.chosen?.truthId == TARGET }
        val wrong = window.any { confident(it) && it.decision.chosen != null && it.decision.chosen.truthId != TARGET }
        val decisionAt = window.indexOfFirst { confident(it) }.let { if (it < 0) window.size else it }
        val asked = window.take(decisionAt).any { it.decision.state == TargetState.LOST || it.decision.state == TargetState.AMBIGUOUS }
        val ok = firstOnTarget >= 0
        stats += ReacquireStats(
            returns = 1,
            reacquired = if (ok) 1 else 0,
            latencyFrames = if (ok) listOf(firstOnTarget) else emptyList(),
            wrongAttach = if (wrong) 1 else 0,
            askedUser = if (asked) 1 else 0,
            faceHiddenReturns = if (faceHidden) 1 else 0,
            faceHiddenReacquired = if (faceHidden && ok) 1 else 0,
            faceHiddenWrongAttach = if (faceHidden && wrong) 1 else 0,
        )
        t = end
    }
    return stats
}
