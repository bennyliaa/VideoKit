"""Read-only E2B integrity and outcome verification; never runs a diagnostic."""
import hashlib,json,zipfile
from pathlib import Path
from profile_audit import verify_configuration,verify_upstreams,is_fixture,SOURCE_FOLDERS
from audit import audit
BASE=Path(__file__).resolve().parents[1];ROOT=BASE.parents[2]
def read(path):return json.loads(path.read_text(encoding='utf-8-sig'))
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def verify():
    frozen=read(BASE/'evidence/freeze-summary.json');source=read(BASE/'evidence/source-manifest.json')
    assert frozen['state']=='E2B_FROZEN_PENDING_INDEPENDENT_REVIEW' and frozen['realExecutionEnabled'] is False and frozen['noInFlightVerified'] is True
    assert source['scope']=='E2B_ADAPTER_SOURCE_AND_COMPLETE_UPSTREAM_RELATION'
    for entry in frozen['files']+frozen['selfcheckFiles']+source['files']:
        path=ROOT/entry['path'];assert path.resolve().is_relative_to((ROOT/'docs').resolve()) and path.stat().st_size==entry['bytes'] and sha(path)==entry['sha256'],entry['path']
    with zipfile.ZipFile(BASE/'artifacts/E2B-source.zip') as zipped:
        assert set(zipped.namelist())=={entry['path'] for entry in source['files']}
        for entry in source['files']:assert hashlib.sha256(zipped.read(entry['path'])).hexdigest()==entry['sha256']
    manifest=read(BASE/'manifest/branches.json');configuration=verify_configuration(manifest);rows=manifest['branches']
    assert configuration['configurationVerified'] and configuration['runtimePolicy']=='APPROVED_TOOL_STRATEGY' and configuration['realExecutionEnabled'] is False
    assert len(rows)==61 and sum(row['nonquery'] for row in rows)+48==351 and sum(row['queriesNew']+row['queriesReplay'] for row in rows)==101
    assert sum(row['inputBytes'] for row in rows)+32==1573522 and sum(row['inputCalls'] for row in rows)+2==59
    assert sum(row['seconds'] for row in rows)+20+20+10+18==180 and manifest['executionOrder'][-2:]==['P10-D','P10-C'] and not manifest['experimentEnabled']
    assert manifest['schema']==3 and manifest['scope']=='E2B_CONFIGURATION_PENDING_ADMISSION_REVIEW' and manifest['realExecutionEnabled'] is False
    assert set(manifest['fixes'])=={'T01','T02','T03','T04','T05'} and set(manifest['completionFixes'])=={'C01','C02'} and set(manifest['startupFixes'])=={'D01'}
    assert manifest['callbackBudget']['fixedWorkers']==2 and manifest['callbackBudget']['maxLiveCells']==8 and manifest['callbackBudget']['maxQueuedPlusActiveNotifications']==8 and manifest['callbackBudget']['maxCallbacksPerCell']==4
    for name,digest in manifest['inputs'].items():
        path=ROOT/name;assert path.resolve().is_relative_to((ROOT/'docs').resolve()) and sha(path)==digest
    upstream=verify_upstreams()
    assert frozen['upstreamFreezeSha256']==upstream['oldE2AFreezeSha256'] and frozen['upstreamE2FreezeSha256']==upstream['oldE2FreezeSha256'] and frozen['upstreamE1EFreezeSha256']==upstream['oldE1EFreezeSha256']
    for key,value in upstream.items():assert frozen[key]==value,key
    recorded=read(BASE/'evidence/audit.json');current=audit()
    assert recorded['status']==current['status']=='PASS' and recorded['noInFlightVerified'] is current['noInFlightVerified'] is True
    keys=('targetedEvidence','targetedAssertions','actualFullEvidence','actualFullStatus','actualFullReportedAssertions','actualFullAssertions','driverSyntheticAssertions',
          'diagnosticEvidence','diagnosticEligible','runtimeAdmission','aliasFixVerified','diagnosticVerified','mockAssertionsIncluded')
    for key in keys:assert frozen[key]==recorded[key]==current[key],key
    assert frozen['diagnosticValidation']==current['diagnostic']['validation'] and frozen['diagnosticLogBytesIncludingSummary']==current['diagnostic']['diagnosticLogBytesIncludingSummary']<=524288
    assert frozen['syntheticAssertions']==frozen['driverSyntheticAssertions']==frozen['targetedAssertions']+frozen['actualFullAssertions']
    assert frozen['actualFullAssertions']==(frozen['actualFullReportedAssertions'] if frozen['actualFullStatus']=='PASS' else 0)
    actual_sources={path.relative_to(ROOT).as_posix() for folder in SOURCE_FOLDERS for path in (BASE/folder).rglob('*') if path.is_file() and '__pycache__' not in path.parts}
    assert actual_sources=={entry['path'] for entry in source['files']}
    checks=[path for path in (BASE/'selfcheck').rglob('*') if path.is_file()]
    assert {path.relative_to(ROOT).as_posix() for path in checks}=={entry['path'] for entry in frozen['selfcheckFiles']}
    docs=[ROOT/'docs/coder'/('D1_E2B_'+name+'_V1.0.md') for name in ('DELIVERY','REAL_IO_ADMISSION','EXECUTION_APPENDIX')]
    sealed=[path for path in (BASE/'artifacts').rglob('*') if path.is_file()]+[path for path in (BASE/'evidence').glob('*') if path.is_file() and path.name!='freeze-summary.json']+docs
    assert {path.relative_to(ROOT).as_posix() for path in sealed}=={entry['path'] for entry in frozen['files']}
    fixture_bytes=sum(path.stat().st_size for path in checks if is_fixture(path))
    logs=sum(path.stat().st_size for path in checks if not is_fixture(path))+sum(path.stat().st_size for path in (BASE/'evidence').glob('*') if path.is_file() and path.name!='freeze-summary.json')
    assert fixture_bytes==frozen['syntheticFixtureBytes']<=2097152 and logs==frozen['logsAndEvidenceBytesBeforeSeal']
    assert logs+(BASE/'evidence/freeze-summary.json').stat().st_size==frozen['logsAndEvidenceBytesIncludingSeal']<=4194304
    print(json.dumps(dict(integrity='PASS',state=frozen['state'],sourceFiles=len(source['files']),frozenFiles=len(frozen['files']),selfcheckFiles=len(frozen['selfcheckFiles']),
                          actualFullStatus=frozen['actualFullStatus'],actualFullAssertions=frozen['actualFullAssertions'],targetedAssertions=frozen['targetedAssertions'],
                          oldE2ADriverAssertions=1003,oldE2ABridgeAssertions=87,oldE2ARecords=326,oldE2ASources=53,
                          oldE2Records=231,oldE2Sources=43,oldE1ERecords=188,oldE1ESources=33,preservedBaselines=13,
                          freezeSha256=sha(BASE/'evidence/freeze-summary.json'),realMedia='NOT_RUN')))
if __name__=='__main__':verify()
