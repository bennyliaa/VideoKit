package com.videokit.playback

import com.videokit.testkit.spec.StateMachineVector
import com.videokit.testkit.spec.StateMachineVectors
import com.videokit.testkit.spec.VectorOutcome
import kotlinx.coroutines.test.runTest
import org.junit.Assume.assumeTrue
import org.junit.Test
import org.junit.runner.RunWith
import org.junit.runners.Parameterized
import java.io.File
import kotlin.time.Duration.Companion.seconds

/**
 * Runs every session vector of `spec/vectors/state-machine/` against the real runtime (02 §4.0.2). Image vectors
 * are skipped until VK-M2 (reported as skipped); every video vector must pass.
 */
@RunWith(Parameterized::class)
class PlaybackSpecVectorsTest(private val vector: StateMachineVector) {
    @Test
    fun vector() = runTest(timeout = 60.seconds) {
        val outcome = StateMachineVectors.runSession(vector, PlaybackContractSubject(backgroundScope))
        assumeTrue("not applicable yet (images, VK-M2): ${vector.id}", outcome != VectorOutcome.SKIPPED)
        org.junit.Assert.assertEquals(VectorOutcome.PASSED, outcome)
    }

    companion object {
        private val specDir = File(System.getProperty("videokit.specDir") ?: error("system property videokit.specDir is not set"))

        @JvmStatic
        @Parameterized.Parameters(name = "{0}")
        fun cases(): List<Array<Any>> = StateMachineVectors
            .parse(File(specDir, "vectors/state-machine/session.json").readText(Charsets.UTF_8), StateMachineVectors.SESSION_KIND)
            .map { arrayOf<Any>(it) }
    }
}
