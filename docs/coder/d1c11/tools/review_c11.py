from pathlib import Path
import hashlib,json,re,subprocess,sys
root=Path(sys.argv[1]).resolve();base=root/'docs/coder/d1c11';e=base/'evidence';old=root/'docs/coder/d1c10'
assert not (e/'freeze-summary.json').exists(),'Read-only verification only after freeze'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def row(p):return {'path':p.relative_to(root).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)}
results=json.loads((e/'local-check-results.json').read_text(encoding='utf-8'));assert len(results)==12 and all(r['exit']==0 for r in results)
assert 'PASS 78 ' in (e/'C11LifecycleSelfCheck.log').read_text(encoding='utf-8')
assert 'PASS 52 ' in (e/'C11CpuSelfCheck.log').read_text(encoding='utf-8')
assert 'PASS 16 ' in (e/'device-guard-selfcheck.log').read_text(encoding='utf-8')
assert 'PASS 12 ' in (e/'device-runner-selfcheck.log').read_text(encoding='utf-8')
assert 'BUILD SUCCESSFUL' in (e/'final-build.log').read_text(encoding='utf-8-sig')
assert json.loads((e/'integrity-check.json').read_text(encoding='utf-8'))['status']=='PASS'
admission=json.loads((e/'inherited-native-admission.json').read_text(encoding='utf-8'))
for r in admission['unchangedNative']+admission['inheritedVerifiedInputs']:assert sha(root/r['path'])==r['sha256'],r['path']
assert len(json.loads((e/'inherited-c09/ffmpeg-object-source-license-map.json').read_text(encoding='utf-8'))['objects'])==266
for p in (base/'tools').glob('*.py'):compile(p.read_text(encoding='utf-8'),str(p),'exec')
client=(base/'android/com/videokit/spike/c11/CpuTaskClient.java').read_text(encoding='utf-8');service=(base/'android/com/videokit/spike/c11/CpuIsolatedService.java').read_text(encoding='utf-8');tests=(base/'device/com/videokit/spike/c11/C11CpuDeviceTests.java').read_text(encoding='utf-8')
production_stop=client.split('private void sendStop()',1)[1].split('public void cancel()',1)[0]
assert 'endpoint.transact(CpuProtocol.STOP,p,a,0)' in production_stop and 'FLAG_ONEWAY' not in production_stop
assert 'STOPS.execute' in production_stop and 'readException(' not in client
assert 'CpuControlRules.synchronous(flags)' in service and 'CpuControlRules.owner' in service and 'CpuControlRules.session' in service
assert 'recordPrimary(primary);throw primary;' in tests and 'primary.addSuppressed(cleanup)' in tests
classes=root/'app/build/intermediates/javac/debug/compileDebugJavaWithJavac/classes'
callback=subprocess.check_output(['D:/Android/Android Studio/jbr/bin/javap.exe','-s','-private','-classpath',str(classes),'com.videokit.spike.c11.CpuIsolatedService$Callbacks']).decode('utf-8');(e/'jni-callback-descriptors.txt').write_text(callback,encoding='utf-8')
descriptors=dict(re.findall(r'GetMethodID\(e,[^,]+,"(\w+)","([^"]+)"\)',(base/'native/cpu.c').read_text(encoding='utf-8')))
for name,descriptor in descriptors.items():assert re.search(r'\b'+name+r'\([^\n]*\)[^\n]*;\s+descriptor: '+re.escape(descriptor),callback),name
unchanged=[]
for folder in ['src','android','native']:
 for p in (old/folder).rglob('*'):
  if not p.is_file() or p.name in ['CpuTaskClient.java','CpuIsolatedService.java','ExitEvidence.java','TombstoneWitness.java']:continue
  relative=p.relative_to(old).as_posix().replace('c10','c11').replace('C10','C11');q=base/relative
  text=p.read_text(encoding='utf-8');hashes=set(re.findall(r'[a-f0-9]{64}',text));slots={h:'HASH_SLOT_'+str(i)+'_END' for i,h in enumerate(hashes)}
  for h,s in slots.items():text=text.replace(h,s)
  if p.name!='quota.c':text=text.replace('c10','c11').replace('C10','C11').replace('vk_c09_','vk_c09_')
  for h,s in slots.items():text=text.replace(s,h)
  assert q.read_text(encoding='utf-8')==text,q
  unchanged.append(row(q))
