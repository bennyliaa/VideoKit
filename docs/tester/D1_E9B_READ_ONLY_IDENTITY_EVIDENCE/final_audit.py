"""Read saved real batch evidence only. No device or production program execution."""
import base64,collections,hashlib,json,pathlib,re
OUT=pathlib.Path(__file__).parent;ROOT=OUT.parents[2]
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(b):return hashlib.sha256(b).hexdigest()
def unpack(s):return base64.urlsafe_b64decode(s+'='*((-len(s))%4))
def fields(p):return read(p)['fields']
scope=read(OUT/'authorized-readonly-scope.json');index=read(OUT/'reviewed-config-command-index.json');config=fields(OUT/'reviewed-manager-config.json');plan=json.loads(unpack(config['plan']))['fields']
checks={}
checks['requirementsPin']=sha((ROOT/scope['requirements']).read_bytes())==scope['requirementsSha256']
checks['actualScopeAuthorizationPin']=config['authorization']==sha((OUT/'authorized-readonly-scope.json').read_bytes())==index['authorizationReferenceSha256']
checks['reviewPin']=config['review']==scope['sourceReview']==sha((ROOT/'docs/tester/D1_E9B_ARCHITECTURE_REVIEW_REPORT_V1.0.md').read_bytes())
checks['configAndPlanPins']=sha((OUT/'reviewed-manager-config.json').read_bytes())==index['configSha256'] and sha(unpack(config['plan']))==config['planSha']==index['planSha256']
checks['descriptorMatchesRealProduction']= (OUT/'reviewed-descriptor.json').read_bytes()==(OUT/'external-registry/descriptor.json').read_bytes()
checks['deviceEnvironmentNotSynthetic']=plan['environment']=='DEVICE_HA1Q6WXR'
artifact=ROOT/'docs/coder/d1e9b/artifacts/D1-20261018-E9B/final';checks['artifactPins']=all(sha((artifact/name).read_bytes())==h for name,h in index['artifactAllowlist'].items())
checks['candidateSealPin']=sha((ROOT/'docs/coder/d1e9b/evidence/e9b-freeze.json').read_bytes())=='6f8c1ffffa6bff17da48b7067594d33980c443ff03a7c547e917f0814add2c92'
intents=[read(p) for p in sorted(OUT.glob('session-*-intent.json'))];counts=collections.Counter(v['stage'] for v in intents)
checks['exactOnceAndNoForbiddenCommands']=all(counts[k]==1 for k in ['DEPLOY','LAUNCH','POLL','ARCHIVE','ACK','FINISH']) and set(counts)<={'DEPLOY','LAUNCH','POLL','ARCHIVE','ACK','FINISH','INSPECT'}
checks['commandPins']=all(sha((OUT/v['path']).read_bytes())==v['sha256'] for v in index['commandFiles'])
checks['explicitReadOnlyMode']=fields(OUT/'command-LAUNCH.json')['mode']=='READ_ONLY_IDENTITY'
registry=OUT/'external-registry';actor_raw=(OUT/'original-actor.json').read_bytes();proof_raw=(OUT/'original-identity-return.json').read_bytes();actor=json.loads(actor_raw)['fields'];proof=json.loads(proof_raw)['fields'];snapshot=fields(OUT/'original-snapshot.json');identity=read(OUT/'identity-independent-check.json')
checks['originalReturnArchivedExactly']=proof_raw==(registry/'actors/0001/returned.json').read_bytes()
checks['actorProofSnapshotBinding']=proof['actor']==snapshot['actor']==sha(actor_raw) and snapshot['returned']==sha(proof_raw)
checks['originalActorScope']=all(actor[k]==scope[k] for k in ['registry','migration','attempt','handle']) and actor['ordinal']=='1' and actor['environment']=='DEVICE_HA1Q6WXR'
checks['actualQualifiedIdentity']=proof['verdict']=='IDENTITY_QUALIFIED' and proof['phase']=='IDENTITY' and proof['unreturned']=='0' and proof['owned']=='2' and int(proof['identityNanos'])<10_000_000_000 and snapshot['safe']=='true'
checks['noCommitDeviceWriteAuthority']=proof['executeDone']=='false' and proof['device']=='ABSENT' and proof['deviceRecord']=='ABSENT' and snapshot['executeReserved']=='false'
checks['independentOSIdentity']=identity['independentOriginalPidAlive'] and identity['independentBootAndStartMatched'] and identity['start']==actor['start'] and identity['bootCount']==actor['boot']
commands=[json.loads(line)['fields'] for line in (registry/'actors/0001/commands.jsonl').read_text().splitlines()]
checks['exactAndroidCommandLedger']=len(commands)==3 and commands[0]['kind']=='launch' and [(v['seq'],v['command']) for v in commands[1:]]==[('1','STATUS'),('2','ACK_FINISH')]
checks['noReservationFinalOrActor2']=not any(p.exists() for p in [registry/'actors/0001/reserve.json',registry/'actors/0002',registry/'final.acceptance.json',registry/'final.seal.json',registry/'activation-release.json'])
responses=[read(p) for p in sorted(OUT.glob('session-*-response.json'))];ack=json.loads(next(v['reply'] for v in responses if v['stage']=='ACK'))['fields'];ack_state=json.loads(unpack(ack['snapshot']))['fields']
checks['ackSameExactReturn']=unpack(ack['returned'])==proof_raw and ack_state['returned']==sha(proof_raw) and ack_state['finishClaimed']=='true' and ack_state['commandSeq']=='2'
log=(registry/'logs/actor-0001.finish.log').read_bytes();text=log.decode('utf-8');anchor='E9_FINAL_FINISH handle='+actor['handle']+' actor='+sha(actor_raw)+' returned='+sha(proof_raw)
at=text.find(anchor);after=text[at+len(anchor):] if at>=0 else ''
checks['uniqueActualFinishAnchor']=text.count(anchor)==1
checks['normalAndroidFinishAfterAnchor']=bool(re.search(r'Force stopping com\.videokit\.app[^\n]*user=0: finished inst',after)) and bool(re.search(r'Killing '+actor['pid']+r'[^\n]*finished inst',after))
finish=fields(registry/'actors/0001/finish.json');checks['typedNormalFinish']=finish['actor']==sha(actor_raw) and finish['returned']==sha(proof_raw) and finish['evidence']==sha(log) and finish['disposition']=='NORMAL_FINISH_CONFIRMED'
head=sha((registry/'descriptor.json').read_bytes());events=[]
for line in (registry/'registry.events.jsonl').read_bytes().splitlines(keepends=True):
    e=json.loads(line)['fields'];ok=e['parent']==head and e['evidence']==sha((registry/e['path']).read_bytes());head=sha(line);events.append(dict(seq=e['seq'],state=e['state'],parentAndEvidenceValid=ok))
