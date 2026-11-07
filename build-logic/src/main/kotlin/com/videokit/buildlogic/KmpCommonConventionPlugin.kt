package com.videokit.buildlogic

import org.gradle.api.Plugin
import org.gradle.api.Project
import org.gradle.api.tasks.testing.Test
import org.jetbrains.kotlin.gradle.dsl.JvmTarget
import org.jetbrains.kotlin.gradle.dsl.KotlinMultiplatformExtension

/**
 * Platform independent modules under `kit/common/` (02 §4.0, 13 §3.2): Kotlin Multiplatform with all code in
 * `commonMain`; V1.0 only enables the `jvm()` target. Because only `commonMain` is compiled for `jvm()`,
 * `java.*`, `javax.*` and `android.*` APIs are not available to the code at compile time.
 *
 * Also: Kotlin explicit API mode, warnings as errors, JVM bytecode 11, dependency locking and the Binary
 * Compatibility Validator (`apiDump` / `apiCheck`, dump in `<module>/api/<module>.api`).
 */
class KmpCommonConventionPlugin : Plugin<Project> {
    override fun apply(target: Project) {
        with(target) {
            pluginManager.apply("org.jetbrains.kotlin.multiplatform")
            pluginManager.apply("org.jetbrains.kotlinx.binary-compatibility-validator")

            extensions.configure(KotlinMultiplatformExtension::class.java) {
                explicitApi()
                jvm {
                    compilerOptions {
                        jvmTarget.set(JvmTarget.JVM_11)
                    }
                }
                compilerOptions {
                    allWarningsAsErrors.set(true)
                }
            }

            // Tests may read the language independent spec assets (spec/vectors, spec/errors.json).
            val specDir = rootProject.layout.projectDirectory.dir("spec")
            tasks.withType(Test::class.java).configureEach {
                inputs.dir(specDir).withPropertyName("videokitSpec").optional()
                systemProperty("videokit.specDir", specDir.asFile.absolutePath)
            }

            // Only commonMain is checked: it is the product code. Test glue in jvmTest may use JVM APIs (JUnit, files).
            val portability = tasks.register("checkCommonPortability", CommonPortabilityCheckTask::class.java) {
                group = "verification"
                description = "Fails when commonMain uses java.*, javax.*, android.* or JVM-only Kotlin APIs (13 §3.2)."
                sources.from(fileTree("src/commonMain") { include("**/*.kt") })
                report.set(layout.buildDirectory.file("reports/portability/commonMain.txt"))
            }
            tasks.named("check").configure { dependsOn(portability) }

            dependencyLocking {
                lockAllConfigurations()
            }
        }
    }
}
