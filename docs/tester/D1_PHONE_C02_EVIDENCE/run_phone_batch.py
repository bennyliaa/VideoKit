"""Run only the authorized frozen C02 phone methods; no build or package changes."""
import datetime
import json
import pathlib
import subprocess
import sys

BASE = pathlib.Path(__file__).resolve().parent
ADB = r"D:\Android\SDK\platform-tools\adb.exe"
SERIAL = "U4999DLBNRR89DOR"
METHODS = ["playbackMp4", "playbackAviSrt", "playbackMkvAss",
           "isolatedWorkerDeathAndTimeout", "offlinePlatformFaceFeasibility"]
if len(sys.argv) > 1:
    requested = sys.argv[1:]
    if any(method not in METHODS for method in requested):
        raise ValueError("Unapproved method")
    METHODS = requested
record_file = BASE / "phone-batch-results.json"
results = json.loads(record_file.read_text(encoding="utf-8")) if record_file.exists() else []
for method in METHODS:
    command = [ADB, "-s", SERIAL, "shell", "am", "instrument", "-w", "-e", "class",
               "com.videokit.spike.c02.C02DeviceTests#" + method,
               "com.videokit.app.test/androidx.test.runner.AndroidJUnitRunner"]
    start = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat()
    print("START " + method + " " + start, flush=True)
    try:
        process = subprocess.run(command, capture_output=True, timeout=180)
        output = (process.stdout + process.stderr).decode("utf-8", errors="replace")
        status = "PASS" if process.returncode == 0 and "OK (1 test)" in output and "FAILURES!!!" not in output else "FAIL"
        code = process.returncode
    except subprocess.TimeoutExpired as error:
        output = ((error.stdout or b"") + (error.stderr or b"")).decode("utf-8", errors="replace")
        output += "\nTESTER_TIMEOUT_180_SECONDS; no broad device kill/cleanup performed\n"
        status, code = "BLOCKED", None
    (BASE / (method + ".log")).write_text(output, encoding="utf-8")
    end = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat()
    results.append({"candidateId": "D1-20261005-C02", "serial": SERIAL, "method": method,
                    "start": start, "end": end, "processExitCode": code, "result": status,
                    "log": method + ".log", "command": command,
                    "scope": "Assertions in frozen method only; no visual/audio quality inference"})
    (BASE / "phone-batch-results.json").write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print("END " + method + " " + status + " " + end, flush=True)
    if status == "BLOCKED":
        break
