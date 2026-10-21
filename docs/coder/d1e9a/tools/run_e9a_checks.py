"""Targeted finite PC/process/console/transport/grant checks; no old32/native/device suite."""
import argparse,hashlib,json,pathlib,subprocess,sys
p=argparse.ArgumentParser();p.add_argument('--attempt',required=True);p.add_argument('--cases',nargs='*');a=p.parse_args();B=pathlib.Path(__file__).resolve().parents[1];R=B.parents[2];out=B/'evidence/selfcheck-attempts'/a.attempt;out.mkdir(parents=True,exist_ok=False);work=B/'.selfcheck'/a.attempt;work.mkdir(parents=True,exist_ok=False)
jdk=pathlib.Path('D:/Android/Android Studio/jbr/bin');support=R/'docs/coder/d1e9/app/build/intermediates/javac/debug/compileDebugJavaWithJavac/classes';classes=work/'classes';classes.mkdir()
sources=sorted((B/'src').rglob('*.java'))+sorted((B/'upstream-c14/src').rglob('*.java'))+[B/'tools'/n for n in ['E9PcSupervisor.java','E9PcClient.java','E9HostDeployment.java','E9HostManager.java','E9HostActivationSession.java','E9ActivationPolicyExport.java','E9TestFiles.java','E9ProductionSelfCheck.java','E9AProductionCheck.java']]
inputs=[]
for source in sources+sorted((B/'reference').glob('*')):
 raw=source.read_bytes();inputs.append(dict(path=str(source.relative_to(R)).replace('\\','/'),bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest()))
(out/'inputs.json').write_text(json.dumps(inputs,indent=2)+'\n',encoding='utf-8');args=work/'compile.args';args.write_text('\n'.join('"'+str(s).replace('\\','/')+'"' for s in sources),encoding='utf-8');commands=[]
def run(name,argv):
 command=[str(x) for x in argv];commands.append(dict(name=name,argv=command));(out/'commands.json').write_text(json.dumps(commands,indent=2)+'\n',encoding='utf-8')
 with (out/(name+'.stdout.txt')).open('xb') as stdout,(out/(name+'.stderr.txt')).open('xb') as stderr:
  result=subprocess.Popen(command,stdout=stdout,stderr=stderr);result.wait()
 print(name,result.returncode,flush=True)
 if result.returncode:print((out/(name+'.stderr.txt')).read_text(encoding='utf-8',errors='replace'),flush=True)
 return result
result=run('compile',[jdk/'javac.exe','-encoding','UTF-8','-cp',support,'-d',classes,'@'+str(args)])
if result.returncode:sys.exit(result.returncode)
results=[]
for case in a.cases or ['TRANSPORT','STATUS_GAP','IDENTITY_CLEANUP','NO_REPLAY','DECODE_DEADLINE','GRANT','CONCURRENT_GRANT','CUSTODY_PIN','REMOTE','EARLY_EOF','READER_ERROR','OUTPUT_BOUND','CONSOLE_EOF','CONSOLE_TRUNCATED','CONSOLE_OVERFLOW','CONTROL5','LATE_VERDICT','CLOSE_LATCH','CLOSE_UNKNOWN']:
 result=run(case,[jdk/'java.exe','-cp',str(classes)+';'+str(support),'com.videokit.spike.e4.E9AProductionCheck',case,work/case,B/'reference']);results.append(dict(case=case,exitCode=result.returncode))
(out/'results.json').write_text(json.dumps(dict(schema=1,scope='targeted actual production PC objects/ProcessBuilder/pipe/console plus shared metadata grant; Android NOT_RUN',results=results),indent=2)+'\n',encoding='utf-8');sys.exit(int(any(r['exitCode'] for r in results)))
