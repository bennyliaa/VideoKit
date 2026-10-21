from pathlib import Path
import json,hashlib,zipfile,struct,ast,re,collections,xml.etree.ElementTree as ET,subprocess,datetime
R=Path('D:/CodexProjects/VideoKit');E=Path(__file__).resolve().parent;B=R/'docs/coder/d1media3-android01';OLD=R/'docs/coder/d1media3-container02'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(name,obj):(E/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf8')
def verify(rows,base=R):
 for r in rows:
  assert '/evidence/suites-001/' not in r['path']
  p=base/r['path'];assert p.stat().st_size==r['bytes'] and sha(p)==r['sha256'],r['path']
seal=B/'evidence/media3-android01-freeze.json';assert sha(seal)=='fca6adcdf9783b91c9af396de3b836efad72c4d59ef820eb1924d8658f0b928a';assert sha(R/'docs/coder/D1_MEDIA3_ANDROID01_READY_DELIVERY_V1.0.md')=='660f33d468ad9f6b905795345edc8970aef641462efaa02fd39aa05759cc194e'
d=load(seal);verify(d['files']);assert len(d['files'])==740
with zipfile.ZipFile(R/d['archive']['path']) as z:
 rows={r['path']:r for r in d['files'] if r['path']!=d['archive']['path']};assert len(z.namelist())==len(set(z.namelist()))==739 and set(z.namelist())==set(rows)
 for n,r in rows.items():assert hashlib.sha256(z.read(n)).hexdigest()==r['sha256']
count=0
for row in load(B/'evidence/frozen-baseline-preservation.json'):
 assert sha(R/row['sealPath'])==row['sealSha256'];old=load(R/row['sealPath']);verify(old['files']);count+=len(old['files'])
assert count==6232
oldEvidence=[]
for row in load(B/'evidence/prior-independent-evidence-preservation.json'):
 p=R/row['manifestPath'];assert sha(p)==row['manifestSha256'];old=load(p);verify(old['evidenceFiles']);assert sha(R/old['report'])==row['reportSha256'];oldEvidence.append(dict(path=row['manifestPath'],files=len(old['evidenceFiles'])))
inputs=load(B/'evidence/final-source-dependency-inputs.json');verify(inputs,B)
for rel in ['settings-gradle.lockfile','gradle/verification-metadata.xml']:assert (B/rel).read_bytes()==(OLD/rel).read_bytes()
changed={'src/com/videokit/d1input/'+n+'.java' for n in ['HostInputFactory','HostMp4Inspection','TemporaryOutput']}
for folder in ['src','android','upstream','platform-fixtures','deps','reference/official-extractor','offline-maven']:
 for p in (OLD/folder).rglob('*'):
  if p.is_file() and p.relative_to(OLD).as_posix() not in changed:assert p.read_bytes()==(B/p.relative_to(OLD)).read_bytes(),str(p)
rows=load(B/'evidence/actual-consumption/artifacts.json');prev=load(OLD/'evidence/actual-consumption/artifacts.json');identity=lambda a:{(x['coordinate'],x['artifact']):x['sha256'] for x in a};assert identity(rows)==identity(prev) and len(rows)==300
events=[json.loads(x) for x in (B/'evidence/build-main-004/consumption.jsonl').read_text().splitlines() if x.strip()];ev={x['id']:x for x in events if x.get('name')=='Dependency verification'};counts=collections.Counter()
for row in rows:
 assert sha(B/row['path'])==row['sha256'];counts[row['kind']]+=1
 if 'reviewCopy' in row:assert sha(B/row['reviewCopy'])==row['sha256']
 m=re.fullmatch(r'Verifying (.+) \(([^:]+):([^:]+):(.+)\)',ev[row['verificationEventId']]['progressName']);a,g,n,v=m.groups();assert a==row['artifact'] and ':'.join([g,n,v])==row['coordinate']
assert dict(counts)==dict(binary=123,module=37,pom=140)
closures=load(B/'evidence/actual-consumption/configuration-closures.json');cEvents=[x for x in events if x.get('event')=='actual-configuration-closure'];assert closures==cEvents
expected=dict(debugRuntimeClasspath=17,debugCompileClasspath=12,debugAndroidTestRuntimeClasspath=0,debugAndroidTestCompileClasspath=12)
closureSummary={}
for c in closures:
 ext=sorted(x['coordinate'] for x in c['components'] if x['external']);assert len(ext)==expected[c['configuration']];assert not any('jcodec' in x or 'test:runner' in x for x in ext);closureSummary[c['configuration']]=ext
assert closureSummary['debugCompileClasspath']==closureSummary['debugAndroidTestCompileClasspath']
jc=load(B/'evidence/actual-consumption/actual-javac-classpaths.json');assert jc==[x for x in events if x.get('event')=='actual-javac-classpath'] and [len(x['files']) for x in jc]==[16,17]
for task in jc:
 for f in task['files']:
  if f.get('sha256'):assert sha(Path(f['file']))==f['sha256']
def locks(p):
 return {line.split('=')[0]:set(line.split('=')[1].split(',')) for line in p.read_text().splitlines() if line and not line.startswith('#')}
oldLock=locks(OLD/'app/gradle.lockfile');newLock=locks(B/'app/gradle.lockfile');assert set(newLock)==set(oldLock)
for coord,scopes in oldLock.items():
 if coord!='empty':assert newLock[coord]-scopes==({'debugAndroidTestCompileClasspath'} if coord in closureSummary['debugAndroidTestCompileClasspath'] else set()) and scopes<=newLock[coord]
assert 'LockMode.STRICT' in (B/'app/build.gradle.kts').read_text();receipt=load(B/'evidence/build-main-004/receipt.json');assert receipt['exitCode']==0 and receipt['strictVerification'] and receipt['strictLockMode'] and receipt['verifyMetadata'] and receipt['offline'];assert '63 actionable tasks: 63 executed' in (B/'evidence/build-main-004/gradle.log').read_text(errors='replace')
tree=ast.parse((R/'docs/tester/D1_INPUT_SINK01_REVIEW_EVIDENCE/audit_frozen.py').read_text());defs=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['pool','axml','dexclasses']];exec(compile(ast.Module(body=defs,type_ignores=[]),'existing_byte_parsers','exec'))
oldApk=OLD/'artifacts/media3-container02-compile-probe-debug.apk'
with zipfile.ZipFile(oldApk) as z:oldAndroid={c for n in z.namelist() if n.endswith('.dex') for c in dexclasses(z.read(n)) if c.startswith('Landroid/')}
assert len(oldAndroid)==280
apks=[];allClasses={}
for kind,expectedHash,expectedBytes,expectedCount in [('app','0477532af0d4f137108780acda9bb01a4fe53434f88a9aebad1f1bfd06666b04',7112721,4937),('test','7ed7e2f6051668f4ed950a48ada3cbd1bfdda4a431cf15054e7066f763794ffe',453174,312)]:
 p=B/f'artifacts/media3-android01-{kind}-debug.apk';assert sha(p)==expectedHash and p.stat().st_size==expectedBytes
 with zipfile.ZipFile(p) as z:
  tags=axml(z.read('AndroidManifest.xml'));classes=[c for n in z.namelist() if n.endswith('.dex') for c in dexclasses(z.read(n))];assert len(classes)==expectedCount;allClasses[kind]=classes
  manifest=tags[0]['attributes'];assert manifest['package']=='com.videokit.d1media3.android01'+('.test' if kind=='test' else '') and manifest['versionCode']==1 and manifest['versionName']=='D1-MEDIA3-ANDROID01-READY' and 'sharedUserId' not in manifest
  assert not any(t['tag'] in ['uses-permission','activity','service','receiver','provider'] for t in tags);assert not any(n.startswith('lib/') and n.endswith('.so') for n in z.namelist());assert {c for c in classes if c.startswith('Landroid/')}==oldAndroid
  checks={x.stem for x in (B/'checks').rglob('*.java')};assert not any('/'+n+';' in c or '/'+n+'$' in c for c in classes for n in checks);assert not any(c.startswith('Lorg/jcodec/') or c in ['Landroid/net/Uri;','Landroid/system/ErrnoException;','Landroid/system/OsConstants;'] for c in classes)
  if kind=='test':
   it=[t['attributes'] for t in tags if t['tag']=='instrumentation'];assert len(it)==1 and it[0]['name']=='com.videokit.d1media3.android01.test.Media3Instrumentation' and it[0]['targetPackage']=='com.videokit.d1media3.android01' and it[0]['targetProcesses']=='com.videokit.d1media3.android01:media3';assert hashlib.sha256(z.read('assets/sample.mp4')).hexdigest()=='720957c94b3665ff97bcc2f59ad5407c5ca54f566b59865723be9eecc0a6a1f9'
  else:assert not any(t['tag']=='instrumentation' for t in tags) and [t['attributes'] for t in tags if t['tag']=='application'][0]['process']==':media3' and 'assets/sample.mp4' not in z.namelist()
  apks.append(dict(kind=kind,bytes=p.stat().st_size,sha256=sha(p),manifest=tags,dexClasses=len(classes),androidDefinitionsUnchanged=280))
