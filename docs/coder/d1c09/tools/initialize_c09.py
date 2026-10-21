from pathlib import Path
import re,sys
root=Path(sys.argv[1]).resolve();old=root/'docs/coder/d1c08';base=root/'docs/coder/d1c09'
def convert(text):
 hashes=set(re.findall(r'[a-f0-9]{64}',text));slots={h:'PRESERVED_HASH_'+str(i)+'_END' for i,h in enumerate(hashes)}
 for h,v in slots.items():text=text.replace(h,v)
 text=text.replace('20261005-C08','20261016-C09').replace('c08','c09').replace('C08','C09')
 for h,v in slots.items():text=text.replace(v,h)
 return text
for folder in ['src','android','device','native','labels']:
 for p in (old/folder).rglob('*'):
  if p.is_file():
   q=base/convert(p.relative_to(old).as_posix());q.parent.mkdir(parents=True,exist_ok=True);q.write_text(convert(p.read_text(encoding='utf-8')),encoding='utf-8')
for name in ['build.gradle.kts','gradle.lockfile','src/main/AndroidManifest.xml']:
 p=old/'worker_app'/name;q=base/'worker_app'/name;q.parent.mkdir(parents=True,exist_ok=True);q.write_text(convert(p.read_text(encoding='utf-8')),encoding='utf-8')
for name in ['app/build.gradle.kts','app/src/debug/AndroidManifest.xml','settings.gradle.kts']:
 p=root/name;p.write_text(convert(p.read_text(encoding='utf-8')),encoding='utf-8')
for name in ['build_native.py','integrity.py','C08ExitRecordSelfCheck.java','C08FormatGuardSelfCheck.java','review_tool_vulnerabilities.py','transfer_fixtures.py','transfer_selfcheck.py']:
 p=old/'tools'/name;(base/'tools'/convert(name)).write_text(convert(p.read_text(encoding='utf-8')),encoding='utf-8')
for folder in ['outputs','classes','artifacts/D1-20261016-C09','native-libs/arm64-v8a']:(base/folder).mkdir(parents=True,exist_ok=True)
print('C09 independent working source initialized once; C01-C08 untouched')
