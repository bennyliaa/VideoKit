plugins {
    id("videokit.android.library")
    id("videokit.dependency-rules")
}

// 14 §2.2: Android dependent test tools (test pattern renderer on a Surface). No Media3, UI or AI libraries.
dependencies {
    api(project(":videokit-testkit"))
    api(project(":videokit-api-android"))
    api(libs.kotlinx.coroutines.core)

    testImplementation(libs.junit)
    testImplementation(libs.kotlinx.coroutines.test)
}
