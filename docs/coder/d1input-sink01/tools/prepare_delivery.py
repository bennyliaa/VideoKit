from pathlib import Path
import json,hashlib,zipfile,shutil,re,subprocess,xml.etree.ElementTree as ET,difflib,collections,datetime
R=Path('D:/CodexProjects/VideoKit');B=R/'docs/coder/d1input-sink01';E=B/'evidence';assert not (E/'input-sink01-freeze.json').exists()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
assert json.loads((E/'build-main-005/receipt.json').read_text(encoding='utf-8-sig'))['exitCode']==0
assert 'LockMode.STRICT' in (B/'app/build.gradle.kts').read_text() and '<verify-metadata>true</verify-metadata>' in (B/'gradle/verification-metadata.xml').read_text()
pins={}
for c in ET.parse(B/'gradle/verification-metadata.xml').getroot().iter():
 if c.tag.split('}')[-1]=='component':
  for a in c:pins[(c.get('group'),c.get('name'),c.get('version'),a.get('name'))]={h.get('value') for h in a if h.tag.split('}')[-1]=='sha256'}
observed={};D=E/'actual-consumption';D.mkdir(exist_ok=True)
for line in (E/'build-main-005/consumption.jsonl').read_text().splitlines():
 op=json.loads(line)
 if op['name']!='Dependency verification':continue
 m=re.fullmatch(r'Verifying (.+) \(([^:]+):([^:]+):(.+)\)',op['progressName']);assert m,op
 artifact,g,a,v=m.groups();p=B/'offline-maven'/g.replace('.','/')/a/v/artifact;h=sha(p);assert h in pins[(g,a,v,artifact)]
 kind='pom' if artifact.endswith('.pom') else 'module' if artifact.endswith('.module') else 'binary';x={'coordinate':':'.join([g,a,v]),'artifact':artifact,'path':p.relative_to(B).as_posix(),'bytes':p.stat().st_size,'sha256':h,'kind':kind,'verificationEventId':op['id']}
 if kind!='binary':
  dest=D/'metadata'/p.relative_to(B/'offline-maven');dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dest);x['reviewCopy']=dest.relative_to(B).as_posix()
 observed[(g,a,v,artifact)]=x
records=sorted(observed.values(),key=lambda x:(x['coordinate'],x['artifact']));dump(D/'artifacts.json',records);dump(D/'summary.json',{'actualArtifacts':len(records),'counts':dict(collections.Counter(x['kind'] for x in records)),'strict':True,'verifyMetadata':True,'strictLocks':True,'buildAttempt':'005','observation':'Actual Gradle verification operations, not all cached candidates','newVerificationPins':0,'verificationMetadataUnchangedFromFrozenRender02':(B/'gradle/verification-metadata.xml').read_bytes()==(R/'docs/coder/d1render02/gradle/verification-metadata.xml').read_bytes()})
def locked(path):return {l.split('=')[0] for l in path.read_text().splitlines() if l and not l.startswith('#') and not l.startswith('empty=')}
runtime=locked(B/'app/gradle.lockfile');old=locked(R/'docs/coder/d1render02/app/gradle.lockfile');oldbom=json.loads((R/'docs/coder/d1render02/render02-sbom.cdx.json').read_text());oldcomp={c.get('group','')+':'+c['name']+':'+c['version']:c for c in oldbom['components'] if c.get('group')}
components=[]
for coordinate in sorted(runtime):
 g,a,v=coordinate.split(':');binary=[x for x in records if x['coordinate']==coordinate and x['kind']=='binary'];license=oldcomp.get(coordinate,{}).get('licenses',[{'expression':'Apache-2.0'}]);components.append({'type':'library','group':g,'name':a,'version':v,'purl':f'pkg:maven/{g}/{a}@{v}','hashes':[{'alg':'SHA-256','content':x['sha256']} for x in binary],'licenses':license,'properties':[{'name':'identitySource','value':'Actual strict build; pre-existing verification pins; official new-use metadata evidence where applicable'},{'name':'binaryKind','value':'actual selected artifact' if binary else 'metadata/variant alias'}]})
