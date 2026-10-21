"""Finalize offline R4 review; does not execute the planned control manifest."""
from pathlib import Path
import hashlib,json,re
from datetime import datetime
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,v):(OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
report=ROOT/'docs/tester/D1_R4_REVIEW_REPORT_V1.0.md';txt=report.read_text(encoding='utf-8')
rows=re.findall(r'^\| R\d{2} \|.*?\| (SUPPORTED|CONTRADICTED|MISSING) \|',txt,re.M)
counts={s:rows.count(s) for s in ['SUPPORTED','CONTRADICTED','MISSING']}
assert counts==dict(SUPPORTED=18,CONTRADICTED=0,MISSING=0),counts
for m in re.finditer(r'\]\((D:/CodexProjects/VideoKit/[^)]+)\)',txt):
 t=m.group(1);lm=re.search(r':(\d+)$',t);ln=int(lm.group(1)) if lm else None
 if lm:t=t[:lm.start()]
 p=Path(t);assert p.exists(),t
 if ln:assert 1<=ln<=len(p.read_text(encoding='utf-8-sig').splitlines()),t
audit=json.loads((OUT/'input-and-link-audit.json').read_text(encoding='utf-8'))
for r in audit['inputs']:assert sha(ROOT/r['path'])==r['sha256']
for r in audit['oldInputsUnchanged']:assert sha(ROOT/r['path'])==r['sha256']
save('review-summary.json',dict(at=datetime.now().astimezone().isoformat(),task='D1-R4 independent whole-package control-manifest review',report=report.relative_to(ROOT).as_posix(),reportSha256=sha(report),counts=counts,conclusion='R3-R01_MATERIAL_GAP_CLOSED; SUFFICIENT_TO_RECOMMEND_SEPARATELY_DISPATCHED_BOUNDED_LOCAL_HARNESS_IMPLEMENTATION',newBlockingDesignFindings=[],controlAllocation=dict(p=176,q=127,PF=16,GC=32,nonQuery=351,query=101,total=452,limit=544),notAuthorizedByThisReport=['Experiment execution','M0','Public API freeze','Product/Android/Windows Kit implementation or admission'],notYetVerified=['Backend compatibility and source version','True OS dup/mailbox/close and process exit','Durability','10ms planning assumption and actual deadlines','Host JNI fault containment'],inputsAndR2R3OriginalsUnchanged=True,functionalTestsRun=0,deviceTestsRun=0,mediaIO=False,adb=False,gradle=False,inFlight=[],D1Passed=False,M0Started=False,C14Resumed=False,notification='Not retried after prior automatic approval rejection; coordinator may retrieve this final result during scheduled status checks'))
print(json.dumps(dict(reportSha256=sha(report),counts=counts,inputsUnchanged=True,inFlight=[]),ensure_ascii=False))
