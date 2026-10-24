from pathlib import Path
import json,hashlib,sys,time
R=Path(__file__).resolve().parent;rev=sys.argv[1];H=R/rev.lower();receipt=R/(rev.lower()+'-freeze.json');assert not receipt.exists()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
r=json.loads((H/'evidence/result.json').read_bytes());assert r['revisionReturnProof']['allOriginalsProven'] and r['auxOriginalsReturned'] and not any(r['custody'].values())
profile=json.loads((H/'reference/profile07.json').read_bytes());assert all(sha(H/x['path'])==x['sha256'] for x in profile)
es=[dict(path=p.relative_to(H).as_posix(),bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(H.rglob('*')) if p.is_file()]
data=dict(revision=rev,files=es,bytes=sum(x['bytes'] for x in es),allPassed=r['allPassed'],allOriginalsProven=True,batchElapsed=r['batchElapsed'],sourceSealSha256=sha(H/'reference/runner-source-seal.json'),profileSha256=sha(H/'reference/profile07.json'),noRerun=True)
receipt.write_bytes((json.dumps(data,ensure_ascii=False,indent=2)+'\n').encode());print(json.dumps(dict(revision=rev,files=len(es),bytes=data['bytes'],allPassed=r['allPassed'],originalsProven=True)))
