plugins {
    kotlin("jvm") version "2.4.21"
    application
}

kotlin {
    jvmToolchain(21)
}

dependencies {
    // Spike only, never in the Kit (the dependency rules forbid AI/vision runtimes there). Fetched only after the
    // user's download approval (reports/S6 §3): OpenCV Java bindings with DNN and objdetect (FaceDetectorYN, VitTrack).
    implementation("org.openpnp:opencv:4.9.0-0")
    testImplementation(kotlin("test"))
}

application {
    mainClass.set("com.videokit.spike.s6.MainKt")
}

tasks.test {
    useJUnitPlatform()
}

// Sample search in a read-only source video (lead 2026-11-08): -Pvideo=... -Pmodel=... -Pout=...
tasks.register<JavaExec>("scanCandidates") {
    classpath = sourceSets["main"].runtimeClasspath
    mainClass.set("com.videokit.spike.s6.video.CandidateScan")
    args = listOf(
        providers.gradleProperty("video").get(),
        providers.gradleProperty("model").get(),
        providers.gradleProperty("out").get(),
    )
}

// One clip: -Pvideo=... -Pout=... -Pname=... -Pstart=<s> -Pend=<s> -Ptarget="..."
tasks.register<JavaExec>("exportClip") {
    classpath = sourceSets["main"].runtimeClasspath
    mainClass.set("com.videokit.spike.s6.video.ClipExport")
    args = listOf("video", "out", "name", "start", "end", "target").map { providers.gradleProperty(it).get() }
}
