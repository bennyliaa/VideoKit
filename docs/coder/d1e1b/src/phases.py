from __future__ import annotations
import base64, copy, json, os, time
from gcore import *
from gengine import Ops,CLOSED,Flow

def preflight(e):
    f=e.begin('PF');o=Ops(e)
    def setup():
        p=e.root/'global.log';e.store.reserve_file(p,131072);e.ledger.acquire('global-log','G','metadata');e.global_log=open(p,'wb',buffering=0);e.global_log.write(b'E1B SYNTHETIC TOOL INTEGRATION\n');e.store.log=e.global_log;return {'scope':'SYNTHETIC_ONLY'}
    f.n('setup',setup)
    for name in ('J','R'):
        def start(name=name):
            e.channels[name]=Channel(name,e.root,e.key,e.ledger);c=e.channels[name];e.states['PF'].setdefault('actors',{})[name]={'pid':c.pid,'started':c.started,'instance':None};return {'started':name,'pid':c.pid}
        f.n('start'+name,start)
    for name in ('J','R'):
        def hello(name=name):
            value=e.remote(name,'HELLO');channel=e.channels[name]
            if name=='J':instance,pid,runtime=value.split('|');pid=int(pid)
            else:instance,pid,runtime=value['instance'],value['pid'],value['runtime']
            e.check(pid==channel.pid,'original-helper-pid');channel.owner=instance;e.states['PF']['actors'][name].update(instance=instance,runtime=runtime);return {'instance':instance,'runtime':runtime}
        f.n('hello'+name,hello)
    o.res();o.guard();o.open_j();o.ref()
    def identity():
        g=e.object(o.rid('guard'));r=e.object(e.states['PF']['currentRef']);j=e.object(e.states['PF']['currentH']);e.check(g['identity']==r['identity'],'guard-reference-physical-identity');e.check(g['length']==j['length']==4096,'java-guard-length');return {'identity':g['identity']}
    f.n('identity',identity)
    j=o.read_j(0,16);r=o.read_r(0,16);e.check(j['sha']==r['sha'],'preflight-independent-real-bytes')
    o.seal();o.close_j();o.close_r();o.close_guard();o.end()
    f.n('caps',lambda:{'windowsDup':'REAL_KERNEL_BINDING','durability':'OS_DATA_SYNC_ONLY','namespace':'UNPROVEN','mediaRead':'SYNTHETIC_FIXTURES_ONLY'})
    f.finish();e.check(e.source_view(e.states['PF'])['state']=='DRAINED','preflight-references-returned')

class Cleanup:
    def __init__(self,e):self.e=e;self.f=e.begin('GC');self.proofs={};self.steps=[]
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
                for op in self.e.states[task]['ops'].values():
                    if r['actor']==actor:op['done']=True
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
                e.remote(actor,'EXIT');proof=e.io_call(e.channels[actor].exited,timeout=min(5,max(.001,e.budget.remaining('GC'))));self.proofs[actor]=proof;e.states['PF']['actors'][actor]['exit']=proof;return proof
            self.invoke('exit'+actor,exit_actor)
        self.owner_notice('J','source');self.owner_notice('R','source');self.owner_notice('R','sink')
        self.end_consumer(0);self.end_consumer(0)
        for actor in ('J','R'):
            for which in ('in','out','err'):self.invoke('pipeClose',lambda actor=actor,which=which:e.channels[actor].close_pipe(which),args=[actor,which])
        for actor in ('J','R'):self.invoke('processClose',e.channels[actor].close_process_handle,args=actor)
        self.invoke('journalClose',lambda:{'openMetadata':sum(r['kind']=='metadata' for k,r in e.ledger.live.items() if k!='global-log')})
        e.check(self.f.ni==31,'gc-first-31-exact-slots');e.check(all(c.proof and c.proof['exited'] for c in e.channels.values()),'both-original-helpers-exited')
    def fence(self,domain):
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
        for task,s in self.e.states.items():
            for key,op in s['ops'].items():
                if not op['done'] and key.endswith('/'+kind):op['done']=True;return {'released':key}
            if kind=='validation' and s.get('validatorHeld'):s['validatorHeld']=False;return {'released':s['V']}
            if kind=='output':
                for key,r in s['objects'].items():
                    if r.get('transportPending'):
                        reply=self.e.remote('R','GATE_CLOSE',[key],task=task);p=reply['ticket'];r.update(disposition=['OWNED_OPEN_RETRYABLE','IN_FLIGHT','CLOSED_PROVEN','UNKNOWN','RELEASED_BY_OWNER_EXIT'][p['disposition']],transportPending=False,nativeCloses=p['delegateCalls']);self.e.ledger.release(key,'NATIVE_CLOSE_RETURNED');return {'released':key}
        return {'skipped':'NO_GATE'}
    def finish(self,report):
        """GC/n32 runs after final accounting. No disk write occurs after the actual close."""
        e=self.e;f=self.f;e.budget.ends['GC']=min(e.budget.started+180,time.monotonic()+10);f.ni+=1;e.budget.charge('GC',n=1);id='GC/n32';s=e.states['PF'];s['usage']['GC']=copy.deepcopy(e.budget.used['GC']);s['finalBudget']=copy.deepcopy(e.budget.globalused);s['globalLogOutcome']='RETURN_CHANNEL_REQUIRED';s['commands'][id]={'status':'ADMITTED','kind':'N','label':'logClose'}
        e.save('PF');e.event({'id':id,'phase':'READY_TO_CLOSE','scope':'RETURN_CHANNEL_WITNESS'})
        report['usage']=copy.deepcopy(e.budget.globalused);report['metadataWritten']=e.store.written;report['metadataPeakBeforeFinalReceipt']=e.store.peak;report['ledgerPeaks']={'os':e.ledger.peak,'media':e.ledger.media_peak,'buffers':e.ledger.buffer_peak};report['logClose']='PENDING_RETURN_CHANNEL'
        data=compact(report);need(len(data)<=131072,'FINAL_RECEIPT_LIMIT')
        with e.store.file(e.root/'result-before-close.json','wb',131072) as file:file.write(data);file.flush();os.fsync(file.fileno())
        s['commands'][id]['status']='READY_TO_CLOSE';e.save('PF')
        need(not any(not f.done() for f in e.pending.values()),'NATIVE_TASKS_PENDING_AT_FINAL_CLOSE');e.io.shutdown(wait=True)
        e.global_log.flush();os.fsync(e.global_log.fileno());e.global_log.close();e.ledger.release('global-log','NATIVE_CLOSE_RETURNED');e.global_close={'closed':True,'id':id,'method':'flush/fsync/close actually returned','exitedHelpers':self.proofs,'remainingResources':len(e.ledger.live)}
        report.update(logClose=e.global_close,remainingResources=len(e.ledger.live),scope='E1B_SYNTHETIC_INTEGRATION_ONLY',mediaRead=False,realPFRun=False,real61Run=False)
        return dict(scope='E1B_SYNTHETIC_INTEGRATION_ONLY',root=e.root.name,
                    status=report['status'],assertions=report['assertions'],rows=len(report['rows']),
                    usage=report['usage'],logClose=e.global_close,metadataPeak=e.store.peak,
                    metadataWritten=e.store.written,ledgerPeaks=report['ledgerPeaks'],
                    precloseSummarySha=sha(data),precloseSummary='result-before-close.json',
                    mediaRead=False,realPFRun=False,real61Run=False)
