"""Prepare one acyclic RESUME02 base. No execution authorization, field mutation of old packages, or live reads."""
from pathlib import Path
import json,hashlib,shutil,uuid,zipfile
B=Path(__file__).resolve().parents[1];R=B.parents[2];OLD=R/'docs/coder/d1resume01-release';CAP=R/'docs/coder/d1resume01-capture'
PRODUCT_REVIEW='0bad8b95ac7e0308713fdfed2f21c9215d18606f86aaa8e4e1dbd09059640743';CAPTURE_REVIEW='ad306682e27cdf1dec67955d9cb7f57bf99cd1451ab3b413963ee03439c6caf9'
def pin(p):b=p.read_bytes();return dict(path=p.relative_to(R).as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def write(p,o):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');return pin(p)
def copy(p,q):q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,q);return pin(q)
def canonical(p,f):p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(('{"e9":1,"fields":'+json.dumps(dict(sorted(f.items())),separators=(',',':'))+'}\n').encode('ascii'));return pin(p)
def fields(p):return json.loads(p.read_text())['fields']
assert not (B/'release/candidate-binding.json').exists(),'PREPARED_ALREADY'
seals=[]
for folder,sha in [(OLD,'b7537e7dd4934c248f727064a103c1fbfc099d0e7a28cce55b28a777df7fd461'),(CAP,'9fd6b86f906f0ae196249e0885a83706be4692c31016bf687f6f07e322ab3b8c')]:
 p=folder/('evidence/release-freeze.json' if folder==OLD else 'evidence/capture-freeze.json');assert pin(p)['sha256']==sha
 for row in json.loads(p.read_text())['immutableFiles']:assert pin(R/row['path'])==row,row['path']
 seals.append(copy(p,B/'reference'/p.name))
old=json.loads((OLD/'release/candidate-binding.json').read_text());reviews=[]
for name,expected in [('D1_RESUME01_STATIC_REVIEW_REPORT_V1.0.md',PRODUCT_REVIEW),('D1_RESUME01_CAPTURE_REVIEW_REPORT_V1.0.md',CAPTURE_REVIEW)]:
 p=R/'docs/tester'/name;assert pin(p)['sha256']==expected;reviews.append(copy(p,B/'reference'/name))
jar=copy(R/old['hostJar']['path'],B/'artifacts/resume02-host-tools.jar');observer=copy(R/old['observer']['path'],B/'tools/observe_original.ps1');entry=copy(CAP/'tools/capture_metadata.ps1',B/'tools/capture_metadata.ps1')
copy(CAP/'reference/frozen-metadata-argv.json',B/'reference/frozen-metadata-argv.json')
for p in (OLD/'disposition').glob('*'):copy(p,B/'disposition'/p.name)
for p in (OLD/'reference/accepted-registry-snapshot').rglob('*'):
 if p.is_file():copy(p,B/'reference/accepted-registry-snapshot'/p.relative_to(OLD/'reference/accepted-registry-snapshot'))
copy(OLD/'evidence/registry-provenance.json',B/'reference/registry-provenance.json')
source=json.loads((OLD/'evidence/source-identity.json').read_text());eq=json.loads((OLD/'evidence/member-equivalence.json').read_text())
for row in source['productionSources']:assert pin(R/row['current']['path'])==row['current']
with zipfile.ZipFile(R/old['hostJar']['path']) as a,zipfile.ZipFile(R/jar['path']) as b:
 assert a.namelist()==b.namelist() and len(a.namelist())==183
 for m in eq['members']:assert a.read(m['entry'])==b.read(m['entry']) and hashlib.sha256(b.read(m['entry'])).hexdigest()==m['sha256']
