package com.videokit.buildlogic

import com.android.build.api.dsl.LibraryExtension
import org.gradle.api.JavaVersion
import org.gradle.api.Plugin
import org.gradle.api.Project
import org.jetbrains.kotlin.gradle.dsl.JvmTarget
import org.jetbrains.kotlin.gradle.dsl.KotlinAndroidProjectExtension

/**
 * Common configuration of every VideoKit Android library module (13 §2, §3):
 * minSdk 31, compileSdk/targetSdk from the version catalog, Java/Kotlin target 11,
 * Kotlin explicit API mode, consumer R8 rules, dependency locking and the Binary Compatibility
 * Validator API dump (`apiDump` writes `<module>/api/<module>.api`, `apiCheck` runs as part of `check`).
 *
 * The Binary Compatibility Validator only hooks into the standalone `org.jetbrains.kotlin.android`
 * plugin, so AGP 9's built-in Kotlin is disabled in gradle.properties (`android.builtInKotlin=false`).
 * (KGP's integrated ABI validation was evaluated: with AGP built-in Kotlin it produced an empty dump.)
 */
class AndroidLibraryConventionPlugin : Plugin<Project> {
    override fun apply(target: Project) {
        with(target) {
            pluginManager.apply("com.android.library")
            pluginManager.apply("org.jetbrains.kotlin.android")
            pluginManager.apply("org.jetbrains.kotlinx.binary-compatibility-validator")

            val catalog = libs
            val compileSdkMajor = catalog.intVersionOf("androidCompileSdk")
            val compileSdkMinor = catalog.intVersionOf("androidCompileSdkMinor")
            val targetSdkLevel = catalog.intVersionOf("androidTargetSdk")
            val minSdkLevel = catalog.intVersionOf("androidMinSdk")

            extensions.configure(LibraryExtension::class.java) {
                // 02 §7: namespace com.videokit.<module>, e.g. videokit-api -> com.videokit.api
                namespace = "com.videokit." + name.removePrefix("videokit-").replace("-", ".")
                compileSdk {
                    version = release(compileSdkMajor) {
                        minorApiLevel = compileSdkMinor
                    }
                }
                defaultConfig {
                    minSdk = minSdkLevel
                    consumerProguardFiles("consumer-rules.pro")
                    // Consumers only need the API level our public API uses (minSdk), not our compileSdk: Flutter module
                    // hosts compile with Flutter's default compileSdk (36 for Flutter 3.47), M1-B1.
                    aarMetadata {
                        minCompileSdk = minSdkLevel
                    }
                }
                compileOptions {
                    sourceCompatibility = JavaVersion.VERSION_11
                    targetCompatibility = JavaVersion.VERSION_11
                }
                // Local Maven publication (KitPublishing): the release variant with sources.
                if (KitPublishing.isPublished(target)) {
                    publishing {
                        singleVariant("release") {
                            withSourcesJar()
                        }
                    }
                }
                lint {
                    targetSdk = targetSdkLevel
                    abortOnError = true
                    warningsAsErrors = true
                    checkDependencies = false
                    // "Newer version available" checks depend on the date and network, so they are not
                    // reproducible; versions are pinned and only upgraded at milestone boundaries (15 §1).
                    disable += setOf("AndroidGradlePluginVersion", "GradleDependency", "NewerVersionAvailable")
                }
                testOptions {
                    targetSdk = targetSdkLevel
                    unitTests.isReturnDefaultValues = true
                }
            }

            extensions.configure(KotlinAndroidProjectExtension::class.java) {
                explicitApi()
                compilerOptions {
                    jvmTarget.set(JvmTarget.JVM_11)
                    allWarningsAsErrors.set(true)
                }
            }

            KitPublishing.apply(target)
            KitPublishing.registerAndroidRelease(target)

            dependencyLocking {
                lockAllConfigurations()
            }
        }
    }
}
