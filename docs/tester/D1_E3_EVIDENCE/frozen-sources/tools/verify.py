"""Read-only full seal verification; existing results are never run or repaired."""
import argparse
import json
import os
import re
import sys
sys.dont_write_bytecode=True
from profile_audit import (BASE, ROOT, PREFIX, SEAL, STATE, ReadBudget, safe, package_path,
                           present, require, files_under, source_paths, runtime_paths,
                           document_paths, verify_archive, verify_upstreams,
                           verify_configuration, verify_batch, preparation_usage)
from audit import verify_build, verify_preparation_checks, verify_native_probes


def output_kind(path):return 'FIXTURE' if re.fullmatch(r'T(?:0[1-9]|10)\.out',path.name) else 'METADATA'


def existing_output_paths(batch):
    roots=[];execution=BASE/'execution';runs=BASE/'runs'
    if present(execution):roots.append(safe(execution))
    if present(runs):
        require({child.name for child in safe(runs).iterdir()}<={batch['uniqueRootName']},'UNAUTHORIZED_OUTPUT_BATCH')
        path=runs/batch['uniqueRootName']
        if present(path):roots.append(safe(path))
    result=[];directories=0
    for root in roots:
        for current,dirs,files in os.walk(root,followlinks=False):
            safe(current);directories+=1;require(directories<=128,'RESULT_DIRECTORY_CAP')
            for name in dirs:safe(os.path.join(current,name))
            for name in files:
                path=safe(os.path.join(current,name));require(path.suffix.lower()!='.bin','NO_SOURCE_COPY_IN_REAL_OUTPUT')
                result.append(path);require(len(result)<=512,'RESULT_FILE_CAP')
    return sorted(result)


def existing_execution(frozen,batch,seal_sha):
    budget=ReadBudget(6291456,512)
    late=BASE/'execution/late-result-manifest.json';initial=BASE/'execution/result-manifest.json'
    path=late if present(late) else initial
    directories={name:present(BASE/name) for name in ('execution','runs')}
    if not present(path):return dict(state='NO_EXECUTION_OUTPUTS_PRESENT' if not any(directories.values()) else 'OUTPUTS_PRESENT_NO_FINAL_INVENTORY',
        directories=directories,reportedStatus='NOT_RUN' if not any(directories.values()) else 'PENDING',finalAggregateUsageVerified=False,
        executionStartedByVerify=False,reservationConsumedByVerify=False,automaticCollectionPerformed=False,outputReadUsage=budget.facts())

    def load_manifest(file):
        require(safe(file).stat().st_size<=49152,'RESULT_MANIFEST_BYTE_CAP')
        value=budget.json(file)
        require(value['schema']==1 and value['scope']=='E3_EXECUTION_RESULT_MANIFEST' and value['batchId']==batch['batchId'],'RESULT_BATCH_SCOPE')
        require(value['expectedFreeze']==seal_sha and value['prepUsage']==frozen['prepUsage'],'RESULT_SEAL_AND_PREP_BINDING')
        require(value['caps']['metadataBytes']==4194304 and value['caps']['fixtureBytes']==2097152,'RESULT_CAP_CHANGED')
        require(type(value['complete']) is type(value['resultHashComplete']) is bool and type(value['originalChildExitObserved']) is bool,'RESULT_UNKNOWN_FACT_TYPE')
        require(value['noInFlight'] is None or type(value['noInFlight']) is bool,'RESULT_QUIESCENCE_FACT_TYPE')
        require(value['manifestBytes']==file.stat().st_size,'RESULT_SELF_BYTES')
        require(type(value.get('batchPassProven')) is bool and value['batchPassProven']==(value['complete'] is True and value['status']=='PASS'),'RESULT_BATCH_PASS_LAYER')
        return value

    result=load_manifest(path);initial_preserved=False
    if path==late:
        original=load_manifest(initial)
        require(original['status']=='PENDING' and original['complete'] is original['resultHashComplete'] is False and original['files']==[] and
                original['outputUsage']==dict(metadataBytes=None,fixtureBytes=None) and original['combinedUsage']=={} and original['noInFlight'] in (None,False),'LATE_MUST_PRESERVE_INITIAL_PENDING')
        # The original child may already have exited while close/owner facts
        # were still UNKNOWN. That valid PENDING is never forced to exit=False.
        initial_preserved=True
    if not result['complete'] or not result['resultHashComplete']:
        require(result['status']=='PENDING' and result['files']==[] and result['outputUsage']==dict(metadataBytes=None,fixtureBytes=None) and result['combinedUsage']=={},'INCOMPLETE_INVENTORY_MUST_REMAIN_UNKNOWN')
        return dict(state='PENDING_INVENTORY_NOT_SCANNED',reportedStatus=result['status'],reportedNoInFlight=result['noInFlight'],
                    originalChildExitObserved=result['originalChildExitObserved'],finalAggregateUsageVerified=False,initialPendingPreserved=initial_preserved,
                    executionStartedByVerify=False,reservationConsumedByVerify=False,automaticCollectionPerformed=False,outputReadUsage=budget.facts())
    require(result['noInFlight'] is True and result['originalChildExitObserved'] is True,'FINAL_INVENTORY_REQUIRES_ORIGINAL_QUIESCENCE')
    manifest_name=path.relative_to(BASE).as_posix()
    paths=existing_output_paths(batch);actual={file.relative_to(BASE).as_posix():file for file in paths}
    rows=result['files'];require(len(rows)==len({row['path'] for row in rows}) and {row['path'] for row in rows}==set(actual)-{manifest_name},'EXACT_FINAL_OUTPUT_INVENTORY')
    usage=dict(metadataBytes=0,fixtureBytes=0);wrapper=0
    for relative,file in actual.items():
        value=budget.fingerprint(file);kind=output_kind(file)
        usage['fixtureBytes' if kind=='FIXTURE' else 'metadataBytes']+=value['bytes']
        if file.is_relative_to(BASE/'execution'):wrapper+=value['bytes']
    for row in rows:
        file=actual[row['path']];require(row['kind']==output_kind(file) and budget.fingerprint(file)==dict(bytes=row['bytes'],sha256=row['sha256']),'RESULT_FILE_HASH_OR_CLASSIFICATION:'+row['path'])
    production=usage['metadataBytes']-wrapper
    require(wrapper<=196608 and production<=3178496 and usage['fixtureBytes']<=655360 and result['wrapperMetadataBytes']==wrapper,'RESULT_SUBLEDGER_CAP')
    combined={key:frozen['prepUsage'][key]+usage[key] for key in usage}
    require(combined['metadataBytes']<=4194304 and combined['fixtureBytes']<=2097152 and result['outputUsage']==usage and result['combinedUsage']==combined,'RESULT_SELF_INCLUDED_AGGREGATE')
    return dict(state='EXISTING_RESULT_INTEGRITY_VERIFIED',reportedStatus=result['status'],reportedNoInFlight=True,originalChildExitObserved=True,
                outputUsage=usage,combinedUsage=combined,wrapperMetadataBytes=wrapper,productionMetadataBytes=production,outputFiles=len(paths),
                finalAggregateUsageVerified=True,initialPendingPreserved=initial_preserved,outputReadUsage=budget.facts(),
                executionOutcomeNotReclassified=True,executionStartedByVerify=False,reservationConsumedByVerify=False,automaticCollectionPerformed=False)


