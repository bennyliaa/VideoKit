"""Targeted finite PC/process/console/transport/grant checks; no old32/native/device suite."""
import argparse,hashlib,json,pathlib,subprocess,sys
p=argparse.ArgumentParser();p.add_argument('--attempt',required=True);p.add_argument('--cases',nargs='*');a=p.parse_args();B=pathlib.Path(__file__).resolve().parents[1];R=B.parents[2];out=B/'evidence/selfcheck-attempts'/a.attempt;out.mkdir(parents=True,exist_ok=False);work=B/'.selfcheck'/a.attempt;work.mkdir(parents=True,exist_ok=False)
jdk=pathlib.Path('D:/Android/Android Studio/jbr/bin');support=R/'docs/coder/d1e9/app/build/intermediates/javac/debug/compileDebugJavaWithJavac/classes';classes=work/'classes';classes.mkdir()
sources=sorted((B/'src').rglob('*.java'))+sorted((B/'upstream-c14/src').rglob('*.java'))+[B/'tools'/n for n in ['E9HostRegistry.java','E9PcSupervisor.java','E9PcClient.java','E9HostDeployment.java','E9HostManager.java','E9HostActivationSession.java','E9ActivationPolicyExport.java','E9TestFiles.java','E9ProductionSelfCheck.java','E9BProductionCheck.java']]
inputs=[]
for source in sources+sorted((B/'reference').glob('*')):
 if not source.is_file():continue
 raw=source.read_bytes();inputs.append(dict(path=str(source.relative_to(R)).replace('\\','/'),bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest()))
(out/'inputs.json').write_text(json.dumps(inputs,indent=2)+'\n',encoding='utf-8');args=work/'compile.args';args.write_text('\n'.join('"'+str(s).replace('\\','/')+'"' for s in sources),encoding='utf-8');commands=[]
def run(name,argv):
 command=[str(x) for x in argv];commands.append(dict(name=name,argv=command));(out/'commands.json').write_text(json.dumps(commands,indent=2)+'\n',encoding='utf-8')
 with (out/(name+'.stdout.txt')).open('xb') as stdout,(out/(name+'.stderr.txt')).open('xb') as stderr:
  result=subprocess.Popen(command,stdout=stdout,stderr=stderr)
  if name=='compile':result.wait(timeout=90)
  else:
   import time
   resultfile=work/name/'result.json';deadline=time.monotonic()+35
   while result.poll() is None and not resultfile.exists() and time.monotonic()<deadline:time.sleep(.05)
   observed=json.loads(resultfile.read_text()) if resultfile.exists() else None
   if observed and not observed['productionExitAllowed']:
    time.sleep(.25);assert result.poll() is None,'UNKNOWN JVM exited without actual return'
    (out/(name+'.fixture-teardown.json')).write_text(json.dumps(dict(scope='controller teardown ONLY synthetic test JVM after finite assertions; no live original child process',pid=result.pid,productionExitAllowed=False,originalCloseAck=False,notASafeExitProof=True))+'\n')
    result.terminate();result.wait(timeout=8);result.returncode=0
   elif observed:result.wait(timeout=8)
   elif result.poll() is None:
    result.terminate();result.wait(timeout=8);raise RuntimeError('FINITE_TEST_TIMEOUT:'+name)

 print(name,result.returncode,flush=True)
 if result.returncode:print((out/(name+'.stderr.txt')).read_text(encoding='utf-8',errors='replace'),flush=True)
 return result
result=run('compile',[jdk/'javac.exe','-encoding','UTF-8','-cp',support,'-d',classes,'@'+str(args)])
if result.returncode:sys.exit(result.returncode)
results=[]
for case in a.cases or ['WALK_NORMAL', 'WALK_ALLOCATE', 'WALK_ALLOCATE_UNKNOWN', 'WALK_READ_EXCEPTION', 'WALK_CLOSE_LATCH_EXCEPTION', 'WALK_CLOSE_LATCH_ERROR', 'WALK_CLOSE_UNKNOWN', 'WALK_ITERATOR_UNKNOWN', 'WALK_CLOSE_ERROR', 'MANAGER_INIT_UNKNOWN', 'MANAGER_OPEN_UNKNOWN', 'ACTIVATION_OPEN_UNKNOWN', 'ACTIVATION_FILE_UNKNOWN', 'ACTIVATION_RELEASE_UNKNOWN', 'EXPORT_SYNTHETIC_REJECTED', 'ACCEPT_SERIAL', 'ACCEPT_UNPROCESSED', 'ACCEPT_CONCURRENT', 'ACCEPT_LISTENER_UNKNOWN', 'ACCEPT_LISTENER_UNKNOWN_BEFORE', 'ACCEPT_LISTENER_UNKNOWN_PROCESS', 'ACCEPT_PROCESS', 'ACCEPT_WALK']:
 result=run(case,[jdk/'java.exe','-Dreference='+str(B/'reference'),'-cp',str(classes)+';'+str(support),'com.videokit.spike.e4.E9BProductionCheck',case,work/case,B/'reference']);results.append(dict(case=case,exitCode=result.returncode))
(out/'results.json').write_text(json.dumps(dict(schema=1,scope='E9B actual production registry walk/entry boundary/accept cap/original ProcessBuilder; synthetic metadata only; Android NOT_RUN',results=results),indent=2)+'\n',encoding='utf-8');sys.exit(int(any(r['exitCode'] for r in results)))
