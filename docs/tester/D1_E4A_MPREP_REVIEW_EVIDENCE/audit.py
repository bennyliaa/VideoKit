"""Read frozen identities and saved local evidence only. No production import/test/device/media access."""
from pathlib import Path
import json,hashlib,io,zipfile
R=Path(__file__).resolve().parents[3];B=R/'docs/coder/d1e4amprep';E=Path(__file__).parent
def sha(b):return hashlib.sha256(b).hexdigest()
sraw=(B/'evidence/mprep-freeze.json').read_bytes();assert sha(sraw)=='96f62df6a902a8b20eab73d97de63ea82321ceffe42c15f983530a245c3b2660';s=json.loads(sraw)
m=json.loads((R/s['manifest']['path']).read_bytes());assert len(m['files'])==163 and len(s['immutable'])==165
for row in s['immutable']:
    p=R/row['path'];b=p.read_bytes();assert not p.is_symlink() and len(b)==row['bytes'] and sha(b)==row['sha256']
z=(R/s['sourceZip']['path']).read_bytes();assert sha(z)=='5c43f62ec601971427ae66bda0fe451c563018c81679c5c07d2f425bb7c01047'
with zipfile.ZipFile(io.BytesIO(z)) as a:
    assert len(a.infolist())==163 and set(a.namelist())=={r['path'] for r in m['files']}
    for row in m['files']:assert sha(a.read(row['path']))==row['sha256']
for name in ('exact_process.py','command_response.py','stream_base64.py'):assert (B/'tools'/name).read_bytes()==(R/'docs/coder/d1e4at6/tools'/name).read_bytes()
proto=(R/'docs/coder/d1e4at6/tools/private_commands.py').read_text().replace('D1-E4A-T6P-TABLET-20261017','D1-E4A-MPREP-TABLET-20261017').replace('E4T6P_TABLET_20261017_ONCE','E4AMPREP_TABLET_20261017_ONCE').replace('files/e4_diag_T6P_TABLET_20261017_once','files/e4_mprep_TABLET_20261017_once')
assert proto==(B/'tools/t6_protocol.py').read_text()
c=json.loads((B/'evidence/local-check-results.json').read_bytes());assert c['assertions']==len(c['checks'])==37 and all(x['passed'] for x in c['checks']) and len(c['records'])==48
def output(r):
    for stream in ('stdout','stderr'):
        d=r[stream];raw=bytes.fromhex(d['prefixHex']);assert not d['prefixTruncated'] and len(raw)==d['bytes'] and sha(raw)==d['sha256'] and d['closeReturned'] and d['error'] is None
    return bytes.fromhex(r['stdout']['prefixHex'])
for r in c['records']:output(r);assert r['ownership']=='RETURNED' and r['originalExitObserved'] and not r['creationUnknown']
u=c['isolatedUnknown'];assert len(u['originals'])==7 and u['retainedUntilInterpreterEnd']==1 and u['nextIoRefused'] and u['osExitNotCredited'] and not c['osExitCredited']
for r in u['originals']:output(r)
inner=u['originals'][-1];assert inner['ownership']=='UNKNOWN_RETAINED' and not inner['sourceCloseReturned'] and inner['rawSource']['actualRawCloseReturned']
cases=[]
for case in c['cases']:
    scope=Path(case['scope']);assert scope.resolve().is_relative_to(B/'evidence/local-main-001');r=case['result'];specs=json.loads((scope/'specs.json').read_bytes())
    assert [x['bytes'] for x in specs]==[65537,70001] and r['retainedLocalOwners']==0 and all(x<=1 for x in r['producerAttempts'].values())
    assert (scope/'files/e4_fixtures/basic.mp4.E4AN_PREP01_81407_a790f44f.keep').read_bytes()==b'OWN_ARCHIVE'
    if case['case']=='success':
        assert r['metadataCommands']==13 and r['receiptMetadataReads']==15 and r['mp4Dependency']['verifiedOriginalStages']==4
        for spec in specs:
            file=r['files'][spec['alias']];ref=file['ready'];raw=(scope/'receipts'/ref['file']).read_bytes();assert len(raw)==ref['bytes'] and sha(raw)==ref['sha256'];ready=json.loads(raw)
            assert ready['file']==spec and ready['evidence']==file['evidence'] and set(ready['originals'])=={'producer','temp','publish','final'}
            originals={}
            for stage,item in ready['originals'].items():
                rr=item['ref'];b=(scope/'receipts'/rr['file']).read_bytes();assert len(b)==rr['bytes'] and sha(b)==rr['sha256'];o=json.loads(b);output(o)
                assert o['argv']==item['expectedArgv'] and o['ownership']=='RETURNED' and o['originalExitCode']==0;originals[stage]=o
            prod=originals['producer'];assert prod['rawSource']['streamBytes']==spec['bytes'] and prod['rawSource']['streamSha256']==spec['sha256'] and prod['submittedBytes']==spec['encodedBytes']
            proof=ready['evidence'];assert proof['tempProof']['before']==proof['finalProof']['before']==proof['publication']['stamp'] and proof['finalProof']['sha']==spec['sha256']
            data=(scope/spec['final']).read_bytes();assert len(data)==spec['bytes'] and sha(data)==spec['sha256'] and not (scope/spec['temp']).exists()
    else:assert r['status']=='NOT_ADMITTED' and r['producerAttempts']['subtitle.avi']==0 and r['mp4Dependency'] is None
    cases.append(dict(case=case['case'],status=r['status'],metadata=r['metadataCommands'],attempts=r['producerAttempts'],firstFailure=r.get('firstFailure'),receiptReads=r['receiptMetadataReads'],receiptReadBytes=r['receiptMetadataReadBytes']))
for row in c['realRenames']:
    r=c['records'][row['recordIndex']];raw=output(r)
    if row['case']=='rename-real':assert r['originalExitCode']==0 and row['expectedStamp'].encode() in raw
    else:assert r['originalExitCode']!=0 and b'mvRc=0' in raw and b'T6_PUBLISHED|' not in raw
fixed=json.loads((B/'tools/fixed-media-manifest.json').read_bytes());prior=json.loads((B/'reference/future-media-plan.json').read_bytes())
for f,old in zip(fixed['files'],prior['files']):assert f['source']==old['source'] and f['bytes']==old['sourceBytesFromFrozenMetadata'] and f['sha256']==old['sourceSha256FromFrozenMetadata'] and f['encodedBytes']==4*((f['bytes']+2)//3)<1073741824
out=dict(status='PASS',scope='FROZEN_IDENTITY_AND_RECORDED_LOCAL_EVIDENCE_ONLY',sourceFiles=163,immutableFiles=165,zipBytes=len(z),recordedAssertions=37,topLevelOriginalRecords=48,isolatedInnerOriginalRecords=7,isolatedHistoricalUnknownOwners=1,osExitCredited=False,cases=cases,initialRequiredKiB=(736803758+67108864+5+1023)//1024,aviRequiredKiB=(736454656+67108864+5+1023)//1024,hostRawReadBudget=1473607516,wireBytes=982405016,deviceHashBudget=1473607516,logCap=8388608,liveProductionInFlight=[],testerAdbCalls=0,testerFakeReruns=0,testerRealMediaStatReadHash=0,testerGradle=0)
(E/'identity-and-recorded-evidence-audit.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
