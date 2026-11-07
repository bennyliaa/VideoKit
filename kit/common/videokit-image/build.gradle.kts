plugins {
    id("videokit.kmp.common")
    id("videokit.dependency-rules")
}

// 02 §4.0 / 15 §2.10: platform independent image rules (decode size, tile scheduling, memory quota, image state)
// and the image controller the media session drives; depends on core only. Decoding is the ImageEngine SPI.
kotlin {
    sourceSets {
        commonMain.dependencies {
            api(project(":videokit-core"))
        }
        commonTest.dependencies {
            implementation(project(":videokit-testkit"))
            implementation(libs.kotlin.test)
            implementation(libs.kotlinx.coroutines.test)
        }
    }
}
