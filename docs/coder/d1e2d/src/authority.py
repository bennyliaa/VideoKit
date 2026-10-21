"""Actual source admission, private completion, and ready identity checks used by G."""
import copy, threading
from dataclasses import dataclass
from gcore import Refused, need, uid
from notifications import DeliveryFuture

@dataclass(frozen=True,slots=True)
class CellAudit:
    """Bounded scalar/tuple evidence; no result, exception or runtime owner."""
    operation:str
    kind:str
    binding:tuple
    handle_key:str|None
    native_done:bool
    gated:bool
    released:bool
    retained:bool
    discarded:bool
    deliveries:int
    callbacks_registered:int
    callbacks_finished:int
    callback_errors:tuple
    error_type:str|None
    error_message:str|None
    notification_done:bool
    notifier_quiescent:bool=True
    archived:bool=True
    def as_dict(self):
        return dict(operation=self.operation,kind=self.kind,binding=dict(self.binding),handle_key=self.handle_key,
                    native_done=self.native_done,gated=self.gated,released=self.released,retained=self.retained,
                    discarded=self.discarded,deliveries=self.deliveries,callbacks_registered=self.callbacks_registered,
                    callbacks_finished=self.callbacks_finished,callback_errors=list(self.callback_errors),
                    error_type=self.error_type,error_message=self.error_message,notification_done=self.notification_done,
                    notifier_quiescent=self.notifier_quiescent,archived=self.archived)

class SourceAuthority:
    def __init__(self,lock=None):self.lock=lock or threading.RLock();self.cells={};self.fenced=False
    def binding(self,s,version,c):
        with self.lock:
            need(version in s['versions'] and c in s['versions'][version]['consumers'],'SESSION_RELEASED')
            return dict(task=s['task'],version=version,consumer=c,generation=s['versions'][version]['consumers'][c]['generation'])
    def reserve(self,s,version,c):
        with self.lock:
            need(not self.fenced and not s.get('recovered') and not s.get('fenced') and not s.get('sourceFenced') and not s.get('globalFence'),'SESSION_RELEASED')
            entry=s['versions'].setdefault(version,dict(sealed=False,consumers={}))
            need(not entry['sealed'] and c not in entry['consumers'],'SESSION_RELEASED')
            entry['consumers'][c]=dict(finished=False,cancelled=False,generation=uid());s['version']=version;s['sourceDone']=False
            return self.binding(s,version,c)
    def validate(self,s,binding,handle=None):
        need(binding.get('task')==s['task'],'SOURCE_BINDING_MISMATCH');v=binding.get('version');c=binding.get('consumer')
        need(v in s['versions'] and c in s['versions'][v]['consumers'],'SOURCE_BINDING_MISMATCH')
        entry=s['versions'][v];consumer=entry['consumers'][c]
        need(consumer['generation']==binding.get('generation'),'SOURCE_BINDING_MISMATCH')
        need(not self.fenced and not consumer['finished'] and not consumer['cancelled'] and not entry['sealed'] and not s.get('recovered') and not s.get('fenced') and not s.get('sourceFenced') and not s.get('globalFence'),'SESSION_RELEASED')
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
        changed=[]
        with self.lock:
            need(version in s['versions'] and c in s['versions'][version]['consumers'],'SESSION_RELEASED')
            s['versions'][version]['consumers'][c]['finished']=True
            changed=self._cancel_locked(s,version,c)
        for cell in changed:cell._post();cell._release_ready()
    def cancel(self,s,version,c):
        changed=[]
        with self.lock:
            need(version in s['versions'] and c in s['versions'][version]['consumers'],'SESSION_RELEASED')
            s['versions'][version]['consumers'][c]['cancelled']=True
            changed=self._cancel_locked(s,version,c)
        for cell in changed:cell._post();cell._release_ready()
    def _cancel_locked(self,s,version,c):
        changed=[]
        for cell in list(self.cells.values()):
            if cell.state is s and cell.binding['version']==version and cell.binding['consumer']==c:
                with cell.lock:cell._decide_locked(Refused('CANCELLED'))
                changed.append(cell)
        return changed
    def register(self,cell):
        with self.lock:self.cells[id(cell)]=cell
    def unregister(self,cell):
        with self.lock:self.cells.pop(id(cell),None)
    def seal(self,s,version):
        with self.lock:s['versions'][version]['sealed']=True
    def fence(self,state=None):
        with self.lock:
            self.fenced=True
            if state is not None:state['sourceFenced']=True
    def _delivery_locked(self,cell):
        """Pure eligibility check of the ORIGINAL operation, never re-admission."""
        s=cell.state;operation=s['ops'].get(cell.operation)
        need(operation and all(operation.get(k)==v for k,v in cell.binding.items()),'SOURCE_BINDING_MISMATCH')
        handle=s['objects'].get(cell.handle_key) if cell.handle_key is not None else None
        if cell.handle_key is not None:need(handle is not None,'SOURCE_BINDING_MISMATCH')
        self.validate(s,cell.binding,handle)
    def _decide_delivery_locked(self,cell):
        if cell.outcome is not None or not cell.native_done or not cell.gated:return
        try:self._delivery_locked(cell)
        except Refused as error:cell._decide_locked(error)
        else:cell._decide_locked()
    def complete(self,cell,value):
        with self.lock:
            self.mark_native(cell.state,cell.operation)
            with cell.lock:cell._native_locked(value);self._decide_delivery_locked(cell)
        cell._post();cell._release_ready()
    def gate(self,cell,timeout=.2):
        with self.lock:
            with cell.lock:
                need(not cell.gated,'GATE_DUPLICATE');cell.gated=True;self._decide_delivery_locked(cell);native=cell.native_done
        cell._post();cell._release_ready()
        if native:cell.hub.wait_cell(cell,timeout)

