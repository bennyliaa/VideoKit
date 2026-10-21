"""One fixed notifier and one deadline monitor; no user code runs under hub locks."""
import threading,time
from collections import deque
from concurrent.futures import Future
from gcore import Stop,Refused,need,uid

class WorkerNotStartedError(RuntimeError):
    """Trusted starter contract: it did not invoke start or run this Thread.

    Ordinary exceptions provide no such proof. A factory must only construct an
    unstarted Thread; it must never start a thread or invoke the supplied target.
    """
    pass

class DeliveryFuture(Future):
    """A real Future with a bounded, pre-decision callback registration window."""
    def __init__(self,cell):super().__init__();self.cell=cell
    def add_done_callback(self,fn):
        cell=self.cell
        need(cell is not None,'CALLBACK_REGISTRATION_CLOSED')
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
    def __init__(self,ledger=None,max_cells=8,callback_timeout=.1,thread_factory=None,starter=None,startup_timeout=1):
        self.ledger=ledger;self.maximum=max_cells;self.callback_timeout=callback_timeout
        self.condition=threading.Condition();self.cells={};self.deadlines={};self.queue=deque();self.active=None;self.active_since=None;self.monitor_inflight=set()
        self.started=False;self.closing=False;self.closed=False;self.blocked=None;self.total=0;self.peak=0;self.notices=0;self.worker_ids=[]
        self.lifecycle='NEW';self.startupError=None;self.startup_in_progress=False;self._stop_workers=False;self.cleanupError=None;self._cleanup_lock=threading.Lock()
        self.thread_factory=thread_factory or (lambda label,**kw:threading.Thread(**kw))
        self.starter=starter or (lambda thread,label:thread.start());self.startup_timeout=startup_timeout
        self.notifier=None;self.monitor=None;self.workers={}
        for label in ('notify','deadline'):
            self.workers[label]=dict(label=label,rid='completion-worker/'+label,state='NEW',history=['NEW'],
                creditReserved=False,creditReleased=False,releaseProof=None,reserveEntered=False,reserveReturned=False,reservationPriorPresent=False,
                thread=None,threadId=uid(),threadCreated=False,startEntered=False,startReturned=False,startInProgress=False,
                entered_event=threading.Event(),exited_event=threading.Event(),entryIdent=None,
                joinEntered=False,joinReturned=False,joined=False,neverStartedProven=False,unknown=False,
                startError=None,reserveError=None,joinError=None,runtimeError=None,observationError=None)
    @staticmethod
    def _error(error):
        try:message=str(error)
        except BaseException:message='UNRENDERABLE_EXCEPTION'
        return dict(type=type(error).__name__[:64],message=message[:160])
    def _state_locked(self,worker,state):
        worker['state']=state
        if worker['history'][-1]!=state:worker['history'].append(state)
    def _observe(self,worker):
        thread=worker['thread']
        if thread is None:return dict(alive=False,ident=None,nativeId=None)
        try:return dict(alive=bool(thread.is_alive()),ident=thread.ident,nativeId=getattr(thread,'native_id',None))
        except BaseException as error:
            with self.condition:worker['observationError']=self._error(error);worker['unknown']=True
            return dict(alive=None,ident=None,nativeId=None)
    def _entry(self,label,target):
        worker=self.workers[label]
        with self.condition:
            worker['entryIdent']=threading.get_ident();worker['entered_event'].set()
            if worker['state']!='FAILED' and self.lifecycle!='FAILED':self._state_locked(worker,'RUNNING')
            self.condition.notify_all()
            stopping=self._stop_workers
        try:
            if not stopping:target()
        except BaseException as error:
            with self.condition:
                worker['runtimeError']=self._error(error);worker['unknown']=True;self._state_locked(worker,'FAILED')
                self.lifecycle='FAILED';self.blocked=self.blocked or 'COMPLETION_WORKER_FAILED';self.closing=True;self._stop_workers=True;self.condition.notify_all()
        finally:
            with self.condition:worker['exited_event'].set();self.condition.notify_all()
    def _request_stop(self):
        with self.condition:self.closing=True;self._stop_workers=True;self.condition.notify_all()
    def _start_worker(self,label,target,end):
        worker=self.workers[label]
        with self.condition:
            if self.closing:raise Stop('COMPLETION_START_CANCELLED')
            self._state_locked(worker,'STARTING');worker['reserveEntered']=True
        # Ledger.acquire normally commits atomically under this same ledger lock.
        # The two observations also cover a trusted injector raising just after
        # that commit, without claiming a pre-existing/foreign reservation.
        prior=None
        if self.ledger:
            with self.ledger.lock:prior=self.ledger.live.get(worker['rid'])
        with self.condition:worker['reservationPriorPresent']=prior is not None
        try:
            if self.ledger:self.ledger.acquire(worker['rid'],'G','worker')
        except BaseException as error:
            current=None
            if self.ledger:
                with self.ledger.lock:current=self.ledger.live.get(worker['rid'])
            with self.condition:
                worker['reserveError']=self._error(error);self._state_locked(worker,'FAILED')
                if prior is None and current is not None and current.get('owner')=='G' and current.get('kind')=='worker':
                    worker['creditReserved']=True;worker['neverStartedProven']=True;self.worker_ids.append(worker['rid'])
                elif current is not None:worker['unknown']=True
            raise
        with self.condition:
            worker['reserveReturned']=True;worker['creditReserved']=True;self.worker_ids.append(worker['rid'])
            if self.closing:worker['neverStartedProven']=True;raise Stop('COMPLETION_START_CANCELLED')
        try:
            thread=self.thread_factory(label=label,target=lambda:self._entry(label,target),name='E2C-'+label,daemon=False)
        except BaseException as error:
            # A trusted factory only constructs; it cannot launch the target.
            with self.condition:worker['neverStartedProven']=True;worker['startError']=self._error(error);self._state_locked(worker,'FAILED')
            raise
        with self.condition:
            worker['thread']=thread;worker['threadCreated']=True
            if label=='notify':self.notifier=thread
            else:self.monitor=thread
            if self.closing:worker['neverStartedProven']=True;raise Stop('COMPLETION_START_CANCELLED')
            worker['startEntered']=True;worker['startInProgress']=True
        try:self.starter(thread,label)
        except BaseException as error:
            observed=self._observe(worker)
            with self.condition:
                worker['startError']=self._error(error);self._state_locked(worker,'FAILED')
                worker['neverStartedProven']=isinstance(error,WorkerNotStartedError) and not worker['entered_event'].is_set() and observed['alive'] is False and observed['ident'] is None
                worker['unknown']=not worker['neverStartedProven']
            raise
        else:
            with self.condition:worker['startReturned']=True
        finally:
            with self.condition:worker['startInProgress']=False;self.condition.notify_all()
        # A returned start alone is insufficient to advertise an operational Hub.
        if not worker['entered_event'].wait(max(0,end-time.monotonic())):
            with self.condition:worker['unknown']=True
            raise Stop('COMPLETION_WORKER_ENTRY_PENDING')
        observed=self._observe(worker)
        with self.condition:
            need(observed['alive'] is True and not worker['exited_event'].is_set() and worker['runtimeError'] is None,'COMPLETION_WORKER_NOT_RUNNING')
    def start(self):
        with self.condition:
            need(not self.started and self.lifecycle=='NEW','COMPLETION_HUB_RESTART_DENIED')
            self.started=True;self.startup_in_progress=True;self.lifecycle='STARTING'
        end=time.monotonic()+self.startup_timeout;label=None
        try:
            for label,target in (('notify',self._notify),('deadline',self._monitor)):self._start_worker(label,target,end)
            with self.condition:
                need(not self.closing and not self.blocked and all(w['entered_event'].is_set() and not w['exited_event'].is_set() for w in self.workers.values()),'COMPLETION_WORKER_NOT_RUNNING')
                self.lifecycle='RUNNING';self.startup_in_progress=False;self.condition.notify_all()
        except BaseException as error:
            with self.condition:
                self.startupError=self.startupError or dict(worker=label,**self._error(error))
                self.lifecycle='FAILED';self.blocked=self.blocked or 'COMPLETION_STARTUP_FAILED';self.startup_in_progress=False
            self._request_stop()
            try:self._cleanup_workers(time.monotonic()+self.startup_timeout)
            except BaseException as cleanup_error:
                # Cleanup failure must not replace the original startup exception.
                with self.condition:self.cleanupError=self._error(cleanup_error)
            raise
        return self
    def ensure_accepting(self):
        with self.condition:
            if self.lifecycle!='RUNNING' or self.closing or self.closed or self.blocked:raise Stop('CALLBACK_DRAIN_PENDING')
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
            if self.active is not cell and id(cell) not in self.monitor_inflight:self.cells.pop(id(cell),None)
            self.deadlines.pop(id(cell),None);self.condition.notify_all()
    def cell_quiescent(self,cell):
        """No Hub worker, queue, deadline or registered ownership of this cell."""
        with self.condition:
            key=id(cell)
            return key not in self.cells and key not in self.deadlines and key not in self.monitor_inflight and self.active is not cell and all(queued is not cell for queued in self.queue)
    def _notify(self):
        while True:
            with self.condition:
                self.condition.wait_for(lambda:self.queue or self._stop_workers)
                if not self.queue and self._stop_workers:return
                cell=self.queue.popleft();self.active=cell;self.active_since=time.monotonic()
            try:cell._publish_outside_locks()
            except BaseException:self.block('NOTIFICATION_UNKNOWN')
            finally:
                with self.condition:
                    if cell.released and id(cell) not in self.monitor_inflight:self.cells.pop(id(cell),None)
                    self.active=None;self.active_since=None
                    # The original publication/callback call has returned. Drop
                    # the idle worker's last strong reference before advertising
                    # quiescence; capacity is not returned ahead of this point.
                    del cell
                    self.condition.notify_all()
    def _monitor(self):
        while True:
            with self.condition:
                if self._stop_workers:return
                now=time.monotonic()
                if self.active is not None and now-self.active_since>=self.callback_timeout:
                    self.blocked=self.blocked or 'CALLBACK_DEADLINE_PENDING'
                due=[self.cells[key] for key,deadline in list(self.deadlines.items()) if deadline<=now and key in self.cells]
                for index in range(len(due)):
                    key=id(due[index]);self.deadlines.pop(key,None);self.monitor_inflight.add(key)
                if not due:self.condition.wait(timeout=.01)
            for index in range(len(due)):
                cell=due[index];key=id(cell)
                try:cell.cancel('SOURCE_TIMEOUT')
                except BaseException:self.block('DEADLINE_NOTIFICATION_UNKNOWN')
                finally:
                    with self.condition:
                        # cancel (including any wrapper) actually returned before
                        # either the list slot or the worker's local is retired.
                        released=cell.released;due[index]=None;del cell
                        self.monitor_inflight.discard(key)
                        if released and (self.active is None or id(self.active)!=key):self.cells.pop(key,None)
                        self.condition.notify_all()
            due.clear()
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
            facts={};credits=[]
            for label,worker in self.workers.items():
                observed=self._observe(worker)
                if worker['creditReserved'] and not worker['creditReleased']:credits.append(worker['rid'])
                facts[label]={k:worker[k] for k in ('state','creditReserved','creditReleased','releaseProof','reserveEntered','reserveReturned','reservationPriorPresent','threadId','threadCreated','startEntered','startReturned','startInProgress','entryIdent','joinEntered','joinReturned','joined','neverStartedProven','unknown','startError','reserveError','joinError','runtimeError','observationError')}
                facts[label]['history']=list(worker['history'])
                facts[label].update(entered=worker['entered_event'].is_set(),exited=worker['exited_event'].is_set(),**observed)
            alive=sum(f['alive'] is True for f in facts.values())
            return dict(cells=len(self.cells),queued=len(self.queue),active=int(self.active is not None),monitorInFlight=len(self.monitor_inflight),blocked=self.blocked,
                        notices=self.notices,peakCells=self.peak,workersAlive=alive,lifecycle=self.lifecycle,closing=self.closing,closed=self.closed,startupError=self.startupError,
                        startupInProgress=self.startup_in_progress,cleanupError=self.cleanupError,workers=facts,remainingCredits=credits,
                        ownershipPending=bool(credits or alive or self.startup_in_progress or self.cells or self.queue or self.active is not None or self.monitor_inflight or any(f['unknown'] for f in facts.values())))
    def stop_when_drained(self):
        # Unknown callback code is never killed. Non-daemon ownership remains
        # observable until all accepted publications actually return.
        self._request_stop()
    def _retire(self,worker,proof):
        with self.condition:
            if not worker['creditReserved'] or worker['creditReleased']:return
            if self.ledger:self.ledger.release(worker['rid'],proof)
            worker['creditReleased']=True;worker['releaseProof']=proof;worker['unknown']=False;self._state_locked(worker,'CLOSED');self.condition.notify_all()
    def _cleanup_workers(self,end):
        """Bounded observation. Never join an unstarted/unknown Thread or invent exit."""
        if not self._cleanup_lock.acquire(timeout=max(0,end-time.monotonic())):return
        try:self._cleanup_workers_owned(end)
        finally:self._cleanup_lock.release()
    def _cleanup_workers_owned(self,end):
        for worker in self.workers.values():
            with self.condition:
                if not worker['creditReserved'] or worker['creditReleased']:continue
                if self.startup_in_progress or worker['startInProgress']:
                    worker['unknown']=True;continue
                never=worker['neverStartedProven'] or not worker['startEntered']
            if never:
                self._retire(worker,'THREAD_NOT_STARTED_PROVEN');continue
            # A generic start exception carries no non-start proof. Give a late
            # wrapper entry the remaining bounded observation window, then retain.
            if not worker['entered_event'].is_set():worker['entered_event'].wait(max(0,end-time.monotonic()))
            observed=self._observe(worker)
            if not worker['entered_event'].is_set():
                with self.condition:worker['unknown']=True
                continue
            if worker['thread'] is threading.current_thread():
                with self.condition:worker['unknown']=True
                continue
            with self.condition:worker['joinEntered']=True
            try:worker['thread'].join(max(0,end-time.monotonic()))
            except BaseException as error:
                with self.condition:worker['joinError']=self._error(error);worker['unknown']=True
                continue
            observed=self._observe(worker)
            with self.condition:
                worker['joinReturned']=True
                proof=worker['entered_event'].is_set() and worker['exited_event'].is_set() and observed['alive'] is False
                worker['joined']=bool(proof);worker['unknown']=not proof
            if proof:self._retire(worker,'THREAD_JOIN_PROVEN')
    def close(self,timeout=1):
        end=time.monotonic()+timeout
        with self.condition:
            if self.closed:return True
            if self.lifecycle=='NEW':self.lifecycle='CLOSED';self.closed=True;self.closing=True;return True
            self.closing=True;self.condition.notify_all()
            if self.startup_in_progress:
                self.lifecycle='FAILED';self.blocked=self.blocked or 'COMPLETION_STARTUP_FAILED'
                self._stop_workers=True;self.condition.notify_all()
                raise Stop('CALLBACK_DRAIN_PENDING')
        if threading.current_thread() in (self.notifier,self.monitor):raise Stop('CALLBACK_DRAIN_PENDING')
        self.drain(max(0,end-time.monotonic()))
        with self.condition:
            while self.monitor_inflight:
                left=end-time.monotonic()
                if left<=0:raise Stop('CALLBACK_DRAIN_PENDING')
                self.condition.wait(left)
            if self.cells:raise Stop('CALLBACK_DRAIN_PENDING')
        self._request_stop()
        try:self._cleanup_workers(end)
        except BaseException as error:
            with self.condition:self.cleanupError=self._error(error)
            raise Stop('CALLBACK_DRAIN_PENDING') from error
        with self.condition:
            if any((w['creditReserved'] and not w['creditReleased']) or w['unknown'] for w in self.workers.values()):raise Stop('CALLBACK_DRAIN_PENDING')
            self.closed=True;self.lifecycle='CLOSED';return True
