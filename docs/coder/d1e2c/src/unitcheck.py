"""Additional state/budget/recovery checks, explicitly separate from media evidence."""
import copy, json, tempfile
from gcore import *
from gengine import Engine
from recovery import recover

def run():
    need(not (BASE/'evidence/freeze-summary.json').exists(),'FROZEN_PACKAGE_READ_ONLY_NEW_AUTHORIZED_BATCH_REQUIRED')
    manifest=json.loads((BASE/'manifest/branches.json').read_text(encoding='utf-8-sig'));passed=[]
    def check(ok,name):need(ok,'UNIT:'+name);passed.append(name)
    def rejects(fn,reason):
        try:fn()
        except Refused as ex:check(str(ex)==reason,'reject-'+reason);return
        raise AssertionError(reason)
    b=Budget(manifest);b.begin('P01-N1');b.charge('P01-N1',ib=131072,ic=2,n=4,records=1)
    before=copy.deepcopy(b.globalused);rejects(lambda:b.charge('P01-N1',ib=1),'BUDGET_STOP:ib');check(b.globalused==before,'failed-reservation-does-not-change-any-scope')
    rejects(lambda:b.charge('P01-N1',n=-1),'BUDGET_STOP:n');check(b.taskused['S01']==b.used['P01-N1'],'task-budget-equals-first-row')
    b.ends['P01-N1']=time.monotonic()-1;rejects(lambda:b.charge('P01-N1',n=0),'ROW_DEADLINE_STOP')
    invalid=empty_usage();invalid['n']=5;rejects(lambda:Budget(manifest).restore([{'usage':{'P01-N1':invalid}}]),'RECOVERED_ROW_OVERFLOW')
    early=empty_usage();early['n']=3;late=empty_usage();late['n']=9;merged=Budget(manifest);merged.restore([{'usage':{'GC':early}},{'usage':{'GC':late}}]);check(merged.globalused['n']==9,'cleanup-cross-shard-reservations-reconcile-by-monotonic-max')
    l=Ledger();row={'task':'S01','mediaHandles':6,'buffers':8}
    for i in range(6):l.acquire(str(i),'owner','media',row)
    rejects(lambda:l.acquire('overflow','owner','media',row),'MEDIA_HANDLE_LIMIT')
    rejects(lambda:l.release('0','UNPROVEN'),'INVALID_RELEASE_PROOF');check(len(l.live)==6,'invalid-proof-retains-every-reference')
    rejects(lambda:l.owner_exit('owner',{'exited':False,'instance':'owner'}),'OWNER_EXIT_NOT_PROVEN')
    l.owner_exit('owner',{'exited':True,'instance':'owner'});check(not l.live,'matching-actual-exit-fact-releases-only-owner')
    try:
        with l.buffer(row,'pending-owner'):raise Stop('pending')
    except Stop:pass
    check(l.buffers==1,'timeout-retains-buffer');l.owner_exit('pending-owner',{'exited':True,'instance':'pending-owner'});check(l.buffers==0,'exit-reconciles-pending-buffer')
    for i in range(24):l.acquire(str(i),'owner','pipe')
    rejects(lambda:l.acquire('overflow','owner','pipe'),'OS_HANDLE_LIMIT')
    root=BASE/'selfcheck'/('unit-'+time.strftime('%Y%m%dT%H%M%S'));root.mkdir(exist_ok=False)
    store=Store(root,Ledger());state={'schema':3,'batch':root.name,'task':'T01','usage':{},'q':{},'objects':{},'commands':{'uncertain':{'status':'ADMITTED','effect':{'kind':'WRITE','requested':1,'epoch':1}}}}
    store.save('T01',state);store.save('T01',state);check(store.load('T01')==state,'two-slot-read-reconstructs-whole-record')
    restored=recover(root,manifest);check(restored['writeCapability'] is False and restored['nativeCalls']==0 and restored['batchState']=='UNKNOWN' and any(x.get('command')=='uncertain' for x in restored['unresolved']),'admitted-effect-without-inventory-remains-unknown-without-reexecution')
    p=root/'T01/state0.slot';raw=p.read_bytes();p.write_bytes(raw[:100]+bytes([raw[100]^1])+raw[101:]);rejects(lambda:store.load('T01'),'JOURNAL_CORRUPT')
    check(not store.ledger.live,'all-metadata-handles-returned-after-corruption')
    e=Engine(root,manifest);e.begin('P01-N1');e.states['S01']=e.new_state('S01');rejects(lambda:e.remote('J','OPEN',['S01-H','C.bin']),'UNADMITTED_OR_REUSED_RPC');e.io.shutdown()
    return {'scope':'LOGICAL_NEGATIVE_CHECKS_ONLY','status':'PASS','assertions':len(passed),'checks':passed,'journalFileBytes':16384,'newHelpers':0}

if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--run',action='store_true');args=parser.parse_args()
    print(json.dumps(run() if args.run else {'mode':'INSPECT_ONLY'},separators=(',',':')))