class PendingCell:
    """Native/private result and consumer response have separate lifetimes."""
    def __init__(self,operation,binding,release,on_drain=None,timeout=None,hub=None,authority=None,state=None,kind='read',handle_key=None):
        need(hub is not None,'EXPLICIT_COMPLETION_HUB_REQUIRED')
        self.operation=operation;self.binding=copy.deepcopy(binding);self.lock=threading.RLock();self.response=DeliveryFuture(self)
        self.native_done=False;self.retained=True;self.discarded=False;self.deliveries=0;self.released=False;self.gated=False;self._value=None;self.release=release;self.on_drain=on_drain
        self.hub=hub;self.authority=authority;self.state=state;self.kind=kind;self.handle_key=handle_key
        self.outcome=None;self.registration_closed=False;self.callbacks_registered=0;self.callbacks_finished=0;self.callback_errors=[]
        self.notification_submitted=False;self.notification_posting=False;self.notification_submit_error=None;self.notification_done=False;self.publication_error=None;self.release_claimed=False;self.release_error=None;self.drained=threading.Event();self.decided=threading.Event()
        self.archived=False;self.audit=None
        hub.register(self,timeout)
        if authority is not None:
            need(state is not None,'SOURCE_STATE_REQUIRED');authority.register(self)
    def _native_locked(self,value):
        need(not self.native_done,'DUPLICATE_NATIVE_COMPLETION');self._value=value;self.native_done=True
    def _decide_locked(self,error=None):
        if self.archived or self.outcome is not None:return False
        self.registration_closed=True;self.outcome=dict(value=self._value if error is None else None,error=error)
        self.discarded=error is not None;self.deliveries=int(error is None);self.decided.set();return True
    def complete(self,value):
        if self.authority is not None:return self.authority.complete(self,value)
        with self.lock:
            self._native_locked(value)
            if self.gated:self._decide_locked()
        self._post();self._release_ready()
    def cancel(self,reason='CANCELLED'):
        with self.lock:self._decide_locked(Refused(reason))
        self._post();self._release_ready()
    def gate(self,timeout=.2):
        if self.authority is not None:return self.authority.gate(self,timeout)
        with self.lock:
            need(not self.gated,'GATE_DUPLICATE');self.gated=True
            if self.native_done:self._decide_locked()
            native=self.native_done
        self._post();self._release_ready()
        if native:self.hub.wait_cell(self,timeout)
    def _post(self):
        with self.lock:
            if self.outcome is None or self.notification_submitted or self.notification_posting or self.notification_submit_error:return
            self.notification_posting=True
        try:self.hub.submit(self)
        except BaseException as error:
            with self.lock:self.notification_submit_error=type(error).__name__;self.notification_posting=False
            self.hub.block('NOTIFICATION_SUBMIT_UNKNOWN');raise
        else:
            with self.lock:self.notification_submitted=True;self.notification_posting=False
    def _publish_outside_locks(self):
        from concurrent.futures import Future
        try:
            if self.outcome['error'] is None:Future.set_result(self.response,self.outcome['value'])
            else:Future.set_exception(self.response,self.outcome['error'])
        except BaseException as error:
            with self.lock:self.publication_error=type(error).__name__
            self.hub.block('NOTIFICATION_UNKNOWN');return
        finally:
            # Registration closed before publication; no concurrent append is legal.
            with self.response._condition:self.response._done_callbacks.clear()
        with self.lock:self.notification_done=self.callbacks_finished==self.callbacks_registered
        if not self.notification_done:self.hub.block('CALLBACK_DRAIN_PENDING');return
        self._release_ready()
    def _release_ready(self):
        with self.lock:
            if self.release_claimed or not(self.native_done and self.gated and self.notification_done):return
            self.release_claimed=True
        try:
            self.release()
            if self.on_drain:self.on_drain()
        except BaseException as error:
            with self.lock:self.release_error=type(error).__name__
            self.hub.block('RESOURCE_DRAIN_UNKNOWN');return
        with self.lock:self._value=None;self.released=True;self.retained=False
        if self.authority is not None:self.authority.unregister(self)
        self.hub.released(self);self.drained.set()
    def archive(self):
        """Detach tool-only edges after the caller and all Hub work have returned.

        This never changes the original Future result/exception/traceback. A
        caller retaining that Future or a traceback can still retain its values.
        Unknown submission/publication/release evidence is never compacted.
        """
        authority=self.authority
        if authority is not None:
            # Same source -> cell order used for admission/completion.
            with authority.lock:
                with self.lock:return self._archive_locked(authority)
        with self.lock:return self._archive_locked(None)
    def _archive_locked(self,authority):
        if self.archived:return self.audit
        if not(self.native_done and self.gated and self.notification_done and self.release_claimed and self.released and not self.retained and self.drained.is_set() and self.registration_closed and self.response.done()):return None
        if self.notification_posting or not self.notification_submitted or self.notification_submit_error or self.publication_error or self.release_error:return None
        if self.callbacks_finished!=self.callbacks_registered or not 0<=self.callbacks_registered<=4:return None
        if authority is not None:
            if id(self) in authority.cells:return None
            operation=self.state.get('ops',{}).get(self.operation) if self.state is not None else None
            if not operation or not operation.get('nativeReturned') or not operation.get('done'):return None
        if type(self.operation) is not str or len(self.operation)>128 or type(self.kind) is not str or len(self.kind)>32:return None
        if self.handle_key is not None and (type(self.handle_key) is not str or len(self.handle_key)>128):return None
        if len(self.binding)>8 or any(type(k) is not str or len(k)>64 or type(v) is not str or len(v)>128 for k,v in self.binding.items()):return None
        hub=self.hub
        if hub is None:return None
        with hub.condition:
            if not hub.cell_quiescent(self):return None
            error=self.outcome['error'];error_type=type(error).__name__[:64] if error is not None else None;message=None
            if error is not None:
                # No user __str__ runs under application locks, and no original
                # exception or traceback enters the immutable audit record.
                if not isinstance(error,BaseException):return None
                args=BaseException.args.__get__(error,BaseException)
                message=args[0][:160] if args and type(args[0]) is str else '<non-string-error>'
            audit=CellAudit(self.operation,self.kind,tuple(sorted(self.binding.items())),self.handle_key,
                            self.native_done,self.gated,self.released,self.retained,self.discarded,self.deliveries,
                            self.callbacks_registered,self.callbacks_finished,tuple(name[:64] for name in self.callback_errors),
                            error_type,message,self.notification_done)
            self.audit=audit;self.archived=True;self.response.cell=None
            self.release=None;self.on_drain=None;self.state=None;self.authority=None;self.hub=None;self._value=None;self.outcome=None
            return audit

class SourceBridge:
    def __init__(self,authority):self.authority=authority
    def read_zero(self,state,binding,handle,delegate):
        with self.authority.lock:self.authority.validate(state,binding,handle)
        return dict(n=0,bytes='',nativeReads=0)

def complete_source_response(authority,state,operation,cell,value,hold=False):
    need(cell.authority is authority and cell.state is state and cell.operation==operation,'SOURCE_BINDING_MISMATCH')
    cell.complete(value)
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
