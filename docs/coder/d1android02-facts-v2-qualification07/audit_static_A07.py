from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parent;T=R.parents[1]/'tester';A=T/'D1_FACTS_V2_QUALIFICATION07_PHASE_A_EVIDENCE';mf=A/'manifest.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(mf)=='0a9173fc3f2c654c408d1a75bb4dc239b6a8437ca1f1840f9b4ef002a0c3e48f'
m=json.loads(mf.read_bytes());es=m['files'];assert len(es)==90
for e in es:
 p=Path(e['path']);p=p if p.is_absolute() else T/p;assert p.stat().st_size==e['bytes'] and sha(p)==e['sha256']
report=T/'D1_FACTS_V2_QUALIFICATION07_PHASE_A_REPORT_V1.0.md';assert sha(report)=='55cebda03133f2a9669da8b2386376c55ee13c750d28e5e82ca68f8d7dfdb4ca'
note=dict(reportSha256=sha(report),manifestSha256=sha(mf),files=90,bytes=sum(e['bytes'] for e in es),bad=0,receivedBefore07ProductCalls=True,appliedConcentrated=['childraw unified source_charge event with exact patch assertion','route child self-hash reservation before original constructor; independent source vs control reads','all named V1/V2 producer pins and inline copies','full RAW/COMPLETE/LIVE obligation tables; keep existing SourceBudget/Runner/host authority domains'],old05Queries=0,productCalls=0)
(R/'static-A07-receipt.json').write_bytes((json.dumps(note,ensure_ascii=False,indent=2)+'\n').encode());print(json.dumps(note))
