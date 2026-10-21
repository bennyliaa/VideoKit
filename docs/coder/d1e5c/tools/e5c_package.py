"""Small E5C overlay plus exact required frozen E5B build sources; never operates a device."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,re,subprocess,zipfile
B=Path(__file__).resolve().parents[1];R=B.parents[2];OLD=R/'docs/coder/d1e5b';ID='D1-20261017-E5C'
DOCS=[R/('docs/coder/D1_E5C_'+s+'_V1.0.md') for s in ['DELIVERY','ARCHITECTURE_AND_THREAT_BOUNDARY','REMAINING_GATE_REVIEW','DEVICE_EXECUTION_APPENDIX']]
CONFIG=['build.gradle.kts','settings.gradle.kts','gradle.properties','settings-gradle.lockfile','gradlew','gradlew.bat','app/build.gradle.kts','app/gradle.lockfile']
def sha(b):return hashlib.sha256(b).hexdigest()
def rel(p):return p.relative_to(R).as_posix()
def data(p):
 p=p.absolute();p.relative_to(R)
 for q in [p,*p.parents]:
  if q==R:break
  if q.is_symlink():raise ValueError('LINK:'+str(q))
 if not p.is_file() or p.stat().st_size>96*1024*1024:raise ValueError('ROLE_BOUND:'+str(p))
 return p.read_bytes()
def row(p):
 b=data(p);return dict(path=rel(p),bytes=len(b),sha256=sha(b))
def write(p,v):
 p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x',encoding='utf-8',newline='\n') as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')
def check(r):
 if row(R/r['path'])!=r:raise ValueError('HASH_CHANGED:'+r['path'])
def tree(p):return [q for q in p.rglob('*') if q.is_file() and '__pycache__' not in q.parts]
def inherited():return sorted(set(p for d in ['src','android','upstream-c14','app/src/androidTest'] for p in tree(OLD/d)))
def inputs():return [row(p) for p in sorted(set(inherited()+tree(B/'app/src')+tree(B/'gradle')+[B/p for p in CONFIG]))]
def snapshot():
 if (B/'evidence/e5c-freeze.json').exists():raise ValueError('FROZEN')
 write(B/'evidence/final-build-inputs.json',dict(schema=1,candidateId=ID,files=inputs(),localPropertiesExcluded=True,deviceCalls=0))
def verify_inputs():
 d=json.loads(data(B/'evidence/final-build-inputs.json'))
 if d['files']!=inputs():raise ValueError('BUILD_INPUT_CHANGED')
 return d
def provenance():
 baseline=json.loads(data(OLD/'evidence/e5b-freeze.json'));assert sha(data(OLD/'evidence/e5b-freeze.json'))=='3c55e0c83517e8937799b72d327dcab98b9d23965dc41813a5d18756640aceee'
 by={x['path']:x for x in baseline['immutableFiles']};rows=[row(p) for p in inherited()]
 mapping=OLD/'evidence/upstream-copy-map.json';check(by[rel(mapping)]);mapped={x['destination']:{'path':x['destination'],'bytes':x['bytes'],'sha256':x['sha256']} for x in json.loads(data(mapping))['files']}
 for key,value in mapped.items():
  if key not in by:by[key]=value
 for r in rows:
  if r!=by[r['path']]:raise ValueError('OLD_PRODUCTION_CHANGED')
 copies=[]
 for p in tree(B/'app/src/main')+tree(B/'app/src/debug'):
  original=OLD/p.relative_to(B);assert data(original)==data(p);check(by[rel(original)]);copies.append(dict(current=row(p),baseline=row(original),relationship='BYTE_IDENTICAL'))
 write(B/'evidence/source-provenance.json',dict(schema=1,status='PASS',baselineFreeze=row(OLD/'evidence/e5b-freeze.json'),inheritedMapping=row(mapping),relationship='BYTE_IDENTICAL_DIRECT_SOURCE_REFERENCE',files=rows,copiedOriginalAppSources=copies,coreMutation=False,oldSelfChecksCopied=False,observationBoundary=row(OLD/'src/com/videokit/spike/e4/E5AFinalObservation.java'),fullCorrespondingNativeSource='docs/coder/d1e5b/upstream-c14/D1-20261016-C14-source.zip'))
def sbom():
 lock=data(B/'app/gradle.lockfile');old=data(OLD/'app/gradle.lockfile');assert lock==old
 bom=json.loads(data(OLD/'evidence/sbom.json'));bom['metadata']['component']['name']='VideoKit E5C Debug isolated guard fixture';bom['metadata']['component']['version']=ID
 coords=[x for x in lock.decode().splitlines() if re.match(r'[^#=]+:[^:]+:[^=]+=',x)];assert len(coords)==35
 write(B/'evidence/sbom.json',bom)
 write(B/'evidence/sbom-difference.json',dict(schema=1,baseline='D1-20261017-E5B',baselineLockSha256=sha(old),currentLockSha256=sha(lock),coordinates=35,coordinateDelta=[],nativeDelta=[],nativeLibraries=7,media3='1.9.3',ffmpeg='8.0.3',newDependencies=False,downloads=0,scope='Identity inheritance only; not vulnerability or license clearance'))
def external():
 p=OLD/'evidence/e5b-freeze.json';assert sha(data(p))=='3c55e0c83517e8937799b72d327dcab98b9d23965dc41813a5d18756640aceee';f=json.loads(data(p))
 for r in f['immutableFiles']:check(r)
 write(B/'evidence/external-readonly-verification.json',dict(schema=1,status='PASS',freeze=row(p),immutableFilesVerified=len(f['immutableFiles']),mutation=False,historicalTestExecution=False,deviceCalls=0,realMediaReads=0))
def local():
 java=Path('D:/Android/Android Studio/jbr/bin');dest=B/'.selfcheck';dest.mkdir(exist_ok=False)
 policy=B/'app/src/androidTest/java/com/videokit/spike/e4/E5CFixtureBounds.java';test=B/'tools/FixtureBoundsSelfCheck.java';entry=B/'app/src/androidTest/java/com/videokit/spike/e4/E5CGuardFixtureTests.java';s=data(entry).decode();cases=[]
 def ok(label,b):
  if not b:raise ValueError(label)
  cases.append(dict(name=label,status='PASS',kind='STATIC_SOURCE_CONSTRAINT'))
 ok('no full observation/recovery execution','.observe(' not in s and '.execute(' not in s and 'E5C_DEATH_DISABLED' in s)
 ok('exclusive fixed root no cleanup','Files.createDirectory(root)' in s and 'Files.delete' not in s and 'Files.exists(root)' not in s)
 ok('true link original inode','Files.move(source,target)' in s and 'Os.symlink(' in s and 'Os.lstat(' in s and 'Os.readlink(' in s and 'expected.inode==t.st_ino' in s)
 ok('exact production observation boundary','getDeclaredMethod("lock",Path.class,E5BGuard.Role.class,String.class,E5BFileId.class)' in s and 'adapter.existingGuard(' in s)
 ok('original worker retained no cancellation','RETAINED.add(run)' in s and 'future.cancel(' not in s and 'shutdownNow(' not in s and 'hostTimedOut' in s)
 ok('bounded nofollow inventory','EnumSet.noneOf(FileVisitOption.class)' in s and 'bound.add(' in s and 'LinkOption.NOFOLLOW_LINKS' in s)
 ok('real ELOOP and actual close','e.errno==OsConstants.ELOOP' in s and 'rawCloseAttempted' in s and '!duplicateFd.valid()' in s)
 ok('precise one-shot case argument','e5cCase' in s and 'consume();' in s and 'E5C_PROCESS_ONCE' in s)
 ok('independent ledger and grant proof','R_count=0 S_count=0' in s and 'grant.get(null)==beforeGrant' in s and 'before.equals(snapshot(dir))' in s)
 commands=[[str(java/'javac.exe'),'-encoding','UTF-8','-d',str(dest),str(policy),str(test)],[str(java/'java.exe'),'-cp',str(dest),'com.videokit.spike.e4.FixtureBoundsSelfCheck']]
 for n,cmd in enumerate(commands):
  result=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=30,check=False);log=B/f'evidence/local-{n}.log';log.write_bytes(result.stdout)
  if result.returncode:raise ValueError('LOCAL_LOGIC_FAILED:'+str(log))
 write(B/'evidence/local-check-results.json',dict(schema=1,status='PASS',scope='10 finite pure-JVM bounds/deadline cases plus 9 source constraints only',jvmCases=10,staticCases=cases,commands=commands,inputs=[row(p) for p in [policy,test,entry]],androidExecution='NOT_RUN',trueSymlink='NOT_RUN',flock='NOT_RUN',actualAndroidFd='NOT_RUN',deviceCalls=0,realMediaReads=0))
 print('PASS JVM bounds/deadline=10 static constraints=9; actual Android NOT_RUN')
def freeze():
 verify_inputs()
 for name in ['local-check-results.json','build-results.json','apk-audit.json','external-readonly-verification.json','source-provenance.json']:
  if json.loads(data(B/'evidence'/name))['status']!='PASS':raise ValueError('UNPASSED:'+name)
 for r in json.loads(data(B/'evidence/local-check-results.json'))['inputs']:check(r)
 build=json.loads(data(B/'evidence/build-results.json'));passing=[a for a in build['attempts'] if a['exitCode']==0];assert passing[-1]['inputSnapshotSha256']==sha(data(B/'evidence/final-build-inputs.json'))
 paths=inherited()+tree(B/'app/src')+tree(B/'gradle')+tree(B/'tools')+tree(B/'reference')+tree(B/'evidence')+[B/p for p in CONFIG]+DOCS
 paths=sorted(set(p for p in paths if p not in [B/'evidence/e5c-freeze.json',B/'evidence/source-manifest.json']));files=[row(p) for p in paths]
 assert len(files)<1024 and sum(r['bytes'] for r in files)<128*1024*1024
 manifest=B/'evidence/source-manifest.json';write(manifest,dict(schema=1,candidateId=ID,files=files,scope='Complete small overlay and exact necessary E5B production/Android sources/native/license container at original relative paths; no old self-check trees, cache, signing key, local.properties, media'))
 z=B/f'artifacts/{ID}/{ID}-source.zip';z.parent.mkdir(parents=True,exist_ok=True)
 with zipfile.ZipFile(z,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as out:
  for p in paths:out.writestr(rel(p),data(p))
 apks=json.loads(data(B/'evidence/apk-audit.json'))['apks'];failedApks=[row(p) for p in sorted((B/f'artifacts/{ID}/pre-debug-manifest-repair').glob('*.apk'))];immutable=files+[row(manifest),row(z)]+[{k:a[k] for k in ['path','bytes','sha256']} for a in apks]+failedApks
 seal=dict(schema=1,candidateId=ID,state='FROZEN_OFFLINE_BUILD_ANDROID_FIXTURE_NOT_RUN',frozenAtUtc=datetime.now(timezone.utc).isoformat(),sourceManifest=row(manifest),sourceZip=row(z),apks=apks,preservedFailedAuditApks=failedApks,documents=[rel(p) for p in DOCS],immutableFiles=immutable,core='E5B_BYTE_IDENTICAL',androidExecution='NOT_RUN',G01='AWAITING_ANDROID_TRUE_FILE_SYMLINK_EVIDENCE_AND_REVIEW',fullObservation='NOT_RUN',N2Recovery='NOT_RUN',D1='NOT_PASSED',M0='NOT_STARTED',allP0='REMAIN_OPEN',historicalSignalGate='FAIL_UNCHANGED',deviceCalls=0,realMediaReads=0)
 write(B/'evidence/e5c-freeze.json',seal);print(json.dumps(dict(freeze=row(B/'evidence/e5c-freeze.json'),sourceZip=seal['sourceZip'],sourceFiles=len(files),immutableFiles=len(immutable))))
def verify():
 p=B/'evidence/e5c-freeze.json';f=json.loads(data(p));assert len(f['immutableFiles'])<1028
 for r in f['immutableFiles']:check(r)
 m=json.loads(data(R/f['sourceManifest']['path']));names=[r['path'] for r in m['files']]
 with zipfile.ZipFile(R/f['sourceZip']['path']) as z:
  assert z.namelist()==names and len(set(names))==len(names) and sum(x.file_size for x in z.infolist())<128*1024*1024
  for r in m['files']:
   raw=z.read(r['path']);assert len(raw)==r['bytes'] and sha(raw)==r['sha256']
 verify_inputs();print(json.dumps(dict(status='PASS',mode='READ_ONLY',freeze=row(p),sourceFiles=len(names),immutableFiles=len(f['immutableFiles']),deviceCalls=0,realMediaReads=0)))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('mode',choices=['snapshot','inputs','provenance','sbom','external','local','freeze','verify']);a=p.parse_args();{'snapshot':snapshot,'inputs':verify_inputs,'provenance':provenance,'sbom':sbom,'external':external,'local':local,'freeze':freeze,'verify':verify}[a.mode]()
