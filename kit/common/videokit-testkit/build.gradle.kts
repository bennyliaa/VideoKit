plugins {
    id("videokit.kmp.common")
    id("videokit.dependency-rules")
}

// 02 §4.0: testkit depends on api (and core); no Android, Media3 or AI libraries.
kotlin {
    sourceSets {
        commonMain.dependencies {
            api(project(":videokit-api"))
            api(project(":videokit-core"))
            api(libs.kotlinx.coroutines.core)
        }
        commonTest.dependencies {
            implementation(libs.kotlin.test)
            implementation(libs.kotlinx.coroutines.test)
        }
        jvmTest.dependencies {
            // JUnit glue only: parameterized runner for the contract suite and file loading of spec/.
            implementation(libs.junit)
        }
    }
}
