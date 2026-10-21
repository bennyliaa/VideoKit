from pathlib import Path
import ast,collections,difflib,hashlib,json,re,shutil,struct,xml.etree.ElementTree as ET,zipfile
B=Path(__file__).resolve().parents[1];R=B.parents[2];E=B/'evidence';O=R/'docs/coder/d1media3-android02';A=B/'artifacts'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,x):p.parent.mkdir(exist_ok=True,parents=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def pin(p):return {'path':p.relative_to(B).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)}
assert not (E/'recovery01-freeze.json').exists()
for n in ['001','002']:
 x=json.loads((E/f'build-{n}/owner.json').read_text());assert x['exitCode']==0 and x['daemonOriginalReturned'] and x['originalClientReturned'] and x['captureHandlesClosed'] and x['daemon']['sameHandleSignalled'] and x['daemon']['exitCode']==0
for x in json.loads((E/'final-build-input-pins.json').read_text()):assert sha(B/x['path'])==x['sha256']
for n in ['gradle/verification-metadata.xml','app/gradle.lockfile','settings-gradle.lockfile']:assert (B/n).read_bytes()==(O/n).read_bytes()
pins={}
for c in ET.parse(B/'gradle/verification-metadata.xml').getroot().iter():
 if c.tag.split('}')[-1]=='component':
  for a in c:pins[(c.get('group'),c.get('name'),c.get('version'),a.get('name'))]={h.get('value') for h in a if h.tag.split('}')[-1]=='sha256'}
events=[json.loads(x) for x in (E/'build-002/consumption.jsonl').read_text().splitlines()];records={}
for op in events:
 if op.get('name')!='Dependency verification':continue
 m=re.fullmatch(r'Verifying (.+) \(([^:]+):([^:]+):(.+)\)',op['progressName']);assert m,op
 artifact,g,a,v=m.groups();p=B/'offline-maven'/g.replace('.','/')/a/v/artifact;assert sha(p) in pins[(g,a,v,artifact)]
 row={'coordinate':':'.join([g,a,v]),'artifact':artifact,'path':p.relative_to(B).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p),'eventId':op['id'],'kind':'pom' if artifact.endswith('.pom') else 'module' if artifact.endswith('.module') else 'binary'}
 if row['kind']!='binary':
  target=E/'actual-consumption/metadata'/p.relative_to(B/'offline-maven');target.parent.mkdir(exist_ok=True,parents=True);shutil.copyfile(p,target);row['reviewCopy']=target.relative_to(B).as_posix()
 records[(g,a,v,artifact)]=row
rows=sorted(records.values(),key=lambda x:(x['coordinate'],x['artifact']));old=json.loads((R/'docs/coder/d1media3-android01/evidence/actual-consumption/artifacts.json').read_text());assert {(x['coordinate'],x['artifact'],x['sha256']) for x in rows}=={(x['coordinate'],x['artifact'],x['sha256']) for x in old}
dump(E/'actual-consumption/artifacts.json',rows)
locks={l.split('=')[0]:set(l.split('=')[1].split(',')) for l in (B/'app/gradle.lockfile').read_text().splitlines() if l and not l.startswith(('#','empty='))};assert len(locks)==17
closures=[x for x in events if x.get('event')=='actual-configuration-closure'];cps=[x for x in events if x.get('event')=='actual-javac-classpath'];assert len(closures)==4 and len(cps)==2
summary={}
for c in closures:
 actual=sorted({x['componentId'] for x in c['components'] if x['external']});assert actual==sorted(k for k,v in locks.items() if c['configuration'] in v);summary[c['configuration']]={'externalCoordinates':actual,'externalCount':len(actual),'projectComponents':[x for x in c['components'] if not x['external']]}
