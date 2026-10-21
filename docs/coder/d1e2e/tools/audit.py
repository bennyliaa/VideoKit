"""Read preparation JSON/source only; never import or call a runtime wrapper."""
import argparse,ast,hashlib,json
from pathlib import Path
from profile_audit import verify_configuration,verify_upstreams,verify_batch

BASE=Path(__file__).resolve().parents[1]
def read(path):return json.loads(path.read_text(encoding='utf-8-sig'))
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def present(path):return path.exists() or path.is_symlink() or path.is_junction()

def verify_preparation_checks():
    path=BASE/'evidence/preparation-checks.json';checks=read(path)
    assert checks['schema']==1 and checks['scope']=='E2E_PREPARATION_STATIC_AND_SYNTHETIC_GUARDS' and checks['status']=='PASS'
    assert type(checks['assertions']) is int and checks['assertions']==len(checks['checks'])>0
    for key in ('newG','helpersStarted','osMetricSamples','actualFullRuns','mediaBytesRead'):assert type(checks[key]) is int and checks[key]==0
    assert checks['realRootCreated'] is checks['reservationConsumed'] is False and checks['noInFlight'] is True
    assert checks['limitations'] and checks['simulatedCases']
    return dict(evidence='evidence/preparation-checks.json',sha256=sha(path),assertions=checks['assertions'],scope=checks['scope'],
                simulatedCases=checks['simulatedCases'],limitations=checks['limitations'],actualGStarted=0,actualOSMetricSamples=0,actualFullRuns=0)

def audit(*,require_unconsumed=True):
    configuration=verify_configuration(read(BASE/'manifest/branches.json'));upstream=verify_upstreams();batch=verify_batch()
    # An unchanged production helper deliberately rejects that old seal name.
    assert not present(BASE/'evidence/freeze-summary.json'),'E2E_USES_E2E_FREEZE_NOT_PRODUCTION_HELPER_BLOCKING_SEAL'
    directories={name:present(BASE/name) for name in ('execution','selfcheck')}
    if require_unconsumed:assert not any(directories.values()),'PREPARATION_CANNOT_CONSUME_OR_CREATE_EXECUTION_ROOTS'
    for pattern in ('targeted*.json','build*.json','run-selfcheck*.json','mock-selfcheck*.json','diagnostic*.json','actual-regression*.json','g-lifecycle*.json','g-comparison*.json'):
        assert not list((BASE/'evidence').glob(pattern)),'E2E_PREPARATION_FORBIDS_RUNTIME_OR_NEW_TARGETED_EVIDENCE:'+pattern
    required={'e2e_admission.py','e2e_driver.py','launch-once.py','check-preparation.py','audit.py','profile_audit.py','freeze.py','verify.py','r-helper.ps1'}
    assert required<={path.name for path in (BASE/'tools').iterdir() if path.is_file()},'E2E_PREPARATION_WRAPPERS_OR_CHECKS_MISSING'
    # Parsing is a static syntax check, never module loading or code execution.
    for path in (BASE/'tools').glob('*.py'):ast.parse(path.read_text(encoding='utf-8'),filename=str(path))
    checks=verify_preparation_checks()
    metadata=sum(path.stat().st_size for path in (BASE/'evidence').rglob('*') if path.is_file())
    assert metadata<=batch['maximumPreparationMetadataBytes'],'PREPARATION_EXHAUSTS_RESERVED_EXECUTION_METADATA'
    snapshot=dict(atSeal=True,state='PREPARED_NOT_RUN_PENDING_TESTER',executionDirectoryCreated=False,selfcheckDirectoryCreated=False,
                  reservationConsumed=False,actualGStarted=0,helpersStarted=0,osMetricSamples=0,actualFullRuns=0,mediaBytesRead=0,
                  currentProcessInspectionPerformed=False,meaning='Historical preparation snapshot; never a claim that later tester execution did not happen')
    return dict(schema=1,status='PASS',scope='E2E_READ_ONLY_PREPARATION_EVIDENCE_AUDIT',configurationVerified=True,configuration=configuration,
                productionBindingVerified=True,productionBinding=configuration['productionBinding'],batch=batch,batchManifestSha256=batch['batchManifestSha256'],
                productionBindings=batch['productionBindings'],preparationChecks=checks,preparationAssertions=checks['assertions'],
                targetedAssertions=0,driverSyntheticAssertions=0,compileInvocations=0,repairCompilations=0,actualFullAssertions=0,
                historicalAssertionsIncluded=False,currentOSObservationsAtSeal=0,preparedNotRun=snapshot,
                currentOutputDirectories=directories,unconsumedRequiredForThisAudit=require_unconsumed,
                preparationEvidenceBytesAtAudit=metadata,maximumPreparationMetadataBytes=batch['maximumPreparationMetadataBytes'],
                runtimeAdmission='PREPARATION_ONLY_TESTER_MUST_VERIFY_AND_EXPLICITLY_CONSUME_NEW_SINGLE_BATCH',
                realExecutionEnabled=False,realMedia='NOT_RUN',realPF='NOT_RUN',D1='NOT_PASSED',M0='NOT_STARTED',**upstream)
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--audit',action='store_true');args=parser.parse_args()
    print(json.dumps(audit() if args.audit else dict(mode='INSPECT_ONLY',executionAllowed=False,reservationConsumed=False),separators=(',',':')))
