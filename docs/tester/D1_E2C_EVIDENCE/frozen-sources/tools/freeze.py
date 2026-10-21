"""Explicit E2C packaging; no builds, diagnostics, helpers, or media access."""
import argparse,hashlib,json,zipfile
from pathlib import Path
from profile_audit import verify_configuration,verify_upstreams,is_fixture,SOURCE_FOLDERS
BASE=Path(__file__).resolve().parents[1];ROOT=BASE.parents[2]
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def record(path):return dict(path=path.relative_to(ROOT).as_posix(),bytes=path.stat().st_size,sha256=sha(path))

def freeze():
    assert not (BASE/'evidence/freeze-summary.json').exists(),'FROZEN_PACKAGE_IS_READ_ONLY'
    verify_configuration(json.loads((BASE/'manifest/branches.json').read_text(encoding='utf-8')));upstream=verify_upstreams()
    audit=json.loads((BASE/'evidence/audit.json').read_text(encoding='utf-8'))
    assert audit['status']=='PASS' and audit['scope']=='E2C_READ_ONLY_EVIDENCE_AUDIT' and audit['configurationVerified']
    assert audit['aliasFixVerified'] and audit['lifecycleFixVerified'] and audit['diagnosticVerified'] and audit['noInFlightVerified'] and audit['realExecutionEnabled'] is False
    assert audit['actualFullStatus']=='NOT_RUN' and audit['actualFullAssertions']==0 and audit['actualFullReportedAssertions'] is None
    assert audit['totalAssertions']==audit['driverSyntheticAssertions']==audit['targetedAssertions']
    for label,records,sources in (('E2B',199,63),('E2A',326,53),('E2',231,43),('E1E',188,33)):
        assert audit['old'+label+'FrozenFilesVerified']==upstream['old'+label+'FrozenFilesVerified']==records
        assert audit['old'+label+'SourceFilesVerified']==upstream['old'+label+'SourceFilesVerified']==sources
    assert audit['preservedBaselines']==13 and audit['oldE2ADriverSyntheticAssertions']==1003 and audit['oldE2AJavaBridgeAssertions']==87
    sources=sorted(path for folder in SOURCE_FOLDERS for path in (BASE/folder).rglob('*') if path.is_file() and '__pycache__' not in path.parts)
    source=dict(scope='E2C_ADAPTER_SOURCE_AND_COMPLETE_UPSTREAM_RELATION',files=[record(path) for path in sources])
    (BASE/'evidence/source-manifest.json').write_text(json.dumps(source,indent=2)+'\n',encoding='utf-8')
    with zipfile.ZipFile(BASE/'artifacts/E2C-source.zip','w',zipfile.ZIP_DEFLATED) as zipped:
        for path in sources:
            info=zipfile.ZipInfo(path.relative_to(ROOT).as_posix(),date_time=(2026,10,17,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;zipped.writestr(info,path.read_bytes())
    docs=[ROOT/'docs/coder'/('D1_E2C_'+name+'_V1.0.md') for name in ('DELIVERY','RESOURCE_LIFECYCLE','EXECUTION_APPENDIX')]
    files=sorted([path for path in (BASE/'artifacts').rglob('*') if path.is_file()]+[path for path in (BASE/'evidence').glob('*') if path.is_file()]+docs)
    checks=sorted(path for path in (BASE/'selfcheck').rglob('*') if path.is_file())
    fixture_bytes=sum(path.stat().st_size for path in checks if is_fixture(path))
    log_bytes=sum(path.stat().st_size for path in checks if not is_fixture(path))+sum(path.stat().st_size for path in files if 'evidence' in path.parts)
    assert fixture_bytes<=2097152 and log_bytes<=4194304 and audit['lifecycle']['diagnosticLogBytesIncludingOuterExit']<=524288
    result=dict(candidate='D1-E2C-20261017',state='E2C_FROZEN_PENDING_INDEPENDENT_REVIEW',
                runtime=audit['lifecycle']['runtime'],
                files=[record(path) for path in files],selfcheckFiles=[record(path) for path in checks],syntheticFixtureBytes=fixture_bytes,logsAndEvidenceBytesBeforeSeal=log_bytes,
                upstreamFreezeSha256=upstream['oldE2BFreezeSha256'],upstreamE2AFreezeSha256=upstream['oldE2AFreezeSha256'],upstreamE2FreezeSha256=upstream['oldE2FreezeSha256'],upstreamE1EFreezeSha256=upstream['oldE1EFreezeSha256'],
                targetedEvidence=audit['targetedEvidence'],targetedAssertions=audit['targetedAssertions'],actualFullReason=audit['actualFullReason'],
                actualFullStatus=audit['actualFullStatus'],actualFullReportedAssertions=audit['actualFullReportedAssertions'],actualFullAssertions=audit['actualFullAssertions'],
                driverSyntheticAssertions=audit['totalAssertions'],syntheticAssertions=audit['totalAssertions'],
                diagnosticEvidence=audit['diagnosticEvidence'],diagnosticOuterExitEvidence=audit['diagnosticOuterExitEvidence'],diagnosticGInstances=1,metricSamples=6,
                lifecycle=audit['lifecycle'],staticEvidence=audit['staticEvidence'],entryDenialsEvidence=audit['entryDenialsEvidence'],
                diagnosticLogBytesIncludingOuterExit=audit['lifecycle']['diagnosticLogBytesIncludingOuterExit'],runtimeAdmission=audit['runtimeAdmission'],
                aliasFixVerified=True,lifecycleFixVerified=True,diagnosticVerified=True,noInFlightVerified=True,mockAssertionsIncluded=False,postFixOSComparisonRun=False,handleTypeCausality='UNKNOWN',
                realExecutionEnabled=False,realMedia='NOT_RUN',realPF='NOT_RUN',physicalVersionGuarantee='REAL_MEDIA_UNPROVEN_SELF_OWNED_ONLY',
                requiredDurability='OS_DATA_SYNC_ACK_TOOL_PROBE_ONLY_NAMESPACE_UNPROVEN',hostJNI='BLOCKED',D1='NOT_PASSED',M0='NOT_STARTED',**upstream)
    # Preserve all evidence, including FAIL/NOT_RUN. Account for the seal's own
    # bytes; a missing proof or an over-budget package cannot be called frozen.
    for _ in range(8):
        data=(json.dumps(result,indent=2)+'\n').encode('utf-8');total=log_bytes+len(data)
        if result.get('logsAndEvidenceBytesIncludingSeal')==total:break
        result['logsAndEvidenceBytesIncludingSeal']=total
    else:raise AssertionError('SEAL_SIZE_ACCOUNTING_DID_NOT_CONVERGE')
    assert total<=4194304
    path=BASE/'evidence/freeze-summary.json';path.write_bytes(data)
    print(json.dumps(dict(state=result['state'],freezeSha256=sha(path),sourceZip=record(BASE/'artifacts/E2C-source.zip'),
                          actualFullStatus=result['actualFullStatus'],actualFullAssertions=result['actualFullAssertions'],targetedAssertions=result['targetedAssertions'],
                          syntheticFixtureBytes=fixture_bytes,logsAndEvidenceBytesIncludingSeal=total)))
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--freeze',action='store_true');args=parser.parse_args()
    if args.freeze:freeze()
    else:print('INSPECT_ONLY: explicit --freeze required')
