from pathlib import Path
import hashlib,json,re,subprocess,sys,zipfile,difflib
root=Path(sys.argv[1]).resolve();base=root/'docs/coder/d1c14';e=base/'evidence';old=root/'docs/coder/d1c13'
assert not (e/'freeze-summary.json').exists()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def row(p):return {'path':p.relative_to(root).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)}
def count(s):
 m=re.search(r'^PASS (\d+) |assertions=(\d+)',s,re.M);assert m,s
 return int(next(v for v in m.groups() if v is not None))
results=json.loads((e/'local-check-results.json').read_text(encoding='utf-8'));assert len(results)==17 and all(r['exit']==0 for r in results)
assert 'BUILD SUCCESSFUL' in (e/'final-build.log').read_text(encoding='utf-8-sig')
assert json.loads((e/'integrity-check.json').read_text(encoding='utf-8'))['status']=='PASS'
admission=json.loads((e/'inherited-native-admission.json').read_text(encoding='utf-8'))
for r in admission['unchangedNative']+admission['inheritedVerifiedInputs']:assert sha(root/r['path'])==r['sha256'],r['path']
assert len(json.loads((e/'inherited-c09/ffmpeg-object-source-license-map.json').read_text(encoding='utf-8'))['objects'])==266
for p in (base/'tools').glob('*.py'):compile(p.read_text(encoding='utf-8'),str(p),'exec')
classes=root/'app/build/intermediates/javac/debug/compileDebugJavaWithJavac/classes'
callback=subprocess.check_output(['D:/Android/Android Studio/jbr/bin/javap.exe','-s','-private','-classpath',str(classes),'com.videokit.spike.c14.CpuIsolatedService$Callbacks']).decode('utf-8');(e/'jni-callback-descriptors.txt').write_text(callback,encoding='utf-8')
descriptors=dict(re.findall(r'GetMethodID\(e,[^,]+,"(\w+)","([^"]+)"\)',(base/'native/cpu.c').read_text(encoding='utf-8')))
for name,descriptor in descriptors.items():assert re.search(r'\b'+name+r'\([^\n]*\)[^\n]*;\s+descriptor: '+re.escape(descriptor),callback),name
changed={'PipelineEncoder.java','RealFramePipeline.java','PipelineOutputSink.java','C13PipelineDeviceTests.java'};same=[];deltas=[]
for folder in ['src','android','native','device']:
 for p in (old/folder).rglob('*'):
  if not p.is_file():continue
  q=base/p.relative_to(old).as_posix().replace('c13','c14').replace('C13','C14');text=p.read_text(encoding='utf-8');hashes=sorted(set(re.findall(r'[a-f0-9]{64}',text)));slots={h:'HASH_SLOT_'+str(i)+'_END' for i,h in enumerate(hashes)}
  for h,s in slots.items():text=text.replace(h,s)
  if p.name!='quota.c':text=text.replace('c13','c14').replace('C13','C14')
  for h,s in slots.items():text=text.replace(s,h)
  if p.name in changed:
   (e/('delta-'+p.name+'.txt')).write_text(''.join(difflib.unified_diff(text.splitlines(True),q.read_text(encoding='utf-8').splitlines(True),fromfile=str(p),tofile=str(q))),encoding='utf-8');deltas.append(row(q))
  else:assert q.read_text(encoding='utf-8')==text,q;same.append(row(q))