jarResults=[]
for kind,filename,classesRoot,pin in [('app','media3-android01-classes.jar','debug/compileDebugJavaWithJavac/classes','a0444cc05bb9d1be24fdf91b86b2e998708be04aba12823f23a5f5e3753cf23d'),('test','media3-android01-instrumentation-classes.jar','debugAndroidTest/compileDebugAndroidTestJavaWithJavac/classes','e2f75ff41b23d94d0f7cf015943528c339679efb7794967e920714317e7f687c')]:
 p=B/'artifacts'/filename;assert sha(p)==pin;root=B/'app/build/intermediates/javac'/classesRoot
 with zipfile.ZipFile(p) as z:
  names=[n for n in z.namelist() if n.endswith('.class')];assert set(names)=={x.relative_to(root).as_posix() for x in root.rglob('*.class')}
  for n in names:assert z.read(n)==(root/n).read_bytes()
  jarResults.append(dict(kind=kind,sha256=pin,classCount=len(names),matchesActualAndroidJavacBytes=True))
save('static-artifact-dependency-audit.json',dict(result='PASS_STATIC_MATERIAL_IDENTITY_ONLY',checkedUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),frozenRecords=740,zipMembers=739,oldFrozenFiles=count,oldEvidence=oldEvidence,inputPins=len(inputs),apks=apks,jars=jarResults,actualConsumption=dict(counts),eventCount=len(events),configurationClosures=closureSummary,actualJavacFiles=[len(x['files']) for x in jc],newDependencies=0,androidExecution='NOT_RUN',fullEntryReplay='NOT_RUN_BY_FORMAL_INSTRUCTION',pendingOwnersNotTouched=True))
# Existing signature verifier and JDK javap are static tools only; no product class initialization/test/attach.
java=Path('D:/Android/Android Studio/jbr/bin/java.exe');javap=java.with_name('javap.exe');verifier=R/'docs/tester/D1_MEDIA3_CONTAINER02_REVIEW_EVIDENCE/signature-classes';sig=B/'offline-maven/com/android/tools/build/apksig/9.3.3/apksig-9.3.3.jar';assert sha(sig)==sha(OLD/'offline-maven/com/android/tools/build/apksig/9.3.3/apksig-9.3.3.jar')
commands=[('signature-'+kind,[str(java),'-cp',str(verifier)+';'+str(sig),'VerifySignature',str(B/f'artifacts/media3-android01-{kind}-debug.apk')]) for kind in ['app','test']]
cp=';'.join(str(B/'artifacts'/n) for n in ['media3-android01-classes.jar','media3-android01-instrumentation-classes.jar'])
commands.append(('javap-static',[str(javap),'-p','-c','-classpath',cp,'com.videokit.d1android.ExperimentContract','com.videokit.d1android.VerifiedFixtureCopy','com.videokit.d1media3.android01.test.Media3Instrumentation','com.videokit.d1media3.android01.test.ExperimentJob','com.videokit.d1media3.android01.test.OwnedFiles$ReadCapability','com.videokit.d1media3.android01.test.OwnedFiles$OutputCapability']))
for name,argv in commands:
 start=datetime.datetime.now(datetime.timezone.utc).isoformat();p=subprocess.run(argv,stdout=subprocess.PIPE,stderr=subprocess.PIPE);(E/(name+'.stdout')).write_bytes(p.stdout);(E/(name+'.stderr')).write_bytes(p.stderr);save(name+'.json',dict(argv=argv,startUtc=start,endUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),exitCode=p.returncode,originalProcessReturned=True,purpose='EXISTING_STATIC_TOOL_NO_PRODUCT_OR_PROPOSAL_EXECUTION'));assert p.returncode==0
