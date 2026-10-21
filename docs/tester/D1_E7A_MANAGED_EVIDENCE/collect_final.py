"""One finite read-only lifecycle/log collection after the sole finish ACK; no controls or retries."""
from pathlib import Path
import subprocess,time,json,hashlib,re
E=Path(__file__).resolve().parent;ADB='D:/Android/SDK/platform-tools/adb.exe'
def save(n,v):
    with (E/n).open('x',encoding='utf-8') as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')
clock=json.loads((E/'launch-result.json').read_bytes())['clock']
calls=[('05-final-lifecycle',['shell','dumpsys activity instrumentation; ps -A -o PID,UID,NAME']),('06-managed-logcat',['logcat','-d','-b','main','-b','system','-b','crash','-v','threadtime,epoch,uid','-T',clock+'.000','E7A_READ_ONLY:I','ActivityManager:I','AndroidRuntime:E','*:S'])]
for name,args in calls:
    argv=[ADB,'-s','HA1Q6WXR',*args];save(name+'-intent.json',dict(argv=argv,began=time.time(),budgetSeconds=15));began=time.monotonic()
    with (E/(name+'-stdout.txt')).open('xb') as out:p=subprocess.run(argv,stdin=subprocess.DEVNULL,stdout=out,stderr=subprocess.STDOUT)
    elapsed=time.monotonic()-began;b=(E/(name+'-stdout.txt')).read_bytes()
    save(name+'-receipt.json',dict(argv=argv,exitCode=p.returncode,elapsedSeconds=elapsed,clientReturned=True,receivedBytes=len(b),savedBytes=len(b),sha256=hashlib.sha256(b).hexdigest(),overflow=False))
    assert p.returncode==0 and elapsed<=15 and sum(x.stat().st_size for x in E.glob('*-stdout.txt'))<=1048576
    print(json.dumps(dict(call=name,exitCode=p.returncode,elapsedSeconds=elapsed,bytes=len(b))),flush=True)
intents=[p for p in E.iterdir() if re.fullmatch(r'control-\d{2}-intent\.json',p.name)]
assert len(intents)==2 and sorted(json.loads(p.read_bytes())['command'] for p in intents)==['ACK_FINISH','STATUS']
save('control-budget-final.json',dict(handle='9f19bfb5-60e0-4bcc-9666-852409cfe3b4',maxRequests=6,used=2,remaining=4,requests=[json.loads(p.read_bytes()) for p in sorted(intents)],ackRequests=1,stopDependencyRequests=0,rule='Only exact control-NN-intent rows represent wire requests. Response capture intents and pre-ADB wrapper failure are not additional requests.',noBudgetReset=True))
