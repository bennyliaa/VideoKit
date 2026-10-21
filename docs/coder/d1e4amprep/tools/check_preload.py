"""One bounded new batch: two synthetic files above64KiB, real mv-n, persisted evidence gates."""
from pathlib import Path
from dataclasses import asdict,replace
from copy import deepcopy
import hashlib
import json
import os
import shlex
import sys
from datetime import datetime,timezone
import exact_process as ep
from command_response import complete_stdout
import preload_once as app
from preload_once import BASE,run_preload,Store,verify_ready,canonical,retained,load_manifest
from media_commands import *
from local_transport import LocalTransport

ROOT=BASE.parents[2];CHECKS=[];RECORDS=[]
def check(v,name):
    CHECKS.append(dict(name=name,passed=bool(v)))
    if not v:raise AssertionError(name)
def row(path):
    raw=path.read_bytes();return dict(path=path.relative_to(ROOT).as_posix(),bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest())
def reject(fn,name):
    try:fn()
    except (ValueError,RuntimeError):check(True,name)
    else:check(False,name)
def scope(root,name):
    d=root/name;d.mkdir();(d/'.owned').write_bytes(b'MPREP_OWN');(d/FIXTURES).mkdir(parents=True)
    fixed,_=load_manifest();out=[]
    for s,n in zip(fixed,[65537,70001]):
        raw=bytes(i%256 for i in range(n));source=d/('source-'+s.alias+'.bin');source.write_bytes(raw)
        out.append(replace(s,source=str(source),bytes=n,sha256=hashlib.sha256(raw).hexdigest(),encodedBytes=4*((n+2)//3),transferSeconds=5,hashSeconds=5))
    (d/'specs.json').write_bytes(canonical([asdict(s) for s in out]));(d/FIXTURES/'basic.mp4.E4AN_PREP01_81407_a790f44f.keep').write_bytes(b'OWN_ARCHIVE')
    return d,tuple(out)
def collect(args):
    r=ep.collect(args,ep.Limits(timeout=5,cleanup=2,stdout_cap=65536,stderr_cap=16384,retained_prefix=65536));RECORDS.append(r);return r
def main():
    root=BASE/'evidence/local-main-001';dest=BASE/'evidence/local-check-results.json'
    if root.exists() or dest.exists() or (BASE/'evidence/mprep-freeze.json').exists():raise ValueError('ONE_TARGETED_BATCH')
    root.mkdir();began=datetime.now(timezone.utc).isoformat();inputs=[row(BASE/'tools'/n) for n in ['exact_process.py','command_response.py','stream_base64.py','t6_protocol.py','media_commands.py','preload_once.py','local_client.py','local_transport.py','close_unknown_case.py','check_preload.py']]
    fixed,_=load_manifest();check([s.encodedBytes for s in fixed]==[465472,981939544] and max(s.encodedBytes for s in fixed)<1073741824,'fixed real source metadata and unchanged1GiB encoded cap, no source query')
    cases=[];successful=None;successful_specs=None;successful_store=None
    for name,variant in [('success','normal'),('short','short'),('wrong-sha','wrong-sha'),('conflict','normal'),('ready-fsync-failure','normal')]:
        d,specs=scope(root,name);t=LocalTransport(d,variant)
        if name=='conflict':(d/specs[0].final).write_bytes(b'CONFLICT_KEEP')
        original_fsync=os.fsync
        if name=='ready-fsync-failure':
            def fsync(fd):
                if any(s.pending and str(s.pending[-1].name).endswith('basic.mp4-ready.json') for s in app.STORES):raise OSError('CONTROLLED_READY_FSYNC_FAILURE')
                return original_fsync(fd)
            os.fsync=fsync
        try:r=run_preload(t,d/'receipts',authorized=True,specs=specs)
        finally:os.fsync=original_fsync
        RECORDS.extend(t.records);cases.append(dict(case=name,result=r,scope=str(d)))
        check(r['metadataCommands']<=20 and all(n<=1 for n in r['producerAttempts'].values()) and r['priorRemoteOwnership']=='UNKNOWN_NOT_CLEARED',name+' finite one-pass budgets and old unknown')
        check((d/FIXTURES/'basic.mp4.E4AN_PREP01_81407_a790f44f.keep').read_bytes()==b'OWN_ARCHIVE',name+' exact own archived dummy untouched')
        check(sum(pth.stat().st_size for pth in (d/'receipts').iterdir())<8388608 and r['retainedLocalOwners']==0,name+' actual logs bounded and original owners returned')
        if name=='success':
            check(r['status']=='TWO_FIXTURES_PREPARED_NOT_PRODUCT_PASS' and r['producerAttempts']=={'basic.mp4':1,'subtitle.avi':1} and r['metadataCommands']==13,'one batch fully prepares both files conditional on MP4')
            for s in specs:
                data=(d/s.final).read_bytes();proof=r['files'][s.alias]['evidence'];check(len(data)==s.bytes and hashlib.sha256(data).hexdigest()==s.sha256 and not (d/s.temp).exists() and proof['tempProof']['before']==proof['finalProof']['before'],s.alias+' actual binary decoded and renamed devinode stable')
            check(r['mp4Dependency']['verifiedContent'] and r['mp4Dependency']['verifiedOriginalStages']==4 and r['receiptMetadataReads']==15,'AVI requires durable readback and four original evidence records, not arbitrarySHA')
            successful=r;successful_specs=specs;successful_store=app.STORES[-1]
            try:run_preload(t,d/'receipts',authorized=True,specs=specs)
            except FileExistsError:check(True,'same evidence attempt refused no retry')
            else:check(False,'same evidence attempt refused no retry')
        else:
            check(r['status']=='NOT_ADMITTED' and r['producerAttempts']['subtitle.avi']==0 and r['mp4Dependency'] is None,name+' immediately blocks AVI')
            if name=='short':check((d/specs[0].temp).stat().st_size==26 and not (d/specs[0].final).exists(),'short exit0 refuses before publication and retains partial')
            if name=='wrong-sha':check((d/specs[0].temp).stat().st_size==specs[0].bytes and not (d/specs[0].final).exists(),'wrong independentSHA refuses before publication')
            if name=='conflict':check((d/specs[0].final).read_bytes()==b'CONFLICT_KEEP' and r['producerAttempts']['basic.mp4']==0,'existing fixture never overwritten or guessed ready')
            if name=='ready-fsync-failure':check((d/specs[0].final).exists() and (d/'receipts/basic.mp4-ready.json').exists() and r['logReservedBytesBeforeResult']>0 and 'CONTROLLED_READY_FSYNC_FAILURE' in r['firstFailure'],'partial durable-ready failure preserves published MP4 and charge, stops AVI')
    # A self-consistent nonempty receipt hash still cannot substitute forged semantic evidence.
    s=successful_specs[0];goodrow=successful['files'][s.alias]['ready'];body=successful_store.read(goodrow);forged=deepcopy(body);forged['evidence']['encoding']['actualSubmittedSha256']='a'*64
    badrow=successful_store.write('forged-ready-own-test.json',forged)
    reject(lambda:verify_ready(successful_store,badrow,forged,s),'even valid nonempty hash and matching receipt body require actual original proofs')
    gap=deepcopy(body);gap['originals'].pop('final');gaprow=successful_store.write('missing-stage-own-test.json',gap)
    reject(lambda:verify_ready(successful_store,gaprow,gap,s),'missing original final publication record refuses')
    # Real filesystem rename and a race inserted after the target-absence guard.
    renames=[]
    for name in ['rename-real','rename-race']:
        d,specs=scope(root,name);s=specs[0];(d/TEMP_DIR).mkdir();(d/s.temp).write_bytes(bytes(i%256 for i in range(s.bytes)))
        pro='set -e; PATH=/usr/bin:/bin; cd '+shlex.quote(d.as_posix())+'; id(){ command printf 10221; }; pwd(){ command printf '+shlex.quote(p.PWD)+'; }; '
        r=collect(['C:/Program Files/Git/usr/bin/sh.exe','-c',pro+f'stat -c {p.STAT} -- {s.temp}']);st=complete_stdout(r).decode().strip();script=publish_script(s,st).replace('/system/bin/toybox ','')
        if name=='rename-race':pro+='mv(){ command printf KEEP > '+s.final+'; command mv "$@"; }; '
        r=collect(['C:/Program Files/Git/usr/bin/sh.exe','-c',pro+script]);raw=bytes.fromhex(r['stdout']['prefixHex'])
        if name=='rename-real':check(r['originalExitCode']==0 and parse_publish(raw,s,st)['stamp']==st and not (d/s.temp).exists(),'real generated mv-n preserves actual devinode across directories')
        else:check(r['originalExitCode']!=0 and b'mvRc=0' in raw and b'T6_PUBLISHED|' not in raw and (d/s.temp).exists() and (d/s.final).read_bytes()==b'KEEP','real mv-n exit0 skipped conflict refuses, no overwrite or false publication')
        renames.append(dict(case=name,expectedStamp=st,recordIndex=len(RECORDS)-1))
    d,specs=scope(root,'syntax');sample=specs[0];syntax=d/'all.sh';scripts=[admission_script(specs),p.processes_script(),p.mkdir_script(),p.decoder_probe_script(),file_guard_script(sample),receiver_script(sample),proof_script(sample),publish_script(sample,'1,2,65537,10221,8180,0'),proof_script(sample,True)];syntax.write_text('\n'.join('( '+x+'\n)' for x in scripts)+'\n',encoding='utf-8',newline='\n')
    r=collect(['C:/Program Files/Git/usr/bin/sh.exe','-n',str(syntax)]);check(r['status']=='PROCESS_IO_COMPLETE_ONLY' and not r['stderr']['bytes'],'all new generated scripts real syntax check')
    d,specs=scope(root,'close-unknown');r=collect([sys.executable,'-X','utf8','-B',str(BASE/'tools/close_unknown_case.py'),str(d)]);unknown=json.loads(complete_stdout(r))
    check(unknown['retainedUntilInterpreterEnd']==1 and unknown['nextIoRefused'] and unknown['osExitNotCredited'] and unknown['result']['producerAttempts']=={'basic.mp4':1,'subtitle.avi':0},'original sourceclose UNKNOWN blocks AVI retains charge and original Job, no OS exit credit')
    reject(lambda:parse_space(b'T6_FILE_GUARD|'+p.NONCE.encode()+b'|x=x\nFilesystem 1K-blocks Used Available Use% Mounted on\nx 1 0 1 1% /data\n','FILE_GUARD',{'x':'x'},736803758),'insufficient free space refuses without deleting historical files')
    check(all(r['ownership']=='RETURNED' and r['originalExitObserved'] for r in RECORDS) and retained()==0,'top-level original local actors returned; isolated inner UNKNOWN kept separate')
    out=dict(schema=1,status='PASS',scope='MPREP_FIXED_TWO_FILE_LOCAL_ONLY',attempt='main-001',beganUtc=began,endedUtc=datetime.now(timezone.utc).isoformat(),assertions=len(CHECKS),checks=CHECKS,inputs=inputs,cases=cases,realRenames=renames,isolatedUnknown=unknown,records=RECORDS,topLevelProcessCalls=len(RECORDS),isolatedInnerProcessCalls=len(unknown['originals']),topLevelRetainedOwners=0,isolatedUnknownOwnersAtCaseEnd=1,osExitCredited=False,adbCalls=0,deviceRuns=0,realMediaStat=0,realMediaBytesRead=0,gradleRuns=0,historicalSuitesRepeated=False)
    with dest.open('x',encoding='utf-8') as f:json.dump(out,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps(dict(status='PASS',assertions=len(CHECKS),topLevelProcessCalls=len(RECORDS),isolatedInnerProcessCalls=len(unknown['originals']),adbCalls=0)))
if __name__=='__main__':main()
