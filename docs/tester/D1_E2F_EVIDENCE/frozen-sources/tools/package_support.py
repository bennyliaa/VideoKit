"""Offline source/receipt packaging; bounded reads and no runtime imports."""
import ast
import hashlib
import json
import os
from pathlib import Path
import stat
import zipfile

BASE = Path(__file__).absolute().parents[1]
PROJECT = BASE.parents[2]
SOURCE_FOLDERS = ('src','tools','manifest','profiles','upstream-e2e','upstream-e2d',
                  'upstream-e2c','upstream-e2b','upstream-e2a','upstream-e2','upstream-e1e')
DOCS = [BASE.parent/('D1_E2F_'+name+'_V1.0.md') for name in ('DELIVERY','EVIDENCE_REEVALUATION','EXECUTION_APPENDIX')]
SEAL = BASE/'evidence/freeze-summary.json'
ARCHIVE = BASE/'artifacts/E2F-source.zip'
ORIGINAL_SEAL = 'aa59420cff4153395af2ab9b97eb47d8f560e91763b730f47c0fda3c0578b66a'
ORIGINAL_ARCHIVE = '2a1202f2bba27d86f20f73af6fe286d5574e0575d67880eb865eb0644bc4db34'
SOURCE_CAP = 268435456


def require(value, code):
    if not value: raise ValueError(code)


def encoded(value):
    return (json.dumps(value,sort_keys=True,indent=2,ensure_ascii=True)+'\n').encode('ascii')


class SourceReader:
    def __init__(self, byte_cap=SOURCE_CAP, file_cap=8192):
        self.bytes = self.files = 0
        self.byte_cap = byte_cap; self.file_cap = file_cap
        self.cache = {}
        self.logical_reserved = 0
        self.logical_reservation_peak = 0

    def path(self, path):
        path = Path(os.path.abspath(path))
        require(path == BASE or path.is_relative_to(BASE) or path in DOCS or
                path == PROJECT/'docs/milestones/D1_E2F_CODER_REQUIREMENTS_V1.0.md', 'PACKAGE_PATH_DENIED')
        for part in reversed((path,*path.parents)):
            info = os.lstat(part)
            require(not stat.S_ISLNK(info.st_mode) and not getattr(info,'st_file_attributes',0)&0x400,'PACKAGE_REPARSE_DENIED')
        return path

    def start(self):
        require(self.files < self.file_cap,'SOURCE_FILE_READ_LIMIT'); self.files += 1

    def charge(self, count):
        require(type(count) is int and count >= 0 and self.bytes+count+self.logical_reserved <= self.byte_cap,'SOURCE_READ_BYTE_LIMIT')
        self.bytes += count

    def available(self):return self.byte_cap-self.bytes-self.logical_reserved

    def reserve_logical(self,count):
        require(type(count) is int and count>0 and count<=self.available(),'SOURCE_ZIP_LOGICAL_RESERVATION')
        self.logical_reserved+=count
        self.logical_reservation_peak=max(self.logical_reservation_peak,self.logical_reserved)

    def blocks(self, path):
        path = self.path(path); self.start()
        require(stat.S_ISREG(os.lstat(path).st_mode),'PACKAGE_REGULAR_FILE_REQUIRED')
        with open(path,'rb',buffering=0) as stream:
            while True:
                remaining = self.available()
                require(remaining > 0,'SOURCE_READ_BYTE_LIMIT')
                block = stream.read(min(65536,remaining))
                if not block: break
                self.charge(len(block)); yield block

    def raw(self,path):
        data=b''.join(self.blocks(path));require(len(data)<=2097152,'PACKAGE_JSON_SIZE_LIMIT');return data

    def json(self,path):return json.loads(self.raw(path).decode('utf-8-sig'))

    def fact(self,path):
        path=Path(path)
        if path not in self.cache:
            sha=hashlib.sha256();count=0
            for block in self.blocks(path):sha.update(block);count+=len(block)
            self.cache[path]={'path':path.relative_to(PROJECT).as_posix(),'bytes':count,'sha256':sha.hexdigest()}
        return dict(self.cache[path])

    def usage(self):return {'bytes':self.bytes,'files':self.files,'byteCap':self.byte_cap,'fileCap':self.file_cap,'hashBlockBytes':65536,
                            'logicalBytesReserved':self.logical_reserved,'logicalReservationPeak':self.logical_reservation_peak}


