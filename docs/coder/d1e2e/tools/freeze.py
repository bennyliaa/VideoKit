"""Seal preparation files only; never create execution/selfcheck or start a child."""
import argparse,hashlib,json,zipfile
from pathlib import Path
from profile_audit import verify_configuration,verify_upstreams,verify_batch,SOURCE_FOLDERS
from audit import present

BASE=Path(__file__).resolve().parents[1];ROOT=BASE.parents[2]
SEAL=BASE/'evidence/e2e-freeze.json'
def read(path):return json.loads(path.read_text(encoding='utf-8-sig'))
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def record(path):return dict(path=path.relative_to(ROOT).as_posix(),bytes=path.stat().st_size,sha256=sha(path))
def source_paths():return sorted(path for folder in SOURCE_FOLDERS for path in (BASE/folder).rglob('*') if path.is_file() and '__pycache__' not in path.parts)
def document_paths():return [ROOT/'docs/coder'/('D1_E2E_'+name+'_V1.0.md') for name in ('DELIVERY','EXECUTION_PLAN','EXECUTION_APPENDIX')]

def freeze():
    assert not present(SEAL),'FROZEN_PREPARATION_IS_IMMUTABLE'
    assert not present(BASE/'execution') and not present(BASE/'selfcheck'),'PREPARATION_MUST_REMAIN_UNCONSUMED'
    assert not present(BASE/'evidence/freeze-summary.json'),'UNCHANGED_R_HELPER_REQUIRES_NEW_PREPARATION_SEAL_NAME'
    configuration=verify_configuration(read(BASE/'manifest/branches.json'));upstream=verify_upstreams();batch=verify_batch()
    audit=read(BASE/'evidence/audit.json')
    assert audit['status']=='PASS' and audit['scope']=='E2E_READ_ONLY_PREPARATION_EVIDENCE_AUDIT'
    assert audit['configurationVerified'] is audit['productionBindingVerified'] is True and audit['historicalAssertionsIncluded'] is False
    assert audit['productionBinding']==configuration['productionBinding'] and audit['batch']==batch
    assert audit['batchManifestSha256']==batch['batchManifestSha256'] and audit['productionBindings']==batch['productionBindings']
    assert audit['unconsumedRequiredForThisAudit'] is True and audit['currentOutputDirectories']==dict(execution=False,selfcheck=False)
    assert audit['preparedNotRun']['atSeal'] is True and audit['preparedNotRun']['reservationConsumed'] is False
    assert audit['targetedAssertions']==audit['driverSyntheticAssertions']==audit['compileInvocations']==audit['repairCompilations']==audit['actualFullAssertions']==audit['currentOSObservationsAtSeal']==0
    assert audit['preparationAssertions']==audit['preparationChecks']['assertions']>0
    for key,value in upstream.items():assert audit[key]==value,key
    sources=source_paths();source=dict(scope='E2E_PREPARATION_SOURCE_AND_COMPLETE_UPSTREAM_RELATION',files=[record(path) for path in sources])
    (BASE/'evidence/source-manifest.json').write_text(json.dumps(source,indent=2)+'\n',encoding='utf-8')
    with zipfile.ZipFile(BASE/'artifacts/E2E-source.zip','w',zipfile.ZIP_DEFLATED) as zipped:
        for path in sources:
            info=zipfile.ZipInfo(path.relative_to(ROOT).as_posix(),date_time=(2026,10,17,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;zipped.writestr(info,path.read_bytes())
    evidence=[path for path in (BASE/'evidence').rglob('*') if path.is_file() and path!=SEAL]
    artifacts=[path for path in (BASE/'artifacts').rglob('*') if path.is_file()]
    immutable=sorted(set(sources+evidence+artifacts+document_paths()))
    records=[record(path) for path in immutable]
    metadata=sum(path.stat().st_size for path in evidence)
    assert not present(BASE/'execution') and not present(BASE/'selfcheck'),'PREPARATION_WAS_CONSUMED_DURING_SEAL'
    result=dict(schema=1,candidate='D1-E2E-20261017',state='PREPARED_NOT_RUN_PENDING_TESTER',batchId=batch['batchId'],
                immutableFiles=records,files=records,selfcheckFiles=[],
                immutableScope='SOURCE_TOOLS_CONFIG_UPSTREAMS_COMPILED_ARTIFACTS_PREPARATION_EVIDENCE_AND_THREE_DOCUMENTS',
                immutableExcludedDirectories=['execution','selfcheck'],selfHashExcluded=True,expectedFreezeProvidedExternally=True,
                sourceManifest='evidence/source-manifest.json',sourceZip=record(BASE/'artifacts/E2E-source.zip'),
                batchManifestSha256=batch['batchManifestSha256'],productionBindings=batch['productionBindings'],productionBinding=configuration['productionBinding'],
                productionBindingVerified=True,configurationVerified=True,preparedNotRun=audit['preparedNotRun'],
                prepUsage=dict(metadataBytes=0,fixtureBytes=0),prepUsageScope='ALL_PREPARATION_EVIDENCE_FILES_INCLUDING_THIS_SEAL; SOURCE_AND_ARTIFACT_ARCHIVES_ACCOUNTED_SEPARATELY',
                prepEvidenceBytesBeforeSeal=metadata,sealBytes=0,maximumPreparationMetadataBytes=batch['maximumPreparationMetadataBytes'],
                maximumPreparationFixtureBytes=batch['maximumPreparationFixtureBytes'],executionReservations=dict(wrapperMetadataBytes=196608,productionMetadataPeakBytes=3178496,productionFixtureBytes=790528),
                combinedCaps=dict(metadataBytes=4194304,fixtureBytes=2097152),preparationAssertions=audit['preparationAssertions'],preparationChecks=audit['preparationChecks'],
                targetedAssertions=0,driverSyntheticAssertions=0,actualFullAssertions=0,compileInvocations=0,repairCompilations=0,currentOSObservationsAtSeal=0,
                historicalAssertionsIncluded=False,runtimeIdentity=batch['runtimeIdentity'],externalRuntimeCompleteRehashPerformed=False,
                externalRuntimeDllRehashedDuringPreparation=False,runtimeLibraryStaticBinding=batch['runtimeLibraryStaticBinding'],
                runtimeAdmission=audit['runtimeAdmission'],realExecutionEnabled=False,realMedia='NOT_RUN',realPF='NOT_RUN',
                hostJNI='BLOCKED',D1='NOT_PASSED',M0='NOT_STARTED',**upstream)
    for _ in range(12):
        data=(json.dumps(result,indent=2)+'\n').encode('utf-8');total=metadata+len(data)
        if result['prepUsage']['metadataBytes']==total and result['sealBytes']==len(data):break
        result['prepUsage']['metadataBytes']=total;result['sealBytes']=len(data)
    else:raise AssertionError('PREPARATION_SEAL_SIZE_ACCOUNTING_DID_NOT_CONVERGE')
    assert total<=batch['maximumPreparationMetadataBytes'] and total+196608+3178496<=4194304
    assert result['prepUsage']['fixtureBytes']+790528<=2097152
    with SEAL.open('xb') as stream:assert stream.write(data)==len(data),'PREPARATION_SEAL_WRITE_UNKNOWN'
    print(json.dumps(dict(state=result['state'],seal='evidence/e2e-freeze.json',expectedFreezeSha256=sha(SEAL),sourceZip=result['sourceZip'],
                          immutableFiles=len(records),prepUsage=result['prepUsage'],preparationAssertions=result['preparationAssertions'],
                          reservationConsumedAtSeal=False,executionStartedByFreeze=False)))
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--freeze',action='store_true');args=parser.parse_args()
    if args.freeze:freeze()
    else:print('INSPECT_ONLY: explicit --freeze required; never starts or reserves a batch')
