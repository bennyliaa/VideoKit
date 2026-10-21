from pathlib import Path
import hashlib,json
B=Path(__file__).resolve().parents[1];R=B.parents[2];sources=[]
assert not (B/'evidence/e13f-freeze.json').exists()
for folder in ['src','android','upstream-c14','binding','checks','gradle','app/src','fixture/src']:sources += [p for p in (B/folder).rglob('*') if p.is_file()]
for folder in [B,B/'app',B/'fixture']:sources += [p for p in folder.iterdir() if p.is_file() and (p.suffix in ['.kts','.properties','.lockfile'] or p.name in ['gradlew','gradlew.bat','fixture-signing.p12'])]
sources += [B/'tools/build_local.ps1'];rows=[]
for p in sorted(set(sources)):
 raw=p.read_bytes();rows.append(dict(path=p.relative_to(R).as_posix(),bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest()))
(B/'evidence/final-build-inputs.json').write_text(json.dumps(dict(scope='E13F focused F01/F02/F03 offline app/test/fixture build',files=rows,fixtureKeyExternalOnly=True),indent=2)+'\n')
print('E13F build inputs',len(rows))
