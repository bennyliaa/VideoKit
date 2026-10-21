"""E2E static/pure-memory guard checks; never consumes the real permit.

No production src module or real runtime backend is imported. Frozen source,
artifact and wrapper bytes are read only as static input. Filesystem mutations,
memory/identity queries, launches and waits below are controlled memory events.
"""
from __future__ import annotations

import argparse
import ast
import copy
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import sys
sys.dont_write_bytecode=True
from unittest import mock

BASE=Path(__file__).resolve().parents[1]
PREFIX='docs/coder/d1e2e/'
_MODULES={}
_FIXTURE_CACHE=None


def load_tool(name):
    if name not in _MODULES:
        path=BASE/'tools'/name
        canonical=name.removesuffix('.py').replace('-','_')
        spec=importlib.util.spec_from_file_location(canonical,path)
        module=importlib.util.module_from_spec(spec);sys.modules[canonical]=module
        spec.loader.exec_module(module);_MODULES[name]=module
    return _MODULES[name]


def fixture(admission):
    """Use the actual frozen inventory layout, not a made-up C freeze schema."""
    global _FIXTURE_CACHE
    if _FIXTURE_CACHE is not None:
        batch,original_files,selected=_FIXTURE_CACHE
        return memory_fixture(admission,copy.deepcopy(batch),dict(original_files),list(selected))
    batch_bytes=(BASE/'manifest/e2e-batch.json').read_bytes();batch=json.loads(batch_bytes)
    files={PREFIX+'manifest/e2e-batch.json':batch_bytes}
    for relative in ('upstream-e2c/freeze-summary.json','upstream-e2c/source-manifest.json','upstream-e2c/E2C-source.zip',
                     'upstream-e2d/freeze-summary.json','upstream-e2d/E2D-source.zip'):
        files[PREFIX+relative]=(BASE/relative).read_bytes()
    old=json.loads(files[PREFIX+'upstream-e2c/freeze-summary.json'])
    source=json.loads(files[PREFIX+'upstream-e2c/source-manifest.json'])
    selected=[]
    for row in source['files']:
        path=row['path'];relative=path.removeprefix('docs/coder/d1e2c/')
        if path.startswith('docs/coder/d1e2c/') and (relative.startswith(('src/','profiles/')) or
                relative in ('manifest/branches.json','tools/r-helper.ps1')):
            selected.append(relative)
    for row in old['files']:
        relative=row['path'].removeprefix('docs/coder/d1e2c/')
        if relative=='artifacts/E2C.dll' or relative.startswith('artifacts/java/'):
            selected.append(relative)
    for relative in selected:files[PREFIX+relative]=(BASE/relative).read_bytes()
    for name in ('e2e_admission.py','e2e_runtime.py','e2e_driver.py','launch-once.py'):
        files[PREFIX+'tools/'+name]=(BASE/'tools'/name).read_bytes()
    _FIXTURE_CACHE=(copy.deepcopy(batch),dict(files),list(selected))
    return memory_fixture(admission,batch,files,selected)


def memory_fixture(admission,batch,files,selected):
    batch_bytes=files[PREFIX+'manifest/e2e-batch.json']
    freeze=dict(schema=1,state='PREPARED_NOT_RUN_PENDING_TESTER',
                immutableFiles=[dict(path=path,bytes=len(data),sha256=admission.digest(data)) for path,data in sorted(files.items())],
                prepUsage=dict(metadataBytes=600000,fixtureBytes=0),batchManifestSha256=admission.digest(batch_bytes),
                productionBindings=copy.deepcopy(batch['productionBindings']))
    storage=dict(files=files,dirs=set(),events=[],nonce=0)
    backend=MemoryBackend(admission,storage)
    backend.seal=freeze;backend.reseal()
    return batch,backend,selected


