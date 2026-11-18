package com.videokit.spike.s6

import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertTrue

class AssociationTest {
    private val full = Features(motion = true, iou = true, face = true, torso = true)

    @Test
    fun boxGeometry() {
        val a = Box(0.0, 0.0, 10.0, 10.0)
        assertEquals(1.0, a.iou(a))
        assertEquals(0.0, a.iou(Box(20.0, 0.0, 10.0, 10.0)))
        assertTrue(cosine(floatArrayOf(1f, 0f), floatArrayOf(1f, 0f)) > 0.999)
        assertTrue(bhattacharyya(floatArrayOf(0.5f, 0.5f), floatArrayOf(0.5f, 0.5f)) > 0.999)
    }

    @Test
    fun faceKeepsTheIdentityThroughACrossing() {
        val crossing = Simulator.scenarios.first { it.name == "crossing" }
        val metrics = (1..5).map { run(Simulator.frames(crossing, it), full) }.reduce(Metrics::plus)
        assertEquals(0, metrics.idSwitches, "$metrics")
    }

    @Test
    fun clothingAloneNeverBringsTheTargetBack() {
        // exit_reenter: 1 (other colour) stands near the exit; with torso only, 0 is never re-acquired by colour.
        val scenario = Simulator.scenarios.first { it.name == "exit_reenter" }
        val torsoOnly = Features(motion = true, iou = true, face = false, torso = true)
        val metrics = (1..5).map { run(Simulator.frames(scenario, it), torsoOnly) }.reduce(Metrics::plus)
        assertEquals(0, metrics.missedWrong, "no confident frame on another person: $metrics")
    }

    @Test
    fun reentryNeverAttachesToSomeoneElse() {
        // Hard requirement (user focus): after leaving the frame the track never lands on another person.
        listOf("exit_reenter", "exit_reenter_back_turned").forEach { name ->
            val scenario = Simulator.scenarios.first { it.name == name }
            val stats = (1..5).map { reacquisition(Simulator.frames(scenario, it), full) }.reduce(ReacquireStats::plus)
            assertTrue(stats.returns > 0, "$name has returns")
            assertEquals(0, stats.wrongAttach, "$name: $stats")
        }
    }

    @Test
    fun everyScenarioRunsForEveryCombination() {
        Simulator.scenarios.forEach { scenario ->
            combos.forEach { features -> assertTrue(run(Simulator.frames(scenario, 1), features).frames > 0) }
        }
    }
}
