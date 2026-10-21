"""Standalone static/archival review. No candidate imports, negatives or runtime."""
from pathlib import Path
from datetime import datetime
import hashlib,json,zipfile,ast
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent;BASE=ROOT/'docs/coder/d1e2f'
def sha(b):return hashlib.sha256(b).hexdigest()
def read(p):return json.loads(p.read_bytes())
def save(n,v):(OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
f=read(BASE/'evidence/freeze-summary.json');s=read(BASE/'evidence/source-manifest.json')
assert sha((BASE/'evidence/freeze-summary.json').read_bytes())=='1a73391a12f9473f661a5e62204218d5a875031f064bb12af262529c4e866dee'
assert sha((BASE/'artifacts/E2F-source.zip').read_bytes())=='a7c09e34a5ccf6a3c980299a6fb0484792ca6496bc52b3bc08f73160ed72c4a5'
assert len(f['files'])==98 and len(s['files'])==79
checked=[]
for r in f['files']:
    p=ROOT/r['path'];assert p.resolve().is_relative_to(ROOT.resolve()) and not p.is_symlink() and not p.is_junction()
    b=p.read_bytes();assert len(b)==r['bytes'] and sha(b)==r['sha256'];checked.append(r)
with zipfile.ZipFile(BASE/'artifacts/E2F-source.zip') as z:
    assert len(z.namelist())==79 and set(z.namelist())=={r['path'] for r in s['files']}
    for r in s['files']:assert sha(z.read(r['path']))==r['sha256']
for r in s['files']:
    p=ROOT/r['path'];dest=OUT/'frozen-sources'/Path(r['path']).relative_to('docs/coder/d1e2f')
    dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(p.read_bytes())
for p in (BASE/'evidence').glob('*.json'):(OUT/p.name).write_bytes(p.read_bytes())
p=BASE/'reevaluation/evidence-reevaluation.json';(OUT/p.name).write_bytes(p.read_bytes())
for n in ('DELIVERY','EVIDENCE_REEVALUATION','EXECUTION_APPENDIX'):
    p=ROOT/f'docs/coder/D1_E2F_{n}_V1.0.md';(OUT/p.name).write_bytes(p.read_bytes())
old=ROOT/'docs/coder/d1e2e'
for p,expected in [(old/'evidence/e2e-freeze.json','aa59420cff4153395af2ab9b97eb47d8f560e91763b730f47c0fda3c0578b66a'),(old/'execution/result-manifest.json','baa6a1ed87764a5d16b1d282717824110d0082bc188606edf4affb33377750ea'),(ROOT/'docs/tester/D1_E2E_ACTUAL_REGRESSION_REPORT_V1.0.md','bb1042940d9c6376bf019c73d95c7001a6887feddc998fe834cffd968c65a2d3')]:assert sha(p.read_bytes())==expected
result=read(BASE/'reevaluation/evidence-reevaluation.json');checks=read(BASE/'evidence/offline-checks.json')
assert checks['assertions']==len(checks['checks'])==452 and checks['status']=='PASS'
assert result['scope']=='EVIDENCE_REEVALUATION' and result['decision']=='SUPPORTED_ORIGINAL_TOOL_FACTS' and result['accepted']
assert result['completion']['accepted'] and result['resources']['accepted']
assert result['originalResult']['driverStatus']==result['originalResult']['launcherStatus']=='FAIL'
assert result['originalResult']['assertions']==160 and result['originalResult']['originalGExitCode']==2 and result['originalResult']['originalToolExitCode']==1
assert result['originalResult']['reservationConsumed'] and all(v==0 for k,v in result['activity'].items() if type(v) is int)
assert not (BASE/'execution').exists() and not (BASE/'selfcheck').exists()
for name in ['completion_evaluation.py','resource_evaluation.py','e2f_wrapper.py','evidence_io.py','reevaluate.py']:
    tree=ast.parse((BASE/'tools'/name).read_text(encoding='utf-8'))
    imports={alias.name.split('.')[0] for n in ast.walk(tree) if isinstance(n,ast.Import) for alias in n.names}|{n.module.split('.')[0] for n in ast.walk(tree) if isinstance(n,ast.ImportFrom) and n.module}
    assert not imports & {'gengine','gcore','authority','notifications','runtime_metrics','runtime_wiring','controller','scenarios','phases','subprocess','ctypes','threading','concurrent'}
save('independent-package-audit.json',dict(at=datetime.now().astimezone().isoformat(),scope='Standalone bytes/ZIP/AST/recorded negative evidence; no candidate imports or rerun',sourceFiles=79,immutableFiles=98,checked=checked,recordedOfflineAssertions=452,recordedNegativeCases=len(checks['negativeCases']),negativeRerun=False,originalE2EFailUnchanged=True,originalTesterReportUnchanged=True,findings=[],fixtureBytes=0,newActualAttempts=0,newOSMetricSamples=0))
print('PASS: 98 immutable/79 sources, ZIP, original E2E/report identities, offline negative records and no runtime imports')
