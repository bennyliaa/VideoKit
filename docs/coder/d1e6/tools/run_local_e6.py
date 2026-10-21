"""Explicit finite logic tests using actual production predicates and Java diagnostic/content classes."""
from pathlib import Path
import subprocess,json
B=Path(__file__).resolve().parents[1];R=B.parents[2];D=B/'.selfcheck';D.mkdir(exist_ok=False)
J=Path('D:/Android/Android Studio/jbr/bin');N=Path('D:/Android/SDK/ndk/30.0.16248370/toolchains/llvm/prebuilt/windows-x86_64/bin');commands=[]
def run(cmd,name):
 p=subprocess.run([str(a) for a in cmd],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=30);log=B/('evidence/'+name+'.log');log.write_bytes(p.stdout);commands.append(dict(argv=[str(a) for a in cmd],exitCode=p.returncode,log=log.relative_to(R).as_posix()))
 if p.returncode:raise RuntimeError(name+': see preserved log')
 return p.stdout.decode(errors='replace')
c14=B/'upstream-c14/src/com/videokit/spike/c14';e4=B/'src/com/videokit/spike/e4';sources=[c14/n for n in ['E6NativeDiagnostic.java','CpuDiagnostics.java','CpuFrameRules.java','PipelineRules.java']]+[e4/'E6FailureCodes.java',B/'tools/E6DiagnosisSelfCheck.java']
run([J/'javac.exe','-encoding','UTF-8','-d',D,*sources],'java-selfcheck-compile')
text=run([J/'java.exe','-cp',D,'com.videokit.spike.c14.E6DiagnosisSelfCheck'],'java-selfcheck-run');assert 'cases=17' in text
definition=D/'kernel32.def';definition.write_text('LIBRARY KERNEL32.dll\nEXPORTS\nExitProcess\n')
run([N/'llvm-dlltool.exe','-m','i386:x86-64','-d',definition,'-l',D/'kernel32.lib'],'c-selfcheck-import')
run([N/'clang.exe','--target=x86_64-pc-windows-msvc','-ffreestanding','-fno-stack-protector','-O2','-Wall','-Wextra','-Werror','-c',B/'tools/e6_verify_selfcheck.c','-o',D/'verify.obj'],'c-selfcheck-compile')
run([N/'ld.lld.exe','-flavor','link','/entry:main','/subsystem:console','/nodefaultlib','/machine:x64','/out:'+str(D/'verify.exe'),D/'verify.obj',D/'kernel32.lib'],'c-selfcheck-link')
run([D/'verify.exe'],'c-selfcheck-run')
result=dict(schema=1,status='PASS',pureJavaCases=17,actualProductionNativePredicateCases=17,scope='Production C header used by actual JNI wrapper, Java diagnostic/first cause/cleanup and unchanged production content/timeline checks; no Android decode or native fault execution',commands=commands,deviceCalls=0)
with (B/'evidence/local-check-results.json').open('x',encoding='utf-8') as f:json.dump(result,f,indent=2);f.write('\n')
print('PASS native production predicate=17 / JVM diagnostic+content=17')
