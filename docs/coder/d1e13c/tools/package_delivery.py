"""Default verify/help are pure read-only; only explicit pack writes the host overlay."""
from pathlib import Path
import argparse,hashlib,json,zipfile
B=Path(__file__).resolve().parents[1];R=B.parents[2]
def pin(p):b=p.read_bytes();return {'path':p.relative_to(R).as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def check(row):assert pin(R/row['path'])=={k:row[k] for k in ['path','bytes','sha256']},row['path']
def verify(expected=None):
 p=B/'evidence/e13c-freeze.json'
 if not p.is_file():return {'status':'NOT_FROZEN','writes':0},2
 sealpin=pin(p)
 if expected:assert sealpin['sha256']==expected,'EXTERNAL_SEAL_SHA'
 seal=json.loads(p.read_text(encoding='utf-8'));rows=seal['immutableFiles'];assert len(rows)==len({r['path'] for r in rows})
 for row in rows:check(row)
 members={r['path']:r for r in rows if r['path']!=seal['archive']['path']}
 with zipfile.ZipFile(R/seal['archive']['path']) as z:
  assert len(z.namelist())==len(members) and set(z.namelist())==set(members)
  for name,row in members.items():raw=z.read(name);assert len(raw)==row['bytes'] and hashlib.sha256(raw).hexdigest()==row['sha256']
 for prior in seal['priorSeals']:
  check(prior['seal'])
  for row in json.loads((R/prior['seal']['path']).read_text(encoding='utf-8'))['immutableFiles']:check(row)
 reuse=json.loads((B/'release/candidate-binding.json').read_text());assert reuse['actualApprovedScope'] is None and reuse['actualRelease'] is None and reuse['actualOnce'] is None and reuse['sourceReview'] is None
 assert reuse['version']==17 and reuse['acceptedSourceVersion']==15 and reuse['onceBasename']=='e13a-activation-deployment.once'
 for row in reuse['targetApks']:check(row)
 check(reuse['metadataManifest']);check(reuse['metadataOverlaySeal'])
 manifest=json.loads((B/'evidence/host-jar-manifest.json').read_text());check(manifest['jar']);check(manifest['baseJar']);assert reuse['hostJar']==manifest['jar']
 assert len(manifest['classes'])==173
 base=json.loads((R/'docs/coder/d1e13a/evidence/host-jar-manifest.json').read_text());baseMembers={r['entry']:r for r in base['classes']}
 with zipfile.ZipFile(R/manifest['jar']['path']) as z,zipfile.ZipFile(R/manifest['baseJar']['path']) as old:
  assert len(z.namelist())==173 and len(set(z.namelist()))==173 and set(z.namelist())=={r['entry'] for r in manifest['classes']}
  unchanged=changed=0
  for row in manifest['classes']:
   check(row['source']);raw=z.read(row['entry']);assert len(raw)==row['bytes'] and hashlib.sha256(raw).hexdigest()==row['sha256']
   if row['relationship']=='EXACT_BASE_JAR_MEMBER':assert raw==old.read(row['entry']) and row['source']==baseMembers[row['entry']]['source'];unchanged+=1
   else:assert row['entry'][:-6].split('$')[0] in ['com/videokit/spike/e4/E11DeploymentOnce','com/videokit/spike/e4/E13HostActivationSession'];changed+=1
  assert unchanged==168 and changed==5
 helper=(B/'tools/E11DeploymentOnce.java').read_text();entry=(B/'tools/E13HostActivationSession.java').read_text()
 assert 'private enum Role { E11, E13A }' in helper and 'Role.E11);' in helper and 'Role.E13A);' in helper
 assert 'E11DeploymentOnce.e13Activation(once,supervisor).record(' in entry and 'new E11DeploymentOnce(once,supervisor).record(' not in entry
 assert 'StandardOpenOption.CREATE_NEW' in helper and 'channel.force(true)' in helper and 'E11_ONCE_ORIGINAL_RETURN_REQUIRED' in helper
 plan=json.loads((B/'release/device-plan.json').read_text());bud=plan['executionBudgetProposal']
 assert bud['successfulPathOperations']==48 and bud['maximumOperations']==50 and bud['textTotal']==2097152
 assert sum(bud[k] for k in ['deploymentEntry','deploymentChildren','caseJavaEntries','caseInstrumentChildren','metadataClients'])==48
 assert bud['successfulPathAllocatedText']+bud['twoOccupiedM1TextReserve']==bud['totalTextAllocated']==1769472
 assert bud['textTotal']-bud['totalTextAllocated']==bud['remainingText']==327680
 assert not bud['oldBatch37of56BalanceInherited'] and plan['freshM1Required'] and plan['actualOnce'] is None
 tests=json.loads((B/'evidence/host-checks-001/results.json').read_text());assert tests['status']=='PASS_E13C_FINITE_HOST_CHECKS' and tests['publicCliAttempts']==8
 unknown=json.loads((B/'evidence/unknown-jar-002/results.json').read_text());assert unknown['status']=='PASS_EXACT_SHIPPED_HELPER_UNKNOWN' and not unknown['actualCustodianUnknownClaim']
 return {'status':'PASS_E13C_STRICT_READONLY_VERIFY','writes':0,'archive':seal['archive'],'externalSeal':sealpin,'archiveEntries':len(members),'immutableRows':len(rows),'jarClasses':173,'exactBaseJarMembers':168,'recompiledMembers':5,'priorSeals':seal['priorSeals'],'productApksReused':3,'apkBuilds':0,'nativeBuilds':0,'deviceCalls':0,'D1':'NOT_PASSED','M0':'NOT_STARTED'},0
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('mode',choices=['verify','pack'],nargs='?',default='verify');p.add_argument('--seal-sha');a=p.parse_args()
 if a.mode=='pack':
  if a.seal_sha:p.error('--seal-sha only for verify')
  import runpy
  runpy.run_path(str(B/'tools/_pack_host.py'),run_name='__main__');return
 result,code=verify(a.seal_sha);print(json.dumps(result,ensure_ascii=False));raise SystemExit(code)
if __name__=='__main__':main()
