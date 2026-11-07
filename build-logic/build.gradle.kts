plugins {
    `kotlin-dsl`
}

group = "com.videokit.buildlogic"

dependencyLocking {
    lockAllConfigurations()
}

dependencies {
    implementation(libs.android.gradle.plugin)
    implementation(libs.kotlin.gradle.plugin)
    implementation(libs.binary.compatibility.validator)
}

gradlePlugin {
    plugins {
        register("videokitAndroidLibrary") {
            id = "videokit.android.library"
            implementationClass = "com.videokit.buildlogic.AndroidLibraryConventionPlugin"
        }
        register("videokitDependencyRules") {
            id = "videokit.dependency-rules"
            implementationClass = "com.videokit.buildlogic.DependencyRulesPlugin"
        }
        register("videokitKmpCommon") {
            id = "videokit.kmp.common"
            implementationClass = "com.videokit.buildlogic.KmpCommonConventionPlugin"
        }
        register("videokitRoot") {
            id = "videokit.root"
            implementationClass = "com.videokit.buildlogic.RootConventionPlugin"
        }
    }
}
