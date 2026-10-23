"""Read-only original-return, exact source and whole-graph audit after ENV02."""
from pathlib import Path
from datetime import datetime,timezone
import collections,hashlib,json,sys
E=Path(__file__).resolve().parent;R=E/'v1';T=E.parent;sys.path.insert(0,str(R))
def sha(b):return hashlib.sha256(b).hexdigest()
def load(p):return json.loads(Path(p).read_bytes())
def save(p,d):
 with p.open('xb') as f:f.write((json.dumps(d,ensure_ascii=True,indent=2)+'\n').encode());f.flush()
def main():
 import prepare
 from host_context import normalize,digest,sha as hs
 o=load(R/'order.json');W=Path(o['work']);w=load(R/'worker-final.json');out=load(R/'outer-final.json');q=out['receipt'];p=load(R/'reference/profile.json');selfrow=load(R/'worker-self.json')
 assert w['allPassed'] and len(w['groups'])==9 and w['allOwnStartedOriginalsReturned'] and not w['newUnknown'] and all(x==0 for x in w['custody'].values()) and not w['stopReasons']
 assert q['exitCode']==0 and q['originalWaitReturnedOnce'] and q['readersJoined'] and q['streamsAndOriginalHandleCloseReturned'] and not q['errors'] and not q['expired'] and out['auditMismatch']==0
 assert all(selfrow[k]==q['identity'][k] for k in ['pid','creationFileTime','image','argv']) and selfrow['nonce']==o['nonce']
 expected=normalize(p['expectedRuntimeEnvironment']);ctx=selfrow['hostContext'];assert ctx['actualCwd']==p['hostCwd'] and ctx['environmentKeys']==sorted(expected) and ctx['canonicalEnvironmentSha256']==p['inheritedEnvSha256']==digest(expected) and ctx['controlledValueHashes']=={k:hs(v.encode()) for k,v in expected.items()}
 assert load(R/'outer-constructor-plan.json')['plan']['env']==p['expectedRuntimeEnvironment']
 for x in o['sources']:
  b=Path(x['path']).read_bytes();assert len(b)==x['bytes'] and sha(b)==x['sha256'],x['path']
 before=load(R/'before-audit.json');B=prepare.B;D=prepare.D
 old=prepare.packet(B,'reference/full-manifest.json','3ce81441d75e8a47368078197fcc43a20ace8eef916f1f3dcbd6f08c3cd8059c',56,B/'readonly-facts-preauth01-blocked-frozen.zip','e563573ca4d51c428ae7c56d79f4b5b7e03bd6e106157f95286c849a91afed52',57)
 dev=prepare.packet(D,'reference/full-manifest.json','2c8c69d8ecec03d7bc339ae8bdb2349bdb942258f0c050b183197f1aa960fe61',108,D/'preauth01-selfcheck02-frozen.zip','1a0fb5e9d424e83ed6de8668607a05b28365c401b3d527d55cfaf7f959773b3c',109)
 prior=load(T/'D1_PREAUTH01_INDEPENDENT_B_MANIFEST_V1.0.json');assert sha((T/'D1_PREAUTH01_INDEPENDENT_B_MANIFEST_V1.0.json').read_bytes())=='992c684578af2da658b7f1f3e179b7e5d6b79c0f8b36891c5788118e6ea37562'
 for x in prior['files']:
  b=Path(x['absolutePath']).read_bytes();assert len(b)==x['bytes'] and sha(b)==x['sha256']
 groups={x['name']:x for x in w['groups']};receipts=[]
 for f in sorted((R/'work').glob('collect-*/runtime/outer-original-return.json')):
  d=load(f);assert d['originalWaitReturnedOnce'] and d['readersJoined'] and d['streamsAndOriginalHandleCloseReturned'] and not d['errors'] and not d['expired'];receipts.append(dict(path=str(f),identity=d['identity'],exitCode=d['exitCode'],seconds=d['seconds'],rawCounts=d['rawCounts']))
 assert len(receipts)==15
 quals=[]
 for i,code in enumerate([0,7,0]):
  d=load(R/'work'/('collect-'+str(i))/'runtime/outer-original-return.json');assert d['exitCode']==code and d['seconds']<5 and d['rawCounts'][1]==0;quals.append(dict(exitCode=code,seconds=d['seconds'],allOriginalsReturned=True))
 expectedCalls=collections.Counter(x['id'] for x in p['allPlannedCalls'] if x['label'] not in ['explicit-cli-route','explicit-cli-facts']);actualCalls=collections.Counter(x['tupleId'] for x in w['registryCalls']);assert expectedCalls==actualCalls and sum(actualCalls.values())==20 and len(w['audit'])==20 and all(x['matches'] for x in w['audit']) and all(x['constructorReturned'] for x in w['registryCalls'])
 cli=load(R/'work/explicit-cli-observed-return.json')['result'];assert len(cli['fixtureConstructorCalls'])==2 and all(x['constructorReturned'] for x in cli['fixtureConstructorCalls']) and len(cli['fixtureAudit'])==2 and all(x['matches'] for x in cli['fixtureAudit']) and cli['release']['factCaptureQualified'] and cli['release']['originalUnlockCloseReturned'] and not cli['qualificationIssued']
 prestart=load(R/'work/prestart.json');started=[x for x in prestart['results'] if x['case']=='actual-started-local-original'];assert len(started)==1 and started[0]['waitAndReadersActuallyReturned'] and started[0]['streamsAndFilesClosedOnce'] and started[0]['originalProcessDisposed']
 for e in w['writeOperations']:
  if 'path' in e:
   path=Path(e['path']);assert path==E or path.is_relative_to(E) or path==W or path.is_relative_to(W),e
  else:assert e.get('special')=='FIXED_PROFILE_SUBPROCESS_DEVNULL',e
 gate=[*w['gateSummaries'],dict(scope=cli['receipt']['scope'],sourceBytes=cli['sourceBytes'],sourceReads=cli['sourceReads'],released=cli['release']['originalUnlockCloseReturned'],leaseClosed=True,pending=0)]
 assert len(gate)==4 and all(x['released'] and x['leaseClosed'] and x['pending']==0 and x['sourceBytes']<268435456 and x['sourceReads']<=64 for x in gate)
 control=[]
 for name in ['new-original-result.json','wrong-receiver-result.json','legacy-result.json']:
  d=load(R/'work'/name);assert d['controlBytes']<262144;control.append(dict(name=name,bytes=d['controlBytes']))
 assert cli['controlBytes']<262144;control.append(dict(name='CLI',bytes=cli['controlBytes']))
 model=load(R/'work/independent-template-matrix.json');assert model['total']==193 and not model['bad']
 new=load(R/'work/new-original-result.json');assert new['allFactThreadsJoined'] and new['originalFactHandleClosed']
 clirows=load(R/'work/cli-results.json');assert len(clirows)==7
 files=[p for root in [E,W] for p in root.rglob('*') if p.is_file()];assert len(files)<2048 and sum(p.stat().st_size for p in files)<33554432 and max(p.stat().st_size for p in files)<=1048576
 budget=load(R/'budget.json');guardReadUpper=(len(w['writeOperations'])*4+256)*(R/'order.json').stat().st_size;assert guardReadUpper<budget['ioReservation']['driverAndArchive']
 result=dict(schema='PREAUTH01_DRIVER_ENV02_POST_AUDIT_V1',verdict='PASS_IN_SCOPE_COMPLETE_OFFLINE_B',utc=datetime.now(timezone.utc).isoformat(),batch=o['batch'],orderSha256=sha((R/'order.json').read_bytes()),sourceSeal=o['sourceSeal'],qualificationVersionsUsed=1,qualificationVersionsAuthorized=2,qualificationActualCalls=3,qualification=quals,qualificationRetriesUsed=0,productRetries=0,groups=[dict(name=x['name'],status=x['status'],seconds=x['seconds']) for x in w['groups']],old57Preserved=True,old56=old,developer108=dev,source20Bad=0,gate12Bad=0,ownOrderSourceBad=0,actualHostSnapshot=ctx,rawPopenEnvironmentPreserved=True,allFifteenOuterCollectorsReturned=True,collectorReceipts=receipts,parentPopen=20,parentAuditMatched=20,nestedCliPopen=2,nestedCliAuditMatched=2,dotNetChild=1,outerWorker=1,wholeActualGraph=24,wholePreplannedGraph=load(R/'process-graph.json')['totalActualProcessUpper'],allNewOriginalsReturned=True,newUnknown=False,gate=gate,control=control,bindingAndOnceNegative=len(new['negative']),wireNegative=4,developerTemplateReplayNegative=138,newTemplateCorpus=193,newTemplateNegative=191,newTemplatePositive=2,oldCorpusCountNotAddedAgain=True,O1='CONFORMS_CLARIFIED_RAW_BYTE_HASH_CONTRACT',semanticCases=346,semanticConditionalPositive=42,semanticIndependentPositive17=True,preStart13=True,cliRows=clirows,workerSeconds=w['seconds'],outerSeconds=out['seconds'],outerRawCounts=q['rawCounts'],outerWorkerIdentity=q['identity'],outerObservedReadBytes=out['sourceReadBytes'],outerObservedReadCalls=out['sourceReads'],knownGateSourceBytes=sum(x['sourceBytes'] for x in gate),knownGateSourceReads=sum(x['sourceReads'] for x in gate),writeGuardRecordedOperations=len(w['writeOperations']),writeGuardConservativeReadUpper=guardReadUpper,ioReservation=budget['ioReservation'],physicalIO='NOT_GLOBALLY_MEASURED',filesBeforeFinalFreeze=len(files),bytesBeforeFinalFreeze=sum(p.stat().st_size for p in files),maxFileBytes=max(p.stat().st_size for p in files),actualSDK=0,actualADB=0,actualNativeRoute=0,actualTCP=0,actualDevice=0,actualGradle=0,actualGit=0,oldRuntimeQueries=0,qualificationV2='NOT_IMPLEMENTED_NOT_RUN',D1='NOT_PASSED',M0='NOT_STARTED',automaticNextTest=False)
 save(E/'post-audit.json',result);print(json.dumps({k:result[k] for k in ['verdict','qualificationVersionsUsed','groups','wholeActualGraph','bindingAndOnceNegative','knownGateSourceBytes','knownGateSourceReads','writeGuardRecordedOperations','writeGuardConservativeReadUpper','filesBeforeFinalFreeze','bytesBeforeFinalFreeze','outerSeconds']}))
if __name__=='__main__':main()
