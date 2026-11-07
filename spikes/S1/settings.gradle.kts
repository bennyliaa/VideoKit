// S1 focused verification (15 §4): host readAt → HostDataSource → Media3 playback. Spike, not part of the Kit build.
// Uses the Kit from the local Maven publication: run `./gradlew publishKitMaven` at the repository root first.
pluginManagement {
    repositories {
        google()
        mavenCentral()
        gradlePluginPortal()
    }
}

dependencyResolutionManagement {
    repositories {
        maven { url = uri(file("../../build/kit-maven")) }
        google()
        mavenCentral()
    }
}

rootProject.name = "videokit-spike-s1"
include(":app")
