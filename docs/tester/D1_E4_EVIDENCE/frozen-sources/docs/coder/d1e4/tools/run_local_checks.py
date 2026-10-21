"""Default inspect. --run performs the two bounded pure-Java compilation/rule commands only."""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import subprocess
from e4_package import BASE_REL, Reader, canonical, require, sha, write_new

INPUTS = (
    BASE_REL + "/src/com/videokit/spike/e4/E4Protocol.java",
    BASE_REL + "/src/com/videokit/spike/e4/E4Broker.java",
    BASE_REL + "/tools/E4CoreSelfCheck.java",
)
SCOPE = "E4_PURE_JVM_PROTOCOL_OWNERSHIP_ONLY"


def command(argv, log, root, timeout):
    record = {"argv": [str(arg) for arg in argv], "log": log.relative_to(root).as_posix(),
              "beganUtc": datetime.now(timezone.utc).isoformat()}
    # Logs are direct files, not unbounded PIPE collectors. Inputs print one finite summary only.
    with log.open("xb") as output:
        try:
            completed = subprocess.run(argv, cwd=root, stdin=subprocess.DEVNULL, stdout=output,
                                       stderr=subprocess.STDOUT, timeout=timeout, check=False)
            record["exitCode"] = completed.returncode
        except subprocess.TimeoutExpired:
            record["exitCode"] = -1; record["error"] = "OWNED_LOCAL_JVM_PROCESS_TIMEOUT"
        except OSError as problem:
            record["exitCode"] = -1; record["error"] = type(problem).__name__
        output.flush(); os.fsync(output.fileno())
    require(log.stat().st_size <= 4 * 1024 * 1024, "local check output exceeded finite budget")
    data = log.read_bytes(); record.update({"bytes": len(data), "sha256": sha(data),
                                          "endedUtc": datetime.now(timezone.utc).isoformat()})
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=str(Path(__file__).resolve().parents[4]))
    parser.add_argument("--run", action="store_true")
    parser.add_argument("--attempt", default="main-001")
    parser.add_argument("--repair", action="store_true")
    parser.add_argument("--java-home", default="D:/Android/Android Studio/jbr")
    args = parser.parse_args(); root = Path(args.root).resolve(); base = root / BASE_REL
    reader = Reader(root); inputs = [reader.row(name) for name in INPUTS]
    require(re.fullmatch(r"[a-z][a-z0-9-]{0,47}", args.attempt), "attempt ID format")
    final = base / "evidence/local-check-results.json"
    require(not (base / "evidence/e4-freeze.json").exists(), "E4 frozen; checks must not mutate it")
    preview = {"schema": 1, "mode": "RUN" if args.run else "INSPECT", "scope": SCOPE,
               "inputs": inputs, "androidExecution": "NOT_RUN", "nativeFaultExecution": "NOT_RUN"}
    if not args.run:
        print(canonical(preview).decode("utf-8")); return
    java_home = Path(args.java_home).resolve()
    javac = java_home / "bin/javac.exe"; java = java_home / "bin/java.exe"
    require(javac.is_file() and java.is_file(), "existing local JDK unavailable; downloading is forbidden")
    require(not final.exists(), "local check final evidence already exists; no duplicate passing run")
    attempt = base / "evidence/jvm-attempts" / args.attempt
    classes = base / "selfcheck" / args.attempt / "classes"
    require(not attempt.exists() and not classes.exists(), "attempt already consumed")
    gate = base / "evidence/jvm-main-reservation.json"
    if not args.repair:
        require(not gate.exists(), "exactly one main JVM check; necessary repairs require --repair")
        write_new(gate, canonical({"schema": 1, "attempt": args.attempt, "state": "RESERVED", "scope": SCOPE}))
    else:
        require(gate.exists(), "repair requires preserved original main attempt")
        prior = sorted((base / "evidence/jvm-attempts").glob("*/attempt-result.json"))
        require(prior and all(json.loads(p.read_text(encoding="utf-8"))["status"] == "FAIL" for p in prior), "repair requires a failed local attempt")
    attempt.mkdir(parents=True, exist_ok=False); classes.mkdir(parents=True, exist_ok=False)
    compile_record = command([str(javac), "-encoding", "UTF-8", "--release", "11", "-Xmaxerrs", "20",
                              "-d", str(classes), *[str(root / name) for name in INPUTS]],
                             attempt / "javac.log", root, 120)
    records = [compile_record]; result = None
    if compile_record["exitCode"] == 0:
        java_record = command([str(java), "-cp", str(classes), "com.videokit.spike.e4.E4CoreSelfCheck"],
                              attempt / "java.log", root, 30)
        records.append(java_record)
        if java_record["exitCode"] == 0:
            lines = (attempt / "java.log").read_text(encoding="utf-8-sig").splitlines()
            try:
                summaries = [json.loads(line) for line in lines if line.startswith("{\"scope\":")]
                require(len(summaries) == 1, "exactly one finite JVM result required")
                result = summaries[0]
                require(result.get("scope") == SCOPE and result.get("result") == "PASS"
                        and result.get("androidCodec") == "NOT_RUN" and result.get("binderIsolation") == "NOT_RUN"
                        and type(result.get("assertions")) is int and result["assertions"] > 0, "JVM result scope mismatch")
            except (ValueError, TypeError):
                result = None; java_record["error"] = "JVM_RESULT_SCOPE_OR_FORMAT_INVALID"
    passed = result is not None
    evidence = {"schema": 1, "scope": SCOPE, "status": "PASS" if passed else "FAIL",
                "attempt": args.attempt, "kind": "REPAIR" if args.repair else "MAIN",
                "javacExit": compile_record["exitCode"],
                "javaExit": records[1]["exitCode"] if len(records) == 2 else None,
                "assertions": result["assertions"] if passed else 0, "inputs": inputs,
                "commands": records, "androidExecution": "NOT_RUN", "nativeFaultExecution": "NOT_RUN"}
    write_new(attempt / "attempt-result.json", canonical(evidence))
    if passed: write_new(final, canonical(evidence))
    print(canonical(evidence).decode("utf-8"))
    if not passed: raise SystemExit(1)


if __name__ == "__main__":
    main()
