from pathlib import Path
import hashlib,json,tarfile,sys
root=Path(sys.argv[1]).resolve();base=root/'docs/coder/d1c09';up=base/'upstream';out=up/'source'
assert '[GNUPG:] VALIDSIG FCF986EA15E6E293A5644F10B4322F04D67658D8 ' in (base/'evidence/ffmpeg-signature.log').read_text(encoding='utf-8-sig')
with tarfile.open(up/'ffmpeg-8.0.3.tar.xz','r:xz') as tar:
 for m in tar:
  if m.isdir():continue
  assert m.isfile(),m.name
  p=(out/m.name).resolve();assert p.is_relative_to(out.resolve()),m.name
  p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(tar.extractfile(m).read())
source=out/'ffmpeg-8.0.3';assert (source/'VERSION').read_text(encoding='utf-8').strip()=='8.0.3'
def row(p):return {'path':p.relative_to(root).as_posix(),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
result={'version':'8.0.3','source_url':'https://ffmpeg.org/releases/ffmpeg-8.0.3.tar.xz','archive':row(up/'ffmpeg-8.0.3.tar.xz'),'key_fingerprint':'FCF986EA15E6E293A5644F10B4322F04D67658D8','patches':[],'files':[row(p) for p in sorted(source.rglob('*')) if p.is_file()]}
(base/'evidence/ffmpeg-source-identity.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print('Verified official source',result['archive'],'files',len(result['files']))
