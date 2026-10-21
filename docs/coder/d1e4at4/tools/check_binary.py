"""One finite T4 batch: native Windows CRT, production orchestration and local binary fake clients."""
from pathlib import Path
import ctypes
import hashlib
import json
import sys
from datetime import datetime,timezone
import exact_process as ep
from binary_commands import *
from diagnose_binary_once import run_diagnostic,plan,retained,BASE

ROOT=BASE.parents[2];CHECKS=[];RECORDS=[]
def check(v,name):
    CHECKS.append(dict(name=name,passed=bool(v)))
    if not v:raise AssertionError(name)
def reject(fn,name):
    try:fn()
    except (ValueError,UnicodeError):check(True,name)
    else:check(False,name)
def row(p):
    raw=p.read_bytes();return dict(path=p.relative_to(ROOT).as_posix(),bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest())

class LocalTransport:
    adb='LOCAL_MODEL_NO_ADB'
    def __init__(self,root,variant):self.root=root;self.variant=variant;self.originalArgs=[]
    def command(self,args):
        self.originalArgs.append(args)
        r=ep.collect([sys.executable,'-X','utf8','-B',str(BASE/'tools/local_binary_client.py'),str(self.root),self.variant,*args[1:]],ep.Limits(timeout=5,cleanup=2,stdout_cap=16384,stderr_cap=16384,retained_prefix=4096));RECORDS.append(r);return r

def crt_read(mode):
    crt=ctypes.CDLL('msvcrt');crt._open.argtypes=[ctypes.c_char_p,ctypes.c_int];crt._open.restype=ctypes.c_int
    crt._read.argtypes=[ctypes.c_int,ctypes.c_void_p,ctypes.c_uint];crt._read.restype=ctypes.c_int
    crt._close.argtypes=[ctypes.c_int];crt._close.restype=ctypes.c_int
    fd=crt._open(str(BASE/'payload256.bin').encode('mbcs'),mode)
    if fd<0:raise OSError('OWNED_CRT_OPEN')
    try:
        buffer=ctypes.create_string_buffer(256);n=crt._read(fd,buffer,256)
        if n<0:raise OSError('OWNED_CRT_READ')
        data=buffer.raw[:n]
    finally:closed=crt._close(fd)
    check(closed==0,'actual CRT original descriptor close mode '+str(mode))
    return dict(bytes=n,sha256=hashlib.sha256(data).hexdigest(),prefixHex=data[:32].hex(),closeReturn=closed)

