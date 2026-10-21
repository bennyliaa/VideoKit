"""Task-private binary transfer through the already-running local ADB server."""
import hashlib, json, pathlib, socket, struct, subprocess, time
ROOT = pathlib.Path(r"D:\CodexProjects\VideoKit")
BASE = pathlib.Path(__file__).resolve().parent
SERIAL = "U4999DLBNRR89DOR"
FIXTURES = [
 ("basic.mp4", "imgs_and_videos/videos/sample.mp4", "720957c94b3665ff97bcc2f59ad5407c5ca54f566b59865723be9eecc0a6a1f9"),
 ("subtitle.avi", "02_videos/History.Channel.How.Bruce.Lee.Changed.The.World.720p.HDTV.X264-DVSKY.avi", "3f0bf3e9fa6f24130a546fee5be98ba43274959cdc0df82a2ee74306ad4ef52f"),
 ("subtitle.srt", "02_videos/History.Channel.How.Bruce.Lee.Changed.The.World.720p.HDTV.X264-DVSKY.chs.srt", "d3a44be0636d9ec4d5a2782d1a5d6ceb7141d7bf4f8df2f693d9850f867144bd"),
 ("large.mkv", "03_large_files/large_video_over_2GiB.mkv", "28af909ce8d9f9e1431253715e07bbfa9024aa8963882a000ee7a15807622b26")]
def receive(sock, count):
    result = bytearray()
    while len(result) < count:
        piece = sock.recv(count - len(result))
        if not piece: raise RuntimeError("ADB stream closed")
        result.extend(piece)
    return bytes(result)
def service(sock, command):
    data = command.encode()
    sock.sendall(f"{len(data):04x}".encode() + data)
    result = receive(sock, 4)
    if result != b"OKAY":
        length = int(receive(sock, 4), 16)
        raise RuntimeError(receive(sock, length).decode(errors="replace"))
records = []
for alias, relative, expected in FIXTURES:
    source = (ROOT / "test_media" / relative).resolve()
    assert source.is_relative_to((ROOT / "test_media").resolve())
    destination = "files/d1_c02_fixtures/" + alias
    digest = hashlib.sha256(); total = 0; last = time.monotonic()
    print("START " + alias, flush=True)
    with socket.create_connection(("127.0.0.1", 5037), timeout=60) as sock:
        service(sock, "host:transport:" + SERIAL)
        service(sock, "shell,v2,raw:run-as com.videokit.app sh -c 'cat > " + destination + "'")
        with source.open("rb") as stream:
            while block := stream.read(32768):
                digest.update(block); total += len(block)
                sock.sendall(struct.pack("<BI", 0, len(block)) + block)
                if time.monotonic() - last > 20:
                    print(f"PROGRESS {alias} {total}/{source.stat().st_size}", flush=True); last = time.monotonic()
        sock.sendall(struct.pack("<BI", 4, 0))
        errors = bytearray()
        while True:
            channel, size = struct.unpack("<BI", receive(sock, 5))
            payload = receive(sock, size)
            if channel == 2: errors.extend(payload)
            if channel == 3:
                if not payload or payload[0] != 0: raise RuntimeError(errors.decode(errors="replace"))
                break
    device = subprocess.check_output([r"D:\Android\SDK\platform-tools\adb.exe", "-s", SERIAL,
                  "shell", "run-as", "com.videokit.app", "sha256sum", destination]).decode().split()[0]
    row = {"alias": alias, "bytes": total, "expectedSha256": expected,
           "hostSha256": digest.hexdigest(), "deviceSha256": device,
           "match": digest.hexdigest() == device == expected, "transport": "local ADB shell v2 raw socket"}
    records.append(row)
    (BASE / "fixture-hash-check.json").write_text(json.dumps(records, indent=2), encoding="utf-8")
    print("END " + alias + " hashMatch=" + str(row["match"]), flush=True)
    if not row["match"]: raise RuntimeError("Fixture identity mismatch; do not test")
