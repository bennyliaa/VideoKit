"""Tester controller for the single authorized E9B read-only device batch. No retry/kill."""
import base64,datetime,hashlib,json,pathlib,queue,re,subprocess,sys,threading,time,uuid
ROOT=pathlib.Path(__file__).resolve().parents[3];OUT=pathlib.Path(__file__).parent
ADB='D:/Android/SDK/platform-tools/adb.exe';SERIAL='HA1Q6WXR'
def now():return datetime.datetime.now().astimezone().isoformat()
def sha(b):return hashlib.sha256(b).hexdigest()
def save(name,value):
    p=OUT/name
    if p.exists():raise RuntimeError('NO_OVERWRITE:'+name)
    p.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def load(name):return json.loads((OUT/name).read_text(encoding='utf-8-sig'))
def wire(fields):return (json.dumps({'e9':1,'fields':dict(sorted(fields.items()))},separators=(',',':'),ensure_ascii=True)+'\n').encode('ascii')
def pack(b):return base64.urlsafe_b64encode(b).rstrip(b'=').decode('ascii')
def putraw(name,b):
    with (OUT/name).open('xb') as f:f.write(b)
def call(label,args,limit=262144):
    index=len(list(OUT.glob('preflight-*-receipt.json')))
    prefix=f'preflight-{index:02d}-{label}';record={'label':label,'argv':args,'began':now(),'scope':'READ_ONLY_METADATA'}
    save(prefix+'-intent.json',record)
    start=time.monotonic();p=subprocess.Popen(args,stdout=subprocess.PIPE,stderr=subprocess.PIPE,creationflags=subprocess.CREATE_NO_WINDOW)
    try:stdout,stderr=p.communicate(timeout=20)
    except subprocess.TimeoutExpired:
        save(prefix+'-pending.json',dict(record,pid=p.pid,disposition='ORIGINAL_CLIENT_UNRETURNED_NO_KILL_NO_RETRY'))
        print('PENDING ORIGINAL_CLIENT pid='+str(p.pid),flush=True)
        while p.poll() is None:time.sleep(1)
        raise RuntimeError('LATE_METADATA_CLIENT_NOT_QUALIFIED')
    (OUT/(prefix+'-stdout.txt')).write_bytes(stdout);(OUT/(prefix+'-stderr.txt')).write_bytes(stderr)
    receipt=dict(record,ended=now(),elapsedSeconds=time.monotonic()-start,pid=p.pid,exitCode=p.returncode,stdoutBytes=len(stdout),stderrBytes=len(stderr),stdoutSha256=sha(stdout),stderrSha256=sha(stderr),originalClientReturned=True,pipesReturned=True)
    save(prefix+'-receipt.json',receipt)
    if p.returncode or len(stdout)+len(stderr)>limit:raise RuntimeError('METADATA_FAILED:'+prefix)
    return stdout.decode('utf-8',errors='strict')
def setup():
    req=ROOT/'docs/milestones/D1_E9B_READ_ONLY_IDENTITY_TESTER_REQUIREMENTS_V1.0.md'
    scope={'kind':'READ_ONLY_IDENTITY_EXECUTION_SCOPE','created':now(),'sourceThread':'01a107c3-2bf9-7fa0-94a0-234258ca6774','source':'Formal E9B_READ_ONLY_IDENTITY dispatch after accepted E9B review; human permanent tablet-use permission and 2026-10-18 resume','requirements':str(req.relative_to(ROOT)).replace('\\','/'),'requirementsSha256':sha(req.read_bytes()),'sourceReview':'03cae4e6313db391ea0838bc289814b97a1319bd98ac6d08e30f2a4df1fa5fb1','serial':SERIAL,'user':0,'appUid':10221,'testUid':10222,'version':13,'mode':'READ_ONLY_IDENTITY','registry':str(uuid.uuid4()),'migration':str(uuid.uuid4()),'attempt':str(uuid.uuid4()),'handle':str(uuid.uuid4()),'actorOrdinal':1,'pcStatusOpCleanupLimit':16,'androidControlLimit':8,'androidStatusLimit':3,'scopeProhibitions':['RESERVE','EXECUTE_COMMIT','SEAL_FINAL','MEDIA','PRODUCT','ACTOR2','ACTOR3','MIGRATION','ACTIVATION','ABORT','BUDGET_CHANGE'],'migrationApprovalToken':'NOT_CREATED','finalCatalog':'NOT_CREATED','authorityMeaning':'SHA binds this explicitly dispatched read-only scope; no commit or product authority'}
    save('authorized-readonly-scope.json',scope)
    save('command-resource-plan.json',{'created':now(),'initialMetadata':['devices','current-user','model','api','app-package','test-package','processes','app-path','test-path','installed-pair-hash'],'futureProductionSession':['DEPLOY_PREPARE only if necessary, app/test install-r each once','LAUNCH ordinal1 explicit READ_ONLY_IDENTITY','POLL bounded <=3 STATUS','ARCHIVE_RETURN only exact valid identity proof','ACK_FINISH once','CAPTURE_FINISH actual original OS evidence','INSPECT and END'],'pcStatusOpCleanupLimit':16,'noAutomaticUnknownRetry':True,'readOnlyCompatibilityCorrectionsLimit':2,'actualDeviceCommands':0,'futureMode':'NOT_EXECUTED'})
    print('SCOPE_SAVED registry='+scope['registry']+' actorHandle='+scope['handle'])
