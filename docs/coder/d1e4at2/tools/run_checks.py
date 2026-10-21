"""Explicit, single bounded LOCAL model batch; no installed ADB, media or device execution."""
from pathlib import Path
from datetime import datetime,timezone
import argparse
import hashlib
import json
import subprocess
import sys

BASE=Path(__file__).resolve().parents[1];ROOT=BASE.parents[2]
def row(p):
    data=p.read_bytes();return dict(path=p.relative_to(ROOT).as_posix(),bytes=len(data),sha256=hashlib.sha256(data).hexdigest())
def new(p,data):
    with p.open('x',encoding='utf-8') as f:json.dump(data,f,ensure_ascii=False,indent=2);f.write('\n')
def main():
    p=argparse.ArgumentParser();p.add_argument('--run',action='store_true');p.add_argument('--attempt',default='main-001');p.add_argument('--repair-reason');a=p.parse_args()
    if (BASE/'evidence/remote-freeze.json').exists():raise ValueError('FROZEN_READ_ONLY')
    if not a.attempt or any(c not in 'abcdefghijklmnopqrstuvwxyz0123456789-' for c in a.attempt):raise ValueError('ATTEMPT_ID')
    inputs=[row(BASE/'tools'/n) for n in ['exact_process.py','remote_command.py','diagnose_once.py','fake_aosp_client.py','run_local_checks.py','run_checks.py']]
    if not a.run:print(json.dumps(dict(mode='INSPECT',inputs=inputs,adbCalls=0)));return
    final=BASE/'evidence/local-check-results.json'
    if final.exists():raise ValueError('NO_DUPLICATE_PASSING_BATCH')
    gate=BASE/'evidence/check-main-reservation.json'
    if gate.exists():
        if not a.repair_reason:raise ValueError('NECESSARY_REPAIR_REASON')
    else:
        if a.repair_reason:raise ValueError('MAIN_REQUIRED')
        new(gate,dict(attempt=a.attempt,scope='T2_LOCAL_MODELS_ONLY'))
    attempt=BASE/'evidence/check-attempts'/a.attempt;attempt.mkdir(parents=True,exist_ok=False);argv=[sys.executable,'-X','utf8','-B',str(BASE/'tools/run_local_checks.py'),str(attempt/'owned')]
    began=datetime.now(timezone.utc).isoformat();log=attempt/'checks.log'
    with log.open('xb') as out:
        try:r=subprocess.run(argv,stdin=subprocess.DEVNULL,stdout=out,stderr=subprocess.STDOUT,cwd=ROOT,timeout=90,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0));code=r.returncode
        except subprocess.TimeoutExpired:code=-1
    result=dict(schema=1,scope='T2_LOCAL_AOSP_ARGV_REAL_GIT_SH',status='PASS' if code==0 else 'FAIL',attempt=a.attempt,kind='REPAIR' if a.repair_reason else 'MAIN',repairReason=a.repair_reason,inputs=inputs,argv=argv,exitCode=code,log=row(log),beganUtc=began,endedUtc=datetime.now(timezone.utc).isoformat(),adbCalls=0,deviceRuns=0,realMediaBytesRead=0,gradleRuns=0)
    if code==0:
        own=attempt/'owned/local-results.json';facts=json.loads(own.read_text('utf-8'));result.update(assertions=facts['assertions'],callRecords=facts['callRecords'],ownedResults=row(own));assert inputs==[row(ROOT/r['path']) for r in inputs]
        new(final,result)
    new(attempt/'attempt-result.json',result);print(json.dumps(result,ensure_ascii=False,indent=2))
    if code:sys.exit(1)
if __name__=='__main__':main()
