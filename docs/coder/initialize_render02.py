from pathlib import Path
import shutil,json,hashlib
R=Path('D:/CodexProjects/VideoKit').resolve();S=R/'docs/coder/d1render01';B=R/'docs/coder/d1render02'
assert not B.exists();B.mkdir()
rows=[]
for d in ['src','android','upstream','app/src','gradle','native-libs','notice-assets','fixture-assets','checks','reused-native-source']:
    for p in sorted((S/d).rglob('*')):
        if not p.is_file():continue
        q=B/p.relative_to(S);q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,q)
        rows.append({'source':p.relative_to(R).as_posix(),'path':q.relative_to(B).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
for name in ['build.gradle.kts','settings.gradle.kts','gradle.properties','local.properties','gradlew.bat','app/build.gradle.kts','app/gradle.lockfile']:
    p=S/name;q=B/name;q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,q);rows.append({'source':p.relative_to(R).as_posix(),'path':q.relative_to(B).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
# Immutable build-only repository reuse. A private physical copy avoids aliasing frozen bytes.
shutil.copytree(S/'offline-maven',B/'offline-maven')
for name in ['local_check.py','VerifyApk.java']:
    q=B/'tools'/name;q.parent.mkdir(exist_ok=True);shutil.copyfile(S/'tools'/name,q)
    if q.suffix=='.py':q.write_text(q.read_text(encoding='utf-8').replace('d1render01','d1render02'),encoding='utf-8')
T=R/'docs/tester/D1_RENDER01_OFFLINE_REVIEW_EVIDENCE/checks'
shutil.copytree(T,B/'review-regression')
(B/'evidence').mkdir();(B/'evidence/reused-render01-inputs.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'reused_source_files':len(rows),'native_rebuilds':0,'fixture_bytes_unchanged':True,'new_directory':str(B)}))
