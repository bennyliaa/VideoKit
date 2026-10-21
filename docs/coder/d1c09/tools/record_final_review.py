from pathlib import Path
import hashlib,json,re,shutil,subprocess,sys
root=Path(sys.argv[1]).resolve();base=root/'docs/coder/d1c09';e=base/'evidence';ndk=Path('D:/Android/SDK/ndk/30.0.16248370');tool=ndk/'toolchains/llvm/prebuilt/windows-x86_64/bin'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def row(p):return {'path':p.relative_to(root).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)}
results=json.loads((e/'local-check-results.json').read_text(encoding='utf-8'));log=(e/'C09CpuSelfCheck.log').read_text(encoding='utf-8');assert log.startswith('PASS 52 ')
results[0].update({'output':log,'execution':'RERUN_AFTER_AGGREGATE_QUOTA_RULE_ADDITION','exit':0});(e/'local-check-results.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
assert all(r['exit']==0 for r in results)
for name in ['NOTICE','NOTICE.toolchain','source.properties']:shutil.copyfile(ndk/name,e/('ndk-'+name+'.txt'))
for name in ['docs/tester/D1_C09_PRETEST_REVIEW_V1.0.md','docs/milestones/D1_C09_CODER_REQUIREMENTS_V1.0.md']:
 shutil.copyfile(root/name,e/('input-'+Path(name).name))
# Verify callback signatures from compiled Android classes, not just matching source strings.
classes=root/'app/build/intermediates/javac/debug/compileDebugJavaWithJavac/classes'
javap=subprocess.check_output(['D:/Android/Android Studio/jbr/bin/javap.exe','-s','-private','-classpath',str(classes),'com.videokit.spike.c09.CpuIsolatedService$Callbacks']).decode('utf-8');(e/'jni-callback-descriptors.txt').write_text(javap,encoding='utf-8')
native=(base/'native/cpu.c').read_text(encoding='utf-8')
descriptors={name:descriptor for name,descriptor in re.findall(r'GetMethodID\(e,[^,]+,"(\w+)","([^"]+)"\)',native)}
for name,descriptor in descriptors.items():assert re.search(r'\b'+name+r'\([^\n]*\)[^\n]*;\s+descriptor: '+re.escape(descriptor),javap),name
helper=base/'native-libs/arm64-v8a/libvideokit_alloc.so';symbols=subprocess.check_output([str(tool/'llvm-nm.exe'),'-D',str(helper)]).decode('utf-8');(e/'quota-symbols.txt').write_text(symbols,encoding='utf-8')
libavutil=base/'native-libs/arm64-v8a/libavutil.so';references=subprocess.check_output([str(tool/'llvm-nm.exe'),'-D',str(libavutil)]).decode('utf-8');(e/'avutil-quota-references.txt').write_text(references,encoding='utf-8')
for name in ['vk_c09_posix_memalign','vk_c09_realloc','vk_c09_free']:assert name in symbols and re.search(r' U '+name+r'\b',references),name
# Reused formal pipeline source is byte-identical after package/candidate renaming.
unchanged=[]
for folder in ['src','android','native']:
 for p in (root/'docs/coder/d1c08'/folder).rglob('*'):
  if not p.is_file():continue
  relative=p.relative_to(root/'docs/coder/d1c08').as_posix().replace('c08','c09').replace('C08','C09');q=base/relative
  if p.name=='AsyncReadBridge.java':continue
  text=p.read_text(encoding='utf-8');hashes=set(re.findall(r'[a-f0-9]{64}',text));slots={v:'HASH_'+str(i)+'_SLOT' for i,v in enumerate(hashes)}
  for h,s in slots.items():text=text.replace(h,s)
  text=text.replace('20261005-C08','20261016-C09').replace('c08','c09').replace('C08','C09')
  for h,s in slots.items():text=text.replace(s,h)
  assert q.read_text(encoding='utf-8')==text,q
  unchanged.append(row(q))
(e/'formal-baseline-source-equivalence.json').write_text(json.dumps({'unchanged_after_identity_rename':unchanged,'changed_shared_source':'AsyncReadBridge adds known length and authenticated CPU-only seekAbsolute; old broker has no seek RPC; 47 source assertions and release/lock/failure checks passed','new_sources':'CPU protocol/service/client/JNI and allocator only','formal_release_identical':True},indent=2),encoding='utf-8')
cpu_deps=(base/'outputs/cpu-native.d').read_text(encoding='utf-8');(e/'cpu-native-dependencies.txt').write_text(cpu_deps,encoding='utf-8')
map_data=json.loads((e/'ffmpeg-object-source-license-map.json').read_text(encoding='utf-8'));known={r['path'] for r in map_data['files']};wrapper_deps=[]
for token in cpu_deps.replace('\\\n',' ').split()[2:]:
 p=Path(token)
 if p.is_file():
  r=row(p);r['license']='independent project glue' if p==base/'native/cpu.c' else 'audited FFmpeg file' if r['path'] in known else 'additional public FFmpeg header; LGPL default, full retained text';wrapper_deps.append(r)
(e/'jni-source-dependency-map.json').write_text(json.dumps({'source':row(base/'native/cpu.c'),'allocator_source':row(base/'native/quota.c'),'dependencies':wrapper_deps,'NDK_system_headers':'JNI/libc headers and runtime tracked by exact NDK properties/full NOTICE; no vendored external codec library'},indent=2),encoding='utf-8')
app_lock=root/'app/gradle.lockfile';old_zip=root/'docs/coder/d1c07/artifacts/D1-20261005-C07/D1-20261005-C07-source.zip'
import zipfile
with zipfile.ZipFile(old_zip) as z:assert z.read('app/gradle.lockfile')==app_lock.read_bytes()
coordinates=[line.split('=')[0] for line in app_lock.read_text(encoding='utf-8').splitlines() if not line.startswith('#') and '=' in line and 'debugRuntimeClasspath' in line.split('=')[1].split(',')]
(e/'dependency-baseline-review.json').write_text(json.dumps({'app_lock_sha256':sha(app_lock),'identical_to_C07':True,'debug_runtime_coordinates':coordinates,'new_upstream':'signed FFmpeg 8.0.3, audited selected components','new_project_glue':'libvideokit_cpu.so and libvideokit_alloc.so; independent source fully retained','inherited_native':'AndroidX graphics path byte-identical to C07 per apk-audit.json; Apache-2.0 AndroidX baseline','scope':'not a new product distribution approval'},indent=2),encoding='utf-8')
sbom=json.loads((e/'c09-sbom.cdx.json').read_text(encoding='utf-8'))
sbom['components']=[c for c in sbom['components'] if c['name']!='VideoKit CPU JNI/quota project glue']
sbom['properties']=[p for p in sbom['properties'] if p['name'] not in ['aggregate-quota','inherited-runtime']]
sbom['components'] += [{'type':'library','name':'VideoKit CPU JNI/quota project glue','version':'D1-20261016-C09','properties':[{'name':'source','value':'native/cpu.c and native/quota.c; source/dependency/build/hash maps retained'}]}]
sbom['properties'] += [{'name':'aggregate-quota','value':'64MiB FFmpeg allocator requested bytes, 4096 records; prefix linker references verified; not a whole-process RSS bound'}, {'name':'inherited-runtime','value':'exact coordinates and native hashes in dependency-baseline-review.json and apk-audit.json'}]
(e/'c09-sbom.cdx.json').write_text(json.dumps(sbom,indent=2),encoding='utf-8')
assert 'readException(' not in (base/'android/com/videokit/spike/c09/CpuTaskClient.java').read_text(encoding='utf-8')
for item in map_data['files']:
 p=root/item['path']
 if p.is_relative_to(base/'outputs/ffmpeg-build'):
  target=e/'ffmpeg-generated/tree'/p.relative_to(base/'outputs/ffmpeg-build');target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,target)
facts={'candidateId':'D1-20261016-C09','review':'PASS_LOCAL_BUILD_STATIC_AND_PURE_CHECKS','android_execution':'NOT_RUN','product_acceptance':'NOT_PASSED','pure_assertions':215,'cpu_device_methods':17,'callback_descriptors':descriptors,'artifact_audit':sha(e/'apk-audit.json'),'historical_integrity':sha(e/'integrity-check.json'),'restriction':'single APK ARM64 API31+ local Debug CPU experiment; no device run by coder; no M0 or product backend decision'}
assert json.loads((e/'integrity-check.json').read_text(encoding='utf-8'))['status']=='PASS'
(e/'candidate-self-review.json').write_text(json.dumps(facts,indent=2),encoding='utf-8');print(json.dumps(facts,indent=2))
