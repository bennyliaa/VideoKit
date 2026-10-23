"""New SELF01 bounded source/evidence files; no IO on import."""
from pathlib import Path
import json,hashlib,os
FILES=[];READS=[];UNKNOWN=[]
def enc(v):return (json.dumps(v,ensure_ascii=False,separators=(',',':'))+'\n').encode()
def sha(b):return hashlib.sha256(b).hexdigest()
def no_links(p):
    for q in [Path(p).absolute(),*Path(p).absolute().parents]:
        if q.exists() and q.stat().st_file_attributes&1024:raise ValueError('REPARSE')
def read(p,cap=536870912):
    p=Path(p);no_links(p);f=None
    try:
        f=p.open('rb');FILES.append(f);size=os.fstat(f.fileno()).st_size
        if size>cap:raise ValueError('READ_BOUND')
        v=f.read(size+1)
        if len(v)!=size:raise ValueError('SOURCE_SIZE_CHANGED_DURING_READ')
        if len(v)>cap:raise ValueError('READ_BOUND')
        READS.append({'path':str(p),'bytes':len(v),'sha256':sha(v)})
        if len(READS)>8192 or sum(r['bytes'] for r in READS)>4294967296:raise ValueError('SOURCE_BUDGET')
        return v
    finally:
        if f is not None:
            try:f.close()
            except BaseException as e:UNKNOWN.extend([f,e,e.__traceback__]);raise
def load(p,cap=1048576):return json.loads(read(p,cap).decode('utf-8-sig'))
def save(p,v):
    p=Path(p);no_links(p);p.parent.mkdir(parents=True,exist_ok=True);data=enc(v)
    if len(data)>1048576:raise ValueError('EVIDENCE_SPLIT_FIRST')
    f=None
    try:
        f=p.open('xb');FILES.append(f)
        if f.write(data)!=len(data):raise IOError('SHORT_EVIDENCE_WRITE')
        f.flush()
    finally:
        if f is not None:
            try:f.close()
            except BaseException as e:UNKNOWN.extend([f,e,e.__traceback__]);raise
    return sha(data)
def known():return not UNKNOWN and all(f.closed for f in FILES)