F=B/'reference/generation-proposal-source';src=F/'jcodec-0.2.5-sources.jar';proposal=load(B/'evidence/generation-proposal.json');assert sha(src)=='9945efa92e16b3fbe8eb8bf37f00be53fa0adb52d09ac978a0744ca2ef3697db' and hashlib.sha1(src.read_bytes()).hexdigest()==(F/'jcodec-0.2.5-sources.jar.sha1').read_text().strip()
matched=[]
with zipfile.ZipFile(src) as z:
 assert len(z.namelist())==807;assert not any(n.lower().endswith(('.class','.dll','.exe','.so','.jar')) for n in z.namelist())
 for p in F.glob('*.java'):
  matches=[n for n in z.namelist() if n.endswith('/'+p.name) or n==p.name];assert len(matches)==1 and z.read(matches[0])==p.read_bytes();matched.append(dict(source=p.name,entry=matches[0],sha256=sha(p)))
pom=ET.parse(F/'jcodec-0.2.5.pom').getroot();ns={'m':'http://maven.apache.org/POM/4.0.0'};assert [pom.find('m:'+n,ns).text for n in ['groupId','artifactId','version']]==['org.jcodec','jcodec','0.2.5'];assert pom.find('m:licenses/m:license/m:name',ns).text=='FreeBSD'
deps=pom.findall('m:dependencies/m:dependency',ns);assert len(deps)==1 and deps[0].find('m:scope',ns).text=='test'
assert not proposal['generationAuthorized'] and 'UNBUILT' in proposal['futureToolBuildHash'];assert sha(B/proposal['exactApiSequence']['path'])==proposal['exactApiSequence']['sha256']
for f in proposal['compilerIdentity']['files']:assert sha(Path(f['path']))==f['sha256']
save('generation-source-static-audit.json',dict(result='PASS_SOURCE_PROPOSAL_IDENTITY_ONLY_UNBUILT_BLOCKS_EXECUTION',sourceBytes=src.stat().st_size,sourceSha256=sha(src),archiveEntries=807,executableEntries=0,exactExcerptSources=matched,pomSha256=sha(F/'jcodec-0.2.5.pom'),repositoryLicenseSha256=sha(F/'LICENSE-official-repository'),licenseScope='Preserved source/POM and current official-repository license text only; not fabricated release tag, no patent/distribution clearance',toolBuildHash='UNBUILT',builtLoadedEncoded=False,gradleOrAppTestDependency=False,apiProposal='STATIC_REVIEW_ONLY',futureBinaryAdmission=False))
plan=load(B/'evidence/execution-plan.json');methods=['inspectKnown','inspectShort3','inspectUnknown','inspectSeek1s','preopenAdmission','muxQualified'];assert [x['case'] for x in plan['methods']]==methods
for m in plan['methods']:
 assert set(m['args'])=={'case','fixtureSha256','runId'} and m['args']['fixtureSha256']=='720957c94b3665ff97bcc2f59ad5407c5ca54f566b59865723be9eecc0a6a1f9' and m['deadlineMs']==60000 and m['receiptUtf8Max']==262144
 a=m['futureCommandArguments'];assert a==['am','instrument','-w','-r','-e','case',m['case'],'-e','fixtureSha256',m['args']['fixtureSha256'],'-e','runId',m['args']['runId'],'com.videokit.d1media3.android01.test/com.videokit.d1media3.android01.test.Media3Instrumentation']
