"""Independent static package/evidence audit. No candidate/model/media/device execution."""
from pathlib import Path
import hashlib,json,zipfile,struct
R=Path(__file__).resolve().parents[3];B='docs/coder/d1e6b/';A='docs/coder/d1e6a/'
def raw(p):
    assert not str(p).lower().endswith(('.mp4','.avi','.mkv')),'MEDIA_FORBIDDEN'
    return (R/p).read_bytes()
def sha(b):return hashlib.sha256(b).hexdigest()
def obj(p):return json.loads(raw(p))
def check(x):
    b=raw(x['path']);assert len(b)==x['bytes'] and sha(b)==x['sha256'],x['path']
seal=B+'evidence/e6b-freeze.json';sealhash='21ef22f4e92535a0d4e50703d87ff46849c4228f5a20dd6f9721c31c87dddc33'
assert sha(raw(seal))==sealhash
f=obj(seal);assert len(f['immutableFiles'])==191
for x in f['immutableFiles']:check(x)
m=obj(f['sourceManifest']['path']);assert len(m['files'])==187
with zipfile.ZipFile(R/f['sourceZip']['path']) as z:
    assert z.namelist()==[x['path'] for x in m['files']] and len(set(z.namelist()))==187
    for x in m['files']:
        assert not x['path'].lower().endswith(('.mp4','.avi','.mkv'))
        b=z.read(x['path']);assert len(b)==x['bytes'] and sha(b)==x['sha256']
prior=obj(A+'evidence/e6a-freeze.json')
assert sha(raw(A+'evidence/e6a-freeze.json'))=='520f980b0523e1c70c6841747ed0170b28a31363874a9b54f66e8684e21411e7'
for x in prior['immutableFiles']:check(x)
snap=B+'evidence/final-build-inputs.json';snaphash='35de0ac79c792f5a6c4f37937a4ee5166557fbcaa001e635110756d0c483fbce'
assert sha(raw(snap))==snaphash
for x in obj(snap)['files']:check(x)
build=obj(B+'evidence/build-results.json');assert len(build['attempts'])==1
attempt=build['attempts'][0];assert attempt['id']=='main-001' and attempt['inputSnapshotSha256']==snaphash and attempt['exitCode']==0 and '--offline' in attempt['arguments']
assert 'BUILD SUCCESSFUL' in raw(attempt['log']).decode(errors='replace')
derived=obj(B+'evidence/source-derivation.json');identical=[];changed=[]
for d in derived['files']:
    check(d['current'])
    if d['relationship']=='BYTE_IDENTICAL':
        check(d['baseline']);assert raw(d['current']['path'])==raw(d['baseline']['path']);identical.append(d['current']['path'])
    else:changed.append(d['current']['path'])
# Compare every runtime source independently of the declared derivation list.
runtime=[]
for root in ['src','android','upstream-c14/src','upstream-c14/android','app/src']:
    for p in (R/B/root).rglob('*.java'):
        relative=p.relative_to(R/B).as_posix();old=raw(A+relative);new=raw(B+relative)
        if new!=old:runtime.append(relative)
assert runtime==['android/com/videokit/spike/c14/E4CpuAdapter.java'],runtime
path=runtime[0];old=raw(A+path).decode();new=raw(B+path).decode()
before='offMain();PipelineRules.timeline(timeline);TrackedProvider tracked=new TrackedProvider(source);final CpuTaskClient verifier;'
after='offMain();\n        try{PipelineRules.timeline(timeline);}catch(Exception|Error failure){throw new E6AFailure("VALIDATOR","NOT_CREATED",11,"TIMELINE",failure,List.of(),null);}\n        TrackedProvider tracked=new TrackedProvider(source);final CpuTaskClient verifier;'
assert new==old.replace(before,after) and old.count(before)==1
assert new.split('// The actual validation/cleanup')[1]==old.split('// The actual validation/cleanup')[1]
inherit=obj(B+'evidence/native-and-strict-logic-inheritance.json')
for group in inherit.values():
    if isinstance(group,list):
        for x in group:
            if isinstance(x,dict) and all(k in x for k in ['path','baseline','bytes','sha256']):
                check(x);assert raw(x['path'])==raw(x['baseline'])
