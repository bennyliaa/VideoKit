"""Static driver derivation; original56 never edited."""
from pathlib import Path
import json,hashlib,difflib,ast
H=Path(__file__).resolve().parent;C=H.parent/'d1android02-readonly-facts-preauth01'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n',encoding='utf-8',newline='\n')
manifest=json.loads((C/'reference/full-manifest.json').read_bytes())
assert sha(C/'reference/full-manifest.json')=='3ce81441d75e8a47368078197fcc43a20ace8eef916f1f3dcbd6f08c3cd8059c'
for row in manifest['files']:assert sha(C/row['path'])==row['sha256'],row['path']
for rel in ('owned_capture.py','reuse/capture_policy.py','reuse/native_identity.py','reuse/evidence_io.py','reuse/owned_child.py','reuse/owned_child.ps1'):
 dst=H/'driver'/rel;dst.parent.mkdir(parents=True,exist_ok=True)
 if not dst.exists():dst.write_bytes((C/'driver'/rel).read_bytes())
 assert sha(dst)==sha(C/'driver'/rel)
old=(C/'selfcheck.py').read_text();s=old
s=s.replace("B=Path(__file__).resolve().parent;sys.path[:0]=[str(B),str(B/'tools'),str(B/'selfchecks'),str(B/'driver'),str(B/'driver/reuse')]", "H=Path(__file__).resolve().parent;B=H.parent/'d1android02-readonly-facts-preauth01';sys.path[:0]=[str(H),str(B/'tools'),str(B/'selfchecks'),str(H/'driver'),str(H/'driver/reuse')]")
s=s.replace('from driver_guard import Registry,PY,PS,ORIGINAL,sha','from driver_guard import Registry,PY,PS,ORIGINAL,sha,resolve_key')
s=s.replace("(B/'reference/profile.json')","(H/'reference/profile.json')").replace("(B/'reference/batch-plan.json')","(H/'reference/batch-plan.json')")
s=s.replace("W=B/'selfchecks/work';W.mkdir(exist_ok=True)","W=H/'work';W.mkdir(exist_ok=True);OWN=Path(PLAN['candidateOwnedOutput'])")
s=s.replace("B/'driver/reuse/", "H/'driver/reuse/")
s=s.replace("save(B/'evidence/", "save(H/'evidence/")
start=s.index('def inputs(name):');end=s.index('def pure_templates():',start)
s=s[:start]+"def inputs(name):\n d=json.loads((H/'reference/prepared-inputs.json').read_bytes())[name];return copy.deepcopy(d['policy']),copy.deepcopy(d['template']),copy.deepcopy(d['pins'])\n"+s[end:]
s=s.replace("folder.mkdir();save(folder/'template.json',t);save(folder/'policy.json',p)","assert (folder/'template.json').read_bytes()==encode(t) and (folder/'policy.json').read_bytes()==encode(p)")
s=s.replace("sha((B/rel).read_bytes())", "sha(resolve_key(rel).read_bytes())").replace("sha((B/r).read_bytes())", "sha(resolve_key(r).read_bytes())")
# Known returned failures must not cancel independent remaining planned groups.
s=s.replace("except BaseException as e:results.append(dict(name=name,status='FAIL',seconds=time.monotonic()-before,error=repr(e)));stopped=True", "except BaseException as e:\n  results.append(dict(name=name,status='FAIL',seconds=time.monotonic()-before,error=repr(e)))\n  if name=='driver-qualification':stopped=True")
s=s.replace("schema='PREAUTH01_BATCH_RESULT_V1'", "schema='PREAUTH01_SELFCHECK02_BATCH_RESULT_V1'")
assert 'B=Path(__file__).resolve().parent' not in s and "save(B/'evidence/" not in s
compile(s,str(H/'worker.py'),'exec');(H/'worker.py').write_text(s,encoding='utf-8',newline='\n')
(H/'reference').mkdir(exist_ok=True)
(H/'reference/worker-delta.patch').write_text(''.join(difflib.unified_diff(old.splitlines(True),s.splitlines(True),fromfile='PREAUTH01/selfcheck.py',tofile='SELFCHECK02/worker.py')),encoding='utf-8')
save(H/'reference/lineage.json',dict(originalManifestSha256=sha(C/'reference/full-manifest.json'),originalWorkerSha256=sha(C/'selfcheck.py'),derivedWorkerSha256=sha(H/'worker.py'),matureCaptures={str(p.relative_to(H).as_posix()):sha(p) for p in (H/'driver').rglob('*') if p.is_file()},changes=['POSIX source keys shared by profile producer/consumer','explicit candidateRoot/driverRoot/output roots','new scope inputs precomputed before dynamic','all exact tuples checked before constructors','known-returned failures recorded without skipping independent groups']))
