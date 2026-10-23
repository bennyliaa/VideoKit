def permit(name,scenario='NONE'):
 if time.monotonic()-START>=600:raise AssertionError('STOP_NEW_CASE_BEFORE_600S')
 folder=W/name;folder.mkdir();home=folder/'actual-home';root=home/'outputs';now=datetime.now(timezone.utc)
 proto=ProductionRunner.__new__(ProductionRunner);proto.plan=plan;proto.root=root
 modes=['identity','global_busy' if scenario=='BUSY' else 'global_idle','app_absence','test_absence','payload_app','payload_test','instrument']
 p={'schema':'VIDEOKIT_PRODUCTION_RUNNER_PERMIT_V2','routeBackend':BACKEND,'authorizationId':str(uuid.uuid4()),'mode':'OFFLINE_FIXTURE','approvedForExecution':True,'notBeforeUtc':(now-timedelta(seconds=1)).isoformat(),'expiresUtc':(now+timedelta(seconds=299)).isoformat(),'planId':str(uuid.uuid4()),'runId':'D1MA02-RUNNER_FIXTURE','scope':'','home':str(home),'evidenceRoot':str(root),'sources':dict(sources),'sourceSeal':{'path':str(B/'reference/runner-source-seal.json'),'sha256':sha((B/'reference/runner-source-seal.json').read_bytes())},'review':{'path':str(folder/'offline-review.txt'),'sha256':sha(b'OFFLINE_FIXTURE_REVIEW_NOT_LIVE\n')},'product':copy.deepcopy(plan['product']),'tools':[{'path':PY,'bytes':Path(PY).stat().st_size,'sha256':sha(Path(PY).read_bytes())}],'roles':[proto.fixture_slot(i,m) for i,m in enumerate(modes)],'operations':list(OPS),'limits':dict(LIMITS),'fixtureScenario':scenario}
 (folder/'offline-review.txt').write_bytes(b'OFFLINE_FIXTURE_REVIEW_NOT_LIVE\n');p['scope']=sha('|'.join((p['planId'],sources['tools/capture_android02.ps1'],p['product']['sealSha256'],sources['reference/exact-seven-role-plan.json'],p['runId'])).encode())
 from fixture_inputs import qualification
 p['globalIdleQualification']=qualification(p['scope'],p['runId']);p['globalIdleQualification']['reviewEvidenceSha256']=p['review']['sha256']
 cases.append({'name':name,'planId':p['planId'],'scope':p['scope'],'home':str(home),'scenario':scenario});return folder,p

def inputs(folder,p,approval_edit=None,raw=None):
 pb=encode(p) if raw is None else raw;ph=sha(pb);instruction='EXECUTE_OFFLINE_PERMIT '+ph
 a={'schema':'VIDEOKIT_RUNNER_APPROVAL_EVIDENCE_V1','mode':'OFFLINE_FIXTURE','evidenceKind':'OFFLINE_TEST_ONLY','sourceThreadId':'01a107c3-2bf9-7fa0-94a0-234258ca6774','sourceTurnId':str(uuid.uuid4()),'instructionText':instruction,'instructionSha256':sha(instruction.encode()),'approvedPermitSha256':ph}
 if approval_edit:approval_edit(a)
 save(folder/'approval.json',a);(folder/'permit.json').write_bytes(pb)
 return ['fixture',str(folder/'permit.json'),ph,str(folder/'approval.json'),sha((folder/'approval.json').read_bytes())]

def construct(args):
 r=ProductionRunner(*args);runners.append(r);return r

def rejection(fn):
 try:fn()
 except (ValueError,TypeError,KeyError) as e:return str(e)
 raise AssertionError('EXPECTED_REJECTION')

def cli(args):
 mode,pp,ph,ap,ah=args
 return child([PY,'-I','-X','utf8','-B',str(B/'tools/production_runner.py'),'--mode',mode,'--permit',pp,'--permit-sha256',ph,'--approval',ap,'--approval-sha256',ah])