class ChargedZipFile:
    """Charge the compressed ZIP stream as well as decompressed member reads."""
    def __init__(self,path,reader):
        reader.path(path);reader.start();self.reader=reader;self.stream=open(path,'rb',buffering=0)
    def read(self,size=-1):
        remaining=self.reader.available()
        require(remaining>0,'SOURCE_ZIP_READ_LIMIT')
        data=self.stream.read(min(remaining,size) if size>=0 else remaining)
        self.reader.charge(len(data));return data
    def seek(self,*args):return self.stream.seek(*args)
    def tell(self):return self.stream.tell()
    def seekable(self):return True
    def close(self):self.stream.close()


def files_under(folder):
    root=BASE/folder;found=[];visited=0
    SourceReader().path(root)
    for directory,dirs,names in os.walk(root,followlinks=False):
        visited+=len(dirs)+len(names)+1;require(visited<=16384,'PACKAGE_NAMESPACE_LIMIT')
        for name in dirs:
            path=Path(directory)/name
            require(not path.is_symlink() and not path.is_junction(),'PACKAGE_DIRECTORY_REPARSE')
        for name in names:
            path=Path(directory)/name
            require(not path.is_symlink() and not path.is_junction() and path.is_file(),'PACKAGE_FILE_REPARSE')
            found.append(path);require(len(found)<=8192,'PACKAGE_FILE_SET_LIMIT')
    return sorted(found)


def sources():return sorted(path for folder in SOURCE_FOLDERS for path in files_under(folder))


def receipts():return sorted(files_under('evidence')+files_under('reevaluation'))


def configuration(reader):
    old=reader.json(BASE/'upstream-e2e/e2e-freeze.json')
    require(reader.fact(BASE/'upstream-e2e/e2e-freeze.json')['sha256']==ORIGINAL_SEAL,'UPSTREAM_E2E_SEAL')
    require(reader.fact(BASE/'upstream-e2e/E2E-source.zip')['sha256']==ORIGINAL_ARCHIVE,'UPSTREAM_E2E_ARCHIVE')
    required={}
    inherited={}
    for row in old['immutableFiles']:
        prefix='docs/coder/d1e2e/'
        if not row['path'].startswith(prefix):continue
        name=row['path'][len(prefix):]
        if name.startswith(('src/','profiles/')) or name=='manifest/branches.json' or name=='tools/r-helper.ps1' or name=='artifacts/E2C.dll' or name.startswith('artifacts/java/'):
            required[name]=row
        if name.startswith(tuple(folder+'/' for folder in SOURCE_FOLDERS if folder.startswith('upstream-') and folder!='upstream-e2e')):
            inherited[name]=row
        mapped={'evidence/source-manifest.json':'upstream-e2e/source-manifest.json',
                'manifest/e2e-batch.json':'upstream-e2e/e2e-batch.json',
                'tools/e2e_driver.py':'upstream-e2e/e2e_driver.py'}.get(name)
        if mapped:inherited[mapped]=row
    require(len(required)==48,'ORIGINAL_PRODUCTION_BINDING_COUNT')
    for name,row in required.items():
        fact=reader.fact(BASE/name)
        require(fact['bytes']==row['bytes'] and fact['sha256']==row['sha256'],'COPIED_PRODUCTION_CHANGED:'+name)
    for name,row in inherited.items():
        fact=reader.fact(BASE/name)
        require(fact['bytes']==row['bytes'] and fact['sha256']==row['sha256'],'INHERITED_EVIDENCE_CHANGED:'+name)
    actual_src={p.relative_to(BASE).as_posix() for p in files_under('src')}
    require(actual_src=={n for n in required if n.startswith('src/')},'PRODUCTION_SOURCE_SET_CHANGED')
    actual_config={p.relative_to(BASE).as_posix() for p in files_under('profiles')}
    require(actual_config=={n for n in required if n.startswith('profiles/')},'PRODUCTION_PROFILE_SET_CHANGED')
    actual_binary={p.relative_to(BASE).as_posix() for p in files_under('artifacts') if p.suffix in ('.dll','.class')}
    require(actual_binary=={n for n in required if n.startswith('artifacts/')},'ORIGINAL_BINARY_SET_CHANGED')
    manifest=reader.json(BASE/'manifest/e2f-reevaluation.json')
    require(manifest['scope']=='EVIDENCE_REEVALUATION_ONLY' and
            manifest['actualExecutionAllowed'] is manifest['newActualPermitGranted'] is manifest['realMediaAllowed'] is manifest['compileAllowed'] is False,'E2F_HAS_NO_EXECUTION_CAPABILITY')
    require(manifest['originalSealSha256']==ORIGINAL_SEAL and
            manifest['originalResultManifestSha256']=='baa6a1ed87764a5d16b1d282717824110d0082bc188606edf4affb33377750ea' and
            manifest['originalPrecloseSha256']=='702d8505e16bf504564179c14477e7cfe50af35c922531034c66645d6bc79032','ORIGINAL_INPUT_BINDING')
    require(manifest['limits']==dict(resultReadBytes=16777216,resultReadFiles=1024,sourceReadBytes=268435456,sourceReadFiles=8192,hashBlockBytes=65536,fixtureBytes=2097152,metadataBytes=4194304),'E2F_LIMITS_CHANGED')
    approval=manifest['approval'];require(approval['path']=='docs/milestones/D1_E2F_CODER_REQUIREMENTS_V1.0.md' and reader.fact(PROJECT/approval['path'])['sha256']==approval['sha256'],'E2F_APPROVAL_CHANGED')
    require(not (BASE/'execution').exists() and not (BASE/'selfcheck').exists(),'E2F_MUST_NOT_HAVE_EXECUTION_OUTPUTS')
    return {'productionSourceFiles':32,'originalConfigurationFiles':5,'compiledArtifacts':10,'originalRHelperPreserved':True,
            'productionChanges':0,'compileInvocations':0,'newActualPermitGranted':False,'originalBindings':manifest,
            'inheritedFilesVerified':len(inherited),
            'productionBindings':[dict(path=name,bytes=row['bytes'],sha256=row['sha256']) for name,row in sorted(required.items())]}


