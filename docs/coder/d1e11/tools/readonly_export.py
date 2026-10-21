"""Pin accepted LOCAL evidence and invoke frozen E10A export branch only. No device/deploy/SEAL."""
import hashlib,json,pathlib,subprocess
R=pathlib.Path(__file__).resolve().parents[4];B=R/'docs/coder/d1e11';M=R/'docs/tester/D1_E10A_EXECUTION/4f21f71a-bf66-4a44-a287-320f0ae25fde';REG=M/'registry'
if (B/'evidence/e11-freeze.json').exists():raise RuntimeError('FROZEN_READ_ONLY')
def sha(b):return hashlib.sha256(b).hexdigest()
def row(p):b=p.read_bytes();return dict(path=p.relative_to(R).as_posix(),bytes=len(b),sha256=sha(b))
def new(p,d):
 with p.open('x',encoding='utf-8') as f:json.dump(d,f,ensure_ascii=False,indent=2);f.write('\n')
report=R/'docs/tester/D1_E10A_FINAL_READONLY_REVIEW_REPORT_V1.0.md';assert sha(report.read_bytes())=='a597bca5c392aaf142f1fa5e74ab4a1aa869fb3cdc367df5005af54e335feaff'
inputs=json.loads((R/'docs/tester/D1_E10A_FINAL_READONLY_REVIEW_EVIDENCE/input-pins.json').read_bytes());files=inputs['allActuallyReadLocalFiles'];assert len(files)==688
for x in files:assert row(R/x['path'])==x,x['path']
manifest=M/'evidence/evidence-manifest.json';assert sha(manifest.read_bytes())=='e045e98bae54159c863f5ac01823cc5fc70c91591247681dc46f3cf917846726'
for x in json.loads(manifest.read_bytes())['files']:assert row(R/x['path'])==x,x['path']
catalog=(REG/'final.acceptance.json').read_bytes();assert len(catalog)==5853 and sha(catalog)=='27fe90573f2d8a3a750c270e760f4e19e797fe188287ade5c58268e8c6d911b7';cat=json.loads(catalog)['fields'];assert cat['head']=='6ce0f654a5bec6527a6773b141f64e49e858d3ef2e51c8c2e52360fd9ce0a4e5'
cfg=json.loads((M/'inputs/manager-config.json').read_bytes())['fields'];fields=dict(kind='activationTrust',plan=cfg['plan'],planSha=cfg['planSha'],authorization=cfg['authorization'],review=cfg['review'],registryPath=REG.as_posix(),head=cat['head'])
raw=('{"e9":1,"fields":'+json.dumps(fields,sort_keys=True,separators=(',',':'))+'}\n').encode('ascii');target=B/'source-export/activation-trust.json'
with target.open('xb') as f:f.write(raw)
argv=['D:/Android/Android Studio/jbr/bin/java.exe','-cp',str(R/'docs/coder/d1e10a/artifacts/D1-20261018-E10A/final/e10a-host-tools.jar'),'com.videokit.spike.e4.E9HostActivationSession','--approved-export',str(target),sha(raw),str(B/'source-export/original-export')]
new(B/'evidence/export-invocation.json',dict(argv=argv,config=row(target),sourceCatalog=row(REG/'final.acceptance.json'),acceptedFinalReview=row(report),independentInputPinsVerified=len(files),deviceCalls=0))
with (B/'evidence/export.stdout.txt').open('xb') as stdout,(B/'evidence/export.stderr.txt').open('xb') as stderr:
 process=subprocess.Popen(argv,stdout=stdout,stderr=stderr)
 try:code=process.wait(timeout=20)
 except subprocess.TimeoutExpired:new(B/'evidence/export-pending.json',dict(pid=process.pid,state='PENDING_ORIGINAL_PROCESS_RETAINED_NO_KILL'));raise
assert code==0,code
before=json.loads((B/'evidence/original-registry-before-export.json').read_bytes())['files'];after=[row(p) for p in sorted(REG.rglob('*')) if p.is_file()];assert before==after
assert (B/'source-export/original-export/final.acceptance.json').read_bytes()==catalog
new(B/'evidence/export-results.json',dict(status='PASS',exitCode=code,originalRegistryFiles=len(after),originalRegistryUnchanged=True,independentInputPinsVerified=len(files),executionManifestItems=len(json.loads(manifest.read_bytes())['files']),deviceCalls=0,scope='Existing frozen original exporter; readonly original Registry calls, NEW output folder only; no deployment/SEAL'))
print('PASS existing production readonly export:5853B actual catalog;original registry unchanged')