def default_deny():
 out=[]
 for argv in ([],['--mode','live']):
  code,b,e=child([PY,'-I','-X','utf8','-B',str(B/'tools/production_runner.py'),*argv]);assert code==2 and not e;out.append(decode(b))
 f,p=permit('live-reject-offline');args=inputs(f,p);args[0]='live';code,b,e=cli(args);assert code==2 and not e and not Path(p['home']).exists();out.append(decode(b))
 return {'rejections':out,'protectedQueries':0,'sdk':0}

def authority():
 edits=[('unapproved',lambda p:p.__setitem__('approvedForExecution',False)),('expired',lambda p:p.update(notBeforeUtc='2026-01-01T00:00:00+00:00',expiresUtc='2026-01-01T00:05:00+00:00')),('future',lambda p:p.update(notBeforeUtc='2090-01-01T00:00:00+00:00',expiresUtc='2090-01-01T00:05:00+00:00')),('scope',lambda p:p.__setitem__('scope','0'*64)),('runner-source',lambda p:p['sources'].__setitem__('tools/production_runner.py','0'*64)),('role',lambda p:p['roles'][0]['argv'].append('UNAUTHORIZED')),('bool-role',lambda p:p['roles'][0].__setitem__('ordinal',True)),('float-budget',lambda p:p['limits'].__setitem__('sdkChildren',7.0)),('extra-operation',lambda p:p['operations'].append('restart_server')),('product',lambda p:p['product'].__setitem__('version','WRONG')),('wrong-path',lambda p:p.__setitem__('home',str(W.parent/'outside-root'))),('missing',lambda p:p.pop('limits')),('extra',lambda p:p.__setitem__('unreviewed',True)),('wrong-mode',lambda p:p.__setitem__('mode','LIVE')),('attempt-retry',lambda p:p['limits'].__setitem__('retry',1))]
 edits += [('legacy-permit',lambda p:p.__setitem__('schema','VIDEOKIT_PRODUCTION_RUNNER_PERMIT_V1')),('missing-backend',lambda p:p.pop('routeBackend')),('wrong-backend',lambda p:p.__setitem__('routeBackend','CIM')),('bool-backend',lambda p:p.__setitem__('routeBackend',True))]
 out=[]
 for name,edit in edits:
  f,p=permit('deny-'+name);edit(p);args=inputs(f,p);msg=rejection(lambda:construct(args));assert not (f/'actual-home').exists();out.append({'case':name,'rejection':msg})
 for name,edit in [('approval-hash-relation',lambda a:a.__setitem__('approvedPermitSha256','0'*64)),('fixture-as-live-evidence',lambda a:a.__setitem__('evidenceKind','COORDINATOR_EXECUTION_ORDER')),('wrong-issuer-source',lambda a:a.__setitem__('sourceThreadId',str(uuid.uuid4())))]:
  f,p=permit(name);args=inputs(f,p,edit);msg=rejection(lambda:construct(args));assert not Path(p['home']).exists();out.append({'case':name,'rejection':msg})
 f,p=permit('duplicate-json');raw=encode(p).replace(b'"retry":0',b'"retry":0,"Retry":0');args=inputs(f,p,raw=raw);out.append({'case':'nested-case-duplicate','rejection':rejection(lambda:construct(args))});assert not Path(p['home']).exists()
 f,p=permit('wrong-external-digest');args=inputs(f,p);args[2]='0'*64;out.append({'case':'command-fixed-hash','rejection':rejection(lambda:construct(args))});assert not Path(p['home']).exists()
 assert not RUNNER_CUSTODY;return out

