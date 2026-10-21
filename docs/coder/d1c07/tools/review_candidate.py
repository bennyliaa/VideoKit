"""Local C07 build/evidence/identity review; no runtime or legal acceptance."""
from pathlib import Path
import json,hashlib,re,sys
root=Path(sys.argv[1]).resolve();base=root/'docs/coder/d1c07';e=base/'evidence';docs=root/'docs/coder'
def read(p):
 b=p.read_bytes();return b.decode('utf-16' if b.startswith((b'\xff\xfe',b'\xfe\xff')) else 'utf-8-sig')
def load(n):return json.loads(read(e/n))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
apks=load('apk-audit.json')['apks'];native=load('native-build.json');rows=[]
for apk in apks:
 if not (apk['path'].endswith('/app-debug.apk') or apk['path'].endswith('/worker-debug.apk')):continue
 prefix=root/'app' if apk['path'].endswith('/app-debug.apk') else base/'worker_app'
 merged=prefix/'build/intermediates/merged_native_libs/debug/mergeDebugNativeLibs/out/lib/arm64-v8a/libvideokit_d1_lease.so';stripped=prefix/'build/intermediates/stripped_native_libs/debug/stripDebugDebugSymbols/out/lib/arm64-v8a/libvideokit_d1_lease.so'
 packaged=next(r['sha256'] for r in apk['native_libraries'] if r['path'].endswith('libvideokit_d1_lease.so'))
 assert sha(merged)==native['native_sha256'] and sha(stripped)==packaged and sha(base/'native/lease.c')==native['source_sha256']
 rows.append({'apk':apk['path'],'own_source_sha256':native['source_sha256'],'merged_native_sha256':sha(merged),'packaged_stripped_sha256':packaged,'scope':'local own JNI provenance, runtime NOT_RUN'})
(e/'native-package-provenance.json').write_text(json.dumps({'status':'PASS','rows':rows},indent=2),encoding='utf-8')
delivery=read(docs/'D1_DELIVERY_D1-20261005-C07.md');appendix=read(docs/'D1_C07_DEVICE_APPENDIX_V1.0.md');options=read(docs/'D1_SINGLE_APP_ISOLATION_OPTIONS_V1.0.md');reuse=load('c06-evidence-reuse.json')
checks={
 'immutable_c01_through_c06_and_media':load('integrity-check.json')['status']=='PASS' and len(load('integrity-check.json')['samples'])==45,
 'exact_four_apks':len(apks)==4 and all(sha(root/r['path'])==r['sha256'] for r in apks),
 'reports_apk_hashes':all(r['sha256'] in delivery and r['sha256'] in appendix for r in apks),
 'no_samples_models_network_or_unadmitted_cpu_libs':all(not r['sample_named_entries'] and not r['model_entries'] and not r['internet_permission'] and r['unadmitted_cpu_libraries_absent'] for r in apks),
 'release_no_spike':all(not r['c07_dex'] for r in apks if 'release' in r['path']),
 'same_three_debug_signatures':len({r['certificate_sha256'] for r in apks if 'certificate_sha256' in r})==1,
 'worker_no_host_capture_business':next(r['host_classes_absent'] for r in apks if 'worker-debug' in r['path']),
 'one_cluster_build': 'BUILD SUCCESSFUL' in read(e/'c07-final-build.log'),
 'configuration_guard_refused': 'D1_C07_TOOL_EXECUTION_RESTRICTED' in read(e/'tool-guard-probe.log') and 'BUILD FAILED' in read(e/'tool-guard-probe.log'),
 '26_new_boundary_assertions':'RESULT c07_format_guard_assertions=26 failures=0' in read(e/'format-guard-probe.log'),
 '141_reused_not_rerun':reuse['reuse_assertions']==141 and not reuse['rerun'] and all(reuse['namespace_normalized_identity'].values()),
 'reuse_hash_provenance':all(sha(root/r['origin'])==r['sha256'] and sha(root/r['copy'])==r['sha256'] for r in reuse['files']),
 'formal_gates_static_only':load('gate-preservation.json')['status']=='PASS_STATIC_ONLY',
 'zero_new_dependencies':not load('baseline-reuse.json')['new_maven_coordinates'],
 'native_provenance':len(rows)==2,
 'cpu_options_unadmitted':'方案未选定、未准入' in options and 'OpenH264 v2.6.0' in options and 'FFmpeg n8.0' in options,
 'ordinary_not_rescheduled':'NOT_SCHEDULED' in appendix and 'UNKNOWN=FAIL' in delivery,
 'not_acceptance':'BLOCKED / NOT_READY' in delivery and 'NOT_RUN' in appendix,
 'sniff_skip_static_proof':'arraylength' in read(e/'bundled-extractors-adapter-javap.txt') and 'if_icmpne     67' in read(e/'bundled-extractors-adapter-javap.txt'),
 'reviewed_source_evidence':load('cpu-route-source-review.json')['status']=='OFFICIAL_FACT_REVIEW_ONLY',
 'advisory_reuse_47':len(list((e/'advisories').glob('*.json')))==47 and load('tool-vulnerability-review.json')['unique_advisories']==47,
}
methods={name:re.findall(r'@Test public void (\w+)\(',read(next((base/'device').rglob(name)))) for name in ['C07DeviceTests.java','C07IsolatedDeviceTests.java']}
checks['29_prepared_28_scheduled']=len(methods['C07DeviceTests.java'])==20 and len(methods['C07IsolatedDeviceTests.java'])==9 and appendix.count('NOT_SCHEDULED')==1
for p in (base/'tools').glob('*.py'):compile(read(p),str(p),'exec')
checks['python_syntax']=True
result={'candidateId':'D1-20261005-C07','status':'PASS' if all(checks.values()) else 'FAIL','checks':checks,'device_methods':methods,'prepared':29,'scheduled':28,'device_execution':'NOT_RUN','scope':'local consistency only; no CPU route admission, no D1/P0 acceptance'}
(e/'candidate-self-review.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result,indent=2));assert result['status']=='PASS'
