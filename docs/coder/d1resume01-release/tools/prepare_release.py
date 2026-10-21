"""One offline material-binding pass. Reads sealed sources and coder snapshots only, never live registry/custody."""
from pathlib import Path
import json,hashlib,shutil,uuid,base64,zipfile
B=Path(__file__).resolve().parents[1];R=B.parents[2];A=R/'docs/coder/d1resume01';F=R/'docs/coder/d1e13f';E11=R/'docs/coder/d1e11'
REVIEW='0bad8b95ac7e0308713fdfed2f21c9215d18606f86aaa8e4e1dbd09059640743'
def pin(p):b=p.read_bytes();return dict(path=p.relative_to(R).as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def check(row):assert pin(R/row['path'])=={k:row[k] for k in ['path','bytes','sha256']},row['path']
def write(p,o):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def copy(p,q):q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,q);return pin(q)
def canonical(p,fields):p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(('{"e9":1,"fields":'+json.dumps(dict(sorted(fields.items())),separators=(',',':'))+'}\n').encode('ascii'));return pin(p)
def fields(p):return json.loads(p.read_text(encoding='ascii'))['fields']
assert not (B/'release/candidate-binding.json').exists(),'Already prepared'
prior=A/'evidence/resume01-freeze.json';assert pin(prior)['sha256']=='1673bca8580d7cba82cc3a518e5a9f888d25e52fb42f83beb2dec2c5b519f661'
seal=json.loads(prior.read_text())
for row in seal['immutableFiles']:check(row)
review=R/'docs/tester/D1_RESUME01_STATIC_REVIEW_REPORT_V1.0.md';assert pin(review)['sha256']==REVIEW
copy(review,B/'reference'/review.name);copy(prior,B/'reference/resume01-freeze.json')
inputs=[]
for row in json.loads((A/'evidence/source-derivation.json').read_text()):
 source=R/row['current'];target=B/source.relative_to(A);inputs.append(dict(source=pin(source),current=copy(source,target)))
old=json.loads((A/'release/candidate-binding.json').read_text());jar=copy(R/old['hostJar']['path'],B/'artifacts/resume01-release-host-tools.jar');observer=copy(R/old['observer']['path'],B/'tools/observe_original.ps1')
for p in sorted((A/'disposition').glob('*')):copy(p,B/'disposition'/p.name)
for name in ['metadata-argv-plan.json','exact-budget.json']:copy(A/'release'/name,B/'reference'/name)
copy(A/'evidence/build-001/host-jar-manifest.json',B/'reference/prior-host-jar-manifest.json')
copy(A/'evidence/build-001/deployment-command-trace.json',B/'reference/prior-scripted-deployment-trace.json')
write(B/'evidence/source-identity.json',dict(productionSources=inputs,changedSources=0,hostBuilds=0,androidBuilds=0,reason='No source or policy constant changes; sourceReview is a canonical scope/release field.',jar=jar,originalJar=old['hostJar'],observer=observer,originalObserver=old['observer']))
members=[]
with zipfile.ZipFile(R/old['hostJar']['path']) as previous,zipfile.ZipFile(R/jar['path']) as current:
 assert previous.namelist()==current.namelist() and len(current.namelist())==183
 for name in current.namelist():
  raw=current.read(name);assert raw==previous.read(name);members.append(dict(entry=name,bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),difference='BYTE_IDENTICAL'))
write(B/'evidence/member-equivalence.json',dict(status='PASS_183_MEMBERS_IDENTICAL',members=members,recompiled=False))
# The original real registry is NOT opened. Bind its historical coder snapshot instead.
before=E11/'evidence/original-registry-before-export.json';inventory=json.loads(before.read_text());copy(before,B/'reference/original-registry-before-export.json')
frozen=E11/'source-export/accepted-registry-snapshot';registryRows=[]
for row in inventory['files']:
 rel=Path(row['path']).relative_to(Path(inventory['root']));p=frozen/rel;raw=p.read_bytes();assert len(raw)==row['bytes'] and hashlib.sha256(raw).hexdigest()==row['sha256']
 registryRows.append(dict(relative=rel.as_posix(),expectedActual=row,snapshot=copy(p,B/'reference/accepted-registry-snapshot'/rel)))
