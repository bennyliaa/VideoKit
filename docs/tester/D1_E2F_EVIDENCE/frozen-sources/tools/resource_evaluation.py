"""Pure evaluation of bounded, already-read E2E evidence. No filesystem/OS IO.

Acceptance is limited evidence reevaluation, never a replacement E2E result or
an execution capability. The caller must AND this with completion evaluation
and the bounded reader's complete immutable-source integrity verification.
"""
import hashlib
import json
import math
import struct
import zlib

SCOPE='EVIDENCE_REEVALUATION_RESOURCES'
BATCH='D1-E2E-201dffc63b60405da3046f21fa7ff26d'
ROOT='e2e-201dffc63b60405da3046f21fa7ff26d'
PREFIX='selfcheck/'+ROOT+'/'
SEAL_SHA='aa59420cff4153395af2ab9b97eb47d8f560e91763b730f47c0fda3c0578b66a'
RESULT_SHA='baa6a1ed87764a5d16b1d282717824110d0082bc188606edf4affb33377750ea'
PRECLOSE_SHA='702d8505e16bf504564179c14477e7cfe50af35c922531034c66645d6bc79032'
POLICY_LOG_SHA='cde527551ddcbc5ecabb18306a485cc97999aadd23b805628dd5c53c609577dc'
METRICS=('threads','handles','workingSetBytes','privateBytes')
DELTA_KEYS=dict(threads='deltaThreads',handles='deltaHandles',workingSetBytes='deltaWorkingSetBytes',privateBytes='deltaPrivateBytes')
IDENTITIES={
    'G':dict(pid=40980,creationTime100ns=134366511035829924,owner='G'),
    'J':dict(pid=40896,creationTime100ns=134366511040679592,owner='03c3668c-6a2d-4c33-b6f7-888ab4d402c0'),
    'R':dict(pid=31648,creationTime100ns=134366511041890791,owner='f9073814f11c42389cc1108fff33b4e3')}
LAUNCHER=dict(pid=39108,creationTime100ns=134366511032212370)
G_PROCESS={key:IDENTITIES['G'][key] for key in ('pid','creationTime100ns')}
LIMITS={
    'G':dict(threads=16,handles=256,workingSetBytes=268435456,privateBytes=268435456,deltaThreads=12,deltaHandles=64,deltaWorkingSetBytes=134217728,deltaPrivateBytes=134217728),
    'J':dict(threads=64,handles=512,workingSetBytes=805306368,privateBytes=805306368,deltaThreads=32,deltaHandles=128,deltaWorkingSetBytes=268435456,deltaPrivateBytes=268435456),
    'R':dict(threads=64,handles=512,workingSetBytes=536870912,privateBytes=536870912,deltaThreads=32,deltaHandles=128,deltaWorkingSetBytes=268435456,deltaPrivateBytes=268435456)}
ORIGINAL_RESULT=dict(status='FAIL',originalGExitCode=2,originalToolExitCode=1,originalAssertions=160,actualFullPasses=0,reservationConsumed=True)

class EvidenceError(ValueError):pass
def need(condition,reason):
    if not condition:raise EvidenceError(reason)
def sha(data):return hashlib.sha256(data).hexdigest()
def encoded(value):return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode('ascii')
def count(value,maximum=None):return type(value) is int and value>=0 and (maximum is None or value<=maximum)
def finite(value):return type(value) in (int,float) and math.isfinite(value) and value>=0
def unique(pairs):
    value={}
    for key,item in pairs:
        need(key not in value,'JSON_DUPLICATE_KEY');value[key]=item
    return value
def invalid_number(value):raise EvidenceError('JSON_NONFINITE_NUMBER')
def decode(raw):return json.loads(raw.decode('utf-8-sig'),object_pairs_hook=unique,parse_constant=invalid_number)
def fixture(name):return name.split('/')[-1] in ('L.bin','C.bin','Z.bin') or name.endswith('.out')
def ceil_kib(value):return (value+1023)//1024

def _load(context):
    bundle=context['bundle'];files=bundle['files']
    need(type(files) is dict and 1<=len(files)<=1024,'RESULT_INPUT_FILE_LIMIT')
    total=0
    for name,raw in files.items():
        need(type(name) is str and ':' not in name and '\\' not in name and all(part not in ('','.','..') for part in name.split('/')),'RESULT_INPUT_PATH')
        need(name.startswith('execution/') or name.startswith(PREFIX),'RESULT_INPUT_SCOPE')
        need(type(raw) is bytes,'RESULT_INPUT_BYTES');total+=len(raw)
    need(total<=16777216,'RESULT_INPUT_BYTE_LIMIT')
    need(type(bundle['sealBytes']) is bytes and len(bundle['sealBytes'])<=2097152,'SEAL_INPUT_BYTES')
    context.update(files=files,result=decode(files['execution/result-manifest.json']),seal=decode(bundle['sealBytes']),
                   preclose=decode(files[PREFIX+'result-before-close.json']),driver=decode(files['execution/driver-result.json']),
                   launcher=decode(files['execution/launcher-result.json']),reservation=decode(files['execution/reservation.json']),
                   launch=decode(files['execution/launch.json']),claim=decode(files['execution/claim.json']),
                   policy=bundle['policy'],manifest=bundle['manifest'],resultInputBytes=total)
    # Decoded inputs and byte counts are not successful binding proofs. Keep
    # them available so one failed anchor cannot hide a separate semantic fault.
    context['witness']=context['driver']['driverWitness']
    context['observedOutputUsage']={
        'fixtureBytes':sum(len(raw) for name,raw in files.items() if fixture(name)),
        'metadataBytes':sum(len(raw) for name,raw in files.items() if not fixture(name))}
    context['observedProductionMetadataBytes']=sum(len(raw) for name,raw in files.items() if name.startswith(PREFIX) and not fixture(name))
    context['observedCombinedUsage']={key:context['seal']['prepUsage'][key]+value for key,value in context['observedOutputUsage'].items()}

