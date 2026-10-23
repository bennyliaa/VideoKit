# Port of frozen independent small-append regression; source preimage hash below.
from pathlib import Path
import json,time
from entry_gates import sha
def exact_append(R,B,W,ns,save,load):
 from production_runner import RUNNER_CUSTODY
 from entry_gates import encode
 from outer_owner import Owner
 f,p=ns['permit']('g');args=ns['inputs'](f,p);src=p['sources'];home=Path(p['home']);root=Path(p['evidenceRoot']);ph=args[2];ah=args[4]
 local=dict(schema='ENTRY_GATES_LOCAL_AUTH_V2',scope=p['scope'],planId=p['planId'],entrySha256=src['tools/capture_android02.ps1'],gateSourcesSha256=src['reference/gate-sources.json'],approvedForLocalMetadata=True,routeBackend=p['routeBackend'])
 policy=json.loads((B/'release/capture-policy.json').read_bytes());policy.update(mode='OFFLINE_FIXTURE',scope=p['scope'],planId=p['planId'],runId=p['runId'],evidenceRoot=str(root),entrySha256=src['tools/capture_android02.ps1'],outerOwnerSha256=src['tools/outer_owner.py'],gateSourcesSha256=src['reference/gate-sources.json'],runnerSourceSha256=src['tools/production_runner.py'],runnerSources=p['sourceSeal'],runnerPermit={'path':str(f/'permit.json'),'sha256':ph},runnerApproval={'path':str(f/'approval.json'),'sha256':ah},toolCandidateSeal=p['sourceSeal'],independentReview=p['review'],toolSha256=p['tools'][0]['sha256'],slots=p['roles'],fixtureScriptSha256=src['selfchecks/capture_fixture.py'],fixtureFault='NONE',fixtureGatePath=str(root/'fixture-gate'),fixtureOuterSeconds=120,fixtureProofSeconds=10,globalIdleQualification=p['globalIdleQualification'],gateAuthorization={'path':str(home/'release/gate-local-authorization.json'),'sha256':sha(encode(local))},authorization={'path':str(home/'release/activation.json'),'sha256':'0'*64},freshRouteProof={'path':str(root/'fresh-route.json'),'sha256':'0'*64})
 activation=dict(schema='ANDROID02_CAPTURE_ACTIVATION_V1',scope=p['scope'],planId=p['planId'],runId=p['runId'],entrySha256=src['tools/capture_android02.ps1'],planSha256=src['reference/exact-seven-role-plan.json'],toolCandidateSealSha256=p['sourceSeal']['sha256'],productSealSha256=p['product']['sealSha256'],reviewSha256=p['review']['sha256'],toolSha256=p['tools'][0]['sha256'],evidenceRoot=str(root),wholeWallSeconds=600,localProofSeconds=10,outerSeconds=120,freshRouteProofSha256='0'*64,initialPredecessorProofSha256='0'*64,outerOwnerSha256=src['tools/outer_owner.py'],outerPythonSha256=policy['outerPythonSha256'],runtimeIdentitySha256=policy['runtimeIdentitySha256'],runtimeBindingSourceSha256=policy['runtimeBindingSourceSha256'],approvedForExecution=True,runnerPermitSha256=ph,runnerSourceSha256=src['tools/production_runner.py'],runnerApprovalSha256=ah,routeBackend=p['routeBackend'])
 pb=len(encode(policy));ab=len(encode(activation));permitBytes=len((f/'permit.json').read_bytes());approvalBytes=len((f/'approval.json').read_bytes());reviewBytes=len((f/'offline-review.txt').read_bytes());setup=permitBytes+approvalBytes+reviewBytes
 pre=setup+len((B/'reference/runner-source-seal.json').read_bytes())+sum(2*(B/rel).stat().st_size for rel in ('tools/capture_android02.ps1','reference/exact-seven-role-plan.json','reference/route-backend-contract.json'))+6144+(B/'release/capture-policy.json').stat().st_size+len(encode(local))+setup
 post=permitBytes+approvalBytes+2048+4096+2*ab+2*pb+4096+1;bound=pre+post+pb;gateBound=pre+32768
 material=dict(preExactIncludingOwnInputWrites=pre,postBound=post,receiverExact=pb,runnerControlBound=bound,gateControlBound=gateBound,localCap=262144,policyExact=pb,activationExact=ab,ownAppend=1,ownBodyReread=0,inputCreationWrites=setup,receiptBound=4096,routeBound=2048,proofBound=4096,precomputedBeforeConstructor=True)
 save(f/'material-bound-before-constructor.json',material)
 assert max(bound,gateBound)<=262144,material
 source=(B/'tools/capture_android02.ps1').read_bytes();save(f/'mutation-pins.json',dict(originalBytes=len(source),originalSha256=sha(source),appendHex='0a',expectedBytes=len(source)+1,expectedSha256=sha(source+b'\n')))
 r=ns['construct'](args);r.consumed=True;facts={};release=None
 try:
  r.event('pre','independent-input-creation-writes',setup);r.prepare_home();r.materialize();r.require();target=r.home/'tools/capture_android02.ps1'
  def append():
   stream=target.open('ab');r.held.append(stream);facts['writeEntered']=True;n=stream.write(b'\n');facts['writeReturned']=True;stream.flush();facts['flushReturned']=True;facts['closeEntered']=True;stream.close();facts['closeReturned']=True;return n
  op=r.operation('independent-one-byte-source-append',append);assert op['value']==1 and facts['closeReturned'];r.event('post','independent-one-byte-source-append',1);r.require()
  try:Owner(r.home,r.gate,r);raise AssertionError('MUTATED_SOURCE_ACCEPTED')
  except ValueError as e:reason=str(e)
  assert reason=='OWNER_SOURCE_PIN_ENTRY' and r.failure is None and r.gate.failure is None,reason
  control=sum(x['bytes'] for lane in (r.pre,r.post,r.receiver,r.final) for x in lane);assert control<=bound and sum(x['bytes'] for x in r.gate.events)<=gateBound
  assert len(r.policy_bytes)==pb and len(r.activation_bytes)==ab and not list(r.root.glob('*-entered.json'))
  detail=dict(exactReason=reason,runnerFailureBeforeFail=r.failure,gateFailureBeforeFail=r.gate.failure,append=facts,control=control,gateControl=sum(x['bytes'] for x in r.gate.events),budget=material,initialProofUnchanged=sha((r.root/'pre_sdk_local_gate-completion-proof.json').read_bytes())==r.initial_hash,pendingOriginals=sum(t.is_alive() for t in r.pending+r.gate.pending),controllerEntered=0,sourceReads=r.source_reads,sourceBytes=r.source_bytes)
  save(f/'before-release.json',detail);r.fail(reason)
  return detail
 finally:
  if any(t.is_alive() for t in r.pending) or r.gate is not None and any(t.is_alive() for t in r.gate.pending):
   save(f/'pending.json',dict(noNewWork=True,originalsRetained=True))
   while True:time.sleep(.1)
  if r.gate is not None and r.gate.lease is not None and not r.gate.released:r.gate.fail(r.failure or 'KNOWN_GROUP_STOP');release=r.gate.release();save(f/'original-release.json',release)
  if r in RUNNER_CUSTODY:RUNNER_CUSTODY.remove(r)