assert [summary[x]['externalCount'] for x in ['debugCompileClasspath','debugRuntimeClasspath','debugAndroidTestCompileClasspath','debugAndroidTestRuntimeClasspath']]==[12,17,12,0]
dump(E/'actual-consumption/configuration-closures.json',closures);dump(E/'actual-consumption/closure-summary.json',summary);dump(E/'actual-consumption/javac-classpaths.json',cps);dump(E/'actual-consumption/summary.json',{'actualArtifacts':len(rows),'counts':dict(collections.Counter(x['kind'] for x in rows)),'sameExternalIdentitiesAsAndroid01':True,'strictActualVerificationEvents':True,'actualSeparateClosureCounts':[12,17,12,0],'finalBuild':'002'})
app=A/'media3-android02-recovery01-app-debug.apk';test=A/'media3-android02-recovery01-test-debug.apk';shutil.copyfile(B/'app/build/outputs/apk/debug/app-debug.apk',app);shutil.copyfile(B/'app/build/outputs/apk/androidTest/debug/app-debug-androidTest.apk',test)
parser=R/'docs/tester/D1_INPUT_SINK01_REVIEW_EVIDENCE/audit_frozen.py';tree=ast.parse(parser.read_text());defs=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['pool','axml','dexclasses']];assert len(defs)==3;exec(compile(ast.Module(body=defs,type_ignores=[]),'frozen_pure_manifest_dex_parser','exec'))
originParser=R/'docs/coder/d1fixture-tool02/tools/audit_build.py';tree=ast.parse(originParser.read_text());defs=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='class_origin'];assert len(defs)==1;exec(compile(ast.Module(body=defs,type_ignores=[]),'frozen_pure_class_origin','exec'))
dump(E/'parser-origins.json',[{'path':str(p),'sha256':sha(p),'functions':f} for p,f in [(parser,['pool','axml','dexclasses']),(originParser,['class_origin'])]])
sources={}
for folder in ['src','android','upstream','instrumentation']:
 for p in (B/folder).rglob('*.java'):
  text=p.read_text();m=re.search(r'package\s+([\w.]+)\s*;',text);key=m.group(1).replace('.','/')+'/'+p.name;assert key not in sources;sources[key]=p
origins=[];jars=[]
for name,folder in [('media3-android02-recovery01-classes.jar','app/build/intermediates/javac/debug/compileDebugJavaWithJavac/classes'),('media3-android02-recovery01-instrumentation-classes.jar','app/build/intermediates/javac/debugAndroidTest/compileDebugAndroidTestJavaWithJavac/classes')]:
 jar=A/name
 with zipfile.ZipFile(jar,'x',zipfile.ZIP_DEFLATED) as z:
  for p in sorted((B/folder).rglob('*.class')):
   cn,sf,major=class_origin(p.read_bytes());key=cn.rsplit('/',1)[0]+'/'+sf;assert key in sources and major==55;source=sources[key];assert cn.startswith('com/videokit/')
   entry=p.relative_to(B/folder).as_posix();assert entry==cn+'.class';z.write(p,entry);origins.append({'className':cn,'classFile':p.relative_to(B).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p),'source':source.relative_to(B).as_posix(),'sourceSha256':sha(source),'sourceFile':sf,'major':major,'jar':jar.relative_to(B).as_posix(),'entry':entry})
 jars.append(pin(jar))
