"""Tester independent read-only byte/provenance audit; verifier only, no candidate tests/JAR/build/device."""
from pathlib import Path
import hashlib,json,os,re,subprocess,sys,zipfile
from datetime import datetime,timezone
R=Path(__file__).resolve().parents[3];O=Path(__file__).resolve().parent;B=R/'docs/coder/d1e13c';E=B/'evidence';C=[]
PIN='14358fdb7e7900de669e76965c4ecce5b008eb8daea216b9abaa7f7891e45762'
def sha(b):return hashlib.sha256(b).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def ck(n,v,d=None):C.append(dict(name=n,passed=bool(v),detail=d))
def verify(row,n):
 raw=(R/row['path']).read_bytes();ck(n,len(raw)==row['bytes'] and sha(raw)==row['sha256'],row['path'])
sealpath=E/'e13c-freeze.json';seal=load(sealpath)
ck('external seal',sha(sealpath.read_bytes())==PIN);ck('141 immutable records',len(seal['immutableFiles'])==141)
for row in seal['immutableFiles']:verify(row,'E13C frozen')
ck('approved archive',seal['archive']['sha256']=='1365dfa17cfaab28e9f4c2c8639bf204a95a0ca4949e837b6c77d3bfb0ced4d9');verify(seal['archive'],'archive pin')
with zipfile.ZipFile(R/seal['archive']['path']) as z:
 expected={p['path']:p for p in seal['immutableFiles'] if p['path']!=seal['archive']['path']}
 ck('140 exact ZIP members',len(z.namelist())==140 and len(set(z.namelist()))==140 and set(z.namelist())==set(expected))
 for n in z.namelist():ck('ZIP member bytes',len(z.read(n))==expected[n]['bytes'] and sha(z.read(n))==expected[n]['sha256'],n)
for old in seal['priorSeals']:
 verify(old['seal'],'old seal')
 for p in load(R/old['seal']['path'])['immutableFiles']:verify(p,'old frozen')
for p in load(E/'requirements-and-review-pins.json')['files']:verify(p,'requirements and reviews')
oldRun=R/'docs/tester/D1_E13A_E13B_TABLET_EXECUTION/db65c958-5163-4467-90e0-6f099076142f'
oldManifest=load(oldRun/'evidence/execution-manifest.json')
for p in oldManifest['files']:verify(p,'old failed execution retained')
ck('old real once still absent',not (oldRun/'deployment/e13a-activation-deployment.once').exists())
bind=load(B/'release/candidate-binding.json');plan=load(B/'release/device-plan.json');draft=load(B/'release/new-scope-draft.json')
for p in bind['targetApks']+[bind['hostJar'],bind['baseHostJar'],bind['metadataManifest'],bind['metadataOverlaySeal']]:verify(p,'bound artifact')
ck('exact new host JAR',bind['hostJar']['sha256']=='9c36d04a728a5a5b6db04ab1ffbe3f5be051b84f249d8bdf868212ed03ef774c')
j=load(E/'host-jar-manifest.json');baseJ=load(R/'docs/coder/d1e13a/evidence/host-jar-manifest.json');baseRows={r['entry']:r for r in baseJ['classes']};compiled=base=byteSame=0
with zipfile.ZipFile(R/j['jar']['path']) as z,zipfile.ZipFile(R/j['baseJar']['path']) as old:
 ck('173 exact production entries',len(z.namelist())==173 and len(set(z.namelist()))==173 and set(z.namelist())=={r['entry'] for r in j['classes']})
 ck('no candidate selfcheck classes',not any(any(k in n for k in ['E13COnceCheck','E13CUnknownCheck','E13ProductionCheck','E13ABindingCheck','E13SourceCases','substitute']) for n in z.namelist()))
 for row in j['classes']:
  data=z.read(row['entry']);verify(row['source'],'class source pin');ck('class bytes',len(data)==row['bytes'] and sha(data)==row['sha256'],row['entry'])
  if row['entry'] in baseRows and data==old.read(row['entry']):byteSame+=1
  if row['relationship']=='EXACT_BASE_JAR_MEMBER':
   base+=1;ck('exact inherited member/source',data==old.read(row['entry']) and row['source']==baseRows[row['entry']]['source'],row['entry'])
  else:
   compiled+=1;top=row['entry'][:-6].split('$')[0];ck('only approved two sources recompiled',top in ['com/videokit/spike/e4/E11DeploymentOnce','com/videokit/spike/e4/E13HostActivationSession'])
   local=B/'.checks/production'/row['entry'];ck('original compiled member equals shipped',local.read_bytes()==data,row['entry'])
 ck('168 inherited plus5 recompiled',base==168 and compiled==5)
 ck('actual shipped factory call and names',b'e13Activation' in z.read('com/videokit/spike/e4/E13HostActivationSession.class') and b'e13a-activation-deployment.once' in z.read('com/videokit/spike/e4/E11DeploymentOnce.class'))
