from pathlib import Path
import hashlib,re,sys,shutil
root=Path(sys.argv[1]).resolve();old=root/'docs/coder/d1c09';base=root/'docs/coder/d1c10'
assert hashlib.sha256((old/'evidence/freeze-summary.json').read_bytes()).hexdigest()=='cdc48afed4f10e38fca5ad5efaf3fb4602947acc2166caa1f08d255bb89ce4fa'
def convert(text):
 hashes=set(re.findall(r'[a-f0-9]{64}',text));slots={v:'HASH_SLOT_'+str(i)+'_END' for i,v in enumerate(hashes)}
 for h,v in slots.items():text=text.replace(h,v)
 text=text.replace('c09','c10').replace('C09','C10').replace('vk_c10_','vk_c09_')
 for h,v in slots.items():text=text.replace(v,h)
 return text
for folder in ['src','android','device','native','labels','notice-assets']:
 for p in (old/folder).rglob('*'):
  if p.is_file():
   q=base/convert(p.relative_to(old).as_posix());q.parent.mkdir(parents=True,exist_ok=True)
   if folder in ['notice-assets'] or p.name=='quota.c':shutil.copyfile(p,q)
   else:q.write_text(convert(p.read_text(encoding='utf-8')),encoding='utf-8')
for name in ['build.gradle.kts','gradle.lockfile','src/main/AndroidManifest.xml']:
 p=old/'worker_app'/name;q=base/'worker_app'/name;q.parent.mkdir(parents=True,exist_ok=True);q.write_text(convert(p.read_text(encoding='utf-8')),encoding='utf-8')
for name in ['app/build.gradle.kts','app/src/debug/AndroidManifest.xml','settings.gradle.kts']:
 p=root/name;p.write_text(convert(p.read_text(encoding='utf-8')),encoding='utf-8')
for folder in ['outputs','classes','evidence','native-libs/arm64-v8a','worker-native-libs/arm64-v8a','artifacts/D1-20261016-C10','upstream']:(base/folder).mkdir(parents=True,exist_ok=True)
(base/'tools').mkdir(exist_ok=True)
for name in ['build_native.py','run_local_checks.py','C09CpuSelfCheck.java','C09CpuSourceSelfCheck.java','C09ExitRecordSelfCheck.java','transfer_fixtures.py','transfer_selfcheck.py','audit_apks.py','freeze_c09.py','verify_c09.py','integrity.py']:
 (base/'tools'/convert(name)).write_text(convert((old/'tools'/name).read_text(encoding='utf-8')),encoding='utf-8')
for name in ['ffmpeg-8.0.3.tar.xz','ffmpeg-8.0.3.tar.xz.asc','ffmpeg-devel.asc']:shutil.copyfile(old/'upstream'/name,base/'upstream'/name)
for p in (old/'native-libs/arm64-v8a').glob('*.so'):
 if p.name not in ['libvideokit_cpu.so','libvideokit_d1_lease.so']:shutil.copyfile(p,base/'native-libs/arm64-v8a'/p.name)
print('Initialized C10 independent sources; inherited FFmpeg/quota binary inputs unchanged; C01-C09 untouched')
