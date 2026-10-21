from pathlib import Path
import json,shutil,hashlib
R=Path(__file__).resolve().parents[2];old=R/'docs/coder/d1e11';new=R/'docs/coder/d1e13'
new.mkdir(exist_ok=False)
rows=[]
def copy(a,b):
 b.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(a,b);raw=a.read_bytes();rows.append({'source':a.relative_to(R).as_posix(),'target':b.relative_to(R).as_posix(),'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()})
for folder in ['src','android','upstream-c14','gradle']:
 for a in (old/folder).rglob('*'):
  if a.is_file():copy(a,new/a.relative_to(old))
for a in (old/'app/src').rglob('*'):
 if a.is_file():copy(a,new/a.relative_to(old))
for n in ['build.gradle.kts','settings.gradle.kts','settings-gradle.lockfile','gradle.properties','gradlew','gradlew.bat','local.properties','app/build.gradle.kts','app/gradle.lockfile']:
 if (old/n).exists():copy(old/n,new/n)
for n in ['E9HostRegistry.java','E9PcSupervisor.java','E9PcClient.java','E9HostDeployment.java','E9HostManager.java','E9ActivationPolicyExport.java','build_local.ps1']:
 copy(old/'tools'/n,new/'tools'/n)
for n in ['E11DeploymentOnce.java','E9HostActivationSession.java']:copy(old/'revision-r1/tools'/n,new/'tools'/n)
(new/'evidence').mkdir()
(new/'evidence/inherited-inputs.json').write_text(json.dumps(rows,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'inherited':len(rows),'nativeBuilds':0,'deviceCalls':0}))
