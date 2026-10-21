"""Pure Python frozen-material audit. No processes, build, media parsing, SDK or device calls."""
from pathlib import Path
import argparse,ast,datetime,hashlib,json,struct,zipfile
B=Path(__file__).resolve().parents[1];R=B.parents[2];E=B/'evidence';S=E/'media3-android02-freeze.json';MAIN=R/'docs/coder/D1_MEDIA3_ANDROID02_CONTAINER_DELIVERY_V1.0.md';ZIP=R/'docs/coder/D1-20261021-MEDIA3-ANDROID02-CONTAINER-source.zip'
FOLDERS=['src','android','upstream','checks','platform-fixtures','instrumentation','instrumentation-assets','notice-assets','deps','licenses','reference','patches','tools','evidence','gradle','app/src','artifacts']
ROOT_FILES=['settings.gradle.kts','settings-gradle.lockfile','build.gradle.kts','gradle.properties','local.properties','app/build.gradle.kts','app/gradle.lockfile']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def selected():return sorted({p for n in FOLDERS for p in (B/n).rglob('*') if p.is_file() and p!=S}|{B/n for n in ROOT_FILES}|{MAIN})
def rows_check(rows):
 for x in rows:
  p=(R/x['path']).resolve();assert p.is_relative_to(R) and p.stat().st_size==x['bytes'] and sha(p)==x['sha256'],str(p)
def inputs():
 assert read(E/'artifact-status.json')['status']=='UNBUILT_GRADLE_DAEMON_CONNECT_FAILED_BEFORE_COMPILE'
 assert not list((B/'app').rglob('*.apk')) and not list((B/'artifacts').glob('*'))
 assert read(E/'build-main-001/receipt.json')['exitCode']==1
 assert 'Could not connect to the Gradle daemon.' in (E/'build-main-001/gradle.log').read_text()
 assert not (E/'build-main-001/consumption.jsonl').exists()
 for x in read(E/'build-input-pins.json'):assert sha(B/x['path'])==x['sha256']
 for x in read(E/'nonmedia-001/source-pins.json'):assert sha(B/x['path'])==x['sha256']
 for n in ['javac','metadata']:
  x=read(E/f'nonmedia-001/{n}-owner.json');assert x['exitCode']==0 and x['originalProcessReturned'] and x['captureHandlesClosed'] and x['killInterruptRetry']==0
 log=(E/'nonmedia-001/metadata.stdout').read_text();assert 'DONE nonMediaChecks=20 originalsReturned=true' in log and 'DONE independentBoundaryPasses=8' in log
 for x in read(E/'baseline-preservation.json'):
  p=R/x['seal'];assert sha(p)==x['sha256'];m=read(p);assert len(m['files'])==x['verifiedRows'];rows_check(m['files'])
 q=read(E/'qualification-preservation.json');rows_check([q['manifest'],q['report']]);rows_check(read(R/q['manifest']['path'])['evidenceFiles'])
 asset=B/'instrumentation-assets/qualified-six-avc.mp4';assert asset.stat().st_size==8849 and sha(asset)=='19e815a413ae8275fe61e917ff9ac3c67d74a4f845df548a6ce2c382c0778a9c'
 rows_check([read(E/'delivery-report-identity.json')])
 for p in (B/'deps').glob('*.jar'):
  assert sha(p)==sha(R/'docs/coder/d1media3-android01/deps'/p.name)
  with zipfile.ZipFile(p) as z:assert not any(n.startswith('org/jcodec/') for n in z.namelist())
 for n in ['gradle/verification-metadata.xml','app/gradle.lockfile','settings-gradle.lockfile']:assert (B/n).read_bytes()==(R/'docs/coder/d1media3-android01'/n).read_bytes()
 origin=read(E/'nonmedia-class-origins.json')
 for x in origin:assert sha(B/x['class'])==x['sha256'] and sha(B/x['source'])==x['sourceSha256'] and x['major']==55
 return {'status':'MATERIALS_MATCH_BUILD_BLOCKED_NOT_ANDROID_PASS','gradleCalls':1,'gradleClientExitCode':1,'newDaemonReturn':'UNKNOWN_UNQUERIED','appOrTestApks':0,'nonmediaParentGroups':20,'inheritedSubcases':8,'nonmediaCompiledClassFiles':len(origin),'AndroidCasesRun':0,'deviceOperations':0,'newProcessesLaunchedByThisReviewer':0,'oldUnknownActions':0}
def verify():
 seal=read(S);rows_check(seal['files']);assert {x['path'] for x in seal['files']}=={p.relative_to(R).as_posix() for p in selected()}
 assert sha(ZIP)==seal['archive']['sha256'] and ZIP.stat().st_size==seal['archive']['bytes']
 with zipfile.ZipFile(ZIP) as z:
  assert z.testzip() is None and set(z.namelist())=={x['path'] for x in seal['files']}
  for x in seal['files']:assert hashlib.sha256(z.read(x['path'])).hexdigest()==x['sha256']
 result=inputs();result.update(sealSha256=sha(S),sealedFiles=len(seal['files']),archiveSha256=sha(ZIP));return result
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--output',required=True);args=parser.parse_args();out=Path(args.output);root=R/'docs/tester/D1_MEDIA3_ANDROID02_REVIEW_EVIDENCE'
 assert out.is_absolute() and out.resolve().parent==root.resolve() and not out.exists()
 result=verify();root.mkdir(exist_ok=True);out.mkdir();result['verifiedUtc']=datetime.datetime.now(datetime.timezone.utc).isoformat();p=out/'material-verification.json';p.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({'receipt':str(p),'sha256':sha(p),'result':result},ensure_ascii=False))