def preflight():
    scope=load('authorized-readonly-scope.json')
    devices=call('devices',[ADB,'devices','-l'])
    rows=[line.split() for line in devices.splitlines() if line.startswith(SERIAL+'\t') or line.startswith(SERIAL+' ')]
    if len(rows)!=1 or rows[0][1]!='device':save('preflight-result.json',{'status':'TABLET_NOT_AVAILABLE_NO_POLL','devices':devices});print('TABLET_NOT_AVAILABLE_NO_POLL');return
    values={}
    commands=[('current-user',['shell','am','get-current-user']),('model',['shell','getprop','ro.product.model']),('api',['shell','getprop','ro.build.version.sdk']),('app-package',['shell','dumpsys','package','com.videokit.app']),('test-package',['shell','dumpsys','package','com.videokit.app.test']),('processes',['shell','ps','-A','-o','PID,UID,NAME']),('app-path',['shell','pm','path','com.videokit.app']),('test-path',['shell','pm','path','com.videokit.app.test'])]
    for label,args in commands:values[label]=call(label,[ADB,'-s',SERIAL]+args)
    if values['current-user'].strip()!='0':raise RuntimeError('WRONG_CURRENT_USER')
    processes=[line for line in values['processes'].splitlines() if 'com.videokit.app' in line]
    if processes:save('preflight-result.json',{'status':'RELATED_PROCESS_PRESENT_STOP','relatedProcesses':processes});print('RELATED_PROCESS_PRESENT_STOP');return
    paths=[]
    for label in ['app-path','test-path']:
        lines=values[label].strip().splitlines()
        if len(lines)!=1 or not lines[0].startswith('package:/data/app/') or not lines[0].endswith('/base.apk'):raise RuntimeError('INSTALLED_APK_PATH')
        paths.append(lines[0][8:])
    values['installed-pair-hash']=call('installed-pair-hash',[ADB,'-s',SERIAL,'shell','sha256sum']+paths)
    hashes=[line.split()[0] for line in values['installed-pair-hash'].strip().splitlines()]
    save('preflight-result.json',{'status':'METADATA_COLLECTED_NO_RELATED_PROCESS','at':now(),'model':values['model'].strip(),'api':values['api'].strip(),'currentUser':0,'appSha256':hashes[0],'testSha256':hashes[1],'relatedProcesses':[],'packageMetadataFiles':'preflight-*-package-stdout.txt','paths':paths})
    print(json.dumps(load('preflight-result.json'),ensure_ascii=False))
