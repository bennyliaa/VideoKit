plugins {
    id("videokit.kmp.common")
    id("videokit.dependency-rules")
}

// 02 §4.0: core depends on the API only. M0 contains the SPI drafts (02 §4.2); the runtime arrives from M1.
kotlin {
    sourceSets {
        commonMain.dependencies {
            api(project(":videokit-api"))
            api(libs.kotlinx.coroutines.core)
        }
        commonTest.dependencies {
            implementation(libs.kotlin.test)
        }
    }
}