trustSource=E11/'source-export/activation-trust.json';trust=fields(trustSource);copy(trustSource,B/'reference/original-activation-trust.json')
catalog=fields(frozen/'final.acceptance.json');assert catalog['head']==trust['head']
e11Seal=E11/'revision-r1/evidence/e11-final-freeze.json';fseal=json.loads((F/'evidence/e13f-freeze.json').read_text());anchor=next(x['seal'] for x in fseal['priorSeals'] if x['seal']['path']==e11Seal.relative_to(R).as_posix());check(anchor)
finalRows=json.loads(e11Seal.read_text())['immutableFiles'];originalSeal=E11/'evidence/e11-freeze.json';originalAnchor=next(r for r in finalRows if r['path']==originalSeal.relative_to(R).as_posix());check(originalAnchor)
e11Rows=json.loads(originalSeal.read_text())['immutableFiles'];needed={before.relative_to(R).as_posix(),trustSource.relative_to(R).as_posix(),*[p.relative_to(R).as_posix() for p in frozen.rglob('*') if p.is_file()]}
anchored={r['path']:r for r in e11Rows if r['path'] in needed};assert set(anchored)==needed
for row in anchored.values():check(row)
copy(e11Seal,B/'reference/e11-final-freeze.json');copy(originalSeal,B/'reference/e11-freeze.json')
write(B/'evidence/registry-provenance.json',dict(anchor=anchor,originalSeal=originalAnchor,anchoredRows=list(anchored.values()),sourceSnapshotOnly=True,liveRegistryRead=False))
write(B/'release/dispatch-authorization.json',dict(kind='CAPTURED_COORDINATOR_RESUME01_RELEASE_DELEGATION',sourceThread='01a107c3-2bf9-7fa0-94a0-234258ca6774',date='2026-10-20',sourceReview=pin(review),acceptedBudget=dict(operations=43,textBytes=3145728,archiveBytes=4194304,unallocatedNotSpendable=409600),instruction='RESUME01独立静态PASS；负责人接受候选及明确新预算；正式派RESUME01_RELEASE一次整批机械绑定；完整冻结后tester独立机械核验，PASS可按负责人同批授权执行M1→无占用且全门通过后部署→M2→仅ordinarySenderCannotBindCodec，首失败/UNKNOWN停止不其余五法；coder不设备/SDK/现场读。',mechanicalReviewRequired=True,freshM1AndZeroOtherProjectOccupancyRequired=True,oldUnknownOrOnceRefunded=False,claimWaiver=False))
auth=pin(B/'release/dispatch-authorization.json');budget=json.loads((A/'release/exact-budget.json').read_text());budget.update(status='ACCEPTED_BY_COORDINATOR_CONDITIONAL_EXECUTION_AFTER_MECHANICAL_PASS',sourceProposal=old['budget'],acceptance=auth)
write(B/'release/exact-budget.json',budget)
batch=str(uuid.uuid4());execution=R/'docs/tester/D1_RESUME01_RELEASE_EXECUTION'/batch
scope=fields(A/'release/templates/scope.template.json');scope.update(scopeId=batch,sourceReview=REVIEW)
sp=canonical(B/'release/runtime-scope.json',scope)
release=fields(A/'release/templates/activation-release.template.json');release.update(head=trust['head'],catalog=pin(frozen/'final.acceptance.json')['sha256'],sourceReview=REVIEW,scope=sp['sha256'])
rp=canonical(B/'release/activation-release.json',release)
config=dict(kind='e13ActivationTrust',plan=trust['plan'],planSha=trust['planSha'],authorization=trust['authorization'],review=trust['review'],registryPath=trust['registryPath'],head=trust['head'],dispatchRecord=(execution/'e13f-lifecycle-deployment.once').as_posix(),scopePath=(R/sp['path']).as_posix(),scopeSha=sp['sha256'])
cp=canonical(B/'release/activation-trust-deploy.json',config)
write(B/'release/registry-plan.json',dict(actualRoot=trust['registryPath'],mode='REUSE_ORIGINAL_REVIEWED_REAL_REGISTRY_NO_COPY_SUBSTITUTE',registryId=catalog['registry'],migrationId=catalog['migration'],head=trust['head'],catalogSha256=release['catalog'],planSha256=trust['planSha'],registryAuthorization=trust['authorization'],registryReview=trust['review'],currentSourceReview=REVIEW,expectedFiles=registryRows,currentState='NOT_READ_BY_CODER; tester must compare exact inventory/bytes and requireDeploymentQuiet before deployment',noRegistryReinitialization=True))
metadata=json.loads((A/'release/metadata-argv-plan.json').read_text());metadata.update(status='BOUND_REQUESTS_CONDITIONAL_ON_MECHANICAL_PASS_AND_LOCAL_ADMISSION',executionBatch=batch,scopeSha256=sp['sha256'])
for item in metadata['commands']:
 item['id']='RESUME01_RELEASE_'+item['id'].replace('-','_');item.update(executionBatch=batch,scope=sp['sha256'],evidenceRoot=str(execution/'outputs'),qualificationSeconds=15,actualReadAccounting='Count every successful original stdout/stderr read, including chunks exceeding save/qualification cap; bytes not captured must not become zero.',onOverflow='FAILED_OVERLIMIT_NO_DEPENDENT_OPERATION; retain original owner, charge actual known raw reads and duplicated output; UNKNOWN amount retains entire category without refund.',allowedRetries=0)
