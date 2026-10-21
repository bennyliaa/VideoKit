from pathlib import Path
import json,subprocess,sys
root=Path(sys.argv[1]).resolve();base=root/'docs/coder/d1c13';jdk=Path('D:/Android/Android Studio/jbr/bin');classes=base/'classes'
sources=list((base/'src').rglob('*.java'))+[base/'tools'/name for name in ['C13CpuSelfCheck.java','C13CpuSourceSelfCheck.java','C13ExitRecordSelfCheck.java','C13LifecycleSelfCheck.java','C13GenerationSelfCheck.java','C13TraceSelfCheck.java','C13RegistrationSelfCheck.java','C13BindingSelfCheck.java','C13PipelineSelfCheck.java','C13QueueSelfCheck.java']]
resume='--resume' in sys.argv
if not resume:
 compile_result=subprocess.run([str(jdk/'javac.exe'),'-encoding','UTF-8','-d',str(classes),*[str(p) for p in sources]],capture_output=True,text=True,encoding='utf-8');(base/'evidence/local-javac.log').write_text(compile_result.stdout+compile_result.stderr,encoding='utf-8');assert compile_result.returncode==0,compile_result.stderr
else:
 assert all((classes/'com/videokit/spike/c13'/p.with_suffix('.class').name).exists() and (classes/'com/videokit/spike/c13'/p.with_suffix('.class').name).stat().st_mtime>=p.stat().st_mtime for p in sources)
names=['C13PipelineSelfCheck','C13QueueSelfCheck','C13RegistrationSelfCheck','C13BindingSelfCheck','C13GenerationSelfCheck','C13TraceSelfCheck','C13CpuSelfCheck','C13CpuSourceSelfCheck','C13ExitRecordSelfCheck','C13LifecycleSelfCheck','C13SelfCheck','C13ControlSelfCheck','C13FailureSelfCheck','C13CaptureSelfCheck','RecoverySelfCheck','ValidationSelfCheck'];results=[]
for name in names:
 if resume and name in names[:3]:
  previous=(base/'evidence'/(name+'.log')).read_text(encoding='utf-8');assert previous.startswith('PASS ');results.append({'class':name,'exit':0,'output':previous,'execution':'REUSED_PREVIOUS_C13_LOCAL_LOG_WITH_UNCHANGED_CHECKED_CLASSES'});continue
 argument=base/'outputs/recovery-checks' if name=='RecoverySelfCheck' else root
 if name=='RecoverySelfCheck':argument.mkdir(exist_ok=True)
 result=subprocess.run([str(jdk/'java.exe'),'-cp',str(classes),'com.videokit.spike.c13.'+name,str(argument)],cwd=base/'outputs',capture_output=True,text=True,encoding='utf-8',timeout=90)
 (base/'evidence'/(name+'.log')).write_text(result.stdout+result.stderr,encoding='utf-8');results.append({'class':name,'exit':result.returncode,'output':result.stdout+result.stderr});print(name,result.returncode,(result.stdout+result.stderr).splitlines()[-1:]);assert result.returncode==0,result.stderr
(base/'evidence/local-check-results.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
