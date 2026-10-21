"""Independent static identity and existing evidence review only; no device/media/model runs."""
from pathlib import Path
import json,hashlib,zipfile,struct
R=Path(__file__).resolve().parents[3];B='docs/coder/d1e7/';OLD='docs/coder/d1e6b/'
def raw(p):
    assert not str(p).lower().endswith(('.mp4','.avi','.mkv')),'MEDIA_FORBIDDEN'
    return (R/p).read_bytes()
def sha(b):return hashlib.sha256(b).hexdigest()
def obj(p):return json.loads(raw(p))
def check(x):
    b=raw(x['path']);assert len(b)==x['bytes'] and sha(b)==x['sha256'],x['path']
seal=B+'evidence/e7-freeze.json';sealhash='b69200b6599144894382e46af0f9555407894f8ce8dd57fad5b71d96bcc63599'
assert sha(raw(seal))==sealhash
f=obj(seal);assert len(f['immutableFiles'])==195
for x in f['immutableFiles']:check(x)
m=obj(f['sourceManifest']['path']);assert len(m['files'])==191
with zipfile.ZipFile(R/f['sourceZip']['path']) as z:
    assert z.namelist()==[x['path'] for x in m['files']] and len(set(z.namelist()))==191
    for x in m['files']:
        assert not x['path'].lower().endswith(('.mp4','.avi','.mkv'))
        b=z.read(x['path']);assert len(b)==x['bytes'] and sha(b)==x['sha256']
prior=obj(OLD+'evidence/e6b-freeze.json');assert len(prior['immutableFiles'])==191
assert sha(raw(OLD+'evidence/e6b-freeze.json'))=='21ef22f4e92535a0d4e50703d87ff46849c4228f5a20dd6f9721c31c87dddc33'
for x in prior['immutableFiles']:check(x)
snapshot=B+'evidence/final-build-inputs.json';snapshotHash='e35aadf762b21cd7ce3f77f847ae88e1468c86f2fa696213c28927518feaa62b'
assert sha(raw(snapshot))==snapshotHash
for x in obj(snapshot)['files']:check(x)
build=obj(B+'evidence/build-results.json');assert len(build['attempts'])==1
a=build['attempts'][0];assert a['inputSnapshotSha256']==snapshotHash and a['id']=='main-001' and a['exitCode']==0 and '--offline' in a['arguments'] and 'BUILD SUCCESSFUL' in raw(a['log']).decode(errors='replace')
derived=obj(B+'evidence/source-derivation.json');same=[];changed=[]
for d in derived['files']:
    check(d['current'])
    if d['relationship']=='BYTE_IDENTICAL':
        check(d['baseline']);assert raw(d['current']['path'])==raw(d['baseline']['path']);same.append(d['current']['path'])
    else:changed.append(d['current']['path'])
for name in ['E5AFinalObservation.java','E5AAdmission.java','E4Owned.java','E5BGuard.java','E5N2Recovery.java','E4OutputBudget.java','E4CpuAdapter.java','PipelineRules.java','E6Muxer.java','E4CodecSink.java']:
    assert any(p.endswith('/'+name) for p in same),name
native=obj(B+'evidence/native-and-strict-logic-inheritance.json')
for x in native['files']:check(x);assert raw(x['path'])==raw(x['path'].replace(B,OLD,1))
apk=obj(B+'evidence/apk-audit.json');align=[]
for x in apk['apks']:
    check(x);assert x['signingVerified'] and x['signerCertificateSha256'] in raw(x['signingReport']).decode()
    with zipfile.ZipFile(R/x['path']) as z:
        dex=b''.join(z.read(n) for n in z.namelist() if n.endswith('.dex'))
        assert b'E7WriterDeathGateSelfCheck' not in dex
        if x['role']=='app-debug':assert b'E7WriterDeathGate' in dex
        if x['role']=='androidTest':assert b'originalRecoveryWriterReadOnly' in dex
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
checks=obj(B+'evidence/local-check-results.json');assert checks['productionGateCases']==27 and checks['assertions']==316 and checks['historyLimit']==8
for x in checks['inputs']:check(x)
for x in checks['commands']:assert x['exitCode']==0;check(x['log'])
assert 'production_gate_cases=27 assertions=316' in raw(B+'evidence/gate-run-001.log').decode()
gate=raw(B+'src/com/videokit/spike/e4/E7WriterDeathGate.java').decode()
assert gate.count('port.history(')==1 and gate.index('if(n!=1)')<gate.index('if(match.reason<=0)')<gate.index('port.proc(')
entryPath=B+'app/src/androidTest/java/com/videokit/spike/e4/E7WriterDeathDiagnosticTests.java';entry=raw(entryPath).decode()
assert 'O_RDONLY|OsConstants.O_NOFOLLOW|OsConstants.O_NONBLOCK' in entry and 'byte[257]' in entry and 'finally{fd.close();}' in entry
assert '.observe(' not in entry and 'fsync' not in entry and 'E5AAdmission.' not in entry
assert 'private static Job original;' in entry and 'original.done.await(10,TimeUnit.SECONDS)' in entry and 'assertTrue("Original owner still in flight; retain and stop batch",completed);' in entry
plan=obj(B+'tools/device_plan.json');assert plan['apks']==apk['apks'] and plan['lastTesterConsumption']==107218 and plan['lastTesterReserved']==0
assert plan['method']=='com.videokit.spike.e4.E7WriterDeathDiagnosticTests#originalRecoveryWriterReadOnly' and plan['arguments']['e7Scope']=='READ_ONLY_NO_ADMISSION' and plan['admission']=='NONE'
priorlog='docs/tester/D1_E6B_NORMAL_EVIDENCE/normalAviSixRealFrames-logcat-stdout.txt'
assert 'Force stopping com.videokit.app appid=10221 user=0: finished inst' in raw(priorlog).decode() and 'Killing 11809:com.videokit.app' in raw(priorlog).decode()
finding=dict(id='E7-F01',priority='P1',issue='TIMED_OUT_OR_UNKNOWN_ORIGINAL_OWNER_CAN_OUTLIVE_JUNIT_WHICH_FINISHES_INSTRUMENTATION',source=entryPath,scope='STATIC_LIFECYCLE_FINDING_WITH_PRIOR_SAME_DEVICE_RUNNER_TEARDOWN_EVIDENCE_NOT_E7_TIMEOUT_REPRODUCTION',priorRunnerLogSha256=sha(raw(priorlog)))
result=dict(integrity='PASS',sourceFiles=191,immutableFiles=195,priorE6BImmutableFilesVerified=191,sealSha256=sealhash,sourceZip=f['sourceZip'],finalBuildInputsSha256=snapshotHash,apks=apk['apks'],nativeIdentical=7,nativeAndZip16kStatic=align,dependencyDelta=0,recordedProductionGateCases=27,recordedAssertions=316,changedOrNew=derived['changedOrNew'],staticFindings=[finding],diagnosticDispatch='NOT_SUPPORTED_UNTIL_ORIGINAL_OWNER_LIFECYCLE_FIXED',longTermAdmission='OPEN_DESIGN_BLOCKED',testerAdbCalls=0,testerMediaOrExportReadBytes=0,testerGradleNativeModelRuns=0,inFlight=[])
Path(__file__).with_name('identity-and-recorded-static-audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:result[k] for k in ['integrity','sourceFiles','immutableFiles','nativeIdentical','recordedProductionGateCases','recordedAssertions','diagnosticDispatch','staticFindings']}))
