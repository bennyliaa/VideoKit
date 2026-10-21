"""One targeted batch, small owned bytes only: streaming/padding, real probe endpoints and pump outcomes."""
from pathlib import Path
import base64
import hashlib
import io
import json
import shlex
import sys
import time
from datetime import datetime,timezone
import exact_process as ep
from stream_base64 import EncodedSource,transfer_base64,encoded_length
from diagnose_ascii_once import BASE,run_diagnostic,LIMITS,plan
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
def newroot(root,name):
    p=root/name;p.mkdir();(p/'.owned').write_bytes(b'T5_LOCAL_ONLY');return p
def collect(args):
    r=ep.collect(args,ep.Limits(timeout=5,cleanup=2,stdout_cap=16384,stderr_cap=16384,retained_prefix=16384));RECORDS.append(r);return r
class ShortSink:
    def __init__(self):self.data=bytearray();self.calls=0
    def write(self,data):self.calls+=1;n=min(3,len(data));self.data.extend(data[:n]);return n
class LocalTransport:
    adb='LOCAL_MODEL_NO_ADB'
    def __init__(self,root,variant):self.root=root;self.variant=variant
    def mapped(self,args):return [sys.executable,'-X','utf8','-B',str(BASE/'tools/local_client.py'),str(self.root),self.variant,*args[1:]]
    def command(self,args):return collect(self.mapped(args))
    def transfer(self,args):
        r=transfer_base64(self.mapped(args),BASE/'payload256.bin',256,SHA,LIMITS);RECORDS.append(r);return r