(e/'baseline-source-equivalence.json').write_text(json.dumps({'unchanged_after_identity_rename':unchanged,'changed_existing':'CPU client/service and shared exit evidence/parser; no codec/Media3/output validators or source bridge behavior changes','new_glue':'WorkerGenerations/ExitTraceCapture/ExitTraceRules; inherited lifecycle/environment/guard behavior preserved'},indent=2),encoding='utf-8')
apks=json.loads((e/'apk-audit.json').read_text(encoding='utf-8'))['apks'];test_methods=next(r['cpu_test_methods'] for r in apks if r['file']=='app-debug-androidTest.apk');assert len(test_methods)==len(re.findall(r'@Test public void (\w+)\(',tests))
assert next(r for r in apks if r['file']=='app-release-unsigned.apk')['unchanged_release_vs_C07']
# Compare exact app dependency lock against frozen C10 source archive, not mutable-root recollection.
import zipfile
with zipfile.ZipFile(old/'artifacts/D1-20261016-C10/D1-20261016-C10-source.zip') as z:assert z.read('app/gradle.lockfile')==(root/'app/gradle.lockfile').read_bytes()
def count(text):
 m=re.search(r'^PASS (\d+) |assertions=(\d+)',text,re.M);assert m,text
 return int(next(v for v in m.groups() if v is not None))
jvm=sum(count(r['output']) for r in results)
scripts=sum(count((e/name).read_text(encoding='utf-8-sig')) for name in ['device-guard-selfcheck.log','device-runner-selfcheck.log'])
assert 'observeDeath()' not in client and 'endpoint.linkToDeath(()->observeDeath(worker)' in client
assert 'workers.allDead()' in client and 'workers.canRelease()' in client and 'workers.primary()==null' in client
orphan_stop=client.split('private void stopRejected(',1)[1].split('public void cancel()',1)[0]
assert 'CpuProtocol.START' not in orphan_stop and 'CpuProtocol.STOP' in orphan_stop
assert 'debug_stop_stall' in service and 'c11_registration' in service
native_rows=[]
for name in ['libavformat.so','libavcodec.so','libavutil.so','libswscale.so','libvideokit_alloc.so']:
 current=base/'native-libs/arm64-v8a'/name;assert sha(current)==sha(old/'native-libs/arm64-v8a'/name);native_rows.append(row(current))
assert (base/'native/quota.c').read_bytes()==(old/'native/quota.c').read_bytes()
for folder in ['device']:
 for name in ['C10DeviceTests.java','C10IsolatedDeviceTests.java']:
  p=next((old/folder).rglob(name));q=base/p.relative_to(old).as_posix().replace('c10','c11').replace('C10','C11');assert q.read_text(encoding='utf-8')==p.read_text(encoding='utf-8').replace('c10','c11').replace('C10','C11')
plan=json.loads((base/'tools/device_plan.json').read_text(encoding='utf-8'));assert set(test_methods)==set(plan['groups']['cpu'])
compiled=[]
for folder,output in [('src',classes),('android',classes),('device',root/'app/build/intermediates/javac/debugAndroidTest/compileDebugAndroidTestJavaWithJavac/classes')]:
 for source in (base/folder).rglob('*.java'):
  compiled_class=output/'com/videokit/spike/c11'/source.with_suffix('.class').name
  assert compiled_class.exists() and compiled_class.stat().st_mtime>=source.stat().st_mtime,source
  compiled.append({'source':row(source),'class':row(compiled_class)})
assert sha(base/'upstream/ffmpeg-8.0.3.tar.xz')=='6136812ea6d4e68bdba27e33c2a94382711cdf4f8602ffef056ff792bd6f9818'
(e/'build-source-binding.json').write_text(json.dumps({'compiled_java':compiled,'artifacts':[{k:r[k] for k in ['path','sha256','bytes']} for r in apks],'scope':'post-build source and class hashes plus mtime; no device execution'},indent=2),encoding='utf-8')
facts={'candidateId':'D1-20261016-C11','review':'PASS_LOCAL_BUILD_STATIC_AND_PURE_CHECKS','jvm_assertions':jvm,'script_assertions':scripts,'total_local_assertions':jvm+scripts,'pure_assertions':jvm,'cpu_device_methods':len(test_methods),'host_device_methods':len(plan['groups']['host']),'legacy_device_methods':len(plan['groups']['legacy']),'device':'NOT_RUN','product_acceptance':'D1_NOT_PASSED','changes':['C10-T01 raw OS/trace separation, collect trace at status0 without promoting signal','C10-T02 fixed primary generation; per-worker registration/death; orphan revoke/quarantine and two CPU slots','C10-ENV01 unchanged hard-stop environment gate'],'unchanged_native':native_rows,'inherited_native':sha(e/'inherited-native-admission.json'),'artifacts':apks,'callback_descriptors':descriptors,'checks':'JVM actual shared rules/readers plus NDK and Android compile/package/static; no ADB/device/GPG/FFmpeg rebuild','limitations':['Android races and App trace availability NOT_RUN','System signal0 remains UNKNOWN/FAIL; original strict tests retained','MAX_WORKERS=4 is history/control quarantine capacity, never decoder capacity','No M0/fullKit/AAR/Flutter/product-distribution acceptance']}
(e/'candidate-self-review.json').write_text(json.dumps(facts,indent=2),encoding='utf-8');print(json.dumps({k:v for k,v in facts.items() if k not in ['artifacts','callback_descriptors','unchanged_native']},indent=2))
