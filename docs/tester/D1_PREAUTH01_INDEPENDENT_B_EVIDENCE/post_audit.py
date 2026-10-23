"""File-only return audit and explicit-time template replay; no new batch start."""
from pathlib import Path
from datetime import datetime,timezone,timedelta
import collections,hashlib,json,sys,time
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R));B=R.parents[1]/'coder/d1android02-readonly-facts-preauth01';D=B.parent/'d1android02-readonly-facts-preauth01-selfcheck02'
def sha(b):return hashlib.sha256(b).hexdigest()
def load(p):return json.loads(Path(p).read_bytes())
def save(p,d):
 with p.open('xb') as f:f.write((json.dumps(d,ensure_ascii=True,indent=2)+'\n').encode());f.flush()
def main():
 start=time.monotonic();o=load(R/'order.json');out=load(R/'outer-final.json');q=out['receipt'];selfrow=load(R/'worker-self.json');W=Path(o['work']);errors=bytes.fromhex(load(R/'runtime/outer-stderr-0.json')['hex']).decode()
 assert q['exitCode']==1 and q['originalWaitReturnedOnce'] and q['readersJoined'] and q['streamsAndOriginalHandleCloseReturned'] and not q['errors'] and not q['expired'] and not out['newUnknown'] and out['auditMismatch']==0
 assert all(selfrow[k]==q['identity'][k] for k in ['pid','creationFileTime','image','argv']) and selfrow['nonce']==o['nonce']
 assert 'ValueError: PROFILE_HOST_ENV_CWD' in errors and "for x in reg.p['allPlannedCalls']" in errors
 assert not W.exists() and not list(R.glob('group-*.json')) and not (R/'worker-final.json').exists()
 assert not list((R/'work').glob('collect-*'))
 for x in o['sources']:
  b=Path(x['path']).read_bytes();assert len(b)==x['bytes'] and sha(b)==x['sha256'],x['path']
 import prepare
 old=prepare.packet(B,'reference/full-manifest.json','3ce81441d75e8a47368078197fcc43a20ace8eef916f1f3dcbd6f08c3cd8059c',56,B/'readonly-facts-preauth01-blocked-frozen.zip','e563573ca4d51c428ae7c56d79f4b5b7e03bd6e106157f95286c849a91afed52',57)
 dev=prepare.packet(D,'reference/full-manifest.json','2c8c69d8ecec03d7bc339ae8bdb2349bdb942258f0c050b183197f1aa960fe61',108,D/'preauth01-selfcheck02-frozen.zip','1a0fb5e9d424e83ed6de8668607a05b28365c401b3d527d55cfaf7f959773b3c',109)
 profile=load(R/'reference/profile.json');actualPlan=load(R/'outer-constructor-plan.json')['plan'];env=actualPlan['env'];assert env==profile['expectedRuntimeEnvironment'];upper={k.upper():v for k,v in env.items()}
 def envhash(d):return sha(json.dumps(d,sort_keys=True,separators=(',',':')).encode())
 assert envhash(env)==profile['inheritedEnvSha256'] and envhash(upper)!=profile['inheritedEnvSha256']
 ospath=Path(sys.base_prefix)/'Lib/os.py';ostext=ospath.read_text();assert 'return encode(key).upper()' in ostext
 context=dict(actualGuardFailure='PROFILE_HOST_ENV_CWD',actualChildCwdOrEnvironmentSnapshot='NOT_RECORDED_DO_NOT_SYNTHESIZE',creatorCwd=actualPlan['cwd'],creatorExplicitEnvironmentKeys=sorted(env),windowsPythonEnvironmentKeysModel=sorted(upper),creatorCaseSensitiveHash=envhash(env),windowsUppercaseKeysModelHash=envhash(upper),hashesMatch=False,primaryLocalSource=str(ospath),primaryLocalSourceSha256=sha(ospath.read_bytes()),sourceRule='CPython Windows os._createenviron defines encodekey(key) as encode(key).upper()',conclusion='Preflight hashed creator mixed-case SystemRoot dictionary as child os.environ. Windows Python uppercases that key. This is a sufficient static mismatch; the original actual full child environment was not saved.',futureStaticProposal='Keep exact raw Popen/audit tuple unchanged; derive separate inherited-child snapshot with Windows key normalization, collision checks, and self cwd/keyset/hash before any qualification admission.',futureProposalImplemented=False,futureProposalExecuted=False,originalOrderOrWorkerModified=False)
 save(R/'host-context-case-analysis.json',context)
 # Save complete per-case evidence using product validate(now=...) only.
 # Frozen helper is not edited; this does not change wall clock or use Gate.
 import fact_preauth as fp
 item=load(R/'reference/prepared-inputs.json')['pure'];modelNow=datetime.fromisoformat(item['template']['notBeforeUtc'])+timedelta(seconds=1)
 class ModelDateTime:
  @staticmethod
  def now(tz):return modelNow
 ns=dict(datetime=ModelDateTime,timezone=timezone,timedelta=timedelta,copy=__import__('copy'),json=json)
 exec(compile((R/'independent_models.py').read_text(),'<frozen-model-explicit-time-replay>','exec'),ns)
 models=ns['matrix'](fp,item['policy'],item['template'],item['pins']);assert models['total']==193 and not models['bad']
 models.update(executionMode='POST_FILE_ONLY_REPLAY_EXPLICIT_VALIDATE_NOW',modelNow=modelNow.isoformat(),originalPreflight=load(R/'pure-matrix-preflight.json'),countsPolicy='One corpus193, not386; runtime worker group did not execute',clockOrProductGuardModified=False)
 save(R/'independent-template-model-evidence.json',models)
 from write_guard import allowed
 roots=[]
 for label,p,want in [('new-evidence',R/'future-static-only.json',True),('new-fixture',W/'new-original/home/outputs/x.json',True),('old-candidate-evidence',B/'evidence/result.json',False),('old-developer',D/'evidence/result.json',False),('reserved-new-name',R/'aux/x.json',False)]:
  try:allowed(p);ok=True;reason='ALLOWED_MODEL_ONLY'
  except ValueError as e:ok=False;reason=str(e)
  assert ok==want;roots.append(dict(case=label,accepted=ok,reason=reason,pureNoOpenOrMkdir=True))
 save(R/'write-root-models.json',roots)
 # Deterministic reached self_io prefix, explicitly not worker final ledger.
 prefix=[R/'order.json',R/'order.json',*[Path(x['path']) for x in o['sources']],R/'worker-admit.json',R/'worker-self.json',R/'reference/profile.json',R/'reused_checks.py']
 files=[p for p in R.rglob('*') if p.is_file()];assert len(files)<2048 and sum(p.stat().st_size for p in files)<33554432 and max(p.stat().st_size for p in files)<=1048576
 result=dict(schema='PREAUTH01_INDEPENDENT_B_POST_AUDIT_V1',status='BLOCKED_TEST_DRIVER_HOST_CONTEXT_BEFORE_QUALIFICATION',batch=o['batch'],orderSha256=sha((R/'order.json').read_bytes()),dynamicBatchStarts=1,retries=0,workerExitCode=1,outerExitCode=1,workerFinalReceiptProduced=False,actualWorkerIdentity=q['identity'],originalWaitReturnedOnce=True,readersJoined=True,streamsAndOriginalHandleCloseReturned=True,allOwnStartedOriginalsReturned=True,newResourceUnknown=False,resourceBasis='Original outer H/wait/readers/streams/close receipt plus exact pre-group exception prefix, empty collect outputs, and never-created fixture root. Not tool exit or empty custody alone.',original56=old,developer108=dev,source20Unchanged=True,gate12Unchanged=True,orderSourcesUnchanged=True,oldResultSha256=sha((B/'evidence/result.json').read_bytes()),oldDeveloperRecoveryHistory='PRESERVED; current originals unchanged throughout this independent attempt; not rewriting prior developer history',independentTemplateCorpus=193,independentTemplateCorpusPassed=193,independentTemplateNegative=sum(x['expected']!='ACCEPT' for x in models['cases']),pureMatrixApprovedHashLayer=dict(collections.Counter(x['layer'] for x in models['cases'])),preplannedPopenTuples=22,preplannedWholeProcessGraph=24,actualWholeStartedProcessGraph=1,qualificationChildrenStarted=0,productGateOrClaimCreated=False,productOnceConsumed=False,originalClaimRelease='N/A_NOT_CREATED',runtimeGroupsNotRun=['driver-qualification','developer-template-replay','independent-two-layer-template-worker-recheck','current-source-346-semantics','original-preStart13','actual-original-V2-binding','actual-wrong-receiver-once','legacy-V1','explicit-CLI-and-replay'],semanticCasesPrepared=346,semanticShardsPrepared=4,semanticCasesActuallyRun=0,actualPSDotNetChild=0,actualCLIChild=0,seconds=out['seconds'],workerSeconds=q['seconds'],stdoutBytes=q['rawCounts'][0],stderrBytes=q['rawCounts'][1],outerObservedReadBytes=out['sourceReadBytes'],outerObservedReadCalls=out['sourceReads'],workerPrefixReconstructedReadBytes=sum(p.stat().st_size for p in prefix),workerPrefixReconstructedReadCalls=len(prefix),workerAccountingBasis='Known reached self_io prefix, not a worker-emitted final ledger or complete physical/import IO',postInventoryFiles=len(files),postInventoryBytes=sum(p.stat().st_size for p in files),postMaxFileBytes=max(p.stat().st_size for p in files),postSeconds=time.monotonic()-start,actualSDK=0,actualADB=0,actualNativeRoute=0,actualTCP=0,actualDevice=0,actualGradle=0,actualGit=0,oldRuntimeQueries=0,qualificationV2='NOT_IMPLEMENTED_NOT_RUN',D1='NOT_PASSED',M0='NOT_STARTED',automaticNextTest=False)
 assert result['oldResultSha256']=='d11659b55f31aa5bed06fbd76aff611da4b8588334f97d425dad2d052ce1fc10'
 save(R/'post-audit.json',result);print(json.dumps({k:result[k] for k in ['status','dynamicBatchStarts','allOwnStartedOriginalsReturned','newResourceUnknown','independentTemplateCorpusPassed','independentTemplateNegative','actualWholeStartedProcessGraph','postInventoryBytes']}))
if __name__=='__main__':main()
