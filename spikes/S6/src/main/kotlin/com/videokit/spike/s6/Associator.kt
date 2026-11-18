package com.videokit.spike.s6

/** Which association features are used (S6 brief: compare the combinations). */
data class Features(val motion: Boolean, val iou: Boolean, val face: Boolean, val torso: Boolean, val markUncertain: Boolean = true) {
    val label: String
        get() = buildList {
            if (motion) add("motion")
            if (iou) add("iou")
            if (face) add("face")
            if (torso) add("torso")
        }.joinToString("+") + if (markUncertain) "" else " (no marking)"
}

/** Thresholds of the association policy; the values S6 has to freeze (09 §7). */
data class Thresholds(
    /** Motion gate in standard deviations of the Kalman prediction. */
    val gate: Double = 4.0,
    /** Face similarity (cosine) that confirms the identity. */
    val faceAccept: Double = 0.45,
    /** Face similarity below which a candidate is another person. */
    val faceReject: Double = 0.25,
    /** Required lead of the best face over the second best. */
    val faceMargin: Double = 0.10,
    /** Required lead of the best combined score over the second best when no face is visible. */
    val scoreMargin: Double = 0.20,
    /** Candidates overlapping each other above this IoU are a crossing: no face, no decision. */
    val crossingIou: Double = 0.15,
    /** Frames the target may be predicted without a detection before it is LOST. */
    val coastFrames: Int = 15,
    /** Frames without a face after which torso/motion alone no longer keep TRACKED (LOW_CONFIDENCE then). */
    val faceStaleFrames: Int = 30,
)

/**
 * Keeps the identity of one selected person (S6, 09 §3). Principle: when the evidence does not single out the target,
 * the state becomes AMBIGUOUS or LOST and the mask is not moved to another person; identity is never switched silently.
 *
 * - motion: Kalman prediction and gating; iou: overlap with the prediction; face: cosine similarity to the target's
 *   face gallery (only when a face is visible); torso: clothing colour histogram similarity, auxiliary only: it never
 *   confirms the identity on its own (it can keep a continuous track as LOW_CONFIDENCE, and it can break ties).
 * - After LOST (left the frame, long occlusion) the target is re-acquired only by a face match.
 */
class Associator(selected: Detection, private val features: Features, private val t: Thresholds = Thresholds()) {
    private val kalman = Kalman(selected.box)
    private var faceGallery: FloatArray? = selected.face?.copyOf()
    private var torsoRef: FloatArray? = selected.torso?.copyOf()
    private var lost = false
    private var framesSinceFace = if (selected.face != null) 0 else Int.MAX_VALUE / 2

    private data class Scored(val d: Detection, val score: Double, val face: Double?, val torso: Double?, val dist: Double)

    fun next(detections: List<Detection>): FrameDecision {
        val predicted = kalman.predict()
        framesSinceFace++
        val scored = detections.map { score(it, predicted) }
        return if (lost) reacquire(scored) else track(scored)
    }

    private fun score(d: Detection, predicted: Box): Scored {
        val dist = kalman.distance(d.box)
        val face = if (features.face && d.face != null) faceGallery?.let { cosine(it, d.face) } else null
        val torso = if (features.torso && d.torso != null) torsoRef?.let { bhattacharyya(it, d.torso) } else null
        var sum = 0.0
        var weights = 0.0
        if (features.motion) {
            sum += 1.0 / (1.0 + dist)
            weights += 1.0
        }
        if (features.iou) {
            sum += d.box.iou(predicted)
            weights += 1.0
        }
        if (face != null) {
            sum += 2.0 * face.coerceAtLeast(0.0)
            weights += 2.0
        }
        if (torso != null) {
            sum += 0.5 * torso
            weights += 0.5
        }
        return Scored(d, if (weights == 0.0) 0.0 else sum / weights, face, torso, dist)
    }

    private fun track(all: List<Scored>): FrameDecision {
        // Motion gate; the face can veto a candidate (it is someone else) but torso cannot.
        val gated = all.filter { !features.motion || it.dist <= t.gate || kalman.coasting > 1 && it.dist <= t.gate * 2 }
            .filter { it.face == null || it.face >= t.faceReject }
            .sortedByDescending { it.score }
        if (gated.isEmpty()) return coast()
        val best = gated.first()
        val second = gated.getOrNull(1)
        if (!features.markUncertain) return accept(best, TargetState.TRACKED)
        if (best.face != null && best.face >= t.faceAccept) {
            // A visible face decides, unless another visible face is about as similar.
            val rival = gated.drop(1).firstOrNull { it.face != null }
            if (rival != null && best.face - rival.face!! < t.faceMargin) return ambiguous(best)
            return accept(best, TargetState.TRACKED)
        }
        // No confirming face: crossings and close calls are not decided by motion and clothing.
        val crossing = second != null && best.d.box.iou(second.d.box) > t.crossingIou
        val closeCall = second != null && best.score - second.score < t.scoreMargin
        if (crossing || closeCall) return ambiguous(best)
        val state = if (framesSinceFace <= t.faceStaleFrames && features.face) TargetState.TRACKED else TargetState.LOW_CONFIDENCE
        return accept(best, state)
    }

    private fun reacquire(all: List<Scored>): FrameDecision {
        if (!features.markUncertain) return all.maxByOrNull { it.score }?.let { accept(it, TargetState.TRACKED, reset = true) } ?: lostNow()
        // Only a face brings the target back (clothing alone never decides identity).
        val faces = all.filter { it.face != null }.sortedByDescending { it.face }
        val best = faces.firstOrNull()
        if (best != null && best.face!! >= t.faceAccept && (faces.getOrNull(1)?.face?.let { best.face - it >= t.faceMargin } != false)) {
            return accept(best, TargetState.TRACKED, reset = true)
        }
        // A strong clothing match is a proposal for the user, not a decision.
        val proposal = all.filter { it.torso != null && it.torso > 0.9 }.maxByOrNull { it.torso!! }
        return if (proposal != null) FrameDecision(TargetState.AMBIGUOUS, proposal.d) else lostNow()
    }

    private fun accept(s: Scored, state: TargetState, reset: Boolean = false): FrameDecision {
        if (reset) {
            lost = false
        }
        kalman.update(s.d.box)
        if (s.face != null && state == TargetState.TRACKED) {
            framesSinceFace = 0
            val gallery = faceGallery
            faceGallery = if (gallery == null) s.d.face!!.copyOf() else FloatArray(gallery.size) { 0.9f * gallery[it] + 0.1f * s.d.face!![it] }
        }
        if (s.d.torso != null && state == TargetState.TRACKED) {
            val ref = torsoRef
            torsoRef = if (ref == null) s.d.torso.copyOf() else FloatArray(ref.size) { 0.95f * ref[it] + 0.05f * s.d.torso[it] }
        }
        return FrameDecision(state, s.d)
    }

    private fun ambiguous(best: Scored): FrameDecision = FrameDecision(TargetState.AMBIGUOUS, best.d)

    private fun coast(): FrameDecision = if (kalman.coasting <= t.coastFrames) FrameDecision(TargetState.LOW_CONFIDENCE, null) else lostNow()

    private fun lostNow(): FrameDecision {
        lost = true
        return FrameDecision(TargetState.LOST, null)
    }
}
