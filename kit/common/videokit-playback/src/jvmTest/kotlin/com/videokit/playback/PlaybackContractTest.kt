package com.videokit.playback

import com.videokit.testkit.contract.ContractCase
import com.videokit.testkit.contract.VideoKitContractSuite
import kotlinx.coroutines.test.runTest
import org.junit.Assume.assumeTrue
import org.junit.Test
import org.junit.runner.RunWith
import org.junit.runners.Parameterized
import kotlin.time.Duration.Companion.seconds

/**
 * Runs every [VideoKitContractSuite] case against the real runtime over the fake engines (04 §11). Cases of feature
 * areas the runtime does not implement yet (images, editing) are reported as skipped (JUnit assumption), not passed.
 */
@RunWith(Parameterized::class)
class PlaybackContractTest(private val case: ContractCase) {
    @Test
    fun contract() = runTest(timeout = 60.seconds) {
        val subject = PlaybackContractSubject(backgroundScope)
        assumeTrue("requires ${case.requires}", VideoKitContractSuite.applies(case, subject))
        VideoKitContractSuite.run(case, subject, backgroundScope)
    }

    companion object {
        @JvmStatic
        @Parameterized.Parameters(name = "{0}")
        fun cases(): List<Array<Any>> = VideoKitContractSuite.cases.map { arrayOf<Any>(it) }
    }
}
