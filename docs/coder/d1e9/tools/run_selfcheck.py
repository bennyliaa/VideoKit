"""Finite production-object selfcheck; no device, native execution or real media."""
import argparse, hashlib, json, pathlib, subprocess, sys, datetime
p=argparse.ArgumentParser();p.add_argument('--attempt',required=True);p.add_argument('--cases',nargs='*');a=p.parse_args()
root=pathlib.Path(__file__).resolve().parents[1]; project=root.parents[2]
out=root/'evidence'/'selfcheck-attempts'/a.attempt
out.mkdir(parents=True,exist_ok=False)
work=root/'.selfcheck'/a.attempt;work.mkdir(parents=True,exist_ok=False)
jdk=pathlib.Path('D:/Android/Android Studio/jbr/bin')
support=project/'docs/coder/d1e7a/app/build/intermediates/javac/debug/compileDebugJavaWithJavac/classes'
sources=sorted((root/'src').rglob('*.java'))+sorted((root/'upstream-c14/src').rglob('*.java'))+[root/'tools'/n for n in ['E9TestFiles.java','E9ProductionSelfCheck.java','E9HostDeployment.java','E9HostManager.java','E9ActivationPolicyExport.java']]
oldroot=project/'docs/coder/d1e7a';oldsrc=sorted((oldroot/'src').rglob('*.java'))+sorted((oldroot/'upstream-c14/src').rglob('*.java'))
inputs={str(f.relative_to(project)).replace('\\','/'):{'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()} for f in sources+oldsrc+sorted((root/'reference').rglob('*')) if f.is_file()}
(out/'inputs.json').write_text(json.dumps(inputs,indent=2)+'\n',encoding='utf-8')
def command(name,args):
 r=subprocess.run([str(x) for x in args],capture_output=True,timeout=90)
 (out/(name+'.stdout.txt')).write_bytes(r.stdout);(out/(name+'.stderr.txt')).write_bytes(r.stderr)
 print(name,r.returncode,flush=True)
 return r
classes=work/'classes';oldclasses=work/'old-reader';classes.mkdir();oldclasses.mkdir()
for name,source,dest in [('compile',sources,classes),('compile-frozen-reader',oldsrc,oldclasses)]:
 arg=work/(name+'.args');arg.write_text('\n'.join('"'+str(s).replace('\\','/')+'"' for s in source),encoding='utf-8')
 r=command(name,[jdk/'javac.exe','-encoding','UTF-8','-cp',support,'-d',dest,'@'+str(arg)])
 if r.returncode: print(r.stderr.decode('utf-8',errors='replace'));sys.exit(r.returncode)
results=[]
for case in a.cases or ['A%02d'%i for i in range(1,24)]+['D%02d'%i for i in range(1,10)]+['A21-'+s for s in ['pending','guard','ledger','close']]:
 r=command(case,[jdk/'java.exe','-cp',str(classes)+';'+str(support),'com.videokit.spike.e4.E9ProductionSelfCheck',case,work/'cases',root/'reference',oldclasses,support])
 results.append({'case':case,'exitCode':r.returncode,'stdout':r.stdout.decode('utf-8',errors='replace'),'stderr':r.stderr.decode('utf-8',errors='replace')})
 if r.returncode: print(results[-1]['stderr'],flush=True)
(out/'results.json').write_text(json.dumps({'scope':'SYNTHETIC_LOCAL_PRODUCTION_OBJECTS','device':'NOT_RUN','results':results},indent=2)+'\n',encoding='utf-8')
sys.exit(int(any(x['exitCode'] for x in results)))
