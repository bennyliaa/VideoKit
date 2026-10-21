"""Read-only E2D configuration and frozen-dependency checks; no media access."""
import hashlib,json,zipfile
from pathlib import Path

BASE=Path(__file__).resolve().parents[1];ROOT=BASE.parents[2]
SOURCE_FOLDERS=('src','tools','manifest','profiles','upstream-e2c','upstream-e2b','upstream-e2a','upstream-e2','upstream-e1e')
E2C_FREEZE_SHA='bccacb2e98b1f4a4d3017fc8efb9bd0f047e58d91e7c910303fff40eb3896179'
E2C_SOURCE_SHA='035263006cbaa99837656bb2b66045a3f5c6181ab8af8c8fe3f5bcf5ba3e5934'

def read(path):return json.loads(path.read_text(encoding='utf-8-sig'))
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def documentation(value):
    path=Path(value)
    if not path.is_absolute():path=ROOT/path
    assert path.resolve().is_relative_to((ROOT/'docs').resolve()),'DOCUMENT_SOURCE_MUST_STAY_UNDER_DOCS'
    return path
def files_under(folder):
    return sorted(path for path in (BASE/folder).rglob('*') if path.is_file() and '__pycache__' not in path.parts)
def is_fixture(path):
    return path.suffix.lower() not in {'.slot','.json','.q','.ops','.log','.txt','.csv','.stdout','.stderr','.err'}

def verify_upstreams():
    result={}
    for folder,label,counts,archive in (
        ('upstream-e2c','E2C',(41,62,70),'E2C-source.zip'),
        ('upstream-e2b','E2B',(27,172,63),'E2B-source.zip'),
        ('upstream-e2a','E2A',(25,301,53),'E2A-source.zip'),
        ('upstream-e2','E2',(15,216,43),'E2-source.zip'),
        ('upstream-e1e','E1E',(11,177,33),'E1E-source.zip')):
        frozen=read(BASE/folder/'freeze-summary.json');source=read(BASE/folder/'source-manifest.json')
        assert (len(frozen['files']),len(frozen['selfcheckFiles']),len(source['files']))==counts,(folder,counts)
        for row in frozen['files']+frozen['selfcheckFiles']+source['files']:
            path=documentation(row['path']);assert path.stat().st_size==row['bytes'] and sha(path)==row['sha256'],row['path']
        with zipfile.ZipFile(BASE/folder/archive) as zipped:
            assert len(zipped.namelist())==len(source['files']) and set(zipped.namelist())=={row['path'] for row in source['files']}
            for row in source['files']:
                data=zipped.read(row['path']);assert len(data)==row['bytes'] and hashlib.sha256(data).hexdigest()==row['sha256'],row['path']
        result['old'+label+'FrozenFilesVerified']=counts[0]+counts[1]
        result['old'+label+'SourceFilesVerified']=counts[2]
        result['old'+label+'FileBreakdown']=dict(frozen=counts[0],selfcheck=counts[1])
        result['old'+label+'FreezeSha256']=sha(BASE/folder/'freeze-summary.json')
    assert (BASE/'upstream-e2c/E2C-source.zip').stat().st_size==6327273 and sha(BASE/'upstream-e2c/E2C-source.zip')==E2C_SOURCE_SHA
    assert result['oldE2CFreezeSha256']==E2C_FREEZE_SHA
    old_c=read(BASE/'upstream-e2c/freeze-summary.json')
    assert old_c['state']=='E2C_FROZEN_PENDING_INDEPENDENT_REVIEW' and old_c['realExecutionEnabled'] is False
    assert old_c['targetedAssertions']==old_c['driverSyntheticAssertions']==1125 and old_c['actualFullStatus']=='NOT_RUN' and old_c['actualFullAssertions']==0
    assert old_c['postFixOSComparisonRun'] is False and old_c['noInFlightVerified'] is True
    result.update(oldE2CTargetedAssertions=1125,oldE2CActualFullStatus='NOT_RUN',oldE2CActualFullAssertions=0,oldE2CPostFixOSComparisonRun=False)
    assert (BASE/'upstream-e2b/E2B-source.zip').stat().st_size==3141738
    assert sha(BASE/'upstream-e2b/E2B-source.zip')=='05eef8aa55013603070fc9fd77ac2adb6ff916ab73825ef7f8e6456ad9a26c43'
    assert result['oldE2BFreezeSha256']=='93941847231390a5ffe4af8656cb5ce8d3120b9c07a16dcf55fcc9d802bf9ab0'
    old_b=read(BASE/'upstream-e2b/freeze-summary.json')
    assert old_b['state']=='E2B_FROZEN_PENDING_INDEPENDENT_REVIEW' and old_b['realExecutionEnabled'] is False
    assert old_b['actualFullStatus']=='FAIL' and old_b['actualFullReportedAssertions']==77 and old_b['actualFullAssertions']==0
    assert old_b['targetedAssertions']==old_b['driverSyntheticAssertions']==955
    assert old_b['runtimeAdmission']=='BLOCKED_G_HANDLES_369_GT_256_AND_DELTA_209_GT_64'
    result.update(oldE2BTargetedAssertions=955,oldE2BActualFullStatus='FAIL',oldE2BActualFullReportedAssertions=77,oldE2BActualFullAssertions=0,oldE2BRuntimeAdmission=old_b['runtimeAdmission'])
    assert (BASE/'upstream-e2a/E2A-source.zip').stat().st_size==1541520
    assert sha(BASE/'upstream-e2a/E2A-source.zip')=='9ea9be9c6a2e734e364bcc22e5946e91eab9c359474ada2870107e56d5526a50'
    assert result['oldE2AFreezeSha256']=='a74cceea70b94354f328cb348ef5c0dd126ce50ca1125b3d7f8fcf401c3ff37e'
    old_a=read(BASE/'upstream-e2a/freeze-summary.json')
    assert old_a['state']=='ADAPTERS_FROZEN_PENDING_INDEPENDENT_REVIEW' and old_a['realExecutionEnabled'] is False
    assert old_a['driverSyntheticAssertions']==old_a['syntheticAssertions']==1003 and old_a['javaBridgeAssertions']==87
    assert old_a['runtimeAdmission']=='BLOCKED_R_HANDLES_519_GT_512'
    result.update(oldE2ADriverSyntheticAssertions=1003,oldE2AJavaBridgeAssertions=87,oldE2ARuntimeAdmission=old_a['runtimeAdmission'])
    assert (BASE/'upstream-e2/E2-source.zip').stat().st_size==739519
    assert sha(BASE/'upstream-e2/E2-source.zip')=='4e3510c4cba3c99919faf26cf5ff72ab2ebe4ada2fcf7db3690fba4451b312c2'
    baselines=read(BASE/'upstream-e1e/preserved-baselines.json');assert len(baselines['files'])==13
    for row in baselines['files']:assert sha(documentation(row['path']))==row['sha256'],row['path']
    result['preservedBaselines']=13;return result

