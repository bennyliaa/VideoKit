"""Read-only E3 package checks. Never imports a runner or touches media paths."""
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath, PureWindowsPath
import stat
import zipfile

BASE=Path(__file__).resolve().parents[1]
ROOT=BASE.parents[2]
PREFIX='docs/coder/d1e3/'
SOURCE_FOLDERS=('src','tools','manifest','profiles','upstream-e2f')
SEAL=BASE/'evidence/e3-freeze.json'
STATE='PREPARED_PENDING_COORDINATOR_HANDOFF'
BYTE_CAP=268435456
FILE_CAP=8192
E2F_SOURCE_SHA='a7c09e34a5ccf6a3c980299a6fb0484792ca6496bc52b3bc08f73160ed72c4a5'
E2F_SOURCE_BYTES=50759794
E2F_SOURCE_MANIFEST_SHA='774decde0e33b75b8ee0ee2c61d12f21a9ec4241121cce335054260072749ef4'
E2F_FREEZE_SHA='1a73391a12f9473f661a5e62204218d5a875031f064bb12af262529c4e866dee'
BUDGET_FIELDS=('task','nonquery','queriesNew','queriesReplay','inputBytes','inputCalls','validationBytes','newTargets','newRecords','outputBytes','mediaHandles','buffers','seconds')
LENGTHS={'L':3212959911,'C':4096,'Z':0}
INPUTS={'L':'03_large_files/large_video_over_2GiB.mkv','C':'04_corrupted_files/corrupted_video.mp4','Z':'04_corrupted_files/empty_video.mkv'}
DOC_NAMES=('DELIVERY','REAL_IO_EXECUTION_PLAN','EXECUTION_APPENDIX')


def require(value,reason):
    if not value:raise AssertionError(reason)


def present(path):return os.path.lexists(path)


def safe(path):
    """Only package files and documentation, with no reparse traversal."""
    path=Path(os.path.abspath(path))
    docs=ROOT/'docs'
    require(path.is_relative_to(docs),'DOCUMENT_OR_PACKAGE_PATH_REQUIRED')
    for item in (path,*path.parents):
        value=os.lstat(item)
        require(not stat.S_ISLNK(value.st_mode) and not getattr(value,'st_file_attributes',0)&0x400,'REPARSE_PACKAGE_PATH_DENIED')
        if item!=path:require(stat.S_ISDIR(value.st_mode),'PACKAGE_ANCESTOR_NOT_DIRECTORY')
    return path


def relative(path):return safe(path).relative_to(ROOT).as_posix()


def package_path(name):
    require(isinstance(name,str) and name.startswith(PREFIX) and '\\' not in name and
            all(part not in ('','.','..') for part in name.split('/')),'PACKAGE_RECORD_PATH')
    return safe(ROOT/name)


