from pathlib import Path
import json,hashlib,zipfile,shutil,difflib,subprocess,datetime,os,re
B=Path(__file__).resolve().parents[1];R=B.parents[2];E=B/'evidence';J=Path('D:/Android/Android Studio/jbr');O=R/'docs/coder/d1fixture-tool02';D=E/'build-001';D.mkdir(exist_ok=False);W=B/'build-output';W.mkdir();C=W/'classes';C.mkdir()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
assert not (E/'observation01-freeze.json').exists()
expected={'source/org/jcodec/containers/mp4/boxes/DataRefBox.java','source/org/jcodec/containers/mp4/boxes/SampleDescriptionBox.java','source/org/jcodec/codecs/h264/mp4/AvcCBox.java'}
original=json.loads((E/'original-source-pins.json').read_text());changes=[];diff=[];P=B/'patches';P.mkdir()
for x in original:
 p=B/x['path'];old=O/x['path'];assert sha(old)==x['sha256']
 if sha(p)!=x['sha256']:
  assert x['path'] in expected;changes.append({'path':x['path'],'oldSha256':x['sha256'],'newSha256':sha(p)})
  text=''.join(difflib.unified_diff(old.read_text().splitlines(True),p.read_text().splitlines(True),fromfile='official-0.2.5/'+x['path'],tofile='0.2.5-videokit-observation01/'+x['path']));(P/(p.stem+'.patch')).write_text(text,encoding='utf-8');diff.append(text)
assert {x['path'] for x in changes}==expected
patch=P/'observation01.patch';patch.write_text(''.join(diff),encoding='utf-8');dump(E/'source-differences.json',{'originalJavaFiles':708,'unchanged':705,'changed':changes,'combinedPatchSha256':sha(patch),'originalSourceArchiveSha256':'9945efa92e16b3fbe8eb8bf37f00be53fa0adb52d09ac978a0744ca2ef3697db','newVersion':'0.2.5-videokit-observation01','parseLegacyListReset':False})
assert sha(B/'reference/jcodec-0.2.5-sources.jar')=='9945efa92e16b3fbe8eb8bf37f00be53fa0adb52d09ac978a0744ca2ef3697db'
with zipfile.ZipFile(B/'reference/jcodec-0.2.5-sources.jar') as z:
 assert len([n for n in z.namelist() if n.endswith('.java')])==708
 for x in original:assert hashlib.sha256(z.read(x['path'][7:])).hexdigest()==x['sha256']
