"""Check final evidence consistency and produce an exact, scoped vulnerability appendix."""
from pathlib import Path
import json,sys,re,hashlib
root=Path(sys.argv[1]).resolve();e=root/'docs/coder/d1c02/evidence';docs=root/'docs/coder'
def read(p):
    raw=p.read_bytes()
    return raw.decode('utf-16' if raw.startswith((b'\xff\xfe',b'\xfe\xff')) else 'utf-8-sig')
def load(name):return json.loads(read(e/name))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
supply=load('supply-inventory.json');vuln=load('osv-results.json');apks=load('apk-audit.json')['apks'];checks={}
checks['license_metadata_missing_zero']=not supply['missing_license_claims']
checks['osv_success_and_exact_final_graph']=vuln['status']=='PASS_QUERY_COMPLETED' and {(x['coordinate'],x['scope']) for x in supply['components']}=={(x['coordinate'],x['scope']) for x in vuln['results']}
checks['c01_and_media_integrity']=load('integrity-check.json')['status']=='PASS'
checks['apk_copy_hashes']=all(sha(root/x['path'])==x['sha256'] for x in apks)
delivery=read(docs/'D1_DELIVERY_D1-20261005-C02.md');request=read(docs/'D1_DEVICE_TEST_REQUEST_V1.0.md')
checks['delivery_hashes']=all(x['sha256'] in delivery for x in apks)
checks['device_request_hashes']=all(x['sha256'] in request for x in apks if 'release' not in x['path'])
checks['no_media_weights_internet_in_apks']=all(not x['sample_named_entries'] and not x['model_entries'] and not x['internet_permission'] for x in apks)
checks['release_excludes_c02']=all(not x['c02_dex'] for x in apks if 'release' in x['path'])
checks['selfcheck_47_pass']='RESULT assertions=47 failures=0' in read(e/'contract-probe.log')
checks['tracking_five_synthetic_pass']=read(e/'traditional-tracking.log').count('PASS ')==5
checks['final_build_pass']='BUILD SUCCESSFUL' in read(e/'final-cluster-build.log')
checks['strict_offline_build_pass']='BUILD SUCCESSFUL' in read(e/'strict-offline-build.log')
checks['no_37_2_range_warning']='37.2' not in read(e/'final-cluster-build.log')
methods=re.findall(r'@Test public void (\w+)\(',read(root/'docs/coder/d1c02/device/com/videokit/spike/c02/C02DeviceTests.java'))
checks['twelve_device_methods_prepared']=len(methods)==12
checks['python_tools_compile']=True
for p in (root/'docs/coder/d1c02/tools').glob('*.py'):compile(read(p),str(p),'exec')
components={x['coordinate']:x for x in supply['components']};lines=['# C02 exact vulnerability matches','Query completion is not a vulnerability-free or reachability verdict. Full raw results: osv-results.json. All matches below are tool/compile/test-only in the final locked graph.']
for row in vuln['results']:
    if not row['vulnerabilities']:continue
    lines+=['\n## '+row['coordinate'],'Scope: '+row['scope'],'Configurations: '+', '.join(components[row['coordinate']]['configurations'])]
    for entry in row['vulnerabilities']:
        identifier=entry['id'];lines+=['- ['+identifier+'](https://osv.dev/vulnerability/'+identifier+')']
(e/'VULNERABILITY_MATCHES.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
result={'candidateId':'D1-20261005-C02','status':'PASS' if all(checks.values()) else 'FAIL','checks':checks,'device_test_methods':methods,'device_execution':'NOT_RUN','scope':'evidence consistency checks only; not D1 acceptance'}
(e/'candidate-self-review.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result,indent=2))
if result['status']!='PASS':raise SystemExit(1)
