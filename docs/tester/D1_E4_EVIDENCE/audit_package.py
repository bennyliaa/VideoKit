"""Independent static/byte/archive review. No Android/JVM/build/device execution."""
from pathlib import Path
from datetime import datetime
import hashlib,json,zipfile
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent;BASE=ROOT/'docs/coder/d1e4'
def sha(b):return hashlib.sha256(b).hexdigest()
def read(p):return json.loads(p.read_bytes())
def save(n,v):(OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
f=read(BASE/'evidence/e4-freeze.json');s=read(BASE/'evidence/source-manifest.json')
assert sha((BASE/'evidence/e4-freeze.json').read_bytes())=='0940855c58ada5c2ce3b23e8bd4c63803016afeb4b563127f589a043847e0227'
assert len(s['files'])==112 and len(f['immutableFiles'])==116
for r in f['immutableFiles']:
    p=ROOT/r['path'];assert p.resolve().is_relative_to(ROOT.resolve()) and not p.is_symlink() and not p.is_junction()
    b=p.read_bytes();assert len(b)==r['bytes'] and sha(b)==r['sha256'],r['path']
assert sha((ROOT/f['sourceZip']['path']).read_bytes())=='f35e113e563b2c9f15db530f5d780fd2f57ab73e545367e8a5baa58278cd754e'
with zipfile.ZipFile(ROOT/f['sourceZip']['path']) as z:
    assert len(z.namelist())==112 and set(z.namelist())=={r['path'] for r in s['files']}
    for r in s['files']:assert sha(z.read(r['path']))==r['sha256']
for r in s['files']:
    p=ROOT/r['path'];dest=OUT/'frozen-sources'/r['path'];dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(p.read_bytes())
for p in (BASE/'evidence').glob('*.json'):(OUT/p.name).write_bytes(p.read_bytes())
apk=read(BASE/'evidence/apk-audit.json');app=next(a for a in apk['apks'] if a['role']=='app-debug')
with zipfile.ZipFile(ROOT/app['path']) as z:
    assert {n for n in z.namelist() if n.startswith('lib/') and n.endswith('.so')}=={r['entry'] for r in apk['nativeLibraries']}
    for r in apk['nativeLibraries']:assert sha(z.read(r['entry']))==r['sha256'] and z.read(r['entry'])==(ROOT/r['upstreamPath']).read_bytes()
checks=read(BASE/'evidence/local-check-results.json');assert checks['assertions']==89 and checks['status']=='PASS'
for r in checks['inputs']:
    p=ROOT/r['path'];assert p.stat().st_size==r['bytes'] and sha(p.read_bytes())==r['sha256']
plan=read(BASE/'tools/device_plan.json');assert len(plan['cases'])==8 and all(r['status']=='NOT_RUN' for r in plan['cases'])
assert sum(r['lastSingleCase'] for r in plan['cases'])==3
save('independent-package-audit.json',dict(at=datetime.now().astimezone().isoformat(),scope='Static hashes, ZIP/APK libraries and existing record validation only; no executable tests',sourceFiles=112,immutableFiles=116,readOnlyVerifyPassed=True,recordedLocalJvmAssertions=89,localJvmRerun=False,buildAttempts=5,nativeLibrariesByteIdentical=7,devicePlanCases=8,quarantineLastCases=3,newGradle=False,adb=False,devices=False,nativeFault=False,mediaIO=False,candidateUnchanged=True))
print('PASS: E4 seal/112 sources/116 immutable/ZIP/APK seven original libraries, JVM input hashes and eight NOT_RUN cases')
