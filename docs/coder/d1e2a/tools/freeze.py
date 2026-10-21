"""Explicit packaging only; no builds, media access or helper launches."""
import argparse, hashlib, json, zipfile
from pathlib import Path
from profile_audit import verify_configuration,verify_upstreams,is_fixture
BASE=Path(__file__).resolve().parents[1];ROOT=BASE.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def record(p):return dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=sha(p))
def freeze():
    assert not (BASE/'evidence/freeze-summary.json').exists(),'FROZEN_PACKAGE_IS_READ_ONLY'
    verify_configuration(json.loads((BASE/'manifest/branches.json').read_text(encoding='utf-8')))
    upstream=verify_upstreams()
    sources=sorted(p for folder in ('src','tools','manifest','profiles','upstream-e2','upstream-e1e') for p in (BASE/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts)
    source={'scope':'E2A_ADAPTER_SOURCE_AND_COMPLETE_UPSTREAM_RELATION','files':[record(p) for p in sources]}
    (BASE/'evidence/source-manifest.json').write_text(json.dumps(source,indent=2)+'\n',encoding='utf-8')
    with zipfile.ZipFile(BASE/'artifacts/E2A-source.zip','w',zipfile.ZIP_DEFLATED) as z:
        for p in sources:
            info=zipfile.ZipInfo(p.relative_to(ROOT).as_posix(),date_time=(2026,10,17,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,p.read_bytes())
    docs=[ROOT/'docs/coder'/('D1_E2A_'+name+'_V1.0.md') for name in ('DELIVERY','REAL_IO_ADMISSION','EXECUTION_APPENDIX')]
    files=sorted([p for p in (BASE/'artifacts').rglob('*') if p.is_file()]+[p for p in (BASE/'evidence').glob('*') if p.is_file()]+docs)
    checks=sorted(p for p in (BASE/'selfcheck').rglob('*') if p.is_file());fixtures=[p for p in checks if is_fixture(p)]
    fixturebytes=sum(p.stat().st_size for p in fixtures);logbytes=sum(p.stat().st_size for p in checks if p not in fixtures)+sum(p.stat().st_size for p in files if 'evidence' in p.parts)
    assert fixturebytes<=2097152 and logbytes<=4194304
    audit=json.loads((BASE/'evidence/audit.json').read_text(encoding='utf-8'));assert audit['status']=='PASS'
    assert audit['startupFixVerified'] and audit['startupLifecycleVerified'] and audit['oldE1EFrozenFilesVerified']==188 and audit['oldE1ESourceFilesVerified']==33 and audit['configurationVerified']
    assert audit['oldE2FrozenFilesVerified']==231 and audit['oldE2SourceFilesVerified']==43 and audit['preservedBaselines']==13
    assert audit['runtimeObservationVerified'] and audit['javaBridgeVerified'] and audit['javaBridgeAssertions']>0
    assert audit['actualRuntimeGateStopVerified'] and audit['runtimeAdmission']=='BLOCKED_R_HANDLES_519_GT_512'
    assert audit['totalAssertions']==audit['syntheticAssertions']+audit['targetedAssertions']
    result={'candidate':'D1-E2A-20261017','state':'ADAPTERS_FROZEN_PENDING_INDEPENDENT_REVIEW','runtime':'PowerShell 7.6.5 / .NET 10.0.11 / JBR 21.0.10 x64 + limited approved FFM flags',
            'files':[record(p) for p in files],'selfcheckFiles':[record(p) for p in checks],'syntheticFixtureBytes':fixturebytes,'logsAndEvidenceBytesBeforeSeal':logbytes,
            'upstreamFreezeSha256':sha(BASE/'upstream-e2/freeze-summary.json'),'upstreamE1EFreezeSha256':sha(BASE/'upstream-e1e/freeze-summary.json'),
            'syntheticAssertions':audit['totalAssertions'],'integrationAssertions':audit['syntheticAssertions'],'targetedAssertions':audit['targetedAssertions'],
            'integrationEvidence':audit['integrationEvidence'],'targetedEvidence':audit['targetedEvidence'],'javaBridgeEvidence':audit['javaBridgeEvidence'],
            'javaBridgeAssertions':audit['javaBridgeAssertions'],'javaBridgeProcesses':audit['javaBridgeProcesses'],'runtimeObservationVerified':True,
            'driverSyntheticAssertions':audit['totalAssertions'],'runtimeAdmission':'BLOCKED_R_HANDLES_519_GT_512',
            'actualRuntimeGateStopVerified':True,'actualRuntimeGateStopEvidence':audit['actualRuntimeGateStop']['evidence'],
            'oldE2FrozenFilesVerified':upstream['oldE2FrozenFilesVerified'],'oldE2SourceFilesVerified':upstream['oldE2SourceFilesVerified'],
            'oldE1EFrozenFilesVerified':upstream['oldE1EFrozenFilesVerified'],'oldE1ESourceFilesVerified':upstream['oldE1ESourceFilesVerified'],'preservedBaselines':13,
            'realExecutionEnabled':False,'realMedia':'NOT_RUN','realPF':'NOT_RUN','physicalVersionGuarantee':'REAL_MEDIA_UNPROVEN_SELF_OWNED_BRIDGE_CHECKED',
            'requiredDurability':'OS_DATA_SYNC_ACK_TOOL_PROBE_ONLY_NAMESPACE_UNPROVEN','hostJNI':'BLOCKED','D1':'NOT_PASSED','M0':'NOT_STARTED'}
    # The seal itself is evidence too. Check its real byte size before writing,
    # rather than leaving a final unchecked tail above the evidence hard limit.
    for _ in range(8):
        data=(json.dumps(result,indent=2)+'\n').encode('utf-8');total=logbytes+len(data)
        if result.get('logsAndEvidenceBytesIncludingSeal')==total:break
        result['logsAndEvidenceBytesIncludingSeal']=total
    else:raise AssertionError('SEAL_SIZE_ACCOUNTING_DID_NOT_CONVERGE')
    assert total<=4194304
    path=BASE/'evidence/freeze-summary.json';path.write_bytes(data)
    print(json.dumps({'state':result['state'],'freezeSha256':sha(path),'sourceZip':record(BASE/'artifacts/E2A-source.zip'),'syntheticFixtureBytes':fixturebytes,'logsAndEvidenceBytesIncludingSeal':total,'javaBridgeAssertions':result['javaBridgeAssertions']}))
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--freeze',action='store_true');args=parser.parse_args()
    if args.freeze:freeze()
    else:print('INSPECT_ONLY: explicit --freeze required')
