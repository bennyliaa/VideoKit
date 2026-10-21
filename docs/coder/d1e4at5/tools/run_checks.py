"""One bounded T5 local batch. No repeat, preserve original source identities, log and status."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib
import json
import subprocess
import sys

BASE=Path(__file__).resolve().parents[1];ROOT=BASE.parents[2]
def main():
    marker=BASE/'evidence/check-attempt.json'
    if marker.exists() or (BASE/'evidence/ascii-freeze.json').exists():raise ValueError('ATTEMPT_ALREADY_CONSUMED')
    inputs=[]
    for p in sorted((BASE/'tools').glob('*.py')):
        raw=p.read_bytes();inputs.append(dict(path=p.relative_to(ROOT).as_posix(),bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest()))
    attempt=dict(attempt='main-001',inputs=inputs,beganUtc=datetime.now(timezone.utc).isoformat(),consumed=True)
    with marker.open('x',encoding='utf-8') as f:json.dump(attempt,f,ensure_ascii=False,indent=2)
    with (BASE/'evidence/checks.log').open('xb') as log:
        try:r=subprocess.run([sys.executable,'-X','utf8','-B',str(BASE/'tools/check_ascii.py')],stdout=log,stderr=subprocess.STDOUT,timeout=60);code=r.returncode
        except subprocess.TimeoutExpired:code=None
    raw=(BASE/'evidence/checks.log').read_bytes();out=dict(status='PASS' if code==0 else 'FAIL',attempt='main-001',exitCode=code,endedUtc=datetime.now(timezone.utc).isoformat(),logBytes=len(raw),logSha256=hashlib.sha256(raw).hexdigest(),adbCalls=0,deviceRuns=0)
    with (BASE/'evidence/check-attempt-result.json').open('x',encoding='utf-8') as f:json.dump(out,f,ensure_ascii=False,indent=2)
    print(json.dumps(out));print(raw[:8192].decode('utf-8'))
    if code!=0:raise SystemExit(1)
if __name__=='__main__':main()
