"""Independent identity and recorded-evidence audit; no candidate execution or media reads."""
from pathlib import Path
import hashlib,json,zipfile,struct
R=Path(__file__).resolve().parents[3]
B='docs/coder/d1e6a/'
def raw(p):
    assert not str(p).lower().endswith(('.mp4','.avi','.mkv')), 'MEDIA_FORBIDDEN'
    return (R/p).read_bytes()
def sha(b):return hashlib.sha256(b).hexdigest()
def obj(p):return json.loads(raw(p))
def check(row):
    b=raw(row['path']);assert len(b)==row['bytes'] and sha(b)==row['sha256'],row['path']
seal=B+'evidence/e6a-freeze.json'
assert sha(raw(seal))=='520f980b0523e1c70c6841747ed0170b28a31363874a9b54f66e8684e21411e7'
f=obj(seal);assert len(f['immutableFiles'])==228
for row in f['immutableFiles']:check(row)
m=obj(f['sourceManifest']['path']);assert len(m['files'])==222
with zipfile.ZipFile(R/f['sourceZip']['path']) as z:
    assert z.namelist()==[x['path'] for x in m['files']] and len(set(z.namelist()))==222
    for row in m['files']:
        assert not row['path'].lower().endswith(('.mp4','.avi','.mkv'))
        b=z.read(row['path']);assert len(b)==row['bytes'] and sha(b)==row['sha256']
snapshot=B+'evidence/final-build-inputs.json'
assert sha(raw(snapshot))=='1d4f86663e8e016b3c175ea7df1cbb9f1a1f64b6b0e77a810000ab7fd073ace0'
for row in obj(snapshot)['files']:check(row)
build=obj(B+'evidence/build-results.json')
assert build['attempts'][-1]['id']=='repair-001' and build['attempts'][-1]['inputSnapshotSha256']==sha(raw(snapshot))
for a in build['attempts']:
    assert a['exitCode']==0 and '--offline' in a['arguments'] and 'BUILD SUCCESSFUL' in raw(a['log']).decode('utf-8',errors='replace')
derivation=obj(B+'evidence/source-derivation.json');identical=[];changed=[]
for d in derivation['files']:
    check(d['current'])
    if d['relationship']=='BYTE_IDENTICAL':
        check(d['baseline']);assert raw(d['current']['path'])==raw(d['baseline']['path']);identical.append(d['current']['path'])
    else:changed.append(d['current']['path'])
for name in ['E5BGuard.java','E5N2Recovery.java','E5AFinalObservation.java','E5AAdmission.java','E5ALifecycle.java','E4OutputBudget.java','E6Muxer.java','E4CodecSink.java','PipelineRules.java']:
    assert any(p.endswith('/'+name) for p in identical),name
inherit=obj(B+'evidence/native-and-strict-logic-inheritance.json')
for row in inherit['nativeSourcesHeadersConfig']:
    check(row);assert raw(row['path'])==raw(row['baseline'])
old=obj('docs/coder/d1e6/evidence/e6-freeze.json')
for row in old['immutableFiles']:check(row)
apk=obj(B+'evidence/apk-audit.json');alignments=[]
for a in apk['apks']:
    check(a);assert a['signingVerified'] and a['signerCertificateSha256'] in raw(a['signingReport']).decode()
appraw=raw(apk['apks'][0]['path'])
with zipfile.ZipFile(R/apk['apks'][0]['path']) as app,zipfile.ZipFile(R/'docs/coder/d1e6/artifacts/D1-20261017-E6/final/app-debug.apk') as prior:
    for n in apk['nativeLibraries']:
        b=app.read(n['entry']);assert b==raw(n['upstreamPath'])==prior.read(n['entry']) and sha(b)==n['sha256'] and len(b)==n['bytes']
        assert b[:6]==b'\x7fELF\x02\x01'
        phoff=struct.unpack_from('<Q',b,32)[0];ents,num=struct.unpack_from('<HH',b,54)
        al=[struct.unpack_from('<IIQQQQQQ',b,phoff+i*ents)[-1] for i in range(num) if struct.unpack_from('<I',b,phoff+i*ents)[0]==1]
        assert al and min(al)>=16384
        info=app.getinfo(n['entry']);fn,ex=struct.unpack_from('<HH',appraw,info.header_offset+26);offset=info.header_offset+30+fn+ex
        assert info.compress_type==0 and offset%16384==0
        alignments.append(dict(entry=n['entry'],elfLoadAlignments=al,zipOffset=offset))
    assert len(alignments)==7
for a in apk['apks']:
    with zipfile.ZipFile(R/a['path']) as z:
        dex=b''.join(z.read(n) for n in z.namelist() if n.endswith('.dex'))
        assert b'sourceNativeDiagnostic' in dex and b'validatorNativeDiagnostic' in dex
        assert b'E6ABoundarySelfCheck' not in dex
