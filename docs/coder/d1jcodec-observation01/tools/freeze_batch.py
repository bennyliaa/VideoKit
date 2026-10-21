"""Seal this failed bounded batch once; no compiler, JVM, media or device access."""
from pathlib import Path
import datetime, hashlib, json, zipfile
from review_materials import B,R,E,SEAL,MAIN,ARCHIVE,verify_inputs,sha
assert not SEAL.exists() and not ARCHIVE.exists()
result=verify_inputs()
paths=sorted([p for p in B.rglob('*') if p.is_file()]+[MAIN])
assert not any(p.suffix.lower() in {'.mp4','.mov','.mkv','.avi','.wav','.mp3','.srt','.dll','.exe','.so','.pyc'} for p in paths)
rows=[{'path':p.relative_to(R).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in paths]
with zipfile.ZipFile(ARCHIVE,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for p in paths: z.write(p,p.relative_to(R).as_posix())
with zipfile.ZipFile(ARCHIVE) as z:
    assert z.testzip() is None and len(z.namelist())==len(rows)
    for x in rows: assert hashlib.sha256(z.read(x['path'])).hexdigest()==x['sha256']
total=sum(x['bytes'] for x in rows)+ARCHIVE.stat().st_size
assert total<64*1024*1024
seal={'frozenUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'FROZEN_BUILT_AUDIT_FORK_METADATA_VALIDATION_BLOCKED_HELPER_FACTORY_CONTEXT_FAILURE','files':rows,'archive':{'path':ARCHIVE.relative_to(R).as_posix(),'bytes':ARCHIVE.stat().st_size,'sha256':sha(ARCHIVE)},'totalMaterialAndArchiveBytesExcludingSeal':total,'validation':result,'scope':'Source/JAR/class/metadata-only failed attempt preserved. No rerun, actual media, old owner, device or product integration action.'}
SEAL.write_text(json.dumps(seal,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
assert total+SEAL.stat().st_size<64*1024*1024
print(json.dumps({'seal':str(SEAL),'sealSha256':sha(SEAL),'files':len(rows),'archive':seal['archive'],'totalBytesIncludingSeal':total+SEAL.stat().st_size,'validation':result},ensure_ascii=False))
