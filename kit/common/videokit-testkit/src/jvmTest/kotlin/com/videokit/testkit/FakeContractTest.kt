package com.videokit.testkit

import com.videokit.testkit.contract.ContractCase
import com.videokit.testkit.contract.FakeContractSubject
import com.videokit.testkit.contract.VideoKitContractSuite
import kotlinx.coroutines.test.runTest
import org.junit.Test
import org.junit.runner.RunWith
import org.junit.runners.Parameterized
import kotlin.time.Duration.Companion.seconds

/** Runs every [VideoKitContractSuite] case against the Kotlin Fake on virtual time (04 §11). */
@RunWith(Parameterized::class)
class FakeContractTest(private val case: ContractCase) {
    @Test
    fun contract() = runTest(timeout = 60.seconds) {
        VideoKitContractSuite.run(case, FakeContractSubject(backgroundScope), backgroundScope)
    }

    companion object {
        @JvmStatic
        @Parameterized.Parameters(name = "{0}")
        fun cases(): List<Array<Any>> = VideoKitContractSuite.cases.map { arrayOf<Any>(it) }
    }
}
