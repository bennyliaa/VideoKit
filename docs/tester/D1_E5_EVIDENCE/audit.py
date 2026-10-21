"""E5 frozen identities and existing evidence only; no Java/Gradle/ADB/test/media execution."""
from pathlib import Path
import json,hashlib,zipfile,re
R=Path(__file__).resolve().parents[3];B=R/'docs/coder/d1e5';E=Path(__file__).parent
def sha(b):return hashlib.sha256(b).hexdigest()
raw=(B/'evidence/e5-freeze.json').read_bytes();assert sha(raw)=='c80c6d32fcbef17fbbffbe5a369dd26cbca72f004ea08fe4d7765dbfc83e568a';s=json.loads(raw)
assert len(s['immutableFiles'])==452
for row in s['immutableFiles']:
    p=R/row['path'];b=p.read_bytes();assert not p.is_symlink() and len(b)==row['bytes'] and sha(b)==row['sha256']
m=json.loads((R/s['sourceManifest']['path']).read_bytes());assert len(m['files'])==448
z=R/s['sourceZip']['path'];assert sha(z.read_bytes())=='7e74d97e5cc3e28f62a289ce75b97dad3c30490086390851b89f5a2a99812026'
with zipfile.ZipFile(z) as a:
    assert len(a.infolist())==448 and a.namelist()==[r['path'] for r in m['files']]
    for row in m['files']:b=a.read(row['path']);assert len(b)==row['bytes'] and sha(b)==row['sha256']
checks=json.loads((B/'evidence/local-check-results.json').read_bytes());assert checks['status']=='PASS'
for row in checks['inputs']:assert sha((R/row['path']).read_bytes())==row['sha256']
logs=[]
for c in checks['commands']:
    assert c['exitCode']==0
    if c.get('log'):
        row=c['log'];b=(R/row['path']).read_bytes();assert len(b)==row['bytes'] and sha(b)==row['sha256'];logs.append(dict(path=row['path'],text=b.decode('utf-8','replace')))
assert [x['assertions'] for x in checks['summaries']]==[48,3,2] and [x['retainedOperations'] for x in checks['summaries']]==[0,1,1]
assert any('89' in row['text'] for row in logs)
build=json.loads((B/'evidence/build-results.json').read_bytes());assert build['attempts'][-1]['id']=='repair-004' and build['attempts'][-1]['exitCode']==0
snapshot=(B/'evidence/final-build-inputs.json').read_bytes();assert sha(snapshot)==build['attempts'][-1]['inputSnapshotSha256']
for row in json.loads(snapshot)['files']:assert sha((R/row['path']).read_bytes())==row['sha256']
assert all('--offline' in c['arguments'] for c in build['attempts'])
audit=json.loads((B/'evidence/apk-audit.json').read_bytes());assert audit['status']=='PASS' and len(audit['apks'])==2 and len(audit['nativeLibraries'])==7
assert [a['sha256'] for a in audit['apks']]==['05d382960573399c6cba78302171f9c058ac9df599b63268d59a6ab3f21d00f8','d93ad2de80ed7b523258cdb7005d97010f8d6950b43a6f9dade9e46f2dddbcc5']
for apk in audit['apks']:
    assert apk['signerCertificateSha256']=='5e841a04968f3f790f6996ca5e286d8c2734338542486909f9a136717dde808f' and apk['signingVerified']
    assert sha((R/apk['path']).read_bytes())==apk['sha256']
old=R/'docs/coder/d1e4a/artifacts/D1-20261017-E4A/final/app-debug.apk'
with zipfile.ZipFile(R/audit['apks'][0]['path']) as new,zipfile.ZipFile(old) as prev:
    for lib in audit['nativeLibraries']:assert sha(new.read(lib['entry']))==lib['sha256']==sha(prev.read(lib['entry']))
assert (B/'app/gradle.lockfile').read_bytes()==(R/'docs/coder/d1e4a/app/gradle.lockfile').read_bytes()
diff=json.loads((B/'evidence/sbom-difference.json').read_bytes());assert diff['coordinates']==35 and diff['coordinateDelta']==diff['nativeDelta']==[]
recovery=(B/'src/com/videokit/spike/e4/E5N2Recovery.java').read_text();budget=(B/'src/com/videokit/spike/e4/E4OutputBudget.java').read_text();session=(B/'android/com/videokit/spike/e4/E4Session.java').read_text();tests=(B/'app/src/androidTest/java/com/videokit/spike/e4/E4DeviceTests.java').read_text()
# Static path witnesses only: no production functions or fault injections run here.
assert recovery.index('stage="ARCHIVE_PENDING_MARKER"')<recovery.index('stage="DURABLE_COMPLETION"')<recovery.index('poisoned=mutated')
assert 'N2-e5-recovery.complete' in budget and 'E5N2Recovery.COMPLETE.equals' in budget
assert session.index('result.complete(report());',session.index('private void run()'))<session.index('owner.execute(this::continueOriginalCleanup)')
assert 'record(r);assertEquals("READY",r.status)' in tests
out=dict(integrity='PASS',scope='FROZEN_IDENTITIES_EXISTING_RECORDS_AND_STATIC_PATHS_ONLY',sourceFiles=448,immutableFiles=452,sourceZip=s['sourceZip'],finalModelAssertions=142,jvmLogs=logs,modelUnknownAtExit=[1,1],osExitNotCredited=True,buildAttempts=[dict(id=c['id'],exit=c['exitCode']) for c in build['attempts']],finalBuildSnapshotSha256=sha(snapshot),apks=audit['apks'],nativeIdentical=7,dependencyCoordinates=35,dependencyDelta=0,staticFindings=['E5-F01_COMPLETION_VISIBLE_BEFORE_FINAL_CLOSE_SYNC_CROSS_HOST_ADMISSION','E5-F02_FAILURE_RESULT_PRECEDES_ORIGINAL_CLEANUP_AND_TEST_TERMINATION'],findingsAreStaticNotDeviceReproduction=True,readonlyQueryMayBeSeparatelyDispatched=True,abortOrProductAdmitted=False,testerAdbCalls=0,testerMediaReads=0,testerJavaOrGradleRuns=0,inFlight=[])
(E/'identity-and-static-evidence-audit.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps(out,ensure_ascii=False,indent=2))
