plugins {
    id("videokit.kmp.common")
    id("videokit.dependency-rules")
}

// 02 §4.0: playback rules and the engine-driven media session over the core runtime and the image rules.
kotlin {
    sourceSets {
        commonMain.dependencies {
            api(project(":videokit-core"))
            // Image sessions (VK-M2): the session drives an ImageController like a playback.
            api(project(":videokit-image"))
        }
        commonTest.dependencies {
            implementation(project(":videokit-testkit"))
            implementation(libs.kotlin.test)
            implementation(libs.kotlinx.coroutines.test)
        }
        jvmTest.dependencies {
            // Contract suite and spec vectors over the fake SPI engines (JUnit glue, file loading of spec/).
            implementation(libs.junit)
        }
    }
}
