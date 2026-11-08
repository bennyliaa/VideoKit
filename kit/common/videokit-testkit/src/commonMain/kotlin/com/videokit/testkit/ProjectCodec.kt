package com.videokit.testkit

import com.videokit.api.SerializedEditProject
import com.videokit.timeline.ProjectDocument
import com.videokit.timeline.ProjectJson

/** Serializable content of a Fake edit project (08 §2.1): the timeline module's document (M4-B1). */
internal typealias ProjectModel = ProjectDocument

/**
 * Versioned JSON codec of the Fake: the timeline module's [ProjectJson] (M4-B1), so the Fake and the real project
 * write and migrate snapshots identically. Reading ignores unknown fields (minor additions), fills defaults for
 * missing optional fields, migrates older schemas and rejects unknown future versions (04 §10).
 */
internal object ProjectCodec {
    const val SCHEMA_VERSION: Int = ProjectJson.SCHEMA_VERSION

    fun encode(model: ProjectModel): SerializedEditProject = ProjectJson.encode(model)

    fun decode(serialized: SerializedEditProject): ProjectModel = ProjectJson.decode(serialized)
}