def main():
    root=BASE/'evidence/local-main-001';destination=BASE/'evidence/local-check-results.json'
    if root.exists() or destination.exists() or (BASE/'evidence/ascii-freeze.json').exists():raise ValueError('ONE_LOCAL_BATCH')
    root.mkdir();began=datetime.now(timezone.utc).isoformat();inputs=[row(BASE/'tools'/n) for n in ['exact_process.py','command_response.py','stream_base64.py','private_commands.py','diagnose_ascii_once.py','local_client.py','close_unknown_case.py','check_ascii.py']]
    lengths=[]
    for n in [0,1,2,3,256,65535,65536,65537]:
        raw=bytes(i%256 for i in range(n));p=root/f'own-{n}.bin';p.write_bytes(raw);sha=hashlib.sha256(raw).hexdigest()
        source=EncodedSource(p,n,sha,time.monotonic()+10,chunk=7);source.open();sink=ShortSink();credits=bytearray()
        while True:
            data=source.read(17)
            if not data:break
            ep.write_all(sink,data,credits.extend)
        source.close();wire=bytes(sink.data)
        check(wire==base64.b64encode(raw) and len(wire)==encoded_length(n) and base64.b64decode(wire,validate=True)==raw,f'production streaming length/padding/3byte carry {n}')
        check(bytes(credits)==wire and (not wire or sink.calls>1) and b'\x1a' not in wire and b'\0' not in wire and b'\n' not in wire,f'production positive short writes and safe ASCII {n}')
        check(source.close_returned and source.peak_buffer<131072,f'bounded tracked buffers and actual sourceclose {n}')
        lengths.append(dict(rawBytes=n,encodedBytes=len(wire),sha=hashlib.sha256(wire).hexdigest(),peakTracked=source.peak_buffer))
    for n in [0,1,65537]:
        scope=newroot(root,'process-'+str(n));p=root/f'own-{n}.bin';r=transfer_base64([sys.executable,'-X','utf8','-B',str(BASE/'tools/local_client.py'),str(scope),'normal','decode-only'],p,n,hashlib.sha256(p.read_bytes()).hexdigest(),ep.Limits(timeout=5,cleanup=2));RECORDS.append(r);decoded=json.loads(ep.stdout_bytes(r))
        check(r['status']=='PROCESS_IO_COMPLETE_ONLY' and decoded['rawBytes']==n and decoded['encodedBytes']==encoded_length(n) and decoded['rawSha256']==r['rawSource']['expectedSha256'],f'actual process streaming decoded raw proof {n}')
        check(r['rawSource']['prehash']['rawBytes']==r['rawSource']['streamBytes']==n and r['rawSource']['prehash']['encodedBytes']==r['submittedBytes']==encoded_length(n),f'raw versus encoded accounting {n}')
    syntax=root/'syntax.sh';scripts=[context_script(),decoder_probe_script(),processes_script(),mkdir_script(),receiver_script(),proof_script()];syntax.write_text('\n'.join('( '+s+'\n)' for s in scripts)+'\n',encoding='utf-8',newline='\n')
    r=collect(['C:/Program Files/Git/usr/bin/sh.exe','-n',str(syntax)]);check(r['status']=='PROCESS_IO_COMPLETE_ONLY' and not r['stderr']['bytes'],'all generated scripts actual syntax check')
    probe_root=newroot(root,'real-probe');(probe_root/'files').mkdir()
    prologue='set -e; PATH=/usr/bin:/bin; cd '+shlex.quote(probe_root.as_posix())+'; id(){ printf 10221; }; pwd(){ printf '+shlex.quote(PWD)+'; }; '
    actual_probe=decoder_probe_script().replace('/system/bin/toybox ','')
    r=collect(['C:/Program Files/Git/usr/bin/sh.exe','-c',prologue+actual_probe]);proof=parse_probe(ep.stdout_bytes(r));check(proof['originalEndpointRc']=={'printf':'0','decoder':'0','od':'0'},'real local printf/base64/od probe all original rc and one00 byte, synthetic identity only')
    failing=actual_probe.replace('base64 -d',"sh -c 'exit 7'")
    r=collect(['C:/Program Files/Git/usr/bin/sh.exe','-c',prologue+failing]);out=ep.stdout_bytes(r)
    check(r['originalExitCode']==0 and b'stage=decoder|rc=7' in out,'actual hidden middle decoder failure recorded despite pipeline last exit0')
    reject(lambda:parse_probe(out),'probe refuses middle failure without pipefail assumption')
    cases=[]
    for name in ['normal','decoder-nonzero','short-exit0','wrong-sha']:
        scope=newroot(root,name);old=scope/'own-old26.bin';old.write_bytes(bytes(range(26)));t=LocalTransport(scope,name);result=run_diagnostic(t,scope/'receipts',authorized=True);cases.append(dict(case=name,result=result))
        check(result['metadataCommands']<=20 and result['producerAttempts']==1 and result['priorRemoteOwnership']=='UNKNOWN_NOT_CLEARED',name+' one attempt and old ownership retained')
        check(old.read_bytes()==bytes(range(26)) and result['rawSource']['prehash']['rawBytes']==result['rawSource']['streamBytes']==256 and result['encoding']['actualSubmittedBytes']==344,name+' old own dummy unchanged and raw/encoded facts')
        if name=='normal':
            check(result['status']=='ASCII_STREAM_DECODE_AND_RAW_SHA_VERIFIED_NOT_A_MEDIA_FIXTURE' and result['metadataCommands']==6 and (scope/'private/payload256.bin').read_bytes()==bytes(range(256)),'production full finite diagnostic with actual binary decode/file and independent hash')
            try:run_diagnostic(t,scope/'receipts',authorized=True)
            except FileExistsError:check(True,'same attempt directory refused')
            else:check(False,'same attempt directory refused')
        else:
            check(result['status']=='NOT_ADMITTED' and result['independentProof'] is None and (scope/'private/payload256.bin').exists(),name+' refused and failed artifact retained')
            if name=='decoder-nonzero':check(result['receiverObservation']['DECODE']=={'rc':'7'} and result['receiverProof'] is None,'original decoder nonzero observed separately from host input completion')
    scope=newroot(root,'close-unknown');r=collect([sys.executable,'-X','utf8','-B',str(BASE/'tools/close_unknown_case.py'),str(scope)]);unknown=json.loads(ep.stdout_bytes(r));check(unknown['retainedUntilInterpreterEnd']==1 and unknown['nextIoRefused'] and unknown['originalRecord']['ownership']=='UNKNOWN_RETAINED','isolated actual sourceclose throw retains original Job and refuses next IO, never credits OS exit cleanup')
    check(all(r['ownership']=='RETURNED' and r['originalExitObserved'] for r in RECORDS) and ep.retained_owners()==0,'top-level tested original process owners returned; isolated UNKNOWN remains separately recorded')
    check(plan()['encodedBytes']==344 and not plan()['executionAuthorized'] and all('/storage/' not in s and 'e4_diag_T3' not in s for s in scripts),'new plan private-only no residual or external paths')
    value=dict(schema=1,status='PASS',scope='T5_STREAMING_ASCII_LOCAL_ONLY',attempt='main-001',beganUtc=began,endedUtc=datetime.now(timezone.utc).isoformat(),assertions=len(CHECKS),checks=CHECKS,inputs=inputs,lengths=lengths,cases=cases,isolatedCloseUnknown=unknown,records=RECORDS,topLevelProcessCalls=len(RECORDS),additionalIsolatedInnerProcessCalls=1,adbCalls=0,deviceRuns=0,realMediaBytesRead=0,realMediaStat=0,gradleRuns=0,topLevelRetainedOwners=0,historicalSuitesRepeated=False)
    with destination.open('x',encoding='utf-8') as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps(dict(status='PASS',assertions=len(CHECKS),topLevelProcessCalls=len(RECORDS),isolatedUnknownOwners=1,adbCalls=0)))
if __name__=='__main__':main()
