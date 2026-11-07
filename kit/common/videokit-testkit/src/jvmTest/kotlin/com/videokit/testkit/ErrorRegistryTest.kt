package com.videokit.testkit

import com.videokit.api.ErrorCode
import com.videokit.api.ErrorStage
import com.videokit.api.SuggestedAction
import com.videokit.testkit.internal.Errors
import com.videokit.testkit.internal.MiniJson
import org.junit.Assert.assertEquals
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
    fun runtimeDefaultsMatchRegistry() {
        codes.forEach { entry ->
            val code = ErrorCode.valueOf(entry["code"] as String)
            val error = Errors.of(code, ErrorStage.valueOf(entry["stage"] as String))
            assertEquals("retryable of $code", entry["retryable"], error.retryable)
            assertEquals("suggestedAction of $code", entry["suggestedAction"], error.suggestedAction.name)
        }
    }
}
