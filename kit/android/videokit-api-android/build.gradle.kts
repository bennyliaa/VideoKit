plugins {
    id("videokit.android.library")
    id("videokit.dependency-rules")
}

// 02 §4.0.1: Android specific public types; depends on the platform independent API and the Android SDK only.
videokitDependencyRules {
    allowedModules.set(
        listOf(
            "org\\.jetbrains\\.kotlin:kotlin-stdlib.*",
            "org\\.jetbrains\\.kotlinx:kotlinx-coroutines-(core|core-jvm|bom)",
            "org\\.jetbrains:annotations",
        ),
    )
}

dependencies {
    api(project(":videokit-api"))
    api(libs.kotlinx.coroutines.core)

    testImplementation(libs.junit)
    testImplementation(libs.kotlinx.coroutines.test)
}
