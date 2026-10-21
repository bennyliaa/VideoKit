"""Read-only immutable preparation verification and existing-result reconciliation."""
import argparse,hashlib,json,zipfile
from pathlib import Path
from profile_audit import verify_configuration,verify_upstreams,verify_batch,SOURCE_FOLDERS,UNIQUE_ROOT
from audit import audit,present

BASE=Path(__file__).resolve().parents[1];ROOT=BASE.parents[2];SEAL=BASE/'evidence/e2e-freeze.json'
def read(path):return json.loads(path.read_text(encoding='utf-8-sig'))
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def document_paths():return [ROOT/'docs/coder'/('D1_E2E_'+name+'_V1.0.md') for name in ('DELIVERY','EXECUTION_PLAN','EXECUTION_APPENDIX')]
def source_paths():return sorted(path for folder in SOURCE_FOLDERS for path in (BASE/folder).rglob('*') if path.is_file() and '__pycache__' not in path.parts)

def output_files():
    """Walk only this batch's existing output trees, rejecting reparse entries."""
    roots=[]
    for name in ('execution','selfcheck'):
        path=BASE/name
        if not present(path):continue
        assert not path.is_symlink() and not path.is_junction() and path.is_dir(),'OUTPUT_ROOT_MUST_BE_OWNED_DIRECTORY'
        assert path.resolve()==path.absolute(),'OUTPUT_ROOT_REDIRECTED'
        if name=='selfcheck':
            children=list(path.iterdir());assert {child.name for child in children}<={UNIQUE_ROOT},'OUTPUT_FROM_UNAUTHORIZED_BATCH'
            path=path/UNIQUE_ROOT
            if not present(path):continue
        roots.append(path)
    result=[];pending=list(roots)
    while pending:
        directory=pending.pop()
        assert not directory.is_symlink() and not directory.is_junction() and directory.resolve()==directory.absolute(),'OUTPUT_DIRECTORY_REPARSE_DENIED'
        for path in directory.iterdir():
            assert not path.is_symlink() and not path.is_junction() and path.resolve()==path.absolute(),'OUTPUT_FILE_REPARSE_DENIED'
            if path.is_dir():pending.append(path)
            else:assert path.is_file(),'OUTPUT_MUST_BE_REGULAR_FILE';result.append(path)
            assert len(result)+len(pending)<=512,'RESULT_FILE_COUNT_LIMIT'
    return sorted(result)

def output_kind(path):
    return 'FIXTURE' if path.name in ('L.bin','C.bin','Z.bin') or path.suffix=='.out' else 'METADATA'