class ReadBudget:
    """Charges actual file bytes AND decoded ZIP bytes, including repeated IO.

    Cached fingerprints do not cause another read. Large archive bytes are not
    cached: call archive verification before the general fingerprint pass.
    """
    def __init__(self,byte_cap=BYTE_CAP,file_cap=FILE_CAP):
        self.physicalBytes=0;self.logicalBytes=0;self.compressedPhysicalBytes=0;self.files=0;self.zipEntries=0
        self.cache={};self.small={};self.memo={};self.byte_cap=byte_cap;self.file_cap=file_cap

    def charge(self,n,logical=False):
        require(type(n) is int and n>=0,'READ_COST_INVALID')
        require(self.physicalBytes+self.logicalBytes+n<=self.byte_cap,'SOURCE_READ_BYTE_CAP')
        if logical:self.logicalBytes+=n
        else:self.physicalBytes+=n

    def event(self,logical=False):
        require(self.files+self.zipEntries<self.file_cap,'SOURCE_READ_FILE_CAP')
        if logical:self.zipEntries+=1
        else:self.files+=1

    @staticmethod
    def stamp(path):
        value=os.lstat(safe(path));require(stat.S_ISREG(value.st_mode),'REGULAR_PACKAGE_FILE_REQUIRED')
        return (value.st_dev,value.st_ino,value.st_size,value.st_mtime_ns)

    def read(self,path):
        path=safe(path);key=str(path);before=self.stamp(path)
        if key in self.small:
            require(self.cache[key][0]==before,'FILE_CHANGED_DURING_VERIFICATION')
            return self.small[key]
        require(before[2]<=self.byte_cap-self.physicalBytes-self.logicalBytes,'SOURCE_READ_BYTE_CAP')
        self.event();parts=[];size=0;digest=hashlib.sha256()
        with path.open('rb',buffering=0) as stream:
            while size<before[2]:
                block=stream.read(min(65536,before[2]-size))
                require(bool(block),'SOURCE_SHORT_READ')
                self.charge(len(block));parts.append(block);size+=len(block);digest.update(block)
                if path.suffix.lower()=='.zip':self.compressedPhysicalBytes+=len(block)
        require(before==self.stamp(path) and size==before[2],'FILE_CHANGED_DURING_VERIFICATION')
        value=b''.join(parts);self.cache[key]=(before,dict(bytes=size,sha256=digest.hexdigest()))
        if size<=2097152:self.small[key]=value
        return value

    def fingerprint(self,path):
        path=safe(path);key=str(path)
        if key not in self.cache:self.read(path)
        require(self.cache[key][0]==self.stamp(path),'FILE_CHANGED_DURING_VERIFICATION')
        return dict(self.cache[key][1])

    def record(self,path):return dict(path=relative(path),**self.fingerprint(path))
    def json(self,path):return json.loads(self.read(path).decode('utf-8-sig'))
    def facts(self):
        return dict(physicalFileBytes=self.physicalBytes,zipCompressedPhysicalBytes=self.compressedPhysicalBytes,zipLogicalBytes=self.logicalBytes,
                    totalBytes=self.physicalBytes+self.logicalBytes,physicalFileReads=self.files,
                    zipEntryReads=self.zipEntries,totalFileReads=self.files+self.zipEntries,
                    byteCap=self.byte_cap,fileCap=self.file_cap,compressedBytesAndLogicalBytesBothCharged=True,
                    nestedArchivesRecursivelyReopened=False,mediaBytesRead=0,mediaStatCalls=0)


def files_under(folder):
    folder=safe(BASE/folder);result=[];directories=0
    for current,dirs,files in os.walk(folder,followlinks=False):
        safe(current);directories+=1;require(directories<=1024,'PACKAGE_DIRECTORY_CAP')
        dirs[:]=sorted(name for name in dirs if name!='__pycache__')
        for name in dirs:safe(Path(current)/name)
        for name in sorted(files):
            path=safe(Path(current)/name)
            require(stat.S_ISREG(os.lstat(path).st_mode),'PACKAGE_NONREGULAR_FILE')
            result.append(path);require(len(result)<=FILE_CAP,'PACKAGE_FILE_CAP')
    return sorted(result)


def source_paths():return sorted(path for name in SOURCE_FOLDERS for path in files_under(name))
def document_paths():return [ROOT/'docs/coder'/('D1_E3_'+name+'_V1.0.md') for name in DOC_NAMES]
def runtime_paths():
    result=[path for name in ('src','tools','manifest','profiles') for path in files_under(name)]
    result.append(safe(BASE/'artifacts/E3.dll'))
    classes=files_under('artifacts/java-e3')
    require(classes and all(path.suffix=='.class' and path.is_relative_to(BASE/'artifacts/java-e3/videokit/e1') for path in classes),'E3_JAVA_ARTIFACT_SET')
    require(any(path.name=='JavaHelper.class' for path in classes) and any(path.name=='JavaBridgeProbe.class' for path in classes),'E3_JAVA_TOPLEVEL_MISSING')
    return sorted(result+classes)


