"""Tester evidence controller for expressly authorized E10A single actor1. No kill/retry."""
import base64,datetime,hashlib,json,pathlib,queue,re,subprocess,sys,threading,time,uuid,os,shlex
ROOT=pathlib.Path(__file__).resolve().parents[2]
B=ROOT/'docs/coder/d1e10a'
STATE=ROOT/'docs/tester/D1_E10A_CURRENT_EXECUTION.json'
ADB='D:/Android/SDK/platform-tools/adb.exe';SERIAL='HA1Q6WXR'
JAVA='D:/Android/Android Studio/jbr/bin/java.exe'
REUSE=False
def now():return datetime.datetime.now().astimezone().isoformat()
def sha(b):return hashlib.sha256(b).hexdigest()
def need(x,m):
 if not x:raise RuntimeError(m)
def read(p):return json.loads(pathlib.Path(p).read_text('utf-8-sig'))
def write(p,v):
 p=pathlib.Path(p);p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x',encoding='utf-8',newline='\n') as f:f.write(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def raw(p,b):
 with pathlib.Path(p).open('xb') as f:f.write(b)
def pin(p):
 p=pathlib.Path(p);b=p.read_bytes();return dict(path=p.relative_to(ROOT).as_posix(),bytes=len(b),sha256=sha(b))
def wire(v):return ('{"e9":1,"fields":'+json.dumps(v,sort_keys=True,separators=(',',':'))+'}\n').encode('ascii')
def pack(b):return base64.urlsafe_b64encode(b).rstrip(b'=').decode()
def unpack(s):return base64.urlsafe_b64decode(s+'='*((-len(s))%4))
def context():
 c=read(STATE);return c,ROOT/c['root'],ROOT/c['root']/'inputs',ROOT/c['root']/'evidence'
def setup():
 need(not STATE.exists(),'SINGLE_ISSUANCE_STATE_ALREADY_EXISTS')
 ids={k:str(uuid.uuid4()) for k in ['registry','migration','attempt','handle']}
 root=ROOT/'docs/tester/D1_E10A_EXECUTION'/ids['migration'];inputs=root/'inputs';e=root/'evidence';inputs.mkdir(parents=True);e.mkdir()
 scope=read(B/'templates/scope.template.json');review=ROOT/'docs/tester/D1_E10A_EXECUTION_PACKAGE_REVIEW_REPORT_V1.0.md'
 need(pin(review)['sha256']=='e8fb76cfac6da5993c7c20638027529188be19e40fe8aae221671cb811ea99f0','ACCEPTED_REVIEW_PIN')
 scope.update(ids);scope.update(status='ISSUED_FOR_EXACT_ACTOR1',issuedAt=now(),executionDispatchEvidence=pin(ROOT/'docs/tester/D1_E10A_AUTHORITY_20261018.json'),acceptedE10AReviewEvidence=pin(review),acceptedE10AReviewSha256=pin(review)['sha256'])
 write(inputs/'scope.json',scope);write(STATE,dict(root=root.relative_to(ROOT).as_posix(),**ids));print(json.dumps(read(STATE)))
def call(label,args,limit=262144):
 c,root,i,e=context();n=len(list(e.glob('metadata-*-receipt.json')))+len(list(e.glob('metadata-*-pending.json')))
 if REUSE:
  old=list(e.glob('metadata-??-'+label+'-receipt.json'))
  if old:
   need(len(old)==1,'CACHE_AMBIGUOUS');r=read(old[0]);p=pathlib.Path(str(old[0]).replace('-receipt.json','-stdout.txt'));b=p.read_bytes()
   need(r['argv']==args and r['exitCode']==0 and r['originalClientReturned'] and r['pipesReturned'] and sha(b)==r['stdoutSha256'],'CACHE_NOT_ORIGINAL_RETURN');return b.decode('utf-8')
 need(n<20,'INDEPENDENT_METADATA_CLIENT_LIMIT');pfx=f'metadata-{n:02d}-{label}'
 intent=dict(label=label,argv=args,began=now(),scope='READ_ONLY_METADATA',ordinal=n+1);write(e/(pfx+'-intent.json'),intent)
 start=time.monotonic();p=subprocess.Popen(args,stdout=subprocess.PIPE,stderr=subprocess.PIPE,creationflags=subprocess.CREATE_NO_WINDOW)
 try:out,err=p.communicate(timeout=20)
 except subprocess.TimeoutExpired:
  write(e/(pfx+'-pending.json'),dict(intent,pid=p.pid,status='ORIGINAL_CLIENT_UNRETURNED_NO_KILL_NO_RETRY'));print('PENDING pid='+str(p.pid),flush=True)
  while p.poll() is None:time.sleep(1)
  raise RuntimeError('LATE_ORIGINAL_NOT_QUALIFIED')
 raw(e/(pfx+'-stdout.txt'),out);raw(e/(pfx+'-stderr.txt'),err)
 write(e/(pfx+'-receipt.json'),dict(intent,ended=now(),elapsedSeconds=time.monotonic()-start,pid=p.pid,exitCode=p.returncode,stdoutBytes=len(out),stderrBytes=len(err),stdoutSha256=sha(out),stderrSha256=sha(err),originalClientReturned=True,pipesReturned=True))
 need(p.returncode==0 and len(out)+len(err)<=limit,'METADATA_FAILED:'+pfx);return out.decode('utf-8')
