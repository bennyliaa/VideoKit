from pathlib import Path
import hashlib,re,shutil
root=Path(__file__).resolve().parents[2];old=root/'docs/coder/d1c11';base=root/'docs/coder/d1c12'
assert not base.exists()
assert hashlib.sha256((old/'evidence/freeze-summary.json').read_bytes()).hexdigest()=='bfe33794c0ac606fef0e5fb498672e3a9e33b8390b0e21fe153eb86877306138'
def convert(text):
 hashes=set(re.findall(r'[a-f0-9]{64}',text));slots={h:'HASH_SLOT_'+str(i)+'_END' for i,h in enumerate(hashes)}
 for h,v in slots.items():text=text.replace(h,v)
 text=text.replace('c11','c12').replace('C11','C12').replace('vk_c12_','vk_c09_')
 for h,v in slots.items():text=text.replace(v,h)
 return text
for folder in ['src','android','device','native','labels','notice-assets','tools']:
 for p in (old/folder).rglob('*'):
  if not p.is_file() or '__pycache__' in p.parts:continue
  q=base/convert(p.relative_to(old).as_posix());q.parent.mkdir(parents=True,exist_ok=True)
  if folder=='notice-assets' or p.name=='quota.c':shutil.copyfile(p,q)
  else:q.write_text(convert(p.read_text(encoding='utf-8')),encoding='utf-8')
for name in ['build.gradle.kts','gradle.lockfile','src/main/AndroidManifest.xml']:
 p=old/'worker_app'/name;q=base/'worker_app'/name;q.parent.mkdir(parents=True,exist_ok=True);q.write_text(convert(p.read_text(encoding='utf-8')),encoding='utf-8')
for name in ['app/build.gradle.kts','app/src/debug/AndroidManifest.xml','settings.gradle.kts']:
 p=root/name;p.write_text(convert(p.read_text(encoding='utf-8')),encoding='utf-8')
for folder in ['outputs','classes','evidence','native-libs/arm64-v8a','worker-native-libs/arm64-v8a','artifacts/D1-20261016-C12','upstream']:(base/folder).mkdir(parents=True,exist_ok=True)
for p in (old/'upstream').iterdir():
 if p.is_file():shutil.copyfile(p,base/'upstream'/p.name)
for p in (old/'native-libs/arm64-v8a').glob('*.so'):
 if p.name not in ['libvideokit_cpu.so','libvideokit_d1_lease.so']:shutil.copyfile(p,base/'native-libs/arm64-v8a'/p.name)
shutil.copytree(old/'evidence/inherited-c09',base/'evidence/inherited-c09')
shutil.copyfile(old/'evidence/inherited-native-admission.json',base/'evidence/inherited-native-admission.json')
for name in ['docs/milestones/D1_C12_CODER_REQUIREMENTS_V1.0.md','docs/tester/D1_C11_TEST_REPORT_V1.0.md']:
 shutil.copyfile(root/name,base/'evidence'/('input-'+Path(name).name))
print('C12 independent snapshot initialized; C01-C11 unchanged')
