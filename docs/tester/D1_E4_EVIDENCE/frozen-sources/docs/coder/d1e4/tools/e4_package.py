"""Read-only bounded E4 packaging helpers; never import Android or media runners."""
from __future__ import annotations

import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import zipfile

CANDIDATE = "D1-20261017-E4"
BASE_REL = "docs/coder/d1e4"
DOCS = (
    "docs/coder/D1_E4_DELIVERY_V1.0.md",
    "docs/coder/D1_E4_ARCHITECTURE_AND_THREAT_BOUNDARY_V1.0.md",
    "docs/coder/D1_E4_DEVICE_EXECUTION_APPENDIX_V1.0.md",
    "docs/coder/D1_E4_REMAINING_GATE_REVIEW_V1.0.md",
)
REQUIRED_EVIDENCE = (
    "evidence/build-results.json", "evidence/local-check-results.json",
    "evidence/apk-audit.json", "evidence/sbom.json", "evidence/upstream-copy-map.json",
)
EXCLUDED_DIRS = {"build", ".gradle", ".kotlin", ".git", "__pycache__", "selfcheck", "local-checks", "artifacts"}
EXCLUDED_FILES = {"local.properties", "freeze-summary.json", "e4-freeze.json", "source-manifest.json"}
FORBIDDEN_DIRS = {"test_media", ".ssh", ".aws", "gpg-home", "credentials", ".codex"}
FORBIDDEN_SUFFIXES = {".jks", ".keystore", ".p12", ".pfx", ".key", ".pem"}
HEX = re.compile(r"^[0-9a-f]{64}$")
MAX_FILES = 4096
MAX_ZIP_LOGICAL = 256 * 1024 * 1024
MAX_FILE = 96 * 1024 * 1024
C14_FREEZE_SHA256 = "880b38f3896df2f6bed2657d54c7fb8a954d3d05d8c730faf1b11278726e7155"
C14_SOURCE_ZIP_SHA256 = "69ca847d7c1947ae65eb3ed6e79d8ab50e21ac9463a1a686cdeda6cfef2d683d"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def sha(data):
    return hashlib.sha256(data).hexdigest()


def fingerprint(value):
    require(isinstance(value, str), "certificate fingerprint missing")
    result = value.replace(":", "").lower()
    require(HEX.fullmatch(result), "certificate SHA-256 invalid")
    return result


def relative_name(name):
    require(isinstance(name, str) and "\\" not in name and ":" not in name, "nonportable package path")
    path = PurePosixPath(name)
    require(not path.is_absolute() and path.parts and all(p not in {"", ".", ".."} for p in path.parts), "unsafe package path")
    return path


def project_path(root, name):
    path = root.joinpath(*relative_name(name).parts)
    require(path.is_file() and not path.is_symlink(), "missing/linked file: " + name)
    require(path.resolve().is_relative_to(root), "file escapes project: " + name)
    # Reparse directories and symlinks cannot silently change the finite package scope.
    for component in (path, *path.parents):
        if component == root.parent:
            break
        require(not component.is_symlink(), "linked package ancestor: " + name)
        attrs = getattr(component.stat(), "st_file_attributes", 0)
        require(not attrs & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400), "reparse package ancestor: " + name)
        if component == root:
            break
    return path


def allowed_member(name):
    p = relative_name(name)
    require(not any(part.lower() in FORBIDDEN_DIRS for part in p.parts), "private/media path in package: " + name)
    require(p.name != "local.properties" and p.name != ".env" and not p.name.startswith(".env."), "machine/secret file in package: " + name)
    require(p.suffix.lower() not in FORBIDDEN_SUFFIXES, "private-key container in package: " + name)


