package com.videokit.timeline

/**
 * One step of the snapshot schema migration (08 §2.1, 04 §10): rewrites the JSON tree of a snapshot written with
 * schema [fromVersion] into the layout of `fromVersion + 1`. The tree uses `Map<String, Any?>`, `List<Any?>`,
 * `String`, `Long`, `Double`, `Boolean` and `null`. A migration only moves and renames data; it must not drop
 * anything the newer schema can hold, and it throws (any exception) on input it cannot read, which restoring
 * reports as a corrupt snapshot.
 */
public interface SchemaMigration {
    /** The schema version this step reads; it produces `fromVersion + 1`. */
    public val fromVersion: Int

    /** Migrates [root] (the snapshot object); returns the migrated object, which may be a new map. */
    public fun migrate(root: Map<String, Any?>): Map<String, Any?>
}

/**
 * An ordered chain of [SchemaMigration]s up to [currentVersion]. The steps must be contiguous and end at
 * [currentVersion]; a snapshot older than [oldestSupportedVersion] or newer than [currentVersion] is rejected.
 */
public class SchemaMigrations(
    steps: List<SchemaMigration>,
    /** The version [ProjectJson] writes. */
    public val currentVersion: Int = ProjectJson.SCHEMA_VERSION,
) {
    private val byVersion: Map<Int, SchemaMigration> = steps.associateBy { it.fromVersion }

    init {
        require(byVersion.size == steps.size) { "duplicate migration steps" }
        val versions = byVersion.keys.sorted()
        val contiguous = versions.isEmpty() || versions == (versions.first() until currentVersion).toList()
        require(contiguous) {
            "migration steps must be contiguous and end at $currentVersion"
        }
    }

    /** The oldest snapshot version that can be restored. */
    public val oldestSupportedVersion: Int = byVersion.keys.minOrNull() ?: currentVersion

    /** Whether [version] can be restored. */
    public fun supports(version: Int): Boolean = version in oldestSupportedVersion..currentVersion

    /** Migrates [root] written with [version] to [currentVersion]. [version] must be [supports]ed. */
    public fun migrate(version: Int, root: Map<String, Any?>): Map<String, Any?> {
        require(supports(version)) { "unsupported schema version $version" }
        var tree = root
        for (from in version until currentVersion) {
            tree = checkNotNull(byVersion[from]).migrate(tree)
        }
        return tree
    }

    public companion object {
        /** The migrations of this Kit version. */
        public val DEFAULT: SchemaMigrations = SchemaMigrations(listOf(V0ToV1))
    }
}

/**
 * Migration v0 → v1 (rule M0 of `spec/schema/edit-project.v1.json`, 04A E2 6). Schema 0 is synthetic: no build wrote
 * it; it exists to test the migration framework and matches the Dart Fake's v0. It is v1 without `schemaVersion`,
 * `schemaMinor`, `createdAt` and `updatedAt`, where:
 * - mask `rangeUs` and `acceptedRanges` items may be arrays `[startUs, endUs]`;
 * - coverage items carry `state` instead of `quality`, and an `accepted` flag;
 * - tracking entries may carry runtime fields (`requestId`, `progress`, …).
 *
 * v1: ranges become objects, coverage items with `accepted = true` are appended to their mask's `acceptedRanges`,
 * `state` becomes `quality`, tracking entries keep only `maskId`, `status` and `coverage`; `createdAt` / `updatedAt`
 * default to 0. Everything else is kept as it is.
 */
public object V0ToV1 : SchemaMigration {
    override val fromVersion: Int = 0

    override fun migrate(root: Map<String, Any?>): Map<String, Any?> {
        val accepted = HashMap<Any?, MutableList<Any?>>()
        val tracking = (root["tracking"] as? List<*>).orEmpty().map { item ->
            val run = item as Map<*, *>
            linkedMapOf(
                "maskId" to run["maskId"],
                "status" to run["status"],
                "coverage" to (run["coverage"] as? List<*>).orEmpty().map { entry ->
                    val segment = entry as Map<*, *>
                    val range = linkedMapOf("startUs" to segment["startUs"], "endUs" to segment["endUs"])
                    if (segment["accepted"] == true) accepted.getOrPut(run["maskId"]) { ArrayList() } += range
                    range + ("quality" to (segment["quality"] ?: segment["state"]))
                },
            )
        }
        val masks = (root["masks"] as? List<*>).orEmpty().map { item ->
            val mask = LinkedHashMap(item as Map<*, *>)
            mask["rangeUs"] = objectRange(mask["rangeUs"])
            mask["acceptedRanges"] = (mask["acceptedRanges"] as? List<*>).orEmpty().map(::objectRange) + accepted[mask["maskId"]].orEmpty()
            mask
        }
        val out = LinkedHashMap<String, Any?>(root)
        out["schemaVersion"] = 1L
        out["schemaMinor"] = 0L
        out["createdAt"] = root["createdAt"] ?: 0L
        out["updatedAt"] = root["updatedAt"] ?: 0L
        out["masks"] = masks
        out["tracking"] = tracking
        return out
    }

    private fun objectRange(range: Any?): Any? = if (range is List<*> && range.size == 2) {
        linkedMapOf("startUs" to range[0], "endUs" to range[1])
    } else {
        range
    }
}