write(B/'release/metadata-requests.json',metadata)
java='D:/Android/Android Studio/jbr/bin/java.exe';jarPath=(R/jar['path']).as_posix();apks=[(R/row['path']).as_posix() for row in old['targetApks']]
deploy=[java,'-cp',jarPath,'com.videokit.spike.e4.E13HostActivationSession','--approved-e13-deploy',(R/cp['path']).as_posix(),cp['sha256'],(R/rp['path']).as_posix(),rp['sha256'],*apks]
case=[java,'-cp',jarPath,'com.videokit.spike.e4.E13HostCase',(R/sp['path']).as_posix(),sp['sha256'],'ordinarySenderCannotBindCodec']
instrument=['D:/Android/SDK/platform-tools/adb.exe','-s','HA1Q6WXR','shell','am','instrument','-w','-r','-e','class','com.videokit.spike.e4.E13DeviceTests#ordinarySenderCannotBindCodec','-e','e13Case','ordinarySenderCannotBindCodec','-e','e13Batch',scope['batch'],'-e','e13ScopeSha256',sp['sha256'],'com.videokit.app.test/com.videokit.spike.e4.E13Instrumentation']
pins=[jar,observer,sp,rp,cp,pin(B/'release/exact-budget.json'),pin(B/'disposition/reviewed-original-disposition.json'),pin(review),auth,*[{k:r[k] for k in ['path','bytes','sha256']} for r in old['targetApks']]]
for role,argv,cap,scopeSha in [('deploy',deploy,81920,cp['sha256']),('case',case,32768,sp['sha256'])]:
 write(B/'release'/('observer-'+role+'-request.json'),dict(id='RESUME01_RELEASE_'+role.upper(),evidenceRoot=str(execution/'outputs'),scope=scopeSha,argv=argv,maxTextBytes=cap,pins=[dict(path=(R/p['path']).as_posix(),sha256=p['sha256']) for p in pins]))
