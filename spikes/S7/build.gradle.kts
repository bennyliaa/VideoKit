plugins {
    kotlin("jvm") version "2.4.21"
    application
}

kotlin {
    jvmToolchain(21)
}

dependencies {
    testImplementation(kotlin("test"))
}

application {
    mainClass.set("com.videokit.spike.s7.MainKt")
}

tasks.test {
    useJUnitPlatform()
}
