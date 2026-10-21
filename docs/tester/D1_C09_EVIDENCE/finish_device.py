import argparse,hashlib,io,json,pathlib,re,subprocess,tarfile
B=pathlib.Path(__file__).resolve().parent;p=argparse.ArgumentParser();p.add_argument('device',choices=['phone','tablet']);a=p.parse_args();O=B/a.device
pre=json.loads((O/'preflight.json').read_text());ADB=r'D:\Android\SDK\platform-tools\adb.exe';serial=pre['serial']
def run(parts,timeout=60):
 r=subprocess.run([ADB,'-s',serial]+parts,capture_output=True,timeout=timeout);assert r.returncode==0,(r.stdout+r.stderr).decode(errors='replace');return r.stdout
snapshot=run(['exec-out','run-as','com.videokit.app','tar','-cf','-','cache'],120);(O/'cache-after-c09.tar').write_bytes(snapshot)
def entries(data):
 with tarfile.open(fileobj=io.BytesIO(data)) as t:return {m.name:dict(bytes=m.size,sha256=hashlib.sha256(t.extractfile(m).read()).hexdigest()) for m in t.getmembers() if m.isfile()}
before=entries((O/'cache-before-c09.tar').read_bytes());after=entries(snapshot)
old={k:v for k,v in before.items() if 'd1_c06_capture_' in k or 'd1_c07_capture_' in k}
assert all(after[k]==v for k,v in old.items()),'OLD_CAPTURE_CHANGED'
new={k:v for k,v in after.items() if k.startswith('cache/d1_c09_')};size=sum(v['bytes'] for v in new.values());count=sum(k.endswith(('.task','.journal')) for k in new)
assert size<=8388608 and count<=32
(O/'output-budget-final.json').write_text(json.dumps(dict(newBytes=size,terminalTaskRecords=count,limitBytes=8388608,limitTaskRecords=32,oldCaptureEntries=len(old),oldCaptureUnchanged=True,files=new,cacheBackupSha256=hashlib.sha256(snapshot).hexdigest()),indent=2),encoding='utf-8')
hashes=run(['shell','run-as','com.videokit.app','sha256sum','files/d1_c09_fixtures/basic.mp4','files/d1_c09_fixtures/subtitle.avi'])
(O/'source-after-hashes.txt').write_bytes(hashes)
assert b'720957c94b3665ff97bcc2f59ad5407c5ca54f566b59865723be9eecc0a6a1f9' in hashes
assert b'3f0bf3e9fa6f24130a546fee5be98ba43274959cdc0df82a2ee74306ad4ef52f' in hashes
path=run(['shell','pm','path','com.videokit.app']).decode().strip().splitlines()[0].removeprefix('package:').strip();dest=O/'installed-c09-app.apk'
if not dest.exists():run(['pull',path,str(dest)])
assert hashlib.sha256(dest.read_bytes()).hexdigest()=='55e5bea436b2195517af72c991c9f36ede75e6da390c450bb65ae9ad2106a9f0'
(O/'installed-c09-package.txt').write_bytes(run(['shell','dumpsys','package','com.videokit.app']))
status=run(['shell','ps','-A','-o','PID,UID,NAME']).decode(errors='replace');(O/'processes-at-end.txt').write_text('\n'.join(s for s in status.splitlines() if 'com.videokit.' in s),encoding='utf-8')
logbytes=sum(f.stat().st_size for f in O.rglob('*') if f.is_file() and f.suffix in ['.log','.txt']);assert logbytes<=33554432
(O/'log-budget-final.json').write_text(json.dumps(dict(bytes=logbytes,limitBytes=33554432)),encoding='utf-8')
print(a.device+' backups, source hashes, package identity and budgets verified; no force-stop or state changes',flush=True)