def validate_receipts(reader):
    change=reader.json(BASE/'evidence/minimal-diff.json')
    require(change['scope']=='E2F_MINIMUM_OFFLINE_WRAPPER_DECISION_REPLACEMENT' and change['originalFrozenDriver']['modified'] is False,'MINIMUM_DIFF_SCOPE')
    require(reader.fact(BASE/'upstream-e2e/e2e_driver.py')['sha256']==change['originalFrozenDriver']['sha256'],'ORIGINAL_DRIVER_DIFF_BINDING')
    require(change['replacement']['countOnlyAcceptanceAllowed'] is change['replacement']['newActualCapability'] is False,'COUNT_ONLY_OR_ACTUAL_DIFF_FORBIDDEN')
    for row in change['coreFiles']:
        require(row['path'] in {'tools/completion_evaluation.py','tools/resource_evaluation.py','tools/e2f_wrapper.py','tools/reevaluate.py'},'MINIMUM_DIFF_FILE_SCOPE')
        fact=reader.fact(BASE/row['path'])
        require(fact['bytes']==row['bytes'] and fact['sha256']==row['sha256'],'MINIMUM_DIFF_SOURCE_HASH_CHANGED')
    checks=reader.json(BASE/'evidence/offline-checks.json')
    require(checks.get('status')=='PASS' and type(checks.get('assertions')) is int and checks['assertions']>0,'OFFLINE_CHECKS_REQUIRED')
    require(checks['assertions']==len(checks['checks']),'OFFLINE_CHECK_COUNT')
    for key in ('newG','helpersStarted','newOSMetricSamples','newActualAttempts','newActualPasses','compileInvocations','originalEvidenceWrites'):
        require(type(checks.get(key)) is int and checks[key]==0,'OFFLINE_ACTIVITY:'+key)
    result=reader.json(BASE/'reevaluation/evidence-reevaluation.json')
    require(result['scope']=='EVIDENCE_REEVALUATION' and result['accepted'] is True and result['decision']=='SUPPORTED_ORIGINAL_TOOL_FACTS','OFFLINE_REEVALUATION_NOT_SUPPORTED')
    original=result['originalResult']
    require(original['driverStatus']==original['launcherStatus']=='FAIL' and original['originalGExitCode']==2 and original['originalToolExitCode']==1 and original['assertions']==160 and original['reservationConsumed'] is True,'ORIGINAL_RESULT_MUST_STAY_FAIL')
    require(result['completion']['accepted'] is result['resources']['accepted'] is True,'ALL_REEVALUATION_GATES_REQUIRED')
    for value in result['readerUsage'].values():require(value['bytes']<=value['byteCap'] and value['files']<=value['fileCap'],'RECORDED_READER_LIMIT')
    return checks,result


