"""Independent static/archival review. Does not import or run candidate modules."""
from pathlib import Path
import ast,hashlib,json,re,struct,zipfile,zlib
from datetime import datetime
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent;BASE=ROOT/'docs/coder/d1e2c'
def digest(raw):return hashlib.sha256(raw).hexdigest()
def save(n,v):(OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
freeze_raw=(BASE/'evidence/freeze-summary.json').read_bytes();freeze=json.loads(freeze_raw);source=json.loads((BASE/'evidence/source-manifest.json').read_bytes())
assert digest(freeze_raw)=='bccacb2e98b1f4a4d3017fc8efb9bd0f047e58d91e7c910303fff40eb3896179'
assert digest((BASE/'artifacts/E2C-source.zip').read_bytes())=='035263006cbaa99837656bb2b66045a3f5c6181ab8af8c8fe3f5bcf5ba3e5934'
audited=[]
for r in freeze['files']+freeze['selfcheckFiles']+source['files']:
 p=ROOT/r['path'];assert p.resolve().is_relative_to(ROOT.resolve());data=p.read_bytes()
 assert len(data)==r['bytes'] and digest(data)==r['sha256'],r['path']
 audited.append(dict(path=r['path'],sha256=r['sha256'],bytes=len(data)))
with zipfile.ZipFile(BASE/'artifacts/E2C-source.zip') as z:
 assert set(z.namelist())=={r['path'] for r in source['files']}
 for r in source['files']:assert digest(z.read(r['path']))==r['sha256']
for r in source['files']:
 p=ROOT/r['path'];dest=OUT/'frozen-sources'/Path(r['path']).relative_to('docs/coder/d1e2c');dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(p.read_bytes())
for rel in ['evidence/freeze-summary.json','evidence/source-manifest.json','manifest/branches.json','evidence/audit.json','evidence/g-lifecycle-1792172968097380400.json','evidence/targeted-1792173615310105000.json']:
 p=BASE/rel;(OUT/p.name).write_bytes(p.read_bytes())
for name in ['D1_E2C_DELIVERY_V1.0.md','D1_E2C_RESOURCE_LIFECYCLE_V1.0.md','D1_E2C_EXECUTION_APPENDIX_V1.0.md']:
 p=ROOT/'docs/coder'/name;(OUT/name).write_bytes(p.read_bytes())
manifest=json.loads((BASE/'manifest/branches.json').read_bytes());prior=json.loads((ROOT/'docs/tester/D1_R4_EVIDENCE/control-and-budget-audit.json').read_bytes());old={r['branch']:r for r in prior['rows']}
def symbols(p):
 out=[]
 for n in ast.parse(p.read_text(encoding='utf-8')).body:
  if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)):out.append(n.name)
  if isinstance(n,ast.ClassDef):out.extend(n.name+'.'+x.name for x in n.body if isinstance(x,(ast.FunctionDef,ast.AsyncFunctionDef)))
 return out
entries=[]
for row in manifest['branches']:
 prev=old[row['id']];assert (row['nonquery'],row['queriesNew'],row['queriesReplay'],row['seconds'])==(prev['N'],prev['queryNew'],prev['queryReplay'],prev['seconds'])
 assert len(row['operations'])==row['nonquery']
 for group in [row['entry']]+[x['entry'] for x in row['operations']]:
  for entry in group.split(' + '):
   rel,sym=entry.split(':',1);assert sym in symbols(BASE/rel),(row['id'],entry)
   entries.append(dict(branch=row['id'],entry=entry,exists=True))
assert len(manifest['branches'])==61 and not manifest['experimentEnabled']
save('archive-and-manifest-audit.json',dict(at=datetime.now().astimezone().isoformat(),scope='Independent hashes/ZIP/AST only, no experimental execution',freezeSha256=digest(freeze_raw),sourceZipSha256=digest((BASE/'artifacts/E2C-source.zip').read_bytes()),sourceFiles=len(source['files']),frozenFiles=len(freeze['files']),selfcheckFiles=len(freeze['selfcheckFiles']),allCheckedEntries=audited,entries=entries,controlQueryTimeMatchesR4=True,experimentEnabled=False))

print('PASS: independent frozen hashes, ZIP, 61 entry symbols and R4 allocations; no execution')