dump(E/'class-origins.json',origins)
audits=[]
for p,pkg,isTest in [(app,'com.videokit.d1media3.android02',False),(test,'com.videokit.d1media3.android02.test',True)]:
 with zipfile.ZipFile(p) as z:
  assert z.testzip() is None;tags=axml(z.read('AndroidManifest.xml'));attrs=tags[0]['attributes'];assert attrs['package']==pkg and attrs['versionCode']==1 and attrs['versionName']=='D1-MEDIA3-ANDROID02-RECOVERY01' and 'sharedUserId' not in attrs
  assert not any(t['tag'] in ['uses-permission','uses-permission-sdk-23','activity','activity-alias','service','provider','receiver'] for t in tags);assert not any(n.startswith('lib/') for n in z.namelist())
  classes=[c for n in z.namelist() if n.endswith('.dex') for c in dexclasses(z.read(n))];assert not any(c.startswith('Lorg/jcodec/') or '/Android02NonMediaCheck' in c or '/ContainerB01Regression' in c or '/InputSinkCheck' in c for c in classes)
  assert not any(c in ['Landroid/net/Uri;','Landroid/system/ErrnoException;','Landroid/system/OsConstants;'] for c in classes)
  oldzip=R/'docs/coder/d1media3-android01/artifacts'/('media3-android01-test-debug.apk' if isTest else 'media3-android01-app-debug.apk')
  with zipfile.ZipFile(oldzip) as oz:oldandroid={c for n in oz.namelist() if n.endswith('.dex') for c in dexclasses(oz.read(n)) if c.startswith('Landroid/')}
  assert {c for c in classes if c.startswith('Landroid/')}==oldandroid
  application=next(t['attributes'] for t in tags if t['tag']=='application');assert application['allowBackup']==False and application['usesCleartextTraffic']==False
  instruments=[t['attributes'] for t in tags if t['tag']=='instrumentation']
  if isTest:
   assert len(instruments)==1 and instruments[0]['name']==pkg+'.Media3Instrumentation' and instruments[0]['targetPackage']=='com.videokit.d1media3.android02' and instruments[0]['targetProcesses']=='com.videokit.d1media3.android02:media3'
   assert not any(c.startswith('Landroidx/media3/') for c in classes)
   for name in ['qualified-six-avc.mp4','qualified-fixture.json','sample.mp4','SOURCE_AND_LICENSE.txt','SYNTHETIC_SOURCE.txt']:assert z.read('assets/'+name)==(B/'instrumentation-assets'/name).read_bytes()
   asset=z.read('assets/qualified-six-avc.mp4');assert len(asset)==8849 and hashlib.sha256(asset).hexdigest()=='19e815a413ae8275fe61e917ff9ac3c67d74a4f845df548a6ce2c382c0778a9c'
  else:assert not instruments and application['process']==':media3' and 'assets/qualified-six-avc.mp4' not in z.namelist()
  audits.append({**pin(p),'package':pkg,'manifest':tags,'dexClassCount':len(classes),'dexClasses':classes,'nativeLibraries':0,'permissions':[],'instruments':instruments,'sameInheritedAndroidDefinitionSet':True,'sameUidIsRceIsolation':False,'AndroidRuntime':'NOT_RUN'})
dump(E/'artifact-audit.json',{'status':'PASS_OFFLINE_APK_MANIFEST_DEX_SOURCE_CLASS_AUDIT_NOT_RUNTIME','apks':audits,'jars':jars,'classFiles':len(origins),'signature':'SEPARATE_REAL_APKSIG_RECEIPT_REQUIRED'})
differences=[]
for folder in ['src','android','upstream','instrumentation','app/src']:
 for p in sorted((B/folder).rglob('*')):
  if not p.is_file():continue
  rel=p.relative_to(B).as_posix();old=O/rel
  if old.exists() and old.read_bytes()==p.read_bytes():continue
  differences.append({'path':rel,'oldSha256':sha(old) if old.exists() else None,'newSha256':sha(p)})
  delta=''.join(difflib.unified_diff(old.read_text().splitlines(True) if old.exists() else [],p.read_text().splitlines(True),fromfile='frozen-android02/'+rel,tofile='recovery01/'+rel));dest=B/'patches'/Path(rel).with_suffix('.patch');dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(delta,encoding='utf-8')
dump(E/'source-differences.json',differences)
print(json.dumps({'apks':[pin(app),pin(test)],'jars':jars,'classOrigins':len(origins),'sourceDifferences':len(differences),'actualArtifacts':len(rows),'closureCounts':[12,17,12,0]},ensure_ascii=False))
