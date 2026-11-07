package com.videokit.testkit.spec

import com.videokit.api.DegradeSuggestion
import com.videokit.api.ReservationResult
import com.videokit.api.ResourceEstimate
import com.videokit.api.ResourceKind
import com.videokit.api.ResourceLease
import com.videokit.api.ResourcePriority
import com.videokit.api.ResourceRequest
import com.videokit.core.runtime.DefaultResourceBudget
import com.videokit.core.runtime.ResourcePressure
import com.videokit.testkit.internal.MiniJson

/** One case of `spec/vectors/multi-instance/resource-budget.json`. */
public class BudgetVector internal constructor(
    /** Case id. */
    public val id: String,
    internal val videoDecoders: Int,
    internal val imageMemoryBytes: Long,
    internal val steps: List<Map<*, *>>,
) {
    override fun toString(): String = id
}

/**
 * Runner of the resource budget vectors (07 §2–§3) against [DefaultResourceBudget]; other platforms run the same
 * file against their budget. A failed expectation throws [IllegalStateException] naming the case and step.
 */
public object BudgetVectors {
    /** Expected `kind` of the file. */
    public const val KIND: String = "resource-budget"

    /** Parses a vector file. */
    public fun parse(json: String): List<BudgetVector> {
        val root = MiniJson.parse(json) as? Map<*, *> ?: throw IllegalArgumentException("vector file is not an object")
        require(root["kind"] == KIND) { "unexpected kind ${root["kind"]}" }
        return (root["cases"] as List<*>).map { raw ->
            val case = raw as Map<*, *>
            BudgetVector(
                id = case["id"] as String,
                videoDecoders = (case["videoDecoders"] as Number).toInt(),
                imageMemoryBytes = (case["imageMemoryBytes"] as Number).toLong(),
                steps = (case["steps"] as List<*>).map { it as Map<*, *> },
            )
        }
    }

    /** Runs [vector]. */
    public suspend fun run(vector: BudgetVector) {
        val budget = DefaultResourceBudget.forDevice(vector.videoDecoders, vector.imageMemoryBytes)
        val leases = mutableMapOf<String, ResourceLease>()
        vector.steps.forEachIndexed { index, step ->
            val where = "${vector.id} step $index (${step["op"]})"
            when (val op = step["op"]) {
                "reserve" -> {
                    val request = ResourceRequest(
                        sessionId = step["session"] as String,
                        kind = ResourceKind.valueOf(step["kind"] as String),
                        estimate = ResourceEstimate(bytes = (step["bytes"] as Number?)?.toLong()),
                        priority = (step["priority"] as String?)?.let(ResourcePriority::valueOf) ?: ResourcePriority.VISIBLE,
                    )
                    val result = budget.reserve(request)
                    check((result is ReservationResult.Granted) == step["granted"]) {
                        "$where: expected granted=${step["granted"]}, got $result"
                    }
                    when (result) {
                        is ReservationResult.Granted -> leases[step["id"] as String] = result.lease

                        is ReservationResult.Denied -> (step["suggestion"] as String?)?.let { expected ->
                            check(result.suggestion == DegradeSuggestion.valueOf(expected)) { "$where: suggestion ${result.suggestion}" }
                        }
                    }
                }

                "release" -> leases[step["id"] as String]?.close() ?: error("$where: unknown lease ${step["id"]}")

                "creationFailed" -> budget.onCreationFailed(ResourceKind.valueOf(step["kind"] as String))

                "pressure" -> budget.setPressure(ResourcePressure.valueOf(step["level"] as String))

                else -> error("$where: unknown op $op")
            }
            (step["expectLimit"] as Number?)?.let { expected ->
                val actual = budget.effectiveLimit(ResourceKind.VIDEO_DECODER)
                check(actual == expected.toInt()) { "$where: limit $actual, expected $expected" }
            }
            (step["expectHeld"] as Map<*, *>?)?.forEach { (kind, held) ->
                val usage = budget.snapshot().usages.single { it.kind == ResourceKind.valueOf(kind as String) }
                check(usage.held == (held as Number).toInt()) { "$where: held $kind ${usage.held}, expected $held" }
            }
        }
    }
}
