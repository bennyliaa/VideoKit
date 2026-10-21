"""One private diagnostic only; Base64 is transport encoding, never a product or permission change."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import time
import exact_process as ep
from command_response import complete_stdout,parse_features
from stream_base64 import transfer_base64
from private_commands import *

BASE=Path(__file__).resolve().parents[1]
LIMITS=ep.Limits(timeout=15,cleanup=2,stdout_cap=16384,stderr_cap=16384,retained_prefix=4096)
class ProcessTransport:
    adb='D:/Android/SDK/platform-tools/adb.exe'
    def command(self,args):return ep.collect(args,LIMITS)
    def transfer(self,args):return transfer_base64(args,BASE/'payload256.bin',256,SHA,LIMITS)
def write_new(path,value):
    raw=(json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    with path.open('xb') as f:f.write(raw);f.flush();os.fsync(f.fileno())
    return len(raw)
def observed_stdout(record):
    s=record['stdout'];raw=bytes.fromhex(s['prefixHex'])
    if s['prefixTruncated'] or not s['closeReturned'] or s['error'] is not None or s['bytes']!=len(raw) or s['sha256']!=hashlib.sha256(raw).hexdigest():raise ValueError('ORIGINAL_OUTPUT_NOT_COMPLETE')
    return raw
def run_diagnostic(transport,evidence,*,authorized=False):
    if not authorized:raise PermissionError('PLAN_ONLY')
    evidence=Path(evidence);evidence.mkdir(parents=True,exist_ok=False)
    used=write_new(evidence/'attempt.json',dict(batch=BATCH,nonce=NONCE,state='CONSUMED_BEFORE_REMOTE_MUTATION',target=TARGET,rawBytes=256,encodedBytes=344))
    result=dict(batch=BATCH,status='NOT_ADMITTED',priorRemoteOwnership='UNKNOWN_NOT_CLEARED',metadataCommands=0,producerAttempts=0,rawSource=None,encoding=None,receiverObservation=None,receiverProof=None,independentProof=None,records=[],nextMediaOrProductAuthorized=False)
    def call(name,args,producer=False):
        nonlocal used
        if ep.retained_owners():raise RuntimeError('ORIGINAL_OWNER_RETAINED_NO_NEXT_IO')
        if used+131072>1048576:raise RuntimeError('TOTAL_LOG_BUDGET')
        field='producerAttempts' if producer else 'metadataCommands';cap=1 if producer else 20
        if result[field]>=cap:raise RuntimeError('ONE_ATTEMPT_OR_METADATA_CAP')
        result[field]+=1;record=transport.transfer(args) if producer else transport.command(args)
        raw=(json.dumps(record,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
        if len(raw)>65536:raise RuntimeError('ORIGINAL_RECORD_CAP')
        path=evidence/(f'{len(result["records"]):02d}-'+name+'.json');used+=write_new(path,record)
        result['records'].append(dict(stage=name,file=path.name,status=record['status'],ownership=record['ownership']))
        if producer:
            result['rawSource']=record['rawSource'];result['encoding']=record['encoding']
            try:result['receiverObservation']=receiver_observation(observed_stdout(record))
            except Exception as error:result['receiverObservationError']=str(error)[:160]
        return complete_stdout(record)
    def remote(name,script):return call(name,argv(transport.adb,script))
    try:
        if 'shell_v2' not in parse_features(call('features',[str(transport.adb),'-s',SERIAL,'features'])):raise ValueError('SHELL_V2_REQUIRED')
        if one(remote('original-context',context_script()),'CONTEXT')!={'uid':str(UID),'pwd':PWD}:raise ValueError('ORIGINAL_CONTEXT')
        result['decoderProbe']=parse_probe(remote('one-byte-no-file-decoder-probe',decoder_probe_script()))
        result['priorProcessObservation']=check_processes(remote('uid-snapshot',processes_script()))
        if one(remote('new-private-directory',mkdir_script()),'DIRECTORY')!={'path':DIRECTORY}:raise ValueError('NEW_PRIVATE_DIRECTORY')
        result['receiverProof']=parse_receiver(call('one-base64-receiver',argv(transport.adb,receiver_script(),True),True))
        result['independentProof']=parse_proof(remote('independent-raw-proof',proof_script()))
        result['status']='ASCII_STREAM_DECODE_AND_RAW_SHA_VERIFIED_NOT_A_MEDIA_FIXTURE'
    except Exception as error:result['firstFailure']=str(error)[:300]
    result['retainedLocalOwners']=ep.retained_owners()
    raw=(json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    if len(raw)>65536 or used+len(raw)>1048576:raise RuntimeError('FINAL_LOG_BUDGET')
    write_new(evidence/'result.json',result);return result
def plan():
    return dict(mode='PLAN_ONLY',executionAuthorized=False,batch=BATCH,nonce=NONCE,serial=SERIAL,uid=UID,pwd=PWD,directory=DIRECTORY,target=TARGET,rawBytes=256,encodedBytes=344,encodedLfBytes=0,sourceRawPrehashBytes=256,sourceRawStreamBytes=256,encodedPrehashBytes=344,encodedSubmitCap=344,independentDeviceHashCap=256,decoderProbeRawBytes=1,decoderProbeEncodedBytes=4,metadataPlanned=6,metadataCap=20,producerCap=1,perCommandSeconds=15,cleanupSeconds=2,logBytes=1048576,oldResidualOrMediaAccess=0,externalStorageAccess=0,permissionsChanged=False)
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--execute',action='store_true');p.add_argument('--formal-batch');p.add_argument('--evidence-dir',type=Path);a=p.parse_args()
    if not a.execute:print(json.dumps(plan(),ensure_ascii=False,indent=2));return
    if a.formal_batch!=BATCH or a.evidence_dir is None or not a.evidence_dir.is_absolute() or a.evidence_dir.resolve().is_relative_to(BASE):raise ValueError('NEW_FORMAL_BATCH_AND_EXTERNAL_EVIDENCE_REQUIRED')
    result=run_diagnostic(ProcessTransport(),a.evidence_dir,authorized=True);print(json.dumps(result,ensure_ascii=False,indent=2))
    if ep.retained_owners():
        print('ORIGINAL_OWNER_RETAINED_NO_RETRY',flush=True)
        while ep.retained_owners():time.sleep(1)
    if result['status']!='ASCII_STREAM_DECODE_AND_RAW_SHA_VERIFIED_NOT_A_MEDIA_FIXTURE':raise SystemExit(1)
if __name__=='__main__':main()