trace=json.loads((A/'evidence/build-001/deployment-command-trace.json').read_text())['children'];expanded=[];pathProducer={};groups=[(1,2,'preData'),(3,7,'artifacts'),(8,14,'preInstalled'),(15,16,'pairInstall'),(17,23,'postInstalled'),(24,25,'postData'),(26,35,'fixture')]
for row in trace:
 argv=row['argv'];n=row['operation'];runtime=[]
 for i,value in enumerate(argv):
  if value.endswith('fake-app.apk'):argv[i]=apks[0]
  elif value.endswith('fake-test.apk'):argv[i]=apks[1]
  elif value.endswith('fake-fixture.apk'):argv[i]=apks[2]
 if 'path' in argv and 'pm' in argv:pathProducer[argv[-1]]=n
 if 'sha256sum' in argv:
  package=argv[-1].split('/')[3];producer=pathProducer[package];runtime.append(dict(argumentIndex=len(argv)-1,fromOperation=producer,stdoutParser='Exactly one ^package:([/A-Za-z0-9_.=+~-]+/base[.]apk) line, path starts /data/app/, no duplicate.',samePackage=package));argv[-1]='RESPONSE_OP_'+str(producer)+'_EXACT_VALIDATED_BASE_APK_PATH'
 expanded.append(dict(operation=n,group=next(g for lo,hi,g in groups if lo<=n<=hi),argv=argv,runtimeArguments=runtime,individualQualificationMax=row['maxBytes'],aggregateSdkRawOutputReserve=524288,originalResponseQualifierSeconds=55,derivedFromRealProductionPortScriptedTrace=True,actualExecution=False))
