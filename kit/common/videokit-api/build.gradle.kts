plugins {
    id("videokit.kmp.common")
    id("videokit.dependency-rules")
}

// 02 §4.0 / 13 §2: the public API only depends on the Kotlin standard library and Coroutines.
videokitDependencyRules {
    allowProjectDependencies.set(false)
    allowedModules.set(
        listOf(
            "org\\.jetbrains\\.kotlin:kotlin-stdlib.*",
            "org\\.jetbrains\\.kotlinx:kotlinx-coroutines-(core|core-jvm|bom)",
            "org\\.jetbrains:annotations",
        ),
    )
}

kotlin {
    sourceSets {
        commonMain.dependencies {
            api(libs.kotlinx.coroutines.core)
        }
        commonTest.dependencies {
            implementation(libs.kotlin.test)
            implementation(libs.kotlinx.coroutines.test)
        }
    }
}