def prepare():
    scope=load('authorized-readonly-scope.json');pre=load('preflight-result.json')
    if pre['status']!='METADATA_COLLECTED_NO_RELATED_PROCESS':raise RuntimeError('PREFLIGHT_NOT_READY')
    old=ROOT/'docs/coder/d1e7a/evidence/apk-audit.json';baseline=json.loads(old.read_text())['apks']
    if [pre['appSha256'],pre['testSha256']]!=[v['sha256'] for v in baseline]:raise RuntimeError('INSTALLED_BASELINE_NOT_APPROVED')
    for v in baseline:
        if sha((ROOT/v['path']).read_bytes())!=v['sha256']:raise RuntimeError('BASELINE_ARTIFACT_MISMATCH')
    appmeta=next(OUT.glob('preflight-*-app-package-stdout.txt')).read_text();testmeta=next(OUT.glob('preflight-*-test-package-stdout.txt')).read_text()
    for text,uid,version in [(appmeta,10221,10),(testmeta,10222,0)]:
        if f'userId={uid}' not in text or f'versionCode={version} ' not in text or not re.search(r'User 0:.*installed=true.*hidden=false.*suspended=false.*enabled=0',text):raise RuntimeError('PACKAGE_IDENTITY_ENABLED_MISMATCH')
    artifacts=ROOT/'docs/coder/d1e9b/artifacts/D1-20261018-E9B/final'
    expected={'app-debug.apk':'ce9e32b280a600792abdf0735925f16d91f4c68fefc1d523e4a5c9fce5e7f020','app-debug-androidTest.apk':'2ee2ada85cbbe6e6a4a8d145a8d7b30a2cebe6a8be4d4c9413f2cd906e36f76b','e9b-host-tools.jar':'4f782d36cd320876f9f48e88d8adab3f5e9889f753800d5fa4cf45343882d707'}
    for name,h in expected.items():
        if sha((artifacts/name).read_bytes())!=h:raise RuntimeError('FINAL_ARTIFACT_MISMATCH:'+name)
    source=(ROOT/'docs/coder/d1e9b/src/com/videokit/spike/e4/E9LegacyProfile.java').read_text()
    immutable=dict(re.findall(r'm.put\("([^\"]+)","([a-f0-9]{64})"\)',source))
    descriptor={'kind':'descriptor','policy':'D1-E8A-LEGACY-N2-TERMINAL-ACCEPTANCE-V2','task':'86cafdb3-0fc4-447d-920b-b19c884bf494','budget':'730a73e1-50e1-4198-a515-047104f00e31','oldAttempt':'8c6673b7-38a5-4a24-838d-ca8466d8b75f','fence':'662e9ecd-bede-42e6-bb58-ce81d668ff44','prefixSha':'f32b1a35689fff1ffae230f2efcd10fbf42adc8c3e2d3e74892d2d8c7da98aba','prefixBytes':'1011','consumed':'107218','archive':sha(''.join(k+' '+v+'\n' for k,v in sorted(immutable.items())).encode('ascii')),'scope':'TERMINAL_LEGACY_NO_MEDIA_MUTATION','schema':'2','ownerId':'64522:20304:10221','leaseId':'64522:20385:10221','oldEpoch':'5131975343750146374','oldGeneration':'1','oldService':'775a5ee9-fff3-4340-a03b-97751099c0c4','oldCloseACK':'FALSE'}
    if len(immutable)!=13:raise RuntimeError('DESCRIPTOR_SOURCE_INVENTORY')
    descriptor_bytes=wire(descriptor);putraw('reviewed-descriptor.json',descriptor_bytes)
    authorization=sha((OUT/'authorized-readonly-scope.json').read_bytes());signer='5e841a04968f3f790f6996ca5e286d8c2734338542486909f9a136717dde808f'
    plan=wire({'kind':'preparePlan','registry':scope['registry'],'migration':scope['migration'],'descriptor':sha(descriptor_bytes),'authorization':authorization,'app':expected['app-debug.apk'],'test':expected['app-debug-androidTest.apk'],'signer':signer,'appId':'com.videokit.app','testId':'com.videokit.app.test','uid':'10221','testUid':'10222','version':'13','role':'PREPARE','abi':'1','sourceReview':scope['sourceReview'],'environment':'DEVICE_HA1Q6WXR'})
    putraw('reviewed-prepare-plan.json',plan)
    config=wire({'kind':'managerTrust','plan':pack(plan),'planSha':sha(plan),'authorization':authorization,'review':scope['sourceReview'],'registryPath':(OUT/'external-registry').as_posix(),'head':'NEW','originalApp':pre['appSha256'],'originalTest':pre['testSha256'],'originalVersion':'10','originalRole':'LEGACY_NO_GATE','originalAbi':'0'})
    putraw('reviewed-manager-config.json',config)
    commands={'DEPLOY':{'operation':'DEPLOY_PREPARE','app':(artifacts/'app-debug.apk').as_posix(),'test':(artifacts/'app-debug-androidTest.apk').as_posix()},'LAUNCH':{'operation':'LAUNCH','ordinal':'1','attempt':scope['attempt'],'handle':scope['handle'],'bootKind':'SYSTEM_BOOT_COUNT','mode':'READ_ONLY_IDENTITY'},'POLL':{'operation':'POLL'},'ARCHIVE':{'operation':'ARCHIVE_RETURN'},'ACK':{'operation':'CONTROL','command':'ACK_FINISH'},'FINISH':{'operation':'CAPTURE_FINISH'},'INSPECT':{'operation':'INSPECT'}}
    rows=[]
    for name,v in commands.items():
        raw=wire(dict(kind='managerCommand',**v));putraw('command-'+name+'.json',raw);rows.append({'stage':name,'path':'command-'+name+'.json','sha256':sha(raw)})
    save('reviewed-config-command-index.json',{'at':now(),'authorizationReferenceSha256':authorization,'authorizationScope':'ONLY_READ_ONLY_IDENTITY_AND_SAME_SCOPE_NORMAL_FINISH','configSha256':sha(config),'planSha256':sha(plan),'descriptorSha256':sha(descriptor_bytes),'descriptorSourceSha256':sha(source.encode()),'commandFiles':rows,'artifactAllowlist':expected,'counterLimits':{'pcQueries':16,'androidControls':8,'androidStatuses':3},'noSyntheticInput':True,'migrationApprovalToken':'NOT_CREATED'})
    print('CONFIG_AND_COMMANDS_PINNED configSha256='+sha(config))
