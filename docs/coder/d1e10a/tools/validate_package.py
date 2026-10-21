"""Strict READ-ONLY local package/bound-input verification. Never issues scope, IDs or commands."""
import argparse,base64,datetime,hashlib,json,pathlib,re,uuid
B=pathlib.Path(__file__).resolve().parents[1];R=B.parents[2]
class Invalid(ValueError):pass
def need(v,m):
 if not v:raise Invalid(m)
def pairs(items):
 d={}
 for k,v in items:need(k not in d,'DUPLICATE_JSON_KEY');d[k]=v
 return d
def decode(raw):return json.loads(raw,object_pairs_hook=pairs,parse_constant=lambda s:(_ for _ in ()).throw(Invalid('JSON_NONFINITE')))
def digest(raw):return hashlib.sha256(raw).hexdigest()
def data(p,maxbytes=96*1024*1024):
 p=pathlib.Path(p);need(p.is_file() and not p.is_symlink(),'FILE_ROLE:'+str(p));need(p.stat().st_size<=maxbytes,'FILE_BOUND');return p.read_bytes()
def read(p,maxbytes=4*1024*1024):return decode(data(p,maxbytes))
def local(root,name):
 need(isinstance(name,str) and name and not re.search(r'(^|[\\/])\.\.([\\/]|$)',name),'RELATIVE_PATH')
 need(not pathlib.Path(name).is_absolute(),'ABSOLUTE_PIN_PATH');p=root/name;need(p.resolve().is_relative_to(root.resolve()),'PATH_ESCAPE');return p
def pin(row,root=R):
 need(set(row)=={'path','bytes','sha256'},'PIN_SCHEMA');need(type(row['bytes']) is int and 0<=row['bytes']<=96*1024*1024,'PIN_SIZE')
 need(isinstance(row['sha256'],str) and re.fullmatch('[a-f0-9]{64}',row['sha256']),'PIN_HASH')
 p=local(root,row['path']);raw=data(p);need(len(raw)==row['bytes'] and digest(raw)==row['sha256'],'PIN_MISMATCH:'+row['path']);return p
def wire(fields):
 need(type(fields) is dict and 0<len(fields)<=48,'WIRE_SCHEMA')
 for k,v in fields.items():need(isinstance(k,str) and re.fullmatch('[a-z][A-Za-z0-9]{0,31}',k) and isinstance(v,str) and re.fullmatch('[A-Za-z0-9._:/,@+~-]{1,8192}',v),'WIRE_FIELD')
 return ('{"e9":1,"fields":'+json.dumps(fields,sort_keys=True,separators=(',',':'))+'}\n').encode('ascii')
def canonical_bytes(raw,maxbytes):
 need(type(raw) is bytes and len(raw)<=maxbytes,'WIRE_BOUND');d=decode(raw);need(type(d) is dict and set(d)=={'e9','fields'} and type(d['e9']) is int and d['e9']==1,'WIRE_HEADER');need(raw==wire(d['fields']),'WIRE_NONCANONICAL');return d['fields'],raw
def canonical(p,maxbytes):return canonical_bytes(data(p,maxbytes),maxbytes)
def timestamp(value):
 need(type(value) is str,'TIMESTAMP_TYPE');d=datetime.datetime.fromisoformat(value);need(d.tzinfo is not None,'TIMESTAMP_NEEDS_ZONE');return d
