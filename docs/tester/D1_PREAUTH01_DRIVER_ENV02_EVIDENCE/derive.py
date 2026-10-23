"""New ENV02 version only; never write prior frozen drivers or product source."""
from pathlib import Path
import hashlib,json,sys
E=Path(__file__).resolve().parent;T=E.parent;OLD=T/'D1_PREAUTH01_INDEPENDENT_B_EVIDENCE';B=T.parent/'coder/d1android02-readonly-facts-preauth01'
def put(p,b):
 assert p.resolve().is_relative_to(E);p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('xb') as f:f.write(b)
def main():
 version=sys.argv[1];assert version in ['v1','v2'];R=E/version;assert not R.exists();R.mkdir()
 m=T/'D1_PREAUTH01_INDEPENDENT_B_MANIFEST_V1.0.json';assert hashlib.sha256(m.read_bytes()).hexdigest()=='992c684578af2da658b7f1f3e179b7e5d6b79c0f8b36891c5788118e6ea37562'
 for x in json.loads(m.read_bytes())['files']:
  b=Path(x['absolutePath']).read_bytes();assert len(b)==x['bytes'] and hashlib.sha256(b).hexdigest()==x['sha256']
 names=['self_io.py','self_observer.py','profile.py','capture_policy.py','native_identity.py','controller.py','driver_guard.py','write_guard.py','reused_checks.py','independent_models.py','worker.py','prepare.py']
 for name in names:
  text=(OLD/name).read_text();text=text.replace("B=R.parents[1]/'coder/d1android02-readonly-facts-preauth01'",'B=Path('+repr(str(B))+')').replace("C=H.parents[1]/'coder/d1android02-readonly-facts-preauth01'",'C=Path('+repr(str(B))+')')
  if name=='write_guard.py':text=text.replace('roots=[R]','roots=[R.parent]')
  if name=='prepare.py':
   text=text.replace("T=R.parent;B=T.parent/",'T=Path('+repr(str(T))+');B=T.parent/')
   text=text.replace("from write_guard import allowed","from write_guard import allowed\nfrom host_context import normalize,pure_models")
   text=text.replace("assert not (R/'order.json').exists()","assert not (R/'order.json').exists()\n save(R/'host-context-pure-models.json',pure_models(R))")
   text=text.replace("inheritedEnvSha256=env_hash(outerEnv)","inheritedEnvSha256=env_hash(normalize(outerEnv))")
  if name=='worker.py':
   text=text.replace("from write_guard import allowed,install,EVENTS as WRITES","from write_guard import allowed,install,EVENTS as WRITES\nfrom host_context import snapshot")
   text=text.replace("ident['nonce']=o['nonce'];rawsave", "ident['nonce']=o['nonce'];ident['hostContext']=snapshot();rawsave")
   text=text.replace("sys.path[:0]=[str(B/'tools'),str(B/'selfchecks')]", "start=json.loads(read(R.parent/'batch-start.json'))['monotonic']\n sys.path[:0]=[str(B/'tools'),str(B/'selfchecks')]")
  if name=='controller.py':
   text=text.replace("start=time.monotonic()", "start=time.monotonic()\n clockPath=R.parent/'batch-start.json'\n if not clockPath.exists():save(clockPath,dict(monotonic=start,wholeSeconds=360,stopNewSeconds=240,maxQualificationVersions=2))\n sharedStart=load(clockPath)['monotonic']\n assert time.monotonic()-sharedStart<240")
   text=text.replace('window=360','window=max(0,360-(time.monotonic()-sharedStart))')
  put(R/name,text.encode())
 put(R/'host_context.py',(E/'host_context_template.py.txt').read_bytes())
 for name in ['owned_child.py','owned_child.ps1']:put(R/'driver/reuse'/name,(OLD/'driver/reuse'/name).read_bytes())
 put(R/'derivation.json',(json.dumps(dict(version=version,old57Bad=0,oldWorkerOrOrderModified=False,productSourceModified=False,rawPopenAuditDictionary='UNCHANGED_EXACT',childSnapshot='Windows uppercase keys only, values unchanged; collisions rejected',sharedBudget='Both qualification versions share batch-start.json360/300/240; product attempt still once',actualSnapshotBeforeContextCheck=True,allowedNewEvidenceRoot=str(E),noNewGitOrDevice=True),indent=2)+'\n').encode())
 print(json.dumps(dict(version=version,path=str(R),old57Bad=0,actualPopen=0)))
if __name__=='__main__':main()
