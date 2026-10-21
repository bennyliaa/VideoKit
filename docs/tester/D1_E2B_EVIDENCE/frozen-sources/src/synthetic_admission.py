"""CREATE_NEW single-use reservation for E2B's conditional owned-file test.

This does not authorize REAL_IO, create a real root, or read test_media.
"""
import json,os,hashlib
from pathlib import Path
from gcore import BASE,need,sha
from diagnostic_gate import SingleActualRegressionGate,validate_diagnostic


def write_new(path,value):
    data=(json.dumps(value,indent=2,allow_nan=False)+'\n').encode('utf-8')
    with path.open('xb',buffering=0) as file:
        need(file.write(data)==len(data),'SYNTHETIC_ADMISSION_SHORT_WRITE');file.flush();os.fsync(file.fileno())


def diagnostic_binding():
    summary=json.loads((BASE/'evidence/diagnostic-summary.json').read_text(encoding='utf-8'))
    relative=summary['evidence'];path=BASE/relative
    need(path.parent==BASE/'evidence' and path.name.startswith('diagnostic-') and path.suffix=='.json','DIAGNOSTIC_RECEIPT_PATH')
    data=path.read_bytes();need(len(data)<=524288,'DIAGNOSTIC_RECEIPT_LIMIT')
    report=json.loads(data);validation=validate_diagnostic(report)
    need(validation==summary['validation'],'DIAGNOSTIC_SUMMARY_MISMATCH')
    need(report['configuration']['assemblySha256']==sha((BASE/'artifacts/E2B.dll').read_bytes()),'DIAGNOSTIC_DLL_CHANGED')
    return report,validation,relative,sha(data)


def reserve_actual(run_id):
    report,validation,relative,digest=diagnostic_binding()
    path=BASE/'evidence/actual-regression-reservation.json'
    prior=json.loads(path.read_text(encoding='utf-8')) if path.exists() else None
    reservation=SingleActualRegressionGate(report,prior_record=prior).reserve(run_id)
    reservation.update(diagnosticEvidence=relative,diagnosticFileSha256=digest,launcherPid=os.getpid(),
                       dllSha256=sha((BASE/'artifacts/E2B.dll').read_bytes()),policySha256=sha((BASE/'profiles/runtime-policy.json').read_bytes()),
                       loader='ABSOLUTE_ASSEMBLY_LOAD_FROM',profile='SYNTHETIC_SELF_OWNED_ONLY')
    # The exclusive file is the cross-process reservation, before even G launch.
    write_new(path,reservation)
    return reservation


def claim_actual(run_id):
    path=BASE/'evidence/actual-regression-reservation.json'
    reservation=json.loads(path.read_text(encoding='utf-8'))
    need(reservation.get('consumed') is True and reservation.get('maximumActualRuns')==1 and reservation.get('runId')==run_id,'SINGLE_ACTUAL_RESERVATION_REQUIRED')
    need(reservation['launcherPid']==os.getppid(),'ORIGINAL_SYNTHETIC_LAUNCHER_REQUIRED')
    report,validation,relative,digest=diagnostic_binding()
    need(validation['eligibleForOneActualSyntheticRegression'] and reservation['diagnosticSha256']==validation['diagnosticSha256'] and reservation['diagnosticEvidence']==relative and reservation['diagnosticFileSha256']==digest,'SYNTHETIC_DIAGNOSTIC_BINDING_CHANGED')
    need(reservation['dllSha256']==sha((BASE/'artifacts/E2B.dll').read_bytes()) and reservation['policySha256']==sha((BASE/'profiles/runtime-policy.json').read_bytes()),'SYNTHETIC_BINARY_OR_POLICY_CHANGED')
    claim=dict(schema=1,scope='E2B_SINGLE_ACTUAL_SYNTHETIC_CLAIM',runId=run_id,controllerPid=os.getpid(),launcherPid=os.getppid(),
               diagnosticSha256=validation['diagnosticSha256'],profile='SYNTHETIC',mockMetricsUsed=False,realExecutionAllowed=False)
    write_new(BASE/'evidence/actual-regression-claim.json',claim)
    return claim