def preparation():
 p=read(B/'plan/execution-plan.json');need(p['state']=='PREPARATION_ONLY_NOT_EXECUTABLE' and p['newIdentity'] is None and p['currentDeviceFacts'] is None,'PREMATURE_ACTUAL_IDENTITY')
 need(p['rebuilds']==1 and p['deviceCalls']==0 and not p['activationBuilt'],'PREPARATION_SCOPE')
 f,desc=canonical(B/'plan/descriptor.json',4096);need(len(desc)==725 and digest(desc)=='4a1877713ba2b6763d777e73e9b956914a3b5fefa8c8c35c340f81531e6c2adb' and f['oldCloseACK']=='FALSE','DESCRIPTOR')
 c,raw=canonical(B/'plan/expected-commit.json',256);need(c==dict(kind='commit',descriptor=digest(desc),payload=digest(desc),policy=f['policy']) and len(raw)==244 and p['deviceContentCeiling']==3017,'EXACT_COST')
 prefix=data(B/'reference/accepted-ledger-prefix.bin',1011);need(len(prefix)==1011 and digest(prefix)==f['prefixSha'],'ACCEPTED_PREFIX')
 settled=[dict(task=s[1],state=s[2],bytes=int(s[3]),sha256=s[4],output='files/e4a_outputs/'+s[1]+'.mp4') for line in prefix.decode('ascii').splitlines() if (s:=line.split()) and s[0]=='S'];need(settled==p['legacy']['settledRecords'] and sum(x['bytes'] for x in settled)==107218,'LEGACY_BASELINE')
 profile=data(B/'src/com/videokit/spike/e4/E9LegacyProfile.java').decode('utf-8');metadata=[dict(relative=k,sha256=h,maxBytes=2048) for k,h in re.findall(r'm.put\("([^"]+)","([a-f0-9]{64})"\)',profile)];need(len(metadata)==13 and metadata==p['legacy']['immutableMetadata'],'EXACT_METADATA_INVENTORY')
 need(p['deployment']['candidatePair']==p['artifacts'][:2] and p['deployment']['candidateVersion']==14 and p['deployment']['sourceVersion']==13,'DEPLOYMENT_PLAN')
 t=read(B/'templates/prepare-plan.template.json');need(t['wireFields']['version']=='14' and t['wireFields']['app']==p['artifacts'][0]['sha256'] and t['wireFields']['test']==p['artifacts'][1]['sha256'],'NEW_PAIR_TEMPLATE')
 cfg=read(B/'templates/manager-config.template.json')['wireFields'];need(cfg['originalVersion']=='13' and cfg['originalApp']==p['deployment']['sourcePair'][0]['sha256'] and cfg['originalTest']==p['deployment']['sourcePair'][1]['sha256'],'SOURCE_PAIR_TEMPLATE')
 deploy=read(B/'templates/00-deploy-prepare.template.json')['wireFields'];need(deploy==dict(kind='managerCommand',operation='DEPLOY_PREPARE',app=(R/p['artifacts'][0]['path']).as_posix(),test=(R/p['artifacts'][1]['path']).as_posix()),'DEPLOY_COMMAND_PAIR')
 stop=read(B/'templates/11-bound-stop-before-execute.template.json')['wireFields'];need(stop==dict(kind='managerCommand',operation='CONTROL',command='STOP_DEPENDENCIES') and len(list((B/'templates').glob('[0-9][0-9]-*.template.json')))==12,'CONDITIONAL_STOP_TEMPLATE')
 for path in (B/'templates').glob('*.template.json'):
  d=read(path)
  if path.name=='scope.template.json':need(d['status']=='DRAFT_NOT_EFFECTIVE' and all(d[k] is None for k in ['registry','migration','attempt','handle','issuedAt','executionDispatchEvidence','acceptedE10AReviewSha256']) and d['artifactPins']==p['artifacts'] and d['sourceInstalledPair']==p['deployment']['sourcePair'],'DRAFT_SCOPE')
  else:need(d['templateOnly'] and d['notForProductionCli'],'TEMPLATE_ROLE');wire(d['wireFields'])
 inputs=read(B/'plan/external-input-pins.json')
 for x in inputs['files']:pin(x)
 verified=[]
 for x in inputs['oldSeals']:
  seal=read(pin(x))
  for item in seal['immutableFiles']:pin(item)
  verified.append(dict(path=x['path'],immutable=len(seal['immutableFiles'])))
 manifest=read(pin(inputs['readonlyDeviceManifest']));root=local(R,inputs['readonlyEvidenceRoot'])
 for x in manifest['files']:pin(x,root)
 return dict(status='PASS_PREPARATION_ONLY_NOT_EXECUTABLE',executionReadiness='PENDING_INDEPENDENT_REVIEW_NOT_AUTHORIZED',oldSeals=verified,historicalDeviceEvidenceVerified=len(manifest['files']),externalInputs=len(inputs['files']),actualNewIdentities=0,scopeIssued=False,deviceCalls=0,mutations=0)
