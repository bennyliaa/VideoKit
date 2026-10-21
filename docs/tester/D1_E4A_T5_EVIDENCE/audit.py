"""Read existing frozen files/receipts only. No production imports, subprocesses or test reruns."""
from pathlib import Path
import hashlib,json,zipfile,io
R=Path(__file__).resolve().parents[3];B=R/'docs/coder/d1e4at5';E=Path(__file__).parent
def sha(b):return hashlib.sha256(b).hexdigest()
sealraw=(B/'evidence/ascii-freeze.json').read_bytes();assert sha(sealraw)=='425c53957f6733eda7c23d3cbb81251c31ddd20c3ab4da5a87187ff799291363'
s=json.loads(sealraw);m=json.loads((R/s['manifest']['path']).read_bytes());assert len(m['files'])==88 and len(s['immutable'])==90
for row in s['immutable']:
    p=R/row['path'];assert not p.is_symlink();b=p.read_bytes();assert len(b)==row['bytes'] and sha(b)==row['sha256']
z=(R/s['sourceZip']['path']).read_bytes();assert sha(z)=='32f5bb3d90c41491b7251f66e75b88798f6489c127f3e9cea92cb784f3de6eb8'
with zipfile.ZipFile(io.BytesIO(z)) as a:
    assert set(a.namelist())=={r['path'] for r in m['files']} and len(a.infolist())==88
    for row in m['files']:assert sha(a.read(row['path']))==row['sha256']
assert (B/'tools/exact_process.py').read_bytes()==(R/'docs/coder/d1e4at4/tools/exact_process.py').read_bytes()
assert (B/'tools/command_response.py').read_bytes()==(R/'docs/coder/d1e4at4/tools/command_response.py').read_bytes()
assert sha((B/'reference/product-freeze.json').read_bytes())=='a7fb8c9b4af7aab8f93f4300b7f4dd090a7d8b2759b42b42d0207244932d663d'
c=json.loads((B/'evidence/local-check-results.json').read_bytes());assert c['assertions']==len(c['checks'])==51 and all(x['passed'] for x in c['checks'])
def record(r):
    for stream in ('stdout','stderr'):
        d=r[stream];raw=bytes.fromhex(d['prefixHex']);assert not d['prefixTruncated'] and len(raw)==d['bytes'] and sha(raw)==d['sha256'] and d['closeReturned'] and d['error'] is None
    return bytes.fromhex(r['stdout']['prefixHex'])
assert len(c['records'])==33
for r in c['records']:
    record(r);assert r['ownership']=='RETURNED' and r['originalExitObserved'] and not r['creationUnknown']
u=c['isolatedCloseUnknown'];inner=u['originalRecord'];record(inner)
assert inner['ownership']=='UNKNOWN_RETAINED' and not inner['sourceCloseReturned'] and inner['rawSource']['actualRawCloseReturned'] and u['retainedUntilInterpreterEnd']==1 and u['nextIoRefused'] and u['unknownNotClearedByOsExit']
assert any('stage=decoder|rc=7' in record(r).decode('ascii','ignore') and r['originalExitCode']==0 for r in c['records'])
cases=[]
for case in c['cases']:
    name=case['case'];p=B/'evidence/local-main-001'/name;r=json.loads((p/'receipts/result.json').read_bytes());assert r==case['result']
    assert r['producerAttempts']==1 and r['retainedLocalOwners']==0 and r['priorRemoteOwnership']=='UNKNOWN_NOT_CLEARED'
    assert r['rawSource']['prehash']['rawBytes']==r['rawSource']['streamBytes']==256 and r['encoding']['actualSubmittedBytes']==344
    target=(p/'private/payload256.bin').read_bytes();assert (p/'own-old26.bin').read_bytes()==bytes(range(26))
    if name=='normal':assert target==bytes(range(256)) and r['independentProof']['sha']==sha(target) and r['metadataCommands']==6
    elif name=='decoder-nonzero':assert target==b'' and r['receiverObservation']['DECODE']=={'rc':'7'} and r['receiverProof'] is None
    elif name=='short-exit0':assert target==bytes(range(26)) and r['receiverProof'] is None
    elif name=='wrong-sha':assert len(target)==256 and sha(target)!=sha(bytes(range(256))) and r['independentProof'] is None
    cases.append(dict(case=name,status=r['status'],firstFailure=r.get('firstFailure'),metadata=r['metadataCommands'],targetBytes=len(target),targetSha256=sha(target)))
for r in c['lengths']:assert r['encodedBytes']==4*((r['rawBytes']+2)//3)
future=json.loads((B/'tools/future-media-plan.json').read_bytes());assert not future['executionAuthorized'] and not future['mediaCliAvailable'] and not future['sourceMetadataRevalidated']
assert sum(f['encodedBytes'] for f in future['files'])==future['wireBytesTotal']==982405016
assert all(f['encodedBytes']==4*((f['sourceBytesFromFrozenMetadata']+2)//3) for f in future['files'])
out=dict(status='PASS',scope='FROZEN_IDENTITY_AND_RECORDED_EVIDENCE_ONLY',sourceFiles=88,immutableFiles=90,zipBytes=len(z),assertionsRecorded=51,topLevelOriginalRecords=33,isolatedInnerRecords=1,isolatedUnknownHistoricalOwners=1,unknownOsExitCredited=False,cases=cases,lengths=c['lengths'],rawDiagnosticBytes=256,encodedDiagnosticBytes=344,encodedMediaWireDesignBytes=982405016,deviceSupport='UNKNOWN_NOT_RUN',testerAdbCalls=0,testerFakeOrProbeReruns=0,testerMediaStatReadHash=0,testerGradle=0,inFlight=[])
(E/'identity-and-recorded-evidence-audit.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
