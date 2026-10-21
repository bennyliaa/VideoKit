"""Local syntax/argv + exact collector fragment with a local dumpsys substitute. No adb/device."""
from pathlib import Path
import hashlib,json,os,re,shlex,subprocess,sys
sys.dont_write_bytecode=True
from process_record import parse
B=Path(__file__).resolve().parents[1];R=B.parents[2];E=B/'evidence';work=B/'.checks/overlay';work.mkdir(parents=True,exist_ok=True)
shell=Path('C:/Program Files/Git/bin/bash.exe');manifest=json.loads((B/'release/metadata/three-client-manifest.json').read_text());syntax=[]
def sha(b):return hashlib.sha256(b).hexdigest()
for item in manifest['clients']:
 script=(R/item['script']['path']).read_text();assert shlex.split(item['argv'][-1])==[script]
 assert script.count((B/'tools/processes_reader.sh').read_text())==1
 assert script.count('if dumpsys activity processes 2>&1;')==1 and 'dumpsys activity instrumentation' not in script and 'awk ' not in script
 bodies=[script]+item['nestedShellBodiesForSyntaxAudit']
 for i,body in enumerate(bodies):
  path=work/(item['id']+'-'+str(i)+'.sh');path.write_text(body,encoding='utf-8',newline='\n')
  command=[str(shell),'--noprofile','--norc','-n',path.as_posix()];result=subprocess.run(command,capture_output=True,timeout=10)
  assert result.returncode==0,(item['id'],i,result.stderr)
  syntax.append({'stage':item['id'],'body':i,'sha256':sha(body.encode()),'argv':command,'exitCode':0,'stderr':result.stderr.decode()})
fragment=json.loads((B/'release/state-collector-fragment.json').read_text())['definition']
stub='''dumpsys() {
 if [ "$#" -ne 2 ] || [ "$1" != activity ] || [ "$2" != processes ]; then return 95;fi
 cat "$E13B_LOCAL_RAW_FILE"
 return "$E13B_LOCAL_RETURN"
}
'''
wrapper=work/'controlled-collector.sh';wrapper.write_text('set -eu\n'+stub+fragment+'\ne13b_collect_state\nprintf "E13B_LOCAL_NEXT_METADATA_STAGE\\n"\n',encoding='utf-8',newline='\n')
cases=[('idle','metadata-03-activity-processes-stdout',0,0,'IDLE'),('active','active-other-project',0,73,'ACTIVE'),('unsupported-zero','unsupported-exit-zero',0,21,'BLOCKED'),('nonzero-original','metadata-03-activity-processes-stdout',1,21,'BLOCKED')]
results=[]
for name,source,status,exitcode,state in cases:
 raw=(E/'metadata-shell-cases'/(source+'.input.txt')).read_text();raw=raw.rsplit('\nE13B_DUMPSYS_EXIT=',1)[0]
 path=work/(name+'.raw.txt');path.write_text(raw,encoding='utf-8',newline='\n')
 env=dict(os.environ,E13B_LOCAL_RAW_FILE=path.as_posix(),E13B_LOCAL_RETURN=str(status),LC_ALL='C')
 command=[str(shell),'--noprofile','--norc','--posix',wrapper.as_posix()];result=subprocess.run(command,capture_output=True,env=env,timeout=20)
 assert result.returncode==exitcode,(name,result.returncode,result.stdout,result.stderr)
 (E/(name+'-collector.stdout.txt')).write_bytes(result.stdout);(E/(name+'-collector.stderr.txt')).write_bytes(result.stderr)
 text=result.stdout.decode();match=re.match(r'BEGIN\tINSTRUMENTATION\n(.*?)\nEND\tINSTRUMENTATION\n',text,re.S);assert match,(name,text)
 if state!='BLOCKED':assert parse(match[1])['state']==state
 else:assert match[1].startswith('E13B_PROCESS_BLOCKED reason=')
 assert ('E13B_LOCAL_NEXT_METADATA_STAGE' in text)==(exitcode==0)
 results.append({'case':name,'source':source,'origin':'CONTROLLED_LOCAL_DUMPSYS_SUBSTITUTE_ONLY','realQueryStatus':status,'expectedExit':exitcode,'exitCode':result.returncode,'state':state,'laterMetadataPrevented':exitcode!=0,'argv':command,'stdoutSha256':sha(result.stdout),'stderrSha256':sha(result.stderr)})
value={'status':'PASS_EXACT_OVERLAY_METADATA_ONLY','syntax':syntax,'collectorCases':results,'argvScriptBytesEqual':3,'queryPerClient':1,'extraClients':0,'deviceCalls':0,'productTests':0,'builds':0}
(E/'overlay-check-results.json').write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print('PASS_EXACT_OVERLAY_METADATA_ONLY syntax='+str(len(syntax))+' collector=4')