checks['readOnlyEventChain']=len(events)==2 and all(v['parentAndEvidenceValid'] for v in events) and [v['state'] for v in events]==['IDENTITY_ONLY_RETURN_NO_COMMIT','NORMAL_FINISH_CONFIRMED']
checks['noFinalMigrationHead']=not (registry/'registry.checkpoint.json').exists() and not (registry/'final.acceptance.json').exists()
queries=[read(p) for p in sorted(OUT.glob('pc-query-*-receipt.json'))];pc=[fields(p) for p in sorted(OUT.glob('pc-query-*-stdout.txt'))]
checks['twoReturnedLocalQueries']=len(queries)==2 and all(v['exitCode']==0 and v['originalClientReturned'] and v['pipesReturned'] for v in queries)
last=pc[-1];checks['production26QualifiedReturned']=last['operations']=='26' and last['unreturnedOperations']=='0' and last['liveProcesses']=='0' and last['nonqualifiedOperations']=='0' and last['unresolvedActors']=='0' and last['registryReturned']=='true' and last['registryOwned']=='0'
managerlog=(OUT/'manager-stderr.txt').read_text();checks['actualClosedOnce']=managerlog.count('E9_PC_CLOSED handle=')==1 and '"allOriginalsReturned":"true"' in managerlog and '"kind":"pcClosed"' in managerlog and 'E9_PC_ISOLATION_ACCEPTED' not in managerlog
receipt=read(OUT/'manager-final-client-receipt.json');host_absence=read(OUT/'final-host-manager-absence.json');checks['originalManagerAndControllerPipesReturned']=receipt['exitCode']==0 and receipt['stdoutReaderReturned'] and receipt['stderrReaderReturned'] and host_absence['absent']
checks['budgetCounts']=receipt['pcQueriesIssued']==2 and receipt['androidControlsIssued']==2 and receipt['androidStatusesIssued']==1
post=read(OUT/'postflight-result.json');checks['finalDeviceNoProcessAndDataInodes']=not post['relatedProcesses'] and all(v['dataInodeMatchesBefore'] for v in post['packages'])
metadata=[read(p) for p in sorted(OUT.glob('preflight-*-receipt.json'))];checks['metadataAllReturned']=len(metadata)==16 and all(v['exitCode']==0 and v['originalClientReturned'] and v['pipesReturned'] for v in metadata)
checks['noHostCompatibilityCorrection']=not list(OUT.glob('bridge-failure-*.json')) and not list(OUT.glob('*pending.json'))
files=[p for p in registry.rglob('*') if p.is_file()];meta=[p for p in files if not p.name.endswith('.log')];rawlogs=[p for p in files if p.name.endswith('.log')]
checks['registryAndLogBounds']=len(meta)<=20 and sum(p.stat().st_size for p in meta)<=155648 and sum(p.stat().st_size for p in rawlogs)<=1048576
result={'result':'PASS_FINITE_REAL_DEVICE_READ_ONLY_IDENTITY' if all(checks.values()) else 'AUDIT_MISMATCH','checks':checks,'actor':actor,'identityReturn':proof,'ackSnapshot':ack_state,'identityIndependent':identity,'scope':scope['handle'],'registry':scope['registry'],'readOnlyEventHead':head,'notMigrationFinalHead':True,'events':events,'sessionCommandCounts':dict(counts),'actualMetadataAdbClients':len(metadata),'productionOriginalProcesses':26,'productionLocalArtifactTools':5,'productionAdbClientsDerivedFromFrozenPort':21,'totalAdbClients':len(metadata)+21,'localQueries':len(queries),'androidControls':2,'androidStatuses':1,'metadataElapsedMaxSeconds':max(v['elapsedSeconds'] for v in metadata),'rawFinishLogBytes':len(log),'registryMetadataFiles':len(meta),'registryMetadataBytes':sum(p.stat().st_size for p in meta),'originalIdentityReturnSha256':sha(proof_raw),'actorSha256':sha(actor_raw),'normalFinishLogSha256':sha(log),'readOnlyConfigSha256':index['configSha256'],'descriptorSourceHashNote':{'indexValueIsNormalizedUtf8SourceSha256':index['descriptorSourceSha256'],'rawFrozenSourceSha256':sha((ROOT/'docs/coder/d1e9b/src/com/videokit/spike/e4/E9LegacyProfile.java').read_bytes())},'limits':{'pcStatusOpCleanup':16,'androidControls':8,'androidStatuses':3,'controlNs':5_000_000_000,'identityNs':10_000_000_000},'notRun':['ordinary-app DUMP negative test','KERNEL_BOOT_ID source','raw syscall/FD trace','faults/timeout/UNKNOWN injection','accept exhaustion','migration/COMMIT/activation','new-host current observation/product/media'],'D1':'NOT_PASSED','M0':'NOT_STARTED','longTermAdmission':'OPEN'}
(OUT/'independent-device-audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
ledger={'scope':scope,'configSha256':index['configSha256'],'planSha256':index['planSha256'],'sessionIntents':intents,'canonicalAndroidLedger':commands,'pcIdentity':read(OUT/'manager-runtime-identity.json'),'pcFinalClientReceipt':receipt,'independentHostManagerAbsence':host_absence,'metadataReceipts':metadata,'localQueryReceipts':queries,'inFlight':[] if all(checks.values()) else ['REVIEW_AUDIT_MISMATCH'],'noForceStopKillClearRestartOrRetry':True,'note':'Production process breakdown follows the frozen port and observed 21/26 operation counts; individual raw subprocess argv/stdout were not separately instrumented.'}
(OUT/'command-resource-ledger.json').write_text(json.dumps(ledger,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
inventory=[{'path':str(p.relative_to(OUT)).replace('\\','/'),'bytes':p.stat().st_size,'sha256':sha(p.read_bytes())} for p in sorted(OUT.rglob('*')) if p.is_file() and p.name not in {'evidence-manifest.json','coordinator-notification.json'}]
(OUT/'evidence-manifest.json').write_text(json.dumps({'scope':'E9B_READ_ONLY_IDENTITY_COMPLETED_DEVICE_EVIDENCE','files':inventory},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k not in ('actor','identityReturn','ackSnapshot','identityIndependent','notRun')},ensure_ascii=False))