write(B/'evidence/production-equivalence.json',dict(productionSources=[r['current'] for r in source['productionSources']],members=eq['members'],hostJar=jar,priorHostJar=old['hostJar'],observer=observer,priorObserver=old['observer'],captureEntry=entry,priorCaptureEntry=pin(CAP/'tools/capture_metadata.ps1'),changedSources=0,changedClasses=0,hostBuilds=0,androidBuilds=0))
preparation=write(B/'release/preparation-authorization.json',dict(kind='CAPTURED_COORDINATOR_PREPARATION_AUTHORITY_ONLY',date='2026-10-20',sourceThread='01a107c3-2bf9-7fa0-94a0-234258ca6774',scope='RESUME02_RELEASE_OFFLINE_PREPARATION',acceptedCaptureReview=CAPTURE_REVIEW,acceptedBudget=dict(operations=43,textBytes=3145728,archiveBytes=4194304,unallocatedNotSpendable=409600),instruction='一次完成准确新release无环绑定/有限离线核验/整包freeze；零Android或host构建，不现场/SDK/5037/设备。准备授权不是设备许可，不伪签执行授权；生产policy必须授权则保持待签，交准确可审差异。',deviceExecutionAuthorized=False))
budget=json.loads((CAP/'release/accounting-feasibility.json').read_text());budget.update(status='ACCEPTED_RESUME02_PREPARATION_NOT_EXECUTION_PERMISSION',preparationAcceptance=preparation)
budgetPin=write(B/'release/exact-budget.json',budget)
batch=str(uuid.uuid4());execution=R/'docs/tester/D1_RESUME01_CAPTURE_EXECUTION'/batch;output=execution/'outputs'
scope=fields(OLD/'release/runtime-scope.json');scope.update(scopeId=batch,sourceReview=PRODUCT_REVIEW);sp=canonical(B/'release/runtime-scope.json',scope)
release=fields(OLD/'release/activation-release.json');release.update(scope=sp['sha256'],sourceReview=PRODUCT_REVIEW);rp=canonical(B/'release/activation-release.json',release)
config=fields(OLD/'release/activation-trust-deploy.json');config.update(scopePath=(R/sp['path']).as_posix(),scopeSha=sp['sha256'],dispatchRecord=(execution/'e13f-lifecycle-deployment.once').as_posix());cp=canonical(B/'release/activation-trust-deploy.json',config)
registry=json.loads((OLD/'release/registry-plan.json').read_text());registry.update(currentSourceReview=PRODUCT_REVIEW,captureReview=CAPTURE_REVIEW,currentState='NOT_READ; new independent mechanical acceptance and fresh original local gates still required.')
for row in registry['expectedFiles']:row['snapshot']=pin(B/'reference/accepted-registry-snapshot'/row['relative'])
registryPin=write(B/'release/registry-plan.json',registry)
base=write(B/'release/base-release-descriptor.json',dict(schema='RESUME02_BASE_RELEASE_V1',candidate='D1-20261020-RESUME02-RELEASE',scopeId=batch,scope=sp,release=rp,config=cp,registryPlan=registryPin,executionRoot=str(execution),captureRoot=str(output),deploymentOncePath=config['dispatchRecord'],caseOnce=dict(type='PERSISTENT_SCOPE_METHOD_CLAIM',scope=sp['sha256'],method=scope['methods']),budget=budgetPin,preparationAuthority=preparation,deviceExecutionAuthority=None,productSourceReview=reviews[0],captureReview=reviews[1],hostJar=jar,observer=observer,captureEntry=entry,targetApks=old['targetApks'],disposition=pin(B/'disposition/reviewed-original-disposition.json'),capturedHistoricalUnknownsPreserved=True))
policy=json.loads((CAP/'release/capture-policy.json').read_text());policy.update(mode='PREPARATION_ONLY',planId=batch,scope=sp['sha256'],evidenceRoot=str(output),entrySha256=entry['sha256'],independentCaptureReview=CAPTURE_REVIEW,releaseBindingDigest=base['sha256'],executionAuthorization=None,executionPins=[dict(path=(R/p['path']).as_posix(),sha256=p['sha256']) for p in [reviews[1],base]])
for slot in policy['slots']:slot['id']=slot['id'].replace('RESUME01_CAPTURE_','RESUME02_')
policyPin=write(B/'release/capture-policy.json',policy)
requests=[]
for slot in policy['slots']:
 requests.append(write(B/'release/metadata-requests'/(slot['id']+'.json'),dict(schema='RESUME01_CAPTURE_REQUEST_V1',id=slot['id'],policySha256=policyPin['sha256'],scope=sp['sha256'],evidenceRoot=str(output),argv=slot['argv'],maxTextBytes=slot['maxTextBytes'],qualificationSeconds=15)))
graph=json.loads((OLD/'release/deployment-command-graph.json').read_text());a=graph['instrumentation'];a[a.index('e13ScopeSha256')+1]=sp['sha256'];graphPin=write(B/'release/deployment-command-graph.json',graph)
pins=[jar,observer,entry,sp,rp,cp,base,policyPin,budgetPin,registryPin,*requests,*reviews,*[{k:r[k] for k in ['path','bytes','sha256']} for r in old['targetApks']],pin(B/'disposition/reviewed-original-disposition.json')]
observerRequests=[]
for role in ['deploy','case']:
 request=json.loads((OLD/'release'/('observer-'+role+'-request.json')).read_text());request.update(id='RESUME02_'+role.upper(),evidenceRoot=str(output),scope=cp['sha256'] if role=='deploy' else sp['sha256'])
 a=request['argv'];a[2]=(R/jar['path']).as_posix()
 if role=='deploy':a[5:9]=[(R/cp['path']).as_posix(),cp['sha256'],(R/rp['path']).as_posix(),rp['sha256']]
 else:a[4:]=[(R/sp['path']).as_posix(),sp['sha256'],scope['methods']]
 # Original observer rejects a null expected digest BEFORE custody/process/root initialization.
 request['pins']=[dict(path=(R/preparation['path']).as_posix(),sha256=None,pendingRole='REAL_DEVICE_EXECUTION_AUTHORIZATION_NOT_ISSUED')]+[dict(path=(R/p['path']).as_posix(),sha256=p['sha256']) for p in pins]
 observerRequests.append(write(B/'release'/('observer-'+role+'-request.pending.json'),request))