def verify_archive(path,records,budget,capture=(),expected=None):
    """Hash the raw archive once, then every declared logical member once."""
    names=[row['path'] for row in records]
    require(len(names)==len(set(names)) and len(names)<=FILE_CAP,'SOURCE_ARCHIVE_DUPLICATE_OR_COUNT')
    for name in names:
        require(isinstance(name,str) and '\\' not in name and not PurePosixPath(name).is_absolute() and
                all(part not in ('','.','..') for part in name.split('/')),'SOURCE_ARCHIVE_MEMBER_PATH')
    raw=budget.read(path);captured={}
    if expected is not None:require(budget.fingerprint(path)==expected,'SOURCE_ARCHIVE_RAW_ANCHOR')
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        entries=archive.infolist();require(len(entries)==len(names) and {item.filename for item in entries}==set(names),'SOURCE_ARCHIVE_EXACT_INVENTORY')
        require(len({item.filename for item in entries})==len(entries),'SOURCE_ARCHIVE_DUPLICATE_MEMBER')
        for row in records:
            item=archive.getinfo(row['path']);require(not item.is_dir() and item.file_size==row['bytes'] and not item.flag_bits&1,'SOURCE_ARCHIVE_LENGTH_OR_ENCRYPTION')
            require(item.file_size<=budget.byte_cap-budget.physicalBytes-budget.logicalBytes,'SOURCE_READ_BYTE_CAP')
            budget.event(True);digest=hashlib.sha256();size=0;parts=[]
            with archive.open(item,'r') as stream:
                while size<item.file_size:
                    block=stream.read(min(65536,item.file_size-size))
                    require(bool(block),'SOURCE_ARCHIVE_SHORT_MEMBER')
                    budget.charge(len(block),True);digest.update(block);size+=len(block)
                    if row['path'] in capture:
                        require(size<=2097152,'CAPTURED_SOURCE_JSON_CAP');parts.append(block)
            require(size==row['bytes'] and digest.hexdigest()==row['sha256'],'SOURCE_ARCHIVE_MEMBER_HASH:'+row['path'])
            if row['path'] in capture:captured[row['path']]=b''.join(parts)
    return captured


def verify_upstreams(budget=None):
    budget=budget or ReadBudget()
    if 'upstream' in budget.memo:return budget.memo['upstream']
    folder=BASE/'upstream-e2f'
    require({path.name for path in files_under('upstream-e2f')}=={'freeze-summary.json','source-manifest.json','E2F-source.zip'},'ONE_COMPLETE_UPSTREAM_ONLY')
    frozen=budget.json(folder/'freeze-summary.json');source=budget.json(folder/'source-manifest.json')
    require(budget.fingerprint(folder/'freeze-summary.json')['sha256']==E2F_FREEZE_SHA,'UPSTREAM_E2F_FREEZE_ANCHOR')
    require(frozen['schema']==1 and frozen['state']=='E2F_FROZEN_PENDING_INDEPENDENT_REVIEW' and frozen['noInFlight'] is True,'UPSTREAM_E2F_STATE')
    require(budget.fingerprint(folder/'source-manifest.json')['sha256']==E2F_SOURCE_MANIFEST_SHA,'UPSTREAM_SOURCE_MANIFEST_ANCHOR')
    require(frozen['sourceZip']==dict(bytes=E2F_SOURCE_BYTES,path='docs/coder/d1e2f/artifacts/E2F-source.zip',sha256=E2F_SOURCE_SHA),'UPSTREAM_SOURCE_ZIP_DECLARATION')
    wanted=['docs/coder/d1e2f/manifest/branches.json','docs/coder/d1e2f/profiles/runtime-policy.json','docs/coder/d1e2f/profiles/inputs.json']
    captured=verify_archive(folder/'E2F-source.zip',source['files'],budget,wanted,dict(bytes=E2F_SOURCE_BYTES,sha256=E2F_SOURCE_SHA))
    require(budget.fingerprint(folder/'E2F-source.zip')==dict(bytes=E2F_SOURCE_BYTES,sha256=E2F_SOURCE_SHA),'UPSTREAM_SOURCE_ZIP_ANCHOR')
    require(len(source['files'])==frozen['sourceFiles']==79,'UPSTREAM_E2F_SOURCE_COUNT')
    old_manifest=json.loads(captured[wanted[0]].decode('utf-8-sig'))
    old_policy=json.loads(captured[wanted[1]].decode('utf-8-sig'))
    require(frozen['originalResult']['driverStatus']==frozen['originalResult']['launcherStatus']=='FAIL' and frozen['originalResult']['originalGExitCode']==2 and frozen['originalResult']['assertions']==160,'HISTORICAL_FAIL_MUST_REMAIN')
    baseline=[];old_prefix='docs/coder/d1e2f/'
    for row in frozen['files']:
        name=row['path'][len(old_prefix):] if row['path'].startswith(old_prefix) else ''
        if name=='artifacts/E2C.dll' or name.startswith('artifacts/java/'):
            require(budget.fingerprint(BASE/name)==dict(bytes=row['bytes'],sha256=row['sha256']),'BASELINE_ARTIFACT_CHANGED:'+name)
            baseline.append(budget.record(BASE/name))
    require(len(baseline)==10,'BASELINE_ARTIFACT_COUNT')
    result=dict(upstreamFreezeSha256=budget.fingerprint(folder/'freeze-summary.json')['sha256'],upstreamSourceZipSha256=E2F_SOURCE_SHA,
                upstreamSourceFiles=79,upstreamFrozenRecords=len(frozen['files']),oldOfflineAssertions=frozen['offlineAssertions'],
                originalResult=frozen['originalResult'],historicalAssertionsIncluded=False,baselineArtifacts=baseline,
                completeDependencyContainer='upstream-e2f/E2F-source.zip',nestedDependenciesVerifiedAsOpaqueFrozenMembers=True)
    budget.memo['oldManifest']=old_manifest;budget.memo['oldPolicy']=old_policy;budget.memo['oldInputs']=json.loads(captured[wanted[2]].decode('utf-8-sig'));budget.memo['upstream']=result
    return result


