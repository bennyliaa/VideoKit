"""Mechanical authorized overlay only. Never invokes an entry, SDK, live file, or product build."""
from pathlib import Path
import json,hashlib,shutil
B=Path(__file__).resolve().parents[1];R=B.parents[2];P=R/'docs/coder/d1resume02-release'
AUTH='04294e2f4e9dc0313b69239c9fd39572c2a449281949970b6ad1247d344c7ee3';PREPARED_REVIEW='75380086d04cfcefa6b1ed6b67307386b3e56f0a19b16366e9be8b55aa47f582'
def pin(p):b=p.read_bytes();return dict(path=p.relative_to(R).as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def check(row):assert pin(Path(row['path']) if Path(row['path']).is_absolute() else R/row['path'])==dict(path=(Path(row['path']).relative_to(R).as_posix() if Path(row['path']).is_absolute() else row['path']),bytes=row['bytes'],sha256=row['sha256']),row['path']
def copy(p,q):q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,q);return pin(q)
def write(p,o):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');return pin(p)
def canonical(p,f):p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(('{"e9":1,"fields":'+json.dumps(dict(sorted(f.items())),separators=(',',':'))+'}\n').encode('ascii'));return pin(p)
assert not (B/'release/candidate-binding.json').exists(),'OVERLAY_ALREADY_PREPARED'
seal=P/'evidence/resume02-freeze.json';assert pin(seal)['sha256']=='0b44299376d4e53f7499403e0122b1a6c21a5ecb14769989e8e810542f39cda9'
for row in json.loads(seal.read_text())['immutableFiles']:check(row)
c=json.loads((P/'release/candidate-binding.json').read_text());authSource=R/'docs/milestones/D1_RESUME02_ACTIVATION_EXECUTION_AUTHORIZATION_V1.0.json';assert pin(authSource)['sha256']==AUTH
auth=json.loads(authSource.read_text());assert auth['deviceExecutionAuthorized'] is True and auth['conditional'] is True and auth['scopeId']==c['scopeId']
for row in auth['pins']:check(row)
authority=copy(authSource,B/'release/execution-authorization.json');copy(seal,B/'reference/prepared-freeze.json')
reviewSource=R/'docs/tester/D1_RESUME02_RELEASE_REVIEW_REPORT_V1.0.md';assert pin(reviewSource)['sha256']==PREPARED_REVIEW;review=copy(reviewSource,B/'reference'/reviewSource.name)
entry=copy(P/'tools/capture_metadata.ps1',B/'tools/capture_metadata.ps1');template=copy(P/'reference/frozen-metadata-argv.json',B/'reference/frozen-metadata-argv.json')
policy=json.loads((P/'release/capture-policy.json').read_text());policy.update(mode='PRODUCTION',executionAuthorization=AUTH)
# The production validator requires exactly ONE digest match for each authority/capture/base proof.
pins={}
for row in [dict(path=(R/authority['path']).as_posix(),sha256=AUTH),*auth['pins']]:
 if row['sha256'] not in pins:pins[row['sha256']]=dict(path=row['path'],sha256=row['sha256'])
policy['executionPins']=list(pins.values());policyPin=write(B/'release/capture-policy.json',policy)
requests=[];mapping={}
mapping[(R/c['captureEntry']['path']).as_posix()]=entry;mapping[(R/c['capturePolicy']['path']).as_posix()]=policyPin
for row in c['captureRequests']:
 p=R/row['path'];req=json.loads(p.read_text());req['policySha256']=policyPin['sha256'];current=write(B/'release/metadata-requests'/p.name,req);requests.append(current);mapping[p.as_posix()]=current
observers=[]
for i,row in enumerate(c['observerRequests']):
 req=json.loads((R/row['path']).read_text());assert req['pins'][0]['sha256'] is None
 bound=[dict(path=(R/authority['path']).as_posix(),sha256=AUTH,role='RESPONSIBLE_COORDINATOR_CONDITIONAL_EXECUTION_AUTHORIZATION')]
 for old in req['pins'][1:]:
  ref=mapping.get(Path(old['path']).as_posix());bound.append(dict(path=(R/ref['path']).as_posix(),sha256=ref['sha256']) if ref else old)
 seen={row['path'] for row in bound}
 for proof in auth['pins']:
  if proof['path'] not in seen:bound.append(dict(path=proof['path'],sha256=proof['sha256']));seen.add(proof['path'])
 req['pins']=bound;observers.append(write(B/'release'/('observer-deploy-request.json' if i==0 else 'observer-case-request.json'),req))
