"""Read-only final overlay validation; explicit pack only. Never execute a production entry or probe a live path."""
from pathlib import Path
import json,hashlib,zipfile,argparse,re
B=Path(__file__).resolve().parents[1];R=B.parents[2];P=R/'docs/coder/d1resume02-release';S=B/'evidence/activation-freeze.json';Z=R/'docs/coder/D1-20261020-RESUME02-ACTIVATION-source.zip'
AUTH='04294e2f4e9dc0313b69239c9fd39572c2a449281949970b6ad1247d344c7ee3'
def pin(p):b=p.read_bytes();return dict(path=p.relative_to(R).as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def check(row):
 p=Path(row['path']);p=p if p.is_absolute() else R/p;b=p.read_bytes();assert len(b)==row['bytes'] and hashlib.sha256(b).hexdigest()==row['sha256'],str(p)
def check_hash(path,sha):assert hashlib.sha256(Path(path).read_bytes()).hexdigest()==sha,path
def diff(a,b):return {k for k in a.keys()|b.keys() if a.get(k)!=b.get(k)}
def validate_policy(c,policy):
 assert policy['mode']=='PRODUCTION' and policy['executionAuthorization']==AUTH
 assert policy['independentCaptureReview']==c['captureReview']['sha256'] and policy['releaseBindingDigest']==c['base']['sha256']
 assert policy['scope']==c['scope']['sha256'] and policy['planId']==c['scopeId'] and policy['entrySha256']==c['captureEntry']['sha256']
 for key in ['executionAuthorization','independentCaptureReview','releaseBindingDigest']:assert sum(x['sha256']==policy[key] for x in policy['executionPins'])==1
 for proof in policy['executionPins']:check_hash(proof['path'],proof['sha256'])
 original=json.loads((P/'release/capture-policy.json').read_text());assert diff(original,policy)=={'mode','executionAuthorization','executionPins'}
def validate_metadata(c,request,slot,policy):
 assert set(request)=={'schema','id','policySha256','scope','evidenceRoot','argv','maxTextBytes','qualificationSeconds'}
 assert request['schema']=='RESUME01_CAPTURE_REQUEST_V1' and request['policySha256']==c['capturePolicy']['sha256']
 assert request['scope']==c['scope']['sha256'] and request['evidenceRoot']==policy['evidenceRoot']
 assert all(request[k]==slot[k] for k in ['id','argv','maxTextBytes','qualificationSeconds'])
def materials():
 c=json.loads((B/'release/candidate-binding.json').read_text());old=json.loads((P/'release/candidate-binding.json').read_text())
 for key in ['preparedSeal','preparedReview','executionAuthorization','base','scope','release','config','budget','registryPlan','hostJar','observer','captureEntry','capturePolicy','runtime','metadataSet','observerSet','issuedPermit','productSourceReview','captureReview','disposition']:check(c[key])
 assert c['scopeId']==old['scopeId']=='20b08d64-6fd0-4a88-8b72-c80615e58258' and c['executionAuthorization']['sha256']==AUTH
 assert c['preparedSeal']['sha256']=='0b44299376d4e53f7499403e0122b1a6c21a5ecb14769989e8e810542f39cda9' and c['preparedReview']['sha256']=='75380086d04cfcefa6b1ed6b67307386b3e56f0a19b16366e9be8b55aa47f582'
 authority=json.loads((R/c['executionAuthorization']['path']).read_text());assert authority['kind']=='RESPONSIBLE_COORDINATOR_CONDITIONAL_EXECUTION_AUTHORIZATION' and authority['deviceExecutionAuthorized'] is True and authority['conditional'] is True and authority['scopeId']==c['scopeId']
 assert authority['issuerThread']=='01a107c3-2bf9-7fa0-94a0-234258ca6774'
 assert authority['budget']=={'operations':43,'textBytes':3145728,'archiveBytes':4194304,'unallocatedNotSpendable':409600,'oldUnknownReserve':8192,'oldKnownBytes':2272}
 for row in authority['pins']:check(row)
 assert c['devicePermitIssued'] and c['conditional'] and not c['consumed'] and not c['allExecutionPreconditionsSatisfied'] and c['independentFinalMechanicalReview'] is None and c['freshRuntimeGates'] is None
 for key in ['base','scope','release','config','budget','registryPlan','hostJar','observer','productSourceReview','captureReview','targetApks','disposition']:assert c[key]==old[key],key
 assert (R/c['captureEntry']['path']).read_bytes()==(R/old['captureEntry']['path']).read_bytes()
 assert (B/'reference/frozen-metadata-argv.json').read_bytes()==(P/'reference/frozen-metadata-argv.json').read_bytes()
 policy=json.loads((R/c['capturePolicy']['path']).read_text());validate_policy(c,policy)
 assert len(c['metadataRequests'])==len(policy['slots'])==5
 requestMap={}
 for i,row in enumerate(c['metadataRequests']):
  check(row);request=json.loads((R/row['path']).read_text());prior=old['captureRequests'][i];original=json.loads((R/prior['path']).read_text());assert diff(request,original)=={'policySha256'}
  validate_metadata(c,request,policy['slots'][i],policy);requestMap[prior['path']]=row
 requestMap[old['captureEntry']['path']]=c['captureEntry'];requestMap[old['capturePolicy']['path']]=c['capturePolicy']
 assert len(c['observerRequests'])==2
 for i,row in enumerate(c['observerRequests']):
  check(row);request=json.loads((R/row['path']).read_text());original=json.loads((R/old['observerRequests'][i]['path']).read_text());assert diff(request,original)=={'pins'}
  first=request['pins'][0];assert first['sha256']==AUTH and Path(first['path'])==R/c['executionAuthorization']['path'] and 'pendingRole' not in first
  for proof in request['pins']:assert proof['sha256'] is not None;check_hash(proof['path'],proof['sha256'])
  actual={(Path(x['path']).as_posix(),x['sha256']) for x in request['pins']}
  for prior in original['pins'][1:]:
   path=Path(prior['path']);ref=requestMap.get(path.relative_to(R).as_posix());expected=((R/ref['path']).as_posix(),ref['sha256']) if ref else (path.as_posix(),prior['sha256']);assert expected in actual
  for proof in authority['pins']:assert (Path(proof['path']).as_posix(),proof['sha256']) in actual
 runtime=json.loads((R/c['runtime']['path']).read_text());assert runtime['currentDeviceExecutionAllowed'] is False and runtime['authorityGranted'] is True and runtime['finalMechanicalReview'] is None
 for i,item in enumerate(runtime['commands']):
  assert item['request']==c['metadataRequests'][i];a=item['captureCommand'];assert Path(a[a.index('-File')+1])==R/c['captureEntry']['path'] and Path(a[a.index('-RequestPath')+1])==R/c['metadataRequests'][i]['path']
  if i>0:assert Path(item['predecessor']['externalProofPath']).name==policy['slots'][i-1]['id']+'-completion-proof.json'
  if i==3:assert item['deployment']['scope']==c['scope']['sha256'] and item['deployment']['releaseBindingDigest']==c['base']['sha256']
 for i,item in enumerate(runtime['javaObserverCommands']):
  a=item['argv'];assert Path(a[a.index('-File')+1])==R/c['observer']['path'] and Path(a[a.index('-RequestPath')+1])==R/c['observerRequests'][i]['path']
 permitPath=R/c['issuedPermit']['path'];raw=permitPath.read_bytes();obj=json.loads(raw);f=obj['fields'];assert obj['e9']==1 and raw==('{"e9":1,"fields":'+json.dumps(dict(sorted(f.items())),separators=(',',':'))+'}\n').encode('ascii')
 assert len(raw)<=8192 and len(f)<=48 and all(re.fullmatch('[A-Za-z0-9._:/,@+~-]{1,8192}',v) for v in f.values())
 assert f['kind']=='resume02ActivationPermit' and f['state']=='ISSUED_CONDITIONAL_NOT_CONSUMED' and f['authorization']==AUTH and f['scopeId']==c['scopeId']
 for field,key in [('scope','scope'),('release','release'),('config','config'),('base','base'),('budget','budget'),('registryPlan','registryPlan'),('jar','hostJar'),('observer','observer'),('captureEntry','captureEntry'),('capturePolicy','capturePolicy'),('metadataSet','metadataSet'),('observerSet','observerSet'),('runtime','runtime')]:assert f[field]==c[key]['sha256']
 assert f['productSourceReview']==c['productSourceReview']['sha256'] and f['captureReview']==c['captureReview']['sha256'] and f['preparedReview']==c['preparedReview']['sha256']
 assert f['method']=='ordinarySenderCannotBindCodec' and f['operations']=='43' and f['textBytes']=='3145728' and f['archiveBytes']=='4194304' and f['unallocatedNotSpendable']=='409600'
 assert json.loads((R/c['metadataSet']['path']).read_text())['requests']==c['metadataRequests'] and json.loads((R/c['observerSet']['path']).read_text())['requests']==c['observerRequests']
 budget=json.loads((R/c['budget']['path']).read_text());assert budget['controlCommittedConservative']==735456 and budget['controlHeadroomNotNewOperations']==50976 and budget['historicalSeparateCarry']['consoleUnknownSlotHeld']==8192 and budget['historicalSeparateCarry']['refunded'] is False
 assert 1949696+735456+50976+409600==3145728
 eq=json.loads((P/'evidence/production-equivalence.json').read_text());assert len(eq['productionSources'])==74 and len(eq['members'])==183
 for row in eq['productionSources']:check(row)
 with zipfile.ZipFile(R/c['hostJar']['path']) as z:
  assert set(z.namelist())=={m['entry'] for m in eq['members']}
  for row in eq['members']:assert hashlib.sha256(z.read(row['entry'])).hexdigest()==row['sha256']
 for row in json.loads((P/'evidence/resume02-freeze.json').read_text())['immutableFiles']:check(row)
 assert not any(p.name.endswith('-completion-proof.json') for p in B.rglob('*') if p.is_file()),'DYNAMIC_PROOF_PRECREATED'
 return c
def verify(expected=None):
 assert S.is_file(),'NOT_FROZEN'
 if expected:assert pin(S)['sha256']==expected,'EXTERNAL_SEAL_PIN'
 seal=json.loads(S.read_text());rows=seal['immutableFiles'];assert len(rows)==len({x['path'] for x in rows})
 for row in rows:check(row)
 members={row['path']:row for row in rows if row['path']!=seal['archive']['path']}
 with zipfile.ZipFile(Z) as z:
  assert len(z.namelist())==len(members) and set(z.namelist())==set(members)
  for name,row in members.items():raw=z.read(name);assert len(raw)==row['bytes'] and hashlib.sha256(raw).hexdigest()==row['sha256']
 c=materials();dag=json.loads((B/'evidence/dependency-dag.json').read_text());done=set()
 for node in dag['nodes']:assert set(node['dependsOn'])<=done;done.add(node['role']);check(node['file'])
 assert json.loads((B/'evidence/offline-checks.json').read_text())['status']=='PASS_STATIC_ACTIVATION_BINDING'
 return dict(status='PASS_ACTIVATION_STRICT_READONLY_VERIFY',writes=0,productionEntryInvoked=False,sdkCalls=0,deviceCalls=0,liveFilesRead=False,seal=pin(S),archive=seal['archive'],archiveEntries=len(members),immutableRows=len(rows),authorization=c['executionAuthorization'],policy=c['capturePolicy'],permit=c['issuedPermit'],base=c['base'],scope=c['scope'],preparedRowsUnchanged=95,productionSourcesUnchanged=74,productionClassesUnchanged=183,hostBuilds=0,androidBuilds=0,conditionalPermitIssued=True,consumed=False,independentFinalMechanicalReview=None,T07='NOT_RUN',D1='NOT_PASSED',M0='NOT_STARTED')
def pack():
 assert not S.exists() and not Z.exists(),'ALREADY_FROZEN';c=materials()
 paths=[p for p in B.rglob('*') if p.is_file() and '__pycache__' not in p.parts];paths.append(R/'docs/coder/D1_RESUME02_ACTIVATION_DELIVERY_V1.0.md');rows=[pin(p) for p in sorted(set(paths))]
 with zipfile.ZipFile(Z,'x',compression=zipfile.ZIP_DEFLATED) as z:
  for row in rows:z.writestr(row['path'],(R/row['path']).read_bytes())
 archive=pin(Z);rows.append(archive);S.write_text(json.dumps(dict(schema=1,candidate=c['candidate'],archive=archive,immutableFiles=rows,conditionalAuthorizationBound=True,independentFinalMechanicalReview='PENDING',executedByCoder=False),indent=2)+'\n');print(json.dumps(dict(status='PACKED_FINAL_CONDITIONAL_ACTIVATION',seal=pin(S),archive=archive,archiveEntries=len(rows)-1)))
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('mode',choices=['verify','pack'],nargs='?',default='verify');p.add_argument('--seal-sha');a=p.parse_args()
 if a.mode=='pack':
  if a.seal_sha:p.error('--seal-sha only for verify')
  pack()
 else:print(json.dumps(verify(a.seal_sha)))
if __name__=='__main__':main()
