"""Bounded metadata-only T04 counterexamples. Root invokes this centrally."""
from __future__ import annotations
import copy
from gcore import *
from recovery import recover

def run_checks(root,manifest):
    root=Path(root).resolve();need(root.is_relative_to((BASE/'selfcheck').resolve()),'SYNTHETIC_ROOT_ONLY');root.mkdir(parents=True,exist_ok=False)
    checks=[]
    def check(ok,name):need(ok,'T04:'+name);checks.append(name)
    row=next(r for r in manifest['branches'] if r['queriesNew']>=2);task=row['task'];rid=row['id']
    source=next(r for r in manifest['branches'] if r['id']=='P01-N1')
    sink=next(r for r in manifest['branches'] if r['task'].startswith('T'))
    def usage(**changes):return dict(empty_usage(),**changes)
    def state(case,task,used=None,**fields):
        return dict(schema=3,batch=case.name,task=task,usage=copy.deepcopy(used or {}),commands={},objects={},versions={},ops={},q={},**fields)
    def prepare(name,specs,inventory=True):
        case=root/name;case.mkdir();store=Store(case,Ledger());pf=state(case,'PF',{'PF':usage(n=1,records=1)})
        if inventory:
            pf['inventory']={'PF':dict(batch=case.name,task='PF',admitted=True,minimumUsage=copy.deepcopy(pf['usage']),initialCommand='PF/n01')}
            for t,minima in specs.items():pf['inventory'][t]=dict(batch=case.name,task=t,admitted=True,minimumUsage=copy.deepcopy(minima),initialCommand=t+'/admitted')
        store.save('PF',pf);return case,store,pf
    def event(case,new=True,n=1):
        return dict(batch=case.name,task=task,row=rid,qid=rid+'/q'+str(n),new=new,view={'task':task,'state':'PENDING','seq':n})
    def statuses(result):return {x['status'] for x in result['unresolved'] if 'status' in x}
    def fenced(result,name):
        check(result['nativeCalls']==0 and result['newProcesses']==0 and result['writeCapability'] is False,name+'-no-effects')
        check(all(s['recovered'] and s['fenced'] and s['globalFence'] and s['confirmed'] is False for s in result['states'].values()),name+'-authority-fenced')
    # Both snapshots and a lower complete log disagree: maximum reservation wins.
    case,store,pf=prepare('high-snapshot-low-log',{task:{rid:usage(qn=1)}})
    store.save(task,state(case,task,{rid:usage(qn=2)}));store.save(task,state(case,task,{rid:usage(qn=1)}));store.event(rid,event(case),query=True)
    wrong=event(case,n=2);wrong['batch']='different-batch';store.event(rid,wrong,query=True)
    result=recover(case,manifest)
    check(result['rowUsage'][rid]['qn']==2,'high-snapshot-not-refunded-by-newer-low-snapshot-or-low-log')
    check(result['completeness']['status']=='UNKNOWN' and 'QUERY_LOG_BEHIND_RESERVED_SNAPSHOT' in statuses(result),'low-log-explicit-unknown')
    check('QUERY_LOG_UNTRUSTED_LINE' in statuses(result) and rid+'/q2' not in result['states'][task]['q'],'different-batch-query-log-not-imported')
    fenced(result,'snapshot-high')
    # A complete prefix is usable; an incomplete final line grants no refund.
    case,store,pf=prepare('partial-query-log',{task:{rid:usage(qn=2)}})
    store.save(task,state(case,task,{rid:usage(qn=2)}));store.event(rid,event(case),query=True)
    path=case/'events'/f'{rid}.q';tail=compact(event(case,n=2))[:41]
    with open(path,'ab',buffering=0) as file:check(file.write(tail)==len(tail),'partial-fixture-single-write')
    result=recover(case,manifest)
    check(result['rowUsage'][rid]['qn']==2 and 'QUERY_LOG_PARTIAL' in statuses(result),'partial-query-retains-two-reserved')
    check(len(result['states'][task]['q'])==1,'partial-query-cache-excludes-incomplete-result')
    fenced(result,'partial-query')
    # A missing admitted directory remains visible and retains reservation credit.
    minima={source['id']:usage(n=1,records=1)}
    case,store,pf=prepare('missing-admitted-shard',{source['task']:minima})
    result=recover(case,manifest)
    check(result['completeness']['missingAdmitted']==[source['task']] and 'ADMITTED_SHARD_MISSING' in statuses(result),'missing-admitted-shard-is-not-not-admitted')
    check(result['states'][source['task']]['unknownShard'] and result['rowUsage'][source['id']]==minima[source['id']],'missing-admitted-retains-minimum-credit')
    check(result['usage']['n']==2 and result['usage']['records']==2,'missing-shard-not-false-zero')
    fenced(result,'missing-admitted')
    # Without inventory no absent task may be declared never admitted.
    case,store,pf=prepare('missing-inventory',{},inventory=False)
    result=recover(case,manifest)
    check(result['completeness']['status']=='UNKNOWN' and not result['completeness']['inventoryKnown'],'absent-inventory-batch-unknown')
    check(not result['completeness']['notAdmitted'] and 'ADMISSION_INVENTORY_UNKNOWN' in statuses(result),'absent-inventory-no-zero-assumption')
    fenced(result,'no-inventory')
    # GC is one shared cumulative row, not separate additive shard credits.
    case,store,pf=prepare('gc-cross-shard-max',{source['task']:{},sink['task']:{}})
    pf['usage']['GC']=usage(n=31);store.save('PF',pf)
    store.save(source['task'],state(case,source['task'],{'GC':usage(n=9)}))
    store.save(sink['task'],state(case,sink['task'],{'GC':usage(n=29)}))
    result=recover(case,manifest)
    check(result['rowUsage']['GC']['n']==31 and result['usage']['n']==32,'gc-cross-shard-monotonic-max-not-sum')
    check(result['usageExact'] and result['completeness']['status']=='COMPLETE','gc-complete-metadata-exact')
    fenced(result,'gc')
    # Resource identities stay unresolved; no journal value becomes an OS handle.
    case,store,pf=prepare('retained-resource',{source['task']:minima})
    live=state(case,source['task'],minima);live['objects']['h']={'owner':'old-instance','disposition':'UNKNOWN','rawHandle':424242,'object':'object-id','ticket':'ticket-id'}
    live['commands']['read']=dict(status='ADMITTED',effect={'kind':'READ','rawHandle':424242})
    store.save(source['task'],live);result=recover(case,manifest)
    check('rawHandle' not in result['states'][source['task']]['objects']['h'],'recovery-does-not-import-persisted-raw-handle')
    check(any(x.get('rule')=='NO_NATIVE_HANDLE_RECONSTRUCTION' and x.get('resource')=='h' for x in result['unresolved']),'retained-resource-needs-original-owner-proof')
    check(any(x.get('rule')=='NO_REEXECUTION_OWNER_PROOF_REQUIRED' and x.get('command')=='read' for x in result['unresolved']),'admitted-effect-not-reexecuted')
    fenced(result,'retained-resource')
    # A complete identity-bound log can raise a stale snapshot's query minimum.
    case,store,pf=prepare('complete-log-ahead',{task:{}})
    store.save(task,state(case,task,{rid:usage()}));store.event(rid,event(case),query=True)
    result=recover(case,manifest)
    check(result['rowUsage'][rid]['qn']==1 and result['usageExact'],'complete-identity-log-raises-snapshot-minimum')
    check(result['states'][task]['q'][rid+'/q1']['task']==task,'identity-bound-cache-restored')
    fenced(result,'complete-log')
    sizes=sum(p.stat().st_size for p in root.rglob('*') if p.is_file())
    check(sizes<=131072,'all-targeted-metadata-within-128KiB')
    return dict(scope='T04_METADATA_ONLY_NEGATIVE_CHECKS',status='PASS',assertions=len(checks),checks=checks,metadataBytes=sizes,newHelpers=0,mediaRead=False)
