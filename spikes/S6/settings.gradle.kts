// S6 focused verification (09, 15 §4 S6): keeping the identity of one selected person among several (association
// logic, scenario metrics). Spike, not part of the Kit build. Pure JVM; the detector/tracker/feature models (YuNet,
// VitTrack, SFace) are added once their download is approved (reports\S6).
pluginManagement {
    repositories {
        gradlePluginPortal()
        mavenCentral()
    }
}

dependencyResolutionManagement {
    repositories {
        mavenCentral()
    }
}

rootProject.name = "videokit-spike-s6"
