package com.videokit.playback

import com.videokit.testkit.spec.FeatureGateVector
import com.videokit.testkit.spec.FeatureGateVectors
import com.videokit.testkit.spec.VectorOutcome
import kotlinx.coroutines.test.runTest
import org.junit.Assume.assumeTrue
import org.junit.Test
import org.junit.runner.RunWith
import org.junit.runners.Parameterized
import java.io.File
import kotlin.time.Duration.Companion.seconds

/**
 * Runs `spec/vectors/features/feature-gate.json` (REQ-API-10) against the real runtime. Cases that need editing are
 * skipped until the core edit project (VK-M4); every other case must pass.
 */
@RunWith(Parameterized::class)
class PlaybackFeatureGateVectorsTest(private val vector: FeatureGateVector) {
    @Test
    fun vector() = runTest(timeout = 60.seconds) {
        val outcome = FeatureGateVectors.run(vector, PlaybackContractSubject(backgroundScope))
        assumeTrue("needs editing (VK-M4): ${vector.id}", outcome != VectorOutcome.SKIPPED)
        org.junit.Assert.assertEquals(VectorOutcome.PASSED, outcome)
    }

    companion object {
        private val specDir = File(System.getProperty("videokit.specDir") ?: error("system property videokit.specDir is not set"))

        @JvmStatic
        @Parameterized.Parameters(name = "{0}")
        fun cases(): List<Array<Any>> =
            FeatureGateVectors.parse(File(specDir, "vectors/features/feature-gate.json").readText(Charsets.UTF_8)).map { arrayOf<Any>(it) }
    }
}
