package com.videokit.spike.s6

import kotlin.math.exp
import kotlin.math.sqrt
import kotlin.random.Random

/**
 * Synthetic multi-person scenes for the association logic (S6 brief scenarios). Three people (id 0 is the one the user
 * selects); per frame each visible person yields a detection with box jitter, occasional misses, a face embedding only
 * while the face is visible (identity vector + noise, as SFace embeddings behave: same person cos about 0.6-0.8,
 * different people about 0), and a torso hue histogram from the clothing colour. These are not detector outputs: they
 * test the association policy and give relative numbers until real detector/feature data from samples is available.
 */
object Simulator {
    const val FRAMES = 300
    private const val EMBED = 128
    private const val BINS = 16
    private const val FACE_W = 40.0
    private const val FACE_H = 48.0

    /** What a person does in a frame. */
    data class Pose(val cx: Double, val cy: Double, val inFrame: Boolean = true, val occluded: Boolean = false, val faceVisible: Boolean = true)

    class Person(val id: Int, val hue: Int, val pose: (Int) -> Pose)

    data class Scenario(val name: String, val description: String, val people: List<Person>)

    private fun walk(t: Int, from: Double, to: Double, start: Int = 0, end: Int = FRAMES): Double {
        val k = ((t - start).toDouble() / (end - start)).coerceIn(0.0, 1.0)
        return from + (to - from) * k
    }

    val scenarios: List<Scenario> = listOf(
        Scenario(
            "crossing",
            "0 and 1 walk towards each other on the same line and cross at frame 150; faces visible; 2 stands aside",
            listOf(
                Person(0, 2) { Pose(walk(it, 80.0, 560.0), 180.0) },
                Person(1, 10) { Pose(walk(it, 560.0, 80.0), 180.0) },
                Person(2, 6) { Pose(320.0, 300.0) },
            ),
        ),
        Scenario(
            "similar_clothes",
            "as crossing, 0 and 1 wear the same colour and both look away (no face) from frame 120 to 180",
            listOf(
                Person(0, 2) { Pose(walk(it, 80.0, 560.0), 180.0, faceVisible = it !in 120..180) },
                Person(1, 2) { Pose(walk(it, 560.0, 80.0), 180.0, faceVisible = it !in 120..180) },
                Person(2, 6) { Pose(320.0, 300.0) },
            ),
        ),
        Scenario(
            "back_turned",
            "0 turns away (no face) from frame 100 to 190 while 1 walks past close by",
            listOf(
                Person(0, 2) { Pose(300.0 + 20.0 * kotlin.math.sin(it / 30.0), 180.0, faceVisible = it !in 100..190) },
                Person(1, 10) { Pose(walk(it, 600.0, 40.0, 90, 210), 190.0) },
                Person(2, 6) { Pose(520.0, 300.0) },
            ),
        ),
        Scenario(
            "exit_reenter",
            "0 leaves on the right at frame 100 and comes back from the left at frame 180; 1 stands near the exit",
            listOf(
                Person(0, 2) {
                    when {
                        it < 100 -> Pose(walk(it, 300.0, 640.0, 0, 100), 180.0)
                        it < 180 -> Pose(0.0, 0.0, inFrame = false)
                        else -> Pose(walk(it, 0.0, 250.0, 180, 300), 180.0)
                    }
                },
                Person(1, 10) { Pose(600.0, 185.0) },
                Person(2, 6) { Pose(150.0, 300.0) },
            ),
        ),
        Scenario(
            "exit_reenter_back_turned",
            "as exit_reenter, but 0 comes back facing away (no face) for 60 frames; 1, same colour, stands near the entry",
            listOf(
                Person(0, 2) {
                    when {
                        it < 100 -> Pose(walk(it, 300.0, 640.0, 0, 100), 180.0)
                        it < 180 -> Pose(0.0, 0.0, inFrame = false)
                        else -> Pose(walk(it, 0.0, 250.0, 180, 300), 180.0, faceVisible = it >= 240)
                    }
                },
                Person(1, 2) { Pose(60.0, 185.0) },
                Person(2, 6) { Pose(450.0, 300.0) },
            ),
        ),
        Scenario(
            "short_occlusion",
            "1 walks in front of 0 and hides it for 12 frames (144-155); same colour clothes",
            listOf(
                Person(0, 2) { Pose(320.0, 180.0, occluded = it in 144..155) },
                Person(1, 2) { Pose(walk(it, 600.0, 40.0, 60, 240), 182.0) },
                Person(2, 6) { Pose(120.0, 300.0) },
            ),
        ),
    )

    /** The frames of [scenario], deterministic for [seed]. */
    fun frames(scenario: Scenario, seed: Int): List<List<Detection>> {
        val random = Random(seed)
        val identities = scenario.people.associate { it.id to unit(FloatArray(EMBED) { random.nextFloat() * 2 - 1 }) }
        return (0 until FRAMES).map { t ->
            scenario.people.mapNotNull { person ->
                val pose = person.pose(t)
                if (!pose.inFrame || pose.occluded || random.nextDouble() < MISS_RATE) return@mapNotNull null
                val box = Box.centered(pose.cx + random.nextGaussian() * JITTER, pose.cy + random.nextGaussian() * JITTER, FACE_W, FACE_H)
                val face = if (pose.faceVisible) noisy(identities.getValue(person.id), random) else null
                Detection(box, face, torso(person.hue, random), person.id)
            }
        }
    }

    private fun noisy(identity: FloatArray, random: Random): FloatArray =
        unit(FloatArray(identity.size) { identity[it] + (random.nextGaussian() * FACE_NOISE).toFloat() })

    private fun torso(hue: Int, random: Random): FloatArray {
        val h = FloatArray(BINS) { bin ->
            val d = minOf((bin - hue + BINS) % BINS, (hue - bin + BINS) % BINS).toDouble()
            (exp(-d * d / 2.0) + random.nextDouble() * 0.15).toFloat()
        }
        val sum = h.sum()
        return FloatArray(BINS) { h[it] / sum }
    }

    private fun unit(v: FloatArray): FloatArray {
        val n = sqrt(v.sumOf { (it * it).toDouble() }).toFloat()
        return FloatArray(v.size) { v[it] / n }
    }

    private fun Random.nextGaussian(): Double {
        // Box-Muller.
        val u = nextDouble().coerceAtLeast(1e-12)
        val v = nextDouble()
        return sqrt(-2 * kotlin.math.ln(u)) * kotlin.math.cos(2 * Math.PI * v)
    }

    private const val JITTER = 3.0
    private const val MISS_RATE = 0.05

    /** Per-dimension noise; with 128 dims it gives a same-person cosine of about 0.6. */
    private const val FACE_NOISE = 0.11
}
