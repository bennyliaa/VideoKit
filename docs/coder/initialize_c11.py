from pathlib import Path
import hashlib,re,shutil
root=Path(__file__).resolve().parents[2];old=root/'docs/coder/d1c10';base=root/'docs/coder/d1c11'
assert not base.exists()
assert hashlib.sha256((old/'evidence/freeze-summary.json').read_bytes()).hexdigest()=='4b728a9b5694e096e0374cd8d2e5bb77ce53afb173e512d0308d8f9ca4e0deec'
def convert(text):
 hashes=set(re.findall(r'[a-f0-9]{64}',text));slots={v:'HASH_SLOT_'+str(i)+'_END' for i,v in enumerate(hashes)}
 for h,v in slots.items():text=text.replace(h,v)
 text=text.replace('c10','c11').replace('C10','C11').replace('vk_c11_','vk_c09_')
 for h,v in slots.items():text=text.replace(v,h)
 return text
for folder in ['src','android','device','native','labels','notice-assets','tools']:
 for p in (old/folder).rglob('*'):
  if p.is_file() and '__pycache__' not in p.parts:
   q=base/convert(p.relative_to(old).as_posix());q.parent.mkdir(parents=True,exist_ok=True)
   if folder=='notice-assets' or p.name=='quota.c':shutil.copyfile(p,q)
   else:q.write_text(convert(p.read_text(encoding='utf-8')),encoding='utf-8')
for name in ['build.gradle.kts','gradle.lockfile','src/main/AndroidManifest.xml']:
 p=old/'worker_app'/name;q=base/'worker_app'/name;q.parent.mkdir(parents=True,exist_ok=True);q.write_text(convert(p.read_text(encoding='utf-8')),encoding='utf-8')
for name in ['app/build.gradle.kts','app/src/debug/AndroidManifest.xml','settings.gradle.kts']:
 p=root/name;p.write_text(convert(p.read_text(encoding='utf-8')),encoding='utf-8')
for folder in ['outputs','classes','evidence','native-libs/arm64-v8a','worker-native-libs/arm64-v8a','artifacts/D1-20261016-C11','upstream']:(base/folder).mkdir(parents=True,exist_ok=True)
for name in ['ffmpeg-8.0.3.tar.xz','ffmpeg-8.0.3.tar.xz.asc','ffmpeg-devel.asc']:shutil.copyfile(old/'upstream'/name,base/'upstream'/name)
for p in (old/'native-libs/arm64-v8a').glob('*.so'):
 if p.name not in ['libvideokit_cpu.so','libvideokit_d1_lease.so']:shutil.copyfile(p,base/'native-libs/arm64-v8a'/p.name)
shutil.copytree(old/'evidence/inherited-c09',base/'evidence/inherited-c09')
shutil.copyfile(old/'evidence/inherited-native-admission.json',base/'evidence/inherited-native-admission.json')
for p in ['docs/milestones/D1_C11_CODER_REQUIREMENTS_V1.0.md','docs/tester/D1_C10_TEST_REPORT_V1.0.md']:
 shutil.copyfile(root/p,base/'evidence'/('input-'+Path(p).name))
print('C11 initialized; C01-C10 untouched')
