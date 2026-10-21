"""Read-only E2 configuration admission. This package has no real-run capability."""
import argparse,copy,json,re
from pathlib import Path, PureWindowsPath

BASE=Path(__file__).resolve().parents[1]
LENGTHS={'L':3212959911,'C':4096,'Z':0}
HASHES={'L':'28af909ce8d9f9e1431253715e07bbfa9024aa8963882a000ee7a15807622b26',
        'C':'c0d66c6510904af0301dc1d923a403a1983f446e5a326299074f1b6a88a75405',
        'Z':'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'}
NAMES={'L':'03_large_files/large_video_over_2GiB.mkv','C':'04_corrupted_files/corrupted_video.mp4','Z':'04_corrupted_files/empty_video.mkv'}
WINDOWS=[2147418112,2147450880,2147483648,3212894375]
BUDGET_FIELDS=('task','nonquery','queriesNew','queriesReplay','inputBytes','inputCalls','validationBytes','newTargets','newRecords','outputBytes','mediaHandles','buffers','seconds')
HARD={'control':452,'controlHard':544,'nonquery':351,'query':101,'inputBytes':1573522,'inputCalls':59,'targets':10,'records':32,'outputBytes':655360,'validationBytes':262144,'filePeakBytes':3178496,'fileHardBytes':4194304,'seconds':180,'osHandles':24,'mediaHandles':6,'buffers64KiB':8}

def load_bundle(base=None):
    root=Path(base) if base is not None else BASE
    # Only these four package configuration files are opened. Input paths are data.
    result={}
    for key,name in (('inputs','inputs.json'),('cases','cases.json'),('machine','machine.json'),('runtime','runtime-policy.json')):
        raw=(root/'profiles'/name).read_bytes()
        if len(raw)>1048576:raise ValueError('CONFIGURATION_FILE_LIMIT')
        result[key]=json.loads(raw.decode('utf-8-sig'))
    return result

