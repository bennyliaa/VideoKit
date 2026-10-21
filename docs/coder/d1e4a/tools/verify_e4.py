"""Read-only E4 identity/membership verification. Never starts a process or consumes a grant."""
from __future__ import annotations
import argparse
from pathlib import Path
from e4_package import BASE_REL, CANDIDATE, Reader, canonical, check_copy_map, check_evidence, check_private_payload, collect_sources, require, sha


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=str(Path(__file__).resolve().parents[4]))
    parser.add_argument("--expected-freeze")
    args = parser.parse_args(); root = Path(args.root).resolve(); reader = Reader(root)
    seal_name = BASE_REL + "/evidence/e4a-freeze.json"
    seal_bytes = reader.data(seal_name); summary = reader.document(seal_name)
    if args.expected_freeze is not None:
        require(sha(seal_bytes) == args.expected_freeze.lower(), "external E4 freeze identity mismatch")
    require(summary.get("schema") == 1 and summary.get("candidateId") == CANDIDATE
            and summary.get("state") == "FROZEN_LOCAL_ONLY_PENDING_COORDINATOR_REVIEW"
            and summary.get("androidExecution") == "NOT_RUN"
            and summary.get("nativeFaultExecution") == "NOT_RUN", "E4 frozen scope mismatch")
    reader.match(summary["sourceManifest"]); reader.match(summary["sourceZip"])
    manifest = reader.document(summary["sourceManifest"]["path"])
    rows = manifest["files"]; expected = {row["path"]: row for row in rows}
    require(len(expected) == len(rows) and sorted(expected) == collect_sources(root), "working source/evidence exact file set changed")
    for row in rows:
        reader.match(row); check_private_payload(row["path"], reader.data(row["path"]))
    immutable = summary["immutableFiles"]
    require(len({row["path"] for row in immutable}) == len(immutable), "duplicate immutable identity")
    required_immutable = set(expected) | {summary["sourceManifest"]["path"], summary["sourceZip"]["path"]}
    required_immutable |= {row["path"] for row in summary["facts"]["apks"] + summary["facts"]["preservedArtifacts"]}
    require({row["path"] for row in immutable} == required_immutable, "immutable file set incomplete/extra")
    for row in immutable: reader.match(row)
    with reader.archive(summary["sourceZip"]["path"]) as archive:
        require(set(archive.namelist()) == set(expected), "source ZIP exact member set changed")
        for name, row in expected.items():
            data = reader.member(archive, name); check_private_payload(name, data)
            require(len(data) == row["bytes"] and sha(data) == row["sha256"], "source ZIP member mismatch: " + name)
    upstream = check_copy_map(reader); facts = check_evidence(reader)
    require(upstream == summary["upstream"] and facts == summary["facts"], "semantic evidence differs from frozen facts")
    print(canonical({"candidateId": CANDIDATE, "integrity": "PASS", "readOnly": True,
                     "externalFreezeIdentityChecked": args.expected_freeze is not None,
                     "freezeSha256": sha(seal_bytes), "sourceFiles": len(rows),
                     "immutableFiles": len(immutable), "sourceZip": summary["sourceZip"],
                     "localAssertions": facts["localAssertions"], "androidExecution": "NOT_RUN",
                     "D1": "NOT_PASSED", "readUsage": reader.usage()}).decode("utf-8"))


if __name__ == "__main__":
    main()
