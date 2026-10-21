"""Read-only preparation audit. No runner/checker/native module is imported."""
import argparse
import json
import sys
sys.dont_write_bytecode=True
from profile_audit import (BASE, PREFIX, ReadBudget, STATE, files_under, runtime_paths,
                           verify_upstreams, verify_configuration, verify_batch,
                           preparation_usage, present, require)


def verify_build(budget):
    build=budget.json(BASE/'evidence/build.json');reservation=budget.json(BASE/'evidence/build-reservation.json')
    require(build['schema']==1 and build['scope']=='E3_COMPILE_ONLY' and build['status']=='PASS','BUILD_NOT_PROVEN')
    require(build['compileInvocations']==reservation['compileInvocations']==1 and build['repairCompilations']==0 and
            build['csharpCompilations']==build['javaCompilations']==1,'SINGLE_NEW_ARTIFACT_COMPILE_REQUIRED')
    require(reservation['scope']=='E3_SINGLE_COMPILE_RESERVATION' and reservation['refundAllowed'] is reservation['repairAllowed'] is False and reservation['createdBeforeCompilers'] is True,'COMPILE_RESERVATION')
    for key in ('helpersStarted','newG','osMetricSamples','realMediaBytesRead','actualFullRuns'):
        require(type(build[key]) is int and build[key]==0,'BUILD_ACTIVITY:'+key)
    runtime=runtime_paths();compiled=[path for path in runtime if path.is_relative_to(BASE/'artifacts')]
    require({PREFIX+row['path'] for row in build['compiledArtifacts']}=={PREFIX+path.relative_to(BASE).as_posix() for path in compiled},'BUILD_ARTIFACT_INVENTORY')
    sources=[path for path in files_under('src') if path.suffix in ('.cs','.java')]
    for name,paths in (('sourceFiles',sources),('compiledArtifacts',compiled)):
        records=build[name];require(len(records)==len(paths) and {row['path'] for row in records}=={path.relative_to(BASE).as_posix() for path in paths},'BUILD_FILE_SET:'+name)
        for row in records:require(budget.fingerprint(BASE/row['path'])==dict(bytes=row['bytes'],sha256=row['sha256']),'BUILD_BOUND_BYTES_CHANGED:'+row['path'])
    return dict(compileInvocations=1,repairCompilations=0,csharpCompilations=1,javaCompilations=1,
                compiledArtifacts=len(compiled),sourceBytesHashed=build['sourceBytesHashed'],artifactBytesHashed=build['artifactBytesHashed'])


def verify_preparation_checks(budget):
    result=budget.json(BASE/'evidence/preparation-checks.json')
    require(result['schema']==1 and result['scope']=='E3_PREPARATION_STATIC_AND_SYNTHETIC_GUARDS' and result['status']=='PASS','PREPARATION_CHECK_RECEIPT')
    require(type(result['assertions']) is int and result['assertions']>0 and len(result['checks'])==result['assertions'] and result['negativeCases'] and result['simulatedCases'],'PREPARATION_CURRENT_ASSERTIONS')
    for key in ('newG','helpersStarted','newOSMetricSamples','newActualAttempts','newActualPasses','compileInvocations','originalEvidenceWrites','mediaStatCalls','mediaBytesRead'):
        require(type(result[key]) is int and result[key]==0,'PURE_PREPARATION_ACTIVITY:'+key)
    for key in ('reservationConsumed','rootCreated','outputRootCreated','executionAllowed','realPFRun','real61Run'):
        require(result[key] is False,'PURE_PREPARATION_GUARD:'+key)
    require(result['noInFlight'] is True,'PREPARATION_CHECK_PENDING')
    return dict(scope=result['scope'],assertions=result['assertions'],receipt=budget.record(BASE/'evidence/preparation-checks.json'),
                purelySynthetic=True,newActualAttempts=0)


