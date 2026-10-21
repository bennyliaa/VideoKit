"""Read-only E1C recovery: reservations are minima, never reusable difference.

Only matching batch/task records and complete identity-bound query lines contribute
credit. Both journal slots, the PF admission inventory and query logs merge by
component-wise maximum. A missing shard is an unknown admitted task, not zero.
No function below constructs Native, Channel, an OS handle, or a writer.
"""
from __future__ import annotations
import copy
from gcore import *

_CLOSED={'CLOSED_PROVEN','RELEASED_BY_OWNER_EXIT'}
_RAW_FIELDS={'rawHandle','nativeHandle','handleValue','raw_handle','native_handle'}

def _problem(out,task,status,**extra):
    item=dict(task=task,status=status,rule='FENCED_NO_CREDIT_REUSE_OR_REEXECUTION',**extra)
    if item not in out:out.append(item)

def _strip_raw(value):
    if isinstance(value,dict):return {k:_strip_raw(v) for k,v in value.items() if k not in _RAW_FIELDS}
    if isinstance(value,list):return [_strip_raw(v) for v in value]
    return value

def _merge_usage(target,source,budget,task,problems,origin):
    if not isinstance(source,dict):
        _problem(problems,task,'USAGE_UNKNOWN',origin=origin);return
    for row,used in source.items():
        if row not in budget.rows or (row!='GC' and budget.rows[row]['task']!=task):
            _problem(problems,task,'USAGE_ROW_IDENTITY_UNKNOWN',row=row,origin=origin);continue
        if not isinstance(used,dict) or set(used)!=set(empty_usage()) or any(type(v) is not int or v<0 for v in used.values()):
            _problem(problems,task,'USAGE_SCHEMA_UNKNOWN',row=row,origin=origin);continue
        previous=target.setdefault(row,empty_usage())
        for key,value in used.items():previous[key]=max(previous[key],value)
        if any(v>Budget.caps(budget.rows[row])[k] for k,v in previous.items()):
            # Preserve the larger value. Clamping to the cap would be a refund.
            _problem(problems,task,'USAGE_EXCEEDS_CAP_UNKNOWN',row=row,origin=origin)

def _slots(store,task,batch,problems):
    found=[]
    for slot in range(2):
        path=store.root/task/f'state{slot}.slot'
        if not path.exists():continue
        try:
            with store.file(path,'rb',8192) as file:
                store.native['read']+=1;raw=file.read(8193)
            seq,state=Store.decode_record(raw)
            need(isinstance(state,dict) and state.get('schema')==3 and state.get('batch')==batch and state.get('task')==task,'RECOVERY_IDENTITY')
            need(all(isinstance(state.get(k),dict) for k in ('usage','commands','objects','q')),'RECOVERY_STATE_SCHEMA')
            found.append((seq,state))
        except (Refused,OSError,ValueError,TypeError,KeyError,zlib.error) as ex:
            _problem(problems,task,'SNAPSHOT_PARTIAL_OR_INVALID',slot=slot,reason=str(ex))
    return sorted(found,key=lambda item:item[0])

def _inventory(slots,batch,budget,problems):
    inventory={};before=len(problems);latest_valid=bool(slots) and isinstance(slots[-1][1].get('inventory'),dict)
    for sequence,state in slots:
        source=state.get('inventory')
        if not isinstance(source,dict):continue
        for task,entry in source.items():
            if task not in {r['task'] for r in budget.rows.values()} or not isinstance(entry,dict) or entry.get('batch')!=batch or entry.get('task')!=task or entry.get('admitted') is not True:
                _problem(problems,'PF','ADMISSION_INVENTORY_ENTRY_UNKNOWN',entryTask=task);continue
            current=inventory.setdefault(task,dict(batch=batch,task=task,admitted=True,minimumUsage={}))
            _merge_usage(current['minimumUsage'],entry.get('minimumUsage'),budget,task,problems,'PF_INVENTORY')
            if 'initialCommand' in entry:current['initialCommand']=copy.deepcopy(entry['initialCommand'])
    if not latest_valid or 'PF' not in inventory:
        _problem(problems,'PF','ADMISSION_INVENTORY_UNKNOWN')
    # A damaged PF slot can hide a later admission. Neither a corrupt slot nor an
    # invalid inventory entry permits a declaration that an absent task was free.
    damaged=any(p['task']=='PF' and p['status']=='SNAPSHOT_PARTIAL_OR_INVALID' for p in problems)
    return inventory,latest_valid and 'PF' in inventory and len(problems)==before and not damaged

