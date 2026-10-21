from pathlib import Path
import json,hashlib
B=Path(__file__).resolve().parents[1];R=B.parents[2];sources=[]
if (B/'evidence/e13e-freeze.json').exists():raise SystemExit('Frozen')
for folder in ['src','android','upstream-c14','gradle','app/src','fixture/src','checks','binding']:sources += [p for p in (B/folder).rglob('*') if p.is_file()]
for folder in [B,B/'app',B/'fixture']:sources += [p for p in folder.iterdir() if p.is_file() and (p.suffix in ['.kts','.properties','.lockfile'] or p.name in ['gradlew','gradlew.bat','fixture-signing.p12'])]
sources += [B/'tools/build_local.ps1'];rows=[]
for p in sorted(set(sources)):
 raw=p.read_bytes();rows.append(dict(path=p.relative_to(R).as_posix(),bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest()))
(B/'evidence/final-build-inputs.json').write_text(json.dumps(dict(scope='E13E corrected actual checks/com source root and original ACK; one final affected offline build',files=rows,fixtureKeyNotDistributed=True),indent=2)+'\n')
print('E13E corrected build snapshot',len(rows))
