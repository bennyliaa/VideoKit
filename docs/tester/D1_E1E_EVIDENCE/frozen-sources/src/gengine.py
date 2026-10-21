from __future__ import annotations
import base64, copy, hashlib, json, os, threading, time
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeout
from pathlib import Path
from gcore import *
from authority import SourceAuthority,SourceBridge,PendingCell,capture_ready_request,validate_ready_request,complete_source_response
from notifications import CompletionHub

CLOSED={'CLOSED_PROVEN','RELEASED_BY_OWNER_EXIT'}
CS_STATE=['OWNED_OPEN_RETRYABLE','IN_FLIGHT','CLOSED_PROVEN','UNKNOWN','RELEASED_BY_OWNER_EXIT']

class Engine:
    def __init__(self,root,manifest):
        self.root=root;self.manifest=manifest;self.budget=Budget(manifest);self.ledger=Ledger();self.store=Store(root,self.ledger);self.native=Native(self.ledger)
        self.states={};self.channels={};self.key=os.urandom(32);self.row=None;self.flow=None;self.assertions=0;self.results=[];self.lock=threading.RLock()
        self.helper_attempts={name:dict(attempted=False,status='NOT_ATTEMPTED') for name in ('J','R')}
        self.io=ThreadPoolExecutor(max_workers=2,thread_name_prefix='E1B-native');self.pending={};self.stopping=False;self.global_log=None;self.global_close=None;self.sources={};self.data_counts={}
        self.admissions={};self.source=SourceAuthority(self.lock);self.bridge=SourceBridge(self.source);self.cells={};self.cell_peak=0;self.completions=CompletionHub(self.ledger)
    def check(self,ok,reason):need(ok,'ASSERT:'+reason);self.assertions+=1
    def io_call(self,fn,timeout=None):
        future=self.io.submit(fn);key=uid();self.pending[key]=future
        try:return future.result(timeout=timeout or max(.001,self.budget.remaining(self.row)))
        except FutureTimeout:self.stopping=True;raise Stop('NATIVE_PENDING_DEADLINE')
        finally:
            if future.done():self.pending.pop(key,None)
    def save(self,task):
        with self.lock:
            self.states[task]['resources']=copy.deepcopy(self.ledger.live)
            self.states[task]['dataCounts']={r+'/'+k:v for (r,k),v in self.data_counts.items() if self.budget.rows[r]['task']==task}
            state=copy.deepcopy(self.states[task])
            self.io_call(lambda:self.store.save(task,state))
    def event(self,event,query=False):self.io_call(lambda:self.store.event(self.row,event,query))
    def new_state(self,task):
        return dict(schema=3,batch=self.root.name,task=task,domain='source' if task.startswith('S') else 'sink' if task.startswith('T') else 'PF',seq=0,usage={},commands={},objects={},versions={},ops={},q={},recovered=False,sourceDone=True)
    def begin(self,row):
        self.row=row;self.budget.begin(row);self.flow=Flow(self,row)
        if self.stopping and row!='GC':raise Stop('STOPPED_NO_NEW_ROW')
        return self.flow
    def remote(self,who,verb,args=(),kind='N',claim='',epoch=None,task=None):
        self.store.ensure_writable()
        f=self.flow;task=task or f.task;s=self.states[task];op=f.current_id
        admission=self.admissions.get(op);need(admission and admission['saved'] and admission['calls']==0,'UNADMITTED_OR_REUSED_RPC')
        allowed={'h+':{'OPEN'},'r+':{'OPEN_REF'},'ch':{'CLOSE','HOLD_CLOSE'},'retry':{'CLOSE'},'cr':{'CLOSE'},'ca':{'CLOSE','HOLD_CLOSE'},'cb':{'CLOSE'},'cv':{'CLOSE'},'allocA':{'CREATE_A'},'dupB':{'DUP'},'sendB':{'SEND'},'takeB':{'TAKE'},'claim':{'CLAIM'},'flushB':{'FLUSH'},'v+':{'OPEN_V'},'gate':{'GATE_CLOSE'},'readJ':{'READ','READ_ZERO'},'readRef':{'READ'},'readV':{'READ'},'write':{'WRITE','WRITE_FAIL'},'writeCurrent':{'WRITE_CURRENT'},'seekW':{'SEEK'},'helloJ':{'HELLO'},'helloR':{'HELLO'},'exitJ':{'EXIT'},'exitR':{'EXIT'},'recoverJournal':{'RECOVER'}}
        need(verb in allowed.get(admission['label'],set()),'RPC_NOT_IN_FROZEN_OPERATION')
        if f.row!='GC':self.completions.ensure_accepting()
        admission['calls']+=1
        if verb in {'CREATE_A','DUP','SEND','TAKE','CLAIM','OPEN_V'}:need(not s.get('globalFence') and not s.get('recovered'),'SINK_FENCED')
        row=f.row;effective_epoch=epoch or s.get('epoch',1);left=max(.001,self.budget.remaining(row));callback=self.recovery_callback if verb=='RECOVER' else None
        result=self.io_call(lambda:self.channels[who].call(op,verb,row,task,effective_epoch,claim,kind,args,timeout=left,callback=callback),timeout=left)
        if verb=='RECOVER':
            sequence,payload=result.split('|',1)
            return {'sequence':int(sequence),'snapshotSha':sha(base64.b64decode(payload)),'recovered':True}
        return result
    def recovery_callback(self,kind,seq,payload):
        f=self.flow;need(f.row=='Q06-LOST','UNPLANNED_CALLBACK')
        if kind=='RECOVERY_QNEW':
            restored=Store.inflate(payload);need(restored['task']==f.task and restored['state']=='READY' and restored.get('token') and restored.get('grant'),'RECOVERY_IDENTITY')
            need(restored.get('schema')==3 and restored.get('batch')==self.root.name,'RECOVERY_IDENTITY')
            from recovery import _merge_usage,_query_log
            issues=[];minimum=copy.deepcopy(self.states[f.task]['usage'])
            _merge_usage(restored['usage'],minimum,self.budget,f.task,issues,'LIVE_RESERVED_MINIMUM')
            for row in self.manifest['branches']:
                if row['task']==f.task:_query_log(self.store,row,restored,issues)
            need(not issues,'RECOVERY_QUERY_OR_USAGE_UNKNOWN')
            self.states[f.task]=restored;self.store.seq[f.task]=seq;restored['recovered']=True
            self.budget.restore(self.states.values())
            for k,v in restored.get('dataCounts',{}).items():
                row,kind=k.rsplit('/',1);self.data_counts[row,kind]=v
            need(not any(r['disposition'] not in CLOSED for r in restored['objects'].values()),'RECOVERY_LIVE_OWNERSHIP_REQUIRES_EXIT_PROOF')
            return f.query()
        need(kind=='RECOVERY_QREPLAY','UNPLANNED_CALLBACK');return f.query(replay=True)
    def source_view(self,s,version=None):
            version=version or s.get('version','v1');v=s['versions'].get(version,{'sealed':False,'consumers':{}})
            live=[r for r in s['objects'].values() if r['version']==version and r['disposition'] not in CLOSED]
            ops=[o for o in s['ops'].values() if o['version']==version and not o['done']]
            reservations=sum(not c['finished'] or any(r.get('consumer')==name for r in live) or any(o['consumer']==name for o in ops) for name,c in v['consumers'].items())
            return dict(task=s['task'],version=version,sealed=v['sealed'],reservations=reservations,handles=len(live),operations=len(ops)+sum(r['disposition']=='IN_FLIGHT' for r in live),seq=s['seq'],state='DRAINED' if v['sealed'] and reservations==0 and not live and not ops else 'PENDING')
    def view(self,task=None):
        s=self.states[task or self.flow.task]
        if s['domain']=='source':return self.source_view(s)
        return dict(task=s['task'],state=s.get('state','NONE'),epoch=s.get('epoch',1),grant=s.get('grant',''),token=s.get('token',''),refs=sum(r['role'] in ('A','B') and r['disposition'] not in CLOSED for r in s['objects'].values()),validators=sum(r['role']=='V' and r['disposition'] not in CLOSED for r in s['objects'].values()),seq=s['seq'])
    def object(self,key):return self.states[self.flow.task]['objects'][key]
    def add_object(self,key,actor,role,version='',consumer=''):
        s=self.states[self.flow.task];need(key not in s['objects'],'OBJECT_ALREADY_EXISTS');owner=self.channels[actor].owner if actor in self.channels else 'G'
        self.ledger.acquire(key,owner,'media',self.budget.rows[self.row]);s['objects'][key]=dict(key=key,actor=actor,owner=owner,role=role,version=version,consumer=consumer,disposition='UNKNOWN',object='',ticket='',revision=0,attempts=0,nativeCloses=0)
        return s['objects'][key]
    def jproof(self,key,text):
        p=text.split('|');r=self.object(key);need(not r['object'] or r['object']==p[0],'OBJECT_PROOF_MISMATCH');r.update(object=p[0],ticket=p[1],disposition=p[2],attempts=int(p[3]),nativeCloses=int(p[4]),revision=int(p[5]),first=p[6])
        if r['disposition'] in CLOSED:self.ledger.release(key,'NATIVE_CLOSE_RETURNED')
        return copy.deepcopy(r)
    def rproof(self,key,proof):
        r=self.object(key);need(not r['object'] or r['object']==proof['objectId'],'OBJECT_PROOF_MISMATCH');need(r['owner']==proof['owner'],'OWNER_PROOF_MISMATCH')
        r.update(object=proof['objectId'],ticket=proof['ticket'],disposition=CS_STATE[proof['disposition']],attempts=proof['attempts'],nativeCloses=proof['delegateCalls'],revision=proof['revision'],first=proof['firstError'])
        if r['disposition'] in CLOSED:self.ledger.release(key,'NATIVE_CLOSE_RETURNED')
        return copy.deepcopy(r)
    def abort_progress(self):
        s=self.states[self.flow.task]
        if s.get('abortRequested') and self.view()['refs']==0 and self.view()['validators']==0 and not s.get('deliveryPending',False):s['state']='ABORTED'
    def private_cell(self,s,operation,binding,kind,buffer=False,timeout=None,handle_key=None):
        with self.lock:
            self.completions.ensure_accepting()
            need(sum(not c.released for c in self.cells.values())<8,'PRIVATE_RESULT_CELL_LIMIT')
            if buffer:
                row=self.budget.rows[self.row]
                with self.ledger.lock:
                    need(self.ledger.buffers<8 and self.ledger.buffers<row['buffers'],'BUFFER_LIMIT')
                    self.ledger.buffers+=1;self.ledger.buffer_peak=max(self.ledger.buffer_peak,self.ledger.buffers)
            def release():
                if buffer:
                    with self.ledger.lock:self.ledger.buffers-=1
            def drained():
                with self.lock:
                    self.source.drain(s,operation)
                    command=s['commands'][operation];error=cell.response.exception()
                    command.update(status='DONE',error=str(error) if error else '',result={'completion':'DISCARDED' if cell.discarded else 'DELIVERED'})
            try:cell=PendingCell(operation,binding,release,drained,timeout,hub=self.completions,authority=self.source,state=s,kind=kind,handle_key=handle_key)
            except BaseException:
                if buffer:
                    with self.ledger.lock:self.ledger.buffers-=1
                raise
            self.cells[operation]=cell
            s['held'+kind.title()]=operation;self.cell_peak=max(self.cell_peak,sum(not c.released for c in self.cells.values()));return cell
    def cancel_cells(self,s,version,c,reason='CANCELLED'):
        for cell in list(self.cells.values()):
            if not cell.released and cell.binding==self.source.binding(s,version,c):cell.cancel(reason)
    def finish_source(self,s,operation,cell,value,hold):
        return complete_source_response(self.source,s,operation,cell,value,hold)