def seal_package():
    require(not SEAL.exists(),'FROZEN_E2F_PACKAGE_READ_ONLY')
    reader=SourceReader();binding=configuration(reader);checks,result=validate_receipts(reader)
    source_files=sources()
    for path in source_files:
        if path.parent==BASE/'tools' and path.suffix=='.py':ast.parse(reader.raw(path).decode('utf-8-sig'),filename=str(path))
    source={'scope':'E2F_OFFLINE_SOURCE_AND_COMPLETE_UPSTREAM_DEPENDENCIES','files':[reader.fact(p) for p in source_files]}
    (BASE/'evidence/source-manifest.json').write_bytes(encoded(source))
    with zipfile.ZipFile(ARCHIVE,'x',zipfile.ZIP_DEFLATED) as archive:
        for path in source_files:
            info=zipfile.ZipInfo(path.relative_to(PROJECT).as_posix(),date_time=(2026,10,17,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED
            with archive.open(info,'w') as member:
                for block in reader.blocks(path):require(member.write(block)==len(block),'SOURCE_ARCHIVE_EXACT_WRITE')
    immutable=sorted(set(source_files+files_under('artifacts')+receipts()+DOCS))
    records=[reader.fact(p) for p in immutable]
    metadata=sum(p.stat().st_size for p in receipts())
    value={'schema':1,'candidate':'D1-E2F-20261017','state':'E2F_FROZEN_PENDING_INDEPENDENT_REVIEW','scope':'EVIDENCE_REEVALUATION',
           'files':records,'sourceFiles':len(source_files),'sourceZip':reader.fact(ARCHIVE),'productionBinding':binding,
           'offlineAssertions':checks['assertions'],'reevaluationDecision':result['decision'],'originalResult':result['originalResult'],
           'newActualAttempts':0,'newActualPasses':0,'newG':0,'helpersStarted':0,'newOSMetricSamples':0,'compileInvocations':0,
           'originalEvidenceWrites':0,'noInFlight':True,'fixtureBytes':0,'metadataBytes':0,'sealBytes':0,
           'originalReadUsage':result['readerUsage'],'packagingSourceReadUsage':reader.usage(),
           'sourceCap':SOURCE_CAP,'resultCap':16777216,'metadataCap':4194304,'fixtureCap':2097152,
           'D1':'NOT_PASSED','M0':'NOT_STARTED','realMedia':'DISABLED','newExecutionCapability':False}
    for _ in range(16):
        data=encoded(value)
        if value['sealBytes']==len(data) and value['metadataBytes']==metadata+len(data):break
        value['sealBytes']=len(data);value['metadataBytes']=metadata+len(data)
    else:raise ValueError('E2F_SEAL_SIZE_FIXED_POINT')
    require(value['metadataBytes']<=4194304,'E2F_METADATA_CAP')
    with open(SEAL,'xb',buffering=0) as target:require(target.write(data)==len(data),'E2F_SEAL_EXACT_WRITE')
    print(json.dumps({'state':value['state'],'freezeSha256':hashlib.sha256(data).hexdigest(),'sourceFiles':len(source_files),
                      'immutableFiles':len(records),'sourceZip':value['sourceZip'],'metadataBytes':value['metadataBytes'],
                      'fixtureBytes':0,'offlineAssertions':checks['assertions'],'newActualAttempts':0,'sourceReadUsage':reader.usage()}))


def verify_package(expected_freeze=None):
    # Recompute the evidence result without writing it or invoking production.
    from evidence_io import load_original_bundle
    from e2f_wrapper import evaluate_bound_bundle
    bundle=load_original_bundle();current=evaluate_bound_bundle(bundle)
    require(current['accepted'] is True,'CURRENT_ORIGINAL_EVIDENCE_NOT_SUPPORTED')
    used=bundle['readerUsage']['source']
    reader=SourceReader(SOURCE_CAP-used['bytes'],8192-used['files'])
    raw=reader.raw(SEAL);seal_hash=hashlib.sha256(raw).hexdigest()
    if expected_freeze is not None:require(expected_freeze==seal_hash,'EXPECTED_E2F_FREEZE_CHANGED')
    frozen=json.loads(raw);require(frozen['state']=='E2F_FROZEN_PENDING_INDEPENDENT_REVIEW','E2F_FREEZE_STATE')
    binding=configuration(reader);checks,recorded=validate_receipts(reader)
    require(binding==frozen['productionBinding'] and recorded==current,'REEVALUATION_OR_BINDING_CHANGED')
    listed=frozen['files'];require(len({r['path'] for r in listed})==len(listed),'DUPLICATE_IMMUTABLE_PATH')
    for row in listed:require(reader.fact(PROJECT/row['path'])==row,'FROZEN_E2F_FILE_CHANGED:'+row['path'])
    source=reader.json(BASE/'evidence/source-manifest.json');source_files=sources()
    require({p.relative_to(PROJECT).as_posix() for p in source_files}=={r['path'] for r in source['files']},'E2F_SOURCE_SET_CHANGED')
    for row in source['files']:require(reader.fact(PROJECT/row['path'])==row,'E2F_SOURCE_CHANGED')
    stream=ChargedZipFile(ARCHIVE,reader)
    try:
        with zipfile.ZipFile(stream) as archive:
            require(len(archive.namelist())==len(source['files']) and set(archive.namelist())=={r['path'] for r in source['files']},'E2F_SOURCE_ZIP_MEMBERS')
            for row in source['files']:
                reader.start();sha=hashlib.sha256();count=0
                with archive.open(row['path']) as member:
                    while True:
                        remaining=reader.available();require(remaining>1,'SOURCE_ZIP_LOGICAL_LIMIT')
                        request=min(65536,remaining//2)
                        reader.reserve_logical(request)
                        try:block=member.read(request)
                        except BaseException:
                            reader.logical_reserved-=request
                            reader.charge(request)
                            raise
                        else:reader.logical_reserved-=request
                        if not block:break
                        reader.charge(len(block));count+=len(block);sha.update(block)
                require(count==row['bytes'] and sha.hexdigest()==row['sha256'],'E2F_SOURCE_ZIP_MEMBER_HASH')
    finally:stream.close()
    actual=set(source_files+files_under('artifacts')+receipts()+DOCS)-{SEAL}
    require({p.relative_to(PROJECT).as_posix() for p in actual}=={r['path'] for r in listed},'E2F_IMMUTABLE_FILE_SET_CHANGED')
    metadata=sum(p.stat().st_size for p in receipts())
    require(metadata==frozen['metadataBytes']<=4194304 and len(raw)==frozen['sealBytes'],'E2F_METADATA_ACCOUNTING')
    require(frozen['fixtureBytes']==0 and frozen['offlineAssertions']==checks['assertions'] and frozen['newActualAttempts']==frozen['newActualPasses']==0,'E2F_ACTIVITY_CHANGED')
    combined={'bytes':used['bytes']+reader.bytes,'files':used['files']+reader.files,'byteCap':SOURCE_CAP,'fileCap':8192}
    print(json.dumps({'integrity':'PASS','state':frozen['state'],'freezeSha256':seal_hash,'expectedFreezeSupplied':expected_freeze is not None,
                      'sourceFiles':len(source_files),'immutableFiles':len(listed),'offlineAssertions':checks['assertions'],
                      'reevaluationDecision':current['decision'],'originalResult':current['originalResult'],
                      'metadataBytes':metadata,'fixtureBytes':0,'sourceReadUsageCombined':combined,'originalResultReadUsage':bundle['readerUsage']['result'],
                      'newActualAttempts':0,'newActualPasses':0,'newG':0,'helpersStarted':0,'newOSMetricSamples':0,'compileInvocations':0,
                      'originalEvidenceWrites':0,'noInFlight':True,'D1':'NOT_PASSED','M0':'NOT_STARTED'}))