draft=write(B/'release/execution-permit.pending.json',dict(kind='UNSIGNED_RESUME02_EXECUTION_PERMIT_DRAFT',state='NOT_ISSUED_NOT_EXECUTABLE',scope=sp,release=rp,config=cp,base=base,capturePolicy=policyPin,captureRequests=requests,observerRequests=observerRequests,preparationAuthority=preparation,executionAuthorization=None,productSourceReview=reviews[0],captureReview=reviews[1],budget=budgetPin,oncePath=config['dispatchRecord'],method=scope['methods'],operations=43,textBytes=3145728,archiveBytes=4194304,globalUnallocatedNotSpendable=409600))
activation=write(B/'release/activation-delta.json',dict(status='REVIEWABLE_PENDING_EXECUTION_AUTHORITY_NO_ACTION_NOW',unchangedBase=[sp,rp,cp,base,budgetPin,registryPin,jar,observer,entry],immutablePreparedDirectory=(B).as_posix(),futureOverlay='New authorized activation directory; never edit this frozen preparation or old packages.',requiredAuthority=dict(issuer='Responsible coordinator after independent mechanical review and fresh exact dispatch decision',mustBind=[base['sha256'],sp['sha256'],rp['sha256'],cp['sha256'],CAPTURE_REVIEW,PRODUCT_REVIEW,budgetPin['sha256']],preparationRecordIsNotAuthority=preparation),orderedChanges=['Issue a real execution authority record in the new overlay referencing this immutable base and exact bounds; do not sign with coder preparation authority.','Copy unchanged capture entry and frozen-metadata-argv reference into overlay tools/reference.','Copy policy data: mode PREPARATION_ONLY -> PRODUCTION; executionAuthorization null -> actual authority SHA; add the exact authority path/SHA to executionPins. Keep this base descriptor SHA, original prepared canonical scope/release/config absolute paths and all SDK argv/caps/root fixed.','Recompute policy SHA and the five metadata request policySha256 fields; argv/root/scope unchanged.','Copy pending Java observer requests into overlay: replace only first pending null pin with actual execution authority path/SHA; update capture policy/request pins to overlay actual files.','Produce a final issued permit and manifest referencing all base+overlay objects; independent final mechanical receipt binds overlay seal outside archive.','Only after actual dispatch and all local gates create this new capture evidenceRoot, then exact M1/deploy/M2/single case.'],noBaseHashCycle=True,noNewScopeOrOnceReusedFromOldRelease=True,executionProofs='Runtime predecessor/deployment completion proofs are not precreated. Physical completion and semantic approvedForNext require separate genuine observations.'))
write(B/'release/candidate-binding.json',dict(candidate='D1-20261020-RESUME02-RELEASE',status='PREPARED_AUTHORIZATION_PENDING',scopeId=batch,productSourceReview=reviews[0],captureReview=reviews[1],base=base,scope=sp,release=rp,config=cp,registryPlan=registryPin,hostJar=jar,observer=observer,captureEntry=entry,capturePolicy=policyPin,captureRequests=requests,observerRequests=observerRequests,targetApks=old['targetApks'],disposition=pin(B/'disposition/reviewed-original-disposition.json'),budget=budgetPin,permitDraft=draft,activationDelta=activation,executionAuthorization=None,devicePermitIssued=False,onceConsumed=False,liveRootCreated=False,hostBuilds=0,androidBuilds=0,independentMechanicalReview='PENDING',T07='NOT_RUN',D1='NOT_PASSED',M0='NOT_STARTED'))
write(B/'evidence/source-inputs.json',dict(oldSeals=seals,capturedReviews=reviews,preparationOnly=True,liveFilesRead=False,sdkCalls=0,hostBuilds=0,androidBuilds=0))
print(json.dumps(dict(status='RESUME02_PREPARED_NO_DEVICE_AUTHORIZATION',scopeId=batch,scope=sp,release=rp,config=cp,base=base,policy=policyPin)))