class Flow:
    def __init__(self,e,row):self.e=e;self.row=row;self.started=time.monotonic();self.spec=e.budget.rows[row];self.task=self.spec['task'];self.ni=0;self.di=0;self.qn=0;self.qr=0;self.local=threading.local();self.control_ids={};self.expected=next((r['operations'] for r in e.manifest['branches'] if r['id']==row),[])
    @property
    def current_id(self):return getattr(self.local,'id','')
    @current_id.setter
    def current_id(self,value):self.local.id=value
    def transaction(self,id,kind,charge,action,label,command=None,args=None,journal_task=None):
        e=self.e
        e.store.ensure_writable()
        hub=getattr(e,'completions',None)
        if self.row!='GC' and hub is not None:
            initial_setup=self.row=='PF' and id=='PF/n01' and label=='setup' and hub.pending()['lifecycle']=='NEW'
            if not initial_setup:hub.ensure_accepting()
        journal_task=journal_task or self.task
        with e.lock:
            fresh=journal_task not in e.states
            if fresh:charge=dict(charge,records=1)
            e.budget.charge(self.row,**charge)
            if fresh:e.states[journal_task]=e.new_state(journal_task)
            s=e.states[journal_task];s['usage'][self.row]=copy.deepcopy(e.budget.used[self.row]);s['seq']+=1
            command=command or id;signature=sha(compact([label,args]));old=s['commands'].get(command)
            if old:
                need(old['signature']==signature,'COMMAND_CONFLICT');cached=True
            else:
                cached=False;s['commands'][command]={'signature':signature,'status':'ADMITTED','result':None,'error':'','kind':kind,'args':args,'label':label}
                allocation={'g+':('G','guard'),'h+':('J','H'),'r+':('R','REF'),'allocA':('R','A'),'dupB':('R','B'),'v+':('R','V')}.get(label)
                if allocation:
                    actor,role=allocation;key=args[0] if isinstance(args,list) else args
                    s['commands'][command]['effect']={'kind':'ALLOCATE','key':key,'actor':actor,'role':role,'owner':e.channels[actor].owner if actor in e.channels else 'G','disposition':'UNKNOWN_UNTIL_COMPLETION'}
                if label in {'write','writeCurrent'}:
                    offset,size,fail=args;need(s.get('confirmed') and not s.get('abortOnly') and not s.get('recovered') and not s.get('globalFence'),'WRITE_FENCED')
                    need(0<=offset<=65536-size and s['spent']+size<=s['credit'],'WRITE_CREDIT');s['spent']+=size
                    s['commands'][command]['effect']={'kind':'WRITE','key':s['B'],'requested':size,'offset':offset,'claim':s['claim'],'epoch':s['epoch']}
            self.current_id=id
            e.admissions[id]={'label':label,'calls':0,'saved':False,'kind':kind}
            if fresh:
                inventory_task='PF' if journal_task!='PF' else journal_task
                inventory=e.states[inventory_task].setdefault('inventory',{})
                inventory[journal_task]={'batch':e.root.name,'task':journal_task,'admitted':True,'minimumUsage':{self.row:copy.deepcopy(e.budget.used[self.row])},'initialCommand':copy.deepcopy(s['commands'][command])}
        pure=label in {'res','seal','end','cancel','version','notice','retire','grant','takeover','ready','abort','cancelO','sourceFence','sinkFence'} and not (label=='grant' and args and args[-1] is True)
        if fresh and journal_task!='PF':e.save('PF')
        elif not pure:e.save(journal_task)
        e.event(dict(id=id,phase='ADMITTED',kind=kind,command=command))
        e.admissions[id]['saved']=True
        error='';result=None
        try:
            if cached:
                need(old['status']=='DONE','COMMAND_PENDING')
                if old['error']:raise Refused(old['error'])
                result=copy.deepcopy(old['result'])
            else:result=action()
        except Refused as ex:error=str(ex)
        except Exception:
            e.stopping=True;s['commands'][command]['status']='UNKNOWN';raise
        with e.lock:
            s=e.states[journal_task]
            waiting=isinstance(result,dict) and result.get('pending') in e.cells
            if not cached:s['commands'][command].update(status='WAITING_COMPLETION' if waiting else 'DONE',result=result,error=error)
            s['seq']+=1
        if not waiting:e.save(journal_task)
        e.event(dict(id=id,phase='WAITING_COMPLETION' if waiting else 'DONE',error=error,kind=kind,resultDigest=sha(compact(result))))
        if error:raise Refused(error)
        return result
    def n(self,label,action,command=None,args=None,extra=None,journal_task=None):
        with self.e.lock:
            self.ni+=1;need(self.ni<=self.spec['nonquery'],'CONTROL_COUNT')
            if self.expected:need(self.expected[self.ni-1]['token'].startswith(label),'CONTROL_ORDER:'+label)
            id=f'{self.row}/n{self.ni:02}';self.control_ids.setdefault(label,id)
        return self.transaction(id,'N',dict(n=1,**(extra or {})),action,label,command,args,journal_task)
    def data(self,label,charge,action,args=None):
        maximum={'write':{'Q01-SEQ':1,'Q04-DUP':1,'Q02-RANDOM':3,'Q04-CLOSEACK':1,'Q05-SPACEFAIL':2,'Q07-TAKEFIRST':1}}
        if label=='readZero':
            need(self.row=='P02-ZERO' and self.e.data_counts.get((self.row,'zero'),0)==0,'ZERO_BRIDGE_STEP_LIMIT');self.e.data_counts[self.row,'zero']=1
        elif label in ('write','writeCurrent','seekW'):
            category='seek' if label=='seekW' else 'write';allowed=3 if category=='seek' and self.row=='Q02-RANDOM' else maximum['write'].get(self.row,0) if category=='write' else 0
            key=(self.row,category);used=self.e.data_counts.get(key,0);need(used<allowed,'DATA_STEP_NOT_IN_FROZEN_ROW');self.e.data_counts[key]=used+1
        else:need(charge and any(charge.values()),'UNMETERED_DATA')
        self.di+=1;id=f'{self.row}/d{self.di:02}';return self.transaction(id,'D',charge,action,label,args=args)
    def query(self,replay=False):
        e=self.e;s=e.states[self.task]
        e.store.ensure_writable()
        if self.row!='GC':e.completions.ensure_accepting()
        if replay:
            need(self.qr<self.spec['queriesReplay'] and self.qn>0,'QUERY_REPLAY_LIMIT');self.qr+=1;charge={'qr':1};qid=f'{self.row}/q1';need(qid in s['q'],'QUERY_CACHE_MISSING');view=copy.deepcopy(s['q'][qid])
        else:
            need(self.qn<self.spec['queriesNew'],'QUERY_FRESH_LIMIT');self.qn+=1;charge={'qn':1};qid=f'{self.row}/q{self.qn}';view=e.view();s['q'][qid]=copy.deepcopy(view)
        before=time.monotonic();e.budget.charge(self.row,**charge);s['usage'][self.row]=copy.deepcopy(e.budget.used[self.row]);e.event(dict(batch=e.root.name,task=self.task,row=self.row,qid=qid,new=not replay,afterControl=self.ni,afterData=self.di,view=view),query=True)
        need(time.monotonic()-before<=.1,'QUERY_OBSERVATION_TIMEOUT');return view
    def finish(self):
        need(self.ni==self.spec['nonquery'],'MISSING_CONTROLS:'+self.row)
        while self.qn<self.spec['queriesNew']:self.query()
        while self.qr<self.spec['queriesReplay']:
            before=self.e.view();old=self.query(True);self.e.check(self.e.view()==before and old['seq']<=before['seq'],'cached-observation-does-not-overwrite-new-state')
        elapsed=time.monotonic()-self.started;need(elapsed<=self.spec['seconds'],'ROW_COMPLETION_DEADLINE')
        self.e.results.append(dict(branch=self.row,scope='SYNTHETIC_CHECKPOINT_ONLY',controls=self.ni,dataSteps=self.di,queryNew=self.qn,queryReplay=self.qr,seconds=self.spec['seconds'],elapsedSeconds=elapsed))

