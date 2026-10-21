"""Independent byte/JSON/AST review; never imports candidate code or samples OS."""
from pathlib import Path
import ast, hashlib, json, zipfile
from datetime import datetime
ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
BASE=ROOT/'docs/coder/d1e2d'
def sha(b): return hashlib.sha256(b).hexdigest()
def read(p): return json.loads(p.read_bytes())
def save(n,v): (OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
f=read(BASE/'evidence/freeze-summary.json'); s=read(BASE/'evidence/source-manifest.json')
assert sha((BASE/'evidence/freeze-summary.json').read_bytes())=='f0a3e8fc9ae7e6e8c3def52d0002d23af77212ad35cb016a612e34e45f42de1b'
assert sha((BASE/'artifacts/E2D-source.zip').read_bytes())=='6c6eef8c0d9541aefe1eb807a312d1fce7ba968038c127e565af9becd7ccf9d8'
checked=[]
for r in f['files']+f['selfcheckFiles']+s['files']:
    p=ROOT/r['path']; assert p.resolve().is_relative_to(ROOT.resolve())
    b=p.read_bytes(); assert len(b)==r['bytes'] and sha(b)==r['sha256'],r['path']
    checked.append(r)
with zipfile.ZipFile(BASE/'artifacts/E2D-source.zip') as z:
    assert set(z.namelist())=={r['path'] for r in s['files']}
    for r in s['files']: assert sha(z.read(r['path']))==r['sha256']
for r in s['files']:
    dest=OUT/'frozen-sources'/Path(r['path']).relative_to('docs/coder/d1e2d')
    dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes((ROOT/r['path']).read_bytes())
for p in (BASE/'evidence').glob('*.json'): (OUT/p.name).write_bytes(p.read_bytes())
for name in ['DELIVERY','G_OS_COMPARISON','EXECUTION_APPENDIX']:
    p=ROOT/f'docs/coder/D1_E2D_{name}_V1.0.md';(OUT/p.name).write_bytes(p.read_bytes())
binding=read(BASE/'evidence/production-binding.json')
assert len(binding['files'])==37
for r in binding['files']:
    for base in [BASE,ROOT/'docs/coder/d1e2c']:
        b=(base/r['path']).read_bytes();assert len(b)==r['bytes'] and sha(b)==r['sha256']
manifest=read(BASE/'manifest/branches.json')
prior=read(ROOT/'docs/tester/D1_R4_EVIDENCE/control-and-budget-audit.json')
old={r['branch']:r for r in prior['rows']}
def symbols(p):
    out=[]
    for n in ast.parse(p.read_text(encoding='utf-8')).body:
        if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)):out.append(n.name)
        if isinstance(n,ast.ClassDef):out.extend(n.name+'.'+x.name for x in n.body if isinstance(x,(ast.FunctionDef,ast.AsyncFunctionDef)))
    return out
entries=[]
for row in manifest['branches']:
    prev=old[row['id']]
    assert (row['nonquery'],row['queriesNew'],row['queriesReplay'],row['seconds'])==(prev['N'],prev['queryNew'],prev['queryReplay'],prev['seconds'])
    assert len(row['operations'])==row['nonquery']
    for group in [row['entry']]+[x['entry'] for x in row['operations']]:
        for entry in group.split(' + '):
            rel,sym=entry.split(':',1);assert sym in symbols(BASE/rel)
            entries.append({'branch':row['id'],'entry':entry})
assert len(manifest['branches'])==61 and not manifest['experimentEnabled']
g=read(BASE/'evidence/g-comparison-1792174935530529100.json')
assert sha((BASE/'evidence/g-comparison-1792174935530529100.json').read_bytes())=='9180cf6fe2b8358d2c3ccdc5a23ce85fbf7b5cda6148ea1da8b98bf7a279667a'
assert len(g['stages'])==6
rows=[]
for i,stage in enumerate(g['stages']):
    refs=stage['referencesBeforeOSQuery']; prod=refs['production']; metrics=stage['metrics']
    assert metrics['handles']==[160,164,161,193,161,161][i]
    assert metrics['threads']==6 and metrics['privateBytes']==18104320
    assert refs['weakCellsAlive']==[0,1,0,8,0,0][i]
    assert refs['weakFuturesAlive']==[0,1,1,9,1,1][i]
    assert refs['weakClosuresAlive']==[0,2,0,16,0,0][i]
    assert prod['total']==[0,1,1,9,9,9][i] and prod['active']==[0,1,0,8,0,0][i]
    assert prod['archived']==[0,0,1,1,9,9][i]
    assert refs['probeAuditCopyCount']==[0,0,1,1,9,0][i]
    assert stage['identity']==g['stages'][0]['identity'] and stage['limitExceedances']==[]
    assert stage['sampleDeadlineMet'] and stage['sampleDurationSeconds']<=0.1
    if i: assert refs['externalFutures']==1
    if i>=2: assert refs['externalFirstOriginalResultStable']
    rows.append(dict(stage=stage['stage'],handles=metrics['handles'],references=refs))
assert len(g['consumptionProofs'])==9
for p in g['consumptionProofs']: assert all(v is True for k,v in p.items() if k!='operation')
n=g['nativeReader'];assert (n['cycles'],n['identityQueries'],n['openedHandles'],n['closedHandles'],n['maximumOwnedHandlesObserved'])==(6,1,13,13,1)
assert not n['closeUnknown'] and not n['observerCreditHeld']
assert g['noInFlight'] and g['remainingResources']=={} and g['remainingBuffers']==0
assert g['externalFutureHeldThroughClosure'] and g['externalFirstOriginalResultStableAfterClosure']
assert g['elapsedSeconds']<=60
save('independent-audit.json',dict(at=datetime.now().astimezone().isoformat(),scope='Only byte hashes, ZIP, JSON and AST; no candidate imports or execution; no OS samples',sourceFiles=63,frozenFiles=32,selfcheckFiles=0,checkedEntries=checked,productionBoundFiles=37,entrySymbols=entries,manifestDisabled=True,stageChecks=rows,smallProbeOnly=True,actualFullRunByTester=False,newBlockingFindings=[]))
print('PASS: independent 95 entry hashes, ZIP, 37 production bindings, 61 rows, six recorded stages; no experimental execution')
