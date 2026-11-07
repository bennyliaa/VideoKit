package com.videokit.buildlogic

import org.gradle.api.Project
import org.gradle.api.publish.PublishingExtension
import org.gradle.api.publish.maven.MavenPublication

/**
 * Local Maven publication of the Kit (M1-B1, 13 §2.1 "AAR versions in sync"): every published module writes
 * `com.videokit:<module>:<version>` into `<repo>/build/kit-maven`, so builds that cannot use `includeBuild` (the
 * generated Flutter module host of `flutter build aar`) resolve the Kit by coordinates. Nothing is published to a
 * remote repository; the directory is a build output and not committed.
 *
 * `./gradlew publishKitMaven` (root) publishes all modules.
 */
internal object KitPublishing {
    const val REPOSITORY_NAME = "KitMaven"
    const val AGGREGATE_TASK = "publishKitMaven"

    /** Build-only modules (no public artifact). */
    fun isPublished(project: Project): Boolean = !project.name.endsWith("-check")

    /** Applies maven-publish and the local repository; Android libraries also need [registerAndroidRelease]. */
    fun apply(project: Project) {
        if (!isPublished(project)) return
        project.pluginManager.apply("maven-publish")
        project.extensions.configure(PublishingExtension::class.java) {
            repositories.maven {
                name = REPOSITORY_NAME
                url = project.rootProject.layout.buildDirectory.dir("kit-maven").get().asFile.toURI()
            }
        }
        val rootTask = project.rootProject.tasks.findByName(AGGREGATE_TASK) ?: project.rootProject.tasks.register(AGGREGATE_TASK) {
            group = "publishing"
            description = "Publishes the Kit modules to build/kit-maven (local Maven repository for Flutter module builds)."
        }.get()
        rootTask.dependsOn(project.tasks.named { it == "publishAllPublicationsTo${REPOSITORY_NAME}Repository" })
    }

    /** Android library: publishes the release variant as `com.videokit:<module>`. */
    fun registerAndroidRelease(project: Project) {
        if (!isPublished(project)) return
        project.afterEvaluate {
            extensions.configure(PublishingExtension::class.java) {
                publications.create("release", MavenPublication::class.java) {
                    artifactId = project.name
                    from(components.getByName("release"))
                }
            }
        }
    }
}
