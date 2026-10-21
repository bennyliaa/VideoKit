from pathlib import Path
import hashlib,json,subprocess
B=Path(__file__).resolve().parents[1];shell=Path('C:/Program Files/Git/bin/bash.exe');scratch=B/'.checks/metadata-syntax';scratch.mkdir(parents=True,exist_ok=True)
manifest=json.loads((B/'release/metadata/three-client-manifest.json').read_text());checks=[]
for item in manifest['clients']:
 bodies=[(B.parents[2]/item['script']['path']).read_text()]+item['nestedShellBodiesForSyntaxAudit']
 for i,body in enumerate(bodies):
  source=scratch/(item['id']+'-'+str(i)+'.sh');source.write_text(body,encoding='utf-8',newline='\n')
  command=[str(shell),'--noprofile','--norc','-n',source.as_posix()];result=subprocess.run(command,capture_output=True,timeout=10)
  assert result.returncode==0,(item['id'],i,result.stderr)
  checks.append({'stage':item['id'],'body':i,'sha256':hashlib.sha256(body.encode()).hexdigest(),'argv':command,'stdout':result.stdout.decode(),'stderr':result.stderr.decode(),'exitCode':0})
 assert item['originalPcClients']==1 and item['recordOutputUpperBound']<=65536 and item['extraJavaWrappers']==0
out={'status':'PASS_LOCAL_SHELL_SYNTAX_ONLY','checks':checks,'scope':'POSIX shell syntax with local Git Bash -n; no script body executes, no adb, no assertion of API31 command output/runtime compatibility','metadataDeviceClientsExecuted':0}
(B/'evidence/metadata-syntax.json').write_text(json.dumps(out,indent=2)+'\n');print('PASS_LOCAL_SHELL_SYNTAX_ONLY',len(checks))