sources=sorted((B/'source').rglob('*.java'))+sorted((B/'checks').rglob('*.java'));assert len(sources)==709
pins=[{'path':p.relative_to(B).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sources];assert sum(x['bytes'] for x in pins)<=16777216;dump(E/'compile-source-pins.json',pins)
for x in json.loads((B/'reference/compiler-identity.json').read_text())['files']:assert sha(Path(x['path']))==x['sha256']
compiler=[{'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p)} for p in [J/'release',J/'bin/java.exe',J/'bin/javac.exe',J/'bin/jar.exe',J/'lib/modules']];dump(E/'compiler-identity.json',compiler)
stage=R/'docs/tester/D1_JCODEC_OBSERVATION01_PHASE_A_EVIDENCE';stageReport=R/'docs/tester/D1_JCODEC_OBSERVATION01_PHASE_A_REPORT_V1.0.md';assert sha(stageReport)=='c28a3285dba537cceaf3ffde80888b975e2e6393b5fb72dbb7b855f59bf7486f';shutil.copyfile(stageReport,B/'reference'/stageReport.name)
for p in stage.glob('*.json'):shutil.copyfile(p,B/'reference'/('phase-a-'+p.name))
req=R/'docs/milestones/D1_JCODEC_OBSERVATION01_CODER_REQUIREMENTS_V1.0.md';shutil.copyfile(req,B/'reference/CODER_REQUIREMENTS_WITH_STAGE_A.md')
notices=[]
for p in sources:
 text=p.read_text();head=re.split(r'(?m)^(?:(?:public|final|abstract|strictfp)\s+)*(?:class|interface|enum)\s+\w+',text,maxsplit=1)[0];notices.append(p.relative_to(B).as_posix()+' SHA256 '+sha(p)+'\n'+'\n'.join(re.findall(r'/\*.*?\*/',head,re.S)))
(B/'licenses/SOURCE_NOTICES.txt').write_text('\n\n'.join(notices)+'\n',encoding='utf-8')
(B/'licenses/MODIFICATION-NOTICE.txt').write_text('VideoKit audit-only JCodec fork 0.2.5-videokit-observation01, modified2026-10-21. This is NOT the official unmodified0.2.5 artifact or the original c4ed encoding tool. Only DataRefBox, SampleDescriptionBox and AvcCBox parse observability changed; original parser/factory/codec/mux/doWrite not replaced. Original source SHA2569945efa92e16b3fbe8eb8bf37f00be53fa0adb52d09ac978a0744ca2ef3697db. Combined patch SHA256 '+sha(patch)+'. Original FreeBSD/JAAD/Guava notices retained. Audit metadata only; no media qualification, product integration, signature or release/patent/FFmpeg clearance.\n',encoding='utf-8')
resources=B/'package-resources/META-INF/licenses';resources.mkdir(parents=True)
for p in (B/'licenses').iterdir():shutil.copyfile(p,resources/p.name)
manifest=W/'MANIFEST.MF';manifest.write_text('Manifest-Version: 1.0\nImplementation-Title: VideoKit JCodec audit observation fork\nImplementation-Version: 0.2.5-videokit-observation01\nAutomatic-Module-Name: com.videokit.audit.jcodec.observation01\nJCodec-Original-Sources-SHA256: 9945efa92e16b3fbe8eb8bf37f00be53fa0adb52d09ac978a0744ca2ef3697db\nVideoKit-Patch-SHA256: '+sha(patch)+'\n\n',encoding='utf-8')
for n in ['empty-classpath','empty-sourcepath','empty-processorpath','temp']:(W/n).mkdir()
args=W/'sources.args';args.write_text('\n'.join('"'+p.as_posix()+'"' for p in sources)+'\n',encoding='utf-8')
jar=B/'artifacts/jcodec-0.2.5-videokit-observation01.jar';pc=W/'production-classes';tc=W/'test-classes'
commands=[('javac',[str(J/'bin/javac.exe'),'-J-Xmx512m','-J-XX:-UsePerfData','--release','11','-encoding','UTF-8','-proc:none','-implicit:none','-classpath',str(W/'empty-classpath'),'-sourcepath',str(W/'empty-sourcepath'),'-processorpath',str(W/'empty-processorpath'),'-d',str(C),'@'+str(args)]),('jar',[str(J/'bin/jar.exe'),'-J-Xmx512m','-J-XX:-UsePerfData','--create','--file',str(jar),'--manifest',str(manifest),'--date=2026-10-21T00:00:00Z','-C',str(pc),'.','-C',str(B/'package-resources'),'.'])]
env=os.environ.copy();removed=[]
for k in ['JAVA_TOOL_OPTIONS','JDK_JAVA_OPTIONS','_JAVA_OPTIONS','JDK_JAVAC_OPTIONS','CLASSPATH']:
 if k in env:env.pop(k);removed.append(k)
env['TEMP']=str(W/'temp');env['TMP']=str(W/'temp');env['JAVA_HOME']=str(J)
dump(E/'build-recipe.json',{'commands':commands,'cwd':str(W),'removedInjectionKeys':removed,'sourceArgFileSha256':sha(args),'sourceInputBytes':sum(x['bytes'] for x in pins),'inputLimit':16777216,'outputLimit':67108864,'toolObservationSeconds':60,'concurrency':1,'attemptsEach':1,'noRuntimeMainOrParserInvokedDuringBuild':True})
owners=[]
for name,argv in commands:
 owner={'tool':name,'argv':argv,'cwd':str(W),'registeredBeforePopen':True,'originalProcessReturned':False,'outputHandlesClosed':False,'unknownSticky':False,'terminationOrRetry':0};owners.append(owner);dump(D/(name+'-owner.json'),owner)
 out=(D/(name+'.stdout')).open('xb');err=(D/(name+'.stderr')).open('xb');p=None
 try:
  owner['startUtc']=now();p=subprocess.Popen(argv,cwd=W,env=env,stdout=out,stderr=err,stdin=subprocess.DEVNULL,shell=False);owner['pid']=p.pid;dump(D/(name+'-owner.json'),owner)
  try:code=p.wait(timeout=60)
  except subprocess.TimeoutExpired:owner['unknownSticky']=True;dump(D/(name+'-owner.json'),owner);code=p.wait()
  owner['exitCode']=code;owner['originalProcessReturned']=True;owner['endUtc']=now()
 finally:
  if p is None or owner['originalProcessReturned']:out.close();err.close();owner['outputHandlesClosed']=True
  dump(D/(name+'-owner.json'),owner)
 if owner.get('exitCode')!=0 or owner['unknownSticky']:break
 if name=='javac':
  pc.mkdir();tc.mkdir();split=[]
  for p in C.rglob('*.class'):
   check=p.name.startswith('MetadataObservationCheck');dest=(tc if check else pc)/p.relative_to(C);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dest);split.append({'originalOutput':p.relative_to(B).as_posix(),'copy':dest.relative_to(B).as_posix(),'sha256':sha(p),'testOnly':check})
  dump(E/'class-split.json',split)
for x in pins:assert sha(B/x['path'])==x['sha256']
outputs=[p for root in [W,D,B/'artifacts',B/'package-resources'] for p in root.rglob('*') if p.is_file()];size=sum(p.stat().st_size for p in outputs);assert size<=67108864
status='BUILT_AUDIT_FORK_ONLY' if len(owners)==2 and all(x.get('exitCode')==0 and x['originalProcessReturned'] and not x['unknownSticky'] for x in owners) else 'BUILD_FAILED_OR_UNKNOWN_NO_RETRY'
dump(E/'build-result.json',{'status':status,'owners':owners,'sourceInputBytes':sum(x['bytes'] for x in pins),'buildOutputBytesAtReturn':size,'outputFiles':[{'path':p.relative_to(B).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in outputs],'compilerCalls':1,'jarCalls':len(owners)-1,'metadataJvms':0,'mediaOrGenerationCalls':0})
print(json.dumps({'status':status,'sourceInputs':709,'sourceInputBytes':sum(x['bytes'] for x in pins),'jarSha256':sha(jar) if jar.exists() else None,'jarBytes':jar.stat().st_size if jar.exists() else None,'buildOutputBytes':size,'patchSha256':sha(patch)},indent=2))
