"""Read-only integrity checks. Never builds or runs helpers or accesses test_media."""
import hashlib,json,zipfile
from pathlib import Path
from profile_audit import verify_configuration,verify_upstreams,is_fixture
BASE=Path(__file__).resolve().parents[1];ROOT=BASE.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def verify():
    freeze=json.loads((BASE/'evidence/freeze-summary.json').read_text(encoding='utf-8'));source=json.loads((BASE/'evidence/source-manifest.json').read_text(encoding='utf-8'))
    for r in freeze['files']+freeze['selfcheckFiles']+source['files']:
        p=ROOT/r['path'];assert p.resolve().is_relative_to(ROOT.resolve()) and p.stat().st_size==r['bytes'] and sha(p)==r['sha256'],r['path']
    with zipfile.ZipFile(BASE/'artifacts/E2A-source.zip') as z:
        assert set(z.namelist())=={r['path'] for r in source['files']}
        for r in source['files']:assert hashlib.sha256(z.read(r['path'])).hexdigest()==r['sha256']
    manifest=json.loads((BASE/'manifest/branches.json').read_text(encoding='utf-8'));rows=manifest['branches']
    configuration=verify_configuration(manifest);assert configuration['configurationVerified'] and configuration['runtimePolicy']=='APPROVED_TOOL_STRATEGY' and configuration['realExecutionEnabled'] is False
    assert len(rows)==61 and sum(r['nonquery'] for r in rows)+48==351
    assert sum(r['queriesNew']+r['queriesReplay'] for r in rows)==101
    assert sum(r['inputBytes'] for r in rows)+32==1573522 and sum(r['inputCalls'] for r in rows)+2==59
    assert sum(r['seconds'] for r in rows)+20+20+10+18==180
    assert manifest['executionOrder'][-2:]==['P10-D','P10-C'] and not manifest['experimentEnabled']
    upstream=verify_upstreams()
    assert sha(BASE/'upstream-e2/freeze-summary.json')==freeze['upstreamFreezeSha256']
    assert sha(BASE/'upstream-e1e/freeze-summary.json')==freeze['upstreamE1EFreezeSha256']
    for path,digest in manifest['inputs'].items():assert sha(ROOT/path)==digest
    audit=json.loads((BASE/'evidence/audit.json').read_text(encoding='utf-8'));negative=json.loads((BASE/audit['targetedEvidence']).read_text(encoding='utf-8'))
    assert audit['status']==negative['status']=='PASS' and audit['syntheticAssertions']+negative['assertions']==freeze['syntheticAssertions']
    assert freeze['integrationAssertions']==audit['syntheticAssertions'] and freeze['targetedAssertions']==negative['assertions']
    bridge=json.loads((BASE/audit['javaBridgeEvidence']).read_text(encoding='utf-8'))
    assert bridge['status']=='PASS' and bridge['noInFlight'] is True and bridge['pending'] is None
    assert bridge['assertions']==audit['javaBridgeAssertions']==freeze['javaBridgeAssertions'] and freeze['javaBridgeAssertions']>0
    assert bridge['completedProcesses']==bridge['plannedProcesses']==freeze['javaBridgeProcesses']
    assert manifest['schema']==3 and manifest['scope']=='E2A_CONFIGURATION_PENDING_ADMISSION_REVIEW' and manifest['realExecutionEnabled'] is False and set(manifest['fixes'])=={'T01','T02','T03','T04','T05'}
    assert set(manifest['completionFixes'])=={'C01','C02'}
    assert set(manifest['startupFixes'])=={'D01'}
    assert manifest['callbackBudget']['fixedWorkers']==2 and manifest['callbackBudget']['maxLiveCells']==8 and manifest['callbackBudget']['maxQueuedPlusActiveNotifications']==8 and manifest['callbackBudget']['maxCallbacksPerCell']==4
    assert audit['startupFixVerified'] and audit['startupLifecycleVerified'] and audit['oldE1EFrozenFilesVerified']==188 and audit['oldE1ESourceFilesVerified']==33 and audit['configurationVerified']
    assert audit['oldE2FrozenFilesVerified']==upstream['oldE2FrozenFilesVerified']==231 and audit['oldE2SourceFilesVerified']==upstream['oldE2SourceFilesVerified']==43
    assert audit['runtimeObservationVerified'] and audit['javaBridgeVerified'] and freeze['runtimeObservationVerified']
    assert audit['actualRuntimeGateStopVerified'] and freeze['actualRuntimeGateStopVerified']
    assert audit['runtimeAdmission']==freeze['runtimeAdmission']=='BLOCKED_R_HANDLES_519_GT_512'
    assert freeze['driverSyntheticAssertions']==freeze['syntheticAssertions'] and audit['runtimeObservation']['mockMetricsUsed'] is True
    actual=json.loads((BASE/freeze['actualRuntimeGateStopEvidence']).read_text(encoding='utf-8'))
    assert actual['exitCode']!=0 and actual['witness']['runtimeObservation']['observation']['scope']=='APPROVED_TOOL_RUNTIME_OBSERVATION'
    assert actual['witness']['runtimeObservation']['observation']['peaks']['R']['handles']==519 and actual['witness']['usage']['ib']==0
    assert freeze['state']=='ADAPTERS_FROZEN_PENDING_INDEPENDENT_REVIEW' and freeze['realExecutionEnabled'] is False
    assert freeze['syntheticFixtureBytes']<=2097152 and freeze['logsAndEvidenceBytesIncludingSeal']<=4194304
    folders=('src','tools','manifest','profiles','upstream-e2','upstream-e1e')
    actual_sources={p.relative_to(ROOT).as_posix() for folder in folders for p in (BASE/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts}
    assert actual_sources=={r['path'] for r in source['files']}
    checks=[p for p in (BASE/'selfcheck').rglob('*') if p.is_file()]
    assert {p.relative_to(ROOT).as_posix() for p in checks}=={r['path'] for r in freeze['selfcheckFiles']}
    docs=[ROOT/'docs/coder'/('D1_E2A_'+name+'_V1.0.md') for name in ('DELIVERY','REAL_IO_ADMISSION','EXECUTION_APPENDIX')]
    sealed=[p for p in (BASE/'artifacts').rglob('*') if p.is_file()]+[p for p in (BASE/'evidence').glob('*') if p.is_file() and p.name!='freeze-summary.json']+docs
    assert {p.relative_to(ROOT).as_posix() for p in sealed}=={r['path'] for r in freeze['files']}
    fixture_bytes=sum(p.stat().st_size for p in checks if is_fixture(p))
    logs_before_seal=sum(p.stat().st_size for p in checks if not is_fixture(p))+sum(p.stat().st_size for p in (BASE/'evidence').glob('*') if p.is_file() and p.name!='freeze-summary.json')
    assert fixture_bytes==freeze['syntheticFixtureBytes']<=2097152
    assert logs_before_seal==freeze['logsAndEvidenceBytesBeforeSeal']
    assert logs_before_seal+(BASE/'evidence/freeze-summary.json').stat().st_size==freeze['logsAndEvidenceBytesIncludingSeal']<=4194304
    print(json.dumps({'integrity':'PASS','state':freeze['state'],'sourceFiles':len(source['files']),'frozenFiles':len(freeze['files']),'selfcheckFiles':len(freeze['selfcheckFiles']),
                      'syntheticAssertions':freeze['syntheticAssertions'],'javaBridgeAssertions':freeze['javaBridgeAssertions'],'oldE2Records':231,'oldE2Sources':43,
                      'oldE1ERecords':188,'oldE1ESources':33,'preservedBaselines':upstream['preservedBaselines'],'freezeSha256':sha(BASE/'evidence/freeze-summary.json'),'media':'NOT_RUN'}))
if __name__=='__main__':verify()
