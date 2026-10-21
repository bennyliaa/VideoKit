import org.gradle.api.file.ConfigurableFileCollection
import org.gradle.api.file.DirectoryProperty
import org.gradle.api.file.FileSystemOperations
import org.gradle.api.tasks.InputFiles
import org.gradle.api.tasks.OutputDirectory
import org.gradle.api.tasks.PathSensitive
import org.gradle.api.tasks.PathSensitivity
import org.gradle.api.tasks.TaskAction
import javax.inject.Inject

plugins { alias(libs.plugins.android.application) }

abstract class PrepareD1WorkerSources : DefaultTask() {
    @get:InputFiles @get:PathSensitive(PathSensitivity.RELATIVE)
    abstract val sourceFiles: ConfigurableFileCollection
    @get:OutputDirectory abstract val outputDirectory: DirectoryProperty
    @get:Inject abstract val fileOperations: FileSystemOperations
    @TaskAction fun prepare() {
        fileOperations.sync { from(sourceFiles); into(outputDirectory) }
    }
}

val syncD1WorkerSources by tasks.registering(PrepareD1WorkerSources::class) {
    sourceFiles.from(fileTree("../src") { include("**/FencedTask.java", "**/OutputValidationRules.java", "**/CodecProbeState.java") },
        fileTree("../android") { include("**/MediaProtocol.java", "**/AndroidLease.java", "**/BrokerDataSource.java",
            "**/FdOutputMuxer.java", "**/AndroidOutputValidator.java", "**/StageLog.java", "**/IsolatedMediaService.java", "**/CodecWorkerSlot1.java") })
    outputDirectory.set(layout.buildDirectory.dir("generated/d1WorkerSources"))
}

android {
    namespace = "com.videokit.worker.spike"
    compileSdk { version = release(36) { minorApiLevel = 1 } }
    ndkVersion = "30.0.16248370"
    defaultConfig {
        applicationId = "com.videokit.worker.spike"
        minSdk = 31
        targetSdk = 36
        versionCode = 1
        versionName = "D1-20261016-C10"
    }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_11
        targetCompatibility = JavaVersion.VERSION_11
    }
    packaging { jniLibs { keepDebugSymbols += "**/*.so" } }
    sourceSets.getByName("debug").jniLibs.srcDir("../worker-native-libs")
}
androidComponents.onVariants { variant ->
    variant.sources.java?.addGeneratedSourceDirectory(syncD1WorkerSources) { it.outputDirectory }
}
dependencyLocking { lockAllConfigurations() }
dependencies {
    implementation(libs.media3.spike.exoplayer)
    implementation(libs.media3.spike.transformer)
    implementation(libs.media3.spike.muxer)
    constraints {
        // Reuse exact already-reviewed runtime coordinates; no silent dependency version drift in the prototype APK.
        rootProject.file("app/gradle.lockfile").readLines().filter { line ->
            !line.startsWith("#") && line.contains("=") && line.substringAfter("=").split(",").contains("debugRuntimeClasspath")
        }.forEach { line -> implementation(line.substringBefore("=")) { version { strictly(line.substringBefore("=").substringAfterLast(":")) } } }
    }
}
