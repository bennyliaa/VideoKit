"""Independent static package and recorded lifecycle evidence audit. No candidate execution/media/device."""
from pathlib import Path
import hashlib,json,zipfile,struct
R=Path(__file__).resolve().parents[3];B='docs/coder/d1e7a/';OLD='docs/coder/d1e7/'
def raw(p):
    assert not str(p).lower().endswith(('.mp4','.avi','.mkv')),'MEDIA_FORBIDDEN'
    return (R/p).read_bytes()
def sha(b):return hashlib.sha256(b).hexdigest()
def obj(p):return json.loads(raw(p))
def check(x):
    b=raw(x['path']);assert len(b)==x['bytes'] and sha(b)==x['sha256'],x['path']
seal=B+'evidence/e7a-freeze.json';sealhash='1264dd365255b8d22fe1586a7b892240a4745dc01e54d6f26c88ec149784cf76'
assert sha(raw(seal))==sealhash
f=obj(seal);assert len(f['immutableFiles'])==200
for x in f['immutableFiles']:check(x)
m=obj(f['sourceManifest']['path']);assert len(m['files'])==196
with zipfile.ZipFile(R/f['sourceZip']['path']) as z:
    assert z.namelist()==[x['path'] for x in m['files']] and len(set(z.namelist()))==196
    for x in m['files']:
        assert not x['path'].lower().endswith(('.mp4','.avi','.mkv'))
        b=z.read(x['path']);assert len(b)==x['bytes'] and sha(b)==x['sha256']
prior=obj(OLD+'evidence/e7-freeze.json');assert len(prior['immutableFiles'])==195
assert sha(raw(OLD+'evidence/e7-freeze.json'))=='b69200b6599144894382e46af0f9555407894f8ce8dd57fad5b71d96bcc63599'
for x in prior['immutableFiles']:check(x)
snapshot=B+'evidence/final-build-inputs.json';snapshotHash='09e62035889c5b37b6acb480711e464c091f7f1074362d90b211b6479548038a'
assert sha(raw(snapshot))==snapshotHash
for x in obj(snapshot)['files']:check(x)
build=obj(B+'evidence/build-results.json');assert len(build['attempts'])==1
a=build['attempts'][0];assert a['inputSnapshotSha256']==snapshotHash and a['id']=='main-001' and a['exitCode']==0 and '--offline' in a['arguments'] and 'BUILD SUCCESSFUL' in raw(a['log']).decode(errors='replace')
derivation=obj(B+'evidence/source-derivation.json');same=[]
for d in derivation['files']:
    check(d['current'])
    if d['relationship']=='BYTE_IDENTICAL':
        check(d['baseline']);assert raw(d['current']['path'])==raw(d['baseline']['path']);same.append(d['current']['path'])
production=[]
for root in ['src','android','native','upstream-c14/src','upstream-c14/android','upstream-c14/native-libs']:
    for p in (R/B/root).rglob('*'):
        if p.is_file():
            relative=p.relative_to(R/B).as_posix();assert raw(B+relative)==raw(OLD+relative),relative;production.append(relative)
apk=obj(B+'evidence/apk-audit.json');align=[]
for x in apk['apks']:
    check(x);assert x['signingVerified'] and x['signerCertificateSha256'] in raw(x['signingReport']).decode()
    with zipfile.ZipFile(R/x['path']) as z:
        dex=b''.join(z.read(n) for n in z.namelist() if n.endswith('.dex'))
        assert b'E7ALifecycleSelfCheck' not in dex
        if x['role']=='androidTest':assert b'E7AReadOnlyInstrumentation' in dex and b'E7ADiagnosticRun' in dex
app=apk['apks'][0]['path'];appbytes=raw(app)
with zipfile.ZipFile(R/app) as z,zipfile.ZipFile(R/prior['apks'][0]['path']) as oldzip:
    for n in apk['nativeLibraries']:
        b=z.read(n['entry']);assert b==raw(n['upstreamPath'])==oldzip.read(n['entry']) and len(b)==n['bytes'] and sha(b)==n['sha256']
        assert b[:6]==b'\x7fELF\x02\x01';phoff=struct.unpack_from('<Q',b,32)[0];ents,num=struct.unpack_from('<HH',b,54)
        als=[struct.unpack_from('<IIQQQQQQ',b,phoff+i*ents)[-1] for i in range(num) if struct.unpack_from('<I',b,phoff+i*ents)[0]==1];assert min(als)>=16384
        info=z.getinfo(n['entry']);fn,ex=struct.unpack_from('<HH',appbytes,info.header_offset+26);offset=info.header_offset+30+fn+ex
        assert info.compress_type==0 and offset%16384==0;align.append(dict(entry=n['entry'],elfLoadAlignments=als,zipOffset=offset))
