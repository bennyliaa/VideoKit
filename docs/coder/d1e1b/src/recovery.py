"""Fail-closed reconstruction. Never imports a raw handle or resumes an admitted effect."""
import copy
from gcore import *

def recover(root,manifest):
    root=root.resolve();need(root.is_relative_to((BASE/'selfcheck').resolve()),'SYNTHETIC_ROOT_ONLY')
    ledger=Ledger();store=Store(root,ledger);budget=Budget(manifest);states={};unresolved=[]
    for task in sorted({r['task'] for r in manifest['branches']}|{'PF'}):
        if not (root/task).exists():continue
        state=store.load(task);need(state.get('schema')==2 and state.get('batch')==root.name and state['task']==task,'RECOVERY_IDENTITY')
        rows=[r for r in manifest['branches'] if r['task']==task];cache=store.reload_queries(task,rows);state['q'].update(cache)
        for row in rows:
            path=root/'events'/f'{row["id"]}.q'
            if path.exists():
                events=[json.loads(x) for x in path.read_bytes().splitlines()]
                usage=state['usage'].setdefault(row['id'],empty_usage())
                usage['qn']=sum(bool(x['new']) for x in events);usage['qr']=sum(not x['new'] for x in events)
        for key,command in state['commands'].items():
            if command['status']!='DONE':
                unresolved.append({'task':task,'command':key,'status':command['status'],'effect':command.get('effect'),'rule':'NO_REEXECUTION_OWNER_PROOF_REQUIRED'})
        for key,resource in state['objects'].items():
            if resource['disposition'] not in {'CLOSED_PROVEN','RELEASED_BY_OWNER_EXIT'}:
                unresolved.append({'task':task,'resource':key,'owner':resource['owner'],'disposition':resource['disposition'],'rule':'NO_NATIVE_HANDLE_RECONSTRUCTION'})
        state.update(recovered=True,fenced=True,globalFence=True,confirmed=False)
        states[task]=state
    need(states,'NO_JOURNALS');budget.restore(states.values())
    return {'scope':'READ_ONLY_AUTHORITY_RECONSTRUCTION','states':states,'usage':budget.globalused,'unresolved':unresolved,'nativeCalls':0,'newProcesses':0,'writeCapability':False}
