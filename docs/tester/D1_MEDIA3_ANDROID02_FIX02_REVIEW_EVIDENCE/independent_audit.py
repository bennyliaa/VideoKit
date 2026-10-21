from pathlib import Path
import ast,collections,datetime,difflib,hashlib,json,re,struct,xml.etree.ElementTree as ET,zipfile
R=Path('D:/CodexProjects/VideoKit');B=R/'docs/coder/d1media3-android02-fix02';O=R/'docs/coder/d1media3-android02-recovery01';E=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def hb(b):return hashlib.sha256(b).hexdigest()
def save(n,x):(E/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def defs(p,names):
 t=ast.parse(p.read_text(encoding='utf-8-sig'));d=[n for n in t.body if isinstance(n,ast.FunctionDef) and n.name in names];assert len(d)==len(names);exec(compile(ast.Module(body=d,type_ignores=[]),str(p),'exec'),globals())
parser=R/'docs/tester/D1_INPUT_SINK01_REVIEW_EVIDENCE/audit_frozen.py';mp=R/'docs/tester/D1_MEDIA3_ANDROID01_READY_PHASE_B_EVIDENCE/audit_dex_and_mapping.py'
defs(parser,{'pool','axml','dexclasses'});defs(mp,{'methods'})
save('parser-origins.json',[{'path':str(p),'sha256':sha(p),'functions':f} for p,f in [(parser,['pool','axml','dexclasses']),(mp,['methods'])]])
s=B/'evidence/fix02-freeze.json';assert sha(s)=='39acf77353697204d0ee94d573708b11d926d4efcfd5b530696a21f52efbe0ad';seal=read(s);assert len(seal['files'])==874
for x in seal['files']:
 p=R/x['path'];assert p.resolve().is_relative_to(R) and p.stat().st_size==x['bytes'] and sha(p)==x['sha256'],x
zpath=R/seal['archive']['path'];assert zpath.stat().st_size==seal['archive']['bytes'] and sha(zpath)==seal['archive']['sha256']
with zipfile.ZipFile(zpath) as z:
 assert len(z.namelist())==len(set(z.namelist()))==874 and set(z.namelist())=={x['path'] for x in seal['files']}
 for x in seal['files']:
  b=z.read(x['path']);assert len(b)==x['bytes'] and hb(b)==x['sha256']
diff=[]
for folder in ['src','android','upstream','instrumentation','app/src']:
 old={p.relative_to(O).as_posix():p for p in (O/folder).rglob('*') if p.is_file()};new={p.relative_to(B).as_posix():p for p in (B/folder).rglob('*') if p.is_file()};assert old.keys()<=new.keys()
 for rel,p in sorted(new.items()):
  if rel not in old or sha(old[rel])!=sha(p):diff.append({'path':rel,'oldSha256':sha(old[rel]) if rel in old else None,'newSha256':sha(p)})
assert {json.dumps(x,sort_keys=True) for x in diff}=={json.dumps(x,sort_keys=True) for x in read(B/'evidence/source-differences.json')} and len(diff)==14
config={n:{'same':(B/n).read_bytes()==(O/n).read_bytes(),'oldSha256':sha(O/n),'newSha256':sha(B/n)} for n in ['app/build.gradle.kts','app/gradle.lockfile','settings-gradle.lockfile','gradle/verification-metadata.xml']};assert all(config[n]['same'] for n in config if n!='app/build.gradle.kts')
delta=''.join(difflib.unified_diff((O/'app/build.gradle.kts').read_text().splitlines(True),(B/'app/build.gradle.kts').read_text().splitlines(True)));assert (O/'app/build.gradle.kts').read_text().replace('D1-MEDIA3-ANDROID02-RECOVERY01','D1-MEDIA3-ANDROID02-FIX02')==(B/'app/build.gradle.kts').read_text()
save('independent-source-differences.json',{'changes':diff,'config':config,'gradleVersionDiff':delta,'wholeProductionFamilySetVerified':True})
pins={}
for c in ET.parse(B/'gradle/verification-metadata.xml').getroot().iter():
 if c.tag.split('}')[-1]=='component':
  coord=':'.join(c.get(k) for k in ['group','name','version'])
  for a in c:pins[(coord,a.get('name'))]={h.get('value') for h in a if h.tag.split('}')[-1]=='sha256'}
assert any(x.tag.split('}')[-1]=='verify-metadata' and x.text=='true' for x in ET.parse(B/'gradle/verification-metadata.xml').getroot().iter())
art=read(B/'evidence/actual-consumption/artifacts.json');expected={(x['coordinate'],x['artifact'],x['sha256']) for x in art};assert len(expected)==300
for x in art:
 assert x['sha256'] in pins[x['coordinate'],x['artifact']] and sha(B/x['path'])==x['sha256']
 if 'reviewCopy' in x:assert sha(B/x['reviewCopy'])==x['sha256']
old=read(R/'docs/coder/d1media3-android01/evidence/actual-consumption/artifacts.json');assert expected=={(x['coordinate'],x['artifact'],x['sha256']) for x in old}
locks={a:set(b.split(',')) for a,b in [l.split('=',1) for l in (B/'app/gradle.lockfile').read_text().splitlines() if l and not l.startswith(('#','empty='))]};assert len(locks)==17
builds=[]
for num in ['001']:
 d=B/'evidence'/('build-'+num);owner=read(d/'owner.json');raw=(d/'stdout.raw').read_text(encoding='utf-8',errors='replace');err=(d/'stderr.raw').read_text(encoding='utf-8',errors='replace');log=(d/'single-use-daemon.raw.log').read_text(encoding='utf-8',errors='replace')
 assert owner['exitCode']==0 and owner['originalClientReturned'] and owner['captureHandlesClosed'] and not owner['captureErrors'] and owner['daemonOriginalReturned'] and owner['daemon']['sameHandleSignalled'] and owner['daemon']['waitResult']==owner['daemon']['exitCode']==0
 assert owner['daemonUid'] in log and ('pid='+str(owner['daemon']['pid'])) in log and ('pid: '+str(owner['daemon']['pid'])) in raw
 assert sha(d/'single-use-daemon.raw.log')==owner['daemonLogSha256'] and 'BUILD SUCCESSFUL' in raw and 'Daemon vm is shutting down' in log
 assert '--offline' in owner['argv'] and '--no-daemon' in owner['argv'] and owner['argv'][owner['argv'].index('--dependency-verification')+1]=='strict' and owner['killInterruptStopRetry']==0
 assert all(':app:'+t in raw for t in ['compileDebugJavaWithJavac','compileDebugAndroidTestJavaWithJavac','assembleDebug','assembleDebugAndroidTest'])
 assert (d/'stdout.raw').stat().st_size==owner['stdoutBytes']<=16777216 and (d/'stderr.raw').stat().st_size==owner['stderrBytes']<=16777216
 events=[json.loads(l) for l in (d/'consumption.jsonl').read_text().splitlines()];identities=set()
 for x in events:
  if x.get('name')=='Dependency verification':
   m=re.fullmatch(r'Verifying (.+) \(([^:]+):([^:]+):(.+)\)',x['progressName']);assert m;an,g,a,v=m.groups();p=B/'offline-maven'/g.replace('.','/')/a/v/an;identities.add((':'.join([g,a,v]),an,sha(p)))
 assert identities==expected
 closures=[x for x in events if x.get('event')=='actual-configuration-closure'];assert len(closures)==4;counts={}
 for c in closures:
  actual={x['componentId'] for x in c['components'] if x['external']};assert actual=={k for k,v in locks.items() if c['configuration'] in v};counts[c['configuration']]=len(actual)
 assert [counts[n] for n in ['debugCompileClasspath','debugRuntimeClasspath','debugAndroidTestCompileClasspath','debugAndroidTestRuntimeClasspath']]==[12,17,12,0]
 cps=[x for x in events if x.get('event')=='actual-javac-classpath'];assert len(cps)==2
 builds.append({'attempt':num,'clientPid':owner['clientPid'],'daemon':owner['daemon'],'daemonUid':owner['daemonUid'],'startUtc':owner['startUtc'],'endUtc':owner['endUtc'],'stdoutBytes':owner['stdoutBytes'],'stderrBytes':owner['stderrBytes'],'strictIdentities':len(identities),'closures':counts,'javacClasspathEvents':len(cps),'oldUnknownNotResolvedByTheseHandles':True})
save('independent-build-consumption.json',{'builds':builds,'artifactKinds':dict(collections.Counter(x['kind'] for x in art)),'locksUnchanged':True,'actualArtifactRows':art,'scope':'FROZEN_ORIGINAL_RECEIPTS_ONLY_NO_NEW_GRADLE_OR_HANDLE_QUERY'})
for x in read(B/'evidence/final-build-input-pins.json'):assert sha(B/x['path'])==x['sha256']
origins=read(B/'evidence/class-origins.json');assert len(origins)==105
def class_origin(b):
 assert b[:4]==bytes.fromhex('cafebabe');major=struct.unpack_from('>H',b,6)[0];n=struct.unpack_from('>H',b,8)[0];cp=[None]*n;p=10;i=1
 while i<n:
  t=b[p];p+=1
  if t==1:k=struct.unpack_from('>H',b,p)[0];p+=2;cp[i]=b[p:p+k].decode('utf-8','replace');p+=k
  elif t in (7,8,16,19,20):cp[i]=struct.unpack_from('>H',b,p)[0];p+=2
  elif t in (3,4,9,10,11,12,17,18):p+=4
  elif t in (5,6):p+=8;i+=1
  elif t==15:p+=3
  else:raise AssertionError(t)
  i+=1
 _,this,superc=struct.unpack_from('>HHH',b,p);p+=6;interfaces=struct.unpack_from('>H',b,p)[0];p+=2+interfaces*2
 for kind in range(2):
  count=struct.unpack_from('>H',b,p)[0];p+=2
  for _ in range(count):
   ac=struct.unpack_from('>H',b,p+6)[0];p+=8
   for a in range(ac):ln=struct.unpack_from('>I',b,p+2)[0];p+=6+ln
 ac=struct.unpack_from('>H',b,p)[0];p+=2;sf=None
 for _ in range(ac):
  key,ln=struct.unpack_from('>HI',b,p);p+=6
  if cp[key]=='SourceFile':sf=cp[struct.unpack_from('>H',b,p)[0]]
  p+=ln
 assert p==len(b);return cp[cp[this]],sf,major
for x in origins:
 b=(B/x['classFile']).read_bytes();assert len(b)==x['bytes'] and hb(b)==x['sha256'] and sha(B/x['source'])==x['sourceSha256'];cn,sf,major=class_origin(b);assert cn==x['className'] and sf==x['sourceFile'] and major==x['major']==55
 assert Path(x['source']).name==sf and cn.rsplit('/',1)[0].replace('/','.') in (B/x['source']).read_text()
 with zipfile.ZipFile(B/x['jar']) as z:assert z.read(x['entry'])==b
for jar in {x['jar'] for x in origins}:
 with zipfile.ZipFile(B/jar) as z:assert set(z.namelist())=={x['entry'] for x in origins if x['jar']==jar}
apks=[]
for kind in ['app','test']:
 p=B/f'artifacts/media3-android02-fix02-{kind}-debug.apk';pkg='com.videokit.d1media3.android02'+('.test' if kind=='test' else '')
 with zipfile.ZipFile(p) as z:
  assert len(z.namelist())==len(set(z.namelist()));tags=axml(z.read('AndroidManifest.xml'));manifest=tags[0]['attributes'];assert manifest['package']==pkg and manifest['versionCode']==1 and manifest['versionName']=='D1-MEDIA3-ANDROID02-FIX02' and 'sharedUserId' not in manifest
  assert not any(t['tag'] in ['uses-permission','uses-permission-sdk-23','activity','activity-alias','service','provider','receiver'] for t in tags);assert not any(n.startswith('lib/') for n in z.namelist())
  app=next(t['attributes'] for t in tags if t['tag']=='application');assert app['allowBackup']==app['usesCleartextTraffic']==0
  cls=[c for n in z.namelist() if n.endswith('.dex') for c in dexclasses(z.read(n))];mm={c:v for n in z.namelist() if n.endswith('.dex') for c,v in methods(z.read(n)).items()}
  assert not any(any(q in c for q in ['Lorg/jcodec/','Lnet/sourceforge/jaad/','Android02NonMediaCheck','ContainerB01Regression','InputSinkCheck','Lcom/videokit/fixturetool/']) for c in cls)
  assert not any(c in cls for c in ['Landroid/net/Uri;','Landroid/system/Os;','Landroid/system/ErrnoException;','Landroid/system/OsConstants;'])
  oldapk=R/'docs/coder/d1media3-android01/artifacts'/f'media3-android01-{kind}-debug.apk'
  with zipfile.ZipFile(oldapk) as oz:oldandroid={c for n in oz.namelist() if n.endswith('.dex') for c in dexclasses(oz.read(n)) if c.startswith('Landroid/')}
  assert {c for c in cls if c.startswith('Landroid/')}==oldandroid
  req=[x for x in origins if ('instrumentation' in x['jar'])==(kind=='test')];assert all('L'+x['className']+';' in cls for x in req)
  implements={}
  checks={'Lcom/videokit/d1media3/android02/test/ExperimentJob;':['run','scopeCases','reserveInput','reserveOutput','receipt','runQualified','resourcesReturned','canFinish'],'Lcom/videokit/d1media3/android02/test/Media3Instrumentation;':['onCreate','onStart','finish','onException'],'Lcom/videokit/d1media3/android02/test/OwnedFiles;':['createNew']} if kind=='test' else {'Lcom/videokit/d1android/QualifiedObservation;':['require','supportedFlags'],'Lcom/videokit/d1input/HostMp4Inspection;':['inspect'],'Landroidx/media3/extractor/mp4/Mp4Extractor;':['read','sniff'],'Landroidx/media3/extractor/mp4/FragmentedMp4Extractor;':['read','sniff'],'Landroidx/media3/muxer/FragmentedMp4Muxer;':['writeSampleData','close']}
  if kind=='test':
   checks['Lcom/videokit/d1media3/android02/test/ExperimentJob;']=['run','scopeCases','receipt','runQualified','resourcesReturned','canFinish','publishCurrent','reserveReceiptEmission']
   del checks['Lcom/videokit/d1media3/android02/test/OwnedFiles;']
   checks['Lcom/videokit/d1media3/android02/test/OwnedFiles$RawWrite;']=['open','write','close','sync']
  else:
   checks.update({'Lcom/videokit/d1android/OriginalOwner;':['allocate','call','closeOnce','returned'],'Lcom/videokit/d1android/ScopeMeter;':['input','nativeAttempt','outputAttempt','snapshot'],'Lcom/videokit/d1android/ScopeJournal;':['current','completed','snapshot','reserveEmission'],'Lcom/videokit/d1android/CompletionPoint;':['finishAfterSignal','timely'],'Lcom/videokit/d1input/MatureMuxerBinding;':['allocate','cleanupCloseOnce','returned']})
  for c,names in checks.items():
   implements[c]=[x for x in mm[c] if x['name'] in names]
   for n in names:assert any(x['name']==n and x['codeOffset']>0 and x['instructionUnits']>0 for x in implements[c]),(c,n)
  assets=[];instruments=[t['attributes'] for t in tags if t['tag']=='instrumentation']
  if kind=='test':
   assert len(instruments)==1 and instruments[0]['name']==pkg+'.Media3Instrumentation' and instruments[0]['targetPackage']=='com.videokit.d1media3.android02' and instruments[0]['targetProcesses']=='com.videokit.d1media3.android02:media3';assert not any(c.startswith('Landroidx/media3/') for c in cls)
   for name in ['qualified-six-avc.mp4','qualified-fixture.json','sample.mp4','SOURCE_AND_LICENSE.txt','SYNTHETIC_SOURCE.txt']:
    b=z.read('assets/'+name);assert b==(B/'instrumentation-assets'/name).read_bytes();assets.append({'asset':name,'bytes':len(b),'sha256':hb(b)})
  else:assert not instruments and app['process']==':media3' and 'assets/qualified-six-avc.mp4' not in z.namelist()
  apks.append({'kind':kind,'bytes':p.stat().st_size,'sha256':sha(p),'manifest':tags,'dexClassCount':len(cls),'sourceClassesPresent':len(req),'actualImplementedDexMethods':implements,'assets':assets,'nativeLibraries':0,'permissions':[],'actualAndroidExecution':'NOT_RUN'})
save('independent-artifact-source-dex.json',{'classOrigins':origins,'apks':apks,'sourceLinkMeaning':'Exact frozen javac class SourceFile+source pins+JAR identical entries+DEX class and method presence; not byte-for-byte JVM-to-DEX equivalence nor Android method execution'})
save('independent-audit-summary.json',{'status':'PASS_FROZEN_ARTIFACT_SOURCE_BUILD_CONSUMPTION_IDENTITIES_ONLY','files':874,'uniqueZipMembers':874,'archiveSha256':sha(zpath),'sourceChanges':14,'versionConfigChangeOnly':True,'javacClasses':105,'productionClasses':94,'instrumentationClasses':11,'apks':[{k:x[k] for k in ['kind','bytes','sha256','dexClassCount']} for x in apks],'actualConsumption':300,'buildOriginalReturns':2,'AndroidRuntime':'NOT_RUN','newGradleDeviceMediaOperations':0,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat()});print('PASS independent 874/ZIP874; fourteen sources/config; one build strict300; class105/JAR/DEX/APK')
