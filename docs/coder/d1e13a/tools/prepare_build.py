from pathlib import Path
import hashlib,json
B=Path(__file__).resolve().parents[1];R=B.parents[2]
p=B/'tools/build_local.ps1';t=p.read_text(encoding='utf-8-sig').replace('d1e11','d1e13').replace('E11_LOCAL_GRADLE_ONLY','E13_LOCAL_GRADLE_ONLY').replace('e11-freeze.json','e13-freeze.json')
if "':fixture:assembleDebug'" not in t:t=t.replace("':app:assembleDebugAndroidTest',", "':app:assembleDebugAndroidTest', ':fixture:assembleDebug',")
p.write_text(t,encoding='utf-8',newline='\n')
sources=[]
for folder in ['src','android','upstream-c14','gradle','app/src','fixture/src','checks','binding']:
 sources += [p for p in (B/folder).rglob('*') if p.is_file()]
for folder in [B,B/'app',B/'fixture']:
 sources += [p for p in folder.iterdir() if p.is_file() and (p.suffix in {'.kts','.properties','.lockfile'} or p.name in {'gradlew','gradlew.bat','fixture-signing.p12'})]
sources += [B/'tools/build_local.ps1']
rows=[]
for p in sorted(set(sources)):
 b=p.read_bytes();rows.append({'path':p.relative_to(R).as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()})
(B/'evidence/final-build-inputs.json').write_text(json.dumps({'schema':1,'scope':'E13A single affected offline app/test/ordinary-UID fixture build','files':rows,'signingKeyExternalLocalOnly':'fixture-signing.p12; hash pinned, not distributed'},indent=2)+'\n',encoding='utf-8')
print('E13 build inputs',len(rows))