for p in load(E/'host-build-001/inputs.json')['sources']:verify(p,'production build source')
ck('host compile natural exit0',load(E/'host-build-001/compile.exit.json')['exitCode']==0)
tests=load(E/'host-checks-001/results.json');helperNames=['E13_OK','E11_OK','E13_OLD_NAME','E11_NEW_NAME','ARBITRARY','WRONG_INTENT','FORCE_FAIL','CLOSE_IN_FLIGHT'];cli=[]
for r in tests['results']:
 for s in ['stdout','stderr']:verify(r[s],'original host test raw')
 ck('recorded original natural return',r['naturalReturn'],r['name'])
 if r['name'] in helperNames:ck('helper recorded pass',r['exitCode']==0 and 'PASS '+r['name'] in (R/r['stdout']['path']).read_text(),r['name'])
 if r['name'].startswith('CLI_'):
  cli.append(r);text=(R/r['stderr']['path']).read_text();ck('public CLI controlled exit1 and real pcClosed',r['exitCode']==1 and '"kind":"pcClosed"' in text and '"allOriginalsReturned":"true"' in text,r['name'])
ck('8 helper /8 actual CLI attempts',len([r for r in tests['results'] if r['name'] in helperNames])==8 and len(cli)==8)
first=E/'host-checks-001/cli-fixtures/CLI_E13_EXACT';args=(first/'first-sdk-argv.txt').read_text().splitlines()
ck('exact first SDK boundary no child',args==['D:\\Android\\SDK\\platform-tools\\adb.exe','-s','HA1Q6WXR','shell','run-as','com.videokit.app','stat','-c','%u:%i','.'] or args==['D:/Android/SDK/platform-tools/adb.exe','-s','HA1Q6WXR','shell','run-as','com.videokit.app','stat','-c','%u:%i','.'])
localConfig=(first/'local-test-config.json').read_bytes();intent=load(first/'e13a-activation-deployment.once')['fields']
ck('local CLI once binds exact config and role',intent['kind']=='e13ActivationDispatchIntent' and intent['config']==sha(localConfig))
for r,needle in [('CLI_E13_EXACT','E13C_LOCAL_FIRST_SDK_BOUNDARY_NO_CHILD'),('CLI_E13_EXACT-cross-jvm-repeat','E11_DEPLOYMENT_ALREADY_RESERVED_NO_RETRY'),('CLI_E13_WRONG_NAME','E13_NEW_FIXED_ONCE_REQUIRED'),('CLI_E13_ARBITRARY','E13_NEW_FIXED_ONCE_REQUIRED'),('CLI_WRONG_CONFIG_ROLE','E13_CONFIG_SCHEMA'),('CLI_SYNTHETIC_DEVICE_GATE_REJECTED','E13_REAL_REGISTRY_REQUIRED'),('CLI_PARTIAL_FILE','E11_DEPLOYMENT_ALREADY_RESERVED_NO_RETRY'),('CLI_EMPTY_FILE','E11_DEPLOYMENT_ALREADY_RESERVED_NO_RETRY')]:ck('actual CLI refusal/boundary',needle in (E/'host-checks-001'/f'{r}.stderr.txt').read_text(),r)
for name in ['CLI_E13_WRONG_NAME','CLI_E13_ARBITRARY','CLI_WRONG_CONFIG_ROLE','CLI_SYNTHETIC_DEVICE_GATE_REJECTED','CLI_PARTIAL_FILE','CLI_EMPTY_FILE']:ck('refused CLI has no SDK boundary marker',not (E/'host-checks-001/cli-fixtures'/name/'first-sdk-argv.txt').exists(),name)
closeRaw=(E/'host-checks-001/CLOSE_IN_FLIGHT.stderr.txt').read_text();ck('actual in-flight keeper and natural closure','"kind":"pcIsolationAck"' in closeRaw and 'NON_DAEMON_ORIGINAL_SUPERVISOR' in closeRaw and 'actualOriginalReturns=true' in closeRaw)
unknown=load(E/'unknown-jar-002/results.json');raw=(E/'unknown-jar-002/unknown.stdout.txt').read_text();ck('exact shipped helper UNKNOWN source',len(unknown['helperClassLoadLines'])==4 and all(line in raw and 'e13c-host-tools.jar' in line for line in unknown['helperClassLoadLines']))
ck('UNKNOWN limited truthful scope',unknown['supervisor']=='FINITE_RETENTION_SUBSTITUTE_ONLY' and not unknown['actualCustodianUnknownClaim'] and not unknown['actualHelperRecompiled'] and not unknown['originalCloseAcknowledged'] and unknown['closeAttempts']==1 and not unknown['secondClose'] and unknown['dispatch']==0 and 'holder=UNKNOWN originalReturn=false dispatch=0 closeAttempts=1 noSecondClose=true' in raw)
ck('unknown JVM natural exit0',load(E/'unknown-jar-002/unknown.exit.json')['exitCode']==0)
bud=plan['executionBudgetProposal'];ck('new fresh batch not replay',plan['newBatchRequired'] and plan['freshM1Required'] and not plan['oldBatchRemainingBudgetReusable'] and draft['scopeId'] is None and draft['actualScope'] is None and bind['actualApprovedScope'] is None and bind['sourceReview'] is None and bind['actualRelease'] is None and bind['actualOnce'] is None)
ck('v17 source15 and exact new once',bind['version']==17 and bind['acceptedSourceVersion']==15 and bind['onceBasename']=='e13a-activation-deployment.once' and '<NEW_SCOPE_UUID>' in draft['oncePathTemplate'])
ck('new budget50 not old56',sum(bud[k] for k in ['deploymentEntry','deploymentChildren','caseJavaEntries','caseInstrumentChildren','metadataClients'])==bud['successfulPathOperations']==48 and bud['maximumOperations']==50 and bud['additionalPreDeployOccupiedM1Rechecks']==2 and bud['recheckSpacingMinimumMinutes']==30 and bud['recoveryOperations']==0 and bud['extraPcQueries']==0 and not bud['oldBatch37of56BalanceInherited'])
ck('text2MiB independent',bud['successfulPathAllocatedText']==1638400 and bud['twoOccupiedM1TextReserve']==131072 and bud['totalTextAllocated']==1769472 and bud['remainingText']==327680 and bud['textTotal']==2097152)
def snapshot():
 paths={R/r['path'] for r in seal['immutableFiles']}|{sealpath}
 for d,dirs,files in os.walk(B):
  dirs[:]=[x for x in dirs if x not in ['.checks','__pycache__']];paths.update(Path(d)/f for f in files)
 return {str(p.relative_to(R)):sha(p.read_bytes()) for p in paths if p.is_file()}
