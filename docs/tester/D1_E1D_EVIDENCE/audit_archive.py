"""Independent static/archival review. Does not import or run candidate modules."""
from pathlib import Path
import ast,hashlib,json,re,struct,zipfile,zlib
from datetime import datetime
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent;BASE=ROOT/'docs/coder/d1e1d'
def digest(raw):return hashlib.sha256(raw).hexdigest()
def save(n,v):(OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
freeze_raw=(BASE/'evidence/freeze-summary.json').read_bytes();freeze=json.loads(freeze_raw);source=json.loads((BASE/'evidence/source-manifest.json').read_bytes())
assert digest(freeze_raw)=='53feba0c78fac9a27f4b1c045f925d5db432b46ed8d1ebbbccdc89333f638186'
assert digest((BASE/'artifacts/E1D-source.zip').read_bytes())=='d5123e6527b6fbd613e7df565319bf14e8c8d6eeaba028e4474c35480c54ca9a'
audited=[]
for r in freeze['files']+freeze['selfcheckFiles']+source['files']:
 p=ROOT/r['path'];assert p.resolve().is_relative_to(ROOT.resolve());data=p.read_bytes()
 assert len(data)==r['bytes'] and digest(data)==r['sha256'],r['path']
 audited.append(dict(path=r['path'],sha256=r['sha256'],bytes=len(data)))
with zipfile.ZipFile(BASE/'artifacts/E1D-source.zip') as z:
 assert set(z.namelist())=={r['path'] for r in source['files']}
 for r in source['files']:assert digest(z.read(r['path']))==r['sha256']
for r in source['files']:
 p=ROOT/r['path'];dest=OUT/'frozen-sources'/Path(r['path']).relative_to('docs/coder/d1e1d');dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(p.read_bytes())
for rel in ['evidence/freeze-summary.json','evidence/source-manifest.json','manifest/branches.json','evidence/audit.json','evidence/selfcheck-1792162234030690200.json','evidence/targeted-1792162366628428500.json']:
 p=BASE/rel;(OUT/p.name).write_bytes(p.read_bytes())
for name in ['D1_E1D_DELIVERY_V1.0.md','D1_E1D_IMPLEMENTATION_BOUNDARY_V1.0.md','D1_E1D_EXECUTION_APPENDIX_V1.0.md']:
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
save('archive-and-manifest-audit.json',dict(at=datetime.now().astimezone().isoformat(),scope='Independent hashes/ZIP/AST only, no experimental execution',freezeSha256=digest(freeze_raw),sourceZipSha256=digest((BASE/'artifacts/E1D-source.zip').read_bytes()),sourceFiles=len(source['files']),frozenFiles=len(freeze['files']),selfcheckFiles=len(freeze['selfcheckFiles']),allCheckedEntries=audited,entries=entries,controlQueryTimeMatchesR4=True,experimentEnabled=False))
w=json.loads((BASE/'evidence/selfcheck-1792162234030690200.json').read_bytes())['witness'];run=BASE/'selfcheck'/w['root'];raw=(run/w['precloseSummary']).read_bytes();assert digest(raw)==w['precloseSummarySha'];pre=json.loads(raw);(OUT/'result-before-close.json').write_bytes(raw)
assert [r['branch'] for r in pre['rows']]==['PF']+manifest['executionOrder']
snapshots={};row_usage={};unresolved=[]
for task in sorted({r['task'] for r in manifest['branches']}|{'PF'}):
 candidates=[]
 for slot in [0,1]:
  p=run/task/f'state{slot}.slot'
  if not p.exists():continue
  raw=p.read_bytes();assert len(raw)==8192;seq,n,_=struct.unpack('<qiI',raw[:16]);assert seq>0 and 0<=n<=8144
  payload=raw[48:48+n];assert digest(raw[:16]+payload)==raw[16:48].hex();d=zlib.decompressobj();data=d.decompress(payload,65537);assert d.eof and len(data)<=65536
  state=json.loads(data);assert (state['schema'],state['batch'],state['task'])==(3,run.name,task);candidates.append((seq,state))
  for row,u in state['usage'].items():
   old_u=row_usage.setdefault(row,{k:0 for k in u})
   for k,v in u.items():old_u[k]=max(old_u[k],v)
 assert candidates,task
 snapshots[task]=max(candidates,key=lambda x:x[0])[1]
 for cid,c in snapshots[task]['commands'].items():
  if c['status']!='DONE':unresolved.append(dict(task=task,command=cid,status=c['status']))
inventory=snapshots['PF']['inventory'];assert set(inventory)==set(snapshots) and len(inventory)==32
for row in manifest['branches']:
 p=run/'events'/f'{row["id"]}.q'
 if not p.exists():continue
 events=[json.loads(line) for line in p.read_bytes().splitlines()];assert all((e['batch'],e['task'],e['row'])==(run.name,row['task'],row['id']) for e in events)
 u=row_usage.setdefault(row['id'],{k:0 for k in w['usage']});u['qn']=max(u['qn'],sum(e['new'] for e in events));u['qr']=max(u['qr'],sum(not e['new'] for e in events))
total={k:sum(u[k] for u in row_usage.values()) for k in w['usage']};assert total==w['usage']
target=json.loads((BASE/'evidence/targeted-1792162366628428500.json').read_bytes());assert target['assertions']==414 and w['assertions']==159
save('archived-evidence-review.json',dict(scope='Independent decoding of existing producer evidence, not re-run',integrationAssertions=159,targetedAssertions=414,total=573,targetGroups=[dict(scope=g['scope'],assertions=g['assertions'],status=g['status']) for g in target['groups']],recordCount=32,inventoryTasks=sorted(inventory),usage=total,unresolvedSnapshotCommands=unresolved,S17=snapshots['S17'],precloseSha256=w['precloseSummarySha'],outerCloseProof=w['logClose'],privateCells=w['privateCells'],metadata={k:v for k,v in w.items() if k.startswith('metadata')},managedResourcePeaks=w['ledgerPeaks'],realMedia=False))
anchors={}
for p in (BASE/'src').glob('*.py'):
 anchors[p.name]=[dict(line=i,text=s) for i,s in enumerate(p.read_text(encoding='utf-8').splitlines(),1) if re.search(r'complete_source_response|set_result|set_exception|def (seal|gate|end|private_cell|ready|exact_write|transaction)|consumer\[|globalFence|_merge_usage|minimumUsage|inventory|ensure_writable',s)]
save('source-anchors.json',anchors)
print(json.dumps(dict(integrity='PASS',sourceFiles=len(source['files']),frozenFiles=len(freeze['files']),selfcheckFiles=len(freeze['selfcheckFiles']),records=32,producerChecks=573,ownFunctionalTests=0),ensure_ascii=False))