def preflight():
 c,root,i,e=context();scope=read(i/'scope.json');plan=read(B/'plan/execution-plan.json')
 devices=call('devices',[ADB,'devices','-l']);rows=[x.split() for x in devices.splitlines() if x.startswith(SERIAL)]
 need(len(rows)==1 and rows[0][1]=='device','TABLET_NOT_AVAILABLE_NO_POLL')
 vals={}
 for name,args in [('user',['am','get-current-user']),('model',['getprop','ro.product.model']),('api',['getprop','ro.build.version.sdk']),('app',['dumpsys','package','com.videokit.app']),('test',['dumpsys','package','com.videokit.app.test']),('processes',['ps','-A','-o','PID,UID,NAME']),('app-path',['pm','path','com.videokit.app']),('test-path',['pm','path','com.videokit.app.test'])]:vals[name]=call(name,[ADB,'-s',SERIAL,'shell']+args)
 need(vals['user'].strip()=='0' and vals['model'].strip()=='TB138FC' and vals['api'].strip()=='31','DEVICE_CONTEXT')
 need(not any('com.videokit.app' in x for x in vals['processes'].splitlines()),'RELATED_PROCESS_PRESENT_STOP')
 for name,uid,version in [('app',10221,13),('test',10222,0)]:need(f'userId={uid}' in vals[name] and f'versionCode={version} ' in vals[name] and re.search(r'User 0:.*installed=true.*hidden=false.*suspended=false.*enabled=0',vals[name]),'SOURCE_PACKAGE_STATE:'+name)
 paths=[]
 for name in ['app-path','test-path']:
  s=vals[name].strip();need('\n' not in s and s.startswith('package:/data/app/') and s.endswith('/base.apk'),'APK_PATH');paths.append(s[8:])
 hashes=call('installed-pair-sha256',[ADB,'-s',SERIAL,'shell','sha256sum']+paths)
 need([x.split()[0] for x in hashes.splitlines()]==[x['sha256'] for x in plan['deployment']['sourcePair']],'EXACT_SOURCE13_PAIR_MISMATCH_STOP')
 write(e/'preflight-package.json',dict(at=now(),sourceVersion=13,installedPaths=paths,model=vals['model'].strip(),api=31,sourcePair=plan['deployment']['sourcePair'],roleAndAbi='Exact frozen APK identity: PREPARE/1; original signer verified by frozen APK audit',appUid=10221,testUid=10222,noRelatedProcess=True))
 print('SOURCE13_EXACT_PACKAGE_PREFLIGHT_RETURNED')
def private_metadata(label,post=False):
 c,root,i,e=context();p=read(B/'plan/execution-plan.json');task=p['legacy']['task']
 items={('files/'+x['relative']):x['maxBytes'] for x in p['legacy']['immutableMetadata']}
 items.update({'files/e4a_output_budget/ledger.bin':131072,'files/e4a_outputs/'+task+'.owner':0})
 if post:
  for row in p['deviceFiles']:items['files/e4a_output_budget/legacy-acceptance/'+c['migration']+'/'+row['relative']]=row['maxBytes']
 dirs=['files','files/e4a_output_budget','files/e4a_outputs','files/e4a_output_budget/N2-e5-recovery']
 stats=['files/'+row['output'][6:] for row in p['legacy']['settledRecords']]
 code=['set -eu',"printf 'INVENTORY_BEGIN\\n'",'find files/e4a_output_budget files/e4a_outputs -maxdepth 4 -print',"printf 'INVENTORY_END\\n'"]
 for path in dirs+list(items)+stats:
  code += ["printf 'STAT\\t%s\\t' "+shlex.quote(path),"stat -c '%d|%i|%u|%f|%s|%b' "+shlex.quote(path)]
 for path,bound in items.items():
  code += ['n=$(stat -c %s '+shlex.quote(path)+')','[ "$n" -le '+str(bound)+' ]',"printf 'DATA_BEGIN\\t%s\\n' "+shlex.quote(path),'base64 '+shlex.quote(path),"printf 'DATA_END\\n'"]
 code += ['if [ -e files/e4a_output_budget/operation.pending ] || [ -L files/e4a_output_budget/operation.pending ]; then exit 71; fi']
 script='\n'.join(code);sp=e/(label+'-remote-program.sh')
 if sp.exists():need(REUSE and sp.read_bytes()==script.encode(),'REMOTE_PROGRAM_NO_OVERWRITE')
 else:raw(sp,script.encode())
 out=call(label,[ADB,'-s',SERIAL,'shell','run-as com.videokit.app sh -c '+shlex.quote(script)],limit=262144).replace('\r\n','\n')
 rows={};data={};active=None;encoded=[]
 for line in out.splitlines():
  if line.startswith('STAT\t'):
   _,path,value=line.split('\t');v=value.split('|');rows[path]=dict(dev=int(v[0]),inode=int(v[1]),uid=int(v[2]),mode=int(v[3],16),size=int(v[4]),blocks=int(v[5]))
  elif line.startswith('DATA_BEGIN\t'):active=line.split('\t')[1];encoded=[]
  elif line=='DATA_END':data[active]=base64.b64decode(''.join(encoded),validate=True);active=None
  elif active:encoded.append(line)
 inv=out.split('INVENTORY_BEGIN\n',1)[1].split('INVENTORY_END\n',1)[0].splitlines()
 for path in dirs:need(rows[path]['mode']&0xf000==0x4000 and rows[path]['uid']==10221,'DIRECTORY_ROLE:'+path)
 for path in items.keys()|set(stats):need(rows[path]['mode']&0xf000==0x8000 and rows[path]['uid']==10221,'FILE_ROLE:'+path)
 for x in p['legacy']['immutableMetadata']:need(sha(data['files/'+x['relative']])==x['sha256'],'IMMUTABLE_METADATA:'+x['relative'])
 owner=rows['files/e4a_outputs/'+task+'.owner'];lease=rows['files/e4a_outputs/'+task+'.lease']
 need(f"{owner['dev']}:{owner['inode']}:{owner['uid']}"==p['legacy']['ownerId'] and owner['size']==0,'OWNER_GUARD')
 need(f"{lease['dev']}:{lease['inode']}:{lease['uid']}"==p['legacy']['leaseId'] and lease['size']==36 and data['files/e4a_outputs/'+task+'.lease'].decode()==p['legacy']['fence'],'LEASE_FENCE')
 ledger=data['files/e4a_output_budget/ledger.bin'];prefix=(B/'reference/accepted-ledger-prefix.bin').read_bytes();need(ledger.startswith(prefix),'LEDGER_PREFIX')
 # Legal suffix must not be silently accepted for this exact 107218 dispatch.
 need(ledger==prefix,'ADDITIONAL_SETTLED_SUFFIX_REQUIRES_DISPATCH_REVIEW');lines=ledger.decode('ascii').splitlines(keepends=True);chain=sha(lines[0].encode());entries={}
 for line in lines[1:]:
  payload,h=line.rstrip('\n').rsplit(' ',1);need(sha((chain+' '+payload).encode())==h,'LEDGER_CHAIN');chain=h;v=payload.split()
  if v[0]=='R':need(v[1] not in entries,'DUPLICATE_R');entries[v[1]]=None
  elif v[0]=='S':need(v[1] in entries and entries[v[1]] is None,'INVALID_S');entries[v[1]]=int(v[3])
  else:raise RuntimeError('LEDGER_RECORD')
 need(len(entries)==3 and all(v is not None for v in entries.values()) and sum(entries.values())==107218,'LEDGER_CONSERVATION')
 for row in p['legacy']['settledRecords']:need(rows[row['output']]['size']==row['bytes'],'OLD_OUTPUT_SIZE')
 legacy='files/e4a_output_budget/legacy-acceptance'
 if not post:need(not any(x.startswith(legacy+'/') for x in inv),'MIGRATION_TARGET_OR_OTHER_CONTROL_PRESENT')
 need(not (root/'registry').exists() if not post else True,'EXTERNAL_REGISTRY_MUST_BE_ABSENT')
 for path,b in data.items():raw(e/(label+'-'+path.replace('/','_')+'.bin'),b)
 result=dict(status='PASS_CURRENT_METADATA',at=now(),rows=rows,inventory=inv,hashes={k:sha(v) for k,v in data.items()},ledgerChain=chain,consumed=107218,reserved=0,oldCloseACK=False,nonzeroMediaPayloadReads=0)
 write(e/(label+'-audit.json'),result);print(label+' PASS metadata='+str(len(data)));return result
