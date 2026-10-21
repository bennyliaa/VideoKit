"""Fixed MP4 then conditional AVI, no arbitrary receipt/source CLI or automatic product tests."""
from pathlib import Path
from dataclasses import asdict
import argparse
import hashlib
import json
import os
import time
import exact_process as ep
from command_response import complete_stdout,parse_features
from stream_base64 import transfer_base64
import t6_protocol as p
from media_commands import *

BASE=Path(__file__).resolve().parents[1];LOG_CAP=8388608;STORES=[]
def canonical(v):return (json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
def limits(seconds=15):return ep.Limits(timeout=seconds,cleanup=2,stdout_cap=16384,stderr_cap=16384,retained_prefix=8192)
def retained():return ep.retained_owners()+sum(len(s.pending) for s in STORES)
def load_manifest():
    raw=(BASE/'tools/fixed-media-manifest.json').read_bytes();m=json.loads(raw)
    specs=tuple(Spec(**x) for x in m['files'])
    if m['batch']!=BATCH or [s.alias for s in specs]!=['basic.mp4','subtitle.avi'] or [s.bytes for s in specs]!=[349102,736454656] or [s.sha256 for s in specs]!=['720957c94b3665ff97bcc2f59ad5407c5ca54f566b59865723be9eecc0a6a1f9','3f0bf3e9fa6f24130a546fee5be98ba43274959cdc0df82a2ee74306ad4ef52f']:raise ValueError('FIXED_MANIFEST_IDENTITY')
    for s in specs:s.validate()
    return specs,hashlib.sha256(raw).hexdigest()
class ProcessTransport:
    adb='D:/Android/SDK/platform-tools/adb.exe';local_only=False
    def record_argv(self,args):return args
    def command(self,args,seconds):return ep.collect(args,limits(seconds))
    def transfer(self,args,s):return transfer_base64(args,s.source,s.bytes,s.sha256,limits(s.transferSeconds))

class Store:
    def __init__(self,root):self.root=Path(root);self.root.mkdir(parents=True,exist_ok=False);self.used=0;self.pending=[];self.read_bytes=0;self.reads=0;STORES.append(self)
    def write(self,name,value,final=False):
        if self.pending:raise RuntimeError('ORIGINAL_ARTIFACT_CLOSE_UNKNOWN')
        raw=canonical(value)
        if len(raw)>131072 or self.used+len(raw)+(0 if final else 131072)>LOG_CAP:raise RuntimeError('LOG_RESERVATION_CAP')
        self.used+=len(raw) # Reservation is cumulative even on write/fsync/close failure; never refunded.
        path=self.root/name
        if Path(name).name!=name:raise ValueError('EXACT_ARTIFACT_NAME')
        f=path.open('xb');self.pending.append(f)
        try:ep.write_all(f,raw,lambda data:None);f.flush();os.fsync(f.fileno())
        finally:
            f.close();self.pending.remove(f) # If close throws, actual original file remains strongly retained.
        return dict(file=name,bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest())
    def read(self,row):
        if self.pending:raise RuntimeError('ORIGINAL_ARTIFACT_CLOSE_UNKNOWN')
        if Path(row['file']).name!=row['file'] or not 0<=row['bytes']<=131072 or self.reads>=128 or self.read_bytes+row['bytes']+1>4194304:raise ValueError('RECEIPT_READ_CAP')
        path=self.root/row['file']
        if path.is_symlink() or not path.is_file() or path.stat().st_size!=row['bytes']:raise ValueError('RECEIPT_ROLE_OR_LENGTH')
        self.reads+=1;f=path.open('rb');self.pending.append(f)
        try:raw=f.read(row['bytes']+1);self.read_bytes+=len(raw)
        finally:f.close();self.pending.remove(f)
        if len(raw)!=row['bytes'] or hashlib.sha256(raw).hexdigest()!=row['sha256']:raise ValueError('RECEIPT_ORIGINAL_BYTES_CHANGED')
        return json.loads(raw)

def validate_producer(s,r):
    complete_stdout(r);raw=r['rawSource'];enc=r['encoding'];pre=raw['prehash']
    if raw['expectedBytes']!=s.bytes or raw['expectedSha256']!=s.sha256 or pre['rawBytes']!=s.bytes or pre['rawSha256']!=s.sha256 or raw['streamBytes']!=s.bytes or raw['streamSha256']!=s.sha256 or not raw['streamReachedDeclaredEnd'] or not raw['actualRawCloseReturned']:raise ValueError('RAW_ORIGINAL_IDENTITY')
    if enc['expectedBytes']!=s.encodedBytes or enc['actualSubmittedBytes']!=s.encodedBytes or pre['encodedBytes']!=s.encodedBytes or pre['encodedSha256']!=enc['expectedSha256'] or enc['actualSubmittedSha256']!=enc['expectedSha256'] or r['submittedBytes']!=s.encodedBytes or not enc['noEncodedDiskCopy']:raise ValueError('ENCODED_ORIGINAL_IDENTITY')
    if any(r[k]!=s.encodedBytes for k in ['expectedBytes','sourcePrehashBytes','sourceStreamReadBytes']) or any(r[k]!=enc['expectedSha256'] for k in ['expectedSha256','sourcePrehashSha256','submittedSha256']):raise ValueError('ORIGINAL_PUMP_ENCODING_BINDING')
    return parse_receiver(complete_stdout(r),s)

def build_file_evidence(s,records):
    if set(records)!={'producer','temp','publish','final'}:raise ValueError('FILE_RECEIPT_STAGES')
    for stage,item in records.items():
        if item['record']['argv']!=item['expectedArgv']:raise ValueError('ORIGINAL_ARGV_MISMATCH')
        complete_stdout(item['record'])
    r=records['producer']['record'];rx=validate_producer(s,r);raw=r['rawSource'];enc=r['encoding']
    temp=parse_proof(complete_stdout(records['temp']['record']),s)
    published=parse_publish(complete_stdout(records['publish']['record']),s,temp['before']);final=parse_proof(complete_stdout(records['final']['record']),s,True,temp['before'])
    return dict(rawSource=raw,encoding=enc,receiver=rx,tempProof=temp,publication=published,finalProof=final,allOriginalOwnersReturned=True,tempAbsenceObserved=True)

def verify_ready(store,row,expected,s):
    if retained():raise RuntimeError('ORIGINAL_OWNER_UNKNOWN_BLOCKS_DEPENDENCY')
    saved=store.read(row)
    if saved!=expected or saved['batch']!=BATCH or saved['file']!=asdict(s) or saved['state']!='READY_FROM_CURRENT_ORIGINAL_RECORDS':raise ValueError('READY_RECEIPT_CONTENT')
    originals={stage:dict(record=store.read(item['ref']),expectedArgv=item['expectedArgv'],ref=item['ref']) for stage,item in saved['originals'].items()}
    if saved['evidence']!=build_file_evidence(s,originals):raise ValueError('READY_RECEIPT_NOT_ORIGINAL_PROOF')
    if retained():raise RuntimeError('ORIGINAL_OWNER_UNKNOWN_BLOCKS_DEPENDENCY')
    return dict(file=row['file'],sha256=row['sha256'],verifiedOriginalStages=4,verifiedContent=True,originalOwnersReturned=True)

def run_preload(transport,evidence,*,authorized=False,specs=None):
    if not authorized:raise PermissionError('PLAN_ONLY')
    fixed,manifest_sha=load_manifest()
    if specs is None:specs=fixed
    elif not getattr(transport,'local_only',False):raise ValueError('FIXED_PRODUCTION_MANIFEST_ONLY')
    else:
        for s in specs:
            if not Path(s.source).resolve().is_relative_to(BASE/'evidence/local-main-001') or s.bytes>131072:raise ValueError('OWNED_SMALL_SYNTHETIC_ONLY')
        manifest_sha=hashlib.sha256(canonical([asdict(s) for s in specs])).hexdigest()
    if [s.alias for s in specs]!=['basic.mp4','subtitle.avi']:raise ValueError('FIXED_ORDER')
    for s in specs:s.validate()
    store=Store(evidence);store.write('attempt.json',dict(batch=BATCH,nonce=NONCE,manifestSha256=manifest_sha,consumed=True,scope='MP4_THEN_CONDITIONAL_AVI',sourceFiles=[asdict(s) for s in specs]))
    result=dict(batch=BATCH,status='NOT_ADMITTED',manifestSha256=manifest_sha,metadataCommands=0,producerAttempts={s.alias:0 for s in specs},files={},mp4Dependency=None,priorRemoteOwnership='UNKNOWN_NOT_CLEARED',productMethodsRun=0,records=[])
    def call(stage,args,seconds=15,spec=None):
        if retained():raise RuntimeError('ORIGINAL_OWNER_UNKNOWN_NO_NEXT_IO')
        if store.used+262144>LOG_CAP:raise RuntimeError('NEXT_CALL_LOG_RESERVATION')
        if spec is None:
            if result['metadataCommands']>=20:raise RuntimeError('METADATA_CAP')
            result['metadataCommands']+=1;r=transport.command(args,seconds)
        else:
            if result['producerAttempts'][spec.alias]>=1:raise RuntimeError('ONE_PRODUCER_PER_SOURCE')
            result['producerAttempts'][spec.alias]+=1;r=transport.transfer(args,spec)
        ref=store.write(f'{len(result["records"]):02d}-{stage}.json',r);item=dict(ref=ref,expectedArgv=transport.record_argv(args),record=r)
        result['records'].append(dict(stage=stage,ref=ref,status=r['status'],ownership=r['ownership']))
        if r['argv']!=item['expectedArgv']:raise ValueError('ORIGINAL_ARGV_MISMATCH')
        complete_stdout(r);return item
    def remote(stage,script,seconds=15):return call(stage,p.argv(transport.adb,script),seconds)
    try:
        if 'shell_v2' not in parse_features(complete_stdout(call('features',[str(transport.adb),'-s',p.SERIAL,'features'])['record'])):raise ValueError('SHELL_V2_REQUIRED')
        total=sum(s.bytes for s in specs)
        result['initialSpace']=parse_space(complete_stdout(remote('initial-admission-space',admission_script(specs))['record']),'ADMISSION',dict(uid=str(p.UID),pwd=p.PWD,parent=FIXTURES),total)
        result['priorProcessObservation']=p.check_processes(complete_stdout(remote('uid-snapshot',p.processes_script())['record']))
        if p.one(complete_stdout(remote('exclusive-temp-directory',p.mkdir_script())['record']),'DIRECTORY')!={'path':TEMP_DIR}:raise ValueError('EXCLUSIVE_DIRECTORY')
        result['decoderProbe']=p.parse_probe(complete_stdout(remote('serial-decoder-probe',p.decoder_probe_script())['record']))
        ready=None;ready_body=None
        for index,s in enumerate(specs):
            if index:
                result['mp4Dependency']=verify_ready(store,ready,ready_body,specs[0]) # Verifies full persisted original evidence, never a nonempty SHA gate.
            guard=remote(s.alias+'-guard-space',file_guard_script(s));result['files'][s.alias]=dict(space=parse_space(complete_stdout(guard['record']),'FILE_GUARD',dict(uid=str(p.UID),pwd=p.PWD,alias=s.alias,temp=s.temp,final=s.final),sum(x.bytes for x in specs[index:])))
            records={};records['producer']=call(s.alias+'-producer',p.argv(transport.adb,receiver_script(s),True),spec=s)
            validate_producer(s,records['producer']['record'])
            records['temp']=remote(s.alias+'-temp-proof',proof_script(s),s.hashSeconds)
            temp=parse_proof(complete_stdout(records['temp']['record']),s)
            records['publish']=remote(s.alias+'-publish',publish_script(s,temp['before']))
            records['final']=remote(s.alias+'-published-proof',proof_script(s,True),s.hashSeconds)
            evidence_value=build_file_evidence(s,records)
            if retained():raise RuntimeError('ORIGINAL_OWNER_UNKNOWN_BEFORE_READY')
            body=dict(schema=1,batch=BATCH,manifestSha256=manifest_sha,state='READY_FROM_CURRENT_ORIGINAL_RECORDS',file=asdict(s),evidence=evidence_value,originals={k:dict(ref=v['ref'],expectedArgv=v['expectedArgv']) for k,v in records.items()})
            row=store.write(s.alias+'-ready.json',body);gate=verify_ready(store,row,body,s)
            result['files'][s.alias].update(ready=row,readyVerified=gate,evidence=evidence_value)
            if index==0:ready=row;ready_body=body
        result['status']='TWO_FIXTURES_PREPARED_NOT_PRODUCT_PASS'
    except Exception as error:result['firstFailure']=str(error)[:400]
    result.update(retainedLocalOwners=retained(),logReservedBytesBeforeResult=store.used,logLimitBytes=LOG_CAP,receiptMetadataReadBytes=store.read_bytes,receiptMetadataReads=store.reads)
    if not store.pending:store.write('result.json',result,final=True)
    else:result['resultPersistence']='BLOCKED_ORIGINAL_ARTIFACT_CLOSE_UNKNOWN_ORIGINAL_FILE_RETAINED'
    return result

def plan():
    specs,sha=load_manifest()
    return dict(mode='PLAN_ONLY',executionAuthorized=False,batch=BATCH,manifestSha256=sha,files=[asdict(s) for s in specs],metadataPlanned=13,metadataCap=20,logBytes=LOG_CAP,artifactFileCap=131072,receiptMetadataReadCap=4194304,receiptMetadataReadCallsCap=128,cleanupSeconds=2,ordinaryMetadataSeconds=15,sourceRawReadBudget=1473607516,wireBytes=982405016,deviceHashBudget=1473607516,deviceHashPassesPerSource=2,newPayloadBytes=736803758,spaceMarginBytes=MARGIN,probeFiles=2,probeNormalBytes=5,probeStateFileCap=4,probeStateBytesCap=4096,productMethodsPlanned=['normalMp4SixRealFrames','normalAviSixRealFrames','capabilityDenialDoesNotOpenSource','cancelRejectsWrongEpochOversizeAndLateFrame'],productMethodsAutoRun=False)
def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--execute',action='store_true');parser.add_argument('--formal-batch');parser.add_argument('--evidence-dir',type=Path);a=parser.parse_args()
    if not a.execute:print(json.dumps(plan(),ensure_ascii=False,indent=2));return
    if a.formal_batch!=BATCH or a.evidence_dir is None or not a.evidence_dir.is_absolute() or a.evidence_dir.resolve().is_relative_to(BASE):raise ValueError('NEW_FORMAL_BATCH_AND_EXTERNAL_EVIDENCE_REQUIRED')
    r=run_preload(ProcessTransport(),a.evidence_dir,authorized=True);print(json.dumps(r,ensure_ascii=False,indent=2))
    if retained():
        print('ORIGINAL_OWNER_RETAINED_NO_RETRY',flush=True)
        while retained():time.sleep(1)
    if r['status']!='TWO_FIXTURES_PREPARED_NOT_PRODUCT_PASS':raise SystemExit(1)
if __name__=='__main__':main()
