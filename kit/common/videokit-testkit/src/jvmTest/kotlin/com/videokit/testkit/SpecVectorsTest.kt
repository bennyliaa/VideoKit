package com.videokit.testkit

import com.videokit.testkit.contract.FakeContractSubject
import com.videokit.testkit.spec.StateMachineVector
import com.videokit.testkit.spec.StateMachineVectors
import com.videokit.testkit.spec.VectorOutcome
import kotlinx.coroutines.test.runTest
import org.junit.Assert.assertEquals
import org.junit.Test
import org.junit.runner.RunWith
import org.junit.runners.Parameterized
import kotlin.time.Duration.Companion.seconds

/** Runs every case of `spec/vectors/state-machine/` against the Kotlin Fake (02 §4.0.2). */
@RunWith(Parameterized::class)
class SpecVectorsTest(private val file: String, private val vector: StateMachineVector) {
    @Test
    fun vector() = runTest(timeout = 60.seconds) {
        val subject = FakeContractSubject(backgroundScope)
        val outcome = when (file) {
            SESSION -> StateMachineVectors.runSession(vector, subject)
            else -> StateMachineVectors.runEdit(vector, subject)
        }
        // The Fake can reach every start state, so nothing may be skipped.
        assertEquals(VectorOutcome.PASSED, outcome)
    }

    companion object {
        private const val SESSION = "state-machine/session.json"
        private const val EDIT = "state-machine/edit-project.json"

        @JvmStatic
        @Parameterized.Parameters(name = "{0}: {1}")
        fun cases(): List<Array<Any>> =
            StateMachineVectors.parse(SpecFiles.read("vectors/$SESSION"), StateMachineVectors.SESSION_KIND).map { arrayOf(SESSION, it) } +
                StateMachineVectors.parse(SpecFiles.read("vectors/$EDIT"), StateMachineVectors.EDIT_KIND).map { arrayOf(EDIT, it) }
    }
}