class Ops:
    def __init__(self,e):self.e=e
    @property
    def f(self):return self.e.flow
    @property
    def s(self):return self.e.states[self.f.task]
    def source_version(self):return self.s.get('version','v1')
    def version(self,name):
        def act():
            self.s['version']=name;self.s['versions'].setdefault(name,dict(sealed=False,consumers={}));return {'version':name}
        return self.f.n('version',act,args=name)
    def res(self,c='a',v=None):
        version=v or (self.source_version() if self.f.task in self.e.states else 'v1')
        def act():
            need(not self.e.states.get('PF',{}).get('sourceFenced'),'SESSION_RELEASED')
            return self.e.source.reserve(self.s,version,c)
        return self.f.n('res',act,args=[version,c])
    def seal(self,v=None):
        version=v or self.source_version()
        def act():
            self.e.source.seal(self.s,version)
        return self.f.n('seal',act,args=version)
    def end(self,c='a',v=None):
        version=v or self.source_version()
        def act():
            self.e.source.end(self.s,version,c)
            with self.e.lock:self.s['sourceDone']=self.e.source_view(self.s,version)['state']=='DRAINED';return {'sourceDone':self.s['sourceDone']}
        return self.f.n('end',act,args=[version,c])
    def cancel_source(self,c='a'):
        def act():
            self.e.source.cancel(self.s,self.source_version(),c)
        return self.f.n('cancel',act,args=c)
    def input_name(self):return 'L.bin' if self.f.task in ('S01','S02') else 'Z.bin' if self.f.task=='S03' else 'C.bin'
    def rid(self,name,v=None):return f'{self.f.task}-{v or self.source_version()}-{name}'
    def guard(self):
        key=self.rid('guard')
        def act():
            r=self.e.add_object(key,'G','guard',self.source_version());proof=self.e.native.open(key,self.e.root/self.input_name(),self.e.budget.rows[self.e.row])
            # Native.open owns admission, so add_object must reserve only once (handled below).
            r.update(proof);return {'identity':proof['identity']}
        return self.f.n('g+',act,args=key)
    def open_j(self,name='H',c='a',v=None,hold=False):
        version=v or self.source_version();key=self.rid(name,version)
        def act():
            with self.e.lock:
                need(not self.e.states.get('PF',{}).get('sourceFenced'),'SESSION_RELEASED')
                binding=self.e.source.binding(self.s,version,c);operation=self.f.current_id;self.e.source.admit(self.s,binding,operation)
                r=self.e.add_object(key,'J','H',version,c);r.update(binding)
                cell=self.e.private_cell(self.s,operation,binding,'open',handle_key=key)
            raw=self.e.remote('J','OPEN',[key,self.input_name()]);p=raw.split('|');r['length']=int(p[0]);r['mtime']=p[1];r['fileKey']=p[2];self.e.jproof(key,'|'.join(p[3:]));self.s['currentH']=key
            return self.e.finish_source(self.s,operation,cell,{'object':key,'length':r['length']},hold)
        value=self.f.n('h+',act,args=[key,c,version,hold])
        return self.e.cells[value['pending']] if hold else value
    def ref(self):
        key=self.rid('ref')
        def act():
            r=self.e.add_object(key,'R','REF',self.source_version());reply=self.e.remote('R','OPEN_REF',[key,self.input_name()]);r['identity']=reply['identity'];self.e.rproof(key,reply['ticket']);self.s['currentRef']=key;return {'identity':r['identity']}
        return self.f.n('r+',act,args=key)
    def close_j(self,name=None,fault='none',hold=False,expected=None,replay=None,label='ch'):
        key=name or self.s['currentH'];revision=expected if expected is not None else self.e.object(key)['revision']
        signature=[key,revision,fault,hold]
        if replay:signature=self.s['commands'][replay]['args']
        def act():
            r=self.e.object(key);need(r['revision']==revision,'STALE_REVISION');need(r['disposition']=='OWNED_OPEN_RETRYABLE','CLOSE_NOT_RETRYABLE');need(r['attempts']<3,'EXHAUSTED')
            raw=self.e.remote('J','HOLD_CLOSE' if hold else 'CLOSE',[key,revision,fault]);return self.e.jproof(key,raw)
        return self.f.n(label,act,command=replay,args=signature)
    def close_r(self,key=None,label='cr',fault='None'):
        key=key or self.s['currentRef']
        def act():
            reply=self.e.remote('R','CLOSE',[key,fault]);proof=self.e.rproof(key,reply['ticket'])
            if key==self.s.get('B') and proof['disposition']=='CLOSED_PROVEN':self.s['deliveryPending']=False
            self.e.abort_progress();return proof
        return self.f.n(label,act,args=[key,fault])
    def close_guard(self):
        key=self.rid('guard')
        def act():self.e.object(key).update(self.e.native.close(key));return {'closed':key}
        return self.f.n('cg',act,args=key)
    def read_j(self,offset,n,cap=65536,hold=False,zero=False,c='a',declared=None):
        key=self.s['currentH'];version=self.e.object(key)['version']
        def act():
            with self.e.lock:
                need(not self.e.states.get('PF',{}).get('sourceFenced'),'SESSION_RELEASED')
                binding=self.e.source.binding(self.s,version,c);operation=self.f.current_id;self.e.source.admit(self.s,binding,operation,self.e.object(key))
                cell=self.e.private_cell(self.s,operation,binding,'read',buffer=True,timeout=1 if self.f.row=='P09-TIMEOUT' else None,handle_key=key)
            reply=self.e.remote('J','READ_ZERO' if zero else 'READ',[key,offset,n,cap],kind='I')
            p=reply.split('|');value=dict(n=int(p[0]),sha=p[1],bytes=p[2],nativeReads=int(p[3]),nativeSeeks=int(p[4]))
            self.e.object(key).update(nativeReads=value['nativeReads'],nativeSeeks=value['nativeSeeks'])
            if n and value['n']==0:cell.cancel('INVALID_PROVIDER_RESULT')
            if value['n']==-1 and declared is not None and offset<declared:cell.cancel('EARLY_EOF')
            value=self.e.finish_source(self.s,operation,cell,value,hold)
            if hold:return value
            return value
        value=self.f.data('readJ',{'ib':n,'ic':1},act,args=[key,offset,n,cap,hold,zero,c])
        return self.e.cells[value['pending']] if hold else value
    def read_zero(self,c='a'):
        key=self.s['currentH'];handle=self.e.object(key);binding=self.e.source.binding(self.s,handle['version'],c)
        return self.f.data('readZero',{},lambda:self.e.bridge.read_zero(self.s,binding,handle,lambda: self.e.remote('J','READ',[key,0,0,1],kind='I')),args=[key,binding,0])
    def read_r(self,offset,n,validation=False,key=None):
        key=key or self.s['currentRef']
        def act():
            with self.e.ledger.buffer(self.e.budget.rows[self.e.row],self.e.channels['R'].owner):return self.e.remote('R','READ',[key,offset,n],kind='V' if validation else 'I')
        return self.f.data('readV' if validation else 'readRef',{'v':n} if validation else {'ib':n,'ic':1},act,args=[key,offset,n])
    def gate(self,kind='read',key=None):
        def act():
            if kind=='close':return self.e.jproof(key,self.e.remote('J','GATE_CLOSE',[key]))
            if kind in ('open','read'):
                operation=self.s['held'+kind.title()];cell=self.e.cells[operation];cell.gate();return {'completed':kind,'discarded':cell.discarded,'delivered':cell.deliveries,'released':cell.released}
            self.s['validatorHeld']=False;return {'completed':kind}
        return self.f.n('gate',act,args=[kind,key])
    def grant(self,change='',replay=None,deny='',alias=False):
        def act():
            need(not self.e.states.get('PF',{}).get('sinkFenced'),'SINK_FENCED');baseline={'planVersion':1,'sourceVersions':['C/v1'],'preset':'IO_BYTE_PROBE'};proposed=copy.deepcopy(baseline)
            if change:proposed[{'Q09-PLAN':'planVersion','Q09-SOURCE':'sourceVersions','Q09-PRESET':'preset'}[change]]='different'
            need(proposed==baseline,'INTENT_CONFLICT')
            if alias:
                key=self.f.task+'-alias';proof=self.e.native.open(key,self.e.root/'C.bin',self.e.budget.rows[self.e.row]);self.e.native.close(key)
                original=self.e.states['PF']['objects']['PF-v1-guard']['identity'];need(proof['identity']!=original,'INPUT_ALIAS')
            capability={'randomAccess':self.f.row!='Q03-RANDOM','validationLease':self.f.row!='Q03-VERIFY'}
            self.s['capability']=capability;need(capability['randomAccess'],'RANDOM_REQUIRED');need(capability['validationLease'],'VALIDATION_REQUIRED')
            self.s.setdefault('state','GRANTED');self.s.setdefault('grant',uid());self.s.setdefault('delivery',uid());self.s.setdefault('receiver',self.e.channels['R'].owner+'/'+self.f.task);self.s.setdefault('claim',uid());self.s.setdefault('epoch',1)
            self.s.setdefault('ownerInstance',uid());self.s.setdefault('attempt',uid())
            return {k:self.s[k] for k in ('task','grant','delivery','receiver','epoch')}
        args=['grant','',False]
        if replay:args=self.s['commands'][replay]['args']
        else:args=['grant',change,deny,alias]
        return self.f.n('grant',act,command=replay,args=args)
    def alloc(self):
        key=self.f.task+'-A'
        def act():
            need(not self.s.get('globalFence') and not self.s.get('recovered'),'WRITE_FENCED');need(self.s['state']=='GRANTED' and not self.s.get('allocated'),'TARGET_ALREADY_SPENT');self.s['allocated']=True;self.s['credit']=65536;self.s['spent']=0
            r=self.e.add_object(key,'R','A');reply=self.e.remote('R','CREATE_A',[key,self.f.task+'.out',self.s['receiver']]);r['identity']=reply['identity'];self.e.rproof(key,reply['ticket']);self.s['A']=key;self.s['state']='PREPARED';return {'target':key}
        return self.f.n('allocA',act,args=key,extra=dict(targets=1,credit=65536))
    def dup(self):
        key=self.f.task+'-B'
        def act():
            need('B' not in self.s,'DUP_SPENT');r=self.e.add_object(key,'R','B');reply=self.e.remote('R','DUP',[key]);self.e.rproof(key,reply['ticket']);r['identity']=reply['identity'];self.s['B']=key;return {'descriptor':key}
        return self.f.n('dupB',act,args=key)
    def send(self,unknown=False):
        def act():
            need(not self.s.get('sent'),'SEND_SPENT');self.s['sent']=True;self.s['deliveryPending']=unknown;self.s['abortOnly']=unknown;reply=self.e.remote('R','SEND',[self.s['delivery'],'unknown' if unknown else 'known']);return reply
        return self.f.n('sendB',act,args=unknown)
    def take(self):
        def act():need(not self.s.get('taken') and not self.s.get('abortOnly'),'TAKE_SPENT');reply=self.e.remote('R','TAKE');self.s['taken']=True;return reply
        return self.f.n('takeB',act)
    def claim(self,unknown=False,bad='',replay=None):
        args=[unknown,bad]
        if replay:args=self.s['commands'][replay]['args']
        def act():
            receiver=self.s['receiver']+('/wrong' if bad=='receiver' else '');claim=self.s['claim']+('/wrong' if bad=='claim' else '')
            need(receiver==self.s['receiver'] and claim==self.s['claim'],'CLAIM_CONFLICT');need(self.s.get('taken') and not self.s.get('claimed') and not self.s.get('abortOnly'),'CLAIM_SPENT')
            reply=self.e.remote('R','CLAIM',['unknown' if unknown else 'known',self.s['receiver'],self.s['delivery']],claim=self.s['claim']);self.s['claimed']=True;self.s['confirmed']=not unknown;self.s['abortOnly']=unknown;self.s['state']='CLAIMED' if not unknown else 'CLAIM_UNKNOWN';return reply
        return self.f.n('claim',act,command=replay,args=args)
    def write(self,offset,data,fail=False,current=False):
        def act():
            need(self.s.get('confirmed') and not self.s.get('abortOnly') and not self.s.get('recovered') and not self.s.get('globalFence'),'WRITE_FENCED')
            need(0<=offset<=65536-len(data),'OUTPUT_RANGE')
            with self.e.ledger.buffer(self.e.budget.rows[self.e.row],self.e.channels['R'].owner):reply=self.e.remote('R','WRITE_FAIL' if fail else 'WRITE_CURRENT' if current else 'WRITE',[self.s['B'],offset,base64.b64encode(data).decode()],kind='W',claim=self.s['claim'])
            if fail:self.s['abortOnly']=True;self.s['state']='WRITE_FAILED';raise Refused('OUTPUT_SPACE_INSUFFICIENT')
            need(reply['n']==len(data),'SHORT_WRITE_STOP');expected=bytearray(base64.b64decode(self.s.get('expected','')))
            if len(expected)<offset+len(data):expected.extend(b'\0'*(offset+len(data)-len(expected)))
            expected[offset:offset+len(data)]=data;self.s['expected']=base64.b64encode(expected).decode();return reply
        return self.f.data('writeCurrent' if current else 'write',{},act,args=[offset,len(data),fail])
    def seek_write(self,offset,data):
        self.f.data('seekW',{},lambda:self.e.remote('R','SEEK',[offset],kind='S',claim=self.s['claim']),args=offset);return self.write(offset,data,current=True)
    def flush(self):return self.f.n('flushB',lambda:self.e.remote('R','FLUSH',claim=self.s['claim']))
    def close_a(self):return self.close_r(self.s['A'],'ca')
    def close_b(self,lost=False):return self.close_r(self.s['B'],'cb','LoseReplyAfterClose' if lost else 'None')
    def vopen(self):
        key=self.f.task+'-V'+str(self.s.get('validationCount',0)+1)
        def act():
            need(self.e.view()['refs']==0 and not self.s.get('abortRequested'),'WRITER_NOT_RELEASED');self.s['validationCount']=self.s.get('validationCount',0)+1;self.s['validationLease']=uid();self.s['revision']=self.s.get('revision',uid());self.s['V']=key
            r=self.e.add_object(key,'R','V');reply=self.e.remote('R','OPEN_V',[key,self.f.task+'.out']);r['identity']=reply['identity'];need(r['identity']==self.e.object(self.s['A'])['identity'],'OUTPUT_REVISION_IDENTITY');self.e.rproof(key,reply['ticket']);return {'lease':self.s['validationLease']}
        return self.f.n('v+',act,args=key)
    def vread(self,hold=False):
        actual=self.read_r(0,32,True,self.s['V']);expected=base64.b64decode(self.s['expected']);need(actual['n']==len(expected) and actual['sha']==sha(expected),'VALIDATION_BYTES_MISMATCH');self.s['validationHash']=actual['sha'];self.s['validatorHeld']=hold;return actual
    def vclose(self):
        def act():
            need(not self.s.get('validatorHeld'),'VALIDATOR_CALLBACK_PENDING');key=self.s['V'];reply=self.e.remote('R','CLOSE',[key,'None']);self.e.rproof(key,reply['ticket']);need(self.e.object(key)['disposition']=='CLOSED_PROVEN','VALIDATOR_CLOSE_UNPROVEN')
            self.s['receipt']=dict(task=self.f.task,grant=self.s['grant'],epoch=self.s['epoch'],revision=self.s['revision'],lease=self.s['validationLease'],sha=self.s['validationHash']);self.s['state']='READY_ELIGIBLE';self.e.abort_progress();return {'receipt':sha(compact(self.s['receipt']))}
        return self.f.n('cv',act,args=self.s['V'])
    def takeover(self):
        def act():
            with self.e.lock:
                if self.s['state'] not in ('READY','ABORTED'):self.s['epoch']+=1;self.s['ownerInstance']=uid();self.s['abortOnly']=True;self.s['confirmed']=False
                return self.e.view()
        return self.f.n('takeover',act)
    def ready_request(self):return capture_ready_request(self.s)
    def ready(self,request=None):
        request=copy.deepcopy(request if request is not None else self.ready_request())
        def act():
            with self.e.lock:
                validate_ready_request(self.s,request);need(self.e.view()['refs']==0 and self.e.view()['validators']==0,'RESOURCE_NOT_RELEASED');self.s['state']='READY';self.s['token']=uid();return self.e.view()
        value=self.f.n('ready',act,args=request)
        # The fixed T01 lost response is applied after the durable commit. Its
        # caller receives no token; later J journal recovery obtains that token.
        return {'ack':'INJECTED_LOST_RESPONSE','token':None} if self.f.row=='Q01-SEQ' else value
    def cancel_output(self,label='cancelO'):
        def act():
            with self.e.lock:
                if self.s.get('state')=='READY':return self.e.view()
                self.s['abortRequested']=True;self.s['abortOnly']=True;self.s['state']='ABORT_PENDING';self.e.abort_progress();return self.e.view()
        return self.f.n(label,act)
    def cpu_preflight(self):need(self.s.get('declaredLength',self.e.object(self.s['currentH'])['length']) is not None,'SOURCE_CAPABILITY_UNSUPPORTED')
    def media_preflight(self):need(self.e.object(self.s['currentH'])['length']!=0,'EMPTY_MEDIA')
