"""Create independent driver from bounded inert definitions, no product execution."""
from pathlib import Path
import ast,json,hashlib
R=Path(__file__).resolve().parent;T=R.parent;D=T.parent/'coder/d1android02-readonly-facts-preauth01-selfcheck02';A=T/'D1_GLOBAL_IDLE_CONTRACT03_SEMANTICS_A_EVIDENCE';P=T/'D1_DRIVER_CAPTURE_FIX01_PACKAGE'
def put(p,b):
 p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('xb') as f:f.write(b)
def main():
 for n,src in [('self_io.py',A/'self_io.py'),('self_observer.py',A/'self_observer.py'),('profile.py',A/'profile.py'),('capture_policy.py',P/'capture_policy.py'),('native_identity.py',P/'native_identity.py')]:
  b=src.read_bytes()
  if n=='self_io.py':b=b.decode().replace('4294967296','2147483648').encode()
  put(R/n,b)
 ctl=(A/'controller.py').read_text().replace('window=300','window=360');put(R/'controller.py',ctl.encode())
 guard=(D/'driver_guard.py').read_text().replace("C=H.parent/'d1android02-readonly-facts-preauth01'","C=H.parents[1]/'coder/d1android02-readonly-facts-preauth01'").replace('def check(self,a,k):','def check(self,a,k,check_host=True):').replace("if str(Path.cwd())!=self.p['hostCwd'] or env_hash(dict(os.environ))!=self.p['inheritedEnvSha256']:","if check_host and (str(Path.cwd())!=self.p['hostCwd'] or env_hash(dict(os.environ))!=self.p['inheritedEnvSha256']):").replace('len(self.calls)>=96','len(self.calls)>=64').replace('>=320','>=240')
 put(R/'driver_guard.py',guard.encode())
 for n in ['owned_child.py','owned_child.ps1']:put(R/'driver/reuse'/n,(D/'driver/reuse'/n).read_bytes())
 src=(D/'worker.py').read_text();wanted={'inputs','reject','pure_templates','semantic','prestart'};pieces=[ast.get_source_segment(src,n) for n in ast.parse(src).body if isinstance(n,ast.FunctionDef) and n.name in wanted];assert len(pieces)==5
 put(R/'reused_checks.py',('\n\n'.join(pieces)+'\n').encode())
 put(R/'derivation.json',(json.dumps(dict(ownDriver=True,executedDeveloperWorkerMain=False,selectedInertFunctions=sorted(wanted),matureObserverSource=str(A/'self_observer.py'),registrySource=str(D/'driver_guard.py'),registryChanges=['exact candidate/driver roots','pure check_host flag only used before dynamic; constructor uses actual context','64 children and240s stop-new'],knownOldFinallyNotCopied=True,allWritesRoutedThroughOwnSave=True),indent=2)+'\n').encode())
 print(json.dumps(dict(staticSetup=True,actualPopen=0,actualGate=0)))
if __name__=='__main__':main()