dump(B/'input-sink01-sbom.cdx.json',{'bomFormat':'CycloneDX','specVersion':'1.6','version':1,'metadata':{'component':{'type':'application','name':'VideoKit D1 INPUT_SINK01 compile probe','version':'D1-20261021-INPUT-SINK01'}},'components':components})
dump(E/'dependency-license-difference.json',{'candidateLockedCoordinates':len(runtime),'newUseComparedToRender02':sorted(runtime-old),'priorProductVersionChanges':[],'notUsedInSeparateCompileProbe':sorted(old-runtime),'oldProductUnmodified':True,'newArtifactDownloads':0,'sameExactMedia3':'1.9.3','officialNewUse':'official-added-dependencies/receipt.json','newUseLicenses':'datasource/database/exif POMs all Apache-2.0; raw license text retained','independentNewUseAdmission':'PENDING_REVIEW_NOT_SELF_APPROVED','notUsedIsNotProductRemoval':True})
for x in json.loads((E/'local-007/source-pins.json').read_text()):assert sha(B/x['path'])==x['sha256']
for x in json.loads((E/'jvm-transitive-classpath.json').read_text()):assert sha(B/x['path'])==x['sha256']
dump(E/'local-007/classpath-end-binding.json',[{'path':p.relative_to(B).as_posix(),'sha256':sha(p),'binding':'end-of-batch check against unchanged original extraction/transitive pins'} for p in sorted((B/'deps').glob('*.jar'))])
art=B/'artifacts';art.mkdir(exist_ok=True);apk=art/'input-sink01-compile-probe-debug.apk';originalApk=B/'app/build/outputs/apk/debug/app-debug.apk'
if apk.exists():assert apk.read_bytes()==originalApk.read_bytes()
else:shutil.copyfile(originalApk,apk)
classes=B/'app/build/intermediates/javac/debug/compileDebugJavaWithJavac/classes';jar=art/'input-sink01-classes.jar'
if jar.exists():
 with zipfile.ZipFile(jar) as z:
  assert set(z.namelist())=={p.relative_to(classes).as_posix() for p in classes.rglob('*.class')}
  for p in classes.rglob('*.class'):assert z.read(p.relative_to(classes).as_posix())==p.read_bytes()
else:
 with zipfile.ZipFile(jar,'x',zipfile.ZIP_DEFLATED) as z:
  for p in sorted(classes.rglob('*.class')):assert p.relative_to(classes).as_posix().startswith('com/videokit/');z.write(p,p.relative_to(classes).as_posix())
z=zipfile.ZipFile(apk);dex=b''.join(z.read(n) for n in z.namelist() if n.endswith('.dex'))
assert not any(n.startswith('lib/') for n in z.namelist());assert b'InputSinkCheck' not in dex and b'controlled_ready_token' not in dex and b'fixture-ui' not in dex
for name in ['HostDataSource','HostInputFactory','TemporaryOutput','MatureMuxerBinding','AndroidGrantedStream','PlatformOutputErrors']:assert ('Lcom/videokit/d1input/'+name+';').encode() in dex
manifest=B/'app/build/intermediates/merged_manifests/debug/processDebugManifest/AndroidManifest.xml';root=ET.parse(manifest).getroot();assert root.get('package')=='com.videokit.d1input';assert not root.findall('uses-permission');assert not list(root.find('application'));shutil.copyfile(manifest,E/'compile-probe-merged-manifest.xml')
V=E/'signature-audit';V.mkdir(exist_ok=True);shutil.copyfile(R/'docs/coder/d1render02/tools/VerifyApk.java',B/'tools/VerifyApk.java');apksig=B/'offline-maven/com/android/tools/build/apksig/9.3.3/apksig-9.3.3.jar';assert sha(apksig) in pins[('com.android.tools.build','apksig','9.3.3',apksig.name)];J=Path('D:/Android/Android Studio/jbr/bin');vc=V/'classes';vc.mkdir(exist_ok=True)
for name,args in [('compile',[str(J/'javac.exe'),'--release','11','-encoding','UTF-8','-cp',str(apksig),'-d',str(vc),str(B/'tools/VerifyApk.java')]),('verify',[str(J/'java.exe'),'-cp',str(vc)+';'+str(apksig),'VerifyApk',str(apk)])]:
 if (V/(name+'.json')).exists():assert json.loads((V/(name+'.json')).read_text())['exitCode']==0
 else:
  p=subprocess.run(args,stdout=subprocess.PIPE,stderr=subprocess.PIPE);(V/(name+'.stdout')).write_bytes(p.stdout);(V/(name+'.stderr')).write_bytes(p.stderr);dump(V/(name+'.json'),{'argv':args,'exitCode':p.returncode,'originalProcessReturned':True,'SDKCommand':False});assert p.returncode==0
