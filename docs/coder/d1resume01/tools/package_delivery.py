"""Default verify/help are strictly read-only. Explicit pack seals this offline candidate once."""
from pathlib import Path
import argparse,json,hashlib,zipfile
B=Path(__file__).resolve().parents[1];R=B.parents[2];S=B/'evidence/resume01-freeze.json';Z=R/'docs/coder/D1-20261020-RESUME01-source.zip'
def pin(p):
 b=p.read_bytes();return dict(path=p.relative_to(R).as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def checked(row):assert pin(R/row['path'])==row,row['path']
def verify(expected=None):
 assert S.is_file(),'NOT_FROZEN'
 if expected:assert pin(S)['sha256']==expected,'EXTERNAL_SEAL_PIN'
 seal=json.loads(S.read_text(encoding='utf-8'));rows=seal['immutableFiles'];assert len(rows)==len({r['path'] for r in rows})
 for row in rows:checked(row)
 members={r['path']:r for r in rows if r['path']!=seal['archive']['path']}
 with zipfile.ZipFile(Z) as z:
  assert len(z.namelist())==len(members) and set(z.namelist())==set(members)
  for name,row in members.items():
   raw=z.read(name);assert len(raw)==row['bytes'] and hashlib.sha256(raw).hexdigest()==row['sha256'],name
 prior=json.loads((B/'evidence/prior-freeze-verification.json').read_text());checked(prior['seal']);checked(prior['archive'])
 for row in json.loads((R/prior['seal']['path']).read_text())['immutableFiles']:checked(row)
 manifest=json.loads((B/'evidence/build-001/host-jar-manifest.json').read_text());checked(manifest['jar'])
 with zipfile.ZipFile(R/manifest['jar']['path']) as z:
  assert len(z.namelist())==183 and set(z.namelist())=={r['entry'] for r in manifest['classes']}
  for row in manifest['classes']:
   checked(row['source']);checked(row['testedClass']);data=z.read(row['entry']);assert len(data)==row['bytes'] and hashlib.sha256(data).hexdigest()==row['sha256'];assert data==(R/row['testedClass']['path']).read_bytes();assert 'ResumeCheck' not in row['entry']
 result=json.loads((B/'evidence/build-001/results.json').read_text());assert result['hostProductionCompilations']==1 and result['testOnlyRepairCompilations']==1 and result['androidBuilds']==0
 assert json.loads((B/'evidence/build-001/selfcheck.exit.json').read_text())['exitCode']!=0
 assert json.loads((B/'evidence/build-001/selfcheck-repair.exit.json').read_text())['exitCode']==0
 initial=json.loads((B/'evidence/build-001/inputs.json').read_text());assert pin(B/'evidence/build-001/ResumeCheck.initial.java.txt')['sha256']==initial[-1]['sha256']
 for row in initial[:-1]:checked(row)
 for row in json.loads((B/'evidence/build-001/test-repair-inputs.json').read_text()):checked(row)
 for row in json.loads((B/'evidence/source-derivation.json').read_text()):checked(row['original'])
 changes=json.loads((B/'evidence/final-source-difference.json').read_text())['changed'];assert len(changes)==4
 assert {Path(r['current']['path']).name for r in changes}=={'E13GuardLocation.java','E13HostActivationSession.java','E13HostCase.java','E13PendingGuard.java'}
 for row in changes:checked(row['original']);checked(row['current'])
 binding=json.loads((B/'release/candidate-binding.json').read_text());assert all(binding[k] is None for k in ['sourceReview','actualScope','actualRelease','actualOnce'])
 for key in ['hostJar','observer','disposition','administrativeReview','authorization','budget','scopeTemplate','releaseTemplate']:checked(binding[key])
 for row in binding['targetApks']:checked({k:row[k] for k in ['path','bytes','sha256']})
 d=json.loads((B/'disposition/reviewed-original-disposition.json').read_text());fields=d['fields'];assert len(fields)==10 and fields['outcome']=='TERMINATED_WITHOUT_RETURN' and fields['originalJavaReturn']=='false'
 for key,file in [('caseEvidence','case-evidence.json'),('diagnosticDisposition','diagnostic-disposition.json'),('review','administrative-review.json'),('authorization','authorization.json')]:assert fields[key]==pin(B/'disposition'/file)['sha256']
 assert ('DISPOSITION_SHA="'+binding['disposition']['sha256']+'"') in (B/'tools/E13GuardLocation.java').read_text()
 assert (B/'tools/observe_original.ps1').read_bytes()==(R/'docs/coder/d1e13f/tools/observe_original.ps1').read_bytes()
 assert 'PENDING_INDEPENDENT_SOURCE_REVIEW' in (B/'release/templates/scope.template.json').read_text()
 budget=json.loads((B/'release/exact-budget.json').read_text());assert sum(r['operations'] for r in budget['groups'])==43==budget['maxOperations']
 assert sum(r['textBytes'] for r in budget['groups'])==budget['rawAndDuplicatedOutputReserve']==1949696
 assert budget['rawAndDuplicatedOutputReserve']+budget['metadataAndControlTextReserve']+budget['unallocatedNotSpendable']==3145728
 assert budget['recordReserves']['subtotal']<=budget['metadataAndControlTextReserve']
 trace=json.loads((B/'evidence/build-001/deployment-command-trace.json').read_text());assert len(trace['children'])==35
 assert not (B/'execution').exists(),'UNEXPECTED_EXECUTION_DIRECTORY'
 return dict(status='PASS_RESUME01_STRICT_READONLY_VERIFY',writes=0,deviceCalls=0,originalCustodyRootAccesses=0,archive=seal['archive'],seal=pin(S),archiveEntries=len(members),immutableRows=len(rows),productionClasses=183,productionCompilations=1,testOnlyRepairCompilations=1,androidBuilds=0,operationProposal=43,textProposal=3145728,sourceReview=None,T07='NOT_RUN',D1='NOT_PASSED',M0='NOT_STARTED')
def pack():
 assert not S.exists() and not Z.exists(),'ALREADY_PACKED'
 paths=[p for p in B.rglob('*') if p.is_file() and '__pycache__' not in p.parts]
 paths += [R/'docs/coder/D1_RESUME_AFTER_TABLET_CLOSEOUT_DELIVERY_D1-20261020-RESUME01.md']
 binding=json.loads((B/'release/candidate-binding.json').read_text());paths += [R/r['path'] for r in binding['targetApks']]
 paths += [R/r['original']['path'] for r in json.loads((B/'evidence/source-derivation.json').read_text())]
 prior=json.loads((B/'evidence/prior-freeze-verification.json').read_text());paths += [R/prior['seal']['path']]
 rows=[pin(p) for p in sorted(set(paths))]
 with zipfile.ZipFile(Z,'x',compression=zipfile.ZIP_DEFLATED) as z:
  for row in rows:z.writestr(row['path'],(R/row['path']).read_bytes())
 archive=pin(Z);rows.append(archive)
 S.write_text(json.dumps(dict(schema=1,candidate='D1-20261020-RESUME01',archive=archive,immutableFiles=rows,sourceReview='PENDING_INDEPENDENT_STATIC_REVIEW',T07='NOT_RUN',deviceExecutionReleased=False),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps(dict(status='PACKED_OFFLINE_CANDIDATE',seal=pin(S),archive=archive,archiveEntries=len(rows)-1)))
def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('mode',choices=['verify','pack'],nargs='?',default='verify');parser.add_argument('--seal-sha');a=parser.parse_args()
 if a.mode=='pack':
  if a.seal_sha:parser.error('--seal-sha is verify-only')
  pack()
 else:print(json.dumps(verify(a.seal_sha)))
if __name__=='__main__':main()