def metadata_preflight():
 c,root,i,e=context();need((e/'preflight-package.json').exists(),'PACKAGE_PREFLIGHT_FIRST');a=private_metadata('legacy-before')
 logs=call('log-headroom',[ADB,'-s',SERIAL,'shell','logcat','-d','-v','brief','-s','E9_MANAGED:I','ActivityManager:I','*:S'],limit=1048576)
 need(len(logs.encode('utf-8'))<=800000,'SYSTEM_LOG_INSUFFICIENT_HEADROOM_STOP_NO_CLEAR')
 p=read(B/'plan/execution-plan.json');write(i/'preflight.json',dict(status='COMPLETE_CONTEXT_REVALIDATED',observedAt=now(),sessionRegistry=c['registry'],serial=SERIAL,user=0,appUid=10221,testUid=10222,version=13,role='PREPARE',abi=1,installedPair=p['deployment']['sourcePair'],relatedProcessPids=[],oldOutputBytes=0,reserved=0,consumed=107218,ownerId=p['legacy']['ownerId'],leaseId=p['legacy']['leaseId'],fence=p['legacy']['fence'],**{k:True for k in ['legacyArchiveMatched','ledgerPrefixMatched','ledgerChainValid','baselineRecordsPreserved','pendingAbsent','migrationTargetAbsent','externalRegistryAbsent','metadataOriginalResourcesReturned','noUnknown']},rawEvidence=[pin(x) for x in sorted(e.glob('metadata-*-receipt.json'))]+[pin(e/'legacy-before-audit.json'),pin(e/'preflight-package.json')],systemLogBytes=len(logs.encode()),nonzeroMediaPayloadReads=0))
 print('FULL_PREFLIGHT_COMPLETE')
def prepare():
 c,root,i,e=context();need(read(i/'preflight.json')['status']=='COMPLETE_CONTEXT_REVALIDATED','CURRENT_PREFLIGHT');scope=read(i/'scope.json')
 plan=read(B/'templates/prepare-plan.template.json')['wireFields'];plan.update(registry=c['registry'],migration=c['migration'],authorization=pin(i/'scope.json')['sha256'],sourceReview=scope['acceptedE10AReviewSha256']);pr=wire(plan);raw(i/'prepare-plan.json',pr)
 cfg=read(B/'templates/manager-config.template.json')['wireFields'];cfg.update(plan=pack(pr),planSha=sha(pr),authorization=plan['authorization'],review=plan['sourceReview'],registryPath=(root/'registry').as_posix());raw(i/'manager-config.json',wire(cfg))
 (i/'commands').mkdir();names=['DEPLOY','LAUNCH','POLL','RESERVE','EXEC','POLL_COMMIT','ARCHIVE','ACK','FINISH','INSPECT','SEAL','STOP'];commands=[]
 for t,name in zip(sorted((B/'templates').glob('[0-9][0-9]-*.template.json')),names):
  f=read(t)['wireFields']
  if f['operation']=='LAUNCH':f.update(attempt=c['attempt'],handle=c['handle'])
  p=i/'commands'/t.name.replace('.template.json','.json');raw(p,wire(f));commands.append(dict(stage=name,path=p.relative_to(e).as_posix() if p.is_relative_to(e) else '../inputs/commands/'+p.name,sha256=pin(p)['sha256']))
 files=[i/'scope.json',i/'prepare-plan.json',i/'manager-config.json',i/'preflight.json']+sorted((i/'commands').glob('*.json'))
 write(i/'input-index.json',dict(at=now(),scopeSha256=plan['authorization'],files=[pin(x) for x in files],configSha256=pin(i/'manager-config.json')['sha256'],commandFiles=commands,artifactAllowlist={x['path'].split('/')[-1]:x['sha256'] for x in scope['artifactPins']}));print('ALL_CANONICAL_INPUTS_PINNED')
