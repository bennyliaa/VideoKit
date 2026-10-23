def permit(name,scenario='NONE'):
 if time.monotonic()-START>=260:raise AssertionError('STOP_NEW_CASE_BEFORE_260S')
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
