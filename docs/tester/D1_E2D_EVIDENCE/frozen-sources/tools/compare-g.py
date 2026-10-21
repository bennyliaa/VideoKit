"""E2D's one authorized post-fix six-point observation; immutable E2C production."""
import argparse,ctypes,gc,hashlib,json,os,platform,sys,threading,time,weakref
from pathlib import Path
from types import SimpleNamespace
BASE=Path(__file__).resolve().parents[1];sys.path.insert(0,str(BASE/'src'))
from gcore import Ledger,Stop,need
from authority import SourceAuthority
from gengine import Engine
from notifications import CompletionHub
from runtime_metrics import Win32MetricReader

STAGES=('ZERO_CELLS','ONE_LIVE','ONE_DRAINED_COMPACTED','EIGHT_LIVE','EIGHT_DRAINED_COMPACTED','PROBE_AUDIT_COPY_RELEASED')
FREEZE='bccacb2e98b1f4a4d3017fc8efb9bd0f047e58d91e7c910303fff40eb3896179'
ARCHIVE='035263006cbaa99837656bb2b66045a3f5c6181ab8af8c8fe3f5bcf5ba3e5934'

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def encode(value):return (json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
def fresh(path,value):
    data=encode(value);need(len(data)<=524288,'DIAGNOSTIC_FILE_LIMIT')
    with path.open('xb',buffering=0) as stream:
        need(stream.write(data)==len(data),'DIAGNOSTIC_WRITE_UNKNOWN');stream.flush();os.fsync(stream.fileno())
    return len(data)

def binding():
    prior=BASE/'upstream-e2c';need(sha(prior/'freeze-summary.json')==FREEZE,'E2C_FREEZE_CHANGED')
    need(sha(prior/'E2C-source.zip')==ARCHIVE,'E2C_SOURCE_ARCHIVE_CHANGED')
    frozen=json.loads((prior/'freeze-summary.json').read_text(encoding='utf-8'))
    source_record=next(row for row in frozen['files'] if row['path']=='docs/coder/d1e2c/evidence/source-manifest.json')
    need((prior/'source-manifest.json').stat().st_size==source_record['bytes'] and sha(prior/'source-manifest.json')==source_record['sha256'],'E2C_SOURCE_MANIFEST_CHANGED')
    manifest=json.loads((prior/'source-manifest.json').read_text(encoding='utf-8'))
    records=[]
    prefix='docs/coder/d1e2c/'
    for row in manifest['files']:
        relative=row['path'].removeprefix(prefix)
        if relative.startswith(('src/','manifest/','profiles/')):
            path=BASE/relative;need(path.stat().st_size==row['bytes'] and sha(path)==row['sha256'],'E2C_PRODUCTION_BINDING_CHANGED:'+relative)
            records.append(dict(path=relative,bytes=row['bytes'],sha256=row['sha256']))
    need(len([r for r in records if r['path'].startswith('src/')])==32,'E2C_SOURCE_SET_INCOMPLETE')
    artifacts=[]
    for row in frozen['files']:
        relative=row['path'].removeprefix(prefix)
        if relative=='artifacts/E2C.dll' or relative.startswith('artifacts/java/'):
            path=BASE/relative;need(path.stat().st_size==row['bytes'] and sha(path)==row['sha256'],'E2C_COMPILED_ARTIFACT_CHANGED')
            artifacts.append(dict(path=relative,bytes=row['bytes'],sha256=row['sha256']))
    return dict(schema=1,scope='E2D_EXACT_E2C_PRODUCTION_BINDING',upstreamFreezeSha256=FREEZE,
                upstreamSourceZipSha256=ARCHIVE,files=records,compiledArtifacts=artifacts,
                productionCodeChanged=False,newCompilations=0,newTargetedRuns=0)

class Probe:
    private_cell=Engine.private_cell
    compact_cells=Engine.compact_cells
    cell_facts=Engine.cell_facts
    def __init__(self,ledger):
        self.lock=threading.RLock();self.ledger=ledger;self.source=SourceAuthority(self.lock)
        self.cells={};self.cell_history=();self.cell_total=0;self.cell_peak=0;self._cell_owner_thread=threading.get_ident()
        self.row='probe';self.budget=SimpleNamespace(rows={'probe':{'buffers':8}})
        # Retain the original Hub even when start partially fails.
        self.completions=CompletionHub(ledger,max_cells=8,callback_timeout=.5)
        self.state=dict(task='G-POSTFIX',versions={},ops={},objects={},commands={})
        self.binding=self.source.reserve(self.state,'v1','consumer');self.audit_copy=[]

def run():
    need(not (BASE/'evidence/freeze-summary.json').exists(),'FROZEN_PACKAGE_READ_ONLY')
    started=time.monotonic();end=started+60;run_id=str(time.time_ns());evidence=BASE/'evidence'
    fresh(evidence/'g-comparison-reservation.json',dict(schema=1,scope='E2D_SINGLE_G_RESERVATION',runId=run_id,pid=os.getpid(),
          maximumG=1,maximumMetricSamples=6,stages=list(STAGES),createdBeforeHubAndCells=True,deadlineSeconds=60,
          realExecutionAllowed=False,actualFullAllowed=False,forceGCAllowed=False,upstreamFreezeSha256=FREEZE))
    report=dict(schema=1,scope='E2D_SINGLE_POSTFIX_G_COMPARISON',runId=run_id,status='PENDING',stageOrder=list(STAGES),
        stages=[],errors=[],cleanupErrors=[],realExecutionAllowed=False,actualFullRun=False,helpersStarted=0,mediaBytesRead=0,
        probeSourceSha256=sha(Path(__file__)),
        productionCodeChanged=False,forceGC=False,gcDisabled=False,baselineReset=False,diagnosticGInstances=1,
        costs=dict(original452Charged=False,metricSamples=0,identityQueries=0,HubWorkers=2,privateCellCreations=0,
                   sourceAdmissions=0,nativeLogicCompletions=0,gates=0,futureConsumptions=0,callbacksReturned=0,
                   normalCompactionCalls=0,cleanupCompactionCalls=0,cleanupNativeLogicCompletions=0,
                   cleanupGates=0,cleanupFutureConsumptions=0,fixtureBytes=0,newRPC=0,newDriverControls=0))
    ledger=None;reader=None;probe=None;identity=None;external=[];expected_first=[]
    cell_refs=[];future_refs=[];closure_refs=[];callback_operations=[];consumption_proofs=[]
    def deadline():need(time.monotonic()<=end,'E2D_60_SECOND_DECISION_BOUND')
    def remaining(cap):return max(0,min(cap,end-time.monotonic()))
    def create(index):
        operation='E2D-CELL-'+str(index)
        probe.source.admit(probe.state,probe.binding,operation);report['costs']['sourceAdmissions']+=1
        probe.state['commands'][operation]={'status':'ADMITTED'}
        cell=probe.private_cell(probe.state,operation,probe.binding,'read',buffer=True)
        report['costs']['privateCellCreations']+=1
        cell.response.add_done_callback(lambda future,operation=operation:callback_operations.append(operation))
        cell_refs.append(weakref.ref(cell));future_refs.append(weakref.ref(cell.response))
        closure_refs.extend((weakref.ref(cell.release),weakref.ref(cell.on_drain)))
        # Only the first external Future escapes. No caller receives a cell.
        if index==1:external.append(cell.response)
    def consume(operation):
        # This entire caller frame returns BEFORE compact_cells is invoked.
        cell=probe.cells[operation];value=dict(operation=operation,value='SELF_OWNED_LOGIC_ONLY')
        cell.complete(value);report['costs']['nativeLogicCompletions']+=1
        cell.gate(timeout=remaining(1));report['costs']['gates']+=1
        result=cell.response.result(timeout=remaining(1));report['costs']['futureConsumptions']+=1
        need(result is value,'ORIGINAL_FUTURE_RESULT_CHANGED')
        if operation=='E2D-CELL-1':expected_first.append(value)
        with probe.completions.condition:
            need(probe.completions.condition.wait_for(lambda:probe.completions.cell_quiescent(cell),timeout=remaining(1)),
                 'ORIGINAL_NOTIFIER_OR_MONITOR_NOT_RETURNED')
        need(cell.drained.is_set() and cell.native_done and cell.gated and cell.notification_done and cell.released,'ORIGINAL_CELL_NOT_DRAINED')
        need(probe.state['ops'][operation]['done'] and probe.state['ops'][operation]['nativeReturned'],'SOURCE_NOT_DRAINED')
        return dict(operation=operation,callerConsumedOriginalFuture=True,sourceDone=True,nativeReturned=True,
                    gateOpened=True,callbackReturned=True,perCellHubQuiescent=True)
    def drain_compact(keys):
        for operation in keys:consumption_proofs.append(consume(operation))
        # consume frames/lambda predicates and their cell locals are gone here.
        count=probe.compact_cells();report['costs']['normalCompactionCalls']+=1
        need(count==len(keys),'PRODUCTION_COMPACTION_INCOMPLETE')
        probe.audit_copy=list(probe.cell_history)
    def references():
        # Scalars only escape; no weak referent remains held during OS sampling.
        cells=futures=closures=backrefs=release_edges=drain_edges=0
        for ref in cell_refs:
            value=ref()
            if value is not None:
                cells+=1;backrefs+=int(getattr(value.response,'cell',None) is value)
                release_edges+=int(value.release is not None);drain_edges+=int(value.on_drain is not None)
        for ref in future_refs:futures+=int(ref() is not None)
        for ref in closure_refs:closures+=int(ref() is not None)
        facts=probe.cell_facts(include_history=True)
        return dict(weakCellsAlive=cells,weakFuturesAlive=futures,weakClosuresAlive=closures,
            futureCellBackrefs=backrefs,releaseClosuresRetained=release_edges,drainClosuresRetained=drain_edges,
            externalFutures=len(external),externalFirstFutureDone=external[0].done() if external else None,
            externalFirstFutureCellDetached=external[0].cell is None if external else None,
            externalFirstOriginalResultStable=bool(expected_first and external[0].result(timeout=0) is expected_first[0]) if external and external[0].done() else None,
            probeAuditCopyCount=len(probe.audit_copy),production=facts,authorityRegistered=len(probe.source.cells),gcCounts=list(gc.get_count()))
    def sample(stage):
        deadline();index=len(report['stages']);need(index<6 and stage==STAGES[index],'FIXED_SIX_POINT_ORDER')
        refs=references() # no cell object survives this function call
        fresh(evidence/('g-comparison-entered-'+str(index)+'.json'),dict(runId=run_id,stage=stage,identity=identity,state='ORIGINAL_QUERY_ENTERED'))
        entered=time.monotonic();value=reader.read_cycle({'G':identity})['G'];returned=time.monotonic()
        metrics={key:value[key] for key in ('threads','handles','workingSetBytes','privateBytes')}
        base=report['stages'][0]['metrics'] if report['stages'] else metrics
        delta={key:metrics[key]-base[key] for key in metrics}
        absolute=dict(threads=16,handles=256,workingSetBytes=268435456,privateBytes=268435456)
        increments=dict(threads=12,handles=64,workingSetBytes=134217728,privateBytes=134217728)
        reasons=[key+':ABSOLUTE' for key in metrics if metrics[key]>absolute[key]]+[key+':DELTA' for key in metrics if delta[key]>increments[key]]
        row=dict(stage=stage,identity=identity,metrics=metrics,deltaFromOriginalZero=delta,limitExceedances=reasons,
                 sampleDurationSeconds=returned-entered,sampleDeadlineSeconds=.1,sampleDeadlineMet=returned-entered<=.1,
                 elapsedSeconds=returned-started,referencesBeforeOSQuery=refs,observerFacts=reader.facts(),hub=probe.completions.pending(),
                 callbacksReturned=len(callback_operations),consumedOriginalFutures=len(consumption_proofs))
        fresh(evidence/('g-comparison-stage-'+str(index)+'.json'),row);report['stages'].append(row)
        report['costs']['metricSamples']=len(report['stages']);deadline()
        if reasons:raise Stop('G_LIMIT_EXCEEDED:'+','.join(reasons))
        need(returned-entered<=.1,'SAMPLE_DEADLINE_EXCEEDED_AFTER_RETURN')
    try:
        bound=binding();fresh(evidence/'production-binding.json',bound);report['productionBindingEvidence']='evidence/production-binding.json'
        need(Probe.private_cell is Engine.private_cell and Probe.compact_cells is Engine.compact_cells and Probe.cell_facts is Engine.cell_facts,'ORIGINAL_PRODUCTION_METHOD_BINDING_REQUIRED')
        report['productionMethodBindings']={name:getattr(Probe,name).__module__+'.'+getattr(Probe,name).__qualname__ for name in ('private_cell','compact_cells','cell_facts')}
        need(sys.version_info[:3]==(3,12,14) and ctypes.sizeof(ctypes.c_void_p)==8,'APPROVED_CPYTHON_RUNTIME_MISMATCH')
        report['runtime']=dict(version=sys.version,versionInfo=list(sys.version_info),implementation=platform.python_implementation(),
              executable=sys.executable,pointerBits=64,compiler=platform.python_compiler(),gcEnabled=gc.isenabled(),gcThresholds=list(gc.get_threshold()),
              runtimeDllSha256=sha(Path(sys.executable).parent/'python312.dll'),forceGCInvocations=0)
        need(report['runtime']['runtimeDllSha256']=='2b6fffde96cf24a57fca642aaefd5788816ab5ef8624ea63b722cbceb94d49b1','ORIGINAL_RUNTIME_DLL_CHANGED')
        need(gc.isenabled() and gc.get_threshold()==(700,10,10),'ORIGINAL_GC_CONFIGURATION_CHANGED')
        ledger=Ledger();reader=Win32MetricReader(ledger);identity=reader.capture_identity(os.getpid(),'E2D-G-'+run_id)
        report['identity']=identity;report['costs']['identityQueries']=1
        probe=Probe(ledger);probe.completions.start()
        sample('ZERO_CELLS')
        create(1);sample('ONE_LIVE')
        drain_compact(['E2D-CELL-1']);sample('ONE_DRAINED_COMPACTED')
        for index in range(2,10):create(index)
        sample('EIGHT_LIVE')
        drain_compact(['E2D-CELL-'+str(index) for index in range(2,10)]);sample('EIGHT_DRAINED_COMPACTED')
        probe.audit_copy.clear() # only a diagnostic copy; production history/total untouched
        need(probe.cell_total==len(probe.cell_history)==9 and not probe.cells,'PRODUCTION_HISTORY_MUST_NOT_BE_REFUNDED')
        sample('PROBE_AUDIT_COPY_RELEASED')
        report['status']='OBSERVED_POSTFIX_SIX_POINTS_WITHIN_LIMITS'
    except BaseException as error:
        report['status']='FAIL';report['errors'].append(dict(type=type(error).__name__,message=str(error)[:240]))
    finally:
        # No new sample/cell/retry. Existing private logic can finish for safe cleanup.
        if probe is not None:
            def clean(operation):
                cell=probe.cells[operation]
                if not cell.native_done:
                    cell.complete(dict(operation=operation,value='CLEANUP'));report['costs']['cleanupNativeLogicCompletions']+=1
                if not cell.gated:
                    cell.gate(timeout=remaining(1));report['costs']['cleanupGates']+=1
                cell.response.result(timeout=remaining(1));report['costs']['cleanupFutureConsumptions']+=1
                with probe.completions.condition:
                    need(probe.completions.condition.wait_for(lambda:probe.completions.cell_quiescent(cell),timeout=remaining(1)),'CLEANUP_CELL_PENDING')
            for operation in list(probe.cells):
                try:clean(operation)
                except BaseException as error:report['cleanupErrors'].append(type(error).__name__+':'+str(error)[:160])
            if probe.cells:
                try:probe.compact_cells();report['costs']['cleanupCompactionCalls']+=1
                except BaseException as error:report['cleanupErrors'].append(type(error).__name__+':'+str(error)[:160])
            try:probe.completions.close(timeout=remaining(2))
            except BaseException as error:report['cleanupErrors'].append(type(error).__name__+':'+str(error)[:160])
            report['closure']=probe.completions.pending();report['finalProductionFacts']=probe.cell_facts(include_history=True)
            report['externalFutureHeldThroughClosure']=len(external)==1
            report['externalFirstOriginalResultStableAfterClosure']=bool(expected_first and external[0].result(timeout=0) is expected_first[0]) if external and external[0].done() else False
        report['costs']['callbacksReturned']=len(callback_operations);report['consumptionProofs']=consumption_proofs
        report['nativeReader']=reader.facts() if reader is not None else None
        report['remainingResources']=dict(ledger.live) if ledger is not None else {}
        report['ledgerPeak']=ledger.peak if ledger is not None else 0;report['bufferPeak']=ledger.buffer_peak if ledger is not None else 0
        report['remainingBuffers']=ledger.buffers if ledger is not None else 0;report['elapsedSeconds']=time.monotonic()-started
        hub_done=probe is None or (probe.completions.pending()['closed'] and not probe.completions.pending()['ownershipPending'])
        reader_done=reader is None or (not reader.reserved and not reader.close_unknown)
        report['noInFlight']=bool(hub_done and reader_done and not report['remainingResources'] and not report['remainingBuffers'])
        if not report['noInFlight']:report['status']='PENDING'
        elif report['cleanupErrors'] or report['elapsedSeconds']>60:report['status']='FAIL'
        report['exactCompiledSynchronizationBackend']='UNKNOWN';report['handleTypeCausality']='UNKNOWN'
        report['fullEngineRuntimeAdmission']='NOT_PROVEN_OLD_G369_AND_R519_FAILURES_PRESERVED'
        report['externalObjectReclamationRequired']=False
        for _ in range(8):
            others=sum(p.stat().st_size for p in evidence.glob('g-comparison-*.json'))
            total=others+len(encode(report))
            if report.get('diagnosticArtifactBytesAtReport')==total:break
            report['diagnosticArtifactBytesAtReport']=total
        else:raise Stop('DIAGNOSTIC_BYTE_ACCOUNTING')
        need(total<=524288,'DIAGNOSTIC_LOG_LIMIT')
        path=evidence/('g-comparison-'+run_id+'.json');fresh(path,report)
        print(json.dumps(dict(evidence=str(path),status=report['status'],samples=len(report['stages']),noInFlight=report['noInFlight'],
              stages=[dict(stage=r['stage'],handles=r['metrics']['handles'],production={k:v for k,v in r['referencesBeforeOSQuery']['production'].items() if k!='history'},
                           weakCellsAlive=r['referencesBeforeOSQuery']['weakCellsAlive'],weakFuturesAlive=r['referencesBeforeOSQuery']['weakFuturesAlive']) for r in report['stages']]),ensure_ascii=False))
    return 0 if report['status']=='OBSERVED_POSTFIX_SIX_POINTS_WITHIN_LIMITS' else 2

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--run',action='store_true');options=parser.parse_args()
    if options.run:raise SystemExit(run())
    print('INSPECT_ONLY: explicit --run required; one G, six samples, no full/real execution')
