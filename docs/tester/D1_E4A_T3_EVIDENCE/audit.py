"""Read-only identity and existing offline-record audit. No production imports or replay."""
from pathlib import Path
import hashlib,json,zipfile,datetime
R=Path(__file__).resolve().parents[3];E=Path(__file__).resolve().parent;B=R/'docs/coder/d1e4at3'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
seal=B/'evidence/features-freeze.json';assert sha(seal)=='4fbeef4948c8615e406b0e3a778d1c499c7a8c6fc133dc75822972a5a38e6628'
s=json.loads(seal.read_text());rows=s['immutable']
for row in rows:
 p=R/row['path'];assert p.stat().st_size==row['bytes'] and sha(p)==row['sha256']
expected={r['path']:r for r in json.loads((R/s['manifest']['path']).read_text())['files']}
with zipfile.ZipFile(R/s['sourceZip']['path']) as z:
 assert len(z.namelist())==len(expected) and set(z.namelist())==set(expected)
 for name,row in expected.items():
  raw=z.read(name);assert len(raw)==row['bytes'] and hashlib.sha256(raw).hexdigest()==row['sha256']
original=B/'reference/features-original-stdout.txt';raw=original.read_bytes()
assert len(raw)==220 and sha(original)=='05d62e60d4eb5bfe83dcc67dcdb28f4139980080ae50761f2f31b2b84eb5dcce'
assert raw==(R/'docs/tester/D1_E4A_T2P_EVIDENCE/features-original-stdout.txt').read_bytes()
assert sha(R/'docs/tester/D1_E4A_T2P_DIAGNOSTIC_REPORT_V1.0.md')=='4b46b978c34b1527121d37069f4f31c8009e9f0cbf3170370d412adc8c7c8d50'
assert sha(B/'tools/exact_process.py')==sha(R/'docs/coder/d1e4at2/tools/exact_process.py')=='f43cbf6d78611b0c441b0b438322e484a8513587ee93de4c32fdee67b84f988d'
old=(R/'docs/coder/d1e4at2/tools/remote_command.py').read_text();new=(B/'tools/remote_command.py').read_text()
assert new==old.replace('files/e4_diag_T2P_TABLET_20261017_once','files/e4_diag_T3P_TABLET_20261017_once').replace('E4T2P_TABLET_20261017_ONCE','E4T3P_TABLET_20261017_ONCE')
checks=json.loads((B/'evidence/local-check-results.json').read_text());assert checks['assertions']==len(checks['checks'])==67 and all(q['passed'] for q in checks['checks'])
assert all(checks[k]==0 for k in ['processStarts','adbCalls','deviceRuns','sourcePayloadBytesRead','gradleRuns','realMediaBytesRead'])
assert len(checks['integrations'])==8 and all(q['result']['priorRemoteOwnership']=='UNKNOWN_NOT_CLEARED' for q in checks['integrations'])
facts={'at':datetime.datetime.now().astimezone().isoformat(),'integrity':'PASS','sourceFiles':len(expected),'immutableFiles':len(rows),'sourceZip':s['sourceZip'],'recordedOfflineAssertions':67,'recordedOfflineIntegrations':8,'actualCheckChildProcesses':0,'raw220ByteIdentity':sha(original),'originalFeatureFinding':'SUPPORTED_FIXED_STATIC_AND_EXISTING_OFFLINE_ONLY','T1PumpByteIdentical':True,'remoteBuildersOnlyNewIdentityAndLineEndings':True,'remainingDeviceFormats':'UNKNOWN_SYNTHETIC_CONTRACT_ONLY','replayExecutedByTester':False,'adbCalls':0,'deviceRuns':0,'realMediaReads':0,'gradleRuns':0,'inFlight':[]}
(E/'identity-and-offline-evidence-audit.json').write_text(json.dumps(facts,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'integrity':'PASS','sourceFiles':len(expected),'immutableFiles':len(rows),'recordedAssertions':67,'deviceRuns':0}))
