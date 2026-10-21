from pathlib import Path
import json,hashlib
B=Path(__file__).resolve().parents[1]
assert not (B/'evidence/build-main-001').exists()
paths=sorted(p for d in ['src','android','upstream','instrumentation','instrumentation-assets','notice-assets','app/src','gradle'] for p in (B/d).rglob('*') if p.is_file())+[B/x for x in ['app/build.gradle.kts','app/gradle.lockfile','settings.gradle.kts','settings-gradle.lockfile','build.gradle.kts','gradle.properties']]
(B/'evidence/build-input-pins.json').write_text(json.dumps([{'path':p.relative_to(B).as_posix(),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in paths],indent=2)+'\n',encoding='utf-8')
print(len(paths),'fixed inputs pinned; no dependency changes')
