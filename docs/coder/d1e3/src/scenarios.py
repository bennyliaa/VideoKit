"""All 61 concrete scenarios. Same orchestration for the synthetic binding profile and
the future approved-media profile; E1B CLI never supplies the latter capability.
"""
from __future__ import annotations
import base64, copy, json, os, threading, time
from concurrent.futures import ThreadPoolExecutor
from gcore import *
from gengine import Engine,Ops,CLOSED
from profile_bindings import boundary_for

class Scenarios:
    def __init__(self,e):self.e=e;self.o=Ops(e);self.payload=None;self.open_cmd='';self.claim_cmd='';self.old_close='';self.s17d='';self.s17c='';self.pending_a=None
    @property
    def f(self):return self.e.flow
    @property
    def s(self):return self.e.states[self.f.task]
    def check(self,value,label):self.e.check(value,label)
    def reject(self,action,expected):
        try:action()
        except Refused as error:self.check(str(error)==expected,'expected-'+expected);return
        raise Refused('ASSERT:MISSING_REJECTION:'+expected)
    def pair(self,offset,n,c='a',cap=65536):
        j=self.o.read_j(offset,n,cap,c=c);r=self.o.read_r(offset,n);self.check(j['n']==r['n'] and j['sha']==r['sha'],'independent-bytes-and-sha');return j
    def close_source(self,reference=True,c='a'):
        self.o.seal();self.o.close_j()
        if reference:self.o.close_r()
        self.o.close_guard();self.o.end(c)
        self.check(self.e.source_view(self.s)['state']=='DRAINED','source-real-resources-drained')
    def create_writer(self):
        self.o.grant();self.o.alloc();self.o.dup();self.o.send();self.o.take();self.o.claim()
    def run(self,row):
        e=self.e;o=self.o
        if row.startswith('P01-N'):
            if row=='P01-N1':o.res();o.guard();o.open_j();o.ref()
            index=int(row[-1])-1;length=e.object(self.s['currentH'])['length'];b=boundary_for(e.profile)
            offset=[b-65536,b-32768,b,length-65536][index];reply=self.pair(offset,65536);self.check(reply['n']==65536,'full-window-synthetic' if b==65536 else 'full-window')
        elif row=='P02-EOF':
            reply=o.read_j(e.object(self.s['currentH'])['length'],1);self.check(reply['n']==-1,'positive-request-real-eof')
        elif row=='P02-ZERO':
            before=e.object(self.s['currentH'])['nativeReads'];value=o.read_zero();self.check(value['n']==0 and value['nativeReads']==0 and e.object(self.s['currentH'])['nativeReads']==before,'actual-bridge-zero-no-provider-io');self.close_source()
        elif row.startswith('P01-S'):
            if row=='P01-S1':o.res();o.guard();o.open_j();o.ref()
            index=int(row[-1])-1;length=e.object(self.s['currentH'])['length'];b=boundary_for(e.profile);offset=[b-65536,b-32768,b,length-65536][index]
            prefix=b''
            for n in range(4):value=o.read_j(offset+n,65536-n,1);self.check(value['n']==1,'legal-short-read');prefix+=base64.b64decode(value['bytes'])
            ref=o.read_r(offset,4);self.check(ref['sha']==sha(prefix),'four-byte-prefix-independent')
            self.s['windowOutcome']='UNFILLED';self.s['windowBytesObserved']=len(prefix)
            self.reject(lambda:e.budget.charge(row,ib=65532,ic=1),'BUDGET_STOP:ib');self.check(e.budget.used[row]['ib']==262142,'no-failed-reservation-refund-or-charge')
            if row=='P01-S4':self.close_source()
        elif row=='P03-RAW':
            o.res();o.guard();o.open_j();self.check(o.read_j(0,16)['n']==-1,'empty-real-file-eof')
        elif row=='P03-MEDIA':self.reject(o.media_preflight,'EMPTY_MEDIA');self.close_source(False)
        elif row=='P04-SEQ':o.res();o.guard();o.open_j();o.ref();self.s['declaredLength']=None;self.pair(0,32)
        elif row=='P04-CPU':self.reject(o.cpu_preflight,'SOURCE_CAPABILITY_UNSUPPORTED');self.close_source()
        elif row=='P05-SHORT7':
            o.res();o.guard();o.open_j();o.ref();actual=b''
            for n in [32,25,18,11,4]:actual+=base64.b64decode(o.read_j(len(actual),n,7)['bytes'])
            ref=o.read_r(0,32);self.check(len(actual)==32 and sha(actual)==ref['sha'],'five-short-reads-complete-32');self.close_source()
        elif row=='P06-ZERO':
            o.res();o.guard();o.open_j();self.reject(lambda:o.read_j(0,32,zero=True),'INVALID_PROVIDER_RESULT');self.close_source(False)
        elif row=='P07-EARLY':
            o.res();o.guard();o.open_j();self.reject(lambda:o.read_j(4096,1,declared=4097),'EARLY_EOF');self.close_source(False)
        elif row=='P08-LATEOPEN':
            o.res();o.guard();cell=o.open_j(hold=True);self.check(cell.native_done and not cell.response.done() and cell.deliveries==0,'open-native-returned-response-still-waiting')
            o.seal();o.cancel_source();self.reject(lambda:cell.response.result(timeout=.1),'CANCELLED');q=self.f.query();self.check(q['operations']==1 and q['state']=='PENDING' and cell.retained,'late-open-private-result-retained')
            o.gate('open');self.check(cell.discarded and cell.released and cell.deliveries==0,'late-open-never-delivered');o.close_j();o.close_guard();o.end();self.check(e.view()['state']=='DRAINED','late-open-closed-not-delivered')
        elif row in ('P09-CANCEL','P09-TIMEOUT'):
            o.res();o.guard();o.open_j();cell=o.read_j(0,32,hold=True);self.check(cell.native_done and not cell.response.done() and e.ledger.buffers==1,'read-response-pending-private-buffer-held')
            if row=='P09-CANCEL':
                o.cancel_source();self.reject(lambda:cell.response.result(timeout=.1),'CANCELLED');self.check(self.f.query()['operations']==1 and e.ledger.buffers==1,'cancel-does-not-release-private-buffer');o.seal()
            else:
                self.check(self.f.query()['operations']==1,'read-active-before-timeout');self.reject(lambda:cell.response.result(timeout=1.5),'SOURCE_TIMEOUT');self.check(self.f.query()['operations']==1 and e.ledger.buffers==1,'timeout-retains-private-buffer');o.seal()
            o.gate('read');self.check(cell.discarded and cell.released and cell.deliveries==0 and e.ledger.buffers==0,'gate-discards-private-buffer-without-delivery');o.close_j();o.close_guard();o.end();self.check(e.view()['state']=='DRAINED','private-read-completion-drained')
        elif row=='P10-A':
            o.res();o.guard();o.open_j();o.seal();r=o.close_j(fault='before');self.check(r['attempts']==1 and r['nativeCloses']==0,'before-delegate-failure')
            self.f.query();revision=r['revision']
            def attempt():
                try:o.close_j(expected=revision,label='retry');return 'closed'
                except Refused as ex:return str(ex)
            with ThreadPoolExecutor(max_workers=2) as pool:results=list(pool.map(lambda _:attempt(),range(2)))
            self.check(results.count('closed')==1 and any(v in ('STALE_REVISION','CLOSE_NOT_RETRYABLE') for v in results),'same-revision-concurrent-one-native-close')
            self.check(e.object(self.s['currentH'])['nativeCloses']==1,'no-double-delegate');o.close_guard();o.end()
        elif row=='P10-B':
            o.res();o.guard();o.open_j('old');old=self.s['currentH'];o.close_j(fault='ack');command=self.f.current_id;self.f.query();o.open_j('new');o.ref();self.pair(0,32)
            o.close_j(old,replay=command);self.reject(lambda:o.close_j(old,expected=0,label='retry'),'STALE_REVISION');self.check(e.object(old)['nativeCloses']==1,'closed-old-not-reclosed');self.close_source()
        elif row=='P11-FUTURE':
            o.res('a');o.res('b');o.guard();o.open_j('HA','a');o.ref();first=o.read_j(0,16,c='a');reference=o.read_r(0,32);o.close_j();o.end('a');q=self.f.query();self.check(q['reservations']==1,'future-consumer-prevents-release')
            o.open_j('HB','b');second=o.read_j(16,16,c='b');self.check(sha(base64.b64decode(first['bytes'])+base64.b64decode(second['bytes']))==reference['sha'],'two-consumer-data-independent-reference');o.seal();o.close_j();o.close_r();o.close_guard();o.end('b');self.check(e.view()['state']=='DRAINED','two-consumers-real-handles-finished')
        elif row=='P11-SEALED':
            o.res('a');o.res('b');o.guard();o.open_j('HA','a');o.ref();self.pair(0,16);o.close_j();o.end('a');o.seal();self.f.query();self.reject(lambda:o.open_j('HB','b'),'SESSION_RELEASED');o.close_r();o.close_guard();o.end('b')
        elif row=='P12-OLDOPEN':
            o.res('a');o.guard();o.open_j('H1');o.ref();self.pair(0,16);self.close_source();o.version('v2');o.res('b');o.guard();o.open_j('H2','b');o.ref();self.pair(0,16,c='b');o.close_j();o.close_r();o.close_guard();o.end('b')
            self.reject(lambda:o.open_j('old','a','v1'),'SESSION_RELEASED');self.check(not self.s['versions']['v2']['sealed'],'v2-active-does-not-inherit-seal')
        elif row=='P12-NOTICE':
            before=copy.deepcopy(self.s['versions']['v2']);self.f.n('notice',lambda:self.s.setdefault('notices',{}).update(v1=1),args=['v1',1]);self.check(self.s['versions']['v2']==before,'old-notice-cannot-seal-or-release-v2')
        elif row=='P12-CHANGED':o.version('v3');o.seal('v2');self.check(e.source_view(self.s,'v2')['state']=='DRAINED','trusted-version-event-not-file-modification')
        elif row=='P13-SEQ':o.res();o.guard();o.open_j();o.ref();self.s['sequentialOnly']=True;self.pair(0,8)
        elif row=='P13-SEEK':
            self.reject(lambda:self.source_seek(),'SEEK_UNSUPPORTED');self.close_source()
        elif row=='P10-D':
            o.res();o.guard();o.open_j('D');self.s17d=self.s['currentH'];o.open_j('C');self.s17c=self.s['currentH'];o.seal();o.close_j(self.s17d,'before',True);o.close_j(self.s17c,'unknown',True)
            o.gate('close',self.s17d);self.f.query();o.close_j(self.s17d,'before',label='retry');self.f.query();o.close_j(self.s17d,'before',label='retry');self.reject(lambda:o.close_j(self.s17d,'before',label='retry'),'EXHAUSTED')
            self.check(e.object(self.s17d)['attempts']==3 and e.object(self.s17d)['nativeCloses']==0,'safe-attempt-exhaustion-no-fourth')
        elif row=='P10-C':
            o.gate('close',self.s17c);self.f.query();self.reject(lambda:o.close_j(self.s17c,label='retry'),'CLOSE_NOT_RETRYABLE');self.f.query();self.f.n('retire',lambda:self.s.update(fenced=True),args='old-owner')
            self.reject(lambda:o.close_j(self.s17c,label='retry'),'CLOSE_NOT_RETRYABLE');self.check(e.object(self.s17c)['disposition']=='UNKNOWN' and e.object(self.s17c)['nativeCloses']==1,'actual-close-return-hidden-still-unknown')
        elif row=='Q09-OPEN2':
            o.grant();self.open_cmd=self.f.current_id;o.grant(replay=self.open_cmd);self.check(len(self.s['objects'])==0,'two-opens-only-metadata')
        elif row=='Q09-CLAIM':o.alloc();o.dup();o.send();o.take();o.claim();self.claim_cmd=self.f.current_id;self.check(self.s['confirmed'],'unique-confirmed-writer')
        elif row=='Q09-SECOND':self.reject(lambda:o.claim(bad='receiver'),'CLAIM_CONFLICT');self.reject(lambda:o.claim(bad='claim'),'CLAIM_CONFLICT')
        elif row=='Q09-REPLAY':o.grant(replay=self.open_cmd);o.claim(replay=self.claim_cmd);self.check(self.s['claimed'] and len(self.s['objects'])==2,'replays-never-owning-wrapper')
        elif row in ('Q09-PLAN','Q09-SOURCE','Q09-PRESET'):self.reject(lambda:o.grant(change=row),'INTENT_CONFLICT')
        elif row=='Q01-SEQ':
            o.res('src');o.guard();o.open_j(c='src');o.ref();j=self.pair(0,32,c='src');self.payload=base64.b64decode(j['bytes']);o.seal();o.close_j();o.close_r();o.close_guard();o.write(0,self.payload);o.flush();o.close_b();o.close_a();o.vopen();o.vread();o.vclose();o.end('src');reply=o.ready();self.check(reply['token'] is None and reply['ack']=='INJECTED_LOST_RESPONSE','ready-commit-before-reply-loss');self.check(self.s['state']=='READY','actual-byte-probe-ready')
        elif row=='Q05-STREAM':self.check(self.s['state']=='READY' and self.s['spent']==32,'unknown-space-bounded-success')
        elif row=='Q06-LOST':
            token=self.s['token'];self.f.n('recoverJournal',lambda:e.remote('J','RECOVER',[self.f.task]));self.check(self.s['token']==token and self.s['state']=='READY' and self.s['recovered'],'cold-authority-reloaded-from-independent-reader')
        elif row=='Q08-READY':o.cancel_output();self.check(self.s['state']=='READY','ready-wins-lost-cancel-reply')
        elif row=='Q07-READYFIRST':token=self.s['token'];o.takeover();o.cancel_output('abort');self.check(self.s['state']=='READY' and self.s['token']==token and self.s['epoch']==1,'ready-before-takeover-stable-token')
        elif row=='Q04-DUP':self.create_writer();o.close_a();o.write(0,self.payload[:1]);self.check(e.object(self.s['A'])['disposition']=='CLOSED_PROVEN' and self.s['spent']==1,'real-B-survives-A-close')
        elif row=='Q02-RANDOM':
            for offset,data in [(7,b'abc'),(0,b'Z'),(2,b'xy')]:o.seek_write(offset,data)
            o.flush();o.close_b();o.vopen();o.vread();o.vclose()
        elif row=='Q08-VALIDATOR':o.vopen();o.vread(True);o.cancel_output();self.check(self.f.query()['validators']==1,'held-validator-pending');o.gate('validation');o.vclose();self.check(self.s['state']=='ABORTED','validator-return-allows-abort')
        elif row=='Q04-CLOSEACK':self.create_writer();o.write(0,self.payload[:1]);o.flush();o.close_b(True);self.check(e.object(self.s['B'])['nativeCloses']==1 and self.f.query()['refs']==1,'B-close-proven-A-still-live')
        elif row=='Q08-WRITER':self.hold_a();o.cancel_output();self.check(self.f.query()['refs']==1,'A-close-inflight-prevents-abort');self.gate_a();self.check(self.s['state']=='ABORTED','A-actual-close-completes-abort')
        elif row=='Q05-SPACEFAIL':self.create_writer();o.write(0,self.payload[:1]);self.reject(lambda:o.write(1,self.payload[:1],True),'OUTPUT_SPACE_INSUFFICIENT');self.check(self.s['spent']==2,'failed-write-request-retains-credit')
        elif row=='Q08-UNKNOWN':o.cancel_output();self.check(self.f.query()['refs']==2 and self.s['state']=='ABORT_PENDING','unknown-cancel-keeps-both-descriptors')
        elif row=='Q08-DRAIN':o.close_a();o.close_b();self.check(self.s['state']=='ABORTED','both-native-closes-abort')
        elif row=='Q07-TAKEFIRST':
            self.create_writer();o.write(0,self.payload);o.flush();o.close_b();o.close_a();o.vopen();o.vread();o.vclose();request=o.ready_request();original=copy.deepcopy(request);self.f.query();o.takeover();self.reject(lambda:o.ready(request),'STALE_OWNER');self.check(request==original and request['epoch']==1 and self.s['epoch']==2 and request['ownerInstance']!=self.s['ownerInstance'],'original-e1-request-rejected-by-persisted-e2-owner');o.cancel_output('abort');self.check(self.s['state']=='ABORTED' and self.s['epoch']==2,'fourteen-independent-controls-takeover-first')
        elif row.startswith('Q09-W'):
            window=int(row[-1]);o.grant()
            if window>=1:o.alloc()
            if window>=2:o.dup()
            if window>=3:o.send(window==3)
            if window>=4:o.take()
            if window>=5:o.claim(True)
            if window in (3,5):self.f.query()
            o.takeover()
            if window>=1:o.close_a()
            if window>=2:o.close_b()
            o.cancel_output('abort');self.check(self.s['state']=='ABORTED','owner-retirement-window-'+str(window))
        elif row=='Q03-RANDOM':self.reject(lambda:o.grant(deny='RANDOM_REQUIRED'),'RANDOM_REQUIRED')
        elif row=='Q03-VERIFY':self.reject(lambda:o.grant(deny='VALIDATION_REQUIRED'),'VALIDATION_REQUIRED')
        elif row=='Q09-ALIAS':self.reject(lambda:o.grant(alias=True),'INPUT_ALIAS')
        else:raise Stop('UNIMPLEMENTED_SCENARIO:'+row)
    def source_seek(self):
        need(not self.s.get('sequentialOnly'),'SEEK_UNSUPPORTED');raise Stop('unexpected-source-seek')
    def hold_a(self):
        key=self.s['A']
        def act():
            self.e.remote('R','HOLD_CLOSE',[key]);self.e.object(key)['transportPending']=True;self.pending_a=key;return {'pending':key}
        self.f.n('ca',act,args=key)
    def gate_a(self):
        key=self.pending_a
        def act():
            reply=self.e.remote('R','GATE_CLOSE',[key]);self.e.rproof(key,reply['ticket']);self.e.object(key)['transportPending']=False;self.e.abort_progress();return {'closed':key}
        self.f.n('gate',act,args=key)