def load(name):return read(context()[3]/name)
def save(name,v):write(context()[3]/name,v)
def putraw(name,b):raw(context()[3]/name,b)
def transport(stage,label):
 c,r,i,e=context();replies=[read(p) for p in sorted(e.glob('session-*-response.json'))];reply=next(x for x in reversed(replies) if x['stage']==stage)['reply'];f=json.loads(reply)['fields']
 parts={k:unpack(f[k]) for k in ['actor','returned','snapshot']};parsed={k:json.loads(v)['fields'] for k,v in parts.items()}
 for k,v in parts.items():raw(e/(label+'-'+k+'.json'),v)
 a=parsed['actor'];p=parsed['returned'];s=parsed['snapshot'];plan=read(i/'prepare-plan.json')['fields']
 for k,w in dict(registry=c['registry'],migration=c['migration'],attempt=c['attempt'],handle=c['handle'],ordinal='1',uid='10221',environment='DEVICE_HA1Q6WXR',bootKind='SYSTEM_BOOT_COUNT',app=plan['app'],test=plan['test'],descriptor=plan['descriptor'],process='com.videokit.app').items():need(a[k]==w,'ACTOR_BINDING:'+k)
 need(p['actor']==sha(parts['actor']) and s['actor']==sha(parts['actor']) and s['returned']==sha(parts['returned']),'PROOF_BINDING')
 need(p['unreturned']=='0' and int(p['owned'])>=1 and int(p['identityNanos'])<10_000_000_000 and s['safe']=='true','QUALIFIED_ORIGINAL_RETURN')
 return parts,parsed
def identity_check():
 c,r,i,e=context();parts,v=transport('POLL','identity-original');a=v['actor'];p=v['returned'];s=v['snapshot']
 need(p['phase']=='IDENTITY' and p['verdict']=='IDENTITY_QUALIFIED' and p['reason']=='ACTUAL_IDENTITY_RETURNED' and p['executeDone']=='false' and p['device']=='ABSENT' and p['deviceRecord']=='ABSENT' and s['executeReserved']=='false' and s['finishClaimed']=='false','ORIGINAL_IDENTITY')
 live=call('identity-processes',[ADB,'-s',SERIAL,'shell','ps','-A','-o','PID,UID,NAME']);rows=[x.split() for x in live.splitlines() if x.split() and x.split()[0]==a['pid']];need(len(rows)==1 and rows[0][1:]==['10221','com.videokit.app'],'ACTUAL_PID_UID')
 boot=call('identity-boot',[ADB,'-s',SERIAL,'shell','settings','get','global','boot_count']).strip();need(boot==a['boot'],'ACTUAL_BOOT')
 stat=call('identity-start',[ADB,'-s',SERIAL,'shell','cat','/proc/'+a['pid']+'/stat']);need(stat[stat.rfind(')')+1:].strip().split()[19]==a['start'],'ACTUAL_START')
 save('identity-independent-check.json',dict(status='QUALIFIED_ACTUAL_IDENTITY',at=now(),actorSha256=sha(parts['actor']),returnSha256=sha(parts['returned']),pid=int(a['pid']),boot=boot,start=a['start'],identityNanos=int(p['identityNanos']),owned=int(p['owned']),unreturned=0,originalClientsReturned=True));print('IDENTITY_INDEPENDENT_PASS pid='+a['pid'])
def reserve_check():
 c,r,i,e=context();aRaw=(e/'identity-original-actor.json').read_bytes();pRaw=(e/'identity-original-returned.json').read_bytes();d=r/'registry';identity=read(d/'actors/0001/identify.json')['fields'];reserveRaw=(d/'actors/0001/reserve.json').read_bytes();v=json.loads(reserveRaw)['fields'];ev=[json.loads(x)['fields'] for x in (d/'registry.events.jsonl').read_bytes().splitlines()]
 need(unpack(identity['actor'])==aRaw and unpack(identity['returned'])==pRaw,'RESERVE_ORIGINAL_IDENTIFY_EXACT');need(v['actor']==sha(aRaw) and v['state']=='BOUND' and v['registry']==c['registry'] and v['ordinal']=='1' and v['descriptor']==read(i/'scope.json')['descriptorSha256'] and v['authorization']==pin(i/'scope.json')['sha256'] and v['preparePlan']==pin(i/'prepare-plan.json')['sha256'] and v['predecessor']=='NONE' and v['predecessorIntent']=='NONE','RESERVE_BINDINGS')
 need(ev[-1]['evidence']==sha(reserveRaw) and ev[-1]['state']=='BOUND','BOUND_EVENT')
 need(not (d/'actors/0001/returned.json').exists() and not (d/'final.acceptance.json').exists(),'NO_EARLY_FINAL')
 save('reserve-independent-check.json',dict(status='DURABLE_SAME_ACTOR_BOUND',at=now(),reserve=pin(d/'actors/0001/reserve.json'),identify=pin(d/'actors/0001/identify.json'),eventHead=sha((wire(ev[-1]))),deviceWrites=0));print('RESERVE_INDEPENDENT_PASS')
