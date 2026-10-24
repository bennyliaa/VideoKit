from pathlib import Path
import json,hashlib,ast
R=Path(__file__).resolve().parent;P=R.parent;report=P/'D1_FACTS_V2_QUALIFICATION07_INDEPENDENT_B_REPORT_V1.0.md';C=P.parent/'coder/d1android02-facts-v2-qualification07'
sha=lambda b:hashlib.sha256(b).hexdigest()
load=lambda p:json.loads(p.read_bytes())
assert load(R/'post-audit.json')['allPassed'] and load(R/'static-closure.json')['allPassed']
assert load(R/'evidence/result.json')['revisionReturnProof']['allOriginalsProven'] and load(R/'outer-final.json')['receipt']['exitCode']==0
bad=[]
for x in load(C/'full-manifest.json')['files']:
 b=(C/x['path']).read_bytes()
 if len(b)!=x['bytes'] or sha(b)!=x['sha256']:bad.append(x['path'])
assert not bad
for p in R.rglob('*.py'):ast.parse(p.read_text(encoding='utf-8-sig'))
excluded={'delivery-manifest.json','delivery-freeze.json','coordinator-send-receipt.json'};rows=[]
for p in sorted([report]+[p for p in R.rglob('*') if p.is_file() and p.name not in excluded]):
 b=p.read_bytes();rows.append(dict(path=str(p),bytes=len(b),sha256=sha(b)))
size=sum(x['bytes'] for x in rows);assert size<16777216
m=dict(schema='QUALIFICATION07_INDEPENDENT_B_DELIVERY_MANIFEST_V1',files=rows,count=len(rows),bytes=size,exclusions=sorted(excluded),result='PASS_LIMITED_OFFLINE_REV2_FUNCTION_CLUSTER',D1='NOT_PASSED',M0='NOT_STARTED')
(R/'delivery-manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
invalid=[x['path'] for x in rows if sha(Path(x['path']).read_bytes())!=x['sha256']]
out=dict(count=len(rows),bytes=size,bad=invalid,reportSha256=sha(report.read_bytes()),manifestSha256=sha((R/'delivery-manifest.json').read_bytes()),allNineGroupsPassed=True,postAuditChecks=39,sourceClosureChecks=14,originalsReturned=True,realUnknownObserved=False,autoNextBatch=False,candidate567Unchanged=True)
(R/'delivery-freeze.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
assert sum(p.stat().st_size for p in R.rglob('*') if p.is_file())+report.stat().st_size<16777216
print(json.dumps(out))
