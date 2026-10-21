from pathlib import Path
import shutil,json,hashlib
B=Path(__file__).resolve().parents[1];R=B.parents[2];A=R/'docs/coder/d1e13a'
if (B/'evidence/prepared.json').exists():raise SystemExit('Already prepared')
for name in ['src','android','upstream-c14','binding','checks','gradle','app/src','fixture/src']:
 shutil.copytree(A/name,B/name,dirs_exist_ok=False)
for folder in ['','app','fixture']:
 for p in (A/folder).iterdir():
  if p.is_file() and (p.suffix in ['.kts','.properties','.lockfile'] or p.name in ['gradlew','gradlew.bat','fixture-signing.p12']):
   shutil.copyfile(p,B/folder/p.name)
for name in ['E9ActivationPolicyExport.java','E9HostActivationSession.java','E9HostDeployment.java','E9HostManager.java','E9HostRegistry.java','E9PcClient.java','E9PcSupervisor.java','E13HostCase.java']:
 shutil.copyfile(A/'tools'/name,B/'tools'/name)
for name in ['E11DeploymentOnce.java','E13HostActivationSession.java']:
 shutil.copyfile(R/'docs/coder/d1e13c/tools'/name,B/'tools'/name)
# Product ABI stays1; new candidate must never masquerade as installed v17.
p=B/'app/build.gradle.kts';p.write_text(p.read_text().replace('versionCode = 17','versionCode = 18').replace('D1-E13A-ACTIVATION','D1-E13E-ACTIVATION'),encoding='utf-8')
p=B/'fixture/build.gradle.kts';p.write_text(p.read_text().replace('versionCode = 1;','versionCode = 2;').replace('E13-negative-fixture','E13E-negative-fixture'),encoding='utf-8')
(B/'evidence').mkdir();(B/'evidence/prepared.json').write_text(json.dumps({'scope':'E13E offline candidate only','base':'E13A source + E13C exact host fix','productVersion':18,'fixtureVersion':2,'installedVersionHistorical':17,'deviceCalls':0})+'\n')
print('prepared E13E sources; old frozen trees unchanged')