def identity_evidence():
    scope=load('authorized-readonly-scope.json')
    replies=[json.loads(p.read_text()) for p in sorted(OUT.glob('session-*-response.json'))]
    reply=next(v for v in replies if v['stage']=='POLL')['reply'];transport=json.loads(reply);fields=transport['fields']
    if fields['mode']!='READ_ONLY_IDENTITY' or fields['uid']!='10221':raise RuntimeError('READONLY_TRANSPORT_SCOPE')
    def unpack(s):return base64.urlsafe_b64decode(s+'='*((-len(s))%4))
    actor_raw=unpack(fields['actor']);proof_raw=unpack(fields['returned']);snapshot_raw=unpack(fields['snapshot']);actor=json.loads(actor_raw)['fields'];proof=json.loads(proof_raw)['fields'];snapshot=json.loads(snapshot_raw)['fields']
    expected={'registry':scope['registry'],'migration':scope['migration'],'attempt':scope['attempt'],'handle':scope['handle'],'ordinal':'1','uid':'10221','environment':'DEVICE_HA1Q6WXR','bootKind':'SYSTEM_BOOT_COUNT'}
    if any(actor[k]!=v for k,v in expected.items()):raise RuntimeError('ACTOR_BINDING')
    if proof['actor']!=sha(actor_raw) or snapshot['actor']!=sha(actor_raw) or snapshot['returned']!=sha(proof_raw):raise RuntimeError('ACTOR_RETURN_BINDING')
    if any(proof[k]!=v for k,v in {'phase':'IDENTITY','verdict':'IDENTITY_QUALIFIED','unreturned':'0','executeDone':'false','device':'ABSENT','deviceRecord':'ABSENT','reason':'NO_WRITE_INGRESS_CLOSED'}.items()):raise RuntimeError('IDENTITY_RETURN_NOT_QUALIFIED')
    if snapshot['safe']!='true' or snapshot['executeReserved']!='false' or snapshot['finishClaimed']!='false' or int(proof['identityNanos'])>=10_000_000_000:raise RuntimeError('ACTUAL_IDENTITY_QUALIFICATION')
    for name,b in [('original-transport.json',(reply+'\n').encode()),('original-actor.json',actor_raw),('original-identity-return.json',proof_raw),('original-snapshot.json',snapshot_raw)]:putraw(name,b)
    live=call('identity-live-processes',[ADB,'-s',SERIAL,'shell','ps','-A','-o','PID,UID,NAME'])
    matches=[line.split() for line in live.splitlines() if line.split() and line.split()[0]==actor['pid']]
    if len(matches)!=1 or matches[0][1:]!=['10221','com.videokit.app']:raise RuntimeError('ORIGINAL_ACTOR_NOT_LIVE')
    boot=call('identity-boot-count',[ADB,'-s',SERIAL,'shell','settings','get','global','boot_count']).strip()
    if boot!=actor['boot']:raise RuntimeError('ACTUAL_BOOT_COUNT_MISMATCH')
    stat=call('identity-proc-stat',[ADB,'-s',SERIAL,'shell','cat','/proc/'+actor['pid']+'/stat'])
    start=stat[stat.rfind(')')+1:].strip().split()[19]
    if start!=actor['start']:raise RuntimeError('ACTUAL_PROC_START_MISMATCH')
    save('identity-independent-check.json',{'status':'ACTUAL_READONLY_IDENTITY_QUALIFIED','at':now(),'actorSha256':sha(actor_raw),'returnSha256':sha(proof_raw),'actorPid':int(actor['pid']),'uid':10221,'bootKind':actor['bootKind'],'bootCount':boot,'start':start,'identityNanos':int(proof['identityNanos']),'owned':int(proof['owned']),'unreturned':0,'executeReserved':False,'executeDone':False,'deviceWriteEvidence':'ABSENT','launcherClientAlreadyReturned':True,'independentOriginalPidAlive':True,'independentBootAndStartMatched':True})
    print(json.dumps(load('identity-independent-check.json')))
