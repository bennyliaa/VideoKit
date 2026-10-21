"""Validate existing original receipts only, no device calls or content pulls."""
from pathlib import Path
import hashlib,json
E=Path(__file__).parent;r=json.loads((E/'result.json').read_bytes());rows=[];decoded={}
for row in r['records']:
    p=E/row['file'];v=json.loads(p.read_bytes())
    assert v['status']=='PROCESS_IO_COMPLETE_ONLY' and v['ownership']=='RETURNED' and v['originalExitCode']==0 and v['originalExitObserved'] and not v['errors'] and not v['creationUnknown']
    assert all(v[k] for k in ('flushReturned','stdinCloseReturned','sourceCloseReturned','writerReturned')) and v['stdinCloseError'] is None
    for stream in ('stdout','stderr'):
        s=v[stream];raw=bytes.fromhex(s['prefixHex']);assert not s['prefixTruncated'] and len(raw)==s['bytes'] and hashlib.sha256(raw).hexdigest()==s['sha256'] and s['closeReturned'] and s['error'] is None
        if stream=='stdout':decoded[row['stage']]=raw.decode('ascii');(E/(row['stage']+'-stdout.txt')).write_bytes(raw)
        else:assert not raw
    rows.append(dict(stage=row['stage'],file=row['file'],sha256=hashlib.sha256(p.read_bytes()).hexdigest(),recordBytes=p.stat().st_size,elapsedSeconds=v['elapsedSeconds'],stdoutBytes=v['stdout']['bytes'],stdoutSha256=v['stdout']['sha256'],stdinBytes=v['submittedBytes'],exit=0,ownership='RETURNED'))
assert len(rows)==7 and r['metadataCommands']==6 and r['producerAttempts']==1 and r['retainedLocalOwners']==0
assert r['status']=='ASCII_STREAM_DECODE_AND_RAW_SHA_VERIFIED_NOT_A_MEDIA_FIXTURE'
assert all(row['stdinBytes']==(344 if row['stage']=='one-base64-receiver' else 0) for row in rows)
rawsha='40aff2e9d2d8922e47afd4648e6967497158785fbd1da870e7110266bf944880';encsha='ab7727e21f4bbba6508dd72804d97435a78eb44a1e277af1c0f65a8522de382e'
s=r['rawSource'];assert s['prehash']['rawBytes']==s['streamBytes']==256 and s['expectedSha256']==s['prehash']['rawSha256']==s['streamSha256']==rawsha and s['actualRawCloseReturned'] and s['streamReachedDeclaredEnd']
assert r['encoding']['actualSubmittedBytes']==344 and r['encoding']['actualSubmittedSha256']==encsha
p=r['decoderProbe'];assert p['originalEndpointRc']=={'printf':'0','decoder':'0','od':'0'} and p['proof']['asciiBytes']=='4' and p['proof']['rawBytes']=='1' and p['proof']['hex'].strip()=='00'
assert len(decoded['one-byte-sequential-file-probe'].splitlines())==4
assert r['receiverObservation']==r['receiverProof'] and r['receiverProof']['BEGIN']['pid']==r['receiverProof']['END']['pid']=='23033' and r['receiverProof']['DECODE']=={'rc':'0'}
p=r['independentProof'];assert p['before']==p['after']=='64522,19424,256,10221,8180,1792206618' and p['sha']==rawsha
originals=[E/'attempt.json',E/'result.json']+[E/row['file'] for row in rows]
out=dict(audit='PASS',records=rows,originalEvidenceBytes=sum(p.stat().st_size for p in originals),uidSnapshot=decoded['uid-snapshot'],probeOriginal=decoded['one-byte-sequential-file-probe'],receiverOriginal=decoded['one-base64-receiver'],independentProof=p,hostRawPrehashAndStreamBytes=512,encodedPrehashAndSubmittedBytes=688,actualEncodedStdin=344,normalStateFiles=2,normalStateBytes=5,normalPayloadBytes=256,deviceIndependentHashBytes=256,retainedLocalOwners=0,inFlight=[],priorRemoteOwnership='UNKNOWN_NOT_CLEARED',mediaOrProductRun=0,oldResidualAccess=0)
(E/'receipt-audit.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