def existing_execution(frozen,batch):
    directories={name:present(BASE/name) for name in ('execution','selfcheck')}
    late_path=BASE/'execution/late-result-manifest.json'
    path=late_path if present(late_path) else BASE/'execution/result-manifest.json'
    manifest_name=path.relative_to(BASE).as_posix()
    if not present(path):
        return dict(state='NO_EXECUTION_OUTPUTS_PRESENT' if not any(directories.values()) else 'OUTPUTS_PRESENT_NO_RESULT_MANIFEST',directories=directories,
                    resultManifestIntegrity='NOT_AVAILABLE',reportedNoInFlight=None,finalAggregateUsageVerified=False,
                    outputUsage=dict(metadataBytes=None,fixtureBytes=None),executionStartedByVerify=False,automaticCollectionPerformed=False)
    assert not path.is_symlink() and not path.is_junction() and path.resolve()==path.absolute() and path.stat().st_size<=49152,'RESULT_MANIFEST_PATH_OR_SIZE'
    result=read(path)
    assert result['schema']==1 and result['scope']=='E2E_EXECUTION_RESULT_MANIFEST' and result['batchId']==batch['batchId']
    assert result['expectedFreeze']==sha(SEAL) and result['prepUsage']==frozen['prepUsage']
    assert result['caps']['metadataBytes']==4194304 and result['caps']['fixtureBytes']==2097152
    assert type(result['complete']) is bool and type(result['resultHashComplete']) is bool
    assert result['manifestBytes']==path.stat().st_size and result['noInFlight'] in (None,True,False)
    initial_pending_preserved=False
    if path==late_path:
        original_path=BASE/'execution/result-manifest.json'
        assert original_path.resolve()==original_path.absolute() and not original_path.is_symlink() and not original_path.is_junction() and original_path.stat().st_size<=49152
        original=read(original_path)
        assert original['schema']==1 and original['scope']=='E2E_EXECUTION_RESULT_MANIFEST' and original['batchId']==batch['batchId']
        assert original['expectedFreeze']==result['expectedFreeze'] and original['prepUsage']==frozen['prepUsage'] and original['caps']==result['caps']
        assert original['status']=='PENDING' and original['complete'] is original['resultHashComplete'] is False
        assert original['files']==[] and original['outputUsage']==dict(metadataBytes=None,fixtureBytes=None) and original['combinedUsage']=={}
        assert type(original['originalChildExitObserved']) is bool and original['noInFlight'] in (None,False) and original['manifestBytes']==original_path.stat().st_size
        initial_pending_preserved=True
    if not result['complete'] or not result['resultHashComplete']:
        assert result['files']==[] and result['outputUsage']==dict(metadataBytes=None,fixtureBytes=None) and result['combinedUsage']=={}
        return dict(state='PENDING_OUTPUT_INVENTORY_NOT_FINAL',directories=directories,resultManifestIntegrity='STRUCTURE_ONLY_INCOMPLETE',
                    resultManifest=manifest_name,reportedStatus=result['status'],reportedNoInFlight=result['noInFlight'],
                    reportedOriginalChildExitObserved=result['originalChildExitObserved'],finalAggregateUsageVerified=False,
                    outputUsage=dict(metadataBytes=None,fixtureBytes=None),executionStartedByVerify=False,automaticCollectionPerformed=False)
    files=output_files();actual={file.relative_to(BASE).as_posix():file for file in files};entries=result['files']
    expected=set(actual)-{manifest_name}
    assert len(entries)==len(expected) and {row['path'] for row in entries}==expected,'RESULT_INVENTORY_MUST_INCLUDE_ALL_EXISTING_BATCH_OUTPUTS'
    usage=dict(metadataBytes=0,fixtureBytes=0)
    for name,file in actual.items():usage['fixtureBytes' if output_kind(file)=='FIXTURE' else 'metadataBytes']+=file.stat().st_size
    wrapper_metadata=sum(file.stat().st_size for file in files if file.is_relative_to(BASE/'execution'))
    production_metadata=usage['metadataBytes']-wrapper_metadata
    assert wrapper_metadata<=196608 and production_metadata<=3178496 and result['wrapperMetadataBytes']==wrapper_metadata,'EXECUTION_METADATA_SUBLEDGER_MISMATCH'
    assert usage['metadataBytes']<=3375104 and usage['fixtureBytes']<=790528,'EXECUTION_EXCEEDS_RESERVED_PRODUCTION_AND_WRAPPER_ALLOWANCE'
    combined={key:frozen['prepUsage'][key]+usage[key] for key in usage}
    assert combined['metadataBytes']<=4194304 and combined['fixtureBytes']<=2097152
    for row in entries:
        file=actual[row['path']];assert row['kind']==output_kind(file) and file.stat().st_size==row['bytes'] and sha(file)==row['sha256'],row['path']
    assert result['outputUsage']==usage and result['combinedUsage']==combined,'RESULT_USAGE_MUST_COUNT_MANIFEST_ITSELF'
    return dict(state='EXISTING_RESULT_MANIFEST_RECONCILED',directories=directories,resultManifestIntegrity='PASS',resultManifest=manifest_name,
                reportedStatus=result['status'],reportedNoInFlight=result['noInFlight'],reportedOriginalChildExitObserved=result['originalChildExitObserved'],
                outputFiles=len(files),outputUsage=usage,wrapperMetadataBytes=wrapper_metadata,productionMetadataBytes=production_metadata,combinedUsage=combined,finalAggregateUsageVerified=True,initialPendingPreserved=initial_pending_preserved,
                executionStartedByVerify=False,automaticCollectionPerformed=False,meaning='Existing result receipt; immutable-package PASS is not an execution or resource-admission PASS')

