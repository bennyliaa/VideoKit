"""Independent package hashes/archive/diff only. Never imports candidate modules."""
from pathlib import Path
import hashlib,json,zipfile,difflib
from datetime import datetime
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent;BASE=ROOT/'docs/coder/d1e3'
def sha(b):return hashlib.sha256(b).hexdigest()
def read(p):return json.loads(p.read_bytes())
def save(n,v):(OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
seal=(BASE/'evidence/e3-freeze.json').read_bytes();f=json.loads(seal);s=read(BASE/'evidence/source-manifest.json')
assert sha(seal)=='7f5c4bda5189f056c089695adc5a94eab31b221db821218bb49bd2ea5222d709'
assert len(s['files'])==54 and len(f['immutableFiles'])==90 and len(f['runtimeFiles'])==65
for r in f['immutableFiles']+f['selfcheckFiles']:
    p=ROOT/r['path'];assert p.resolve().is_relative_to(ROOT.resolve()) and not p.is_symlink() and not p.is_junction()
    b=p.read_bytes();assert len(b)==r['bytes'] and sha(b)==r['sha256'],r['path']
assert sha((BASE/'artifacts/E3-source.zip').read_bytes())=='aa966284378778d799d473446e744a939a5b83817c867fce13eaea96b84902e7'
with zipfile.ZipFile(BASE/'artifacts/E3-source.zip') as z:
    assert len(z.namelist())==54 and set(z.namelist())=={r['path'] for r in s['files']}
    for r in s['files']:assert sha(z.read(r['path']))==r['sha256']
for r in s['files']:
    p=ROOT/r['path'];dest=OUT/'frozen-sources'/Path(r['path']).relative_to('docs/coder/d1e3')
    dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(p.read_bytes())
for p in (BASE/'evidence').glob('*.json'):(OUT/p.name).write_bytes(p.read_bytes())
for name in ('DELIVERY','REAL_IO_EXECUTION_PLAN','EXECUTION_APPENDIX'):
    p=ROOT/f'docs/coder/D1_E3_{name}_V1.0.md';(OUT/p.name).write_bytes(p.read_bytes())
changes=[];diff=[]
for p in (BASE/'src').rglob('*'):
    if not p.is_file():continue
    rel=p.relative_to(BASE/'src');old=ROOT/'docs/coder/d1e2f/src'/rel
    if not old.exists() or old.read_bytes()!=p.read_bytes():
        changes.append(str(rel));diff+=list(difflib.unified_diff(old.read_text(encoding='utf-8').splitlines(keepends=True) if old.exists() else [],p.read_text(encoding='utf-8').splitlines(keepends=True),fromfile='E2F/'+str(rel),tofile='E3/'+str(rel)))
(OUT/'production-diff.txt').write_text(''.join(diff),encoding='utf-8')
assert not (BASE/'execution').exists() and not (BASE/'runs').exists()
save('independent-package-audit.json',dict(at=datetime.now().astimezone().isoformat(),sourceFiles=54,immutableFiles=90,runtimeFiles=65,changedProductionFiles=changes,codeImport=False,mediaStat=False,mediaRead=False,testsRerun=False,newExecution=False,reservationConsumed=False))
print(json.dumps(dict(integrity='PASS',changedProductionFiles=changes,diffLines=len(diff)),ensure_ascii=False))