out=[{'path':p.relative_to(R).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in [apk,jar]];dump(E/'artifact-audit.json',{'result':'PASS_COMPILE_PROBE_ONLY','artifacts':out,'package':'com.videokit.d1input','versionCode':1,'permissions':[],'components':[],'nativeLibraries':0,'testAndPlatformPortClassesExcluded':True,'APKRuntime':'NOT_RUN','actualMedia3AndAndroidCompile':True,'signerCertificateSha256':'5e841a04968f3f790f6996ca5e286d8c2734338542486909f9a136717dde808f','publicSignatureVerification':'signature-audit/verify.stdout'})
preserved=[]
for directory,filename in [('d1render01','render01-freeze.json'),('d1render02','render02-freeze.json'),('d1render02-capture','capture-adapt-freeze.json')]:
 s=R/'docs/coder'/directory/'evidence'/filename;f=json.loads(s.read_text());assert all(sha(R/x['path'])==x['sha256'] for x in f['files']);preserved.append({'candidate':directory,'sealSha256':sha(s),'filesUnchanged':len(f['files'])})
dump(E/'frozen-baseline-preservation.json',preserved)
reuse=json.loads((E/'reused-source-pins.json').read_text());changes=[];evolution=[]
for x in reuse:
 p=B/x['path']
 if sha(R/x['source'])!=x['sha256']:
  assert x['source']=='docs/milestones/D1_INPUT_SINK01_CODER_REQUIREMENTS_V1.0.md';oldText=p.read_text();newText=(R/x['source']).read_text();assert newText.startswith(oldText.rstrip()) and '阶段A集中基线补充' in newText[len(oldText.rstrip()):];latest=B/'reference/D1_INPUT_SINK01_CODER_REQUIREMENTS_WITH_PHASE_A_SUPPLEMENT.md';shutil.copyfile(R/x['source'],latest);evolution.append({'source':x['source'],'initialSha256':x['sha256'],'currentSha256':sha(R/x['source']),'latestCopy':latest.relative_to(B).as_posix(),'reason':'Coordinator-approved Phase A A01/A02 append-only supplement received during batch; both old snapshot and latest retained; production frozen sources unchanged'})
 if sha(p)!=x['sha256']:
  changes.append({'path':x['path'],'originalSha256':x['sha256'],'candidateSha256':sha(p)});(E/(p.stem+'-source-diff.patch')).write_text(''.join(difflib.unified_diff((R/x['source']).read_text().splitlines(True),p.read_text().splitlines(True),fromfile=x['source'],tofile=x['path'])),encoding='utf-8')
assert {Path(x['path']).stem for x in changes}=={'E13SourceGroup','SinkCoordinator'};dump(E/'upstream-source-differences.json',changes)
dump(E/'requirement-evolution.json',evolution)
for name in ['docs/tester/D1_INPUT_SINK01_OFFLINE_BASELINE_REPORT_V1.0.md','docs/tester/D1_INPUT_SINK01_PHASE_A_EVIDENCE/reusable-regression-cases.json']:
 p=R/name;shutil.copyfile(p,B/'reference'/p.name)
assert sha(B/'reference/D1_INPUT_SINK01_OFFLINE_BASELINE_REPORT_V1.0.md')=='db797e0a7714982b85dc474eabc70273c9ea49fc97c88fdf98a54ea0874379a1'
cases=json.loads((B/'reference/reusable-regression-cases.json').read_text())['cases'];dump(B/'independent-regression-map.json',{'baselineReportSha256':'db797e0a7714982b85dc474eabc70273c9ea49fc97c88fdf98a54ea0874379a1','cases':[{'id':x['id'],'title':x['title'],'candidateCoderResult':'NOT_RUN_PLATFORM' if x['id']=='S05' else 'PASS_LIMITED_LOCAL','scope':'actual DataSource/host ports and original bridge/registry/coordinator; controlled validator never actual media format; S05 Android muxer/FD NOT_RUN'} for x in cases],'localSemanticGroups':20,'notAll19PlatformCasesPassed':True})
fixture=evidence=E/'local-007/generated-4b.tmp';data32=bytes((((p*1664525+0x20261020)>>9)&255) for p in range(32));dump(E/'generated-fixture-identities.json',{'seed':0x20261020,'pattern':'((position*1664525+0x20261020) >>>9)&255','sparseLogicalOffset':3*1024*1024*1024+7,'maximumAllocatedTestBlockBytes':65537,'realFileBytes':fixture.stat().st_size,'realFileSha256':sha(fixture),'partialInput32Sha256':hashlib.sha256(data32).hexdigest(),'actualContainerFixture':False,'giantFileAllocated':False})
inputs=[{'path':p.relative_to(B).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(B.rglob('*')) if p.is_file() and (p.relative_to(B).parts[0] in ['src','android','upstream','deps','gradle','offline-maven'] or p.relative_to(B).as_posix() in ['build.gradle.kts','settings.gradle.kts','gradle.properties','local.properties','app/build.gradle.kts','app/gradle.lockfile','settings-gradle.lockfile','app/src/main/AndroidManifest.xml'])];dump(E/'final-source-dependency-inputs.json',inputs)
dump(B/'completion-matrix.json',{'candidate':'D1-20261021-INPUT-SINK01','D1':'NOT_PASSED','M0':'NOT_STARTED','rows':[{'id':i,'status':s,'scope':scope} for i,s,scope in [
 ('ACTUAL_DATASOURCE','PASS','real Media3 1.9.3 DataSource/Factory/DataSpec;20 local semantic groups'),('GAP_A01','PASS','shared Provider capability one read in flight, queue0;two total sources;original registry remains sole release authority'),('GAP_A02','PASS','controlled actual7/attempt32;SDK acknowledged lower bound0 + UNKNOWN;no rewind/retry/READY/COMMIT'),('OUTPUT_LAYERS','PASS','host capability/partial writes/flush-close/original workers/reopen/hash/controlled validation/READY/explicit controlled COMMIT separated'),('REAL_HOST_FILE_REOPEN','PASS','generated4B real local file only; controlled validation rejection;not actual media'),('PLATFORM_MUXER_FD','NOT_RUN','actual Android/Media3/E6 interfaces compiled;real codec/muxer/FD/fsync/container validation not executed'),('DEPENDENCY_IDENTITY','PASS','same1.9.3 cached pinned binaries;official fixed module/POM and Apache source evidence;strict locks/metadata'),('NEW_USE_INDEPENDENT_ADMISSION','BLOCKED','datasource/database/exif new-use intake pending independent review;not self-approved'),('FROZEN_PRIOR_CANDIDATES','PASS','1699 old frozen files unchanged;old source pins unchanged'),('REAL_DEVICE_AND_HOST_COMMIT','NOT_RUN','no SDK/ADB/5037/device/old handles;controlled host commit not business publication'),('M0_API','NOT_RUN','candidate invariants documented;final API/thresholds not frozen;M0 not started'),('FULL_D1','BLOCKED','all inherited P0/UNKNOWN/licensing and actual effects not closed')]]})
print(json.dumps({'artifacts':out,'runtimeCoordinates':len(runtime),'actualArtifacts':len(records),'newUse':sorted(runtime-old),'sourceDifferences':changes,'baselinePreserved':preserved},ensure_ascii=False,indent=2))