assert len(expanded)==35
write(B/'release/deployment-command-graph.json',dict(status='EXACT_SOURCE_EXPANSION_WITH_CORRELATED_RESPONSE_ARGUMENTS',operations=expanded,noLiteralScriptedRemotePathPermitted=True,actualResolvedArgvRecordedByOriginalArchiveBeforeChild=True,instrumentation=instrument,children35=True))
capture=A/'reference/D1_TABLET_CLOSEOUT_CONT_EVIDENCE/recorded-standard-client-capture-command.txt';capturePin=copy(capture,B/'reference/recorded-standard-client-capture-command.txt')
write(B/'release/admission-and-accounting.json',dict(scope=sp,release=rp,config=cp,registryPlan=pin(B/'release/registry-plan.json'),standardMetadataCaptureReference=capturePin,sourceReview=pin(review),mechanicalReview='Required independent receipt bound externally to final seal; not fabricated in this package.',localPreflight=['Pin all inputs and original tool bytes before starting a client; ADB mismatch stops without restarting server.','Match original accepted registry inventory and exact bytes; do not initialize/copy-replace live registry.','Reconcile ledger, administrative A/K and independent B/H; do not refund old UNKNOWN.','Inspect fixed guard root once under authorization; <=32 exact claims, no symlinks; any unresolved claim stops with specific identity, no deletion/reset/admin waiver.','New deployment once path must not exist. Existing root disposition must match exact approved bytes, or be absent until post-M1 CREATE_NEW installation.'],expectedM1=dict(serial='HA1Q6WXR',model='TB138FC',api=31,user=0,appVersion=17,fixtureVersion=1,appSha256=scope['sourceApp'],testSha256=scope['sourceTest'],fixtureSha256='868f581538d4a92908870d9066d5dfce18d847a5d9559e827e24cbb3ca3544d8',appSigner=old['targetApks'][0]['signer'],fixtureSigner=scope['fixtureSigner'],uids=[10221,10222,10228],data=['10221:6972','10222:4741'],fixtureData='Capture fresh complete UID:inode and require unchanged in M2.'),expectedM2=dict(appVersion=19,fixtureVersion=3,appSha256=scope['app'],testSha256=scope['test'],fixtureSha256=scope['fixture'],uids=[10221,10222,10228],data=['10221:6972','10222:4741'],fixtureData='Exactly equal fresh M1 identity.'),occupancy='Full activity-process and ps records; no other project live tasks or unknown ownership. Absence of instrumentation alone insufficient. If occupied, stop this scope without automatic retry.',dispositionInstallation='Only after all M1 gates: CREATE_NEW approved exact bytes in fixed root if absent, read back and verify original close. Existing equal bytes reuse; mismatch stops, never overwrite. Do not alter any claim/pointer/return marker.',deploymentOnce=config['dispatchRecord'],caseOnce=dict(type='EXISTING_SCOPE_METHOD_CLAIM',scopeSha256=sp['sha256'],method=scope['methods'],persistentRoot='D:/CodexProjects/VideoKit/docs/tester/VideoKit-device-custody/HA1Q6WXR',reentryEvenAfterReturn='REJECTED'),rawCapsArePhysicalHardBounds=False,counting='All original successful raw reads are charged even if over cap or not saved; duplicated forwarding/records charged separately. Unknown exact original read count is UNKNOWN, not cap or savedBytes; entire category remains reserved.',overflow='Stop all subsequent admission, preserve original owner and first failure; any actual overrun remains explicitly charged, never borrow the unallocated409600B.',internalSdkReaderOverflow='If frozen PC/archive does not expose exact overshoot count, record actual UNKNOWN / above qualifier with full category retained; no dependent work or fabricated precise amount.',controlReserve=budget['recordReserves'],metadataControlReserve=786432,unallocatedNotSpendable=409600,externalCallsBeyondPlan='NOT_AUTHORIZED; no process/handle/status polling, retry, termination or later five methods.'))
accountingPath=B/'release/admission-and-accounting.json';accounting=json.loads(accountingPath.read_text());accounting.update(toolCompatibility=dict(adbSha256='b4a6b455702684652cccf7b46258b29e653538904359a58fd4931cf3ef286b3f',beforeAnyClient='One local existing-listener/source check using existing host APIs, not an extra ADB version/start/query. Require existing 127.0.0.1:5037 listener executable D:/Android/SDK/platform-tools/adb.exe, exact approved on-disk hash, unchanged file predating the current server creation; unresolved provenance blocks.',noHistoricalPidReuse=True,environment='Require default local5037 routing; ADB_SERVER_SOCKET, ANDROID_ADB_SERVER_PORT, ADB_SERVER_PORT must not redirect. Unexplained override blocks.',serverAbsentOrMismatch='STOP_NO_START_NO_RESTART_NO_NEW_PROTOCOL'),controlAllocation='releaseAndScopeRecords 6x8192: scope, release, config, permit, dispatch authorization, and one bounded local preflight receipt. No new operation allowance. Static artifact/input reads are not newly generated process output. All new records/console/forwarding are charged.',operationDefinition='43 approved dispatch work units in the accepted groups; controller context does not authorize extra SDK/Java children. Record actual controller/child identities and text overhead without claiming 43 is a count of every OS-created Android/system process.')
write(accountingPath,accounting)
permit=canonical(B/'release/one-shot-permit.json',dict(kind='resume01ReleasePermit',scopeId=batch,scope=sp['sha256'],release=rp['sha256'],config=cp['sha256'],sourceReview=REVIEW,authorization=auth['sha256'],jar=jar['sha256'],observer=observer['sha256'],disposition=old['disposition']['sha256'],budget=pin(B/'release/exact-budget.json')['sha256'],registryPlan=pin(B/'release/registry-plan.json')['sha256'],method=scope['methods'],operations='43',textBytes='3145728',archiveBytes='4194304',unallocatedNotSpendable='409600',precondition='INDEPENDENT_MECHANICAL_PASS_AND_FRESH_M1_ALL_GATES',state='ISSUED_NOT_CONSUMED'))
write(B/'release/candidate-binding.json',dict(candidate='D1-20261020-RESUME01-RELEASE',status='FROZEN_MATERIALS_FOR_INDEPENDENT_MECHANICAL_REVIEW',executionBatch=batch,sourceCandidate='D1-20261020-RESUME01',sourceReview=pin(review),hostJar=jar,observer=observer,targetApks=old['targetApks'],disposition=pin(B/'disposition/reviewed-original-disposition.json'),scope=sp,release=rp,config=cp,permit=permit,budget=pin(B/'release/exact-budget.json'),registryPlan=pin(B/'release/registry-plan.json'),deploymentOncePath=config['dispatchRecord'],caseOnce='PERSISTENT_SCOPE_METHOD_CLAIM',onceConsumed=False,liveRecordsCreated=False,hostBuilds=0,androidBuilds=0,mechanicalReview='PENDING_INDEPENDENT_RECEIPT',T07='NOT_RUN',D1='NOT_PASSED',M0='NOT_STARTED'))
print(json.dumps(dict(status='RELEASE_BOUND_NO_BUILD_OR_DEVICE',batch=batch,scope=sp,release=rp,config=cp,permit=permit)))