def verify_native_probes(budget):
    result=budget.json(BASE/'evidence/native-probes.json')
    require(result['schema']==1 and result['scope']=='E3_SELF_OWNED_NATIVE_INPUT_PROBES' and result['status']=='PASS','NATIVE_PROBE_RECEIPT')
    cases=result['cases'];require(len(cases)==2 and {case['mode'] for case in cases}=={'strict-success','strict-guard-mismatch'},'EXACT_TWO_NATIVE_PROBE_CASES')
    total=0
    for case in cases:
        require(case['exitCode']==0 and case['processExitObserved'] is True,'PROBE_ORIGINAL_EXIT_REQUIRED')
        require(type(case['stdoutBytes']) is int and 0<case['stdoutBytes']<=65536 and type(case['stderrBytes']) is int and 0<=case['stderrBytes']<=65536,'PROBE_PIPE_BYTE_CAP')
        value=case['receipt'];positive=case['mode']=='strict-success'
        require(value['scope']=='SELF_OWNED_NON_MEDIA_JAVA_STRICT_INPUT_PROBE' and value['status']=='PASS' and value['mode']==case['mode'],'PROBE_ORIGINAL_RECEIPT')
        require(value['shareMode']==1 and value['access']=='READ_ONLY' and value['creation']=='OPEN_EXISTING' and value['nativeOpens']==value['nativeCloses']==1,'STRICT_ORIGINAL_HANDLE_CONTRACT')
        require(value['identityQueries']==(2 if positive else 1) and value['nativeReads']==value['nativeSeeks']==(1 if positive else 0) and value['requestedInputBytes']==(2 if positive else 0) and value['actualInputBytes']==(1 if positive else 0),'STRICT_PREBYTE_VERSION_AND_SHORT_READ')
        require(value['threadsStarted']==value['realMediaBytesRead']==0 and type(value['assertions']) is int and value['assertions']==len(value['checks'])>0,'STRICT_PROBE_SCOPE')
        total+=value['assertions']
    return dict(nativeProbeAssertions=total,selfOwnedJavaProbeProcesses=2,requestedSyntheticInputBytes=2,actualSyntheticInputBytes=1,
                newG=0,newR=0,realPFRun=False,real61Run=False,receipt=budget.record(BASE/'evidence/native-probes.json'))


def audit(require_unconsumed=True,budget=None):
    budget=budget or ReadBudget();upstream=verify_upstreams(budget)
    configuration=verify_configuration(budget.json(BASE/'manifest/branches.json'),budget);batch=verify_batch(budget)
    if require_unconsumed:
        require(not present(BASE/'execution') and not present(BASE/'runs'),'PREPARATION_ALREADY_CONSUMED')
    require(not present(BASE/'evidence/freeze-summary.json'),'ACTIVE_SEAL_MUST_USE_E3_NAME')
    build=verify_build(budget);checks=verify_preparation_checks(budget);probes=verify_native_probes(budget)
    usage=preparation_usage();require(usage['metadataBytes']<=819200 and usage['fixtureBytes']<=1441792,'PREPARATION_RESERVED_CREDIT')
    return dict(schema=1,scope='E3_READ_ONLY_PREPARATION_EVIDENCE_AUDIT',status='PASS',state=STATE,
                configuration=configuration,batch=batch,upstream=upstream,build=build,preparationChecks=checks,nativeProbes=probes,
                preparationAssertions=checks['assertions'],nativeProbeAssertions=probes['nativeProbeAssertions'],historicalAssertionsIncluded=False,
                currentActualFullAssertions=0,currentRealMediaBytesRead=0,currentRealPFRun=False,currentReal61Run=False,
                preparedNotRun=dict(atSeal=True,reservationConsumed=False,rootCreated=False,executionAuthorized=False),
                unconsumedRequiredForThisAudit=require_unconsumed,prepUsageAtAudit=usage,sourceReadUsage=budget.facts(),
                runtimeAdmission='PREPARED_ONLY_FRESH_AND_ORIGINAL_BASELINE_GATES_REQUIRED_AFTER_COORDINATOR_HANDOFF',
                noInFlight=True,executionStartedByAudit=False,reservationConsumedByAudit=False,realExecutionEnabled=False,
                D1='NOT_PASSED',M0='NOT_STARTED')


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--audit',action='store_true');args=parser.parse_args()
    print(json.dumps(audit() if args.audit else dict(scope='E3_PREPARATION_INSPECT',status='NOT_RUN',executionAllowed=False,
        reservationConsumed=False,rootCreated=False,newActualAttempts=0),sort_keys=True))
