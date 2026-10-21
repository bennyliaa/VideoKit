"""Explicit E2D packaging; no compilation, process observation, or probe execution."""
import argparse,hashlib,json,zipfile
from pathlib import Path
from profile_audit import verify_configuration,verify_upstreams,is_fixture,SOURCE_FOLDERS

BASE=Path(__file__).resolve().parents[1];ROOT=BASE.parents[2]
def read(path):return json.loads(path.read_text(encoding='utf-8-sig'))
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def record(path):return dict(path=path.relative_to(ROOT).as_posix(),bytes=path.stat().st_size,sha256=sha(path))

def freeze():
    assert not (BASE/'evidence/freeze-summary.json').exists(),'FROZEN_PACKAGE_IS_READ_ONLY'
    configuration=verify_configuration(read(BASE/'manifest/branches.json'));upstream=verify_upstreams()
    audit=read(BASE/'evidence/audit.json')
    assert audit['status']=='PASS' and audit['scope']=='E2D_READ_ONLY_COMPARISON_EVIDENCE_AUDIT'
    assert audit['configurationVerified'] is audit['productionBindingVerified'] is audit['comparisonVerified'] is audit['noInFlightVerified'] is True
    assert audit['realExecutionEnabled'] is False and audit['postFixOSComparisonRun'] is True
    assert audit['actualFullStatus']=='NOT_RUN' and audit['actualFullAssertions']==0 and audit['actualFullReportedAssertions'] is None
    assert audit['totalAssertions']==audit['driverSyntheticAssertions']==audit['targetedAssertions']==0
    assert audit['compileInvocations']==audit['repairCompilations']==audit['targetedRuns']==audit['actualFullRuns']==0
    assert audit['productionBinding']==configuration['productionBinding']
    for key,value in upstream.items():assert audit[key]==value,key
    sources=sorted(path for folder in SOURCE_FOLDERS for path in (BASE/folder).rglob('*') if path.is_file() and '__pycache__' not in path.parts)
    source=dict(scope='E2D_UNCHANGED_E2C_PRODUCTION_COMPARISON_TOOLS_AND_COMPLETE_UPSTREAM_RELATION',files=[record(path) for path in sources])
    (BASE/'evidence/source-manifest.json').write_text(json.dumps(source,indent=2)+'\n',encoding='utf-8')
    with zipfile.ZipFile(BASE/'artifacts/E2D-source.zip','w',zipfile.ZIP_DEFLATED) as zipped:
        for path in sources:
            info=zipfile.ZipInfo(path.relative_to(ROOT).as_posix(),date_time=(2026,10,17,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;zipped.writestr(info,path.read_bytes())
    docs=[ROOT/'docs/coder'/('D1_E2D_'+name+'_V1.0.md') for name in ('DELIVERY','G_OS_COMPARISON','EXECUTION_APPENDIX')]
    files=sorted([path for path in (BASE/'artifacts').rglob('*') if path.is_file()]+[path for path in (BASE/'evidence').glob('*') if path.is_file()]+docs)
    checks=sorted(path for path in (BASE/'selfcheck').rglob('*') if path.is_file())
    fixture_bytes=sum(path.stat().st_size for path in checks if is_fixture(path))
    log_bytes=sum(path.stat().st_size for path in checks if not is_fixture(path))+sum(path.stat().st_size for path in files if 'evidence' in path.parts)
    assert fixture_bytes<=2097152 and log_bytes<=4194304 and audit['comparison']['diagnosticLogBytesIncludingOuterExit']<=524288
    result=dict(candidate='D1-E2D-20261017',state='E2D_FROZEN_PENDING_INDEPENDENT_REVIEW',
                files=[record(path) for path in files],selfcheckFiles=[record(path) for path in checks],syntheticFixtureBytes=fixture_bytes,logsAndEvidenceBytesBeforeSeal=log_bytes,
                runtime=audit['comparison']['runtime'],productionBinding=audit['productionBinding'],productionBindingVerified=True,configurationVerified=True,
                upstreamFreezeSha256=upstream['oldE2CFreezeSha256'],upstreamE2BFreezeSha256=upstream['oldE2BFreezeSha256'],upstreamE2AFreezeSha256=upstream['oldE2AFreezeSha256'],
                upstreamE2FreezeSha256=upstream['oldE2FreezeSha256'],upstreamE1EFreezeSha256=upstream['oldE1EFreezeSha256'],
                comparisonEvidence=audit['comparisonEvidence'],comparisonOuterExitEvidence=audit['comparisonOuterExitEvidence'],comparison=audit['comparison'],comparisonStatus=audit['comparisonStatus'],
                comparisonVerified=True,diagnosticGInstances=1,metricSamples=audit['metricSamples'],postFixOSComparisonRun=True,
                diagnosticLogBytesIncludingOuterExit=audit['comparison']['diagnosticLogBytesIncludingOuterExit'],runtimeAdmission=audit['runtimeAdmission'],
                actualFullReason=audit['actualFullReason'],actualFullStatus='NOT_RUN',actualFullReportedAssertions=None,actualFullAssertions=0,
                targetedAssertions=0,driverSyntheticAssertions=0,syntheticAssertions=0,totalAssertions=0,targetedRuns=0,actualFullRuns=0,compileInvocations=0,repairCompilations=0,
                currentAssertionMeaning='NO_NEW_TARGETED_OR_FULL_ASSERTIONS; OBSERVATIONS_AND_READ_ONLY_INTEGRITY_CHECKS_REPORTED_SEPARATELY',
                noInFlightVerified=True,mockAssertionsIncluded=False,handleTypeCausality='UNKNOWN',realExecutionEnabled=False,realMedia='NOT_RUN',realPF='NOT_RUN',
                physicalVersionGuarantee='REAL_MEDIA_UNPROVEN_NO_MEDIA_OR_FILE_IO_IN_THIS_PROBE',requiredDurability='NOT_RUN_DURABILITY_UNPROVEN',
                hostJNI='BLOCKED',D1='NOT_PASSED',M0='NOT_STARTED',**upstream)
    # Seal bytes are part of the batch evidence budget; preserve every failure
    # and unknown record instead of deleting or compressing it to meet a cap.
    for _ in range(8):
        data=(json.dumps(result,indent=2)+'\n').encode('utf-8');total=log_bytes+len(data)
        if result.get('logsAndEvidenceBytesIncludingSeal')==total:break
        result['logsAndEvidenceBytesIncludingSeal']=total
    else:raise AssertionError('SEAL_SIZE_ACCOUNTING_DID_NOT_CONVERGE')
    assert total<=4194304
    path=BASE/'evidence/freeze-summary.json';path.write_bytes(data)
    print(json.dumps(dict(state=result['state'],freezeSha256=sha(path),sourceZip=record(BASE/'artifacts/E2D-source.zip'),comparisonStatus=result['comparisonStatus'],
                          metricSamples=result['metricSamples'],actualFullStatus='NOT_RUN',actualFullAssertions=0,targetedAssertions=0,compileInvocations=0,
                          syntheticFixtureBytes=fixture_bytes,logsAndEvidenceBytesIncludingSeal=total)))
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--freeze',action='store_true');args=parser.parse_args()
    if args.freeze:freeze()
    else:print('INSPECT_ONLY: explicit --freeze required; does not run compare-g')
