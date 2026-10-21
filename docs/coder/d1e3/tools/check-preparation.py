"""E3 bounded metadata and pure-memory preparation guards; no execution.

Only declared package JSON/source and the three frozen E2F metadata baselines
are opened. Input path strings are never passed to a filesystem or OS API.
No Engine, native adapter, worker, helper, media byte or permit is constructed.
"""
from __future__ import annotations

import argparse
import ast
import builtins
import copy
import hashlib
import importlib.util
import json
from pathlib import Path, PureWindowsPath
import sys

sys.dont_write_bytecode=True
BASE=Path(__file__).resolve().parents[1]
OLD=BASE.parent/'d1e2f'
_MODULES={}
_RAW={}
_READS=dict(bytes=0,files=0,byteCap=4194304,fileCap=64)
FORBIDDEN={'gengine','gcore','controller','scenarios','phases','authority','notifications',
           'runtime_metrics','runtime_wiring','subprocess','ctypes','threading','concurrent','e3_runtime'}
LENGTHS=dict(L=3212959911,C=4096,Z=0)
OFFSETS=[2147418112,2147450880,2147483648,3212894375]
BUDGET_FIELDS=('task','nonquery','queriesNew','queriesReplay','inputBytes','inputCalls','validationBytes',
               'newTargets','newRecords','outputBytes','mediaHandles','buffers','seconds','operations')


def metadata(path):
    """Fixed local source/config paths only; all bytes read are accounted."""
    path=Path(path)
    if not (path.is_relative_to(BASE) or path.is_relative_to(OLD)):
        raise AssertionError('METADATA_SCOPE')
    if path.suffix not in ('.json','.py'):raise AssertionError('METADATA_TYPE')
    if str(path) in _RAW:return _RAW[str(path)]
    if _READS['files']>=_READS['fileCap']:raise AssertionError('METADATA_FILE_LIMIT')
    _READS['files']+=1;parts=[]
    with open(path,'rb',buffering=0) as stream:
        while True:
            remaining=_READS['byteCap']-_READS['bytes']
            if remaining<=0:raise AssertionError('METADATA_BYTE_LIMIT')
            block=stream.read(min(65536,remaining))
            if not block:break
            _READS['bytes']+=len(block);parts.append(block)
    value=b''.join(parts);_RAW[str(path)]=value;return value


def json_metadata(path):return json.loads(metadata(path).decode('utf-8-sig'))


def load_module(folder,name):
    key=(folder,name)
    if key not in _MODULES:
        canonical=name.removesuffix('.py').replace('-','_')
        spec=importlib.util.spec_from_file_location(canonical,BASE/folder/name)
        module=importlib.util.module_from_spec(spec);sys.modules[canonical]=module
        previous=builtins.__import__
        def guarded(module_name,*args,**kwargs):
            if module_name.split('.')[0] in FORBIDDEN:raise AssertionError('NONPURE_PREPARATION_IMPORT:'+module_name)
            return previous(module_name,*args,**kwargs)
        builtins.__import__=guarded
        try:spec.loader.exec_module(module)
        finally:builtins.__import__=previous
        _MODULES[key]=module
    return _MODULES[key]