class Reader:
    """One in-command cache; explicit finite totals include compressed and logical archive reads."""
    def __init__(self, root):
        self.root = Path(root).resolve()
        self.cache = {}
        self.read_bytes = 0
        self.logical_bytes = 0
        self.file_reads = 0

    def data(self, name):
        if name not in self.cache:
            p = project_path(self.root, name)
            require(p.stat().st_size <= MAX_FILE, "file read bound: " + name)
            data = p.read_bytes()
            require(len(data) == p.stat().st_size, "file changed during read: " + name)
            self.cache[name] = data
            self.read_bytes += len(data); self.file_reads += 1
            require(self.file_reads <= MAX_FILES and self.read_bytes <= MAX_ZIP_LOGICAL * 2, "package read budget")
        return self.cache[name]

    def document(self, name):
        require(len(self.data(name)) <= 4 * 1024 * 1024, "metadata document bound: " + name)
        return json.loads(self.data(name).decode("utf-8-sig"))

    def row(self, name):
        data = self.data(name)
        return {"path": name, "bytes": len(data), "sha256": sha(data)}

    def match(self, row):
        require(isinstance(row, dict) and set(row) >= {"path", "bytes", "sha256"}, "hash row schema")
        actual = self.row(row["path"])
        require(actual == {key: row[key] for key in actual}, "file identity mismatch: " + row["path"])

    def archive(self, name):
        archive = zipfile.ZipFile(io.BytesIO(self.data(name)), "r")
        entries = archive.infolist()
        require(len(entries) <= MAX_FILES and len({e.filename for e in entries}) == len(entries), "archive member count/duplicate")
        total = sum(e.file_size for e in entries)
        require(total <= MAX_ZIP_LOGICAL, "archive logical bound")
        for entry in entries:
            relative_name(entry.filename)
            require(entry.file_size <= MAX_FILE and not entry.flag_bits & 1, "archive encrypted/oversized member")
            require(not stat.S_ISLNK(entry.external_attr >> 16), "archive symlink")
        return archive

    def member(self, archive, name):
        data = archive.read(name)
        self.logical_bytes += len(data)
        require(self.logical_bytes <= MAX_ZIP_LOGICAL * 2, "archive logical read budget")
        return data

    def usage(self):
        return {"physicalBytesRead": self.read_bytes, "logicalArchiveBytesRead": self.logical_bytes,
                "fileReads": self.file_reads, "mediaBytesRead": 0, "recursiveArchiveExpansion": False}


def collect_sources(root):
    base = root / BASE_REL
    names = []
    for directory, folders, files in os.walk(base, followlinks=False):
        folders[:] = sorted(f for f in folders if f not in EXCLUDED_DIRS)
        for filename in sorted(files):
            path = Path(directory) / filename
            name = path.relative_to(root).as_posix()
            if filename in EXCLUDED_FILES or filename.endswith((".pyc", ".class")):
                continue
            allowed_member(name)
            names.append(name)
    names.extend(DOCS)
    require(len(names) == len(set(names)) and len(names) <= MAX_FILES, "source set count/duplicate")
    return sorted(names)


def check_private_payload(name, data):
    allowed_member(name)
    if Path(name).suffix.lower() in {".java", ".kt", ".kts", ".py", ".ps1", ".txt", ".md", ".json", ".xml", ".properties", ".toml", ".bat", ".lockfile"}:
        require(not re.search(rb"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----", data), "private-key text in source package: " + name)