assert len(align)==7
sbom=obj(B+'evidence/sbom-difference.json');assert sbom['coordinates']==35 and sbom['coordinateDelta']==[] and sbom['nativeDelta']==[] and not sbom['nativeRebuild']
assert raw(B+'app/gradle.lockfile')==raw(OLD+'app/gradle.lockfile')
checks=obj(B+'evidence/local-check-results.json');assert checks['actualJobFinishCases']==28 and checks['assertions']==338 and checks['earlyPlatformFinishes']==0 and checks['reopens']==0
for x in checks['inputs']:check(x)
for x in checks['commands']:assert x['exitCode']==0;check(x['log'])
assert 'actual_job_finish_cases=28 assertions=338' in raw(B+'evidence/lifecycle-run-002.log').decode()
provenance=obj(B+'evidence/test-expansion-provenance.json');check(provenance['preservedExactPriorSource']);assert provenance['priorInput']['sha256']==provenance['preservedExactPriorSource']['sha256']
prefix=B+'app/src/androidTest/java/com/videokit/spike/e4/'
run=raw(prefix+'E7ADiagnosticRun.java').decode();runner=raw(prefix+'E7AReadOnlyInstrumentation.java').decode();legacy=raw(prefix+'E7WriterDeathDiagnosticTests.java').decode()
assert 'E7A_MANAGED_RUNNER_REQUIRED_NO_JOB_STARTED' in legacy and 'new Job' not in legacy
assert 'extends Instrumentation' in runner and 'AndroidJUnitRunner' not in runner
assert runner.count('super.finish(')==1 and runner.index('unregisterReceiver(control)')<runner.index('super.finish(')
assert 'private void finishPlatform(' in runner and 'original.beginLaunch();attempted=true;' in runner
assert 'if(archivedSequence' not in run and 'archivedSequence!=sequence' in run and 'if(!safeResources())' in run
assert 'owner.state()==E4Owned.State.EMPTY||owner.returned()' in run and 'workerReturned&&' in run
assert 'if(!verdict.equals("PENDING"))' in run and 'clock.now()>=deadline' in run
assert '.observe(' not in runner and 'fsync' not in runner and 'O_RDONLY|OsConstants.O_NOFOLLOW|OsConstants.O_NONBLOCK' in runner
manifest=raw(B+'evidence/test-manifest-xmltree.txt').decode();assert 'com.videokit.spike.e4.E7AReadOnlyInstrumentation' in manifest and 'targetPackage' in manifest
plan=obj(B+'tools/device_plan.json');assert plan['apks']==apk['apks'] and plan['versionCode']==10 and plan['lastTesterConsumption']==107218 and plan['lastTesterReserved']==0
assert plan['component']=='com.videokit.app.test/com.videokit.spike.e4.E7AReadOnlyInstrumentation' and plan['control']['maxRequests']==6 and plan['control']['responseBudgetSeconds']==5
assert plan['control']['senderPermission']=='android.permission.DUMP' and plan['qualificationNs']==10000000000 and plan['admission']=='NONE'
result=dict(integrity='PASS',sourceFiles=196,immutableFiles=200,priorE7ImmutableFilesVerified=195,sealSha256=sealhash,sourceZip=f['sourceZip'],finalBuildInputsSha256=snapshotHash,apks=apk['apks'],nativeIdentical=7,nativeAndZip16kStatic=align,allComparedProductionFilesIdentical=len(production),dependencyDelta=0,recordedActualJobFinishCases=28,recordedAssertions=338,oldE7F01='STATIC_FIX_AND_RECORDED_PRODUCTION_BOUNDARY_SUPPORTED_ANDROID_NOT_RUN',newFindings=[],diagnosticDispatch='SUPPORTED_FOR_SEPARATE_FORMAL_MANAGED_READ_ONLY_DISPATCH',longTermAdmission='OPEN_DESIGN_BLOCKED',AndroidLifecycleBroadcastAndFinish='NOT_RUN',testerAdbCalls=0,testerMediaOrExportReadBytes=0,testerGradleNativeModelRuns=0,inFlight=[])
Path(__file__).with_name('identity-and-recorded-static-audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:result[k] for k in ['integrity','sourceFiles','immutableFiles','nativeIdentical','allComparedProductionFilesIdentical','recordedActualJobFinishCases','recordedAssertions','diagnosticDispatch','newFindings']}))
