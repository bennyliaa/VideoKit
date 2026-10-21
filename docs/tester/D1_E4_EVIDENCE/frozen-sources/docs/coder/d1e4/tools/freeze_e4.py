"""Default inspect only. --freeze creates one immutable local-only E4 handoff."""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import io
from pathlib import Path
import zipfile
from e4_package import BASE_REL, CANDIDATE, DOCS, canonical, inspect, require, sha, write_new


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=str(Path(__file__).resolve().parents[4]))
    parser.add_argument("--freeze", action="store_true")
    args = parser.parse_args()
    root = Path(args.root).resolve(); base = root / BASE_REL
    reader, sources, upstream, facts = inspect(root)
    seal = base / "evidence/e4-freeze.json"
    manifest_path = base / "evidence/source-manifest.json"
    zip_path = base / ("artifacts/" + CANDIDATE + "/" + CANDIDATE + "-source.zip")
    require(not seal.exists() and not manifest_path.exists() and not zip_path.exists(), "E4 already frozen or partial freeze retained; never overwrite")
    rows = [reader.row(name) for name in sources]
    preview = {"candidateId": CANDIDATE, "mode": "FREEZE" if args.freeze else "INSPECT",
               "sourceFiles": len(rows), "sourceBytes": sum(r["bytes"] for r in rows),
               "androidExecution": "NOT_RUN", "facts": facts, "upstream": upstream,
               "readUsage": reader.usage()}
    if not args.freeze:
        print(canonical(preview).decode("utf-8")); return
    manifest = {"schema": 1, "candidateId": CANDIDATE, "gitCommit": None, "files": rows,
                "privacyExclusions": ["local.properties", "private keys and credential containers", "Gradle caches and machine build state"],
                "scope": "E4 sources, exact dependency copy, complete frozen C14 source container, four reports and preserved local evidence; original media excluded"}
    manifest_bytes = canonical(manifest)
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for name in sources:
            info = zipfile.ZipInfo(name, date_time=(2026, 10, 17, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED; info.external_attr = 0o100644 << 16
            archive.writestr(info, reader.data(name), compress_type=zipfile.ZIP_DEFLATED, compresslevel=6)
    zip_bytes = buffer.getvalue()
    # All validation precedes the first mutation. A partial write is retained, never silently retried.
    write_new(manifest_path, manifest_bytes); write_new(zip_path, zip_bytes)
    manifest_row = {"path": manifest_path.relative_to(root).as_posix(), "bytes": len(manifest_bytes), "sha256": sha(manifest_bytes)}
    zip_row = {"path": zip_path.relative_to(root).as_posix(), "bytes": len(zip_bytes), "sha256": sha(zip_bytes)}
    immutable = {r["path"]: r for r in rows}
    immutable[manifest_row["path"]] = manifest_row; immutable[zip_row["path"]] = zip_row
    for apk in facts["apks"]:
        immutable[apk["path"]] = {k: apk[k] for k in ("path", "bytes", "sha256")}
    summary = {"schema": 1, "candidateId": CANDIDATE, "gitCommit": None,
               "frozenAtUtc": datetime.now(timezone.utc).isoformat(),
               "state": "FROZEN_LOCAL_ONLY_PENDING_COORDINATOR_REVIEW",
               "D1": "NOT_PASSED", "M0": "NOT_STARTED", "allP0": "REMAIN_OPEN",
               "androidExecution": "NOT_RUN", "nativeFaultExecution": "NOT_RUN",
               "sourceManifest": manifest_row, "sourceZip": zip_row,
               "documents": list(DOCS), "immutableFiles": sorted(immutable.values(), key=lambda r: r["path"]),
               "facts": facts, "upstream": upstream,
               "sourceMembership": "exact file list in sourceManifest; complete historical source container hash-bound once without recursive expansion",
               "scope": "compile/JVM rule evidence only; no Android codec, hardware, isolation, fault, media or device execution claim",
               "readUsageBeforeFreeze": reader.usage()}
    seal_bytes = canonical(summary); write_new(seal, seal_bytes)
    preview.update({"freezeSha256": sha(seal_bytes), "sourceZip": zip_row, "freezeFile": seal.relative_to(root).as_posix()})
    print(canonical(preview).decode("utf-8"))


if __name__ == "__main__":
    main()