budget=plan['proposedWholeFutureBudget'];assert budget['inputApkBytesExact']==7112721+453174;assert budget['outerTransferBytesWhole']==sum(budget[k] for k in ['inputBytesWhole','textBytesWhole','controlBytesWhole','proofBytesWhole']);assert len(plan['proposedOperations'])==budget['deviceOperationsMax']==14;assert plan['scopeId'] is None and plan['captureToolIdentity'] is None
pending=load(B/'evidence/earlier-suite-pending.json');assert not pending['processReturnProven'] and pending['toolSession']==48945 and pending['threadDumpAttempt']['toolSession']==17257 and len(pending['completedReceipts'])==29
summary=load(B/'evidence/documented-entry-prefreeze/summary.json');assert len(summary['runs'])==62 and all(x['exitCode']==0 for x in summary['runs'])
save('execution-and-unknown-review.json',dict(materialPlan='SIX_METHODS_STATICALLY_MATCHED_NOT_EXECUTED',methods=plan['methods'],budget=budget,executionAuthorized=False,unknownOriginal=dict(javaPidAtPriorObservation=39256,parentPidAtPriorObservation=35988,toolSession=48945,jcmdSession=17257,priorCompletedReceipts=29,currentProcessState='NOT_OBSERVED_NO_QUERY_OR_ATTACH_BY_THIS_REVIEW',returnProven=False,rootCause='UNKNOWN',later62ReceiptsDoNotReplaceOriginalReturn=True,activeDirectoryRead=False,ownerTouched=False),coderLaterRuns=62,independentFullOrFocusedReplay='NOT_RUN_FORMALLY_WITHHELD',generation='UNBUILT_NOT_EXECUTED',devices=0))
print('PASS static740/ZIP739; APKs/JARs/strict closures; existing signature tools and javap returned; source proposal only; all functional replays NOT_RUN')
