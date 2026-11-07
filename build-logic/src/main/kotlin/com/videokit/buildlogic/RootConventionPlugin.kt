package com.videokit.buildlogic

import org.gradle.api.Plugin
import org.gradle.api.Project
import org.gradle.api.attributes.Bundling
import org.gradle.api.attributes.Category
import org.gradle.api.attributes.Usage
import org.gradle.api.tasks.JavaExec

/**
 * Root project conventions: `base` lifecycle tasks, dependency locking for the root project and the
 * ktlint static check (13 §3). ktlint runs from the root project so that its embedded Kotlin compiler is
 * resolved in an isolated configuration that the Kotlin Gradle plugin does not align to the project's
 * Kotlin version.
 */
class RootConventionPlugin : Plugin<Project> {
    override fun apply(target: Project) {
        with(target) {
            pluginManager.apply("base")
            dependencyLocking {
                lockAllConfigurations()
            }

            val ktlint = configurations.create("ktlint") {
                isCanBeConsumed = false
                isCanBeResolved = true
                description = "ktlint CLI used by ktlintCheck and ktlintFormat"
                // ktlint-cli publishes a plain and a shadowed runtime variant; use the self-contained shadowed one.
                attributes {
                    attribute(Usage.USAGE_ATTRIBUTE, objects.named(Usage::class.java, Usage.JAVA_RUNTIME))
                    attribute(Category.CATEGORY_ATTRIBUTE, objects.named(Category::class.java, Category.LIBRARY))
                    attribute(Bundling.BUNDLING_ATTRIBUTE, objects.named(Bundling::class.java, Bundling.SHADOWED))
                }
            }
            dependencies.add(ktlint.name, libs.findLibrary("ktlint-cli").get())

            val editorConfig = layout.projectDirectory.file("gradle/ktlint/ktlint.editorconfig")
            val includes = listOf(
                "kit/**/src/**/*.kt",
                "kit/**/*.gradle.kts",
                "build-logic/src/**/*.kt",
                "build-logic/*.gradle.kts",
                "*.gradle.kts",
            )
            val patterns = includes + "!**/build/**"
            val sources = fileTree(projectDir) {
                include(includes)
                exclude("**/build/**")
            }
            val reportFile = layout.buildDirectory.file("reports/ktlint/ktlint.txt")
            val editorConfigPath = editorConfig.asFile.path
            val reportPath = reportFile.get().asFile.path

            val ktlintCheck = tasks.register("ktlintCheck", JavaExec::class.java) {
                group = "verification"
                description = "Checks Kotlin sources and Gradle scripts with ktlint."
                classpath = ktlint
                mainClass.set("com.pinterest.ktlint.Main")
                workingDir = projectDir
                inputs.files(sources).withPropertyName("ktlintSources")
                inputs.file(editorConfig).withPropertyName("ktlintEditorConfig")
                outputs.file(reportFile).withPropertyName("ktlintReport")
                args(
                    listOf(
                        "--editorconfig=$editorConfigPath",
                        "--relative",
                        "--reporter=plain",
                        "--reporter=plain,output=$reportPath",
                    ) + patterns,
                )
            }
            tasks.register("ktlintFormat", JavaExec::class.java) {
                group = "formatting"
                description = "Formats Kotlin sources and Gradle scripts with ktlint."
                classpath = ktlint
                mainClass.set("com.pinterest.ktlint.Main")
                workingDir = projectDir
                args(listOf("--editorconfig=$editorConfigPath", "--relative", "--format") + patterns)
            }
            tasks.named("check").configure { dependsOn(ktlintCheck) }
        }
    }
}