def postflight():
    if load('manager-final-client-receipt.json')['exitCode']!=0:raise RuntimeError('MANAGER_NOT_RETURNED')
    values={}
    for label,args in [('final-app-package',['dumpsys','package','com.videokit.app']),('final-test-package',['dumpsys','package','com.videokit.app.test']),('final-processes',['ps','-A','-o','PID,UID,NAME'])]:values[label]=call(label,[ADB,'-s',SERIAL,'shell']+args)
    related=[line for line in values['final-processes'].splitlines() if 'com.videokit.app' in line]
    if related:raise RuntimeError('FINAL_RELATED_PROCESS_PRESENT')
    rows=[]
    for label,uid,version,inode in [('final-app-package',10221,13,'6972'),('final-test-package',10222,0,'4741')]:
        text=values[label]
        if f'userId={uid}' not in text or f'versionCode={version} ' not in text or not re.search(r'User 0:.*ceDataInode='+inode+r'.*installed=true.*hidden=false.*suspended=false.*enabled=0',text):raise RuntimeError('FINAL_PACKAGE_OR_DATA_IDENTITY_MISMATCH')
        rows.append({'package':label,'uid':uid,'versionCode':version,'ceDataInode':inode,'dataInodeMatchesBefore':True})
    save('postflight-result.json',{'status':'FINAL_PACKAGE_AND_PROCESS_METADATA_PASS','at':now(),'relatedProcesses':[],'packages':rows,'newDeviceOrProductWork':False})
    print(json.dumps(load('postflight-result.json')))
def session():
    index=load('reviewed-config-command-index.json');scope=load('authorized-readonly-scope.json')
    java='D:/Android/Android Studio/jbr/bin/java.exe';jar=ROOT/'docs/coder/d1e9b/artifacts/D1-20261018-E9B/final/e9b-host-tools.jar';config=OUT/'reviewed-manager-config.json'
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
        if name in {'DEPLOY','LAUNCH','ARCHIVE','ACK','FINISH'} and name in used:raise RuntimeError('STAGE_ONCE_NO_REPLAY:'+name)
        if manager_failed.is_set():raise RuntimeError('MANAGER_HAS_FAILED_NO_DEPENDENT_WORK')
        row=next(v for v in index['commandFiles'] if v['stage']==name);raw=(OUT/row['path']).read_bytes()
        if sha(raw)!=row['sha256']:raise RuntimeError('COMMAND_PIN')
        if name in {'POLL','ACK'}:
            android_controls+=1
            if name=='POLL':statuses+=1
            if android_controls>8 or statuses>3:raise RuntimeError('ANDROID_REQUEST_BUDGET')
        sequence+=1;save(f'session-{sequence:02d}-intent.json',{'at':now(),'stage':name,'sha256':sha(raw),'androidControlsIssued':android_controls,'androidStatusesIssued':statuses,'pcQueriesIssued':pc_queries})
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
                if command not in {'DEPLOY','LAUNCH','POLL','ARCHIVE','ACK','FINISH','INSPECT'}:raise RuntimeError('BRIDGE_WHITELIST')
                send(command)
                if command in {'POLL','ACK'}:reply=await_line('frame',8)
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
    if sys.argv[1]=='setup':setup()
    elif sys.argv[1]=='preflight':preflight()
    elif sys.argv[1]=='prepare':prepare()
    elif sys.argv[1]=='session':session()
    elif sys.argv[1]=='identity-evidence':identity_evidence()
    elif sys.argv[1]=='postflight':postflight()
    else:raise RuntimeError('EXPLICIT_STAGE_REQUIRED')
