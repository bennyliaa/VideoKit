"""File-only adjudication after the one admitted worker returned; never rerun it."""
from pathlib import Path
import ast, hashlib, json, time, zipfile
R=Path(__file__).resolve().parent; T=R.parent; C=T.parent/'coder'
READ=[]
def rd(p):
 p=Path(p)
 with p.open('rb') as f:b=f.read()
 READ.append(dict(path=str(p),bytes=len(b)))
 return b
def sha(b):return hashlib.sha256(b).hexdigest()
def load(p):return json.loads(rd(p))
def save(p,d):
 with p.open('xb') as f:f.write((json.dumps(d,ensure_ascii=True,indent=2)+'\n').encode());f.flush()
def packet(base,rel,h,n):
 raw=rd(base/rel);assert sha(raw)==h
 m=json.loads(raw);assert len(m['files'])==n
 for x in m['files']:
  p=Path(x['absolutePath']) if 'absolutePath' in x else base/x['path']
  b=rd(p);assert len(b)==x['bytes'] and sha(b)==x['sha256'],str(p)
 return dict(manifestSha256=h,files=n,bytes=sum(x['bytes'] for x in m['files']),bad=0)
def main():
 start=time.monotonic();o=load(R/'order.json');W=Path(o['work']);out=load(R/'outer-final.json');q=out['receipt']
 assert q['exitCode']==1 and q['originalWaitReturnedOnce'] and q['readersJoined'] and q['streamsAndOriginalHandleCloseReturned'] and not q['errors'] and not q['expired']
 assert out['allOwnEvidenceFilesClosed'] and out['newUnknown'] is False and out['auditObserved']==1 and out['auditMismatch']==0
 stderr=bytes.fromhex(load(R/'runtime/outer-stderr-0.json')['hex']).decode('utf-8')
 assert "NameError: name 'BACKEND' is not defined" in stderr and 'line 20, in main' in stderr
 assert not list(W.rglob('*.*')) and (W/'one').is_dir() and not (W/'one/actual-home').exists()
 for name in ['actual-input-binding.json','checker-profile-before-constructor.json','worker-final.json']:
  assert not (R/name).exists(),name
 worker=rd(R/'worker.py').decode();defs=rd(R/'input_definitions.py').decode();ast.parse(worker);ast.parse(defs)
 assert "sources=load" in worker and 'BACKEND=' not in worker and "'routeBackend':BACKEND" in defs
 assert worker.index("f,p=ns['permit']")<worker.index("sys.addaudithook(audit)")<worker.index("r=pr.ProductionRunner.__new__")<worker.index('observer.start()')
 for x in o['sources']:
  b=rd(x['path']);assert len(b)==x['bytes'] and sha(b)==x['sha256']
 b=C/'d1android02-global-idle-contract03-fix';d=C/'d1android02-global-idle-contract03-selfcheck02'
 freezes={
  'candidate98':packet(b,'reference/freeze-manifest.json','55e8f1b6a9fc1ccd4111ad4c1a1ddf4324ffc60951892d8f54e8ba636bde3d81',98),
  'developer484':packet(d,'reference/material-manifest.json','ec171260f95bfcfd712d4e2245c68b6612f2a8939631ba79a92f9b7f73b2343a',484),
  'semanticA408':packet(T,'D1_GLOBAL_IDLE_CONTRACT03_SEMANTICS_A_MANIFEST_V1.0.json','8208c09cd12d91c942a9ceadaffe17842ddc0911515b276ccd5c18877210c066',408),
  'independentB744':packet(T,'D1_GLOBAL_IDLE_CONTRACT03_INDEPENDENT_B_MANIFEST_V1.0.json','19cf9a1e3d8f01c08ed8d8727ca2495bc9b836eb72bc1a7da939a7bd49824bb2',744)}
 archives=[]
 for p,h,n in [(C/'d1android02-global-idle-contract03-fix-blocked-frozen.zip','45fb593f8b7aa916095540275a7287bdf01e524f5a983befc3768e9c9cb4a58c',99),(C/'d1android02-global-idle-contract03-selfcheck02-frozen.zip','d3425d18bbf12910ac204bf9d0db7ab03c32687c4f47f95266387aca72af2c65',485)]:
  assert sha(rd(p))==h
  with zipfile.ZipFile(p) as z:
   names=z.namelist();assert len(names)==n and len(set(names))==n
  archives.append(dict(path=str(p),sha256=h,members=n,allFilesClosed=True))
 # Independent evidence-admission examples, never candidate execution.
 rows=[]
 for phase in ['no-permit','constructor','gate-prepared','proof-read','activation']:
  for code in ['PERMIT_EXPIRED_OR_FUTURE','RUNNER_PROOF_STICKY','RUNNER_CONTROL_CAP']:
   accepted=phase=='proof-read' and code=='PERMIT_EXPIRED_OR_FUTURE'
   rows.append(dict(phase=phase,reason=code,exactTargetIfOtherTimingAndReturnPredicatesHold=accepted,pureOnly=True))
 e=load(R/'timing-envelope.json')
 assert e['lower']<e['ttlSeconds']<e['upper'] and e['maxProofStart']+e['maxPostProofReadUpper']+.5+.25==e['lower']
 rows.extend([dict(name='ttl-inside-empirical-reserved-interval',passed=True,pureOnly=True),dict(name='original-9s-not-upper-bound',passed=True,pureOnly=True),dict(name='same-reason-before-proof-not-accepted',passed=not rows[0]['exactTargetIfOtherTimingAndReturnPredicatesHold'],pureOnly=True)])
 save(R/'pure-adjudication-model.json',dict(executedCandidateBodies=False,models=rows,productTestPasses=0))
 # Reconstruct the deterministic completed worker self_io reads from its prefix.
 # Not a worker-emitted final ledger and not total physical/runtime import IO.
 workerPaths=[R/'order.json',R/'order.json',*[Path(x['path']) for x in o['sources']],R/'worker-admit.json',R/'worker-self.json',b/'reference/runner-source-seal.json',b/'reference/exact-seven-role-plan.json',R/'input_definitions.py']
 reconstructedBytes=sum(p.stat().st_size for p in workerPaths)
 runtimeFiles=[p for p in R.rglob('*') if p.is_file() and p.name!='post_audit.py']
 result=dict(schema='CONTRACT03_COVERAGE_CHECKPOINT01_POST_AUDIT_V1',batch=o['batch'],orderSha256=sha(rd(R/'order.json')),status='FAIL_TEST_DRIVER_PRE_PERMIT_TARGET_NOT_COVERED',error="NameError: name 'BACKEND' is not defined",workerExitCode=1,outerExitCode=1,workerFinalReceiptProduced=False,dynamicAttempts=1,retries=0,additionalAttemptsAllowed=0,permitGenerated=False,productConstructorEntered=False,gatePrepared=False,materializerProofReadReturned=False,activationCreated=False,controllersEntered=0,productClaimCreated=False,productClaimRelease='NOT_APPLICABLE_NOT_CREATED',ownWorkerIdentity=q['identity'],originalWaitReturnedOnce=True,readersJoined=True,streamsAndOriginalHandleCloseReturned=True,newResourceUnknown=False,resourceConclusionBasis='Original H wait/readers/streams/close receipt plus exact unhandled pre-permit exception prefix; no product constructor, observer thread or checker constructed. Not custody emptiness alone.',outerSeconds=out['seconds'],workerSeconds=q['seconds'],stdoutBytes=q['rawCounts'][0],stderrBytes=q['rawCounts'][1],actualNewAuxiliaryChildren=1,routeCheckerChildren=0,productSourceFrozen=True,freezes=freezes,archives=archives,pureAdjudicationModels=len(rows),outerObservedReadBytes=out['sourceReadBytes'],outerObservedReadCalls=out['sourceReads'],workerPrefixReconstructedReadBytes=reconstructedBytes,workerPrefixReconstructedReadCalls=len(workerPaths),workerAccountingBasis='Deterministic reached self_io prefix; final worker ledger absent; excludes import/runtime/physical IO.',runtimeInventoryFiles=len(runtimeFiles),runtimeInventoryBytes=sum(p.stat().st_size for p in runtimeFiles),postReadBytes=sum(x['bytes'] for x in READ),postReadCalls=len(READ),postSeconds=time.monotonic()-start,actualSDK=0,actualADB=0,actualNativeRoute=0,deviceCalls=0,oldRuntimeQueries=0,allOwnStartedOriginalsReturned=True,gitAllowedOnlyAfterReportFreeze=True,D1='NOT_PASSED',M0='NOT_STARTED',automaticNextTest=False)
 assert result['runtimeInventoryBytes']<16777216 and result['runtimeInventoryFiles']<512 and result['outerObservedReadBytes']+reconstructedBytes<268435456
 save(R/'post-audit.json',result)
 print(json.dumps({k:result[k] for k in ['status','dynamicAttempts','newResourceUnknown','allOwnStartedOriginalsReturned','runtimeInventoryFiles','runtimeInventoryBytes','postReadBytes','postReadCalls']}))
if __name__=='__main__':main()
