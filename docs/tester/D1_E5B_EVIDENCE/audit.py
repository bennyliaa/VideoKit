"""Tester read-only identity/log audit; no production import, JVM/model/device execution."""
from pathlib import Path
import hashlib,json,zipfile
R=Path(__file__).resolve().parents[3]
B=R/'docs/coder/d1e5b'
def sha(b): return hashlib.sha256(b).hexdigest()
def raw(p): return (R/p).read_bytes()
def obj(p): return json.loads(raw(p))
def check(row):
    b=raw(row['path'])
    assert len(b)==row['bytes'] and sha(b)==row['sha256'],row['path']
seal=B/'evidence/e5b-freeze.json'
assert sha(seal.read_bytes())=='3c55e0c83517e8937799b72d327dcab98b9d23965dc41813a5d18756640aceee'
f=json.loads(seal.read_bytes())
assert len(f['immutableFiles'])==1561
for row in f['immutableFiles']:check(row)
m=obj(f['sourceManifest']['path'])
assert len(m['files'])==1557
assert f['sourceZip']['sha256']=='366417dd96f3c6a65824a845f7e7334cdeb96a1815a152288151824931cc1a33'
with zipfile.ZipFile(R/f['sourceZip']['path']) as z:
    assert z.namelist()==[r['path'] for r in m['files']]
    assert len(set(z.namelist()))==1557
    for row in m['files']:
        b=z.read(row['path']);assert len(b)==row['bytes'] and sha(b)==row['sha256'],row['path']
snapshot='docs/coder/d1e5b/evidence/final-build-inputs.json'
assert sha(raw(snapshot))=='8d9004bfd016ca1aed4340b67e2d020b03bebc4c58a3f93b99ac17d0cb4a091e'
for row in obj(snapshot)['files']:check(row)
build=obj('docs/coder/d1e5b/evidence/build-results.json')
assert len(build['attempts'])==1
for a in build['attempts']:
    assert a['exitCode']==0 and '--offline' in a['arguments']
    assert a['inputSnapshotSha256']==sha(raw(snapshot))
    assert 'BUILD SUCCESSFUL' in raw(a['log']).decode('utf-8',errors='replace')
apk=obj('docs/coder/d1e5b/evidence/apk-audit.json')
for a in apk['apks']:
    check(a);assert a['signingVerified']
    s=raw(a['signingReport']).decode('utf-8',errors='replace')
    assert a['signerCertificateSha256'] in s
assert len(apk['nativeLibraries'])==7
with zipfile.ZipFile(R/apk['apks'][0]['path']) as current,zipfile.ZipFile(R/'docs/coder/d1e5a/artifacts/D1-20261017-E5A/final/app-debug.apk') as old:
    for n in apk['nativeLibraries']:
        b=current.read(n['entry']);assert b==old.read(n['entry'])==raw(n['upstreamPath'])
        assert len(b)==n['bytes'] and sha(b)==n['sha256']
assert (B/'app/gradle.lockfile').read_bytes()==(R/'docs/coder/d1e5a/app/gradle.lockfile').read_bytes()==(R/'docs/coder/d1e4a/app/gradle.lockfile').read_bytes()
preserved=obj('docs/coder/d1e5b/evidence/preserved-invariants.json')
for row in preserved['files']:
    assert sha(raw(row['path']))==row['sha256']
    assert raw(row['path'])==raw(row['path'].replace('/d1e5b/','/d1e5a/'))
checks=obj('docs/coder/d1e5b/evidence/local-check-results.json')
for row in checks['inputs']:check(row)
for c in checks['commands']:
    assert c['exitCode']==0;check(c['log'])
assert checks['summary']['assertions']==82 and checks['summary']['cases']==16
assert checks['summary']['trueSymbolicLink']=='NOT_RUN_OS_PRIVILEGE_1314'
cases=['healthy','missing-owner','missing-lease','owner-directory','lease-directory','owner-length','lease-length-0','lease-length-35','lease-length-37','lease-fence','owner-replaced','lease-replaced','owner-junction','lease-junction','guard-record-missing','guard-record-replaced']
records=[]
base=B/'evidence/jvm-attempts/repair-003/owned'
for case in cases:
    producer=json.loads((base/case/'producer.log').read_text(encoding='utf-8-sig'))
    observation=json.loads((base/case/'observation.log').read_text(encoding='utf-8-sig'))
    assert producer['status']=='ABORTED_SETTLED'
    assert observation['status']=='PASS' and observation['createCalls']==0
    assert observation['outcome'].startswith('FRESH_OBSERVATION_ADMITTED' if case=='healthy' else 'BLOCKED')
    records.append(observation)
late=json.loads((base/'close-unknown/producer.log').read_text(encoding='utf-8-sig'))
assert late['status']=='BLOCKED'
late_observation=json.loads((base/'close-unknown/fresh-observation.log').read_text(encoding='utf-8-sig'))
assert late_observation['outcome'].startswith('FRESH_OBSERVATION_ADMITTED')
for role in ['owner','lease']:
    x=json.loads((base/('recovery-missing-'+role)/'recovery.log').read_text(encoding='utf-8-sig'));assert x['status']=='PASS'
guard=(B/'src/com/videokit/spike/e4/E5BGuard.java').read_text()
android=(B/'android/com/videokit/spike/e4/E5BAndroidGuardIO.java').read_text()
existing=android.split('public void openExistingNoFollow')[1].split('public void createNewNoFollow')[0]
assert 'O_NOFOLLOW' in existing and 'O_CREAT' not in existing and 'O_TRUNC' not in existing
assert 'io.pathStatNoFollow(p)' in guard and 'io.handleStat(g.descriptor)' in guard
assert 'g.verifyExisting();io.lock(g.descriptor);g.locked=true;g.verifyExisting();' in guard
legacy=(B/'android/com/videokit/spike/c14/AndroidLease.java').read_text()
assert 'MODE_CREATE' not in legacy and 'exclusiveInto' not in legacy
result=dict(integrity='PASS',sourceFiles=1557,immutableFiles=1561,sourceZip=f['sourceZip'],buildSnapshotSha256=sha(raw(snapshot)),buildAttempts=build['attempts'],apks=apk['apks'],nativeByteIdentical=7,dependencyDelta=0,preservedByteIdentical=preserved['files'],recordedParentAssertions=82,recordedObservationCases=records,closeUnknownWriter=late,closeUnknownFreshHostObservation=late_observation,trueFileSymlink='NOT_RUN_OS_PRIVILEGE_1314',junctionCases=2,androidFstatFlock='NOT_RUN',newSourceBlockers=0,oldE5AF01='STATIC_FIX_AND_SUPPORTED_CASES_VERIFIED_VALIDATION_GATE_OPEN',query='SUPPORTED_FOR_SEPARATE_FORMAL_DISPATCH',writeRecoveryAndObservation='BLOCKED_PENDING_TRUE_SYMLINK_EVIDENCE_AND_REVIEW',testerAdbCalls=0,testerMediaStatReadHash=0,testerJavaGradleOrModelRuns=0,inFlight=[])
out=Path(__file__).with_name('identity-and-recorded-static-audit.json')
out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:result[k] for k in ['integrity','sourceFiles','immutableFiles','recordedParentAssertions','trueFileSymlink','testerAdbCalls','testerJavaGradleOrModelRuns']}))
