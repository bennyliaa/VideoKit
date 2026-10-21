"""ENV03 data-only verification; default verify/help read-only. No entry invocation or live directory probing."""
from pathlib import Path
import json,hashlib,argparse,re,zipfile
B=Path(__file__).resolve().parents[1];R=B.parents[2];S=B/'evidence/env03-freeze.json';Z=R/'docs/coder/D1-20261020-ENV03-source.zip';ID_RE=r'^[A-Za-z0-9_]{1,80}$'
def pin(p):raw=p.read_bytes();return dict(path=p.relative_to(R).as_posix(),bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest())
def check(row):p=Path(row['path']);p=p if p.is_absolute() else R/p;raw=p.read_bytes();assert hashlib.sha256(raw).hexdigest()==row['sha256'];assert 'bytes' not in row or len(raw)==row['bytes']
def admitted_index(policy,id):
 positions=[i for i,s in enumerate(policy['slots']) if s['id']==id]
 if len(positions)!=1 or not re.fullmatch(ID_RE,id):raise ValueError('EXACT_REQUEST_SLOT')
 return positions[0]
def materials():
 c=json.loads((B/'release/candidate-binding.json').read_text())
 for key in ['plan','authorization','budget','entry','reference','captureReview','policy','runtime','sourceFreeze','sourceHistory']:check(c[key])
 assert c['scopeId']=='f0be73d2-01d2-4775-be6d-b6e55b8b77b3' and c['scope']==c['plan']['sha256']
 assert c['authorization']['sha256']=='dcc163aa7f4764a7cef146b33dadf1e5c86793be987efc95aefc1c315fcec44c'
 a=json.loads((R/c['authorization']['path']).read_text());assert a['kind']=='RESPONSIBLE_COORDINATOR_ENVIRONMENT_RECHECK_AUTHORIZATION' and a['issuerThread']=='01a107c3-2bf9-7fa0-94a0-234258ca6774' and a['deviceExecutionAuthorized'] is True and a['scopeId']==c['scopeId']
 assert a['operations']==2 and a['textBytes']==a['archiveBytes']==1048576 and a['captureCaps']==[65536,524288] and a['qualificationSeconds']==15
 for row in a['pins']:check(row)
 policy=json.loads((R/c['policy']['path']).read_text());plan=json.loads((R/c['plan']['path']).read_text());assert policy['mode']=='PRODUCTION' and policy['planId']==c['scopeId'] and policy['scope']==c['scope'] and policy['evidenceRoot']==plan['evidenceRoot']
 assert policy['releaseBindingDigest']==c['plan']['sha256'] and policy['executionAuthorization']==c['authorization']['sha256'] and policy['independentCaptureReview']==c['captureReview']['sha256']
 for key in ['executionAuthorization','independentCaptureReview','releaseBindingDigest']:assert sum(x['sha256']==policy[key] for x in policy['executionPins'])==1
 for row in policy['executionPins']:check(row)
 assert c['entry']['sha256']==policy['entrySha256']=='fef62cb2a2ddbca49e22b1f041e59387185323539945d86e06dd8823449e25fe'
 assert (R/c['entry']['path']).read_bytes()==(R/'docs/coder/d1resume02-activation/tools/capture_metadata.ps1').read_bytes()
 templates=json.loads((R/c['reference']['path']).read_text())['commands'];assert len(policy['slots'])==len(templates)==5
 for i,slot in enumerate(policy['slots']):assert slot['argv']==templates[i]['argv'] and slot['maxTextBytes']==[65536,524288,65536,65536,524288][i] and slot['qualificationSeconds']==15 and slot['phase']==('M1' if i<3 else 'M2')
 eligible=[s['id'] for s in policy['slots'] if re.fullmatch(ID_RE,s['id'])];assert eligible==plan['authorizedRequestIds']==['ENV03_M1_identity','ENV03_M1_global'] and len(set(s['id'] for s in policy['slots']))==5
 assert [s['id'] for s in policy['slots'][2:]]==plan['inactiveTemplateIds'] and all(':' in s['id'] for s in policy['slots'][2:])
 code=(R/c['entry']['path']).read_text();assert "$slots[$i].id -ceq $request.id" in code and "$request.id -cnotmatch '^[A-Za-z0-9_]{1,80}$'" in code and "throw 'EXACT_REQUEST_SLOT'" in code
 assert len(c['requests'])==len(list((B/'release/requests').glob('*.json')))==2
 for i,row in enumerate(c['requests']):
  check(row);req=json.loads((R/row['path']).read_text());assert set(req)=={'schema','id','policySha256','scope','evidenceRoot','argv','maxTextBytes','qualificationSeconds'}
  assert req['schema']=='RESUME01_CAPTURE_REQUEST_V1' and req['policySha256']==c['policy']['sha256'] and req['scope']==c['scope'] and req['evidenceRoot']==policy['evidenceRoot'] and admitted_index(policy,req['id'])==i
  assert all(req[k]==policy['slots'][i][k] for k in ['id','argv','maxTextBytes','qualificationSeconds'])
 d=json.loads((R/c['runtime']['path']).read_text());assert d['maxOperations']==2 and d['stopAfterSecondRegardlessOfOccupancy'] is True and d['completionProofAfterGlobalNotAuthorized'] is True and d['thirdSlotRuntimeAdmission'] is False
 assert len(d['commands'])==2 and d['requests']==c['requests'] and d['independentMechanicalReview'] is None and d['freshLocalGates'] is None
 for i,item in enumerate(d['commands']):
  cmd=item['argv'];assert Path(cmd[cmd.index('-File')+1])==R/c['entry']['path'] and Path(cmd[cmd.index('-RequestPath')+1])==R/c['requests'][i]['path']
  if i==1:assert Path(item['predecessor']['path']).name=='ENV03_M1_identity-completion-proof.json' and item['predecessor']['argument']=='-PredecessorProofSha'
 budget=json.loads((R/c['budget']['path']).read_text());assert budget['operations']==2 and budget['textBytes']==budget['archiveBytes']==1048576 and budget['oldBalanceInherited'] is False
 assert budget['rawReadReserve']==589824 and budget['captureControlReserve']==55296 and budget['localPreludeRecordsAndConsole']==16384 and budget['finalReportAndResultReserve']==32768
 assert budget['totalAssigned']==sum(budget[k] for k in ['rawReadReserve','captureControlReserve','localPreludeRecordsAndConsole','finalReportAndResultReserve'])==694272
 assert budget['totalAssigned']+budget['unassignedNotAdditionalPermission']==1048576 and budget['oldSdkReadBytes']==388818
 contract=json.loads((B/'release/semantic-and-accounting-contract.json').read_text());assert 'version17' in contract['testApkVersionRule'] and 'No extra' in contract['testApkVersionRule'] and 'testVersion' not in contract['identity']
 assert c['productReleaseGenerated'] is False and c['productPermitGenerated'] is False and c['productSourcesChanged']==c['hostBuilds']==c['androidBuilds']==0
 for row in json.loads((R/c['sourceFreeze']['path']).read_text())['immutableFiles']:check(row)
 assert not any(p.name.endswith('-completion-proof.json') for p in B.rglob('*') if p.is_file())
 return c
