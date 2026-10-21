"""Static identity and recorded-case audit only; never imports production or fake runners."""
from pathlib import Path
import json,hashlib,zipfile,datetime
R=Path(__file__).resolve().parents[3];E=Path(__file__).resolve().parent;B=R/'docs/coder/d1e4at1'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
seal=B/'evidence/close-freeze.json';assert sha(seal)=='954288092916e5281c7a50183adc9041e82c05d16cfe6fd6cd5013fb75139c0f'
s=json.loads(seal.read_text());rows=s['immutable']
for r in rows:
 p=R/r['path'];assert p.stat().st_size==r['bytes'] and sha(p)==r['sha256']
manifest=json.loads((R/s['manifest']['path']).read_text());expected={r['path']:r for r in manifest['files']}
with zipfile.ZipFile(R/s['sourceZip']['path']) as z:
 assert len(z.namelist())==len(expected) and set(z.namelist())==set(expected)
 for n,r in expected.items():
  d=z.read(n);assert len(d)==r['bytes'] and hashlib.sha256(d).hexdigest()==r['sha256']
assert sha(R/'docs/coder/d1e4at/evidence/transfer-freeze.json')=='3b650fd8f14956216e9fa5c9f43ebe916e5b832980a6e450515275e09425902a'
assert sha(R/'docs/coder/d1e4a/evidence/e4a-freeze.json')=='a7fb8c9b4af7aab8f93f4300b7f4dd090a7d8b2759b42b42d0207244932d663d'
assert sha(R/'docs/tester/D1_E4A_T_TRANSFER_REVIEW_REPORT_V1.0.md')=='c71df0e928657020f3816b462a733dbd78aca3c87a7de0aa8b301fea3706beaa'
assert sha(B/'tools/fixture_transfer.py')==sha(R/'docs/coder/d1e4at/tools/fixture_transfer.py')
assert sha(B/'tools/fake_child.py')==sha(R/'docs/coder/d1e4at/tools/fake_child.py')
checks=json.loads((B/'evidence/local-check-results.json').read_text());cases=[]
for row in checks['cases']:
 p=json.loads((R/row['result']['path']).read_text());assert p['status']=='PASS' and p['assertions']==row['assertions'];assert not p['registryManuallyCleared'] and not p['forcedGc']
 if row['case'].startswith('throw_'):
  q=p['results'][0];assert q['ownership']=='UNKNOWN_RETAINED' and q['originalExitCode']==0 and q['writerReturned'] and not q['stdinCloseReturned'] and p['retainedOwnersAtCaseExit']==1 and p['proof']['closeCalls']==1
 cases.append({'case':row['case'],'assertions':p['assertions'],'actualChildLaunches':p['actualChildLaunches'],'retainedOwnersAtCaseExit':p['retainedOwnersAtCaseExit'],'originalResults':p['results']})
assert sum(c['assertions'] for c in cases)==63 and sum(c['actualChildLaunches'] for c in cases)==7
facts={'at':datetime.datetime.now().astimezone().isoformat(),'integrity':'PASS','sourceFiles':len(expected),'immutableFiles':len(rows),'sourceZip':s['sourceZip'],'cases':cases,'legacyToolAndProductAndReportUnchanged':True,'F01':'SUPPORTED_FIXED_STATIC_AND_RECORDED_NARROW_EVIDENCE','opaqueStartupFailure':'STATIC_FAIL_CLOSED_NOT_A_SEPARATE_EXECUTED_CASE','fakeRerun':False,'adbCalls':0,'mediaReads':0,'deviceRuns':0,'gradleRuns':0,'inFlight':[]}
(E/'identity-and-cases-audit.json').write_text(json.dumps(facts,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'integrity':'PASS','sourceFiles':len(expected),'immutableFiles':len(rows),'recordedAssertions':63,'intentionalUnknownCases':2}))
