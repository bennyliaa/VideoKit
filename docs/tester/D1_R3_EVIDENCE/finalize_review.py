"""Finalize static review evidence only; no experimental execution."""
from pathlib import Path
import json,hashlib,re
from datetime import datetime
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,v):(OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
report=ROOT/'docs/tester/D1_R3_REVIEW_REPORT_V1.0.md'
text=report.read_text(encoding='utf-8')
rows=re.findall(r'^\| R\d{2} \|.*?\| (SUPPORTED|CONTRADICTED|MISSING) \|',text,re.M)
counts={s:rows.count(s) for s in ['SUPPORTED','CONTRADICTED','MISSING']}
assert counts==dict(SUPPORTED=15,CONTRADICTED=0,MISSING=1),counts
for m in re.finditer(r'\]\((D:/CodexProjects/VideoKit/[^)]+)\)',text):
 t=m.group(1);lm=re.search(r':(\d+)$',t);line=int(lm.group(1)) if lm else None
 if lm:t=t[:lm.start()]
 p=Path(t);assert p.exists(),t
 if line:assert 1<=line<=len(p.read_text(encoding='utf-8-sig').splitlines()),t
inputs=json.loads((OUT/'input-and-link-audit.json').read_text(encoding='utf-8'))
post=[]
for r in inputs['inputs']:
 digest=sha(ROOT/r['path']);assert digest==r['sha256']
 post.append(dict(path=r['path'],sha256=digest,unchanged=True))
for r in inputs['r2Unchanged']:assert sha(ROOT/r['path'])==r['expected']
operations=['openTemporary/grant','receiver claim','writer finalize/close request (all writer references grouped)','validation lease authorization/open','validation lease return/close','takeover','old-owner markReady rejected','new-owner abort']
save('control-operation-review.json',dict(scope='Static counterexample under independent-request decomposition, not an executed trace or an impossibility proof for all aggregate APIs',branch='Q07-TAKEFIRST',task='T05',rowLimit=6,conventionalIndependentRequests=operations,count=len(operations),excludedFromExample=['actual allocation/dup/send/take','write/flush','query','separate close of each descriptor'],missing='Predefined aggregate-command signatures, bounded suboperations and per-row request mapping. A defined finalize/validate aggregate may reduce external commands, but none is specified.',conclusion='MISSING; aggregate allocated total 515 is arithmetically correct, not a proof of row feasibility'))
save('review-summary.json',dict(at=datetime.now().astimezone().isoformat(),task='D1-R3 independent whole-package design re-review',report=report.relative_to(ROOT).as_posix(),reportSha256=sha(report),counts=counts,conclusion='CLOSE_AND_WRITER_DESIGN_SUPPORTED; CONTROL_OPERATION_MAPPING_MISSING_BEFORE_FULL_EXPERIMENT_DISPATCH',r2Findings={'R2-R01':'Design supplementation supported; implementation not verified','R2-R02':'Design supplementation supported; implementation not verified','R2-R03':'Branch/numeric budget supported; row control feasibility remains MISSING'},findings=[dict(id='R3-R01',severity='P1',classification='MISSING',topic='Per-row control-operation trace and aggregate command granularity')],inputsPostCheck=post,r2OriginalsUnchanged=True,functionalTestsRun=0,deviceTestsRun=0,mediaIO=False,gradle=False,adb=False,inFlight=[],D1Passed=False,M0Started=False,notification='Not retried after prior automatic approval rejection; final completion available to coordinator scheduled checks'))
print(json.dumps(dict(reportSha256=sha(report),counts=counts,inputsUnchanged=True,inFlight=[]),ensure_ascii=False))