def main():
    root=BASE/'evidence/local-main-001';destination=BASE/'evidence/local-check-results.json'
    if root.exists() or destination.exists() or (BASE/'evidence/binary-freeze.json').exists():raise ValueError('ONE_LOCAL_BATCH_ONLY')
    root.mkdir();began=datetime.now(timezone.utc).isoformat();inputs=[row(BASE/'tools'/n) for n in ['exact_process.py','command_response.py','binary_commands.py','diagnose_binary_once.py','local_binary_client.py','check_binary.py']]
    crt=dict(text=crt_read(0x4000),binary=crt_read(0x8000))
    check(crt['text']['bytes']==26 and crt['text']['sha256']==hashlib.sha256(bytes(range(26))).hexdigest(),'actual local CRT text mode stops before0x1A, not installedADB proof')
    check(crt['binary']['bytes']==256 and crt['binary']['sha256']==SHA,'actual local CRT binary mode preserves all256')
    scripts=[base_script(False),base_script(True),processes_script(),create_stage_script(),stage_access_script(True),stage_access_script(False),proof_script(True),copy_script('1,2,256,2000,8180,0'),proof_script(False)]
    syntax=root/'generated-syntax.sh';syntax.write_text('\n'.join('( '+s+'\n)' for s in scripts)+'\n',encoding='utf-8',newline='\n')
    r=ep.collect(['C:/Program Files/Git/usr/bin/sh.exe','-n',str(syntax)],ep.Limits(timeout=5,cleanup=2));RECORDS.append(r)
    check(r['status']=='PROCESS_IO_COMPLETE_ONLY' and ep.stdout_bytes(r)==b'' and r['stderr']['bytes']==0,'actual Git sh syntax-only check, no scripts executed')
    check(all('-n' in argv('MODEL',s) and '-T' in argv('MODEL',s) for s in scripts),'all command routes explicitly no host stdin and noPTY')
    check(all('/e4_diag_T3P_' not in s and 'e4_fixtures' not in s and 'chmod' not in s and 'mkdir -p' not in s for s in scripts),'no old residual/media path or permission widening/parent creation')
    check('head -c 256' in proof_script(True) and 'head -c 256' in proof_script(False) and 'head -c 256' in scripts[-2] and 'set -C' in scripts[-2],'both hashes and copy bounded256; internal noclobber')
    cases=[]
    for name,variant in [('success','normal'),('short-stage','short-stage'),('denied-base','denied'),('stage-conflict','conflict')]:
        scope=root/name;scope.mkdir();(scope/'.owned').write_bytes(b'T4_LOCAL_ONLY');old=scope/'old26.bin';old.write_bytes(bytes(range(26)))
        if variant=='conflict':(scope/'stage').mkdir();(scope/'stage/conflict.keep').write_bytes(b'KEEP')
        transport=LocalTransport(scope,variant);result=run_diagnostic(transport,scope/'receipts',authorized=True);cases.append(dict(case=name,result=result,plannedArgv=transport.originalArgs))
        check(result['metadataCommands']<=20 and result['pushAttempts']<=1 and result['copyAttempts']<=1,name+' finite calls')
        check(result['priorRemoteOwnership']=='UNKNOWN_NOT_CLEARED' and result['payloadStdinBytes']==0 and result['retainedLocalOwners']==0,name+' owners and stdin separation')
        check(old.read_bytes()==bytes(range(26)),name+' own old26 dummy unchanged')
        if name=='success':
            check(result['status']=='BINARY_PUSH_AND_LOCAL_COPY_VERIFIED_NOT_A_MEDIA_FIXTURE' and result['metadataCommands']==9 and result['pushAttempts']==result['copyAttempts']==1,'production successful push+copy+two independent proofs')
            check((scope/'stage/payload256.bin').read_bytes()==bytes(range(256)) and (scope/'internal/payload256.bin').read_bytes()==bytes(range(256)),'actual local binary source and internal files contain all256')
            check(result['stageProof']['sha']==result['internalProof']['sha']==SHA and result['hostSourcePrehashBytes']==256 and result['hostSourceCloseReturned'],'stage/internal proof and host source actualclose')
            check(any(a[3:6]==['push','-q','-Z'] and Path(a[6]).resolve()==BASE/'payload256.bin' and a[7]==SOURCE for a in transport.originalArgs),'production push passes fixed file as argv not stdin')
            try:run_diagnostic(transport,scope/'receipts',authorized=True)
            except FileExistsError:check(True,'same evidence attempt cannot be reused')
            else:check(False,'same evidence attempt cannot be reused')
        elif name=='short-stage':
            check(result['status']=='NOT_ADMITTED' and result['pushAttempts']==1 and result['copyAttempts']==0 and result['internalProof'] is None,'exit0 push with26 bytes refused before any copy')
            check((scope/'stage/payload256.bin').read_bytes()==bytes(range(26)) and not (scope/'internal').exists(),'failed partial stage retained no internal mutation')
        else:
            check(result['status']=='NOT_ADMITTED' and result['pushAttempts']==result['copyAttempts']==0 and result['hostSourcePrehashBytes']==0,'preflight access/conflict stops before host source or push')
            if variant=='conflict':check((scope/'stage/conflict.keep').read_bytes()==b'KEEP','conflicting stage preserved')
    proof=cases[0]['result']['internalProof'];valid='T4_INTERNAL_PROOF|'+NONCE+'|'+'|'.join(k+'='+v for k,v in proof.items())+'\r\n'
    check(parse_proof(valid.encode(),False)==proof,'strict internal proof acceptsCRLF')
    for changed in [valid.replace(SHA,'0'*64),valid.replace('uid=10221','uid=2000'),valid.replace(TARGET,TARGET+'.other'),valid.replace(proof['after'],'1,2,26,10221,8180,0')]:reject(lambda changed=changed:parse_proof(changed.encode(),False),'wrong independent context/hash/length refused')
    reject(lambda:parse_stamp('1,2,256,10221,8182,0'),'world writable file refused')
    reject(lambda:parse_stamp('1,2,256,2000,8180,0',True,True),'internal nonapp owner refused')
    reject(lambda:parse_copy(b'T4_COPY_BEGIN|'+NONCE.encode()+b'|uid=10221\n'),'BEGIN-only copy refused')
    reject(lambda:check_processes(('T4_PS|'+NONCE+'|self=123\nPID PPID UID ARGS\n 9 1 10221 tee old\n').encode()),'old receiver evidence stops no signal')
    check(plan()['executionAuthorized'] is False and plan()['payloadStdinBytes']==0,'default plan not execution')
    check(all(r['ownership']=='RETURNED' and r['originalExitObserved'] and r['submittedBytes']==0 for r in RECORDS) and retained()==0,'all actual local children returned original zero-byte stdin')
    result=dict(schema=1,status='PASS',scope='T4_FIXED_BINARY_ROUTE_LOCAL_ONLY',attempt='main-001',beganUtc=began,endedUtc=datetime.now(timezone.utc).isoformat(),assertions=len(CHECKS),checks=CHECKS,inputs=inputs,crt=crt,cases=cases,records=RECORDS,actualLocalProcessCalls=len(RECORDS),adbCalls=0,deviceRuns=0,realMediaStat=0,realMediaBytesRead=0,gradleRuns=0,retainedLocalOwners=retained(),historicalSuitesRepeated=False)
    with destination.open('x',encoding='utf-8') as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps(dict(status='PASS',assertions=len(CHECKS),localProcessCalls=len(RECORDS),adbCalls=0)))
if __name__=='__main__':main()