def verify(expected=None):
 assert S.is_file(),'NOT_FROZEN'
 if expected:assert pin(S)['sha256']==expected,'EXTERNAL_SEAL_PIN'
 seal=json.loads(S.read_text());rows=seal['immutableFiles'];assert len(rows)==len({x['path'] for x in rows})
 for row in rows:check(row)
 members={x['path']:x for x in rows if x['path']!=seal['archive']['path']}
 with zipfile.ZipFile(Z) as z:
  assert len(z.namelist())==len(members) and set(z.namelist())==set(members)
  for name,row in members.items():raw=z.read(name);assert len(raw)==row['bytes'] and hashlib.sha256(raw).hexdigest()==row['sha256']
 c=materials();assert json.loads((B/'evidence/admission-proof.json').read_text())['eligibleRequestCount']==2
 return dict(status='PASS_ENV03_STRICT_READONLY_VERIFY',writes=0,productionEntryInvoked=False,sdkCalls=0,deviceCalls=0,liveFilesRead=False,seal=pin(S),archive=seal['archive'],archiveEntries=len(members),immutableRows=len(rows),authorization=c['authorization'],plan=c['plan'],policy=c['policy'],authorizedRequests=2,inactiveTemplates=3,entry=c['entry'],productReleaseGenerated=False,hostBuilds=0,androidBuilds=0,old388818Preserved=True,consumed=False,independentMechanicalReview=None,D1='NOT_PASSED',M0='NOT_STARTED')
def pack():
 assert not S.exists() and not Z.exists(),'ALREADY_FROZEN';c=materials();paths=[p for p in B.rglob('*') if p.is_file() and '__pycache__' not in p.parts];paths.append(R/'docs/coder/D1_ENV03_DELIVERY_V1.0.md');rows=[pin(p) for p in sorted(set(paths))]
 with zipfile.ZipFile(Z,'x',compression=zipfile.ZIP_DEFLATED) as z:
  for row in rows:z.writestr(row['path'],(R/row['path']).read_bytes())
 archive=pin(Z);rows.append(archive);S.write_text(json.dumps(dict(schema=1,candidate=c['candidate'],archive=archive,immutableFiles=rows,authorizedRequestCount=2,entryInvokedByCoder=False,independentMechanicalReview='PENDING'),indent=2)+'\n');print(json.dumps(dict(status='PACKED_ENV03',seal=pin(S),archive=archive,archiveEntries=len(rows)-1)))
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('mode',choices=['verify','pack'],nargs='?',default='verify');p.add_argument('--seal-sha');a=p.parse_args()
 if a.mode=='pack':
  if a.seal_sha:p.error('--seal-sha only for verify')
  pack()
 else:print(json.dumps(verify(a.seal_sha)))
if __name__=='__main__':main()
