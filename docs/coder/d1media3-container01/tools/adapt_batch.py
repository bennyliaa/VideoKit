from pathlib import Path
B=Path(__file__).resolve().parents[1];assert not (B/'evidence/media3-container01-freeze.json').exists(),'FROZEN'
for name in ['local_check.py','review_all.py','run_suites.py','build_candidate.ps1']:
 p=B/'tools'/name;s=p.read_text()
 s=s.replace("r'd1input-sink([0-9]{2})'","r'd1media3-container([0-9]{2})'")
 s=s.replace("'D1_INPUT_SINK'","'D1_MEDIA3_CONTAINER'")
 s=s.replace("'input-sink'+","'media3-container'+")
 s=s.replace('input-sink05','media3-container01')
 p.write_text(s,encoding='utf-8')
p=B/'app/build.gradle.kts';s=p.read_text().replace('versionCode = 5','versionCode = 6').replace('D1-INPUT-SINK05','D1-MEDIA3-CONTAINER01').replace(' implementation("androidx.media3:media3-muxer:1.9.3")',' implementation("androidx.media3:media3-muxer:1.9.3")\n implementation("androidx.media3:media3-extractor:1.9.3")');p.write_text(s)
p=B/'app/gradle.lockfile';s=p.read_text();lines=s.splitlines();base=next(l.split('=',1)[1] for l in lines if l.startswith('androidx.media3:media3-muxer:'))
lines += ['androidx.media3:media3-decoder:1.9.3='+base,'androidx.media3:media3-extractor:1.9.3='+base]
p.write_text('\n'.join([l for l in lines if l.startswith('#')]+sorted(l for l in lines if not l.startswith('#')))+'\n')
print('New batch tools and exact same-version locks prepared; no Gradle executed.')