def verify(expected_freeze=None):
    budget=ReadBudget();frozen=budget.json(SEAL);seal_sha=budget.fingerprint(SEAL)['sha256']
    if expected_freeze is not None:require(isinstance(expected_freeze,str) and re.fullmatch('[0-9a-f]{64}',expected_freeze) and expected_freeze==seal_sha,'EXPECTED_FREEZE_MISMATCH')
    require(frozen['schema']==1 and frozen['state']==STATE and frozen['selfHashExcluded'] is frozen['expectedFreezeProvidedExternally'] is True,'PREPARATION_SEAL_SCHEMA')
    require(frozen['files']==frozen['immutableFiles'] and frozen['immutableExcludedDirectories']==['execution','runs','selfcheck'],'SEPARATE_IMMUTABLE_AND_OUTPUT_SETS')
    require(frozen['preparedNotRun']==dict(atSeal=True,reservationConsumed=False,rootCreated=False,executionAuthorized=False),'PREPARED_FACTS_APPLY_AT_SEAL')
    source=budget.json(BASE/'evidence/source-manifest.json')
    require(source['schema']==1 and source['scope']=='E3_SOURCE_AND_SINGLE_COMPLETE_UPSTREAM_CONTAINER','SOURCE_MANIFEST_SCOPE')
    archive=BASE/'artifacts/E3-source.zip'
    require(frozen['sourceZip']['path']==PREFIX+'artifacts/E3-source.zip','SOURCE_ZIP_PATH')
    # Decode the outer ZIP first so subsequent file-record checks reuse its
    # already charged raw digest rather than reading that large file twice.
    verify_archive(archive,source['files'],budget,expected={key:frozen['sourceZip'][key] for key in ('bytes','sha256')})
    upstream=verify_upstreams(budget)
    require(upstream==frozen['upstream'],'UPSTREAM_ANCHOR_FACTS_CHANGED')
    configuration=verify_configuration(budget.json(BASE/'manifest/branches.json'),budget);batch=verify_batch(budget)
    require(frozen['configuration']==configuration and frozen['batch']==batch and frozen['batchId']==batch['batchId'],'CONFIGURATION_OR_BATCH_BINDING')
    require(frozen['batchManifestSha256']==batch['batchManifestSha256'] and frozen['manifestSha256']==budget.fingerprint(BASE/'manifest/branches.json')['sha256'],'MANIFEST_HASH_BINDING')
    require(frozen['profileHashes']=={name:budget.fingerprint(BASE/'profiles'/name)['sha256'] for name in ('inputs.json','cases.json','runtime-policy.json','machine.json')},'FOUR_PROFILE_HASH_BINDING')
    entries=frozen['immutableFiles'];require(len(entries)==len({row['path'] for row in entries}),'IMMUTABLE_DUPLICATE')
    allowed_docs={path.relative_to(ROOT).as_posix() for path in document_paths()}
    for row in entries:
        name=row['path'];require(name.startswith(PREFIX) or name in allowed_docs,'IMMUTABLE_DOCUMENT_SCOPE')
        path=package_path(name) if name.startswith(PREFIX) else safe(ROOT/name)
        require(path!=SEAL and not any(path.is_relative_to(BASE/folder) for folder in ('execution','runs','selfcheck')),'OUTPUT_IN_IMMUTABLE_SET')
        require(budget.fingerprint(path)==dict(bytes=row['bytes'],sha256=row['sha256']),'IMMUTABLE_FILE_CHANGED:'+name)
    expected=set(source_paths()+[path for path in files_under('evidence') if path!=SEAL]+files_under('artifacts')+document_paths())
    require({path.relative_to(ROOT).as_posix() for path in expected}=={row['path'] for row in entries},'IMMUTABLE_EXACT_FILE_SET')
    require({path.relative_to(ROOT).as_posix() for path in source_paths()}=={row['path'] for row in source['files']} and len(source['files'])==frozen['sourceFiles'],'SOURCE_EXACT_FILE_SET')
    for row in source['files']:require(budget.fingerprint(package_path(row['path']))==dict(bytes=row['bytes'],sha256=row['sha256']),'SOURCE_FILE_CHANGED')
    runtime=[budget.record(path) for path in runtime_paths()]
    require(runtime==frozen['runtimeFiles'] and all(row in entries for row in runtime),'EXACT_RUNTIME_SUBSET')
    require(frozen['baselineArtifacts']==upstream['baselineArtifacts'],'BASELINE_ARTIFACTS_ARE_NOT_RUNTIME')
    selfcheck=files_under('selfcheck') if present(BASE/'selfcheck') else []
    require([budget.record(path) for path in selfcheck]==frozen['selfcheckFiles'],'PREPARATION_SELFCHECK_SET_CHANGED')
    build=verify_build(budget);checks=verify_preparation_checks(budget);probes=verify_native_probes(budget)
    recorded=budget.json(BASE/'evidence/audit.json')
    require(recorded['status']=='PASS' and recorded['configuration']==configuration and recorded['upstream']==upstream and recorded['batch']==batch and recorded['build']==build,'FROZEN_AUDIT_BINDING')
    require(recorded['preparationChecks']==checks and recorded['nativeProbes']==probes and frozen['preparationAssertions']==checks['assertions'] and frozen['nativeProbeAssertions']==probes['nativeProbeAssertions'],'SEPARATE_PREPARATION_AND_NATIVE_COUNTS')
    require(frozen['historicalAssertionsIncluded'] is False and frozen['actualFullAssertions']==frozen['currentRealMediaBytesRead']==frozen['currentOSMetricSamples']==0 and frozen['realPF']==frozen['real61']=='NOT_RUN','NO_REAL_RUN_AT_SEAL')
    usage=preparation_usage();require(usage==frozen['prepUsage'] and frozen['sealBytes']==SEAL.stat().st_size and usage['metadataBytes']==frozen['prepEvidenceBytesBeforeSeal']+frozen['sealBytes'],'SEAL_SELF_INCLUDED_PREP_USAGE')
    require(usage['metadataBytes']<=819200 and usage['metadataBytes']+3178496+196608<=4194304 and usage['fixtureBytes']+655360<=2097152,'PREPARATION_AND_EXECUTION_RESERVES')
    execution=existing_execution(frozen,batch,seal_sha)
    result=dict(integrity='PASS',state=STATE,stateMeaning='PREPARATION_AT_SEAL_ONLY_NOT_EXECUTION_ADMISSION',batchId=batch['batchId'],freezeSha256=seal_sha,
                expectedFreezeSupplied=expected_freeze is not None,sourceFiles=len(source['files']),immutableFiles=len(entries),runtimeFiles=len(runtime),baselineArtifacts=10,
                preparationAssertions=checks['assertions'],nativeProbeAssertions=probes['nativeProbeAssertions'],historicalAssertionsIncluded=False,
                sourceReadUsage=budget.facts(),prepUsage=usage,execution=execution,executionStartedByVerify=False,reservationConsumedByVerify=False,
                externalRuntimeCompleteRehashPerformed=False,externalRuntimeDllRehashedDuringPreparation=False,D1='NOT_PASSED',M0='NOT_STARTED')
    print(json.dumps(result,sort_keys=True));return result


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--expected-freeze');args=parser.parse_args();verify(args.expected_freeze)
