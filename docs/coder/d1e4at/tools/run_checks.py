"""Default inspect; --run runs only the finite OWNED fake-process batch. Never invokes ADB."""
from pathlib import Path
import argparse
from datetime import datetime,timezone
import hashlib
import json
import subprocess
import sys

BASE=Path(__file__).resolve().parents[1]
ROOT=BASE.parents[2]
def row(path):
    data=path.read_bytes();return dict(path=path.relative_to(ROOT).as_posix(),bytes=len(data),sha256=hashlib.sha256(data).hexdigest())
def new(path,value):
    with path.open('x',encoding='utf-8') as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n')
def main():
    p=argparse.ArgumentParser();p.add_argument('--run',action='store_true');p.add_argument('--attempt',default='main-001');p.add_argument('--repair-reason');a=p.parse_args()
    if (BASE/'evidence/transfer-freeze.json').exists():raise ValueError('FROZEN_READ_ONLY')
    if not a.attempt or any(c not in 'abcdefghijklmnopqrstuvwxyz0123456789-' for c in a.attempt):raise ValueError('ATTEMPT_ID')
    inputs=[row(BASE/'tools'/name) for name in ('exact_process.py','fixture_transfer.py','fake_child.py','selfcheck.py','run_checks.py')]
    if not a.run:print(json.dumps(dict(mode='INSPECT',inputs=inputs,adbCalls=0,sourceMediaOpened=False)));return
    final=BASE/'evidence/local-check-results.json'
    if final.exists():
        prior=json.loads(final.read_text(encoding='utf-8'))
        if not a.repair_reason or prior['inputs']==inputs:raise ValueError('NO_DUPLICATE_PASSING_BATCH')
        preserved=BASE/('evidence/local-check-results-before-'+a.attempt+'.json')
        if preserved.exists():raise ValueError('PRESERVED_MAIN_ALREADY_EXISTS')
        final.rename(preserved)
    gate=BASE/'evidence/check-main-reservation.json'
    if gate.exists():
        if not a.repair_reason:raise ValueError('PRESERVED_MAIN_REQUIRES_NECESSARY_REPAIR_REASON')
    else:
        if a.repair_reason:raise ValueError('REPAIR_REQUIRES_MAIN')
        new(gate,dict(attempt=a.attempt,scope='LOCAL_OWNED_FAKE_PROCESSES_ONLY'))
    attempt=BASE/'evidence/check-attempts'/a.attempt;attempt.mkdir(parents=True,exist_ok=False)
    command=[sys.executable,'-X','utf8','-B',str(BASE/'tools/selfcheck.py'),str(attempt/'owned')]
    began=datetime.now(timezone.utc).isoformat();log=attempt/'selfcheck.log'
    with log.open('xb') as out:
        try:completed=subprocess.run(command,cwd=ROOT,stdin=subprocess.DEVNULL,stdout=out,stderr=subprocess.STDOUT,timeout=90,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0));code=completed.returncode
        except subprocess.TimeoutExpired:code=-1
    if log.stat().st_size>1048576:raise ValueError('SELF_CHECK_LOG_BUDGET')
    result=dict(schema=1,status='PASS' if code==0 else 'FAIL',attempt=a.attempt,kind='REPAIR' if a.repair_reason else 'MAIN',repairReason=a.repair_reason,inputs=inputs,argv=command,exitCode=code,log=row(log),beganUtc=began,endedUtc=datetime.now(timezone.utc).isoformat(),adbCalls=0,gradleRuns=0,deviceRuns=0,realMediaBytesRead=0)
    if code==0:
        facts=json.loads((attempt/'owned/selfcheck-results.json').read_text('utf-8'));result.update(assertions=facts['assertions'],fakeProcessCommands=facts['commands'],ownedResults=row(attempt/'owned/selfcheck-results.json'))
        if facts['status']!='PASS' or facts['retainedProcessOwners']!=0 or facts['commands']>128:raise ValueError('FINITE_BATCH_FACTS')
        if inputs!=[row(ROOT/r['path']) for r in inputs]:raise ValueError('SOURCE_CHANGED_DURING_BATCH')
        new(final,result)
    new(attempt/'attempt-result.json',result);print(json.dumps(result,ensure_ascii=False,indent=2))
    if code:sys.exit(1)
if __name__=='__main__':main()
