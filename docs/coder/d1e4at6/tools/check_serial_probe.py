"""One finite real-shell probe batch; no stress/retry, device or historical suites."""
from pathlib import Path
import hashlib
import json
import shlex
import sys
from datetime import datetime,timezone
import exact_process as ep
from stream_base64 import transfer_base64
from diagnose_ascii_once import BASE,run_diagnostic,LIMITS,observed_stdout,plan
from private_commands import *
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
def collect(args):
    r=ep.collect(args,ep.Limits(timeout=5,cleanup=2,stdout_cap=16384,stderr_cap=16384,retained_prefix=16384));RECORDS.append(r);return r
class LocalTransport:
    adb='LOCAL_MODEL_NO_ADB'
    def __init__(self,root):self.root=root
    def mapped(self,args):return [sys.executable,'-X','utf8','-B',str(BASE/'tools/local_client.py'),str(self.root),'normal',*args[1:]]
    def command(self,args):return collect(self.mapped(args))
    def transfer(self,args):
        r=transfer_base64(self.mapped(args),BASE/'payload256.bin',256,SHA,LIMITS);RECORDS.append(r);return r
def main():
    root=BASE/'evidence/local-main-001';destination=BASE/'evidence/local-check-results.json'
    if root.exists() or destination.exists() or (BASE/'evidence/serial-freeze.json').exists():raise ValueError('ONE_NEW_BATCH')
    root.mkdir();began=datetime.now(timezone.utc).isoformat();inputs=[row(BASE/'tools'/n) for n in ['exact_process.py','command_response.py','stream_base64.py','private_commands.py','diagnose_ascii_once.py','local_client.py','check_serial_probe.py']]
    script=decoder_probe_script();mapped=script.replace('/system/bin/toybox ','')
    check('exec 3' not in script and '>&3' not in script and ' | ' not in script and '&' not in script.replace('&&',''),'structural no concurrent receipt writers, pipeline or FD3')
    check(script.index('if printf AA==')<script.index('base64 -d')<script.index('od -An')<script.index('T6_PROBE_RC'),'all receipt printing follows synchronous operations')
    cases=[];normal=None
    overrides={
        'normal':'',
        'printf-nonzero':'printf(){ if test "$1" = AA==; then return 7; fi; command printf "$@"; }; ',
        'decoder-nonzero':'base64(){ return 8; }; ',
        'od-nonzero':'od(){ return 9; }; ',
        'truncated-file':'printf(){ if test "$1" = AA==; then command printf A; else command printf "$@"; fi; }; ',
        'wrong-hex':'base64(){ command printf "\\001"; }; ',
    }
    for name,override in overrides.items():
        scope=root/name;scope.mkdir();(scope/DIRECTORY).mkdir(parents=True)
        prologue='set -e; PATH=/usr/bin:/bin; cd '+shlex.quote(scope.as_posix())+'; id(){ command printf 10221; }; pwd(){ command printf '+shlex.quote(PWD)+'; }; '
        r=collect(['C:/Program Files/Git/usr/bin/sh.exe','-c',prologue+override+mapped]);raw=observed_stdout(r)
        states=[]
        for p in [scope/PROBE_ASCII,scope/PROBE_RAW]:
            if p.exists():states.append(dict(name=p.name,bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
        check(len(states)<=2 and sum(s['bytes'] for s in states)<=4096,name+' bounded retained state files')
        check(r['ownership']=='RETURNED' and r['originalExitObserved'],name+' original local shell and pipes returned')
        lines=raw.decode('ascii').splitlines();check(len(lines)==4 and [parse_line(line,'PROBE_RC')['stage'] for line in lines[:3]]==['printf','decoder','od'],name+' parent serial complete stage order')
        if name=='normal':
            normal=raw;proof=parse_probe(raw);check(proof['originalEndpointRc']=={'printf':'0','decoder':'0','od':'0'} and r['originalExitCode']==0,'actual shell original all endpoints0 and hex00')
            check((scope/PROBE_ASCII).read_bytes()==b'AA==' and (scope/PROBE_RAW).read_bytes()==b'\0','actual two retained state files4B plus1B')
        else:
            reject(lambda raw=raw:parse_probe(raw),name+' strict refusal')
            if name in ['printf-nonzero','decoder-nonzero','od-nonzero']:
                stage,code={'printf-nonzero':('printf','7'),'decoder-nonzero':('decoder','8'),'od-nonzero':('od','9')}[name]
                check(any(parse_line(line,'PROBE_RC')=={'stage':stage,'rc':code} for line in lines[:3]) and r['originalExitCode']!=0,name+' exact original failure retained')
        cases.append(dict(case=name,recordIndex=len(RECORDS)-1,stdoutSha256=hashlib.sha256(raw).hexdigest(),states=states))
    for raw,name in [(b'\n'.join(normal.splitlines()[1:]),'missing status'),(normal[:-8],'truncated final status'),(normal.replace(b'stage=decoder|rc=0',b'stage=decoder|rc='),'truncated endpoint rc'),(normal+normal.splitlines()[0]+b'\n','duplicate status'),(b'\n'.join([normal.splitlines()[1],normal.splitlines()[0],*normal.splitlines()[2:]]),'out of order')]:reject(lambda raw=raw:parse_probe(raw),'strict '+name+' refuses no reconstruction')
    old=(BASE/'reference/T5P-interleaved-stdout.txt').read_bytes()
    check(len(old)==286 and hashlib.sha256(old).hexdigest()=='f15424ea4759dc3e299308d50f8da8ebf3a48d0e79169ee65525122a2ad7a8d3','exact original interleaved286B identity')
    reject(lambda:parse_probe(old),'original real interleaved bytes refused')
    rewritten=old.replace(b'T5',b'T6');reject(lambda:parse_probe(rewritten),'interleaved structure refused even under new nonce/prefix, no repair')
    check(parse_probe(normal.replace(b'\r\n',b'\n').replace(b'\n',b'\r\n'))['originalEndpointRc']=={'printf':'0','decoder':'0','od':'0'},'strict serial parser supports CRLF')
    syntax=root/'syntax.sh';syntax.write_text('\n'.join('( '+s+'\n)' for s in [context_script(),processes_script(),mkdir_script(),decoder_probe_script(),receiver_script(),proof_script()])+'\n',encoding='utf-8',newline='\n')
    r=collect(['C:/Program Files/Git/usr/bin/sh.exe','-n',str(syntax)]);check(r['status']=='PROCESS_IO_COMPLETE_ONLY' and not r['stderr']['bytes'],'six production scripts actual syntax check')
    scope=root/'integration';scope.mkdir();(scope/'.owned').write_bytes(b'T6_LOCAL_ONLY');t=LocalTransport(scope);result=run_diagnostic(t,scope/'receipts',authorized=True)
    check(result['status']=='ASCII_STREAM_DECODE_AND_RAW_SHA_VERIFIED_NOT_A_MEDIA_FIXTURE' and result['metadataCommands']==6 and result['producerAttempts']==1,'production new directory then serial probe then one producer and independentSHA')
    check((scope/'private/payload256.bin').read_bytes()==bytes(range(256)) and (scope/'private/probe.ascii').read_bytes()==b'AA==' and (scope/'private/probe.raw').read_bytes()==b'\0','actual local model256B and two5B states')
    check(result['rawSource']['streamBytes']==256 and result['encoding']['actualSubmittedBytes']==344 and result['independentProof']['sha']==SHA and result['priorRemoteOwnership']=='UNKNOWN_NOT_CLEARED','unchanged streaming raw encoded and independent proof semantics')
    check(all(r['ownership']=='RETURNED' and r['originalExitObserved'] for r in RECORDS) and ep.retained_owners()==0,'all actual local original owners returned')
    check(plan()['probeStateFilesPlanned']==2 and plan()['probeStateBytesPlanned']==5 and plan()['probeStateFileCap']==4 and plan()['probeStateBytesCap']==4096 and not plan()['executionAuthorized'],'exact new state plan only')
    value=dict(schema=1,status='PASS',scope='T6_SERIAL_PARENT_PROBE_LOCAL_ONLY',attempt='main-001',beganUtc=began,endedUtc=datetime.now(timezone.utc).isoformat(),assertions=len(CHECKS),checks=CHECKS,inputs=inputs,realShellCases=cases,integration=result,records=RECORDS,actualLocalProcessCalls=len(RECORDS),adbCalls=0,deviceRuns=0,realMediaStat=0,realMediaBytesRead=0,gradleRuns=0,retainedLocalOwners=0,historicalSuitesRepeated=False,stressAttempts=0)
    with destination.open('x',encoding='utf-8') as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps(dict(status='PASS',assertions=len(CHECKS),actualLocalProcessCalls=len(RECORDS),adbCalls=0)))
if __name__=='__main__':main()