def commit_check():
 c,r,i,e=context();parts,v=transport('POLL','commit-original');p=v['returned'];s=v['snapshot']
 need(p['phase']=='COMMIT' and p['verdict']=='QUALIFIED_MIGRATION' and p['reason']=='ACTUAL_ALL_RETURNED' and p['executeDone']=='true' and int(p['executeNanos'])<10_000_000_000 and s['executeReserved']=='true' and s['finishClaimed']=='false','ORIGINAL_COMMIT_NOT_QUALIFIED')
 device=unpack(p['deviceRecord']);need(sha(device)==p['device'],'DEVICE_RECORD_HASH');raw(e/'original-device-record.json',device)
 save('commit-independent-check.json',dict(status='QUALIFIED_ACTUAL_COMMIT_ORIGINAL_RETURN',at=now(),actor=pin(e/'commit-original-actor.json'),returned=pin(e/'commit-original-returned.json'),device=pin(e/'original-device-record.json'),identityNanos=int(p['identityNanos']),executeNanos=int(p['executeNanos']),owned=int(p['owned']),unreturned=0));print('COMMIT_INDEPENDENT_PASS')
def archive_check():
 c,r,i,e=context();p=r/'registry/actors/0001/returned.json';need(p.read_bytes()==(e/'commit-original-returned.json').read_bytes(),'ARCHIVE_NOT_EXACT_ORIGINAL')
 save('archive-independent-check.json',dict(status='EXACT_ORIGINAL_COMMIT_ARCHIVED',at=now(),archive=pin(p)));print('ARCHIVE_INDEPENDENT_PASS')
def ack_check():
 c,r,i,e=context();parts,v=transport('ACK','ack-original');need(parts['returned']==(e/'commit-original-returned.json').read_bytes() and v['snapshot']['finishClaimed']=='true','ACK_NOT_ORIGINAL_OR_FINISH_NOT_CLAIMED')
 save('ack-independent-check.json',dict(status='ACK_ORIGINAL_RETURN_EXACT_FINISH_CLAIMED_NOT_YET_OS_FINISH',at=now(),returned=pin(e/'ack-original-returned.json')));print('ACK_INDEPENDENT_PASS')
def device_final_check():
 c,r,i,e=context();d=r/'registry';actorRaw=(e/'commit-original-actor.json').read_bytes();actor=json.loads(actorRaw)['fields'];ret=(e/'commit-original-returned.json').read_bytes();finishRaw=(d/'actors/0001/finish.json').read_bytes();finish=json.loads(finishRaw)['fields'];log=(d/'logs/actor-0001.finish.log').read_bytes();text=log.decode('utf-8')
 need(finish['actor']==sha(actorRaw) and finish['returned']==sha(ret) and finish['evidence']==sha(log) and finish['disposition']=='NORMAL_FINISH_CONFIRMED' and len(log)<=1048576,'ORIGINAL_NORMAL_FINISH_BINDING')
 anchor='E9_FINAL_FINISH handle='+actor['handle']+' actor='+sha(actorRaw)+' returned='+sha(ret)
 need(text.count(anchor)==1,'UNIQUE_ORIGINAL_FINISH_ANCHOR');tail=text.split(anchor,1)[1]
 need(re.search(r'Force stopping com[.]videokit[.]app[^\n]*finished inst',tail) and re.search(r'Killing '+actor['pid']+r'[^\n]*finished inst',tail),'ORIGINAL_SYSTEM_NORMAL_FINISH')
 ps=call('finished-processes',[ADB,'-s',SERIAL,'shell','ps','-A','-o','PID,UID,NAME']);need(not any('com.videokit.app' in x or (x.split() and x.split()[0]==actor['pid']) for x in ps.splitlines()),'ACTOR_NOT_ABSENT')
 a=private_metadata('legacy-after',post=True);before=read(e/'legacy-before-audit.json');need(all(a['rows'][p]==v for p,v in before['rows'].items() if p not in ['files','files/e4a_output_budget']),'OLD_FILE_FSTAT_PRESERVATION');need(all(a['hashes'][p]==v for p,v in before['hashes'].items()),'OLD_METADATA_OR_LEDGER_BYTES_CHANGED')
 base='files/e4a_output_budget/legacy-acceptance';scope=base+'/'+c['migration'];expectedDirs={base,scope,scope+'/actors'};expectedFiles={scope+'/actors/0001.intent',scope+'/n2-v2.acceptance',scope+'/n2-v2.commit'}
 need(set(a['inventory'])-set(before['inventory'])==expectedDirs|expectedFiles,'EXACT_NEW_DEVICE_INVENTORY');need(set(before['inventory'])<=set(a['inventory']),'OLD_INVENTORY_REMOVED')
 reserve=(d/'actors/0001/reserve.json').read_bytes();intent=wire(dict(actor,kind='intent',actor=sha(actorRaw),reserve=sha(reserve)));payload=(B/'plan/descriptor.json').read_bytes();commit=(B/'plan/expected-commit.json').read_bytes();expected={scope+'/actors/0001.intent':intent,scope+'/n2-v2.acceptance':payload,scope+'/n2-v2.commit':commit}
 for path,v in expected.items():need(a['hashes'][path]==sha(v) and a['rows'][path]['size']==len(v),'EXACT_DEVICE_FILE:'+path)
 device=read(e/'original-device-record.json')['fields'];need(device['intent1']==sha(intent) and device['intent2']=='ABSENT' and device['payload']==sha(payload) and device['commit']==sha(commit) and device['migration']==c['migration'],'RETURNED_DEVICE_BINDING')
 need(sum(len(v) for v in expected.values())<=3017 and len(intent)<=2048 and len(payload)==725 and len(commit)==244,'DEVICE_CONTENT_BOUND')
 for name,uid,ver,inode in [('app',10221,14,'6972'),('test',10222,0,'4741')]:
  meta=call('finished-'+name+'-package',[ADB,'-s',SERIAL,'shell','dumpsys','package','com.videokit.app'+('.test' if name=='test' else '')]);need(f'userId={uid}' in meta and f'versionCode={ver} ' in meta and re.search(r'User 0:.*ceDataInode='+inode+r'.*installed=true.*hidden=false.*suspended=false.*enabled=0',meta),'POST_PACKAGE_DATA_IDENTITY')
 save('device-final-independent-check.json',dict(status='PASS_ACTUAL_THREE_RECORDS_OLD_ACCOUNTING_AND_NORMAL_FINISH',at=now(),migration=c['migration'],actorSha256=sha(actorRaw),returnedSha256=sha(ret),finish=pin(d/'actors/0001/finish.json'),originalSystemLog=pin(d/'logs/actor-0001.finish.log'),originalPidAbsent=True,noRelatedProcess=True,newFiles=[dict(path=k,bytes=len(v),sha256=sha(v),stat=a['rows'][k]) for k,v in expected.items()],newDirectories=sorted(expectedDirs),totalNewContentBytes=sum(map(len,expected.values())),declaredFileCapacityCeiling=6400,observedFileBlocks512Bytes=sum(a['rows'][k]['blocks'] for k in expectedFiles)*512,allOldFileIdentityAndMetadataUnchanged=True,ledgerBytesUnchanged=True,consumed=107218,reserved=0,oldCloseACK=False,nonzeroMediaPayloadReads=0,productActivation=False));print('DEVICE_FINAL_INDEPENDENT_PASS content='+str(sum(map(len,expected.values()))))
