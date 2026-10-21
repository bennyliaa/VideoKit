import collections,hashlib,json,pathlib,re,struct,zipfile
R=pathlib.Path(r'D:\CodexProjects\VideoKit');B=pathlib.Path(__file__).resolve().parent;E=R/'docs/coder/d1c09/evidence'
def sha(data):return hashlib.sha256(data).hexdigest()
assert sha((E/'freeze-summary.json').read_bytes())=='cdc48afed4f10e38fca5ad5efaf3fb4602947acc2166caa1f08d255bb89ce4fa'
assert sha((R/'docs/coder/d1c09/artifacts/D1-20261016-C09/D1-20261016-C09-source.zip').read_bytes())=='7551a6bb0fc94cf0d66a65b4b027925ec85c17e19d03a796b072eaaa31e3af28'
def check(row):
 data=(R/row['path']).read_bytes();assert len(data)==row['bytes'] and sha(data)==row['sha256'],row['path']
m=json.loads((E/'ffmpeg-object-source-license-map.json').read_text())
for row in m['objects']:check(row['object']);check(row['dependency_file'])
for row in m['files']:check(row)
assert len(m['objects'])==266 and len(m['files'])==608 and not m['gpl_header_violations']
admission=json.loads((E/'ffmpeg-admission.json').read_text());assert admission['version']=='8.0.3'
config=(R/'docs/coder/d1c09/outputs/ffmpeg-build/config.h').read_text()
for k in ['GPL','NONFREE','VERSION3','NETWORK']:assert re.search(r'^#define CONFIG_'+k+r' 0$',config,re.M)
assert '#define MALLOC_PREFIX vk_c09_' in config
security=json.loads((E/'ffmpeg-security-coverage.json').read_text());patches=security['official_patch_checks'];assert len(patches)==8
iamf=(R/'docs/coder/d1c09/upstream/source/ffmpeg-8.0.3/libavformat/iamf_parse.c').read_text()
start=iamf.index('static int scalable_channel_layout_config(');end=iamf.find('\nstatic ',start+1);function=iamf[start:end if end!=-1 else None]
assert 'if (k != audio_element->nb_substreams)' in function
assert 'if (i && ch_layout.nb_channels <= audio_element->element->layers[i-1]->ch_layout.nb_channels)' in function
for row in patches:check(row['patch']);assert row['all_added_lines_present']
apk_audit=json.loads((E/'apk-audit.json').read_text());native=0;notices=0
for apk in apk_audit['apks']:
 data=(R/apk['path']).read_bytes();assert sha(data)==apk['sha256']
 with zipfile.ZipFile(R/apk['path']) as z:
  for row in apk['native_libraries']:
   raw=z.read(row['path']);assert len(raw)==row['bytes'] and sha(raw)==row['sha256']
   zi=z.getinfo(row['path']);offset=zi.header_offset;name,extra=struct.unpack_from('<HH',data,offset+26);actual=offset+30+name+extra
   assert zi.compress_type==0 and actual%16384==0
   if raw[4]==2:
    phoff=struct.unpack_from('<Q',raw,32)[0];size,num=struct.unpack_from('<HH',raw,54);fmt='<IIQQQQQQ'
   else:
    assert raw[4]==1;phoff=struct.unpack_from('<I',raw,28)[0];size,num=struct.unpack_from('<HH',raw,42);fmt='<IIIIIIII'
   loads=[struct.unpack_from(fmt,raw,phoff+i*size) for i in range(num)];assert all(p[7]>=16384 for p in loads if p[0]==1)
   native+=1
  if apk['file']=='app-debug.apk':
   for name in z.namelist():
    if name.startswith('assets/licenses/'):
     assert z.read(name)==(R/'docs/coder/d1c09/notice-assets/licenses'/pathlib.Path(name).name).read_bytes();notices+=1
  if apk['file']=='app-release-unsigned.apk':assert apk['sha256']=='71aa8b8b25e1e94d14a6f2939b536b71eea6d043974397120fafad35ebc5f03e'
with zipfile.ZipFile(R/'docs/coder/d1c09/artifacts/D1-20261016-C09/D1-20261016-C09-source.zip') as z:
 for name in z.namelist():
  if name.endswith(('/C09CpuDeviceTests.java','/C09DeviceTests.java','/C09IsolatedDeviceTests.java','/DeviceFixtures.java','/CpuTaskClient.java','/CpuIsolatedService.java','/CpuProtocol.java','/native/cpu.c','/native/quota.c')):
   (B/pathlib.Path(name).name).write_bytes(z.read(name))
result=dict(result='DEBUG_G01_STATIC_REVIEW_PASS',objects=266,sourceDependencies=608,licenseClassificationCounts=dict(collections.Counter(r['classification'] for r in m['files'])),patches=8,iamfTwoGuardsIndependentlyChecked=True,apkNativeEntriesVerified=native,packagedLicenseAssetsVerified=notices,productAdmission='NOT_APPROVED',runtime='NOT_RUN',notes=['object-map scope string says 267 but actual array and current admission say 266; report actual count','GPG frozen receipts inspected, not rerun','No claim of exhaustive vulnerability or full product license clearance'])
(B/'admission-check.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(result,ensure_ascii=False,indent=2))
