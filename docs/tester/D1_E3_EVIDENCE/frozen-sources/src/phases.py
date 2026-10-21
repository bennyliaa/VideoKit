from __future__ import annotations
import base64, copy, json, os, time
from gcore import *
from gengine import Engine,Ops,CLOSED,Flow

def preflight(e):
    from namespaces import Namespaces
    real=e.profile['kind']=='REAL_IO'
    e.namespace=Namespaces(e.root,e.profile['inputs'] if real else None,mode='CANDIDATE_IO' if real else 'SYNTHETIC')
    e.runtime.start()
    f=e.begin('PF');o=Ops(e)
    def setup():
        e.completions.start()
        e.global_log=e.store.open_log(b'E3 LIMITED REAL IO TOOL INTEGRATION\n' if real else b'E2A SYNTHETIC TOOL INTEGRATION\n');e.runtime.attach();return {'scope':'REAL_IO_TOOL_ONLY' if real else 'SYNTHETIC_ONLY'}
    f.n('setup',setup)
    for name in ('J','R'):
        def start(name=name):
            e.helper_attempts[name]=dict(attempted=True,status='CONSTRUCTING')
            try:e.channels[name]=Channel(name,e.root,e.key,e.ledger,bindings={alias+'.bin':str(path) for alias,path in e.namespace.inputs.items()},namespace_mode='CANDIDATE_IO' if real else 'SYNTHETIC')
            except BaseException:
                e.helper_attempts[name]['status']='UNKNOWN';raise
            c=e.channels[name];e.helper_attempts[name].update(status='CONSTRUCTED',pid=c.pid)
            e.states['PF'].setdefault('actors',{})[name]={'pid':c.pid,'started':c.started,'instance':None};return {'started':name,'pid':c.pid}
        f.n('start'+name,start)
    for name in ('J','R'):
        def hello(name=name):
            value=e.remote(name,'HELLO');channel=e.channels[name]
            if name=='J':instance,pid,runtime=value.split('|');pid=int(pid)
            else:instance,pid,runtime=value['instance'],value['pid'],value['runtime']
            e.check(pid==channel.pid,'original-helper-pid');channel.owner=instance
            original=e.runtime.register(name,channel)
            e.states['PF']['actors'][name].update(instance=instance,runtime=runtime,creationTime100ns=original['creationTime100ns']);return {'instance':instance,'runtime':runtime}
        f.n('hello'+name,hello)
    o.res();o.guard();o.open_j();o.ref()
    def identity():
        g=e.object(o.rid('guard'));r=e.object(e.states['PF']['currentRef']);j=e.object(e.states['PF']['currentH']);e.check(g['identity']==r['identity'],'guard-reference-physical-identity');e.check(g['length']==j['length']==4096,'java-guard-length');return {'identity':g['identity']}
    f.n('identity',identity)
    j=o.read_j(0,16);r=o.read_r(0,16);e.check(j['sha']==r['sha'],'preflight-independent-real-bytes')
    o.seal();o.close_j();o.close_r();o.close_guard();o.end()
    f.n('caps',lambda:{'windowsDup':'REAL_KERNEL_BINDING','durability':'OS_DATA_SYNC_ONLY','namespace':'UNPROVEN','mediaRead':'AUTHORIZED_R2_LIMITED_BYTES_ONLY' if real else 'SYNTHETIC_FIXTURES_ONLY',
                       'sourceVersion':'OPENED_IDENTITY_LENGTH_MTIME_SHARE_READ_DURING_CONTROLLED_ACCESS','wholeFileSnapshot':False,'existingWritableMappingsBlocked':False})
    f.finish();e.check(e.source_view(e.states['PF'])['state']=='DRAINED','preflight-references-returned')