def final_dag_check():
 c,r,i,e=context();d=r/'registry';need(read(e/'device-final-independent-check.json')['status']=='PASS_ACTUAL_THREE_RECORDS_OLD_ACCOUNTING_AND_NORMAL_FINISH','DEVICE_AUDIT_BEFORE_FINAL')
 def record(p):
  b=p.read_bytes();f=json.loads(b)['fields'];need(wire(f)==b,'FINAL_CANONICAL:'+str(p));return b,f
 descriptor,df=record(d/'descriptor.json');need(descriptor==(B/'plan/descriptor.json').read_bytes(),'DESCRIPTOR_EXACT');plan=(i/'prepare-plan.json').read_bytes();need((d/'prepare-deployment.json').read_bytes()==plan,'DEPLOYMENT_PLAN_EXACT')
 auth,af=record(d/'authorization-reference.json');need(af['reference']==pin(i/'scope.json')['sha256'] and af['migration']==c['migration'] and af['registry']==c['registry'],'AUTH_BINDING')
 ar=(e/'commit-original-actor.json').read_bytes();head=sha(descriptor);evrows=[]
 for n,line in enumerate((d/'registry.events.jsonl').read_bytes().splitlines(keepends=True),1):
  v=json.loads(line)['fields'];need(wire(v)==line and v['seq']==str(n) and v['parent']==head and v['actor']==sha(ar),'EVENT_CONTINUITY');ep=d/v['path'];need(ep.resolve().is_relative_to(d.resolve()) and ep.read_bytes() and v['evidence']==pin(ep)['sha256'],'EVENT_EVIDENCE');need(v['path'] not in ['final.acceptance.json','registry.checkpoint.json','final.seal.json'],'ACYCLIC_EVENT');head=sha(line);evrows.append(v)
 need([v['state'] for v in evrows]==['BOUND','RETURN_VERIFIED_IN_TIME','NORMAL_FINISH_CONFIRMED','FINAL_ACCEPTED'],'NORMAL_ACTOR1_FINAL_CHAIN')
 cat,cf=record(d/'final.acceptance.json');check,kf=record(d/'registry.checkpoint.json');seal,sf=record(d/'final.seal.json');scope=read(i/'scope.json');ret=(d/'actors/0001/returned.json').read_bytes()
 for k,w in dict(kind='catalog',actorCount='1',registry=c['registry'],migration=c['migration'],head=head,authorization=pin(i/'scope.json')['sha256'],review=scope['acceptedE10AReviewSha256'],environment='DEVICE_HA1Q6WXR',disposition1='RETURN_VERIFIED_IN_TIME',termination1='ABSENT').items():need(cf[k]==w,'CATALOG_BINDING:'+k)
 for k,p in [('actor1',e/'commit-original-actor.json'),('reserve1',d/'actors/0001/reserve.json'),('returned1',d/'actors/0001/returned.json'),('finish1',d/'actors/0001/finish.json'),('descriptor',d/'descriptor.json'),('device',e/'original-device-record.json')]:need(unpack(cf[k])==p.read_bytes(),'CATALOG_RAW_BINDING:'+k)
 need(all(cf[k+'2']=='ABSENT' for k in ['actor','reserve','returned','finish','termination','disposition']),'ACTOR2_ABSENT')
 need(kf==dict(kind='checkpoint',head=head,catalog=sha(cat),registry=c['registry']),'CHECKPOINT_BINDING')
 need(sf==dict(kind='seal',head=head,catalog=sha(cat),checkpoint=sha(check),descriptor=sha(descriptor),preparePlan=sha(plan),review=scope['acceptedE10AReviewSha256']),'SEAL_DAG_BINDING')
 cmds=(d/'actors/0001/commands.jsonl').read_bytes().splitlines(keepends=True);controls=[json.loads(x)['fields'] for x in cmds[1:]]
 need([v['command'] for v in controls]==['STATUS','EXECUTE_COMMIT','STATUS','ACK_FINISH'] and [v['seq'] for v in controls]==['1','2','3','4'],'EXACT_CONTROL_SEQUENCE')
 need(not (d/'actors/0002').exists() and not (d/'activation-release.json').exists(),'NO_ACTOR2_OR_ACTIVATION')
 rows=[pin(p) for p in sorted(d.rglob('*')) if p.is_file()];metadata=[x for x in rows if not x['path'].endswith('.log')];need(len(metadata)<=20 and sum(x['bytes'] for x in metadata)<=155648 and sum(x['bytes'] for x in metadata)<=196608,'REGISTRY_METADATA_BOUND')
 save('final-dag-independent-check.json',dict(status='PASS_ACTUAL_FINAL_DAG',at=now(),head=head,catalog=pin(d/'final.acceptance.json'),checkpoint=pin(d/'registry.checkpoint.json'),seal=pin(d/'final.seal.json'),events=evrows,actorSha256=sha(ar),actualControlSequence=controls,registryFiles=rows,registryMetadataFileCount=len(metadata),registryMetadataBytes=sum(x['bytes'] for x in metadata),systemLogSeparateBytes=pin(d/'logs/actor-0001.finish.log')['bytes'],cycleFree=True,actor2=False,productGrant=False));print('FINAL_DAG_PASS head='+head)