def _original_binding(c):
    b=c['bundle'];files=c['files'];seal=c['seal'];result=c['result'];pre=c['preclose'];driver=c['driver'];launcher=c['launcher']
    need(sha(b['sealBytes'])==SEAL_SHA,'ORIGINAL_SEAL_SHA')
    need(sha(files['execution/result-manifest.json'])==RESULT_SHA,'ORIGINAL_RESULT_MANIFEST_SHA')
    need(sha(files[PREFIX+'result-before-close.json'])==PRECLOSE_SHA,'ORIGINAL_PRECLOSE_SHA')
    need(seal['schema']==1 and seal['state']=='PREPARED_NOT_RUN_PENDING_TESTER' and seal['batchId']==BATCH,'ORIGINAL_SEAL_IDENTITY')
    need(result['schema']==1 and result['scope']=='E2E_EXECUTION_RESULT_MANIFEST' and result['batchId']==BATCH and result['expectedFreeze']==SEAL_SHA,'RESULT_MANIFEST_IDENTITY')
    need(driver['scope']=='E2E_ACTUAL_SELF_OWNED_DRIVER' and driver['status']=='FAIL' and driver['firstFailure']=='INCOMPLETE_FULL_ROW_COUNT','ORIGINAL_DRIVER_FAILURE_PRESERVED')
    need(launcher['scope']=='E2E_ORIGINAL_LAUNCHER_RESULT' and launcher['batchId']==BATCH and launcher['expectedFreeze']==SEAL_SHA and launcher['status']=='FAIL','ORIGINAL_LAUNCHER_FAILURE_PRESERVED')
    need(result['status']=='FAIL' and pre['status']=='PASS' and pre['error'] is None,'ORIGINAL_PRECLOSE_AND_FINAL_RESULTS_DISTINCT')
    witness=driver['driverWitness'];c['witness']=witness
    need(witness['status']=='FAIL' and witness['scope']=='E2C_SYNTHETIC_INTEGRATION_ONLY' and witness['root']==ROOT,'ORIGINAL_WITNESS_IDENTITY')
    need(pre['assertions']==witness['assertions']==160,'ORIGINAL_ASSERTIONS_PRESERVED')
    need(witness['precloseSummary']=='result-before-close.json' and witness['precloseSummarySha']==PRECLOSE_SHA,'RETURN_CHANNEL_PRECLOSE_BINDING')
    need(driver['actualFullAttempt'] is driver['productionScopePreserved'] is True and driver['mockMetricsUsed'] is driver['realExecutionAllowed'] is False,'ACTUAL_SELF_OWNED_SCOPE')
    for key,value in (('preclose',pre),('driver',driver),('launcher',launcher)):
        if key in b:need(b[key]==value,'DERIVED_'+key.upper()+'_DIFFERS_FROM_ORIGINAL_BYTES')
    integrity=b['sourceIntegrity'];need(integrity['status']=='VERIFIED' and integrity['sealSha256']==SEAL_SHA and integrity['immutableFiles']==90,'IMMUTABLE_SOURCE_INTEGRITY_REQUIRED')
    for key in ('mediaRead','realPFRun','real61Run'):need(witness[key] is False,'REAL_MEDIA_SCOPE_REJECTED')
    c['facts']['originalBindings']=dict(sealSha256=SEAL_SHA,resultManifestSha256=RESULT_SHA,precloseSha256=PRECLOSE_SHA,sourceIntegrityRequired=True,originalAssertions=160)

def _identities(c):
    reservation=c['reservation'];launch=c['launch'];claim=c['claim'];driver=c['driver'];launcher=c['launcher']
    need(reservation['schema']==1 and reservation['scope']=='E2E_ONE_SHOT_RESERVATION' and reservation['batchId']==BATCH and reservation['rootName']==ROOT,'RESERVATION_IDENTITY')
    need(reservation['consumed'] is reservation['createdBeforeG'] is True and reservation['refundAllowed'] is False and reservation['maximumG']==1,'RESERVATION_ONCE_CONSUMED')
    need(reservation['expectedFreeze']==launch['expectedFreeze']==claim['expectedFreeze']==SEAL_SHA,'CLAIM_FREEZE_IDENTITY')
    need(reservation['launcher']==launch['launcher']==claim['launcher']==LAUNCHER and launch['child']==claim['child']==G_PROCESS,'ORIGINAL_PARENT_CHILD_IDENTITY')
    need(launch['batchId']==claim['batchId']==BATCH and claim['rootName']==ROOT and claim['schema']==1 and claim['scope']=='E2E_SINGLE_ACTUAL_SELF_OWNED_CLAIM','CLAIM_BATCH_ROOT')
    need(launch['reservationSha256']==claim['reservationSha256']==sha(c['files']['execution/reservation.json'])==sha(encoded(reservation)),'RESERVATION_RAW_CANONICAL_HASH')
    need(claim['launchSha256']==sha(c['files']['execution/launch.json'])==sha(encoded(launch)),'LAUNCH_RAW_CANONICAL_HASH')
    need(claim['profile']=='SYNTHETIC' and claim['observerMode']=='ACTUAL_OS_OBSERVER' and claim['mockMetricsUsed'] is claim['realExecutionAllowed'] is False,'CLAIM_ACTUAL_OS_ONLY')
    need(reservation['productionBindings']==c['seal']['productionBindings'],'RESERVATION_PRODUCTION_BINDINGS')
    need(driver['claim']==c['witness']['actualRegressionAdmission']==c['preclose']['actualRegressionAdmission']==claim,'ORIGINAL_CLAIM_RETURN_BINDING')
    need(launcher['originalChild']==G_PROCESS and launcher['originalChildExitObserved'] is True and launcher['originalChildExitCode']==2 and launcher['reservationConsumed'] is True,'ORIGINAL_G_EXIT_AND_CONSUMPTION')
    need(launcher['stoppedWaitingOnly'] is False and launcher['remaining']=={} and launcher['noInFlight'] is driver['noInFlight'] is c['result']['noInFlight'] is True,'ORIGINAL_NO_INFLIGHT_RETURN')
    receipt=c['bundle']['originalCallReceipt']
    need(receipt['exit_code']==1 and finite(receipt['wall_time_seconds']) and receipt['wall_time_seconds']<=200,'ORIGINAL_CALLER_EXIT_BOUND')
    need(json.loads(receipt['output'])==launcher,'ORIGINAL_CALLER_RECEIPT_BINDING')
    c['facts']['identities']=dict(launcher=dict(LAUNCHER),roles={role:dict(value) for role,value in IDENTITIES.items()},GExitCode=2,toolExitCode=1,callerSeconds=receipt['wall_time_seconds'],claimBeforeProduction=True)