def check_copy_map(reader):
    rows = reader.document(BASE_REL + "/evidence/upstream-copy-map.json")["files"]
    require(isinstance(rows, list) and len(rows) <= 128, "upstream copy map bound")
    require(len({r["destination"] for r in rows}) == len(rows), "duplicate copied destination")
    java = 0; native = 0
    copied_c14_rows = []
    for row in rows:
        source, dest = row["source"], row["destination"]
        relative_name(source); relative_name(dest)
        require(dest.startswith(BASE_REL + "/") and not source.startswith("test_media/"), "copy map scope")
        require(row["relationship"] == "BYTE_IDENTICAL", "unaccounted derivative upstream source")
        expected = {"path": dest, "bytes": row["bytes"], "sha256": row["sha256"]}
        reader.match(expected)
        require(reader.data(source) == reader.data(dest), "original upstream changed: " + source)
        if source.startswith("docs/coder/d1c14/"):
            if source.endswith(".java"): java += 1
            if source.endswith(".so"): native += 1
            copied_c14_rows.append(row)
    require(java == 23 and native == 7, "C14 finite closure must contain 23 Java classes and seven unchanged libraries")
    c14_seal = BASE_REL + "/upstream-c14/freeze-summary.json"
    require(sha(reader.data(c14_seal)) == C14_FREEZE_SHA256, "previously frozen C14 identity changed")
    frozen = reader.document(c14_seal)
    source_manifest_name = BASE_REL + "/upstream-c14/source-manifest.json"
    require(sha(reader.data(source_manifest_name)) == frozen["source_manifest_sha256"], "C14 source manifest binding")
    original_rows = {r["path"]: r for r in reader.document(source_manifest_name)["source_files"]}
    zip_name = BASE_REL + "/upstream-c14/D1-20261016-C14-source.zip"
    original_zip_row = next(r for r in frozen["artifacts"] if r["path"].endswith("/D1-20261016-C14-source.zip"))
    require(original_zip_row["sha256"] == C14_SOURCE_ZIP_SHA256, "C14 original complete source ZIP binding changed")
    require(len(reader.data(zip_name)) == original_zip_row["bytes"] and sha(reader.data(zip_name)) == original_zip_row["sha256"], "complete C14 source container identity")
    with reader.archive(zip_name) as archive:
        require(set(archive.namelist()) == set(original_rows), "C14 frozen container exact member set")
        # Copy closure is checked directly against the frozen container; other members remain hash-bound.
        for row in copied_c14_rows:
            if row["source"] in original_rows:
                data = reader.member(archive, row["source"])
                require(len(data) == row["bytes"] and sha(data) == row["sha256"], "C14 copied member mismatch")
    return {"javaClasses": java, "nativeLibraries": native, "copiedFiles": len(rows),
            "completeSourceZipSha256": original_zip_row["sha256"], "originalFilesUnchanged": True}


