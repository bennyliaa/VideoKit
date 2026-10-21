"""One bounded targeted batch; each intentional UNKNOWN lives in its own child interpreter."""
from pathlib import Path
from datetime import datetime,timezone
import argparse
import hashlib
import json
import subprocess
import sys

BASE=Path(__file__).resolve().parents[1];ROOT=BASE.parents[2]
def row(path):
    raw=path.read_bytes();return dict(path=path.relative_to(ROOT).as_posix(),bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest())
def new(path,value):
    with path.open('x',encoding='utf-8') as file:json.dump(value,file,ensure_ascii=False,indent=2);file.write('\n')
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--run',action='store_true');parser.add_argument('--attempt',default='main-001');parser.add_argument('--repair-reason');a=parser.parse_args()
    if (BASE/'evidence/close-freeze.json').exists():raise ValueError('FROZEN_READ_ONLY')
    inputs=[row(BASE/'tools'/n) for n in ['exact_process.py','fixture_transfer.py','fake_child.py','close_case.py','run_close_checks.py']]
    if not a.run:print(json.dumps(dict(mode='INSPECT',inputs=inputs,adbCalls=0)));return
    final=BASE/'evidence/local-check-results.json'
    if final.exists():raise ValueError('NO_DUPLICATE_PASSING_BATCH')
    gate=BASE/'evidence/check-main-reservation.json'
    if gate.exists():
        if not a.repair_reason:raise ValueError('NECESSARY_REPAIR_REASON_REQUIRED')
    else:
        if a.repair_reason:raise ValueError('MAIN_MISSING')
        new(gate,dict(attempt=a.attempt,scope='T1_TARGETED_STDIN_CLOSE_ONLY'))
    attempt=BASE/'evidence/check-attempts'/a.attempt;attempt.mkdir(parents=True,exist_ok=False)
    cases=[];began=datetime.now(timezone.utc).isoformat()
    for name in ['success_transfer','no_process','no_stdin','throw_before','throw_after','blocked_return']:
        argv=[sys.executable,'-X','utf8','-B',str(BASE/'tools/close_case.py'),name,str(attempt/name)];log=attempt/(name+'.log')
        with log.open('xb') as out:
            try:p=subprocess.run(argv,cwd=ROOT,stdin=subprocess.DEVNULL,stdout=out,stderr=subprocess.STDOUT,timeout=12,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0));code=p.returncode
            except subprocess.TimeoutExpired:code=-1
        if log.stat().st_size>65536:raise ValueError('CASE_LOG_BOUND')
        record=dict(case=name,argv=argv,exitCode=code,log=row(log));cases.append(record)
        if code!=0:break
        case_result=json.loads((attempt/name/'case-result.json').read_text('utf-8'));record['result']=row(attempt/name/'case-result.json');record['assertions']=case_result['assertions'];record['actualChildLaunches']=case_result['actualChildLaunches'];record['retainedOwnersAtCaseExit']=case_result['retainedOwnersAtCaseExit']
    passed=len(cases)==6 and all(c['exitCode']==0 for c in cases)
    result=dict(schema=1,scope='T1_PRODUCTION_STDIN_CLOSE_AND_ALLOCATION_ONLY',status='PASS' if passed else 'FAIL',attempt=a.attempt,kind='REPAIR' if a.repair_reason else 'MAIN',repairReason=a.repair_reason,inputs=inputs,cases=cases,assertions=sum(c.get('assertions',0) for c in cases),beganUtc=began,endedUtc=datetime.now(timezone.utc).isoformat(),adbCalls=0,deviceRuns=0,gradleRuns=0,realMediaBytesRead=0,legacy72Repeated=False)
    new(attempt/'attempt-result.json',result)
    if passed:
        if inputs!=[row(ROOT/r['path']) for r in inputs]:raise ValueError('INPUTS_CHANGED_DURING_CHECK')
        new(final,result)
    print(json.dumps(result,ensure_ascii=False,indent=2))
    if not passed:sys.exit(1)
if __name__=='__main__':main()
