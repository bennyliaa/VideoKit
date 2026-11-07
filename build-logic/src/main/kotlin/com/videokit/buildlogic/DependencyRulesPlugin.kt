package com.videokit.buildlogic

import com.android.build.api.variant.LibraryAndroidComponentsExtension
import org.gradle.api.DefaultTask
import org.gradle.api.GradleException
import org.gradle.api.Plugin
import org.gradle.api.Project
import org.gradle.api.artifacts.component.ModuleComponentIdentifier
import org.gradle.api.artifacts.component.ProjectComponentIdentifier
import org.gradle.api.artifacts.result.ResolvedComponentResult
import org.gradle.api.artifacts.result.ResolvedDependencyResult
import org.gradle.api.provider.ListProperty
import org.gradle.api.provider.MapProperty
import org.gradle.api.provider.Property
import org.gradle.api.tasks.Input
import org.gradle.api.tasks.TaskAction

/**
 * Module dependency rules (02 §4.0, 13 §2): a module declares which external modules it may depend on
 * and which are forbidden. The check walks the resolved compile and runtime classpaths of every variant
 * and fails the build on a violation. It is wired into `check`.
 */
abstract class DependencyRulesExtension {
    /** Regular expressions matched against `group:name`; every external module must match one. Empty = no allowlist. */
    abstract val allowedModules: ListProperty<String>

    /** Regular expression on `group:name` mapped to the rule text reported when it matches. */
    abstract val forbiddenModules: MapProperty<String, String>

    /** Whether the module may depend on other projects of this build. */
    abstract val allowProjectDependencies: Property<Boolean>
}

class DependencyRulesPlugin : Plugin<Project> {
    override fun apply(target: Project) {
        with(target) {
            val extension = extensions.create("videokitDependencyRules", DependencyRulesExtension::class.java)
            extension.allowProjectDependencies.convention(true)
            // 13 §2: kit/common/** must not depend on any Android, Media3, AI or OpenCV library, nor on kit/android/**.
            val commonLayer = isUnder(target, "kit/common")
            extension.forbiddenModules.convention(if (commonLayer) DEFAULT_FORBIDDEN + COMMON_LAYER_FORBIDDEN else DEFAULT_FORBIDDEN)
            val androidLayerProjects = rootProject.subprojects.filter { isUnder(it, "kit/android") }.map { it.path }

            val checkTask = tasks.register("checkDependencyRules", CheckDependencyRulesTask::class.java) {
                group = "verification"
                description = "Fails when the module depends on modules forbidden by the VideoKit dependency rules."
                modulePath.set(target.path)
                allowedModules.set(extension.allowedModules)
                forbiddenModules.set(extension.forbiddenModules)
                allowProjectDependencies.set(extension.allowProjectDependencies)
                forbiddenProjects.set(if (commonLayer) androidLayerProjects else emptyList())
                // Demonstration hook: -Pvideokit.dependencyRules.probe=group:name:version injects a coordinate.
                probeCoordinates.set(
                    providers.gradleProperty("videokit.dependencyRules.probe")
                        .map { value -> value.split(',').map(String::trim).filter(String::isNotEmpty) }
                        .orElse(emptyList()),
                )
            }

            pluginManager.withPlugin("com.android.library") {
                val components = extensions.getByType(LibraryAndroidComponentsExtension::class.java)
                components.onVariants { variant ->
                    checkTask.configure {
                        rootComponents.add(variant.compileConfiguration.incoming.resolutionResult.rootComponent)
                        rootComponents.add(variant.runtimeConfiguration.incoming.resolutionResult.rootComponent)
                    }
                }
                tasks.named("check").configure { dependsOn(checkTask) }
            }
            pluginManager.withPlugin("org.jetbrains.kotlin.multiplatform") {
                val checked = setOf("jvmCompileClasspath", "jvmRuntimeClasspath")
                configurations.matching { it.name in checked }.all {
                    val configuration = this
                    checkTask.configure {
                        rootComponents.add(configuration.incoming.resolutionResult.rootComponent)
                    }
                }
                tasks.named("check").configure { dependsOn(checkTask) }
            }
        }
    }

