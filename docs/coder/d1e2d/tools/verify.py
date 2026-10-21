"""Read-only E2D frozen-evidence verification; never imports or runs the probe."""
import hashlib,json,zipfile
from pathlib import Path
from profile_audit import verify_configuration,verify_upstreams,is_fixture,SOURCE_FOLDERS
from audit import audit

BASE=Path(__file__).resolve().parents[1];ROOT=BASE.parents[2]
def read(path):return json.loads(path.read_text(encoding='utf-8-sig'))
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def verify():
    frozen=read(BASE/'evidence/freeze-summary.json');source=read(BASE/'evidence/source-manifest.json')
    assert frozen['state']=='E2D_FROZEN_PENDING_INDEPENDENT_REVIEW' and frozen['realExecutionEnabled'] is False and frozen['noInFlightVerified'] is True
    assert source['scope']=='E2D_UNCHANGED_E2C_PRODUCTION_COMPARISON_TOOLS_AND_COMPLETE_UPSTREAM_RELATION'
    for row in frozen['files']+frozen['selfcheckFiles']+source['files']:
        path=ROOT/row['path'];assert path.resolve().is_relative_to((ROOT/'docs').resolve()) and path.stat().st_size==row['bytes'] and sha(path)==row['sha256'],row['path']
    with zipfile.ZipFile(BASE/'artifacts/E2D-source.zip') as zipped:
        assert len(zipped.namelist())==len(source['files']) and set(zipped.namelist())=={row['path'] for row in source['files']}
        for row in source['files']:
            data=zipped.read(row['path']);assert len(data)==row['bytes'] and hashlib.sha256(data).hexdigest()==row['sha256'],row['path']
    configuration=verify_configuration(read(BASE/'manifest/branches.json'));upstream=verify_upstreams()
    assert frozen['productionBinding']==configuration['productionBinding'] and frozen['productionBindingVerified'] is True
    assert frozen['upstreamFreezeSha256']==upstream['oldE2CFreezeSha256'] and frozen['upstreamE2BFreezeSha256']==upstream['oldE2BFreezeSha256']
    assert frozen['upstreamE2AFreezeSha256']==upstream['oldE2AFreezeSha256'] and frozen['upstreamE2FreezeSha256']==upstream['oldE2FreezeSha256'] and frozen['upstreamE1EFreezeSha256']==upstream['oldE1EFreezeSha256']
    for key,value in upstream.items():assert frozen[key]==value,key
    recorded=read(BASE/'evidence/audit.json');current=audit()
    assert recorded['status']==current['status']=='PASS' and recorded['noInFlightVerified'] is current['noInFlightVerified'] is True
    keys=('productionBinding','productionBindingVerified','comparisonEvidence','comparisonOuterExitEvidence','comparisonStatus','comparisonVerified','comparison',
          'actualFullReason','actualFullStatus','actualFullReportedAssertions','actualFullAssertions','driverSyntheticAssertions','targetedAssertions','totalAssertions',
          'diagnosticGInstances','metricSamples','runtimeAdmission','mockAssertionsIncluded','postFixOSComparisonRun','handleTypeCausality',
          'targetedRuns','actualFullRuns','compileInvocations','repairCompilations')
    for key in keys:assert frozen[key]==recorded[key]==current[key],key
    assert frozen['actualFullStatus']=='NOT_RUN' and frozen['actualFullAssertions']==0 and frozen['actualFullReportedAssertions'] is None
    assert frozen['syntheticAssertions']==frozen['driverSyntheticAssertions']==frozen['targetedAssertions']==frozen['totalAssertions']==0
    assert frozen['targetedRuns']==frozen['actualFullRuns']==frozen['compileInvocations']==frozen['repairCompilations']==0
    assert frozen['diagnosticLogBytesIncludingOuterExit']==current['comparison']['diagnosticLogBytesIncludingOuterExit']<=524288
    actual_sources={path.relative_to(ROOT).as_posix() for folder in SOURCE_FOLDERS for path in (BASE/folder).rglob('*') if path.is_file() and '__pycache__' not in path.parts}
    assert actual_sources=={row['path'] for row in source['files']}
    checks=[path for path in (BASE/'selfcheck').rglob('*') if path.is_file()]
    assert {path.relative_to(ROOT).as_posix() for path in checks}=={row['path'] for row in frozen['selfcheckFiles']}
    docs=[ROOT/'docs/coder'/('D1_E2D_'+name+'_V1.0.md') for name in ('DELIVERY','G_OS_COMPARISON','EXECUTION_APPENDIX')]
    sealed=[path for path in (BASE/'artifacts').rglob('*') if path.is_file()]+[path for path in (BASE/'evidence').glob('*') if path.is_file() and path.name!='freeze-summary.json']+docs
    assert {path.relative_to(ROOT).as_posix() for path in sealed}=={row['path'] for row in frozen['files']}
    fixture_bytes=sum(path.stat().st_size for path in checks if is_fixture(path))
    logs=sum(path.stat().st_size for path in checks if not is_fixture(path))+sum(path.stat().st_size for path in (BASE/'evidence').glob('*') if path.is_file() and path.name!='freeze-summary.json')
    assert fixture_bytes==frozen['syntheticFixtureBytes']<=2097152 and logs==frozen['logsAndEvidenceBytesBeforeSeal']
    assert logs+(BASE/'evidence/freeze-summary.json').stat().st_size==frozen['logsAndEvidenceBytesIncludingSeal']<=4194304
    print(json.dumps(dict(integrity='PASS',state=frozen['state'],sourceFiles=len(source['files']),frozenFiles=len(frozen['files']),selfcheckFiles=len(frozen['selfcheckFiles']),
                          comparisonStatus=frozen['comparisonStatus'],diagnosticGInstances=1,metricSamples=frozen['metricSamples'],postFixOSComparisonRun=True,
                          actualFullStatus='NOT_RUN',actualFullAssertions=0,targetedAssertions=0,compileInvocations=0,productionChanges=0,
                          oldE2CRecords=103,oldE2CSources=70,oldE2CTargetedAssertions=1125,oldE2BActualStatus='FAIL',oldE2BReportedAssertions=77,oldE2BPassedAssertions=0,oldE2BRecords=199,oldE2BSources=63,
                          oldE2ADriverAssertions=1003,oldE2ABridgeAssertions=87,oldE2ARecords=326,oldE2ASources=53,oldE2Records=231,oldE2Sources=43,oldE1ERecords=188,oldE1ESources=33,preservedBaselines=13,
                          freezeSha256=sha(BASE/'evidence/freeze-summary.json'),realMedia='NOT_RUN',runtimeAdmission=frozen['runtimeAdmission'])))
if __name__=='__main__':verify()
