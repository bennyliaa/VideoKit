"""Explicit preparation sealing only; never grants or starts this batch."""
import argparse
import hashlib
import json
import sys
import zipfile
sys.dont_write_bytecode=True
from profile_audit import (BASE, ROOT, PREFIX, SEAL, STATE, ReadBudget, source_paths,
                           document_paths, runtime_paths, files_under, present,
                           preparation_usage, verify_upstreams, require)
from audit import audit


def write_new(path,data):
    with path.open('xb',buffering=0) as stream:
        require(stream.write(data)==len(data),'SEAL_METADATA_SHORT_WRITE')


def freeze():
    require(not present(SEAL),'FROZEN_PREPARATION_IS_IMMUTABLE')
    require(not present(BASE/'execution') and not present(BASE/'runs'),'PREPARATION_ALREADY_CONSUMED')
    source_manifest=BASE/'evidence/source-manifest.json';archive_path=BASE/'artifacts/E3-source.zip'
    require(not present(source_manifest) and not present(archive_path),'SOURCE_SEAL_OUTPUT_ALREADY_EXISTS_NO_OVERWRITE')
    budget=ReadBudget();current=audit(True,budget);recorded=budget.json(BASE/'evidence/audit.json')
    for key in ('scope','status','state','configuration','batch','upstream','build','preparationChecks','nativeProbes','preparationAssertions','nativeProbeAssertions','preparedNotRun','runtimeAdmission'):
        require(recorded[key]==current[key],'AUDIT_SNAPSHOT_CHANGED:'+key)
    require(recorded['unconsumedRequiredForThisAudit'] is True and recorded['noInFlight'] is True,'AUDIT_NOT_FINAL_UNCONSUMED')
    paths=source_paths();records=[]
    # Each source is read once for this archive write. Its fingerprint is then
    # reused for the immutable inventory. A nested source ZIP stays one member.
    with zipfile.ZipFile(archive_path,'x',zipfile.ZIP_DEFLATED) as archive:
        for path in paths:
            raw=budget.read(path);records.append(budget.record(path))
            info=zipfile.ZipInfo(path.relative_to(ROOT).as_posix(),date_time=(2026,10,17,0,0,0))
            info.compress_type=zipfile.ZIP_DEFLATED;archive.writestr(info,raw)
    source=dict(schema=1,scope='E3_SOURCE_AND_SINGLE_COMPLETE_UPSTREAM_CONTAINER',files=records,
                upstreamContainer='upstream-e2f/E2F-source.zip',nestedDependencies='FROZEN_OPAQUE_ZIP_MEMBERS_NOT_RECURSIVELY_REOPENED')
    write_new(source_manifest,(json.dumps(source,indent=2)+'\n').encode('utf-8'))
    evidence=[path for path in files_under('evidence') if path!=SEAL]
    artifacts=files_under('artifacts');docs=document_paths()
    immutable=sorted(set(paths+evidence+artifacts+docs))
    immutable_records=[budget.record(path) for path in immutable]
    selfcheck=files_under('selfcheck') if present(BASE/'selfcheck') else []
    selfcheck_records=[budget.record(path) for path in selfcheck]
    runtime=[budget.record(path) for path in runtime_paths()]
    require({row['path'] for row in runtime}<={row['path'] for row in immutable_records},'RUNTIME_MUST_BE_IMMUTABLE_SUBSET')
    before=preparation_usage();batch=current['batch']
    profile_hashes={name:budget.fingerprint(BASE/'profiles'/name)['sha256'] for name in ('inputs.json','cases.json','runtime-policy.json','machine.json')}
    result=dict(schema=1,candidate='D1-E3-20261017',state=STATE,batchId=batch['batchId'],immutableFiles=immutable_records,files=immutable_records,
                runtimeFiles=runtime,baselineArtifacts=current['upstream']['baselineArtifacts'],selfcheckFiles=selfcheck_records,
                immutableExcludedDirectories=['execution','runs','selfcheck'],selfHashExcluded=True,expectedFreezeProvidedExternally=True,
                runtimeInventoryRule='EXACT_SRC_TOOLS_PROFILES_MANIFEST_PLUS_ONLY_E3_DLL_AND_JAVA_E3_CLASSES',
                sourceManifest='evidence/source-manifest.json',sourceFiles=len(records),sourceZip=budget.record(archive_path),
                profileHashes=profile_hashes,manifestSha256=budget.fingerprint(BASE/'manifest/branches.json')['sha256'],batchManifestSha256=batch['batchManifestSha256'],
                upstream=current['upstream'],configuration=current['configuration'],batch=batch,build=current['build'],
                preparationAssertions=current['preparationAssertions'],nativeProbeAssertions=current['nativeProbeAssertions'],
                historicalAssertionsIncluded=False,actualFullAssertions=0,currentRealMediaBytesRead=0,currentOSMetricSamples=0,
                realPF='NOT_RUN',real61='NOT_RUN',realExecutionEnabled=False,preparedNotRun=current['preparedNotRun'],noInFlight=True,
                prepUsage=dict(metadataBytes=0,fixtureBytes=before['fixtureBytes']),prepEvidenceBytesBeforeSeal=before['metadataBytes'],sealBytes=0,
                preparationCaps=dict(metadataBytes=819200,fixtureBytes=1441792),
                executionReservations=dict(productionMetadataPeakBytes=3178496,wrapperMetadataBytes=196608,productionFixtureBytes=655360),
                combinedCaps=dict(metadataBytes=4194304,fixtureBytes=2097152),sourceReadUsage=budget.facts(),
                runtimeAdmission=current['runtimeAdmission'],externalRuntimeCompleteRehashPerformed=False,externalRuntimeDllRehashedDuringPreparation=False,
                executionStartedByFreeze=False,reservationConsumedByFreeze=False,hostJNI='BLOCKED',D1='NOT_PASSED',M0='NOT_STARTED')
    for _ in range(16):
        data=(json.dumps(result,indent=2)+'\n').encode('utf-8');total=before['metadataBytes']+len(data)
        if result['sealBytes']==len(data) and result['prepUsage']['metadataBytes']==total:break
        result['sealBytes']=len(data);result['prepUsage']['metadataBytes']=total
    else:raise AssertionError('SEAL_SIZE_ACCOUNTING_DID_NOT_CONVERGE')
    require(total<=819200 and total+3178496+196608<=4194304 and before['fixtureBytes']+655360<=2097152,'PREPARATION_AND_RUN_AGGREGATE_CAP')
    require(not present(BASE/'execution') and not present(BASE/'runs'),'PREPARATION_CONSUMED_DURING_SEAL')
    write_new(SEAL,data)
    value=dict(state=STATE,seal='evidence/e3-freeze.json',expectedFreezeSha256=hashlib.sha256(data).hexdigest(),
               sourceZip=result['sourceZip'],sourceFiles=len(records),immutableFiles=len(immutable_records),runtimeFiles=len(runtime),
               selfcheckFiles=len(selfcheck_records),prepUsage=result['prepUsage'],sourceReadUsage=budget.facts(),
               preparationAssertions=result['preparationAssertions'],nativeProbeAssertions=result['nativeProbeAssertions'],
               executionStarted=False,reservationConsumedAtSeal=False)
    print(json.dumps(value,sort_keys=True));return value


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--freeze',action='store_true');args=parser.parse_args()
    if args.freeze:freeze()
    else:print('INSPECT_ONLY: explicit --freeze required; never starts, reserves, or grants a batch')
