from pathlib import Path
import hashlib,json,shutil
B=Path(__file__).resolve().parents[1];R=B.parents[2];A=R/'docs/coder/d1e13a'
p=B/'tools/build_local.ps1';assert not p.exists();p.write_text((A/'tools/build_local.ps1').read_text(encoding='utf-8-sig').replace('d1e13a','d1e13e').replace('e13a-freeze.json','e13e-freeze.json').replace('E13A','E13E'),encoding='utf-8')
p=B/'tools/audit_artifacts.py';t=(A/'tools/audit_artifacts.py').read_text();t=t.replace('D1-20261018-E13A','D1-20261018-E13E').replace("versionCode='17'","versionCode='18'").replace('D1-E13A-ACTIVATION','D1-E13E-ACTIVATION').replace('VideoKit E13A binding return Debug','VideoKit E13E lifecycle Debug');p.write_text(t,encoding='utf-8')
sources=[]
for folder in ['src','android','upstream-c14','gradle','app/src','fixture/src','checks','binding']:sources += [p for p in (B/folder).rglob('*') if p.is_file()]
for folder in [B,B/'app',B/'fixture']:sources += [p for p in folder.iterdir() if p.is_file() and (p.suffix in ['.kts','.properties','.lockfile'] or p.name in ['gradlew','gradlew.bat','fixture-signing.p12'])]
sources += [B/'tools/build_local.ps1'];rows=[]
for p in sorted(set(sources)):
 raw=p.read_bytes();rows.append(dict(path=p.relative_to(R).as_posix(),bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest()))
(B/'evidence/final-build-inputs.json').write_text(json.dumps(dict(scope='E13E one necessary offline app/test/fixture build; excluded JVM substitutes pinned but not compiled into APK',files=rows,fixtureKeyNotDistributed=True),indent=2)+'\n')
print('E13E final APK build inputs',len(rows))
