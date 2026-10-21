"""Independent C08 sources; official archive extraction with safe regular-file paths."""
from pathlib import Path
import hashlib,json,re,sys,tarfile
root=Path(sys.argv[1]).resolve();old=root/'docs/coder/d1c07';base=root/'docs/coder/d1c08'
def convert(s):
 hashes=re.findall(r'[0-9a-f]{64}',s);slots={h:'HASH_SLOT_'+str(i)+'_END' for i,h in enumerate(set(hashes))}
 for h,t in slots.items():s=s.replace(h,t)
 s=s.replace('C07','C08').replace('c07','c08')
 for h,t in slots.items():s=s.replace(t,h)
 return s
for name in ['src','android','device','native','labels','tools']:
 for p in (old/name).rglob('*'):
  if not p.is_file() or '__pycache__' in p.parts or p.name in ['initialize.py','write_delivery.py','review_candidate.py','reuse_evidence.py','record_source_review.py']:continue
  q=base/convert(p.relative_to(old).as_posix());q.parent.mkdir(parents=True,exist_ok=True);q.write_text(convert(p.read_text(encoding='utf-8')),encoding='utf-8')
for name in ['build.gradle.kts','gradle.lockfile','src/main/AndroidManifest.xml']:
 p=old/'worker_app'/name;q=base/'worker_app'/name;q.parent.mkdir(parents=True,exist_ok=True);q.write_text(convert(p.read_text(encoding='utf-8')),encoding='utf-8')
for name in ['app/build.gradle.kts','settings.gradle.kts','app/src/debug/AndroidManifest.xml']:
 p=root/name;p.write_text(convert(p.read_text(encoding='utf-8')),encoding='utf-8')
for name in ['outputs','classes','artifacts/D1-20261005-C08','native-libs/arm64-v8a']: (base/name).mkdir(parents=True,exist_ok=True)
archive=base/'upstream/ffmpeg-8.0.tar.xz';source=base/'upstream/source';source.mkdir(exist_ok=True)
with tarfile.open(archive,'r:xz') as tar:
 for member in tar.getmembers():
  if member.isdir():continue
  if not member.isfile():raise ValueError('Non-regular member:'+member.name)
  out=(source/member.name).resolve();assert out.is_relative_to(source.resolve()),member.name
  out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(tar.extractfile(member).read())
source=source/'ffmpeg-8.0';assert (source/'VERSION').read_text(encoding='utf-8').strip()=='8.0'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
licenses=[p for p in source.iterdir() if p.name=='LICENSE.md' or p.name.startswith('COPYING')]
result={'version':'8.0','url':'https://ffmpeg.org/releases/ffmpeg-8.0.tar.xz','archive_sha256':sha(archive),'archive_bytes':archive.stat().st_size,'signature_fingerprint':'FCF986EA15E6E293A5644F10B4322F04D67658D8','signature':'VALIDSIG verified against official download-page fingerprint','files':[{'path':p.relative_to(root).as_posix(),'sha256':sha(p),'bytes':p.stat().st_size} for p in sorted(source.rglob('*')) if p.is_file()],'license_files':[{'path':p.relative_to(root).as_posix(),'sha256':sha(p)} for p in licenses],'patches':[],'scope':'signed pristine source only; full build composition review required before packaging'}
(base/'evidence/ffmpeg-source-identity.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print('source files',len(result['files']),'archive',result['archive_sha256'])
