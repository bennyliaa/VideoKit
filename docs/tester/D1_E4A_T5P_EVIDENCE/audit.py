"""Existing original receipts only; no device calls or probe replay."""
from pathlib import Path
import json,hashlib
E=Path(__file__).parent;rows=[]
for n in ('00-features.json','01-original-context.json','02-one-byte-no-file-decoder-probe.json'):
    p=E/n;r=json.loads(p.read_bytes())
    assert r['ownership']=='RETURNED' and r['originalExitCode']==0 and r['originalExitObserved'] and not r['creationUnknown'] and not r['errors']
    assert all(r[k] for k in ('stdinCloseReturned','sourceCloseReturned','writerReturned','flushReturned')) and r['stdinCloseError'] is None and r['submittedBytes']==r['sourceStreamReadBytes']==0
    for stream in ('stdout','stderr'):
        s=r[stream];b=bytes.fromhex(s['prefixHex']);assert not s['prefixTruncated'] and len(b)==s['bytes'] and hashlib.sha256(b).hexdigest()==s['sha256'] and s['closeReturned'] and s['error'] is None
        if n.startswith('02'):(E/('probe-original-'+stream+'.txt')).write_bytes(b)
    rows.append(dict(file=n,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),recordBytes=p.stat().st_size,exit=r['originalExitCode'],elapsedSeconds=r['elapsedSeconds'],ownership=r['ownership'],stdoutBytes=r['stdout']['bytes'],stderrBytes=r['stderr']['bytes']))
p=json.loads((E/'02-one-byte-no-file-decoder-probe.json').read_bytes());raw=bytes.fromhex(p['stdout']['prefixHex']);lines=raw.decode('ascii').splitlines()
assert len(lines)==4 and lines[0].startswith('TT5_PROBE_RC|') and lines[1]=='decoder|rc=0'
assert lines[2]=='T5_PROBE_RC|E4T5P_TABLET_20261017_ONCE|stage=od|rc=0'
assert lines[3]=='T5_PROBE|E4T5P_TABLET_20261017_ONCE|uid=10221|pwd=/data/user/0/com.videokit.app|pipelineRc=0|fd3CloseRc=0|hex= 00'
r=json.loads((E/'result.json').read_bytes());assert r['firstFailure']=='MARKER_IDENTITY' and r['metadataCommands']==3 and r['producerAttempts']==r['retainedLocalOwners']==0
originals=[E/n for n in ('attempt.json','result.json','00-features.json','01-original-context.json','02-one-byte-no-file-decoder-probe.json')]
out=dict(audit='PASS',scope='ORIGINAL_RECEIPTS_ONLY',records=rows,probeStdoutSha256=hashlib.sha256(raw).hexdigest(),probeOriginalLines=lines,firstFailure='MARKER_IDENTITY',finding='E4AT5P-F01_SHARED_FD3_ENDPOINT_MARKER_FRAMING',metadataCommands=3,producerAttempts=0,originalEvidenceBytes=sum(p.stat().st_size for p in originals),retainedLocalOwners=0,inFlight=[],priorRemoteOwnership='UNKNOWN_NOT_CLEARED',probeOverallAdmission='FAIL_MARKER_FRAMING',decoderIndividualRc='NOT_INDEPENDENTLY_FRAMED',lastPipelineRc=0,fd3CloseRc=0,lastHex='00',deviceWrites=0,hostRawPayloadReadBytes=0)
(E/'receipt-audit.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