class MemoryBackend:
    def __init__(self,module,storage):
        self.module=module;self.storage=storage;self.role='launcher';self.machine='LZF'
        self.parent=dict(pid=101,creationTime100ns=100001);self.child=dict(pid=202,creationTime100ns=200002)
        self.memory=dict(status='MEMORY_READY',stopAcceptance=False,minimumAvailablePhysicalBytes=2147483648,
                         observation=dict(availablePhysicalBytes=2147483648),sampleDurationSeconds=0)
        self.before_mkdir=None;self.before_create=None;self.runtime_error=None;self.seal=None;self.expected=None
        self.wait_response=None;self.before_wait=None;self.spawn_error=None;self.wait_error=None;self.child_error=None
        self.process=None;self.spawn_partial=True;self.parent_handle_closed=False
    @property
    def events(self):return self.storage['events']
    def event(self,name,**fields):self.events.append(dict(event=name,**fields))
    def reseal(self):
        raw=self.module.encoded(self.seal);self.storage['files'][PREFIX+'evidence/e2e-freeze.json']=raw
        self.expected=self.module.digest(raw)
    def read(self,relative):return self.read_project(PREFIX+relative)
    def read_project(self,path):return self.storage['files'][str(path).replace('\\','/')]
    def machine_name(self):self.event('machine');return self.machine
    def exists(self,relative):
        return relative in self.storage['dirs'] or PREFIX+relative in self.storage['files']
    def mkdir_new(self,relative):
        if self.before_mkdir:
            callback,self.before_mkdir=self.before_mkdir,None;callback()
        if self.exists(relative):raise FileExistsError(relative)
        self.storage['dirs'].add(relative);self.event('mkdir_new',path=relative)
    def create_new(self,relative,value):
        if self.before_create:
            callback,self.before_create=self.before_create,None;callback(relative,value)
        path=PREFIX+relative
        if path in self.storage['files']:raise FileExistsError(relative)
        self.storage['files'][path]=self.module.encoded(copy.deepcopy(value));self.event('create_new',path=relative)
    def identity(self,role):
        self.event('identity',role=role)
        return copy.deepcopy(self.parent if role=='parent' or self.role=='launcher' else self.child)
    def verify_runtime(self,identity):
        self.event('verify_runtime')
        if self.runtime_error:raise self.module.AdmissionError(self.runtime_error)
    def fresh_memory(self):self.event('fresh_memory');return copy.deepcopy(self.memory)
    def nonce(self):self.storage['nonce']+=1;return format(self.storage['nonce'],'032x')
    def now(self):return 1000.0
    def await_launch(self,seconds):
        self.event('await_launch',seconds=seconds)
        if not self.exists('execution/launch.json'):raise self.module.AdmissionError('LAUNCH_RECORD_PENDING')
        return json.loads(self.read('execution/launch.json'))
    def as_child(self):
        child=MemoryBackend(self.module,self.storage);child.role='child';child.parent=copy.deepcopy(self.parent);child.child=copy.deepcopy(self.child)
        child.seal=self.seal;child.expected=self.expected;return child
    def spawn(self,reservation,expected_freeze,batch_id):
        self.event('spawn',pid=self.child['pid'])
        if self.spawn_error:
            if self.spawn_partial:self.process=object()
            raise self.module.AdmissionError(self.spawn_error)
        self.process=object()
        return self.process
    def child_identity(self,process):
        if process is not self.process:raise AssertionError('Replacement fake process')
        self.event('child_identity',pid=self.child['pid'])
        if self.child_error:raise self.module.AdmissionError(self.child_error)
        return copy.deepcopy(self.child)
    def wait_bounded(self,process,seconds):
        if process is not self.process:raise AssertionError('Replacement fake process')
        self.event('wait_bounded',seconds=seconds,pid=self.child['pid'])
        if self.before_wait:
            callback,self.before_wait=self.before_wait,None;callback()
        if self.spawn_error:
            return dict(status='PENDING',exitObserved=False,exitCode=None,stoppedWaitingOnly=True)
        if self.wait_error:raise self.module.AdmissionError(self.wait_error)
        if self.wait_response.get('exitObserved') is True and self.wait_response.get('parentProcessHandleCloseProven') is True:
            self.parent_handle_closed=True
        return copy.deepcopy(self.wait_response)
    def facts(self):
        return dict(identityRemaining=0,identityCloseUnknown=False,metadataRemaining=[],metadataCloseUnknown=False,
                    spawnCalls=sum(row['event']=='spawn' for row in self.events),parentPipes=0,parentCollectorWorkers=0,
                    parentProcessHandleCloseProven=self.parent_handle_closed)
    def record_result(self,receipt,freeze,late=False):
        self.event('record_result',receipt=copy.deepcopy(receipt),late=late)
        self.create_new('execution/late-exit.json' if late else 'execution/launcher-result.json',receipt)
        return copy.deepcopy(receipt)


