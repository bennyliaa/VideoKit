// S7 focused verification (REQ-ED-07, 15 §2.9, 04A E6): head cutout to a transparent-edged PNG. Spike, not part of the
// Kit build. Pure JVM; the face detector (YuNet) and matting models (MODNet, PP-HumanSeg, MediaPipe Selfie
// Multiclass) are added once their download is approved (reports/S7).
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

rootProject.name = "videokit-spike-s7"