def session():
    c,root,i,OUT=context();index=read(i/'input-index.json');scope=read(i/'scope.json')
    need((OUT/'bound-validation-stdout.txt').exists() and 'PASS_BOUND_STATIC_BINDINGS_NOT_DEVICE_AUTHORITY' in (OUT/'bound-validation-stdout.txt').read_text(),'BOUND_VALIDATION_FIRST')
    java='D:/Android/Android Studio/jbr/bin/java.exe';jar=ROOT/'docs/coder/d1e10a/artifacts/D1-20261018-E10A/final/e10a-host-tools.jar';config=i/'manager-config.json'
    if sha(config.read_bytes())!=index['configSha256'] or sha(jar.read_bytes())!=index['artifactAllowlist'][jar.name]:raise RuntimeError('SESSION_INPUT_PIN')
    args=[java,'-cp',str(jar),'com.videokit.spike.e4.E9HostManager','--approved-session',str(config),index['configSha256']]
    save('manager-launch-intent.json',{'at':now(),'argv':args,'scope':scope['handle']})
    manager=subprocess.Popen(args,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,creationflags=subprocess.CREATE_NO_WINDOW)
    lines=queue.Queue();errors=queue.Queue();ready={};manager_failed=threading.Event()
    def capture(stream,name,target):
        with (OUT/name).open('xb') as out:
            for line in iter(stream.readline,b''):
                out.write(line);out.flush();text=line.decode('utf-8',errors='replace').strip();target.put(text)
                if 'E9_PC_SUPERVISOR_READY' in text:
                    m=re.search(r'handle=([a-f0-9-]+).*pcPid=(\d+).*127.0.0.1:(\d+)',text)
                    if m:ready.update(handle=m.group(1),pcPid=int(m.group(2)),port=int(m.group(3)))
                if any(x in text for x in ['Exception in thread','E9_PC_REGISTRY_ENTRY_END','E9_PC_MAIN_EXIT_BOUNDARY']):manager_failed.set()
        stream.close()
    readers=[threading.Thread(target=capture,args=(manager.stdout,'manager-stdout.txt',lines)),threading.Thread(target=capture,args=(manager.stderr,'manager-stderr.txt',errors))]
    for t in readers:t.start()
    until=time.monotonic()+8
    while not ready and time.monotonic()<until and manager.poll() is None:time.sleep(.02)
    if ready:save('manager-runtime-identity.json',dict(ready,at=now(),controllerPid=__import__('os').getpid(),managerPid=manager.pid))
    print('BRIDGE_READY '+json.dumps(ready),flush=True)
    sequence=0;pc_queries=0;android_controls=0;statuses=0;used=set();halted=False
    def send(name):
        nonlocal sequence,android_controls,statuses
        if name in {'DEPLOY','LAUNCH','RESERVE','EXEC','ARCHIVE','ACK','FINISH','SEAL','STOP'} and name in used:raise RuntimeError('STAGE_ONCE_NO_REPLAY:'+name)
        if manager_failed.is_set():raise RuntimeError('MANAGER_HAS_FAILED_NO_DEPENDENT_WORK')
        row=next(v for v in index['commandFiles'] if v['stage']==name);raw=(OUT/row['path']).read_bytes()
        if sha(raw)!=row['sha256']:raise RuntimeError('COMMAND_PIN')
        if name in {'POLL','EXEC','ACK','STOP'}:
            android_controls+=1
            if name=='POLL':statuses+=1
            if android_controls>8 or statuses>3:raise RuntimeError('ANDROID_REQUEST_BUDGET')
        sequence+=1;save(f'session-{sequence:02d}-intent.json',{'at':now(),'stage':name,'sha256':sha(raw),'androidControlsIssued':android_controls,'androidStatusesIssued':statuses,'pcQueriesIssued':pc_queries})
        required={'RESERVE':'identity-independent-check.json','EXEC':'reserve-independent-check.json','ARCHIVE':'commit-independent-check.json','ACK':'archive-independent-check.json','FINISH':'ack-independent-check.json','SEAL':'device-final-independent-check.json'}
        if name in required:need((OUT/required[name]).is_file(),'INDEPENDENT_GATE:'+name)
        used.add(name);manager.stdin.write(raw);manager.stdin.flush()
    def await_line(kind,seconds=8):
        end=time.monotonic()+seconds
        while time.monotonic()<end:
            try:line=lines.get(timeout=.05)
            except queue.Empty:
                if manager_failed.is_set() or manager.poll() is not None:raise RuntimeError('MANAGER_NOT_QUALIFIED')
                continue
            if kind=='inspect' and line.startswith('knownHead='):return line
            if kind=='frame' and line.startswith('{"e9":1,'):return line
        raise RuntimeError('MANAGER_RESPONSE_UNKNOWN_NO_RETRY')
    try:
        for text in sys.stdin:
            command=text.strip().upper()
            try:
                if command=='END':
                    manager.stdin.close();rc=manager.wait(timeout=10)
                    for t in readers:t.join(2)
                    save('manager-final-client-receipt.json',{'at':now(),'exitCode':rc,'managerPid':manager.pid,'stdoutReaderReturned':not readers[0].is_alive(),'stderrReaderReturned':not readers[1].is_alive(),'pcQueriesIssued':pc_queries,'androidControlsIssued':android_controls,'androidStatusesIssued':statuses,'scope':scope['handle']})
                    print('BRIDGE_END originalManagerExit='+str(rc),flush=True);return
                if command=='STATUS':
                    pc_queries+=1
                    if pc_queries>16:raise RuntimeError('PC_QUERY_BUDGET')
                    args=[java,'-cp',str(jar),'com.videokit.spike.e4.E9PcClient','--status',str(ready['port']),ready['handle']]
                    save(f'pc-query-{pc_queries:02d}-intent.json',{'at':now(),'argv':args,'issued':pc_queries})
                    q=subprocess.Popen(args,stdout=subprocess.PIPE,stderr=subprocess.PIPE,creationflags=subprocess.CREATE_NO_WINDOW);stdout,stderr=q.communicate(timeout=8)
                    putraw(f'pc-query-{pc_queries:02d}-stdout.txt',stdout);putraw(f'pc-query-{pc_queries:02d}-stderr.txt',stderr)
                    save(f'pc-query-{pc_queries:02d}-receipt.json',{'at':now(),'exitCode':q.returncode,'clientPid':q.pid,'originalClientReturned':True,'pipesReturned':True})
                    if q.returncode:raise RuntimeError('LOCAL_QUERY_FAILED_NO_RETRY')
                    print('PC_STATUS '+stdout.decode().strip(),flush=True);continue
                if halted:raise RuntimeError('CONTROLLER_PENDING_NO_DEPENDENT_WORK')
                if command not in {'DEPLOY','LAUNCH','POLL','RESERVE','EXEC','ARCHIVE','ACK','FINISH','INSPECT','SEAL','STOP'}:raise RuntimeError('BRIDGE_WHITELIST')
                send(command)
                if command in {'POLL','EXEC','ACK','STOP'}:reply=await_line('frame',8)
                else:
                    if command!='INSPECT':send('INSPECT')
                    reply=await_line('inspect',90 if command=='DEPLOY' else 8)
                save(f'session-{sequence:02d}-response.json',{'at':now(),'stage':command,'reply':reply,'scope':scope['handle']})
                print('STAGE_RETURNED '+command+' '+reply,flush=True)
            except Exception as e:
                halted=True
                save(f'bridge-failure-{sequence:02d}-{pc_queries:02d}.json',{'at':now(),'command':command,'error':repr(e),'managerPid':manager.pid,'managerAlive':manager.poll() is None,'custodian':ready,'disposition':'STOP_DEPENDENCIES_NO_REPLAY_NO_KILL'})
                print('BRIDGE_PENDING '+repr(e),flush=True)
    finally:
        if manager.poll() is None:
            print('ORIGINAL_MANAGER_RETAINED pid='+str(manager.pid)+' '+json.dumps(ready),flush=True)
            # Do not end the owner process, cancel it or manufacture a close receipt.
            while manager.poll() is None:time.sleep(1)