def verify_production_binding():
    """Bind every copied production/configuration byte and all compiled binaries."""
    assert sha(BASE/'upstream-e2c/freeze-summary.json')==E2C_FREEZE_SHA
    assert sha(BASE/'upstream-e2c/E2C-source.zip')==E2C_SOURCE_SHA
    frozen=read(BASE/'upstream-e2c/freeze-summary.json')
    prefix='docs/coder/d1e2c/'
    source_record=next(row for row in frozen['files'] if row['path']==prefix+'evidence/source-manifest.json')
    source_path=BASE/'upstream-e2c/source-manifest.json'
    assert source_path.stat().st_size==source_record['bytes'] and sha(source_path)==source_record['sha256'],'COPIED_E2C_SOURCE_MANIFEST_MUST_BIND_TO_FROZEN_RECORD'
    source=read(source_path)
    branch_record=next(row for row in source['files'] if row['path']==prefix+'manifest/branches.json')
    assert (BASE/'upstream-e2c/branches.json').stat().st_size==branch_record['bytes'] and sha(BASE/'upstream-e2c/branches.json')==branch_record['sha256']
    expected={row['path'][len(prefix):]:row for row in source['files'] if row['path'].startswith(prefix) and row['path'][len(prefix):].split('/')[0] in {'src','manifest','profiles'}}
    actual={path.relative_to(BASE).as_posix():path for folder in ('src','manifest','profiles') for path in files_under(folder)}
    assert set(actual)==set(expected) and sum(name.startswith('src/') for name in expected)==32,'E2D_PRODUCTION_FILE_SET_MUST_EQUAL_FROZEN_E2C'
    bindings=[]
    for name,row in sorted(expected.items()):
        path=actual[name];assert path.stat().st_size==row['bytes'] and sha(path)==row['sha256'],'E2D_PRODUCTION_BYTES_CHANGED:'+name
        bindings.append(dict(path=name,bytes=row['bytes'],sha256=row['sha256'],upstreamPath=row['path']))
    binaries={row['path'][len(prefix):]:row for row in frozen['files'] if row['path'].startswith(prefix+'artifacts/') and (row['path']==prefix+'artifacts/E2C.dll' or row['path'].startswith(prefix+'artifacts/java/'))}
    actual_binaries={path.relative_to(BASE).as_posix():path for path in (BASE/'artifacts').rglob('*') if path.is_file() and (path.suffix.lower() in {'.dll','.class'})}
    assert set(actual_binaries)==set(binaries) and len(binaries)==10,'E2D_COMPILED_ARTIFACT_SET_CHANGED'
    artifacts=[]
    for name,row in sorted(binaries.items()):
        path=actual_binaries[name];assert path.stat().st_size==row['bytes'] and sha(path)==row['sha256'],'E2D_COMPILED_ARTIFACT_BYTES_CHANGED:'+name
        artifacts.append(dict(path=name,bytes=row['bytes'],sha256=row['sha256'],upstreamPath=row['path']))
    return dict(scope='E2D_BYTE_IDENTICAL_FROZEN_E2C_PRODUCTION_AND_ARTIFACTS',upstreamFreezeSha256=E2C_FREEZE_SHA,upstreamSourceZipSha256=E2C_SOURCE_SHA,
                productionSourceFiles=32,configurationFiles=len(bindings)-32,productionAndConfigurationFiles=bindings,compiledArtifacts=artifacts,compileInvocations=0,repairCompilations=0,productionChanges=0)

