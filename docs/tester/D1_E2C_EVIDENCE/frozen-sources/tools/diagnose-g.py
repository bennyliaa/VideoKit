"""The one authorized E2C G lifecycle observation. Never creates Engine/Native/Channel."""
import argparse,ctypes,gc,hashlib,inspect,json,os,platform,sys,sysconfig,threading,time,weakref
from pathlib import Path
BASE=Path(__file__).resolve().parents[1];sys.path.insert(0,str(BASE/'src'))
from gcore import Ledger,Stop,need
from authority import PendingCell,SourceAuthority
from notifications import CompletionHub
from runtime_metrics import Win32MetricReader

STAGES=('ZERO_CELLS','ONE_LIVE','ONE_DRAINED','EIGHT_LIVE','EIGHT_DRAINED','TOOL_HISTORY_RELEASED')

def encode(value):return (json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
def fresh_file(path,value):
    data=encode(value)
    if len(data)>524288:raise Stop('DIAGNOSTIC_LOG_LIMIT')
    with path.open('xb',buffering=0) as stream:
        if stream.write(data)!=len(data):raise Stop('DIAGNOSTIC_WRITE_UNKNOWN')
        stream.flush();os.fsync(stream.fileno())
    return len(data)
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def run():
    if (BASE/'evidence/freeze-summary.json').exists():raise Stop('FROZEN_PACKAGE_READ_ONLY')
    started=time.monotonic();run_id=str(time.time_ns());end=started+60
    evidence=BASE/'evidence';evidence.mkdir(exist_ok=True)
    reservation=evidence/'g-lifecycle-reservation.json'
    fresh_file(reservation,dict(schema=1,scope='E2C_SINGLE_G_LIFECYCLE_RESERVATION',runId=run_id,pid=os.getpid(),
        maximumDiagnosticG=1,stages=list(STAGES),maximumSamples=6,deadlineSeconds=60,realExecutionAllowed=False,
        helpersAllowed=False,actualFullAllowed=False,createdBeforeHubAndCells=True,forceGCAllowed=False))
    report=dict(schema=1,scope='E2C_SINGLE_G_LIFECYCLE_DIAGNOSTIC',runId=run_id,status='PENDING',
        actualOSMetrics=True,realExecutionAllowed=False,actualFullRun=False,helpersStarted=0,mediaBytesRead=0,
        forceGC=False,baselineReset=False,stageOrder=list(STAGES),stages=[],unknowns=[],cleanupErrors=[],
        sourceEvidence=[],synchronizationBackend=dict(exactCBackend='UNKNOWN',handleTypeCausality='UNKNOWN'))
    ledger=Ledger();reader=Win32MetricReader(ledger);hub=None;source=None
    history={};external=[];cell_refs=[];future_refs=[];closure_refs=[]
    releases=[];drains=[];callbacks=[];identity=None
    # These imports/type/source observations happen before the sole zero baseline.
    import _thread,concurrent.futures
    py_thread=Path(threading.__file__);py_future=Path(concurrent.futures._base.__file__)
    report['runtime']=dict(version=sys.version,versionInfo=list(sys.version_info),implementation=platform.python_implementation(),
        executable=sys.executable,cacheTag=sys.implementation.cache_tag,compiler=platform.python_compiler(),
        pointerBits=ctypes.sizeof(ctypes.c_void_p)*8,Py_GIL_DISABLED=sysconfig.get_config_var('Py_GIL_DISABLED'),
        gilEnabled=sys._is_gil_enabled() if hasattr(sys,'_is_gil_enabled') else 'UNAVAILABLE',
        gcEnabled=gc.isenabled(),gcThresholds=list(gc.get_threshold()),forceGCInvocations=0)
    report['synchronizationBackend'].update(lockType=str(_thread.LockType),rlockFactory=str(_thread.RLock),
        lockModule=_thread.LockType.__module__,rlockModule=_thread.RLock.__module__,threadModuleOrigin=getattr(_thread.__spec__,'origin',None),
        threadingSource=dict(path=str(py_thread),sha256=sha(py_thread)),futureSource=dict(path=str(py_future),sha256=sha(py_future)),
        pythonConditionWaitUsesAllocateLock='_allocate_lock()' in inspect.getsource(threading.Condition.wait),
        limitation='Local Python source and concrete built-in types prove Python-level synchronization objects only. Exact compiled C primitive and per-object OS handle attribution are not proven.')
    baseline_dir=BASE/'artifacts/diagnostic-source-before';baseline_dir.mkdir(parents=True,exist_ok=False)
    for name in ('authority.py','notifications.py','gengine.py','phases.py'):
        original=BASE/'src'/name;copy=baseline_dir/name;copy.write_bytes(original.read_bytes())
        report['sourceEvidence'].append(dict(path='src/'+name,sha256=sha(original),preservedPath=copy.relative_to(BASE).as_posix()))
    def deadline():
        if time.monotonic()>end:raise Stop('G_LIFECYCLE_60_SECOND_DECISION_BOUND')
    def references():
        live=[value for ref in cell_refs if (value:=ref()) is not None]
        return dict(toolHistoryCells=len(history),externalFutures=len(external),weakCellsAlive=len(live),
            weakFuturesAlive=sum(r() is not None for r in future_refs),weakClosuresAlive=sum(r() is not None for r in closure_refs),
            releasedAlive=sum(c.released for c in live),nativeDoneAlive=sum(c.native_done for c in live),
            futureCellBackrefs=sum(getattr(c.response,'cell',None) is c for c in live),
            releaseClosureRetained=sum(c.release is not None for c in live),drainClosureRetained=sum(c.on_drain is not None for c in live),
            completedCallbackSlots=sum(len(c.response._done_callbacks) for c in live if c.notification_done),
            authorityRegistered=len(source.cells) if source is not None else 0,
            externalFirstFutureDone=external[0].done() if external else None,
            externalFirstFutureCellAlive=external[0].cell is not None if external else None,
            ioFutureScope='NOT_INSTANTIATED_NO_ENGINE_NO_NATIVE_IO; static Engine.io_call evidence preserved',
            gcCounts=list(gc.get_count()))
    def sample(stage):
        deadline();index=len(report['stages']);need(stage==STAGES[index],'FIXED_STAGE_ORDER')
        fresh_file(evidence/('g-lifecycle-entered-'+str(index)+'.json'),dict(runId=run_id,stage=stage,pid=os.getpid(),state='ORIGINAL_QUERY_ENTERED'))
        observed=time.monotonic();value=reader.read_cycle({'G':identity})['G'];returned=time.monotonic()
        limits=dict(threads=16,handles=256,workingSetBytes=268435456,privateBytes=268435456)
        base=report['stages'][0]['metrics'] if report['stages'] else value
        delta_limits=dict(threads=12,handles=64,workingSetBytes=134217728,privateBytes=134217728)
        metrics={key:value[key] for key in limits};delta={key:value[key]-base[key] for key in limits}
        reasons=[key+':ABSOLUTE' for key in limits if value[key]>limits[key]]+[key+':DELTA' for key in limits if delta[key]>delta_limits[key]]
        record=dict(stage=stage,identity=identity,metrics=metrics,deltaFromOriginalZero=delta,
            originalCreationValidated=True,sampleDurationSeconds=returned-observed,elapsedSeconds=returned-started,
            sampleDeadlineSeconds=.1,sampleDeadlineMet=returned-observed<=.1,
            approvedLimitExceedances=reasons,observerFacts=reader.facts(),references=references(),
            hub=hub.pending(),releaseCount=len(releases),drainCount=len(drains),callbackCount=len(callbacks))
        fresh_file(evidence/('g-lifecycle-stage-'+str(index)+'.json'),record)
        report['stages'].append(record);deadline()
        if returned-observed>.1:raise Stop('SAMPLE_DEADLINE_EXCEEDED_AFTER_RETURN')
    def make_cell(index):
        operation='G-CELL-'+str(index);binding=source.binding(state,'v1','consumer')
        source.admit(state,binding,operation);state['commands'][operation]={'status':'PENDING'}
        ledger.buffers+=1;ledger.buffer_peak=max(ledger.buffer_peak,ledger.buffers)
        def release():
            ledger.buffers-=1;releases.append(operation)
        def drained():
            source.drain(state,operation)
            error=cell.response.exception()
            state['commands'][operation].update(status='DONE',error=str(error) if error else '')
            drains.append(operation)
        cell=PendingCell(operation,binding,release,drained,hub=hub,authority=source,state=state)
        cell.response.add_done_callback(lambda future,operation=operation:callbacks.append(operation))
        history[operation]=cell;cell_refs.append(weakref.ref(cell));future_refs.append(weakref.ref(cell.response))
        closure_refs.extend((weakref.ref(release),weakref.ref(drained)))
        return cell
    def finish_cells(keys):
        for operation in keys:
            cell=history[operation];cell.complete(dict(operation=operation,value='SELF_OWNED_LOGIC_ONLY'));cell.gate(timeout=1)
        hub.drain(timeout=1)
        for operation in keys:
            cell=history[operation]
            need(cell.drained.is_set() and cell.released and cell.native_done and cell.gated and cell.notification_done,'ORIGINAL_DRAIN_NOT_PROVEN')
        need(hub.pending()['cells']==0,'NOTIFIER_NOT_RETURNED')
    try:
        identity=reader.capture_identity(os.getpid(),'E2C-G-'+run_id)
        report['identity']=identity
        hub=CompletionHub(ledger,max_cells=8,callback_timeout=.5).start()
        source=SourceAuthority();state=dict(task='G-LIFECYCLE',versions={},ops={},objects={},commands={})
        source.reserve(state,'v1','consumer')
        sample('ZERO_CELLS')
        cell=make_cell(1);external.append(cell.response);del cell
        sample('ONE_LIVE')
        finish_cells(['G-CELL-1'])
        sample('ONE_DRAINED')
        for index in range(2,10):make_cell(index)
        sample('EIGHT_LIVE')
        finish_cells(['G-CELL-'+str(index) for index in range(2,10)])
        sample('EIGHT_DRAINED')
        history.clear()
        # The externally owned first response deliberately survives this point.
        sample('TOOL_HISTORY_RELEASED')
        need(external[0].result(timeout=0)==dict(operation='G-CELL-1',value='SELF_OWNED_LOGIC_ONLY'),'EXTERNAL_FUTURE_CHANGED')
        report['externalFutureAfterToolHistoryRelease']='RESULT_STABLE_EXTERNAL_OWNERSHIP_RETAINED'
        report['status']='OBSERVED_FIXED_SIX_POINTS'
    except BaseException as error:
        report['status']='FAIL_OR_PENDING';report['unknowns'].append(dict(type=type(error).__name__,message=str(error)[:240]))
    finally:
        # Only operations already admitted above may finish. No new cell/query/retry.
        for cell in list(history.values()):
            try:
                if not cell.native_done:cell.complete(dict(operation=cell.operation,value='CLEANUP'))
                if not cell.gated:cell.gate(timeout=max(0,min(1,end-time.monotonic())))
            except BaseException as error:report['cleanupErrors'].append(type(error).__name__+':'+str(error)[:160])
        if hub is not None:
            try:hub.close(timeout=max(0,min(2,end-time.monotonic())))
            except BaseException as error:report['cleanupErrors'].append(type(error).__name__+':'+str(error)[:160])
            report['closure']=hub.pending()
        external.clear();history.clear()
        report['nativeReader']=reader.facts();report['remainingResources']=dict(ledger.live)
        report['ledgerPeak']=ledger.peak;report['bufferPeak']=ledger.buffer_peak;report['remainingBuffers']=ledger.buffers
        report['resourceReleases']=releases;report['sourceDrains']=drains;report['callbacksReturned']=callbacks
        report['elapsedSeconds']=time.monotonic()-started
        report['diagnosticGInstances']=1;report['metricSamples']=len(report['stages']);report['totalCellsCreated']=len(cell_refs)
        report['noInFlight']=bool(hub is not None and hub.pending()['closed'] and not hub.pending()['ownershipPending'] and not ledger.live and ledger.buffers==0 and not reader.reserved and not reader.close_unknown)
        report['allFinalReferencesReclaimed']='NOT_CLAIMED_NO_FORCED_GC_EXTERNAL_VALUES_RESPECTED'
        report['realRuntimeAdmission']='BLOCKED_G_HANDLES_369_GT_256_AND_DELTA_209_GT_64_E2B_HISTORY_PRESERVED'
        for _ in range(8):
            others=sum(p.stat().st_size for p in evidence.glob('g-lifecycle-*.json'))
            size=others+len(encode(report))
            if report.get('diagnosticArtifactBytes')==size:break
            report['diagnosticArtifactBytes']=size
        else:raise Stop('DIAGNOSTIC_SIZE_ACCOUNTING')
        need(size<=524288,'DIAGNOSTIC_LOG_LIMIT')
        report_path=evidence/('g-lifecycle-'+run_id+'.json');fresh_file(report_path,report)
        print(json.dumps(dict(evidence=str(report_path),status=report['status'],samples=len(report['stages']),noInFlight=report['noInFlight'],
            metrics=[dict(stage=row['stage'],handles=row['metrics']['handles'],references=row['references']) for row in report['stages']]),ensure_ascii=False))
    return 0 if report['status']=='OBSERVED_FIXED_SIX_POINTS' and report['noInFlight'] else 1

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--run',action='store_true');options=parser.parse_args()
    if options.run:raise SystemExit(run())
    print('INSPECT_ONLY: explicit --run required; one original G only')