def verify(expected_freeze=None):
    seal_hash=sha(SEAL)
    if expected_freeze is not None:assert type(expected_freeze) is str and len(expected_freeze)==64 and expected_freeze==seal_hash,'EXPECTED_FREEZE_MISMATCH'
    frozen=read(SEAL);source=read(BASE/'evidence/source-manifest.json')
    assert frozen['schema']==1 and frozen['state']=='PREPARED_NOT_RUN_PENDING_TESTER'
    assert frozen['preparedNotRun']['atSeal'] is True and frozen['preparedNotRun']['reservationConsumed'] is False
    assert frozen['immutableExcludedDirectories']==['execution','selfcheck'] and frozen['selfHashExcluded'] is frozen['expectedFreezeProvidedExternally'] is True
    assert source['scope']=='E2E_PREPARATION_SOURCE_AND_COMPLETE_UPSTREAM_RELATION'
    assert frozen['files']==frozen['immutableFiles'] and frozen['selfcheckFiles']==[]
    entries=frozen['immutableFiles'];assert len({row['path'] for row in entries})==len(entries)
    for row in entries:
        path=ROOT/row['path'];assert path.resolve().is_relative_to((ROOT/'docs').resolve()) and path.stat().st_size==row['bytes'] and sha(path)==row['sha256'],row['path']
        assert path!=SEAL and not path.is_relative_to(BASE/'execution') and not path.is_relative_to(BASE/'selfcheck'),'OUTPUTS_MUST_NOT_ENTER_IMMUTABLE_PREPARATION'
    sources=source_paths();assert {path.relative_to(ROOT).as_posix() for path in sources}=={row['path'] for row in source['files']}
    for row in source['files']:
        path=ROOT/row['path'];assert path.stat().st_size==row['bytes'] and sha(path)==row['sha256'],row['path']
    with zipfile.ZipFile(BASE/'artifacts/E2E-source.zip') as zipped:
        assert len(zipped.namelist())==len(source['files']) and set(zipped.namelist())=={row['path'] for row in source['files']}
        for row in source['files']:
            data=zipped.read(row['path']);assert len(data)==row['bytes'] and hashlib.sha256(data).hexdigest()==row['sha256'],row['path']
    configuration=verify_configuration(read(BASE/'manifest/branches.json'));upstream=verify_upstreams();batch=verify_batch()
    assert frozen['batchId']==batch['batchId'] and frozen['batchManifestSha256']==batch['batchManifestSha256'] and frozen['productionBindings']==batch['productionBindings']
    assert frozen['externalRuntimeCompleteRehashPerformed'] is frozen['externalRuntimeDllRehashedDuringPreparation'] is False
    assert frozen['runtimeLibraryStaticBinding']==batch['runtimeLibraryStaticBinding']
    assert frozen['productionBinding']==configuration['productionBinding'] and frozen['productionBindingVerified'] is frozen['configurationVerified'] is True
    for key,value in upstream.items():assert frozen[key]==value,key
    recorded=read(BASE/'evidence/audit.json');current=audit(require_unconsumed=False)
    for key in ('batch','productionBinding','batchManifestSha256','productionBindings','preparationChecks','preparationAssertions','preparedNotRun','runtimeAdmission'):
        assert recorded[key]==current[key],key
    assert recorded['status']==current['status']=='PASS' and recorded['currentOutputDirectories']==dict(execution=False,selfcheck=False) and recorded['unconsumedRequiredForThisAudit'] is True
    assert frozen['preparationChecks']==current['preparationChecks'] and frozen['preparationAssertions']==current['preparationAssertions']
    assert frozen['preparedNotRun']==current['preparedNotRun'] and frozen['runtimeAdmission']==current['runtimeAdmission']
    for key in ('targetedAssertions','driverSyntheticAssertions','actualFullAssertions','compileInvocations','repairCompilations','currentOSObservationsAtSeal'):assert frozen[key]==recorded[key]==current[key]==0
    evidence=[path for path in (BASE/'evidence').rglob('*') if path.is_file() and path!=SEAL]
    artifacts=[path for path in (BASE/'artifacts').rglob('*') if path.is_file()]
    expected={path.relative_to(ROOT).as_posix() for path in set(sources+evidence+artifacts+document_paths())}
    assert expected=={row['path'] for row in entries},'IMMUTABLE_FILE_SET_CHANGED'
    metadata=sum(path.stat().st_size for path in evidence)
    assert frozen['prepEvidenceBytesBeforeSeal']==metadata and frozen['sealBytes']==SEAL.stat().st_size
    assert frozen['prepUsage']==dict(metadataBytes=metadata+SEAL.stat().st_size,fixtureBytes=0)
    assert frozen['prepUsage']['metadataBytes']<=819200 and frozen['prepUsage']['metadataBytes']+196608+3178496<=4194304
    execution=existing_execution(frozen,batch)
    result=dict(integrity='PASS',state=frozen['state'],stateMeaning='IMMUTABLE_PREPARATION_STATE_AT_SEAL_ONLY',batchId=batch['batchId'],
                expectedFreezeSupplied=expected_freeze is not None,freezeSha256=seal_hash,sourceFiles=len(source['files']),immutableFiles=len(entries),
                productionSourceFiles=32,originalConfigurationFiles=5,compiledArtifacts=10,productionChanges=0,compileInvocationsAtSeal=0,
                preparationAssertions=frozen['preparationAssertions'],targetedAssertionsAtSeal=0,actualFullAssertionsAtSeal=0,currentOSObservationsAtSeal=0,
                prepUsage=frozen['prepUsage'],preparedNotRun=frozen['preparedNotRun'],execution=execution,externalRuntimeCompleteRehashPerformed=False,
                externalRuntimeDllRehashedDuringPreparation=False,runtimeLibraryStaticBinding=batch['runtimeLibraryStaticBinding'],
                oldE2DRecords=32,oldE2DSources=63,oldE2DMetricSamples=6,oldE2CRecords=103,oldE2CSources=70,oldE2CTargetedAssertions=1125,
                oldE2BRecords=199,oldE2BSources=63,oldE2BActualStatus='FAIL',oldE2BReportedAssertions=77,oldE2BPassedAssertions=0,
                oldE2ARecords=326,oldE2ASources=53,oldE2ADriverAssertions=1003,oldE2ABridgeAssertions=87,oldE2Records=231,oldE2Sources=43,oldE1ERecords=188,oldE1ESources=33,preservedBaselines=13,
                executionStartedByVerify=False,reservationConsumedByVerify=False,realMedia='NOT_RUN',D1='NOT_PASSED',M0='NOT_STARTED')
    print(json.dumps(result));return result
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--expected-freeze');args=parser.parse_args();verify(args.expected_freeze)
