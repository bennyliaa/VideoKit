"""Independent static identity/evidence audit only. Never reads original/export/replay media or runs candidate code."""
from pathlib import Path
import hashlib,json,zipfile,struct
R=Path(__file__).resolve().parents[3];B=R/'docs/coder/d1e6'
def sha(b):return hashlib.sha256(b).hexdigest()
def raw(p):
    assert not str(p).lower().endswith(('.mp4','.avi','.mkv')),'MEDIA_READ_FORBIDDEN'
    return (R/p).read_bytes()
def obj(p):return json.loads(raw(p))
def check(row):
    b=raw(row['path']);assert len(b)==row['bytes'] and sha(b)==row['sha256'],row['path']
seal='docs/coder/d1e6/evidence/e6-freeze.json'
assert sha(raw(seal))=='362429a40889e84df49228c684feaec93faca036eeb26a5fd535147329d32265'
f=obj(seal);assert len(f['immutableFiles'])==254
for row in f['immutableFiles']:check(row)
m=obj(f['sourceManifest']['path']);assert len(m['files'])==246
with zipfile.ZipFile(R/f['sourceZip']['path']) as z:
    assert z.namelist()==[x['path'] for x in m['files']] and len(set(z.namelist()))==246
    for row in m['files']:
        assert not row['path'].lower().endswith(('.mp4','.avi','.mkv'))
        b=z.read(row['path']);assert len(b)==row['bytes'] and sha(b)==row['sha256']
snapshot='docs/coder/d1e6/evidence/final-build-inputs.json'
assert sha(raw(snapshot))=='3ac4722ad91be6e06572a1c30c31849753b5425cd36da208c4819627783523c9'
for row in obj(snapshot)['files']:check(row)
build=obj('docs/coder/d1e6/evidence/build-results.json');assert build['attempts'][-1]['id']=='repair-002' and build['attempts'][-1]['inputSnapshotSha256']==sha(raw(snapshot))
for a in build['attempts']:
    assert a['exitCode']==0 and '--offline' in a['arguments'] and 'BUILD SUCCESSFUL' in raw(a['log']).decode('utf-8',errors='replace')
derivation=obj('docs/coder/d1e6/evidence/source-derivation.json');identical=[]
for d in derivation['files']:
    check(d['current'])
    if d['relationship']=='BYTE_IDENTICAL':check(d['baseline']);assert raw(d['current']['path'])==raw(d['baseline']['path']);identical.append(d['current']['path'])
for name in ['E5BGuard.java','E5N2Recovery.java','E5AFinalObservation.java','E5AAdmission.java','E5ALifecycle.java','E4OutputBudget.java']:
    assert any(p.endswith('/'+name) for p in identical),name
apk=obj('docs/coder/d1e6/evidence/apk-audit.json')
for a in apk['apks']:
    check(a);assert a['signingVerified'] and a['signerCertificateSha256'] in raw(a['signingReport']).decode('utf-8',errors='replace')
native=obj('docs/coder/d1e6/evidence/cpu-native-build.json')
for row in native['inputs']:check(row)
check(native['output']);assert native['output']['sha256']=='2547b07d7d4b298e8b455c5f24d0d1fbcdf7068b016527edbf5f80f31d16191a'
alignments=[];same=0;changed=[]
appraw=raw(apk['apks'][0]['path'])
with zipfile.ZipFile(R/apk['apks'][0]['path']) as app,zipfile.ZipFile(R/'docs/coder/d1e5b/artifacts/D1-20261017-E5B/final/app-debug.apk') as old:
    for n in apk['nativeLibraries']:
        b=app.read(n['entry']);assert b==raw(n['upstreamPath']) and sha(b)==n['sha256'] and len(b)==n['bytes']
        if b==old.read(n['entry']):same+=1
        else:changed.append(n['entry'])
        assert b[:6]==b'\x7fELF\x02\x01'
        phoff=struct.unpack_from('<Q',b,32)[0];ents,num=struct.unpack_from('<HH',b,54)
        al=[struct.unpack_from('<IIQQQQQQ',b,phoff+i*ents)[-1] for i in range(num) if struct.unpack_from('<I',b,phoff+i*ents)[0]==1]
        assert al and min(al)>=16384
        info=app.getinfo(n['entry']);fn,ex=struct.unpack_from('<HH',appraw,info.header_offset+26);offset=info.header_offset+30+fn+ex
        assert info.compress_type==0 and offset%16384==0
        alignments.append(dict(entry=n['entry'],elfLoadAlignments=al,zipOffset=offset))
    assert any(b'validatorNativeDiagnostic' in app.read(n) for n in app.namelist() if n.endswith('.dex'))