sbom=obj(B+'evidence/sbom-difference.json')
assert sbom['coordinates']==35 and sbom['coordinateDelta']==[] and sbom['nativeDelta']==[] and not sbom['nativeRebuild']
assert raw(B+'app/gradle.lockfile')==raw('docs/coder/d1e6/app/gradle.lockfile')
checks=obj(B+'evidence/local-check-results.json')
assert checks['productionBoundaryCases']==20 and checks['assertions']==112
for row in checks['inputs']:check(row)
for c in checks['commands']:assert c['exitCode']==0;check(c['log'])
log=raw(B+'evidence/boundary-run-005.log').decode()
assert log.count('CASE ')==20 and 'production_boundary_cases=20 assertions=112' in log
assert checks['concurrency']==dict(threads=16,published=1,duplicateRejected=15,firstRetained=True)
session=raw(B+'android/com/videokit/spike/e4/E4Session.java').decode()
assert session.index('nativeDiagnostics.sourceEnter()')<session.index('source.next(sequence)')<session.index('nativeDiagnostics.sourceSuccess(')
assert session.index('nativeDiagnostics.validatorEnter()')<session.index('E4CpuAdapter.validate(')<session.index('nativeDiagnostics.validatorSuccess(')
assert 'nativeDiagnostics.failure(error)' in session and 'E6_VALIDATOR_REJECTED' not in session
inbox=raw(B+'upstream-c14/src/com/videokit/spike/c14/E6ADiagnosticInbox.java').decode()
assert inbox.index('payload.parse()')<inbox.index('payload.end()')<inbox.index('first.compareAndSet')
plan=obj(B+'tools/device_plan.json')
assert plan['apks']==apk['apks'] and plan['priorConsumptionBytes']==53651 and plan['stableBudget']=='730a73e1-50e1-4198-a515-047104f00e31'
assert [s['method'] for s in plan['steps']]==['normalMp4SixRealFrames','normalAviSixRealFrames','capabilityDenialDoesNotOpenSource','cancelRejectsWrongEpochOversizeAndLateFrame']
assert plan['steps'][-1]['arguments']['e4NormalReceiptSha256']=='<SHA256_OF_INDEPENDENTLY_REVIEWED_THIS_E6A_TWO_NORMAL_RESULT_REPORT>'
adapter=raw(B+'android/com/videokit/spike/c14/E4CpuAdapter.java').decode()
public_validate=adapter[adapter.index('public static Verification validate(Context'):adapter.index('// The actual validation/cleanup')]
assert public_validate.index('PipelineRules.timeline(timeline)')<public_validate.index('try{verifier=new CpuTaskClient')
router=raw(B+'src/com/videokit/spike/e4/E6ADiagnosticState.java').decode()
assert 'start=UNKNOWN' in router and 'error instanceof E6AFailure' in router
finding=dict(id='E6A-F01',priority='P2',previous='E6-F02',issue='PUBLIC_VALIDATOR_PRECREATE_TIMELINE_ERROR_LEAVES_UNKNOWN_INSTEAD_OF_KNOWN_NOT_STARTED',evidence='STATIC_SOURCE_ONLY_NOT_RERUN',normalSessionImpact='NORMAL_SESSION_HAS_PRIOR_E4PROTOCOL_TIMELINE_GUARD; NO_OBSERVED_NORMAL_REGRESSION')
result=dict(integrity='PASS',sourceFiles=222,immutableFiles=228,priorE6ImmutableFilesVerified=len(old['immutableFiles']),sourceZip=f['sourceZip'],sealSha256=sha(raw(seal)),finalBuildSnapshotSha256=sha(raw(snapshot)),apks=apk['apks'],nativeByteIdentical=7,nativeChanged=[],nativeAndZip16kStatic=alignments,dependencyDelta=0,coreByteIdentical=identical,sourceChangedOrAdded=changed,recordedProductionBoundaryCases=20,recordedAssertions=112,recordedConcurrency=checks['concurrency'],oldP2Disposition=dict(F01='STATIC_AND_RECORDED_BOUNDARY_SUPPORTED',F02='PARTIAL_PUBLIC_PRESTART_GAP',F03='STATIC_AND_RECORDED_BOUNDARY_SUPPORTED',Android='NOT_RUN'),staticFindings=[finding],normalRegression='TECHNICALLY_SUPPORTED_WITH_P2_NOTE_SEPARATE_FORMAL_DISPATCH_REQUIRED',testerAdbCalls=0,testerMediaOrExportReadBytes=0,testerGradleOrNativeOrModelRuns=0,inFlight=[])
Path(__file__).with_name('identity-and-recorded-static-audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:result[k] for k in ['integrity','sourceFiles','immutableFiles','priorE6ImmutableFilesVerified','nativeByteIdentical','recordedProductionBoundaryCases','recordedAssertions','sourceChangedOrAdded']}))
