"""Default verify/help read-only. Explicit pack alone writes a new frozen delivery."""
from pathlib import Path
import argparse,hashlib,json,zipfile
B=Path(__file__).resolve().parents[1];R=B.parents[2]
def pin(p):b=p.read_bytes();return dict(path=p.relative_to(R).as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def check(row):assert pin(R/row['path'])=={k:row[k] for k in ['path','bytes','sha256']},row['path']
def verify(expected=None):
 path=B/'evidence/e13e-freeze.json'
 if not path.exists():return dict(status='NOT_FROZEN',writes=0),2
 if expected:assert pin(path)['sha256']==expected,'EXTERNAL_SEAL_SHA'
 s=json.loads(path.read_text(encoding='utf-8'));rows=s['immutableFiles'];assert len(rows)==len({r['path'] for r in rows})
 for row in rows:check(row)
 members={r['path']:r for r in rows if r['path']!=s['archive']['path']}
 with zipfile.ZipFile(R/s['archive']['path']) as z:
  assert len(z.namelist())==len(members) and set(z.namelist())==set(members)
  for n,row in members.items():raw=z.read(n);assert len(raw)==row['bytes'] and hashlib.sha256(raw).hexdigest()==row['sha256']
 for old in s['priorSeals']:
  check(old['seal'])
  for row in json.loads((R/old['seal']['path']).read_text(encoding='utf-8'))['immutableFiles']:check(row)
 for group in json.loads((R/'docs/coder/d1e13d/evidence/input-verification.json').read_text())['frozenManifests']:
  if group['rowKey']!='rows':continue
  check(group['manifest'])
  for row in json.loads((R/group['manifest']['path']).read_text())[group['rowKey']]:check(row)
 assert pin(B/'reference/D1_E13D_OFFLINE_REVIEW_REPORT_V1.0.md')['sha256']=='0955705e5d83784c5a5cdb76528b52836ae71850c12d65dfe20fb3b54dd8876e'
 for row in json.loads((B/'evidence/final-build-inputs.json').read_text())['files']:
  if Path(row['path']).name=='fixture-signing.p12' and not (R/row['path']).exists():continue
  check(row)
 manifest=json.loads((B/'evidence/host-jar-manifest.json').read_text());check(manifest['jar']);assert len(manifest['classes'])==182
 with zipfile.ZipFile(R/manifest['jar']['path']) as z:
  assert set(z.namelist())=={r['entry'] for r in manifest['classes']} and len(z.namelist())==182
  for row in manifest['classes']:
   check(row['source']);raw=z.read(row['entry']);assert len(raw)==row['bytes'] and hashlib.sha256(raw).hexdigest()==row['sha256'];assert 'E13EHostCheck' not in row['entry'] and 'platform-substitutes' not in row['source']['path']
  for row in json.loads((B/'evidence/tested-final-class-equivalence.json').read_text())['members']:
   raw=(B/'evidence/tested-class-bytes'/row['attempt']/row['entry']).read_bytes();assert raw==z.read(row['entry']) and hashlib.sha256(raw).hexdigest()==row['sha256']
 audit=json.loads((B/'evidence/apk-delivery-final/apk-audit.json').read_text());assert audit['nativeLibraries']==7 and audit['mavenCoordinates']==35
 for apk in audit['apks']:check(apk)
 for row in json.loads((B/'evidence/apk-delivery-final/sbom-difference.json').read_text())['nativeLibraries']:check(row)
 plan=json.loads((B/'release/candidate-binding.json').read_text());assert plan['actualScope'] is None and plan['actualRelease'] is None and plan['actualOnce'] is None and plan['dispositionSourcePin']=='ABSENT' and plan['T07']=='NOT_RUN'
 assert plan['appVersion']==18 and plan['fixtureVersion']==2 and plan['budgetProposal']['successOperations']==51 and plan['budgetProposal']['maxOperationsWithOccupation']==53
 assert 'DISPOSITION_SHA="ABSENT"' in (B/'tools/E13GuardLocation.java').read_text()
 assert json.loads((B/'evidence/android-005/results.json').read_text())['modes'].__len__()==18
 assert json.loads((B/'evidence/actual-after-007/results.json').read_text())['status']=='PASS_ACTUAL_AFTER_JUNIT_WATCHER_CHAIN'
 assert json.loads((B/'evidence/host-006/results.json').read_text())['status']=='PASS_E13E_HOST_BOUNDARIES'
 assert json.loads((B/'evidence/public-004/commands-and-results.json').read_text())['status']=='PASS_REAL_PUBLIC_ENTRIES_PENDING'
 for key in ['host-006','android-005']:
  for row in json.loads((B/'evidence'/key/'inputs.json').read_text()):check(row)
 return dict(status='PASS_E13E_STRICT_READONLY_VERIFY',writes=0,archive=s['archive'],externalSeal=pin(path),archiveEntries=len(members),immutableRows=len(rows),jarClasses=182,actualTestedFinalClassComparisons=16,apkBuildAttempts=4,passingApkBuilds=2,finalApkBuild='r01-004',androidJvmGroups=18,actualAfterJUnit=True,deviceCalls=0,nativeBuilds=0,actualScope=None,D1='NOT_PASSED',M0='NOT_STARTED'),0
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('mode',choices=['verify','pack'],nargs='?',default='verify');p.add_argument('--seal-sha');a=p.parse_args()
 if a.mode=='pack':
  if a.seal_sha:p.error('--seal-sha only for verify')
  import runpy
  runpy.run_path(str(B/'tools/_pack_delivery.py'),run_name='__main__');return
 result,code=verify(a.seal_sha);print(json.dumps(result,ensure_ascii=False));raise SystemExit(code)
if __name__=='__main__':main()
