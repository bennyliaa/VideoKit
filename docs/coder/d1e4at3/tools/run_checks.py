"""Single in-process offline batch; preserve attempt and failure evidence, never retry."""
from pathlib import Path
from contextlib import redirect_stdout,redirect_stderr
from datetime import datetime,timezone
import hashlib
import io
import json
import runpy
import sys
import traceback

BASE=Path(__file__).resolve().parents[1]
def main():
    path=BASE/'evidence/attempt-main-001.json'
    if path.exists() or (BASE/'evidence/features-freeze.json').exists():raise ValueError('ATTEMPT_ALREADY_CONSUMED')
    with path.open('x',encoding='utf-8') as f:json.dump(dict(attempt='main-001',consumed=True,beganUtc=datetime.now(timezone.utc).isoformat(),scope='ONLY_OWN_OFFLINE_PARSER'),f)
    sys.path.insert(0,str(BASE/'tools'));log=io.StringIO();status='FAIL'
    with redirect_stdout(log),redirect_stderr(log):
        try:runpy.run_path(str(BASE/'tools/check_features.py'),run_name='__main__');status='PASS'
        except BaseException:traceback.print_exc()
    raw=log.getvalue().encode('utf-8');raw=raw[:16384]
    with (BASE/'evidence/checks.log').open('xb') as f:f.write(raw)
    result=dict(status=status,attempt='main-001',endedUtc=datetime.now(timezone.utc).isoformat(),logBytes=len(raw),logSha256=hashlib.sha256(raw).hexdigest(),processStarts=0,adbCalls=0)
    with (BASE/'evidence/attempt-result.json').open('x',encoding='utf-8') as f:json.dump(result,f,ensure_ascii=False,indent=2)
    print(json.dumps(result));print(raw.decode('utf-8'))
    if status!='PASS':raise SystemExit(1)
if __name__=='__main__':main()
