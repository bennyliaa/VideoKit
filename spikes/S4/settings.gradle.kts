// S4 focused verification (15 §4, §2.8): export in an isolatedProcess with FD-proxied input and output, fault injection. Spike, not part of the Kit build.
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

rootProject.name = "videokit-spike-s4"
include(":app")
