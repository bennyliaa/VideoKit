import hashlib,json
from pathlib import Path
p=Path(__file__).parent
rows=[]
for name in ('00-features.json','01-shell-existing-base.json'):
    raw=(p/name).read_bytes();r=json.loads(raw)
    for stream in ('stdout','stderr'):
        s=r[stream];b=bytes.fromhex(s['prefixHex'])
        assert not s['prefixTruncated'] and len(b)==s['bytes'] and hashlib.sha256(b).hexdigest()==s['sha256']
        assert s['closeReturned'] and s['error'] is None
    assert r['ownership']=='RETURNED' and r['originalExitObserved'] and not r['creationUnknown']
    assert all(r[k] for k in ('flushReturned','stdinCloseReturned','sourceCloseReturned','writerReturned'))
    assert r['submittedBytes']==0 and r['sourceStreamReadBytes']==0 and r['stdinCloseError'] is None
    rows.append(dict(file=name,recordBytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),exit=r['originalExitCode'],elapsedSeconds=r['elapsedSeconds'],ownership=r['ownership'],stdoutBytes=r['stdout']['bytes'],stderrBytes=r['stderr']['bytes']))
assert rows[0]['exit']==0 and rows[1]['exit']==1
result=json.loads((p/'result.json').read_text(encoding='utf-8'))
assert result['metadataCommands']==2 and result['pushAttempts']==result['copyAttempts']==result['retainedLocalOwners']==0
assert result['hostSourcePrehashBytes']==0 and result['stageProof'] is result['copyProof'] is result['internalProof'] is None
originals=[p/n for n in ('attempt.json','00-features.json','01-shell-existing-base.json','result.json')]
out=dict(audit='PASS',scope='HOST_EXISTING_RECEIPTS_ONLY_NO_ADB',records=rows,originalEvidenceBytes=sum(f.stat().st_size for f in originals),retainedLocalOwners=0,inFlight=[],remoteOwnership='UNKNOWN_NOT_CLEARED',specificFailedPredicate='UNKNOWN_NO_OUTPUT')
(p/'receipt-audit.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
print(json.dumps(out,indent=2))
