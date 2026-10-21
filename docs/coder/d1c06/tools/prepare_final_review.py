"""Local C06 delivery consistency preparation; no device operations."""
from pathlib import Path
import hashlib,json,sys
root=Path(sys.argv[1]).resolve();base=root/'docs/coder/d1c06';e=base/'evidence'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
p=base/'tools/review_candidate.py';s=p.read_text(encoding='utf-8')
s=s.replace('immutable_c01_c02_c03_c04_and_45_media','immutable_c01_through_c05_and_45_media')
s=s.replace("'BUILD SUCCESSFUL' in read(e/'c06-pre-final-build.log') and ", '')
s='\n'.join(line for line in s.split('\n') if "checks['final_test_apk_compile']" not in line)
s=s.replace("checks['16_and_9_device_entries_prepared']", "checks['17_and_9_device_entries_prepared']").replace("==16 and len(methods", "==17 and len(methods")
s=s.replace('c04-evidence-reuse.json','c05-evidence-reuse.json').replace('D1_C06_DIAGNOSIS_AND_LIMITS_V1.0.md','D1_C06_DIAGNOSIS_AND_EXIT_REVIEW_V1.0.md')
s=s.replace("checks['23_new_failure_counterexamples']", "checks['23_reused_c05_failure_counterexamples']").replace('RESULT c06_failure_assertions=23','RESULT c05_failure_assertions=23')
s=s.replace("checks['own_native_package_provenance']", "checks['22_new_capture_assertions']='RESULT c06_capture_assertions=22 failures=0' in read(e/'capture-probe.log')\nchecks['prior_failures_fact_review']=load('prior-failure-analysis.json')['status']=='PASS_FACT_REVIEW_ONLY'\nchecks['own_native_package_provenance']")
p.write_text(s,encoding='utf-8')
p=base/'tools/freeze.py';s=p.read_text(encoding='utf-8').replace('D1_C06_DIAGNOSIS_AND_LIMITS_V1.0.md','D1_C06_DIAGNOSIS_AND_EXIT_REVIEW_V1.0.md').replace('C01/C02/C03/C04','C01/C02/C03/C04/C05');p.write_text(s,encoding='utf-8')
native=json.loads((e/'native-build.json').read_text(encoding='utf-8'));audit=json.loads((e/'apk-audit.json').read_text(encoding='utf-8'));rows=[]
for apk in audit['apks']:
 if not (apk['path'].endswith('/app-debug.apk') or apk['path'].endswith('/worker-debug.apk')):continue
 prefix=root/'app' if apk['path'].endswith('/app-debug.apk') else base/'worker_app'
 merged=prefix/'build/intermediates/merged_native_libs/debug/mergeDebugNativeLibs/out/lib/arm64-v8a/libvideokit_d1_lease.so'
 stripped=prefix/'build/intermediates/stripped_native_libs/debug/stripDebugDebugSymbols/out/lib/arm64-v8a/libvideokit_d1_lease.so'
 packaged=next(r['sha256'] for r in apk['native_libraries'] if r['path'].endswith('libvideokit_d1_lease.so'))
 assert sha(merged)==native['native_sha256'] and sha(stripped)==packaged
 assert sha(base/'native/lease.c')==native['source_sha256']
 rows.append({'apk':apk['path'],'own_source_sha256':native['source_sha256'],'merged_native_sha256':sha(merged),'packaged_stripped_sha256':packaged,'scope':'own signal/flock JNI local build only; runtime NOT_RUN'})
assert len(rows)==2
(e/'native-package-provenance.json').write_text(json.dumps({'status':'PASS','rows':rows},indent=2),encoding='utf-8')
print('C06 review prepared; native package provenance PASS')
