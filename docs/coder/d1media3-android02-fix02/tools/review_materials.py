"""Pure Python file/class/JAR/ZIP material audit; no subprocess, SDK, JVM or media parser."""
from pathlib import Path
import argparse,datetime,hashlib,json,zipfile
B=Path(__file__).resolve().parents[1];R=B.parents[2];E=B/'evidence';SEAL=E/'fix02-freeze.json';MAIN=R/'docs/coder/D1_MEDIA3_ANDROID02_FIX02_DELIVERY_V1.0.md';ZIP=R/'docs/coder/D1-20261021-MEDIA3-ANDROID02-FIX02-source.zip'
FOLDERS=['src','android','upstream','checks','platform-fixtures','instrumentation','instrumentation-assets','notice-assets','deps','licenses','reference','gradle','app/src','tools','evidence','artifacts','patches']
ROOT=['settings.gradle.kts','settings-gradle.lockfile','build.gradle.kts','gradle.properties','local.properties','app/build.gradle.kts','app/gradle.lockfile','media3-android02-fix02-sbom.cdx.json']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def check_rows(rows):
 for x in rows:
  p=(R/x['path']).resolve();assert p.is_relative_to(R) and p.stat().st_size==x['bytes'] and sha(p)==x['sha256'],str(p)
def selected():
 paths={p for f in FOLDERS for p in (B/f).rglob('*') if p.is_file() and p!=SEAL}|{B/n for n in ROOT}|{MAIN};paths.update(B/x['classFile'] for x in read(E/'class-origins.json'));return sorted(paths)
def inputs():
 x=read(E/'build-001/owner.json');assert x['exitCode']==0 and x['originalClientReturned'] and x['captureHandlesClosed'] and x['daemonOriginalReturned'] and x['daemon']['sameHandleSignalled'] and x['daemon']['exitCode']==0 and not x['transportFailure'] and not x['sourceCompileFailure'] and x['stdoutBytes']<=16777216 and x['stderrBytes']<=16777216
 assert (E/'build-001/stdout.raw').stat().st_size==x['stdoutBytes'] and (E/'build-001/stderr.raw').stat().st_size==x['stderrBytes'] and sha(E/'build-001/single-use-daemon.raw.log')==x['daemonLogSha256'];assert not (E/'build-002').exists()
 for x in read(E/'final-build-input-pins.json'):assert sha(B/x['path'])==x['sha256']
 reconstructed={x['path'].split('reconstructed-typed-sources/',1)[1]:x for x in read(E/'reconstructed-typed-sources.json')}
 for x in read(E/'typed-001/source-pins.json'):
  if sha(B/x['path'])!=x['sha256']:assert x['path'] in reconstructed and sha(B/reconstructed[x['path']]['path'])==x['sha256']
 for n in ['compile','typed']:
  x=read(E/f'typed-001/{n}-owner.json');assert x['exitCode']==0 and x['originalProcessReturned'] and x['captureHandlesClosed'] and x['killInterruptRetry']==0
 t=read(E/'typed-001/result.json');assert t['typedCases']==36 and t['wholeWindowReturnedWithin30s'] and t['sameOriginalThreadsJoined']
 sig=read(E/'signatures-001/owner.json');assert sig['exitCode']==0 and sig['originalProcessReturned'] and sig['captureHandlesClosed'];assert read(E/'signatures-001/result.json')['allInputsUnchanged']
 for x in read(E/'signatures-001/inputs.json'):assert sha(Path(x['path']))==x['sha256']
 origins=read(E/'class-origins.json');assert len(origins)==105
 for x in origins:
  assert sha(B/x['source'])==x['sourceSha256'] and sha(B/x['classFile'])==x['sha256'] and (B/x['classFile']).stat().st_size==x['bytes']
  with zipfile.ZipFile(B/x['jar']) as z:assert hashlib.sha256(z.read(x['entry'])).hexdigest()==x['sha256']
 audit=read(E/'artifact-audit.json')
 for x in audit['apks']+audit['jars']:assert (B/x['path']).stat().st_size==x['bytes'] and sha(B/x['path'])==x['sha256']
 for x in audit['apks']:
  with zipfile.ZipFile(B/x['path']) as z:
   assert z.testzip() is None and not any(n.startswith('lib/') for n in z.namelist())
   if x['package'].endswith('.test'):assert hashlib.sha256(z.read('assets/qualified-six-avc.mp4')).hexdigest()=='19e815a413ae8275fe61e917ff9ac3c67d74a4f845df548a6ce2c382c0778a9c'
 for x in read(E/'actual-consumption/artifacts.json'):
  assert sha(B/x['path'])==x['sha256']
  if 'reviewCopy' in x:assert sha(B/x['reviewCopy'])==x['sha256']
 assert read(E/'actual-consumption/summary.json')['actualSeparateClosureCounts']==[12,17,12,0]
 for n in ['gradle/verification-metadata.xml','app/gradle.lockfile','settings-gradle.lockfile']:assert (B/n).read_bytes()==(R/'docs/coder/d1media3-android02-recovery01'/n).read_bytes()
 for x in read(E/'all-baseline-preservation.json'):
  if 'seal' in x:check_rows([x['seal']]);check_rows(read(R/x['seal']['path'])['files'])
  else:check_rows([x['manifest'],x['report']]);check_rows(read(R/x['manifest']['path'])['evidenceFiles'])
 check_rows([read(E/'main-report-identity.json')]);assert {x['id'] for x in read(E/'five-fix-completion-matrix.json')['fixes']}=={'R01-B01','R01-B02','R01-B03','R01-B04','R01-B05'}
 return {'status':'FIX02_OFFLINE_MATERIALS_MATCH_TYPED36_PENDING_INDEPENDENT_B','gradleBuildCalls':1,'originalClientAndNewDaemonReturned':True,'actualFinalApks':2,'realSignaturesVerified':2,'productionClasses':94,'instrumentationClasses':11,'actualStrictArtifacts':300,'actualClosures':[12,17,12,0],'typedStateCases':36,'typedJvms':1,'postBuildSignatureOnlyJvms':1,'independentFiveFindingClosure':'PENDING','AndroidNativeOrMediaRuntimeCases':0,'deviceOperations':0,'oldUnknownActions':0,'processesLaunchedByThisVerifier':0}
def verify():
 seal=read(SEAL);check_rows(seal['files']);assert {x['path'] for x in seal['files']}=={p.relative_to(R).as_posix() for p in selected()};assert sha(ZIP)==seal['archive']['sha256'] and ZIP.stat().st_size==seal['archive']['bytes']
 with zipfile.ZipFile(ZIP) as z:
  assert z.testzip() is None and set(z.namelist())=={x['path'] for x in seal['files']}
  for x in seal['files']:assert hashlib.sha256(z.read(x['path'])).hexdigest()==x['sha256']
 result=inputs();result.update(sealSha256=sha(SEAL),sealedFiles=len(seal['files']),archiveSha256=sha(ZIP));return result
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--output',required=True);args=p.parse_args();out=Path(args.output);root=R/'docs/tester/D1_MEDIA3_ANDROID02_FIX02_REVIEW_EVIDENCE';assert out.is_absolute() and out.resolve().parent==root.resolve() and not out.exists()
 result=verify();root.mkdir(exist_ok=True);out.mkdir();result['verifiedUtc']=datetime.datetime.now(datetime.timezone.utc).isoformat();receipt=out/'material-verification.json';receipt.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({'receipt':str(receipt),'sha256':sha(receipt),'result':result},ensure_ascii=False))
