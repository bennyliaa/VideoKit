"""C04 consistency review, not stage acceptance or device execution."""
from pathlib import Path
import json,sys,re,hashlib
root=Path(sys.argv[1]).resolve();base=root/'docs/coder/d1c04';e=base/'evidence';docs=root/'docs/coder'
def read(p):
 b=p.read_bytes();return b.decode('utf-16' if b.startswith((b'\xff\xfe',b'\xfe\xff')) else 'utf-8-sig')
def load(n):return json.loads(read(e/n))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
apks=load('apk-audit.json')['apks'];supply=load('supply-inventory.json');vuln=load('osv-results.json');review=load('tool-vulnerability-review.json');checks={}
checks['immutable_c01_c02_c03_and_45_media']=load('integrity-check.json')['status']=='PASS' and len(load('integrity-check.json')['samples'])==45
checks['four_copied_apks']=len(apks)==4 and all(sha(root/r['path'])==r['sha256'] for r in apks)
delivery=read(docs/'D1_DELIVERY_D1-20261005-C04.md');appendix=read(docs/'D1_C04_DEVICE_APPENDIX_V1.0.md')
checks['delivery_and_appendix_exact_apk_hashes']=all(r['sha256'] in delivery and r['sha256'] in appendix for r in apks)
checks['no_declared_internet_named_samples_model_entries']=all(not r['internet_permission'] and not r['sample_named_entries'] and not r['model_entries'] for r in apks)
checks['release_excludes_c04']=all(not r['c04_dex'] for r in apks if 'release' in r['path'])
checks['companion_no_host_business_classes']=next(r['host_classes_absent'] for r in apks if 'worker-debug' in r['path'])
checks['three_signed_apks_same_certificate']=len({r['certificate_sha256'] for r in apks if 'certificate_sha256' in r})==1
checks['47_contract_assertions']='RESULT assertions=47 failures=0' in read(e/'contract-probe.log')
checks['24_recovery_assertions']='RESULT recovery_assertions=24 failures=0' in read(e/'recovery-probe.log')
checks['12_validation_counterexamples']='RESULT assertions=12 failures=0' in read(e/'validation-probe.log')
checks['native_source_still_same']=sha(base/'native/lease.c')==load('native-build.json')['source_sha256']
checks['full_cluster_and_final_strict_build']='BUILD SUCCESSFUL' in read(e/'c04-pre-report-build.log') and 'BUILD SUCCESSFUL' in read(e/'c04-final-build.log')
checks['tool_guard_expected_refusal']='D1_C04_TOOL_EXECUTION_RESTRICTED' in read(e/'tool-guard-probe.log') and 'BUILD FAILED' in read(e/'tool-guard-probe.log')
checks['zero_new_maven_coordinates']=not load('baseline-reuse.json')['new_maven_coordinates']
checks['reuse_exact_osv_graph']={(r['coordinate'],r['scope']) for r in supply['components']}=={(r['coordinate'],r['scope']) for r in vuln['results']}
checks['all_16_components_47_advisory_details']=review['matched_components']==16 and review['unique_advisories']==47 and not review['fetch_failures'] and len(list((e/'advisories').glob('*.json')))==47
checks['no_false_patched_claim']=all(not r['patched'] for r in review['components'])
checks['metadata_missing_zero']=not supply['missing_license_claims']
methods={n:re.findall(r'@Test public void (\w+)\(',read(base/'device/com/videokit/spike/c04'/n)) for n in ['C04DeviceTests.java','C04IsolatedDeviceTests.java']}
checks['14_and_9_device_entries_prepared']=len(methods['C04DeviceTests.java'])==14 and len(methods['C04IsolatedDeviceTests.java'])==9
checks['device_status_explicit']='NOT_RUN' in appendix and 'BLOCKED / NOT_READY' in delivery
checks['7_control_assertions']='RESULT control_assertions=7 failures=0' in read(e/'control-probe.log')
checks['6_binary_protocol_assertions']=load('transfer-selfcheck.json')['status']=='PASS' and load('transfer-selfcheck.json')['assertions']==6 and load('transfer-selfcheck.json')['streamed_large_bytes']>2**31
checks['gate_preservation_static']=load('gate-preservation.json')['status']=='PASS_STATIC_ONLY'
reuse=load('c03-evidence-reuse.json')
checks['unchanged_rule_decoder_selfcheck_sources']=all(reuse['namespace_normalized_identity'].values())
checks['reuse_provenance_verified']=all(sha(root/r['origin'])==r['sha256'] and ('copy' not in r or sha(root/r['copy'])==r['sha256']) for r in reuse['files'])
checks['isolation_ac3_options_exist']=(docs/'D1_C04_ISOLATION_AND_AC3_OPTIONS_V1.0.md').exists()
checks['own_native_package_provenance']=load('native-package-provenance.json')['status']=='PASS'
checks['python_syntax']=True
for p in (base/'tools').glob('*.py'):compile(read(p),str(p),'exec')
result={'candidateId':'D1-20261005-C04','status':'PASS' if all(checks.values()) else 'FAIL','checks':checks,'device_methods':methods,'device_execution':'NOT_RUN','scope':'local evidence consistency and build/probe review; not D1/M0/P0 acceptance'}
(e/'candidate-self-review.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result,indent=2));assert result['status']=='PASS'
