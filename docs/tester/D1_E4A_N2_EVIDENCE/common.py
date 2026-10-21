"""N2 bounded original process ownership; only declared metadata and exact method calls."""
from pathlib import Path
import sys,hashlib,json,os,time,io,shlex
E=Path(__file__).resolve().parent;ROOT=E.parents[2];B=ROOT/'docs/coder/d1e4amprep/tools'
assert hashlib.sha256((B/'exact_process.py').read_bytes()).hexdigest()=='f43cbf6d78611b0c441b0b438322e484a8513587ee93de4c32fdee67b84f988d'
sys.path.insert(0,str(B));import exact_process as ep
ADB='D:/Android/SDK/platform-tools/adb.exe';SERIAL='HA1Q6WXR';BATCH='D1-E4A-N2-TABLET-20261017';BUDGET='730a73e1-50e1-4198-a515-047104f00e31'
PENDING_FILES=[]
def new(name,obj):
    assert not PENDING_FILES
    raw=(json.dumps(obj,ensure_ascii=False,indent=2)+'\n').encode()
    assert len(raw)<=20*1048576 and sum(p.stat().st_size for p in E.iterdir() if p.is_file())+len(raw)<33554432
    f=(E/name).open('xb');PENDING_FILES.append(f)
    try:ep.write_all(f,raw,lambda data:None);f.flush();os.fsync(f.fileno())
    finally:f.close();PENDING_FILES.remove(f)
def call(args,name,seconds=15,cap=131072):
    assert not PENDING_FILES and not ep.retained_owners() and 0<seconds<=90 and 0<cap<=4194304
    argv=[ADB,'-s',SERIAL,*args]
    # Same locked original Job/_run; caller-authorized N2 metadata/log limits exceed old collect's 64KiB prefix.
    # No pump source/payload or device logic changed; preserve every original close/thread/wait predicate.
    job=ep.Job(argv,0,ep.EMPTY_SHA,ep.Limits(timeout=seconds,cleanup=2,stdout_cap=cap,stderr_cap=131072,retained_prefix=cap));ep._reserve(job);job.source_sha=ep.EMPTY_SHA
    r=ep._run(job,io.BytesIO());new(name+'.json',r)
    if ep.retained_owners():
        print('UNKNOWN_ORIGINAL_INTERPRETER_RETAINED',flush=True)
        while ep.retained_owners():time.sleep(1)
    assert r['ownership']=='RETURNED' and r['originalExitObserved'] and not r['creationUnknown']
    for stream in ('stdout','stderr'):
        s=r[stream];raw=bytes.fromhex(s['prefixHex']);assert not s['prefixTruncated'] and len(raw)==s['bytes'] and hashlib.sha256(raw).hexdigest()==s['sha256'] and s['closeReturned'] and s['error'] is None
        (E/(name+'-'+stream+'.txt')).write_bytes(raw)
    return r,bytes.fromhex(r['stdout']['prefixHex']).decode('utf-8','strict')
def shell(script,name,app=True,seconds=15):
    return call(['shell','-n','-T','-e','none',*(['run-as','com.videokit.app'] if app else []),'sh','-c',shlex.quote(script)],name,seconds)
def hold():
    while ep.retained_owners() or PENDING_FILES:print('ORIGINAL_OWNERS_RETAINED',flush=True);time.sleep(1)