def _outputs(c):
    files=c['files'];result=c['result'];seal=c['seal']
    need(result['complete'] is result['resultHashComplete'] is result['originalChildExitObserved'] is True,'FINAL_OUTPUT_INVENTORY_REQUIRED')
    entries=result['files'];need(type(entries) is list and len(entries)==145 and len(files)==146,'EXACT_ORIGINAL_OUTPUT_FILE_SET')
    need(len({row['path'] for row in entries})==len(entries) and {row['path'] for row in entries}==set(files)-{'execution/result-manifest.json'},'OUTPUT_MANIFEST_EXACT_MEMBERS')
    usage=dict(metadataBytes=0,fixtureBytes=0);wrapper=0
    for name,raw in files.items():
        kind='FIXTURE' if fixture(name) else 'METADATA';usage['fixtureBytes' if kind=='FIXTURE' else 'metadataBytes']+=len(raw)
        if name.startswith('execution/'):wrapper+=len(raw)
    for row in entries:
        raw=files[row['path']]
        need(count(row['bytes']) and len(raw)==row['bytes'] and sha(raw)==row['sha256'],'OUTPUT_FILE_HASH_OR_LENGTH')
        need(row['kind']==('FIXTURE' if fixture(row['path']) else 'METADATA'),'OUTPUT_FILE_CLASSIFICATION')
    need(result['manifestBytes']==len(files['execution/result-manifest.json']),'RESULT_MANIFEST_OWN_BYTES')
    prep=seal['prepUsage'];need(prep==result['prepUsage'] and count(prep['metadataBytes'],819200) and prep['fixtureBytes']==0,'PREPARATION_USAGE_BINDING')
    declared=sum(row['bytes'] for row in seal['immutableFiles'] if row['path'].startswith('docs/coder/d1e2e/evidence/'))
    need(prep['metadataBytes']==declared+len(c['bundle']['sealBytes']) and seal['sealBytes']==len(c['bundle']['sealBytes']),'PREPARATION_SEAL_OWN_BYTES')
    combined={key:prep[key]+usage[key] for key in usage}
    need(result['outputUsage']==usage and result['combinedUsage']==combined and result['wrapperMetadataBytes']==wrapper,'OUTPUT_AND_COMBINED_BYTE_LEDGER')
    need(combined['metadataBytes']<=4194304 and combined['fixtureBytes']<=2097152 and wrapper<=196608 and usage['fixtureBytes']<=790528,'COMBINED_OUTPUT_CAP')
    need(usage['metadataBytes']-wrapper<=3178496,'PRODUCTION_METADATA_CAP')
    caps=result['caps'];need(caps['metadataBytes']==4194304 and caps['fixtureBytes']==2097152 and caps['wrapperMetadataBytes']==196608 and caps['productionMetadataPeakBytes']==3178496,'OUTPUT_CAPS_UNCHANGED')
    independent=[]
    for name,length in (('L.bin',131072),('C.bin',4096),('Z.bin',0)):
        expected=(bytes(range(251))*((length+250)//251))[:length];raw=files[PREFIX+name]
        need(raw==expected,'INDEPENDENT_AUTHORED_INPUT_BYTES');independent.append(dict(name=name,bytes=len(raw),sha256=sha(raw)))
    for index in range(1,11):
        name='T'+str(index).zfill(2)+'.out';raw=files[PREFIX+name]
        expected=bytes(range(32)) if index in (1,5) else b'Z\0xy\0\0\0abc' if index==2 else b'\0' if index in (3,4) else b''
        need(raw==expected,'INDEPENDENT_CLOSED_OUTPUT_BYTES');independent.append(dict(name=name,bytes=len(raw),sha256=sha(raw)))
    c['facts']['outputLedger']=dict(files=len(files),outputUsage=usage,prepUsage=prep,combinedUsage=combined,wrapperMetadataBytes=wrapper,productionMetadataBytes=usage['metadataBytes']-wrapper,independentlyVerifiedInputsAndOutputs=independent)

def _snapshots(c):
    tasks={'PF'}|{row['task'] for row in c['manifest']['branches']};need(len(tasks)==32,'APPROVED_RECORD_TASK_SET')
    states={};slots=0
    for task in sorted(tasks):
        found=[]
        for slot in (0,1):
            name=PREFIX+task+'/state'+str(slot)+'.slot'
            if name not in c['files']:continue
            raw=c['files'][name];need(len(raw)==8192,'SNAPSHOT_SIZE');sequence,length,reserved=struct.unpack('<qiI',raw[:16])
            need(sequence>0 and sequence%2==slot and 0<=length<=8144 and reserved==0,'SNAPSHOT_HEADER')
            payload=raw[48:48+length];need(sha(raw[:16]+payload)==raw[16:48].hex(),'SNAPSHOT_DIGEST')
            decompressor=zlib.decompressobj();logical=decompressor.decompress(payload,65537)
            need(len(logical)<=65536 and decompressor.eof and not decompressor.unused_data,'SNAPSHOT_LOGICAL_BOUND')
            state=decode(logical);need(state['schema']==3 and state['task']==task and state['batch']==ROOT,'SNAPSHOT_TASK_BATCH_IDENTITY')
            found.append((sequence,state));slots+=1
        need(found,'ADMITTED_TASK_SNAPSHOT_MISSING');states[task]=max(found,key=lambda row:row[0])[1]
    c['states']=states;pf=states['PF'];actors=pf['actors'];need(set(actors)=={'J','R'},'PF_ORIGINAL_HELPER_ACTORS')
    for role in ('J','R'):
        actor=actors[role];identity=IDENTITIES[role]
        need(actor['pid']==identity['pid'] and actor['instance']==identity['owner'] and actor['creationTime100ns']==identity['creationTime100ns'],'PF_ORIGINAL_HELPER_IDENTITY')
    command=pf['commands']['GC/n32']
    need(command['status']=='READY_TO_CLOSE' and command['label']=='logClose' and pf['globalLogOutcome']=='RETURN_CHANNEL_REQUIRED','GC_N32_INTENT_IS_NOT_RETURN')
    need(pf['finalBudget']==c['witness']['usage'],'PF_FINAL_BUDGET_BINDING')
    c['facts']['snapshots']=dict(tasks=len(states),slots=slots,selection='HIGHEST_VALID_SEQUENCE_OF_PRESENT_ORIGINAL_SHARDS',GCn32SnapshotIsIntentOnly=True)

def _global_log(c):
    raw=c['files'][PREFIX+'global.log'];need(raw.endswith(b'\n') and len(raw)<=131072,'GLOBAL_LOG_BOUND')
    lines=raw.splitlines(keepends=True);need(lines[0]==b'E2A SYNTHETIC TOOL INTEGRATION\n','GLOBAL_LOG_HEADER')
    metrics=[];headers=[];events=[];metric_bytes=0;metric_positions=[]
    for index,line in enumerate(lines[1:],1):
        value=decode(line)
        if type(value) is list:
            need(len(line)<=128 and len(value)==4,'METRIC_ROW_BOUND');metrics.append(value);metric_bytes+=len(line);metric_positions.append(index)
        elif type(value) is dict and 'runtimeMetricFormat' in value:
            need(len(line)<=1024,'METRIC_HEADER_BOUND');headers.append(value);metric_bytes+=len(line)
        else:need(type(value) is dict and len(line)<=1024,'GLOBAL_EVENT_SCHEMA');events.append(value)
    need(len(headers)==1 and headers[0]==dict(runtimeMetricFormat=['milliseconds','G','J','R'],units=['threads','handles','workingSetKiB','privateKiB'],policySha256=POLICY_LOG_SHA,scope='SAMPLED_ORIGINAL_TOOL_INSTANCES'),'ORIGINAL_METRIC_POLICY_HEADER')
    ready=[event for event in events if event.get('id')=='GC/n32']
    need(ready==[dict(id='GC/n32',phase='READY_TO_CLOSE',scope='RETURN_CHANNEL_WITNESS')] and decode(lines[-1])==ready[0],'GC_N32_LAST_INTENT_RECORD')
    event_bytes=len(raw)-metric_bytes
    need(metric_bytes<=26752 and event_bytes<=104320,'SPLIT_GLOBAL_LOG_CAP')
    counters=c['witness']['runtimeObservation']['log'];need(counters==c['preclose']['runtimeObservation']['log'],'PRECLOSE_METRIC_COUNTER_BINDING')
    need(counters['metricBytes']==metric_bytes and counters['metricRows']==len(metrics) and counters['eventBytes']+len(lines[-1])==event_bytes,'FINAL_N32_EVENT_BYTES_SEPARATE_FROM_PRECLOSE')
    c.update(metric_rows=metrics,global_events=events)
    c['facts']['log']=dict(totalBytes=len(raw),eventBytes=event_bytes,metricBytes=metric_bytes,metricRows=len(metrics),precloseEventBytes=counters['eventBytes'],postSnapshotN32EventBytes=len(lines[-1]),GCn32DiskRowIsIntentOnly=True)

def _metrics(c):
    policy=c['policy'];need(policy['state']=='APPROVED_TOOL_STRATEGY' and policy['executionAuthorized'] is False and policy['limits']==LIMITS,'APPROVED_RESOURCE_POLICY')
    need((policy['intervalSeconds'],policy['maxSamples'],policy['maxGapSeconds'],policy['sampleDeadlineSeconds'])==(1,201,2.5,.1),'ORIGINAL_SAMPLE_POLICY')
    need(policy['managedLimits']==dict(osResources=24,mediaHandles=6,buffers64KiB=8) and policy['maxThreadEntries']==16384 and policy['maxRecordBytes']==128 and policy['maxLogBytes']==26752 and policy['minimumAvailablePhysicalBytes']==2147483648,'APPROVED_MANAGED_AND_OBSERVER_LIMITS')
    need(sha(json.dumps(policy,separators=(',',':'),ensure_ascii=True).encode())==POLICY_LOG_SHA,'POLICY_CANONICAL_LOG_BINDING')
    runtime=c['witness']['runtimeObservation'];obs=runtime['observation'];reader=runtime['reader'];rows=c['metric_rows']
    need(runtime==c['preclose']['runtimeObservation'],'ORIGINAL_RUNTIME_RETURN_BINDING')
    need(runtime['wired'] is runtime['started'] is runtime['finished'] is True and runtime['mode']=='ACTUAL_OS_OBSERVER','ACTUAL_OS_OBSERVATION_REQUIRED')
    need(runtime['mockMetricsUsed'] is runtime['nativeQueryPending'] is runtime['realExecutionAuthorized'] is False and runtime['policyState']=='APPROVED_TOOL_STRATEGY','NO_MOCK_OR_UNKNOWN_OBSERVER')
    need(runtime['newThreads']==runtime['newRPC']==runtime['newJournalTransactions']==0,'ORIGINAL_OBSERVER_OVERHEAD_CONTRACT')
    need(runtime['GAnchor']=='BEFORE_PF_N01_NEVER_RESET' and runtime['originalIdentities']==IDENTITIES and obs['gBaselineAnchor']=='ORIGINAL_PROCESS_BEFORE_PF_NOT_RESET','ORIGINAL_IDENTITIES_AND_BASELINE_ANCHOR')
    need(obs['scope']=='APPROVED_TOOL_RUNTIME_OBSERVATION' and obs['status']=='OBSERVED' and obs['stopAcceptance'] is False and obs['reasons']==[],'OBSERVER_STOP_LATCH_MUST_BE_CLEAR')
    need(obs['runtimePolicyApproved'] is obs['observationFinished'] is obs['peaksAreSampled'] is True and obs['realExecutionApproved'] is False,'OBSERVER_FINISHED_APPROVAL_FACTS')
    need(obs['baselineRoles']==obs['registeredRoles']==['G','J','R'] and obs['activeRoles']==['G'],'ORIGINAL_ROLE_LIFECYCLE')
    need(count(obs['samples'],201) and obs['samples']==len(rows)==reader['cycles'] and rows and rows[0][0]==0,'ORIGINAL_SAMPLE_CYCLE_COUNT')
    need(finite(obs['sampleDurationSeconds']) and obs['sampleDurationSeconds']<=.1 and finite(obs['maxObservedGapSeconds']) and obs['maxObservedGapSeconds']<=2.5,'ORIGINAL_SAMPLE_DURATION_OR_GAP_GUARD')
    times=[row[0] for row in rows];need(all(count(value) for value in times) and all(a<b for a,b in zip(times,times[1:])),'METRIC_SAMPLE_CLOCK_MONOTONIC')
    gaps=[(b-a)/1000 for a,b in zip(times,times[1:])]
    need(all(.899<=gap<=2.601 for gap in gaps) and (not gaps or abs(max(gaps)-obs['maxObservedGapSeconds'])<=.102),'COMPACT_LOG_GAP_AND_GUARD_COHERENCE')
    roles={}
    for column,role in enumerate(('G','J','R'),1):
        baseline=obs['baselines'][role];latest=obs['observations'][role];peak=obs['peaks'][role];identity=IDENTITIES[role]
        need(all(baseline[key]==latest[key]==identity[key] for key in ('pid','creationTime100ns','owner')),'OBSERVED_ORIGINAL_ROLE_IDENTITY:'+role)
        samples=[row[column] for row in rows if row[column] is not None];need(samples,'ROLE_BASELINE_MISSING:'+role)
        need(all(type(row) is list and len(row)==4 and all(count(value) for value in row) for row in samples),'COMPACT_METRIC_VALUE_SCHEMA:'+role)
        first=next(index for index,row in enumerate(rows) if row[column] is not None)
        need(all(row[column] is not None for row in rows[first:]) and first==column-1,'FIXED_ORIGINAL_HELLO_BASELINE_ORDER:'+role)
        for index,key in enumerate(METRICS):
            need(count(baseline[key]) and count(latest[key]) and count(peak[key]) and peak[key]>=max(baseline[key],latest[key]),'RAW_METRIC_PEAK_SCHEMA:'+role+':'+key)
            need(peak[key]<=LIMITS[role][key] and peak[key]-baseline[key]<=LIMITS[role][DELTA_KEYS[key]],'ABSOLUTE_OR_ORIGINAL_DELTA_LIMIT:'+role+':'+key)
            encode_value=(lambda value:value) if index<2 else ceil_kib
            need(samples[0][index]==encode_value(baseline[key]) and samples[-1][index]==encode_value(latest[key]) and max(row[index] for row in samples)==encode_value(peak[key]),'COMPACT_AND_RAW_PEAK_BINDING:'+role+':'+key)
        roles[role]=dict(identity=dict(identity),baseline={key:baseline[key] for key in METRICS},sampledPeak=peak,deltaAtSampledPeak={key:peak[key]-baseline[key] for key in METRICS})
    need(reader['scope']=='READ_ONLY_WIN32_PROCESS_METADATA' and reader['identityQueries']==3 and reader['borrowedIdentityQueries']==2 and reader['openedHandles']==reader['closedHandles'] and count(reader['lastThreadEntries'],16384),'ORIGINAL_READER_IDENTITY_AND_CLOSE_COUNTERS')
    need(reader['maximumOwnedHandlesObserved']==1 and reader['observerCreditHeld'] is reader['closeUnknown'] is False and reader['peaksAreSampled'] is True,'OBSERVER_UNKNOWN_OR_CREDIT_RETAINED')
    need(reader['mediaCalls']==reader['rpcCalls']==reader['newWorkers']==0,'OBSERVER_NO_MEDIA_RPC_WORKERS')
    need(reader['openedHandles']==1+sum(1+sum(row[column] is not None for column in (1,2,3)) for row in rows),'OBSERVER_EXACT_NATIVE_OPEN_CLOSE_BUDGET')
    memory=[]
    for label,value in (('launcher',decode(c['files']['execution/fresh-memory.json'])),('child',decode(c['files']['execution/child-memory.json'])),('originalSampler',runtime['freshMemory'])):
        need(value['status']=='MEMORY_READY' and value['stopAcceptance'] is False and value['reasons']==[] and value['minimumAvailablePhysicalBytes']==2147483648 and value['realExecutionApproved'] is False,'FRESH_MEMORY_ADMISSION:'+label)
        observation=value['observation'];need(count(observation['availablePhysicalBytes']) and observation['availablePhysicalBytes']>=2147483648 and observation['source']=='FRESH_READ_ONLY_GLOBAL_MEMORY_STATUS_EX','FRESH_MEMORY_FLOOR:'+label)
        need(finite(value['sampleDurationSeconds']) and value['sampleDurationSeconds']<=.1 and finite(observation['observedAtMonotonic']),'FRESH_MEMORY_QUERY_RETURN:'+label)
        memory.append(dict(stage=label,availablePhysicalBytes=observation['availablePhysicalBytes'],observedAtMonotonic=observation['observedAtMonotonic']))
    need(all(a['observedAtMonotonic']<=b['observedAtMonotonic'] for a,b in zip(memory,memory[1:])),'FRESH_MEMORY_ORDER_NOT_HISTORICAL_SNAPSHOT')
    c['facts']['runtime']=dict(roles=roles,samples=len(rows),compactSampleMilliseconds=times,compactGapsSeconds=gaps,maxObservedGapSeconds=obs['maxObservedGapSeconds'],lastSampleDurationSeconds=obs['sampleDurationSeconds'],freshMemory=memory,reader=reader,
        sampleDeadlineEvidence='Bound immutable observer has a permanent stop latch; final OBSERVED/no reasons/finished plus last duration and gap guards. Per-cycle raw duration values were not separately persisted.',
        memoryLogMeaning='ceilKiB numeric log cross-checked against original exact-byte baselines/peaks; never reconstructed as exact per-cycle byte readings',peaksAreSampled=True,continuousKernelPeakClaim=False)

def _closure_and_budgets(c):
    w=c['witness'];pre=c['preclose'];hub=w['callbackHub'];close=w['logClose'];states=c['states'];usage=w['usage'];limit=c['manifest']['limits']
    need(close==dict(closed=True,id='GC/n32',method='flush/fsync/close actually returned',exitedHelpers=close['exitedHelpers'],remainingResources=0),'GC_N32_ACTUAL_RETURN_REQUIRED')
    need(pre['logClose']=='PENDING_RETURN_CHANNEL','PRECLOSE_IS_NOT_FINAL_CLOSE_PROOF')
    need(hub==pre['callbackHub'] and hub['lifecycle']=='CLOSED' and hub['closed'] is True and hub['remainingCredits']==[] and hub['ownershipPending'] is False,'ORIGINAL_HUB_CLOSED')
    need(all(hub[key]==0 for key in ('active','cells','queued','monitorInFlight','workersAlive')) and hub['startupInProgress'] is False and hub['startupError'] is hub['cleanupError'] is hub['blocked'] is None,'HUB_OR_CALLBACK_OWNERSHIP_PENDING')
    need(set(hub['workers'])=={'notify','deadline'},'ORIGINAL_TWO_HUB_WORKERS')
    for worker in hub['workers'].values():
        need(all(worker[key] is True for key in ('creditReserved','creditReleased','reserveEntered','reserveReturned','threadCreated','startEntered','startReturned','entered','exited','joinEntered','joinReturned','joined')) and worker['releaseProof']=='THREAD_JOIN_PROVEN','WORKER_ACTUAL_RETURN_JOIN_PROOF')
        need(worker['state']=='CLOSED' and worker['alive'] is worker['unknown'] is worker['startInProgress'] is False and all(worker[key] is None for key in ('reserveError','startError','runtimeError','joinError','observationError')),'WORKER_UNKNOWN_OR_FAILURE')
        need(count(worker['entryIdent']) and worker['entryIdent']==worker['ident']==worker['nativeId'] and worker['threadId'],'WORKER_ORIGINAL_IDENTITY')
    need(len({worker['threadId'] for worker in hub['workers'].values()})==2,'WORKER_IDENTITY_ALIAS')
    cells=w['privateCells'];history=pre['cellHistory'];need(cells==pre['privateCells'] and cells['active']==cells['retained']==0 and cells['total']==cells['archived']==len(history)<=64 and 0<=cells['peak']<=8,'PRIVATE_CELL_HISTORY_OR_OWNERSHIP')
    need(hub['notices']==cells['total'] and hub['peakCells']<=8 and len({row['operation'] for row in history})==len(history),'PRIVATE_CELL_AUDIT_UNIQUENESS')
    for row in history:
        need(all(row[key] is True for key in ('native_done','gated','released','notification_done','notifier_quiescent','archived')) and row['retained'] is False,'CELL_ORIGINAL_DRAIN_REQUIRED')
        need(count(row['deliveries'],1) and count(row['callbacks_registered'],4) and row['callbacks_registered']==row['callbacks_finished'] and row['callback_errors']==[],'CELL_CALLBACK_DRAIN_OR_DELIVERY')
        state=states[row['binding']['task']];operation=state['ops'][row['operation']]
        need(operation['done'] is operation['nativeReturned'] is True,'SOURCE_OPERATION_NOT_RETURNED')
    proofs=close['exitedHelpers'];need(set(proofs)=={'J','R'} and proofs==w['runtimeObservation']['observation']['retired'],'EXACT_ORIGINAL_HELPER_EXIT_SET')
    for role,proof in proofs.items():
        actor=states['PF']['actors'][role];identity=IDENTITIES[role]
        need(proof['pid']==identity['pid'] and proof['instance']==identity['owner'] and proof['exited'] is True and proof['code']==0,'ORIGINAL_HELPER_EXIT_IDENTITY:'+role)
        need(proof==actor['exit'] and proof['started']==actor['started'] and count(proof['started']) and proof['observed']>=proof['started'],'ORIGINAL_HELPER_EXIT_TIME_BINDING:'+role)
    objects=0
    for state in states.values():
        for record in state['objects'].values():
            objects+=1;need(record['disposition'] in ('CLOSED_PROVEN','RELEASED_BY_OWNER_EXIT'),'NATIVE_OBJECT_OWNERSHIP_UNKNOWN')
            if record['actor'] in ('J','R'):need(record['owner']==IDENTITIES[record['actor']]['owner'],'MEDIA_OBJECT_ORIGINAL_OWNER')
            if record['disposition']=='RELEASED_BY_OWNER_EXIT':need(record['actor'] in proofs and record['exitProof']==proofs[record['actor']],'OWNER_EXIT_RELEASE_REQUIRES_ORIGINAL_PROOF')
    need(w.get('nativePending',[])==[] and w.get('logOwnershipPending',False) is False,'NATIVE_IO_OR_LOG_PENDING')
    need(w['ledgerPeaks']==pre['ledgerPeaks'] and all(count(w['ledgerPeaks'][key],maximum) for key,maximum in (('os',24),('media',6),('buffers',8))),'MANAGED_LEDGER_PEAK')
    need(w['metadataCommitStatus']==pre['metadataCommitStatus']=='HEALTHY' and w['metadataUnknownRequestedBytes']==pre['metadataUnknownRequestedBytes']==0,'METADATA_WRITE_OR_CLOSE_UNKNOWN')
    need(count(w['metadataRequested']) and w['metadataRequested']==w['metadataWritten']>=pre['metadataRequestedBeforeFinalReceipt']==pre['metadataWrittenBeforeFinalReceipt'],'MONOTONIC_METADATA_REQUEST_WRITE_COUNTER')
    need(count(w['metadataPeak'],3178496) and w['metadataPeak']>=pre['metadataPeakBeforeFinalReceipt'] and c['observedProductionMetadataBytes']<=w['metadataPeak'],'METADATA_STOCK_PEAK_NOT_CUMULATIVE_WRITES')
    need(usage==pre['usage'] and all(count(value) for value in usage.values()),'ORIGINAL_GLOBAL_USAGE_BINDING')
    mapping=dict(n='nonquery',ib='inputBytes',ic='inputCalls',v='validationBytes',targets='targets',records='records',credit='outputBytes')
    need(all(usage[key]<=limit[target] for key,target in mapping.items()) and usage['qn']+usage['qr']<=limit['query'] and usage['n']+usage['qn']+usage['qr']<=limit['control']<=limit['controlHard'],'GLOBAL_CONTROL_QUERY_IO_TARGET_RECORD_BUDGET')
    need(limit==dict(control=452,controlHard=544,nonquery=351,query=101,inputBytes=1573522,inputCalls=59,targets=10,records=32,outputBytes=655360,validationBytes=262144,filePeakBytes=3178496,fileHardBytes=4194304,metadataWriteBytes='separate-monotonic-counter',seconds=180,osHandles=24,mediaHandles=6,buffers64KiB=8),'ORIGINAL_BUDGET_NOT_RELAXED')
    need(usage['records']==32 and usage['targets']==10 and usage['credit']==655360,'ORIGINAL_FULL_ALLOCATION_COUNTS')
    c['facts']['closure']=dict(GCn32ActualReturn=True,GCn32DiskIntentAloneInsufficient=True,remainingResources=close['remainingResources'],helperExits=proofs,Hub=hub,privateCells=cells,nativeObjectsWithProvenClosure=objects,
        ioAndNativeDrainEvidence='The immutable Cleanup.finish checks pending native Futures, returns from original IO shutdown, then emits this actual GC/n32 flush/fsync/close return. No independent per-thread IO join receipt was serialized.',
        metadataCumulativeRequested=w['metadataRequested'],metadataCumulativeWritten=w['metadataWritten'],metadataStockPeak=w['metadataPeak'],ledgerPeaks=w['ledgerPeaks'],usage=usage)

def _wrapper_exit_and_independent(c):
    parent=c['launcher']['wrapperFacts'];child=c['driver']['wrapperFacts'];result=c['result']['wrapperFacts']
    for label,facts in (('parent',parent),('child',child),('resultCollector',result)):
        need(facts['gateReadByteCap']==268435456 and facts['gateFileReadCap']==8192 and count(facts['gateMetadataReadBytes'],268435456) and count(facts['gateMetadataFileReads'],8192) and facts['hashBlockBytes']==65536,'BOUNDED_WRAPPER_INTEGRITY_HASH:'+label)
        need(facts['identityHandlesOpened']==facts['identityHandlesClosed'] and count(facts['identityOwnedPeak'],1) and facts['identityRemaining']==0 and facts['identityCloseUnknown'] is False,'WRAPPER_IDENTITY_CLOSE_OR_UNKNOWN:'+label)
        need(facts['metadataRemaining']==[] and facts['metadataCreditRemaining']==0 and facts['metadataCloseUnknown'] is False and count(facts['metadataHandlePeak'],1),'WRAPPER_METADATA_OWNERSHIP_UNKNOWN:'+label)
        need(facts['parentSpawnCreditsRemaining']==0 and facts['parentProcessHandleCloseUnknown'] is False and facts['spawnError'] is None and facts['parentPipes']==facts['parentCollectorWorkers']==0,'WRAPPER_PROCESS_OR_THREAD_OWNERSHIP_UNKNOWN:'+label)
        need(facts['resultHashByteCap']==6291456 and count(facts['resultHashBytes'],6291456),'RESULT_HASH_READ_BUDGET:'+label)
        need(facts['spawnParentKernelHandlePeakCap']==6 and facts['spawnTemporaryDevnullHandleCap']==4 and facts['spawnTemporaryPrimaryThreadHandleCap']==1,'STATIC_SPAWN_HANDLE_CAPS_NOT_OS_PEAKS')
    need(parent['spawnCalls']==result['spawnCalls']==1 and child['spawnCalls']==0 and parent['parentProcessHandleCloseProven'] is result['parentProcessHandleCloseProven'] is True,'ORIGINAL_PARENT_HANDLE_ACTUALLY_CLOSED')
    need(parent['launchPublicationCalls']==result['launchPublicationCalls']==1 and child['launchPublicationCalls']==0,'ONE_ORIGINAL_LAUNCH_PUBLICATION')
    need(result['gateMetadataReadBytes']==parent['gateMetadataReadBytes'] and result['gateMetadataFileReads']==parent['gateMetadataFileReads'],'COLLECTOR_SAME_ORIGINAL_PARENT')
    expected_hash_bytes=sum(len(raw) for name,raw in c['files'].items() if name!='execution/result-manifest.json')
    need(result['resultHashBytes']==expected_hash_bytes,'RESULT_HASH_COUNTER_EXACT_BYTES')
    audit=c['bundle']['testerAudit']
    need(audit['batchStatus']=='FAIL' and audit['rawBatchFailurePreserved'] is True and audit['actualAttempts']==1 and audit['fullBatchPasses']==0 and audit['assertions']==160,'INDEPENDENT_ORIGINAL_FAILURE_CORROBORATION')
    need(audit['resultManifestSha256']==RESULT_SHA and audit['precloseSha256']==PRECLOSE_SHA and audit['originalG']==G_PROCESS and audit['originalLauncher']==LAUNCHER and audit['originalGExitCode']==2,'INDEPENDENT_IDENTITY_AND_HASH_CORROBORATION')
    need(audit['noInFlight'] is True and audit['GCn32ReturnProven'] is True and audit['helpers']==c['witness']['logClose']['exitedHelpers'],'INDEPENDENT_CLOSE_CORROBORATION')
    need(audit['outputUsage']==c['observedOutputUsage'] and audit['combinedUsage']==c['observedCombinedUsage'],'INDEPENDENT_OUTPUT_BYTE_CORROBORATION')
    expected_outputs={}
    for index in range(1,11):
        name='T'+str(index).zfill(2)+'.out'
        expected=bytes(range(32)) if index in (1,5) else b'Z\0xy\0\0\0abc' if index==2 else b'\0' if index in (3,4) else b''
        expected_outputs[name]=dict(name=name,bytes=len(expected),sha256=sha(expected))
    need(len(audit['independentOutputs'])==10 and {row['name'] for row in audit['independentOutputs']}==set(expected_outputs),'INDEPENDENT_OUTPUT_SET_CORROBORATION')
    for row in audit['independentOutputs']:
        expected=expected_outputs[row['name']];need(row['bytes']==expected['bytes'] and row['sha256']==expected['sha256'] and row['matchesIndependentExpectedBytes'] is True,'INDEPENDENT_OUTPUT_HASH_CORROBORATION')
    c['facts']['wrapper']=dict(parent=parent,child=child,resultCollector=result,originalGExitCode=2,originalCallerExitCode=1,parentHandleCloseProven=True,noInFlight=True,resultHashBytes=expected_hash_bytes,spawnHandleMeaning='Static cap 6, not a measured OS handle peak')

def evaluate_resources(bundle):
    """Evaluate only supplied dicts/bytes. Never reads, writes, starts or probes."""
    context=dict(bundle=bundle,facts={});reasons=[];completed=[]
    phases=(('input',_load),('originalBinding',_original_binding),('identity',_identities),('outputs',_outputs),('snapshots',_snapshots),('globalLog',_global_log),('runtime',_metrics),('closureAndBudgets',_closure_and_budgets),('wrapperExitAndIndependent',_wrapper_exit_and_independent))
    for label,action in phases:
        try:action(context);completed.append(label)
        except EvidenceError as error:reasons.append(str(error))
        except Exception as error:reasons.append('MISSING_OR_INVALID_'+label.upper()+':'+type(error).__name__)
    facts=context['facts'];facts['completedEvidenceSections']=completed;facts['allRequiredSections']=len(completed)==len(phases)
    facts['limitations']=['Discrete sampled metrics are not continuous kernel peaks.',
        'Per-cycle raw sample durations were not persisted; no per-cycle timing values are reconstructed. Final immutable stop-latch/finished/duration/gap evidence is required.',
        'IO/native shutdown has no separate serialized join boolean; actual GC/n32 return is accepted only with the immutable production control flow, complete source integrity, original owner exit and all closure facts.',
        'The original E2E FAIL, exit codes, consumed reservation and 160 original assertions remain unchanged; no new actual attempt or product admission follows.']
    return dict(scope=SCOPE,accepted=not reasons,reasons=list(dict.fromkeys(reasons)),facts=facts,originalResult=dict(ORIGINAL_RESULT),newActualAttempts=0)
