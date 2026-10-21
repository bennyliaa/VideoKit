"""Tester standalone integrity/archive review; never imports candidate code."""
from pathlib import Path
import hashlib,json,zipfile,stat
from datetime import datetime
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent;BASE=ROOT/'docs/coder/d1e2e'
EXPECTED='aa59420cff4153395af2ab9b97eb47d8f560e91763b730f47c0fda3c0578b66a'
def sha(b):return hashlib.sha256(b).hexdigest()
def save(n,v):(OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
seal=(BASE/'evidence/e2e-freeze.json').read_bytes();assert sha(seal)==EXPECTED
f=json.loads(seal);s=json.loads((BASE/'evidence/source-manifest.json').read_bytes())
assert len(f['immutableFiles'])==90 and len(s['files'])==73
entries=[]
for r in f['immutableFiles']+s['files']:
    p=ROOT/r['path'];assert p.resolve().is_relative_to(ROOT.resolve())
    assert not p.is_symlink() and not p.is_junction() and stat.S_ISREG(p.stat().st_mode)
    b=p.read_bytes();assert len(b)==r['bytes'] and sha(b)==r['sha256'],r['path']
    entries.append(r)
assert sha((BASE/'artifacts/E2E-source.zip').read_bytes())=='2a1202f2bba27d86f20f73af6fe286d5574e0575d67880eb865eb0644bc4db34'
with zipfile.ZipFile(BASE/'artifacts/E2E-source.zip') as z:
    assert len(z.namelist())==len(s['files']) and set(z.namelist())=={r['path'] for r in s['files']}
    for r in s['files']:assert sha(z.read(r['path']))==r['sha256']
for r in s['files']:
    p=ROOT/r['path'];dest=OUT/'frozen-sources'/Path(r['path']).relative_to('docs/coder/d1e2e')
    dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(p.read_bytes())
for p in (BASE/'evidence').glob('*.json'):(OUT/p.name).write_bytes(p.read_bytes())
for n in ('DELIVERY','EXECUTION_PLAN','EXECUTION_APPENDIX'):
    p=ROOT/f'docs/coder/D1_E2E_{n}_V1.0.md';(OUT/p.name).write_bytes(p.read_bytes())
assert not (BASE/'execution').exists() and not (BASE/'selfcheck').exists()
save('pre-execution-review.json',dict(at=datetime.now().astimezone().isoformat(),scope='Standalone hashes/ZIP/archival and source review, no candidate import or OS measurements',freezeSha256=EXPECTED,sourceFiles=73,immutableFiles=90,entries=entries,preparationAssertions=153,preparationAssertionsAreRuntimeProof=False,executionDirectoryBeforeRun=False,selfcheckDirectoryBeforeRun=False,productionCodeChanges=0,reviewedNewRuntimeFiles=['launch-once.py','e2e_admission.py','e2e_runtime.py','e2e_driver.py'],originalOrchestrationCompared=True,findings=[],conclusion='STATIC_ADMISSION_CLEAR; ONE_FORMAL_ATTEMPT_MUST_ENFORCE_FRESH_MEMORY_AFTER_NONREFUNDABLE_RESERVATION',actualRunInvocationsByThisAudit=0))
print('PASS: external seal, 90 immutable/73 source entries, ZIP and pre-run output absence; no experimental execution')
