"""Independent read-only seal/source/log audit. No import or execution of candidate tools/models."""
from pathlib import Path
import hashlib,json,zipfile
R=Path(__file__).resolve().parents[3];B=R/'docs/coder/d1e5c'
def sha(b):return hashlib.sha256(b).hexdigest()
def raw(p):return (R/p).read_bytes()
def obj(p):return json.loads(raw(p))
def check(row):
    b=raw(row['path']);assert len(b)==row['bytes'] and sha(b)==row['sha256'],row['path']
seal=B/'evidence/e5c-freeze.json'
assert sha(seal.read_bytes())=='75ad67f90cb7689cd4b7d765afc6b9101dcf75cc1f9e5f1343b9d7db9a1be47c'
f=json.loads(seal.read_bytes());assert len(f['immutableFiles'])==144
for row in f['immutableFiles']:check(row)
m=obj(f['sourceManifest']['path']);assert len(m['files'])==138
assert f['sourceZip']['sha256']=='ac7d5bc2901ab66bb16299cf8c2052e6e7bd3344276b1c3d2a0b50b38a291743'
with zipfile.ZipFile(R/f['sourceZip']['path']) as z:
    assert z.namelist()==[r['path'] for r in m['files']] and len(set(z.namelist()))==138
    for r in m['files']:
        b=z.read(r['path']);assert len(b)==r['bytes'] and sha(b)==r['sha256'],r['path']
snapshot='docs/coder/d1e5c/evidence/final-build-inputs.json'
assert sha(raw(snapshot))=='6af5f97db1f2e74ac35627fc3a46bc6b2b74037f495b422d3af522987827bd36'
for r in obj(snapshot)['files']:check(r)
old=obj('docs/coder/d1e5b/evidence/e5b-freeze.json')
assert sha(raw('docs/coder/d1e5b/evidence/e5b-freeze.json'))=='3c55e0c83517e8937799b72d327dcab98b9d23965dc41813a5d18756640aceee'
for r in old['immutableFiles']:check(r)
by={r['path']:r for r in old['immutableFiles']}
mapping=obj('docs/coder/d1e5b/evidence/upstream-copy-map.json')
for r in mapping['files']:
    by.setdefault(r['destination'],dict(path=r['destination'],bytes=r['bytes'],sha256=r['sha256']))
provenance=obj('docs/coder/d1e5c/evidence/source-provenance.json')
for r in provenance['files']:check(r);assert r==by[r['path']]
for p in provenance['copiedOriginalAppSources']:
    check(p['current']);check(p['baseline']);assert raw(p['current']['path'])==raw(p['baseline']['path'])
assert provenance['coreMutation'] is False
apk=obj('docs/coder/d1e5c/evidence/apk-audit.json')
for a in apk['apks']:
    check(a);assert a['signingVerified'] and a['signerCertificateSha256'] in raw(a['signingReport']).decode('utf-8',errors='replace')
assert len(apk['nativeLibraries'])==7
with zipfile.ZipFile(R/apk['apks'][0]['path']) as current,zipfile.ZipFile(R/'docs/coder/d1e5b/artifacts/D1-20261017-E5B/final/app-debug.apk') as previous:
    for n in apk['nativeLibraries']:
        b=current.read(n['entry']);assert b==previous.read(n['entry'])==raw(n['upstreamPath'])
        assert len(b)==n['bytes'] and sha(b)==n['sha256']
assert (B/'app/gradle.lockfile').read_bytes()==(R/'docs/coder/d1e5b/app/gradle.lockfile').read_bytes()
build=obj('docs/coder/d1e5c/evidence/build-results.json')
assert len(build['attempts'])==2 and build['attempts'][-1]['id']=='repair-001'
assert build['attempts'][-1]['inputSnapshotSha256']==sha(raw(snapshot))
for a in build['attempts']:
    assert a['exitCode']==0 and '--offline' in a['arguments']
    assert 'BUILD SUCCESSFUL' in raw(a['log']).decode('utf-8',errors='replace')
manifest=raw('docs/coder/d1e5c/evidence/app-manifest-xmltree.txt').decode('utf-8',errors='replace')
assert 'E4CodecService' in manifest and 'CpuIsolatedService' in manifest
checks=obj('docs/coder/d1e5c/evidence/local-check-results.json')
for r in checks['inputs']:check(r)
assert checks['jvmCases']==10 and len(checks['staticCases'])==9
assert 'PASS finite policy cases=10' in (B/'evidence/local-1.log').read_text()
plan=obj('docs/coder/d1e5c/tools/device_plan.json')
assert plan['artifactIdentity']==apk['apks'] and len(plan['steps'])==4
assert plan['fixtureArguments']['class']=='com.videokit.spike.e4.E5CGuardFixtureTests#isolatedOriginalInodeSymlinks'
assert plan['queryArguments']['e5N2Action']=='QUERY'
assert plan['queryArguments']['e5RecoveryBatch']=='D1-E5B-N2-RECOVERY-20261017'
s=(B/'app/src/androidTest/java/com/videokit/spike/e4/E5CGuardFixtureTests.java').read_text()
assert '.observe(' not in s and '.execute(' not in s and 'adapter.existingGuard(p,role,fence,expected,holder)' in s
assert 'Os.symlink(' in s and 'expected.inode==t.st_ino' in s and 'e.errno==OsConstants.ELOOP' in s
assert 'RETAINED.add(run)' in s and 'shutdownNow(' not in s and '.cancel(' not in s
result=dict(integrity='PASS',sourceFiles=138,immutableFiles=144,baselineImmutableVerified=len(old['immutableFiles']),sourceZip=f['sourceZip'],finalBuildSnapshotSha256=sha(raw(snapshot)),buildAttempts=build['attempts'],apks=apk['apks'],preservedFailedAuditApks=f['preservedFailedAuditApks'],nativeByteIdentical=7,dependencyDelta=0,productionRelationship=provenance['relationship'],productionCoreMutation=False,recordedJvmBoundsCases=10,recordedStaticConstraints=9,exactBoundary='E5AFinalObservation.private lock -> E5N2RecoveryAndroid.existingGuard -> E5BGuard -> E5BAndroidGuardIO',devicePlan='SUPPORTED_FOR_SEPARATE_FORMAL_DISPATCH',G01='AWAITING_REAL_ANDROID_EVIDENCE_AND_REVIEW',fullObservation='NOT_RUN',N2Recovery='NOT_RUN',testerAdbCalls=0,testerMediaStatReadHash=0,testerJavaGradleOrModelRuns=0,newSourceBlockers=0,inFlight=[])
Path(__file__).with_name('identity-and-recorded-static-audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:result[k] for k in ['integrity','sourceFiles','immutableFiles','baselineImmutableVerified','recordedJvmBoundsCases','recordedStaticConstraints','newSourceBlockers']}))
