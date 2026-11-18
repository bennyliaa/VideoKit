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
        // Flutter engine artifacts (embedding) for compiling the Flutter plugin sources; only io.flutter is served from here.
        exclusiveContent {
            forRepository { maven("https://storage.googleapis.com/download.flutter.io") { name = "FlutterEngine" } }
            filter { includeGroup("io.flutter") }
        }
        // add-to-app (14 §9, 13 §2.1): the Flutter module AAR from `flutter build aar` in flutter/videokit_embed, used by
        // sample-host's embedded flavor only with -Pvideokit.embedAar=true (see sample-host/measure/README.md).
        if (providers.gradleProperty("videokit.embedAar").orNull == "true") {
            exclusiveContent {
                forRepository { maven(file("flutter/videokit_embed/build/host/outputs/repo")) { name = "VideoKitEmbedAar" } }
                filter {
                    includeGroup("com.videokit.embed")
                    includeGroup("com.videokit.flutter")
                }
            }
        }
    }
}

buildscript {
    configurations.classpath {
        resolutionStrategy.activateDependencyLocking()
    }
}

rootProject.name = "VideoKit"

// 13 §1: platform independent modules (KMP commonMain) in kit/common, Android implementations in kit/android.
val commonModules = listOf("videokit-api", "videokit-core", "videokit-image", "videokit-playback", "videokit-timeline", "videokit-testkit")
val androidModules = listOf(
    "videokit-api-android",
    "videokit-image-android",
    "videokit-media3",
    "videokit-export-android",
    "videokit-platform-android",
    "videokit-testkit-android",
    "videokit-flutter-plugin-check",
    "videokit-ui-android",
)

// Native sample host app (13 §1: sample-host/ at the repository root).
include(":sample-host")

commonModules.forEach { name ->
    include(":$name")
    project(":$name").projectDir = file("kit/common/$name")
}
androidModules.forEach { name ->
    include(":$name")
    project(":$name").projectDir = file("kit/android/$name")
}

// Native sample host app (13 §1: sample-host/ at the repository root).
include(":sample-host")
