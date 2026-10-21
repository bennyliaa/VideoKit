"""Independent archival/AST review only. Never imports or runs E1B modules/helpers."""
from pathlib import Path
import ast,hashlib,json,re,struct,zipfile,zlib
from datetime import datetime
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent;BASE=ROOT/'docs/coder/d1e1b'
def digest(b):return hashlib.sha256(b).hexdigest()
def save(n,v):(OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
freeze_data=(BASE/'evidence/freeze-summary.json').read_bytes()
assert digest(freeze_data)=='231782d7bf337d0c2b3a9062f9a2b92a107b6c870d03637ab8fb40fe433abbcb'
freeze=json.loads(freeze_data);source=json.loads((BASE/'evidence/source-manifest.json').read_bytes())
assert digest((BASE/'artifacts/E1B-source.zip').read_bytes())=='770d77af488f21f2cbc20456eefe8f81e5b2d93589c53336010a9843b50431e0'
audited=[]
for r in freeze['files']+freeze['selfcheckFiles']+source['files']:
 p=ROOT/r['path'];assert p.resolve().is_relative_to(ROOT.resolve())
 raw=p.read_bytes();assert len(raw)==r['bytes'] and digest(raw)==r['sha256'],r['path']
 audited.append(dict(path=r['path'],sha256=r['sha256'],bytes=len(raw)))
with zipfile.ZipFile(BASE/'artifacts/E1B-source.zip') as z:
 assert set(z.namelist())=={r['path'] for r in source['files']}
 for r in source['files']:assert digest(z.read(r['path']))==r['sha256']
for p in [BASE/'evidence/freeze-summary.json',BASE/'evidence/source-manifest.json',BASE/'manifest/branches.json',BASE/'evidence/negative-checks.json',BASE/'evidence/audit.json',BASE/'evidence/selfcheck-1792157499032096500.json']:
 (OUT/p.name).write_bytes(p.read_bytes())
for r in source['files']:
 p=ROOT/r['path'];dest=OUT/'frozen-sources'/Path(r['path']).relative_to('docs/coder/d1e1b')
 dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(p.read_bytes())
for name in ['D1_E1B_DELIVERY_V1.0.md','D1_E1B_IMPLEMENTATION_BOUNDARY_V1.0.md','D1_E1B_EXECUTION_APPENDIX_V1.0.md']:
 p=ROOT/'docs/coder'/name;(OUT/name).write_bytes(p.read_bytes())
manifest=json.loads((BASE/'manifest/branches.json').read_bytes());prior=json.loads((ROOT/'docs/tester/D1_R4_EVIDENCE/control-and-budget-audit.json').read_bytes());prior_by={r['branch']:r for r in prior['rows']}
assert len(manifest['branches'])==61
for row in manifest['branches']:
 old=prior_by[row['id']]
 assert (row['nonquery'],row['queriesReplay'],row['queriesNew'],row['seconds'])==(old['N'],old['queryReplay'],old['queryNew'],old['seconds'])
 assert len(row['operations'])==row['nonquery']
def symbols(p):
 tree=ast.parse(p.read_text(encoding='utf-8'));out=[]
 for node in tree.body:
  if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)):out.append(node.name)
  if isinstance(node,ast.ClassDef):
   out.append(node.name)
   out.extend(node.name+'.'+n.name for n in node.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)))
 return out
entry_audit=[]
for row in manifest['branches']:
 for composite in [row['entry']]+[o['entry'] for o in row['operations']]:
  for entry in composite.split(' + '):
   rel,symbol=entry.split(':',1);p=BASE/rel
   exists=symbol in symbols(p)
   entry_audit.append(dict(branch=row['id'],entry=entry,exists=exists))
   assert exists,(row['id'],entry)