def run_checks():
    admission=load_tool('e2e_admission.py');passed=[];negative=[]
    def check(value,name):
        if not value:raise AssertionError('PREPARATION_CHECK:'+name)
        passed.append(name)
    def refuses(action,reason,name):
        try:action()
        except admission.AdmissionError as error:
            check(reason in str(error),name);negative.append(dict(check=name,reason=str(error)));return
        raise AssertionError('Missing refusal:'+name)
    def rejected(action,name):
        try:action()
        except (admission.AdmissionError,FileExistsError,KeyError,ValueError,TypeError):check(True,name);return
        raise AssertionError('Missing rejection:'+name)
    def fresh():return fixture(admission)
    def effects(backend):return [row for row in backend.events if row['event'] not in ('machine',)]
    def count(backend,name):return sum(row['event']==name for row in backend.events)

    batch,backend,selected=fresh();once=admission.OnceAdmission(batch,backend)
    check(len(selected)==48 and sum(path.startswith('src/') for path in selected)==32 and
          sum(path.startswith('profiles/') for path in selected)==4,'actual-C-freeze-and-source-manifest-are-distinct-immutable-inventories')
    before=set(backend.storage['files']);prepared=once.prepare(backend.expected,batch['batchId'])
    check(prepared==backend.seal and set(backend.storage['files'])==before and not backend.storage['dirs'] and not effects(backend),
          'prepare-is-read-only-without-reservation-runtime-memory-identity-launch-or-root')
    inspected=admission.inspect_receipt()
    check(inspected['status']=='NOT_RUN' and not inspected['executionAllowed'] and not inspected['reservationConsumed'] and
          not inspected['outputRootCreated'] and inspected['helpersStarted']==inspected['mediaBytesRead']==0,
          'default-inspect-does-not-authorize-or-consume-any-attempt')
    for field,value in (('batchId','other-batch'),('machineName','OTHER'),('uniqueRootName','../reused-root'),('profile','REAL_IO'),
                        ('observerMode','MOCK'),('mockAllowed',True),('realExecutionAllowed',True),('maximumG',2),('maximumFullAttempts',2)):
        candidate=copy.deepcopy(batch);candidate[field]=value
        refuses(lambda candidate=candidate:admission.validate_batch(candidate),'BATCH_FIELD:'+field,'batch-cannot-change-'+field)
    candidate=copy.deepcopy(batch);candidate['limits']['parentWaitSeconds']=201
    refuses(lambda:admission.validate_batch(candidate),'BATCH_LIMITS_CHANGED','original-200s-wait-is-not-expanded')
    candidate=copy.deepcopy(batch);candidate['limits']['minimumAvailablePhysicalBytes']=0
    refuses(lambda:admission.validate_batch(candidate),'BATCH_LIMITS_CHANGED','fresh2GiB-floor-is-not-lowered')
    batch,backend,_=fresh();backend.machine='OTHER'
    refuses(lambda:admission.OnceAdmission(batch,backend).prepare(backend.expected,batch['batchId']),
            'MACHINE_NOT_AUTHORIZED','another-machine-cannot-prepare-this-batch')
    check(not effects(backend) and not backend.storage['dirs'],'machine-refusal-has-no-execution-effects')
    batch,backend,_=fresh()
    refuses(lambda:admission.OnceAdmission(batch,backend).prepare('0'*64,batch['batchId']),
            'EXPECTED_FREEZE_MISMATCH','concrete-freeze-hash-is-required')
    check(not effects(backend),'freeze-refusal-never-queries-runtime-or-starts-G')
    for output in ('execution/reservation.json','selfcheck/foreign.out','evidence/e2e-freeze.json'):
        batch,backend,_=fresh();path=PREFIX+output;backend.storage['files'][path]=b'fake-output'
        backend.seal['immutableFiles'].append(dict(path=path,bytes=11,sha256=admission.digest(b'fake-output')));backend.reseal()
        refuses(lambda:admission.OnceAdmission(batch,backend).prepare(backend.expected,batch['batchId']),
                'OUTPUT_IN_IMMUTABLE_INVENTORY','execution-output-cannot-enter-immutable-code-set-'+output)
    for relative in ('src/authority.py','profiles/runtime-policy.json','tools/r-helper.ps1'):
        batch,backend,_=fresh();path=PREFIX+relative;backend.storage['files'][path]+=b'\nCONTROLLED_CHANGE'
        refuses(lambda:admission.OnceAdmission(batch,backend).prepare(backend.expected,batch['batchId']),
                'IMMUTABLE_FILE_CHANGED','frozen-file-byte-change-is-rejected-'+relative)
        # Even a freshly rebound preparation seal cannot replace original C
        # production, policy or the actual R LoadFrom script.
        for row in backend.seal['immutableFiles']:
            if row['path']==path:row.update(bytes=len(backend.storage['files'][path]),sha256=admission.digest(backend.storage['files'][path]))
        backend.reseal()
        refuses(lambda:admission.OnceAdmission(batch,backend).prepare(backend.expected,batch['batchId']),
                'PRODUCTION_CHANGED','new-seal-cannot-rebind-original-production-'+relative)

    batch,backend,_=fresh();once=admission.OnceAdmission(batch,backend);reservation=once.reserve(backend.expected,batch['batchId'])
    events=[row['event']+':'+row.get('path','') for row in backend.events]
    check(events.index('create_new:execution/reservation.json')<events.index('fresh_memory:') and
          reservation['consumed'] and reservation['refundAllowed'] is False and reservation['createdBeforeG'],
          'durable-one-shot-reservation-precedes-fresh-memory-and-G')
    original=backend.read('execution/reservation.json')
    refuses(lambda:admission.OnceAdmission(batch,backend).reserve(backend.expected,batch['batchId']),
            'ONCE_OUTPUT_ALREADY_EXISTS','second-reservation-cannot-refund-or-retry-the-original-owner')
    check(backend.read('execution/reservation.json')==original and count(backend,'fresh_memory')==1 and count(backend,'spawn')==0,
          'duplicate-attempt-preserves-first-record-and-does-not-resample')

    batch,backend,_=fresh();winner=[]
    def compete():winner.append(admission.OnceAdmission(batch,backend).reserve(backend.expected,batch['batchId']))
    backend.before_mkdir=compete
    rejected(lambda:admission.OnceAdmission(batch,backend).reserve(backend.expected,batch['batchId']),
             'deterministic-competing-attempt-loses-before-any-second-reservation')
    check(len(winner)==1 and count(backend,'mkdir_new')==1 and count(backend,'create_new')==2 and
          count(backend,'fresh_memory')==1 and count(backend,'spawn')==0,
          'shared-atomic-CREATE_NEW-namespace-has-one-winner-with-no-threads-or-G')
    for memory in (dict(status='STOP_PENDING',stopAcceptance=True,minimumAvailablePhysicalBytes=2147483648,observation=dict(availablePhysicalBytes=2147483647)),
                   dict(status='MEMORY_READY',stopAcceptance=False,minimumAvailablePhysicalBytes=2147483648,observation=dict(availablePhysicalBytes=True))):
        batch,backend,_=fresh();backend.memory=memory;once=admission.OnceAdmission(batch,backend)
        refuses(lambda:once.reserve(backend.expected,batch['batchId']),'FRESH_MEMORY_REJECTED_RESERVATION_CONSUMED',
                'low-or-invalid-fresh-memory-consumes-once-without-G-'+str(memory['observation']['availablePhysicalBytes']))
        check(once.reservation is not None and backend.exists('execution/reservation.json') and count(backend,'spawn')==0,
              'memory-refusal-keeps-original-consumed-reservation')
        refuses(lambda:admission.OnceAdmission(batch,backend).reserve(backend.expected,batch['batchId']),
                'ONCE_OUTPUT_ALREADY_EXISTS','fresh-refusal-never-automatically-restarts-or-seeks-low-value')
        check(count(backend,'fresh_memory')==1,'memory-refusal-never-resamples')

    driver=load_tool('e2e_driver.py');launcher=load_tool('launch-once.py')
    check(not launcher.RETAINED_ORIGINALS,'pure-check-starts-with-no-original-process-owners')
    # A real claim guard with a fake execution body proves ordering without
    # importing or constructing Engine, its workers, helpers or fixtures.
    batch,backend,_=fresh();owner=admission.OnceAdmission(batch,backend)
    reservation=owner.reserve(backend.expected,batch['batchId']);launch=owner.bind_launch(reservation,backend.child)
    child_backend=backend.as_child();child=admission.OnceAdmission(batch,child_backend);executed=[]
    def body(claim):
        check(child_backend.exists('execution/claim.json'),'claim-is-durable-before-any-fake-fixture-body')
        child_backend.event('fake_fixture_body');executed.append(claim);return 'logical-only-body'
    value=driver.run_claimed(child,backend.expected,batch['batchId'],body)
    check(value=='logical-only-body' and len(executed)==1 and executed[0]['child']==backend.child and
          executed[0]['launcher']==backend.parent and not executed[0]['realExecutionAllowed'],
          'only-original-parent-and-child-claim-can-enter-controlled-body')
    check(count(backend,'await_launch')==1 and next(row for row in backend.events if row['event']=='await_launch')['seconds']==1.0,
          'child-handshake-wait-is-bounded-without-new-identity-or-replacement')
    rejected(lambda:driver.run_claimed(admission.OnceAdmission(batch,child_backend),backend.expected,batch['batchId'],body),
             'duplicate-child-claim-is-CREATE_NEW-and-cannot-enter-body-again')
    check(len(executed)==1 and count(backend,'fake_fixture_body')==1,'claim-replay-never-repeats-fixture-work')
    valid=admission.bind_claim(reservation,launch,backend.parent,backend.child)
    check(valid['reservationSha256']==admission.digest(admission.encoded(reservation)) and
          valid['launchSha256']==admission.digest(admission.encoded(launch)),
          'claim-binds-exact-original-reservation-and-launch-bytes')
    for role,key in (('parent','pid'),('parent','creationTime100ns'),('child','pid'),('child','creationTime100ns')):
        parent=copy.deepcopy(backend.parent);child_identity=copy.deepcopy(backend.child)
        (parent if role=='parent' else child_identity)[key]+=1
        refuses(lambda parent=parent,child_identity=child_identity:admission.bind_claim(reservation,launch,parent,child_identity),
                'ORIGINAL_LAUNCHER_REQUIRED' if role=='parent' else 'ORIGINAL_CHILD_REQUIRED',
                'same-or-reused-PID-cannot-replace-original-'+role+'-'+key)
    for field,newvalue,reason in (('reservationSha256','0'*64,'LAUNCH_RESERVATION_BINDING'),
                                  ('expectedFreeze','0'*64,'CLAIM_FREEZE_BINDING'),
                                  ('batchId','foreign','CLAIM_FREEZE_BINDING')):
        changed=copy.deepcopy(launch);changed[field]=newvalue
        refuses(lambda changed=changed:admission.bind_claim(reservation,changed,backend.parent,backend.child),reason,
                'launch-binding-cannot-change-'+field)
    changed=copy.deepcopy(reservation);changed['nonce']='replacement'
    refuses(lambda:admission.bind_claim(changed,launch,backend.parent,backend.child),'LAUNCH_RESERVATION_BINDING',
            'reservation-nonce-change-invalidates-existing-launch')
    for role,key in (('parent','pid'),('parent','creationTime100ns'),('child','pid'),('child','creationTime100ns')):
        batch,backend,_=fresh();owner=admission.OnceAdmission(batch,backend)
        reservation=owner.reserve(backend.expected,batch['batchId']);owner.bind_launch(reservation,backend.child)
        child_backend=backend.as_child();getattr(child_backend,role)[key]+=1;executed=[]
        rejected(lambda:driver.run_claimed(admission.OnceAdmission(batch,child_backend),backend.expected,batch['batchId'],
                                          lambda claim:executed.append(claim)),
                 'driver-rejects-'+role+'-'+key+'-before-body')
        check(not executed and not backend.exists('execution/claim.json') and not backend.exists('selfcheck'),
              'identity-refusal-has-no-claim-or-fixture-'+role+'-'+key)
    batch,backend,_=fresh();owner=admission.OnceAdmission(batch,backend);owner.reserve(backend.expected,batch['batchId'])
    executed=[]
    refuses(lambda:driver.run_claimed(admission.OnceAdmission(batch,backend.as_child()),backend.expected,batch['batchId'],
                                      lambda claim:executed.append(claim)),'LAUNCH_RECORD_PENDING',
            'child-without-parent-launch-record-does-not-invent-a-new-launch')
    check(not executed and count(backend,'await_launch')==1 and not backend.exists('execution/claim.json'),
          'missing-launch-keeps-admission-closed-with-no-fixtures')
    for directory in ('execution','selfcheck'):
        batch,backend,_=fresh();backend.storage['dirs'].add(directory)
        refuses(lambda:admission.OnceAdmission(batch,backend).reserve(backend.expected,batch['batchId']),
                'ONCE_OUTPUT_ALREADY_EXISTS','any-existing-'+directory+'-prevents-root-reuse')
        check(count(backend,'fresh_memory')==count(backend,'spawn')==0,'root-reuse-refusal-is-before-fresh-or-launch-'+directory)
    batch,backend,_=fresh();backend.runtime_error='RUNTIME_BINDING_CHANGED'
    refuses(lambda:admission.OnceAdmission(batch,backend).reserve(backend.expected,batch['batchId']),
            'RUNTIME_BINDING_CHANGED','runtime-mismatch-cannot-consume-or-start-the-prepared-attempt')
    check(not backend.storage['dirs'] and count(backend,'fresh_memory')==count(backend,'spawn')==0,
          'runtime-mismatch-rejects-before-reservation-or-G')

    simulated=[]
    def fake_driver_return(backend,status):
        claimed=admission.OnceAdmission(batch,backend.as_child())
        def execute(claim):
            backend.event('fake_actual_body')
            return dict(scope='CONTROLLED_MEMORY_BODY',status=status,claim=claim,noInFlight=True,
                        actualFullAttempt=False,driverWitness=dict(status=status,rows=0,assertions=0,remainingResources=0))
        receipt=driver.run_claimed(claimed,backend.expected,batch['batchId'],execute)
        backend.create_new('execution/driver-result.json',receipt)
    for outcome,exit_code in (('PASS',0),('FAIL',1)):
        batch,backend,_=fresh();once=admission.OnceAdmission(batch,backend)
        backend.wait_response=dict(exitObserved=True,exitCode=exit_code,parentProcessHandleCloseProven=True)
        backend.before_wait=lambda backend=backend,outcome=outcome:fake_driver_return(backend,outcome)
        receipt=launcher.run_once(once,backend,backend.expected,batch['batchId'])
        first_reservation=backend.read('execution/reservation.json');first_return=backend.read('execution/launcher-result.json')
        check(receipt['status']==outcome and receipt['reservationConsumed'] and receipt['noInFlight'] is True and
              count(backend,'spawn')==count(backend,'wait_bounded')==count(backend,'fake_actual_body')==1,
              'controlled-'+outcome+'-has-one-launch-one-claim-and-one-original-wait')
        check(next(row for row in backend.events if row['event']=='wait_bounded')['seconds']==200 and not launcher.RETAINED_ORIGINALS,
              'observed-original-exit-removes-fake-owner-only-after-bounded-wait-'+outcome)
        again=launcher.run_once(admission.OnceAdmission(batch,backend),backend,backend.expected,batch['batchId'])
        check(again['status'] in ('FAIL','PENDING') and count(backend,'spawn')==count(backend,'fresh_memory')==count(backend,'wait_bounded')==1 and
              backend.read('execution/reservation.json')==first_reservation and backend.read('execution/launcher-result.json')==first_return,
              'first-'+outcome+'-is-not-erased-or-retried-to-find-PASS')
        simulated.append(dict(case='controlled-'+outcome,scope='PURE_MEMORY_ONLY',fakeLaunches=1,fakeBodies=1,
                              actualG=0,duplicateRejected=True,firstReturnPreserved=True))
    batch,backend,_=fresh();once=admission.OnceAdmission(batch,backend)
    backend.wait_response=dict(status='PENDING',exitObserved=False,exitCode=None,stoppedWaitingOnly=True)
    pending=launcher.run_once(once,backend,backend.expected,batch['batchId'])
    try:
        original_return=backend.read('execution/launcher-result.json')
        check(pending['status']=='PENDING' and pending['originalChild']==backend.child and pending['noInFlight'] is None and
              pending['stoppedWaitingOnly'] is True and launcher.RETAINED_ORIGINALS==[(backend,backend.process)],
              '200s-PENDING-retains-the-original-fake-process-and-unknown-ownership')
        duplicate=launcher.run_once(admission.OnceAdmission(batch,backend),backend,backend.expected,batch['batchId'])
        check(duplicate['status'] in ('FAIL','PENDING') and count(backend,'spawn')==count(backend,'fresh_memory')==count(backend,'wait_bounded')==1 and
              launcher.RETAINED_ORIGINALS==[(backend,backend.process)] and backend.read('execution/launcher-result.json')==original_return,
              'PENDING-never-kills-replaces-restarts-or-overwrites-the-first-return')
        # Only a controlled later fact changes this fake owner's exit state.
        # It does not turn the original PENDING notice into a successful run.
        backend.create_new('execution/driver-result.json',dict(status='FAIL',noInFlight=True,actualFullAttempt=False))
        late=launcher.completion_receipt(once,backend,dict(exitObserved=True,exitCode=1,parentProcessHandleCloseProven=True),
                                         backend.expected,backend.child)
        late['initialPendingPreserved']=True;backend.record_result(late,once.freeze,late=True)
        check(late['status']=='FAIL' and late['originalChild']==pending['originalChild'] and
              backend.read('execution/launcher-result.json')==original_return and backend.exists('execution/late-exit.json') and
              count(backend,'spawn')==count(backend,'fresh_memory')==1,
              'late-original-exit-has-distinct-evidence-and-preserves-first-PENDING')
        simulated.append(dict(case='controlled-original-PENDING',scope='PURE_MEMORY_ONLY',fakeLaunches=1,fakeWaits=1,
                              actualG=0,originalOwnerRetained=True,initialPendingPreserved=True,lateReturnSeparate=True))
    finally:
        # This is a plain object fixture, never an OS process or real owner.
        if (backend,backend.process) in launcher.RETAINED_ORIGINALS:launcher.RETAINED_ORIGINALS.remove((backend,backend.process))
    for fault in ('child_error','wait_error'):
        batch,backend,_=fresh();once=admission.OnceAdmission(batch,backend)
        setattr(backend,fault,'CONTROLLED_'+fault.upper())
        backend.wait_response=dict(exitObserved=True,exitCode=1,parentProcessHandleCloseProven=True)
        try:
            receipt=launcher.run_once(once,backend,backend.expected,batch['batchId'])
            check(receipt['status'] in ('FAIL','PENDING') and receipt['reservationConsumed'] and
                  count(backend,'spawn')==1 and count(backend,'fresh_memory')==1 and count(backend,'fake_actual_body')==0,
                  'controlled-'+fault+'-does-not-refund-relaunch-or-enter-fixtures')
            check(count(backend,'wait_bounded')==1,
                  'controlled-'+fault+'-waits-at-most-once-on-original-object')
            if fault=='wait_error':
                check(receipt['status']=='PENDING' and receipt['noInFlight'] is None and launcher.RETAINED_ORIGINALS==[(backend,backend.process)],
                      'unknown-wait-keeps-original-owner-and-does-not-claim-cleanup')
            replay=launcher.run_once(admission.OnceAdmission(batch,backend),backend,backend.expected,batch['batchId'])
            check(replay['status'] in ('FAIL','PENDING') and count(backend,'spawn')==count(backend,'wait_bounded')==1,
                  'controlled-'+fault+'-blocks-another-attempt-without-touching-old-process')
            simulated.append(dict(case='controlled-'+fault,scope='PURE_MEMORY_ONLY',fakeLaunches=1,actualG=0,noRetry=True))
        finally:
            if (backend,backend.process) in launcher.RETAINED_ORIGINALS:launcher.RETAINED_ORIGINALS.remove((backend,backend.process))
    for has_partial in (False,True):
        batch,backend,_=fresh();once=admission.OnceAdmission(batch,backend)
        backend.spawn_error='CONTROLLED_START_RETURN_UNKNOWN';backend.spawn_partial=has_partial
        try:
            receipt=launcher.run_once(once,backend,backend.expected,batch['batchId'])
            check(receipt['status']=='PENDING' and receipt['noInFlight'] is None and receipt['reservationConsumed'] and
                  count(backend,'spawn')==count(backend,'fresh_memory')==1 and count(backend,'fake_actual_body')==0,
                  'unknown-start-with-'+('partial-object' if has_partial else 'no-object')+'-never-claims-absence-or-cleanup')
            check(count(backend,'wait_bounded')==(1 if has_partial else 0) and
                  launcher.RETAINED_ORIGINALS==([(backend,backend.process)] if has_partial else []),
                  'unknown-start-retains-exact-partial-object-without-inventing-one-'+str(has_partial))
            simulated.append(dict(case='controlled-unknown-start-'+str(has_partial),scope='PURE_MEMORY_ONLY',
                                  fakeLaunchCalls=1,actualG=0,noInFlight=None,partialObject=has_partial,noRetry=True))
        finally:
            if (backend,backend.process) in launcher.RETAINED_ORIGINALS:launcher.RETAINED_ORIGINALS.remove((backend,backend.process))

    # Exercise actual default mains under an import tripwire. No real backend
    # module, production module or OS adapter can be imported on Inspect.
    import builtins
    original_import=builtins.__import__
    forbidden={'e2e_runtime','gengine','gcore','authority','notifications','runtime_metrics','controller','scenarios','phases'}
    def guarded_import(name,*args,**kwargs):
        if name.split('.')[0] in forbidden:raise AssertionError('Unexpected runtime import:'+name)
        return original_import(name,*args,**kwargs)
    for tool in (driver,launcher):
        stream=io.StringIO()
        with mock.patch.object(sys,'argv',[str(BASE/'tools'/Path(tool.__file__).name)]),mock.patch.object(builtins,'__import__',guarded_import),contextlib.redirect_stdout(stream):
            code=tool.main()
        receipt=json.loads(stream.getvalue())
        check(code==0 and receipt==admission.inspect_receipt() and not launcher.RETAINED_ORIGINALS,
              'actual-default-main-is-closed-and-imports-no-runtime-'+Path(tool.__file__).name)

    # These are schema-only witnesses, not claims about actual worker/helper
    # state. Missing evidence must not collapse to all(empty)==True.
    joined=dict(unknown=False,alive=False,startInProgress=False,joined=True,entered=True,exited=True,
                joinReturned=True,creditReleased=True,releaseProof='THREAD_JOIN_PROVEN')
    witness=dict(status='PASS',nativePending=[],logOwnershipPending=False,
                 logClose=dict(closed=True,remainingResources=0),
                 callbackHub=dict(lifecycle='CLOSED',workersAlive=0,remainingCredits=[],ownershipPending=False,
                                  cells=0,queued=0,active=0,monitorInFlight=0,
                                  workers={label:copy.deepcopy(joined) for label in ('notify','deadline')}),
                 helpers={role:dict(pid=pid,instance=role+'-original',exitObserved=True,
                                   exitProof=dict(pid=pid,instance=role+'-original',code=0,exited=True))
                          for role,pid in (('J',303),('R',404))})
    check(driver.quiescence(witness) is True,'bounded-short-witness-with-all-original-exit-proofs-can-prove-quiescence')
    for kind in ('missing-helpers','missing-R','unknown-worker','missing-worker','unproven-worker-join',
                 'active-notification','missing-log-close','unknown-log-close','PENDING','helper-reused-instance'):
        changed=copy.deepcopy(witness)
        if kind=='missing-helpers':changed['helpers']={}
        elif kind=='missing-R':changed['helpers'].pop('R')
        elif kind=='unknown-worker':changed['callbackHub']['workers']['notify']['unknown']=True
        elif kind=='missing-worker':changed['callbackHub']['workers'].pop('deadline')
        elif kind=='unproven-worker-join':changed['callbackHub']['workers']['notify']['joinReturned']=False
        elif kind=='active-notification':changed['callbackHub']['active']=1
        elif kind=='missing-log-close':changed['logClose'].pop('closed')
        elif kind=='unknown-log-close':changed['logOwnershipPending']=True
        elif kind=='PENDING':changed['status']='PENDING'
        else:changed['helpers']['R']['exitProof']['instance']='replacement-R'
        check(driver.quiescence(changed) is False,'short-witness-cannot-claim-noInFlight-for-'+kind)

    batch,backend,_=fresh();root='selfcheck/'+batch['uniqueRootName']+'/'
    prep=dict(metadataBytes=600000,fixtureBytes=0)
    entries=[dict(path='execution/launcher-result.json',bytes=1000,kind='METADATA'),
             dict(path=root+'global.log',bytes=3000000,kind='METADATA'),
             dict(path=root+'L.bin',bytes=524305,kind='FIXTURE'),dict(path=root+'Z.bin',bytes=0,kind='FIXTURE')]
    usage=admission.validate_result_inventory(batch,prep,entries,1024)
    check(usage['outputUsage']==dict(metadataBytes=3002024,fixtureBytes=524305) and
          usage['combinedUsage']==dict(metadataBytes=3602024,fixtureBytes=524305) and usage['wrapperMetadataBytes']==2024,
          'execution-result-manifest-includes-preparation-plus-run-and-its-own-bytes')
    for changed,name,reason in (
            (entries+[copy.deepcopy(entries[0])],'duplicate-output-path','RESULT_INVENTORY_ENTRY'),
            ([dict(path='selfcheck/foreign/global.log',bytes=1,kind='METADATA')],'foreign-root','RESULT_OUTPUT_SCOPE'),
            ([dict(path='src/authority.py',bytes=1,kind='METADATA')],'immutable-production-as-output','RESULT_OUTPUT_SCOPE'),
            ([dict(path=root+'L.bin',bytes=1,kind='METADATA')],'fixture-reclassified-as-metadata','RESULT_CLASSIFICATION'),
            ([dict(path='execution/result.json',bytes=-1,kind='METADATA')],'negative-output-credit','RESULT_INVENTORY_ENTRY'),
            ([dict(path='execution/result.json',bytes=True,kind='METADATA')],'boolean-output-credit','RESULT_INVENTORY_ENTRY'),
            ([dict(path='execution/result.json',bytes=196609,kind='METADATA')],'wrapper-total-over-cap','RESULT_AGGREGATE_CAP_EXCEEDED'),
            ([dict(path=root+'global.log',bytes=3594305,kind='METADATA')],'preparation-plus-run-over-4MiB','RESULT_AGGREGATE_CAP_EXCEEDED'),
            ([dict(path=root+'L.bin',bytes=790529,kind='FIXTURE')],'execution-fixture-over-reserved-credit','RESULT_AGGREGATE_CAP_EXCEEDED')):
        refuses(lambda changed=changed:admission.validate_result_inventory(batch,prep,changed),reason,'result-ledger-rejects-'+name)
    for bad in (-1,True):
        rejected(lambda bad=bad:admission.validate_result_inventory(batch,prep,[],bad),'result-ledger-rejects-invalid-own-manifest-byte-count-'+str(bad))
    for key,bad in (('metadataBytes',-1),('fixtureBytes',True)):
        changed=copy.deepcopy(prep);changed[key]=bad
        rejected(lambda changed=changed:admission.validate_result_inventory(batch,changed,[]),'result-ledger-rejects-invalid-preparation-credit-'+key)
    for outcome in ('PASS','FAIL'):
        final=dict(status=outcome,noInFlight=True,originalChildExitObserved=True)
        check(admission.result_finalizable(final,1) is True,'only-exited-and-drained-original-'+outcome+'-can-have-final-output-hashes')
        for field,value in (('noInFlight',None),('noInFlight',False),('originalChildExitObserved',False),('status','PENDING')):
            changed=dict(final);changed[field]=value
            check(admission.result_finalizable(changed,1) is False,
                  'G-exit-does-not-finalize-unknown-driver-or-helper-'+outcome+'-'+field+'-'+str(value))
        check(admission.result_finalizable(final,1,local_clear=False) is False,
              'unknown-local-close-retains-incomplete-manifest-for-'+outcome)
    check(admission.result_finalizable(dict(status='FAIL',noInFlight=True,originalChildExitObserved=False),0) is True,
          'proven-no-spawn-clean-refusal-may-finalize-only-existing-wrapper-evidence')
    check(admission.result_finalizable(dict(status='PENDING',noInFlight=True,originalChildExitObserved=True),0) is False,
          'even-exit-and-claimed-clear-do-not-finalize-a-PENDING-return')
    for bad in (-1,2,True):
        refuses(lambda bad=bad:admission.result_finalizable(dict(status='FAIL',noInFlight=True),bad),
                'RESULT_SPAWN_COUNT','finalization-rejects-invalid-spawn-count-'+str(bad))

    # Static source checks cover resource-shape properties without importing
    # the real backend or touching any OS/resource API.
    trees={name:ast.parse((BASE/'tools'/name).read_text(encoding='utf-8-sig')) for name in
           ('e2e_admission.py','e2e_runtime.py','e2e_driver.py','launch-once.py')}
    def function(tree,name):return next(node for node in ast.walk(tree) if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)) and node.name==name)
    def attrs(node,names):return [item for item in ast.walk(node) if isinstance(item,ast.Call) and isinstance(item.func,ast.Attribute) and item.func.attr in names]
    check(len(attrs(function(trees['launch-once.py'],'run_once'),{'spawn'}))==1,
          'launcher-source-has-one-spawn-site-and-no-relaunch-loop')
    for name,tree in trees.items():
        check(not attrs(tree,{'kill','terminate','send_signal','communicate'}),
              'wrapper-never-kills-or-uses-unbounded-PIPE-collection-'+name)
    spawn=function(trees['e2e_runtime.py'],'spawn')
    popen=[node for node in attrs(spawn,{'__init__'}) if isinstance(node.func.value,ast.Attribute) and node.func.value.attr=='Popen']
    check(len(popen)==1 and {keyword.arg for keyword in popen[0].keywords}>={'stdin','stdout','stderr'} and
          all(isinstance(keyword.value,ast.Attribute) and keyword.value.attr=='DEVNULL'
              for keyword in popen[0].keywords if keyword.arg in ('stdin','stdout','stderr')),
          'real-spawn-source-declares-three-DEVNULL-streams-with-no-parent-reader-workers')
    allocations=[node for node in attrs(spawn,{'__new__'}) if isinstance(node.func.value,ast.Attribute) and node.func.value.attr=='Popen']
    check(len(allocations)==1 and allocations[0].lineno<popen[0].lineno,
          'original-partial-Popen-owner-is-captured-before-constructor-can-raise')
    check(not any(isinstance(node,ast.Name) and node.id in ('Thread','ThreadPoolExecutor','Win32MetricReader','Engine','Native','Channel')
                  for node in ast.walk(trees['e2e_runtime.py'])),
          'real-wrapper-source-adds-no-worker-helper-engine-or-metric-reader')
    create=function(trees['e2e_runtime.py'],'create_new')
    check(any(isinstance(node,ast.Constant) and node.value=='xb' for node in ast.walk(create)) and bool(attrs(create,{'fsync'})),
          'real-write-contract-is-CREATE_NEW-plus-durable-exact-write-without-overwrite')
    for name in ('e2e_driver.py','launch-once.py'):
        main=function(trees[name],'main');body=main.body
        inspect_index=next(index for index,node in enumerate(body) if isinstance(node,ast.If) and
                           isinstance(node.test,ast.UnaryOp) and isinstance(node.test.op,ast.Not) and
                           isinstance(node.test.operand,ast.Attribute) and node.test.operand.attr=='run')
        runtime_index=next(index for index,node in enumerate(body) if isinstance(node,ast.ImportFrom) and node.module=='e2e_runtime')
        check(inspect_index<runtime_index and any(isinstance(node,ast.Return) for node in ast.walk(body[inspect_index])),
              'default-inspect-return-precedes-real-backend-import-'+name)
    production=function(trees['e2e_driver.py'],'execute_production')
    owner_append=next(node for node in attrs(production,{'append'}) if isinstance(node.func.value,ast.Name) and node.func.value.id=='RETAINED_ENGINES')
    engine_new=next(node for node in attrs(production,{'__new__'}) if isinstance(node.func.value,ast.Name) and node.func.value.id=='Engine')
    engine_init=next(node for node in attrs(production,{'__init__'}) if isinstance(node.func.value,ast.Name) and node.func.value.id=='Engine')
    check(engine_new.lineno<owner_append.lineno<engine_init.lineno,
          'original-Engine-owner-is-strongly-retained-before-partial-constructor-can-fail')
    owner_remove=next(node for node in attrs(production,{'remove'}) if isinstance(node.func.value,ast.Name) and node.func.value.id=='RETAINED_ENGINES')
    remove_if=next(node for node in ast.walk(production) if isinstance(node,ast.If) and owner_remove in list(ast.walk(node)))
    check(isinstance(remove_if.test,ast.Name) and remove_if.test.id=='drained' and
          any(isinstance(node,ast.Assign) and any(isinstance(target,ast.Name) and target.id=='drained' for target in node.targets) and
              isinstance(node.value,ast.Call) and isinstance(node.value.func,ast.Name) and node.value.func.id=='quiescence'
              for node in ast.walk(production)),
          'Engine-strong-owner-is-released-only-under-original-quiescence-proof')
    main=function(trees['e2e_driver.py'],'main');holds=attrs(main,{'hold_unknown_ownership'})
    driver_write=next(node for node in attrs(main,{'create_new'}) if any(isinstance(arg,ast.Constant) and arg.value=='execution/driver-result.json' for arg in node.args))
    check(len(holds)==1 and driver_write.lineno<holds[0].lineno,
          'driver-publishes-original-first-return-before-holding-unknown-internal-owners')
    hold=function(trees['e2e_runtime.py'],'hold_unknown_ownership')
    check(not attrs(hold,{'spawn','Popen','kill','terminate','fresh_memory','sample','remote','run','finish','shutdown'}),
          'unknown-ownership-hold-has-no-new-run-sample-RPC-or-destructive-cleanup')
    record=function(trees['e2e_runtime.py'],'record_result')
    final_gate=next(node for node in ast.walk(record) if isinstance(node,ast.Assign) and
                    any(isinstance(target,ast.Name) and target.id=='complete' for target in node.targets))
    check(isinstance(final_gate.value,ast.Call) and isinstance(final_gate.value.func,ast.Name) and
          final_gate.value.func.id=='result_finalizable',
          'real-result-writer-uses-the-pure-original-owner-finalization-gate')
    inventories=attrs(record,{'_inventory'})
    inventory_if=next(node for node in ast.walk(record) if isinstance(node,ast.If) and
                      any(call in list(ast.walk(node)) for call in inventories))
    check(len(inventories)==1 and isinstance(inventory_if.test,ast.Name) and inventory_if.test.id=='complete',
          'unknown-exit-or-drain-never-reads-and-hashes-the-mutable-execution-root')
    check(not launcher.RETAINED_ORIGINALS and not driver.RETAINED_ENGINES and 'e2e_runtime' not in sys.modules,
          'pure-suite-finishes-with-no-real-backend-import-or-fake-owner-leak')
    return dict(schema=1,scope='E2E_PREPARATION_STATIC_AND_SYNTHETIC_GUARDS',status='PASS',assertions=len(passed),checks=passed,
                negativeCases=negative,simulatedCases=simulated,newG=0,helpersStarted=0,osMetricSamples=0,actualFullRuns=0,mediaBytesRead=0,
                realRootCreated=False,reservationConsumed=False,noInFlight=True,
                limitations='All mutations, identities, memory responses, launches and waits are pure memory fakes. Actual frozen source/artifact bytes are static inputs only; no production src/real runtime backend is imported or instantiated. No execution/selfcheck path is written and no actual permit is consumed.')


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');options=parser.parse_args()
    print(json.dumps(run_checks() if options.check else dict(scope='E2E_PREPARATION_CHECK_INSPECT',status='NOT_RUN',
          newG=0,helpersStarted=0,osMetricSamples=0,actualFullRuns=0,reservationConsumed=False,realRootCreated=False),separators=(',',':')))
