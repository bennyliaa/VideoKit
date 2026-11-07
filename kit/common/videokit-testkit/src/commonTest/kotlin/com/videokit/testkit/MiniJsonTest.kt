package com.videokit.testkit

import com.videokit.testkit.internal.MiniJson
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.fail

class MiniJsonTest {
    @Test
    fun roundTrip() {
        val value = linkedMapOf(
            "s" to "a \"quoted\" \\ line\nnext\u0001",
            "l" to 9_000_000_000L,
            "d" to 0.1f,
            "b" to true,
            "n" to null,
            "list" to listOf(1L, "x", listOf<Any?>(), mapOf<String, Any?>()),
            "中文" to "值",
        )
        val text = MiniJson.write(value)
        val parsed = MiniJson.parse(text) as Map<*, *>
        assertEquals(value["s"], parsed["s"])
        assertEquals(9_000_000_000L, parsed["l"])
        assertEquals(0.1f, (parsed["d"] as Double).toFloat())
        assertEquals(true, parsed["b"])
        assertEquals(null, parsed["n"])
        assertEquals(listOf(1L, "x", emptyList<Any?>(), emptyMap<String, Any?>()), parsed["list"])
        assertEquals("值", parsed["中文"])
    }

    @Test
    fun rejectsMalformedInput() {
        listOf("{", "[1,]", "{\"a\" 1}", "tru", "\"unterminated", "{} x").forEach { text ->
            try {
                MiniJson.parse(text)
                fail("accepted $text")
            } catch (expected: IllegalArgumentException) {
                // expected
            }
        }
    }
}