before=snapshot();runs=[]
for mode,args in [('default',[]),('verify',['verify','--seal-sha',PIN]),('help',['--help']),('pack-help',['pack','--help'])]:
 argv=[sys.executable,'-X','utf8','-B',str(B/'tools/package_delivery.py')]+args;p=subprocess.run(argv,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=30);(O/('readonly-'+mode+'.txt')).write_bytes(p.stdout)
 ck('readonly entry exit0',p.returncode==0,mode)
 if mode in ['default','verify']:ck('readonly verifier result',json.loads(p.stdout)['status']=='PASS_E13C_STRICT_READONLY_VERIFY',mode)
 runs.append(dict(mode=mode,argv=argv,exitCode=p.returncode,bytes=len(p.stdout),sha256=sha(p.stdout)))
ck('snapshot unchanged',before==snapshot(),len(before))
result=dict(atUtc=datetime.now(timezone.utc).isoformat(),status='PASS_INDEPENDENT_HOST_FIX_REVIEW_BYTES' if all(c['passed'] for c in C) else 'FAIL_INDEPENDENT_HOST_FIX_REVIEW_BYTES',checkCount=len(C),failed=[c for c in C if not c['passed']],checks=C,readonlyEntryRuns=runs,snapshotFilesUnchanged=len(before),jarProvenance=dict(inheritedMembers=base,recompiledMembers=compiled,byteIdenticalToBaseMembers=byteSame),deviceCalls=0,candidateTestsRerun=0,builds=0)
(O/'independent-audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:result[k] for k in ['status','checkCount','failed','snapshotFilesUnchanged','jarProvenance']},ensure_ascii=False))
