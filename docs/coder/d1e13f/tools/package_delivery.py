"""Default verify/help are strictly read-only. Only explicit pack creates a new delivery."""
from pathlib import Path
import argparse,hashlib,json,zipfile
B=Path(__file__).resolve().parents[1];R=B.parents[2]
def pin(p):b=p.read_bytes();return dict(path=p.relative_to(R).as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def check(row):assert pin(R/row['path'])=={k:row[k] for k in ['path','bytes','sha256']},row['path']
def verify(expected=None):
 p=B/'evidence/e13f-freeze.json'
 if not p.exists():return dict(status='NOT_FROZEN',writes=0),2
 if expected:assert pin(p)['sha256']==expected,'EXTERNAL_SEAL_SHA'
 s=json.loads(p.read_text(encoding='utf-8'));rows=s['immutableFiles'];assert len(rows)==len({r['path'] for r in rows})
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
 assert pin(B/'reference/D1_E13E_LIFECYCLE_REVIEW_REPORT_V1.0.md')['sha256']=='3193a7728e84d860d03b14447214901f0641ccf135ffd655cfc69fc0938f9d6d'
 inputs=json.loads((B/'evidence/final-build-inputs.json').read_text())['files'];assert len(inputs)==142
 for row in inputs:
  if Path(row['path']).name=='fixture-signing.p12' and not (R/row['path']).exists():continue
  check(row)
 manifest=json.loads((B/'evidence/host-jar-manifest.json').read_text());check(manifest['jar']);assert len(manifest['classes'])==183
 eq=json.loads((B/'evidence/tested-final-class-equivalence.json').read_text());assert len(eq['members'])==183
 with zipfile.ZipFile(R/manifest['jar']['path']) as z:
  assert len(z.namelist())==183 and set(z.namelist())=={r['entry'] for r in manifest['classes']}
  for row in manifest['classes']:
   check(row['source']);raw=z.read(row['entry']);assert len(raw)==row['bytes'] and hashlib.sha256(raw).hexdigest()==row['sha256'];assert not any(x in row['entry'] for x in ['FCompletionCheck','FPublicChainCheck','FJoinOrderCheck'])
  for row in eq['members']:assert (B/'evidence/tested-class-bytes'/row['attempt']/row['entry']).read_bytes()==z.read(row['entry'])
 audit=json.loads((B/'evidence/apk-delivery-final/apk-audit.json').read_text());assert audit['nativeLibraries']==7 and audit['mavenCoordinates']==35
 for apk in audit['apks']:check(apk)
 for row in json.loads((B/'evidence/apk-delivery-final/sbom-difference.json').read_text())['nativeLibraries']:check(row)
 plan=json.loads((B/'release/candidate-binding.json').read_text());assert all(plan[k] is None for k in ['actualScope','actualRelease','actualOnce','sourceReview']);assert plan['dispositionSourcePin']=='ABSENT' and plan['T07']=='NOT_RUN' and plan['appVersion']==19 and plan['fixtureVersion']==3
 assert plan['budgetProposal']['successOperations']==51 and plan['budgetProposal']['maxOperationsWithOccupation']==53
 assert 'DISPOSITION_SHA="ABSENT"' in (B/'tools/E13GuardLocation.java').read_text()
 assert 'setDaemon(false)' in (B/'tools/E13GuardLocation.java').read_text()
 assert json.loads((B/'evidence/host-007/results.json').read_text())['status']=='PASS_F02_ACTUAL_REQUEST_FAIL'
 for row in json.loads((B/'evidence/host-007/inputs.json').read_text()):check(row)
 public=json.loads((B/'evidence/public-008/results.json').read_text());assert public['roles']==['CASE','DEPLOY','LEGACY'] and public['normalChains']==3 and public['failedMarkerChains']==3
 for role in public['roles']:
  for mode in ['NORMAL','FAIL_MARKER']:assert json.loads((B/'evidence/public-008'/(role+'-'+mode)/'exit.json').read_text())['exitCode']==0
 assert len(json.loads((B/'evidence/join-orders-009/results.json').read_text())['orders'])==3
 build=json.loads((B/'evidence/build-results.json').read_text());assert build['status']=='PASS' and len(build['attempts'])==1 and build['attempts'][0]['exitCode']==0
 return dict(status='PASS_E13F_STRICT_READONLY_VERIFY',writes=0,archive=s['archive'],externalSeal=pin(p),archiveEntries=len(members),immutableRows=len(rows),jarClasses=183,actualTestedFinalClassComparisons=183,apkBuildAttempts=1,passingApkBuilds=1,finishGroups=2,publicCombinedGroups=6,joinOrders=3,deviceCalls=0,nativeBuilds=0,actualScope=None,D1='NOT_PASSED',M0='NOT_STARTED'),0
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('mode',choices=['verify','pack'],nargs='?',default='verify');p.add_argument('--seal-sha');a=p.parse_args()
 if a.mode=='pack':
  if a.seal_sha:p.error('--seal-sha only for verify')
  import runpy
  runpy.run_path(str(B/'tools/_pack_delivery.py'),run_name='__main__');return
 result,code=verify(a.seal_sha);print(json.dumps(result,ensure_ascii=False));raise SystemExit(code)
if __name__=='__main__':main()
