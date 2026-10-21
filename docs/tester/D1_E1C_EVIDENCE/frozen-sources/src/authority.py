"""Actual source admission, private completion, and ready identity checks used by G."""
import copy, threading
from concurrent.futures import Future
from gcore import Refused, need, uid

class SourceAuthority:
    def __init__(self,lock=None):self.lock=lock or threading.RLock()
    def binding(self,s,version,c):
        with self.lock:
            need(version in s['versions'] and c in s['versions'][version]['consumers'],'SESSION_RELEASED')
            return dict(task=s['task'],version=version,consumer=c,generation=s['versions'][version]['consumers'][c]['generation'])
    def reserve(self,s,version,c):
        with self.lock:
            need(not s.get('recovered') and not s.get('fenced') and not s.get('sourceFenced') and not s.get('globalFence'),'SESSION_RELEASED')
            entry=s['versions'].setdefault(version,dict(sealed=False,consumers={}))
            need(not entry['sealed'] and c not in entry['consumers'],'SESSION_RELEASED')
            entry['consumers'][c]=dict(finished=False,cancelled=False,generation=uid());s['version']=version;s['sourceDone']=False
            return self.binding(s,version,c)
    def validate(self,s,binding,handle=None):
        need(binding.get('task')==s['task'],'SOURCE_BINDING_MISMATCH');v=binding.get('version');c=binding.get('consumer')
        need(v in s['versions'] and c in s['versions'][v]['consumers'],'SOURCE_BINDING_MISMATCH')
        entry=s['versions'][v];consumer=entry['consumers'][c]
        need(consumer['generation']==binding.get('generation'),'SOURCE_BINDING_MISMATCH')
        need(not consumer['finished'] and not consumer['cancelled'] and not entry['sealed'] and not s.get('recovered') and not s.get('fenced') and not s.get('sourceFenced') and not s.get('globalFence'),'SESSION_RELEASED')
        if handle is not None:
            need(all(handle.get(k)==binding[k] for k in ('task','version','consumer','generation')),'SOURCE_BINDING_MISMATCH')
            need(handle.get('disposition')=='OWNED_OPEN_RETRYABLE','OBJECT_NOT_OPEN')
    def admit(self,s,binding,operation,handle=None):
        with self.lock:
            self.validate(s,binding,handle);need(operation not in s['ops'],'SOURCE_OPERATION_REUSED')
            op=dict(binding,done=False,nativeReturned=False);s['ops'][operation]=op;return op
    def mark_native(self,s,operation):
        with self.lock:s['ops'][operation]['nativeReturned']=True
    def drain(self,s,operation):
        with self.lock:
            need(s['ops'][operation]['nativeReturned'],'NATIVE_COMPLETION_NOT_RETURNED');s['ops'][operation]['done']=True
    def end(self,s,version,c):
        with self.lock:
            need(version in s['versions'] and c in s['versions'][version]['consumers'],'SESSION_RELEASED')
            s['versions'][version]['consumers'][c]['finished']=True
    def cancel(self,s,version,c):
        with self.lock:
            need(version in s['versions'] and c in s['versions'][version]['consumers'],'SESSION_RELEASED')
            s['versions'][version]['consumers'][c]['cancelled']=True

class PendingCell:
    """Native/private result and consumer response have separate lifetimes."""
    def __init__(self,operation,binding,release,on_drain=None,timeout=None):
        self.operation=operation;self.binding=copy.deepcopy(binding);self.response=Future();self.lock=threading.RLock()
        self.native_done=False;self.retained=True;self.discarded=False;self.deliveries=0;self.released=False;self.gated=False;self._value=None;self.release=release;self.on_drain=on_drain
        self.timer=None
        if timeout is not None:
            self.timer=threading.Timer(timeout,lambda:self.cancel('SOURCE_TIMEOUT'));self.timer.daemon=True;self.timer.start()
    def complete(self,value):
        drained=False
        with self.lock:
            need(not self.native_done,'DUPLICATE_NATIVE_COMPLETION');self._value=value;self.native_done=True
            if self.gated:drained=self._drain()
        if drained and self.on_drain:self.on_drain()
    def cancel(self,reason='CANCELLED'):
        drained=False
        with self.lock:
            if not self.response.done():self.response.set_exception(Refused(reason))
            if self.gated and self.native_done:drained=self._drain()
        if drained and self.on_drain:self.on_drain()
    def gate(self):
        drained=False
        with self.lock:
            need(not self.gated,'GATE_DUPLICATE');self.gated=True
            if self.native_done:drained=self._drain()
        if drained and self.on_drain:self.on_drain()
    def _drain(self):
        if self.released:return False
        if self.response.done():self.discarded=True
        else:self.deliveries+=1;self.response.set_result(self._value)
        self._value=None;self.release();self.released=True;self.retained=False
        if self.timer:self.timer.cancel()
        return True

class SourceBridge:
    def __init__(self,authority):self.authority=authority
    def read_zero(self,state,binding,handle,delegate):
        with self.authority.lock:self.authority.validate(state,binding,handle)
        return dict(n=0,bytes='',nativeReads=0)

def complete_source_response(authority,state,operation,cell,value,hold=False):
    with authority.lock:
        authority.mark_native(state,operation);cell.complete(value)
        consumer=state['versions'][cell.binding['version']]['consumers'][cell.binding['consumer']]
        if consumer['finished'] or consumer['cancelled']:cell.cancel('CANCELLED')
        if not hold:cell.gate()
    return {'pending':operation,'nativeReturned':True} if hold else cell.response.result()

def capture_ready_request(s):
    return {k:copy.deepcopy(v) for k,v in dict(ownerInstance=s['ownerInstance'],epoch=s['epoch'],export=s['task'],handle=s['grant'],attempt=s['attempt'],revision=s['revision'],receipt=s['receipt']).items()}

def validate_ready_request(s,request):
    need(isinstance(request,dict),'READY_REQUEST_SCHEMA')
    need(request.get('ownerInstance')==s['ownerInstance'] and request.get('epoch')==s['epoch'],'STALE_OWNER')
    need(all(request.get(k)==v for k,v in dict(export=s['task'],handle=s['grant'],attempt=s['attempt'],revision=s['revision']).items()),'READY_BINDING_MISMATCH')
    need(request.get('receipt')==s['receipt'] and s['receipt']['epoch']==s['epoch'],'RECEIPT_MISMATCH')
    need(s['state']=='READY_ELIGIBLE' and s.get('sourceDone') and not s.get('abortOnly'),'NOT_READY_ELIGIBLE')
