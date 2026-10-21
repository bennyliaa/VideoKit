"""Verify/help are read-only. Explicit pack seals offline capture preparation once, never runs SDK/fixtures."""
from pathlib import Path
import json,hashlib,zipfile,argparse,re
B=Path(__file__).resolve().parents[1];R=B.parents[2];S=B/'evidence/capture-freeze.json';Z=R/'docs/coder/D1-20261020-RESUME01-CAPTURE-source.zip'
def pin(p):b=p.read_bytes();return dict(path=p.relative_to(R).as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def check(row):assert pin(R/row['path'])=={k:row[k] for k in ['path','bytes','sha256']},row['path']
def excluded(p):
 return p.is_relative_to(B/'selfchecks/work') or p.is_relative_to(B/'evidence/fixture-002') or '__pycache__' in p.parts
def materials():
 policy=json.loads((B/'release/capture-policy.json').read_text());assert policy['mode']=='PREPARATION_ONLY'
 entry=pin(B/'tools/capture_metadata.ps1');assert policy['entrySha256']==entry['sha256']
 assert all(policy[k] is None for k in ['executionAuthorization','independentCaptureReview','releaseBindingDigest'])
 assert policy['scope']==pin(B/'release/preparation-plan.json')['sha256']
 templates=json.loads((B/'reference/frozen-metadata-argv.json').read_text())['commands'];assert len(policy['slots'])==len(templates)==5
 requests=sorted((B/'release/requests').glob('*.json'));assert len(requests)==5
 for slot in policy['slots']:
  i=policy['slots'].index(slot);assert slot['argv']==templates[i]['argv'] and slot['maxTextBytes']==[65536,524288,65536,65536,524288][i] and slot['qualificationSeconds']==15
  req=json.loads((B/'release/requests'/(slot['id']+'.json')).read_text());assert set(req)=={'schema','id','policySha256','scope','evidenceRoot','argv','maxTextBytes','qualificationSeconds'}
  assert req['schema']=='RESUME01_CAPTURE_REQUEST_V1' and req['policySha256']==pin(B/'release/capture-policy.json')['sha256']
  assert all(req[k]==policy[k] for k in ['scope','evidenceRoot']) and all(req[k]==slot[k] for k in ['argv','maxTextBytes','qualificationSeconds'])
 code=(B/'tools/capture_metadata.ps1').read_text();assert not re.search(r'(?i)[.]kill\s*\(|Stop-Process|TerminateProcess|kill-server',code)
 assert 'processDisposeEntered' in code and 'waitEntered' in code and 'writeStartUnknown' in code and 'rawKnownIsPrefix' in code
 result=json.loads((B/'evidence/fixture-004/results.json').read_text());assert result['status']=='PASS_CAPTURE_FINITE_LOCAL_FIXTURES' and result['assertions']==145 and result['kills']==0 and result['ownerPending'] is False
 for row in json.loads((B/'evidence/fixture-004/inputs.json').read_text()):check(row)
 snapshots=json.loads((B/'evidence/test-work-snapshot-index.json').read_text());assert snapshots['fixture002ControllerExit']=='UNKNOWN_RETAINED'
 mapping={row['originalPath']:R/row['snapshot']['path'] for row in snapshots['rows']}
 for row in snapshots['rows']:check(row['snapshot'])
 commands=json.loads((B/'evidence/fixture-004/commands.json').read_text());byPid={row['pid']:row for row in commands}
 for item in result['results']:
  c=item['console'];command=byPid[c['controllerPid']];argv=command['argv'];requestOriginal=Path(argv[argv.index('-RequestPath')+1]);request=json.loads(mapping[requestOriginal.relative_to(R).as_posix()].read_text());root=Path(request['evidenceRoot'])
  for reader in c['readers']:
   original=root/(c['id']+'-'+reader['role']+'.bin');saved=mapping[original.relative_to(R).as_posix()]
   assert saved.stat().st_size==reader['savedBytes'] and reader['pipeCloseReturned'] and reader['fileCloseReturned']
  assert all(r['closed'] for r in c['metadata']) and c['allOriginalResourcesReturnedAtConsole']
  clonedEntry=Path(argv[argv.index('-File')+1]);assert pin(mapping[clonedEntry.relative_to(R).as_posix()])['sha256']==entry['sha256']
 for command in commands:
  row=json.loads((B/'evidence/fixture-004'/(command['name']+'.exit.json')).read_text());assert row['naturalReturn'] and row['pid']==command['pid']
 for row in json.loads((B/'reference/fixture-002-snapshot-index.json').read_text())['rows']:
  p=R/row['snapshot'];assert p.stat().st_size==row['bytes'] and pin(p)['sha256']==row['sha256']
 production=json.loads((B/'evidence/production-unchanged.json').read_text());assert production['productionChanges']==production['productBuilds']==production['androidBuilds']==0 and len(production['sources'])==74 and len(production['members'])==183
 for row in production['sources']:check(row)
 check(production['jar'])
 with zipfile.ZipFile(R/production['jar']['path']) as jar:
  assert set(jar.namelist())=={r['entry'] for r in production['members']}
  for row in production['members']:assert hashlib.sha256(jar.read(row['entry'])).hexdigest()==row['sha256']
 old=R/'docs/coder/d1resume01-release/evidence/release-freeze.json';assert pin(old)['sha256']=='b7537e7dd4934c248f727064a103c1fbfc099d0e7a28cce55b28a777df7fd461'
 for row in json.loads(old.read_text())['immutableFiles']:check(row)
 a=json.loads((B/'release/accounting-feasibility.json').read_text());assert a['controlCommittedConservative']==735456 and a['controlHeadroomNotNewOperations']==50976
 assert 1949696+735456+50976+409600==3145728 and a['newDevicePermitIssued'] is False and a['historicalSeparateCarry']['consoleActualBytes']=='UNKNOWN'
 return entry
def verify(expected=None):
 assert S.is_file(),'NOT_FROZEN'
 if expected:assert pin(S)['sha256']==expected,'EXTERNAL_SEAL_PIN'
 seal=json.loads(S.read_text());rows=seal['immutableFiles'];assert len(rows)==len({r['path'] for r in rows})
 for row in rows:check(row)
 members={r['path']:r for r in rows if r['path']!=seal['archive']['path']}
 with zipfile.ZipFile(Z) as z:
  assert len(z.namelist())==len(members) and set(z.namelist())==set(members)
  for name,row in members.items():raw=z.read(name);assert len(raw)==row['bytes'] and hashlib.sha256(raw).hexdigest()==row['sha256']
 entry=materials();return dict(status='PASS_CAPTURE_STRICT_READONLY_VERIFY',writes=0,sdkCalls=0,deviceCalls=0,seal=pin(S),archive=seal['archive'],archiveEntries=len(members),immutableRows=len(rows),entry=entry,finalLocalAssertions=145,productionSourcesUnchanged=74,productionClassesUnchanged=183,androidBuilds=0,newDevicePermitIssued=False,historicalFixture002OuterReturn='UNKNOWN_RETAINED',D1='NOT_PASSED',M0='NOT_STARTED')
def pack():
 assert not S.exists() and not Z.exists(),'ALREADY_FROZEN';materials()
 paths=[p for p in B.rglob('*') if p.is_file() and not excluded(p)];paths.append(R/'docs/coder/D1_RESUME01_CAPTURE_DELIVERY_V1.0.md');rows=[pin(p) for p in sorted(set(paths))]
 with zipfile.ZipFile(Z,'x',compression=zipfile.ZIP_DEFLATED) as z:
  for row in rows:z.writestr(row['path'],(R/row['path']).read_bytes())
 archive=pin(Z);rows.append(archive);S.write_text(json.dumps(dict(schema=1,candidate='D1-20261020-RESUME01-CAPTURE',archive=archive,immutableFiles=rows,excludedOriginalTestScratch=True,fixture002OriginalMutablePathsExcluded=True,newDevicePermitIssued=False,independentReview='PENDING'),indent=2)+'\n')
 print(json.dumps(dict(status='PACKED_OFFLINE_CAPTURE',seal=pin(S),archive=archive,archiveEntries=len(rows)-1)))
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('mode',choices=['verify','pack'],nargs='?',default='verify');p.add_argument('--seal-sha');a=p.parse_args()
 if a.mode=='pack':
  if a.seal_sha:p.error('--seal-sha only for verify')
  pack()
 else:print(json.dumps(verify(a.seal_sha)))
if __name__=='__main__':main()
