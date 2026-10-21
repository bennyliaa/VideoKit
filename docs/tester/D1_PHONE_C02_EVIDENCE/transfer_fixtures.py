"""Phone-only transfer workaround: shell v2 -T gives remote EOF/exit acknowledgement."""
import hashlib
import base64
import json
import pathlib
import subprocess
import time

ROOT = pathlib.Path(r"D:\CodexProjects\VideoKit")
BASE = pathlib.Path(__file__).resolve().parent
PREFIX = [r"D:\Android\SDK\platform-tools\adb.exe", "-s", "U4999DLBNRR89DOR"]
FIXTURES = [
    ("basic.mp4", "imgs_and_videos/videos/sample.mp4", "720957c94b3665ff97bcc2f59ad5407c5ca54f566b59865723be9eecc0a6a1f9"),
    ("subtitle.avi", "02_videos/History.Channel.How.Bruce.Lee.Changed.The.World.720p.HDTV.X264-DVSKY.avi", "3f0bf3e9fa6f24130a546fee5be98ba43274959cdc0df82a2ee74306ad4ef52f"),
    ("subtitle.srt", "02_videos/History.Channel.How.Bruce.Lee.Changed.The.World.720p.HDTV.X264-DVSKY.chs.srt", "d3a44be0636d9ec4d5a2782d1a5d6ceb7141d7bf4f8df2f693d9850f867144bd"),
    ("large.mkv", "03_large_files/large_video_over_2GiB.mkv", "28af909ce8d9f9e1431253715e07bbfa9024aa8963882a000ee7a15807622b26"),
]
records = []
for alias, relative, expected in FIXTURES:
    source = (ROOT / "test_media" / relative).resolve()
    assert source.is_relative_to((ROOT / "test_media").resolve())
    destination = "files/d1_c02_fixtures/" + alias
    process = subprocess.Popen(PREFIX + ["shell", "-T", "run-as", "com.videokit.app", "sh", "-c", "'base64 -d > " + destination + "'"],
                               stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    digest = hashlib.sha256()
    total = 0
    last = time.monotonic()
    print("START " + alias, flush=True)
    with source.open("rb") as stream:
        while block := stream.read(3 * 256 * 1024):
            digest.update(block)
            process.stdin.write(base64.b64encode(block))
            total += len(block)
            if time.monotonic() - last > 20:
                print(f"PROGRESS {alias} {total}/{source.stat().st_size}", flush=True)
                last = time.monotonic()
    process.stdin.close()
    process.stdin = None
    _, error = process.communicate(timeout=180)
    if process.returncode:
        raise RuntimeError(error.decode(errors="replace"))
    host_hash = digest.hexdigest()
    device_hash = subprocess.check_output(PREFIX + ["shell", "run-as", "com.videokit.app", "sha256sum", destination]).decode().split()[0]
    record = {"alias": alias, "bytes": total, "expectedSha256": expected,
              "hostSha256": host_hash, "deviceSha256": device_hash,
              "match": host_hash == device_hash == expected, "transport": "adb shell -T run-as sh base64 -d; ASCII stdin workaround"}
    records.append(record)
    (BASE / "fixture-hash-check.json").write_text(json.dumps(records, indent=2), encoding="utf-8")
    print("END " + alias + " hashMatch=" + str(record["match"]), flush=True)
    if not record["match"]:
        raise RuntimeError("Fixture identity mismatch; do not test")
