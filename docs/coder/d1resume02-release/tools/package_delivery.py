"""RESUME02 preparation verifier. Verify/help are read-only; explicit pack never signs or executes."""
from pathlib import Path
import json,hashlib,zipfile,argparse,base64,re
B=Path(__file__).resolve().parents[1];R=B.parents[2];S=B/'evidence/resume02-freeze.json';Z=R/'docs/coder/D1-20261020-RESUME02-RELEASE-source.zip'
def pin(p):b=p.read_bytes();return dict(path=p.relative_to(R).as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def check(row):assert pin(R/row['path'])=={k:row[k] for k in ['path','bytes','sha256']},row['path']
def record(p,keys):
 raw=p.read_bytes();obj=json.loads(raw);f=obj['fields'];assert obj['e9']==1 and set(obj)=={'e9','fields'} and set(f)==set(keys)
 assert raw==('{"e9":1,"fields":'+json.dumps(dict(sorted(f.items())),separators=(',',':'))+'}\n').encode('ascii')
 assert len(raw)<=8192 and all(isinstance(v,str) and re.fullmatch('[A-Za-z0-9._:/,@+~-]{1,8192}',v) for v in f.values());return f
def materials():
 c=json.loads((B/'release/candidate-binding.json').read_text());assert c['status']=='PREPARED_AUTHORIZATION_PENDING' and c['executionAuthorization'] is None and c['devicePermitIssued'] is False
 for key in ['productSourceReview','captureReview','base','scope','release','config','registryPlan','hostJar','observer','captureEntry','capturePolicy','disposition','budget','permitDraft','activationDelta']:check(c[key])
 assert c['productSourceReview']['sha256']=='0bad8b95ac7e0308713fdfed2f21c9215d18606f86aaa8e4e1dbd09059640743' and c['captureReview']['sha256']=='ad306682e27cdf1dec67955d9cb7f57bf99cd1451ab3b413963ee03439c6caf9'
 for row in c['targetApks']+c['captureRequests']+c['observerRequests']:check(row)
 s=record(R/c['scope']['path'],['kind','batch','scopeId','sourceAcceptance','sourceApp','sourceTest','app','test','fixture','fixtureSigner','sourceReview','methods','budget'])
 rel=record(R/c['release']['path'],['kind','head','catalog','app','test','signer','role','abi','version','sourceReview','environment','sourceAcceptance','scope'])
 cfg=record(R/c['config']['path'],['kind','plan','planSha','authorization','review','registryPath','head','dispatchRecord','scopePath','scopeSha'])
 assert s['scopeId']==c['scopeId'] and s['sourceReview']==rel['sourceReview']==c['productSourceReview']['sha256']
 assert rel['scope']==cfg['scopeSha']==c['scope']['sha256'] and cfg['scopePath']==(R/c['scope']['path']).as_posix()
 assert s['methods']=='ordinarySenderCannotBindCodec' and s['budget']=='source4096/read65536/open8/close16/process43/text3145728/output0'
 assert s['batch']=='D1-E13F-LIFECYCLE-20261018' and rel['version']=='19' and rel['role']=='ACTIVATION'
 assert cfg['dispatchRecord'].endswith('/'+c['scopeId']+'/e13f-lifecycle-deployment.once')
 raw=base64.urlsafe_b64decode(cfg['plan']+'='*(-len(cfg['plan'])%4));assert hashlib.sha256(raw).hexdigest()==cfg['planSha']
 old=record(R/'docs/coder/d1resume01-release/release/activation-trust-deploy.json',['kind','plan','planSha','authorization','review','registryPath','head','dispatchRecord','scopePath','scopeSha'])
 assert all(cfg[k]==old[k] for k in ['plan','planSha','authorization','review','registryPath','head'])
 registry=json.loads((B/'release/registry-plan.json').read_text());assert registry['actualRoot']==cfg['registryPath'] and registry['head']==cfg['head']==rel['head'] and registry['catalogSha256']==rel['catalog']
 for row in registry['expectedFiles']:check(row['snapshot']);assert row['snapshot']['sha256']==row['expectedActual']['sha256']
 base=json.loads((B/'release/base-release-descriptor.json').read_text());assert base['deviceExecutionAuthority'] is None
 for key in ['scope','release','config','registryPlan','hostJar','observer','captureEntry','budget']:assert base[key]==c[key]
 authority=json.loads((B/'release/preparation-authorization.json').read_text());assert authority['deviceExecutionAuthorized'] is False
 budget=json.loads((B/'release/exact-budget.json').read_text());assert budget['existingRuntimeProposal']=={'operations':43,'textBytes':3145728,'archiveBytes':4194304}
 assert budget['controlCommittedConservative']==735456 and budget['controlHeadroomNotNewOperations']==50976 and budget['historicalSeparateCarry']['consoleUnknownSlotHeld']==8192 and budget['historicalSeparateCarry']['refunded'] is False
 assert budget['rawAndDuplicatedOutputReserve']+budget['controlCommittedConservative']+budget['controlHeadroomNotNewOperations']+budget['globalUnallocatedNotSpendable']==3145728
 p=json.loads((B/'release/capture-policy.json').read_text());assert p['mode']=='PREPARATION_ONLY' and p['executionAuthorization'] is None
 assert p['independentCaptureReview']==c['captureReview']['sha256'] and p['releaseBindingDigest']==c['base']['sha256'] and p['entrySha256']==c['captureEntry']['sha256']
 assert p['planId']==c['scopeId'] and p['scope']==c['scope']['sha256'] and p['evidenceRoot']==base['captureRoot']
 assert Path(base['captureRoot']).name=='outputs' and Path(base['captureRoot']).parent.name==c['scopeId']
 templates=json.loads((B/'reference/frozen-metadata-argv.json').read_text())['commands'];assert len(p['slots'])==len(c['captureRequests'])==len(templates)==5
 for i,slot in enumerate(p['slots']):
  assert slot['argv']==templates[i]['argv'] and slot['maxTextBytes']==[65536,524288,65536,65536,524288][i] and slot['qualificationSeconds']==15 and slot['phase']==('M1' if i<3 else 'M2')
  req=json.loads((R/c['captureRequests'][i]['path']).read_text());assert req['scope']==p['scope'] and req['evidenceRoot']==p['evidenceRoot'] and req['policySha256']==c['capturePolicy']['sha256']
  assert all(req[k]==slot[k] for k in ['id','argv','maxTextBytes','qualificationSeconds'])
 for proofPin in p['executionPins']:assert hashlib.sha256(Path(proofPin['path']).read_bytes()).hexdigest()==proofPin['sha256']
 for i,row in enumerate(c['observerRequests']):
  req=json.loads((R/row['path']).read_text());assert req['pins'][0]['sha256'] is None and req['pins'][0]['pendingRole']=='REAL_DEVICE_EXECUTION_AUTHORIZATION_NOT_ISSUED'
  assert Path(req['pins'][0]['path'])==B/'release/preparation-authorization.json'
  for proofPin in req['pins'][1:]:assert hashlib.sha256(Path(proofPin['path']).read_bytes()).hexdigest()==proofPin['sha256']
  a=req['argv'];assert a[2]==(R/c['hostJar']['path']).as_posix() and req['evidenceRoot']==base['captureRoot']
  if i==0:assert a[5:9]==[(R/c['config']['path']).as_posix(),c['config']['sha256'],(R/c['release']['path']).as_posix(),c['release']['sha256']] and req['scope']==c['config']['sha256']
  else:assert a[4:]==[(R/c['scope']['path']).as_posix(),c['scope']['sha256'],s['methods']] and req['scope']==c['scope']['sha256']
 draft=json.loads((B/'release/execution-permit.pending.json').read_text());assert draft['state']=='NOT_ISSUED_NOT_EXECUTABLE' and draft['executionAuthorization'] is None and draft['scope']==c['scope']
 graph=json.loads((B/'release/deployment-command-graph.json').read_text());assert len(graph['operations'])==35
 for i,row in enumerate(graph['operations'],1):
  assert row['operation']==i and all('fake-' not in a for a in row['argv'])
  for arg in row['runtimeArguments']:assert 1<=arg['fromOperation']<i and graph['operations'][arg['fromOperation']-1]['argv'][-1]==arg['samePackage']
 assert graph['instrumentation'][graph['instrumentation'].index('e13ScopeSha256')+1]==c['scope']['sha256']
 eq=json.loads((B/'evidence/production-equivalence.json').read_text());assert len(eq['productionSources'])==74 and len(eq['members'])==183 and eq['changedSources']==eq['changedClasses']==eq['hostBuilds']==eq['androidBuilds']==0
 for row in eq['productionSources']:check(row)
 for new,oldKey in [('hostJar','priorHostJar'),('observer','priorObserver'),('captureEntry','priorCaptureEntry')]:check(eq[oldKey]);assert c[new]['sha256']==eq[oldKey]['sha256']
 with zipfile.ZipFile(R/c['hostJar']['path']) as z:
  assert set(z.namelist())=={r['entry'] for r in eq['members']}
  for row in eq['members']:assert hashlib.sha256(z.read(row['entry'])).hexdigest()==row['sha256']
 disposition=json.loads((B/'disposition/reviewed-original-disposition.json').read_text())['fields'];assert disposition['outcome']=='TERMINATED_WITHOUT_RETURN' and disposition['originalJavaReturn']=='false'
 for key,file in [('caseEvidence','case-evidence.json'),('diagnosticDisposition','diagnostic-disposition.json'),('review','administrative-review.json'),('authorization','authorization.json')]:assert disposition[key]==pin(B/'disposition'/file)['sha256']
 return c
def verify(expected=None):
 assert S.exists(),'NOT_FROZEN'
 if expected:assert pin(S)['sha256']==expected,'EXTERNAL_SEAL_PIN'
 seal=json.loads(S.read_text());rows=seal['immutableFiles'];assert len(rows)==len({r['path'] for r in rows})
 for row in rows:check(row)
 members={r['path']:r for r in rows if r['path']!=seal['archive']['path']}
 with zipfile.ZipFile(Z) as z:
  assert len(z.namelist())==len(members) and set(z.namelist())==set(members)
  for name,row in members.items():raw=z.read(name);assert len(raw)==row['bytes'] and hashlib.sha256(raw).hexdigest()==row['sha256']
 c=materials();guards=json.loads((B/'evidence/guard-001/results.json').read_text());assert guards['rejectedBeforeChild']==7 and guards['sdkCalls']==0 and guards['status']=='PASS_PREPARATION_GUARDS'
 dag=json.loads((B/'evidence/dependency-dag.json').read_text());done=set()
 for node in dag['nodes']:assert set(node['dependsOn'])<=done;done.add(node['role']);check(node['file'])
 for row in json.loads((B/'evidence/source-inputs.json').read_text())['oldSeals']:
  for oldRow in json.loads((R/row['path']).read_text())['immutableFiles']:check(oldRow)
 return dict(status='PASS_RESUME02_READONLY_PREPARATION_VERIFY',writes=0,sdkCalls=0,deviceCalls=0,liveFilesRead=False,seal=pin(S),archive=seal['archive'],archiveEntries=len(members),immutableRows=len(rows),scope=c['scope'],release=c['release'],config=c['config'],base=c['base'],policy=c['capturePolicy'],productionSourcesUnchanged=74,productionClassesUnchanged=183,hostBuilds=0,androidBuilds=0,deviceExecutionAuthorization=None,devicePermitIssued=False,blockedRealEntryInvocations=7,T07='NOT_RUN',D1='NOT_PASSED',M0='NOT_STARTED')
def pack():
 assert not S.exists() and not Z.exists(),'ALREADY_FROZEN';c=materials()
 paths=[p for p in B.rglob('*') if p.is_file() and '__pycache__' not in p.parts];paths += [R/r['path'] for r in c['targetApks']]+[R/'docs/coder/D1_RESUME02_RELEASE_DELIVERY_V1.0.md'];rows=[pin(p) for p in sorted(set(paths))]
 with zipfile.ZipFile(Z,'x',compression=zipfile.ZIP_DEFLATED) as z:
  for row in rows:z.writestr(row['path'],(R/row['path']).read_bytes())
 archive=pin(Z);rows.append(archive);S.write_text(json.dumps(dict(schema=1,candidate=c['candidate'],archive=archive,immutableFiles=rows,deviceAuthorization='NOT_ISSUED',independentMechanicalReview='PENDING'),indent=2)+'\n');print(json.dumps(dict(status='PACKED_RESUME02_AUTH_PENDING',seal=pin(S),archive=archive,archiveEntries=len(rows)-1)))
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('mode',choices=['verify','pack'],nargs='?',default='verify');p.add_argument('--seal-sha');a=p.parse_args()
 if a.mode=='pack':
  if a.seal_sha:p.error('--seal-sha only for verify')
  pack()
 else:print(json.dumps(verify(a.seal_sha)))
if __name__=='__main__':main()