def validate_profile(bundle,manifest):
    errors=[]
    def require(condition,reason):
        if not condition:errors.append(reason)
    try:
        inputs=bundle['inputs'];cases=bundle['cases'];runtime=bundle['runtime']
        require(inputs.get('executionAuthorized') is False and cases.get('executionEnabled') is False,'REAL_EXECUTION_FLAG_MUST_BE_FALSE')
        require(cases['boundaryBytes']==2147483648,'REAL_BOUNDARY_MISMATCH')
        launch=cases['launchContract']
        require(launch['executionAuthorized'] is False and launch['defaultBatchId'] is None and launch['outputRootDefault'] is None,'EXECUTION_BATCH_MUST_BE_UNASSIGNED')
        require(launch['outputRootTemplate']=='D:/CodexProjects/VideoKit/docs/coder/d1e2/runs/{approvedBatchId}-{uniqueNonce}','OUTPUT_NAMESPACE_MISMATCH')
        require(set(inputs['inputs'])==set(LENGTHS),'INPUT_ALIAS_MISMATCH')
        for alias,length in LENGTHS.items():
            item=inputs['inputs'][alias];historical=item['historical'];stat=item['currentStat']
            expected=PureWindowsPath('D:/CodexProjects/VideoKit/test_media')/PureWindowsPath(NAMES[alias])
            require(PureWindowsPath(item['path'])==expected,'INPUT_PATH_MISMATCH:'+alias)
            require(type(historical['bytes']) is int and historical['bytes']==length,'INPUT_LENGTH_MISMATCH:'+alias)
            require(historical['sha256']==HASHES[alias],'HISTORICAL_HASH_MISMATCH:'+alias)
            require(item.get('currentContentVerified') is False,'CURRENT_CONTENT_CLAIM_UNSUPPORTED:'+alias)
            require(stat.get('exists') is True and type(stat.get('bytes')) is int and stat['bytes']==length,'INPUT_STAT_MISMATCH:'+alias)
            require(stat.get('reparsePoint') is False and stat.get('isDirectory') is False,'INPUT_ITEM_REPARSE_OR_DIRECTORY:'+alias)
            declared=cases['inputs'][alias]
            require(declared['lengthBytes']==length and declared['historicalSha256']==HASHES[alias] and PureWindowsPath(declared['absolutePath'])==expected,'CASE_INPUT_BINDING_MISMATCH:'+alias)
        windows=inputs['largeFileWindows']['windows']
        require([(item['offset'],item['requestedBytes']) for item in windows]==[(offset,65536) for offset in WINDOWS],'REAL_WINDOWS_MISMATCH')
        require(len(cases['cases'])==len(manifest['branches'])==61,'BRANCH_COUNT_MISMATCH')
        require([row['id'] for row in cases['cases']]==[row['id'] for row in manifest['branches']],'BRANCH_ID_ORDER_MISMATCH')
        originals={row['id']:row for row in manifest['branches']}
        total=dict(inputBytes=0,inputCalls=0,validationBytes=0)
        def usage(windows):
            result=dict(inputBytes=0,inputCalls=0,validationBytes=0)
            for window in windows:
                requested=window['requestedBytes'];offset=window['offsetBytes']
                require(type(requested) is int and 0<=requested<=65536 and type(offset) is int and 0<=offset<2**63-requested,'WINDOW_RANGE_INVALID')
                require(type(window.get('delegateCalls')) is int and window['delegateCalls'] in (0,1),'WINDOW_DELEGATE_COUNT_INVALID')
                require(type(window.get('inputRequestCharged')) is bool,'WINDOW_CHARGE_FLAG_INVALID')
                if window.get('inputRequestCharged') is False:
                    require(requested==0 and window.get('delegateCalls')==0,'UNCHARGED_WINDOW_HAS_IO')
                if window.get('inputRequestCharged') is True:
                    if window['budgetClass']=='INPUT':result['inputBytes']+=requested;result['inputCalls']+=1
                    elif window['budgetClass']=='VALIDATION':result['validationBytes']+=requested
                    else:require(False,'WINDOW_BUDGET_CLASS_INVALID')
            return result
        pf_usage=usage(cases['phaseProfiles']['PF']['windows'])
        require(pf_usage==dict(inputBytes=32,inputCalls=2,validationBytes=0),'PF_REQUEST_USAGE_MISMATCH')
        total.update(pf_usage)
        for row in cases['cases']:
            original=originals.get(row['id'])
            require(original is not None,'UNKNOWN_BRANCH:'+row['id'])
            if original is None:continue
            for key in BUDGET_FIELDS:
                require(row[key]==original[key] and (type(row[key]) is int if key!='task' else isinstance(row[key],str)),'ROW_ALLOCATION_MISMATCH:'+row['id']+':'+key)
            require([op['token'] for op in row['operations']]==[op['token'] for op in original['operations']],'ROW_OPERATION_MISMATCH:'+row['id'])
            declared_io=row['realIO'];actual=usage(declared_io['windows'])
            require(actual==declared_io['expectedRequestUsage'],'ROW_REQUEST_USAGE_MISMATCH:'+row['id'])
            require(all(actual[key]<=row[key] for key in actual),'ROW_REQUEST_ALLOCATION_EXCEEDED:'+row['id'])
            require(declared_io['boundaryBytes']==2147483648,'CASE_BOUNDARY_MISMATCH:'+row['id'])
            for key,value in actual.items():total[key]+=value
            durability=row['requiredDurability'];level=durability['level']
            require(level in ('NONE','OS_DATA_SYNC_ACK','NAMESPACE_DURABLE'),'DURABILITY_LEVEL_INVALID:'+row['id'])
            require(durability.get('productReady') is False and durability.get('businessCommit') is False and durability.get('powerLossClaim') is False,'PRODUCT_DURABILITY_SCOPE_INVALID:'+row['id'])
            require(not durability.get('namespaceRequired') or level=='NAMESPACE_DURABLE','DURABILITY_DOWNGRADE:'+row['id'])
            if row['id'] in ('P01-N1','P01-N2','P01-N3','P01-N4','P01-S1','P01-S2','P01-S3','P01-S4'):
                offset=WINDOWS[int(row['id'][-1])-1]
                require(any(window['offsetBytes']==offset for window in row['realIO']['windows']),'CASE_WINDOW_MISMATCH:'+row['id'])
        for key,value in HARD.items():
            require(type(cases['limits'][key]) is int and cases['limits'][key]==value and manifest['limits'][key]==value,'GLOBAL_ALLOCATION_MISMATCH:'+key)
        expected_usage=dict(inputBytes=1573492,inputCalls=59,validationBytes=128)
        require(cases['plannedRequestUsage']==total==expected_usage,'PLANNED_REQUEST_USAGE_MISMATCH')
        require(runtime['state']=='PROPOSED' and runtime['executionAuthorized'] is False,'RUNTIME_POLICY_UNAPPROVED_STATE_CHANGED')
        require(runtime['managedLimits']=={'osResources':24,'mediaHandles':6,'buffers64KiB':8},'MANAGED_LIMITS_MISMATCH')
        require(runtime['intervalSeconds']==1 and runtime['maxSamples']==201 and runtime['maxRecordBytes']==128 and runtime['maxLogBytes']==26752,'OBSERVER_BUDGET_MISMATCH')
        require(set(runtime['limits'])=={'G','J','R'},'RUNTIME_ROLE_MISMATCH')
    except (KeyError,TypeError,ValueError,IndexError) as error:
        errors.append('CONFIGURATION_SCHEMA_ERROR:'+type(error).__name__)
    return dict(valid=not errors,errors=errors)

