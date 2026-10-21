"""Clone immutable C06 implementation into independent C07 working candidate."""
from pathlib import Path
import shutil,re,sys,zipfile,subprocess,hashlib,json
root=Path(sys.argv[1]).resolve();old=root/'docs/coder/d1c06';base=root/'docs/coder/d1c07'
def convert(s):
 hashes=re.findall(r'[0-9a-f]{64}',s);slots={h:'HASH_SLOT_'+str(i)+'_END' for i,h in enumerate(set(hashes))}
 for h,t in slots.items():s=s.replace(h,t)
 s=s.replace('C06','C07').replace('c06','c07')
 for h,t in slots.items():s=s.replace(t,h)
 return s
for name in ['src','android','device','native','labels','tools']:
 for p in (old/name).rglob('*'):
  if not p.is_file() or '__pycache__' in p.parts or p.name in ['initialize.py','prepare_final_review.py','write_delivery.py','review_candidate.py']:continue
  q=base/convert(p.relative_to(old).as_posix());q.parent.mkdir(parents=True,exist_ok=True);q.write_text(convert(p.read_text(encoding='utf-8')),encoding='utf-8')
for name in ['build.gradle.kts','gradle.lockfile','src/main/AndroidManifest.xml']:
 p=old/'worker_app'/name;q=base/'worker_app'/name;q.parent.mkdir(parents=True,exist_ok=True);q.write_text(convert(p.read_text(encoding='utf-8')),encoding='utf-8')
for name in ['app/build.gradle.kts','settings.gradle.kts','app/src/debug/AndroidManifest.xml']:
 p=root/name;p.write_text(convert(p.read_text(encoding='utf-8')),encoding='utf-8')
for name in ['evidence','outputs','classes','artifacts/D1-20261005-C07']: (base/name).mkdir(parents=True,exist_ok=True)
cache=Path('C:/Users/benny/.gradle/caches/modules-2/files-2.1/androidx.media3');rows=[]
for module in ['media3-exoplayer','media3-extractor','media3-common']:
 aar=next((cache/module/'1.9.3').rglob('*.aar'));out=base/'outputs'/(module+'.jar')
 with zipfile.ZipFile(aar) as z:out.write_bytes(z.read('classes.jar'))
 rows.append({'origin':str(aar),'aar_sha256':hashlib.sha256(aar.read_bytes()).hexdigest(),'classes_sha256':hashlib.sha256(out.read_bytes()).hexdigest()})
cmd=['D:/Android/Android Studio/jbr/bin/javap.exe','-classpath',str(base/'outputs/media3-exoplayer.jar'),'-c','-p','androidx.media3.exoplayer.source.BundledExtractorsAdapter']
r=subprocess.run(cmd,capture_output=True,text=True,encoding='utf-8');assert r.returncode==0,r.stderr
(base/'evidence/bundled-extractors-adapter-javap.txt').write_text(r.stdout,encoding='utf-8')
(base/'evidence/approved-jar-provenance.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
print('C07 independent sources and approved cache inspection prepared')