def full_cli():
 global positive
 f,p=permit('full-entry');args=inputs(f,p);code,b,e=cli(args);save(f/'original-entry-return.json',{'argvMode':'fixture','exitCode':code,'stdoutSha256':sha(b),'stderrSha256':sha(e),'originalWaitReadersStreamsHandleReturned':True});(f/'entry-stdout.bin').write_bytes(b);(f/'entry-stderr.bin').write_bytes(e)
 assert code==0 and not e,(code,b,e)
 terminal=decode(b);root=Path(p['evidenceRoot']);assert terminal['rolesCompleted']==7 and terminal['initialProofUnchanged'] and terminal['claimRelease']['originalUnlockCloseReturned']
 pr=decode((root/'pre_sdk_local_gate-completion-proof.json').read_bytes());m=decode((root/'runner-materialization.json').read_bytes());ad=decode((root/'identity-owner-admission.json').read_bytes());co=decode((root/'identity-console.bin').read_bytes());act=decode((Path(p['home'])/'release/activation.json').read_bytes());policy=decode((Path(p['home'])/'release/capture-policy.json').read_bytes())
 assert act['initialPredecessorProofSha256']==sha((root/'pre_sdk_local_gate-completion-proof.json').read_bytes())==terminal['initialProofSha256']
 assert act['freshRouteProofSha256']==sha((root/'fresh-route.json').read_bytes())==policy['freshRouteProof']['sha256']
 assert sha((Path(p['home'])/'release/activation.json').read_bytes())==policy['authorization']['sha256']==m['activationSha256']
 h=ad['runnerHandoff'];assert h['postControlBytes']==m['controlBeforeReceipt']+m['receiptWriteBytes']>0 and h['receiverControlBytes']>0
 assert pr['scopeStartTick']==m['scopeStartTick']==co['scopeStartTick']==terminal['scopeStartTick']
 assert co['batchGroups']['control']>pr['batchGroups']['control']+h['postControlBytes']+h['receiverControlBytes']>0
 assert terminal['batchControlBytesKnown']<=1048576 and terminal['totalLogicalInboundBytesKnown']<=3276800
 last=decode((root/'scope_all-completion-proof.json').read_bytes());assert last['nextId']=='END' and terminal['batchControlBytesKnown']==last['batchGroups']['control']+terminal['terminalWriteBytes']
 code2,b2,e2=cli(args);assert code2==2 and not e2 and 'FRESH_ONCE_EXACT_HOME' in decode(b2)['reason'];positive=(f,p,args)
 return {'terminal':terminal,'initialControl':pr['batchGroups']['control'],'firstControl':co['batchGroups']['control'],'postDelta':h,'sameOriginalPID':ad['ownerPid'],'firstLogicalReads':co['logicalControlReads'],'repeatAdmissionRejected':decode(b2),'originalEntryProcessObservedReturned':True,'actualSDK':0}

