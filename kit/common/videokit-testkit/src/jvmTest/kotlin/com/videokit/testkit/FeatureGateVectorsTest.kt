package com.videokit.testkit

import com.videokit.api.ErrorCode
import com.videokit.api.FeatureMode
import com.videokit.api.UnsupportedReason
import com.videokit.api.VideoKitFeature
import com.videokit.core.runtime.FeatureGate
import com.videokit.testkit.contract.FakeContractSubject
import com.videokit.testkit.spec.FeatureGateVector
import com.videokit.testkit.spec.FeatureGateVectors
import com.videokit.testkit.spec.VectorOutcome
import kotlinx.coroutines.test.runTest
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test
import org.junit.runner.RunWith
import org.junit.runners.Parameterized
import kotlin.time.Duration.Companion.seconds

/** Runs `spec/vectors/features/feature-gate.json` (REQ-API-10, VK-A2) against the Kotlin Fake: nothing may be skipped. */
@RunWith(Parameterized::class)
class FeatureGateVectorsTest(private val vector: FeatureGateVector) {
    @Test
    fun vector() = runTest(timeout = 60.seconds) {
        assertEquals(VectorOutcome.PASSED, FeatureGateVectors.run(vector, FakeContractSubject(backgroundScope)))
    }

    companion object {
        @JvmStatic
        @Parameterized.Parameters(name = "{0}")
        fun cases(): List<Array<Any>> =
            FeatureGateVectors.parse(SpecFiles.read("vectors/features/feature-gate.json")).map { arrayOf<Any>(it) }
    }
}

/** Registry checks of the feature types (REQ-API-10) against `spec/errors.json` and the vector file. */
class FeatureRegistryTest {
    @Test
    fun featureCodesAreRegisteredWithTheirParams() {
        val errors = SpecFiles.read("errors.json")
        for (code in listOf(ErrorCode.FEATURE_DISABLED, ErrorCode.FEATURE_DENIED)) {
            assertTrue("${code.name} not registered", errors.contains("\"code\": \"${code.name}\""))
        }
        assertTrue("feature params not registered", errors.contains("\"feature\":") && errors.contains("\"badge\":"))
    }

    @Test
    fun everyConfigurableFeatureAppearsInTheVectors() {
        val vectors = SpecFiles.read("vectors/features/feature-gate.json")
        for (feature in VideoKitFeature.CONFIGURABLE) assertTrue("$feature not covered", vectors.contains("\"${feature.name}\""))
    }

    @Test
    fun parentsAreHiddenTransitively() {
        val gate = FeatureGate(mapOf(VideoKitFeature.EDIT to FeatureMode.HIDDEN)) { _, _ -> null }
        assertEquals(setOf(VideoKitFeature.EDIT, VideoKitFeature.MASK_TRACKING, VideoKitFeature.AVATAR), gate.hiddenFeatures)
        // EXPORT and MULTI_VIEW do not depend on EDIT (user 2026-11-08).
        assertEquals(FeatureMode.ENABLED, gate.mode(VideoKitFeature.EXPORT))
        assertEquals(FeatureMode.ENABLED, gate.mode(VideoKitFeature.MULTI_VIEW))
        assertEquals(
            listOf("MULTI_VIEW", "EDIT", "MASK_TRACKING", "AVATAR", "EXPORT"),
            VideoKitFeature.CONFIGURABLE.map { it.name },
        )
        assertEquals(FeatureMode.ENABLED, gate.mode(VideoKitFeature.UNKNOWN))
    }

    @Test
    fun wireNamesFallBack() {
        assertEquals(VideoKitFeature.UNKNOWN, VideoKitFeature.fromWireName("FUTURE"))
        assertEquals(FeatureMode.ENABLED, FeatureMode.fromWireName("FUTURE"))
        assertEquals(UnsupportedReason.UNKNOWN, UnsupportedReason.fromWireName("FUTURE"))
        assertEquals(UnsupportedReason.FEATURE_DENIED, UnsupportedReason.fromWireName("FEATURE_DENIED"))
    }
}