def future_completion_fixture(manifest,profile,assertions=173,batch='FUTURE-E3-LOGICAL-A',freeze='7'*64):
    """Authored JSON only, deliberately unrelated to an executed batch."""
    data_overrides={'P02-ZERO':1,'Q01-SEQ':4,'Q04-DUP':1,'Q02-RANDOM':7,'Q08-VALIDATOR':1,
                    'Q04-CLOSEACK':1,'Q05-SPACEFAIL':2,'Q07-TAKEFIRST':2}
    errors={'P06-ZERO/d01':'INVALID_PROVIDER_RESULT','P07-EARLY/d01':'EARLY_EOF','P10-B/n08':'STALE_REVISION',
            'P11-SEALED/n09':'SESSION_RELEASED','P12-OLDOPEN/n19':'SESSION_RELEASED',
            'Q09-SECOND/n01':'CLAIM_CONFLICT','Q09-SECOND/n02':'CLAIM_CONFLICT','Q09-PLAN/n01':'INTENT_CONFLICT',
            'Q09-SOURCE/n01':'INTENT_CONFLICT','Q09-PRESET/n01':'INTENT_CONFLICT',
            'Q05-SPACEFAIL/d02':'OUTPUT_SPACE_INSUFFICIENT','Q07-TAKEFIRST/n13':'STALE_OWNER',
            'Q03-RANDOM/n01':'RANDOM_REQUIRED','Q03-VERIFY/n01':'VALIDATION_REQUIRED','Q09-ALIAS/n01':'INPUT_ALIAS',
            'P10-D/n11':'EXHAUSTED','P10-C/n02':'CLOSE_NOT_RETRYABLE','P10-C/n04':'CLOSE_NOT_RETRYABLE',
            'P10-A/n06':'STALE_REVISION'}
    waiting={'P08-LATEOPEN/n03':'CANCELLED','P09-CANCEL/d01':'CANCELLED','P09-TIMEOUT/d01':'SOURCE_TIMEOUT'}
    profile_sha=hashlib.sha256(json.dumps(profile,sort_keys=True,separators=(',',':')).encode('ascii')).hexdigest()
    claim=dict(batchId=batch,rootName='logical-'+batch.lower(),profile='REAL_IO',profileSha256=profile_sha,
               profileGeometry=dict(boundary=2147483648,lengths=dict(LENGTHS)),expectedFreeze=freeze,
               child=dict(pid=202,creationTime100ns=200002),launcher=dict(pid=101,creationTime100ns=100001),
               observerMode='ACTUAL_OS_OBSERVER',mockMetricsUsed=False,realExecutionAllowed=True)
    specs={'PF':dict(nonquery=16,queriesNew=0,queriesReplay=0,seconds=20,inputCalls=2)}
    specs.update({row['id']:row for row in manifest['branches']});order=['PF',*manifest['executionOrder']]
    rows=[];events=[];history=[]
    for name in order:
        spec=specs[name];data_steps=data_overrides.get(name,spec['inputCalls'])
        rows.append(dict(branch=name,scope='REAL_IO_TOOL_CHECKPOINT_ONLY',controls=spec['nonquery'],dataSteps=data_steps,
                         queryNew=spec['queriesNew'],queryReplay=spec['queriesReplay'],seconds=spec['seconds'],elapsedSeconds=.001))
        if name.startswith('P01-S'):rows[-1].update(windowOutcome='UNFILLED',windowBytesObserved=4)
        for prefix,count,kind in (('n',spec['nonquery'],'N'),('d',data_steps,'D')):
            for index in range(1,count+1):
                operation=name+'/'+prefix+format(index,'02d')
                if operation!='PF/n01':events.append(dict(id=operation,phase='ADMITTED',kind=kind,command=operation))
                events.append(dict(id=operation,phase='WAITING_COMPLETION' if operation in waiting else 'DONE',
                                   error=errors.get(operation,''),kind=kind,resultDigest='1'*64))
                if operation in waiting:
                    history.append(dict(operation=operation,kind='open' if operation.startswith('P08-') else 'read',
                        native_done=True,gated=True,released=True,notification_done=True,notifier_quiescent=True,
                        archived=True,retained=False,discarded=True,deliveries=0,callbacks_registered=0,
                        callbacks_finished=0,callback_errors=[],error_type='Refused',error_message=waiting[operation]))
    for index in range(1,32):
        operation='GC/n'+format(index,'02d');events.append(dict(id=operation,phase='ADMITTED',kind='N',command=operation))
        events.append(dict(id=operation,phase='DONE',kind='N',error='',resultDigest='2'*64))
    events.append(dict(id='GC/n32',phase='READY_TO_CLOSE',scope='RETURN_CHANNEL_WITNESS'))
    usage=dict(n=sum(row['controls'] for row in rows)+32,qn=sum(row['queryNew'] for row in rows),
               qr=sum(row['queryReplay'] for row in rows),ib=1573492,ic=59,v=128,targets=10,records=32,credit=655360)
    trace=[dict(seq=index+1,row=order[index%len(order)],label='logical-assertion-'+str(index+1)) for index in range(assertions)]
    report=dict(status='PASS',error=None,rows=rows,assertions=assertions,assertionEvidence=trace,cellHistory=history,
                usage=copy.deepcopy(usage),actualRegressionAdmission=copy.deepcopy(claim),logClose='PENDING_RETURN_CHANNEL')
    report_sha=hashlib.sha256(json.dumps(report,separators=(',',':'),ensure_ascii=True).encode('ascii')).hexdigest()
    trace_sha=hashlib.sha256(json.dumps(trace,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode('ascii')).hexdigest()
    witness=dict(status='PASS',rows=len(rows),assertions=assertions,assertionEvidenceCount=assertions,
                 assertionEvidenceSha256=trace_sha,usage=copy.deepcopy(usage),
                 actualRegressionAdmission=copy.deepcopy(claim),root=claim['rootName'],precloseSummary='result-before-close.json',
                 precloseSummarySha=report_sha,logClose=dict(id='GC/n32',closed=True,
                     method='flush/fsync/close actually returned',remainingResources=0))
    return dict(report=report,witness=witness,claim=claim,events=events)


def run_checks():
    passed=[];negative=[]
    def check(value,label):
        if not value:raise AssertionError('E3_PREPARATION_CHECK:'+label)
        passed.append(label)
    def rejects(action,label):
        try:action()
        except (ValueError,TypeError,KeyError):check(True,label);negative.append(label);return
        raise AssertionError('MISSING_PREPARATION_REFUSAL:'+label)
    bundle={key:json_metadata(BASE/'profiles'/name) for key,name in
            (('inputs','inputs.json'),('cases','cases.json'),('machine','machine.json'),('runtime','runtime-policy.json'))}
    manifest=json_metadata(BASE/'manifest/branches.json')
    old_manifest=json_metadata(OLD/'manifest/branches.json');old_cases=json_metadata(OLD/'profiles/cases.json')
    old_policy=metadata(OLD/'profiles/runtime-policy.json');current_policy=metadata(BASE/'profiles/runtime-policy.json')
    check(current_policy==old_policy,'approved-runtime-policy-is-byte-for-byte-unchanged')
    check(manifest['limits']==old_manifest['limits']==bundle['cases']['limits'],
          'all-original-global-allocations-remain-unchanged')
    check(manifest['executionOrder']==old_manifest['executionOrder'] and len(manifest['executionOrder'])==61,
          'original-61-scenario-order-is-preserved')
    check(manifest['phases']==old_manifest['phases'],'original-PF16-and-GC32-operations-are-unchanged')
    old_rows={row['id']:row for row in old_manifest['branches']}
    for row in manifest['branches']:
        check(all(row[key]==old_rows[row['id']][key] for key in BUDGET_FIELDS),'original-row-budget-and-operation-allocation-'+row['id'])
    check([row['id'] for row in bundle['cases']['cases']]==[row['id'] for row in old_cases['cases']],
          'case-profile-does-not-add-remove-or-reorder-scenarios')
    for row,old in zip(bundle['cases']['cases'],old_cases['cases']):
        check(row['realIO']['windows']==old['realIO']['windows'] and row['realIO']['outputWrites']==old['realIO']['outputWrites'] and
              row['realIO']['expectedRequestUsage']==old['realIO']['expectedRequestUsage'] and
              row['requiredDurability']==old['requiredDurability'] and row.get('productVariant')==old.get('productVariant'),
              'original-window-durability-and-request-allocation-'+row['id'])
    check(bundle['cases']['plannedRequestUsage']==dict(inputBytes=1573492,inputCalls=59,validationBytes=128),
          'planned-request-charge-stays-below-original-reservation-with-no-refund')
    inputs=bundle['inputs'];machine=bundle['machine']
    check('historicalObservedBatchAtUtc' in inputs and 'observedBatchAtUtc' not in inputs and
          inputs['activity']['mediaStatCalls']==inputs['activity']['mediaBytesRead']==0,
          'preparation-declarations-do-not-claim-a-fresh-media-stat-or-read')
    check(all('historicalStat' in row and 'currentStat' not in row and row['currentContentVerified'] is False
              for row in inputs['inputs'].values()) and inputs['admissionFacts']['currentLengthsMatchHistorical'] is None,
          'historical-stat-and-hash-do-not-prove-current-opened-version')
    check(machine['declaredMachineName']=='LZF' and 'historicalMemorySnapshot' in machine and
          machine['activity']['newMachineQueries']==0 and machine['requiredExecutionAdmission']['freshMemoryCollectedInPreparation'] is False,
          'machine-snapshot-does-not-substitute-for-fresh2GiB-and-original-process-baselines')
    for index,offset in enumerate(OFFSETS,1):
        normal=next(row for row in bundle['cases']['cases'] if row['id']=='P01-N'+str(index))['realIO']
        short=next(row for row in bundle['cases']['cases'] if row['id']=='P01-S'+str(index))['realIO']
        check([(row['offsetBytes'],row['requestedBytes']) for row in normal['windows']]==[(offset,65536),(offset,65536)],
              'real-64bit-normal-window-'+str(index))
        check([(row['offsetBytes'],row['requestedBytes'],row['expectedActualBytes']) for row in short['windows']]==
              [(offset+step,65536-step,1) for step in range(4)]+[(offset,4,4)] and
              'WINDOW_UNFILLED' in short['successCriteria'] and short['expectedRequestUsage']['inputBytes']==262142,
              'legal-short-read-UNFILLED-with-no-fifth-delegate-'+str(index))

    gate=load_module('tools','e3_admission.py')
    profile_module=load_module('src','profile_bindings.py');admission=load_module('src','admission.py')
    profile=profile_module.real_profile(bundle)
    check(profile_module.validate_real_profile(profile)==profile and profile['kind']=='REAL_IO' and profile['lengths']==LENGTHS and
          profile_module.boundary_for(profile)==2147483648,'real-profile-is-pure-explicit-geometry')
    check(gate.build_profile(bundle['inputs'])==profile,'launcher-and-Engine-bind-exactly-the-same-normalized-profile-hash')
    geometry=profile_module.validate_geometry(profile)
    check(geometry['B']==2147483648 and geometry['offsets']==OFFSETS and geometry['requestBytes']==65536,
          'geometry-is-not-inferred-from-root-or-selfcheck-name')
    before=copy.deepcopy(bundle);valid=admission.validate_profile(bundle,manifest)
    check(valid['valid'] is True and bundle==before,'declared-real-profile-validates-without-IO-or-mutation')
    for key,value in (('boundary',65536),('kind','SYNTHETIC')):
        changed=copy.deepcopy(profile);changed[key]=value
        rejects(lambda changed=changed:profile_module.validate_real_profile(changed),'real-profile-rejects-'+key)
    for alias in ('L','C','Z'):
        changed=copy.deepcopy(profile);changed['lengths'][alias]+=1
        rejects(lambda changed=changed:profile_module.validate_real_profile(changed),'real-profile-rejects-length-'+alias)
        changed=copy.deepcopy(profile);changed['inputs'][alias]='D:/foreign/'+alias
        rejects(lambda changed=changed:profile_module.validate_real_profile(changed),'real-profile-rejects-path-'+alias)
    for fake_permit in (None,True,{'approved':True},{'profile':'REAL_IO','approved':True,'executionAllowed':True}):
        rejects(lambda fake_permit=fake_permit:profile_module.profile_for_engine(profile,fake_permit,'selfcheck-looks-real'),
                'approval-like-object-is-not-an-original-runtime-permit-'+str(fake_permit))
    def invalid_profile(label,mutate):
        changed=copy.deepcopy(bundle);mutate(changed)
        result=admission.validate_profile(changed,manifest)
        check(result['valid'] is False and bool(result['errors']),label);negative.append(label)
    invalid_profile('large-geometry-cannot-revert-to-synthetic-B',lambda b:b['cases'].__setitem__('boundaryBytes',65536))
    invalid_profile('declared-large-length-cannot-be-rebased',lambda b:b['inputs']['inputs']['L']['historical'].__setitem__('bytes',131072))
    invalid_profile('normal-window-cannot-be-shifted',lambda b:b['cases']['cases'][0]['realIO']['windows'][0].__setitem__('offsetBytes',2147418113))
    invalid_profile('uncharged-window-cannot-delegate-one-byte',lambda b:b['cases']['cases'][0]['realIO']['windows'].append(
        dict(actor='J',offsetBytes=0,requestedBytes=1,expectedActualBytes=1,delegateCalls=1,inputRequestCharged=False,budgetClass='INPUT')))
    invalid_profile('global-control-cap-cannot-increase',lambda b:b['cases']['limits'].__setitem__('control',453))
    invalid_profile('namespace-durability-cannot-be-downgraded',lambda b:b['cases']['cases'][0]['requiredDurability'].update(namespaceRequired=True,level='OS_DATA_SYNC_ACK'))
    for approval in (True,{'approved':True},{'executionAllowed':True,'currentVersionProven':True}):
        inspected=admission.inspect_admission(bundle,manifest,approval=approval,stat_metadata={'openedVersionProven':True})
        check(inspected['executionAllowed'] is False and inspected['cachedStatIsVersionProof'] is False,
              'approval-dictionary-or-cached-stat-does-not-grant-real-entry-'+str(approval))
    calls=[]
    code,denial=admission.request_real_run('unapproved',bundle,manifest,media_reader=lambda:calls.append('media'),helper_launcher=lambda:calls.append('helper'))
    check(code!=0 and not calls and denial['executionAllowed'] is False and denial['outputRootCreated'] is False,
          'legacy-request-entry-never-calls-media-helper-or-creates-root')

    def authority_rejects(action,label):
        try:action()
        except gate.AdmissionError as error:
            check(bool(str(error)),label);negative.append(dict(check=label,reason=str(error)));return
        raise AssertionError('MISSING_AUTHORITY_REFUSAL:'+label)
    logical_token='ab'*32;logical_commitment=hashlib.sha256(bytes.fromhex(logical_token)).hexdigest()
    check(gate.verify_grant(logical_token,logical_commitment) is True and logical_commitment!=gate.GRANT_COMMITMENT,
          'pure-secret-proof-positive-uses-only-an-unrelated-logical-commitment')
    for token in (None,True,{'approved':True},'ab'*31,'0'*64,gate.GRANT_COMMITMENT):
        authority_rejects(lambda token=token:gate.verify_grant(token,gate.GRANT_COMMITMENT),
                          'public-commitment-or-approval-data-is-not-the-formal-secret-'+str(type(token).__name__)+'-'+str(token))
    authority_rejects(lambda:gate.RuntimePermit({},profile),
                      'public-construction-cannot-mint-a-durable-original-runtime-permit')
    authority_rejects(lambda:gate.RuntimePermit({},profile,gate._ISSUER),
                      'module-private-issuer-without-formal-secret-still-cannot-mint-a-runtime-permit')
    prepared=dict(schema=1,batchId=gate.BATCH,machineName='LZF',uniqueRootName=gate.ROOT_NAME,state=gate.STATE,
                  profile='REAL_IO',observerMode='ACTUAL_OS_OBSERVER',executionAuthorized=False,mockAllowed=False,
                  externalGrantRequired=True,maximumG=1,maximumFullAttempts=1,executionDirectory='execution',
                  outputParent='runs',packageRoot=gate.PACKAGE,sealFile='evidence/e3-freeze.json',
                  coordinatorGrantCommitment=gate.GRANT_COMMITMENT,limits=copy.deepcopy(gate.LIMITS),
                  runtimeIdentity=dict(pythonVersion='3.12.14',pointerBits=64,
                     pythonExecutable='C:/Users/benny/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe',
                     pythonDllSha256='2b6fffde96cf24a57fca642aaefd5788816ab5ef8624ea63b722cbceb94d49b1'))
    check(gate.validate_batch(prepared)==prepared and gate.inspect_receipt()['executionAllowed'] is False and
          gate.inspect_receipt()['reservationConsumed'] is False,'fixed-prepared-batch-is-data-with-no-reservation-or-grant')
    for key,value in (('batchId','another'),('machineName','OTHER'),('uniqueRootName','reused-root'),('profile','SYNTHETIC'),
                      ('mockAllowed',True),('executionAuthorized',True),('externalGrantRequired',False),('maximumG',2),
                      ('coordinatorGrantCommitment',logical_commitment)):
        changed=copy.deepcopy(prepared);changed[key]=value
        authority_rejects(lambda changed=changed:gate.validate_batch(changed),'formal-prepared-batch-rejects-'+key)
    read_calls=[]
    authority_rejects(lambda:gate.validate_freeze({},'1'*64,'2'*64,lambda path:read_calls.append(path),'LZF'),
                      'wrong-external-freeze-is-rejected-before-any-runtime-file-read')
    check(not read_calls,'wrong-freeze-does-not-query-inputs-or-source-files')
    authority_rejects(lambda:gate.validate_freeze(dict(schema=1,state=gate.STATE),'1'*64,'1'*64,
                      lambda path:read_calls.append(path),'OTHER'),'wrong-machine-freeze-is-rejected-before-runtime-reads')
    parent=dict(pid=101,creationTime100ns=100001);child=dict(pid=202,creationTime100ns=200002)
    reservation=dict(batchId=gate.BATCH,rootName=gate.ROOT_NAME,expectedFreeze='1'*64,launcher=parent,
                     profileSha256=hashlib.sha256(gate.encoded(profile)).hexdigest())
    launch=dict(batchId=gate.BATCH,expectedFreeze='1'*64,launcher=parent,child=child,
                reservationSha256=hashlib.sha256(gate.encoded(reservation)).hexdigest())
    for role,key in (('parent','pid'),('parent','creationTime100ns'),('child','pid'),('child','creationTime100ns')):
        p=copy.deepcopy(parent);c=copy.deepcopy(child);(p if role=='parent' else c)[key]+=1
        authority_rejects(lambda p=p,c=c:gate.bind_claim(reservation,launch,p,c),
                          'original-owner-PID-reuse-refused-'+role+'-'+key)
    changed=copy.deepcopy(launch);changed['expectedFreeze']='2'*64
    authority_rejects(lambda:gate.bind_claim(reservation,changed,parent,child),'claim-cannot-change-external-freeze')
    check(read_calls==[],'pure-owner-and-grant-tests-have-no-backend-read-or-claim-side-effects')

    completion=load_module('tools','completion_evaluation.py')
    def completed(fixture):
        return completion.evaluate_completion(manifest,fixture['report'],fixture['witness'],fixture['claim'],fixture['events'])
    future=future_completion_fixture(manifest,profile)
    future_before=copy.deepcopy(future);verdict=completed(future)
    check(verdict['accepted'] is True and verdict['executionAllowed'] is False and future==future_before,
          'future-real-batch-completion-uses-173-traced-assertions-with-new-bindings')
    another=future_completion_fixture(manifest,profile,assertions=181,batch='FUTURE-E3-LOGICAL-B',freeze='9'*64)
    check(completed(another)['accepted'] is True,'second-future-batch-is-not-bound-to-old-E2E-hash-160-or-original-FAIL')
    def invalid_completion(label,mutate):
        candidate=copy.deepcopy(future);mutate(candidate)
        # These are newly authored logical reports, not the sealed E2E result.
        # Rebind their hashes so malformed rows/trace must be rejected by their
        # own semantics rather than an incidental stale digest.
        if candidate['report']!=future['report']:
            candidate['witness']['precloseSummarySha']=hashlib.sha256(json.dumps(candidate['report'],separators=(',',':'),
                ensure_ascii=True).encode('ascii')).hexdigest()
            candidate['witness']['assertionEvidenceSha256']=hashlib.sha256(json.dumps(candidate['report']['assertionEvidence'],
                sort_keys=True,separators=(',',':'),ensure_ascii=True).encode('ascii')).hexdigest()
        before=copy.deepcopy(candidate)
        result=completed(candidate)
        check(result['accepted'] is False and bool(result['reasons']),label)
        check(candidate==before,'completion-input-is-not-rewritten-'+label)
        negative.append(dict(check=label,reasons=result['reasons']))
    invalid_completion('future-completion-missing-row',lambda f:f['report']['rows'].pop(2))
    invalid_completion('future-completion-duplicate-row-with-same-count',
                       lambda f:f['report']['rows'].__setitem__(2,copy.deepcopy(f['report']['rows'][1])))
    invalid_completion('future-completion-order-is-exact',
                       lambda f:f['report']['rows'].__setitem__(slice(1,3),list(reversed(f['report']['rows'][1:3]))))
    invalid_completion('future-completion-extra-row',lambda f:f['report']['rows'].append(copy.deepcopy(f['report']['rows'][1])))
    invalid_completion('future-completion-PF-required',lambda f:f['report']['rows'].pop(0))
    invalid_completion('future-completion-row-not-finished',lambda f:f['report']['rows'][1].__setitem__('completed',False))
    invalid_completion('future-completion-query-missing',lambda f:f['report']['rows'][1].__setitem__('queryNew',0))
    invalid_completion('future-completion-row-time-invalid',lambda f:f['report']['rows'][1].__setitem__('elapsedSeconds',float('inf')))
    invalid_completion('future-completion-real-scope-cannot-use-synthetic-row',
                       lambda f:f['report']['rows'][1].__setitem__('scope','SYNTHETIC_CHECKPOINT_ONLY'))
    invalid_completion('future-completion-assertion-count-needs-original-trace',lambda f:f['report'].__setitem__('assertions',174))
    invalid_completion('future-completion-assertion-sequence-gap',lambda f:f['report']['assertionEvidence'][1].__setitem__('seq',3))
    invalid_completion('future-completion-assertion-label-required',lambda f:f['report']['assertionEvidence'][1].__setitem__('label',''))
    invalid_completion('future-completion-assertion-row-approved',lambda f:f['report']['assertionEvidence'][1].__setitem__('row','UNAPPROVED'))
    invalid_completion('future-completion-n32-intent-does-not-prove-return',lambda f:f['witness']['logClose'].__setitem__('closed',False))
    invalid_completion('future-completion-resources-unknown',lambda f:f['witness']['logClose'].__setitem__('remainingResources',None))
    invalid_completion('future-completion-FAIL-not-relabelled',lambda f:f['witness'].__setitem__('status','FAIL'))
    invalid_completion('future-completion-original-claim-cannot-change-root',lambda f:f['claim'].__setitem__('rootName','replacement-root'))
    invalid_completion('future-completion-original-claim-cannot-change-freeze',lambda f:f['claim'].__setitem__('expectedFreeze','0'*64))
    invalid_completion('future-completion-wrong-valid-preclose-hash',lambda f:f['witness'].__setitem__('precloseSummarySha','0'*64))
    def wrong_claim_geometry(fixture):
        fixture['claim']['profileGeometry']['boundary']=65536
        fixture['report']['actualRegressionAdmission']=copy.deepcopy(fixture['claim'])
        fixture['witness']['actualRegressionAdmission']=copy.deepcopy(fixture['claim'])
    invalid_completion('future-completion-cannot-use-small-B-with-a-coherently-bound-real-profile',wrong_claim_geometry)
    invalid_completion('future-completion-WAITING-original-notifier-required',lambda f:f['report']['cellHistory'][0].__setitem__('notifier_quiescent',False))
    invalid_completion('future-completion-WAITING-unknown-retained',lambda f:f['report']['cellHistory'][0].__setitem__('retained',True))
    invalid_completion('future-completion-short-read-must-remain-UNFILLED',lambda f:next(
        row for row in f['report']['rows'] if row['branch']=='P01-S1').__setitem__('windowOutcome','FILLED'))
    invalid_completion('future-completion-short-read-cannot-invent-unread-bytes',lambda f:next(
        row for row in f['report']['rows'] if row['branch']=='P01-S1').__setitem__('windowBytesObserved',65536))
    invalid_completion('future-completion-unapproved-Refused-error',lambda f:next(
        row for row in f['events'] if row.get('id')=='P01-N1/n01' and row.get('phase')=='DONE').__setitem__('error','UNAPPROVED'))
    invalid_completion('future-completion-GC-missing-return',lambda f:f['events'].remove(next(
        row for row in f['events'] if row.get('id')=='GC/n05' and row.get('phase')=='DONE')))
    driver=load_module('tools','e3_driver.py')
    identities=dict(G=dict(future['claim']['child'],owner='G'),
                    J=dict(pid=303,creationTime100ns=300003,owner='logical-J'),
                    R=dict(pid=404,creationTime100ns=400004,owner='logical-R'))
    baselines={role:dict(identity,threads=5 if role=='G' else 20,handles=160 if role=='G' else 200,
                        workingSetBytes=1048576,privateBytes=1048576) for role,identity in identities.items()}
    peaks={role:{key:value[key] for key in ('threads','handles','workingSetBytes','privateBytes')}
           for role,value in baselines.items()};peaks['G'].update(threads=12,handles=200)
    exits={role:dict(pid=identities[role]['pid'],instance=identities[role]['owner'],code=0,exited=True) for role in ('J','R')}
    joined=dict(unknown=False,alive=False,startInProgress=False,joined=True,entered=True,exited=True,
                joinReturned=True,creditReleased=True,releaseProof='THREAD_JOIN_PROVEN')
    logical_resources=dict(status='PASS',nativePending=[],logOwnershipPending=False,
        logClose=dict(closed=True,remainingResources=0,id='GC/n32',method='flush/fsync/close actually returned',exitedHelpers=exits),
        callbackHub=dict(lifecycle='CLOSED',workersAlive=0,remainingCredits=[],ownershipPending=False,
                         blocked=None,startupError=None,notices=1,
                         cells=0,queued=0,active=0,monitorInFlight=0,workers={name:dict(joined) for name in ('notify','deadline')}),
        metadataCommitStatus='HEALTHY',metadataUnknownRequestedBytes=0,metadataPeak=1024,
        identityQueries=dict(G=1,J=2,R=2,perActorCap=512,extraRPCs=0,extraSourceBytes=0),
        ledgerPeaks=dict(os=12,media=3,buffers=1),privateCells=dict(total=1,peak=1,active=0,retained=0,archived=1),
        runtimeObservation=dict(wired=True,started=True,finished=True,nativeQueryPending=False,mode='ACTUAL_OS_OBSERVER',
            mockMetricsUsed=False,originalIdentities=identities,
            freshMemory=dict(status='MEMORY_READY',stopAcceptance=False,observation=dict(availablePhysicalBytes=2147483648)),
            observation=dict(status='OBSERVED',stopAcceptance=False,reasons=[],observationFinished=True,runtimePolicyApproved=True,
                gBaselineAnchor='ORIGINAL_PROCESS_BEFORE_PF_NOT_RESET',samples=2,maxObservedGapSeconds=1,sampleDurationSeconds=.001,
                baselines=baselines,peaks=peaks,retired=copy.deepcopy(exits)),
            reader=dict(openedHandles=2,closedHandles=2,closeUnknown=False,observerCreditHeld=False,maximumOwnedHandlesObserved=1)))
    resource_verdict=driver.resource_gate(logical_resources,bundle['runtime'],future['claim'],20.0)
    check(resource_verdict['accepted'] is True and resource_verdict['additionalSamples']==0 and
          resource_verdict['executionAllowed'] is False,'pure-resource-model-is-accepted-without-observing-any-process')
    resource_cases=[(('logClose','closed'),False),(('nativePending',),['unknown-native']),
                    (('callbackHub','workers','notify','joined'),False),(('callbackHub','ownershipPending'),True),
                    (('runtimeObservation','reader','closeUnknown'),True),
                    (('runtimeObservation','reader','observerCreditHeld'),True),
                    (('runtimeObservation','observation','samples'),202),
                    (('runtimeObservation','observation','maxObservedGapSeconds'),2.50001),
                    (('runtimeObservation','observation','sampleDurationSeconds'),.10001),
                    (('runtimeObservation','observation','peaks','G','handles'),225),
                    (('runtimeObservation','observation','peaks','R','handles'),513),
                    (('runtimeObservation','originalIdentities','G','creationTime100ns'),999999),
                    (('metadataUnknownRequestedBytes',),1),(('privateCells','total'),65),(('ledgerPeaks','buffers'),9),
                    (('identityQueries','J'),513),(('identityQueries','extraRPCs'),1),(('identityQueries','extraSourceBytes'),1)]
    for path,value in resource_cases:
        candidate=copy.deepcopy(logical_resources);target=candidate
        for key in path[:-1]:target=target[key]
        target[path[-1]]=value
        result=driver.resource_gate(candidate,bundle['runtime'],future['claim'],20.0)
        check(result['accepted'] is False and bool(result['reasons']),'pure-resource-gate-rejects-'+'-'.join(path))
        negative.append(dict(check='resource-'+'-'.join(path),reasons=result['reasons']))
    for elapsed in (181.0,float('nan'),None):
        result=driver.resource_gate(logical_resources,bundle['runtime'],future['claim'],elapsed)
        check(result['accepted'] is False and 'ORIGINAL_180_SECOND_COMPLETION_BOUND' in result['reasons'],
              'pure-resource-gate-rejects-unknown-or-over180-completion-'+str(elapsed))
    for folder,name in (('src','profile_bindings.py'),('src','admission.py'),('tools','e3_admission.py'),('tools','completion_evaluation.py')):
        tree=ast.parse(metadata(BASE/folder/name).decode('utf-8-sig'))
        imports=[node.module.split('.')[0] for node in ast.walk(tree) if isinstance(node,ast.ImportFrom) and node.module]
        imports += [alias.name.split('.')[0] for node in ast.walk(tree) if isinstance(node,ast.Import) for alias in node.names]
        check(not set(imports)&FORBIDDEN,'preparation-contract-imports-no-runner-native-or-OS-adapter-'+name)
    gate_tree=ast.parse(metadata(BASE/'tools/e3_admission.py').decode('utf-8-sig'))
    def fn(tree,name):return next(node for node in ast.walk(tree) if isinstance(node,ast.FunctionDef) and node.name==name)
    def calls(node,name):return [call for call in ast.walk(node) if isinstance(call,ast.Call) and
                                ((isinstance(call.func,ast.Name) and call.func.id==name) or
                                 (isinstance(call.func,ast.Attribute) and call.func.attr==name))]
    for name in ('reserve','claim'):
        source=fn(gate_tree,name);verify=calls(source,'verify_grant')[0]
        check(isinstance(verify.args[1],ast.Name) and verify.args[1].id=='GRANT_COMMITMENT' and
              verify.lineno<calls(source,'verify_runtime')[0].lineno,
              'formal-'+name+'-pins-source-secret-proof-before-runtime-or-media-admission')
    source=fn(gate_tree,'claim');claim_write=next(call for call in calls(source,'create_new') if
            isinstance(call.args[0],ast.Constant) and call.args[0].value=='execution/claim.json')
    check(claim_write.lineno<calls(source,'RuntimePermit')[0].lineno,
          'formal-runtime-capability-is-issued-only-after-durable-original-claim')
    driver_tree=ast.parse(metadata(BASE/'tools/e3_driver.py').decode('utf-8-sig'))
    source=fn(driver_tree,'run_claimed')
    check(calls(source,'claim')[0].lineno<calls(source,'execute')[0].lineno,
          'driver-claims-original-identity-before-any-execution-callback')
    launch_tree=ast.parse(metadata(BASE/'tools/launch-once.py').decode('utf-8-sig'));source=fn(launch_tree,'run_once')
    check(calls(source,'reserve')[0].lineno<calls(source,'stage_grant')[0].lineno<calls(source,'spawn')[0].lineno,
          'launcher-uses-one-secret-bound-reservation-before-staging-and-the-only-spawn')
    check(len(calls(source,'spawn'))==1,'prepared-launcher-has-one-spawn-site-with-no-retry')
    activity=dict(newG=0,helpersStarted=0,newOSMetricSamples=0,newActualAttempts=0,newActualPasses=0,
                  compileInvocations=0,originalEvidenceWrites=0,mediaStatCalls=0,mediaBytesRead=0)
    check(all(type(value) is int and value==0 for value in activity.values()),'preparation-activity-is-exact-integer-zero')
    return dict(schema=1,scope='E3_PREPARATION_STATIC_AND_SYNTHETIC_GUARDS',status='PASS',assertions=len(passed),checks=passed,
                negativeCases=negative,**activity,metadataReadUsage=dict(_READS),reservationConsumed=False,
                rootCreated=False,outputRootCreated=False,noInFlight=True,executionAllowed=False,realPFRun=False,real61Run=False,
                simulatedCases=[dict(id='future-completion-A',scope='PURE_JSON_ONLY',assertions=173,actualRuns=0),
                                dict(id='future-completion-B',scope='PURE_JSON_ONLY',assertions=181,actualRuns=0),
                                dict(id='unrelated-logical-secret-proof',formalCommitmentUsed=False,actualClaims=0)],
                limitations='Metadata and memory-only guards; no current media stat/bytes, original process, native resource, real PF/full, device, compile, actual claim or execution permit.')


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');options=parser.parse_args()
    value=run_checks() if options.check else dict(scope='E3_PREPARATION_INSPECT',status='NOT_RUN',executionAllowed=False,
                                               reservationConsumed=False,rootCreated=False,newActualAttempts=0)
    print(json.dumps(value,sort_keys=True,separators=(',',':')))
