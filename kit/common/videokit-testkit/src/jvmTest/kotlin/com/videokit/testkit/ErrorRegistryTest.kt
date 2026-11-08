package com.videokit.testkit

import com.videokit.api.ErrorCode
import com.videokit.api.ErrorParams
import com.videokit.api.ErrorStage
import com.videokit.api.SinkErrorCode
import com.videokit.api.SuggestedAction
import com.videokit.api.VideoKitSinkException
import com.videokit.testkit.internal.Errors
import com.videokit.testkit.internal.MiniJson
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test

/** Verifies the Kotlin [ErrorCode] enum and the runtime defaults against `spec/errors.json` (02 §4.0.2). */
class ErrorRegistryTest {
    private val registry = MiniJson.parse(SpecFiles.read("errors.json")) as Map<*, *>
    private val codes = (registry["codes"] as List<*>).map { it as Map<*, *> }

    @Test
    fun enumMatchesRegistryInOrder() {
        assertEquals(1L, registry["schemaVersion"])
        assertEquals(codes.map { it["code"] }, ErrorCode.entries.map { it.name })
    }

    @Test
    fun unknownCodeFallbackMatches() {
        assertEquals(registry["unknownCodeFallback"], ErrorCode.fromWireName("NOT_IN_THE_REGISTRY").name)
    }

    @Test
    fun stagesAndSuggestionsAreKnownValues() {
        codes.forEach { entry ->
            ErrorStage.valueOf(entry["stage"] as String)
            SuggestedAction.valueOf(entry["suggestedAction"] as String)
        }
    }

    @Test
    fun registeredParamsAreKnownKeys() {
        // UI-AUDIT-A1 J8: message parameter keys of each code ("params") are the ErrorParams constants.
        val known = setOf(ErrorParams.REQUIRED_BYTES)
        val registered = codes.associate { it["code"] to ((it["params"] as? Map<*, *>)?.keys ?: emptySet<Any>()) }
        registered.values.flatten().forEach { key -> assertTrue("unknown param $key", key in known) }
        assertEquals(setOf(ErrorParams.REQUIRED_BYTES), registered["OUTPUT_SPACE_INSUFFICIENT"])
        val withBytes = Errors.spaceInsufficient(ErrorStage.SINK, 120_000_000L)
        assertEquals("120000000", withBytes.params[ErrorParams.REQUIRED_BYTES])
        // Unknown or non-positive shortfall: no parameter, the UI shows the generic text.
        assertTrue(Errors.spaceInsufficient(ErrorStage.SINK, null).params.isEmpty())
        assertTrue(Errors.spaceInsufficient(ErrorStage.SINK, 0L).params.isEmpty())
        val fromSink = Errors.fromSinkFailure(VideoKitSinkException(SinkErrorCode.SPACE_INSUFFICIENT, requiredBytes = 5L))
        assertEquals("5", fromSink.params[ErrorParams.REQUIRED_BYTES])
        // requiredBytes only applies to the space code.
        assertTrue(Errors.fromSinkFailure(VideoKitSinkException(SinkErrorCode.IO_FAILED, requiredBytes = 5L)).params.isEmpty())
    }

    @Test
    fun runtimeDefaultsMatchRegistry() {
        codes.forEach { entry ->
            val code = ErrorCode.valueOf(entry["code"] as String)
            val error = Errors.of(code, ErrorStage.valueOf(entry["stage"] as String))
            assertEquals("retryable of $code", entry["retryable"], error.retryable)
            assertEquals("suggestedAction of $code", entry["suggestedAction"], error.suggestedAction.name)
        }
    }
}