def ps_post_guards():
 f,p,args=positive;root=Path(p['evidenceRoot']);home=Path(p['home']);ad=decode((root/'identity-owner-admission.json').read_bytes());items=[]
 def add(name,edit):
  d=copy.deepcopy(ad);edit(d);fp=f/(name+'-admission.json');save(fp,d);items.append({'name':name,'path':str(fp)})
 add('good',lambda d:None)
 add('post-reset',lambda d:d['runnerHandoff'].__setitem__('postControlBytes',0))
 add('post-duplicate',lambda d:d['runnerHandoff'].__setitem__('postControlBytes',2*d['runnerHandoff']['postControlBytes']))
 add('receiver-reset',lambda d:d['runnerHandoff'].__setitem__('receiverControlBytes',1))
 add('wrong-event',lambda d:d['runnerHandoff'].__setitem__('eventId','0'*64))
 add('wrong-source',lambda d:d['runnerHandoff'].__setitem__('runnerSourceSha256','0'*64))
 add('wrong-holder',lambda d:d['runnerHandoff'].__setitem__('ownerPid',d['ownerPid']+1))
 add('wrong-mode',lambda d:d['runnerHandoff'].__setitem__('kind','LIVE'))
 add('bool-post',lambda d:d['runnerHandoff'].__setitem__('postControlBytes',True))
 add('extra',lambda d:d['runnerHandoff'].__setitem__('unreviewed',True))
 source=(B/'tools/capture_android02.ps1').read_text();prefix=source[source.index("$ErrorActionPreference='Stop'"):source.index('$policyPath=')]
 sp=home/'tools/post-guard-host.ps1'
 script=prefix+"\n$root='"+str(root)+"';$policyPath='"+str(home/'release/capture-policy.json')+"';$policy=ReadJsonExact $policyPath @() 65536;$script:policyBodyBytes=$script:lastJsonBytes.Length;$script:activationStartupBytes=0;$slots=@($policy.slots);$fixture=$true;$proof=ReadJsonExact '"+str(root/'pre_sdk_local_gate-completion-proof.json')+"' @() 4096;$PredecessorProofSha=Digest '"+str(root/'pre_sdk_local_gate-completion-proof.json')+"';$script:initialGateReceipt=ReadJsonExact '"+str(root/'gate-original-return.json')+"' @() 16384\n"
 script+="$cases='"+json.dumps(items,separators=(',',':')).replace("'","''")+"'|ConvertFrom-Json;$all=@();foreach($case in $cases){$ad=ReadJsonExact $case.path @() 8192;try{$n=CheckRunnerMaterialization $ad $policy $proof $true;$all+=@{name=$case.name;accepted=$true;readBytes=$n}}catch{$all+=@{name=$case.name;accepted=$false;error=$_.Exception.Message}}}\n"
 script+="$final=@();foreach($name in @('good','proof-window','gate-window','whole-window','expired','future-proof','bool-tick')){$ad=ReadJsonExact '"+str(root/'identity-owner-admission.json')+"' @() 8192;$now=[Environment]::TickCount64;$ad.runnerHandoff.scopeStartTick=$now-1000;$ad.runnerHandoff.initialProofStartTick=$now-500;$ad.runnerHandoff.permitExpiresUtc=[DateTimeOffset]::UtcNow.AddSeconds(10).ToString('o');$idx=0;switch($name){'proof-window'{$ad.runnerHandoff.scopeStartTick=$now-15000;$ad.runnerHandoff.initialProofStartTick=$now-10100};'gate-window'{$ad.runnerHandoff.scopeStartTick=$now-30100};'whole-window'{$ad.runnerHandoff.scopeStartTick=$now-600100;$idx=6};'expired'{$ad.runnerHandoff.permitExpiresUtc=[DateTimeOffset]::UtcNow.AddSeconds(-1).ToString('o')};'future-proof'{$ad.runnerHandoff.initialProofStartTick=$now+1000};'bool-tick'{$ad.runnerHandoff.initialProofStartTick=$true}};try{RunnerFinalStartGate $ad $policy $ad.runnerHandoff.scopeStartTick $idx $true;$final+=@{name=$name;accepted=$true}}catch{$final+=@{name=$name;accepted=$false;error=$_.Exception.Message}}};@{post=$all;finalStart=$final}|ConvertTo-Json -Depth 8 -Compress\n"
 sp.write_text(script,encoding='utf-8');code,out,err=child([PS,'-NoProfile','-NonInteractive','-File',str(sp)]);assert code==0 and not err,(code,out,err);facts=decode(out)
 for rows in (facts['post'],facts['finalStart']):assert rows[0]['accepted'] and all(not x['accepted'] for x in rows[1:]),rows
 save(f/'post-guards-result.json',facts);return facts

def changed_materialization():
 f,p=permit('changed-original-materialization');r=construct(inputs(f,p));r.consumed=True;r.prepare_home();r.materialize();fp=r.root/'runner-materialization.json';original=fp.read_bytes();(f/'materialization-before-change.bin').write_bytes(original)
 def change():
  stream=fp.open('ab');r.held.append(stream);n=stream.write(b' ');stream.flush();stream.close();return n
 x=r.operation('fixture-change-own-materialization',change);r.event('post','fixture-change-own-materialization',x['value'])
 from outer_owner import Owner
 msg=rejection(lambda:Owner(r.home,r.gate,r));r.fail(msg);release=r.gate.release();RUNNER_CUSTODY.remove(r)
 assert msg=='MATERIALIZATION_ORIGINAL_PENDING_OR_BYTES' and not list(r.root.glob('*-entered.json'));return {'rejection':msg,'release':release,'originalBeforeHash':sha(original),'afterHash':sha(fp.read_bytes())}