def _query_log(store,row,state,problems):
    """Accept complete E1C lines only; a partial tail is unknown, not a query refund."""
    rid=row['id'];task=row['task'];path=store.root/'events'/f'{rid}.q';counts={'qn':0,'qr':0};cache={};valid=True
    if path.exists():
        try:
            with store.file(path,'rb',8192) as file:
                store.native['read']+=1;raw=file.read(8193)
            need(len(raw)<=8192,'QCACHE_LIMIT')
        except (Refused,OSError) as ex:
            _problem(problems,task,'QUERY_LOG_UNREADABLE',row=rid,reason=str(ex));return counts,False
        for number,line in enumerate(raw.splitlines(keepends=True),1):
            if not line.endswith(b'\n'):
                _problem(problems,task,'QUERY_LOG_PARTIAL',row=rid,line=number);valid=False;break
            try:
                event=json.loads(line)
                need(isinstance(event,dict) and event.get('batch')==store.root.name and event.get('task')==task and event.get('row')==rid,'QUERY_LOG_IDENTITY')
                need(type(event.get('new')) is bool and isinstance(event.get('view'),dict) and event['view'].get('task')==task,'QUERY_LOG_SCHEMA')
                qid=event.get('qid');need(isinstance(qid,str) and qid.startswith(rid+'/q'),'QUERY_LOG_QID')
                suffix=qid[len(rid)+2:];need(suffix.isdigit() and str(int(suffix))==suffix and 1<=int(suffix)<=row['queriesNew'],'QUERY_LOG_QID')
                if event['new']:
                    need(qid not in cache or cache[qid]==event['view'],'QUERY_CACHE_CONFLICT')
                    cache[qid]=copy.deepcopy(event['view']);counts['qn']+=1
                else:
                    known=cache.get(qid,state['q'].get(qid));need(known is not None and known==event['view'],'QUERY_REPLAY_IDENTITY')
                    counts['qr']+=1
            except (Refused,ValueError,TypeError,KeyError) as ex:
                _problem(problems,task,'QUERY_LOG_UNTRUSTED_LINE',row=rid,line=number,reason=str(ex));valid=False
        # A trusted prefix remains a minimum even when the tail is damaged.
        for qid,view in cache.items():
            previous=state['q'].get(qid)
            if previous is not None and previous!=view:
                _problem(problems,task,'QUERY_CACHE_SNAPSHOT_CONFLICT',row=rid,qid=qid);valid=False
            else:state['q'][qid]=view
    usage=state['usage'].setdefault(rid,empty_usage())
    if counts['qn']<usage['qn'] or counts['qr']<usage['qr']:
        _problem(problems,task,'QUERY_LOG_BEHIND_RESERVED_SNAPSHOT',row=rid,snapshot={'qn':usage['qn'],'qr':usage['qr']},completeLog=copy.deepcopy(counts));valid=False
    for key in ('qn','qr'):usage[key]=max(usage[key],counts[key])
    if usage['qn']>row['queriesNew'] or usage['qr']>row['queriesReplay']:
        _problem(problems,task,'QUERY_LOG_OVER_CAP_UNKNOWN',row=rid);valid=False
    return counts,valid

def _totals(states,budget):
    """The GC row is one shared counter recorded in several shards, never a sum."""
    rows={}
    for state in states.values():
        for row,used in state['usage'].items():
            previous=rows.setdefault(row,empty_usage())
            for key,value in used.items():previous[key]=max(previous[key],value)
    total=empty_usage()
    for used in rows.values():
        for key,value in used.items():total[key]+=value
    return rows,total

