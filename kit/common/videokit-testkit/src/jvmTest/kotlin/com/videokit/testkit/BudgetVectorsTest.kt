package com.videokit.testkit

import com.videokit.testkit.spec.BudgetVector
import com.videokit.testkit.spec.BudgetVectors
import kotlinx.coroutines.test.runTest
import org.junit.Test
import org.junit.runner.RunWith
import org.junit.runners.Parameterized

/** Runs `spec/vectors/multi-instance/resource-budget.json` against the default budget of videokit-core (07 §2–§3). */
@RunWith(Parameterized::class)
class BudgetVectorsTest(private val vector: BudgetVector) {
    @Test
    fun vector() = runTest { BudgetVectors.run(vector) }

    companion object {
        @JvmStatic
        @Parameterized.Parameters(name = "{0}")
        fun cases(): List<Array<Any>> =
            BudgetVectors.parse(SpecFiles.read("vectors/multi-instance/resource-budget.json")).map { arrayOf<Any>(it) }
    }
}
