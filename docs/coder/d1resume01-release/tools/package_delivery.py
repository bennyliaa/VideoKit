"""Mechanical release verify/help are read-only. Explicit pack seals one new release; never dispatches."""
from pathlib import Path
import argparse,json,hashlib,zipfile,base64,re
B=Path(__file__).resolve().parents[1];R=B.parents[2];S=B/'evidence/release-freeze.json';Z=R/'docs/coder/D1-20261020-RESUME01-RELEASE-source.zip'
REVIEW='0bad8b95ac7e0308713fdfed2f21c9215d18606f86aaa8e4e1dbd09059640743'
def pin(p):b=p.read_bytes();return dict(path=p.relative_to(R).as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def check(row):assert pin(R/row['path'])=={k:row[k] for k in ['path','bytes','sha256']},row['path']
def record(p,keys):
 raw=p.read_bytes();d=json.loads(raw);f=d['fields'];assert set(d)=={'e9','fields'} and d['e9']==1 and set(f)==set(keys)
 assert raw==('{"e9":1,"fields":'+json.dumps(dict(sorted(f.items())),separators=(',',':'))+'}\n').encode('ascii')
 assert len(raw)<=8192 and all(re.fullmatch('[A-Za-z0-9._:/,@+~-]{1,8192}',v) for v in f.values())
 return f
def materials():
 binding=json.loads((B/'release/candidate-binding.json').read_text())
 for key in ['sourceReview','hostJar','observer','disposition','scope','release','config','permit','budget','registryPlan']:check(binding[key])
 assert binding['sourceReview']['sha256']==REVIEW
 for row in binding['targetApks']:check(row)
 scope=record(R/binding['scope']['path'],['kind','batch','scopeId','sourceAcceptance','sourceApp','sourceTest','app','test','fixture','fixtureSigner','sourceReview','methods','budget'])
 release=record(R/binding['release']['path'],['kind','head','catalog','app','test','signer','role','abi','version','sourceReview','environment','sourceAcceptance','scope'])
 config=record(R/binding['config']['path'],['kind','plan','planSha','authorization','review','registryPath','head','dispatchRecord','scopePath','scopeSha'])
 assert scope['sourceReview']==release['sourceReview']==REVIEW and scope['scopeId']==binding['executionBatch']
 assert scope['methods']=='ordinarySenderCannotBindCodec' and scope['budget']=='source4096/read65536/open8/close16/process43/text3145728/output0'
 assert release['scope']==binding['scope']['sha256']==config['scopeSha']
 assert config['scopePath']==(R/binding['scope']['path']).as_posix()
 assert config['dispatchRecord']==binding['deploymentOncePath'] and config['dispatchRecord'].endswith('/'+binding['executionBatch']+'/e13f-lifecycle-deployment.once')
 assert config['kind']=='e13ActivationTrust' and scope['kind']=='e13DispatchScope' and release['kind']=='activationRelease'
 planRaw=base64.urlsafe_b64decode(config['plan']+'='*(-len(config['plan'])%4));assert hashlib.sha256(planRaw).hexdigest()==config['planSha']
 trust=json.loads((B/'reference/original-activation-trust.json').read_text())['fields']
 assert all(config[k]==trust[k] for k in ['plan','planSha','authorization','review','registryPath','head'])
 registry=json.loads((B/'release/registry-plan.json').read_text());assert registry['actualRoot']==trust['registryPath'] and registry['currentSourceReview']==REVIEW
 for row in registry['expectedFiles']:
  check(row['snapshot']);assert row['snapshot']['sha256']==row['expectedActual']['sha256']
 assert pin(B/'reference/accepted-registry-snapshot/final.acceptance.json')['sha256']==release['catalog']
 assert release['head']==config['head']==registry['head']
 for key in ['app','test','sourceAcceptance']:assert scope[key]==release[key]
 assert all(scope[k]==binding['targetApks'][i]['sha256'] for i,k in enumerate(['app','test','fixture']))
 assert release['version']=='19' and release['abi']=='1' and release['role']=='ACTIVATION' and release['environment']=='DEVICE_HA1Q6WXR'
 assert scope['fixtureSigner']==binding['targetApks'][2]['signer']!=release['signer']==binding['targetApks'][0]['signer']
 d=record(B/'disposition/reviewed-original-disposition.json',['kind','originalScope','serial','packages','outcome','originalJavaReturn','caseEvidence','diagnosticDisposition','review','authorization'])
 assert d['outcome']=='TERMINATED_WITHOUT_RETURN' and d['originalJavaReturn']=='false'
 for key,name in [('caseEvidence','case-evidence.json'),('diagnosticDisposition','diagnostic-disposition.json'),('review','administrative-review.json'),('authorization','authorization.json')]:assert d[key]==pin(B/'disposition'/name)['sha256']
 source=json.loads((B/'evidence/source-identity.json').read_text());assert source['changedSources']==source['hostBuilds']==source['androidBuilds']==0
 for row in source['productionSources']:check(row['source']);check(row['current']);assert row['source']['sha256']==row['current']['sha256']
 check(source['originalJar']);check(source['originalObserver']);assert binding['hostJar']['sha256']==source['originalJar']['sha256'] and binding['observer']['sha256']==source['originalObserver']['sha256']
 eq=json.loads((B/'evidence/member-equivalence.json').read_text());assert len(eq['members'])==183
 with zipfile.ZipFile(R/binding['hostJar']['path']) as jar:
  assert set(jar.namelist())=={r['entry'] for r in eq['members']}
  for row in eq['members']:assert hashlib.sha256(jar.read(row['entry'])).hexdigest()==row['sha256']
 budget=json.loads((B/'release/exact-budget.json').read_text());assert sum(g['operations'] for g in budget['groups'])==43 and budget['totalTextBytes']==3145728 and budget['archiveDiskBytes']==4194304 and budget['unallocatedNotSpendable']==409600
 assert sum(g['textBytes'] for g in budget['groups'])==1949696 and 1949696+786432+409600==3145728
 metadata=json.loads((B/'release/metadata-requests.json').read_text());assert len(metadata['commands'])==5
 assert [r['maxTextBytes'] for r in metadata['commands']]==[65536,524288,65536,65536,524288]
 graph=json.loads((B/'release/deployment-command-graph.json').read_text());assert len(graph['operations'])==35
 for i,row in enumerate(graph['operations'],1):
  assert row['operation']==i and not any('fake-' in a for a in row['argv'])
  for arg in row['runtimeArguments']:
   assert 1<=arg['fromOperation']<i and graph['operations'][arg['fromOperation']-1]['argv'][-1]==arg['samePackage']
 assert graph['instrumentation'][graph['instrumentation'].index('e13ScopeSha256')+1]==binding['scope']['sha256']
 assert graph['instrumentation'][graph['instrumentation'].index('e13Case')+1]==scope['methods']
 expectedRoles={'deploy':('com.videokit.spike.e4.E13HostActivationSession',81920,binding['config']['sha256']),'case':('com.videokit.spike.e4.E13HostCase',32768,binding['scope']['sha256'])}
 for role,(klass,cap,scopeSha) in expectedRoles.items():
  request=json.loads((B/'release'/('observer-'+role+'-request.json')).read_text());assert request['argv'][3]==klass and request['argv'][2]==(R/binding['hostJar']['path']).as_posix() and request['maxTextBytes']==cap and request['scope']==scopeSha
  for p in request['pins']:assert hashlib.sha256(Path(p['path']).read_bytes()).hexdigest()==p['sha256']
  assert REVIEW in {p['sha256'] for p in request['pins']}
  if role=='case':assert request['argv'][4:]==[(R/binding['scope']['path']).as_posix(),binding['scope']['sha256'],scope['methods']]
  else:assert request['argv'][4:9]==['--approved-e13-deploy',(R/binding['config']['path']).as_posix(),binding['config']['sha256'],(R/binding['release']['path']).as_posix(),binding['release']['sha256']]
 permit=record(R/binding['permit']['path'],['kind','scopeId','scope','release','config','sourceReview','authorization','jar','observer','disposition','budget','registryPlan','method','operations','textBytes','archiveBytes','unallocatedNotSpendable','precondition','state'])
 assert permit['scope']==binding['scope']['sha256'] and permit['release']==binding['release']['sha256'] and permit['config']==binding['config']['sha256'] and permit['sourceReview']==REVIEW and permit['state']=='ISSUED_NOT_CONSUMED'
 assert permit['authorization']==pin(B/'release/dispatch-authorization.json')['sha256']
 accounting=json.loads((B/'release/admission-and-accounting.json').read_text());assert accounting['rawCapsArePhysicalHardBounds'] is False and accounting['unallocatedNotSpendable']==409600
 provenance=json.loads((B/'evidence/registry-provenance.json').read_text());check(provenance['anchor']);check(provenance['originalSeal'])
 for row in provenance['anchoredRows']:check(row)
 return binding
def verify(expected=None):
 assert S.exists(),'NOT_FROZEN'
 if expected:assert pin(S)['sha256']==expected,'EXTERNAL_SEAL_PIN'
 seal=json.loads(S.read_text());rows=seal['immutableFiles'];assert len(rows)==len({r['path'] for r in rows})
 for row in rows:check(row)
 with zipfile.ZipFile(Z) as z:
  members={r['path']:r for r in rows if r['path']!=seal['archive']['path']};assert len(z.namelist())==len(members) and set(z.namelist())==set(members)
  for name,row in members.items():raw=z.read(name);assert len(raw)==row['bytes'] and hashlib.sha256(raw).hexdigest()==row['sha256']
 binding=materials()
 previous=json.loads((B/'reference/resume01-freeze.json').read_text())
 for row in previous['immutableFiles']:check(row)
 return dict(status='PASS_RESUME01_RELEASE_READONLY_MECHANICAL_SELFVERIFY',writes=0,deviceCalls=0,liveRegistryRead=False,seal=pin(S),archive=seal['archive'],archiveEntries=len(members),immutableRows=len(rows),hostBuilds=0,androidBuilds=0,productionMembersIdentical=183,scope=binding['scope'],release=binding['release'],config=binding['config'],permit=binding['permit'],onceConsumed=False,mechanicalIndependentReview='PENDING',T07='NOT_RUN',D1='NOT_PASSED',M0='NOT_STARTED')
def pack():
 assert not S.exists() and not Z.exists(),'ALREADY_FROZEN'
 binding=materials();paths=[p for p in B.rglob('*') if p.is_file() and '__pycache__' not in p.parts]
 paths+=[R/r['path'] for r in binding['targetApks']]+[R/'docs/coder/D1_RESUME01_RELEASE_DELIVERY_V1.0.md']
 rows=[pin(p) for p in sorted(set(paths))]
 with zipfile.ZipFile(Z,'x',compression=zipfile.ZIP_DEFLATED) as z:
  for row in rows:z.writestr(row['path'],(R/row['path']).read_bytes())
 archive=pin(Z);rows.append(archive);S.write_text(json.dumps(dict(schema=1,candidate=binding['candidate'],archive=archive,immutableFiles=rows,independentMechanicalReview='PENDING',executionDispatchedByCoder=False),indent=2)+'\n')
 print(json.dumps(dict(status='PACKED_RELEASE',seal=pin(S),archive=archive,archiveEntries=len(rows)-1)))
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('mode',choices=['verify','pack'],nargs='?',default='verify');p.add_argument('--seal-sha');a=p.parse_args()
 if a.mode=='pack':
  if a.seal_sha:p.error('--seal-sha only for verify')
  pack()
 else:print(json.dumps(verify(a.seal_sha)))
if __name__=='__main__':main()
