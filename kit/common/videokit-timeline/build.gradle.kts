plugins {
    id("videokit.kmp.common")
    id("videokit.dependency-rules")
}

// 12 VK-M4 (M4-B1): the platform independent timeline layer: project schema and versioned JSON, edit commands with
// undo/redo, snapshot/restore with schema migrations, and the pure rules of the concat path decision (08 §3.1).
// No media engine; editing stays unavailable in EditingCapabilities until the engine batch after S3.
kotlin {
    sourceSets {
        commonMain.dependencies {
            api(project(":videokit-core"))
        }
        commonTest.dependencies {
            implementation(libs.kotlin.test)
            implementation(libs.kotlinx.coroutines.test)
        }
        jvmTest.dependencies {
            // Spec vectors (spec/vectors/timeline, spec/vectors/state-machine/edit-project.json) loaded from files.
            implementation(libs.junit)
        }
    }
}
