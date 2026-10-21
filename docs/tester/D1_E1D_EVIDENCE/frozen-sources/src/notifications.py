"""One fixed notifier and one deadline monitor; no user code runs under hub locks."""
import threading,time
from collections import deque
from concurrent.futures import Future
from gcore import Stop,Refused,need,uid

class DeliveryFuture(Future):
    """A real Future with a bounded, pre-decision callback registration window."""
    def __init__(self,cell):super().__init__();self.cell=cell
    def add_done_callback(self,fn):
        cell=self.cell
        with cell.lock:
            need(not cell.registration_closed,'CALLBACK_REGISTRATION_CLOSED')
            need(cell.callbacks_registered<4,'CALLBACK_LIMIT');need(callable(fn),'CALLBACK_NOT_CALLABLE')
            cell.callbacks_registered+=1
            def guarded(future):
                try:fn(future)
                except BaseException as error:
                    with cell.lock:cell.callback_errors.append(type(error).__name__)
                    cell.hub.block('CALLBACK_FAILED')
                finally:
                    with cell.lock:cell.callbacks_finished+=1
            # Registration is closed atomically before publication, so the base
            # immediate-callback branch cannot be reached while this lock is held.
            super().add_done_callback(guarded)
    def cancel(self):raise Refused('COMPLETION_OWNED_BY_HUB')
    def set_result(self,value):raise Refused('COMPLETION_OWNED_BY_HUB')
    def set_exception(self,error):raise Refused('COMPLETION_OWNED_BY_HUB')

class CompletionHub:
    def __init__(self,ledger=None,max_cells=8,callback_timeout=.1):
        self.ledger=ledger;self.maximum=max_cells;self.callback_timeout=callback_timeout
        self.condition=threading.Condition();self.cells={};self.deadlines={};self.queue=deque();self.active=None;self.active_since=None
        self.started=False;self.closing=False;self.closed=False;self.blocked=None;self.total=0;self.peak=0;self.notices=0;self.worker_ids=[]
    def start(self):
        with self.condition:
            need(not self.started,'COMPLETION_HUB_RESTART_DENIED');self.started=True
            if self.ledger:
                for label in ('notify','deadline'):
                    rid='completion-worker/'+label;self.ledger.acquire(rid,'G','worker');self.worker_ids.append(rid)
            self.notifier=threading.Thread(target=self._notify,name='E1D-notify',daemon=False)
            self.monitor=threading.Thread(target=self._monitor,name='E1D-deadline',daemon=False)
            self.notifier.start();self.monitor.start()
        return self
    def ensure_accepting(self):
        with self.condition:
            if not self.started or self.closing or self.closed or self.blocked:raise Stop('CALLBACK_DRAIN_PENDING')
    def register(self,cell,timeout):
        with self.condition:
            self.ensure_accepting();need(len(self.cells)<self.maximum,'PRIVATE_RESULT_CELL_LIMIT')
            self.cells[id(cell)]=cell;self.total+=1;self.peak=max(self.peak,len(self.cells))
            if timeout is not None:self.deadlines[id(cell)]=time.monotonic()+timeout
            self.condition.notify_all()
    def submit(self,cell):
        with self.condition:
            need(id(cell) in self.cells and not self.closed,'COMPLETION_OWNER_UNKNOWN')
            # Each registered live cell owns one notification credit in advance.
            need(len(self.queue)+(self.active is not None)<self.maximum,'COMPLETION_QUEUE_LIMIT')
            self.queue.append(cell);self.deadlines.pop(id(cell),None);self.notices+=1;self.condition.notify_all()
    def block(self,reason):
        with self.condition:
            self.blocked=self.blocked or reason;self.condition.notify_all()
    def released(self,cell):
        with self.condition:
            # The active notice keeps its capacity credit through notifier
            # return, even when its private resources have already drained.
            if self.active is not cell:self.cells.pop(id(cell),None)
            self.deadlines.pop(id(cell),None);self.condition.notify_all()
    def _notify(self):
        while True:
            with self.condition:
                self.condition.wait_for(lambda:self.queue or self.closing)
                if not self.queue and self.closing:return
                cell=self.queue.popleft();self.active=cell;self.active_since=time.monotonic()
            try:cell._publish_outside_locks()
            except BaseException:self.block('NOTIFICATION_UNKNOWN')
            finally:
                with self.condition:
                    if cell.released:self.cells.pop(id(cell),None)
                    self.active=None;self.active_since=None;self.condition.notify_all()
    def _monitor(self):
        while True:
            with self.condition:
                if self.closing:return
                now=time.monotonic()
                if self.active is not None and now-self.active_since>=self.callback_timeout:
                    self.blocked=self.blocked or 'CALLBACK_DEADLINE_PENDING'
                due=[self.cells[key] for key,deadline in list(self.deadlines.items()) if deadline<=now and key in self.cells]
                for cell in due:self.deadlines.pop(id(cell),None)
                if not due:self.condition.wait(timeout=.01)
            for cell in due:
                try:cell.cancel('SOURCE_TIMEOUT')
                except BaseException:self.block('DEADLINE_NOTIFICATION_UNKNOWN')
    def drain(self,timeout=.2):
        end=time.monotonic()+timeout
        with self.condition:
            while self.queue or self.active is not None:
                left=end-time.monotonic()
                if left<=0:
                    self.blocked=self.blocked or 'CALLBACK_DEADLINE_PENDING';raise Stop('CALLBACK_DRAIN_PENDING')
                self.condition.wait(left)
        return True
    def wait_cell(self,cell,timeout=.2):
        if not cell.drained.wait(timeout):self.block('CALLBACK_DEADLINE_PENDING');raise Stop('CALLBACK_DRAIN_PENDING')
        return True
    def pending(self):
        with self.condition:
            return dict(cells=len(self.cells),queued=len(self.queue),active=int(self.active is not None),blocked=self.blocked,
                        notices=self.notices,peakCells=self.peak,workersAlive=sum(t.is_alive() for t in (getattr(self,'notifier',None),getattr(self,'monitor',None)) if t))
    def stop_when_drained(self):
        # Unknown callback code is never killed. Non-daemon ownership remains
        # observable until all accepted publications actually return.
        with self.condition:self.closing=True;self.condition.notify_all()
    def close(self,timeout=1):
        if not self.started:return True
        if threading.current_thread() in (self.notifier,self.monitor):raise Stop('CALLBACK_DRAIN_PENDING')
        self.drain(timeout)
        with self.condition:
            if self.cells:raise Stop('CALLBACK_DRAIN_PENDING')
            self.closing=True;self.condition.notify_all()
        end=time.monotonic()+timeout
        for thread in (self.notifier,self.monitor):thread.join(max(0,end-time.monotonic()))
        if self.notifier.is_alive() or self.monitor.is_alive():raise Stop('CALLBACK_DRAIN_PENDING')
        if self.ledger:
            for rid in self.worker_ids:self.ledger.release(rid,'THREAD_JOIN_PROVEN')
        self.closed=True;return True
