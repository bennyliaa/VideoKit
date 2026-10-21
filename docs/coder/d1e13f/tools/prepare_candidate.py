from pathlib import Path
import shutil,json
B=Path(__file__).resolve().parents[1];R=B.parents[2];A=R/'docs/coder/d1e13e'
if (B/'evidence/prepared.json').exists():raise SystemExit('Prepared already')
for name in ['src','android','upstream-c14','binding','checks/com','gradle','app/src','fixture/src']:shutil.copytree(A/name,B/name)
for folder in ['','app','fixture']:
 for p in (A/folder).iterdir():
  if p.is_file() and (p.suffix in ['.kts','.properties','.lockfile'] or p.name in ['gradlew','gradlew.bat','fixture-signing.p12']):shutil.copyfile(p,B/folder/p.name)
for p in (A/'tools').glob('*.java'):shutil.copyfile(p,B/'tools'/p.name)
for name in ['build_local.ps1','audit_artifacts.py','observe_original.ps1']:
 t=(A/'tools'/name).read_text(encoding='utf-8-sig').replace('d1e13e','d1e13f').replace('e13e-freeze','e13f-freeze').replace('D1-20261018-E13E','D1-20261018-E13F').replace('D1-E13E-ACTIVATION','D1-E13F-ACTIVATION').replace("versionCode='18'","versionCode='19'").replace('E13E','E13F');(B/'tools'/name).write_text(t,encoding='utf-8')
for name in ['app/build.gradle.kts','fixture/build.gradle.kts','app/src/androidTest/java/com/videokit/spike/e4/E13DeviceTests.java','src/com/videokit/spike/e4/E13Selection.java','src/com/videokit/spike/e4/E9DeploymentGate.java','tools/E13HostActivationSession.java','tools/E9HostDeployment.java','tools/E11DeploymentOnce.java']:
 p=B/name;t=p.read_text(encoding='utf-8-sig').replace('D1-E13E-ACTIVATION','D1-E13F-ACTIVATION').replace('D1-E13E-LIFECYCLE','D1-E13F-LIFECYCLE').replace('e13e-lifecycle-deployment.once','e13f-lifecycle-deployment.once')
 if name=='app/build.gradle.kts':t=t.replace('versionCode = 18','versionCode = 19')
 if name=='fixture/build.gradle.kts':t=t.replace('versionCode = 2;','versionCode = 3;').replace('E13E-negative-fixture','E13F-negative-fixture')
 if name.endswith('E13DeviceTests.java'):t=t.replace('assertEquals(18,','assertEquals(19,')
 if name.endswith('E9DeploymentGate.java'):t=t.replace('!=18)','!=19)')
 if name.endswith('E13HostActivationSession.java'):t=t.replace('10222,18,1,false','10222,19,1,false')
 if name.endswith('E9HostDeployment.java'):t=t.replace('equals("2") || !certificate(file)','equals("3") || !certificate(file)')
 p.write_text(t,encoding='utf-8')
(B/'evidence').mkdir();(B/'evidence/prepared.json').write_text(json.dumps(dict(base='FROZEN_E13E',scope='F01/F02/F03 offline only',appVersion=19,fixtureVersion=3,deviceCalls=0))+'\n')
print('E13F source prepared; old E13E unchanged')