def verify_configuration(manifest,budget=None):
    budget=budget or ReadBudget();verify_upstreams(budget)
    old=budget.memo['oldManifest'];policy=budget.json(BASE/'profiles/runtime-policy.json')
    require(manifest['schema']==3 and manifest['experimentEnabled'] is manifest['realExecutionEnabled'] is False,'MANIFEST_IS_CONFIGURATION_ONLY')
    require(manifest['limits']==old['limits'] and manifest['executionOrder']==old['executionOrder'] and manifest['callbackBudget']==old['callbackBudget'],'ORIGINAL_LIMIT_ORDER_OR_CALLBACK_CHANGED')
    require(len(manifest['branches'])==len(old['branches'])==61,'EXACT_61_BRANCHES')
    for current,previous in zip(manifest['branches'],old['branches']):
        require(current['id']==previous['id'] and all(current[key]==previous[key] for key in BUDGET_FIELDS),'BRANCH_ALLOCATION_CHANGED:'+current['id'])
        require([(op['requestId'],op['token'],op.get('concurrentGroup')) for op in current['operations']]==[(op['requestId'],op['token'],op.get('concurrentGroup')) for op in previous['operations']],'BRANCH_CONTROL_SEQUENCE_CHANGED')
    old_policy_row=next(row for row in budget.json(BASE/'upstream-e2f/source-manifest.json')['files'] if row['path']=='docs/coder/d1e2f/profiles/runtime-policy.json')
    require(budget.fingerprint(BASE/'profiles/runtime-policy.json')==dict(bytes=old_policy_row['bytes'],sha256=old_policy_row['sha256']),'RUNTIME_POLICY_NOT_BYTE_IDENTICAL')
    require(policy==budget.memo['oldPolicy'] and policy['state']=='APPROVED_TOOL_STRATEGY' and policy['executionAuthorized'] is False,'RUNTIME_POLICY_STATE')
    inputs=budget.json(BASE/'profiles/inputs.json');cases=budget.json(BASE/'profiles/cases.json')
    require(inputs['sourceDocuments']==budget.memo['oldInputs']['sourceDocuments'],'HISTORICAL_DOCUMENT_BINDINGS_CHANGED')
    require(inputs['executionAuthorized'] is cases['executionEnabled'] is False and cases['limits']==manifest['limits'] and len(cases['cases'])==61,'PROFILE_EXECUTION_REMAINS_CLOSED')
    require(set(inputs['inputs'])==set(cases['inputs'])==set(LENGTHS),'EXACT_INPUT_ALIASES')
    for alias,length in LENGTHS.items():
        declared=inputs['inputs'][alias];case=cases['inputs'][alias]
        expected=PureWindowsPath(str(ROOT/'test_media'/INPUTS[alias])).as_posix().casefold()
        require(PureWindowsPath(declared['path']).as_posix().casefold()==expected==PureWindowsPath(case['absolutePath']).as_posix().casefold(),'DECLARED_INPUT_PATH:'+alias)
        require(declared['historical']['bytes']==case['lengthBytes']==length and declared['historical']['sha256']==case['historicalSha256'],'DECLARED_INPUT_GEOMETRY:'+alias)
        require(declared['currentContentVerified'] is case['historicalHashRecomputed'] is False and declared['currentVersionGuarantee']=='UNPROVEN','HISTORICAL_METADATA_NOT_CURRENT_PROOF')
    require([row['offset'] for row in inputs['largeFileWindows']['windows']]==[2147418112,2147450880,2147483648,3212894375] and all(row['requestedBytes']==65536 for row in inputs['largeFileWindows']['windows']),'EXACT_REAL_WINDOWS')
    by_id={row['id']:row for row in cases['cases']}
    for row in manifest['branches']:
        case=by_id[row['id']];require(all(case[key]==row[key] for key in BUDGET_FIELDS),'CASE_BUDGET_CHANGED')
        required=case['requiredDurability'];require(required['productReady'] is required['businessCommit'] is required['powerLossClaim'] is False,'NO_PRODUCT_READY_CLAIM')
    for name in ('Q01-SEQ','Q05-STREAM','Q06-LOST','Q08-READY','Q07-READYFIRST'):
        require(by_id[name]['productVariant']['admission']=='NOT_RUN_DURABILITY_UNPROVEN','PRODUCT_VARIANT_REMAINS_NOT_RUN')
    require(all(inputs['activity'][key]==0 for key in ('mediaStatCalls','mediaBytesRead','mediaHashesComputed','helperProcessesStarted')),'PREPARATION_MEDIA_ACTIVITY')
    return dict(configurationVerified=True,cases=61,declaredLengths=LENGTHS,boundaryBytes=2147483648,runtimePolicyByteIdentical=True,
                runtimePolicy='APPROVED_TOOL_STRATEGY',mediaStatCalls=0,mediaBytesRead=0,currentOpenedVersionProof=False,
                eventLogCap=104320,metricLogCap=26752,realExecutionEnabled=False)


