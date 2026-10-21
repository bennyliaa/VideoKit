"""Read configuration/documentation only; never stat, open, or hash a media input."""
import hashlib,json
from pathlib import Path
BASE=Path(__file__).resolve().parents[1];ROOT=BASE.parents[2]
def read(path):return json.loads(path.read_text(encoding='utf-8-sig'))
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def documentation(path):
    value=Path(path)
    if not value.is_absolute():value=ROOT/value
    assert value.resolve().is_relative_to((ROOT/'docs').resolve()),'DOCUMENT_SOURCE_MUST_STAY_UNDER_DOCS'
    return value
def verify_configuration(manifest):
    inputs=read(BASE/'profiles/inputs.json');machine=read(BASE/'profiles/machine.json')
    cases=read(BASE/'profiles/cases.json');runtime=read(BASE/'profiles/runtime-policy.json')
    upstream=read(BASE/'upstream-e1e/branches.json')
    assert inputs['schema']==machine['schema']==cases['schema']==runtime['schema']==1
    assert inputs['executionAuthorized'] is False and cases['executionEnabled'] is False
    assert runtime['state']=='PROPOSED' and runtime['executionAuthorized'] is False
    assert manifest['scope']=='E2_CONFIGURATION_PENDING_ADMISSION_REVIEW' and manifest['realExecutionEnabled'] is False
    assert cases['boundaryBytes']==inputs['largeFileWindows']['boundaryBytes']==2147483648
    assert cases['limits']==manifest['limits']==upstream['limits']
    expected_files={'L':('03_large_files/large_video_over_2GiB.mkv',3212959911),'C':('04_corrupted_files/corrupted_video.mp4',4096),'Z':('04_corrupted_files/empty_video.mkv',0)}
    assert set(inputs['inputs'])==set(cases['inputs'])==set(expected_files)
    for source in inputs['sourceDocuments'].values():
        path=documentation(source['path']);assert path.stat().st_size==source['bytes'] and sha(path)==source['sha256']
    historical=read(documentation(inputs['sourceDocuments']['R2_HISTORICAL_IDENTITIES']['path']))
    historical_by_path={row['relative_path']:row for row in historical['inputs']}
    for alias,(relative,length) in expected_files.items():
        entry=inputs['inputs'][alias];case=cases['inputs'][alias];old=historical_by_path[relative]
        # Lexical comparisons only. The real input path is never resolved or opened.
        assert Path(entry['path'])==ROOT/'test_media'/relative and case['absolutePath']==entry['path']
        assert entry['historical']['bytes']==entry['currentStat']['bytes']==case['lengthBytes']==old['bytes']==length
        assert entry['historical']['sha256']==case['historicalSha256']==old['sha256']
        assert entry['currentContentVerified'] is False and entry['currentVersionGuarantee']=='UNPROVEN'
        assert case['historicalHashRecomputed'] is False and isinstance(entry['currentStat']['mtimeUtc'],str)
    assert inputs['activity']['mediaBytesRead']==inputs['activity']['mediaHashesComputed']==0
    assert machine['activity']['mediaBytesRead']==machine['activity']['mediaHashesComputed']==0
    assert inputs['admissionFacts']['currentContentHashProven'] is False and inputs['admissionFacts']['versionGuarantee']=='UNPROVEN'
    assert inputs['admissionFacts']['guardJavaReferenceSameObjectProven'] is False
    assert machine['resourceAccountingBoundary']['runtimeStopThresholdsApproved'] is False
    base_path=documentation(cases['baseManifest']['path']);assert sha(base_path)==cases['baseManifest']['sha256']
    assert len(cases['cases'])==len(manifest['branches'])==len(upstream['branches'])==61
    allocations=('task','nonquery','queriesNew','queriesReplay','inputBytes','inputCalls','validationBytes','newTargets','newRecords','outputBytes','mediaHandles','buffers','seconds','operations')
    by_id={row['id']:row for row in cases['cases']};current={row['id']:row for row in manifest['branches']}
    assert set(by_id)==set(current)=={row['id'] for row in upstream['branches']}
    for original in upstream['branches']:
        row=by_id[original['id']];now=current[original['id']]
        assert all(row[key]==now[key]==original[key] for key in allocations),original['id']
        assert row['realIO']['executionStatus']=='NOT_RUN_CONFIGURATION_ONLY'
        durability=row['requiredDurability'];assert durability['productReady'] is False and durability['businessCommit'] is False and durability['powerLossClaim'] is False
    windows=inputs['largeFileWindows']['windows']
    assert [row['offset'] for row in windows]==[2147418112,2147450880,2147483648,3212894375] and all(row['requestedBytes']==65536 for row in windows)
    assert runtime['managedLimits']=={'osResources':24,'mediaHandles':6,'buffers64KiB':8}
    assert runtime['intervalSeconds']>0 and runtime['maxSamples']>0 and runtime['sampleDeadlineSeconds']>0
    assert runtime['observer']['rpcCalls']==runtime['observer']['mediaCalls']==runtime['observer']['journalTransactions']==0
    adapter=read(BASE/'evidence/adapter-feasibility.json')
    assert sha(documentation(adapter['sourceArchive']['path']))==adapter['sourceArchive']['sha256']
    assert adapter['mediaBytesRead']==adapter['helpersStarted']==adapter['experimentsRun']==0
    assert adapter['r4Preservation']['extraControlTokens']==adapter['r4Preservation']['extraRPC']==0
    return dict(configurationVerified=True,realExecutionEnabled=False,cases=61,boundaryBytes=2147483648,runtimePolicy='PROPOSED',historicalSourcesVerified=len(inputs['sourceDocuments']),mediaRead=False,mediaStat=False)
