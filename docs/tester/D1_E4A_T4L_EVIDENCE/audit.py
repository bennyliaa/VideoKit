from pathlib import Path
import json,hashlib,re
E=Path(__file__).resolve().parent;out={'audit':'PASS','records':{},'deviceCommands':2,'deviceWrites':0,'fileContentReads':0,'retainedLocalOwners':0,'inFlight':[]}
for name in ('shell','app'):
    p=E/(name+'-original.json');r=json.loads(p.read_text());assert r['ownership']=='RETURNED' and r['originalExitCode']==0 and not r['errors']
    assert all(r[k] for k in ('originalExitObserved','stdinCloseReturned','sourceCloseReturned','writerReturned','flushReturned')) and r['submittedBytes']==0
    texts={}
    for stream in ('stdout','stderr'):
        s=r[stream];b=bytes.fromhex(s['prefixHex']);assert len(b)==s['bytes'] and hashlib.sha256(b).hexdigest()==s['sha256'] and not s['prefixTruncated'] and s['closeReturned'] and s['error'] is None
        texts[stream]=b.decode();(E/(name+'-'+stream+'.txt')).write_bytes(b)
    lines=texts['stdout'].splitlines();assert lines[-1]=='CHECKLIST_END'
    begins=[l.split('|')[1] for l in lines if l.startswith('STEP_BEGIN|')]
    ends=[re.fullmatch(r'STEP_END\|([^|]+)\|rc=(\d+)',l).groups() for l in lines if l.startswith('STEP_END|')]
    assert begins==[e[0] for e in ends] and len(set(begins))==len(begins)
    out['records'][name]=dict(sha256=hashlib.sha256(p.read_bytes()).hexdigest(),recordBytes=p.stat().st_size,identity=lines[0],steps=dict((k,int(v)) for k,v in ends),stepCount=len(ends),elapsedSeconds=r['elapsedSeconds'],stdoutBytes=r['stdout']['bytes'],stderrBytes=r['stderr']['bytes'])
out['allEvidenceBytesBeforeAuditOutput']=sum(p.stat().st_size for p in E.iterdir() if p.is_file())
(E/'audit-summary.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