if __name__=='__main__':
 action=sys.argv[1]
 if action=='setup':setup()
 elif action=='preflight':preflight()
 elif action=='resume-preflight':
  REUSE=True;c,r,i,e=context();write(e/'host-readonly-compatibility-correction-01.json',dict(at=now(),originalError='DEVICE_CONTEXT',reason='ro.product.model actual TB138FC; erroneous host literal Lenovo TB138FC',deviceStateMismatch=False,deviceRetry=False,reuseAllSuccessfulOriginalClients=True));preflight()
 elif action=='metadata-preflight':metadata_preflight()
 elif action=='resume-metadata-preflight':
  REUSE=True;c,r,i,e=context();write(e/'host-readonly-compatibility-correction-02.json',dict(at=now(),originalError='INVENTORY_BEGIN separator parsing',reason='ADB shell CRLF transport; normalize only parser text, preserve original raw bytes and decoded metadata',deviceRetry=False,reuseAllSuccessfulOriginalClients=True));metadata_preflight()
 elif action=='prepare':prepare()
 elif action=='session':session()
 elif action=='identity-check':identity_check()
 elif action=='reserve-check':reserve_check()
 elif action=='commit-check':commit_check()
 elif action=='archive-check':archive_check()
 elif action=='ack-check':ack_check()
 elif action=='device-final-check':device_final_check()
 elif action=='final-dag-check':final_dag_check()
 else:raise RuntimeError('EXPLICIT_STAGE_REQUIRED')
