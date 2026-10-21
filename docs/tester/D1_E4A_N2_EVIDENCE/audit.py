"""Independent existing N2 receipt review only. No device calls or media reads."""
from pathlib import Path
import json,hashlib,re,struct
E=Path(__file__).parent
def sha(b):return hashlib.sha256(b).hexdigest()
rows=[]
for p in E.glob('*.json'):
    r=json.loads(p.read_bytes())
    if 'argv' not in r:continue
    assert r['ownership']=='RETURNED' and r['originalExitObserved'] and not r['creationUnknown'] and not r['terminatedOwnedChild']
    assert all(r[k] for k in ('stdinCloseReturned','sourceCloseReturned','writerReturned','flushReturned')) and r['stdinCloseError'] is None
    for stream in ('stdout','stderr'):
        s=r[stream];raw=bytes.fromhex(s['prefixHex']);assert not s['prefixTruncated'] and len(raw)==s['bytes'] and sha(raw)==s['sha256'] and s['closeReturned'] and s['error'] is None
    rows.append(dict(file=p.name,bytes=p.stat().st_size,sha256=sha(p.read_bytes()),exit=r['originalExitCode'],elapsedSeconds=r['elapsedSeconds'],stdoutBytes=r['stdout']['bytes'],stderrBytes=r['stderr']['bytes'],hostOwnership=r['ownership']))
assert len(rows)==8
pre=(E/'02-private-admission-stdout.txt').read_text();post=(E/'03-post-failure-private-state-stdout.txt').read_text()
assert 'BUDGET_DIR_ABSENT' in pre and 'OUTPUT_DIRECTORY_ABSENT' in pre and 'ORIGINAL_PENDING_ABSENT' in pre and 'ORIGINAL_PENDING_PRESENT' in post
ledger=post.split('METADATA_BEGIN|files/e4a_output_budget/ledger.bin\n',1)[1].split('METADATA_END|',1)[0].strip()+'\n';lines=ledger.splitlines();assert len(lines)==2
header=lines[0]+'\n';payload,chain=lines[1].rsplit(' ',1)
assert header=='E4A1 730a73e1-50e1-4198-a515-047104f00e31 4194304 2097152 128\n'
assert chain==sha((sha(header.encode())+' '+payload).encode()) and payload=='R 86cafdb3-0fc4-447d-920b-b19c884bf494 D1-E4A-N2-TABLET-20261017'
def metadata(name):
    part=post.split('NEW_METADATA|files/e4a_outputs/86cafdb3-0fc4-447d-920b-b19c884bf494'+name+'\n',1)[1].split('NEW_METADATA|',1)[0]
    lines=part.splitlines();n=int(lines[0]);b=bytes.fromhex(' '.join(lines[1:]));assert len(b)==n;return b
identity=metadata('.identity');journal=metadata('.journal')
class Reader:
    def __init__(self,b):self.b=b;self.i=0
    def read(self,n):b=self.b[self.i:self.i+n];assert len(b)==n;self.i+=n;return b
    def utf(self):n=struct.unpack('>H',self.read(2))[0];b=self.read(n);assert all(c<128 for c in b);return b.decode('ascii')
    def integer(self):return struct.unpack('>i',self.read(4))[0]
    def long(self):return struct.unpack('>q',self.read(8))[0]
d=Reader(identity);idfields=dict(magic=d.utf(),batch=d.utf(),budget=d.utf(),task=d.utf(),epoch=d.long(),generation=d.long(),serviceInstance=d.utf(),hostUid=d.integer(),serviceUid=d.integer(),outputTask=d.utf());assert d.i==len(identity)
j=Reader(journal);jfields=dict(magic=j.integer(),task=j.utf(),state=j.integer(),epoch=j.utf(),granted=bool(j.read(1)[0]));assert j.i==len(journal) and jfields['state']==0 and jfields['granted']
inst=(E/'normalMp4SixRealFrames-instrumentation-stdout.txt').read_bytes();text=inst.decode();logs=(E/'normalMp4SixRealFrames-logcat-stdout.txt').read_text()
assert 'status=PENDING error=E4_REMOTE_PENDING received=0 inputs=0 outputs=0' in text and 'released=false' in text and 'Tests run: 1,  Failures: 1' in text
assert '24853:com.videokit.app' in logs and '24873:com.videokit.app:e4_codec' in logs and 'due to finished inst' in logs and 'E4_SOURCE_FRAME' not in logs
review=dict(status='FAIL_PENDING_DEPENDENTS_BLOCKED',dependentEncoderAdmitted=False,method='normalMp4SixRealFrames',batch='D1-E4A-N2-TABLET-20261017',originalReceipt='normalMp4SixRealFrames-instrumentation-stdout.txt',originalReceiptSha256=sha(inst),sourceFrames=0,encoderInputs=0,encoderOutputs=0,productResourcesReleased=False,budgetPending=True,settlementPresent=False,consumedSettledBytes=0,outstandingReservationBytes=2097152,independentRejectionAdmitted=False,cancelAdmitted=False,reason='Same service/Sink/stable ledger pending; no independent unknown-free capability session proven')
(E/'normalMp4SixRealFrames-independent-review.json').write_text(json.dumps(review,indent=2)+'\n')
out=dict(audit='PASS_ORIGINAL_EVIDENCE_INTEGRITY_NOT_PRODUCT_PASS',calls=rows,independentReview=review,identityRecord=idfields,journalRecord=jfields,identityBytes=len(identity),journalBytes=len(journal),fixtureFullHashBytesExecuted=698204,fixtureFullHashBytesPlannedAllFour=1475003924,extraFixtureHashBytes=0,productCpuRequestsObserved=0,productCpuReadBytesObserved=0,productOutputHashBytesProven=0,productOutputProtocolSha='UNKNOWN',hostClientOwnersReturned=True,activeHostClientHandles=[],productProtocolOwnership='UNKNOWN_NOT_RELEASED_DESPITE_SYSTEM_PROCESS_EXIT',methods={'normalMp4SixRealFrames':'FAIL','normalAviSixRealFrames':'BLOCKED','capabilityDenialDoesNotOpenSource':'BLOCKED','cancelRejectsWrongEpochOversizeAndLateFrame':'BLOCKED'},methodArtifactBytes=sum(p.stat().st_size for p in E.glob('normalMp4SixRealFrames*') if p.is_file()),batchArtifactBytesBeforeAudit=sum(p.stat().st_size for p in E.iterdir() if p.is_file()))
(E/'receipt-audit.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
