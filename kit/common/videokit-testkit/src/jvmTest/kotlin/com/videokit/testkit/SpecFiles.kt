package com.videokit.testkit

import java.io.File

/** Locates the repository `spec/` directory (set by the build as the `videokit.specDir` system property). */
internal object SpecFiles {
    val dir: File = File(System.getProperty("videokit.specDir") ?: error("system property videokit.specDir is not set"))

    fun read(relativePath: String): String = File(dir, relativePath).readText(Charsets.UTF_8)
}