save('archive-and-manifest-audit.json',dict(at=datetime.now().astimezone().isoformat(),scope='Independent file/hash/ZIP/AST checks, not execution',freezeSha256=digest(freeze_data),sourceZipSha256=digest((BASE/'artifacts/E1B-source.zip').read_bytes()),sourceFiles=len(source['files']),frozenFiles=len(freeze['files']),selfcheckFiles=len(freeze['selfcheckFiles']),allCheckedEntries=audited,manifestBranches=61,allR4ControlQueryTimeAllocationsMatch=True,entryAudit=entry_audit,experimentEnabled=manifest['experimentEnabled']))
evidence=json.loads((BASE/'evidence/selfcheck-1792157499032096500.json').read_bytes());w=evidence['witness'];run=BASE/'selfcheck'/w['root'];pre=(run/w['precloseSummary']).read_bytes();assert digest(pre)==w['precloseSummarySha']
(OUT/'result-before-close.json').write_bytes(pre)
summary=json.loads(pre);assert [r['branch'] for r in summary['rows']]==['PF']+manifest['executionOrder']
records=[];snapshots={};unresolved=[];usage={}
for task in sorted({r['task'] for r in manifest['branches']}|{'PF'}):
 candidates=[]
 for slot in [0,1]:
  p=run/task/f'state{slot}.slot'
  if not p.exists():continue
  raw=p.read_bytes();assert len(raw)==8192
  seq,n,_=struct.unpack('<qiI',raw[:16]);assert seq>0 and 0<=n<=8144;packed=raw[48:48+n]
  assert digest(raw[:16]+packed)==raw[16:48].hex()
  d=zlib.decompressobj();decoded=d.decompress(packed,65537);assert len(decoded)<=65536 and d.eof
  state=json.loads(decoded);assert state['schema']==2 and state['batch']==run.name and state['task']==task
  candidates.append((seq,state))
 seq,state=max(candidates,key=lambda x:x[0]);snapshots[task]=state
 records.append(dict(task=task,sequence=seq,commandCount=len(state['commands']),objectCount=len(state['objects'])))
 for cid,c in state['commands'].items():
  if c['status']!='DONE':unresolved.append(dict(task=task,command=cid,status=c['status']))
 for row,u in state['usage'].items():
  if row in usage:assert row=='GC'
  old=usage.get(row,{k:0 for k in u});usage[row]={k:max(old[k],u[k]) for k in u}
raw_snapshot_usage={k:sum(u[k] for u in usage.values()) for k in w['usage']}
for row in manifest['branches']:
 p=run/'events'/f'{row["id"]}.q'
 if not p.exists():continue
 events=[json.loads(line) for line in p.read_bytes().splitlines()]
 usage.setdefault(row['id'],{k:0 for k in w['usage']})
 usage[row['id']]['qn']=sum(bool(e['new']) for e in events)
 usage[row['id']]['qr']=sum(not e['new'] for e in events)
total={k:sum(u[k] for u in usage.values()) for k in w['usage']}
assert total==w['usage']
query_events={}
for branch in ['P08-LATEOPEN','P09-CANCEL','P09-TIMEOUT','P10-C','Q07-TAKEFIRST','Q06-LOST']:
 p=run/'events'/f'{branch}.q';events=[json.loads(line) for line in p.read_bytes().splitlines()];query_events[branch]=events
 (OUT/(branch+'.q')).write_bytes(p.read_bytes())
save('archived-synthetic-review.json',dict(scope='Existing producer evidence independently decoded, no re-run and no counterexample executed',producerAssertions=w['assertions'],negativeAssertions=20,precloseSha256=digest(pre),rows=len(summary['rows']),PFPlus61Only=True,recordCount=len(records),records=records,snapshotUsageBeforeQueryReconciliation=raw_snapshot_usage,originalUsageAfterExistingQueryLogs=total,n32OriginalStatus=unresolved,ownerExit=w['logClose']['exitedHelpers'],originalN32Return=w['logClose'],S17=snapshots['S17'],queryCheckpoints=query_events,metadataPeak=w['metadataPeak'],metadataCumulativeWritten=w['metadataWritten'],managedResourcePeak=w['ledgerPeaks'],realMediaNotRun=True))
anchors={}
patterns=r'def (open_j|read_j|end|ready|query|finish|recover|restore|save)|need\(not old|time.sleep|bridge-zero|finished|if not \(root/task\)|usage\[.q[nr].\]|file.write|f.write|hold:self|globalFence|abortOnly'
for p in (BASE/'src').glob('*'):
 if p.suffix not in ['.py','.cs','.java']:continue
 anchors[p.name]=[dict(line=i,text=line) for i,line in enumerate(p.read_text(encoding='utf-8').splitlines(),1) if re.search(patterns,line)]
save('source-anchors.json',anchors)
print(json.dumps(dict(integrity='PASS',sources=len(source['files']),frozen=len(freeze['files']),records=len(records),producerChecks=168,realMedia='NOT_RUN',ownFunctionalChecks=0),ensure_ascii=False))