apk=obj(B+'evidence/apk-audit.json');align=[]
for x in apk['apks']:
    check(x);assert x['signingVerified'] and x['signerCertificateSha256'] in raw(x['signingReport']).decode()
    with zipfile.ZipFile(R/x['path']) as z:
        dex=b''.join(z.read(n) for n in z.namelist() if n.endswith('.dex'))
        assert b'sourceNativeDiagnostic' in dex and b'validatorNativeDiagnostic' in dex
        assert b'E6BPublicPreflightSelfCheck' not in dex and b'E6B_CREATION_PROBE' not in dex
ap=apk['apks'][0]['path'];ar=raw(ap)
with zipfile.ZipFile(R/ap) as z,zipfile.ZipFile(R/prior['apks'][0]['path']) as priorzip:
    for n in apk['nativeLibraries']:
        b=z.read(n['entry']);assert b==raw(n['upstreamPath'])==priorzip.read(n['entry']) and sha(b)==n['sha256'] and len(b)==n['bytes']
        assert b[:6]==b'\x7fELF\x02\x01'
        phoff=struct.unpack_from('<Q',b,32)[0];ents,num=struct.unpack_from('<HH',b,54)
        al=[struct.unpack_from('<IIQQQQQQ',b,phoff+i*ents)[-1] for i in range(num) if struct.unpack_from('<I',b,phoff+i*ents)[0]==1];assert min(al)>=16384
        info=z.getinfo(n['entry']);fn,ex=struct.unpack_from('<HH',ar,info.header_offset+26);offset=info.header_offset+30+fn+ex
        assert info.compress_type==0 and offset%16384==0;align.append(dict(entry=n['entry'],elfLoadAlignments=al,zipOffset=offset))
assert len(align)==7
s=obj(B+'evidence/sbom-difference.json');assert s['coordinates']==35 and s['coordinateDelta']==[] and s['nativeDelta']==[] and not s['nativeRebuild']
assert raw(B+'app/gradle.lockfile')==raw(A+'app/gradle.lockfile')
c=obj(B+'evidence/local-check-results.json')
assert (c['publicEntryCases'],c['assertions'],c['badTimelineCases'],c['badTimelineCpuCreations'],c['legalPreflightCreationTripwire'])==(6,59,5,0,1)
for x in c['inputs']:check(x)
for x in c['commands']:assert x['exitCode']==0;check(x['log'])
log=raw(B+'evidence/public-run-001.log').decode();assert log.count('CASE ')==6 and 'public_entry_cases=6 assertions=59' in log
plan=obj(B+'tools/device_plan.json')
assert plan['apks']==apk['apks'] and plan['priorConsumptionBytes']==53651 and plan['stableBudget']=='730a73e1-50e1-4198-a515-047104f00e31'
assert [x['method'] for x in plan['steps']]==['normalMp4SixRealFrames','normalAviSixRealFrames','capabilityDenialDoesNotOpenSource','cancelRejectsWrongEpochOversizeAndLateFrame']
assert plan['steps'][-1]['arguments']['e4NormalReceiptSha256']=='<SHA256_OF_INDEPENDENTLY_REVIEWED_THIS_E6B_TWO_NORMAL_RESULT_REPORT>'
result=dict(integrity='PASS',sourceFiles=187,immutableFiles=191,priorE6AImmutableFilesVerified=228,sealSha256=sealhash,sourceZip=f['sourceZip'],finalBuildInputSha256=snaphash,apks=apk['apks'],runtimeChanged=runtime,exactOnlyPublicTimelineCatch=True,ownedBodyIdentical=True,nativeIdentical=7,nativeAndZip16kStatic=align,dependencyDelta=0,recordedPublicEntryCases=6,recordedAssertions=59,badTimelineCreations=0,legalCreationTripwire=1,oldP2='E6A-F01_STATIC_CLOSED_RECORDED_PUBLIC_BOUNDARY_SUPPORTED',newFindings=[],normalRegression='SUPPORTED_FOR_SEPARATE_FORMAL_DISPATCH',Android='NOT_RUN',testerAdbCalls=0,testerMediaOrExportReadBytes=0,testerGradleNativeModelRuns=0,inFlight=[])
Path(__file__).with_name('identity-and-recorded-static-audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:result[k] for k in ['integrity','sourceFiles','immutableFiles','runtimeChanged','nativeIdentical','recordedPublicEntryCases','recordedAssertions','oldP2','newFindings']}))
