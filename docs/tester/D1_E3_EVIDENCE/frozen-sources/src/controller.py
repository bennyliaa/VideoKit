"""Opt-in synthetic tool integration. Import and default CLI perform no execution."""
import argparse, json, sys, traceback
from gcore import *
from gengine import Engine
from scenarios import Scenarios
from phases import preflight, Cleanup

def fixtures(root):
    root.mkdir(parents=True,exist_ok=False)
    for name,n in [('L.bin',131072),('C.bin',4096),('Z.bin',0)]:
        with open(root/name,'xb') as file:
            for start in range(0,n,4096):file.write(bytes((i%251 for i in range(start,min(start+4096,n)))))

def stop_failure(e,error,*,timeout=.2):
    """Bounded original return-channel receipt, including a pre-helper PF failure.

    This is not a replacement GC or an extra RPC. Unknown native/helper ownership
    stays PENDING; only local proven-safe Hub/log cleanup is attempted here.
    """
    end=time.monotonic()+max(0,timeout);cleanup_errors=[]
    left=lambda:max(0,end-time.monotonic())
    try:e.completions.close(timeout=left())
    except BaseException as failure:cleanup_errors.append('hub:'+type(failure).__name__+':'+str(failure)[:160])
    hub=e.completions.pending()
    native_pending=[str(key) for key,future in getattr(e,'pending',{}).items() if not future.done()]
    callback_pending=bool(hub['cells'] or hub['queued'] or hub['active'] or hub['ownershipPending'])
    if callback_pending:
        try:e.completions.stop_when_drained()
        except BaseException as failure:cleanup_errors.append('stop:'+type(failure).__name__)
    helpers={}
    for name in ('J','R'):
        channel=getattr(e,'channels',{}).get(name)
        if channel is None:
            attempt=getattr(e,'helper_attempts',{}).get(name)
            never=attempt is not None and attempt.get('attempted') is False
            helpers[name]=dict(started=False if never else None,pid=None,instance=None,exitObserved=False,
                               attempt=attempt,status='NOT_ATTEMPTED' if never else 'START_UNKNOWN')
        else:
            proof=getattr(channel,'proof',None)
            helpers[name]=dict(started=True,pid=getattr(channel,'pid',None),instance=getattr(channel,'owner',None),
                               exitObserved=bool(proof and proof.get('exited')),exitProof=proof)
    # A startup failure precedes helper creation and log opening. Missing helpers
    # are explicit absence, never sent EXIT or accessed as if they existed.
    ledger=getattr(e,'ledger',None)
    def resources():
        if ledger is None:return {}
        with ledger.lock:return dict(ledger.live)
    live=resources()
    store=getattr(e,'store',None);log=getattr(store,'log',None)
    log_opened=bool(log is not None or getattr(e,'global_log',None) is not None or 'global-log' in live)
    log_closed=bool(getattr(e,'global_close',None) and e.global_close.get('closed'))
    if log is not None and not callback_pending and not native_pending and left()>0:
        future=None
        try:
            future=e.io.submit(store.close_log);future.result(timeout=left());log_closed=True
            e.global_close=dict(closed=True,scope='FAILURE_RETURN_CHANNEL',method='flush/fsync/close actually returned')
        except BaseException as failure:
            cleanup_errors.append('log:'+type(failure).__name__+':'+str(failure)[:160])
            if future is not None and not future.done():
                getattr(e,'pending',{})['failure-log-close']=future;native_pending.append('failure-log-close')
    if getattr(e,'io',None) is not None:
        try:e.io.shutdown(wait=False,cancel_futures=True)
        except BaseException as failure:cleanup_errors.append('io:'+type(failure).__name__)
    # Keep any recorded start error even after a later idempotent close succeeds.
    hub=e.completions.pending();live=resources()
    private_cells=None
    if hasattr(e,'cells') and hasattr(e,'lock'):
        Engine.compact_cells(e);private_cells=Engine.cell_facts(e)
    log_pending=log_opened and not log_closed
    ownership=bool(hub['ownershipPending'] or hub['cells'] or hub['queued'] or hub['active'] or native_pending or live or log_pending or
                   any(value['started'] is not False and not value['exitObserved'] for value in helpers.values()))
    witness=dict(scope='E2C_FAILURE_RETURN_CHANNEL',status='PENDING' if ownership else 'FAIL',pid=os.getpid(),
                 actualRegressionAdmission=getattr(e,'actual_regression_claim',None),
                 error=str(error)[:512],startupError=hub['startupError'],hub=hub,remainingWorkerCredits=hub['remainingCredits'],
                 helpers=helpers,nativePending=native_pending[:8],remainingResources=len(live),resources=live,
                 privateCells=private_cells,
                 logOpened=log_opened,logCloseProven=log_closed,logOwnershipPending=log_pending,
                 cleanupErrors=cleanup_errors[:8],mediaRead=None if getattr(e,'profile',{}).get('kind')=='REAL_IO' and getattr(e,'budget',None) and e.budget.globalused.get('ib',0)>0 else False,
                 realPFRun=False,real61Run=False,sourceByteRequests=getattr(e,'budget',None).globalused.get('ib',0) if getattr(e,'budget',None) else None,
                 profileKind=getattr(e,'profile',{}).get('kind'),completionRequiresWrapperEvaluation=True)
    need(len(compact(witness))<=8192,'FAILURE_RECEIPT_LIMIT')
    return 2,witness