    internal companion object {
        private fun isUnder(project: Project, relativeDir: String): Boolean {
            val base = project.rootProject.layout.projectDirectory.dir(relativeDir).asFile.toPath().normalize()
            return project.projectDir.toPath().normalize().startsWith(base)
        }

        /** Everything Android-specific; added for modules in kit/common/. */
        val COMMON_LAYER_FORBIDDEN: Map<String, String> = linkedMapOf(
            "androidx\\..*:.*" to "kit/common must not depend on AndroidX (13 §2, §3.2)",
            "com\\.android\\..*:.*" to "kit/common must not depend on Android libraries (13 §2, §3.2)",
            "com\\.google\\.android\\..*:.*" to "kit/common must not depend on Android libraries (13 §2, §3.2)",
        )

        /** Android UI, Media3/ExoPlayer, Flutter embedding and AI/ML runtimes. */
        val DEFAULT_FORBIDDEN: Map<String, String> = linkedMapOf(
            "androidx\\.media3:.*" to "Media3 is not allowed (02 §4.0)",
            "com\\.google\\.android\\.exoplayer.*:.*" to "ExoPlayer is not allowed (02 §4.0)",
            "androidx\\.compose.*:.*" to "Android UI (Compose) is not allowed",
            "androidx\\.(appcompat|fragment|activity|recyclerview|constraintlayout|viewpager|viewpager2|transition|window):.*" to
                "Android UI libraries are not allowed",
            "com\\.google\\.android\\.material:.*" to "Android UI (Material Components) is not allowed",
            "io\\.flutter:.*" to "Flutter embedding is not allowed",
            "org\\.tensorflow:.*" to "AI runtime (TensorFlow) is not allowed",
            "com\\.google\\.mlkit:.*" to "AI runtime (ML Kit) is not allowed",
            "com\\.google\\.android\\.gms:play-services-mlkit.*" to "AI runtime (ML Kit) is not allowed",
            "com\\.google\\.mediapipe:.*" to "AI runtime (MediaPipe) is not allowed",
            "com\\.microsoft\\.onnxruntime:.*" to "AI runtime (ONNX Runtime) is not allowed",
            "org\\.opencv:.*" to "AI/vision runtime (OpenCV) is not allowed",
            "org\\.pytorch:.*" to "AI runtime (PyTorch) is not allowed",
        )
    }
}

abstract class CheckDependencyRulesTask : DefaultTask() {
    @get:Input
    abstract val modulePath: Property<String>

    @get:Input
    abstract val rootComponents: ListProperty<ResolvedComponentResult>

    @get:Input
    abstract val allowedModules: ListProperty<String>

    @get:Input
    abstract val forbiddenModules: MapProperty<String, String>

    @get:Input
    abstract val allowProjectDependencies: Property<Boolean>

    @get:Input
    abstract val probeCoordinates: ListProperty<String>

    /** Project paths this module must not depend on (the kit/android modules, for modules in kit/common). */
    @get:Input
    abstract val forbiddenProjects: ListProperty<String>

    @TaskAction
    fun check() {
        val modules = sortedSetOf<String>()
        val projects = sortedSetOf<String>()
        val visited = mutableSetOf<ResolvedComponentResult>()
        rootComponents.get().forEach { root -> collect(root, modules, projects, visited) }
        // Probe entries starting with ":" are project paths, the others group:name:version coordinates.
        probeCoordinates.get().forEach { if (it.startsWith(":")) projects += it else modules += it }

        val allowed = allowedModules.get().map(::Regex)
        val forbidden = forbiddenModules.get().map { (pattern, reason) -> Regex(pattern) to reason }
        val violations = mutableListOf<String>()
        modules.forEach { coordinate ->
            val groupAndName = coordinate.split(':').take(2).joinToString(":")
            forbidden.firstOrNull { (regex, _) -> regex.matches(groupAndName) }?.let { (_, reason) ->
                violations += "$coordinate: $reason"
            }
            if (allowed.isNotEmpty() && allowed.none { it.matches(groupAndName) }) {
                violations += "$coordinate: not in the allowlist of ${modulePath.get()}"
            }
        }
        if (!allowProjectDependencies.get()) {
            projects.forEach { violations += "project $it: ${modulePath.get()} must not depend on other modules" }
        }
        val forbiddenProjectPaths = forbiddenProjects.get().toSet()
        projects.filter { it in forbiddenProjectPaths }.forEach {
            violations += "project $it: kit/common modules must not depend on kit/android modules"
        }
        if (violations.isNotEmpty()) {
            throw GradleException(
                "VideoKit dependency rule violation in ${modulePath.get()}:\n" +
                    violations.distinct().joinToString("\n") { "  - $it" },
            )
        }
        logger.lifecycle("Dependency rules OK for ${modulePath.get()}: ${modules.size} external modules checked.")
    }

    private fun collect(
        component: ResolvedComponentResult,
        modules: MutableSet<String>,
        projects: MutableSet<String>,
        visited: MutableSet<ResolvedComponentResult>,
    ) {
        if (!visited.add(component)) return
        component.dependencies.filterIsInstance<ResolvedDependencyResult>().forEach { dependency ->
            val selected = dependency.selected
            when (val id = selected.id) {
                is ModuleComponentIdentifier -> modules += "${id.group}:${id.module}:${id.version}"
                is ProjectComponentIdentifier -> if (id.projectPath != modulePath.get()) projects += id.projectPath
            }
            collect(selected, modules, projects, visited)
        }
    }
}
