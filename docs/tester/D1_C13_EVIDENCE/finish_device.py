"""Read-only final C13 evidence; bounded transfer, no device cleanup or state changes."""
import argparse,hashlib,io,json,pathlib,re,subprocess,tarfile,threading
B=pathlib.Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('device',choices=['phone','tablet']);a=p.parse_args();O=B/a.device
pre=json.loads((O/'preflight.json').read_text());ADB=r'D:\Android\SDK\platform-tools\adb.exe';serial=pre['serial']
def run(parts,limit=1048576,timeout=60):
 proc=subprocess.Popen([ADB,'-s',serial]+parts,stdout=subprocess.PIPE,stderr=subprocess.PIPE);out=[];err=[];fail=[]
 def read(pipe,target,cap):
  size=0
  try:
   while True:
    chunk=pipe.read1(min(65536,cap-size+1))
    if not chunk:break
    size+=len(chunk)
    if size>cap:raise RuntimeError('READ_BUDGET_EXCEEDED')
    target.append(chunk)
  except Exception as e:fail.append(str(e));proc.kill()
 ts=[threading.Thread(target=read,args=(proc.stdout,out,limit),daemon=True),threading.Thread(target=read,args=(proc.stderr,err,16384),daemon=True)]
 for t in ts:t.start()
 try:code=proc.wait(timeout=timeout)
 except subprocess.TimeoutExpired:proc.kill();raise RuntimeError('ADB_CLIENT_TIMEOUT_NOT_REMOTE_STOP')
 for t in ts:t.join(3)
 assert not fail and not any(t.is_alive() for t in ts) and code==0,(fail,b''.join(err).decode(errors='replace'))
 return b''.join(out)
def entries(data):
 with tarfile.open(fileobj=io.BytesIO(data)) as t:
  return {m.name:dict(bytes=m.size,sha256=hashlib.sha256(t.extractfile(m).read()).hexdigest()) for m in t.getmembers() if m.isfile()}
dest=O/'cache-after-c13.tar';assert not dest.exists(),'NO_OVERWRITE'
snapshot=run(['exec-out','run-as','com.videokit.app','tar','-cf','-','cache'],134217728,120);dest.write_bytes(snapshot)
before=entries((O/'cache-before-c13.tar').read_bytes());after=entries(snapshot)
old={k:v for k,v in before.items() if 'd1_c06_capture_' in k or 'd1_c07_capture_' in k}
assert all(after.get(k)==v for k,v in old.items()),'OLD_CAPTURE_CHANGED'
new={k:v for k,v in after.items() if k.startswith('cache/d1_c13_')};size=sum(v['bytes'] for v in new.values());count=sum(k.endswith(('.task','.journal')) for k in new)
assert size<=8388608 and count<=32
pipeline={k:v for k,v in new.items() if k.startswith('cache/d1_c13_pipeline_outputs/')}
pipe_bytes=sum(v['bytes'] for v in pipeline.values());pipe_records=sum(k.endswith(('.task','.journal')) for k in pipeline)
assert pipe_bytes<=4194304 and pipe_records<=24
assert all(v['bytes']<=2097152 for k,v in pipeline.items() if k.endswith('.mp4'))
(O/'pipeline-budget-final.json').write_text(json.dumps(dict(bytes=pipe_bytes,records=pipe_records,limitBytes=4194304,limitRecords=24,maxSingleOutput=2097152,files=pipeline),indent=2),encoding='utf-8')
(O/'output-budget-final.json').write_text(json.dumps(dict(newBytes=size,terminalTaskRecords=count,limitBytes=8388608,limitTaskRecords=32,oldCaptureEntries=len(old),oldCaptureUnchanged=True,files=new,cacheBackupSha256=hashlib.sha256(snapshot).hexdigest()),indent=2),encoding='utf-8')
if a.device=='tablet':
 hashes=run(['shell','run-as','com.videokit.app','sha256sum','files/d1_c13_fixtures/basic.mp4','files/d1_c13_fixtures/subtitle.avi'],4096,180)
 (O/'source-after-hashes.txt').write_bytes(hashes)
 for expected in ['720957c94b3665ff97bcc2f59ad5407c5ca54f566b59865723be9eecc0a6a1f9','3f0bf3e9fa6f24130a546fee5be98ba43274959cdc0df82a2ee74306ad4ef52f']:assert expected.encode() in hashes
 package='com.videokit.worker.spike';path=run(['shell','pm','path',package],4096).decode().strip().removeprefix('package:');worker=O/'installed-c13-worker.apk';assert not worker.exists()
 assert run(['pull',path,str(worker)],4096) is not None
 assert hashlib.sha256(worker.read_bytes()).hexdigest()=='3dde3ed9ab312a791886c889b50abbc13c08ced1eaf313323e5f3a13e784c217'
(O/'package-at-end.txt').write_bytes(run(['shell','dumpsys','package','com.videokit.app']))
status=run(['shell','ps','-A','-o','PID,UID,NAME'],262144).decode(errors='replace');lines=[s for s in status.splitlines() if 'com.videokit.' in s]
(O/'processes-at-end.txt').write_text('\n'.join(lines),encoding='utf-8')
assert not any(':d1_cpu_worker' in s or ':d1_media_worker' in s for s in lines),'ACTIVE_WORKER_AT_END'
logbytes=sum(f.stat().st_size for f in O.rglob('*') if f.is_file() and f.suffix in ['.log','.txt']);assert logbytes<=33554432
(O/'log-budget-final.json').write_text(json.dumps(dict(bytes=logbytes,limitBytes=33554432,boundedDuringCapture=True)),encoding='utf-8')
print(a.device+' final backups, captures, sources, identity and budgets verified; no cleanup or state change',flush=True)
