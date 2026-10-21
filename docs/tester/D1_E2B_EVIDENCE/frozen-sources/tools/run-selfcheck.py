"""Outer caller saves the existing return-channel witness after G closes its log."""
import argparse, hashlib, json, subprocess, sys, time
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--run',action='store_true');parser.add_argument('--synthetic-observer-mock',action='store_true');args=parser.parse_args()
    if not args.run:print('INSPECT_ONLY: explicit --run required');return 0
    if (BASE/'evidence/freeze-summary.json').exists():raise RuntimeError('FROZEN_PACKAGE_READ_ONLY_NEW_AUTHORIZED_BATCH_REQUIRED')
    started=time.time_ns()
    argv=[sys.executable,'-B',str(BASE/'src/controller.py'),'--synthetic-selfcheck']
    if args.synthetic_observer_mock:argv.append('--synthetic-observer-mock')
    else:
        sys.path.insert(0,str(BASE/'src'))
        from synthetic_admission import reserve_actual,write_new
        try:reservation=reserve_actual(str(started))
        except Exception as error:
            # No process/fixture has been created. A failed condition does not
            # spend a second test or substitute a mock for actual admission.
            report=dict(scope='E2B_CONDITIONAL_ACTUAL_REGRESSION',status='NOT_RUN',reason=str(error)[:256],helpersStarted=0,noInFlight=True,realExecutionAllowed=False)
            path=BASE/'evidence/actual-regression-not-run.json'
            if not path.exists():write_new(path,report)
            print(json.dumps(report));return 2
        argv+=['--actual-run-id',reservation['runId']]
    process=subprocess.Popen(argv,stdout=subprocess.PIPE,stderr=subprocess.PIPE,creationflags=subprocess.CREATE_NO_WINDOW)
    try:
        stdout,stderr=process.communicate(timeout=200)
    except subprocess.TimeoutExpired:
        pending={'scope':'OUTER_CALLER_RETURN_CHANNEL','status':'PENDING','pid':process.pid,'started':started,'exited':False,'rule':'STOP_WAITING_NO_NATIVE_COMPLETION_OR_EXIT_INFERRED'}
        path=BASE/'evidence'/('pending-'+str(started)+'.json');path.write_text(json.dumps(pending,indent=2)+'\n',encoding='utf-8');print(json.dumps(pending));return 2
    result=subprocess.CompletedProcess(process.args,process.returncode,stdout,stderr)
    if len(result.stdout)>8192 or len(result.stderr)>65536:raise RuntimeError('CALLER_RECEIPT_LIMIT')
    stdout=result.stdout.decode();stderr=result.stderr.decode();witness=json.loads(stdout) if stdout.strip() else None
    hub=(witness.get('callbackHub') or witness.get('hub') or {}) if witness else {}
    remaining=witness.get('remainingResources',witness.get('logClose',{}).get('remainingResources')) if witness else None
    helpers_done=(all(p.get('exited') is True for p in witness['logClose']['exitedHelpers'].values()) if witness and witness.get('logClose',{}).get('exitedHelpers') else
                  all(p.get('started') is False or p.get('exitObserved') is True for p in witness.get('helpers',{}).values()) if witness else False)
    no_in_flight=bool(witness and remaining==0 and hub.get('ownershipPending') is False and hub.get('workersAlive')==0 and helpers_done and
                      not witness.get('nativePending') and not witness.get('logOwnershipPending') and not witness.get('runtimeObservation',{}).get('nativeQueryPending'))
    evidence={'scope':'OUTER_CALLER_RETURN_CHANNEL','exitCode':result.returncode,'started':started,'ended':time.time_ns(),'witness':witness,'stderr':stderr,'noInFlight':no_in_flight,'mockMetricsUsed':args.synthetic_observer_mock}
    path=BASE/'evidence'/(('mock-selfcheck-' if args.synthetic_observer_mock else 'run-selfcheck-')+str(started)+'.json');path.write_text(json.dumps(evidence,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'evidence':str(path),'exitCode':result.returncode,'witness':witness,'stderr':stderr},separators=(',',':')))
    return result.returncode
if __name__=='__main__':sys.exit(main())