runtime=json.loads((P/'release/runtime-dependency-contract.json').read_text());runtime.update(currentDeviceExecutionAllowed=False,authorityGranted=True,conditionalExecutionOnly=True,state='BOUND_AWAIT_FINAL_MECHANICAL_AND_FRESH_GATES',executionAuthorization=authority,finalMechanicalReview=None)
for i,item in enumerate(runtime['commands']):
 item['request']=requests[i];item['captureCommand'][item['captureCommand'].index('-File')+1]=str(R/entry['path']);item['captureCommand'][item['captureCommand'].index('-RequestPath')+1]=str(R/requests[i]['path']);item['currentState']='CONDITIONALLY_BOUND_RUNTIME_PROOFS_AND_SEMANTICS_REQUIRED'
runtime['javaObserverCommands']=[dict(role=role,argv=['C:/Users/benny/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/powershell/pwsh.exe','-NoLogo','-NoProfile','-NonInteractive','-File',str(R/c['observer']['path']),'-RequestPath',str(R/ref['path'])]) for role,ref in zip(['DEPLOY','CASE'],observers)]
runtimePin=write(B/'release/runtime-dependency-contract.json',runtime)
requestSet=write(B/'release/metadata-request-set.json',dict(policy=policyPin,requests=requests,entry=entry));observerSet=write(B/'release/observer-request-set.json',dict(observer=c['observer'],requests=observers))
for name in ['deployment-command-graph.json','fresh-admission-requirements.json','external-completion-proof.contract.json','deployment-completion-proof.contract.json']:copy(P/'release'/name,B/'reference'/name)
permit=canonical(B/'release/issued-permit.json',dict(kind='resume02ActivationPermit',scopeId=c['scopeId'],scope=c['scope']['sha256'],release=c['release']['sha256'],config=c['config']['sha256'],base=c['base']['sha256'],authorization=AUTH,preparedReview=PREPARED_REVIEW,productSourceReview=c['productSourceReview']['sha256'],captureReview=c['captureReview']['sha256'],budget=c['budget']['sha256'],registryPlan=c['registryPlan']['sha256'],jar=c['hostJar']['sha256'],observer=c['observer']['sha256'],captureEntry=entry['sha256'],capturePolicy=policyPin['sha256'],metadataSet=requestSet['sha256'],observerSet=observerSet['sha256'],runtime=runtimePin['sha256'],method='ordinarySenderCannotBindCodec',operations='43',textBytes='3145728',archiveBytes='4194304',unallocatedNotSpendable='409600',state='ISSUED_CONDITIONAL_NOT_CONSUMED',condition='FINAL_MECHANICAL_PASS_AND_FRESH_RUNTIME_GATES'))
write(B/'release/candidate-binding.json',dict(candidate='D1-20261020-RESUME02-ACTIVATION',status='BOUND_FOR_FINAL_INDEPENDENT_MECHANICAL_REVIEW',scopeId=c['scopeId'],preparedSeal=pin(seal),preparedReview=review,executionAuthorization=authority,authorizationKind='RESPONSIBLE_COORDINATOR_CONDITIONAL_EXECUTION_AUTHORIZATION_NOT_USER_NEW_SIGNATURE_OR_CRYPTOGRAPHIC_SEAL',base=c['base'],scope=c['scope'],release=c['release'],config=c['config'],budget=c['budget'],registryPlan=c['registryPlan'],hostJar=c['hostJar'],observer=c['observer'],captureEntry=entry,capturePolicy=policyPin,metadataRequests=requests,observerRequests=observers,runtime=runtimePin,metadataSet=requestSet,observerSet=observerSet,issuedPermit=permit,productSourceReview=c['productSourceReview'],captureReview=c['captureReview'],targetApks=c['targetApks'],disposition=c['disposition'],devicePermitIssued=True,conditional=True,consumed=False,allExecutionPreconditionsSatisfied=False,independentFinalMechanicalReview=None,freshRuntimeGates=None,liveRootCreated=False,hostBuilds=0,androidBuilds=0,T07='NOT_RUN',D1='NOT_PASSED',M0='NOT_STARTED'))
write(B/'evidence/overlay-difference.json',dict(preparedCandidate=pin(P/'release/candidate-binding.json'),oldPolicy=c['capturePolicy'],newPolicy=policyPin,allowedPolicyChangedKeys=['mode','executionAuthorization','executionPins'],entry=entry,originalEntry=c['captureEntry'],requests=[dict(old=a,new=b,allowedChangedKeys=['policySha256']) for a,b in zip(c['captureRequests'],requests)],observers=[dict(old=a,new=b,allowedChangedKeys=['pins']) for a,b in zip(c['observerRequests'],observers)],baseHashesChanged=False,productionSourcesChanged=0,productionClassesChanged=0,hostBuilds=0,androidBuilds=0,sdkCalls=0,liveFilesRead=False))
print(json.dumps(dict(status='FINAL_OVERLAY_BOUND_NOT_EXECUTED',authority=authority,policy=policyPin,permit=permit,scope=c['scope'],base=c['base'])))
