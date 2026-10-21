"""Read existing frozen E5A evidence only. No Java/model/Gradle/ADB/media execution."""
from pathlib import Path
import json,hashlib,zipfile
R=Path(__file__).resolve().parents[3];B=R/'docs/coder/d1e5a';E=Path(__file__).parent
def sha(b):return hashlib.sha256(b).hexdigest()
raw=(B/'evidence/e5a-freeze.json').read_bytes();assert sha(raw)=='f2d7a6905eaf67c1979ae29c4e15ea9975417a15e3a421f4197b31288a70a841';s=json.loads(raw);assert len(s['immutableFiles'])==2247
for row in s['immutableFiles']:
    p=R/row['path'];b=p.read_bytes();assert not p.is_symlink() and len(b)==row['bytes'] and sha(b)==row['sha256']
m=json.loads((R/s['sourceManifest']['path']).read_bytes());assert len(m['files'])==2243
z=R/s['sourceZip']['path'];assert sha(z.read_bytes())=='9c4b8bb12701e0de331e43075b9218037aa76e491acdaca1f5ce5c2ef3aef00e'
with zipfile.ZipFile(z) as a:
    assert len(a.infolist())==2243 and a.namelist()==[r['path'] for r in m['files']]
    for row in m['files']:b=a.read(row['path']);assert len(b)==row['bytes'] and sha(b)==row['sha256']
c=json.loads((B/'evidence/local-check-results.json').read_bytes());assert c['status']=='PASS'
for row in c['inputs']:assert sha((R/row['path']).read_bytes())==row['sha256']
assert [r['assertions'] for r in c['summaries']]==[48,3,2,128]
logs=[]
for cmd in c['commands']:
    assert cmd['exitCode']==0
    row=cmd['log'];b=(R/row['path']).read_bytes();assert len(b)==row['bytes'] and sha(b)==row['sha256'];logs.append(dict(path=row['path'],text=b.decode('utf-8','replace')))
assert any('"assertions":89' in row['text'] for row in logs)
allroot=Path(c['commands'][-1]['argv'][-1]);assert allroot.is_relative_to(B)
late=[]
for mode in ('healthy','completion-force','completion-close','completion-close-held','dir-force','dir-force-held','dir-close','dir-close-held'):
    d=allroot/mode;writer=json.loads((d/'writer.log').read_text().strip());deny=json.loads((d/'new-host-after-exit.log').read_text().strip());observe=json.loads((d/'fresh-observation.log').read_text().strip())
    assert deny['status']==observe['status']=='PASS' and not deny['observe'] and observe['observe']
    old=writer['result'];assert old==('ABORTED_SETTLED' if mode=='healthy' or mode.endswith('-held') else 'BLOCKED')
    assert writer['retainedOriginalOperations']==(0 if old=='ABORTED_SETTLED' else 1)
    completion=d/'case/e4a_output_budget/N2-e5-recovery.complete';assert completion.read_text().startswith('E5_N2_ABORTED_SETTLED ')
    if mode.endswith('-held'):
        assert (d/'case/fault-entered').read_text()=='originalDescriptorOpen=true activeRecovery=1'
        assert json.loads((d/'new-host-while-held.log').read_text())['status']=='PASS' and json.loads((d/'observer-while-held.log').read_text())['expectedLive']
    late.append(dict(mode=mode,originalWriterResult=old,originalRetainedAtExit=writer['retainedOriginalOperations'],coldHostDenied=True,freshObservationPassedAfterWriterExit=True,heldActualFdProof=mode.endswith('-held')))
build=json.loads((B/'evidence/build-results.json').read_bytes());last=build['attempts'][-1];assert last['id']=='repair-002' and last['exitCode']==0 and all('--offline' in x['arguments'] for x in build['attempts'])
snapshot=(B/'evidence/final-build-inputs.json').read_bytes();assert sha(snapshot)==last['inputSnapshotSha256']=='10d7f7eb36b2c685620b2f214148d1bdc9ec4c0ff4b1b41bcd1402d1be8cb76d'
for row in json.loads(snapshot)['files']:assert sha((R/row['path']).read_bytes())==row['sha256']
a=json.loads((B/'evidence/apk-audit.json').read_bytes());assert a['status']=='PASS' and len(a['nativeLibraries'])==7
assert [r['sha256'] for r in a['apks']]==['d490b9abcbc5f47074ff2e20e8163f26ab0c200b452a8c187524a6caf98eca33','4b088c49ce864d029555c664208b60bb0a04fdaf19d095a7465b3a98b3ce324e']
for apk in a['apks']:assert apk['signerCertificateSha256']=='5e841a04968f3f790f6996ca5e286d8c2734338542486909f9a136717dde808f' and apk['signingVerified']
with zipfile.ZipFile(R/a['apks'][0]['path']) as new,zipfile.ZipFile(R/'docs/coder/d1e5/artifacts/D1-20261017-E5/final/app-debug.apk') as old:
    for lib in a['nativeLibraries']:assert sha(new.read(lib['entry']))==sha(old.read(lib['entry']))==lib['sha256']
assert (B/'app/gradle.lockfile').read_bytes()==(R/'docs/coder/d1e5/app/gradle.lockfile').read_bytes()
obs=(B/'src/com/videokit/spike/e4/E5AFinalObservation.java').read_text();adapter=(B/'android/com/videokit/spike/e4/E5N2RecoveryAndroid.java').read_text();lease=(B/'android/com/videokit/spike/c14/AndroidLease.java').read_text()
assert 'owner=lock(out.resolve(E5N2Recovery.TASK+".owner"));lease=lock' in obs
metadata=obs.split('private void metadata()',1)[1].split('private E4Owned',1)[0];assert '.owner' not in metadata
assert 'AndroidLease.exclusiveInto(p,h)' in adapter and 'ParcelFileDescriptor.MODE_CREATE|ParcelFileDescriptor.MODE_READ_WRITE' in lease
out=dict(integrity='PASS',sourceFiles=2243,immutableFiles=2247,sourceZip=s['sourceZip'],assertionsFinalCount=270,parentE5ACount=128,nestedChildAssertionsNotAdded=True,lateCases=late,finalJvmLogs=logs,buildAttempts=[dict(id=x['id'],exit=x['exitCode']) for x in build['attempts']],finalBuildSnapshotSha256=sha(snapshot),apks=a['apks'],nativeByteIdentical=7,dependencyDelta=0,oldE5F01='STATIC_FIX_AND_RECORDED_LATE_CASES_VERIFIED',oldE5F02='STATIC_FIX_AND_RECORDED_LIFECYCLE_VERIFIED',newStaticFinding='E5A-F01_OBSERVER_CREATES_MISSING_ORIGINAL_OWNER_OR_LEASE',newFindingDeviceOrModelReproduced=False,readonlyQueryTechnicallySupportedForSeparateDispatch=True,observerAndProductAdmitted=False,testerAdbCalls=0,testerMediaStatReadHash=0,testerJavaGradleOrModelRuns=0,inFlight=[])
(E/'identity-and-recorded-static-audit.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps(out,ensure_ascii=False,indent=2))