def inspect_admission(bundle,manifest,approval=None,stat_metadata=None,runtime_policy=None):
    # Approval-like dictionaries and cached stat never mint execution authority.
    checked=copy.deepcopy(bundle)
    if runtime_policy is not None:checked['runtime']=runtime_policy
    diagnostic=validate_profile(checked,manifest)
    blockers=['REAL_EXECUTION_NOT_AUTHORIZED','INDEPENDENT_ADMISSION_REVIEW_REQUIRED','RUNTIME_THRESHOLDS_UNAPPROVED',
              'BLOCKED_VERSION_NOT_PROVEN','REAL_ADAPTER_BINDING_REQUIRED','OBSERVER_LOG_CREDIT_APPROVAL_REQUIRED']
    if not diagnostic['valid']:blockers.append('CONFIGURATION_INVALID')
    case_admissions=[]
    for row in checked.get('cases',{}).get('cases',[]):
        requirement=row.get('requiredDurability',{});level=requirement.get('level')
        namespace=level=='NAMESPACE_DURABLE' or requirement.get('namespaceRequired') is True
        case_admissions.append(dict(id=row.get('id'),status='NOT_RUN_DURABILITY_UNPROVEN' if namespace else 'PREPARED_CONDITIONAL_IO_PROBE',requiredDurability=level,
                                    productVariant=row.get('productVariant',{}).get('admission')))
    return dict(scope='E2_CONFIGURATION_ADMISSION_ONLY',status='PREPARED_PENDING_ADMISSION_REVIEW' if diagnostic['valid'] else 'CONFIGURATION_INVALID',
                configurationValid=diagnostic['valid'],errors=diagnostic['errors'],executionAllowed=False,blockers=blockers,
                approvalConsumed=False,cachedStatIsVersionProof=False,currentContentHashProven=False,caseAdmissions=case_admissions,
                requiredNextDecisions=['Approve a distinct execution batch and unused output root bound to frozen hashes.',
                'Review requiredDurability case scope without changing product P0.',
                'Choose and review the opened-Java-FD identity and exact input/output namespace adapters.',
                'Approve runtime proposals and combined observer/event-log reservation before real PF.'],
                mediaBytesRead=0,helpersStarted=0,realPFRun=False,real61Run=False)

def request_real_run(batch_id,bundle,manifest,*,media_reader=None,helper_launcher=None):
    report=inspect_admission(bundle,manifest)
    # Deliberately no callback invocation, path stat, mkdir, Engine or helper import.
    return 2,dict(scope='E2_REAL_REQUEST_REJECTED',status='NOT_RUN_AUTHORIZATION_REQUIRED',batchId=str(batch_id)[:64],
                  executionAllowed=False,configurationValid=report['configurationValid'],blockers=report['blockers'],
                  outputRootCreated=False,mediaBytesRead=0,helpersStarted=0,realPFRun=False,real61Run=False)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--inspect',action='store_true');parser.add_argument('--request-real',metavar='BATCH_ID');options=parser.parse_args()
    bundle=load_bundle();manifest=json.loads((BASE/'manifest/branches.json').read_text(encoding='utf-8-sig'))
    if options.request_real is not None:code,report=request_real_run(options.request_real,bundle,manifest)
    else:
        report=inspect_admission(bundle,manifest);code=0 if report['configurationValid'] else 2
    print(json.dumps(report,separators=(',',':')));return code

if __name__=='__main__':raise SystemExit(main())