(e/'baseline-source-equivalence.json').write_text(json.dumps({'baseline':'C13','unchanged_after_identity_rename':same,'changed_existing':deltas,'scope':'C13 CPU/exit/source/native and 17 pipeline methods preserved; two CPU signal methods deliberately NOT_RUN_UNCHANGED_PLATFORM_LIMIT; encoder and detailed diagnostics changed.'},indent=2),encoding='utf-8')
plan=json.loads((base/'tools/device_plan.json').read_text(encoding='utf-8'));apks=json.loads((e/'apk-audit.json').read_text(encoding='utf-8'))['apks'];test=next(r for r in apks if r['file']=='app-debug-androidTest.apk')
assert set(test['cpu_test_methods'])==set(plan['groups']['cpu'])|{r['method'] for r in plan['not_run_unchanged_platform_limit']};assert set(test['pipeline_test_methods'])==set(plan['groups']['pipeline'])
assert [len(plan['groups'][g]) for g in ['cpu','host','legacy','pipeline','encoder']]==[35,7,8,17,6];assert plan['total_per_eligible_device']==73;assert set(test['encoder_test_methods'])==set(plan['groups']['encoder'])
assert next(r for r in apks if r['file']=='app-release-unsigned.apk')['unchanged_release_vs_C07']
with zipfile.ZipFile(old/'artifacts/D1-20261016-C13/D1-20261016-C13-source.zip') as z:
 assert z.read('app/gradle.lockfile')==(root/'app/gradle.lockfile').read_bytes()
 assert z.read('app/src/debug/AndroidManifest.xml').decode('utf-8').replace('\r\n','\n').replace('c13','c14').replace('C13','C14')==(root/'app/src/debug/AndroidManifest.xml').read_text(encoding='utf-8')
compiled=[]
for folder,output in [('src',classes),('android',classes),('device',root/'app/build/intermediates/javac/debugAndroidTest/compileDebugAndroidTestJavaWithJavac/classes')]:
 for p in (base/folder).rglob('*.java'):
  q=output/'com/videokit/spike/c14'/p.with_suffix('.class').name;assert q.exists() and q.stat().st_mtime>=p.stat().st_mtime,p;compiled.append({'source':row(p),'class':row(q)})
native=json.loads((e/'cpu-native-build.json').read_text(encoding='utf-8'));assert native['sourceSha256']==sha(base/'native/cpu.c') and native['librarySha256']==sha(base/'native-libs/arm64-v8a/libvideokit_cpu.so')
assert sha(base/'upstream/ffmpeg-8.0.3.tar.xz')=='6136812ea6d4e68bdba27e33c2a94382711cdf4f8602ffef056ff792bd6f9818'
assert (base/'native/quota.c').read_bytes()==(old/'native/quota.c').read_bytes()
for name in ['libavformat.so','libavcodec.so','libavutil.so','libswscale.so','libvideokit_alloc.so']:assert sha(base/'native-libs/arm64-v8a'/name)==sha(old/'native-libs/arm64-v8a'/name)
(e/'build-source-binding.json').write_text(json.dumps({'compiled_java':compiled,'native':native,'artifacts':apks,'scope':'actual compile/static binding only; device NOT_RUN'},indent=2),encoding='utf-8')
jvm=sum(count(r['output']) for r in results);scripts=sum(count((e/n).read_text(encoding='utf-8-sig')) for n in ['device-guard-selfcheck.log','device-runner-selfcheck.log'])
facts={'candidateId':'D1-20261016-C14','review':'PASS_LOCAL_BUILD_STATIC_AND_PURE_CHECKS','pure_assertions':jvm,'jvm_assertions':jvm,'script_assertions':scripts,'total_local_assertions':jvm+scripts,**{g+'_device_methods':len(v) for g,v in plan['groups'].items()},'unchanged_signal_methods':plan['not_run_unchanged_platform_limit'],'scheduled_device_methods':plan['total_per_eligible_device'],'compiled_designated_methods':plan['compiled_method_count'],'device':'NOT_RUN','product_acceptance':'D1_NOT_PASSED','artifacts':apks,'callback_descriptors':descriptors,'changes':['Finite 4-attempt public AVC negotiation, actual release fences and typed diagnostics','Unchanged real six-frame/PTS/content/full EOF pipeline thresholds; all 14 formerly blocked counterexamples retained','C13-T02 remains FAIL/OPEN; two unchanged CPU crash methods not dispatched','Correct internal naming and conservative 8-array accounting'],'limitations':['No device/runtime pipeline success claimed','Host codec/JNI, legacy host validation/display/audio/tracking remain OPEN','Not continuous decoder/dualtrack export/full Kit/AAR/Flutter','No new models/media/dependencies/permissions; no ADB; C01-C13 readonly']}
(e/'candidate-self-review.json').write_text(json.dumps(facts,indent=2),encoding='utf-8');print('C14 review PASS',jvm,scripts,'73 scheduled + 2 unchanged-signal NOT_RUN methods')
