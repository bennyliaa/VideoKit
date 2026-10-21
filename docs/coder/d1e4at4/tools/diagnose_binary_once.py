"""Plan by default. One standard push and one bounded device-local copy, no payload on stdin."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import time
import exact_process as ep
from command_response import complete_stdout,parse_features
from binary_commands import *

BASE=Path(__file__).resolve().parents[1]
LIMITS=ep.Limits(timeout=15,cleanup=2,stdout_cap=16384,stderr_cap=16384,retained_prefix=4096)
SOURCE_OWNERS=[]

class ProcessTransport:
    adb='D:/Android/SDK/platform-tools/adb.exe'
    def command(self,args):return ep.collect(args,LIMITS) # Always empty original stdin, including push.

def retained():return ep.retained_owners()+len(SOURCE_OWNERS)

def prepare_source(receipt):
    p=BASE/'payload256.bin'
    if p.is_symlink() or not p.is_file() or p.stat().st_size!=256:raise ValueError('FIXED_SYNTHETIC_SOURCE_ROLE')
    owner=dict(file=p.open('rb',buffering=0),closeReturned=False);SOURCE_OWNERS.append(owner)
    receipt['hostSourcePrehashBytes']=None;receipt['hostSourceCloseReturned']=False
    try:
        raw=owner['file'].read(257)
        receipt['hostSourcePrehashBytes']=len(raw)
        if len(raw)!=256 or hashlib.sha256(raw).hexdigest()!=SHA:raise ValueError('FIXED_SYNTHETIC_SOURCE_IDENTITY')
        result=dict(path=str(p),prehashBytes=len(raw),sha256=SHA,readCap=257)
    finally:
        owner['file'].close();owner['closeReturned']=True;receipt['hostSourceCloseReturned']=True;SOURCE_OWNERS.remove(owner)
    return result

def write_new(path,value):
    raw=(json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    with path.open('xb') as f:f.write(raw);f.flush();os.fsync(f.fileno())
    return len(raw)

def run_diagnostic(transport,evidence,*,authorized=False):
    if not authorized:raise PermissionError('PLAN_ONLY')
    evidence=Path(evidence);evidence.mkdir(parents=True,exist_ok=False)
    used=write_new(evidence/'attempt.json',dict(batch=BATCH,nonce=NONCE,state='CONSUMED_BEFORE_REMOTE_MUTATION',stage=SOURCE,target=TARGET))
    result=dict(batch=BATCH,status='NOT_ADMITTED',priorRemoteOwnership='UNKNOWN_NOT_CLEARED',metadataCommands=0,pushAttempts=0,copyAttempts=0,payloadStdinBytes=0,hostSourcePrehashBytes=0,adbSourceReadBytes='NOT_OBSERVABLE_FROM_CLIENT_RECEIPT',stageProof=None,copyProof=None,internalProof=None,records=[],nextMediaOrProductAuthorized=False)
    def call(name,args,kind='metadata'):
        nonlocal used
        if retained():raise RuntimeError('ORIGINAL_OWNER_RETAINED_NO_NEXT_IO')
        if used+131072>1048576:raise RuntimeError('TOTAL_LOG_CAP_BEFORE_CALL')
        field={'metadata':'metadataCommands','push':'pushAttempts','copy':'copyAttempts'}[kind]
        cap=20 if kind=='metadata' else 1
        if result[field]>=cap:raise RuntimeError('ATTEMPT_OR_COMMAND_CAP')
        result[field]+=1
        record=transport.command(args)
        raw=(json.dumps(record,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
        if len(raw)>65536:raise RuntimeError('ORIGINAL_RECORD_CAP')
        path=evidence/(f'{len(result["records"]):02d}-'+name+'.json');used+=write_new(path,record)
        result['records'].append(dict(stage=name,kind=kind,file=path.name,status=record['status'],ownership=record['ownership']))
        return complete_stdout(record)
    def remote(name,script,app=True,kind='metadata'):return call(name,argv(transport.adb,script,app),kind)
    try:
        if 'shell_v2' not in parse_features(call('features',[str(transport.adb),'-s',SERIAL,'features'])):raise ValueError('SHELL_V2_REQUIRED_NO_FALLBACK')
        result['shellBase']=parse_base(remote('shell-existing-base',base_script(False),False),False)
        result['appBase']=parse_base(remote('app-existing-base',base_script(True)),True)
        result['priorProcessObservation']=check_processes(remote('uid-snapshot',processes_script()))
        result['hostSource']=prepare_source(result)
        parse_stage(remote('create-exclusive-stage',create_stage_script(),False),created=True)
        parse_stage(remote('app-stage-access',stage_access_script(True)),app=True)
        parse_stage(remote('shell-stage-before-push',stage_access_script(False),False))
        call('one-standard-push',[str(transport.adb),'-s',SERIAL,'push','-q','-Z',str(BASE/'payload256.bin'),SOURCE],'push')
        result['stageProof']=parse_proof(remote('independent-stage-proof',proof_script(True)),True)
        result['copyProof']=parse_copy(remote('one-internal-copy',copy_script(result['stageProof']['before']),kind='copy'))
        result['internalProof']=parse_proof(remote('independent-internal-proof',proof_script(False)),False)
        result['status']='BINARY_PUSH_AND_LOCAL_COPY_VERIFIED_NOT_A_MEDIA_FIXTURE'
    except Exception as error:result['firstFailure']=str(error)[:300]
    result['retainedLocalOwners']=retained()
    final=(json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    if len(final)>65536 or used+len(final)>1048576:raise RuntimeError('FINAL_RECEIPT_CAP')
    write_new(evidence/'result.json',result);return result

def plan():
    return dict(mode='PLAN_ONLY',executionAuthorized=False,batch=BATCH,serial=SERIAL,uid=UID,pwd=PWD,existingAppExternalBase=EXT,stage=SOURCE,internal=TARGET,nonce=NONCE,payloadBytes=256,payloadSha256=SHA,metadataPlanned=9,metadataCap=20,pushCap=1,copyCap=1,perCommandSeconds=15,cleanupSeconds=2,logBytes=1048576,hostPrehashCap=257,adbNominalFileBytes=256,adbActualReadCount='UNKNOWN',stageHashCap=256,internalHashCap=256,deviceLocalCopyCap=256,payloadStdinBytes=0,old26ByteFileAccess=0,realMediaAccess=0,stagingPermissionAndSELinux='UNKNOWN_REQUIRE_DUAL_CONTEXT_ADMISSION',pushAtomicNoReplace='NOT_PROVIDED_BY_ADB; new exclusive scoped directory and immediate conflict guards, no adversarial race guarantee')

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--execute',action='store_true');p.add_argument('--formal-batch');p.add_argument('--evidence-dir',type=Path);a=p.parse_args()
    if not a.execute:print(json.dumps(plan(),ensure_ascii=False,indent=2));return
    if a.formal_batch!=BATCH or a.evidence_dir is None or not a.evidence_dir.is_absolute() or a.evidence_dir.resolve().is_relative_to(BASE):raise ValueError('NEW_FORMAL_BATCH_AND_EXTERNAL_EVIDENCE_REQUIRED')
    result=run_diagnostic(ProcessTransport(),a.evidence_dir,authorized=True);print(json.dumps(result,ensure_ascii=False,indent=2))
    if retained():
        print('ORIGINAL_OWNER_RETAINED_NO_RETRY',flush=True)
        while retained():time.sleep(1)
    if result['status']!='BINARY_PUSH_AND_LOCAL_COPY_VERIFIED_NOT_A_MEDIA_FIXTURE':raise SystemExit(1)
if __name__=='__main__':main()
