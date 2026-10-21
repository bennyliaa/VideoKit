"""Explicit offline two-source host rebuild; no APK/Gradle/SDK clients."""
from pathlib import Path
import hashlib,json,subprocess,zipfile,sys
B=Path(__file__).resolve().parents[1];R=B.parents[2];A=R/'docs/coder/d1e13a';J=Path('D:/Android/Android Studio/jbr/bin')
def sha(b):return hashlib.sha256(b).hexdigest()
def pin(p):b=p.read_bytes();return dict(path=p.relative_to(R).as_posix(),bytes=len(b),sha256=sha(b))
def write(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def main():
 if sys.argv[1:]!=['build']:raise SystemExit('Explicit build argument required')
 if (B/'evidence/e13c-freeze.json').exists():raise SystemExit('FROZEN')
 out=B/'evidence/host-build-001';out.mkdir(exist_ok=False);classes=B/'.checks/production';classes.mkdir(parents=True,exist_ok=False)
 old=json.loads((A/'evidence/host-jar-manifest.json').read_text());jar=R/old['jar']['path'];assert pin(jar)==old['jar']
 src=[B/'tools/E11DeploymentOnce.java',B/'tools/E13HostActivationSession.java'];cmd=[str(J/'javac.exe'),'-encoding','UTF-8','-cp',str(jar),'-d',str(classes),*[str(p) for p in src]]
 write(out/'inputs.json',{'sources':[pin(p) for p in src],'baseJar':pin(jar),'javac':{'path':str(J/'javac.exe'),'sha256':sha((J/'javac.exe').read_bytes())},'argv':cmd})
 with (out/'compile.stdout.txt').open('xb') as so,(out/'compile.stderr.txt').open('xb') as se:
  p=subprocess.Popen(cmd,stdout=so,stderr=se);code=p.wait(timeout=60)
 write(out/'compile.exit.json',{'exitCode':code,'pid':p.pid,'naturalReturn':True});assert code==0
 target=B/'artifacts/e13c-host-tools.jar';target.parent.mkdir(exist_ok=True);rows=[]
 prefixes=['com/videokit/spike/e4/E11DeploymentOnce','com/videokit/spike/e4/E13HostActivationSession']
 with zipfile.ZipFile(jar) as zi,zipfile.ZipFile(target,'x',compression=zipfile.ZIP_DEFLATED) as zo:
  for row in old['classes']:
   if any(row['entry'][:-6].split('$')[0]==p for p in prefixes):continue
   raw=zi.read(row['entry']);assert sha(raw)==row['sha256'];zo.writestr(row['entry'],raw);rows.append({**row,'relationship':'EXACT_BASE_JAR_MEMBER'})
  for p in sorted(classes.rglob('*.class')):
   entry=p.relative_to(classes).as_posix();top=entry[:-6].split('$')[0];assert top in prefixes
   raw=p.read_bytes();zo.writestr(entry,raw);source=src[prefixes.index(top)];rows.append({'entry':entry,'bytes':len(raw),'sha256':sha(raw),'source':pin(source),'relationship':'RECOMPILED_TWO_SOURCE_HOST_FIX'})
 write(B/'evidence/host-jar-manifest.json',{'jar':pin(target),'baseJar':pin(jar),'classes':rows,'compiledSources':[pin(p) for p in src],'apkBuilds':0,'nativeBuilds':0,'deviceCalls':0})
 print(json.dumps({'status':'PASS_HOST_ONLY_BUILD','jar':pin(target),'classes':len(rows),'exactBaseMembers':sum(x['relationship']=='EXACT_BASE_JAR_MEMBER' for x in rows)}))
if __name__=='__main__':main()
