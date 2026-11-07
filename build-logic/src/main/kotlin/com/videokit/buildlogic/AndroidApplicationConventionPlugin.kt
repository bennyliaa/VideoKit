package com.videokit.buildlogic

import com.android.build.api.dsl.ApplicationExtension
import org.gradle.api.JavaVersion
import org.gradle.api.Plugin
import org.gradle.api.Project
import org.jetbrains.kotlin.gradle.dsl.JvmTarget
import org.jetbrains.kotlin.gradle.dsl.KotlinAndroidProjectExtension

/**
 * Common configuration of VideoKit Android sample apps (`sample-host`, 13 §1): the same SDK levels, Java/Kotlin
 * target, lint strictness and dependency locking as the library modules; no explicit API mode and no ABI dump
 * (apps have no public API). The app sets its own namespace and application id.
 */
class AndroidApplicationConventionPlugin : Plugin<Project> {
    override fun apply(target: Project) {
        with(target) {
            pluginManager.apply("com.android.application")
            pluginManager.apply("org.jetbrains.kotlin.android")

            val catalog = libs
            val compileSdkMajor = catalog.intVersionOf("androidCompileSdk")
            val compileSdkMinor = catalog.intVersionOf("androidCompileSdkMinor")
            val targetSdkLevel = catalog.intVersionOf("androidTargetSdk")
            val minSdkLevel = catalog.intVersionOf("androidMinSdk")

            extensions.configure(ApplicationExtension::class.java) {
                compileSdk {
                    version = release(compileSdkMajor) {
                        minorApiLevel = compileSdkMinor
                    }
                }
                defaultConfig {
                    minSdk = minSdkLevel
                    targetSdk = targetSdkLevel
                }
                compileOptions {
                    sourceCompatibility = JavaVersion.VERSION_11
                    targetCompatibility = JavaVersion.VERSION_11
                }
                lint {
                    abortOnError = true
                    warningsAsErrors = true
                    checkDependencies = false
                    // Same reproducibility exclusions as the libraries (versions are pinned, 15 §1).
                    disable += setOf("AndroidGradlePluginVersion", "GradleDependency", "NewerVersionAvailable")
                }
            }

            extensions.configure(KotlinAndroidProjectExtension::class.java) {
                compilerOptions {
                    jvmTarget.set(JvmTarget.JVM_11)
                    allWarningsAsErrors.set(true)
                }
            }

            dependencyLocking {
                lockAllConfigurations()
            }
        }
    }
}
