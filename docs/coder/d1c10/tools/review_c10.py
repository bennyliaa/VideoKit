from pathlib import Path
import hashlib,json,re,subprocess,sys
root=Path(sys.argv[1]).resolve();base=root/'docs/coder/d1c10';e=base/'evidence';old=root/'docs/coder/d1c09'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def row(p):return {'path':p.relative_to(root).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)}
results=json.loads((e/'local-check-results.json').read_text(encoding='utf-8'));assert len(results)==10 and all(r['exit']==0 for r in results)
assert 'PASS 78 ' in (e/'C10LifecycleSelfCheck.log').read_text(encoding='utf-8')
assert 'PASS 52 ' in (e/'C10CpuSelfCheck.log').read_text(encoding='utf-8')
assert 'PASS 16 ' in (e/'device-guard-selfcheck.log').read_text(encoding='utf-8')
assert 'PASS 12 ' in (e/'device-runner-selfcheck.log').read_text(encoding='utf-8')
assert 'BUILD SUCCESSFUL' in (e/'final-build.log').read_text(encoding='utf-8-sig')
assert json.loads((e/'integrity-check.json').read_text(encoding='utf-8'))['status']=='PASS'
admission=json.loads((e/'inherited-native-admission.json').read_text(encoding='utf-8'))
for r in admission['unchangedNative']+admission['inheritedVerifiedInputs']:assert sha(root/r['path'])==r['sha256'],r['path']
assert len(json.loads((e/'inherited-c09/ffmpeg-object-source-license-map.json').read_text(encoding='utf-8'))['objects'])==266
for p in (base/'tools').glob('*.py'):compile(p.read_text(encoding='utf-8'),str(p),'exec')
client=(base/'android/com/videokit/spike/c10/CpuTaskClient.java').read_text(encoding='utf-8');service=(base/'android/com/videokit/spike/c10/CpuIsolatedService.java').read_text(encoding='utf-8');tests=(base/'device/com/videokit/spike/c10/C10CpuDeviceTests.java').read_text(encoding='utf-8')
production_stop=client.split('private void sendStop()',1)[1].split('public void cancel()',1)[0]
assert 'endpoint.transact(CpuProtocol.STOP,p,a,0)' in production_stop and 'FLAG_ONEWAY' not in production_stop
assert 'STOPS.execute' in production_stop and 'readException(' not in client
assert 'CpuControlRules.synchronous(flags)' in service and 'CpuControlRules.owner' in service and 'CpuControlRules.session' in service
assert 'recordPrimary(primary);throw primary;' in tests and 'primary.addSuppressed(cleanup)' in tests
classes=root/'app/build/intermediates/javac/debug/compileDebugJavaWithJavac/classes'
callback=subprocess.check_output(['D:/Android/Android Studio/jbr/bin/javap.exe','-s','-private','-classpath',str(classes),'com.videokit.spike.c10.CpuIsolatedService$Callbacks']).decode('utf-8');(e/'jni-callback-descriptors.txt').write_text(callback,encoding='utf-8')
descriptors=dict(re.findall(r'GetMethodID\(e,[^,]+,"(\w+)","([^"]+)"\)',(base/'native/cpu.c').read_text(encoding='utf-8')))
for name,descriptor in descriptors.items():assert re.search(r'\b'+name+r'\([^\n]*\)[^\n]*;\s+descriptor: '+re.escape(descriptor),callback),name
unchanged=[]
for folder in ['src','android','native']:
 for p in (old/folder).rglob('*'):
  if not p.is_file() or p.name in ['CpuTaskClient.java','CpuIsolatedService.java','CpuProtocol.java']:continue
  relative=p.relative_to(old).as_posix().replace('c09','c10').replace('C09','C10');q=base/relative
  text=p.read_text(encoding='utf-8');hashes=set(re.findall(r'[a-f0-9]{64}',text));slots={h:'HASH_SLOT_'+str(i)+'_END' for i,h in enumerate(hashes)}
  for h,s in slots.items():text=text.replace(h,s)
  if p.name!='quota.c':text=text.replace('c09','c10').replace('C09','C10').replace('vk_c10_','vk_c09_')
  for h,s in slots.items():text=text.replace(s,h)
  assert q.read_text(encoding='utf-8')==text,q
  unchanged.append(row(q))
(e/'baseline-source-equivalence.json').write_text(json.dumps({'unchanged_after_identity_rename':unchanged,'changed_existing':'CPU client/service/protocol and CPU test harness only; no codec/Media3/output validators or source bridge behavior changes','new_glue':'CpuLifecycle/CpuDiagnostics/CpuControlRules/CpuEnvironment, device hard-stop/result/bounded-output guard'},indent=2),encoding='utf-8')
apks=json.loads((e/'apk-audit.json').read_text(encoding='utf-8'))['apks'];test_methods=next(r['cpu_test_methods'] for r in apks if r['file']=='app-debug-androidTest.apk');assert len(test_methods)==25
assert next(r for r in apks if r['file']=='app-release-unsigned.apk')['unchanged_release_vs_C07']
# Compare exact app dependency lock against frozen C09 source archive, not mutable-root recollection.
import zipfile
with zipfile.ZipFile(old/'artifacts/D1-20261016-C09/D1-20261016-C09-source.zip') as z:assert z.read('app/gradle.lockfile')==(root/'app/gradle.lockfile').read_bytes()
facts={'candidateId':'D1-20261016-C10','review':'PASS_LOCAL_BUILD_STATIC_AND_PURE_CHECKS','jvm_assertions':293,'script_assertions':28,'total_local_assertions':321,'pure_assertions':293,'cpu_device_methods':25,'device':'NOT_RUN','product_acceptance':'D1_NOT_PASSED','changes':['C09-T01 strict sync STOP, actual-release/recovery facts','C09-T02 stable first phase/reason and suppressed cleanup','C09-ENV01 read-only enabled/component/visibility gate; fail-stop guarded scripts','C09 audit wording 267 -> actual 266 in new metadata only'],'inherited_native':sha(e/'inherited-native-admission.json'),'artifacts':apks,'callback_descriptors':descriptors,'checks':'local pure rules plus NDK/Android compile/static package; no ADB/device/GPG/FFmpeg rebuild in C10'}
(e/'candidate-self-review.json').write_text(json.dumps(facts,indent=2),encoding='utf-8');print(json.dumps({k:v for k,v in facts.items() if k not in ['artifacts','callback_descriptors']},indent=2))