def emit_failure(e,error,*,timeout=.2):
    code,witness=stop_failure(e,error,timeout=timeout)
    print(json.dumps(witness,separators=(',',':')))
    return code

def run():
    parser=argparse.ArgumentParser();modes=parser.add_mutually_exclusive_group();modes.add_argument('--synthetic-selfcheck',action='store_true');modes.add_argument('--recover-selfcheck');parser.add_argument('--profile',choices=('SYNTHETIC','REAL_IO'),default='SYNTHETIC')
    parser.add_argument('--synthetic-observer-mock',action='store_true',help='Explicit authored-fixture driver regression; mock metric values are not OS peaks or admission.')
    parser.add_argument('--actual-run-id',help='Historical option only; E2C forbids any complete-driver run.')
    # parse below after every option is registered
    options=parser.parse_args()
    manifest=json.loads((BASE/'manifest/branches.json').read_text(encoding='utf-8-sig'))
    if options.profile=='REAL_IO':
        from admission import load_bundle,request_real_run
        code,receipt=request_real_run('UNAUTHORIZED_PROFILE_REQUEST',load_bundle(),manifest)
        print(json.dumps(receipt,separators=(',',':')));return code
    if options.recover_selfcheck:
        from recovery import recover
        need(Path(options.recover_selfcheck).name==options.recover_selfcheck,'SELF_CHECK_NAME_ONLY')
        result=recover(BASE/'selfcheck'/options.recover_selfcheck,manifest)
        print(json.dumps(result,separators=(',',':')));return 0
    if not options.synthetic_selfcheck:
        print(json.dumps({'mode':'INSPECT_ONLY','branches':len(manifest['branches']),'mediaExecution':'DISABLED'}));return 0
    print(json.dumps(dict(scope='E2C_FULL_DRIVER_REJECTED',status='NOT_RUN_E2C_SCOPE',executionAllowed=False,
                         reason='E2C permits one fixed G lifecycle diagnostic and bounded logic checks only.',
                         helpersStarted=0,mediaBytesRead=0,outputRootCreated=False,actualFullRun=False)))
    return 2
    need(not (BASE/'evidence/freeze-summary.json').exists(),'FROZEN_PACKAGE_READ_ONLY_NEW_AUTHORIZED_BATCH_REQUIRED')
    claim=None
    if not options.synthetic_observer_mock:
        from synthetic_admission import claim_actual
        claim=claim_actual(options.actual_run_id)
    else:need(options.actual_run_id is None,'MOCK_CANNOT_CONSUME_ACTUAL_RESERVATION')
    existing=[p for p in (BASE/'selfcheck').rglob('*') if p.is_file()]
    fixture_bytes=sum(p.stat().st_size for p in existing if p.name in ('L.bin','C.bin','Z.bin') or p.suffix=='.out')
    log_bytes=sum(p.stat().st_size for p in existing if not(p.name in ('L.bin','C.bin','Z.bin') or p.suffix=='.out'))
    need(fixture_bytes+135500<=2097152,'AGGREGATE_SYNTHETIC_LIMIT');need(log_bytes+800000<=4194304,'AGGREGATE_LOG_LIMIT')
    root=BASE/'selfcheck'/('check-'+time.strftime('%Y%m%dT%H%M%S'))
    fixtures(root);e=Engine(root,manifest,synthetic_observer_mock=options.synthetic_observer_mock);e.actual_regression_claim=claim;driver=Scenarios(e);error=None
    try:
        preflight(e)
        ordered=[r for r in manifest['branches'] if r['id'] not in ('P10-D','P10-C')]+[r for r in manifest['branches'] if r['id'] in ('P10-D','P10-C')]
        for row in ordered:
            e.begin(row['id']);driver.run(row['id']);e.flow.finish()
    except Exception:
        error=traceback.format_exc();print(error,file=sys.stderr)
    startup=e.completions.pending()
    if error is not None and (startup['lifecycle']!='RUNNING' or any(name not in e.channels for name in ('J','R')) or
                              any(not future.done() for future in e.pending.values()) or any(worker['unknown'] for worker in startup['workers'].values())):
        return emit_failure(e,error,timeout=1)
    try:
        cleanup=Cleanup(e);cleanup.run()
        report={'status':'PASS' if error is None else 'FAIL','error':error,'rows':e.results,'assertions':e.assertions}
        witness=cleanup.finish(report);print(json.dumps(witness,separators=(',',':')))
        return 0 if error is None else 1
    except Exception:
        cleanup_error=traceback.format_exc();print(cleanup_error,file=sys.stderr)
        return emit_failure(e,error or cleanup_error,timeout=1)

if __name__=='__main__':sys.exit(run())
