"""Prepare immutable authorized inputs only. No process/device dispatch or once creation."""
from pathlib import Path
import hashlib,json,uuid
from datetime import datetime,timezone
R=Path(__file__).resolve().parents[2]
def sha(b):return hashlib.sha256(b).hexdigest()
def pin(p):return dict(path=p.relative_to(R).as_posix(),bytes=p.stat().st_size,sha256=sha(p.read_bytes()))
def jsbytes(x):return (json.dumps(x,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
def record(fields):return ('{"e9":1,"fields":'+json.dumps(dict(sorted(fields.items())),ensure_ascii=True,separators=(',',':'))+'}\n').encode('ascii')
batch=str(uuid.uuid4());base=R/'docs/tester/D1_E13A_E13B_TABLET_EXECUTION'/batch
for d in ['inputs','evidence','deployment','harness']:(base/d).mkdir(parents=True,exist_ok=False)
def write(name,value):
    raw=value if isinstance(value,bytes) else jsbytes(value)
    with (base/name).open('xb') as f:f.write(raw)
    return pin(base/name)
now=datetime.now(timezone.utc).isoformat();requirements=R/'docs/milestones/D1_E13A_E13B_TABLET_TESTER_REQUIREMENTS_V1.0.md'
human=R/'docs/tester/D1_E11_DEVICE_AUTHORITY_20261018.json'
authority=write('inputs/authority.json',dict(status='COORDINATOR_FORMAL_DISPATCH_WITH_STANDING_HUMAN_DEVICE_AUTHORITY',atUtc=now,coordinatorThread='01a107c3-2bf9-7fa0-94a0-234258ca6774',humanDirectQuote='以后使用平板测试，不需再重复授权，你可以直接使用。',standingAuthority=pin(human),requirements=pin(requirements),dispatch='E13A+E13B_OVERLAY六方法正式平板批次；总50=原成功路径48+至多两次正常半小时M1占用复查，文本2MiB不变；不抢其他项目设备，不重试产品失败或安装。',authorizationNotReasked=True))
overlay=R/'docs/coder/d1e13b';product=R/'docs/coder/d1e13a'
reuse=json.loads((overlay/'release/overlay-binding.json').read_text())
for a in reuse['baseArtifacts']:assert pin(R/a['path'])['sha256']==a['sha256']
reviews=[R/'docs/tester/D1_E13A_ARCHITECTURE_REVIEW_REPORT_V1.0.md',R/'docs/tester/D1_E13B_METADATA_REVIEW_REPORT_V1.0.md']
assert pin(reviews[1])['sha256']=='b3f19c478dbae2218b0b776b6f85463d43c1df70c4e6baccdb1a2d63fc51c876'
meta=json.loads((overlay/'release/metadata/three-client-manifest.json').read_text())
old=R/'docs/tester/D1_E11_FINAL_R1_TABLET_EXECUTION/a129ad0a-9d93-49c6-8289-9087afd419ff/inputs/activation-trust-deploy.json'
trust=json.loads(old.read_text())['fields'];art={a.get('kind','jar'):a for a in reuse['baseArtifacts']}
methods=['ordinarySenderCannotBindCodec','authorizedHostSourceReadAndClose','oldGenerationNeverOpensSource','twoConsumersHoldSourceUntilLastReturn','cancelLateOpenRetainsOriginalOwner','lateReadAndCloseFailureDoNotReleaseEarly']
scopefields=dict(kind='e13DispatchScope',batch='D1-E13A-SOURCE-20261018',scopeId=batch,sourceAcceptance='60eb18e88e346e49ec34491083f2b67da21670d7cd5fde40ce3b72ba8246b635',sourceApp='2f323c16e896b0535e80cccce05bbcf3051224f0add279a51392312083e89f48',sourceTest='e644dce77be6ccb0e7f99d82f2479fc92238aad682bb022bb95835fc015d0bfb',app=art['app']['sha256'],test=art['test']['sha256'],fixture=art['fixture']['sha256'],fixtureSigner=art['fixture']['signer'],sourceReview=pin(reviews[1])['sha256'],methods=','.join(sorted(methods)),budget='source4096/read65536/open8/close16/process48/text2097152/output0')
runtimeScope=write('inputs/runtime-scope.json',record(scopefields))
once=base/'deployment/e13a-activation-deployment.once';assert not once.exists()
release=write('inputs/activation-release.json',record(dict(kind='activationRelease',head=trust['head'],catalog='27fe90573f2d8a3a750c270e760f4e19e797fe188287ade5c58268e8c6d911b7',app=art['app']['sha256'],test=art['test']['sha256'],signer=art['app']['signer'],role='ACTIVATION',abi='1',version='17',sourceReview=pin(reviews[1])['sha256'],environment='DEVICE_HA1Q6WXR',sourceAcceptance=scopefields['sourceAcceptance'],scope=runtimeScope['sha256'])))
config=write('inputs/activation-trust-deploy.json',record(dict(kind='e13ActivationTrust',plan=trust['plan'],planSha=trust['planSha'],authorization=trust['authorization'],review=trust['review'],registryPath=trust['registryPath'],head=trust['head'],dispatchRecord=once.as_posix(),scopePath=(base/'inputs/runtime-scope.json').as_posix(),scopeSha=runtimeScope['sha256'])))
eScope=write('inputs/execution-scope.json',dict(schema=1,batchId=batch,atUtc=now,authority=authority,requirements=pin(requirements),reviews=[pin(p) for p in reviews],productSeal=pin(product/'evidence/e13a-freeze.json'),overlaySeal=pin(overlay/'evidence/e13b-freeze.json'),overlayArchive=pin(R/'docs/coder/D1-20261018-E13B-metadata.zip'),metadataManifest=pin(overlay/'release/metadata/three-client-manifest.json'),metadataArgv=[pin(overlay/'release/metadata'/(m['id']+'.argv.json')) for m in meta['clients']],artifacts=reuse['baseArtifacts'],runtimeScope=runtimeScope,release=release,config=config,oncePath=once.as_posix(),onceCreatedByPreparation=False,methods=methods,device='HA1Q6WXR',user=0,productVersion=17,sourceVersion=15,maxOriginalOperations=50,successfulPathOperations=48,extraM1OccupancyReviews=2,extraM1CadenceMinutes=30,maxTextBytes=2097152,remainingTextAfterTwoExtraM1=327680,extraControlConnections=0,hostReadonlyCompatibilityCorrections=2,source=dict(fixtureBytes=4096,preparedTotalBytes=20480,plannedOpen=6,plannedReadBytes=4224,plannedClose=7,maxOpen=8,maxReadBytes=65536,maxClose=16,perOriginalTicketMaxAttempts=3,bridgeAwaitMillis=5000,caseQualificationSeconds=30),mediaOutputBytes=0,newR=0,newS=0,legacy=dict(ledgerBytes=2271,ledgerSha256='e7d6441ca5bdb050fa8f584152f64da5e6009e4d751ac610f33e42797710b649',consumed=214483,recordsR=7,recordsS=7,reserved=0),historicalTrustExplanation='Historical prepare plan/authorization/review are read-only registry provenance; this authority.json and reviewed release/runtime scope govern the new execution, not the old migration approval.',state='WAIT_CONTROLLER_EXCLUSIVITY_BEFORE_M1'))
write('inputs/input-index.json',dict(executionScope=eScope,authority=authority,runtimeScope=runtimeScope,release=release,config=config))
write('evidence/resource-ledger.json',dict(state='WAIT_CONTROLLER_EXCLUSIVITY_BEFORE_M1',deviceOperationsStarted=0,productOperationsStarted=0,metadataClientsStarted=0,pcControlConnections=0,actualTextBytes=0,pcOperationLimit=50,textLimit=2097152,onceExists=False,cases={m:'NOT_RUN' for m in methods}))
print(json.dumps(dict(batchId=batch,root=base.as_posix(),scope=eScope,runtimeScope=runtimeScope,config=config,release=release),ensure_ascii=False))
