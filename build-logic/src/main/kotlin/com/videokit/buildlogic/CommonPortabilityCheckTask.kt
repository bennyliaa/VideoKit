package com.videokit.buildlogic

import org.gradle.api.DefaultTask
import org.gradle.api.GradleException
import org.gradle.api.file.ConfigurableFileCollection
import org.gradle.api.file.RegularFileProperty
import org.gradle.api.tasks.InputFiles
import org.gradle.api.tasks.OutputFile
import org.gradle.api.tasks.PathSensitive
import org.gradle.api.tasks.PathSensitivity
import org.gradle.api.tasks.TaskAction

/**
 * Portability check of `commonMain` sources (13 §3.2).
 *
 * With only the `jvm()` target enabled, the Kotlin compiler compiles `commonMain` as JVM code and the
 * metadata compilation is skipped, so `java.*` / `android.*` APIs and JVM-only standard library functions
 * would compile. This task closes that gap at source level until a second target is enabled.
 */
abstract class CommonPortabilityCheckTask : DefaultTask() {
    @get:InputFiles
    @get:PathSensitive(PathSensitivity.RELATIVE)
    abstract val sources: ConfigurableFileCollection

    @get:OutputFile
    abstract val report: RegularFileProperty

    @TaskAction
    fun check() {
        val violations = mutableListOf<String>()
        sources.files.sortedBy { it.path }.forEach { file ->
            file.readLines(Charsets.UTF_8).forEachIndexed { index, raw ->
                val code = codePart(raw) ?: return@forEachIndexed
                RULES.forEach { (regex, rule) ->
                    if (regex.containsMatchIn(code)) violations += "${file.path}:${index + 1}: $rule: ${raw.trim()}"
                }
            }
        }
        val reportFile = report.get().asFile
        reportFile.parentFile.mkdirs()
        reportFile.writeText(if (violations.isEmpty()) "OK\n" else violations.joinToString("\n", postfix = "\n"), Charsets.UTF_8)
        if (violations.isNotEmpty()) {
            throw GradleException("Platform specific API in commonMain (13 §3.2):\n" + violations.joinToString("\n") { "  - $it" })
        }
    }

    /** The code part of a line: comment lines are skipped, trailing `//` comments and string contents are removed. */
    private fun codePart(line: String): String? {
        val trimmed = line.trimStart()
        if (trimmed.startsWith("*") || trimmed.startsWith("/*") || trimmed.startsWith("//")) return null
        val withoutStrings = line.replace(STRING_LITERAL, "\"\"")
        return withoutStrings.substringBefore("//")
    }

    private companion object {
        val STRING_LITERAL = Regex("\"(?:[^\"\\\\]|\\\\.)*\"")
        val RULES: List<Pair<Regex, String>> = listOf(
            Regex("(^|[^\\w.])(java|javax|android|androidx|sun|dalvik)\\.[a-zA-Z]") to "platform package",
            Regex("(^|[^\\w.])synchronized\\s*\\(") to "JVM-only synchronized()",
            Regex("@Synchronized\\b") to "JVM-only @Synchronized",
            Regex("\\.javaClass\\b|::class\\.java\\b") to "JVM class reflection",
            Regex("(^|[^\\w.])(System|Thread|Charsets)\\.") to "JVM-only API",
            Regex("String\\.format\\(") to "JVM-only String.format (and locale dependent)",
        )
    }
}
