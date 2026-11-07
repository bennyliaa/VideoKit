pluginManagement {
    includeBuild("build-logic")
    repositories {
        google {
            content {
                includeGroupByRegex("com\\.android.*")
                includeGroupByRegex("com\\.google.*")
                includeGroupByRegex("androidx.*")
            }
        }
        mavenCentral()
        gradlePluginPortal()
    }
}

dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {
        google {
            content {
                includeGroupByRegex("com\\.android.*")
                includeGroupByRegex("com\\.google.*")
                includeGroupByRegex("androidx.*")
            }
        }
        mavenCentral()
    }
}

buildscript {
    configurations.classpath {
        resolutionStrategy.activateDependencyLocking()
    }
}

rootProject.name = "VideoKit"

// 13 §1: platform independent modules (KMP commonMain) in kit/common, Android implementations in kit/android.
val commonModules = listOf("videokit-api", "videokit-core", "videokit-testkit")
val androidModules = listOf("videokit-api-android", "videokit-testkit-android")

commonModules.forEach { name ->
    include(":$name")
    project(":$name").projectDir = file("kit/common/$name")
}
androidModules.forEach { name ->
    include(":$name")
    project(":$name").projectDir = file("kit/android/$name")
}
