"""Outer caller saves the existing return-channel witness after G closes its log."""
import argparse, hashlib, json, subprocess, sys, time
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--run',action='store_true');args=parser.parse_args()
    if not args.run:print('INSPECT_ONLY: explicit --run required');return 0
    started=time.time_ns()
    process=subprocess.Popen([sys.executable,'-B',str(BASE/'src/controller.py'),'--synthetic-selfcheck'],stdout=subprocess.PIPE,stderr=subprocess.PIPE,creationflags=subprocess.CREATE_NO_WINDOW)
    try:
        stdout,stderr=process.communicate(timeout=200)
    except subprocess.TimeoutExpired:
        pending={'scope':'OUTER_CALLER_RETURN_CHANNEL','status':'PENDING','pid':process.pid,'started':started,'exited':False,'rule':'STOP_WAITING_NO_NATIVE_COMPLETION_OR_EXIT_INFERRED'}
        path=BASE/'evidence'/('pending-'+str(started)+'.json');path.write_text(json.dumps(pending,indent=2)+'\n',encoding='utf-8');print(json.dumps(pending));return 2
    result=subprocess.CompletedProcess(process.args,process.returncode,stdout,stderr)
    if len(result.stdout)>8192 or len(result.stderr)>65536:raise RuntimeError('CALLER_RECEIPT_LIMIT')
    stdout=result.stdout.decode();stderr=result.stderr.decode();witness=json.loads(stdout) if stdout.strip() else None
    evidence={'scope':'OUTER_CALLER_RETURN_CHANNEL','exitCode':result.returncode,'started':started,'ended':time.time_ns(),'witness':witness,'stderr':stderr}
    path=BASE/'evidence'/('selfcheck-'+str(started)+'.json');path.write_text(json.dumps(evidence,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'evidence':str(path),'exitCode':result.returncode,'witness':witness,'stderr':stderr},separators=(',',':')))
    return result.returncode
if __name__=='__main__':sys.exit(main())