def verify_batch(budget=None):
    budget=budget or ReadBudget();batch=budget.json(BASE/'manifest/e3-batch.json')
    require(batch['schema']==1 and batch['state']==STATE and batch['profile']=='REAL_IO' and batch['observerMode']=='ACTUAL_OS_OBSERVER','BATCH_PREPARED_REAL_IO_STATE')
    require(batch['executionAuthorized'] is batch['mockAllowed'] is False and batch['externalGrantRequired'] is True,'COORDINATOR_HANDOFF_REQUIRED')
    require(batch['maximumG']==batch['maximumFullAttempts']==1 and batch['machineName']=='LZF' and batch['executionDirectory']=='execution' and batch['outputParent']=='runs','ONCE_BATCH_CONTRACT')
    require(PureWindowsPath(batch['packageRoot'])==PureWindowsPath(str(BASE)) and batch['sealFile']=='evidence/e3-freeze.json','EXACT_PACKAGE_AND_SEAL')
    require(batch['limits']==dict(metadataBytes=4194304,fixtureBytes=2097152,wrapperMetadataBytes=196608,productionMetadataPeakBytes=3178496,parentWaitSeconds=200,driverSeconds=180,minimumAvailablePhysicalBytes=2147483648),'BATCH_LIMITS')
    require(batch['batchId'].startswith('D1-E3-') and batch['uniqueRootName']=='e3-'+batch['batchId'].removeprefix('D1-E3-') and len(batch['coordinatorGrantCommitment'])==64,'FIXED_BATCH_IDENTITY')
    return dict(batchId=batch['batchId'],uniqueRootName=batch['uniqueRootName'],batchManifestSha256=budget.fingerprint(BASE/'manifest/e3-batch.json')['sha256'],
                state=STATE,profile='REAL_IO',realExecutionEnabled=False,externalGrantRequired=True,maximumG=1,maximumFullAttempts=1,
                maximumPreparationMetadataBytes=819200,maximumPreparationFixtureBytes=1441792,productionFixtureReservedBytes=655360)


def fixture_kind(path):return 'FIXTURE' if path.suffix.lower() in ('.bin','.out') else 'METADATA'


def preparation_usage():
    evidence=files_under('evidence');selfcheck=files_under('selfcheck') if present(BASE/'selfcheck') else []
    return dict(metadataBytes=sum(path.stat().st_size for path in evidence)+sum(path.stat().st_size for path in selfcheck if fixture_kind(path)=='METADATA'),
                fixtureBytes=sum(path.stat().st_size for path in selfcheck if fixture_kind(path)=='FIXTURE'))


if __name__=='__main__':
    print(json.dumps(dict(scope='E3_PROFILE_INSPECT',status='NOT_RUN',executionAllowed=False,
                         reservationConsumed=False,mediaStatCalls=0,mediaBytesRead=0)))