def check_evidence(reader):
    for name in REQUIRED_EVIDENCE:
        reader.data(BASE_REL + "/" + name)
    build = reader.document(BASE_REL + "/evidence/build-results.json")
    require(build.get("schema") == 1 and build.get("status") == "PASS" and build.get("offline") is True, "local offline build evidence not PASS")
    attempts = build.get("attempts")
    require(isinstance(attempts, list) and 1 <= len(attempts) <= 8, "build attempts bound")
    require(sum(a.get("kind") == "MAIN" for a in attempts) == 1 and attempts[0].get("kind") == "MAIN", "exactly one preserved main build")
    require(attempts[-1].get("exitCode") == 0 and all(a.get("kind") in {"MAIN", "REPAIR"} for a in attempts), "final build did not succeed")
    require(len({a["id"] for a in attempts}) == len(attempts), "duplicate build attempt")
    for attempt in attempts:
        require(attempt.get("exitCode") is not None, "in-flight build attempt")
        require(attempt["log"].startswith(BASE_REL + "/evidence/"), "build log scope")
        reader.data(attempt["log"])
    final_inputs = reader.document(BASE_REL + "/evidence/final-build-inputs.json")
    require(final_inputs.get("scope") == "E4_FINAL_REPAIR_SOURCE_BINDING" and final_inputs.get("schema") == 1,
            "final Android build source snapshot missing")
    require(isinstance(final_inputs.get("files"), list) and 8 <= len(final_inputs["files"]) <= 128,
            "final Android build source count")
    for row in final_inputs["files"]:
        require(row["path"].startswith(BASE_REL + "/"), "final build source scope")
        reader.match(row)
    checks = reader.document(BASE_REL + "/evidence/local-check-results.json")
    require(checks.get("schema") == 1 and checks.get("status") == "PASS"
            and checks.get("scope") == "E4_PURE_JVM_PROTOCOL_OWNERSHIP_ONLY"
            and checks.get("javacExit") == 0 and checks.get("javaExit") == 0
            and type(checks.get("assertions")) is int and checks["assertions"] > 0, "pure JVM evidence not PASS")
    expected_check_inputs = {
        BASE_REL + "/src/com/videokit/spike/e4/E4Protocol.java",
        BASE_REL + "/src/com/videokit/spike/e4/E4Broker.java",
        BASE_REL + "/tools/E4CoreSelfCheck.java",
    }
    require({row.get("path") for row in checks.get("inputs", [])} == expected_check_inputs, "JVM source inputs must be exact finite core/checker set")
    for row in checks["inputs"]: reader.match(row)
    commands = checks.get("commands")
    require(isinstance(commands, list) and len(commands) == 2 and all(c.get("exitCode") == 0 for c in commands), "two completed javac/java records required")
    for command in commands:
        require(command["log"].startswith(BASE_REL + "/evidence/"), "JVM log scope")
        reader.match({"path": command["log"], "bytes": command["bytes"], "sha256": command["sha256"]})
    java_lines = reader.data(commands[1]["log"]).decode("utf-8-sig").splitlines()
    java_results = [json.loads(line) for line in java_lines if line.startswith('{"scope":')]
    require(len(java_results) == 1 and java_results[0].get("scope") == checks["scope"]
            and java_results[0].get("result") == "PASS" and java_results[0].get("assertions") == checks["assertions"]
            and java_results[0].get("androidCodec") == "NOT_RUN" and java_results[0].get("binderIsolation") == "NOT_RUN",
            "JVM assertion count/scope must match preserved actual return log")
    audit = reader.document(BASE_REL + "/evidence/apk-audit.json")
    require(audit.get("schema") == 1 and audit.get("status") == "PASS" and audit.get("singleApk") is True, "APK identity audit not PASS")
    apks = audit.get("apks")
    require(isinstance(apks, list) and len(apks) == 2 and {a.get("role") for a in apks} == {"app-debug", "androidTest"}, "exactly one app APK plus instrumentation APK")
    app = next(a for a in apks if a["role"] == "app-debug")
    require(app.get("applicationId") == "com.videokit.app", "application ID changed")
    signer = None
    for apk in apks:
        require(apk["path"].startswith(BASE_REL + "/artifacts/") and apk["path"].endswith(".apk"), "APK artifact scope")
        reader.match(apk)
        require(apk.get("signingVerified") is True, "APK signing was not verified")
        cert = fingerprint(apk["signerCertificateSha256"])
        signer = cert if signer is None else signer
        require(cert == signer, "app/instrumentation certificate differs")
        report = reader.data(apk["signingReport"]).decode("utf-8-sig")
        digests = [fingerprint(m) for m in re.findall(r"certificate SHA-256 digest:\s*([0-9a-fA-F:]{64,95})", report)]
        require(cert in digests, "certificate fingerprint not in preserved apksigner report")
    libraries = audit.get("nativeLibraries")
    require(isinstance(libraries, list) and len(libraries) == 7, "seven unchanged native libraries required")
    require(len({n["entry"] for n in libraries}) == 7, "duplicate native library audit")
    with reader.archive(app["path"]) as archive:
        actual_libs = {n for n in archive.namelist() if n.startswith("lib/") and n.endswith(".so")}
        require(actual_libs == {n["entry"] for n in libraries}, "APK native library exact set")
        for lib in libraries:
            require(lib["apkPath"] == app["path"] and lib["upstreamPath"].startswith(BASE_REL + "/upstream-c14/native-libs/"), "native library provenance scope")
            data = reader.member(archive, lib["entry"])
            require(len(data) == lib["bytes"] and sha(data) == lib["sha256"], "APK native library mismatch")
            require(data == reader.data(lib["upstreamPath"]), "APK expanded/modified native library")
    sbom = reader.document(BASE_REL + "/evidence/sbom.json")
    require(sbom.get("bomFormat") == "CycloneDX" and isinstance(sbom.get("components"), list)
            and len(sbom["components"]) > 0, "SBOM missing components")
    plan = reader.document(BASE_REL + "/tools/device_plan.json")
    require(plan.get("schema") == 1 and plan.get("status") == "NOT_RUN", "device plan must remain NOT_RUN")
    return {"localAssertions": checks["assertions"], "buildAttempts": len(attempts),
            "signerCertificateSha256": signer, "apks": apks, "nativeLibraryCount": len(libraries),
            "androidExecution": "NOT_RUN", "nativeFaultExecution": "NOT_RUN", "devicePlan": "NOT_RUN"}


def write_new(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as output:
        output.write(data); output.flush(); os.fsync(output.fileno())


def inspect(root):
    root = Path(root).resolve()
    reader = Reader(root)
    sources = collect_sources(root)
    for name in sources:
        data = reader.data(name); check_private_payload(name, data)
    require(sum(len(reader.data(n)) for n in sources) <= MAX_ZIP_LOGICAL, "source logical package budget")
    upstream = check_copy_map(reader)
    facts = check_evidence(reader)
    return reader, sources, upstream, facts
