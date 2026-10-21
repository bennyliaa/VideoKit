from pathlib import Path
import json,hashlib,zipfile,subprocess,datetime,os,re,shutil,sys
B=Path(__file__).resolve().parents[1];R=B.parents[2];E=B/'evidence';J=Path('D:/Android/Android Studio/jbr')
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for block in iter(lambda:f.read(65536),b''):h.update(block)
 return h.hexdigest()
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def dump(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
assert sys.argv[1:]==['--single-authorized-build']
assert not (E/'fixture-tool01-freeze.json').exists()
D=E/'build-001';D.mkdir(exist_ok=False) # one build; existence is a replay rejection, not a permission token
W=B/'build-output';W.mkdir(exist_ok=False);C=W/'classes';C.mkdir();TEMP=W/'temp';TEMP.mkdir()
for n in ['empty-classpath','empty-sourcepath','empty-processorpath']:(W/n).mkdir()
stage=R/'docs/tester/D1_FIXTURE_TOOL01_BUILD_PHASE_A_EVIDENCE'
assert sha(R/'docs/tester/D1_FIXTURE_TOOL01_BUILD_PHASE_A_REPORT_V1.0.md')=='1c823c521003c3384cc60a4396c559e5bb98eb5398a60a2d7979508f9c41a330'
for p in stage.glob('*.json'):shutil.copyfile(p,B/'reference'/('phase-a-'+p.name))
for p in [R/'docs/tester/D1_FIXTURE_TOOL01_BUILD_PHASE_A_REPORT_V1.0.md',R/'docs/milestones/D1_FIXTURE_TOOL01_BUILD_CODER_REQUIREMENTS_V1.0.md']:shutil.copyfile(p,B/'reference'/p.name)
shutil.copyfile(R/'docs/coder/d1media3-android01/notice-assets/Apache-2.0.txt',B/'licenses/Apache-2.0.txt')
source=json.loads((E/'extracted-source-identity.json').read_text());assert len(source['unmodifiedJavaFiles'])==708 and source['totalBytes']==4435752
for x in source['unmodifiedJavaFiles']:assert sha(B/x['path'])==x['sha256']
with zipfile.ZipFile(B/'reference/jcodec-0.2.5-sources.jar') as z:
 assert len(z.namelist())==807
 for x in source['unmodifiedJavaFiles']:assert (B/x['path']).read_bytes()==z.read(x['archiveEntry'])
sources=sorted((B/'source').rglob('*.java'))+sorted((B/'driver').rglob('*.java'));assert len(sources)==711
for p in sources:
 for imp in re.findall(r'^import\s+(?:static\s+)?([\w.]+)',p.read_text(),re.M):assert imp.startswith(('java.','javax.','org.jcodec.','net.sourceforge.jaad.','com.videokit.fixturetool.')),(p,imp)
driver='\n'.join(p.read_text() for p in (B/'driver').rglob('*.java'))
for forbidden in ['System.exit(','.interrupt(','.destroy(','.destroyForcibly(','.exec(', 'MediaCodec','ProcessBuilder','test_media','http://','https://']:assert forbidden not in driver,forbidden
for token in ['source.slice()','attempted += count','while (source.hasRemaining())','returned < 1','MAX_ATTEMPT - count','position < 0','physicalPositionUnknown=true','events.size() >= 512']:assert token in driver,token
for token in ['CREATE_NEW','NOFOLLOW_LINKS','toRealPath()','getTrackTotalDuration()','H264Utils.parseAVCC','H264Utils.saveCodecPrivate','worker.join(DEADLINE_MS)','worker.join()','encoder.setKeyInterval(1)','encoder.setMotionSearchRange(0)']:assert token in driver,token
assert 'H264Utils.encodeMOVPacket(' not in driver # only mature CodecMP4MuxerTrack performs the actual conversion
notices=[];licenseRows=[]
for p in sources:
 rel=p.relative_to(B).as_posix();text=p.read_text();before=re.split(r'(?m)^(?:(?:public|final|abstract|strictfp)\s+)*(?:class|interface|enum)\s+\w+',text,maxsplit=1)[0]
 comments='\n'.join(re.findall(r'/\*.*?\*/',before,re.S))
 label='PROJECT_AUTHORED_INTERNAL_REVIEW_NO_RELEASE_LICENSE_GRANTED' if rel.startswith('driver/') else 'Apache-2.0' if rel.endswith('/Preconditions.java') else 'Public-Domain-with-JCodec-FreeBSD-modifications' if rel.startswith('source/net/sourceforge/jaad/') else 'JCodec-source-notices-retained-see-verbatim-header'
 licenseRows.append({'path':rel,'sha256':sha(p),'declaredAttributionClassification':label,'verbatimHeader':comments})
 notices.append(rel+' SHA256 '+sha(p)+'\n'+comments+'\n')
(B/'licenses/SOURCE_NOTICES.txt').write_text('\n'.join(notices),encoding='utf-8')
(B/'licenses/PROJECT-CODE-NOTICE.txt').write_text('The com.videokit.fixturetool driver is project-authored internal review code. No public distribution license is inferred. Upstream source notices and licenses remain applicable; this build does not provide patent/commercial-release/FFmpeg clearance.\n',encoding='utf-8')
dump(E/'source-license-inventory.json',licenseRows)
resources=B/'package-resources/META-INF/licenses';resources.mkdir(parents=True)
for p in (B/'licenses').iterdir():shutil.copyfile(p,resources/p.name)
prior=json.loads((B/'reference/proposed-compiler-identity.json').read_text())
for row in prior['files']:assert sha(Path(row['path']))==row['sha256']
compilerFiles=[J/'release',J/'bin/java.exe',J/'bin/javac.exe',J/'bin/jar.exe',J/'lib/modules']
compiler=[{'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p)} for p in compilerFiles]
assert 'JAVA_VERSION="21.0.10"' in (J/'release').read_text();dump(E/'compiler-identity.json',{'files':compiler,'jdkRelease':(J/'release').read_text(),'encoderClassLoaded':False})
pins=[{'path':p.relative_to(B).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sources];assert sum(x['bytes'] for x in pins)<=16*1024*1024
dump(E/'source-input-pins.json',pins)
arguments=W/'sources.args';arguments.write_text('\n'.join('"'+p.as_posix()+'"' for p in sources)+'\n',encoding='utf-8')
jar=B/'artifacts/videokit-fixture-tool01.jar'
javac=[str(J/'bin/javac.exe'),'-J-Xmx512m','-J-XX:-UsePerfData','--release','11','-encoding','UTF-8','-proc:none','-implicit:none','-classpath',str(W/'empty-classpath'),'-sourcepath',str(W/'empty-sourcepath'),'-processorpath',str(W/'empty-processorpath'),'-d',str(C),'@'+str(arguments)]
jarcmd=[str(J/'bin/jar.exe'),'-J-Xmx512m','-J-XX:-UsePerfData','--create','--file',str(jar),'--main-class','com.videokit.fixturetool.SixFrameDriver','--date=2026-10-21T00:00:00Z','-C',str(C),'.','-C',str(B/'package-resources'),'.']
env=os.environ.copy();removed=[]
for k in ['JAVA_TOOL_OPTIONS','JDK_JAVA_OPTIONS','_JAVA_OPTIONS','JDK_JAVAC_OPTIONS','CLASSPATH']:
 if k in env:env.pop(k);removed.append(k)
env['TMP']=str(TEMP);env['TEMP']=str(TEMP);env['JAVA_HOME']=str(J)
inputs=[p for p in B.rglob('*') if p.is_file() and not p.is_relative_to(W) and not p.is_relative_to(D)]
dump(D/'prebuild-all-candidate-input-pins.json',[{'path':p.relative_to(B).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(inputs)])
recipe={'sourceInputBytes':sum(x['bytes'] for x in pins),'allSourceDriverInputLimit':16777216,'buildOutputLimit':67108864,'commands':[javac,jarcmd],'workingDirectory':str(W),'sourceArgFileSha256':sha(arguments),'sourceArgFile':arguments.relative_to(B).as_posix(),'removedInjectionEnvironmentKeys':removed,'environmentControls':{'TMP':str(TEMP),'TEMP':str(TEMP),'JAVA_HOME':str(J)},'processConcurrency':1,'attemptsEach':1,'observationWindowSecondsEach':60,'onTimeout':'Admission stops, retain SAME Popen/handles; wait its original natural return; do not admit jar or retry even if compiler later exits0','mainOrClassInitializationRun':False,'outputQuotaMeaning':'Actual complete footprint measured after tool returns; no OS-quota/host-isolation assertion. Source fixed/trusted, no annotation processors. If actual budget exceeded => no downstream admission, not force-kill/refund.'}
dump(E/'build-recipe.json',recipe)
owners=[]
def run(name,argv):
 owner={'tool':name,'registeredUtc':now(),'argv':argv,'cwd':str(W),'state':'REGISTERED_BEFORE_POPEN','observationDeadlineSeconds':60,'timedOutSticky':False,'originalProcessReturned':False,'outputHandlesClosed':False,'terminationActions':0};owners.append(owner);dump(D/(name+'-owner.json'),owner)
 out=(D/(name+'.stdout')).open('xb');err=(D/(name+'.stderr')).open('xb');proc=None
 try:
  owner['state']='ALLOCATION_ENTERED';dump(D/(name+'-owner.json'),owner)
  proc=subprocess.Popen(argv,cwd=W,env=env,stdout=out,stderr=err,stdin=subprocess.DEVNULL,shell=False)
  owner['pid']=proc.pid;owner['startUtc']=now();owner['state']='ORIGINAL_PROCESS_STARTED';dump(D/(name+'-owner.json'),owner)
  try:code=proc.wait(timeout=60)
  except subprocess.TimeoutExpired:
   owner['timedOutSticky']=True;owner['state']='UNKNOWN_ORIGINAL_RETAINED_NO_NEXT_TOOL';dump(D/(name+'-owner.json'),owner)
   code=proc.wait() # Same original; do not kill/interrupt/cancel or release handles.
  owner['exitCode']=code;owner['endUtc']=now();owner['originalProcessReturned']=True;owner['state']='NATURAL_ORIGINAL_RETURN_AFTER_DEADLINE_UNKNOWN' if owner['timedOutSticky'] else 'NATURAL_ORIGINAL_RETURN'
 finally:
  if proc is None or owner['originalProcessReturned']:
   out.close();err.close();owner['outputHandlesClosed']=True
  dump(D/(name+'-owner.json'),owner)
 return owner
result=run('javac',javac)
for row in pins:assert sha(B/row['path'])==row['sha256']
if result.get('exitCode')==0 and not result['timedOutSticky']:
 classBytes=sum(p.stat().st_size for p in C.rglob('*') if p.is_file())
 if classBytes<67108864:result=run('jar',jarcmd)
 else:result={'state':'BUILD_OUTPUT_LIMIT_BLOCKED_BEFORE_JAR'}
files=[p for root in [W,D,B/'artifacts',B/'package-resources'] for p in root.rglob('*') if p.is_file()]
size=sum(p.stat().st_size for p in files);assert size<=67108864,'OUTPUT_LIMIT_EXCEEDED_NO_RETRY'
dump(E/'build-result.json',{'status':'COMPILED_AND_PACKAGED_ONLY_NOT_RUN' if len(owners)==2 and all(x.get('exitCode')==0 and x['originalProcessReturned'] and x['outputHandlesClosed'] and not x['timedOutSticky'] for x in owners) else 'BUILD_FAILED_OR_UNKNOWN_NO_RETRY','tools':owners,'actualBuildOutputFiles':[{'path':p.relative_to(B).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(files)],'actualBuildOutputBytesAtNaturalReturn':size,'sourceInputBytes':sum(x['bytes'] for x in pins),'runtimeCalls':0,'newMediaFiles':0,'compilerInvocations':1,'jarInvocations':max(0,len(owners)-1),'newOriginalOwnerOrDeviceQueries':0})
print(json.dumps({'result':json.loads((E/'build-result.json').read_text())['status'],'sourceInputBytes':sum(x['bytes'] for x in pins),'outputBytes':size,'jarBytes':jar.stat().st_size if jar.exists() else None,'jarSha256':sha(jar) if jar.exists() else None},indent=2))
