import argparse,json,pathlib,re,shutil,subprocess
B=pathlib.Path(__file__).resolve().parent;p=argparse.ArgumentParser();p.add_argument('device',choices=['phone','tablet']);p.add_argument('--archive-disabled-attempt',action='store_true');a=p.parse_args();O=B/a.device
pre=json.loads((O/'preflight.json').read_text());serial=pre['serial'];ADB=r'D:\Android\SDK\platform-tools\adb.exe'
def run(args):
 r=subprocess.run([ADB,'-s',serial]+args,capture_output=True,timeout=30);assert r.returncode==0,(r.stdout+r.stderr).decode(errors='replace');return r.stdout.decode(errors='replace')
before=run(['shell','dumpsys','package','com.videokit.app']);match=re.search(r'User 0:.*?enabled=(\d+)',before);assert match
state=int(match.group(1));(O/'app-enabled-before.txt').write_text(before,encoding='utf-8')
assert state in [0,1,2,3],state
if a.archive_disabled_attempt:
 assert state in [2,3]
 records=json.loads((O/'results.json').read_text());cpu=[r for r in records if r['group']=='cpu'];assert len(cpu)==17
 archive=O/'environment-disabled-attempt';archive.mkdir(exist_ok=False)
 (archive/'results.json').write_text(json.dumps(cpu,ensure_ascii=False,indent=2),encoding='utf-8')
 for r in cpu:
  for f in O.glob(r['method']+'*'):
   if f.is_file():shutil.copy2(f,archive/f.name)
 for name in ['cpu-system-bind-diagnostic.log','processes-after-cpu.txt']:
  if (O/name).exists():shutil.copy2(O/name,archive/name)
 kept=[r for r in records if r['group']!='cpu' or (r['method']=='cpuUnknownAndEmptyLengthRejectWithActualClose' and r['result']=='PASS')]
 (O/'results.json').write_text(json.dumps(kept,ensure_ascii=False,indent=2),encoding='utf-8')
if state in [2,3]:
 output=run(['shell','pm','enable','--user','0','com.videokit.app']);print(output.strip())
else:output='Already enabled/default; no mutation'
after=run(['shell','dumpsys','package','com.videokit.app']);(O/'app-enabled-after.txt').write_text(after,encoding='utf-8')
assert re.search(r'User 0:.*?enabled=([01])(?:\s|$)',after)
(O/'app-state-adjustment.json').write_text(json.dumps(dict(originalEnabledState=state,temporaryEnabled=state in [2,3],reason='Authorized same-package test requires services enabled; restore prior state at batch end',output=output),ensure_ascii=False,indent=2),encoding='utf-8')