with zipfile.ZipFile(R/apk['apks'][1]['path']) as z:assert any(b'validatorNativeDiagnostic' in z.read(n) for n in z.namelist() if n.endswith('.dex'))
assert same==6 and changed==['lib/arm64-v8a/libvideokit_cpu.so']
assert (B/'app/gradle.lockfile').read_bytes()==(R/'docs/coder/d1e5b/app/gradle.lockfile').read_bytes()
checks=obj('docs/coder/d1e6/evidence/local-check-results.json')
assert checks['pureJavaCases']==17 and checks['actualProductionNativePredicateCases']==17
for row in checks['inputs']:check(row)
assert all(x['exitCode']==0 for x in checks['commands'])
assert 'cases=17' in raw('docs/coder/d1e6/evidence/java-selfcheck-run.log').decode()
analysis=obj('docs/coder/d1e6/evidence/export-analysis.json');replay=obj('docs/coder/d1e6/evidence/muxer-replay-results.json')
assert analysis['bytes']==53651 and analysis['totalExplicitPythonExportReadBytes']==107302
assert analysis['fragmentSampleCounts']==[5,1] and analysis['lastDeviationUs']==41667
old_pts=replay['cases'][0]['inferredPtsUs'];new_pts=replay['cases'][1]['inferredPtsUs']
assert old_pts[-1]==round(18750*5/90000*1000000)==1041667
dur=replay['cases'][1]['trunDurations90000'][0]
assert dur==[18750,18750,18750,18750,15000,18000]
assert new_pts==[round(sum(dur[:i])/90000*1000000) for i in range(6)]==[0,208333,416667,625000,833333,1000000]
plan=obj('docs/coder/d1e6/tools/device_plan.json');assert plan['apks']==apk['apks']
assert plan['priorConsumptionBytes']==53651 and plan['stableBudget']=='730a73e1-50e1-4198-a515-047104f00e31'
assert len(plan['steps'])==4 and plan['steps'][0]['method']=='normalMp4SixRealFrames' and plan['steps'][1]['method']=='normalAviSixRealFrames'
assert plan['steps'][-1]['arguments']['e4NormalReceiptSha256']=='<SHA256_OF_INDEPENDENTLY_REVIEWED_THIS_E6_TWO_NORMAL_RESULT_REPORT>'
# Static witnesses for the two non-blocking diagnostic notes; no runtime reproduction.
adapter=(B/'android/com/videokit/spike/c14/E4CpuAdapter.java').read_text()
session=(B/'android/com/videokit/spike/e4/E4Session.java').read_text()
assert adapter.index('PipelineValidationReceipt.prove')<adapter.index('return new Verification(verifier,proof)')
assert 'primary=failure;throw failure;' in adapter and 'nativeFailure' not in adapter
assert session.index('source.next(sequence)')<session.index('E4CpuAdapter.validate')<session.index('E6FailureCodes.diagnostic(error)')
result=dict(integrity='PASS',sourceFiles=246,immutableFiles=254,sourceZip=f['sourceZip'],finalBuildSnapshotSha256=sha(raw(snapshot)),apks=apk['apks'],buildAttempts=build['attempts'],nativeByteIdentical=6,nativeChanged=changed,nativeBuild=native['output'],nativeAndZip16kStatic=alignments,dependencyDelta=0,coreByteIdentical=identical,recordedNativeCases=17,recordedJavaCases=17,oldPts=old_pts,newPts=new_pts,desktopAndAndroidDecoder='NOT_RUN',rootCauseSupport='RECORDED_CONTAINER_AND_ACTUAL_MEDIA3_REPLAY_WITH_STRICT_GATE_SOURCE_ONLY_NOT_OLD_ANDROID_BRANCH_TRACE',staticFindings=[dict(id='E6-F01',priority='P2',issue='NATIVE_SUCCESS_SNAPSHOT_NOT_ATTACHED_WHEN_LATER_JAVA_VALIDATION_OR_CLEANUP_FAILS'),dict(id='E6-F02',priority='P2',issue='SOURCE_NATIVE_FAILURE_CAN_BE_MISLABELLED_AS_VALIDATOR_DIAGNOSTIC'),dict(id='E6-F03',priority='P2',issue='NATIVE_DIAGNOSTIC_ONCE_CHECK_AND_PUBLICATION_NOT_ATOMIC_UNDER_CONCURRENT_BINDER_CALLS')],findingDeviceOrModelReproduced=False,normalRegression='TECHNICALLY_SUPPORTED_FOR_SEPARATE_FORMAL_DISPATCH_WITH_P2_NOTES',testerAdbCalls=0,testerMediaOrExportReadBytes=0,testerGradleOrNativeOrModelRuns=0,inFlight=[])
Path(__file__).with_name('identity-and-recorded-static-audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:result[k] for k in ['integrity','sourceFiles','immutableFiles','nativeByteIdentical','nativeChanged','recordedNativeCases','recordedJavaCases','staticFindings']}))