def identity(ids,old):
 need(set(ids)=={'registry','migration','attempt','handle'},'NEW_ID_SCHEMA');need(len(set(ids.values()))==4,'ID_COLLISION')
 for k,s in ids.items():
  need(isinstance(s,str) and str(uuid.UUID(s))==s and s!='00000000-0000-0000-0000-000000000000','NEW_UUID_CANONICAL')
  need(s not in [old[n] for n in ['registry','migration','attempt','handle']],'READONLY_ID_REUSE')
def bound(folder):
 folder=folder.resolve();need(folder.is_relative_to((R/'docs/tester/D1_E10A_EXECUTION').resolve()),'BOUND_FOLDER_ROLE')
 expected=read(B/'plan/execution-plan.json');scopepath=folder/'scope.json';scope=read(scopepath);need(scope['kind']=='E10A_EXACT_ACTOR1_MIGRATION_SCOPE' and scope['status']=='ISSUED_FOR_EXACT_ACTOR1','UNISSUED_SCOPE')
 need(scope['issuerRole']=='PROJECT_COORDINATOR' and scope['issuerThread']=='01a107c3-2bf9-7fa0-94a0-234258ca6774' and scope['issuedAt'],'SCOPE_ISSUER')
 pin(scope['executionDispatchEvidence']);review=pin(scope['acceptedE10AReviewEvidence']);need(scope['acceptedE10AReviewSha256']==digest(data(review)),'E10A_REVIEW_PIN')
 ids={k:scope[k] for k in ['registry','migration','attempt','handle']};identity(ids,expected['historicalReadOnly'])
 need(scope['actorOrdinal']==1 and scope['mode']=='REGISTERED_MIGRATION' and scope['artifactPins']==expected['artifacts'],'SCOPE_PAIR_ACTOR')
 need(scope['serial']=='HA1Q6WXR' and type(scope['user']) is int and scope['user']==0,'SCOPE_DEVICE')
 template=read(B/'templates/scope.template.json');need(set(scope)==set(template)|{'acceptedE10AReviewEvidence'},'SCOPE_EXACT_SCHEMA');need(scope['prohibitions']==template['prohibitions'],'SCOPE_PROHIBITIONS')
 need(scope['authoritySourceReferences']==template['authoritySourceReferences'] and scope['authorityMeaning']==template['authorityMeaning'],'SCOPE_AUTHORITY_MEANING')
 for key in ['policy','descriptorSha256','deviceFileLimit','deviceContentCeiling','deviceDirectoriesCeiling','pcQueriesLimit','androidControlsLimit','androidStatusesLimit','independentMetadataClientLimit','pcProcessLimit','candidateVersion','sourceInstalledPair','cleanupPolicy']:need(scope[key]==template[key],'SCOPE_LIMIT:'+key)
 plan,praw=canonical(folder/'prepare-plan.json',8192);want=dict(read(B/'templates/prepare-plan.template.json')['wireFields']);want.update(registry=ids['registry'],migration=ids['migration'],authorization=digest(data(scopepath)),sourceReview=scope['acceptedE10AReviewSha256']);need(plan==want,'PLAN_BINDINGS')
 config,craw=canonical(folder/'manager-config.json',24576);want=dict(read(B/'templates/manager-config.template.json')['wireFields']);target=(folder.parent/'registry').as_posix();want.update(plan=base64.urlsafe_b64encode(praw).decode().rstrip('='),planSha=digest(praw),authorization=plan['authorization'],review=plan['sourceReview'],registryPath=target);need(config==want,'CONFIG_BINDINGS')
 need(not pathlib.Path(target).exists(),'REGISTRY_MUST_BE_NEW')
 for path in sorted((B/'templates').glob('[0-9][0-9]-*.template.json')):
  want=dict(read(path)['wireFields'])
  if want['operation']=='LAUNCH':want.update(attempt=ids['attempt'],handle=ids['handle'])
  actual,_=canonical(folder/'commands'/path.name.replace('.template.json','.json'),8192);need(actual==want,'COMMAND_BINDING:'+path.name)
 pre=read(folder/'preflight.json');need(pre['status']=='COMPLETE_CONTEXT_REVALIDATED' and pre['sessionRegistry']==ids['registry'],'FRESH_PREFLIGHT_SCOPE')
 need(timestamp(pre['observedAt'])>=timestamp(scope['issuedAt']),'PREFLIGHT_PREDATES_SCOPE')
 for k in ['legacyArchiveMatched','ledgerPrefixMatched','ledgerChainValid','baselineRecordsPreserved','pendingAbsent','migrationTargetAbsent','externalRegistryAbsent','metadataOriginalResourcesReturned','noUnknown']:need(pre[k] is True,'PREFLIGHT_GATE:'+k)
 for key in ['oldOutputBytes','reserved','consumed','user','appUid','testUid','version','abi']:need(type(pre[key]) is int,'PREFLIGHT_INTEGER:'+key)
 need(pre['relatedProcessPids']==[] and pre['oldOutputBytes']==0 and pre['reserved']==0 and 107218<=pre['consumed']<=4194304,'PREFLIGHT_ACCOUNTING')
 need(pre['installedPair']==expected['deployment']['sourcePair'] and pre['serial']=='HA1Q6WXR' and pre['user']==0 and pre['appUid']==10221 and pre['testUid']==10222 and pre['version']==expected['deployment']['sourceVersion'] and pre['role']=='PREPARE' and pre['abi']==1,'PREFLIGHT_INSTALLED_PAIR')
 need(pre['ownerId']==expected['legacy']['ownerId'] and pre['leaseId']==expected['legacy']['leaseId'] and pre['fence']==expected['legacy']['fence'],'PREFLIGHT_GUARD_IDENTITIES')
 need(isinstance(pre['rawEvidence'],list) and pre['rawEvidence'],'PREFLIGHT_RAW_RECEIPTS')
 for x in pre['rawEvidence']:pin(x)
 index=read(folder/'input-index.json');need(index['scopeSha256']==plan['authorization'],'INPUT_INDEX_SCOPE')
 required=[scopepath,folder/'prepare-plan.json',folder/'manager-config.json',folder/'preflight.json']+sorted((folder/'commands').glob('*.json'))
 need({x['path'] for x in index['files']}=={x.relative_to(R).as_posix() for x in required},'INPUT_INDEX_INVENTORY')
 for x in index['files']:pin(x)
 return dict(status='PASS_BOUND_STATIC_BINDINGS_NOT_DEVICE_AUTHORITY',executionReadiness='PENDING_INDEPENDENT_REVIEW_NOT_AUTHORIZED',configSha256=digest(craw),mutations=0,deviceCalls=0,qualification='Independent repaired implementation/package acceptance and formal dispatch still required. Trusted issuer/collector provenance and actual fresh现场 must be independently accepted; receipt assertions cannot replace production guard/original return gates')
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--bound-dir',type=pathlib.Path);args=a.parse_args()
 try:
  result=preparation()
  if args.bound_dir:result=bound(args.bound_dir)
  print(json.dumps(result,ensure_ascii=False,sort_keys=True))
 except (ValueError,KeyError,TypeError,OSError,AssertionError) as e:print(json.dumps(dict(status='REJECTED',reason=str(e),deviceCalls=0,mutations=0)));raise SystemExit(1)
