"""Update copied accepted allocations to the implemented E1E entry points."""
import argparse, hashlib, json
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]
ENTRIES={'res':'res','g+':'guard','h+':'open_j','r+':'ref','seal':'seal','end':'end','cancel':'cancel_source','cancelO':'cancel_output','ch':'close_j','cr':'close_r','cg':'close_guard','retry':'close_j','gate':'gate','version':'version','grant':'grant','allocA':'alloc','dupB':'dup','sendB':'send','takeB':'take','claim':'claim','flushB':'flush','ca':'close_a','cb':'close_b','v+':'vopen','cv':'vclose','takeover':'takeover','ready':'ready','abort':'cancel_output'}
def generate():
    assert not (BASE/'evidence/freeze-summary.json').exists(),'FROZEN_PACKAGE_READ_ONLY_NEW_AUTHORIZED_BATCH_REQUIRED'
    manifest=json.loads((BASE/'upstream-e1d/branches.json').read_text(encoding='utf-8-sig'))
    manifest.update(schema=3,scope='E1E_IMPLEMENTATION_PENDING_INDEPENDENT_REVIEW',missingFullDriver=False,experimentEnabled=False)
    for row in manifest['branches']:
        row.update(entry='src/scenarios.py:Scenarios.run',implementation='CONCRETE_SYNTHETIC_DRIVER',executionStatus='REAL_MEDIA_NOT_RUN',blockers=['Independent review and separate media-experiment authorization required'])
        for op in row['operations']:
            name=next((x for x in sorted(ENTRIES,key=len,reverse=True) if op['token'].startswith(x)),None)
            op['entry']='src/gengine.py:Ops.'+ENTRIES[name] if name else 'src/gengine.py:Flow.n + src/scenarios.py:Scenarios.run'
            op['binding']='ADMISSION_JOURNAL_THEN_NATIVE_OR_AUTHORITY'
    manifest['executionOrder']=[r['id'] for r in manifest['branches'] if r['id'] not in ('P10-D','P10-C')]+['P10-D','P10-C']
    for phase,rows in manifest['phases'].items():
        for row in rows:row.update(implementation='src/phases.py:'+('preflight' if phase=='PF' else 'Cleanup.finish' if row['id']=='GC/n32' else 'Cleanup.run'))
    for rows in manifest['phases'].values():
        for row in rows:
            if row['id']=='PF/n01':row['boundedEffects']='唯一PF记录；日志/journal仅元数据不计媒体目标；在同一setup内启动固定notify/deadline两个G本地线程，各占一个worker credit。E1E逐worker保存预留、对象创建、start返回/异常和原线程身份；部分启动失败仅在该内部步骤有界收尾，从未启动以THREAD_NOT_STARTED_PROVEN证明归还，真实启动须原实例join才归还；未知保留PENDING并停止接纳。无新增N/RPC/事务'
            if row['id']=='GC/n31':row['boundedEffects']='每事务journal/reader应已关；异常所有权未知保持PENDING。正常或异常启动状态均逐worker有界收尾；真实启动线程须原实例join后归还credit，从未启动须THREAD_NOT_STARTED_PROVEN证明，未知不伪造退出。仅复用本控制步骤及异常GC收尾，不增加N/RPC/事务'
    manifest['dataBinding']='src/scenarios.py -> Ops.read_j/read_r/write/seek_write -> Flow.data -> Engine.remote -> JavaHelper/RHost'
    manifest['recoveryBinding']='J independent bounded record read + Engine.recovery_callback; src/recovery.py whole-authority read-only reconstruction'
    manifest['fixes']={
        'T01':{'entry':'authority.py:PendingCell/complete_source_response + gengine.py:Engine.private_cell/Ops.read_zero','checks':'authority_checks.py + P02-ZERO/P08-LATEOPEN/P09-CANCEL/P09-TIMEOUT'},
        'T02':{'entry':'authority.py:SourceAuthority.admit/end/cancel + gengine.py:Ops.open_j/read_j','checks':'authority_checks.py exact binding and deterministic lifecycle/admission races'},
        'T03':{'entry':'authority.py:capture_ready_request/validate_ready_request + gengine.py:Ops.ready/takeover','checks':'authority_checks.py + Q07-TAKEFIRST real captured e1 request'},
        'T04':{'entry':'gengine.py:Flow.transaction PF inventory + recovery.py:recover','checks':'recovery_checks.py monotonic reservations/missing shard/GC max/no raw reconstruction'},
        'T05':{'entry':'gcore.py:Store.exact_write/ensure_writable + phases.py','checks':'metadata_checks.py one bounded short return and real Flow downstream0'}}
    manifest['completionFixes']={
        'C01':{'entry':'authority.py:SourceAuthority._delivery_locked/_decide_delivery_locked/complete/gate',
               'checks':'completion_checks.py single seal, both winning orders, ordinary/held open/read, fence and exact binding',
               'readPolicy':'Undecided admitted read is discarded if seal/fence/end/cancel wins. Original immutable delivery decision is never readmitted or reversed.'},
        'C02':{'entry':'notifications.py:CompletionHub/DeliveryFuture + authority.py:PendingCell._post/_publish_outside_locks/_release_ready',
               'checks':'completion_checks.py real add_done_callback lock probes across complete/gate/end/cancel/deadline/GC, controlled slow callback, bounded credits and notification lag',
               'linearization':'One source/cell-locked outcome; asynchronous Future publication and callbacks run outside every application lock; resource release waits native+gate+actual callbacks.'}}
    manifest['startupFixes']={'D01':{
        'entry':'notifications.py:CompletionHub.start/close/pending + controller.py startup failure cleanup',
        'checks':'startup_checks.py deterministic self-owned worker factory failures, per-worker identity/proof/credit and bounded cleanup',
        'rule':'Track each worker reservation/object/start result independently. Return only never-started credit by worker-only THREAD_NOT_STARTED_PROVEN proof, or original started worker credit after actual join. Any unknown remains PENDING and blocks new admission.',
        'budgetMapping':'Worker failure cleanup is internal to PF/n01 and existing exceptional GC cleanup. No new N/RPC, journal transaction, replacement worker, or retry run.'}}
    manifest['callbackBudget']={'fixedWorkers':2,'notifierWorkers':1,'deadlineWorkers':1,'maxLiveCells':8,'maxQueuedPlusActiveNotifications':8,'maxCallbacksPerCell':4,
        'registrationWindow':'Before outcome decision only; later registration is refused without inline callback invocation.',
        'workerCredits':'Two G-local worker leases. Each returns only by original worker actual join or worker-only THREAD_NOT_STARTED_PROVEN on failed startup; unknown remains reserved. Active notification retains capacity credit through notifier return.',
        'pendingRule':'Callback or publication uncertainty stops new admission and preserves ownership; no forced interruption or early resource release.',
        'internalSteps':[{'within':'PF/n01','entry':'phases.py:preflight -> CompletionHub.start','operation':'Start two fixed G-local notification/deadline workers; no N/RPC or journal transaction added.'},
                         {'within':'GC/n31','entry':'phases.py:Cleanup.run -> CompletionHub.close','operation':'Bounded actual worker joins before worker-credit release; no N/RPC or journal transaction added.'},
                         {'within':'PF/n01 or existing exceptional GC cleanup','entry':'notifications.py:CompletionHub.start/close + controller.py','operation':'On partial startup failure inspect each original worker; prove never-started or actual join individually; unknown ownership stays PENDING. No extra N/RPC/journal transaction or replacement worker.'}]}
    manifest['journalTransactionChange']='First task admission writes its PF inventory instead of task slot, completion writes task slot: at most two. No additional N/RPC. Pending completion uses original admission plus existing gate transactions.'
    manifest['profile']={'synthetic':{'L':131072,'C':4096,'Z':0,'boundary':65536},'realMedia':'DISABLED; no physical version/durability/media-boundary claim'}
    assert len(manifest['branches'])==61 and sum(r['nonquery'] for r in manifest['branches'])+48==351
    (BASE/'manifest/branches.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'branches':61,'controls':452,'mode':'IMPLEMENTATION_MAPPING_ONLY'}))
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--generate',action='store_true');args=parser.parse_args()
    if args.generate:generate()
    else:print('INSPECT_ONLY: explicit --generate required')
