"""Default plan only. One separately dispatched tablet diagnostic, never media provisioning."""
from pathlib import Path
from dataclasses import asdict
import argparse
import hashlib
import json
import os
import time
import exact_process as ep
from remote_command import *

BASE=Path(__file__).resolve().parents[1]
BATCH='D1-E4A-T2P-TABLET-20261017'
PAYLOAD_SHA=hashlib.sha256(bytes(range(256))).hexdigest()
LIMITS=ep.Limits(timeout=15,cleanup=2,stdout_cap=16384,stderr_cap=16384,retained_prefix=4096)

class ProcessTransport:
    def __init__(self,adb='D:/Android/SDK/platform-tools/adb.exe'):self.adb=adb
    def command(self,argv):return ep.collect(argv,LIMITS)
    def receive(self,argv,payload):return ep.transfer_file(argv,payload,256,PAYLOAD_SHA,LIMITS)

def write_new(path,value):
    raw=(json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    with path.open('xb') as file:file.write(raw);file.flush();os.fsync(file.fileno())
    return len(raw)

def run_diagnostic(transport,evidence,c=Context(),*,authorized=False,payload=None):
    if not authorized:raise PermissionError('PLAN_ONLY_NO_DEVICE_AUTHORIZATION')
    c.validate();evidence=Path(evidence);evidence.mkdir(parents=True,exist_ok=False)
    payload=BASE/'payload256.bin' if payload is None else Path(payload)
    # No --source option: exactly the frozen synthetic all-byte payload, never a fixture.
    if payload.resolve()!=BASE/'payload256.bin':raise ValueError('ONLY_FROZEN_OWNED_PAYLOAD')
    attempt=evidence/'attempt.json';used=write_new(attempt,dict(batch=BATCH,context=asdict(c),payloadBytes=256,payloadSha=PAYLOAD_SHA,state='CONSUMED_BEFORE_REMOTE_MUTATION'))
    records=[];metadata=0;producer=False;result=dict(batch=BATCH,status='NOT_ADMITTED',receiverExecution='NO_COMPLETE_RECEIVER_PROOF',priorRemoteOwnership='UNKNOWN_NOT_CLEARED',realMediaContentBytes=0,hostSubmittedBytesSnapshot=0,records=records)
    def call(name,argv,data=False):
        nonlocal metadata,producer,used
        if used+65536+65536>1048576:raise RuntimeError('TOTAL_LOG_BUDGET_BEFORE_CALL')
        if data:
            if producer:raise RuntimeError('ONE_PRODUCER_ALREADY_CONSUMED')
            producer=True;result['hostSubmittedBytesSnapshot']=None;r=transport.receive(argv,payload);result['hostSubmittedBytesSnapshot']=r['submittedBytes']
        else:
            if metadata>=20:raise RuntimeError('METADATA_COMMAND_BUDGET')
            metadata+=1;r=transport.command(argv)
        raw=(json.dumps(r,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
        if len(raw)>65536:raise RuntimeError('BOUNDED_ORIGINAL_RECORD_EXCEEDED')
        path=evidence/(f'{len(records):02d}-'+name+'.json');used+=write_new(path,r);records.append(dict(stage=name,file=path.name,originalStatus=r['status'],ownership=r['ownership']))
        if r['status']!='PROCESS_IO_COMPLETE_ONLY':raise RuntimeError('ORIGINAL_COMMAND_NOT_COMPLETE_'+name)
        if r['stderr']['bytes']:raise RuntimeError('ORIGINAL_STDERR_'+name)
        return ep.stdout_bytes(r)
    def remote(name,script):return call(name,run_as_argv(transport.adb,'HA1Q6WXR','shell',script))
    try:
        features=call('features',[str(transport.adb),'-s','HA1Q6WXR','features']).decode('ascii').strip().split(',')
        if 'shell_v2' not in features:raise RuntimeError('SHELL_V2_REQUIRED_NO_FALLBACK')
        ctx=parse_line(remote('context',preflight_script(c)).decode().strip(),'E4T2_CONTEXT',c)
        if ctx!={'uid':str(c.uid),'pwd':c.pwd}:raise RuntimeError('PREFLIGHT_ORIGINAL_UID_PWD')
        snapshot=remote('prior-uid-processes',process_script(c)).decode('utf-8','strict').splitlines()
        if not snapshot or not snapshot[0].startswith('E4T2_PS|'+c.nonce+'|self='):raise RuntimeError('PROCESS_SNAPSHOT_MISSING')
        self_pid=snapshot[0].rsplit('=',1)[1]
        if not self_pid.isdigit():raise RuntimeError('PROCESS_SNAPSHOT_SELF')
        for line in snapshot[1:]:
            fields=line.split(None,3)
            if len(fields)==4 and fields[0].isdigit() and fields[2]==str(c.uid) and fields[0]!=self_pid:
                args=fields[3]
                head=args.strip().split()[0].rsplit('/',1)[-1] if args.strip() else ''
                if any(token in args for token in ['E4AT1P','exec cat','tee files/e4_fixtures']) or head in {'cat','tee','sh','mksh'}:raise RuntimeError('POSSIBLE_PRIOR_RECEIVER_STOP_NO_KILL')
        result['priorProcessObservation']='One UID-only snapshot; no matching receiver observed; not all resources proven returned'
        result['historicalExactLstat']=remote('history-lstat-only',history_script(c)).decode('utf-8','strict')
        created=parse_line(remote('new-diagnostic-directory',mkdir_script(c)).decode().strip(),'E4T2_DIRECTORY',c)
        if created!={'path':c.directory}:raise RuntimeError('DIAGNOSTIC_DIRECTORY_NOT_PROVEN')
        raw=call('single-receiver',run_as_argv(transport.adb,'HA1Q6WXR','shell',receiver_script(c)),True)
        result['originalReceiver']=parse_receiver(raw,c)
        result['receiverExecution']='ORIGINAL_CONTEXT_AND_END_OBSERVED'
        result['independentFile']=parse_independent(remote('independent-diagnostic-stat-sha',independent_script(c)),c,PAYLOAD_SHA)
        result['status']='SYNTHETIC_DIAGNOSTIC_VERIFIED_NOT_A_MEDIA_FIXTURE'
    except Exception as error:result['firstFailure']=str(error)[:300]
    result.update(metadataCommands=metadata,producerAttempts=int(producer),syntheticPayloadBudgetBytes=256 if producer else 0,retainedLocalOwners=ep.retained_owners(),nextMediaOrProductAuthorized=False)
    final=(json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    if len(final)>65536 or used+len(final)>1048576:raise RuntimeError('FINAL_RECEIPT_BUDGET')
    write_new(evidence/'result.json',result);return result

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--execute',action='store_true');p.add_argument('--formal-batch');p.add_argument('--evidence-dir',type=Path);a=p.parse_args()
    if not a.execute:
        print(json.dumps(dict(mode='PLAN_ONLY',executionAuthorized=False,batch=BATCH,context=asdict(Context()),receiverArgv=run_as_argv('D:/Android/SDK/platform-tools/adb.exe','HA1Q6WXR','shell',receiver_script(Context())),maxPayloadBytes=256,metadataCommandsPlanned=6,metadataCommandsCap=20,adbCalls=0),ensure_ascii=False,indent=2));return
    if a.formal_batch!=BATCH or a.evidence_dir is None or not a.evidence_dir.is_absolute() or a.evidence_dir.resolve().is_relative_to(BASE):raise ValueError('SEPARATE_FORMAL_BATCH_AND_NEW_EXTERNAL_EVIDENCE_REQUIRED')
    result=run_diagnostic(ProcessTransport(),a.evidence_dir,authorized=True);print(json.dumps(result,ensure_ascii=False,indent=2))
    if ep.retained_owners():
        print('UNKNOWN_ORIGINAL_INTERPRETER_RETAINED_NO_RETRY',flush=True)
        while ep.retained_owners():time.sleep(1)
    if result['status']!='SYNTHETIC_DIAGNOSTIC_VERIFIED_NOT_A_MEDIA_FIXTURE':raise SystemExit(1)
if __name__=='__main__':main()