def recover(root,manifest):
    root=Path(root).resolve();need(root.is_relative_to((BASE/'selfcheck').resolve()),'SYNTHETIC_ROOT_ONLY')
    need(root.exists(),'NO_JOURNALS')
    ledger=Ledger();store=Store(root,ledger);budget=Budget(manifest);states={};issues=[];unresolved=[]
    expected=sorted({r['task'] for r in manifest['branches']}|{'PF'})
    slots={task:_slots(store,task,root.name,issues) for task in expected}
    inventory,inventory_known=_inventory(slots['PF'],root.name,budget,issues)
    present={task for task,records in slots.items() if records};admitted=set(inventory);missing=[];not_admitted=[]
    for task in expected:
        records=slots[task];minimum=inventory.get(task,{}).get('minimumUsage',{})
        if not records and task not in admitted:
            if inventory_known and not (root/task).exists():not_admitted.append(task)
            else:_problem(issues,task,'ADMISSION_OR_SHARD_UNKNOWN')
            continue
        if records:
            state=_strip_raw(copy.deepcopy(records[-1][1]));state['usage']={}
            for sequence,record in records:_merge_usage(state['usage'],record['usage'],budget,task,issues,'SNAPSHOT:'+str(sequence))
            if inventory_known and task not in admitted:_problem(issues,task,'PRESENT_SHARD_ABSENT_FROM_INVENTORY')
        else:
            missing.append(task)
            state=dict(schema=3,batch=root.name,task=task,usage={},commands={},objects={},versions={},ops={},q={},unknownShard=True)
            _problem(issues,task,'ADMITTED_SHARD_MISSING',initialCommand=_strip_raw(copy.deepcopy(inventory[task].get('initialCommand'))))
        _merge_usage(state['usage'],minimum,budget,task,issues,'PF_INVENTORY_MINIMUM')
        if records:
            for row in manifest['branches']:
                if row['task']==task:_query_log(store,row,state,issues)
        for key,command in state['commands'].items():
            if not isinstance(command,dict) or command.get('status')!='DONE':
                unresolved.append(dict(task=task,command=key,status=command.get('status','UNKNOWN') if isinstance(command,dict) else 'UNKNOWN',effect=command.get('effect') if isinstance(command,dict) else None,rule='NO_REEXECUTION_OWNER_PROOF_REQUIRED'))
        for key,resource in state['objects'].items():
            if not isinstance(resource,dict) or resource.get('disposition') not in _CLOSED:
                unresolved.append(dict(task=task,resource=key,owner=resource.get('owner') if isinstance(resource,dict) else None,disposition=resource.get('disposition','UNKNOWN') if isinstance(resource,dict) else 'UNKNOWN',rule='NO_NATIVE_HANDLE_RECONSTRUCTION'))
        state.update(recovered=True,fenced=True,globalFence=True,confirmed=False)
        states[task]=state
    rows,total=_totals(states,budget)
    if any(v>budget.globalcap[k] for k,v in total.items()):_problem(issues,'PF','GLOBAL_USAGE_EXCEEDS_CAP_UNKNOWN')
    # Apply the production validator, preserving the larger minimum on corruption.
    try:budget.restore(states.values())
    except Refused as ex:_problem(issues,'PF','RECOVERED_BUDGET_UNKNOWN',reason=str(ex))
    unresolved.extend(issues);status='UNKNOWN' if issues else 'COMPLETE'
    return dict(scope='READ_ONLY_AUTHORITY_RECONSTRUCTION',states=states,usage=total,rowUsage=rows,
                usageKnownMinimum=copy.deepcopy(total),usageExact=not issues,
                completeness=dict(status=status,inventoryKnown=inventory_known,admitted=sorted(admitted),present=sorted(present),missingAdmitted=missing,notAdmitted=not_admitted),
                batchState='UNKNOWN' if issues else 'FENCED_RECOVERED',unresolved=unresolved,
                nativeCalls=0,newProcesses=0,writeCapability=False)