def verify_configuration(manifest):
    binding=verify_production_binding()
    inputs=read(BASE/'profiles/inputs.json');machine=read(BASE/'profiles/machine.json');cases=read(BASE/'profiles/cases.json');runtime=read(BASE/'profiles/runtime-policy.json')
    original=read(BASE/'upstream-e2c/branches.json');assert manifest==original,'E2D_MANIFEST_MUST_REMAIN_FROZEN_E2C'
    assert manifest['scope']=='E2C_CONFIGURATION_PENDING_ADMISSION_REVIEW' and manifest['schema']==3 and manifest['experimentEnabled'] is manifest['realExecutionEnabled'] is False
    assert inputs['schema']==machine['schema']==cases['schema']==runtime['schema']==1
    assert inputs['executionAuthorized'] is cases['executionEnabled'] is runtime['executionAuthorized'] is False
    assert runtime['state']=='APPROVED_TOOL_STRATEGY' and machine['resourceAccountingBoundary']['runtimeStopThresholdsApproved'] is True
    assert cases['limits']==manifest['limits'] and len(cases['cases'])==len(manifest['branches'])==61
    by_id={row['id']:row for row in cases['cases']}
    allocations=('task','nonquery','queriesNew','queriesReplay','inputBytes','inputCalls','validationBytes','newTargets','newRecords','outputBytes','mediaHandles','buffers','seconds','operations')
    for row in manifest['branches']:
        assert all(row[key]==by_id[row['id']][key] for key in allocations),row['id']
        assert by_id[row['id']]['realIO']['executionStatus']=='NOT_RUN_CONFIGURATION_ONLY'
        required=by_id[row['id']]['requiredDurability'];assert required['productReady'] is required['businessCommit'] is required['powerLossClaim'] is False
    rows=manifest['branches'];assert sum(row['nonquery'] for row in rows)+48==351 and sum(row['queriesNew']+row['queriesReplay'] for row in rows)==101
    assert sum(row['inputBytes'] for row in rows)+32==1573522 and sum(row['inputCalls'] for row in rows)+2==59
    assert sum(row['seconds'] for row in rows)+20+20+10+18==180 and manifest['executionOrder'][-2:]==['P10-D','P10-C']
    assert manifest['callbackBudget']==original['callbackBudget'] and manifest['callbackBudget']['fixedWorkers']==2 and manifest['callbackBudget']['maxLiveCells']==8
    for name,digest in manifest['inputs'].items():assert sha(documentation(name))==digest,name
    for row in inputs['sourceDocuments'].values():
        path=documentation(row['path']);assert path.stat().st_size==row['bytes'] and sha(path)==row['sha256']
    historical=read(documentation(inputs['sourceDocuments']['R2_HISTORICAL_IDENTITIES']['path']));historical_by_path={row['relative_path']:row for row in historical['inputs']}
    files={'L':('03_large_files/large_video_over_2GiB.mkv',3212959911),'C':('04_corrupted_files/corrupted_video.mp4',4096),'Z':('04_corrupted_files/empty_video.mkv',0)}
    assert set(inputs['inputs'])==set(cases['inputs'])==set(files)
    for alias,(relative,length) in files.items():
        row=inputs['inputs'][alias];case=cases['inputs'][alias];old=historical_by_path[relative]
        # Compare declared strings only. Never resolve/stat/open the media path.
        assert Path(row['path'])==ROOT/'test_media'/relative and case['absolutePath']==row['path']
        assert row['historical']['bytes']==row['currentStat']['bytes']==case['lengthBytes']==old['bytes']==length
        assert row['historical']['sha256']==case['historicalSha256']==old['sha256']
        assert row['currentContentVerified'] is case['historicalHashRecomputed'] is False and row['currentVersionGuarantee']=='UNPROVEN'
    assert inputs['activity']['mediaBytesRead']==inputs['activity']['mediaHashesComputed']==machine['activity']['mediaBytesRead']==machine['activity']['mediaHashesComputed']==0
    assert inputs['admissionFacts']['currentContentHashProven'] is inputs['admissionFacts']['guardJavaReferenceSameObjectProven'] is False and inputs['admissionFacts']['versionGuarantee']=='UNPROVEN'
    assert cases['boundaryBytes']==inputs['largeFileWindows']['boundaryBytes']==2147483648
    windows=inputs['largeFileWindows']['windows'];assert [row['offset'] for row in windows]==[2147418112,2147450880,2147483648,3212894375] and all(row['requestedBytes']==65536 for row in windows)
    assert runtime['managedLimits']==dict(osResources=24,mediaHandles=6,buffers64KiB=8)
    assert (runtime['intervalSeconds'],runtime['maxSamples'],runtime['maxGapSeconds'],runtime['sampleDeadlineSeconds'])==(1,201,2.5,.1)
    assert runtime['maxThreadEntries']==16384 and runtime['maxRecordBytes']==128 and runtime['maxLogBytes']==26752 and runtime['minimumAvailablePhysicalBytes']==2147483648
    assert runtime['limits']=={
        'G':dict(threads=16,handles=256,workingSetBytes=268435456,privateBytes=268435456,deltaThreads=12,deltaHandles=64,deltaWorkingSetBytes=134217728,deltaPrivateBytes=134217728),
        'J':dict(threads=64,handles=512,workingSetBytes=805306368,privateBytes=805306368,deltaThreads=32,deltaHandles=128,deltaWorkingSetBytes=268435456,deltaPrivateBytes=268435456),
        'R':dict(threads=64,handles=512,workingSetBytes=536870912,privateBytes=536870912,deltaThreads=32,deltaHandles=128,deltaWorkingSetBytes=268435456,deltaPrivateBytes=268435456)}
    assert runtime['observer']['rpcCalls']==runtime['observer']['mediaCalls']==runtime['observer']['journalTransactions']==0
    for row in cases['cases']:
        if row['id'] in {'Q01-SEQ','Q05-STREAM','Q06-LOST','Q08-READY','Q07-READYFIRST'}:assert row['productVariant']['admission']=='NOT_RUN_DURABILITY_UNPROVEN'
    return dict(configurationVerified=True,realExecutionEnabled=False,cases=61,boundaryBytes=2147483648,runtimePolicy='APPROVED_TOOL_STRATEGY',GDeltaThreads=12,
                eventLogCap=104320,metricLogCap=26752,historicalSourcesVerified=len(inputs['sourceDocuments']),mediaRead=False,mediaStat=False,productionBinding=binding)