class Cleanup:
    def __init__(self,e):
        self.e=e;self.f=e.begin('GC');self.proofs={};self.steps=[]
        # A still-running external callback owns its references. Do not close
        # helpers/descriptors under it merely because the Future is already done.
        e.completions.drain(timeout=min(.2,max(.001,e.budget.remaining('GC'))))
    def invoke(self,label,action,target='PF',args=None):
        result=self.f.n(label,action,journal_task=target,args=args);self.steps.append(dict(slot=self.f.ni,target=target,result=result));return result
    def active_task(self,domain=None):
        for task,s in reversed(list(self.e.states.items())):
            if task=='PF':continue
            if domain and s['domain']!=domain:continue
            if any(r['disposition'] not in CLOSED for r in s['objects'].values()) or any(not c['finished'] for v in s['versions'].values() for c in v['consumers'].values()):return task
        return 'PF'
    def resource(self,actor,role):
        for task,s in reversed(list(self.e.states.items())):
            for key,r in s['objects'].items():
                if r['actor']==actor and r['role']==role and r['disposition'] not in CLOSED:return task,key,r
        return None
    def safe_close(self,actor,role,label):
        found=self.resource(actor,role);target=found[0] if found else 'PF'
        def act():
            if not found:return {'skipped':'ALREADY_PROVEN'}
            task,key,r=found
            if r['disposition']!='OWNED_OPEN_RETRYABLE' or r['attempts']>=3 or r.get('transportPending'):return {'skipped':'NOT_SAFE_TO_RETRY','ticket':r['ticket']}
            if actor=='G':r.update(self.e.native.close(key));return {'closed':key}
            reply=self.e.remote(actor,'CLOSE',[key,r['revision'],'none'] if actor=='J' else [key,'None'],task=task)
            # Proof is applied to the original task, not the GC header task.
            if actor=='J':
                p=reply.split('|');need(p[0]==r['object'] and p[1]==r['ticket'],'CLOSE_PROOF_IDENTITY');r.update(disposition=p[2],attempts=int(p[3]),nativeCloses=int(p[4]),revision=int(p[5]),first=p[6])
            else:
                p=reply['ticket'];need(p['objectId']==r['object'] and p['ticket']==r['ticket'],'CLOSE_PROOF_IDENTITY');r.update(disposition=['OWNED_OPEN_RETRYABLE','IN_FLIGHT','CLOSED_PROVEN','UNKNOWN','RELEASED_BY_OWNER_EXIT'][p['disposition']],nativeCloses=p['delegateCalls'])
            if r['disposition']=='CLOSED_PROVEN':self.e.ledger.release(key,'NATIVE_CLOSE_RETURNED')
            return {'disposition':r['disposition'],'closed':key}
        return self.invoke(label,act,target)
    def owner_notice(self,actor,domain):
        proof=self.proofs.get(actor);owner=self.e.channels[actor].owner
        matches=[]
        for task,s in self.e.states.items():
            for key,r in s['objects'].items():
                source=r['role'] in ('H','REF')
                if r['owner']==owner and r['disposition'] not in CLOSED and source==(domain=='source'):matches.append((task,key,r))
        targets={m[0] for m in matches};need(len(targets)<=1,'MULTIPLE_ACTIVE_TASKS_AT_STOP');target=next(iter(targets),'PF')
        def act():
            need(proof and proof['exited'] and proof['instance']==owner,'OWNER_EXIT_NOT_PROVEN')
            for task,key,r in matches:
                r['originalCloseDisposition']=r['disposition'];r['disposition']='RELEASED_BY_OWNER_EXIT';r['exitProof']=copy.deepcopy(proof)
                self.e.ledger.release(key,'OWNER_EXIT_PROVEN')
                for operation,op in self.e.states[task]['ops'].items():
                    # Child exit proves its references, not release of G's private
                    # result cell. Only that cell's actual drain may finish it.
                    cell=self.e.cells.get(operation)
                    if r['actor']==actor and (cell is None or cell.released):op['done']=True
            return {'owner':owner,'references':len(matches),'exited':True}
        return self.invoke('notice-'+actor+'-'+domain,act,target)
    def end_consumer(self,index):
        target=self.active_task();s=self.e.states[target]
        consumers=[(v,name,c) for v,entry in s['versions'].items() for name,c in entry['consumers'].items() if not c['finished']]
        selected=consumers[index] if len(consumers)>index else None
        def act():
            if not selected:return {'skipped':'NO_CONSUMER'}
            v,name,c=selected;c['finished']=True;view=self.e.source_view(s,v);return {'consumer':name,'state':view['state']}
        return self.invoke('end',act,target)
    def run(self):
        e=self.e
        self.invoke('sourceFence',lambda:self.fence('source'))
        self.invoke('sinkFence',lambda:self.fence('sink'))
        self.invoke('cancel',lambda:self.cancel_consumer(0),self.active_task())
        self.invoke('cancel',lambda:self.cancel_consumer(1),self.active_task())
        self.invoke('abort',self.abort_active,self.active_task('sink'))
        for kind in ('open','read','output','validation'):self.invoke('gate',lambda kind=kind:self.release_gate(kind),self.active_task())
        self.safe_close('J','H','ch');self.safe_close('G','guard','cg');self.safe_close('R','REF','cr');self.safe_close('R','A','ca');self.safe_close('R','B','cb');self.safe_close('R','V','cv')
        for actor in ('J','R'):
            def exit_actor(actor=actor):
                e.runtime.exits_in_progress=True
                reply=e.remote(actor,'EXIT')
                if actor=='J':
                    values=reply.split('|');need(len(values)==3 and values[0]==e.channels[actor].owner and values[2]=='512','HELPER_IDENTITY_EXIT_PROOF');queries=int(values[1])
                else:
                    need(reply.get('instance')==e.channels[actor].owner and reply.get('identityQueryLimit')==512,'HELPER_IDENTITY_EXIT_PROOF');queries=reply.get('identityQueries')
                need(type(queries) is int and 0<=queries<=512,'HELPER_IDENTITY_QUERY_CAP');e.identity_facts[actor]=queries
                proof=e.io_call(e.channels[actor].exited,timeout=min(5,max(.001,e.budget.remaining('GC'))));self.proofs[actor]=proof;e.states['PF']['actors'][actor]['exit']=proof;e.runtime.retired(actor,proof)
                if actor=='R':e.runtime.exits_in_progress=False
                return proof
            self.invoke('exit'+actor,exit_actor)
        self.owner_notice('J','source');self.owner_notice('R','source');self.owner_notice('R','sink')
        self.end_consumer(0);self.end_consumer(0)
        for actor in ('J','R'):
            for which in ('in','out','err'):self.invoke('pipeClose',lambda actor=actor,which=which:e.channels[actor].close_pipe(which),args=[actor,which])
        for actor in ('J','R'):self.invoke('processClose',e.channels[actor].close_process_handle,args=actor)
        def finish_workers():
            e.completions.close(timeout=min(1,max(.001,e.budget.remaining('GC'))))
            return {'openMetadata':sum(r['kind']=='metadata' for k,r in e.ledger.live.items() if k!='global-log'),'callbackWorkers':e.completions.pending()}
        self.invoke('journalClose',finish_workers)
        e.check(self.f.ni==31,'gc-first-31-exact-slots');e.check(all(c.proof and c.proof['exited'] for c in e.channels.values()),'both-original-helpers-exited')
    def fence(self,domain):
        with self.e.lock:
            if domain=='source':self.e.source.fence()
            self.e.states['PF'][domain+'Fenced']=True
            for s in self.e.states.values():
                if s['domain']==domain:s['globalFence']=True
        return {'fenced':domain}
    def cancel_consumer(self,index):
        task=self.active_task();s=self.e.states[task];consumers=[c for v in s['versions'].values() for c in v['consumers'].values() if not c['finished']]
        if len(consumers)>index:consumers[index]['cancelled']=True
        return {'cancelled':index if len(consumers)>index else None}
    def abort_active(self):
        task=self.active_task('sink');s=self.e.states[task]
        if s.get('state') not in ('READY','ABORTED',None):s.update(abortOnly=True,abortRequested=True,state='ABORT_PENDING')
        return {'task':task,'state':s.get('state','NONE')}
    def release_gate(self,kind):
        # Operates only on already admitted operations; no new allocation or read.
        if kind in ('open','read'):
            for operation,cell in list(self.e.cells.items()):
                if cell.kind==kind and not cell.released:
                    cell.cancel('CANCELLED')
                    if not cell.gated:cell.gate()
                    return dict(released=operation,privateReleased=cell.released,discarded=cell.discarded,nativeReturned=cell.native_done,consumerDelivered=cell.deliveries)
        for task,s in self.e.states.items():
            if kind=='validation' and s.get('validatorHeld'):s['validatorHeld']=False;return {'released':s['V']}
            if kind=='output':
                for key,r in s['objects'].items():
                    if r.get('transportPending'):
                        reply=self.e.remote('R','GATE_CLOSE',[key],task=task);p=reply['ticket'];r.update(disposition=['OWNED_OPEN_RETRYABLE','IN_FLIGHT','CLOSED_PROVEN','UNKNOWN','RELEASED_BY_OWNER_EXIT'][p['disposition']],transportPending=False,nativeCloses=p['delegateCalls']);self.e.ledger.release(key,'NATIVE_CLOSE_RETURNED');return {'released':key}
        return {'skipped':'NO_GATE'}
    def finish(self,report):
        """GC/n32 runs after final accounting. No disk write occurs after the actual close."""
        e=self.e;f=self.f;e.store.ensure_writable();Engine.compact_cells(e)
        e.check(all(cell.released for cell in e.cells.values()),'all-private-result-cells-released-before-final-close')
        e.check(not e.cells,'all-private-result-cells-quiescent-before-final-close')
        report['privateCells']=Engine.cell_facts(e);report['cellHistory']=[item.as_dict() for item in e.cell_history];report['assertions']=e.assertions
        report['callbackHub']=e.completions.pending();hub=report['callbackHub']
        e.check(hub['workersAlive']==0 and hub['cells']==0 and hub['lifecycle']=='CLOSED' and not hub['remainingCredits'] and not hub['ownershipPending'] and hub['startupError'] is None,'callback-workers-actually-joined');report['assertions']=e.assertions
        e.runtime.finish();report['runtimeObservation']=e.runtime.facts()
        report['assertionEvidence']=copy.deepcopy(e.assertionEvidence)
        e.identity_facts['G']=e.native.identity_queries
        report['identityQueries']=copy.deepcopy(e.identity_facts)
        assertion_sha=sha(json.dumps(report['assertionEvidence'],sort_keys=True,separators=(',',':'),ensure_ascii=True).encode('ascii'))
        report['actualRegressionAdmission']=getattr(e,'actual_regression_claim',None)
        e.budget.ends['GC']=min(e.budget.started+180,time.monotonic()+10);f.ni+=1;e.budget.charge('GC',n=1);id='GC/n32';s=e.states['PF'];s['usage']['GC']=copy.deepcopy(e.budget.used['GC']);s['finalBudget']=copy.deepcopy(e.budget.globalused);s['globalLogOutcome']='RETURN_CHANNEL_REQUIRED';s['commands'][id]={'status':'ADMITTED','kind':'N','label':'logClose'}
        e.save('PF');e.event({'id':id,'phase':'READY_TO_CLOSE','scope':'RETURN_CHANNEL_WITNESS'})
        report['usage']=copy.deepcopy(e.budget.globalused);report['metadataRequestedBeforeFinalReceipt']=e.store.requested;report['metadataWrittenBeforeFinalReceipt']=e.store.written;report['metadataUnknownRequestedBytes']=e.store.unknown_requested_bytes;report['metadataCommitStatus']=e.store.commit_status;report['metadataPeakBeforeFinalReceipt']=e.store.peak;report['ledgerPeaks']={'os':e.ledger.peak,'media':e.ledger.media_peak,'buffers':e.ledger.buffer_peak};report['logClose']='PENDING_RETURN_CHANNEL'
        data=compact(report);need(len(data)<=131072,'FINAL_RECEIPT_LIMIT')
        e.store.write_receipt(data)
        s['commands'][id]['status']='READY_TO_CLOSE';e.save('PF')
        need(not any(not f.done() for f in e.pending.values()),'NATIVE_TASKS_PENDING_AT_FINAL_CLOSE');e.io.shutdown(wait=True)
        e.store.close_log();e.global_close={'closed':True,'id':id,'method':'flush/fsync/close actually returned','exitedHelpers':self.proofs,'remainingResources':len(e.ledger.live)}
        real=e.profile['kind']=='REAL_IO'
        report.update(logClose=e.global_close,remainingResources=len(e.ledger.live),scope='E3_REAL_IO_TOOL_ONLY' if real else 'E3_SYNTHETIC_INTEGRATION_ONLY',mediaRead=real,realPFRun=real,real61Run=False,completionRequiresWrapperEvaluation=True)
        return dict(scope=report['scope'],root=e.root.name,
                    status=report['status'],assertions=report['assertions'],rows=len(report['rows']),
                    usage=report['usage'],logClose=e.global_close,metadataPeak=e.store.peak,
                    metadataRequested=e.store.requested,metadataWritten=e.store.written,metadataUnknownRequestedBytes=e.store.unknown_requested_bytes,metadataCommitStatus=e.store.commit_status,ledgerPeaks=report['ledgerPeaks'],privateCells=report['privateCells'],callbackHub=report['callbackHub'],
                    runtimeObservation=report['runtimeObservation'],
                    actualRegressionAdmission=report['actualRegressionAdmission'],
                    precloseSummarySha=sha(data),precloseSummary='result-before-close.json',assertionEvidenceCount=len(report['assertionEvidence']),assertionEvidenceSha256=assertion_sha,
                    identityQueries=copy.deepcopy(e.identity_facts),mediaRead=real,realPFRun=real,real61Run=False,completionRequiresWrapperEvaluation=True)
